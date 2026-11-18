#!/usr/bin/env python3
"""Tests for pre_tool_use.py's handling of the user's cross-project memory.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_pre_tool_use_user_memory.py

Why this exists ([memory-setup-skill-user-memory-across-projects]): the
memory-setup skill builds one memory about the user in `~/.claude/memory/`,
outside every project, and any chat may later add or correct a note there.
The safety check admits a path by shape, a `memory` folder beneath a `.claude`
folder, so a note is writable in a session with no build and in a build run
whose working file does not list it; the import line the skill adds to the
global instructions file still asks the user. Pinned too: the skill's own name
is one of the method's commands, which Claude never starts by itself.
"""

import json
import os
import subprocess
import sys
import tempfile

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

HOOKS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "plugin", "throughliner", "hooks",
)
HOOK = os.path.join(HOOKS, "pre_tool_use.py")

failures = []


def check(label, got, expected):
    ok = got == expected
    print("  %s %s -> %r" % ("ok  " if ok else "FAIL", label, got))
    if not ok:
        failures.append("%s (expected %r, got %r)" % (label, expected, got))


root = tempfile.mkdtemp(prefix="user-memory-root-")
with open(os.path.join(root, "SPEC.md"), "w", encoding="utf-8") as f:
    f.write("# SPEC\n")
with open(os.path.join(root, "QUEUE.md"), "w", encoding="utf-8") as f:
    f.write("# QUEUE\n\n## Processed\n\n## Unprocessed\n")

home = tempfile.mkdtemp(prefix="user-memory-home-")
memory = os.path.join(home, ".claude", "memory")
os.makedirs(memory)
GLOBAL = os.path.join(home, ".claude", "CLAUDE.md")
with open(GLOBAL, "w", encoding="utf-8") as f:
    f.write("# Global instructions\n")
NOTE = os.path.join(memory, "pronouns.md")
INDEX = os.path.join(memory, "MEMORY.md")
home_env = {"USERPROFILE": home, "HOME": home}


def decide(tool_name, tool_input, session_id):
    payload = {"cwd": root, "tool_name": tool_name, "tool_input": tool_input,
               "session_id": session_id}
    proc = subprocess.run(
        [sys.executable, HOOK], input=json.dumps(payload),
        capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **home_env},
    )
    if not proc.stdout.strip():
        return "pass"
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return "pass"
    return (out.get("hookSpecificOutput") or {}).get("permissionDecision", "pass")


print("test_pre_tool_use_user_memory")

# A session with no build running.
check("no build: Write a note in ~/.claude/memory/",
      decide("Write", {"file_path": NOTE, "content": "x"}, "mem-plain"), "pass")
check("no build: Write the index",
      decide("Write", {"file_path": INDEX, "content": "x"}, "mem-plain"), "pass")
check("no build: Edit the global instructions file still asks",
      decide("Edit", {"file_path": GLOBAL, "old_string": "# Global instructions",
                      "new_string": "# Global instructions\n@~/.claude/memory/MEMORY.md"},
             "mem-plain"), "ask")
check("no build: another file in the home .claude folder is not admitted",
      decide("Write", {"file_path": os.path.join(home, ".claude", "settings.json"),
                       "content": "{}"}, "mem-plain") != "pass", True)

# A build run whose working file does not list the note.
with open(os.path.join(root, "_build-mem-build.md"), "w", encoding="utf-8") as f:
    f.write("# Active Build\n\nRun: build alpha\n\nFiles:\n- product.md\n\nProgress:\n")
check("build run: Write a note the working file does not list",
      decide("Write", {"file_path": NOTE, "content": "x"}, "mem-build"), "pass")
check("build run: Edit the global instructions file still asks",
      decide("Edit", {"file_path": GLOBAL, "old_string": "a", "new_string": "b"},
             "mem-build"), "ask")
os.remove(os.path.join(root, "_build-mem-build.md"))

# The skill is the user's to type.
check("Skill throughliner:memory-setup is refused as a method command",
      decide("Skill", {"skill": "throughliner:memory-setup"}, "mem-plain"), "deny")

print()
if failures:
    print("%d check(s) FAILED:" % len(failures))
    for line in failures:
        print("  " + line)
    sys.exit(1)
print("all checks passed")
