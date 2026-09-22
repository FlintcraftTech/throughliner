#!/usr/bin/env python3
"""Regression tests for session_start.py's naming of a malformed cycles-doc
definition ([malformed-cycle-definition-named-and-refused]).

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_session_start_cycles_malformed.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

A definition carrying neither `Cadence:` nor `Trigger:` used to come back as
a cycle with no cadence, no observable and no trigger — a checklist whose
firing word sat under a label the parser does not read fired nothing, and the
opening reported an empty cycle with nobody told why. The opening now names
it as malformed, and the cycles and checklists lines leave it out.
"""

import importlib.util
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
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "session_start.py")

_spec = importlib.util.spec_from_file_location("session_start", HOOK)
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)

failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        failures.append(name)


DOC = """# CYCLES

## Session prep [prep]

**Steps of one turn.** Each step fires on the one before it.

1. Read the roster.
2. Print the handouts.

**Fires on the word:** the user says "prep".

## Rezip [rezip]

**Trigger:** the user says "rezip".

**Steps of one turn.** Each step fires on the one before it.

1. Install the local build.
"""


def project():
    d = tempfile.mkdtemp(prefix="session-start-malformed-")
    for name in ("SPEC.md", "QUEUE.md"):
        with open(os.path.join(d, name), "w", encoding="utf-8") as f:
            f.write("# " + name + "\n\n## Processed\n\n## Unprocessed\n"
                    if name == "QUEUE.md" else "# SPEC\n")
    with open(os.path.join(d, "CYCLES.md"), "w", encoding="utf-8") as f:
        f.write(DOC)
    return d


d = project()
check("the Fires-on-the-word definition is named as malformed",
      hook.malformed_definitions(d) == ["prep"],
      repr(hook.malformed_definitions(d)))
check("the checklist carrying Trigger: is a checklist",
      [s for s, _, _ in hook.checklists_facts(d)] == ["rezip"],
      repr(hook.checklists_facts(d)))
check("the malformed definition is not reported as a cycle",
      hook.cycles_facts(d) == [], repr(hook.cycles_facts(d)))
check("a project with no cycles doc has nothing malformed",
      hook.malformed_definitions(tempfile.mkdtemp(prefix="no-doc-")) is None)

# Driven whole: the opening's context names the malformed slug and both
# field names, and the checklists line names the well-formed one.
proc = subprocess.run(
    [sys.executable, HOOK],
    input=json.dumps({"cwd": d, "session_id": "malformed-test"}),
    capture_output=True, text=True, encoding="utf-8", cwd=d, timeout=120)
context = ""
try:
    out = json.loads(proc.stdout) if proc.stdout.strip() else {}
    context = (out.get("hookSpecificOutput") or {}).get("additionalContext") \
        or out.get("additionalContext") or ""
except ValueError:
    context = proc.stdout
check("the opening names [prep] as carrying neither field",
      "[prep]" in context and "neither a Cadence: line nor a Trigger: line"
      in context, context[-1500:])
check("the opening names cycle_define as what writes the field",
      "cycle_define" in context, context[-800:])
check("the checklists line carries [rezip] and not [prep]",
      "Checklists on file (1): [rezip]" in context, context[-1500:])
shutil.rmtree(d, ignore_errors=True)

print()
if failures:
    print("%d failure(s):" % len(failures))
    for name in failures:
        print("  " + name)
    sys.exit(1)
print("all cases passed")
