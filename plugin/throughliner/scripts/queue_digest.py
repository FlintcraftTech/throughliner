#!/usr/bin/env python3
"""Print a one-line-per-item digest of QUEUE.md.

Sibling to reorder_queue.py: a mechanical reader alongside the mechanical
writer. /plan's read-state runs this instead of paging the whole queue, and
can re-run it at any point in the session.

Why this exists. Reading QUEUE.md whole costs tens of thousands of tokens and
most of it is rationale prose, which queue-wide reasoning never touches — the
droppable skim, the ordering, and the below-line revisit all read headings,
tags, blockers and flags. This prints those and nothing else.

Why it satisfies the page-to-the-end rule rather than trading it away. That
rule exists because a truncated read is indistinguishable from a complete one
to whatever reasons over it. A digest generated from the whole file by code
cannot be silently truncated, so the guarantee is stronger than paging gives.
The field list is fixed by what queue-wide reasoning actually consumes; a step
needing an item's prose reads that item's prose at the moment it presents it.

Every field here reports a FACT, never a VERDICT. "Cites [X]; [X] has a LOG
entry" is a lookup anyone can check; "ready to lift" is an interpretation, and
interpreting dependency conditions was retired from this method along with the
classifier built to do it. No field may become a threshold either — "more than
three citations", "older than thirty days" — because a number with no
derivation behind it is exactly what this project bans. Whoever edits this
script next inherits that constraint.

Usage:
    python queue_digest.py <QUEUE.md path>

Exit codes: 0 on success, 1 on a usage or read error.
"""

import os
import re
import subprocess
import sys

# Force UTF-8 on the console output, once, before anything is printed. The
# digest echoes item headings, which routinely carry em-dashes and arrows; on
# Windows an unconfigured stream falls back to the console code page and a
# heading containing one crashes the run. Same fix, same reason, as
# reorder_queue.py. errors='replace' keeps a console that genuinely cannot
# render a character from turning a cosmetic problem into a crash.
for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        # Python < 3.7, or a stream that cannot be reconfigured (a pipe, or a
        # test harness replacement). Degraded, never fatal.
        pass

SLUG_RE = re.compile(r"\[([a-z0-9][a-z0-9-]*)\]\s*$")
ITEM_RE = re.compile(r"^####\s+\S")
# `Blocked by:` takes ONE OR MORE slugs, and an item lifts only when every one
# of them resolves. Matched as a line, then every `[slug]` on it is read out; a
# single-slug pattern silently dropped the rest, which is how a group condition
# would report liftable with most of the group outstanding.
BLOCKED_RE = re.compile(r"^Blocked by:", re.IGNORECASE)
SLUG_REF_RE = re.compile(r"\[([a-z0-9][a-z0-9-]*)\]")
# `Not before: YYYY-MM-DD` — the second holding fact, and the only one that
# resolves without anyone confirming it. Printed with whether the date has
# passed, so the lift is a fact on the line rather than a date the reader has
# to compare against today by hand.
NOT_BEFORE_RE = re.compile(r"^Not before:\s*(\S+)\s*$", re.IGNORECASE)
# `Cycle: [slug]` — the capture is a named cycle's material rather than a
# pending decision, so that cycle's turns draw from it and the planning ladder
# passes over it. Printed as a bare fact: whether the named definition exists
# is what decides the pass-over, and a cycle deleted from the doc releases its
# material by itself.
CYCLE_RE = re.compile(r"^Cycle:\s*\[?([a-z0-9][a-z0-9-]*)\]?\s*$",
                      re.IGNORECASE)
FLAG_RE = re.compile(r"^Red flag\s*·\s*State:\s*(\w+)", re.IGNORECASE)
FLAVOR_RE = re.compile(r"^\[(audit|user|freeform|co-write)\]\s*", re.IGNORECASE)
# "Runs alone" — the item is ready, but /next must not build it alongside other
# work. Printed on the item's digest line because a solo item changes how much
# of the ready region a single run can actually clear, which is exactly what a
# planning session is deciding when it reads the digest.
RUNS_ALONE_RE = re.compile(r"^\**Runs alone\**\s*$", re.IGNORECASE)
# The readiness marker. Matched as a whole line, never as a substring: an item's
# own prose may legitimately quote the marker text while describing how the queue
# works, and a substring test would take that sentence as the readiness line and
# silently move it. Same anchored predicate reorder_queue.py uses.
MARKER_RE = re.compile(r"^---\s*Cleared to run above this line\s*---\s*$")

# Placement-contradiction signals. Each is a contradiction the queue's own text
# already contains, so the check reports something rather than nothing — which
# is why this is a detector and not a duty to review periodically.
#
# An item is examined on the way into Processed and never again. A gate on the
# door and no inspection of the room are two different failures, and only the
# first was built. The live instance that produced these: an item sat cleared to
# run carrying, in its own bold text, "it must not be built as written."
DO_NOT_BUILD_PHRASES = (
    "must not be built as written",
    "must not be built",
    "returned unbuilt",
    "cannot be scoped by a build",
)
# The keep-check's second limb, failing after the fact: an item whose Files line
# names nothing, or whose build list is its own design's output, says outright
# that there is nothing for a build to change.
NO_FILES_PHRASES = (
    "none yet",
    "the design's output",
    "design's output",
)
FILES_LINE_RE = re.compile(r"^\**Files\b[^:]*:\**\s*(.*)$", re.IGNORECASE)

# A research file cited in a work item's prose. Research is filed because it
# will be re-read and reused, so a research file is an upstream dependency of
# everything scoped against it — but citation runs one way. When a finding is
# superseded there is no path back to the decisions built on it, and those
# decisions do not announce that they rest on anything. The convention that
# closes it: a superseded research file gains a `Superseded by:` line at its
# top, written at the moment someone already has the file open to re-validate
# it, and this check reads that line back.
RESEARCH_CITE_RE = re.compile(
    r"(?:workshop/)?resources/research/([a-z0-9][a-z0-9._-]*\.md)")
SUPERSEDED_RE = re.compile(r"^\**Superseded by:?\**\s*(.+)$",
                           re.IGNORECASE | re.MULTILINE)


def _research_path(root, name):
    """Where a cited research finding lives, new home first.

    Findings live under `workshop/resources/research/`. A project that has not
    yet run the migration still has them at the old root `resources/research/`,
    and an item written before the move still cites the old path — so both are
    tried and the citation keeps resolving either way.
    """
    new = os.path.join(root, "workshop", "resources", "research", name)
    if os.path.exists(new):
        return new
    return os.path.join(root, "resources", "research", name)

