#!/usr/bin/env python3
"""Stop hook: catch a report that names a work item which isn't there.

The failure this exists for ([write-first-report-without-write]). Under the old
show-first rule the text appeared in chat before the write, so reporting and
showing were one act and a report could not precede its write. Under write-first
the report follows the write — which means a turn that never executes the write
can still emit the report, and the two are indistinguishable to the user. The
live instance: Claude said "Filed as [some-slug]" having made no write at all,
and the user acted on the false report before the item existed.

Sharper wording is a remedy already spent. The write-then-verify-then-point rule
is shipped, always-loaded and correctly worded, and it still failed live. So this
is a mechanism instead.

WHY THIS IS CHECKABLE AT ALL, and why no understanding of meaning is required.
The shipped rule already requires the report to name what landed and where, which
in practice is a fixed shape: "filed as [slug]", "moved to Processed as [slug]".
A slug either exists in QUEUE.md as a `#### ` heading or it does not. So a false
report is not a judgment about meaning — it is a named artifact that is absent.
This is the check-the-world rule the method already applies to `[user]` items,
turned on Claude's own claims.

WHY `Stop` AND NOT `PreToolUse`. `workshop/resources/research/hook-enforced-doc-reading.md`
establishes that PreToolUse can read the transcript and deny. That is the wrong
surface here: a false report is text with NO tool call attached, so a hook gated
on tool calls never fires on it. `Stop` fires when Claude finishes responding and
receives `last_assistant_message` — the complete final response text, handed over
directly, so no transcript parsing is needed. Returning
`{"decision": "block", "reason": "..."}` does not end the turn: it feeds the
reason back and the conversation continues, so the write can be made and the
correction can reach the user before they act on the false report.

THE LIMIT, STATED RATHER THAN DISCOVERED. This catches reports that NAME the
artifact. A vague report ("I've written that up") escapes it entirely. That is
acceptable rather than a hole: the shipped rule already requires the report to
name what landed, so the hook enforces the rule as written and no more.

LOOP PROTECTION. A `stop_hook_active`-style flag is not documented, so this
carries its own: it blocks once per identical claim and then downgrades to
non-blocking feedback. A persistent mismatch would otherwise bounce forever.
"""

import json
import os
import re
import sys

# Report-shaped claims that NAME a slug. Deliberately narrow — each requires a
# reporting verb near a bracketed slug, so ordinary prose mentioning an item
# ("as [some-slug] says") does not match.
CLAIM_PATTERNS = [
    # Queue-FILING verbs only. "logged", "recorded" and "wrote" are deliberately
    # absent: /done legitimately says it logged a slug that it then removed from
    # the queue, and a LOG entry is not a QUEUE heading — this check is
    # QUEUE-specific, so those verbs would fire on correct reports.
    re.compile(
        r"\b(filed|captured|appended|created)\b"
        r"[^.\n]{0,80}?\[([a-z0-9][a-z0-9-]*)\]",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(moved|promoted|kept|processed|lifted)\b"
        r"[^.\n]{0,80}?\[([a-z0-9][a-z0-9-]*)\]",
        re.IGNORECASE,
    ),
    re.compile(
        r"\[([a-z0-9][a-z0-9-]*)\][^.\n]{0,40}?\b"
        r"(is now in|has been filed|has been added|landed in)\b",
        re.IGNORECASE,
    ),
]

# A placeholder slug from a specimen, not a real one. The boundary is derived
# rather than invented: it is the shipped docs' own specimen vocabulary —
# [slug-a], [some-slug], [work-slug], [old-slug] — while no real slug in this
# project's history contains the word "slug", because a real slug names its
# work. Discussing specimens is ordinary planning work, and the check was
# firing on it.
#
# The residual, stated: an item deliberately named `something-slug` slips the
# check. That is now also a reason not to name one that way.
PLACEHOLDER_SLUG = re.compile(r"(^|-)slug($|-)", re.IGNORECASE)

