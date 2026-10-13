#!/usr/bin/env python3
"""Regression tests for pre_tool_use.py's writes outside the project.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_pre_tool_use_task_list.py

Why this exists: the one permitted write outside a project root is the user's
global instructions file, CLAUDE.md in the home `.claude` folder
([user-facts-to-global-instructions]): an Edit asks the user in planning and
mid-build alike ([global-instructions-write-gated-by-procedure-only]), a
Write over an existing file is refused, and another file in the home folder
stays denied.

The task-list permission this suite once pinned — any edit to the file a
project's `Task list:` line names — was retired 2026-10-12
([user-task-line-lives-in-queue-with-tasks-marks]): a task line lives in its
own queue item, and the `Task list:` line now names the user's query note,
which no session writes. Pinned here: a write to that named file is an
ordinary outside write and is denied, in planning and mid-build.
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
HOOK = os.path.join(HOOKS, "pre_tool_use.py")

failures = []


def _check(label, got, expected, what):
    status = "ok" if got == expected else "FAIL"
    if got != expected:
        failures.append((label, expected, got, what))
    print(f"[{status}] {label} -> {got!r} ({what})")


_root = tempfile.mkdtemp(prefix="task-list-root-")
_outside = tempfile.mkdtemp(prefix="task-list-outside-")
LIST = os.path.join(_outside, "Tasks.md")
with open(os.path.join(_root, "SPEC.md"), "w", encoding="utf-8") as f:
    f.write("# SPEC\n")
with open(os.path.join(_root, "CLAUDE.md"), "w", encoding="utf-8") as f:
    f.write(f"# CLAUDE.md\n\nTask list: {LIST}\n")
with open(LIST, "w", encoding="utf-8") as f:
    f.write("# Tasks\n\n```tasks\nnot done\n```\n")

_home = tempfile.mkdtemp(prefix="task-list-home-")
os.makedirs(os.path.join(_home, ".claude"))
GLOBAL = os.path.join(_home, ".claude", "CLAUDE.md")
with open(GLOBAL, "w", encoding="utf-8") as f:
    f.write("# Global instructions\n\nI'm Sam.\n")
_home_env = {"USERPROFILE": _home, "HOME": _home}


def _decide(cwd, tool_name, tool_input, session_id="task-list-test-session"):
    payload = {"cwd": cwd, "tool_name": tool_name, "tool_input": tool_input,
               "session_id": session_id}
    proc = subprocess.run(
        [sys.executable, HOOK], input=json.dumps(payload),
        capture_output=True, text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **_home_env},
    )
    if not proc.stdout.strip():
        return "pass"
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return "pass"
    return (out.get("hookSpecificOutput") or {}).get("permissionDecision", "pass")


# --- the query note the Task list: line names is not written ----------------
APPEND = {"file_path": LIST, "old_string": "not done\n",
          "new_string": "not done\n- [ ] second (Demo)\n"}
REWRITE = {"file_path": LIST, "content": "# Tasks\n"}

_check("planning edit of the query note", _decide(_root, "Edit", APPEND), "deny",
       "the file the Task list: line names is an ordinary outside write")
_check("planning rewrite of the query note", _decide(_root, "Write", REWRITE),
       "deny", "a Write there is refused too")

_sid = "task-list-build-session"
with open(os.path.join(_root, f"_build-{_sid}.md"), "w", encoding="utf-8") as f:
    f.write("# Active Build\n\nFiles:\n- src/app.py\n")
_check("build edit of the query note", _decide(_root, "Edit", APPEND, _sid),
       "deny", "mid-build the same edit is refused")

# --- the global instructions file ([user-facts-to-global-instructions]) --------
GLOBAL_EDIT = {"file_path": GLOBAL, "old_string": "I'm Sam.\n",
               "new_string": "I'm Sam.\nMy timezone is UTC.\n"}
GLOBAL_REWRITE = {"file_path": GLOBAL, "content": "# Global instructions\n"}
HOME_OTHER = {"file_path": os.path.join(_home, ".claude", "settings.json"),
              "old_string": "a", "new_string": "b"}

_check("global edit, planning", _decide(_root, "Edit", GLOBAL_EDIT), "ask",
       "an edit to the global instructions file asks the user in a planning session")
_check("global rewrite, planning", _decide(_root, "Write", GLOBAL_REWRITE),
       "deny", "a whole-file Write over the existing global file is refused")
_check("other home file, planning", _decide(_root, "Edit", HOME_OTHER), "deny",
       "another file in the home .claude folder is refused as before")
_check("global edit, build", _decide(_root, "Edit", GLOBAL_EDIT, _sid), "ask",
       "an edit to the global instructions file asks the user mid-build")
_check("global rewrite, build", _decide(_root, "Write", GLOBAL_REWRITE, _sid),
       "deny", "a whole-file Write over the existing global file is refused mid-build")
_check("other home file, build", _decide(_root, "Edit", HOME_OTHER, _sid), "deny",
       "another file in the home .claude folder is refused mid-build")

print()
if failures:
    print(f"{len(failures)} failure(s):")
    for label, expected, got, what in failures:
        print(f"  {label}: expected {expected!r}, got {got!r} — {what}")
    sys.exit(1)
print("all cases passed")
