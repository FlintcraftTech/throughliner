#!/usr/bin/env python3
"""Mechanical QUEUE.md work-item reorder mover.

Why this exists: /plan's close-out reorder re-sorts the queue sections, but the
only editing primitive Claude has is exact-string replace — so moving a work
item means retyping its whole prose block verbatim, twice. Work items run to
several hundred words, so on a long queue the sort silently degrades to a
partial move, and a single transcription slip corrupts an item with no error.
This script moves whole work-item blocks byte-for-byte: Claude supplies only the
desired slug order, the script rewrites the section, and nothing passes through
Claude's hands.

Contract:
  python reorder_queue.py <queue_path> <section> <slug1> <slug2> ... [--marker-after <slug|TOP|BOTTOM>]
  python reorder_queue.py <queue_path> <section> --move <slug> <TOP|BOTTOM> [--marker-after ...]
  python reorder_queue.py <queue_path> <section> --move <slug> <BEFORE|AFTER> <anchor-slug> [--marker-after ...]
  python reorder_queue.py <queue_path> --move-section <slug> <FromSection> <ToSection> [--position <TOP|BOTTOM>] [--marker-after ...]
  python reorder_queue.py <queue_path> --move-section <slug> <FromSection> <ToSection> --position <BEFORE|AFTER> <anchor-slug> [--marker-after ...]
  python reorder_queue.py <queue_path> --delete <slug> <Section>
  python reorder_queue.py <queue_path> --append <Section> --body <path>
  python reorder_queue.py <queue_path> --replace-in <slug> --old <literal> --new <literal> [--section <Section>]

  <section>  one of: Processed | Unprocessed
  <slug...>  the FULL desired order of that section's work-item slugs, top to
             bottom. Every slug currently in the section must appear exactly
             once; no extra slugs. (The full-set check stays on this total form
             — it is what guarantees no item is silently lost in a reorder.)
  --move <slug> <TOP|BOTTOM>  single-item-move mode: relocate exactly one item
             to the top or bottom of its section, keeping every other item in
             its current relative order. The caller names only the one slug —
             the script derives the full order from the file — so a common move
             (e.g. /plan's skip-to-defer sending an item to the bottom of
             Unprocessed) needs no hand-typed slug list. The same byte-for-byte
             block preservation and self-checks apply. Mutually exclusive with a
             positional slug list.
  --move <slug> <BEFORE|AFTER> <anchor-slug>  relative form of the same move:
             place the item immediately before/after another item in the same
             section, all other items keeping their relative order. Exists so a
             two-item reorder never demands the section's full slug list. To
             clear several held items, run one --move per item with
             --marker-after naming that item, so each command clears only
             what it names — the full slug list is never needed for that.
  --move-section <slug> <From> <To>  cross-section move: relocate one item's
             whole block byte-for-byte from one section to the other — the
             Unprocessed → Processed keep-move is /plan's most frequent
             structural write, and without this it was hand-retyped. Default
             lands at the BOTTOM of the target section — which in Processed is
             BELOW the cleared-to-run marker, so an item moved there because it
             was cleared needs --position, and --marker-after in the SAME call
             where the marker should move too, or the file reads as though
             nothing was cleared. --position takes
             TOP or BOTTOM alone, or BEFORE/AFTER followed by an anchor slug
             in the target section as its next bare word. The
             heading text is NOT rewritten — a processed item's new description
             is a separate deliberate edit, made after the mechanical move.
  --append <Section> --body <path>  file one NEW entry at the bottom of a
             section, addressed by section rather than by an anchor — so a file
             that changes underneath the write cannot send it into the wrong
             one. The entry's text comes from a file (write it to the session
             scratchpad first), because a multi-paragraph rationale does not
             survive shell quoting. Refuses a body that is not a single
             `#### ` entry with a slug, and refuses a slug already in use.

  --replace-in <slug> --old <literal> --new <literal>  replace one literal
             string inside one entry's block, touching no other entry. Refuses
             unless the old string occurs exactly once in that entry — make it
             longer until it is unique. The narrow fix for pointer drift (an
             entry naming a filename that moved), performable at a build close
             where hand edits to the queue are refused. Judgment edits stay
             out: the replacement is byte-literal and uniqueness-checked.
             --section bounds the slug lookup to one section; without it both
             are searched and a slug found twice refuses.

  --delete <slug> <Section>  remove one item's whole block, addressed by slug.
             The removal every /plan keep-or-delete decision and every close
             clearing shipped work needs — and the one operation this script
             used to lack, which is exactly why removals fell back to
             hand-editing long blocks. Refuses rather than guessing when the
             slug resolves to nothing or to more than one block, prints the
             heading line it removed, and re-anchors the readiness marker if
             the deleted item was what the marker sat after. Adding is
             deliberately not offered: an append needs no existing block
             reproduced, so it was never the dangerous case.
  --marker-after (Processed only): where the `--- Cleared to run above this
             line ---` marker lands — after the named slug, or TOP / BOTTOM of
             the section. Omit to keep the marker in its current relative spot
             (immediately after whichever slug it currently follows). Ignored
             with a warning if the section has no marker.

The ordering input is ephemeral by design — one rearrange, then discarded. It is
deliberately NOT a persistent queue index: a standing short-line index invites
reasoning from the compressed lines instead of the real work items, the exact
proxy-reasoning the method forbids.

Self-check (refuses to write on any failure, exits non-zero, changes nothing):
  - the multiset of slugs after == before (no item lost, added, or duplicated);
  - each slug's block content is byte-for-byte identical before and after;
  - the marker is present after iff it was present before;
  - everything outside the target section is untouched.
"""

import sys
import os
import re

# Force UTF-8 on the console output, once, before any message is emitted.
#
# Every message this script prints goes out through `sys.stderr.write`, and on
# Windows an unconfigured stderr falls back to the console's ANSI code page —
# so any character outside it is replaced. The echo that confirms which item was
# moved or deleted prints the item's own heading back, and headings routinely
# carry em-dashes and arrows, which came back mangled on every run. The file
# handles were never affected: they are opened with encoding='utf-8'
# explicitly, so the queue itself was always written correctly. Only the echo
# was damaged — and the echo is how the caller checks the right item was
# addressed, which matters most on two headings that differ only in the middle.
#
# `errors='replace'` keeps a console that genuinely cannot render a character
# from turning a cosmetic problem into a crash mid-edit.
for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        # Python < 3.7, or a stream that cannot be reconfigured (redirected to
        # a pipe or replaced by a test harness). Messages then behave as before
        # — degraded, never fatal.
        pass

MARKER_RE = re.compile(r'^---\s*Cleared to run above this line\s*---\s*$')
SECTION_RE = re.compile(r'^##\s+(Processed|Unprocessed)\s*$')
ITEM_RE = re.compile(r'^####\s')
# Slug = the last [bracketed] token on the heading line (a leading [user]/[audit]
# flavor tag never collides — it isn't at end of line).
SLUG_RE = re.compile(r'\[([^\]]+)\]\s*$')


def die(msg):
    sys.stderr.write("reorder_queue: " + msg + "\n")
    sys.exit(1)


def heading_slug(line):
    m = SLUG_RE.search(line.rstrip())
    return m.group(1) if m else None


def parse(lines):
    """Return (before_lines, section_name->(start,end)) index of section body
    line ranges. A section body runs from the line after its `## Name` heading
    up to (not including) the next `## ` heading or EOF."""
    sections = {}
    heading_idx = {}
    for i, line in enumerate(lines):
        m = SECTION_RE.match(line)
        if m:
            heading_idx[m.group(1)] = i
    # compute body ranges
    all_h2 = [i for i, l in enumerate(lines) if l.startswith('## ')]
    for name, hi in heading_idx.items():
        nxt = min([h for h in all_h2 if h > hi], default=len(lines))
        sections[name] = (hi + 1, nxt)
    return sections