# Words that mean the sentence is talking ABOUT a slug rather than claiming it
# was just written. Cheap false-positive suppression.
#
# Scoped to the claim's OWN sentence, and that scope is the whole guard. A
# fixed character window reaches backwards past the full stop into whatever
# preceded it, and `next-build.md` REQUIRES a capture report to say why the
# thing was captured rather than done now — so the mandated wording ("I
# captured this rather than folding it in. Filed as [slug].") puts this
# pattern's own trigger words in the previous sentence, and three real filing
# claims went undetected because of it. A past-tense claim standing as its own
# sentence is a claim whatever precedes it; a genuine hedge ("I would file
# [slug]", "I'll file [slug] once the build lands") shares the claim's
# sentence and is still suppressed.
NEGATION_NEAR = re.compile(
    r"\b(will|would|should|could|about to|going to|plan to|propose|"
    r"recommend|suggest|if |once |before |instead of|rather than|not )\b",
    re.IGNORECASE,
)


# A sentence ends at ./!/? followed by whitespace or the end of the text, or at
# a line break. Deliberately crude: the cost of splitting one sentence in two is
# a hedge that stops suppressing, which fails toward blocking and is visible;
# the cost of not splitting is a hedge that suppresses a real claim, which is
# silent. Bullet and heading markers count as breaks because they are newlines.
SENTENCE_BREAK = re.compile(r"(?:[.!?](?=\s|$))|\n")


def _sentence_span(message, start, end):
    """The bounds of the sentence containing message[start:end]."""
    left = 0
    for match in SENTENCE_BREAK.finditer(message, 0, start):
        left = match.end()
    right = len(message)
    match = SENTENCE_BREAK.search(message, end)
    if match:
        right = match.end()
    return left, right


def _strip_quoted(message, spans=False):
    """The message with blockquoted lines and fenced code blocks blanked.

    A capture report is never inside a blockquote or a code fence; a quoted
    draft, a specimen or a pasted post always is. Lines are replaced with
    empty strings rather than removed, so nothing else shifts. With `spans`
    set, inline code and quotation-marked spans are blanked too — the time-word
    scan uses that form, since a quoted phrase is someone else's words.
    """
    out = []
    in_fence = False
    for line in message.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append("\n" if line.endswith("\n") else "")
            continue
        if in_fence or stripped.startswith(">"):
            out.append("\n" if line.endswith("\n") else "")
            continue
        out.append(_QUOTED_SPAN.sub(" ", line) if spans else line)
    return "".join(out)


# --- Relative time words with no source ([unfounded-time-words-stopped-once]) ---
#
# A COPY of pre_tool_use.py's TIME_WORD_PATTERN and _QUOTED_SPAN: the hooks run
# standalone from a copied plugin cache and cannot import a shared module.
# Change one, change both. pre_tool_use.py scans text written into a record,
# the queue or SPEC; this scans the finished reply. Each distinct phrase blocks
# once per session, then passes, through the same marker mechanism as the
# filing-claim check. The limit, stated: a bare wrong clock time or a wrong
# date is not a phrase and is not reached.
TIME_WORD_PATTERN = re.compile(
    r"\b(?:"
    r"(?:\d+|a|an|one|two|three|four|five|few|a few|couple of|several)"
    r"\s+(?:minutes?|hours?|days?|weeks?|months?)\s+ago"
    r"|just now|moments ago|earlier today|this morning|this afternoon"
    r"|this evening|tonight|yesterday|today|tomorrow|last week|next week"
    r"|last night"
    r")\b",
    re.IGNORECASE,
)
_QUOTED_SPAN = re.compile(r"`[^`\n]*`|\"[^\"\n]*\"|“[^”\n]*”")


def _unfounded_time_words(message):
    """Distinct time phrases in the reply outside quoted text, lowercased."""
    found = []
    for match in TIME_WORD_PATTERN.finditer(_strip_quoted(message, spans=True)):
        phrase = " ".join(match.group(0).lower().split())
        if phrase not in found:
            found.append(phrase)
    return found


