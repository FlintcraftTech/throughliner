#!/usr/bin/env python3
"""pre_tool_use.py refuses a `git commit` while a tracked file carries a
git conflict marker, naming the file — bare, and `git -C <inner> commit`.

Run: py tests/test_pre_tool_use_conflict_markers.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

Why this exists ([merge-conflicts-unhandled]): nothing checked for markers
before a commit, so /close would have committed a half-merged queue clean.
Each case builds a temp git repository, drives the hook as a subprocess with
a real PreToolUse payload, and asserts on the decision that comes back.
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

failures = []


def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label
          + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True,
                          text=True, encoding="utf-8", timeout=30)


def repo(td, conflicted):
    """A git repository with SPEC.md (adopted) and one tracked file, which
    carries conflict markers where `conflicted`."""
    git(td, "init", "-q")
    git(td, "config", "user.email", "suite@example.invalid")
    git(td, "config", "user.name", "Suite")
    with open(os.path.join(td, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    with open(os.path.join(td, "QUEUE.md"), "w", encoding="utf-8") as f:
        f.write("# QUEUE\n\n## Processed\n\n## Unprocessed\n")
    git(td, "add", "SPEC.md", "QUEUE.md")
    git(td, "commit", "-q", "-m", "seed")
    if conflicted:
        with open(os.path.join(td, "QUEUE.md"), "a", encoding="utf-8") as f:
            f.write("<<<<<<< HEAD\n#### Mine [mine]\nR.\n=======\n"
                    "#### Theirs [theirs]\nR.\n>>>>>>> origin/main\n")


def decision(cwd, command):
    payload = {"cwd": cwd, "tool_name": "Bash",
               "tool_input": {"command": command},
               "session_id": "conflict-suite"}
    proc = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                          capture_output=True, text=True, encoding="utf-8",
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    if not proc.stdout.strip():
        return "pass", ""
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return "pass", proc.stdout
    hso = out.get("hookSpecificOutput") or {}
    return hso.get("permissionDecision", "pass"), hso.get("permissionDecisionReason", "")


def test_bare_commit_is_refused_while_a_tracked_file_is_conflicted():
    td = tempfile.mkdtemp(prefix="conflict-suite-")
    try:
        repo(td, conflicted=True)
        d, reason = decision(td, 'git add QUEUE.md && git commit -m "x"')
        check("a commit over a conflicted tracked file is denied",
              d == "deny" and "conflict marker" in reason, f"{d}: {reason[:200]}")
        check("the refusal names the file", "QUEUE.md" in reason, reason[:200])
    finally:
        shutil.rmtree(td, ignore_errors=True)


def test_commit_in_an_inner_repository_is_read_there():
    td = tempfile.mkdtemp(prefix="conflict-suite-")
    try:
        repo(td, conflicted=False)
        inner = os.path.join(td, "product")
        os.makedirs(inner)
        repo(inner, conflicted=True)
        d, reason = decision(td, 'git -C product commit -m "x"')
        check("git -C <inner> commit reads the inner repository",
              d == "deny" and "conflict marker" in reason, f"{d}: {reason[:200]}")
        d, reason = decision(td, 'git commit -m "x"')
        check("the outer, clean, is not refused for the inner's conflict",
              d != "deny", f"{d}: {reason[:200]}")
    finally:
        shutil.rmtree(td, ignore_errors=True)


def test_clean_repository_commits():
    td = tempfile.mkdtemp(prefix="conflict-suite-")
    try:
        repo(td, conflicted=False)
        d, reason = decision(td, 'git commit -m "x"')
        check("a clean repository's commit is not refused", d != "deny",
              f"{d}: {reason[:200]}")
    finally:
        shutil.rmtree(td, ignore_errors=True)


if __name__ == "__main__":
    print("test_pre_tool_use_conflict_markers")
    test_bare_commit_is_refused_while_a_tracked_file_is_conflicted()
    test_commit_in_an_inner_repository_is_read_there()
    test_clean_repository_commits()
    print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
    sys.exit(1 if failures else 0)
