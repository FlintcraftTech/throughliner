#!/usr/bin/env python3
"""Fixture suite for the untracked-core-docs check.

Run: py tests/test_session_start_untracked_docs.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

What this is guarding. A whole planning session ran in a consumer project — a red
flag cleared, three SPEC edits, eight work items, nine captures — and only at the
close did anyone discover `.gitignore` carried SPEC.md, QUEUE.md and LOG/. The
adoption commit's message said it had written SPEC.md as product truth; that
commit contains no SPEC.md.

The check is deliberately NOT a fault report. `setup.md` offers to ignore exactly
these three paths, so a check asserting the state is wrong would fire on a
configuration the method itself creates on request — hardest right after the user
chose it. What was missing is that nobody was ever told what follows. So the
assertions here are about detection and about the consequences being stated, and
one of them pins that no fault language appears.
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
    print(("  PASS  " if ok else "  FAIL  ") + label + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


def load():
    spec = importlib.util.spec_from_file_location("session_start", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def repo(gitignore=""):
    """A real git repository, because `git check-ignore` needs one."""
    d = tempfile.mkdtemp(prefix="untracked-docs-test-")
    subprocess.run(["git", "init", "-q"], cwd=d, capture_output=True)
    for name in ("SPEC.md", "QUEUE.md"):
        with open(os.path.join(d, name), "w", encoding="utf-8") as f:
            f.write("# " + name + "\n")
    os.makedirs(os.path.join(d, "LOG"), exist_ok=True)
    with open(os.path.join(d, "LOG", "index.md"), "w", encoding="utf-8") as f:
        f.write("# index\n")
    if gitignore:
        with open(os.path.join(d, ".gitignore"), "w", encoding="utf-8") as f:
            f.write(gitignore)
    return d


def test_nothing_ignored_reports_nothing():
    """The control. A check that fires on the ordinary case is worse than none."""
    mod = load()
    d = repo()
    check("a fully tracked project reports no ignored docs",
          mod._untracked_core_docs(d) == [], str(mod._untracked_core_docs(d)))
    shutil.rmtree(d, ignore_errors=True)


def test_each_path_is_detected_on_its_own():
    """Per document, because the privacy offer is per document.

    A user can reasonably want a private queue and a public history, so a check
    that only recognised all three together would miss the combination the
    method explicitly supports.
    """
    mod = load()
    for path, line in (("SPEC.md", "SPEC.md\n"),
                       ("QUEUE.md", "QUEUE.md\n"),
                       ("LOG/", "LOG/\n")):
        d = repo(line)
        found = mod._untracked_core_docs(d)
        check(f"{path} alone is detected",
              any(path.rstrip("/") in f for f in found), f"{path}: got {found}")
        shutil.rmtree(d, ignore_errors=True)


def test_all_three_are_detected_together():
    """The reported case: all three ignored at once."""
    mod = load()
    d = repo("SPEC.md\nQUEUE.md\nLOG/\n")
    found = mod._untracked_core_docs(d)
    check("all three are detected", len(found) == 3, str(found))
    shutil.rmtree(d, ignore_errors=True)


def test_outside_a_repository_degrades_quietly():
    """No git, no answer — and no error.

    A project need not be a repository at all, and the check must not turn that
    into noise at every session opening.
    """
    mod = load()
    d = tempfile.mkdtemp(prefix="untracked-docs-nogit-")
    check("no repository means no report and no crash",
          mod._untracked_core_docs(d) == [], str(mod._untracked_core_docs(d)))
    shutil.rmtree(d, ignore_errors=True)


def test_an_unrelated_ignore_line_is_not_reported():
    """Only the three core docs. An ignore file has other things in it."""
    mod = load()
    d = repo("node_modules/\n*.log\n.throughliner/\n")
    check("unrelated ignore lines are not reported",
          mod._untracked_core_docs(d) == [], str(mod._untracked_core_docs(d)))
    shutil.rmtree(d, ignore_errors=True)


def test_the_report_names_snapshots_and_not_show_first():
    """The consequence text must match what the plugin now actually does.

    Snapshots restore recoverability for untracked documents, so write-first
    stands and the old "text is SHOWN to you first instead" clause became false.
    A stale consequence line is worse than none: it tells the user to expect a
    behaviour no session will produce. The limit — one machine, no history —
    is pinned too, because a net described as an equal replacement for git is
    the over-claim this project guards hardest against.
    """
    with open(HOOK, encoding="utf-8") as handle:
        source = handle.read()
    check("the untracked report names the snapshot folder",
          ".throughliner/snapshots/" in source, "snapshot path not named")
    check("the untracked report states the one-machine limit",
          "lost disk loses them" in source, "limit not stated")
    check("the retired show-first consequence is gone",
          "is SHOWN to you first instead" not in source,
          "stale show-first clause still present")


if __name__ == "__main__":
    print("test_session_start_untracked_docs")
    test_nothing_ignored_reports_nothing()
    test_each_path_is_detected_on_its_own()
    test_all_three_are_detected_together()
    test_outside_a_repository_degrades_quietly()
    test_an_unrelated_ignore_line_is_not_reported()
    test_the_report_names_snapshots_and_not_show_first()
    print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
    sys.exit(1 if failures else 0)
