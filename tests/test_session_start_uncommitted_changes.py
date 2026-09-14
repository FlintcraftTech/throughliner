#!/usr/bin/env python3
"""Regression tests for how session_start.py reports uncommitted changes.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_session_start_uncommitted_changes.py

No test framework, matching the suites alongside it: this project has no test
runner, and `python` on the author's machine resolves to an application's
bundled interpreter that has no pytest.

What this pins is the difference between a change the hook can explain and one
it cannot. The hash backfill runs by itself at every session start, so its
changes are the most common thing in a dirty tree — and lumping them into a
bare count made an opening report a number nobody could interpret.

These build real git repositories in a temp folder, because the thing under
test reads `git status` and `git diff`.
"""

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "session_start.py")

_spec = importlib.util.spec_from_file_location("session_start", HOOK)
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)

_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        _failures.append(name)


def git(cwd, *args):
    subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True,
                   text=True, encoding="utf-8", errors="replace", timeout=30)


def repo():
    d = tempfile.mkdtemp(prefix="session-start-dirty-")
    git(d, "init")
    git(d, "config", "user.email", "test@example.invalid")
    git(d, "config", "user.name", "Test")
    os.makedirs(os.path.join(d, "LOG"))
    return d


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


ENTRY_PLACEHOLDER = "# [HASH] — A session entry\n\nBody prose.\n"
ENTRY_FILLED = "# a1b2c3d — A session entry\n\nBody prose.\n"
INDEX_PLACEHOLDER = "# Index\n\n- [HASH] — A session entry — entry.md\n"
INDEX_FILLED = "# Index\n\n- a1b2c3d — A session entry — entry.md\n"


def test_a_pure_backfill_is_recognised():
    d = repo()
    write(os.path.join(d, "LOG", "entry.md"), ENTRY_PLACEHOLDER)
    write(os.path.join(d, "LOG", "index.md"), INDEX_PLACEHOLDER)
    git(d, "add", "-A")
    git(d, "commit", "-m", "first")
    write(os.path.join(d, "LOG", "entry.md"), ENTRY_FILLED)
    write(os.path.join(d, "LOG", "index.md"), INDEX_FILLED)

    paths = hook._dirty_paths(d)
    backfilled = [p for p in paths if p.startswith("LOG/")
                  and hook._is_hash_backfill_diff(d, p)]
    shutil.rmtree(d, ignore_errors=True)
    check("both changed LOG files are read as dirty",
          sorted(paths) == ["LOG/entry.md", "LOG/index.md"], repr(paths))
    check("both are recognised as the hash backfill",
          sorted(backfilled) == ["LOG/entry.md", "LOG/index.md"],
          repr(backfilled))


def test_a_real_edit_in_the_same_file_fails_back_to_the_count():
    """The safe direction: anything beyond a filled hash is not the backfill."""
    d = repo()
    write(os.path.join(d, "LOG", "entry.md"), ENTRY_PLACEHOLDER)
    git(d, "add", "-A")
    git(d, "commit", "-m", "first")
    write(os.path.join(d, "LOG", "entry.md"),
          "# a1b2c3d — A session entry\n\nBody prose, rewritten by hand.\n")

    d2 = repo()
    write(os.path.join(d2, "LOG", "entry.md"), ENTRY_PLACEHOLDER)
    git(d2, "add", "-A")
    git(d2, "commit", "-m", "first")
    write(os.path.join(d2, "LOG", "entry.md"),
          "# [HASH] — A session entry retitled\n\nBody prose.\n")

    edited = hook._is_hash_backfill_diff(d, "LOG/entry.md")
    retitled = hook._is_hash_backfill_diff(d2, "LOG/entry.md")
    shutil.rmtree(d, ignore_errors=True)
    shutil.rmtree(d2, ignore_errors=True)
    check("a hash filled AND prose edited is not called a backfill",
          edited is False, repr(edited))
    check("a heading retitled with the placeholder left in is not a backfill",
          retitled is False, repr(retitled))


def test_mixed_changes_separate():
    """A backfilled LOG file and an ordinary edit are two different reports."""
    d = repo()
    write(os.path.join(d, "LOG", "entry.md"), ENTRY_PLACEHOLDER)
    write(os.path.join(d, "SPEC.md"), "# SPEC\n\nOriginal.\n")
    git(d, "add", "-A")
    git(d, "commit", "-m", "first")
    write(os.path.join(d, "LOG", "entry.md"), ENTRY_FILLED)
    write(os.path.join(d, "SPEC.md"), "# SPEC\n\nEdited.\n")

    paths = hook._dirty_paths(d)
    backfilled = [p for p in paths if p.startswith("LOG/")
                  and hook._is_hash_backfill_diff(d, p)]
    remaining = [p for p in paths if p not in backfilled]
    shutil.rmtree(d, ignore_errors=True)
    check("the backfilled entry is on the backfill side",
          backfilled == ["LOG/entry.md"], repr(backfilled))
    check("the hand-edited file stays on the plain-count side",
          remaining == ["SPEC.md"], repr(remaining))


def test_a_clean_tree_reports_nothing():
    d = repo()
    write(os.path.join(d, "LOG", "entry.md"), ENTRY_FILLED)
    git(d, "add", "-A")
    git(d, "commit", "-m", "first")
    paths = hook._dirty_paths(d)
    shutil.rmtree(d, ignore_errors=True)
    check("a clean tree has no dirty paths", paths == [], repr(paths))


if __name__ == "__main__":
    print("test_session_start_uncommitted_changes.py")
    test_a_pure_backfill_is_recognised()
    test_a_real_edit_in_the_same_file_fails_back_to_the_count()
    test_mixed_changes_separate()
    test_a_clean_tree_reports_nothing()
    print()
    if _failures:
        print(f"{len(_failures)} failure(s): " + ", ".join(_failures))
        sys.exit(1)
    print("all passed")
