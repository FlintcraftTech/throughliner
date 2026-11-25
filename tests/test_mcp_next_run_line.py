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
      "1 build and 1 audit cleared, [alpha] first" in block
      and "1 step of yours also cleared" in block
      and "2 captures waiting" in block, repr(block))
check("the task line says what done looks like",
      "done when the run reaches the line" in block, repr(block))
check("the task line carries #user, the slug and the project",
      "(Demo)" in block and "🆔 next-run #user" in block, repr(block))
check("the date is a cleared step's, never the held item's passed Not before",
      "📅 2026-12-01 🆔 next-run" in block and "📅 %s" % today not in block,
      repr(block))
check("the body says where the date came from",
      "the step [phone-office]" in block, repr(block))
answer = call(d, "next_command")
check("next_command names the same command and words as the line written",
      answer.startswith("Next command: build — Run /build in Demo: 1 build "
                        "and 1 audit cleared, [alpha] first, done when the "
                        "run reaches the line")
      and "Dated 2026-12-01" in answer, repr(answer))
check("next_command writes nothing", queue_text(d) == after, "queue changed")

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

# --- a Due: line dates the line only where the named command can do it ------
with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8", newline="") as f:
    f.write(QUEUE.replace("Not before: 2020-01-01", "Not before: 2099-01-01")
            .replace("Delta's rationale.", "Delta's rationale.\nDue: 2026-11-20"))
call(d, "next_run_line")
after4 = queue_text(d)
check("a capture's Due: does not date a build line, which cannot sort it",
      "📅 2026-12-01 🆔 next-run" in after4, repr(after4))
with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8", newline="") as f:
    f.write(QUEUE.replace("Not before: 2020-01-01", "Not before: 2099-01-01")
            .replace("Alpha's rationale.", "Alpha's rationale.\nDue: 2026-11-20"))
call(d, "next_run_line")
after4 = queue_text(d)
check("a Due: line on a cleared item dates a build line where it is nearest",
      "📅 2026-11-20 🆔 next-run" in after4, repr(after4))
shutil.rmtree(os.path.dirname(d), ignore_errors=True)

# --- only steps of the user's cleared, captures waiting: process ------------
STEPS_AND_CAPTURES = """# QUEUE

## Processed

#### [user] Phone the office [phone-office]
A step of yours.
- [ ] Phone the office (Demo) 📅 2026-12-01 🆔 phone-office #user

--- Cleared to run above this line ---

#### [user] Sign the form [sign-form]
A held step of yours.
- [ ] Sign the form (Demo) 📅 2026-11-01 🆔 sign-form #user
Blocked by: [phone-office]

## Unprocessed

#### Delta — a capture [delta]
Delta's rationale.

#### Epsilon — a capture [epsilon]
Epsilon's rationale.
Not before: 2099-01-01
"""
d = project(STEPS_AND_CAPTURES)
answer = call(d, "next_command")
call(d, "next_run_line")
after = queue_text(d)
line = next(l for l in after.splitlines() if "🆔 next-run" in l)
check("steps of the user's cleared with captures waiting answers process",
      answer.startswith("Next command: process — Run /process in Demo: "
                        "1 capture waiting to be sorted, done when none are "
                        "left to sort; 1 step of yours also cleared"),
      repr(answer))
check("a capture held by a date still ahead is not counted as waiting",
      "2 captures" not in answer, repr(answer))
check("the line written names the same command as next_command",
      "Run /process in Demo: 1 capture waiting to be sorted" in line, repr(line))
check("neither a held step's 📅 nor a cleared step's dates a process line",
      "📅" not in line, repr(line))
shutil.rmtree(os.path.dirname(d), ignore_errors=True)

# --- only steps of the user's cleared, nothing to sort: build, to walk ------
d = project(STEPS_AND_CAPTURES.split("## Unprocessed")[0] + "## Unprocessed\n")
answer = call(d, "next_command")
call(d, "next_run_line")
line = next(l for l in queue_text(d).splitlines() if "🆔 next-run" in l)
check("only steps of the user's cleared answers build, to walk them",
      answer.startswith("Next command: build — Run /build in Demo: to walk "
                        "1 step of yours, done when each is done or put off"),
      repr(answer))
check("the cleared step's 📅 dates that line, the held step's does not",
      "📅 2026-12-01 🆔 next-run" in line, repr(line))
shutil.rmtree(os.path.dirname(d), ignore_errors=True)

# --- a due chain step whose definition names the user's part comes first ----
CYCLES = """# CYCLES

## Release cycle [release-cycle]

**Cadence:** none; a sequential chain with no date on any step.

**Chain:** one turn, in order.
0. **Beta pick [beta-pick]** — on the user's word.
1. **Release [release]** — after [beta-pick].

**Observable:** the latest release.

# Checklists

## Beta pick [beta-pick]

**Trigger:** the user naming a build as the beta.

**Your part:** Run the plan command and say yes when it names the build

## Release [release]

**Trigger:** after [beta-pick] in [release-cycle].

**Your part:** Run the plan command and say yes when it asks whether to
release the build you have been running.
"""
d = project(QUEUE)
with open(os.path.join(d, "CYCLES.md"), "w", encoding="utf-8") as f:
    f.write(CYCLES)
answer = call(d, "next_command")
check("with the chain waiting on the user's word the cycles doc changes nothing",
      answer.startswith("Next command: build —"), repr(answer))
os.makedirs(os.path.join(d, "LOG"))
with open(os.path.join(d, "LOG", "2026-01-05-beta-pick.md"), "w",
          encoding="utf-8") as f:
    f.write("# abc1234 — beta pick\n\nRecorded 2026-01-05 10:00, read from "
            "the clock.\n")
