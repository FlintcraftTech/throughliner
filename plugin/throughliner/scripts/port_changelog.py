#!/usr/bin/env python3
"""Generate the port-facing changelog for a release.

## What this is for

Someone porting Throughliner to another tool needs to know what changed since
the version they ported from — and the session records already carry exactly
that shape: which file, what changed inside it in behavioural terms, and why.
What was missing was a per-release view of them, filtered to what actually
ships.

**The ship boundary is a folder, which is what makes this derivable rather than
hand-written.** Everything under `plugin/throughliner/` ships; everything else
belongs to the development project. A large share of that project's work is
explicitly host-only — release checklists, the rule gate, the compliance checklist
— so a porter following the session records blind would try to port things that
were never meant to leave.

## Three limits it states about itself, printed in its own header

It says what changed and never how to map it onto another harness — the
translating stays the port's. A change to a Python hook may have no equivalent
on their side at all. And a format-epoch bump means their own users' documents
need migrating, which is theirs to handle: this flags it and stops there.

## How an entry is found

A session's commit hash is written into the session records it produced, so the
records for a commit are the `LOG/` entries whose heading carries that hash. An
entry is included when its own `Files touched:` line names a path under the
plugin package — per entry rather than per commit, because one commit routinely
carries both shipped and host-only work.

Where the records live apart from the product (`--log-root`, a nested project),
their headings carry the other repository's hashes and no hash can match. A
commit the hash match leaves empty then takes the records whose `Files touched:`
names a path it changed and whose own `Date:` or `Recorded` line falls after
the previous shipped commit and no later than this one. A record goes to one
commit only, the earliest that fits, and a record with no readable date is not
matched this way. A record dated after its commit is not matched: a day's grace
was tried, and on the v1.25.0 range its only matches were two records of work
built the day after the release.

Where a commit touches the package but no entry can be matched to it, the commit
is reported on its own subject line and marked as carrying no session record.
Silence there would be the one failure mode that matters: a shipped change the
changelog never mentioned.

## Standard library only

Per this project's scripting constraints. `git` is invoked as a subprocess with
the encoding named explicitly, which this project has been bitten by omitting.

    py plugin/throughliner/scripts/port_changelog.py . --from v1.20.0 --to v1.21.0
"""

import argparse
import os
import re
import subprocess
import sys

# Copied from reorder_queue.py, which is the canonical copy. The duplication is
# deliberate: these scripts run standalone from a copied plugin cache and cannot
# import a shared module, which is also why a shared module was rejected.
for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        # Python < 3.7, or a stream that cannot be reconfigured. Messages then
        # behave as before — degraded, never fatal.
        pass

SHIPPED_PREFIX = "plugin/throughliner/"
LOG_DIR = "LOG"
EPOCH_PATTERN = re.compile(r"^[-+]FORMAT_EPOCH\s*=\s*(\d+)", re.MULTILINE)
HEADING_PATTERN = re.compile(r"^#\s+([0-9a-f]{7,40})\s+[—-]\s+(.*)$")
HOST_ONLY_PATTERN = re.compile(r"host[- ]only", re.IGNORECASE)


