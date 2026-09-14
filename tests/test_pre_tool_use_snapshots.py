#!/usr/bin/env python3
"""Fixture suite for the pre-change snapshots of untracked method documents.

Run: py tests/test_pre_tool_use_snapshots.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

What this is guarding. Write-first — Claude writes to a project document and then
reports what landed — rests on the previous version being recoverable without the
user's help. Git supplied that for tracked documents; for an untracked one nothing
did, so the rule flipped those documents to show-first. These snapshots supply it
instead, which is what lets write-first stand in the configuration setup now
proposes.

The assertions therefore cover the three ways the net can silently fail to exist:
snapshotting only tracked files (nothing saved where it matters), snapshotting
nothing at all on an error path, and growing without bound. The prune window is
asserted as git's own reflog-expiry default rather than as a chosen number, since
a bare number is the failure the method's own rules forbid.
"""

import datetime
import importlib.util
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
    print(("  PASS  " if ok else "  FAIL  ") + label + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


def load():
    spec = importlib.util.spec_from_file_location("pre_tool_use", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def repo(gitignore="", commit=False):
    """A real git repository, because tracked-versus-untracked is a git fact."""
    d = tempfile.mkdtemp(prefix="snapshot-test-")
    subprocess.run(["git", "init", "-q"], cwd=d, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@example.invalid"],
                   cwd=d, capture_output=True)
    subprocess.run(["git", "config", "user.name", "t"],
                   cwd=d, capture_output=True)
    for name in ("SPEC.md", "QUEUE.md"):
        with open(os.path.join(d, name), "w", encoding="utf-8") as f:
            f.write("# " + name + "\noriginal\n")
    if gitignore:
        with open(os.path.join(d, ".gitignore"), "w", encoding="utf-8") as f:
            f.write(gitignore)
    if commit:
        subprocess.run(["git", "add", "-A"], cwd=d, capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"],
                       cwd=d, capture_output=True)
    return d


def snaps(d):
    snap_dir = os.path.join(d, ".throughliner", "snapshots")
    if not os.path.isdir(snap_dir):
        return []
    return sorted(os.listdir(snap_dir))


def test_untracked_document_is_snapshotted():
    """The case the whole mechanism exists for."""
    mod = load()
    d = repo(gitignore="QUEUE.md\n", commit=True)
    mod._snapshot_before_write(d, os.path.join(d, "QUEUE.md"))
    found = snaps(d)
    check("an untracked QUEUE.md is snapshotted before a write",
          len(found) == 1 and found[0].startswith("QUEUE.md@"), str(found))
    if found:
        path = os.path.join(d, ".throughliner", "snapshots", found[0])
        with open(path, encoding="utf-8") as handle:
            body = handle.read()
        check("the snapshot holds the contents as they stood",
              "original" in body, body[:60])
    shutil.rmtree(d, ignore_errors=True)


def test_tracked_document_is_not_snapshotted():
    """Git already holds it. A copy here would be pure duplication."""
    mod = load()
    d = repo(commit=True)
    mod._snapshot_before_write(d, os.path.join(d, "QUEUE.md"))
    check("a tracked QUEUE.md is not snapshotted", snaps(d) == [], str(snaps(d)))
    shutil.rmtree(d, ignore_errors=True)


def test_a_non_method_document_is_not_snapshotted():
    """The subject set is the project's own method documents and nothing else."""
    mod = load()
    d = repo(gitignore="*\n", commit=False)
    other = os.path.join(d, "README.md")
    with open(other, "w", encoding="utf-8") as handle:
        handle.write("readme\n")
    mod._snapshot_before_write(d, other)
    check("a non-method document is not snapshotted", snaps(d) == [], str(snaps(d)))
    shutil.rmtree(d, ignore_errors=True)


def test_an_unchanged_file_adds_no_second_version():
    """Duplicate collapse. Without it a run of forty writes stores forty copies
    of an unchanged file, and the folder's size stops tracking real versions."""
    mod = load()
    d = repo(gitignore="QUEUE.md\n", commit=True)
    path = os.path.join(d, "QUEUE.md")
    mod._snapshot_before_write(d, path)
    mod._snapshot_before_write(d, path)
    check("an unchanged file is snapshotted once", len(snaps(d)) == 1, str(snaps(d)))
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("# QUEUE.md\nchanged\n")
    mod._snapshot_before_write(d, path)
    check("a changed file adds a version", len(snaps(d)) == 2, str(snaps(d)))
    shutil.rmtree(d, ignore_errors=True)


def test_a_missing_file_is_skipped_quietly():
    """A first-ever write has no previous version, and that is not an error."""
    mod = load()
    d = repo(gitignore="QUEUE.md\n", commit=True)
    mod._snapshot_before_write(d, os.path.join(d, "CYCLES.md"))
    check("a file that does not exist yet is skipped with no crash",
          snaps(d) == [], str(snaps(d)))
    shutil.rmtree(d, ignore_errors=True)


def test_no_repository_still_snapshots():
    """Failing toward saving. No git means no undo at all, which is exactly
    when the copy matters most — the opposite direction would withdraw the net
    at the moment nobody can tell it is gone."""
    mod = load()
    d = tempfile.mkdtemp(prefix="snapshot-nogit-")
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8") as handle:
        handle.write("# QUEUE.md\n")
    mod._snapshot_before_write(d, os.path.join(d, "QUEUE.md"))
    check("a project with no git repository is still snapshotted",
          len(snaps(d)) == 1, str(snaps(d)))
    shutil.rmtree(d, ignore_errors=True)


def test_old_snapshots_are_pruned_at_gits_own_window():
    """The window is derived, not chosen: git's `gc.reflogExpire` default."""
    mod = load()
    check("the window is git's reflog-expiry default of 90 days",
          mod.SNAPSHOT_WINDOW_DAYS == 90, str(mod.SNAPSHOT_WINDOW_DAYS))

    d = repo(gitignore="QUEUE.md\n", commit=True)
    snap_dir = os.path.join(d, ".throughliner", "snapshots")
    os.makedirs(snap_dir, exist_ok=True)
    old = (datetime.datetime.now()
           - datetime.timedelta(days=mod.SNAPSHOT_WINDOW_DAYS + 1))
    fresh = datetime.datetime.now() - datetime.timedelta(days=1)
    for stamp in (old, fresh):
        name = "QUEUE.md@" + stamp.strftime("%Y%m%dT%H%M%S%f")
        with open(os.path.join(snap_dir, name), "w", encoding="utf-8") as handle:
            handle.write("x\n")
    mod._prune_snapshots(snap_dir)
    remaining = snaps(d)
    check("a snapshot past the window is pruned", len(remaining) == 1, str(remaining))
    check("a snapshot inside the window is kept",
          remaining and remaining[0].endswith(fresh.strftime("%Y%m%dT%H%M%S%f")),
          str(remaining))
    shutil.rmtree(d, ignore_errors=True)


def test_the_snapshot_folder_is_one_git_already_ignores():
    """Snapshots of documents kept out of the repository must not themselves be
    committed. `.throughliner/` is the folder setup already adds an ignore line
    for, which is why it is the one used."""
    with open(HOOK, encoding="utf-8") as handle:
        source = handle.read()
    check("snapshots live under the already-ignored .throughliner/ folder",
          '".throughliner", "snapshots"' in source, "snapshot folder moved")


def _drive(cwd, payload):
    """Run the hook as the app does — a subprocess reading JSON on stdin."""
    proc = subprocess.run([sys.executable, HOOK], cwd=cwd,
                          input=json.dumps(payload), capture_output=True,
                          text=True, encoding="utf-8")
    return proc.returncode, proc.stdout


def _log_lines(d):
    path = os.path.join(d, ".throughliner", "pre-tool-use.log")
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as handle:
        return handle.read().splitlines()


def test_every_decision_leaves_a_line_naming_its_branch():
    """[research-writes-passed-lock-unexplained]: a write that passes with no
    line is a hook that did not run. An allow and a deny each leave one line
    carrying the tool, the decision, the deciding branch and the target."""
    d = repo(commit=True)
    # A planning session (no build working file): QUEUE.md is on the standing
    # list and passes; README.md is not and is refused.
    rc, out = _drive(d, {"cwd": d, "tool_name": "Edit", "session_id": "s1",
                         "tool_input": {"file_path": os.path.join(d, "QUEUE.md")}})
    rc2, out2 = _drive(d, {"cwd": d, "tool_name": "Edit", "session_id": "s1",
                           "tool_input": {"file_path": os.path.join(d, "README.md")}})
    lines = _log_lines(d)
    check("the hook exits 0 on both calls", rc == 0 and rc2 == 0, f"{rc} {rc2}")
    check("the allow left no deny output and the deny did",
          out.strip() == "" and '"deny"' in out2, repr((out, out2)))
    check("two decisions, two lines", len(lines) == 2, repr(lines))
    if len(lines) == 2:
        allow, deny = lines
        # Six columns since [sweep-security-users-door-is-self-declared]:
        # the session id closes each line, after the target.
        check("the allow line names its branch, target and session",
              "\tEdit\tallow\tplanning standing list\t" in allow
              and allow.endswith("QUEUE.md\ts1"), allow)
        check("the deny line names its branch, target and session",
              "\tEdit\tdeny\tplanning standing list: not on it\t" in deny
              and deny.endswith("README.md\ts1"), deny)
        check("each line opens with a clock stamp",
              all(len(l.split("\t")[0]) == 19 for l in lines), repr(lines))
    # A shell command that no guard matches is an allow with the command as
    # its target.
    _drive(d, {"cwd": d, "tool_name": "Bash", "session_id": "s1",
               "tool_input": {"command": "git status"}})
    lines = _log_lines(d)
    check("a shell allow names its branch and the command",
          lines and "\tBash\tallow\tshell command: no guard matched\tgit status"
          in lines[-1], repr(lines[-1:] if lines else lines))
    shutil.rmtree(d, ignore_errors=True)


def test_no_log_in_an_unadopted_folder():
    """An unadopted folder must not gain a .throughliner/ folder from a hook
    that fired in passing."""
    d = tempfile.mkdtemp(prefix="decision-log-unadopted-")
    _drive(d, {"cwd": d, "tool_name": "Bash", "session_id": "s1",
               "tool_input": {"command": "git status"}})
    check("no .throughliner/ folder appears in an unadopted folder",
          not os.path.isdir(os.path.join(d, ".throughliner")))
    shutil.rmtree(d, ignore_errors=True)


def test_the_decision_log_is_pruned():
    """The bound: the newest 500 lines, about a session's worth of calls."""
    mod = load()
    d = repo(commit=True)
    mod._ctx.update({"cwd": d, "tool": "Edit", "target": "x"})
    for i in range(mod._DECISION_LOG_LINES + 40):
        mod._log_decision("allow", "branch %d" % i)
    lines = _log_lines(d)
    check("the log holds exactly the newest bound of lines",
          len(lines) == mod._DECISION_LOG_LINES, str(len(lines)))
    check("the oldest lines are the ones that went",
          lines and lines[0].endswith("branch 40\tx\tunknown")
          and lines[-1].endswith("branch %d\tx\tunknown" % (mod._DECISION_LOG_LINES + 39)),
          repr((lines[:1], lines[-1:])))
    mod._ctx.update({"cwd": "", "tool": "", "target": ""})
    shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    print("test_pre_tool_use_snapshots")
    test_every_decision_leaves_a_line_naming_its_branch()
    test_no_log_in_an_unadopted_folder()
    test_the_decision_log_is_pruned()
    test_untracked_document_is_snapshotted()
    test_tracked_document_is_not_snapshotted()
    test_a_non_method_document_is_not_snapshotted()
    test_an_unchanged_file_adds_no_second_version()
    test_a_missing_file_is_skipped_quietly()
    test_no_repository_still_snapshots()
    test_old_snapshots_are_pruned_at_gits_own_window()
    test_the_snapshot_folder_is_one_git_already_ignores()
    print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
    sys.exit(1 if failures else 0)
