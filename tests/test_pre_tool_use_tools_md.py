#!/usr/bin/env python3
"""Regression tests for pre_tool_use.py's TOOLS.md permission.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_pre_tool_use_tools_md.py

Why this exists ([no-home-for-a-projects-tool-facts]): facts about what a
project has on hand — a tool installed at a known path, a command that fails
specifically from Claude's shell — had no home, so every session re-derived
them or assumed wrong. `TOOLS.md` at the project root is that home, and it is
writable in a planning session and mid-build alike: the moment a session learns
such a fact is the moment it must be written down, and a build whose Files list
does not happen to name TOOLS.md would otherwise be denied.

The two branches of the scope-lock are separate code paths and both have to
permit it, which is what the two end-to-end blocks below pin. The unrelated
cases in each block are the guard: the permission is ONE root-level path, not a
widening of either branch.
"""

import json
import os
import subprocess
import sys
import tempfile

HOOKS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "plugin", "throughliner", "hooks",
)
sys.path.insert(0, HOOKS)

import pre_tool_use  # noqa: E402

HOOK = os.path.join(HOOKS, "pre_tool_use.py")

CWD = os.path.normpath(r"C:\Users\Someone\Projects\My Project") if os.name == "nt" \
    else "/home/someone/projects/My Project"

failures = []

# --- the helper itself -------------------------------------------------------

UNIT = [
    ("TOOLS.md", True, "the file itself"),
    (os.path.join("src", "TOOLS.md"), False,
     "a TOOLS.md in a subfolder is NOT exempted — root-level and exact"),
    ("TOOLS.markdown", False, "a near-miss name is not on the list"),
    ("TOOLSET.md", False, "a longer name that starts the same is not on the list"),
]

for rel, expected, what in UNIT:
    got = pre_tool_use._is_tools_file(os.path.join(CWD, rel), CWD)
    status = "ok" if got == expected else "FAIL"
    if got != expected:
        failures.append((rel, expected, got, what))
    print(f"[{status}] {rel!r} -> {got} ({what})")

# Windows hands the hook paths whose casing differs from the project root's, and
# every other path check in this hook has been broken by exactly that once.
if os.name == "nt":
    for path, expected, what in [
        (CWD.lower() + os.sep + "tools.md", True, "an all-lowercase absolute path"),
        (CWD.upper() + os.sep + "TOOLS.MD", True, "an all-uppercase absolute path"),
        (CWD.lower() + os.sep + "readme.md", False,
         "case-insensitivity must not widen the permission"),
    ]:
        got = pre_tool_use._is_tools_file(path, CWD)
        status = "ok" if got == expected else "FAIL"
        if got != expected:
            failures.append((path, expected, got, what))
        print(f"[{status}] {path!r} -> {got} ({what})")
else:
    print("[skip] mixed-case cases are Windows-only — "
          "normcase is the identity on this platform")


def _decide(cwd, path, session_id="tools-md-test-session"):
    payload = {
        "cwd": cwd,
        "tool_name": "Write",
        "tool_input": {"file_path": path, "content": "x"},
        "session_id": session_id,
    }
    proc = subprocess.run(
        [sys.executable, HOOK], input=json.dumps(payload),
        capture_output=True, text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if not proc.stdout.strip():
        return "pass"
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return "pass"
    return (out.get("hookSpecificOutput") or {}).get("permissionDecision", "pass")


# --- end to end, planning session (no build working file) --------------------

_plan_tmp = tempfile.mkdtemp(prefix="tools-md-plan-")
with open(os.path.join(_plan_tmp, "SPEC.md"), "w", encoding="utf-8") as _f:
    _f.write("# SPEC\n")

for rel, expected, what in [
    ("TOOLS.md", "pass", "TOOLS.md is writable in a planning session"),
    ("README.md", "deny", "an ordinary root file is still denied"),
    (os.path.join("src", "TOOLS.md"), "deny",
     "a nested TOOLS.md is still denied"),
]:
    got = _decide(_plan_tmp, os.path.join(_plan_tmp, rel))
    status = "ok" if got == expected else "FAIL"
    if got != expected:
        failures.append((rel, expected, got, what))
    print(f"[{status}] planning {rel!r} -> {got} ({what})")

# --- end to end, mid-build (a working file whose Files list omits TOOLS.md) ---
#
# The build branch is the one that matters most here: a build learns an
# environment fact while its scope is locked to files chosen before the fact
# existed, so TOOLS.md is never in the list by construction.

_build_session = "tools-md-build-session"
_build_tmp = tempfile.mkdtemp(prefix="tools-md-build-")
with open(os.path.join(_build_tmp, "SPEC.md"), "w", encoding="utf-8") as _f:
    _f.write("# SPEC\n")
with open(
    os.path.join(_build_tmp, f"_build-{_build_session}.md"), "w", encoding="utf-8"
) as _f:
    _f.write("# Active Build\n\nFiles:\n- src/app.py\n")

for rel, expected, what in [
    ("TOOLS.md", "pass", "TOOLS.md is writable mid-build though unlisted"),
    (os.path.join("src", "app.py"), "pass", "a listed file still passes"),
    (os.path.join("src", "other.py"), "deny", "an unlisted file is still denied"),
    (os.path.join("src", "TOOLS.md"), "deny",
     "a nested TOOLS.md is still denied mid-build"),
]:
    got = _decide(_build_tmp, os.path.join(_build_tmp, rel), _build_session)
    status = "ok" if got == expected else "FAIL"
    if got != expected:
        failures.append((rel, expected, got, what))
    print(f"[{status}] build {rel!r} -> {got} ({what})")

print()
if failures:
    print(f"{len(failures)} failure(s):")
    for path, expected, got, what in failures:
        print(f"  {path!r}: expected {expected}, got {got} — {what}")
    sys.exit(1)
print("all cases passed")
