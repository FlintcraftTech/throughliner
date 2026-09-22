#!/usr/bin/env python3
"""Regression tests for pre_tool_use.py's refusal of a malformed cycles-doc
definition at the write ([malformed-cycle-definition-named-and-refused]).

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_pre_tool_use_cycles_write.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

A definition written into CYCLES.md carrying neither `Cadence:` nor
`Trigger:` is refused, naming the slug, both field names and the
cycle_define tool. The refusal reaches the definition the call writes or
changes, by comparing the doc before and after: one already there and left
untouched is not refused for it.
"""

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
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "pre_tool_use.py")

SESSION = "cycles-write-session"
failures = []


def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


def project(cycles_doc=None):
    d = tempfile.mkdtemp(prefix="cycles-write-test-")
    for name in ("SPEC.md", "QUEUE.md"):
        with open(os.path.join(d, name), "w", encoding="utf-8") as f:
            f.write("# " + name + "\n")
    os.makedirs(os.path.join(d, "LOG"))
    if cycles_doc is not None:
        with open(os.path.join(d, "CYCLES.md"), "w", encoding="utf-8") as f:
            f.write(cycles_doc)
    return d


def drive(cwd, tool_name, tool_input):
    payload = {
        "cwd": cwd,
        "tool_name": tool_name,
        "tool_input": dict(tool_input, file_path=os.path.join(cwd, "CYCLES.md")),
        "session_id": SESSION,
    }
    proc = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                          capture_output=True, text=True, encoding="utf-8")
    if not proc.stdout.strip():
        return {}
    return json.loads(proc.stdout)["hookSpecificOutput"]


def decision(result):
    return result.get("permissionDecision", "allow")


MALFORMED = """# CYCLES

## Session prep [prep]

**Steps of one turn.** Each step fires on the one before it.

1. Read the roster.

**Fires on the word:** the user says "prep".
"""

WELL_FORMED = MALFORMED.replace("**Fires on the word:**", "**Trigger:**")

ADDED = """
## Rezip [rezip]

**Trigger:** the user says "rezip".

1. Install the local build.
"""


def main():
    print("test_pre_tool_use_cycles_write")

    # 1. A Write of a doc holding a Fires-on-the-word definition is refused,
    #    naming the slug and the tool.
    d = project()
    r = drive(d, "Write", {"content": MALFORMED})
    reason = r.get("permissionDecisionReason", "")
    check("a Write carrying a definition with neither field is refused",
          decision(r) == "deny", repr(r))
    check("the refusal names the slug", "[prep]" in reason, reason)
    check("the refusal names both field names and cycle_define",
          "`Cadence:`" in reason and "`Trigger:`" in reason
          and "cycle_define" in reason, reason)
    check("nothing was written", not os.path.exists(os.path.join(d, "CYCLES.md")))
    shutil.rmtree(d, ignore_errors=True)

    # 2. The same doc with Trigger: is allowed.
    d = project()
    r = drive(d, "Write", {"content": WELL_FORMED})
    check("a Write of the same doc with Trigger: is allowed",
          decision(r) == "allow", repr(r))
    shutil.rmtree(d, ignore_errors=True)

    # 3. An Edit adding a well-formed definition beside a pre-existing
    #    malformed one is allowed — the refusal reaches what the call writes.
    d = project(MALFORMED)
    r = drive(d, "Edit", {"old_string": 'the user says "prep".\n',
                          "new_string": 'the user says "prep".\n' + ADDED})
    check("an Edit adding a well-formed definition beside an untouched "
          "malformed one is allowed", decision(r) == "allow", repr(r))

    # 4. An Edit that changes the malformed definition without mending it is
    #    refused for it.
    r = drive(d, "Edit", {"old_string": "1. Read the roster.",
                          "new_string": "1. Read the roster.\n2. Print handouts."})
    check("an Edit touching the malformed definition without a field is refused",
          decision(r) == "deny" and "[prep]" in r.get("permissionDecisionReason", ""),
          repr(r))

    # 5. An Edit that mends it passes.
    r = drive(d, "Edit", {"old_string": "**Fires on the word:**",
                          "new_string": "**Trigger:**"})
    check("an Edit that adds the Trigger: field is allowed",
          decision(r) == "allow", repr(r))
    shutil.rmtree(d, ignore_errors=True)

    print()
    if failures:
        print("%d failure(s):" % len(failures))
        for name in failures:
            print("  " + name)
        return 1
    print("all cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
