#!/usr/bin/env python3
"""Fixture suite for the queue lint's once-only "gone" notice.

Run: py tests/test_post_tool_use_lint_state.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

Why this exists ([lint-gone-notice-repeats-every-call]): both warning
directions read the last commit as their baseline, so a flag cleared this
session stayed "gone against the commit" after every tool call until the
close committed — one notice, dozens of times, for a whole planning session.
The gone direction now reads a second baseline, the bodies the previous lint
run found, kept in the project's ignored `.throughliner/` folder, and prints a
notice only where a body was present at the previous run and is absent now.
The new-flag direction keeps the commit baseline unchanged.

Three lint runs on one git project: the first with the flag present (the
state file learns it), the second after the fix (the notice prints once), the
third with nothing changed (silence).
"""

import contextlib
import importlib.util
import io
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
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "post_tool_use.py")

failures = []


def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


def load_hook():
    spec = importlib.util.spec_from_file_location("post_tool_use", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(cwd, *args):
    return subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True,
                          text=True, encoding="utf-8")


FLAGGED = """# QUEUE

## Processed

#### Alpha — a cleared build [alpha]
Rationale for alpha.

--- Cleared to run above this line ---

#### Beta — a held build [beta]
Rationale for beta.
Blocked by: [nope]

## Unprocessed

#### Gamma — a capture [gamma]
Rationale for gamma.
"""

FIXED = FLAGGED.replace("Blocked by: [nope]", "Blocked by: [alpha]")


def write_queue(d, text):
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8", newline="") as f:
        f.write(text)


def run_lint(hook, d):
    """One lint run over the project's QUEUE.md, returning the emitted text."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        hook._lint_queue(os.path.join(d, "QUEUE.md"), with_growth=False)
    raw = out.getvalue().strip()
    if not raw:
        return ""
    return json.loads(raw)["hookSpecificOutput"]["additionalContext"]


hook = load_hook()

d = tempfile.mkdtemp(prefix="lint-state-")
git(d, "init", "-q")
git(d, "config", "user.email", "suite@example.invalid")
git(d, "config", "user.name", "suite")
with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
    f.write("# SPEC\n")
write_queue(d, FLAGGED)
git(d, "add", "QUEUE.md", "SPEC.md")
git(d, "commit", "-q", "-m", "a queue with a dangling blocker")

state_path = os.path.join(d, ".throughliner", "queue-lint-last.json")

# Run 1: the flag is present in both commit and working tree. Nothing is new,
# nothing is gone; the state file learns the standing flag.
text1 = run_lint(hook, d)
check("run 1: nothing reported while the flag stands unchanged",
      "gone from the working tree" not in text1, repr(text1))
check("run 1: the state file exists", os.path.isfile(state_path))
with open(state_path, "r", encoding="utf-8") as f:
    state = json.load(f)
check("run 1: the state file carries the standing flag's body",
      any("nope" in body for body in state), repr(state))

# Run 2: the flag is fixed in the working tree, still present in the commit.
write_queue(d, FIXED)
text2 = run_lint(hook, d)
check("run 2: the gone notice prints once the flag clears",
      "gone from the working tree" in text2 and "nope" in text2, repr(text2))
check("run 2: no new flag is reported", "known violations" not in text2,
      repr(text2))

# Run 3: nothing changed since run 2. Against the commit the flag is still
# gone; against the previous run it is not — so silence.
text3 = run_lint(hook, d)
check("run 3: the notice does not repeat on the next tool call",
      "gone from the working tree" not in text3, repr(text3))

# A missing state file means no gone notices that run, and never an error.
os.remove(state_path)
text4 = run_lint(hook, d)
check("no state file: no gone notice, no error",
      "gone from the working tree" not in text4, repr(text4))
check("no state file: the run rewrites it", os.path.isfile(state_path))

# An unreadable state file is treated as missing.
with open(state_path, "w", encoding="utf-8") as f:
    f.write("not json {")
text5 = run_lint(hook, d)
check("unreadable state file: no gone notice, no error",
      "gone from the working tree" not in text5, repr(text5))

shutil.rmtree(d, ignore_errors=True)

print()
if failures:
    print("%d failure(s):" % len(failures))
    for name in failures:
        print("  " + name)
    sys.exit(1)
print("all checks passed")
