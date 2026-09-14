#!/usr/bin/env python3
"""Regression tests for session_start.py's installed-since date.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_session_start_install_age.py

Why this exists ([session-start-reports-install-age]): a session weighing how
long the installed build has been in place had nothing to read and had to
guess. The CLI writes the snapshot into
`~/.claude/plugins/cache/<owner>/<plugin>/<version>/` at install time and does
not touch it after, so that directory's mtime is when the build arrived.

The degrade cases are the point of the file. A wrong date here would be read as
evidence about how tested a build is, so every failure has to produce NO age
claim rather than a plausible one.
"""

import datetime
import importlib.util
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "session_start.py")

_spec = importlib.util.spec_from_file_location("session_start", HOOK)
session_start = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(session_start)

failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        failures.append(name)


# A fixture cache directory, shaped like the real one.
cache = tempfile.mkdtemp(prefix="install-age-test-")
version_dir = os.path.join(cache, "flintcraft", "throughliner", "1.21.0")
os.makedirs(version_dir)
with open(os.path.join(version_dir, "plugin.json"), "w", encoding="utf-8") as f:
    f.write("{}")

got = session_start.install_date(version_dir)
check(
    "a real directory yields today's date in ISO form",
    got == datetime.date.today().isoformat(),
    f"got {got!r}",
)

# An older install — the case the fact exists for. Set the directory's mtime
# back and read the date off it.
old = datetime.date(2026, 8, 9)
stamp = datetime.datetime(2026, 8, 9, 12, 0, 0).timestamp()
os.utime(version_dir, (stamp, stamp))
got = session_start.install_date(version_dir)
check(
    "an older install reports the date it was written, not today",
    got == old.isoformat(),
    f"got {got!r}",
)

# --- the degrade cases: no claim rather than a guess -------------------------

for value, what in [
    ("", "an empty root"),
    (os.path.join(cache, "does-not-exist"), "a missing directory"),
    (os.path.join(version_dir, "plugin.json"), "a file rather than a directory"),
]:
    got = session_start.install_date(value)
    check(
        f"{what} produces no age claim",
        got == "",
        f"got {got!r}",
    )

# A lost timestamp. Windows clamps an out-of-range mtime to zero rather than
# raising, so this arrives as a perfectly well-formed 1970-01-01 that no
# exception handler can catch — which is why the helper carries a date floor
# and not only a try/except. This case is what found that.
try:
    os.utime(version_dir, (2 ** 62, 2 ** 62))
except (OSError, OverflowError, ValueError):
    print("[skip] this platform refuses an out-of-range mtime — "
          "the guard is unreachable here")
else:
    got = session_start.install_date(version_dir)
    check(
        "a lost timestamp produces no age claim rather than a 1970 date",
        got == "",
        f"got {got!r}",
    )

# The floor itself, driven directly: a date before the plugin existed cannot be
# an install date whatever the filesystem says.
stamp = datetime.datetime(2025, 1, 1, 12, 0, 0).timestamp()
os.utime(version_dir, (stamp, stamp))
got = session_start.install_date(version_dir)
check(
    "a date before the plugin was rebuilt produces no age claim",
    got == "",
    f"got {got!r}",
)

# And the floor does not swallow a legitimate early install.
stamp = datetime.datetime(2026, 6, 2, 12, 0, 0).timestamp()
os.utime(version_dir, (stamp, stamp))
got = session_start.install_date(version_dir)
check(
    "a date just after the floor still reports",
    got == "2026-06-02",
    f"got {got!r}",
)

shutil.rmtree(cache, ignore_errors=True)

print()
if failures:
    print(f"{len(failures)} failure(s):")
    for name in failures:
        print(f"  {name}")
    sys.exit(1)
print("all cases passed")