def split_blocks(body):
    """Split a section body (list of lines) into a leading preamble (non-item
    lines before the first ####), a list of item blocks, and the marker.

    Returns (preamble_lines, blocks, marker_after_slug_or_None, had_marker).
    Each block is (slug, list_of_lines) covering the #### heading through the
    lines up to the next #### / marker. The marker line and any blank lines
    around it are handled separately so item text stays byte-exact.
    """
    # find first item
    first = next((i for i, l in enumerate(body) if ITEM_RE.match(l)), None)
    if first is None:
        # No items at all: the marker (if any) is still somewhere in the body.
        kept = [l for l in body if not MARKER_RE.match(l)]
        return kept, [], None, len(kept) != len(body)
    # The marker can sit ABOVE every item, in which case it lands in the
    # preamble and the item-scanning loop below never sees it. Scan the
    # preamble for it explicitly and strip it, or the marker's text survives
    # in the preamble while had_marker stays False — reassembly then
    # contradicts itself and the self-check refuses to write.
    preamble = [l for l in body[:first] if not MARKER_RE.match(l)]
    marker_above_all = len(preamble) != first
    blocks = []
    marker_after = None
    had_marker = marker_above_all
    cur_slug = None
    cur = []
    prev_slug = None  # slug of the most-recently-completed block (marker anchor)

    def flush():
        nonlocal cur, cur_slug, prev_slug
        if cur_slug is not None:
            # Strip trailing blank lines — inter-block spacing is regenerated
            # canonically at reassembly, so a block stores only heading + body
            # (internal blank lines within the rationale are kept).
            block = cur[:]
            while block and block[-1].strip() == '':
                block.pop()
            blocks.append((cur_slug, block))
            prev_slug = cur_slug  # last completed item = what a following marker anchors to
        cur, cur_slug = [], None

    for line in body[first:]:
        if MARKER_RE.match(line):
            flush()
            had_marker = True
            marker_after = prev_slug  # None => marker at TOP (before all items)
            continue
        if ITEM_RE.match(line):
            flush()
            cur_slug = heading_slug(line)
            if cur_slug is None:
                # "entry" rather than "work item": this reads both sections, and
                # only Processed holds work items.
                die("entry heading has no [slug]: " + line.strip())
            cur = [line]
        else:
            cur.append(line)
    flush()
    return preamble, blocks, marker_after, had_marker


def assemble_section(preamble, elements):
    """Reassemble a section body: preamble, then every element (a block's lines,
    or the marker as its own element) separated by exactly one blank line.
    Returns the list of output lines, starting with the blank line that follows
    the `## Section` heading."""
    pre = list(preamble)
    while pre and pre[0].strip() == '':
        pre.pop(0)
    while pre and pre[-1].strip() == '':
        pre.pop()
    out = ['\n']            # blank line after the `## Section` heading
    if pre:
        out.extend(pre)
        out.append('\n')
    for el in elements:
        out.extend(el)
        out.append('\n')   # one blank line after each element
    return out


def elements_with_marker(new_blocks, had_marker, pref):
    """Order blocks and (if present) the marker into the element list."""
    marker_line = "--- Cleared to run above this line ---\n"
    elements = []
    if had_marker and pref == 'TOP':
        elements.append([marker_line])
    for s, blk in new_blocks:
        elements.append(blk)
        if had_marker and pref == s:
            elements.append([marker_line])
    if had_marker and pref == 'BOTTOM':
        elements.append([marker_line])
    return elements


def section_slugs(lines, section):
    """Slugs of the work items in one section, as a set. Empty if absent."""
    sections = parse(lines)
    if section not in sections:
        return set()
    start, end = sections[section]
    _, blocks, _, _ = split_blocks(lines[start:end])
    return {s for s, _ in blocks if s}


def crossing_note(before_order, before_anchor, after_order, after_anchor,
                  named=None):
    """Which items changed side of the readiness line, and what to say about it.

    Returns (unnamed_crossers, note). The caller refuses on a non-empty
    unnamed list and prints the note otherwise.

    Two behaviours, and the line between them matters. An item the caller NAMED
    crossing the line REPORTS and does not block: moving an item across the
    line is a legitimate way to clear or shelve work, and refusing would force
    a two-step dance for an ordinary operation. That reasoning is unchanged and
    is why it is restated here.

    What it never addressed is items the caller did NOT name crossing, as a
    side effect of where the marker landed: a `--move-section ... --position
    BOTTOM --marker-after` swept four held items into the cleared region and
    reported only that the moved item was now cleared.

    **The refusal is two-directional.** An unnamed crossing INTO the cleared
    region hands unvetted work to a run with nobody watching; an unnamed
    crossing OUT of it drops vetted work below the line with nothing saying
    why, so the next run quietly does less. Both refuse, and the refusal names
    each item that would cross and the route that moves them one at a time
    ([queue-move-downward-sweep-unguarded]). The route is the same in either
    direction: one --move per item, each naming itself as --marker-after.

    Factored out of the within-section reorder path, which was the only path
    that ever ran it — the crossing report was absent from --move-section,
    where the largest crossings happen.
    """
    def _above(order, anchor):
        if anchor == 'TOP':
            return []
        if anchor == 'BOTTOM':
            return list(order)
        if anchor not in order:
            return []
        return order[:order.index(anchor) + 1]

    was = _above(before_order, before_anchor)
    now = _above(after_order, after_anchor)
    note = ", %d item%s above the line" % (len(now),
                                           "" if len(now) == 1 else "s")
    crossed = [s for s in after_order if (s in was) != (s in now)]
    named = list(named or [])
    # Any crossing the caller did not name refuses, in either direction.
    # Each unnamed crosser is paired with where it would land, so the refusal
    # can say which way it was going.
    unnamed = [(s, s in now) for s in crossed if s not in named]
    for s in crossed:
        direction = ("now CLEARED to run" if s in now
                     else "now BELOW the line, no longer cleared")
        # ASCII only: this goes to stderr, and a Windows console under a
        # legacy code page mangles non-ASCII into replacement characters.
        note += "\nreorder_queue: [%s] crossed the readiness line: %s" \
                % (s, direction)
    return unnamed, note


def unnamed_crossing_message(unnamed, marker_pref):
    """The refusal text for crossings the caller never named, or None.

    `unnamed` is crossing_note()'s list of (slug, now_cleared) pairs. Kept
    separate from the die() so the state server can print the same words at
    its door before the script runs.
    """
    if not unnamed:
        return None
    up = [s for s, cleared in unnamed if cleared]
    down = [s for s, cleared in unnamed if not cleared]
    parts = []
    if up:
        parts.append("CLEAR %d item%s you did not name: %s — placing the "
                     "marker after '%s' puts %s above the readiness line, so "
                     "an unattended /next run could build %s"
                     % (len(up), "" if len(up) == 1 else "s",
                        ", ".join("[%s]" % s for s in up), marker_pref,
                        "it" if len(up) == 1 else "them",
                        "it" if len(up) == 1 else "them"))
    if down:
        parts.append("DROP %d cleared item%s you did not name below the "
                     "line: %s — placing the marker after '%s' shelves %s "
                     "with nothing saying why, so the next run quietly does "
                     "less"
                     % (len(down), "" if len(down) == 1 else "s",
                        ", ".join("[%s]" % s for s in down), marker_pref,
                        "it" if len(down) == 1 else "them"))
    return ("this would %s.\n"
            "  Nothing was written. Name --marker-after as the LAST item that "
            "should stay cleared, rather than the item you just placed.\n"
            "  To move several items across the line, run one --move per item "
            "with --marker-after naming that item, so each command crosses "
            "only what it names." % "; and ".join(parts))