# A finding another project owns, copied in rather than pointed at. The copy
# carries a `Copied from:` line naming the owning project — never a path, since
# the always-loaded scrub list bans a path that identifies a person or an
# organisation from a committed document, which is the same reason the address
# book lives inside the gitignored mailbox.
#
# What this flag says is that the item rests on a SNAPSHOT: a copy taken on a
# date. It is a permanent label and NOT a staleness check, and must never be
# described as one — nothing reads the other project's folder, so nothing here
# can tell whether the original has changed since.
COPIED_FROM_RE = re.compile(r"^\**Copied from:?\**\s*(.+)$",
                            re.IGNORECASE | re.MULTILINE)

# Any [slug] appearing in an item's prose. The always-loaded rules require a
# cross-reference to be written as a slug in prose — they say a slug in prose is
# the only thing that makes a cross-reference exist at all — so prose is where
# the dependency information actually lives, and reading only `Blocked by:`
# lines would miss most of it.
SLUG_CITE_RE = re.compile(r"\[([a-z0-9][a-z0-9-]*)\]")
# A path inside a Files line. Files lines write paths in backticks, mixed with
# prose describing what changes in each, so the backticks are what separates a
# path from the sentence around it.
FILES_PATH_RE = re.compile(r"`([^`]+)`")
# What counts as a path inside those backticks. Files lines also backtick
# skill names (`/plan`) and field names, so a bare "contains a slash" test
# collects those too; a real path ends in a file extension or a folder slash.
PATH_SHAPE_RE = re.compile(r"(\.(md|py|json|js|txt|ya?ml|toml)|/)$", re.IGNORECASE)
# The flavor tags are written in the same square brackets as a slug, so prose
# saying an item is `[freeform]` would otherwise read as a citation of a slug
# by that name — and this project has a LOG entry that would resolve it.
FLAVOR_TAGS = frozenset({"audit", "user", "freeform", "co-write"})
# A LOG entry filename: <date>-<slug>.md. A slug having an entry means it
# shipped, which is the whole resolve — no history scan needed.
LOG_ENTRY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-([a-z0-9][a-z0-9-]*)\.md$")
# A record's kind suffix, or the legacy numeric one. A slug's second record
# cannot reuse the bare filename, so /done suffixes the record's kind —
# and older records took a bare number instead. Both are stripped so the
# record still attributes to its slug; without this a second record is
# invisible to the digest and its item reads as never written about.
# Only these three exact shapes are stripped. Prefix-matching arbitrary
# suffixes was refused: a slug that extends another slug would misattribute.
RECORD_SUFFIX_RE = re.compile(r"-(?:plan|build|\d+)$")
# A bare date on its own line in the git log pass below: the commit's date,
# emitted by --format=%as ahead of that commit's patch.
GIT_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse(path):
    """Read the queue into a list of item dicts. Raises OSError if unreadable."""
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    items = []
    section = None
    above_marker = True
    current = None

    for lineno, raw in enumerate(lines, start=1):
        stripped = raw.strip()

        if re.match(r"^##\s+Processed\b", stripped, re.IGNORECASE):
            section, above_marker, current = "Processed", True, None
            continue
        if re.match(r"^##\s+Unprocessed\b", stripped, re.IGNORECASE):
            section, current = "Unprocessed", None
            continue
        if MARKER_RE.match(stripped):
            above_marker, current = False, None
            continue

        if ITEM_RE.match(stripped):
            if section is None:
                current = None
                continue
            heading = re.sub(r"^#+\s+", "", stripped)
            slug_match = SLUG_RE.search(heading)
            slug = slug_match.group(1) if slug_match else None
            heading = SLUG_RE.sub("", heading).strip()
            flavor_match = FLAVOR_RE.match(heading)
            flavor = flavor_match.group(1).lower() if flavor_match else "build"
            heading = FLAVOR_RE.sub("", heading).strip()
            current = {
                "section": section,
                # Only meaningful in Processed; Unprocessed has no marker.
                "cleared": above_marker if section == "Processed" else None,
                "flavor": flavor,
                "heading": heading,
                "slug": slug,
                # A LIST — one or more blockers, all of which must resolve.
                "blocked_by": [],
                # The `Blocked by:` lines as written. Kept because an item can
                # carry the line and still yield no blockers — an unbracketed
                # slug matches no `[slug]` — and the two states are otherwise
                # indistinguishable from `blocked_by` alone.
                "blocked_raw": [],
                "not_before": None,
                "flag": None,
                "cycle": None,
                "runs_alone": False,
                # Lowercased prose, for the placement-contradiction checks. Not
                # printed — the digest stays one line per item.
                "prose": [],
                "prose_at": [],
                "files_line": None,
                "files_line_raw": None,
                # Line span, for the ladder's above-median longest-first rung.
                # The arithmetic is the point: last line minus first, with
                # nothing counting words and nothing reading the entry to place
                # it. `last_line` is advanced by every line that belongs to this
                # entry, so the span is closed by whatever ends the entry.
                "first_line": lineno,
                "last_line": lineno,
            }
            items.append(current)
            continue

        if current is not None and stripped:
            current["last_line"] = lineno

        if current is not None:
            if BLOCKED_RE.match(stripped):
                current["blocked_raw"].append(stripped)
                for ref in SLUG_REF_RE.findall(stripped):
                    if ref not in current["blocked_by"]:
                        current["blocked_by"].append(ref)
            not_before = NOT_BEFORE_RE.match(stripped)
            if not_before:
                current["not_before"] = not_before.group(1).strip()
            cycle = CYCLE_RE.match(stripped)
            if cycle:
                current["cycle"] = cycle.group(1).lower()
            flag = FLAG_RE.match(stripped)
            if flag:
                current["flag"] = flag.group(1).lower()
            if RUNS_ALONE_RE.match(stripped):
                current["runs_alone"] = True
            files = FILES_LINE_RE.match(stripped)
            if files and current["files_line"] is None:
                current["files_line"] = files.group(1).lower()
                # The same text with its capitals intact, for printing. The
                # matching copy above is lowercased so the phrase checks can
                # compare case-insensitively, and the paths ride along with it
                # — which is why the digest used to report `spec.md` and
                # `claude.md` for files that are SPEC.md and CLAUDE.md.
                current["files_line_raw"] = files.group(1)
            if stripped:
                current["prose"].append(stripped.lower())
                # Line number and original casing, so a flag can say WHERE it
                # fired and quote what it matched. Locating one flagged phrase
                # by hand cost three round-trips, and the first repair fixed
                # the wrong occurrence because the item contained it twice.
                current["prose_at"].append((lineno, stripped))

    return items