def _claimed_slugs(message):
    """Slugs the message claims to have just written. Possibly empty."""
    found = set()
    message = _strip_quoted(message)
    for pattern in CLAIM_PATTERNS:
        for match in pattern.finditer(message):
            groups = [g for g in match.groups() if g]
            # The slug is whichever group looks like a slug, not the verb.
            slug = None
            for group in groups:
                if re.fullmatch(r"[a-z0-9][a-z0-9-]*", group) and "-" in group:
                    slug = group
            if not slug:
                continue
            if PLACEHOLDER_SLUG.search(slug):
                continue
            # Look at the claim's OWN sentence for hedging language — not a
            # fixed window, which reached back into the preceding sentence.
            left, right = _sentence_span(message, match.start(), match.end())
            window = message[left:right]
            if NEGATION_NEAR.search(window):
                continue
            found.add(slug)
    return found


def _slugs_in_queue(queue_path):
    """Every slug present in QUEUE.md as a real `#### ` heading."""
    try:
        with open(queue_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    except (OSError, UnicodeDecodeError):
        return None
    slugs = set()
    for raw in lines:
        stripped = raw.strip()
        if not stripped.startswith("#### "):
            continue
        match = re.search(r"\[([a-z0-9][a-z0-9-]*)\]\s*$", stripped)
        if match:
            slugs.add(match.group(1))
    return slugs


def _slugs_with_a_log_entry(cwd):
    """Every slug that names recorded work, read off LOG/ filenames.

    A session record is named `<date>-<slug>.md`, so a slug with an entry names
    work that shipped rather than a filing that failed. Once an item is built it
    leaves QUEUE.md, so from the queue alone a citation of finished work and a
    report of a write that never happened look identical — which is the whole
    defect: five recorded instances, every one a session correctly citing its own
    completed work and being blocked for it.

    Returns an empty set where `LOG/` is absent or unreadable, so a project
    without one behaves exactly as before.
    """
    log_dir = os.path.join(cwd, "LOG")
    found = set()
    try:
        names = os.listdir(log_dir)
    except OSError:
        return found
    for name in names:
        if not name.endswith(".md"):
            continue
        # The date prefix is stripped rather than matched around. A slug
        # contains dashes, so a plain "text after the last dash" read of
        # `2026-08-21-already-shipped.md` yields `08-21-already-shipped` — the
        # leftmost match wins and the date is swallowed into the slug.
        match = re.match(
            r"^(?:\d{4}-\d{2}-\d{2}-)?([a-z0-9][a-z0-9-]*)\.md$", name
        )
        if match:
            found.add(match.group(1))
    return found


def _slugs_ticked_in_working_file(cwd, session_id):
    """Slugs ticked in THIS session's build working file.

    Between an item's tick and /done it is in neither the queue (the run
    removed it at the tick) nor LOG/ (/done writes the entry), so a
    citation of work built minutes earlier in the same run still drew a block
    — a guard false-firing at the moment of highest confidence. A tick line
    reads `- [x] <description>` under Progress, and the run's items carry
    their slugs in the `Run:` line and per-entry lines, so any bracketed slug
    on a ticked line or in the file at all is read as this run's own work.

    Deliberately broad: over-suppressing here only quiets the guard about
    slugs this session's own working file names, which are this session's own
    work by construction. A missing or unparseable working file returns an
    empty set, so a session without one behaves exactly as before.
    """
    if not session_id:
        return set()
    safe_id = re.sub(r"[^A-Za-z0-9._-]", "_", session_id)
    path = os.path.join(cwd, "_build-%s.md" % safe_id)
    found = set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError):
        return found
    for match in re.finditer(r"\[([a-z0-9][a-z0-9-]*)\]", text):
        slug = match.group(1)
        if "-" in slug:
            found.add(slug)
    return found


