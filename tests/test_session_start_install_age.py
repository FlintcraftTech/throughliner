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

# --- installed copy versus loaded in place -----------------------------------
# ([installed-plugin-reads-source-folder-directly]) Claude Code copies a plugin
# from a GitHub-hosted marketplace into ~/.claude/plugins/cache/ and loads one
# from a local-folder marketplace straight from that folder. The two opening
# lines say which, by where the plugin root sits.

home = tempfile.mkdtemp(prefix="install-place-test-")
cached_root = os.path.join(home, ".claude", "plugins", "cache",
                           "flintcraft", "throughliner", "1.25.0")
os.makedirs(cached_root)
stamp = datetime.datetime(2026, 11, 19, 12, 0, 0).timestamp()
os.utime(cached_root, (stamp, stamp))
source_root = os.path.join(home, "project", "plugin", "throughliner")
os.makedirs(source_root)

check("a root under the plugin cache is not loaded in place",
      session_start.loaded_in_place(cached_root) is False)
check("a root outside the plugin cache is loaded in place",
      session_start.loaded_in_place(source_root) is True)
check("an empty root is not loaded in place",
      session_start.loaded_in_place("") is False)

line = session_start.installed_version_line("1.25.0", cached_root)
check(
    "under a cache path the version line keeps the installed-copy wording",
    "1.25.0, installed since 2026-11-19" in line
    and "host-side deferred test has gone live" in line
    and "loaded in place" not in line,
    line,
)
line = session_start.installed_stamp_line("abc123", cached_root)
check(
    "under a cache path the stamp line keeps the compare instruction",
    "abc123" in line and "stamps differ" in line,
    line,
)

line = session_start.installed_version_line("1.25.0", source_root)
check(
    "outside the cache the version line says loaded in place, naming the folder",
    "1.25.0" in line and "loaded in place from " + source_root in line
    and "live at the next session start" in line
    and "installed since" not in line,
    line,
)
line = session_start.installed_stamp_line("abc123", source_root)
check(
    "outside the cache the stamp line is the stamp alone",
    "abc123" in line and "compare" not in line and "stamps differ" not in line,
    line,
)

shutil.rmtree(home, ignore_errors=True)

print()
if failures:
    print(f"{len(failures)} failure(s):")
    for name in failures:
        print(f"  {name}")
    sys.exit(1)
print("all cases passed")
