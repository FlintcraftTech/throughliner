#!/usr/bin/env python3
"""Measure how long this project's written shapes have grown over time.

Ships with the plugin. It used to be a host-only dev artifact while the
always-loaded rules told every consumer to run it, so every consumer was pointed
at a path their project did not have — and the rules presented their figures as
"traceable and revisable", which they could not be without this.

Run:  py <plugin-root>/scripts/measure_written_shape_length.py .
      py <plugin-root>/scripts/measure_written_shape_length.py . --history

Four shapes, each reported as a LENGTH AGAINST A DATE and nothing more:

    captures          word count of an item's block the first time it appears
                      in QUEUE.md at all, against the date it appeared
    work items        word count of the same item's block while it sits in
                      Processed, against date, and against its own first-filed
                      length — the growth an item accrues between capture and
                      being built
    LOG entries       word count per entry file, against the date in its name,
                      split by flavor (a planning session's entry versus a
                      build's) — preceded by the PRE-SPLIT BASELINE, every entry
                      in the combined `log.md` / `log-v*.md` files measured as
                      one undifferentiated group, since flavor was not recorded
                      in that era. That baseline is the era before the growth,
                      so without it the growth is only ever reported from
                      inside the period it happened in.
    LOG index lines   word count per index line, against date, beside the word
                      count of the entry that line points at — the inflation
                      path the user named: a longer index line implies a longer
                      entry

Both modes invent no threshold and pass no judgment on any figure. The default
prints this project's current distributions; `--history` prints the same shapes
against dates, replayed from git.

**`--bands` is retired and now exits with an error naming why.** It reported the
project against the length caps in `skill-nonspecific-rules.md`, and those caps
were repealed on 2026-08-19 — on an argument that came from this file. A band
printed inside a distribution report is a threshold read off the thing being
questioned, so it can only tell you what you already do; the shipped bands were
exactly that, the middle of what this corpus had already written. The script
declined to do what the rules did, and the rules have now stopped.

**No band may be read off the middle of either report**, and none is printed. Do
not reinstate one here: this corpus is the bloated one, so its typical length is
not a target, and a figure re-derived from it would carry the same circularity
with the objection deleted.

Method: the queue's own patch history is replayed from git, one blob per commit
that touched QUEUE.md, through a single `git cat-file --batch` rather than a
`git show` per commit. The LOG is read straight off disk, since entries are
immutable once written and their date is in the filename.
"""

import os
import re
import subprocess
import sys
from collections import defaultdict

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

SLUG_RE = re.compile(r"\[([a-z0-9][a-z0-9-]*)\]\s*$")
ITEM_RE = re.compile(r"^####\s+\S")
# Matched as a whole line, never as a substring — an item's prose may quote the
# marker text, and a substring test would read that sentence as the readiness
# line. Same anchored predicate reorder_queue.py uses.
MARKER_RE = re.compile(r"^---\s*Cleared to run above this line\s*---\s*$")
LOG_ENTRY_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-([a-z0-9][a-z0-9-]*)\.md$")
INDEX_LINE_RE = re.compile(r"^-\s+(.*?)\s*(?:→|->)\s*([0-9a-z._-]+\.md)\s*$")


def words(text):
    return len(text.split())


# --- git ---------------------------------------------------------------------