def _already_blocked(cwd, session_id, slug):
    """True if this exact claim was blocked once already this session.

    The downgrade after one block is the loop protection. Marker files live in
    `.throughliner/`, which the project already gitignores. Never raises: if the
    marker cannot be written, the caller treats the claim as un-blocked, which
    fails toward blocking once rather than never.
    """
    if not session_id:
        return False
    safe_slug = re.sub(r"[^a-z0-9-]", "", slug)[:60]
    marker_dir = os.path.join(cwd, ".throughliner")
    marker = os.path.join(
        marker_dir, "stop-claim-%s-%s.marker" % (session_id[:40], safe_slug)
    )
    try:
        if os.path.exists(marker):
            return True
        os.makedirs(marker_dir, exist_ok=True)
        with open(marker, "w", encoding="utf-8") as f:
            f.write("blocked once\n")
    except OSError:
        return False
    return False


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    message = payload.get("last_assistant_message") or ""
    if not message:
        sys.exit(0)

    cwd = payload.get("cwd") or os.getcwd()
    session_id = payload.get("session_id") or ""
    queue_path = os.path.join(cwd, "QUEUE.md")

    # No QUEUE.md means this isn't a set-up project, or the file is unreadable.
    # Either way there is nothing to check against, and a hook that cannot tell
    # must not block.
    queue_slugs = _slugs_in_queue(queue_path)
    if queue_slugs is None:
        sys.exit(0)

    # Second claim class: a relative time word with no source. Blocks once per
    # distinct phrase per session; a phrase already blocked passes silently,
    # since the reply is then expected to carry its source in the sentence.
    fresh = [
        p for p in _unfounded_time_words(message)
        if not _already_blocked(cwd, session_id, "time-" + p.replace(" ", "-"))
    ]
    if fresh:
        listed = ", ".join('"%s"' % p for p in fresh)
        print(json.dumps({
            "decision": "block",
            "reason": (
                "Your last message says when something happened with no "
                f"source: {listed}. Read the clock or the record and put the "
                "source in the sentence, or drop the word — a wrong time in "
                "chat proliferates into the records. This phrase is stopped "
                "once; it passes on the next reply."
            ),
        }))
        sys.exit(0)

    claimed = _claimed_slugs(message)
    if not claimed:
        # The overwhelming majority of turns. No work done.
        sys.exit(0)

    # A slug absent from the queue but present in LOG/ names recorded work, so
    # the message is citing something that shipped rather than reporting a
    # filing that failed. Suppressing on the record rather than on the sentence
    # is deliberate: the item's own finding is that a citation and a
    # filing-claim are identical at the level this detector reads, so parsing
    # the sentence to tell them apart cannot work.
    recorded = _slugs_with_a_log_entry(cwd)
    # ...and a slug named in this session's own build working file is work this
    # run built (or is building): between its tick and /done it is in
    # neither the queue nor LOG/, so without this the guard fired on a run
    # correctly citing its own finished work.
    ticked = _slugs_ticked_in_working_file(cwd, session_id)
    missing = sorted(
        slug for slug in claimed
        if slug not in queue_slugs and slug not in recorded
        and slug not in ticked
    )
    if not missing:
        sys.exit(0)

    names = ", ".join("[%s]" % slug for slug in missing)
    downgraded = all(_already_blocked(cwd, session_id, slug) for slug in missing)

    # States what it observed and stops there. It used to end with "Make the
    # write now if it is missing" — an instruction to perform a write, from a
    # hook with no way to know whether the user approved one. A hook is frozen
    # text and the rules move: today write-first means the write was always
    # going to happen, but a message that instructs it would invert an approval
    # the moment any draft-then-approve shape returns anywhere in the method.
    # The stakes sentence stays, because it states what is at risk rather than
    # instructing anything, and it is what makes a session take the block
    # seriously.
    reason = (
        "Your last message reported writing %s, but %s not in QUEUE.md as a "
        "work-item heading. Either the write did not happen, or it landed "
        "somewhere else. Tell the user plainly what actually happened — they "
        "may already be acting on the report. If the item genuinely lives "
        "elsewhere (an archived message, another project's queue, a LOG "
        "entry), say so in one line and carry on."
        % (names, "it is" if len(missing) == 1 else "they are")
    )

    if downgraded:
        # Second time on the same claim: feed it back without blocking, so a
        # genuine mismatch cannot bounce the turn forever.
        print(reason, file=sys.stderr)
        sys.exit(0)

    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


if __name__ == "__main__":
    main()
