#!/usr/bin/env python3
"""Regression tests for scripts/log_backlinks.py.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_log_backlinks.py

No test framework, matching the suites alongside it.

Why this exists ([log-backlink-index-generated]): the backlink file is what
lets the planning decision step open the records that name a slug or a
mechanism instead of guessing search words. This suite pins the key set and
the listing: a slug named in two bodies lists both, a hook name named in one
lists one, a key named nowhere is absent, the generated header line is
present, and non-ASCII content round-trips.
"""

import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "plugin", "throughliner", "scripts",
                      "log_backlinks.py")

failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        failures.append(name)


d = tempfile.mkdtemp(prefix="log-backlinks-")
log = os.path.join(d, "LOG")
os.makedirs(log)
records = {
    "2026-09-01-first-thing.md":
        "# abc — the first thing\n\nBuilt [first-thing]; touches "
        "[shared-slug] and the stop hook — stop.py — with a résumé.\n",
    "2026-09-02-second-thing.md":
        "# def — the second thing\n\nAlso names [shared-slug], and the "
        "server's file_capture tool.\n",
    "2026-09-03-third-thing.md":
        "# ghi — the third thing\n\nNames nothing shared; mentions the "
        "unstoppable word and a full stop, neither of which is a hook.\n",
}
for name, text in records.items():
    with open(os.path.join(log, name), "w", encoding="utf-8") as f:
        f.write(text)
with open(os.path.join(log, "index.md"), "w", encoding="utf-8") as f:
    f.write("# LOG Index\n\n"
            "- abc — first thing: built the first thing → 2026-09-01-first-thing.md\n"
            "- def — second thing: “curly” words → 2026-09-02-second-thing.md\n"
            "- ghi — third thing → 2026-09-03-third-thing.md\n")

proc = subprocess.run([sys.executable, SCRIPT, d], capture_output=True,
                      encoding="utf-8", errors="replace")
check("the script exits 0", proc.returncode == 0, proc.stdout + proc.stderr)
check("it prints the key and record counts",
      "key(s) over 3 record(s)" in proc.stdout, proc.stdout)

path = os.path.join(log, "backlinks.md")
check("LOG/backlinks.md is written", os.path.isfile(path))
text = open(path, "rb").read().decode("utf-8") if os.path.isfile(path) else ""
check("the generated header line is present",
      "never edited by hand" in text.splitlines()[2] if len(text.splitlines()) > 2 else False,
      text[:200])


def section(key):
    marker = "\n## %s\n" % key
    if marker not in text:
        return None
    body = text.split(marker, 1)[1]
    return body.split("\n## ", 1)[0]


shared = section("shared-slug")
check("a slug named in two bodies lists both",
      shared is not None and "2026-09-01-first-thing.md" in shared
      and "2026-09-02-second-thing.md" in shared
      and "2026-09-03-third-thing.md" not in shared, repr(shared))
stop = section("stop")
check("a hook name named in one record lists one",
      stop is not None and "2026-09-01-first-thing.md" in stop
      and "2026-09-03-third-thing.md" not in stop, repr(stop))
check("a tool name named in one record lists one",
      section("file_capture") is not None
      and "2026-09-02-second-thing.md" in section("file_capture"),
      repr(section("file_capture")))
check("a key named nowhere is absent",
      section("pre_tool_use") is None and section("catchup") is None,
      text)
check("each line carries the record's filename and its index line's opening words",
      "- 2026-09-01-first-thing.md — abc — first thing: built the first thing" in text,
      text)
check("non-ASCII content round-trips",
      "“curly” words" in text and "â€œ" not in text, text)
shutil.rmtree(d, ignore_errors=True)

print()
if failures:
    print(f"{len(failures)} failure(s):")
    for name in failures:
        print(f"  {name}")
    sys.exit(1)
print("all cases passed")