def refuse_unnamed_crossings(unnamed, marker_pref):
    """Refuse a write that would move items across the line that the caller
    never named — in either direction."""
    msg = unnamed_crossing_message(unnamed, marker_pref)
    if msg:
        die(msg)


# How long the write waits before its one retry, in seconds. A tunable
# constant stated with no derivation — long enough for a sync client's
# momentary hold on the file to pass, short enough not to feel like a hang.
# Revisable once seen in use.
RETRY_PAUSE_SECONDS = 1.5

# The errno values a held file produces on the platforms this runs on:
# EINVAL is what a cloud-sync client's momentary hold looked like here
# ([mcp-write-invalid-argument-transient]); EACCES and PermissionError are an
# editor or antivirus holding the handle.
_HELD_FILE_ERRNOS = (22, 13)  # EINVAL, EACCES


def _is_held_file_error(exc):
    return isinstance(exc, PermissionError) or \
        getattr(exc, "errno", None) in _HELD_FILE_ERRNOS


def _write_with_one_retry(queue_path, text):
    """Write `text` over `queue_path` atomically, retrying once if the OS
    refuses the handle.

    The bytes go to a temporary file in the same folder, forced to disk, and
    swapped in with os.replace — so the queue on disk is always either the
    old whole file or the new whole file, never a truncated one.
    """
    import time
    tmp_path = queue_path + ".tmp-reorder"
    attempts = 0
    while True:
        attempts += 1
        try:
            with open(tmp_path, 'w', encoding='utf-8', newline='') as f:
                f.write(text)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, queue_path)
            return
        except OSError as exc:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except OSError:
                pass
            if not _is_held_file_error(exc) or attempts >= 2:
                if _is_held_file_error(exc):
                    die("could not write %s: the operating system refused the "
                        "file twice (%s). Something is holding it open — check "
                        "for a sync client (Google Drive, OneDrive, Dropbox) "
                        "mid-sync, or an editor with the file open — then "
                        "re-run the command. Nothing was written; the queue "
                        "is as it was." % (queue_path, exc))
                raise
            sys.stderr.write("reorder_queue: the operating system refused the "
                             "write once (%s); waiting %.1fs and trying "
                             "again.\n" % (exc, RETRY_PAUSE_SECONDS))
            time.sleep(RETRY_PAUSE_SECONDS)


def write_verified(queue_path, new_lines, absent=(), present=()):
    """Write the queue, force it to disk, read it back, and confirm the write
    actually landed before reporting success.

    Why this exists: a --delete once printed its normal success line, exited
    zero, and left the item sitting in the file. Re-running the identical
    command a moment later worked. That is worse than a loud failure, which
    costs one retry — /next treats the success line as proof an item was built
    and removed, and the whole copy-per-item design rests on "an item still
    showing in QUEUE.md means exactly one thing: not built yet". A false
    success breaks that guarantee silently.

    `absent` and `present` are (slug, section) pairs the re-read must confirm.

    The flush-and-fsync is not decoration. This project lives under a
    file-sync layer, and a normal file close leaves the write in flight — so a
    plain read-back could be served the same in-flight content and pass for
    exactly the reason the check exists. Forcing the bytes to disk first is
    what makes the re-read evidence rather than an echo.

    The honest limit: this catches a write that never reached the file. It
    cannot catch a sync layer that reverts the file some time after the
    process has exited, because nothing is still running to look.

    The write lands on a temporary file beside the queue and is swapped in
    with os.replace, so the queue is never half-written: a refusal at the
    open leaves it intact, and so does a refusal partway through the write.
    Where the operating system refuses the handle — EINVAL, EACCES, a
    PermissionError, the shapes a sync client or an editor holding the file
    produce — the script waits and tries once more, saying so; a second
    refusal names what to check.
    """
    _write_with_one_retry(queue_path, ''.join(new_lines))

    with open(queue_path, 'r', encoding='utf-8', newline='') as f:
        after = f.read().splitlines(keepends=True)

    for slug, section in absent:
        if slug in section_slugs(after, section):
            die("write did NOT land: [%s] is still an entry in %s after the "
                "file was written and read back. Nothing downstream should "
                "treat this as done — re-run the command and check the file."
                % (slug, section))
    for slug, section in present:
        if slug not in section_slugs(after, section):
            die("write did NOT land: [%s] is not an entry in %s after the "
                "file was written and read back. Nothing downstream should "
                "treat this as done — re-run the command and check the file."
                % (slug, section))


STAMP_RE = re.compile(r"^Filed \d{4}-\d{2}-\d{2} \d{2}:\d{2}, stamped by the "
                      r"(capture|queue) tool\.\s*$")
# The lines a capture may end on after its prose: the parsed fields. A stamp
# goes before the first of them, so it stays the last prose line.
FIELD_LINE_RE = re.compile(
    r"^(Blocked by|Not before|Cycle|Red flag|Runs alone)\b")


def stamp_filed_at(body_lines):
    """Add a filed-at stamp, read from the clock, where the body carries none.

    The capture tool stamps every capture it files; this route — the one the
    always-loaded rules name — stamped nothing, so a planning session filing
    thirty captures through it wrote every time by hand, counted up from the
    opening. A body already carrying either tool's stamp is returned as it is.
    """
    if any(STAMP_RE.match(l.strip()) for l in body_lines):
        return body_lines
    import datetime
    eol = '\r\n' if body_lines and body_lines[0].endswith('\r\n') else '\n'
    stamp = "Filed %s, stamped by the queue tool.%s" % (
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), eol)
    insert_at = len(body_lines)
    # Walk back over trailing field lines so the stamp lands before them.
    while insert_at > 1 and FIELD_LINE_RE.match(body_lines[insert_at - 1].strip()):
        insert_at -= 1
    return body_lines[:insert_at] + [stamp] + body_lines[insert_at:]