def git(project_root, *args):
    """Run one git command and return its stdout, or raise on failure."""
    result = subprocess.run(
        ["git", "-C", project_root] + list(args),
        capture_output=True, encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        raise SystemExit(
            "git %s failed:\n%s" % (" ".join(args), result.stderr.strip()))
    return result.stdout


def shipped_commits(project_root, since, until):
    """Commits in the range that touch the plugin package, oldest first."""
    span = "%s..%s" % (since, until) if since else until
    raw = git(project_root, "log", "--reverse", "--format=%H%x1f%s",
              span, "--", SHIPPED_PREFIX)
    out = []
    for line in raw.splitlines():
        if "\x1f" in line:
            full, subject = line.split("\x1f", 1)
            out.append((full, subject))
    return out


MANIFEST = SHIPPED_PREFIX + ".claude-plugin/plugin.json"


def version_bump_only(project_root, commit, paths):
    """Whether this commit's only shipped change is the manifest's version.

    A rezip stamps a `-testN` suffix onto the version and the release strips it
    again, and neither changes what the plugin does — which is why the installed
    build's content stamp drops the version key before hashing. A changelog
    entry saying "read the diff" for one of those is noise, and this project has
    repealed measures for crying wolf. Any OTHER change to the manifest is
    reported normally.
    """
    if paths != [MANIFEST]:
        return False
    diff = git(project_root, "show", "--format=", "--unified=0", commit,
               "--", MANIFEST)
    changed = [line for line in diff.splitlines()
               if line[:1] in "+-" and not line.startswith(("+++", "---"))]
    return bool(changed) and all('"version"' in line for line in changed)


def epoch_move(project_root, commit):
    """The new FORMAT_EPOCH value where this commit changed it, else None.

    Read from the diff rather than from the file, so the answer is what this
    commit did rather than what the value happens to be now.
    """
    diff = git(project_root, "show", "--format=", "--unified=0", commit,
               "--", SHIPPED_PREFIX + "hooks/session_start.py")
    added = [m.group(1) for m in EPOCH_PATTERN.finditer(diff)
             if m.group(0).startswith("+")]
    return added[-1] if added else None


def read_records(log_path):
    """Every session record under `log_path`, oldest filename first, each with
    the hash its heading is stamped with (or None), its title, its files and
    its own date."""
    try:
        names = sorted(os.listdir(log_path))
    except OSError:
        return []
    records = []
    for name in names:
        if not name.endswith(".md") or name.startswith("index"):
            continue
        try:
            with open(os.path.join(log_path, name), encoding="utf-8") as handle:
                text = strip_front_matter(handle.read())
        except OSError:
            continue
        first = text.split("\n", 1)[0]
        match = HEADING_PATTERN.match(first)
        if match:
            stamped, title = match.group(1), match.group(2).strip()
        else:
            stamped = None
            title = LOOSE_HEADING.sub("", first).strip()
        records.append({
            "file": name,
            "stamped": stamped,
            "title": title,
            "text": text,
            "files": files_touched(text),
            "date": record_date(text),
        })
    return records


# A heading with no hash in its slot: `# <placeholder> — title`, or a bare
# `# title`. Only the leading mark and one slot are dropped.
LOOSE_HEADING = re.compile(r"^#\s+(?:\S+\s+[—-]\s+)?")
# The record's own date line: `Date: 2026-11-19 10:10, read from the clock…`
# or `Recorded 2026-11-19 10:10, read from the clock…`, plain or bold.
RECORD_DATE = re.compile(
    r"^\**(?:Date:|Recorded)\**\s*(\d{4}-\d{2}-\d{2})(?:[ T](\d{2}:\d{2}))?",
    re.MULTILINE)


def record_date(text):
    """The record's own date as `YYYY-MM-DD HH:MM`, or None where it carries
    no `Date:` or `Recorded` line. A date with no time reads as the day's end,
    so a record dated on a commit's day is not placed after it by default."""
    match = RECORD_DATE.search(text)
    if not match:
        return None
    return "%s %s" % (match.group(1), match.group(2) or "23:59")


def hash_matches(stamped, commit):
    """Git abbreviates a hash to whatever length is unambiguous, and the
    records are stamped with the abbreviated form, so the match is a prefix."""
    return bool(stamped) and (commit.startswith(stamped)
                              or stamped.startswith(commit))


def log_entries_for(project_root, commit, log_root=None, fallback=None):
    """Session records for this commit: those whose heading carries its hash,
    and where none does, the records `fallback` gives it.

    `log_root` is where `LOG/` lives when it is not beside the git history —
    a nested project keeps the records in its outer repository and the product
    in the inner. Defaults to `project_root`, which is the flat case.

    `fallback` is `match_by_files_and_date()`'s answer for the whole range, a
    mapping from commit to records. In a nested project the records carry the
    OUTER repository's hash and this script walks the inner one's commits, so
    the hash match finds nothing and the fallback is the only route.
    """
    log_path = os.path.join(log_root or project_root, LOG_DIR)
    found = [record for record in read_records(log_path)
             if hash_matches(record["stamped"], commit)]
    if found or not fallback:
        return found
    return list(fallback.get(commit, []))


def commit_times(project_root, commits, since):
    """`YYYY-MM-DD HH:MM` for each commit, in the committer's own clock, and
    for the `since` ref the range opens after (None where it cannot be read).
    Records are dated from the same machine's clock, so the two compare as
    written."""
    times = {}
    for commit in commits:
        times[commit] = git(project_root, "show", "-s", "--format=%ci",
                            commit).strip()[:16]
    opening = None
    if since:
        probe = subprocess.run(
            ["git", "-C", project_root, "show", "-s", "--format=%ci",
             since + "^{commit}"],
            capture_output=True, encoding="utf-8", errors="replace")
        if probe.returncode == 0:
            opening = probe.stdout.strip()[:16]
    return times, opening


def match_by_files_and_date(project_root, candidates, since, log_root):
    """Records matched to commits where no hash can match: {commit: [record]}.

    `candidates` is [(commit, paths, basenames)] oldest first, every shipped
    commit in the range; one whose paths are None takes no record (a
    version-only bump, or a commit its own hash already matched) and still
    bounds its neighbours' windows. A record belongs to a commit where its
    `Files touched:` names at least one path the commit changed and its own
    date falls after the previous shipped commit's time and no later than
    this commit's. A record is given to one commit only, the earliest whose
    window it falls in; a record with no readable date, or one whose heading
    carries a hash of this range, is left out.
    """
    log_path = os.path.join(log_root, LOG_DIR)
    commits = [commit for commit, _paths, _names in candidates]
    times, opening = commit_times(project_root, commits, since)
    records = [record for record in read_records(log_path)
               if record["date"] and record["files"]
               and not any(hash_matches(record["stamped"], commit)
                           for commit in commits)]
    assigned = {}
    for record in records:
        previous = opening
        for commit, paths, basenames in candidates:
            start, end = previous, times[commit]
            previous = end
            if paths is None:
                continue
            if start and record["date"] <= start:
                continue
            if record["date"] > end:
                continue
            if not entry_is_shipped(record, paths, basenames):
                continue
            assigned.setdefault(commit, []).append(record)
            break
    return assigned


FILES_LABEL = re.compile(r"^\**Files touched:\**\s*", re.IGNORECASE)
FIELD_LABEL = re.compile(r"^\**[A-Z][A-Za-z ]{2,30}:\**\s")


def files_touched(text):
    """The names on an entry's `Files touched:` line.

    Three shapes are in the corpus and all three are read: the label plain or
    bolded, and the list wrapping onto following lines. What comes back is what
    the record says — routinely a bare filename rather than a repo path, since
    the records name a doc by the name a reader would use. Matching those to
    what actually shipped is `shipped_names()`'s job, from git.
    """
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = FILES_LABEL.match(line)
        if not match:
            continue
        collected = [line[match.end():]]
        for following in lines[index + 1:]:
            stripped = following.strip()
            if not stripped or FIELD_LABEL.match(stripped):
                break
            collected.append(stripped)
        block = " ".join(collected)

        # Four shapes are in the corpus: the list inline after the label or
        # starting on the next line, and each name either backticked or bare.
        # Backticks are read first because the wrapped shape puts a prose
        # description after each name, which no comma split survives.
        quoted = [token.strip() for token in re.findall(r"`([^`]+)`", block)]
        names = [token for token in quoted if "." in token or "/" in token]
        if names:
            return names

        for chunk in block.split(","):
            chunk = chunk.strip().strip(".").strip().strip("`").strip()
            chunk = chunk.split(" (")[0].strip()
            if chunk and chunk.lower() not in ("none", "no files"):
                names.append(chunk)
        return names
    return []


def shipped_names(project_root, commit):
    """The plugin-package paths this commit changed, and their basenames.

    Grounded in git rather than in the record's prose: a record names a doc by
    the name a reader would use, so an entry cannot be classified as shipped by
    reading its own file list against a path prefix.
    """
    raw = git(project_root, "show", "--format=", "--name-only", commit,
              "--", SHIPPED_PREFIX)
    paths = [line.strip() for line in raw.splitlines() if line.strip()]
    return paths, {os.path.basename(path) for path in paths}


def entry_is_shipped(entry, paths, basenames):
    """Whether this record describes work inside the plugin package."""
    for name in entry["files"]:
        name = name.replace("\\", "/")
        if name.startswith(SHIPPED_PREFIX) and name in paths:
            return True
        if os.path.basename(name) in basenames:
            return True
    return False


def strip_front_matter(text):
    """The record's text after its leading `---` front-matter block — the
    summary field the index is generated from sits above the heading this
    script reads ([log-index-generated-from-front-matter]). Copied per
    reader, since the scripts run standalone."""
    if not text.startswith("---"):
        return text
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[i + 1:])
    return text


