#!/usr/bin/env python3
"""The state server's next_run_line tool ([next-run-line-at-close]).

Run: py tests/test_mcp_next_run_line.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

Every close leaves one standing [user] item, slug `next-run`, whose task
line says what the project wants run and why, with the digest's standing
cleared-to-run counts by kind, dated from the nearest due thing in the queue.
The server is driven end to end as a subprocess, as the other tool suites do.
"""

import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER = os.path.join(ROOT, "plugin", "throughliner", "mcp", "server.py")

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

#### [audit] Beta — a cleared audit [beta]
Beta's rationale.

#### [user] Phone the office [phone-office]
A step of yours.
- [ ] Phone the office (Demo) 📅 2026-12-01 🆔 phone-office #user

--- Cleared to run above this line ---

#### Gamma — a held build [gamma]
Gamma's rationale.
Not before: 2020-01-01

## Unprocessed

#### Delta — a capture [delta]
Delta's rationale.

#### Epsilon — a capture [epsilon]
Epsilon's rationale.
"""

MARKER = "--- Cleared to run above this line ---"


def project(text):
    d = os.path.join(tempfile.mkdtemp(prefix="next-run-"), "Demo")
    os.makedirs(d)
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    return d


def call(cwd, name, arguments=None):
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": name, "arguments": arguments or {}}},
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


def queue_text(d):
    with open(os.path.join(d, "QUEUE.md"), "rb") as f:
        return f.read().decode("utf-8")


print("test_mcp_next_run_line")
today = datetime.date.today().isoformat()

# --- the ordinary case: cleared work, a dated step, a passed hold -----------
d = project(QUEUE)
text = call(d, "next_run_line")
after = queue_text(d)
check("the tool reports the line it wrote",
      text.startswith("Wrote the next-run line") and "Run /build in Demo" in text,
      repr(text))
block = after.split("[next-run]")[1].split(MARKER)[0] if "[next-run]" in after else ""
check("the standing item sits as the last cleared item, above the marker",
      "[next-run]" in after and after.index("[next-run]") < after.index(MARKER)
      and after.index("[phone-office]") < after.index("[next-run]"), repr(after))
check("the heading carries the [user] tag",
      "#### [user] Run /build in Demo:" in after, repr(after))
check("the task line carries the counts by kind and the first cleared item",
      "1 build, 1 audit and 1 step of yours cleared, [alpha] first" in block
      and "2 captures waiting" in block, repr(block))
check("the task line carries #user, the slug and the project",
      "(Demo)" in block and "🆔 next-run #user" in block, repr(block))
check("the date is the nearest due thing: the passed Not before, today",
      "📅 %s" % today in block, repr(block))
check("the body says where the date came from",
      "past its Not before: date" in block, repr(block))

# --- the standing counts leave the line itself out --------------------------
counts = call(d, "queue_checkpoint_counts")
check("the checkpoint counts do not count the standing line",
      "Cleared to run (Processed, above the line): 3" in counts, repr(counts))

# --- a second call rewrites one item, never two -----------------------------
text2 = call(d, "next_run_line")
after2 = queue_text(d)
check("a second close rewrites the one standing item",
      after2.count("[next-run]") == 1 and after2.count("🆔 next-run") == 1,
      repr(after2))

# --- with the hold's date ahead, the step's 📅 is the nearest ---------------
with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8", newline="") as f:
    f.write(QUEUE.replace("Not before: 2020-01-01", "Not before: 2099-01-01"))
call(d, "next_run_line")
after3 = queue_text(d)
check("a dated step of the user's dates the line",
      "📅 2026-12-01 🆔 next-run" in after3, repr(after3))

# --- a Due: line on a capture is read too -----------------------------------
with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8", newline="") as f:
    f.write(QUEUE.replace("Not before: 2020-01-01", "Not before: 2099-01-01")
            .replace("Delta's rationale.", "Delta's rationale.\nDue: 2026-11-20"))
call(d, "next_run_line")
after4 = queue_text(d)
check("a Due: line on any entry dates the line where it is nearest",
      "📅 2026-11-20 🆔 next-run" in after4, repr(after4))
shutil.rmtree(os.path.dirname(d), ignore_errors=True)

# --- nothing cleared, little waiting, nothing dated: quiet and undated -------
QUIET = """# QUEUE

## Processed

--- Cleared to run above this line ---

## Unprocessed

#### Delta — a capture [delta]
Delta's rationale.
"""
d = project(QUIET)
text = call(d, "next_run_line")
after = queue_text(d)
check("with nothing cleared the line says to run plan",
      "Run /plan in Demo when you like: 1 capture waiting to be planned" in after,
      repr(after))
check("the quiet line carries no date", "📅" not in after.split("[next-run]")[1],
      repr(after))
check("with no marker anchor the item still sits above the marker",
      after.index("[next-run]") < after.index(MARKER), repr(after))

# --- nothing queued at all: the standing item is removed --------------------
EMPTY_WITH_LINE = after.split("#### Delta")[0] + after.split("Delta's rationale.\n")[1]
with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8", newline="") as f:
    f.write(EMPTY_WITH_LINE)
check("the fixture for the empty case still carries the standing line",
      "[next-run]" in EMPTY_WITH_LINE and "[delta]" not in EMPTY_WITH_LINE,
      repr(EMPTY_WITH_LINE))
text = call(d, "next_run_line")
after = queue_text(d)
check("with nothing queued the standing item is removed and the tool says so",
      "[next-run]" not in after and "removed" in text, repr(text) + repr(after))
text = call(d, "next_run_line")
check("with nothing queued and no item, nothing is written",
      "no next-run line was written" in text and "[next-run]" not in queue_text(d),
      repr(text))
shutil.rmtree(os.path.dirname(d), ignore_errors=True)

print()
if failures:
    print("%d failure(s):" % len(failures))
    for name in failures:
        print("  " + name)
    sys.exit(1)
print("all cases passed")
