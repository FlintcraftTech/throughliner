#!/usr/bin/env python3
"""Regression test for the LOG index generated from each record's summary
field, and for the readers of a record's first line
([log-index-generated-from-front-matter]).

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_log_front_matter.py

Each record now carries `---` / `summary: …` / `---` above its heading. Three
halves: every reader of a record's first line skips that block, so a record
with front matter is read the same as one without — the digest's record
classifier, the shape-length measurer, the port changelog's heading read,
the backlinks script's own parser and the development project's
rule_signals hash read; the generator writes the current month's lines into
index.md and each completed month's into its own file, newest first by the
record's own date field, in the existing line shape, a record with no front
matter indexed from its heading and a pre-split line carried over; and
--backfill-summaries, the one-time migration, writes each record's existing
index line into it.
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
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "plugin", "throughliner", "scripts")
SCRIPT = os.path.join(SCRIPTS, "log_backlinks.py")
OUTER = os.path.dirname(ROOT)

failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        failures.append(name)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


digest = load("digest_fm", os.path.join(SCRIPTS, "queue_digest.py"))
measure = load("measure_fm", os.path.join(SCRIPTS, "measure_written_shape_length.py"))
port = load("port_fm", os.path.join(SCRIPTS, "port_changelog.py"))
backlinks = load("backlinks_fm", SCRIPT)

PLAIN = "# abc1234 — build — the thing\n\nRecorded 2026-09-24 10:00.\n\nFiles touched: x.md.\n"
FRONT = "---\nsummary: build — the thing, built\n---\n" + PLAIN

print("test_log_front_matter")

# --- the readers -------------------------------------------------------------
check("digest: record_kind reads a front-matter record as the plain one",
      digest.record_kind(FRONT) == digest.record_kind(PLAIN) == "built")
check("measure: the summary field is not counted in the record's words",
      measure.words(measure.strip_front_matter(FRONT)) == measure.words(PLAIN))

d = tempfile.mkdtemp(prefix="front-matter-")
os.makedirs(os.path.join(d, "LOG"))
with open(os.path.join(d, "LOG", "2026-09-24-the-thing.md"), "w", encoding="utf-8") as f:
    f.write(FRONT)
found = port.log_entries_for(d, "abc1234")
check("port changelog: a front-matter record is found by its heading's hash",
      len(found) == 1 and found[0]["title"] == "build — the thing", repr(found))
fields, body = backlinks.split_front_matter(FRONT)
check("backlinks: the summary field and the body are split",
      fields.get("summary") == "build — the thing, built" and body == PLAIN,
      repr((fields, body[:40])))
check("backlinks: a record with no front matter splits to no fields",
      backlinks.split_front_matter(PLAIN) == ({}, PLAIN))
check("backlinks: the heading's hash and text are read after the block",
      backlinks.heading_of(body) == ("abc1234", "build — the thing"))
shutil.rmtree(d, ignore_errors=True)

rule_signals_path = os.path.join(OUTER, "method", "rule_signals.py")
if os.path.isfile(rule_signals_path):
    rs = load("rule_signals_fm", rule_signals_path)
    d2 = tempfile.mkdtemp(prefix="front-matter-rs-")
    path = os.path.join(d2, "record.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(FRONT)
    check("rule_signals: the heading hash is read past the front matter",
          rs._heading_hash(path) == "abc1234", repr(rs._heading_hash(path)))
    os.makedirs(os.path.join(d2, "LOG"))
    with open(os.path.join(d2, "LOG", "2026-09-24-the-thing.md"), "w", encoding="utf-8") as f:
        f.write(FRONT + "\nRule gate: not needed — a hook change.\n")
    found = rs._log_dispositions(d2)
    check("rule_signals: a disposition is attributed to the heading's hash past the front matter",
          found.get("abc1234") == {"not needed"}, repr(found))
    shutil.rmtree(d2, ignore_errors=True)
else:
    print("  (rule_signals.py not beside this repository — skipped)")

# --- the generator -----------------------------------------------------------
d = tempfile.mkdtemp(prefix="log-index-gen-")
log = os.path.join(d, "LOG")
os.makedirs(log)
today = datetime.date.today()
this_month = today.strftime("%Y-%m")
last_month = (today.replace(day=1) - datetime.timedelta(days=1)).strftime("%Y-%m")
records = {
    "%s-01-older-thing.md" % last_month:
        "---\nsummary: plan — the older thing, kept\n---\n# aaa1111 — plan — the older thing\n\n"
        "Recorded %s-01 09:00, read from the clock.\n\nWork processed: one.\n" % last_month,
    "%s-02-newer-thing.md" % this_month:
        "---\nsummary: build — the newer thing, built and confirmed\n---\n# bbb2222 — build — the newer thing\n\n"
        "Recorded %s-02 14:00, read from the clock.\n\nFiles touched: x.md.\n" % this_month,
    "%s-02-later-thing.md" % this_month:
        "---\nsummary: build — the later thing\n---\n# ccc3333 — build — the later thing\n\n"
        "Recorded %s-02 16:30, read from the clock.\n\nFiles touched: y.md.\n" % this_month,
    "%s-03-no-front-matter.md" % this_month:
        "# [HASH] — build — indexed from its heading\n\nRecorded %s-03 08:00.\n\nFiles touched: z.md.\n" % this_month,
}
for name, text in records.items():
    with open(os.path.join(log, name), "w", encoding="utf-8") as f:
        f.write(text)
with open(os.path.join(log, "index-%s.md" % last_month), "w", encoding="utf-8") as f:
    f.write("# LOG index — %s\n\n- old9999 — a pre-split entry → log.md\n" % last_month)

proc = subprocess.run([sys.executable, SCRIPT, d], capture_output=True,
                      encoding="utf-8", errors="replace")
check("generation: the script exits 0", proc.returncode == 0, proc.stdout + proc.stderr)
index = open(os.path.join(log, "index.md"), encoding="utf-8").read()
lines = [ln for ln in index.splitlines() if ln.startswith("- ")]
check("generation: the current month's lines land in index.md, newest first by the record's date field",
      lines == [
          "- [HASH] — build — indexed from its heading → %s-03-no-front-matter.md" % this_month,
          "- ccc3333 — build — the later thing → %s-02-later-thing.md" % this_month,
          "- bbb2222 — build — the newer thing, built and confirmed → %s-02-newer-thing.md" % this_month],
      repr(lines))
check("generation: index.md says it is generated", "never edited by hand" in index, index[:300])
month_file = open(os.path.join(log, "index-%s.md" % last_month), encoding="utf-8").read()
check("generation: the completed month's line lands in its own file, the pre-split line carried after it",
      "- aaa1111 — plan — the older thing, kept → %s-01-older-thing.md\n- old9999 — a pre-split entry → log.md" % last_month
      in month_file, month_file)
check("generation: the older record is not in index.md", "older-thing" not in index, index)
check("generation: backlinks.md is still written", os.path.isfile(os.path.join(log, "backlinks.md")))

# --- the one-time backfill ---------------------------------------------------
proc = subprocess.run([sys.executable, SCRIPT, d, "--backfill-summaries"],
                      capture_output=True, encoding="utf-8", errors="replace")
check("backfill: the script exits 0 and reports what it wrote",
      proc.returncode == 0 and "summary fields written into 1 record(s)" in proc.stdout,
      proc.stdout + proc.stderr)
backfilled = open(os.path.join(log, "%s-03-no-front-matter.md" % this_month), encoding="utf-8").read()
check("backfill: the record gains its summary from its index line",
      backfilled.startswith("---\nsummary: build — indexed from its heading\n---\n# [HASH] — build"),
      backfilled[:120])
check("backfill: a record already carrying a field is left alone",
      open(os.path.join(log, "%s-02-later-thing.md" % this_month), encoding="utf-8").read()
      == records["%s-02-later-thing.md" % this_month])
shutil.rmtree(d, ignore_errors=True)

if failures:
    print("\n%d FAILURE(S)" % len(failures))
    sys.exit(1)
print("\nall passed")
