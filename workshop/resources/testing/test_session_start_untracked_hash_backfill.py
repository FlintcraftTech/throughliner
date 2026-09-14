#!/usr/bin/env python3
"""Regression test for the hash backfill's untracked-log arm.

Host-only dev artifact — not shipped in the plugin package.

Run:  py workshop/resources/testing/test_session_start_untracked_hash_backfill.py

Why this exists ([untracked-log-hash-placeholders-never-fill]): in a project
whose LOG/ is gitignored, no record file appears in any commit, so the
backfill could attribute nothing and every placeholder a close did not write
stayed for good — and the close handed the tidy-up to the user. The arm now
fills a placeholder from the record's own date line, with the one commit
that follows it before the next record's time, and leaves it where the
window holds none or several.

Cases: one commit in the window (filled); none (left, named); two (left,
named); a tracked log (the tracked arm, unchanged).
"""

import datetime
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "session_start.py")
_spec = importlib.util.spec_from_file_location("session_start", HOOK)
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)

_failures = []
OFFSET = datetime.datetime.now().astimezone().strftime("%z")


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        _failures.append(name)


def git(cwd, *args, when=None):
    env = dict(os.environ)
    if when:
        stamp = when + OFFSET
        env["GIT_AUTHOR_DATE"] = stamp
        env["GIT_COMMITTER_DATE"] = stamp
    return subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True,
                          text=True, encoding="utf-8", env=env)


def repo(untracked=True):
    d = tempfile.mkdtemp(prefix="untracked-backfill-")
    git(d, "init", "-q")
    git(d, "config", "user.email", "suite@example.invalid")
    git(d, "config", "user.name", "suite")
    os.mkdir(os.path.join(d, "LOG"))
    if untracked:
        with open(os.path.join(d, ".gitignore"), "w", encoding="utf-8") as f:
            f.write("LOG/\n")
    return d


def commit(d, name, when):
    with open(os.path.join(d, name), "w", encoding="utf-8") as f:
        f.write(name + "\n")
    git(d, "add", name)
    git(d, "commit", "-q", "-m", "commit " + name, when=when)
    return git(d, "log", "-1", "--pretty=%h").stdout.strip()


def record(d, name, when, title="A record"):
    with open(os.path.join(d, "LOG", name), "w", encoding="utf-8", newline="") as f:
        f.write("# [HASH] — %s\n\nDate: %s\n\nBody.\n" % (title, when))


def read(d, name):
    with open(os.path.join(d, "LOG", name), encoding="utf-8") as f:
        return f.read()


def main():
    print("untracked-log hash backfill:")

    # 1. One commit in the window: filled.
    d = repo()
    record(d, "2026-01-01-first.md", "2026-01-01 10:00")
    record(d, "2026-01-01-second.md", "2026-01-01 14:00", title="Second record")
    h1 = commit(d, "a.txt", "2026-01-01T11:00:00")
    h2 = commit(d, "b.txt", "2026-01-01T15:00:00")
    report = hook.backfill_log_hashes(d)
    check("the first record is filled with the commit inside its window",
          read(d, "2026-01-01-first.md").startswith("# %s — A record" % h1),
          read(d, "2026-01-01-first.md")[:60])
    check("the last record is filled with the commit after it",
          read(d, "2026-01-01-second.md").startswith("# %s — Second record" % h2),
          read(d, "2026-01-01-second.md")[:60])
    check("the report says two were filled from record times",
          "filled 2" in report and "not tracked" in report, report)
    shutil.rmtree(d, ignore_errors=True)

    # 2. No commit in the window: left and named.
    d = repo()
    record(d, "2026-01-01-first.md", "2026-01-01 10:00")
    record(d, "2026-01-01-second.md", "2026-01-01 12:00", title="Second record")
    commit(d, "a.txt", "2026-01-01T13:00:00")  # after the second record only
    report = hook.backfill_log_hashes(d)
    check("no commit in the window: the placeholder stays",
          read(d, "2026-01-01-first.md").startswith("# [HASH]"))
    check("no commit in the window: the record is named",
          "2026-01-01-first.md" in report and "keep their placeholder" in report, report)
    shutil.rmtree(d, ignore_errors=True)

    # 3. Two commits in the window: left and named.
    d = repo()
    record(d, "2026-01-01-first.md", "2026-01-01 10:00")
    commit(d, "a.txt", "2026-01-01T11:00:00")
    commit(d, "b.txt", "2026-01-01T12:00:00")
    report = hook.backfill_log_hashes(d)
    check("two commits in the window: the placeholder stays",
          read(d, "2026-01-01-first.md").startswith("# [HASH]"))
    check("two commits in the window: the record is named",
          "2026-01-01-first.md" in report, report)
    shutil.rmtree(d, ignore_errors=True)

    # 4. A tracked log takes the tracked arm, unchanged.
    d = repo(untracked=False)
    with open(os.path.join(d, "LOG", "index.md"), "w", encoding="utf-8") as f:
        f.write("# index\n")
    git(d, "add", "LOG")
    git(d, "commit", "-q", "-m", "baseline")
    with open(os.path.join(d, "LOG", "2026-01-02-thing.md"), "w", encoding="utf-8", newline="") as f:
        f.write("# [HASH] — Tracked fixture entry\n\nDate: 2026-01-02 10:00\n\nBody.\n")
    git(d, "add", "LOG")
    git(d, "commit", "-q", "-m", "fixture")
    expected = git(d, "log", "-1", "--pretty=%h").stdout.strip()
    report = hook.backfill_log_hashes(d)
    check("a tracked log is filled by the tracked arm from git's own record",
          read(d, "2026-01-02-thing.md").startswith("# %s — Tracked" % expected),
          read(d, "2026-01-02-thing.md")[:60])
    check("the tracked arm's report is the old one",
          "not tracked" not in report, report)
    shutil.rmtree(d, ignore_errors=True)

    if _failures:
        print(f"\n{len(_failures)} FAILURE(S)")
        return 1
    print("\nall passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
