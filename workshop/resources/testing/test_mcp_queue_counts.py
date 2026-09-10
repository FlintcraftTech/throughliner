#!/usr/bin/env python3
"""Regression tests for mcp/server.py's queue_checkpoint_counts tool.

Host-only dev artifact — not shipped in the plugin package.

Run:  py workshop/resources/testing/test_mcp_queue_counts.py

No test framework, matching the suites alongside it.

Why this exists ([checkpoint-counts-tool-reports-presentable-count]): the tool
returned 63 where the checkpoint's own definition gave about 32 — it counted
every capture, and the checkpoint counts only the presentable ones (minus those
dated out, owned by a cycle, or held behind an open blocker). Both figures now
come out side by side, the presentable one from the digest's own pass-over
function, which is also what `--next` picks from — so the two cannot disagree.
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SERVER = os.path.join(ROOT, "plugin", "throughliner", "mcp", "server.py")
DIGEST = os.path.join(ROOT, "plugin", "throughliner", "scripts", "queue_digest.py")

_spec = importlib.util.spec_from_file_location("queue_digest", DIGEST)
digest = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(digest)

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

#### One — dated out [one]
Waits on the world.
Not before: 2031-01-01

#### Two — a cycle's material [two]
Drawn by the cycle's turns.
Cycle: [weekly-release]

#### Three — held behind an open blocker [three]
Waits on one, which is still a capture. (A capture held on a PROCESSED item is
presentable under the rule — see test_queue_digest.py — so the hold here names
an entry still in Unprocessed.)
Blocked by: [one]

#### Four — plain [four]
Ordinary.

#### Five — plain [five]
Ordinary.
"""

CYCLES = """# CYCLES

## Weekly release [weekly-release]
Cadence: weekly.
Observable: the latest release's date.
"""

d = tempfile.mkdtemp(prefix="mcp-queue-counts-")
with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8", newline="") as f:
    f.write(QUEUE)
with open(os.path.join(d, "CYCLES.md"), "w", encoding="utf-8") as f:
    f.write(CYCLES)

requests = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
     "params": {"name": "queue_checkpoint_counts", "arguments": {}}},
]
payload = "".join(json.dumps(r) + "\n" for r in requests).encode("utf-8")
env = dict(os.environ)
env["THROUGHLINER_PROJECT_ROOT"] = d
proc = subprocess.run([sys.executable, SERVER], input=payload, cwd=d,
                      capture_output=True, env=env, timeout=60)
text = ""
for line in proc.stdout.decode("utf-8").splitlines():
    if line.strip():
        r = json.loads(line)
        if r.get("id") == 2:
            text = r["result"]["content"][0]["text"]

check("the tool answers", proc.returncode == 0 and text, repr(proc.stderr))
check("raw count is 5", "captures waiting: 5 (raw)" in text, repr(text))
check("presentable count is 2", "left to process: 2 (presentable" in text,
      repr(text))

# The presentable figure equals what --next picks from.
items = digest.parse(os.path.join(d, "QUEUE.md"))
pool = digest.offerable(items, d)
check("the digest's own pass-over yields the same 2",
      sorted(i["slug"] for i in pool) == ["five", "four"], repr(pool))
rung, why, item = digest.whats_next(items, d, os.path.join(d, "QUEUE.md"))
check("--next picks from that same pool", item is not None and
      item["slug"] in ("four", "five"), repr((rung, why)))

shutil.rmtree(d, ignore_errors=True)

# --- host_currency answers in the nested layout -------------------------------
# [mcp-host-currency-misses-inner-root]: since the wrap the plugin source sits
# under the one child folder that carries its own .git, so the flat path is
# absent and the tool used to refuse. A root with no CLAUDE.md exercises the
# one-child-with-.git fallback rather than the Visibility-line read.
d = tempfile.mkdtemp(prefix="mcp-host-currency-nested-")
inner_hooks = os.path.join(d, "product", "plugin", "throughliner", "hooks")
os.makedirs(inner_hooks)
os.makedirs(os.path.join(d, "product", ".git"))
with open(os.path.join(inner_hooks, "session_start.py"), "w",
          encoding="utf-8") as f:
    f.write("# a stand-in for the hook, so the source folder has a file\n")
requests = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
     "params": {"name": "host_currency", "arguments": {}}},
]
payload = "".join(json.dumps(r) + "\n" for r in requests).encode("utf-8")
env = dict(os.environ)
env["THROUGHLINER_PROJECT_ROOT"] = d
proc = subprocess.run([sys.executable, SERVER], input=payload, cwd=d,
                      capture_output=True, env=env, timeout=60)
text = ""
for line in proc.stdout.decode("utf-8").splitlines():
    if line.strip():
        r = json.loads(line)
        if r.get("id") == 2:
            text = r["result"]["content"][0]["text"]
check("host_currency resolves the source under the inner repository",
      proc.returncode == 0 and "Source stamp" in text
      and "No plugin source" not in text, repr(text or proc.stderr))
shutil.rmtree(d, ignore_errors=True)

print()
if failures:
    print("%d failure(s):" % len(failures))
    for name in failures:
        print("  " + name)
    sys.exit(1)
print("all cases passed")