def append_item(queue_path, section, body_path):
    """Append one new entry at the bottom of a named section.

    The last queue operation still done by hand. Filing a capture had no tool,
    so every one was an exact-string edit anchored to whatever text sat at the
    end of the file — and an anchor read before the file changed underneath it
    puts the append in the wrong place. That happened: a capture landed in
    Processed above the readiness line, where a run would have tried to build an
    item whose whole content was three undesigned routes, and it was found only
    because the user asked for an unrelated summary. Two safe operations, the
    mover and the edit, composed into an unsafe one.

    Addressed by section rather than by anchor, so there is no anchor to go
    stale. The gain is the mover's own, applied to the operation it never
    covered.

    **The body arrives by FILE, never on the command line.** A multi-paragraph
    rationale passed as an argument breaks on Windows over quoting, newlines and
    em-dashes. Claude writes the text to the session scratchpad with the ordinary
    editing tools — that path is already permitted — and this reads it. The queue
    itself is still only ever touched by this script.

    Refuses rather than guesses: a body that is not a single `#### ` entry with a
    slug, or a slug already present in either section, exits non-zero and changes
    nothing.
    """
    if section not in ('Processed', 'Unprocessed'):
        die("section must be Processed or Unprocessed, got: " + section)

    try:
        with open(body_path, 'r', encoding='utf-8', newline='') as f:
            body_lines = f.read().splitlines(keepends=True)
    except OSError as exc:
        die("--body could not be read: %s" % exc)

    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)
    while body_lines and not body_lines[-1].strip():
        body_lines.pop()
    if not body_lines:
        die("--body file is empty. It must hold one entry, starting with a "
            "'#### ' heading carrying a [slug].")
    if not body_lines[0].startswith('#### '):
        die("--body must start with a '#### ' heading line, got: %r"
            % body_lines[0][:60])

    headings = [i for i, l in enumerate(body_lines) if l.startswith('#### ')]
    if len(headings) > 1:
        die("--body holds %d '#### ' headings. Append one entry per call, so "
            "each one's placement is checked on its own." % len(headings))

    new_slug = heading_slug(body_lines[0])
    if not new_slug:
        die("--body heading carries no [slug]. The slug sits at the END of the "
            "heading line, in square brackets.")

    with open(queue_path, 'r', encoding='utf-8', newline='') as f:
        lines = f.read().splitlines(keepends=True)
    sections = parse(lines)
    if section not in sections:
        die("section '%s' not found in %s" % (section, queue_path))

    for name, (s, e) in sections.items():
        for existing in section_slugs(lines, name):
            if existing == new_slug:
                die("slug '%s' is already an entry in section %s. Slugs are "
                    "unique across the queue — pick another, or edit the "
                    "existing entry instead." % (new_slug, name))

    start, end = sections[section]
    preamble, blocks, marker_after, had_marker = split_blocks(lines[start:end])

    if not body_lines[-1].endswith('\n'):
        body_lines[-1] += '\n'
    if section == 'Unprocessed':
        body_lines = stamp_filed_at(body_lines)
    new_blocks = blocks + [(new_slug, body_lines)]

    # The marker keeps its anchor, so an append to Processed lands BELOW the
    # readiness line whenever the marker is anchored to an existing item. That
    # is the safe direction: a new entry is never silently cleared to run.
    pref = 'TOP' if marker_after is None else marker_after
    out = assemble_section(preamble,
                           elements_with_marker(new_blocks, had_marker, pref))
    new_lines = lines[:start] + out + lines[end:]

    # ---- Self-checks: refuse to write on any failure ----
    out_text = ''.join(out)
    for s, blk in blocks:
        if ''.join(blk) not in out_text:
            die("self-check failed: existing block for [%s] changed content" % s)
    if ''.join(body_lines) not in out_text:
        die("self-check failed: the appended entry is not present verbatim")
    if had_marker != any(MARKER_RE.match(l) for l in out):
        die("self-check failed: marker presence changed")
    if lines[:start] != new_lines[:start] or lines[end:] != new_lines[start + len(out):]:
        die("self-check failed: content outside section %s changed" % section)

    write_verified(queue_path, new_lines, present=((new_slug, section),))
    print("reorder_queue: appended to %s: %s"
          % (section, body_lines[0].rstrip('\n')))


def delete_item(queue_path, slug, section):
    """Remove one work item's whole block, addressed by slug.

    Why this exists at all: removing an item was the ONE queue write the mover
    couldn't do, so every removal fell back to hand-editing a long prose block
    with exact-string replace — and that is precisely the moment a scripted
    shell splice starts looking cheaper than the sanctioned path. It was
    reached for three times, once in an unattended run with the warning about
    it sitting in the very file being edited. The fix is not a louder rule: it
    is making the safe path the cheap path, so there is nothing to be tempted
    away from.

    Refuses rather than guesses: a slug resolving to nothing, or to more than
    one block, exits non-zero and changes nothing. Prints the heading line it
    removed, so the deletion is visible in the transcript and in a later read
    of the session rather than being a silent shrinkage of the file.

    Adding is deliberately NOT here. A capture is an append of fresh text with
    no existing block to reproduce, so Edit handles it cleanly and there is no
    shortcut to be tempted by. The danger is specific to removal.
    """
    if section not in ('Processed', 'Unprocessed'):
        die("section must be Processed or Unprocessed, got: " + section)

    with open(queue_path, 'r', encoding='utf-8', newline='') as f:
        lines = f.read().splitlines(keepends=True)
    sections = parse(lines)
    if section not in sections:
        die("section '%s' not found in %s" % (section, queue_path))

    start, end = sections[section]
    preamble, blocks, marker_after, had_marker = split_blocks(lines[start:end])

    matches = [s for s, _ in blocks if s == slug]
    if not matches:
        die("--delete slug '%s' is not an entry in section %s. Check the "
            "spelling, and check the other section — the script refuses rather "
            "than guessing." % (slug, section))
    if len(matches) > 1:
        die("--delete slug '%s' matches %d entries in section %s. Refusing: "
            "two items sharing a slug is itself a fault, and deleting the wrong "
            "one is unrecoverable from here. Fix the duplicate first."
            % (slug, len(matches), section))

    removed_heading = next(b[0].rstrip('\n') for s, b in blocks if s == slug)
    new_blocks = [(s, b) for s, b in blocks if s != slug]

    # Re-anchor the readiness marker if it was anchored to the item being
    # removed. Left alone, its anchor slug would resolve to nothing and the
    # marker would silently vanish — clearing every shelved item below it. The
    # marker keeps its POSITION: it still follows whatever item now precedes it.
    pref = 'TOP' if marker_after is None else marker_after
    if had_marker and pref == slug:
        order = [s for s, _ in blocks]
        idx = order.index(slug)
        preceding = [s for s in order[:idx] if s != slug]
        pref = preceding[-1] if preceding else 'TOP'

    out = assemble_section(preamble,
                           elements_with_marker(new_blocks, had_marker, pref))
    new_lines = lines[:start] + out + lines[end:]

    # ---- Self-checks: refuse to write on any failure ----
    out_text = ''.join(out)
    for s, blk in new_blocks:
        if ''.join(blk) not in out_text:
            die("self-check failed: block for [%s] changed content" % s)
    if had_marker != any(MARKER_RE.match(l) for l in out):
        die("self-check failed: marker presence changed")
    if lines[:start] != new_lines[:start] or lines[end:] != new_lines[start + len(out):]:
        die("self-check failed: content outside the section changed")

    write_verified(queue_path, new_lines, absent=[(slug, section)])
    sys.stderr.write("reorder_queue: deleted from %s: %s\n"
                     % (section, removed_heading))

    # Warn when other work names the deleted slug as its blocker. Prevention at
    # the source, where whoever is deleting can still act on it: once the item
    # is gone, a deleted blocker and a shipped one are indistinguishable from
    # the queue alone, and the held item was designed assuming its blocker
    # would happen — so its premise may not survive the deletion.
    #
    # This does not make the plan-side branch and the lint message redundant. A
    # deletion can happen by hand edit, bypassing this script entirely.
    dependents = []
    for i, line in enumerate(new_lines):
        # `Blocked by:` may name several slugs, so every one on the line is read
        # rather than only the first. A single-slug match missed a dependent
        # whose second or third blocker was the item being deleted, and that is
        # exactly the item whose premise most needs re-examining.
        stripped_line = line.strip()
        names = (re.findall(r'\[([a-z0-9][a-z0-9-]*)\]', stripped_line)
                 if re.match(r'^Blocked by:', stripped_line, re.I) else [])
        if slug in names:
            heading = None
            for j in range(i, -1, -1):
                if ITEM_RE.match(new_lines[j]):
                    heading = heading_slug(new_lines[j]) or new_lines[j].strip()
                    break
            dependents.append(heading or ('line %d' % (i + 1)))
    if dependents:
        # Deliberately states both readings instead of asserting one. This same
        # --delete removes a BUILT item during a /next run and a DROPPED item at
        # /plan, and the script cannot tell which — so a message that assumed
        # "deleted as not worth doing" would cry wolf on every build removal of
        # an item other work waits on, which is the common case. A warning that
        # is usually wrong is one people learn to scroll past.
        sys.stderr.write(
            "reorder_queue: NOTE — %d held item(s) name [%s] as their blocker: "
            "%s. Their Blocked by: lines now point at nothing, and from the "
            "queue alone a shipped blocker and a dropped one look identical. "
            "If [%s] SHIPPED, those items may be ready to lift. If it was "
            "DROPPED as not worth doing, re-examine them instead — each was "
            "designed assuming it would happen, so its premise may not "
            "survive.\n"
            % (len(dependents), slug, ', '.join('[%s]' % d for d in dependents),
               slug))

    # The wider case: any item whose PROSE names the deleted slug. A blocker is
    # one kind of inbound reference and the rarer one; a citation in prose is
    # the common one, and until this printed, those were found by grepping
    # afterwards. One delete left five citing items, repaired across three
    # passes, the first incomplete because the grep output was truncated.
    #
    # Reported, never repaired: rewriting another item's prose is an authoring
    # decision, and a delete is already the user's call. Same register as the
    # readiness-line crossing report — a mechanical consequence of a write,
    # computed from data the script already has.
    citing = []
    seen_headings = set()
    current = None
    for line in new_lines:
        if ITEM_RE.match(line):
            current = heading_slug(line) or line.strip()
            continue
        if current is None or current in seen_headings:
            continue
        # A `Cycle:` line names a cycle DEFINITION of the same slug as a
        # cycle's turn capture, never the capture — so deleting a spent turn
        # capture must not list the whole pool as citing it.
        if re.match(r'^(Blocked by|Cycle):', line.strip(), re.I):
            continue
        if ('[%s]' % slug) in line:
            seen_headings.add(current)
            citing.append(current)
    if citing:
        sys.stderr.write(
            "reorder_queue: NOTE — %d item(s) still cite [%s] in their prose: "
            "%s. Those references now name work that is no longer in the "
            "queue. Read each before assuming it needs an edit: a citation of "
            "SHIPPED work is often correct as written, while a citation of "
            "dropped work may leave the citing item's premise wrong.\n"
            % (len(citing), slug, ', '.join('[%s]' % c for c in citing)))


