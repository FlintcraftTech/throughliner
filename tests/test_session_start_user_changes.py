#!/usr/bin/env python3
"""Regression tests for how session_start.py splits uncommitted changes by
whether the safety check's decision log shows Claude making them, and names
captures that arrived in Unprocessed since the last commit
([user-edits-noticed-sorted-and-cross-checked]).

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_session_start_user_changes.py

No test framework, matching the suites alongside it. These build real git
repositories in a temp folder, because the thing under test reads `git log`
and `git show`.
"""

import datetime
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
    d = tempfile.mkdtemp(prefix="session-start-user-changes-")
    git(d, "init")
    git(d, "config", "user.email", "test@example.invalid")
    git(d, "config", "user.name", "Test")
    # A real project ignores its working folder, as setup scaffolds it.
    write(os.path.join(d, ".gitignore"), ".throughliner/\n")
    return d


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def log_write(d, tool, decision, rel, when):
    """Append one decision-log line in the safety check's own shape."""
    folder = os.path.join(d, ".throughliner")
    os.makedirs(folder, exist_ok=True)
    target = os.path.join(d, rel.replace("/", os.sep))
    line = "%s\t%s\t%s\tbuild scope: in Files list\t%s\tsid\n" % (
        when.strftime("%Y-%m-%d %H:%M:%S"), tool, decision, target)
    with open(os.path.join(folder, "pre-tool-use.log"), "a",
              encoding="utf-8") as f:
        f.write(line)


QUEUE = ("# QUEUE\n\n## Processed\n\n#### Kept work [kept-work]\nWhy.\n\n"
         "--- Cleared to run above this line ---\n\n## Unprocessed\n\n"
         "#### Old capture [old-capture]\nWhy.\n")


def test_split_by_what_the_log_shows():
    d = repo()
    write(os.path.join(d, "SPEC.md"), "# SPEC\n\nOriginal.\n")
    write(os.path.join(d, "notes.md"), "Original.\n")
    git(d, "add", "-A")
    git(d, "commit", "-m", "first")
    later = datetime.datetime.now() + datetime.timedelta(seconds=5)
    earlier = datetime.datetime.now() - datetime.timedelta(days=2)
    write(os.path.join(d, "SPEC.md"), "# SPEC\n\nEdited by Claude.\n")
    write(os.path.join(d, "notes.md"), "Edited by hand.\n")
    log_write(d, "Edit", "allow", "SPEC.md", later)
    # A write logged before the last commit is not this change.
    log_write(d, "Edit", "allow", "notes.md", earlier)
    # A refused write is not a write.
    log_write(d, "Write", "deny", "notes.md", later)

    paths = hook._dirty_paths(d)
    claude, other = hook._split_by_author(d, paths)
    shutil.rmtree(d, ignore_errors=True)
    check("the logged edit is on Claude's side", claude == ["SPEC.md"],
          repr(claude))
    check("the edit the log does not show is the user's", other == ["notes.md"],
          repr(other))


def test_archived_log_is_read_too():
    d = repo()
    write(os.path.join(d, "a.md"), "x\n")
    git(d, "add", "-A")
    git(d, "commit", "-m", "first")
    write(os.path.join(d, "a.md"), "y\n")
    log_write(d, "Write", "allow", "a.md",
              datetime.datetime.now() + datetime.timedelta(seconds=5))
    folder = os.path.join(d, ".throughliner")
    os.replace(os.path.join(folder, "pre-tool-use.log"),
               os.path.join(folder, "pre-tool-use-2099-01.log"))
    claude, other = hook._split_by_author(d, hook._dirty_paths(d))
    shutil.rmtree(d, ignore_errors=True)
    check("a write recorded in a monthly archive counts as Claude's",
          claude == ["a.md"] and other == [], repr((claude, other)))