def summary_of(text):
    """The entry's behavioural summary — its first paragraph of prose."""
    body = text.split("\n", 1)[1] if "\n" in text else ""
    for block in body.split("\n\n"):
        block = block.strip()
        if block and not block.startswith("#"):
            return " ".join(block.split())
    return ""


DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}-")
SLUG_SUFFIX = re.compile(r"-(plan|build|\d+)$")


def slug_of(name):
    """The work-item slug a record's filename carries.

    Records are named `<date>-<slug>.md`, with planning records for the same
    item as `<date>-<slug>-plan.md` (and occasional `-build`/`-2` variants).
    Stripping those affixes is what lets a build record and the planning
    record that decided it be matched without any stored index.
    """
    base = DATE_PREFIX.sub("", name[:-3] if name.endswith(".md") else name)
    return SLUG_SUFFIX.sub("", base)


def deciding_record(project_root, entry_file, log_root=None):
    """The planning record for this entry's item, or None.

    The reason a change was made is written where it was decided — the
    planning session's per-item record — and the build record only carries
    the doing. The match is by slug, which is the same retrieval idea the
    development project's own rules write down (search the index for the
    rule's words); here the slug is mechanical where the words are not.

    `log_root` as in `log_entries_for`: where `LOG/` lives when it is not
    beside the git history.
    """
    slug = slug_of(entry_file)
    log_path = os.path.join(log_root or project_root, LOG_DIR)
    candidates = []
    try:
        names = sorted(os.listdir(log_path))
    except OSError:
        return None
    for name in names:
        if not name.endswith(".md") or name == entry_file:
            continue
        if slug_of(name) != slug:
            continue
        if "plan" not in name:
            continue
        candidates.append(name)
    if not candidates:
        return None
    name = candidates[-1]  # newest by the date-prefixed sort
    try:
        with open(os.path.join(log_path, name), encoding="utf-8") as handle:
            text = handle.read()
    except OSError:
        return None
    return {"file": name, "summary": summary_of(text)}