def replace_in_item(queue_path, slug, old, new, section=None):
    """Replace one literal string inside one entry's block, and nothing else.

    Why this exists ([pointer-drift-unfixable-at-a-build-close]): /done's
    staleness sweep may find a pure pointer drift — an entry naming a filename
    that has since moved — and the fix is mechanical, but a build close's
    scope-lock refuses hand edits to QUEUE.md, so the sweep's arm was
    unperformable exactly where it fires. A literal, uniqueness-checked replace
    through the sanctioned tool is narrow enough to run in a build: judgment
    edits stay out, because the old string must occur exactly once in that
    entry and the replacement is byte-literal.

    Refuses rather than guesses: a slug resolving to nothing or to more than
    one entry, an old string absent or appearing more than once in the entry,
    or old == new, each exit non-zero and change nothing.
    """
    if old == new:
        die("--replace-in: --old and --new are identical; nothing to do")
    if not old:
        die("--replace-in: --old must not be empty")

    with open(queue_path, 'r', encoding='utf-8', newline='') as f:
        lines = f.read().splitlines(keepends=True)
    sections = parse(lines)
    search_sections = [section] if section else ['Processed', 'Unprocessed']
    found = []
    for sec in search_sections:
        if sec not in sections:
            if section:
                die("section '%s' not found in %s" % (sec, queue_path))
            continue
        start, end = sections[sec]
        preamble, blocks, marker_after, had_marker = split_blocks(lines[start:end])
        for s, blk in blocks:
            if s == slug:
                found.append((sec, start, end, preamble, blocks, marker_after,
                              had_marker, blk))
    if not found:
        die("--replace-in slug '%s' is not an entry%s. The script refuses "
            "rather than guessing." % (slug,
            " in section %s" % section if section else ""))
    if len(found) > 1:
        die("--replace-in slug '%s' matches %d entries. Two items sharing a "
            "slug is itself a fault; fix the duplicate first."
            % (slug, len(found)))

    sec, start, end, preamble, blocks, marker_after, had_marker, blk = found[0]
    block_text = ''.join(blk)
    count = block_text.count(old)
    if count == 0:
        die("--replace-in: the old string does not occur in entry [%s]. "
            "Nothing was changed." % slug)
    if count > 1:
        die("--replace-in: the old string occurs %d times in entry [%s], and "
            "a replace that could land on the wrong one is refused. Make the "
            "old string longer until it is unique in the entry." % (count, slug))

    new_block_text = block_text.replace(old, new)
    new_blk = new_block_text.splitlines(keepends=True)
    new_blocks = [(s, new_blk if s == slug else b) for s, b in blocks]
    pref = 'TOP' if marker_after is None else marker_after
    out = assemble_section(preamble,
                           elements_with_marker(new_blocks, had_marker, pref))
    new_lines = lines[:start] + out + lines[end:]

    # Self-checks: every other block byte-identical, nothing outside changes.
    out_text = ''.join(out)
    for s, b in blocks:
        if s != slug and ''.join(b) not in out_text:
            die("self-check failed: block for [%s] changed content" % s)
    if new_block_text not in out_text:
        die("self-check failed: the edited block did not land intact")
    if had_marker != any(MARKER_RE.match(l) for l in out):
        die("self-check failed: marker presence changed")
    if lines[:start] != new_lines[:start] or lines[end:] != new_lines[start + len(out):]:
        die("self-check failed: content outside the section changed")

    write_verified(queue_path, new_lines, present=[(slug, sec)])
    sys.stderr.write("reorder_queue: replaced in [%s] (%s): %r -> %r\n"
                     % (slug, sec, old, new))


def retitle_item(queue_path, slug, heading):
    """Rewrite one entry's heading line and nothing else.

    Why this exists ([queue-tool-no-heading-fix]): the lint's article-leading
    heading flag fired on a capture filed mid-run, and the only sanctioned
    correction was a delete and a re-append — two commands, a second filing
    stamp, and a delete the queue's own notes treat as a signal worth
    explaining. This is the one queue write a build was otherwise missing.

    The slug is supplied from the match and never retyped: slugs are stable
    by rule and every record cites them. The body is carried byte-identical.
    Refuses where the slug names no entry or more than one, where the new
    text is empty, or where it contains a bracket that would read as a
    second slug.
    """
    heading = heading.strip()
    if not heading:
        die("--retitle: --heading must not be empty")
    if '[' in heading or ']' in heading:
        die("--retitle: the new heading contains a bracket, which would read "
            "as a second slug. Give the heading text alone; the slug [%s] is "
            "kept by the tool." % slug)

    with open(queue_path, 'r', encoding='utf-8', newline='') as f:
        lines = f.read().splitlines(keepends=True)
    sections = parse(lines)
    found = []
    for sec in ('Processed', 'Unprocessed'):
        if sec not in sections:
            continue
        start, end = sections[sec]
        preamble, blocks, marker_after, had_marker = split_blocks(lines[start:end])
        for s, blk in blocks:
            if s == slug:
                found.append((sec, start, end, preamble, blocks, marker_after,
                              had_marker, blk))
    if not found:
        die("--retitle slug '%s' is not an entry in either section. The "
            "script refuses rather than guessing." % slug)
    if len(found) > 1:
        die("--retitle slug '%s' matches %d entries. Two items sharing a "
            "slug is itself a fault; fix the duplicate first." % (slug, len(found)))

    sec, start, end, preamble, blocks, marker_after, had_marker, blk = found[0]
    old_heading = blk[0]
    ending = '\r\n' if old_heading.endswith('\r\n') else '\n'
    new_heading = '#### %s [%s]%s' % (heading, slug, ending)
    if new_heading == old_heading:
        die("--retitle: the heading already reads that way; nothing to do")
    new_blk = [new_heading] + blk[1:]
    new_blocks = [(s, new_blk if s == slug else b) for s, b in blocks]
    pref = 'TOP' if marker_after is None else marker_after
    out = assemble_section(preamble,
                           elements_with_marker(new_blocks, had_marker, pref))
    new_lines = lines[:start] + out + lines[end:]

    out_text = ''.join(out)
    for s, b in blocks:
        if s != slug and ''.join(b) not in out_text:
            die("self-check failed: block for [%s] changed content" % s)
    if ''.join(new_blk) not in out_text:
        die("self-check failed: the retitled block did not land intact")
    if had_marker != any(MARKER_RE.match(l) for l in out):
        die("self-check failed: marker presence changed")
    if lines[:start] != new_lines[:start] or lines[end:] != new_lines[start + len(out):]:
        die("self-check failed: content outside the section changed")

    write_verified(queue_path, new_lines, present=[(slug, sec)])
    sys.stderr.write("reorder_queue: retitled [%s] (%s)\n  old: %s\n  new: %s\n"
                     % (slug, sec, old_heading.rstrip('\r\n'),
                        new_heading.rstrip('\r\n')))


