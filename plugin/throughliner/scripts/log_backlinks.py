#!/usr/bin/env python3
"""Generate LOG/backlinks.md: a map from each queue slug and each of the
plugin's own names to the session records that name it.

Usage:
    python log_backlinks.py <project root>

Why this exists ([log-backlink-index-generated]): the planning decision step
greps the index files for a mechanism's distinctive words, and an entry
indexed under other phrasing is missed. Links in the record go one way and
nothing computes backlinks. This reads every record and index file, collects
a key set — every `[slug]` seen anywhere, each hook filename stem under the
plugin's `hooks/`, each skill folder name under `skills/`, each tool name the
state server advertises — and writes one heading per key with one line per
record naming it. Computed from the artifacts every time, never stored by
hand, and the records themselves are never edited.

The limit, stated: a record that names a mechanism by neither its slug nor
its package name is still not reached.

Standard library only. UTF-8 reconfiguration copied from reorder_queue.py.
"""

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
SLUG_RE = re.compile(r"\[([a-z0-9][a-z0-9-]*)\]")
TOOL_NAME_RE = re.compile(r'^\s*"name":\s*"([a-z_][a-z0-9_]*)"', re.MULTILINE)
INDEX_LINE_RE = re.compile(r"^- .*?→\s*(\S+\.md)\s*$")


def read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


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


def index_openings(log_dir):
    """Record filename -> the opening words of its index line."""
    openings = {}
    for name in sorted(os.listdir(log_dir)):
        if not (name == "index.md" or re.match(r"^index-\d{4}-\d{2}\.md$", name)):
            continue
        for line in read(os.path.join(log_dir, name)).splitlines():
            m = INDEX_LINE_RE.match(line.strip())
            if not m:
                continue
            body = line.strip()[2:].split("→")[0].strip()
            words = " ".join(body.split()[:12])
            openings.setdefault(m.group(1), words)
    return openings


def main(argv):
    if len(argv) != 1:
        sys.stderr.write("usage: log_backlinks.py <project root>\n")
        return 2
    root = os.path.abspath(argv[0])
    log_dir = os.path.join(root, "LOG")
    if not os.path.isdir(log_dir):
        sys.stderr.write("log_backlinks: no LOG/ folder under %s\n" % root)
        return 1

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