def build(project_root, since, until, log_root=None):
    """The changelog as a list of lines. Empty where nothing shipped.

    Every git read stays on `project_root`; the two `LOG/` reads go to
    `log_root` where one is given, else `project_root`.
    """
    lines = []
    commits = shipped_commits(project_root, since, until)
    shipped = {}
    for commit, _subject in commits:
        paths, basenames = shipped_names(project_root, commit)
        shipped[commit] = (paths, basenames,
                           version_bump_only(project_root, commit, paths))

    # Where the records live apart from the product, their headings carry the
    # other repository's hashes: every commit the hash match leaves empty is
    # offered to the files-and-date match, worked out once for the range.
    fallback = None
    if log_root:
        candidates = []
        for commit, _subject in commits:
            paths, basenames, bump_only = shipped[commit]
            if bump_only or log_entries_for(project_root, commit, log_root):
                candidates.append((commit, None, None))
            else:
                candidates.append((commit, paths, basenames))
        fallback = match_by_files_and_date(project_root, candidates, since,
                                           log_root)

    for commit, subject in commits:
        paths, basenames, bump_only = shipped[commit]
        if bump_only:
            continue
        entries = [entry for entry in log_entries_for(project_root, commit,
                                                      log_root, fallback)
                   if entry_is_shipped(entry, paths, basenames)]
        epoch = epoch_move(project_root, commit)

        if not entries:
            lines.append("### %s — %s" % (commit[:7], subject))
            lines.append("")
            lines.append("No session record could be matched to this commit, "
                         "so there is no behavioural summary for it. Read the "
                         "diff.")
            if epoch:
                lines.append("")
                lines.append("**FORMAT EPOCH -> %s.** Your own users' "
                             "documents need migrating; that is yours to "
                             "handle." % epoch)
            lines.append("")
            continue

        for entry in entries:
            lines.append("### %s — %s" % (commit[:7], entry["title"]))
            lines.append("")
            named = [name for name in entry["files"]
                     if name.replace("\\", "/") in paths
                     or os.path.basename(name) in basenames]
            lines.append("Shipped files: %s" % ", ".join(named))
            if HOST_ONLY_PATTERN.search(entry["text"]):
                lines.append("")
                lines.append("**The record for this change discusses "
                             "host-only reasoning.** Read it before porting: "
                             "part of what it describes may belong to the "
                             "development project rather than to the plugin.")
            summary = summary_of(entry["text"])
            if summary:
                lines.append("")
                lines.append(summary)
            deciding = deciding_record(project_root, entry["file"], log_root)
            if deciding and deciding["summary"]:
                lines.append("")
                lines.append("**Why it was made** (from the record of the "
                             "session that decided it, `LOG/%s`): %s"
                             % (deciding["file"], deciding["summary"]))
            if epoch:
                lines.append("")
                lines.append("**FORMAT EPOCH -> %s.** Your own users' "
                             "documents need migrating; that is yours to "
                             "handle." % epoch)
            lines.append("")
            lines.append("Record: `LOG/%s`" % entry["file"])
            lines.append("")
    return lines


