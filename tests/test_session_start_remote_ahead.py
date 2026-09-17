#!/usr/bin/env python3
"""session_start.py's remote-ahead line: where the checkout's upstream has
commits it does not, one fact line says so and nothing pulls.

Run: py tests/test_session_start_remote_ahead.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

Why this exists ([merge-conflicts-unhandled]): nothing told a session the
other person had pushed, so the push was discovered when its own push failed.
The fixture is a bare "remote" on disk, a clone with an upstream, and a second
clone that pushes one commit — so the first clone's remote is genuinely ahead.
"""

import importlib.util
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

failures = []


def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label
          + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


def load_hook():
    spec = importlib.util.spec_from_file_location("session_start", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True,
                          text=True, encoding="utf-8", timeout=30)


def fixture(td):
    """remote (bare), mine (a clone), theirs (a clone that pushes once)."""
    remote = os.path.join(td, "remote.git")
    git(td, "init", "-q", "--bare", "--initial-branch=main", remote)
    theirs = os.path.join(td, "theirs")
    git(td, "clone", "-q", remote, theirs)
    git(theirs, "config", "user.email", "suite@example.invalid")
    git(theirs, "config", "user.name", "Suite")
    git(theirs, "checkout", "-q", "-b", "main")
    with open(os.path.join(theirs, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    git(theirs, "add", "SPEC.md")
    git(theirs, "commit", "-q", "-m", "seed")
    git(theirs, "push", "-q", "-u", "origin", "main")
    mine = os.path.join(td, "mine")
    git(td, "clone", "-q", remote, mine)
    return remote, mine, theirs


def test_remote_ahead_is_reported_and_nothing_pulls():
    hook = load_hook()
    td = tempfile.mkdtemp(prefix="remote-ahead-")
    try:
        remote, mine, theirs = fixture(td)
        check("nothing ahead reads as None", hook._remote_ahead(mine) is None)
        with open(os.path.join(theirs, "QUEUE.md"), "w", encoding="utf-8") as f:
            f.write("# QUEUE\n")
        git(theirs, "add", "QUEUE.md")
        git(theirs, "commit", "-q", "-m", "their push")
        git(theirs, "push", "-q")
        ahead = hook._remote_ahead(mine)
        check("one commit ahead is reported with the upstream's name",
              ahead is not None and ahead[1] == 1 and "origin/main" in ahead[0],
              repr(ahead))
        check("nothing was pulled", not os.path.exists(os.path.join(mine, "QUEUE.md")))
        lines = hook._remote_ahead_lines(mine)
        check("the opening's line says pull before working the queue",
              len(lines) == 1 and "pull before working the queue" in lines[0]
              and "1 commit " in lines[0], repr(lines))
    finally:
        shutil.rmtree(td, ignore_errors=True)


def test_no_remote_is_silent():
    hook = load_hook()
    td = tempfile.mkdtemp(prefix="remote-ahead-")
    try:
        git(td, "init", "-q")
        check("a repository with no upstream reads as None",
              hook._remote_ahead(td) is None)
        check("and prints no line", hook._remote_ahead_lines(td) == [])
    finally:
        shutil.rmtree(td, ignore_errors=True)


if __name__ == "__main__":
    print("test_session_start_remote_ahead")
    test_remote_ahead_is_reported_and_nothing_pulls()
    test_no_remote_is_silent()
    print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
    sys.exit(1 if failures else 0)
