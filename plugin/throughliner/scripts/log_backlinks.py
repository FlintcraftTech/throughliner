#!/usr/bin/env python3
"""Generate LOG/backlinks.md and the LOG index files from the records.

Usage:
    python log_backlinks.py <project root>
    python log_backlinks.py <project root> --backfill-summaries

Why this exists ([log-backlink-index-generated]): the planning decision step
greps the index files for a mechanism's distinctive words, and an entry
indexed under other phrasing is missed. Links in the record go one way and
nothing computes backlinks. This reads every record and index file, collects
a key set — every `[slug]` seen anywhere, each hook filename stem under the
plugin's `hooks/`, each skill folder name under `skills/`, each tool name the
state server advertises — and writes one heading per key with one line per
record naming it. Computed from the artifacts every time, never stored by
hand, and the records themselves are never edited.

The index files are generated the same way ([log-index-generated-from-front-matter]):
each record carries its own one-line summary in a front-matter field at the
top of the file —

    ---
    summary: <the index line's text after the hash>
    ---
    # <hash> — <heading>

— and `LOG/index.md` (the current month) and `LOG/index-YYYY-MM.md` (each
completed month) are written from those fields, newest first by the record's
own date field, in the existing line shape `- <hash> — <summary> → <filename>`.
A record with no front matter keeps its existing index line's text where one
names it, and is indexed from its heading line otherwise. An index line
whose target is not a per-entry record — the pre-split combined logs — is
carried over from the existing file unchanged, after the generated lines of
its month. `--backfill-summaries` is the one-time migration: every record with
no front matter gains a summary field from its existing index line, or from
its heading where no line names it, and the index files are then regenerated.

The limit, stated: a record that names a mechanism by neither its slug nor
its package name is still not reached by the backlinks.

Standard library only. UTF-8 reconfiguration copied from reorder_queue.py.
"""

import datetime
import os
import re
import sys

# Status lines can carry non-ASCII characters; a console that cannot render
# them must degrade, never crash.
for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

# This file sits at <plugin-root>/scripts/, so the plugin root is its parent.
PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = "backlinks.md"
HEADER = ("# LOG backlinks\n\n"
          "Generated at every close by the plugin's `log_backlinks.py` and "
          "never edited by hand: one heading per queue slug or plugin name, "
          "one line per record naming it.\n")
INDEX_HEADER = ("# LOG Index\n\n"
                "One-line summaries of each session. Newest first. Generated at "
                "every close from each record's own summary field by the "
                "plugin's `log_backlinks.py`, never edited by hand.\n\n")
MONTH_HEADER = ("# LOG index — %s\n\n"
                "One line per session entry, newest first. Generated at every "
                "close from each record's own summary field, never edited by "
                "hand.\n\n")
SLUG_RE = re.compile(r"\[([a-z0-9][a-z0-9-]*)\]")
TOOL_NAME_RE = re.compile(r'^\s*"name":\s*"([a-z_][a-z0-9_]*)"', re.MULTILINE)
INDEX_LINE_RE = re.compile(r"^- .*?→\s*(\S+\.md)\s*$")
RECORD_NAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-[a-z0-9][a-z0-9-]*\.md$")
# The hash slot admits a two-commit stamp ("df8fdbb / 99296df"), which a
# nested project's records carry where one close made two commits.
HEADING_RE = re.compile(r"^#\s+(\S+(?:\s*/\s*\S+)*?)\s+[—–-]\s+(.*)$")
# The record's own date-and-time line, in the two shapes the records use.
RECORD_TIME_RE = re.compile(
    r"^(?:\*{0,2}Date:?\*{0,2}\s*|Recorded\s+)(\d{4}-\d{2}-\d{2})(?:[ T](\d{2}:\d{2}))?",
    re.MULTILINE)


def read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def split_front_matter(text):
    """(fields, body): the leading `---` block's `key: value` lines as a dict,
    and the text after it. A file with no such block is ({}, text)."""
    if not text.startswith("---"):
        return {}, text
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return {}, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fields = {}
            for raw in lines[1:i]:
                if ":" in raw:
                    key, _, value = raw.partition(":")
                    fields[key.strip()] = value.strip()
            return fields, "\n".join(lines[i + 1:])
    return {}, text


def strip_front_matter(text):
    return split_front_matter(text)[1]


def heading_of(body):
    """(hash-or-placeholder, heading text) from the body's first heading
    line, or ("", "") where there is none."""
    for line in body.split("\n"):
        if line.startswith("#"):
            m = HEADING_RE.match(line.rstrip())
            if m:
                return m.group(1), m.group(2).strip()
            return "", line.lstrip("#").strip()
    return "", ""


