#!/usr/bin/env python3
"""
PostToolUse hook — advisory lint of QUEUE.md structure after edits.

Fires after Edit/Write/MultiEdit lands on the project's QUEUE.md, and after
any Bash/PowerShell command in an adopted project — a shell write bypasses the
editing tools entirely, so an edit-only trigger left that whole class unlinted.
Reads
the file from disk and flags known format violations against the
two-section work-item model:

  1. A work item whose description heading doesn't end in a [slug]. A
     work item renders as a #### heading under ## Processed or
     ## Unprocessed; the slug at the end of that heading is what lets a
     later LOG entry name the work precisely.
  2. A missing section heading — both ## Processed and ## Unprocessed
     must be present. They are the two sections the whole model runs on.
  3. A red-flag marker line ("Red flag · State: ...") whose state isn't
     one of cleared / uncleared. A red flag is an ordinary work
     line carrying this one extra marker; the state must be valid.

Provenance labels are NOT linted. The old model required every work item
to carry a "captured by you" / "by Claude" label; that requirement is
gone. The convention is asymmetric and default-AI: an unmarked item is
assumed to come from the AI, and an explicit "captured by you" credit is
written only when the user personally raised, pushed through, or wrote
the item. No AI-authorship label is ever written. Because a user-credit
is optional and an AI label is absent by design, there is nothing to
enforce — so the lint neither requires a label nor forbids one (a
leftover "by Claude" on an old item is harmless).

  4. What IS checked is narrower still: a claim about the user's WORDING
     made as an INTRODUCER — "Her words:" or "in her own words" — that
     shows no quoted text. A possessive plus "words" in ordinary prose
     claims nothing about wording and is left alone. An
     ORIGIN claim ("captured by you") is never checked, because it says
     where the item came from rather than how it was phrased, and a
     paraphrase is the normal way to state that.

Deny-list by design: only known violations are flagged; unknown or
novel structure passes in silence, so the format can evolve (new
sections, new line shapes) without fighting the linter. All findings
are advisory — fed back to Claude as context next to the tool result,
never blocking: the edit has already landed, and judging whether a
flag is real stays with the session.
"""

import json
import os
import re
import sys


# A work item renders as a #### heading; its slug sits at the end of that
# heading line (processed and unprocessed work show this way, so the list
# — including anything below the cleared-to-run line — is navigable from
# an editor outline). The heading line is the work item's description line.
WORKLINE_HEADING = re.compile(r"^####\s+\S")

# The trailing [slug] on a work-item heading: lowercase kebab, two chars
# minimum, so a stray [x] tick or an [PROMPT]-style token never counts.
SLUG_AT_END = re.compile(r"\[([a-z0-9][a-z0-9-]+)\]\s*$")

# A red-flag marker line: "Red flag · State: <state>". The middle dot is
# U+00B7 and is matched leniently (optional) so a spacing slip still reads
# as a marker and its state still gets validated.
RED_FLAG_MARKER = re.compile(r"^Red flag\s*·?\s*State:\s*(.*)$", re.IGNORECASE)

# The two sections the whole model runs on.
WORK_SECTIONS = ("Processed", "Unprocessed")

VALID_FLAG_STATES = {"cleared", "uncleared"}

# The single boundary /next runs on, and the shape of any structural
# `--- ... ---` line that legitimately sits between work items.
CLEARED_MARKER = "--- Cleared to run above this line ---"
STRUCTURAL_LINE = re.compile(r"^---\s.*---$")


