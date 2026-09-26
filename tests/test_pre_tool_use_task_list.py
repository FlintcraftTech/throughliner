#!/usr/bin/env python3
"""Regression tests for pre_tool_use.py's task-list permission.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_pre_tool_use_task_list.py

Why this exists ([task-list-above-projects]): a project's own CLAUDE.md may
carry one line, `Task list: <absolute path>`, naming the user's one markdown
task list above every project. Planning appends a checkbox line there when it
keeps a task-shaped [user] item. It is the one permitted write outside the
project root, and it is APPEND-ONLY — the person edits the file by hand in
their notes app, so Claude never removes or reorders a line.

Pinned here: the line is read from CLAUDE.md and only an absolute path opens
the permission; the path matches exactly; an append passes in a planning
session and mid-build alike; a rewrite is refused in both; and an unrelated
path outside the project is still denied, so the permission is one file and
not a widening of either scope branch.
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

failures = []


def _check(label, got, expected, what):
    status = "ok" if got == expected else "FAIL"
    if got != expected:
        failures.append((label, expected, got, what))
    print(f"[{status}] {label} -> {got!r} ({what})")


# --- the readers themselves ---------------------------------------------------

_root = tempfile.mkdtemp(prefix="task-list-root-")
_outside = tempfile.mkdtemp(prefix="task-list-outside-")
LIST = os.path.join(_outside, "Tasks.md")


def _write_claude(text):
    with open(os.path.join(_root, "CLAUDE.md"), "w", encoding="utf-8") as f:
        f.write(text)


_check("no CLAUDE.md", pre_tool_use._task_list_path(_root), "",
       "a project with no CLAUDE.md names no list")

_write_claude("# CLAUDE.md\n\nVisibility: flat\n")
_check("no line", pre_tool_use._task_list_path(_root), "",
       "a CLAUDE.md with no Task list: line names no list")

_write_claude("# CLAUDE.md\n\nTask list:\n\n<!-- a comment on the next line -->\n")
_check("blank line", pre_tool_use._task_list_path(_root), "",
       "a blank Task list: line names no list and does not read the next line")

_write_claude("# CLAUDE.md\n\nTask list: notes/Tasks.md\n")
_check("relative path", pre_tool_use._task_list_path(_root), "",
       "a relative path names no list — setup refuses to write one")

_write_claude(f"# CLAUDE.md\n\nTask list: {LIST}\n")
_check("absolute path", pre_tool_use._task_list_path(_root), LIST,
       "the absolute path is read back as written")
_check("the file itself", pre_tool_use._is_task_list_file(LIST, _root), True,
       "the named file matches")
_check("a sibling", pre_tool_use._is_task_list_file(
    os.path.join(_outside, "Other.md"), _root), False,
    "a sibling file outside the project does not match")

# --- append or not --------------------------------------------------------------

_check("Write, no file", pre_tool_use._is_task_list_append(
    "Write", {"content": "# Tasks\n"}, LIST), True,
    "a Write creating the list is an append")
with open(LIST, "w", encoding="utf-8") as f:
    f.write("# Tasks\n- [ ] first (Demo)\n")
_check("Write, existing", pre_tool_use._is_task_list_append(
    "Write", {"content": "# Tasks\n"}, LIST), False,
    "a Write over an existing list is a rewrite")
_check("Edit append", pre_tool_use._is_task_list_append(
    "Edit", {"old_string": "- [ ] first (Demo)\n",
             "new_string": "- [ ] first (Demo)\n- [ ] second (Demo)\n"}, LIST),
    True, "new text beginning with the old text is an append")
_check("Edit reword", pre_tool_use._is_task_list_append(
    "Edit", {"old_string": "- [ ] first (Demo)\n",
             "new_string": "- [ ] FIRST (Demo)\n"}, LIST),
    False, "new text not beginning with the old text is a rewrite")
_check("Edit remove", pre_tool_use._is_task_list_append(
    "Edit", {"old_string": "- [ ] first (Demo)\n", "new_string": ""}, LIST),
    False, "an empty replacement removes a line")
_check("Edit empty old", pre_tool_use._is_task_list_append(
    "Edit", {"old_string": "", "new_string": "- [ ] x\n"}, LIST),
    False, "an empty anchor is not an append the hook can read")


# --- end to end ------------------------------------------------------------------

def _decide(cwd, tool_name, tool_input, session_id="task-list-test-session"):
    payload = {
        "cwd": cwd,
        "tool_name": tool_name,
        "tool_input": tool_input,
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


APPEND = {"file_path": LIST, "old_string": "- [ ] first (Demo)\n",
          "new_string": "- [ ] first (Demo)\n- [ ] second (Demo)\n"}
REWRITE = {"file_path": LIST, "content": "# Tasks\n"}
OTHER = {"file_path": os.path.join(_outside, "Other.md"), "content": "x"}

# planning session: SPEC.md present, no build working file
with open(os.path.join(_root, "SPEC.md"), "w", encoding="utf-8") as f:
    f.write("# SPEC\n")

_check("planning append", _decide(_root, "Edit", APPEND), "pass",
       "an append to the task list passes in a planning session")
_check("planning rewrite", _decide(_root, "Write", REWRITE), "deny",
       "a rewrite of the task list is refused in a planning session")
_check("planning other outside", _decide(_root, "Write", OTHER), "deny",
       "an unrelated file outside the project is still denied")

# mid-build: a working file whose Files list omits the task list
_sid = "task-list-build-session"
with open(os.path.join(_root, f"_build-{_sid}.md"), "w", encoding="utf-8") as f:
    f.write("# Active Build\n\nFiles:\n- src/app.py\n")

_check("build append", _decide(_root, "Edit", APPEND, _sid), "pass",
       "an append to the task list passes mid-build though unlisted")
_check("build rewrite", _decide(_root, "Write", REWRITE, _sid), "deny",
       "a rewrite of the task list is refused mid-build")
_check("build other outside", _decide(_root, "Write", OTHER, _sid), "deny",
       "an unrelated file outside the project is still denied mid-build")

# no line at all: the same append is an ordinary outside write and is denied
_write_claude("# CLAUDE.md\n")
_check("no line, planning append", _decide(_root, "Edit", APPEND), "deny",
       "with no Task list: line the permission never opens")

print()
if failures:
    print(f"{len(failures)} failure(s):")
    for label, expected, got, what in failures:
        print(f"  {label}: expected {expected!r}, got {got!r} — {what}")
    sys.exit(1)
print("all cases passed")
