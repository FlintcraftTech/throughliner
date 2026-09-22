#!/usr/bin/env python3
"""Regression tests for queue_digest.py's `Left to process, this one included` line.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_queue_digest_next_count.py

No test framework, matching the suites alongside it.

Why this exists ([checkpoint-count-from-next-pick-tool]): plan.md's checkpoint
reports how many entries are left to process, and a planning session counted
the raw size of Unprocessed — eighteen, every checkpoint — when the rule
excludes what the ladder will never offer. The `--next` output now prints the
offerable count on its own line, computed from the same pass-over the pick
itself uses, and the state server's next-pick tool passes it through unchanged.
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER = os.path.join(ROOT, "plugin", "throughliner", "mcp", "server.py")
DIGEST = os.path.join(ROOT, "plugin", "throughliner", "scripts", "queue_digest.py")

failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        failures.append(name)


QUEUE = """# QUEUE

## Processed

#### Alpha — a cleared build [alpha]
Alpha's rationale.

--- Cleared to run above this line ---

## Unprocessed

#### One — dated ahead [one]
Waits on the world.
Not before: 2031-01-01

#### Two — a cycle's material [two]
Drawn by the cycle's turns.
Cycle: [weekly-release]

#### Three — held on an unprocessed entry [three]
Waits on one, still a capture.
Blocked by: [one]

#### Four — plain [four]
Ordinary.

#### Five — plain [five]
Ordinary.

#### Six — plain [six]
Ordinary.
"""

CYCLES = """# CYCLES

## Weekly release [weekly-release]
Cadence: weekly, declared by the user 2026-01-01.
Observable: the latest release's date.
"""


def project():
    d = tempfile.mkdtemp(prefix="digest-next-count-")
    for name, text in (("QUEUE.md", QUEUE), ("CYCLES.md", CYCLES)):
        with open(os.path.join(d, name), "w", encoding="utf-8", newline="") as f:
            f.write(text)
    return d


def run_digest(d, *extra):
    proc = subprocess.run(
        [sys.executable, DIGEST, os.path.join(d, "QUEUE.md"), "--next", *extra],
        capture_output=True, encoding="utf-8", cwd=d, timeout=60)
    if proc.returncode != 0:
        raise AssertionError("digest exited %d\n%s" % (proc.returncode,
                                                       proc.stderr))
    return proc.stdout


def offerable_line(text):
    for line in text.splitlines():
        if line.startswith("Left to process, this one included:"):
            return line
    return None


def call_server(cwd, arguments):
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": "queue_next_pick", "arguments": arguments}},
    ]
    payload = "".join(json.dumps(r, ensure_ascii=False) + "\n"
                      for r in requests).encode("utf-8")
    env = dict(os.environ)
    env["THROUGHLINER_PROJECT_ROOT"] = cwd
    proc = subprocess.run([sys.executable, SERVER], input=payload, cwd=cwd,
                          capture_output=True, env=env, timeout=60)
    if proc.returncode != 0:
        raise AssertionError("server exited %d\nstdout: %r\nstderr: %r"
                             % (proc.returncode, proc.stdout, proc.stderr))
    for line in proc.stdout.decode("utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("id") == 2:
            return r.get("result", {}).get("content", [{}])[0].get("text", "")
    return ""


d = project()

# Three plain captures are offerable; one, two and three are passed over.
text = run_digest(d)
check("with nothing skipped, three are left with the pick counted in",
      offerable_line(text) == "Left to process, this one included: 3", repr(text))
check("the line sits above the medians line",
      text.index("Left to process, this one included") < text.index("medians:"))

# One plain capture skipped: the pick takes another; two left, it included.
text = run_digest(d, "--skip", "four")
check("one skipped leaves two, the pick counted in",
      offerable_line(text) == "Left to process, this one included: 2", repr(text))
check("the three passed-over kinds are never counted",
      "[one]" not in text.split("\n\n", 1)[0]
      and "[two]" not in text.split("\n\n", 1)[0])

# Every plain capture skipped: nothing to pick, and the count is 0.
text = run_digest(d, "--skip", "four,five,six")
check("at rest the count prints as 0 beside the nothing line",
      text.startswith("Next: nothing")
      and offerable_line(text) == "Left to process, this one included: 0", repr(text))

# The state server passes the line through as the script printed it.
server_text = call_server(d, {"skip": ["four"]})
check("queue_next_pick carries the same line",
      offerable_line(server_text) == "Left to process, this one included: 2",
      repr(server_text))
server_text = call_server(d, {"skip": ["four", "five", "six"]})
check("queue_next_pick carries the 0 at rest",
      offerable_line(server_text) == "Left to process, this one included: 0",
      repr(server_text))

shutil.rmtree(d, ignore_errors=True)

print()
if failures:
    print("%d failure(s):" % len(failures))
    for name in failures:
        print("  " + name)
    sys.exit(1)
print("all cases passed")