def write_editing_marker(cwd: str, session_id: str, filepath: str, active: bool) -> None:
    """Clear the editing-state signal after a write. Never raises.

    The closing half of the heartbeat pre_tool_use starts: same file, same
    shape, `active` false and a fresh timestamp, keeping the last-written path
    so a reader can see which document was touched. Kept as a full rewrite
    rather than a patch of the existing file, so a marker left behind by a
    crashed session is replaced wholesale rather than merged with.

    The timestamp still leads on safety: even if this never runs — the session
    dies, the write is denied — the reader treats the stale marker as "not
    editing". Same never-fail rule as the pre-write half: any error here is
    swallowed, because a companion-app convenience must not be able to break
    the user's actual work.
    """
    try:
        import datetime

        marker_dir = os.path.join(cwd, ".throughliner")
        os.makedirs(marker_dir, exist_ok=True)
        safe_id = re.sub(r"[^A-Za-z0-9._-]", "_", session_id or "unknown")
        # Version-2 shape, kept field-for-field with pre_tool_use's opening
        # half: project-relative `files` (forward slashes, no leading "./",
        # absolute fallback for a file outside the project), `written_at` for
        # diagnosis-not-freshness, `producer` constant, pid/session dropped.
        # The version stamp and the path shape must move together — a marker
        # carrying version 2's relative paths under a version-1 stamp resolves
        # against the wrong root and holds nothing, with no error.
        if filepath:
            rel = os.path.relpath(os.path.abspath(filepath), cwd)
            marker_path = (
                os.path.abspath(filepath)
                if rel.startswith("..")
                else rel.replace(os.sep, "/")
            )
            files = [marker_path]
        else:
            files = []
        payload = {
            "version": 2,
            "active": bool(active),
            "written_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "files": files,
            "producer": "throughliner",
        }
        with open(
            os.path.join(marker_dir, f"editing-{safe_id}.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(payload, f)
    except Exception:
        return


def _normalise(path: str) -> str:
    return os.path.normcase(os.path.normpath(path))


def _annotate(content: str):
    """Yield (index, stripped line, current h2, is_heading) per line.

    h2 is the nearest preceding `## ` heading (the section the line sits
    in); is_heading is true for any markdown heading line (`#`..`######`).
    """
    h2 = None
    out = []
    for i, raw in enumerate(content.splitlines()):
        stripped = raw.strip()
        is_heading = bool(re.match(r"#{1,6}\s", raw))
        if raw.startswith("## ") and not raw.startswith("### "):
            h2 = raw[3:].strip()
        out.append((i, stripped, h2, is_heading))
    return out


def _workline_blocks(annotated):
    """Group each #### work item under a work section with its own block.

    A block is the heading line plus every following line up to the next
    #### heading, the next heading of any level, or a section change. Lines
    outside the Processed/Unprocessed sections are ignored entirely, so a
    #### heading elsewhere in the file is never treated as a work item.
    """
    blocks = []
    current = None
    for i, line, h2, is_heading in annotated:
        if h2 not in WORK_SECTIONS:
            if current:
                blocks.append(current)
                current = None
            continue
        if WORKLINE_HEADING.match(line):
            if current:
                blocks.append(current)
            current = {"idx": i, "heading": line, "lines": [line], "section": h2}
        elif is_heading:
            # Any other heading (a section change, a stray sub-heading) ends
            # the current work-item block.
            if current:
                blocks.append(current)
                current = None
        elif current is not None:
            current["lines"].append(line)
    if current:
        blocks.append(current)
    return blocks


def _check_slugs(blocks, warnings):
    """Check 1: every work-item heading ends in a [slug]."""
    for b in blocks:
        if not SLUG_AT_END.search(b["heading"]):
            warnings.append(
                # "entry", not "work item": this fires on Unprocessed blocks too,
                # and only Processed holds work items. Neutral vocabulary that is
                # true in both sections, rather than the user's, which draws a
                # distinction the parser does not.
                f"line {b['idx'] + 1}: entry {b['heading'][:60]!r} has no "
                "[slug] at the end of its description line — every entry "
                "needs one so a later LOG entry can name it."
            )


ARTICLE_HEADING_RE = re.compile(r"^####\s+(?:\[[a-z]+\]\s+)?(?:The|A|An)\b",
                                re.IGNORECASE)


def _check_heading_articles(blocks, warnings):
    """Advisory: a heading whose first word is The, A or An.

    The heading word-order rule puts distinguishing words first, because the
    queue is read through an outline that truncates each heading — and the
    rule did not fire on a fresh capture, which the user then could not find
    in her outline. This flags the article case only, not a generically
    front-loaded heading: detecting generic front-loading needs judgment a
    lint cannot have, and the message states that limit. New-heading scoping
    comes from the lint's existing split against HEAD.
    """
    for b in blocks:
        if ARTICLE_HEADING_RE.match(b["heading"]):
            warnings.append(
                f"line {b['idx'] + 1}: entry {b['heading'][:60]!r} starts "
                "with an article (The/A/An) — put the heading's "
                "distinguishing words first, since the outline view truncates "
                "each heading mid-phrase. Rewrite it in place with the queue "
                "tool: reorder_queue.py <QUEUE.md> --retitle <slug> --heading "
                "\"<new heading>\". Advisory, and it reaches the "
                "article case only, not every front-loaded heading."
            )


def _check_sections(annotated, warnings):
    """Check 2: both ## Processed and ## Unprocessed headings are present."""
    present = {h2 for _i, _l, h2, _ih in annotated if h2}
    for name in WORK_SECTIONS:
        if name not in present:
            warnings.append(
                f"the '## {name}' section heading is missing — the queue holds "
                "two sections, Processed (discussed, kept work) and Unprocessed "
                "(captured, not yet fully processed)."
            )


def _check_red_flag_states(annotated, warnings):
    """Check 3: a red-flag marker line names a valid state.

    Scans every line, not only work-item blocks: a marker is only ever
    valid under a work item, but validating it wherever it appears is the
    fail-safe direction — a stray marker with a bad state still gets caught.
    """
    for i, line, _h2, _ih in annotated:
        match = RED_FLAG_MARKER.match(line)
        if not match:
            continue
        rest = match.group(1).strip()
        token = rest.split()[0].strip(".,;:—–-").lower() if rest else ""
        if token not in VALID_FLAG_STATES:
            shown = rest[:30] if rest else "(none)"
            warnings.append(
                f"line {i + 1}: red-flag marker has state {shown!r}, but a red "
                "flag's state must be one of cleared / uncleared."
            )


def _check_readiness_marker(annotated, blocks, warnings):
    """Check 4: exactly one readiness marker, in Processed, when work exists.

    The marker is the single boundary /next runs on, so its absence or
    duplication is a structural fault even though every item validates.
    Flagged, not repaired — advisory like the rest. The dangerous half of
    the failure (a missing marker silently clearing everything) is closed
    read-side in next.md, which now treats no-marker as nothing-cleared;
    this check is what makes the fault visible at the moment of the write.
    """
    marker_lines = [
        (i, h2) for i, line, h2, _ih in annotated if line == CLEARED_MARKER
    ]
    processed_has_items = any(
        h2 == "Processed" and WORKLINE_HEADING.match(line)
        for _i, line, h2, _ih in annotated
    )
    if len(marker_lines) > 1:
        lines_shown = ", ".join(str(i + 1) for i, _s in marker_lines)
        warnings.append(
            f"lines {lines_shown}: the cleared-to-run marker appears "
            f"{len(marker_lines)} times — there must be exactly one; /next "
            "runs on a single boundary and two markers make the run bound "
            "ambiguous."
        )
    elif not marker_lines and processed_has_items:
        warnings.append(
            "Processed holds work items but the '--- Cleared to run above "
            "this line ---' marker is missing — /next treats a missing "
            "marker as NOTHING cleared, so no work will run until the "
            "marker is restored."
        )
    for i, h2 in marker_lines:
        if h2 == "Unprocessed":
            warnings.append(
                f"line {i + 1}: the cleared-to-run marker sits in Unprocessed "
                "— it belongs in Processed, where it bounds what /next may "
                "run."
            )


BLOCKED_BY_LINE = re.compile(r"^\*{0,2}Blocked by:?\*{0,2}\s*(.+)$", re.IGNORECASE)
SLUG_REF = re.compile(r"\[([a-z0-9][a-z0-9-]*)\]")
# `Not before: YYYY-MM-DD` — the second thing that may hold an item below the
# line. The date is captured loosely here and validated as a real calendar date
# by _parse_not_before, so a malformed date is reported rather than accepted.
NOT_BEFORE_LINE = re.compile(
    r"^\*{0,2}Not before:?\*{0,2}\s*(.+?)\s*$", re.IGNORECASE
)


def _parse_not_before(raw):
    """A `Not before:` value as a date, or None when it is not a real one.

    Held-until-a-date is the one holding fact that resolves itself: no session
    and no user has to confirm it, so the lint's whole job here is making sure
    the date can actually be read. A value that is not a real `YYYY-MM-DD`
    would sit unnoticed and hold the item forever.
    """
    import datetime

    try:
        return datetime.date.fromisoformat(raw.strip())
    except ValueError:
        return None


def _check_blocked_by(annotated, blocks, warnings):
    """Check 5: below the line means blocked by a named queue item.

    Below-the-line used to mean "shelved for any reason", with the reason
    written as a prose lift-condition inside the item — a sentence like
    "cleared once [slug] ships" or "after a full computer restart". That model
    failed in a specific, repeated way: a blocker written as a sentence inside
    another item's prose is invisible as work, so nothing ever picks it up. One
    item sat below the line for weeks with a genuine user action buried in its
    lift-condition; the moment it was split out as its own work item it became
    visible immediately.

    So the rule is now exactly two things, and both name the holding fact on the
    item itself: an item sits below the marker if and only if a NAMED queue item
    blocks it (`Blocked by: [slug]`) or a date it must not be built before has
    not yet passed (`Not before: YYYY-MM-DD`). Anything else waiting on the world
    gets described as its own item in Unprocessed, where /plan will process it,
    and the blocked item names that item as its blocker.

    A date earns its own field rather than a proxy item because it resolves
    itself: every other blocker needs a human or a build to clear it, which is
    why blockers are queue items, but a date is checkable by a script and costs
    no attention at all. Expressing one as a capture someone has to confirm cost
    a planning session per post and still failed — the item it was pacing simply
    never went out. This check is what makes
    the rule real rather than a convention sessions drift from — the below-line
    population becomes derivable instead of remembered.

    Advisory like every other check here: it reports, never blocks or repairs.

    On "sits above": the queue item that decided this asked for a blocker that
    "resolves and sits above the item", which reads naturally but cannot be
    taken as literal file order — Unprocessed sits BELOW Processed in the file,
    and an Unprocessed blocker is the rule's own recommended shape. So above-ness
    is checked only where it means something: within Processed, where position
    is build order. A blocker in Unprocessed is fine by construction.

    Two parts of this check span BOTH sections, because both fields are
    available in both. `Not before:` on a capture means "do not offer this again
    before this date" rather than "do not build this yet", so an unparseable date
    holds an Unprocessed entry out of view forever. `Blocked by:` on a capture
    means "do not offer this again while the named entry is open", so a slug
    resolving to nothing is a hold nothing can lift — and on a capture there is
    no marker position to give the mistake away: the entry simply stops being
    offered, silently, for good. So the malformed-date warning, the slug
    resolution and the names-itself case all run in both sections.

    The above/below warnings stay scoped to Processed, because position relative
    to the marker means nothing outside it — and so does the blocker-sits-below
    ordering warning, which reads build order.
    """
    marker_idx = next(
        (i for i, line, _h2, _ih in annotated if line == CLEARED_MARKER), None
    )
    if marker_idx is None:
        # A missing marker is already reported by the readiness check, and
        # without one there is no below-the-line to check.
        return

    known = {}
    for b in blocks:
        m = SLUG_AT_END.search(b["heading"])
        if m:
            known[m.group(1)] = b

    for b in blocks:
        below = b["idx"] > marker_idx
        refs = []
        dates = []
        bad_dates = []
        for line in b["lines"][1:]:
            m = BLOCKED_BY_LINE.match(line)
            if m:
                refs.extend(SLUG_REF.findall(m.group(1)))
            d = NOT_BEFORE_LINE.match(line.strip())
            if d:
                parsed = _parse_not_before(d.group(1))
                if parsed is None:
                    bad_dates.append(d.group(1))
                else:
                    dates.append(parsed)

        # The malformed-date check runs in BOTH sections, because `Not before:`
        # is available in both: on a work item it means do not build before the
        # date, on a capture it means do not offer it again before the date. An
        # unparseable date holds the entry forever either way, and an Unprocessed
        # entry is the case nothing else here would ever look at.
        for raw in bad_dates:
            warnings.append(
                f"line {b['idx'] + 1}: {b['heading'][:60]!r} carries "
                f"'Not before: {raw}', which is not a date in YYYY-MM-DD form. "
                "A date nobody can read holds the entry forever, because nothing "
                "can ever tell that it has passed."
            )

        # Slug resolution runs in BOTH sections, for the same reason the
        # malformed-date check does: `Blocked by:` is available in both. On a
        # work item it means do not build this until the named entries resolve;
        # on a capture it means do not offer this again while one is still open.
        # A slug that resolves to nothing is a hold nothing can ever lift, and on
        # a capture there is no marker position to give the mistake away — the
        # entry simply stops being offered, silently, forever.
        for slug in refs:
            target = known.get(slug)
            if target is None:
                warnings.append(
                    f"line {b['idx'] + 1}: {b['heading'][:60]!r} is blocked by "
                    f"[{slug}], which is not in the queue right now. That has "
                    "four causes: the blocker has "
                    "already shipped and been removed, it is in flight (a run "
                    "has taken it into its build working file), it was "
                    "DELETED as not worth doing, or the reference is wrong. "
                    "Only the last is a fault in the reference — but deletion "
                    "is not benign either: the held entry was written assuming "
                    "its blocker would happen, so its premise may not survive "
                    "and it needs re-examining rather than lifting. "
                    "Check LOG before changing anything — a correct reference "
                    "reads exactly like a broken one here."
                )
            elif target["idx"] == b["idx"]:
                warnings.append(
                    f"line {b['idx'] + 1}: {b['heading'][:60]!r} names itself "
                    "as its own blocker."
                )

        # Everything below is about position relative to the cleared-to-run
        # marker, which only means something inside Processed.
        if b["section"] != "Processed":
            continue

        if not below:
            if refs:
                warnings.append(
                    f"line {b['idx'] + 1}: {b['heading'][:60]!r} sits ABOVE the "
                    "cleared-to-run marker but carries a 'Blocked by:' line — "
                    "cleared work has nothing blocking it. Either move it below "
                    "the marker or drop the blocker."
                )
            if dates:
                warnings.append(
                    f"line {b['idx'] + 1}: {b['heading'][:60]!r} sits ABOVE the "
                    "cleared-to-run marker but carries a 'Not before:' line — "
                    "cleared work has nothing holding it. Either move it below "
                    "the marker or drop the date."
                )
            continue

        if not refs and not dates:
            warnings.append(
                f"line {b['idx'] + 1}: {b['heading'][:60]!r} sits below the "
                "cleared-to-run marker with no 'Blocked by: [slug]' line and no "
                "'Not before: YYYY-MM-DD' line. Below the line means held by a "
                "named queue item or by a date, and nothing else — if nothing "
                "holds it, move it above the marker; if it waits on something in "
                "the world, file that as its own item in Unprocessed and name it "
                "here."
            )
            continue

        if not refs:
            # Held by a date alone, which is complete on its own: a date needs
            # no blocker item, because it resolves without anyone confirming it.
            continue

        # Resolution and the self-blocker case are already reported above, for
        # both sections. What is left here is the one check that reads position:
        # within Processed, order is build order, so a blocker must come first.
        for slug in refs:
            target = known.get(slug)
            if target is None or target["idx"] == b["idx"]:
                continue
            if target["section"] == "Processed" and target["idx"] > b["idx"]:
                warnings.append(
                    f"line {b['idx'] + 1}: {b['heading'][:60]!r} is blocked by "
                    f"[{slug}], which sits BELOW it in Processed. Within "
                    "Processed, position is build order, so a blocker must come "
                    "first."
                )


def _check_orphaned_prose(annotated, warnings):
    """Check 5: every non-blank line in a work section belongs to a block.

    A line is orphaned when it sits inside Processed or Unprocessed with no
    #### heading above it (since the section started, or since a non-item
    heading ended the previous block). Structural `--- ... ---` marker lines
    are exempt, and so are blockquote lines (`> ...`): /setup scaffolds each
    work section's description paragraph as a blockquote immediately under the
    section heading — positionally identical to a destroyed first item's
    stranded rationale, so position cannot discriminate; form does. A stranded
    work-item rationale is never a blockquote. One flag per contiguous orphan
    run, so a destroyed heading yields one warning rather than one per
    rationale line.
    """
    in_block = False
    flagged_run = False
    for i, line, h2, is_heading in annotated:
        if h2 not in WORK_SECTIONS:
            in_block = False
            flagged_run = False
            continue
        if WORKLINE_HEADING.match(line):
            in_block = True
            flagged_run = False
            continue
        if is_heading:
            # A section heading or stray sub-heading ends any block.
            in_block = False
            flagged_run = False
            continue
        if not line or STRUCTURAL_LINE.match(line) or line.startswith(">"):
            flagged_run = False if not line else flagged_run
            continue
        if not in_block and not flagged_run:
            warnings.append(
                # "entry" for the same reason as the slug warning above.
                f"line {i + 1}: prose belongs to no entry — the text "
                f"starting {line[:50]!r} has no #### heading above it in this "
                "section. A destroyed or missing heading leaves an item's "
                "rationale orphaned like this; check whether an item's "
                "heading line was overwritten."
            )
            flagged_run = True


# Two different claims, and only one of them is about wording.
#
# An ORIGIN claim — "captured by you", "you raised this" — says where something
# came from. A paraphrase is the normal way to state it, so requiring a quote
# applies a wording test to a claim that was never about wording, and the
# cheapest way to satisfy it is to ask the user to prove her own work is hers.
# Origin claims are therefore not checked at all.
#
# A QUOTE claim — "your words", quotation marks — is about wording, and shows
# the words or it is unsupported. That is the bar this check makes visible.
# Each pronoun needs both forms: "her words" does not match "her own words",
# which is the phrasing this corpus actually reaches for most often, so the
# check silently passed every one of them until a test exercised it.
QUOTE_CLAIM_PHRASES = (
    "your own words",
    "your words",
    "her own words",
    "her words",
    "his own words",
    "his words",
    "their own words",
    "their words",
    "the user's own words",
)
# The phrase alone is not the claim. A possessive plus "words" appears in
# ordinary prose that claims nothing about wording — "her words as closely as
# he can recall them" is a consumer's sentence this check flagged, and it is a
# disclaimer of verbatimness rather than a claim of it. What makes it a quote
# claim is an INTRODUCER: the phrase followed by a colon ("Her words:"), or
# the "in <possessive> own words" form. Only those two shapes fire.
_QUOTE_PHRASE_ALT = "|".join(re.escape(p) for p in QUOTE_CLAIM_PHRASES)
QUOTE_CLAIM_INTRODUCERS = (
    re.compile(r"(" + _QUOTE_PHRASE_ALT + r")\s*:", re.IGNORECASE),
    re.compile(
        r"in\s+(your|her|his|their|the user's)\s+own\s+words", re.IGNORECASE
    ),
)
# What counts as showing them: a quoted string of any of the three shapes this
# corpus actually uses. Deliberately generous — the check exists to catch a
# credit with NOTHING quoted anywhere in the item, not to police quote style.
QUOTE_SHAPES = (
    re.compile(r"[“”][^“”]{3,}[“”]"),
    re.compile(r'"[^"]{3,}"'),
    re.compile(r"^>\s+\S", re.MULTILINE),
)


def _check_quote_claim_without_quote(blocks, warnings):
    """Check 6: an item claiming the user's WORDS shows some of them.

    Advisory, like everything here. It cannot tell invented reasoning from real
    reasoning and must never be described as if it could — what it does is
    raise the cost of an unsupported credit from nothing to fabricating a
    quotation, and make the omission visible to a reader. That is a real
    difference and it is not verification.

    Why it fires here rather than in a digest read hours later: the failure
    happens at the moment of writing, so the report belongs at the write.

    The accepted miss, stated rather than discovered: only an introducer shape
    fires — the phrase followed by a colon, or "in <possessive> own words". A
    quote claim made in some other construction goes uncaught. That is the
    price of not flagging ordinary prose that merely contains a possessive and
    "words", which this check did until a consumer's sentence was flagged.
    """
    for b in blocks:
        text = "\n".join(b["lines"])
        match = next(
            (m for m in (r.search(text) for r in QUOTE_CLAIM_INTRODUCERS) if m),
            None,
        )
        if not match:
            continue
        claimed = match.group(0).strip()
        if any(shape.search(text) for shape in QUOTE_SHAPES):
            continue
        warnings.append(
            f"line {b['idx'] + 1}: {b['heading'][:60]!r} says "
            f'"{claimed}" but quotes nothing. That phrase claims the user\'s '
            "wording, so it needs the words themselves — quote them, or say "
            "where the item came from instead (\"captured by you\"), which "
            "claims origin and needs no quote."
        )


RULE_GATE_LINE = re.compile(r"^\*{0,2}Rule gate:?\*{0,2}\s", re.IGNORECASE)

# The rule gate's own trigger-path set, as enumerated in the host CLAUDE.md.
# Literal substrings, matched against an item's whole block: an item whose
# work touches any of these is authoring or amending a method rule. The
# `resources/` entries are written unprefixed deliberately — as substrings they
# match the `workshop/resources/` form these files moved to as well as the old
# root path, so a project mid-migration is covered from both sides.
GATE_TRIGGER_PATHS = (
    "plugin/throughliner/docs/",
    "resources/self-authoring-rules.md",
    "resources/rule-maintenance.md",
    "resources/method-compliance-audit-checklist.md",
    "CLAUDE.md",
)


# The lines that name what an item's build changes. Only these are read by the
# two path-scoped checks below — a path mentioned in rationale prose is not a
# claim that the build touches it, and matching the whole block would flag
# every item that merely discusses the queue or a doc.
FILES_LINE = re.compile(r"^\*{0,2}(Files|Changes):?\*{0,2}\s", re.IGNORECASE)


def _files_text(b):
    return "\n".join(l for l in b["lines"][1:] if FILES_LINE.match(l))


def _block_slug(b):
    m = SLUG_AT_END.search(b["heading"])
    return m.group(1) if m else b["heading"][:40]


def _check_duplicate_gate_lines(blocks, warnings):
    """Check 9: an item block carries its `Rule gate:` line at most once.

    A processed item was found carrying the line twice, the second a truncated
    copy of the first — two dispositions on one item make the record ambiguous
    about which one was authored. Advisory: flagged by slug, never repaired.
    """
    for b in blocks:
        gate_lines = [l for l in b["lines"][1:] if RULE_GATE_LINE.match(l)]
        if len(gate_lines) >= 2:
            warnings.append(
                f"line {b['idx'] + 1}: [{_block_slug(b)}] carries "
                f"{len(gate_lines)} 'Rule gate:' lines — duplicate Rule gate: "
                "line; keep the authored one."
            )


def _check_cleared_gate_disposition(annotated, blocks, warnings):
    """Check 10: a cleared rule-touching item carries a gate disposition.

    The gate's site is the keep-step, and /next only transcribes — so an item
    that names a gate-trigger path and clears with no `Rule gate:` line sends a
    build into a halt the keep-step should have prevented. Scoped to cleared
    items only: held work and captures are not yet through the keep-step.
    """
    marker_idx = next(
        (i for i, line, _h2, _ih in annotated if line == CLEARED_MARKER), None
    )
    if marker_idx is None:
        return
    for b in blocks:
        if b["section"] != "Processed" or b["idx"] > marker_idx:
            continue
        files = _files_text(b)
        if not any(p in files for p in GATE_TRIGGER_PATHS):
            continue
        if any(RULE_GATE_LINE.match(l) for l in b["lines"][1:]):
            continue
        warnings.append(
            f"line {b['idx'] + 1}: [{_block_slug(b)}] — rule-touching item "
            "cleared with no gate disposition. Its work names a rule-gate "
            "trigger path, so the keep-step owes it a 'Rule gate:' line; "
            "without one the build halts rather than composing a disposition."
        )


def _check_cleared_names_queue(annotated, blocks, warnings):
    """Check 11: a cleared item whose work names QUEUE.md cannot be built.

    A run never reads or edits the queue — the scope-lock refuses it — so an
    item whose described work is queue content can be cleared but never built,
    whatever its flavor. Queue content is planning work. Flagged by slug.
    """
    marker_idx = next(
        (i for i, line, _h2, _ih in annotated if line == CLEARED_MARKER), None
    )
    if marker_idx is None:
        return
    for b in blocks:
        if b["section"] != "Processed" or b["idx"] > marker_idx:
            continue
        if "QUEUE.md" not in _files_text(b):
            continue
        warnings.append(
            f"line {b['idx'] + 1}: [{_block_slug(b)}] names QUEUE.md — a run "
            "cannot reach the queue; queue content is planning work."
        )


# Check 8, the cleared-item-must-carry-a-build-block check, is RETIRED
# (2026-08-27, [builds-read-the-queue-again]).
#
# It existed because a run read a generated view assembled from those delimited
# blocks: an item without one reached the run with no instructions at all. A run
# now reads each item whole from this file, so there is no block that can be
# missing. What replaces it is not another check — an item that fails to say
# what changes inside the files it names is underspecified, and that is judgment
# the decision step makes and no delimiter can test.
#
# The delimiters themselves are left alone wherever they still sit in existing
# items: they read as ordinary text now, and rewriting them would be editing
# records to match a vocabulary they predate.


# The three field markers whose readers are ALL anchored to the start of a
# line — the queue digest's flag scan, the session opening's dependency facts,
# this lint, and the queue mover. A marker written mid-line is therefore
# invisible to every one of them, and it fails silently: nothing errors, the
# field simply does not exist as far as the tools are concerned.
#
# The instance: an item's red flag sat at the end of a prose sentence and the
# digest never reported it, so the ordering ladder's "an uncleared red flag
# outranks everything" rung fired by luck rather than by machinery. A vanished
# `Blocked by:` or `Not before:` is worse still — it releases held work early.
#
# Flagging at the WRITING end is the deliberate choice. The tolerate-at-the-
# reading-end move has already been taken twice in this family (widening the
# patterns for a bolded `Rule gate:`), and it leaves the deviation itself
# invisible. One canonical shape, checked where it is written.
MID_LINE_MARKERS = ("Red flag · State:", "Blocked by:", "Not before:",
                    "Cycle:")


def _check_mid_line_markers(annotated, warnings):
    """Flag a field marker that is not at the start of its line."""
    in_fence = False
    for i, line, h2, is_heading in annotated:
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        # A fenced block is where the markers are legitimately QUOTED — the
        # section preamble shows the line format, and an item may show one as
        # an example. Quoting a shape is not writing a field.
        if in_fence or is_heading:
            continue
        if h2 not in ("Processed", "Unprocessed"):
            continue
        for marker in MID_LINE_MARKERS:
            pos = line.find(marker)
            if pos <= 0:
                continue
            # `**Blocked by:` is the ordinary Markdown instinct and every
            # reader tolerates the emphasis, so it is not a deviation.
            if line[:pos].strip("*") == "":
                continue
            # A field name inside backticks is prose DISCUSSING the mechanism
            # — "rather than by a `Blocked by:` line" — not a field being
            # written, and no reader would parse it either way. A corpus-wide
            # check found every mid-line occurrence backticked and zero bare,
            # so this drops the false positives (nine per tool call in one
            # live session) and loses no real case: a load-bearing field
            # written bare mid-line is still caught.
            if line.count("`", 0, pos) % 2 == 1:
                continue
            warnings.append(
                f"line {i + 1}: '{marker}' appears mid-line rather than at the "
                "start of its own line. Every tool that reads this field — the "
                "queue digest, the session opening, this lint, the queue mover "
                "— anchors to the start of a line, so as written the field is "
                "invisible to all of them and fails silently. Put it on its own "
                "line, or in backticks where the words are prose discussing "
                "the field."
            )
    _check_unbracketed_blocker(annotated, warnings)


def _check_unbracketed_blocker(annotated, warnings):
    """Flag a `Blocked by:` line whose blocker is not in square brackets.

    Same silent-failure family as the mid-line markers above, caught at the
    writing end for the same reason. Every reader of this field matches
    `[slug]`, so `Blocked by: bravo` parses to no blockers at all: the digest
    prints nothing for it and reads the item as unheld, while the item itself
    stays below the readiness line and is never built. The below-the-line
    revisit works by reading what each held item names, so an item naming
    nothing has no arm of the revisit — not lifted, not surfaced, not flagged.
    Silent and permanent.

    Reproduced under control by a consumer project on a four-item scratch queue,
    where the bracketed and unbracketed forms sat side by side and only the
    bracketed one resolved. Caught there by eye rather than by any tool.
    """
    in_fence = False
    for i, line, h2, is_heading in annotated:
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or is_heading:
            continue
        if h2 not in ("Processed", "Unprocessed"):
            continue
        match = BLOCKED_BY_LINE.match(line.strip())
        if not match:
            continue
        if SLUG_REF.search(match.group(1)):
            continue
        warnings.append(
            f"line {i + 1}: 'Blocked by:' names no slug in square brackets, so "
            "every reader of this field parses it as no blocker at all — the "
            "item stays below the readiness line and nothing will ever lift "
            f"it. Write the blocker as [slug]: {line.strip()}"
        )


def lint(content: str) -> list[str]:
    annotated = _annotate(content)
    blocks = _workline_blocks(annotated)
    warnings = []
    _check_slugs(blocks, warnings)
    _check_heading_articles(blocks, warnings)
    _check_sections(annotated, warnings)
    _check_red_flag_states(annotated, warnings)
    _check_mid_line_markers(annotated, warnings)
    _check_readiness_marker(annotated, blocks, warnings)
    _check_blocked_by(annotated, blocks, warnings)
    _check_orphaned_prose(annotated, warnings)
    _check_quote_claim_without_quote(blocks, warnings)
    _check_duplicate_gate_lines(blocks, warnings)
    _check_cleared_gate_disposition(annotated, blocks, warnings)
    _check_cleared_names_queue(annotated, blocks, warnings)
    return warnings


def _item_word_counts(content: str) -> dict:
    """{slug: word count} for every work item in a queue's text.

    The readiness marker is excluded from every item's span. It is not part of
    any item — it sits between them — but it falls inside the span of whichever
    item it happens to follow, so moving the line alone changed that item's
    count and the report named an item the edit never touched. Six words
    attributed to the wrong work is worse than no report: the reader goes and
    reads an item that did not change.
    """
    counts = {}
    for b in _workline_blocks(_annotate(content)):
        m = SLUG_AT_END.search(b["heading"])
        if m:
            body = [ln for ln in b["lines"] if ln.strip() != CLEARED_MARKER]
            counts[m.group(1)] = len("\n".join(body).split())
    return counts


def _item_sections(content: str) -> dict:
    """{slug: section name} for every work item, read from the same blocks."""
    sections = {}
    for b in _workline_blocks(_annotate(content)):
        m = SLUG_AT_END.search(b["heading"])
        if m:
            sections[m.group(1)] = b.get("section")
    return sections


def _section_medians(counts: dict, sections: dict) -> dict:
    """{section name: median word count of its items}, as the queue now stands.

    The median is the bound the always-loaded authoring standard reads off the
    corpus — the same count `scripts/measure_written_shape_length.py` prints,
    counted the same way (whitespace-split words; copied rather than imported,
    since a hook runs standalone from a copied cache). Printed beside a changed
    item's total so the bound is in front of the writer at the moment of
    writing. A number, not a threshold: nothing here judges it.
    """
    by_section = {}
    for slug, count in counts.items():
        by_section.setdefault(sections.get(slug), []).append(count)
    medians = {}
    for section, values in by_section.items():
        values = sorted(values)
        n = len(values)
        if n == 0:
            continue
        mid = n // 2
        medians[section] = (values[mid] if n % 2
                            else (values[mid - 1] + values[mid]) / 2)
    return medians


_SECTION_SHAPE = {"Processed": "work items", "Unprocessed": "captures"}


def _head_queue(cwd: str) -> str:
    """QUEUE.md as last committed, or "" when there is no answer.

    git is the state. A cached copy on disk would be a state file that must be
    maintained, and the first session that forgets makes the output lie — the
    same ground on which one was refused for the growth report.

    Never raises: no git, no repository, or no committed QUEUE.md returns "".
    """
    try:
        import subprocess

        proc = subprocess.run(
            ["git", "show", "HEAD:QUEUE.md"],
            cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            encoding="utf-8", errors="replace", timeout=15,
        )
        if proc.returncode != 0 or not proc.stdout:
            return ""
        return proc.stdout
    except Exception:
        return ""


def _snapshot_queue(cwd: str) -> str:
    """QUEUE.md as last snapshotted, or "" — the untracked project's baseline.

    Untracked-by-design is the configuration setup proposes, so a missing
    committed copy is normal there — and treating it as everything-new made
    the whole standing flag set print after every tool call, which is the
    cry-wolf shape this lint exists to avoid. The pre-change snapshots exist
    precisely because these files have no git history: the newest one is the
    previous version of the queue, so a report against it means "what this
    change introduced", exactly what the committed copy means for a tracked
    project. Never raises.
    """
    snap_dir = os.path.join(cwd, ".throughliner", "snapshots")
    try:
        names = [n for n in os.listdir(snap_dir)
                 if n.startswith("QUEUE.md@")]
    except OSError:
        return ""
    if not names:
        return ""
    # The stamp suffix is zero-padded (%Y%m%dT%H%M%S%f), so the lexical
    # maximum is the newest snapshot.
    try:
        with open(os.path.join(snap_dir, max(names)), "r",
                  encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def _baseline_queue(cwd: str):
    """(content, kind) — the queue's previous version, from wherever one exists.

    kind is "commit", "snapshot", or None. Both warning directions — new
    flags and cleared flags — read this same baseline, so they cannot
    disagree about what the previous version was.
    """
    head = _head_queue(cwd)
    if head:
        return head, "commit"
    snap = _snapshot_queue(cwd)
    if snap:
        return snap, "snapshot"
    return "", None


# A warning's line number moves whenever anything above it is edited, but its
# body names the item, so the body is what identifies the same finding across
# two versions of the file.
_WARN_PREFIX_RE = re.compile(r"^line \d+: ")


def _warning_body(warning: str) -> str:
    return _WARN_PREFIX_RE.sub("", warning)


def _split_warnings(warnings: list, head_content: str):
    """(new, pre_existing) — findings this working tree introduced, and the rest.

    Pre-existing flags were shown in full on every fire, so five standing flags
    in a long queue were re-reported after every edit and every shell command.
    Identical advisory output repeated is what gets skimmed past, and being
    skimmed past is what makes a genuine new flag invisible. Reporting against
    HEAD gives the new finding — the work just done — the full message, and
    collapses everything else to a count.
    """
    if not head_content:
        return list(warnings), []
    try:
        known = {_warning_body(w) for w in lint(head_content)}
    except Exception:
        return list(warnings), []
    new, old = [], []
    for w in warnings:
        (old if _warning_body(w) in known else new).append(w)
    return new, old


_LINT_STATE_NAME = "queue-lint-last.json"


def _read_lint_state(cwd: str):
    """The warning bodies the previous lint run found, or None.

    A cleared flag's "gone" notice reads this rather than the commit: against
    the commit a flag cleared this session stays "gone" after every tool call
    until /done commits, and one notice printed dozens of times in a
    session. Missing or unreadable means no gone notices this run — never an
    error, since the lint is advisory.
    """
    path = os.path.join(cwd, ".throughliner", _LINT_STATE_NAME)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(data, list):
        return None
    return {b for b in data if isinstance(b, str)}


def _write_lint_state(cwd: str, warnings: list) -> None:
    """Record this run's warning bodies for the next run's gone direction.

    The folder is the project's ignored `.throughliner/`, which already holds
    the hook's snapshots. A failure to write changes nothing the lint reports.
    """
    folder = os.path.join(cwd, ".throughliner")
    try:
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, _LINT_STATE_NAME), "w",
                  encoding="utf-8") as f:
            json.dump(sorted({_warning_body(w) for w in warnings}), f)
    except (OSError, TypeError, ValueError):
        pass


def _cleared_warnings(warnings: list, head_content: str) -> list:
    """Flags the last commit carried that the working tree no longer does.

    The other half of reporting a CHANGE rather than a state. A flag appearing
    is worth a line; a flag going away is worth one too, and between them they
    are the whole of what has changed — which is why an unchanged set can then
    say nothing at all.
    """
    if not head_content:
        return []
    try:
        head_warnings = lint(head_content)
    except Exception:
        return []
    current = {_warning_body(w) for w in warnings}
    return [w for w in head_warnings if _warning_body(w) not in current]


def _growth_report(cwd: str, content: str) -> list[str]:
    """Per-item word deltas since the last commit, as bare facts.

    **No threshold, no verdict, and none may be added.** A threshold here would
    be a bare number, and the research this rests on states explicitly that no
    band may be read off this corpus, because this corpus is the bloated one.
    The report makes growth visible and enforces nothing — the same register as
    the readiness-line crossing report the queue mover prints.

    The baseline is the queue as last committed, not as it stood before this
    particular edit. A hook is given no before-image, and the alternative was a
    cached copy on disk — a state file that must be maintained, where the first
    session that forgets makes the output lie. Since a session's edits are
    reported against the state its work started from, the committed version is
    the honest baseline and needs nothing kept in step.

    Never raises: no git, no repository, or no committed QUEUE.md returns
    nothing at all.
    """
    try:
        import subprocess

        proc = subprocess.run(
            ["git", "show", "HEAD:QUEUE.md"],
            cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            encoding="utf-8", errors="replace", timeout=15,
        )
        if proc.returncode != 0 or not proc.stdout:
            return []
        before = _item_word_counts(proc.stdout)
    except Exception:
        return []

    now = _item_word_counts(content)
    return _growth_lines(before, now, _item_sections(content))


def _growth_lines(before: dict, now: dict, sections: dict) -> list[str]:
    """One line per changed item: the growth, the item's total now, and the
    median of its section's items — "[slug] +119 words, now 916; work items
    median 525". The total and the median are the two facts the authoring
    bound is read against; the growth alone said nothing about either."""
    medians = _section_medians(now, sections)
    lines = []
    for slug, count in now.items():
        was = before.get(slug)
        if was is None or count == was:
            continue
        section = sections.get(slug)
        shape = _SECTION_SHAPE.get(section, "items")
        median = medians.get(section)
        median_text = (f"{median:g}" if median is not None else "n/a")
        lines.append(f"[{slug}] {count - was:+d} words, now {count}; "
                     f"{shape} median {median_text}")
    return lines


# --- Secret-shape scan ---
#
# Runs over the project's own prose docs (QUEUE.md, SPEC.md, LOG/) because those
# get committed, and a commit is permanent even if the text is deleted later.
#
# HIGH-CONFIDENCE SHAPES ONLY, and that narrowness is the design rather than a
# limitation. This scan's only value is that it is deterministic: it either
# matches a shape or it doesn't, so it never produces false confidence. The
# moment it started guessing at whether prose is sensitive it would become
# another judgment pass wearing a machine's authority.
#
# WHAT IT CANNOT DO, and this must never be sanded off. The thing that actually
# leaks from these docs is ordinary prose about a real person or a real case,
# and no pattern catches that. So this scan must never be described to a user as
# "your files are scrubbed" — a gate that over-claims is worse than no gate,
# because the user publishes more freely believing it worked. The same line the
# method holds on red flags: provide risk-addressing, never promise risk
# management. The prose half is a pre-write checklist Claude runs (see
# skill-nonspecific-rules.md), and the real protection for a public repo is not
# publishing these artifacts at all.
#
# Advisory, like every check in this file. It reports; it never blocks or edits.
#
# Distinct from scripts/scrub_sweep.py, which is an on-demand, human-run,
# whole-repo sweep for OTHER PEOPLE's names. Different question, different
# trigger, and neither replaces the other.
SECRET_SHAPES = (
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "a private-key block"),
    (re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{16,}"), "an Anthropic API key"),
    (re.compile(r"\bsk-[A-Za-z0-9]{32,}"), "an API key"),
    (re.compile(r"\b(?:ghp|gho|ghu|ghs)_[A-Za-z0-9]{20,}"), "a GitHub token"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"), "a GitHub fine-grained token"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "an AWS access key id"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}"), "a Slack token"),
    (re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b"), "a Google API key"),
    (re.compile(r"\b[0-9a-fA-F]{32,}\b"), "a long hex string"),
    # No `/` in the class, and a digit and a capital are both required. Without
    # those three constraints this matched an ordinary filesystem path in a LOG
    # entry (`~/.claude/plugins/cache/flintcraft/throughliner`) — a run
    # of forty-odd letters and slashes reads as base64 to a regex. Real base64
    # secrets carry digits and mixed case; prose and paths usually don't.
    (
        re.compile(
            r"\b(?=[A-Za-z0-9+]*[0-9])(?=[A-Za-z0-9+]*[A-Z])"
            r"[A-Za-z0-9+]{40,}={0,2}\b"
        ),
        "a long base64-looking string",
    ),
    (
        re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),
        "an email address",
    ),
)