def queue_history(root):
    """[(date, blob_text)] for every commit that touched QUEUE.md, oldest first."""
    try:
        log = subprocess.run(
            ["git", "log", "--reverse", "--format=%H|%as", "--", "QUEUE.md"],
            cwd=root, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            encoding="utf-8", errors="replace", timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if log.returncode != 0 or not log.stdout.strip():
        return []

    commits = []
    for line in log.stdout.splitlines():
        if "|" in line:
            sha, date = line.split("|", 1)
            commits.append((sha.strip(), date.strip()))

    request = "".join(f"{sha}:QUEUE.md\n" for sha, _ in commits).encode("utf-8")
    try:
        batch = subprocess.run(
            ["git", "cat-file", "--batch"],
            cwd=root, input=request,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=180,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if batch.returncode != 0:
        return []

    out, buf, i = [], batch.stdout, 0
    for _, date in commits:
        nl = buf.find(b"\n", i)
        if nl == -1:
            break
        header = buf[i:nl].decode("utf-8", "replace").split()
        i = nl + 1
        # "<oid> missing" — the file did not exist at that commit.
        if len(header) < 3:
            continue
        size = int(header[2])
        out.append((date, buf[i:i + size].decode("utf-8", "replace")))
        i += size + 1
    return out


# --- queue snapshots ----------------------------------------------------------

def items_in(text):
    """{slug: (section, cleared, word_count)} for one QUEUE.md snapshot."""
    found, section, cleared, slug, block = {}, None, True, None, []

    def flush():
        if slug:
            found[slug] = (section, cleared, words("\n".join(block)))

    for raw in text.splitlines():
        line = raw.strip()
        if re.match(r"^##\s+Processed\b", line, re.IGNORECASE):
            flush()
            section, cleared, slug, block = "Processed", True, None, []
            continue
        if re.match(r"^##\s+Unprocessed\b", line, re.IGNORECASE):
            flush()
            section, slug, block = "Unprocessed", None, []
            continue
        if MARKER_RE.match(line.strip()):
            cleared = False
            continue
        if ITEM_RE.match(line):
            flush()
            match = SLUG_RE.search(line)
            slug, block = (match.group(1) if match else None), []
            continue
        if slug:
            block.append(line)
    flush()
    return found


def queue_lengths(root):
    """(captures, growth) — first-filed lengths, and capture-to-Processed growth."""
    history = queue_history(root)
    captures, processed_now = {}, {}
    for date, text in history:
        for slug, (section, _cleared, count) in items_in(text).items():
            captures.setdefault(slug, (date, count, section))
            if section == "Processed":
                processed_now[slug] = count

    growth = []
    for slug, (date, first, _section) in captures.items():
        if slug in processed_now:
            growth.append((date, slug, first, processed_now[slug]))
    return captures, growth


# --- the LOG ------------------------------------------------------------------

def log_entries(root):
    """{filename: (date, flavor, word_count)} for every per-entry LOG file."""
    folder = os.path.join(root, "LOG")
    out = {}
    try:
        names = os.listdir(folder)
    except OSError:
        return out
    for name in names:
        match = LOG_ENTRY_RE.match(name)
        if not match:
            continue
        date, slug = match.group(1), match.group(2)
        try:
            with open(os.path.join(folder, name), "r", encoding="utf-8") as f:
                body = f.read()
        except OSError:
            continue
        # A planning session's entry is named for the session, not for a work
        # item, so the slug is where the flavor is legible without opening it.
        flavor = "plan" if slug == "plan" or slug.startswith("plan-") else "build"
        out[name] = (date, flavor, words(strip_front_matter(body)))
    return out


def strip_front_matter(text):
    """The record's text after its leading `---` front-matter block, which
    carries the summary field the index is generated from and is not part
    of the record's own length ([log-index-generated-from-front-matter]).
    Copied per reader, since the scripts run standalone."""
    if not text.startswith("---"):
        return text
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[i + 1:])
    return text


# An entry heading in a pre-split combined log: `## <hash> — <title>`.
LEGACY_FILE_RE = re.compile(r"^log(-v[0-9][0-9a-z.]*)?\.md$")
LEGACY_HEADING_RE = re.compile(r"^##\s+\S")


def legacy_entries(root):
    """[(filename, title, word_count)] for every entry in the combined logs.

    Measured as ONE undifferentiated group, with no plan/build split. Flavor was
    not recorded in that era, and inferring it from a title's wording would be
    guesswork printed as measurement.
    """
    folder = os.path.join(root, "LOG")
    out = []
    try:
        names = sorted(os.listdir(folder))
    except OSError:
        return out
    for name in names:
        if not LEGACY_FILE_RE.match(name):
            continue
        try:
            with open(os.path.join(folder, name), "r", encoding="utf-8") as f:
                body = f.read()
        except OSError:
            continue
        title, block = None, []
        for raw in body.splitlines():
            if LEGACY_HEADING_RE.match(raw):
                if title is not None:
                    out.append((name, title, words("\n".join(block))))
                title, block = raw.lstrip("# ").strip(), []
                continue
            if title is not None:
                block.append(raw)
        if title is not None:
            out.append((name, title, words("\n".join(block))))
    return out


def index_lines(root, entries):
    """[(date, line_words, entry_words, filename)] across LOG/index*.md.

    The index is split by month — index.md for the current month, one
    index-YYYY-MM.md per completed month — so the shape is measured over every
    index file, not just the current one.
    """
    folder = os.path.join(root, "LOG")
    lines = []
    try:
        names = sorted(n for n in os.listdir(folder)
                       if n == "index.md"
                       or re.match(r"index-\d{4}-\d{2}\.md$", n))
    except OSError:
        return []
    for name in names:
        try:
            with open(os.path.join(folder, name), "r", encoding="utf-8") as f:
                lines.extend(f.read().splitlines())
        except OSError:
            continue
    out = []
    for raw in lines:
        match = INDEX_LINE_RE.match(raw.strip())
        if not match:
            continue
        name = match.group(2)
        entry = entries.get(name)
        if not entry:
            continue
        out.append((entry[0], words(match.group(1)), entry[2], name))
    return out


# --- reporting ----------------------------------------------------------------

def by_month(rows, value):
    """{YYYY-MM: [values]} — a month is a grouping, not a threshold."""
    buckets = defaultdict(list)
    for row in rows:
        buckets[row[0][:7]].append(value(row))
    return buckets


def describe(buckets):
    out = []
    for month in sorted(buckets):
        vals = sorted(buckets[month])
        n = len(vals)
        median = vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) // 2
        out.append(
            f"| {month} | {n} | {min(vals)} | {median} | {sum(vals) // n} | {max(vals)} |"
        )
    return out