HEADER = """# Port-facing changelog: %s

For anyone running Throughliner on a tool other than Claude Code. Every entry
below is a change inside the shipped plugin package; the development project's
own work is not listed.

Three limits this states about itself:

- it says WHAT changed, never how to map it — the translating stays yours;
- a change to a Python hook may have no equivalent on your side at all;
- a format-epoch bump means your own users' documents need migrating, which is
  yours to handle. It is flagged here and nothing more.
"""


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate the port-facing changelog for a release.")
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument("--from", dest="since",
                        help="the previous release's tag or commit")
    parser.add_argument("--to", dest="until", default="HEAD",
                        help="this release's tag or commit (default: HEAD)")
    parser.add_argument(
        "--as", dest="label", metavar="LABEL",
        help="the name used for --to in the heading, where the tag does "
             "not exist yet — a release generates the changelog before it "
             "tags, so `--to HEAD --as v1.24.0` heads it with the tag")
    parser.add_argument(
        "--catch-up", dest="catch_up", metavar="VERSION",
        help="everything since the version you last ported from, up to HEAD "
             "— for a porter picking up after a gap, possibly spanning "
             "several releases. Takes a tag, a commit, or a bare version "
             "number (1.19.0 is tried as v1.19.0 too).")
    parser.add_argument("--out", help="write to this path instead of stdout")
    parser.add_argument(
        "--log-root", dest="log_root", metavar="PATH",
        help="the folder holding LOG/, where it is not the project root — a "
             "nested project keeps its records in the outer repository and "
             "the product in the inner (default: the project root)")
    args = parser.parse_args(argv)

    since = args.since
    if args.catch_up:
        if since:
            parser.error("--catch-up replaces --from; pass one or the other")
        since = args.catch_up
        # A porter reasonably types the bare version number; git knows the tag.
        probe = subprocess.run(
            ["git", "-C", args.project_root, "rev-parse", "--verify",
             since + "^{commit}"],
            capture_output=True, encoding="utf-8", errors="replace")
        if probe.returncode != 0:
            since = "v" + args.catch_up
    if not since:
        parser.error("one of --from or --catch-up is required")

    lines = build(args.project_root, since, args.until, args.log_root)
    args.since = since

    if not lines:
        print("Nothing shipped between %s and %s — every commit in that range "
              "touches only the development project's own files, so there is "
              "no changelog to publish."
              % (args.since, args.until))
        return 0

    span = "%s..%s" % (args.since, args.label or args.until)
    document = HEADER % span + "\n" + "\n".join(lines).rstrip() + "\n"

    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(document)
        print("Wrote %s (%d entr%s)."
              % (args.out, document.count("\n### "),
                 "y" if document.count("\n### ") == 1 else "ies"))
    else:
        sys.stdout.write(document)
    return 0


if __name__ == "__main__":
    sys.exit(main())
