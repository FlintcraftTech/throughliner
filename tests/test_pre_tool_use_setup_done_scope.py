#!/usr/bin/env python3
"""Regression test for pre_tool_use.py's setup-done close scope.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_pre_tool_use_setup_done_scope.py

Why this exists ([setup-close-cannot-fix-setup-output]): a consumer's first
/done run, in the same chat as a completed setup, found two corrections to
what setup had just written and the standing list refused both — the setup
marker had been deleted at the run's end, so the close ran as an ordinary
no-build session. Setup now RENAMES its marker to `.throughliner-setup-done`;
while that stands together with the close marker, the close may write the
scaffolded set.

Two assertions: both markers present, an Edit to CLAUDE.md is allowed; only
the setup-done marker (a planning run before the close), the same Edit is
refused.
"""

import json
import os
import subprocess
import sys
import tempfile

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = os.path.join(ROOT, "plugin", "throughliner", "hooks")
HOOK = os.path.join(HOOKS, "pre_tool_use.py")
sys.path.insert(0, HOOKS)
import pre_tool_use  # noqa: E402

SESSION = "setup-done-scope-test-session"
_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("  -- " + detail if detail else ""))
        _failures.append(name)


def make_project():
    d = tempfile.mkdtemp(prefix="setup-done-test-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    with open(os.path.join(d, "CLAUDE.md"), "w", encoding="utf-8") as f:
        f.write("# CLAUDE\n")
    return d


def drive_edit(cwd, filepath, session=SESSION):
    payload = {"cwd": cwd, "tool_name": "Edit",
               "tool_input": {"file_path": filepath}, "session_id": session}
    proc = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                          capture_output=True, text=True, encoding="utf-8")
    if not proc.stdout.strip():
        return "allow"
    return json.loads(proc.stdout)["hookSpecificOutput"].get("permissionDecision", "allow")


def main():
    print("setup-done close scope:")
    scratch = os.path.join(tempfile.gettempdir(), "claude", "setup-done-test-project",
                           SESSION, "scratchpad")
    os.makedirs(scratch, exist_ok=True)
    done_marker = os.path.join(scratch, pre_tool_use.SETUP_DONE_MARKER_NAME)
    if os.path.exists(done_marker):
        os.remove(done_marker)

    d = make_project()
    # The close marker lives in the project's own working folder since
    # [scratchpad-refused-after-resume-close-marker]; the setup-done marker
    # stays in the scratchpad.
    os.makedirs(os.path.join(d, ".throughliner"), exist_ok=True)
    close_marker = os.path.join(d, ".throughliner",
                                pre_tool_use.CLOSE_MARKER_PREFIX + SESSION)
    claude_md = os.path.join(d, "CLAUDE.md")
    gitignore = os.path.join(d, ".gitignore")
    part_spec = os.path.join(d, "part", "SPEC.md")
    other = os.path.join(d, "src", "app.py")

    check("no markers: CLAUDE.md refused", drive_edit(d, claude_md) == "deny")

    with open(done_marker, "w", encoding="utf-8") as f:
        f.write("")
    check("setup-done marker alone (a planning run before the close): refused",
          drive_edit(d, claude_md) == "deny")

    with open(close_marker, "w", encoding="utf-8") as f:
        f.write("")
    check("both markers: CLAUDE.md allowed", drive_edit(d, claude_md) == "allow")
    check("both markers: .gitignore allowed", drive_edit(d, gitignore) == "allow")
    check("both markers: a part's SPEC.md allowed", drive_edit(d, part_spec) == "allow")
    check("both markers: a file setup never scaffolds is still refused",
          drive_edit(d, other) == "deny")
    check("both markers, another session: refused",
          drive_edit(d, claude_md, session="some-other-session") == "deny")

    os.remove(done_marker)
    check("close marker alone: CLAUDE.md refused as before",
          drive_edit(d, claude_md) == "deny")
    os.remove(close_marker)

    # Setup no longer renames its active marker; it writes the done marker
    # beside it ([setup-done-marker-rename-fails-in-powershell]). With BOTH
    # setup markers standing, the setup-run door is closed: a scaffold write
    # outside the standing list is refused as in a planning session, and the
    # /done run's correction is still allowed once the close marker joins.
    active_marker = os.path.join(scratch, pre_tool_use.SETUP_MARKER_NAME)
    for m in (active_marker, done_marker):
        with open(m, "w", encoding="utf-8") as f:
            f.write("")
    check("active + done markers: the setup door is closed, CLAUDE.md refused",
          drive_edit(d, claude_md) == "deny")
    check("active + done markers: a file setup never scaffolds is refused",
          drive_edit(d, other) == "deny")
    with open(close_marker, "w", encoding="utf-8") as f:
        f.write("")
    check("active + done + close markers: the close's correction still allowed",
          drive_edit(d, claude_md) == "allow")
    os.remove(close_marker)
    os.remove(done_marker)
    check("active marker alone: the setup door is open, CLAUDE.md allowed",
          drive_edit(d, claude_md) == "allow")
    os.remove(active_marker)

    if _failures:
        print(f"\n{len(_failures)} FAILURE(S)")
        return 1
    print("\nall passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