def record_date(body, name):
    """(date, time) from the record's own date line, the filename's date and
    an empty time where the line is absent."""
    m = RECORD_TIME_RE.search(body)
    if m:
        return m.group(1), m.group(2) or ""
    nm = RECORD_NAME_RE.match(name)
    return (nm.group(1) if nm else ""), ""


def package_names():
    """(key, pattern) pairs for the hook stems, skill folder names and the
    server's advertised tool names, read off the package rather than any
    map. A hook or skill stem is an ordinary English word — stop, plan, next
    — so it counts only where a record writes it as the package thing: the
    filename, "<stem> hook", "/<name>" or "<name> skill". A tool name carries
    an underscore and is matched bare."""
    pairs = []
    hooks = os.path.join(PLUGIN_ROOT, "hooks")
    if os.path.isdir(hooks):
        for n in sorted(os.listdir(hooks)):
            if n.endswith(".py") and not n.startswith("_"):
                stem = n[:-3]
                pairs.append((stem, re.compile(
                    r"\b%s(?:\.py|[ -]hook)\b" % re.escape(stem))))
    skills = os.path.join(PLUGIN_ROOT, "skills")
    if os.path.isdir(skills):
        for n in sorted(os.listdir(skills)):
            if os.path.isdir(os.path.join(skills, n)):
                pairs.append((n, re.compile(
                    r"(?:/%s\b|\b%s(?: skill|\.md)\b)"
                    % (re.escape(n), re.escape(n)))))
    server = os.path.join(PLUGIN_ROOT, "mcp", "server.py")
    if os.path.isfile(server):
        for n in sorted(set(TOOL_NAME_RE.findall(read(server)))):
            pairs.append((n, re.compile(
                r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(n))))
    return pairs


def index_files(log_dir):
    return sorted(n for n in os.listdir(log_dir)
                  if n == "index.md" or re.match(r"^index-\d{4}-\d{2}\.md$", n))


def index_lines_by_target(log_dir):
    """Record filename -> (index file, full line) for every index line."""
    found = {}
    for name in index_files(log_dir):
        for line in read(os.path.join(log_dir, name)).splitlines():
            m = INDEX_LINE_RE.match(line.strip())
            if m:
                found.setdefault(m.group(1), (name, line.strip()))
    return found


def index_openings(log_dir):
    """Record filename -> the opening words of its index line."""
    openings = {}
    for target, (_file, line) in index_lines_by_target(log_dir).items():
        body = line[2:].rsplit("→", 1)[0].strip()
        openings[target] = " ".join(body.split()[:12])
    return openings


def summary_line_text(line):
    """The summary text of an index line: what follows the hash and its dash,
    up to the LAST arrow — the summary itself may carry one ("91,613 →
    69,126 bytes"), and the filename follows the last."""
    body = line.strip()[2:].rsplit("→", 1)[0].strip()
    m = re.match(r"^\S+(?:\s*/\s*\S+)*?\s+[—–-]\s+(.*)$", body)
    return (m.group(1) if m else body).strip()


def per_entry_records(log_dir):
    return sorted(n for n in os.listdir(log_dir) if RECORD_NAME_RE.match(n))


def backfill_summaries(log_dir, refresh=False):
    """Write a summary field into every per-entry record lacking front
    matter, from its index line where one names it and from its heading
    otherwise. With `refresh`, a record that already carries a field takes
    its index line's text again where one names it and differs — the
    repair for a field written wrongly, run against index files restored
    from history. Returns (from index lines, from headings)."""
    by_target = index_lines_by_target(log_dir)
    from_index = from_heading = 0
    for name in per_entry_records(log_dir):
        path = os.path.join(log_dir, name)
        with open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
            text = f.read()
        fields, body = split_front_matter(text)
        if "summary" in fields:
            if not refresh or name not in by_target:
                continue
            summary = summary_line_text(by_target[name][1])
            if summary == fields["summary"]:
                continue
            from_index += 1
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write("---\nsummary: %s\n---\n%s" % (summary, body))
            continue
        if name in by_target:
            summary = summary_line_text(by_target[name][1])
            from_index += 1
        else:
            summary = heading_of(text)[1]
            from_heading += 1
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write("---\nsummary: %s\n---\n%s" % (summary, text))
    return from_index, from_heading