def move_section(queue_path, slug, sec_from, sec_to, position, anchor,
                 marker_pref=None):
    """Move one item's block byte-for-byte between sections.

    Same guarantees as a reorder: refuses to write on any failure, block
    content byte-identical, marker presence preserved per section, nothing
    outside the two sections changed.

    `marker_pref` places the destination's readiness marker in the same call.
    Moving an item across sections AND clearing it is the ordinary shape of
    keeping work at /plan — the commonest planning operation, not an edge
    case — and it used to take two commands, because this branch accepted
    --marker-after and then silently ignored it. Silently: the move succeeded,
    exit code 0, and only the marker half went missing.

    Every check below runs BEFORE anything is written, so the call either does
    both halves or neither. A half-applied queue edit is worse than a plain
    refusal, because the readiness marker decides how much work an unattended
    /next run may build without the user present.
    """
    for name in (sec_from, sec_to):
        if name not in ('Processed', 'Unprocessed'):
            die("section must be Processed or Unprocessed, got: " + name)
    if sec_from == sec_to:
        die("--move-section needs two different sections; use --move within one")

    with open(queue_path, 'r', encoding='utf-8', newline='') as f:
        lines = f.read().splitlines(keepends=True)
    sections = parse(lines)
    for name in (sec_from, sec_to):
        if name not in sections:
            die("section '%s' not found in %s" % (name, queue_path))

    f_start, f_end = sections[sec_from]
    t_start, t_end = sections[sec_to]
    f_pre, f_blocks, f_marker_after, f_had = split_blocks(lines[f_start:f_end])
    t_pre, t_blocks, t_marker_after, t_had = split_blocks(lines[t_start:t_end])

    f_slugs = [s for s, _ in f_blocks]
    if slug not in f_slugs:
        die("--move-section slug '%s' is not in section %s" % (slug, sec_from))
    if slug in [s for s, _ in t_blocks]:
        die("slug '%s' already exists in section %s" % (slug, sec_to))
    moved = dict(f_blocks)[slug]
    f_new = [(s, b) for s, b in f_blocks if s != slug]

    t_slugs = [s for s, _ in t_blocks]
    if position in ('BEFORE', 'AFTER'):
        if anchor is None:
            die("--position %s needs an anchor slug" % position)
        if anchor not in t_slugs:
            die("anchor slug '%s' is not in section %s" % (anchor, sec_to))
        idx = t_slugs.index(anchor) + (1 if position == 'AFTER' else 0)
    elif position == 'TOP':
        idx = 0
    else:  # BOTTOM (default)
        idx = len(t_blocks)
    t_new = t_blocks[:idx] + [(slug, moved)] + t_blocks[idx:]

    f_pref = 'TOP' if f_marker_after is None else f_marker_after
    t_pref = 'TOP' if t_marker_after is None else t_marker_after

    # --marker-after applies to the DESTINATION section, which is the only one
    # gaining an item. Validated here, before any write, so a bad value refuses
    # the whole call rather than leaving the move applied and the marker not.
    if marker_pref is not None:
        if not t_had:
            die("--marker-after: section %s has no cleared-to-run marker, so "
                "there is nothing to place. The marker lives in Processed."
                % sec_to)
        t_new_slugs = [s for s, _ in t_new]
        if marker_pref not in ('TOP', 'BOTTOM') and marker_pref not in t_new_slugs:
            die("--marker-after slug '%s' is not in section %s (after the move)"
                % (marker_pref, sec_to))
        t_pref = marker_pref
    # The moved item must never silently land above the target's readiness
    # marker: if it was inserted before the marker anchor resolves, the marker
    # keeps its anchor slug, which is unaffected by an insertion.
    # The destination's crossings, computed before any write. This path never
    # ran the crossing report at all, and it is the path where a whole held
    # region can move at once: --marker-after resolves against the destination
    # section, so placing it past held items sweeps every one of them into the
    # cleared region. Only the moved slug is "named" here.
    t_crossing_note = ""
    if t_had:
        t_unnamed, t_crossing_note = crossing_note(
            [s for s, _ in t_blocks], t_marker_after if t_marker_after else 'TOP',
            [s for s, _ in t_new], t_pref, named=[slug],
        )
        refuse_unnamed_crossings(t_unnamed, t_pref)

    f_out = assemble_section(f_pre, elements_with_marker(f_new, f_had, f_pref))
    t_out = assemble_section(t_pre, elements_with_marker(t_new, t_had, t_pref))

    # Rebuild the file: replace both section bodies. Handle either order.
    if f_start < t_start:
        new_lines = (lines[:f_start] + f_out + lines[f_end:t_start] + t_out
                     + lines[t_end:])
    else:
        new_lines = (lines[:t_start] + t_out + lines[t_end:f_start] + f_out
                     + lines[f_end:])

    # ---- Self-checks ----
    new_text = ''.join(new_lines)
    if ''.join(moved) not in new_text:
        die("self-check failed: moved block for [%s] changed content" % slug)
    old_all = sorted(f_slugs + t_slugs)
    new_all = sorted([s for s, _ in f_new] + [s for s, _ in t_new])
    if old_all != new_all:
        die("self-check failed: slug set changed across the two sections")
    for had, out in ((f_had, f_out), (t_had, t_out)):
        if had != any(MARKER_RE.match(l) for l in out):
            die("self-check failed: marker presence changed in a section")

    # A move is a delete plus an add, so it is verified on both sides.
    write_verified(queue_path, new_lines,
                   absent=[(slug, sec_from)], present=[(slug, sec_to)])
    sys.stderr.write("reorder_queue: moved [%s] %s -> %s (%s)%s\n"
                     % (slug, sec_from, sec_to, position or 'BOTTOM',
                        t_crossing_note))

    # Report which side of the readiness marker the item landed on. The marker
    # is a line, not an item, so "AFTER <the last cleared item>" is ambiguous:
    # positionally the marker sits between that item and the next, and a move
    # intended to CLEAR an item has landed it below the marker — shelved, not
    # cleared — with a normal success line and nothing else noticing (a live
    # defect, 2026-08-07). Stating the side makes the ambiguity visible at the
    # moment it happens rather than removing it.
    if t_had:
        marker_i = item_i = None
        for i, l in enumerate(t_out):
            if MARKER_RE.match(l):
                marker_i = i
            elif ITEM_RE.match(l) and heading_slug(l) == slug:
                # ITEM_RE guard, matching the only other heading_slug call.
                # heading_slug matches ANY line ending in [slug], not only a
                # `#### ` heading — so `Blocked by: [slug]` on a held item
                # matched too, and this loop keeps the LAST match. Whenever the
                # moved item was one that other work waits on, the report named
                # the held item's position instead of the moved item's, and
                # said "waiting, NOT cleared to run" about an item that was in
                # fact cleared. That is the dangerous direction: it invites a
                # session to correct a placement that was already right.
                item_i = i
        if marker_i is not None and item_i is not None:
            side = "ABOVE" if item_i < marker_i else "BELOW"
            state = ("cleared to run" if side == "ABOVE"
                     else "waiting, NOT cleared to run")
            sys.stderr.write(
                "reorder_queue: [%s] now sits %s the cleared-to-run marker "
                "in %s (%s)\n" % (slug, side, sec_to, state))