def _self_referential_phrase(item):
    """A do-not-build phrase this item says about ITSELF, or None.

    Precision matters more than reach here. Queue prose routinely quotes another
    item's text — one item's rationale for building a detector quoted the very
    words the detector looks for — and a flag that fires on a discussion of a
    problem, rather than on the problem, is how a lint becomes noise people learn
    to scroll past. That is the one real cost weighed against building this.

    The discriminator is mechanical: a slug reference appearing BEFORE the phrase
    on the same line means the sentence is about that other item. A slug after
    the phrase is a cross-reference hanging off a statement about this item, so
    it does not suppress.

    A second discriminator covers a different failure — the phrase matching as a
    substring of itself plus the next word. "Must not be built into this item"
    says other work stays out, which is the OPPOSITE of what this check reads,
    and the slug discriminator cannot see it: there is no slug, and the sentence
    genuinely is about this item. Built-into means folded-into, a different verb
    sense, so a following "into" suppresses the match.
    """
    for idx, line in enumerate(item["prose"]):
        for phrase in DO_NOT_BUILD_PHRASES:
            at = line.find(phrase)
            if at == -1:
                continue
            if line[at + len(phrase):].lstrip().startswith("into"):
                continue
            before = line[:at]
            others = [
                s for s in re.findall(r"\[([a-z0-9][a-z0-9-]*)\]", before)
                if s != item["slug"]
            ]
            if others:
                continue
            # Where it fired and what it matched, not just the phrase. An item
            # can carry the same phrase twice, so the phrase alone sends a
            # reader to the wrong occurrence — which happened.
            lineno, raw = (item["prose_at"][idx] if idx < len(item["prose_at"])
                           else (None, line))
            return phrase, lineno, raw
    return None


def research_cited(item):
    """Research filenames this item names in its prose, in order, deduplicated.

    Same coverage limit as the superseded check below: it reaches an item that
    NAMES a research file. An item that restates a finding in its own words
    cites nothing and is invisible here, which is the failure this printing
    exists to make visible rather than to detect.
    """
    out, seen = [], set()
    for line in item["prose"]:
        for name in RESEARCH_CITE_RE.findall(line):
            # index.md is the shelf, not a finding. An item naming it has said
            # where to look, not what it rests on.
            if name != "index.md" and name not in seen:
                seen.add(name)
                out.append(name)
    return out


def _superseded_research(item, root):
    """Research files this item cites that carry a `Superseded by:` line.

    Returns a list of (filename, what superseded it).

    COVERAGE LIMIT, stated here and in the digest's own output because it must
    never be read as complete: this catches only items that NAME the research
    file in their prose. An item scoped on a finding it never cites stays
    invisible, and nothing here reaches it.
    """
    if not root:
        return []
    hits, seen = [], set()
    for line in item["prose"]:
        for name in RESEARCH_CITE_RE.findall(line):
            if name in seen:
                continue
            seen.add(name)
            path = _research_path(root, name)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    # The line sits at the top of the file, so reading the
                    # opening is enough and a large file costs nothing.
                    head = f.read(4000)
            except OSError:
                continue
            match = SUPERSEDED_RE.search(head)
            if match:
                # A superseded note legitimately explains WHAT was superseded
                # and what still stands, so it can run to a paragraph. The
                # digest is one line per finding, so show the head of it and
                # let the reader open the file for the rest.
                by = " ".join(match.group(1).split())
                if len(by) > 90:
                    by = by[:90].rstrip() + "…"
                hits.append((name, by))
    return hits


def _snapshot_research(item, root):
    """Research files this item cites that are copies another project owns.

    Returns a list of (filename, the owning project as the line names it).

    Same coverage limit as the superseded check above, and the same reason: it
    reaches an item that NAMES the file. An item resting on a copied finding it
    never cites stays invisible.

    Reads the same head of the file as the superseded check, so an item citing
    both pays one read per file rather than two.
    """
    if not root:
        return []
    hits, seen = [], set()
    for line in item["prose"]:
        for name in RESEARCH_CITE_RE.findall(line):
            if name in seen:
                continue
            seen.add(name)
            path = _research_path(root, name)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    head = f.read(4000)
            except OSError:
                continue
            match = COPIED_FROM_RE.search(head)
            if match:
                owner = " ".join(match.group(1).split())
                if len(owner) > 90:
                    owner = owner[:90].rstrip() + "…"
                hits.append((name, owner))
    return hits


def shipped_slugs(root, wanted=None):
    """Slugs that have a LOG entry, mapped to what KIND of record it is.

    The name is kept for the references to it elsewhere in the queue; what it
    returns is deliberately not a set of shipped slugs, because that was the
    defect.

    A record existing says only that a session wrote about that slug. It does
    not say the work was built: a planning session writes a record for each
    item it PROCESSES and a build writes one for each item it BUILDS, and both
    are named `<date>-<slug>.md`, so the filename cannot tell them apart. The
    body has to be read.

        "built"      the entry carries `Files touched:`
        "processed"  it carries `Work processed:` and not `Files touched:`
        "unknown"    it carries neither — an older format, reported as found
                     but unclassified rather than guessed at

    A slug's second record cannot take the bare `<date>-<slug>.md` name, so it
    carries a kind suffix (`-plan` / `-build`) or, in older records, a bare
    number. Those suffixes are stripped before the slug is read, so a second
    record attributes to its item instead of to a slug nothing cites.

    `wanted` bounds which entries are opened, to the slugs the caller will
    actually print. Reading every entry costs megabytes to answer a handful of
    citations. Passing None reads them all. Degrades to an empty mapping where
    there is no LOG/ folder at all.
    """
    if not root:
        return {}
    kinds = {}
    folder = os.path.join(root, "LOG")
    try:
        names = os.listdir(folder)
    except OSError:
        return {}
    for name in names:
        match = LOG_ENTRY_RE.match(name)
        if not match:
            continue
        slug = RECORD_SUFFIX_RE.sub("", match.group(1))
        if wanted is not None and slug not in wanted:
            continue
        try:
            with open(os.path.join(folder, name), "r", encoding="utf-8") as f:
                body = f.read()
        except OSError:
            kinds.setdefault(slug, "unknown")
            continue
        if "Files touched:" in body:
            kind = "built"
        elif "Work processed:" in body:
            kind = "processed"
        else:
            kind = "unknown"
        # A slug with several entries is built if any one of them built it —
        # an item processed in planning and built later has both records, and
        # the built one is the answer.
        if kinds.get(slug) != "built":
            kinds[slug] = kind
    return kinds