SCANNED_DOCS = ("QUEUE.md", "SPEC.md")


def _is_scannable_doc(filepath: str, cwd: str) -> bool:
    norm = _normalise(filepath)
    for doc in SCANNED_DOCS:
        if norm == _normalise(os.path.join(cwd, doc)):
            return True
    log_dir = _normalise(os.path.join(cwd, "LOG"))
    return norm.startswith(log_dir + os.sep)


def _scan_secrets(path: str) -> list:
    """Report high-confidence secret shapes in a project prose doc."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    except (OSError, UnicodeDecodeError):
        return []

    found = []
    for n, line in enumerate(lines, 1):
        for pattern, label in SECRET_SHAPES:
            m = pattern.search(line)
            if m:
                snippet = m.group(0)
                if len(snippet) > 12:
                    snippet = snippet[:6] + "…" + snippet[-4:]
                found.append(
                    f"line {n}: {label} ({snippet}). This file gets committed, "
                    "and a commit keeps the text even if you delete it later."
                )
                break
    return found[:10]


def _emit(message: str) -> int:
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": message,
        }
    }
    json.dump(output, sys.stdout)
    return 0


def _lint_queue(queue_path: str, with_growth: bool = True) -> int:
    """Lint QUEUE.md at `queue_path` and emit any warnings as advisory context.

    Shared by both entry paths — an edit that landed on QUEUE.md, and any shell
    command in an adopted project. A missing or unreadable file is silently
    fine: this hook is advisory and never fails a tool call.

    `with_growth` is False for the shell path, where the tool input does not say
    which file was written, so a run of unrelated commands would otherwise
    re-emit an identical growth report after each one. The residual is stated
    rather than solved: a shell command CAN reach the queue through a script,
    and that write now gets no growth report. Closing it needs remembered state
    between fires, which is refused here on the project's own ground — a state
    file must be maintained, and the first session that forgets makes the output
    lie. The lint itself still runs on the shell path, so corruption is caught.
    """
    try:
        with open(queue_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        return 0

    cwd = os.path.dirname(queue_path) or "."
    baseline_content, baseline_kind = _baseline_queue(cwd)

    sections = []
    warnings = lint(content)
    # The gone direction's baseline is the previous lint RUN, not the commit;
    # read before this run's bodies overwrite it.
    last_run = _read_lint_state(cwd)
    _write_lint_state(cwd, warnings)
    if baseline_kind is None:
        # No committed copy and no snapshot: a report with no baseline is not
        # a comparison, so it is one plain line — never everything-as-new,
        # which printed the whole standing set after every tool call.
        if warnings:
            sections.append(
                "[Throughliner] QUEUE.md structure lint (advisory): "
                f"{len(warnings)} flag(s) in the file, and no previous "
                "version to compare against (no committed copy, no snapshot) "
                "— so new-vs-standing cannot be told apart. Run the lint "
                "script directly for the full listing."
            )
        new, pre_existing = [], list(warnings)
    else:
        new, pre_existing = _split_warnings(warnings, baseline_content)
    if new:
        baseline_name = ("the last commit" if baseline_kind == "commit"
                         else "the previous version")
        body = "\n".join(f"- {w}" for w in new)
        if pre_existing:
            body += (
                f"\n\n{len(pre_existing)} further flag(s) were already present "
                f"in {baseline_name} and are not repeated here."
            )
        sections.append(
            "[Throughliner] QUEUE.md structure lint (advisory). "
            "These flag known violations only — novel structure is allowed "
            "and never flagged. Judge each one: fix what's genuinely wrong "
            "in a follow-up edit, leave what isn't.\n" + body
        )
    elif baseline_kind is not None:
        # An unchanged flag set says nothing, so it emits nothing, and silence
        # carries the meaning the constant line pretended to.
        #
        # The line it replaces reported a COUNT and no more, after every edit
        # and every unrelated shell command. Two failures came of that. It
        # trained the reader to skim — the cry-wolf shape this project has
        # repealed measures for twice — and because it never named a flag, a
        # standing set hid any NEW KIND joining it: one session watched the
        # count creep from 20 to 27 with the wording never changing once. A
        # pre-existing flag was invisible in exactly the way an absent one is.
        #
        # The NEW direction is computed against the commit (or the newest
        # pre-change snapshot where the queue is untracked) every time. The
        # GONE direction reads a second baseline: the bodies the previous lint
        # run found, kept in `.throughliner/queue-lint-last.json`. Against the
        # commit alone, a flag cleared this session stayed "gone" until the
        # close committed, and one notice printed after every tool call for a
        # whole planning session. A notice now prints only where the body was
        # present at the previous run and is absent now — once. No state file
        # means no gone notices this run. The full listing stays available by
        # running the lint script directly.
        for cleared in _cleared_warnings(warnings, baseline_content):
            if last_run is None or _warning_body(cleared) not in last_run:
                continue
            sections.append(
                "[Throughliner] QUEUE.md structure lint (advisory): a flag "
                "present in the previous version is gone from the working "
                f"tree — {cleared}"
            )

    if with_growth:
        growth = _growth_report(cwd, content)
        if growth:
            sections.append(
                "[Throughliner] Queue item word growth since the last commit, "
                "as bare facts — no threshold, no judgment, and none is "
                "implied.\n" + "\n".join(f"- {g}" for g in growth)
            )

    secrets = _scan_secrets(queue_path)
    if secrets:
        sections.append(_secret_message("QUEUE.md", secrets))

    if not sections:
        return 0
    return _emit("\n\n".join(sections))


def _secret_message(name: str, findings: list) -> str:
    return (
        f"[Throughliner] Possible secret in {name} (advisory). "
        "These match known credential shapes only — deterministic, no "
        "judgement. Tell the user plainly what was found and where, and let "
        "them decide.\n"
        + "\n".join(f"- {f}" for f in findings)
        + "\n\nSay plainly, if it comes up, that this check finds credential "
        "SHAPES and nothing else. It cannot tell whether ordinary prose here "
        "names a real person or a real case, which is the thing that actually "
        "leaks from these files — so never tell the user their docs are "
        "scrubbed or safe to publish on the strength of it."
    )


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError, ValueError):
        return 0

    if not isinstance(data, dict):
        return 0

    cwd = data.get("cwd", "")
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input") or {}

    if tool_name not in ("Edit", "Write", "MultiEdit", "Bash", "PowerShell"):
        return 0

    if not cwd:
        return 0

    is_adopted = os.path.isfile(os.path.join(cwd, "SPEC.md"))

    # A shell command names no file, so there is nothing to compare against
    # QUEUE.md — the lint simply runs over QUEUE.md whatever the command was.
    #
    # WHY THIS BRANCH EXISTS. The lint used to fire after Edit/Write/MultiEdit
    # only, so a write that reached QUEUE.md through a shell bypassed it
    # entirely. That is not hypothetical: a scripted write corrupted QUEUE.md
    # on 2026-08-09 — duplicating a header fragment and leaving six built work
    # items in place — and nothing surfaced it. It was found several steps
    # later by an unrelated `git status`, and a close would otherwise have
    # committed it. Firing here catches the damage whatever caused it, which is
    # the point: the companion fix in pre_tool_use.py stops one route in, and
    # this stops the class.
    #
    # The cost is one file read and one lint per shell command, and the lint
    # stays ADVISORY exactly as it is after an edit — it reports, never blocks.
    if tool_name in ("Bash", "PowerShell"):
        if not is_adopted:
            return 0
        return _lint_queue(os.path.join(cwd, "QUEUE.md"), with_growth=False)

    filepath = tool_input.get("file_path", "")
    if not filepath:
        return 0

    # Clear the editing-state signal for whatever file was just written —
    # every file, not only QUEUE.md, and before the QUEUE.md gate below.
    #
    # Gated on adoption to match pre_tool_use, which returns early with no
    # SPEC.md and so writes the OPENING marker only in adopted projects.
    # Without this the two hooks are asymmetric: an unadopted folder gets a
    # closing marker for a session that never opened one, so marker files
    # accumulate in projects that have nothing to do with this plugin — and
    # no .gitignore covers them, since /setup is what adds that entry and
    # those folders have never run it.
    if is_adopted:
        write_editing_marker(cwd, data.get("session_id", ""), filepath, False)

    if not is_adopted:
        return 0

    # Only the project-root QUEUE.md gets the structure lint. SPEC.md and LOG/
    # entries get the secret scan alone — they have no structure to lint, but
    # they are committed prose exactly like the queue.
    if _normalise(filepath) == _normalise(os.path.join(cwd, "QUEUE.md")):
        return _lint_queue(filepath)

    if _is_scannable_doc(filepath, cwd):
        secrets = _scan_secrets(filepath)
        if secrets:
            return _emit(
                _secret_message(os.path.basename(filepath), secrets)
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