answer = call(d, "next_command")
call(d, "next_run_line")
line = next(l for l in queue_text(d).splitlines() if "🆔 next-run" in l)
check("a due chain step answers its own command, in its definition's words",
      answer.startswith("Next command: plan — Run /plan in Demo: [release] is "
                        "due: Run the plan command and say yes when it asks "
                        "whether to release the build you have been running, "
                        "done when that step has its record"), repr(answer))
check("the line written for a due step names the same command, dated today",
      "Run /plan in Demo: [release] is due" in line
      and "📅 %s 🆔 next-run" % today in line, repr(line))
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
check("with nothing cleared the line says to run process",
      "Run /process in Demo when you like: 1 capture waiting to be sorted, "
      "done when none are left to sort" in after,
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

# --- a hold date still ahead ([not-before-dates-offer-a-reminder]) ----------
ahead = (datetime.date.today() + datetime.timedelta(days=20)).isoformat()
nearer = (datetime.date.today() + datetime.timedelta(days=5)).isoformat()
HELD_ONLY = """# QUEUE

## Processed

--- Cleared to run above this line ---

#### [user] Edit the checklist tip once a release ships [edit-tip]
A walkthrough of yours.
Not before: %s

## Unprocessed
""" % ahead

# Nothing else queued: the line is the hold's own, dated on the hold date.
d = project(HELD_ONLY)
text = call(d, "next_run_line",
            {"hold_reason": "the release that carries the edit."})
after = queue_text(d)
check("a held item's future date writes the line in the command, thing and "
      "reason form",
      "Run /build in Demo to edit the checklist tip once a release ships, "
      "due %s for the release that carries the edit" % ahead in after,
      repr(text) + repr(after))
check("the line is dated on the hold date",
      "📅 %s 🆔 next-run #user" % ahead in after, repr(after))
check("the body says the date is the hold's",
      "the hold date on [edit-tip]" in after, repr(after))
text = call(d, "next_run_line")
after = queue_text(d)
check("with no reason passed the line says held until the date",
      "Run /build in Demo to edit the checklist tip once a release ships, "
      "held until %s" % ahead in after and after.count("[next-run]") == 1,
      repr(after))
shutil.rmtree(os.path.dirname(d), ignore_errors=True)

# A capture held by date reads as a processing run.
d = project(HELD_ONLY.replace(
    "#### [user] Edit the checklist tip once a release ships [edit-tip]\n"
    "A walkthrough of yours.\nNot before: %s\n\n## Unprocessed\n" % ahead,
    "## Unprocessed\n\n#### Renewal of the domain [renew-domain]\n"
    "Waits on the registrar's window.\nNot before: %s\n" % ahead))
call(d, "next_run_line", {"hold_reason": "the registrar's renewal window"})
after = queue_text(d)
check("a capture's future date writes a process line, dated on the hold date",
      "Run /process in Demo to renewal of the domain, due %s for the "
      "registrar's renewal window" % ahead in after
      and "📅 %s 🆔 next-run" % ahead in after, repr(after))
shutil.rmtree(os.path.dirname(d), ignore_errors=True)

# A held item whose date has passed dates nothing: no command can do it until
# an opening lifts it, and the line keeps the counts form.
d = project(HELD_ONLY.replace("Not before: %s" % ahead, "Not before: 2020-01-01")
            .replace("## Unprocessed\n", "## Unprocessed\n\n#### Delta — a capture [delta]\nDelta's rationale.\n"))
call(d, "next_run_line", {"hold_reason": "unused"})
after = queue_text(d)
line = next(l for l in after.splitlines() if "🆔 next-run" in l)
check("a held item's passed date does not date the line, which keeps the "
      "counts form",
      "📅" not in line and "Run /process in Demo when you like:" in line
      and "1 item held below the line" in line and "held until" not in line,
      repr(line))
shutil.rmtree(os.path.dirname(d), ignore_errors=True)

# A hold date later than a nearer Due: the Due dates the line.
d = project(HELD_ONLY.replace(
    "## Unprocessed\n",
    "## Unprocessed\n\n#### Delta — a capture [delta]\nDelta's rationale.\nDue: %s\n" % nearer))
call(d, "next_run_line", {"hold_reason": "unused"})
after = queue_text(d)
check("a nearer Due: dates the line ahead of a later hold date",
      "📅 %s 🆔 next-run" % nearer in after and "Run /process in Demo:" in after
      and "held until" not in after.split("[next-run]")[1].split("\n")[0],
      repr(after))
shutil.rmtree(os.path.dirname(d), ignore_errors=True)

# Work ready now keeps its own line and date; the hold is a closing clause.
d = project(QUEUE.replace("Not before: 2020-01-01", "Not before: %s" % ahead)
            .replace(" 📅 2026-12-01", ""))
call(d, "next_run_line", {"hold_reason": "unused"})
after = queue_text(d)
block = after.split("[next-run]")[1].split(MARKER)[0]
check("with work cleared now the line keeps its counts and stays undated, "
      "so a list of what is due does not hide it",
      "1 build and 1 audit cleared, [alpha] first" in block
      and "📅" not in block.split("\n")[1], repr(block))
check("and names the hold in a closing clause",
      "; [gamma] held until %s" % ahead in block, repr(block))
shutil.rmtree(os.path.dirname(d), ignore_errors=True)

print()
if failures:
    print("%d failure(s):" % len(failures))
    for name in failures:
        print("  " + name)
    sys.exit(1)
print("all cases passed")
