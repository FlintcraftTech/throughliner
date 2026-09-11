#!/usr/bin/env python3
"""Regression tests for pre_tool_use.py's checklist `Writes:` field in a BUILD.

Host-only dev artifact — not shipped in the plugin package.

Run:  py workshop/resources/testing/test_pre_tool_use_ritual_writes.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

[ritual-writes-refused-in-build-sessions]: SPEC says a path a checklist
definition declares is permitted whenever the project is open, and the hook
read the field only in the planning branch — the rezip's plugin.json bump was
refused inside a build run. The build branch's allow chain now carries the
same check, after the working file's Files list and before the standing
exemptions, logged under the branch "checklist Writes: field".
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

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "pre_tool_use.py")

SESSION = "checklist-writes-session"
failures = []


def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


def project(cycles=True):
    """A build session: SPEC.md, a working file naming ONE path, and — when
    asked — a CYCLES.md whose checklist declares a different folder."""
    d = tempfile.mkdtemp(prefix="checklist-writes-test-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    with open(os.path.join(d, f"_build-{SESSION}.md"), "w", encoding="utf-8") as f:
        f.write("# Active Build\n\nFiles:\n- src/listed.py\n\nProgress:\n")
    if cycles:
        with open(os.path.join(d, "CYCLES.md"), "w", encoding="utf-8") as f:
            f.write("# CYCLES\n\n## Rezip [rezip]\n\n**Writes:** "
                    "`plugin/rezip-archive/`, `plugin/plugin.json`\n")
    return d


def drive(cwd, filepath):
    payload = {
        "cwd": cwd,
        "tool_name": "Edit",
        "tool_input": {"file_path": filepath, "old_string": "a",
                       "new_string": "b"},
        "session_id": SESSION,
    }
    proc = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                          capture_output=True, text=True, encoding="utf-8")
    if not proc.stdout.strip():
        return {}
    return json.loads(proc.stdout)["hookSpecificOutput"]


def decision(result):
    return result.get("permissionDecision", "allow")


def log_text(d):
    with open(os.path.join(d, ".throughliner", "pre-tool-use.log"),
              encoding="utf-8") as f:
        return f.read()


print("test_pre_tool_use_checklist_writes")

# 1. A build session writing a declared path outside its Files list is allowed,
# and the log line names the branch.
d = project(cycles=True)
declared = os.path.join(d, "plugin", "rezip-archive", "readme.md")
r = drive(d, declared)
check("a declared folder's path is allowed in a build session",
      decision(r) == "allow", repr(r))
check("the decision log names the branch 'checklist Writes: field'",
      "\tallow\tchecklist Writes: field\t" in log_text(d), log_text(d))
r = drive(d, os.path.join(d, "plugin", "plugin.json"))
check("a declared file is allowed too", decision(r) == "allow", repr(r))

# 1b. The Files list still governs: a listed path passes, an unlisted and
# undeclared path is refused.
r = drive(d, os.path.join(d, "src", "listed.py"))
check("a listed path is still allowed", decision(r) == "allow", repr(r))
r = drive(d, os.path.join(d, "src", "other.py"))
check("an unlisted, undeclared path is still refused",
      decision(r) == "deny", repr(r))
shutil.rmtree(d, ignore_errors=True)

# 2. The same write with no cycles doc present is refused.
d = project(cycles=False)
r = drive(d, os.path.join(d, "plugin", "rezip-archive", "readme.md"))
check("the same path with no cycles doc is refused", decision(r) == "deny",
      repr(r))
shutil.rmtree(d, ignore_errors=True)

print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)