def first_seen(root, queue_path, held_dates=None):
    """First date each slug's heading appears in QUEUE.md, as {slug: date}.

    When `held_dates` is passed a dict, it is filled with {slug: date} for the
    first date that slug's item was seen carrying a hold — a `Blocked by:` or
    `Not before:` line — off the same pass. That date is what turns "four items
    are held" into "held since the 14th", which is the difference between
    background noise and something a reader acts on: a bare count was printed
    at every session start while a chain sat stuck for a day and nobody noticed.

    **Attribution is partial, and the caller states it rather than hiding it.**
    With no diff context, a hold line can only be attributed to an item when the
    two were added together — which is the ordinary case, since an item is
    normally written already held. An item that was cleared and later held by a
    line added on its own gets no date, and prints none. A missing date is
    therefore "not known", never "not held".

    One git pass for the whole queue, not one per slug. The per-slug form
    (`git log -S"[slug]"`) costs about a tenth of a second each and this script
    re-runs several times a session; walking the queue's own patch history once
    returns every item's date together.

    Degrades quietly and completely: a project may not be a git repository, may
    have no git on PATH, or may have a QUEUE.md that was never committed. Any of
    those returns {} — no date on any line, no error, no noise.
    """
    if not root:
        return {}
    try:
        proc = subprocess.run(
            ["git", "log", "--reverse", "--format=%as", "-U0", "-p", "--",
             os.path.basename(queue_path)],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return {}
    if proc.returncode != 0 or not proc.stdout:
        return {}

    dates = {}
    date = None
    # The slug of the item whose heading was added in the run of added lines
    # currently being read. Reset by anything that ends that run, so a hold
    # line is only ever attributed to a heading added beside it.
    pending_slug = None
    for line in proc.stdout.splitlines():
        if GIT_DATE_RE.match(line):
            date = line
            pending_slug = None
            continue
        if not line.startswith("+"):
            pending_slug = None
            continue
        if line.startswith("+####"):
            match = SLUG_RE.search(line.rstrip())
            pending_slug = match.group(1) if match else None
            if match and date:
                dates.setdefault(match.group(1), date)
            continue
        if held_dates is not None and pending_slug and date:
            body = line[1:].strip()
            if BLOCKED_RE.match(body) or NOT_BEFORE_RE.match(body):
                held_dates.setdefault(pending_slug, date)
    return dates


def citations(item):
    """Slugs this item's prose names, excluding its own. Order preserved."""
    seen, out = set(), []
    for line in item["prose"]:
        for slug in SLUG_CITE_RE.findall(line):
            if slug == item["slug"] or slug in seen or slug in FLAVOR_TAGS:
                continue
            seen.add(slug)
            out.append(slug)
    return out


def files_named(items):
    """{path: [slugs]} for every path named by TWO OR MORE items.

    A file named by one item surfaces nothing, and a per-item field would be
    noise on a line-per-item digest. What earns its own block is the overlap:
    two items naming the same file are merge candidates, and merging them means
    one run touches that file once instead of twice.

    **Grouped case-insensitively, printed as written.** Two items naming the
    same file in different casing are still the same file and still merge
    candidates, so the grouping key stays lowercased — but the path shown is the
    one the item actually wrote, because a reader who copies `spec.md` or
    `claude.md` off this block is copying a filename that does not exist.
    """
    by_path = {}
    display = {}
    for item in items:
        raw_line = item["files_line_raw"] or item["files_line"]
        if not raw_line:
            continue
        slug = item["slug"] or "NO-SLUG"
        for path in FILES_PATH_RE.findall(raw_line):
            path = path.strip()
            if not PATH_SHAPE_RE.search(path):
                continue
            key = path.lower()
            display.setdefault(key, path)
            by_path.setdefault(key, [])
            if slug not in by_path[key]:
                by_path[key].append(slug)
    return {display[k]: s for k, s in sorted(by_path.items()) if len(s) > 1}


def contradictions(items, root=""):
    """Items whose placement contradicts their own text. Flags, never decides.

    Moving an item out of Processed is a fate decision and stays the user's at
    /plan, so this reports and stops there.
    """
    found = []
    for item in items:
        slug = item["slug"] or "NO-SLUG"

        for name, by in _superseded_research(item, root):
            found.append(
                f"[{slug}] is scoped against workshop/resources/research/{name}, which "
                f"is marked superseded by {by} — re-read the item's premise "
                "before building it"
            )

        for name, owner in _snapshot_research(item, root):
            found.append(
                f"[{slug}] rests on a SNAPSHOT: workshop/resources/research/{name} is a "
                f"copy of a finding owned by {owner}. That is a permanent "
                "label and not a staleness check — nothing here reads the "
                "other project, so whether the original has moved on is "
                "unknown rather than checked"
            )

        if item["section"] == "Processed":
            hit = _self_referential_phrase(item)
            if hit:
                phrase, lineno, raw = hit
                where = f" (line {lineno})" if lineno else ""
                found.append(
                    f"[{slug}] sits in Processed but its own text says "
                    f'"{phrase}"{where}: {raw}'
                )

            # The cleared-item-with-no-build-block report is retired
            # (2026-08-27, [builds-read-the-queue-again]). A run reads each item
            # whole from the queue now, so there is no block that can be
            # missing; whether an item says what changes inside its files is
            # judgment the decision step makes, not something a delimiter test
            # can answer.

            # A build block the format migration wrote under an existing item
            # carries a line saying it was never checked at planning; a cleared
            # item still carrying it has never passed the buildability check.
            if item["cleared"] and any(
                    "written by the format migration" in p
                    and "not yet checked at planning" in p
                    for p in item["prose"]):
                found.append(
                    f"[{slug}] is cleared but its build block was written by a "
                    "migration and never checked — re-run the buildability "
                    "check before a run builds it"
                )

            files_line = item["files_line"]
            if files_line is not None:
                for phrase in NO_FILES_PHRASES:
                    if phrase in files_line:
                        shown = item["files_line_raw"] or files_line
                        found.append(
                            f"[{slug}] sits in Processed but its Files line "
                            f'says "{phrase}" — nothing for a build to change: '
                            f"{shown}"
                        )
                        break

        # A hold nothing can read is a permanent hold. An item below the line
        # is never built, and the below-the-line revisit works by reading what
        # each held item NAMES — so an item whose `Blocked by:` line names
        # nothing resolvable has no arm of the revisit at all: not lifted, not
        # surfaced, not flagged. The longest it sits the more it reads as
        # deliberate deferral rather than a typo. Reported here as a
        # contradiction between the item's placement and its own text, which is
        # the block that already exists for exactly that.
        for raw in item["blocked_raw"]:
            if not SLUG_REF_RE.search(raw):
                found.append(
                    f"[{slug}] carries a Blocked by: line naming no slug in "
                    f"brackets, so nothing reads it as held: {raw} — the "
                    "blocker's name goes in square brackets"
                )

        if _blocker_loop(item, items):
            found.append(
                f"[{slug}] sits in a loop of blockers that comes back to "
                "itself — nothing in the loop can ever be released"
            )

        # Newly filed work can invalidate work already cleared to run, and
        # nothing else looks. The recorded instance: filing a capture about a
        # bot limitation revealed that a cleared item could not be built as
        # written, and it was caught only because one session happened to hold
        # both in view — the condition a fresh short session never has.
        #
        # The crossing is arithmetic on data already computed: the capture's
        # cited slugs, and which items sit in the cleared region.
        for cited in _cites_cleared(item, items):
            found.append(
                f"[{slug}] is a capture whose prose names [{cited}], which is "
                "cleared to run — re-read that item's premise before a run "
                "builds it"
            )

    return found


def _cites_cleared(item, items):
    """Slugs this Unprocessed capture names that sit in the cleared region."""
    if item["section"] != "Unprocessed":
        return []
    cleared = {i["slug"] for i in items
               if i["section"] == "Processed" and i["cleared"] and i["slug"]}
    seen, hits = set(), []
    for line in item["prose"]:
        for ref in SLUG_REF_RE.findall(line):
            if ref in cleared and ref != item["slug"] and ref not in seen:
                seen.add(ref)
                hits.append(ref)
    return hits


def _blocker_loop(item, items):
    """True where following this item's blockers revisits a slug already seen.

    A chain of held items is NOT reported. Every held item's own digest line
    already prints `Blocked by: [X] -> Processed/held`, so the chain is on the
    page item by item; restating it under a heading reading *contradiction*
    duplicated a line the reader had one row above, and fired on correct work —
    a deliberate pacing chain, built on the user's instruction, produced three of
    these on every run. A flag that fires on correct work gets learned past, and
    then a real one arrives looking exactly like the three that are always there.

    What survives is the distinction plan.md already draws: a chain that
    terminates is slow, a chain that loops never resolves. Terminating anywhere
    — Unprocessed, cleared, or a blocker that resolves to nothing — means the
    chain releases when that end does, and nothing is reported. Revisiting a slug
    means it never releases. Purely mechanical; no interpretation.

    An absent blocker is deliberately left alone here: a chain ending in a slug
    that resolves to nothing is a wrong reference rather than a loop, and it
    already has two homes — session_start names held items whose blocker is in
    neither section, and plan.md's below-the-line revisit treats it as a fault to
    fix that session.
    """
    by_slug = {i["slug"]: i for i in items if i["slug"]}

    # Depth-first over the blocker graph, because an item may name several
    # blockers and a cycle can run through any one of them.
    #
    # The set tracked is the CURRENT PATH — added on descent, removed on unwind
    # — and never every node visited. A visited-set reports a converging chain
    # as a loop: where C is blocked by A and B, and B is also blocked by A, A is
    # reached twice by two different routes and the second arrival looks
    # identical to a cycle. Nothing in that shape fails to release — A ships,
    # then B, then C — and it is an ordinary way to express "these three must
    # land in this order". A slug on the current path is genuinely waiting on
    # itself; a slug merely seen before is not.
    def walk(node, path):
        if node is None or not node["blocked_by"]:
            return False
        if node["slug"] in path:
            return True
        path.add(node["slug"])
        for ref in node["blocked_by"]:
            if walk(by_slug.get(ref), path):
                return True
        path.discard(node["slug"])
        return False

    return walk(item, set())


def not_before_state(raw):
    """Whether a `Not before:` date has arrived, as a printable phrase.

    Computed rather than left to the reader: a date is the one holding fact
    that resolves itself, so the digest can say the item is ready without
    anyone comparing it against today by hand. An unreadable date says so —
    the queue lint reports it at the edit that wrote it, and a digest that
    quietly ignored it would hold the item forever with nothing on the line.
    """
    import datetime

    try:
        when = datetime.date.fromisoformat(raw)
    except ValueError:
        return "NOT A DATE (YYYY-MM-DD expected)"
    today = datetime.date.today()
    if when <= today:
        return "passed, ready to lift"
    return f"{(when - today).days} day(s) away"


def entry_lines(item):
    """One entry's length, as last line minus first, inclusive.

    The arithmetic and nothing else — no word counting, no reading the entry to
    judge how substantial it looks. Computed here so the ladder's rung reads a
    field rather than anyone subtracting two numbers by hand and getting a
    different answer each time.
    """
    return item["last_line"] - item["first_line"] + 1


def median_lines(items):
    """The median entry length of one section, or None when it is empty.

    A proportion of the thing it governs, which is what the derivation rule
    admits; a bare figure like "twelve lines and over" is what it bans. The
    ladder partitions its long-and-old rung here so that the rung terminates.
    """
    return _median(sorted(entry_lines(i) for i in items))


def _median(values):
    """The middle value of a sorted list, or None when it is empty."""
    if not values:
        return None
    mid = len(values) // 2
    if len(values) % 2:
        return values[mid]
    return values[mid - 1] + (values[mid] - values[mid - 1]) // 2


def median_first_seen(items, ages):
    """The section's median first-seen date, or None when it cannot be had.

    The ladder's rung 3 is an intersection of two medians — at or above the
    section's median line count AND at or above its median age — so the age half
    needs a computed field exactly as the length half does. Without it the rung
    reads a date per entry and nothing to compare it against, which puts the
    median back in someone's head; the whole point of the ladder is that every
    rung reads a field or subtracts two numbers.

    Both are proportions of the section they govern, which is what the
    derivation rule admits. A bare cut-off like "filed before March" is what it
    bans.

    Entries whose first-seen date could not be attributed are left out of the
    calculation rather than defaulted, so an unattributable date never drags the
    median in either direction.
    """
    dates = sorted(
        ages[i["slug"]] for i in items
        if i["slug"] and i["slug"] in ages
    )
    if not dates:
        return None
    # Dates are ISO strings, so the middle element is the median for an odd
    # count. For an even count the lower of the two middles is taken rather
    # than a midpoint invented between them: a date halfway between two real
    # dates is not a date anything here filed, and "at or above" only needs a
    # boundary that partitions, not one that averages.
    return dates[(len(dates) - 1) // 2]


def locate(slug, items, kinds=None):
    """Where a slug sits, for resolving a Blocked by: reference.

    A blocker that has left the queue is reported with the KIND of record it
    left behind, never as bare absence. The below-the-line revisit lifts an
    item when its blockers have resolved, and a blocker that a planning session
    merely processed has not resolved — reading a record's existence as proof
    of building would release work whose dependency is still outstanding.
    """
    for item in items:
        if item["slug"] == slug:
            if item["section"] == "Unprocessed":
                return "Unprocessed"
            return "Processed/cleared" if item["cleared"] else "Processed/held"
    kind = (kinds or {}).get(slug)
    if kind == "built":
        return "ABSENT, built"
    if kind == "processed":
        return "ABSENT, only processed — not built"
    if kind == "unknown":
        return "ABSENT, has a record of unknown kind"
    return "ABSENT"


def render(items, root="", queue_path="QUEUE.md"):
    out = []
    # Bound the entry-reading to the slugs that can actually be printed: every
    # slug some item cites, and every slug named as a blocker. Reading the whole
    # folder is megabytes to answer a handful of citations.
    wanted = set()
    for item in items:
        wanted.update(citations(item))
        wanted.update(item["blocked_by"])
    shipped = shipped_slugs(root, wanted)
    held_dates = {}
    ages = first_seen(root, queue_path, held_dates)
    # How many other entries name each capture — the count the planning
    # opening reads to name a passed-over capture that other captures wait
    # on. Computed by the same function rung 2 of the ladder reads.
    incoming = incoming_citations(items)
    for section in ("Processed", "Unprocessed"):
        in_section = [i for i in items if i["section"] == section]
        out.append(f"## {section} — {len(in_section)} item(s)")
        if section == "Processed":
            cleared = sum(1 for i in in_section if i["cleared"])
            out.append(f"   {cleared} cleared to run, {len(in_section) - cleared} held below the line")
        # The section's median line count, printed once. The ladder's rung 3
        # orders only the entries at or above it, which is what makes that rung
        # terminate instead of ranking the whole section forever. A proportion
        # of the section it governs, never a bare figure — printed here so the
        # rung reads a computed field rather than anyone deciding a threshold.
        med = median_lines(in_section)
        if med is not None:
            out.append(f"   median entry length: {med} lines")
        # The section's median age, the other half of rung 3's intersection.
        # An entry at or above BOTH medians is one that has been enriched across
        # many sessions without resolving, and that intersection is roughly a
        # quarter of the section — small enough to finish in one session, which
        # is what lets the rung sit above the alternation without starving it.
        med_age = median_first_seen(in_section, ages)
        if med_age is not None:
            out.append(f"   median first seen: {med_age}")
        for item in in_section:
            bits = []
            if section == "Processed":
                bits.append("cleared" if item["cleared"] else "held")
            bits.append(item["flavor"])
            if item["runs_alone"]:
                bits.append("runs alone")
            slug = item["slug"] or "NO-SLUG"
            line = f"- [{slug}] ({', '.join(bits)}) {item['heading']}"
            if item["blocked_by"]:
                # Every blocker is printed with where it sits, because the item
                # lifts only when all of them resolve — printing the first alone
                # would read as one outstanding dependency when there are four.
                shown = ", ".join(
                    f"[{ref}] -> {locate(ref, items, shipped)}"
                    for ref in item["blocked_by"]
                )
                line += f"  | Blocked by: {shown}"
            if item["not_before"]:
                line += f"  | Not before: {item['not_before']} -> {not_before_state(item['not_before'])}"
            if item["cycle"]:
                line += f"  | Cycle: [{item['cycle']}]"
            if item["flag"]:
                line += f"  | Red flag: {item['flag']}"
            if section == "Unprocessed" and item["slug"] and incoming.get(item["slug"]):
                line += f"  | Cited by: {incoming[item['slug']]} other entr" + (
                    "y" if incoming[item["slug"]] == 1 else "ies")
            # Only citations that resolve to a LOG entry are printed. A citation
            # with no record at all is the normal state and would print on
            # nearly every line for nothing; a citation with one is the signal.
            #
            # Built and processed print as SEPARATE lists rather than one, because
            # they carry different weight: an item leaning on work already built
            # has a premise worth re-reading before it runs, while an item leaning
            # on work that was only agreed has a weaker premise still. Collapsing
            # them reported the second as the first. Suppressing the processed
            # case was refused — a weaker premise is a fact worth seeing, and the
            # digest states facts rather than hiding them.
            built = [s for s in citations(item) if shipped.get(s) == "built"]
            processed = [s for s in citations(item) if shipped.get(s) == "processed"]
            unclassified = [s for s in citations(item) if shipped.get(s) == "unknown"]
            if built:
                line += "  | Cites shipped: " + ", ".join(f"[{s}]" for s in built)
            if processed:
                line += "  | Cites processed: " + ", ".join(f"[{s}]" for s in processed)
            # An older-format record carries neither marker. Reported as found
            # and unclassified rather than guessed at — partial coverage, said
            # plainly, which is the posture the rest of this digest takes.
            if unclassified:
                line += "  | Cites: " + ", ".join(
                    f"[{s}] (record kind unknown)" for s in unclassified
                )
            # Research files the item names. Printed for every citation, not
            # only superseded ones: the superseded flag tells a session that a
            # finding it already knows about has moved, while this tells the
            # session which findings the item rests on at all. An item that
            # restates a finding without naming it prints nothing here, and
            # nothing detects that — see the coverage limit in the footer.
            researched = research_cited(item)
            if researched:
                line += "  | Cites research: " + ", ".join(researched)
            # Line count, and whether it sits at or above the section median.
            # Both rungs of the ladder that read this now read a computed field
            # instead of anyone subtracting numbers by hand.
            span = entry_lines(item)
            line += f"  | Lines: {span}"
            if med is not None and span >= med:
                line += " (at/above median)"
            if item["slug"] and item["slug"] in ages:
                line += f"  | First seen: {ages[item['slug']]}"
                # Tagged the same way the line count is, so rung 3 reads two
                # computed flags rather than comparing dates by hand. "At/above
                # median age" means filed on or before the median date — older,
                # not later.
                if med_age is not None and ages[item["slug"]] <= med_age:
                    line += " (at/above median age)"
            # Held-since prints only on a held item, and only where the date
            # could be attributed. A count of held items reads as background;
            # a date is what makes a stuck item visible as stuck.
            if (section == "Processed" and not item["cleared"]
                    and item["slug"] in held_dates):
                line += f"  | Held since: {held_dates[item['slug']]}"
            out.append(line)
        out.append("")

    flags = contradictions(items, root)
    out.append(f"## Placement contradictions — {len(flags)}")
    if flags:
        out.extend(f"- {f}" for f in flags)
        out.append(
            "These are flags, not decisions. Moving an item out of Processed is "
            "the user's call at /plan."
        )
    else:
        out.append("- none")
    out.append(
        "Placement flags match a fixed set of known phrases, so a clean result "
        "means none of the phrases this check knows were found — not that no "
        "contradiction exists. Partial coverage, not a clean bill."
    )
    out.append(
        "Capture-bears-on-cleared flags reach a capture that NAMES the cleared "
        "item's slug. A capture that invalidates cleared work without naming it "
        "is not reached, and nothing here can tell whether a named one actually "
        "invalidates anything — read it as a prompt to look, not as a verdict."
    )
    out.append(
        "Superseded-research flags cover only items that NAME the research file "
        "in their prose. An item scoped on a finding it never cites is not "
        "reached by this check — read it as partial coverage, not a clean bill."
    )
    out.append(
        "A SNAPSHOT flag says a cited finding is a copy another project owns. "
        "It is permanent and says nothing about currency: nothing reads the "
        "owning project, so whether the original has changed since the copy was "
        "taken is unknown rather than checked."
    )
    out.append(
        "The same limit binds `Cites research:`. It reports what an item names; "
        "an item that restates a finding in its own words prints nothing, and "
        "nothing detects that. A blank there means no citation was written, "
        "never that the item rests on no research."
    )
    out.append("")

    shared = files_named(items)
    out.append(f"## Files named by two or more items — {len(shared)}")
    if shared:
        for path, slugs in shared.items():
            out.append(f"- {path}: " + ", ".join(f"[{s}]" for s in slugs))
    else:
        out.append("- none")
    out.append("")

    # How much ready work sits in front of each `Runs alone` item.
    #
    # /next stops BEFORE such an item, so it is reached only once everything
    # ahead of it has been built — and every planning session adds newly ready
    # work ahead of it. So a correctly placed item quietly recedes each time the
    # queue is worked, and nothing in the queue shows that happening.
    #
    # A COUNT is reportable where an age is not: how long something has been
    # ready would need a threshold nobody can derive, while what sits in front of
    # it is arithmetic. A fact, like every other line here, never a verdict —
    # moving the item is the user's decision.
    alone = [i for i in items
             if i["section"] == "Processed" and i["cleared"] and i["runs_alone"]]
    out.append(f"## Runs-alone work, and what is ahead of it — {len(alone)}")
    if alone:
        cleared_order = [i for i in items
                         if i["section"] == "Processed" and i["cleared"]]
        for item in alone:
            ahead = cleared_order.index(item)
            out.append(
                f"- [{item['slug'] or 'NO-SLUG'}]: {ahead} cleared item(s) ahead of it"
            )
    else:
        out.append("- none")
    out.append("")
    return "\n".join(out)


def incoming_citations(items):
    """How many OTHER entries cite each entry's slug. Rung 2 of the ladder.

    Computed here and nowhere else, which is what makes the claim that every
    rung reads a computed field true rather than aspirational: before this, the
    count was worked out by hand at every pick.
    """
    counts = {item["slug"]: 0 for item in items if item["slug"]}
    for item in items:
        for cited in set(citations(item)):
            if cited in counts and cited != item["slug"]:
                counts[cited] += 1
    return counts


def medians_for(items, root, queue_path, medians=None):
    """The two medians a pick ranks against, and where they came from.

    Returns (median_lines, median_first_seen, source). With `medians` given
    — the pair the opening printed, `(lines, date)` — those are used and the
    source reads "passed in"; otherwise both are recomputed from the section
    as it stands now, and the source says so. The ladder promises the two
    sets are fixed when the run opens, so a pass that recomputes them at every
    pick drifts from that promise silently: entries leave the section as they
    are processed, the medians fall, and entries the opening excluded become
    long. The source line is what makes a forgotten argument visible.
    """
    if medians:
        return medians[0], medians[1], "passed in"
    ages = first_seen(root, queue_path)
    in_section = [i for i in items if i["section"] == "Unprocessed"]
    return (median_lines(in_section), median_first_seen(in_section, ages),
            "recomputed from the file now; pass --medians to hold the "
            "opening's")


def parse_medians(text):
    """`<lines>,<YYYY-MM-DD>` -> (int, str), or None where it does not parse."""
    if not text:
        return None
    parts = text.split(",", 1)
    try:
        lines = int(parts[0].strip())
    except (ValueError, IndexError):
        return None
    date = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
    return (lines, date)


def whats_next(items, root, queue_path, skip=(), picked=0, today=None,
               medians=None):
    """Which rung the ladder falls to, and that rung's top item.

    Answers the one question a pick actually asks, so re-deriving it costs a
    scoped call rather than a full digest. The rung is re-derived at EVERY pick
    because the queue changes underneath the answer — entries leave it, get set
    aside, new ones land — so this is a recurring cost rather than a one-off,
    which is why the opening digest's fields cannot stand in for it.

    `skip` and `picked` are session state the script cannot see: which entries
    the user set aside this session, and how many picks have been made (rung 5
    alternates on that parity). Without them the mode would answer wrongly the
    moment anything was skipped, which is the case it exists for.

    The plan-time pass-overs are all applied here, so a session reading the
    pick never re-applies them by hand: a `Not before:` still ahead, a
    `Blocked by:` naming an open entry, and a `Cycle:` naming a live
    definition (that cycle's turns draw the entry; a cycle deleted from the
    doc releases its material, so a dead reference ranks normally). The first
    two were implemented from the start; the cycle pass-over was left to the
    reader and re-applied by hand on every pick of a thirty-odd-pick session,
    which is the derivation cost this mode exists to remove.

    Returns (rung number, rung name, item) or (None, why not, None).
    """
    ages = first_seen(root, queue_path)
    cycle_slugs = _cycle_definition_slugs(root)
    pool = offerable(items, root, skip=skip, today=today)

    if not pool:
        return None, "nothing in Unprocessed is offerable right now", None

    flagged = [i for i in pool if i["flag"] == "uncleared"]
    if flagged:
        return 1, "an uncleared red flag", flagged[0]

    # Due cycle work: a capture filed UNDER a cycle definition's own slug is
    # that cycle's due turn — timing work that loses its value waiting in the
    # pack. Distinct from the Cycle: field above, which marks standing
    # material the ladder passes over.
    due = [i for i in pool if i["slug"] and i["slug"] in cycle_slugs]
    if due:
        return 2, "due cycle work — its slug names a cycle definition", due[0]

    counts = incoming_citations(items)
    cited = [i for i in pool if i["slug"] and counts.get(i["slug"], 0) > 0]
    if cited:
        cited.sort(key=lambda i: (-counts[i["slug"]], i["first_line"]))
        n = counts[cited[0]["slug"]]
        return 3, ("unblock potential — %d other entr%s cite%s it"
                   % (n, "y" if n == 1 else "ies",
                      "s" if n == 1 else "")), cited[0]

    med_lines, med_age, _source = medians_for(items, root, queue_path, medians)

    def is_long(item):
        return med_lines is not None and entry_lines(item) >= med_lines

    def age_of(item):
        return ages.get(item["slug"]) or "9999-99-99"

    def is_old(item):
        return med_age is not None and age_of(item) <= med_age

    both = sorted([i for i in pool if is_long(i) and is_old(i)],
                  key=age_of)
    if both:
        return 4, "both longer and older than the section's medians", both[0]

    # Rung 5 alternates: oldest first, with every other pick required to be one
    # of the long entries. Alternation is what makes a short old entry
    # reachable at all — ordering by one key then the other only relabels the
    # starvation under a new name.
    by_age = sorted(pool, key=age_of)
    if picked % 2 == 1:
        long_ones = [i for i in by_age if is_long(i)]
        if long_ones:
            return 5, "alternating — this pick must be a long entry", long_ones[0]
    return 5, "alternating — oldest first", by_age[0]


def offerable(items, root, skip=(), today=None):
    """The Unprocessed entries a pick may offer right now — the pass-overs
    applied in one place.

    A capture bows out while a date holds it, until every entry its `Blocked
    by:` names is processed or built, or while a live cycle definition claims
    it as material; a slug the session set aside is passed over too. This is
    the one implementation of the pass-over: `whats_next` picks from it, and
    the checkpoint-counts tool counts it, so the two can never disagree about
    what is presentable.
    """
    import datetime
    today = today or datetime.date.today().isoformat()
    cycle_slugs = _cycle_definition_slugs(root)
    wanted = set()
    for item in items:
        if item["section"] == "Unprocessed":
            wanted.update(item["blocked_by"])
    shipped = shipped_slugs(root, wanted) if wanted else {}

    pool = []
    for item in items:
        if item["section"] != "Unprocessed":
            continue
        if item["slug"] and item["slug"] in skip:
            continue
        # A capture bows out while a date holds it or a named entry still
        # holds it — both mean "do not OFFER this again", which is what a pick
        # does.
        if item["not_before"] and item["not_before"] > today:
            continue
        if any(_entry_holds(items, ref, shipped) for ref in item["blocked_by"]):
            continue
        if item["cycle"] and item["cycle"] in cycle_slugs:
            continue
        pool.append(item)
    return pool


def _entry_holds(items, slug, shipped):
    """Whether a capture's `Blocked by:` reference still holds it.

    The rule reads "do not OFFER this again until every named entry is
    processed or built": an entry kept into Processed counts as processed, so
    only one still sitting in Unprocessed holds the capture. An absent entry
    with a build record was built and releases it; an absent entry with no
    record is a wrong reference — the lint reports it — and stays a hold.
    """
    for i in items:
        if i["slug"] == slug:
            return i["section"] == "Unprocessed"
    return shipped.get(slug) != "built"


def _cycle_definition_slugs(root):
    """Slugs of the definitions in the project's cycles doc, or an empty set.

    Read live at each pick rather than stored, so a definition deleted from
    the doc releases its material by itself — the same recompute-from-the-
    artifact posture every other field here takes.
    """
    path = os.path.join(root, "CYCLES.md")
    slugs = set()
    try:
        with open(path, "r", encoding="utf-8") as handle:
            for line in handle:
                match = re.match(
                    r"^#{2,4}\s+.*\[([a-z0-9][a-z0-9-]*)\]\s*$", line.strip())
                if match:
                    slugs.add(match.group(1))
    except OSError:
        return set()
    return slugs


def render_whats_next(items, root, queue_path, skip=(), picked=0,
                      medians=None):
    """The scoped answer: the rung, the item, its line number, its text —
    and which medians it ranked against, with their source."""
    med_lines, med_age, source = medians_for(items, root, queue_path, medians)
    medians_line = "medians: %s lines, %s — %s" % (
        med_lines if med_lines is not None else "none",
        med_age if med_age else "no date", source)
    rung, why, item = whats_next(items, root, queue_path, skip, picked,
                                 medians=(med_lines, med_age))
    if item is None:
        return "Next: nothing — %s.\n%s" % (why, medians_line)

    try:
        with open(queue_path, "r", encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except OSError:
        lines = []
    text = "\n".join(lines[item["first_line"] - 1:item["last_line"]])

    out = [
        "Rung %d: %s" % (rung, why),
        "Next: [%s] — %s" % (item["slug"] or "NO-SLUG", item["heading"]),
        "Starts at line %d of %s" % (item["first_line"], queue_path),
        medians_line,
        "",
        text,
    ]
    return "\n".join(out)


def main(argv):
    args = argv[1:]
    scoped = False
    skip = []
    picked = 0
    medians = None
    path = None

    index = 0
    while index < len(args):
        token = args[index]
        if token == "--next":
            scoped = True
        elif token == "--skip":
            index += 1
            skip = [s for s in args[index].split(",") if s] if index < len(args) else []
        elif token == "--medians":
            index += 1
            medians = parse_medians(args[index]) if index < len(args) else None
        elif token == "--picked":
            index += 1
            try:
                picked = int(args[index])
            except (IndexError, ValueError):
                picked = 0
        elif path is None:
            path = token
        index += 1

    if path is None:
        print("usage: queue_digest.py <QUEUE.md path> "
              "[--next [--skip slug,slug] [--picked N] "
              "[--medians <lines>,<YYYY-MM-DD>]]", file=sys.stderr)
        return 1
    try:
        items = parse(path)
    except OSError as exc:
        print(f"queue_digest: cannot read {path}: {exc}", file=sys.stderr)
        return 1
    # The project root is the queue file's own folder, so the research files an
    # item cites can be opened without asking for a second argument.
    root = os.path.dirname(os.path.abspath(path))
    if scoped:
        print(render_whats_next(items, root, path, tuple(skip), picked,
                                medians=medians))
    else:
        print(render(items, root, path))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