TABLE_HEAD = ["| month | n | min | median | mean | max |",
              "|---|---|---|---|---|---|"]


def report(root):
    lines = ["# Written-shape length growth", "",
             "**Measured**, by the plugin's "
             "`scripts/measure_written_shape_length.py`. "
             "Every figure is a word count against a date. No threshold is "
             "stated here and none may be read off the middle of these "
             "distributions — this is the corpus the measurement exists to "
             "question, so its typical length is not a target.", ""]

    captures, growth = queue_lengths(root)
    if not captures:
        lines += ["## Queue", "", "No git history for QUEUE.md — nothing measured.", ""]
    else:
        rows = [(date, count) for _slug, (date, count, _s) in captures.items()]
        history = queue_history(root)
        first_commit = history[0][0] if history else "?"
        earliest = min(r[0] for r in rows)
        lines += ["## Captures — length when first filed", "",
                  f"{len(rows)} items, first appearance in QUEUE.md.", ""]
        if earliest > first_commit:
            lines += [
                f"**Coverage limit.** QUEUE.md's history starts {first_commit}, "
                f"but the earliest item this reads is {earliest}. The queue used "
                "a different section structure before the two-section model, so "
                "snapshots older than that parse to no items and contribute "
                "nothing. Read the earliest month as the start of the "
                "measurable record, not the start of the project.", ""]
        lines += TABLE_HEAD + describe(by_month(rows, lambda r: r[1])) + [""]

        lines += ["## Work items — growth from first filing to Processed", "",
                  f"{len(growth)} items currently in Processed, each compared "
                  "against its own first-filed length. Grouped by the month it "
                  "was FIRST filed.", ""]
        lines += TABLE_HEAD[:1] + ["|---|---|---|---|---|---|"]
        lines += describe(by_month(growth, lambda r: r[3] - r[2]))
        lines += ["", "Per item, largest growth first:", ""]
        for date, slug, first, now in sorted(growth, key=lambda r: r[2] - r[3])[:15]:
            lines.append(f"- [{slug}] filed {date}: {first} -> {now} words")
        lines.append("")

    entries = log_entries(root)
    if not entries:
        lines += ["## LOG entries", "", "No per-entry LOG files found.", ""]
    else:
        rows = list(entries.values())
        split = min(r[0] for r in rows)
        legacy = legacy_entries(root)
        lines += ["## LOG entries — the pre-split baseline", ""]
        if not legacy:
            lines += ["No combined log files found under LOG/.", ""]
        else:
            counts = sorted(w for _f, _t, w in legacy)
            n = len(counts)
            median = (counts[n // 2] if n % 2
                      else (counts[n // 2 - 1] + counts[n // 2]) // 2)
            lines += [
                f"{n} entries in `LOG/log.md` and `LOG/log-v*.md`, the era before "
                f"entries became one file each (per-entry files start {split}). "
                "Measured as ONE group: flavor was not recorded then, and "
                "inferring it from a title would be guesswork printed as "
                "measurement. This is the baseline the later tables are read "
                "against.", "",
                "| group | n | min | median | mean | max |",
                "|---|---|---|---|---|---|",
                f"| pre-split | {n} | {counts[0]} | {median} | "
                f"{sum(counts) // n} | {counts[-1]} |", "",
                "Longest pre-split entries:", ""]
            for name, title, count in sorted(legacy, key=lambda r: -r[2])[:10]:
                head = title if len(title) <= 80 else title[:80].rstrip() + "…"
                lines.append(f"- {count} words ({name}): {head}")
            lines.append("")

        lines += ["## LOG entries — by flavor, per-entry era", "",
                  f"{len(rows)} entries, each its own file, from {split} onward.",
                  ""]
        for flavor in ("plan", "build"):
            subset = [r for r in rows if r[1] == flavor]
            if not subset:
                continue
            lines += [f"### {flavor} entries — {len(subset)}", ""]
            lines += TABLE_HEAD + describe(by_month(subset, lambda r: r[2])) + [""]

        idx = index_lines(root, entries)
        lines += ["## LOG index lines — line length, and the entry it points at", "",
                  f"{len(idx)} index lines resolved to an entry file.", ""]
        lines += TABLE_HEAD + describe(by_month(idx, lambda r: r[1])) + [""]
        lines += ["Longest index lines, with the entry each points at:", ""]
        for date, line_w, entry_w, name in sorted(idx, key=lambda r: -r[1])[:15]:
            lines.append(f"- {date}: index line {line_w} words -> entry {entry_w} words ({name})")
        lines.append("")

    return "\n".join(lines)


# --- current shapes -----------------------------------------------------------

# The five written shapes this reports on. There is deliberately no band, floor
# or ceiling beside them: the caps were retired on 2026-08-19, and the argument
# that retired them came from this file — a band printed inside a distribution
# report is a threshold read off the thing being questioned, so it can only tell
# you what you already do. Reinstating one here would be that circularity with
# the objection deleted.
SHAPES = ("capture", "work item", "build entry", "plan entry", "index line")


def current_shapes(root):
    """{shape: [(name, word_count)]} for the project as it stands today."""
    out = {shape: [] for shape in SHAPES}

    try:
        with open(os.path.join(root, "QUEUE.md"), "r", encoding="utf-8") as f:
            queue = f.read()
    except OSError:
        queue = ""
    for slug, (section, _cleared, count) in items_in(queue).items():
        if section == "Unprocessed":
            out["capture"].append((slug, count))
        elif section == "Processed":
            out["work item"].append((slug, count))

    entries = log_entries(root)
    for name, (_date, flavor, count) in entries.items():
        out["plan entry" if flavor == "plan" else "build entry"].append((name, count))

    for _date, line_w, _entry_w, name in index_lines(root, entries):
        out["index line"].append((name, line_w))

    return out


def current_report(root):
    """This project's own distributions, with no threshold of any kind."""
    lines = ["# Written shapes as they stand today", "",
             "How long this project's captures, work items, session records and "
             "index lines actually run. **No band, floor or ceiling is printed, "
             "and none is implied** — these are facts about what you write, not a "
             "standard to write to.", ""]

    shapes = current_shapes(root)
    for shape in SHAPES:
        rows = sorted(shapes[shape], key=lambda r: -r[1])
        lines += [f"## {shape}", ""]
        if not rows:
            lines += ["Nothing found.", ""]
            continue
        counts_sorted = sorted(c for _n, c in rows)
        n = len(counts_sorted)
        median = (counts_sorted[n // 2] if n % 2
                  else (counts_sorted[n // 2 - 1] + counts_sorted[n // 2]) // 2)
        lines += [f"{n} measured. Median {median} words, "
                  f"shortest {counts_sorted[0]}, longest {counts_sorted[-1]}.", ""]
        # The ten longest, so the distribution's tail is visible without
        # printing every row. Naming them is not a finding against them: a long
        # entry is often long because it holds a lot, which is the judgment the
        # retired ceilings were making on nobody's behalf.
        lines.append("Longest:")
        for name, count in rows[:10]:
            lines.append(f"- {count} words — {name}")
        lines.append("")

    return "\n".join(lines)


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    root = os.path.abspath(args[0] if args else ".")
    if not os.path.isfile(os.path.join(root, "QUEUE.md")):
        print(f"measure_written_shape_length: no QUEUE.md under {root}", file=sys.stderr)
        return 1
    if "--bands" in flags:
        # Named rather than ignored. A flag that silently does something else is
        # worse than one that says it is gone.
        print("measure_written_shape_length: --bands is retired. The length caps "
              "it reported against were repealed on 2026-08-19; this script "
              "reports distributions and no thresholds.", file=sys.stderr)
        return 1
    # `--current` kept as an accepted no-op spelling of the default, since the
    # historical report below is the other half of what this script does.
    print(report(root) if "--history" in flags else current_report(root))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