def test_arrived_captures_named():
    d = repo()
    write(os.path.join(d, "QUEUE.md"), QUEUE)
    git(d, "add", "-A")
    git(d, "commit", "-m", "first")
    write(os.path.join(d, "QUEUE.md"),
          QUEUE + "\n#### New capture [new-capture]\nWhy.\n")
    arrived = hook._arrived_captures(d)
    shutil.rmtree(d, ignore_errors=True)
    check("a capture absent from the last commit is named as arrived",
          arrived == ["new-capture"], repr(arrived))


def test_processed_entry_is_not_an_arrival():
    d = repo()
    write(os.path.join(d, "QUEUE.md"), QUEUE)
    git(d, "add", "-A")
    git(d, "commit", "-m", "first")
    write(os.path.join(d, "QUEUE.md"), QUEUE.replace(
        "--- Cleared", "#### Another kept [another-kept]\nWhy.\n\n--- Cleared"))
    arrived = hook._arrived_captures(d)
    shutil.rmtree(d, ignore_errors=True)
    check("a new entry in Processed is not named as an arrived capture",
          arrived == [], repr(arrived))


def test_untracked_queue_reports_nothing():
    d = repo()
    write(os.path.join(d, "README.md"), "x\n")
    git(d, "add", "-A")
    git(d, "commit", "-m", "first")
    write(os.path.join(d, "QUEUE.md"), QUEUE)
    arrived = hook._arrived_captures(d)
    shutil.rmtree(d, ignore_errors=True)
    check("a queue git does not hold reports no arrivals", arrived == [],
          repr(arrived))


SENT_BLOCK = ("\n#### Sent capture [sent-capture]\nWhat was noticed.\n"
              "From: other project, sent 2026-10-08 12:17\n"
              "Filed 2026-10-08 12:17, stamped by the queue tool.\n")


def test_queue_whose_only_change_is_a_sent_capture_is_not_the_users_edit():
    """A capture another project's tool appended logs no write here, so the
    author split named QUEUE.md as the user's edit in the same breath as the
    arrivals line ([sent-captures-read-as-user-edits])."""
    d = repo()
    write(os.path.join(d, "QUEUE.md"), QUEUE)
    git(d, "add", "-A")
    git(d, "commit", "-m", "first")
    write(os.path.join(d, "QUEUE.md"), QUEUE + SENT_BLOCK)
    arrived = hook._arrived_captures(d)
    only = hook._queue_diff_is_arrivals_only(d, arrived)
    shutil.rmtree(d, ignore_errors=True)
    check("the appended capture is named as arrived",
          arrived == ["sent-capture"], repr(arrived))
    check("a queue whose whole diff is the arrived block is not a user edit",
          only is True, repr(only))


def test_queue_with_a_reworded_line_is_still_the_users_edit():
    d = repo()
    write(os.path.join(d, "QUEUE.md"), QUEUE)
    git(d, "add", "-A")
    git(d, "commit", "-m", "first")
    write(os.path.join(d, "QUEUE.md"),
          QUEUE.replace("#### Old capture", "#### Old capture, reworded")
          + SENT_BLOCK)
    arrived = hook._arrived_captures(d)
    only = hook._queue_diff_is_arrivals_only(d, arrived)
    shutil.rmtree(d, ignore_errors=True)
    check("a reworded existing line keeps the file on the author-split side",
          only is False, repr(only))


if __name__ == "__main__":
    print("test_session_start_user_changes.py")
    test_queue_whose_only_change_is_a_sent_capture_is_not_the_users_edit()
    test_queue_with_a_reworded_line_is_still_the_users_edit()
    test_split_by_what_the_log_shows()
    test_archived_log_is_read_too()
    test_arrived_captures_named()
    test_processed_entry_is_not_an_arrival()
    test_untracked_queue_reports_nothing()
    print()
    if _failures:
        print(f"{len(_failures)} failure(s): " + ", ".join(_failures))
        sys.exit(1)
    print("all passed")