def generate_index(log_dir, today=None):
    """Write LOG/index.md and LOG/index-YYYY-MM.md from the records'
    summary fields. Returns the number of generated lines."""
    today = today or datetime.date.today()
    current_month = today.strftime("%Y-%m")
    existing = index_lines_by_target(log_dir)
    rows = []
    for name in per_entry_records(log_dir):
        text = read(os.path.join(log_dir, name))
        fields, body = split_front_matter(text)
        hash_, heading = heading_of(body)
        # A record with no summary field keeps its existing index line's
        # text where one names it — the same rule the backfill applies — and
        # is indexed from its heading only where no line does.
        summary = fields.get("summary")
        if not summary and name in existing:
            summary = summary_line_text(existing[name][1])
        summary = summary or heading
        date, time = record_date(body, name)
        if not date:
            continue
        rows.append((date, time, name, hash_ or "[HASH]", summary))
    rows.sort(reverse=True)
    generated = {}
    for date, time, name, hash_, summary in rows:
        generated.setdefault(date[:7], []).append(
            "- %s — %s → %s" % (hash_, summary, name))
    # Every existing `- ` line that does not point at a per-entry record —
    # a pre-split combined log's entry, an old-format line with no arrow at
    # all — is carried over from the file it sits in, after that month's
    # generated lines. Nothing hand-written is dropped.
    records = set(per_entry_records(log_dir))
    carried = {}
    for fname in index_files(log_dir):
        month = fname[6:13] if fname != "index.md" else None
        for line in read(os.path.join(log_dir, fname)).splitlines():
            if not line.startswith("- "):
                continue
            m = INDEX_LINE_RE.match(line.strip())
            if m and m.group(1) in records:
                continue
            key = month or current_month
            carried.setdefault(key, []).append(line.rstrip())
    months = sorted(set(generated) | set(carried))
    written = 0
    for month in months:
        lines = generated.get(month, []) + carried.get(month, [])
        if month == current_month or month > current_month:
            fname, header = "index.md", INDEX_HEADER
        else:
            fname, header = "index-%s.md" % month, MONTH_HEADER % month
        with open(os.path.join(log_dir, fname), "w", encoding="utf-8",
                  newline="\n") as f:
            f.write(header + "\n".join(lines) + ("\n" if lines else ""))
        written += len(lines)
    if current_month not in months:
        with open(os.path.join(log_dir, "index.md"), "w", encoding="utf-8",
                  newline="\n") as f:
            f.write(INDEX_HEADER)
    return written


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    known = ("--backfill-summaries", "--refresh-summaries")
    if len(args) != 1 or any(f not in known for f in flags):
        sys.stderr.write("usage: log_backlinks.py <project root> "
                         "[--backfill-summaries | --refresh-summaries]\n")
        return 2
    root = os.path.abspath(args[0])
    log_dir = os.path.join(root, "LOG")
    if not os.path.isdir(log_dir):
        sys.stderr.write("log_backlinks: no LOG/ folder under %s\n" % root)
        return 1

    if "--backfill-summaries" in flags or "--refresh-summaries" in flags:
        from_index, from_heading = backfill_summaries(
            log_dir, refresh="--refresh-summaries" in flags)
        print("log_backlinks: summary fields written into %d record(s) from "
              "their index lines and %d from their headings"
              % (from_index, from_heading))

    index_count = generate_index(log_dir)
    print("log_backlinks: %d index line(s) generated across LOG/index*.md"
          % index_count)

    records = sorted(n for n in os.listdir(log_dir)
                     if n.endswith(".md") and n != OUTPUT
                     and not n.startswith("index"))
    texts = {n: read(os.path.join(log_dir, n)) for n in records}
    openings = index_openings(log_dir)

    keys = []
    seen = set()
    for name in records:
        for slug in SLUG_RE.findall(texts[name]):
            if "-" in slug and slug not in seen:
                seen.add(slug)
                keys.append((slug, re.compile(r"\[" + re.escape(slug) + r"\]")))
    for name, pattern in package_names():
        if name not in seen:
            seen.add(name)
            keys.append((name, pattern))

    out = [HEADER]
    written = 0
    for key, pattern in keys:
        hits = [n for n in records if pattern.search(texts[n])]
        if not hits:
            continue
        written += 1
        out.append("\n## %s\n\n" % key)
        for n in hits:
            out.append("- %s — %s\n" % (n, openings.get(n, "(no index line)")))

    with open(os.path.join(log_dir, OUTPUT), "w", encoding="utf-8",
              newline="\n") as f:
        f.write("".join(out))
    print("log_backlinks: %d key(s) over %d record(s) written to LOG/%s"
          % (written, len(records), OUTPUT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