def main():
    args = sys.argv[1:]
    marker_pref = None
    if '--marker-after' in args:
        k = args.index('--marker-after')
        try:
            marker_pref = args[k + 1]
        except IndexError:
            die("--marker-after needs a value (a slug, TOP, or BOTTOM)")
        args = args[:k] + args[k + 2:]

    if '--append' in args:
        k = args.index('--append')
        try:
            ap_section = args[k + 1]
        except IndexError:
            die("--append needs a section: <Processed|Unprocessed>")
        rest = args[:k] + args[k + 2:]
        if '--body' not in rest:
            die("--append needs --body <path> — the entry's text lives in a "
                "file, not on the command line, because a multi-paragraph "
                "rationale does not survive shell quoting. Write it to the "
                "session scratchpad with the editing tools first.")
        b = rest.index('--body')
        try:
            body_path = rest[b + 1]
        except IndexError:
            die("--body needs a path to the file holding the entry's text")
        rest = rest[:b] + rest[b + 2:]
        if len(rest) != 1:
            die("usage: reorder_queue.py <queue_path> --append "
                "<Processed|Unprocessed> --body <path>")
        append_item(rest[0], ap_section, body_path)
        return

    if '--delete' in args:
        k = args.index('--delete')
        try:
            del_slug, del_section = args[k + 1], args[k + 2]
        except IndexError:
            die("--delete needs two values: <slug> <Section>")
        rest = args[:k] + args[k + 3:]
        if len(rest) != 1:
            die("usage: reorder_queue.py <queue_path> --delete <slug> "
                "<Processed|Unprocessed>")
        delete_item(rest[0], del_slug, del_section)
        return

    if '--retitle' in args:
        k = args.index('--retitle')
        try:
            rt_slug = args[k + 1]
        except IndexError:
            die("--retitle needs a slug")
        rest = args[:k] + args[k + 2:]
        if '--heading' not in rest:
            die("--retitle needs --heading \"<new heading text>\" — the text "
                "alone, without the slug, which the tool keeps.")
        j = rest.index('--heading')
        try:
            rt_heading = rest[j + 1]
        except IndexError:
            die("--heading needs a value")
        rest = rest[:j] + rest[j + 2:]
        if len(rest) != 1:
            die("usage: reorder_queue.py <queue_path> --retitle <slug> "
                "--heading \"<new heading text>\"")
        retitle_item(rest[0], rt_slug, rt_heading)
        return

    if '--replace-in' in args:
        k = args.index('--replace-in')
        try:
            ri_slug = args[k + 1]
        except IndexError:
            die("--replace-in needs a slug")
        rest = args[:k] + args[k + 2:]
        ri_old = ri_new = None
        for flag in ('--old', '--new'):
            if flag not in rest:
                die("--replace-in needs %s <literal string>" % flag)
            j = rest.index(flag)
            try:
                val = rest[j + 1]
            except IndexError:
                die("%s needs a value" % flag)
            if flag == '--old':
                ri_old = val
            else:
                ri_new = val
            rest = rest[:j] + rest[j + 2:]
        ri_section = None
        if '--section' in rest:
            j = rest.index('--section')
            try:
                ri_section = rest[j + 1]
            except IndexError:
                die("--section needs a value: Processed or Unprocessed")
            rest = rest[:j] + rest[j + 2:]
        if len(rest) != 1:
            die("usage: reorder_queue.py <queue_path> --replace-in <slug> "
                "--old <literal> --new <literal> [--section <Section>]")
        replace_in_item(rest[0], ri_slug, ri_old, ri_new, ri_section)
        return

    if '--move-section' in args:
        k = args.index('--move-section')
        try:
            ms_slug, ms_from, ms_to = args[k + 1], args[k + 2], args[k + 3]
        except IndexError:
            die("--move-section needs three values: <slug> <FromSection> <ToSection>")
        rest = args[:k] + args[k + 4:]
        position, anchor = 'BOTTOM', None
        if '--position' in rest:
            p = rest.index('--position')
            try:
                position = rest[p + 1]
            except IndexError:
                die("--position needs a value: TOP, BOTTOM, BEFORE, or AFTER")
            if position in ('BEFORE', 'AFTER'):
                # The anchor is POSITIONAL — it follows the direction word with
                # no flag of its own. Naming that here is the point: a session
                # that gets this wrong reaches for `--anchor <slug>` next, which
                # used to be swallowed as the anchor itself and then surface as
                # the generic usage line, two turns from the real problem.
                try:
                    anchor = rest[p + 2]
                except IndexError:
                    die("--position %s needs an anchor slug straight after it: "
                        "--position %s <anchor-slug>" % (position, position))
                if anchor.startswith('-'):
                    die("--position %s takes the anchor as a bare slug, not a "
                        "flag: --position %s <anchor-slug> (got %r)"
                        % (position, position, anchor))
                rest = rest[:p] + rest[p + 3:]
            elif position in ('TOP', 'BOTTOM'):
                rest = rest[:p] + rest[p + 2:]
            else:
                die("--position must be TOP, BOTTOM, BEFORE, or AFTER, got: "
                    + position
                    + "\nTOP and BOTTOM take nothing after them; BEFORE and "
                      "AFTER each take an anchor slug as the next bare word: "
                      "--position AFTER <anchor-slug>. There is no numeric "
                      "position.")
        if len(rest) != 1:
            die("usage: reorder_queue.py <queue_path> --move-section <slug> "
                "<FromSection> <ToSection> [--position <TOP|BOTTOM|BEFORE|AFTER> "
                "[anchor]] [--marker-after <slug|TOP|BOTTOM>]")
        move_section(rest[0], ms_slug, ms_from, ms_to, position, anchor,
                     marker_pref)
        return

    move_slug = None
    move_pos = None
    move_anchor = None
    if '--move' in args:
        k = args.index('--move')
        try:
            move_slug = args[k + 1]
            move_pos = args[k + 2]
        except IndexError:
            die("--move needs values: <slug> <TOP|BOTTOM>, or <slug> <BEFORE|AFTER> <anchor-slug>")
        if move_pos in ('BEFORE', 'AFTER'):
            try:
                move_anchor = args[k + 3]
            except IndexError:
                die("--move %s needs an anchor slug straight after it: "
                    "--move <slug> %s <anchor-slug>" % (move_pos, move_pos))
            if move_anchor.startswith('-'):
                die("--move %s takes the anchor as a bare slug, not a flag: "
                    "--move <slug> %s <anchor-slug> (got %r)"
                    % (move_pos, move_pos, move_anchor))
            args = args[:k] + args[k + 4:]
        elif move_pos in ('TOP', 'BOTTOM'):
            args = args[:k] + args[k + 3:]
        else:
            die("--move position must be TOP, BOTTOM, BEFORE, or AFTER, got: "
                + move_pos
                + "\nTOP and BOTTOM take nothing after them; BEFORE and AFTER "
                  "each take an anchor slug as the next word: "
                  "--move <slug> AFTER <anchor-slug>. There is no numeric "
                  "position.")
    if len(args) < 2:
        # The usage message lists EVERY form the script supports. It used to
        # print only two of the four, and the reader who hit an error learned
        # the tool was less capable than it is — a real close restated a full
        # 23-slug order twice when two relative moves would have done it.
        die("usage: reorder_queue.py <queue_path> <section> <slug...> "
            "[--marker-after <slug|TOP|BOTTOM>]\n"
            "   or: reorder_queue.py <queue_path> <section> --move <slug> "
            "<TOP|BOTTOM> [--marker-after ...]\n"
            "   or: reorder_queue.py <queue_path> <section> --move <slug> "
            "<BEFORE|AFTER> <anchor-slug> [--marker-after ...]\n"
            "   or: reorder_queue.py <queue_path> --move-section <slug> "
            "<FromSection> <ToSection> [--position <TOP|BOTTOM>]\n"
            "   or: reorder_queue.py <queue_path> --move-section <slug> "
            "<FromSection> <ToSection> --position <BEFORE|AFTER> "
            "<anchor-slug>\n"
            "   or: reorder_queue.py <queue_path> --delete <slug> "
            "<Processed|Unprocessed>\n"
            "For one or two items out of place, a relative --move is the "
            "cheap form; the full slug list is only needed when the whole "
            "section genuinely re-sorts.")
    queue_path, section = args[0], args[1]
    desired = args[2:]  # empty in --move mode; derived from the file below
    if move_slug is not None and desired:
        die("--move takes no positional slug list (it derives the order from "
            "the file)")
    if move_slug is None and not desired:
        die("no order supplied: pass a full slug list or use --move")
    if section not in ('Processed', 'Unprocessed'):
        die("section must be Processed or Unprocessed, got: " + section)

    with open(queue_path, 'r', encoding='utf-8', newline='') as f:
        text = f.read()
    lines = text.splitlines(keepends=True)

    sections = parse(lines)
    if section not in sections:
        die("section '%s' not found in %s" % (section, queue_path))
    start, end = sections[section]
    body = lines[start:end]
    preamble, blocks, marker_after, had_marker = split_blocks(body)

    have = [s for s, _ in blocks]

    # In --move mode, derive the desired order from the file: keep every item in
    # its current relative order, with the named slug lifted to TOP or BOTTOM.
    if move_slug is not None:
        if move_slug not in have:
            die("--move slug '%s' is not in section %s" % (move_slug, section))
        rest = [s for s in have if s != move_slug]
        if move_pos == 'TOP':
            desired = [move_slug] + rest
        elif move_pos == 'BOTTOM':
            desired = rest + [move_slug]
        else:  # BEFORE / AFTER an anchor
            if move_anchor == move_slug:
                die("--move anchor cannot be the moved slug itself")
            if move_anchor not in rest:
                die("--move anchor slug '%s' is not in section %s"
                    % (move_anchor, section))
            idx = rest.index(move_anchor) + (1 if move_pos == 'AFTER' else 0)
            desired = rest[:idx] + [move_slug] + rest[idx:]

    if sorted(have) != sorted(desired):
        die("slug set mismatch.\n  in file: %s\n  supplied: %s"
            % (sorted(have), sorted(desired)))
    if len(desired) != len(set(desired)):
        die("duplicate slug in supplied order")

    by_slug = dict(blocks)
    new_blocks = [(s, by_slug[s]) for s in desired]

    # Resolve marker placement.
    marker_line = None
    if had_marker:
        marker_line = "--- Cleared to run above this line ---\n"
        pref = marker_pref if marker_pref is not None else (
            'TOP' if marker_after is None else marker_after)

        # Re-anchor when the MOVED item is the marker's anchor.
        #
        # The marker is not stored as a position: split_blocks records it as an
        # anchor slug — the item directly above it — and elements_with_marker
        # re-inserts it after that same item, WHEREVER that item has moved to.
        # So without this branch the marker follows its anchor around the
        # section instead of holding its place, and a plain --move of the
        # anchor silently drags the readiness boundary with it. That is not a
        # cosmetic reshuffle: the marker sets how much work an unattended /next
        # run may build without the user present, so moving it as a side effect
        # of an unrelated request silently widens what an autonomous run is
        # allowed to do. Observed live: moving the anchor below a deliberately
        # shelved item cleared that item to run, and the script reported only
        # "marker placed".
        #
        # delete_item() has carried this protection since it was written; the
        # reorder path — used by both --move and the full-slug-list form — never
        # got it. The marker keeps its POSITION: it re-anchors to whatever item
        # now precedes it in the original order. An explicit --marker-after
        # always wins, because that is the caller asking for the marker to move.
        if marker_pref is None and move_slug is not None and pref == move_slug:
            idx = have.index(move_slug)
            preceding = [s for s in have[:idx] if s != move_slug]
            pref = preceding[-1] if preceding else 'TOP'

        if pref not in ('TOP', 'BOTTOM') and pref not in desired:
            die("--marker-after slug '%s' is not in the section" % pref)
    elif marker_pref is not None:
        sys.stderr.write("reorder_queue: warning: section has no marker; "
                         "--marker-after ignored\n")

    # Crossings are computed BEFORE the write, so an unnamed sweep refuses the
    # whole call rather than being reported after the fact.
    crossing_report = ""
    if had_marker:
        unnamed, crossing_report = crossing_note(
            have, 'TOP' if marker_after is None else marker_after,
            desired, pref,
            # The full-slug-list form names every slug the caller passed, so
            # nothing crosses unnamed there. --move names exactly one.
            named=[move_slug] if move_slug is not None else desired,
        )
        refuse_unnamed_crossings(unnamed, pref)

    # Build the ordered element list and reassemble with canonical spacing —
    # shared with --move-section via the two helpers.
    out = assemble_section(
        preamble,
        elements_with_marker(new_blocks, had_marker,
                             pref if had_marker else None))

    new_lines = lines[:start] + out + lines[end:]

    # ---- Self-checks: refuse to write on any failure ----
    out_text = ''.join(out)
    # 1. every block's content (heading + body, sans trailing blanks) preserved
    for s in desired:
        if ''.join(by_slug[s]) not in out_text:
            die("self-check failed: block for [%s] changed content" % s)
    # 2. marker presence preserved
    has_after = any(MARKER_RE.match(l) for l in out)
    if had_marker != has_after:
        die("self-check failed: marker presence changed")
    # 3. nothing outside the section changed
    if lines[:start] != new_lines[:start] or lines[end:] != new_lines[start + len(out):]:
        die("self-check failed: content outside the section changed")
    new_text = ''.join(new_lines)

    write_verified(queue_path, new_lines,
                   present=[(s, section) for s in desired])

    # Report the marker's ACTUAL position, not merely that one was written.
    # "marker placed" read as reassurance and said nothing: it appeared
    # identically whether the boundary held still or moved under an unrelated
    # request. What a reader needs is how much work now sits above the line.
    note = crossing_report

    sys.stderr.write("reorder_queue: %s reordered (%d items)%s\n"
                     % (section, len(desired), note))


if __name__ == '__main__':
    main()
