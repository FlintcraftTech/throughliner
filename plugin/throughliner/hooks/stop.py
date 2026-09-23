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
directly, so no transcript parsing is needed. One check reads the transcript's
tail on purpose ([process-now-offer-fixed-and-enforced]): the process-now offer
is ordinarily made a turn before the filing it governs, and only the transcript
shows that turn. Returning
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

# A time word whose own sentence carries its source passes
# ([time-word-check-blocks-planning-openings]): a date in YYYY-MM-DD form, or
# one of the phrases the always-loaded rule names as a reading. The sentence
# is the text between full stops around the word — a source three paragraphs
# away is what a reader cannot check, so it does not count. A COPY sits in
# pre_tool_use.py; change one, change both.
TIME_SOURCE_PATTERN = re.compile(
    r"\d{4}-\d{2}-\d{2}"
    r"|read from the clock|by the session clock|per the [^.\n]*?record"
    r"|the opening'?s clock line|the register",
    re.IGNORECASE,
)


# What may stand between a sentence's start and its first word: whitespace,
# quotation marks, opening brackets and markdown leaders. A COPY of
# pre_tool_use.py's; change one, change both.
_TIME_SENTENCE_LEAD = re.compile(r"^[\s\"'“‘(\[{#*>-]*$")


def _is_name_mid_sentence(text, start, word):
    """True where the matched time word opens with a capital and is not the
    first word of its sentence — a product's own page or feature written as a
    name ([time-word-check-hits-product-nouns]). A capital at a sentence's
    start says nothing, so that case still counts as a time word."""
    if not word[:1].isupper():
        return False
    left, _ = _sentence_span(text, start, start)
    return not _TIME_SENTENCE_LEAD.match(text[left:start])


# A day word denotes a date computable from the clock
# ([time-word-check-passes-denoted-date]): where that date appears anywhere
# in the reply — before or after the word, in brackets or not — the word is
# sourced and passes. Words with no computable date keep the sentence-source
# rule. A COPY of pre_tool_use.py's; change one, change both.
_DENOTED_OFFSETS = {
    "yesterday": -1, "today": 0, "tonight": 0, "this morning": 0,
    "this afternoon": 0, "this evening": 0, "earlier today": 0, "tomorrow": 1,
}
# A sentence carrying this many distinct phrases from the check's own list is
# read as a list of the words — mentioned, not used — and is not refused. A
# tunable heuristic derived from the one instance (a planning chat quoting the
# list), stated here as such.
_MENTIONED_LIST_MIN = 3


def _clock_today():
    """Today as YYYY-MM-DD; the suites pin it with THROUGHLINER_TEST_CLOCK."""
    import datetime as _dt
    pinned = os.environ.get("THROUGHLINER_TEST_CLOCK", "")
    if pinned:
        return pinned.partition(" ")[0]
    return _dt.date.today().isoformat()


def _denoted_date(phrase):
    offset = _DENOTED_OFFSETS.get(phrase)
    if offset is None:
        return None
    import datetime as _dt
    try:
        day = _dt.date.fromisoformat(_clock_today())
    except ValueError:
        return None
    return (day + _dt.timedelta(days=offset)).isoformat()


def _unfounded_time_phrases(message):
    """(phrase, sentence) pairs for each distinct time phrase in the reply
    outside quoted text, lowercased — leaving out any whose sentence also
    carries a source, any written as a name with a capital mid-sentence, any
    whose denoted date the reply names anywhere, and any in a sentence that
    lists three or more of the check's own phrases."""
    found = []
    text = _strip_quoted(message, spans=True)
    for match in TIME_WORD_PATTERN.finditer(text):
        if _is_name_mid_sentence(text, match.start(), match.group(0)):
            continue
        left, right = _sentence_span(text, match.start(), match.end())
        if TIME_SOURCE_PATTERN.search(text, left, right):
            continue
        sentence = text[left:right]
        distinct = {" ".join(m.group(0).lower().split())
                    for m in TIME_WORD_PATTERN.finditer(sentence)}
        if len(distinct) >= _MENTIONED_LIST_MIN:
            continue
        phrase = " ".join(match.group(0).lower().split())
        denoted = _denoted_date(phrase)
        if denoted and denoted in message:
            continue
        if phrase not in [p for p, _ in found]:
            found.append((phrase, " ".join(sentence.split())))
    return found


def _unfounded_time_words(message):
    """The phrases alone, for callers that key on them."""
    return [phrase for phrase, _ in _unfounded_time_phrases(message)]


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


def _slugs_in_section(queue_path, section):
    """The slugs under one `## <section>` heading of QUEUE.md — a sibling of
    `_slugs_in_queue` that keeps the section. Empty where the file is
    unreadable or the section absent."""
    try:
        with open(queue_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    except (OSError, UnicodeDecodeError):
        return set()
    slugs = set()
    inside = False
    for raw in lines:
        stripped = raw.strip()
        if stripped.startswith("## "):
            inside = stripped[3:].strip() == section
            continue
        if inside and stripped.startswith("#### "):
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


# --- Turn length, and bold mid-sentence ([turn-length-check-in-stop-hook]) ---
#
# Every written shape is bounded against a measured median, and nothing
# bounded a chat turn — the one text the user reads every turn. The bound is
# 175 prose words: the 90th percentile of Claude's replies of fifteen words or
# more across this project's three latest planning transcripts on 2026-09-23
# (171 turns; median 66, 75th percentile 115, 90th 173, longest 288), rounded.
# A median would send back half of all turns. Re-derived by
# method/measure_chat_turns.py in the development project; a tunable
# constant, revisable once seen. Prose means lines outside fenced blocks that
# do not open with a list marker, a numbered-list marker, `>` or `#` — the
# same exemption for structured content that [BRIEF] carries. Each check
# blocks once per session, then passes.
#
# The second trigger, from [item-summary-content-line-and-list-shape]: a bold
# run that starts anywhere but at the head of a line or of a list item gives
# a reader no scan path; the register rule says bold leads the line and a
# list carries one item per line.
TURN_PROSE_BOUND = 175
_LIST_OR_STRUCTURE_LEAD = re.compile(r"^\s*(?:[-*+]\s|\d+[.)]\s|>|#)")
_LIST_HEAD = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)?")
_BOLD_RUN = re.compile(r"\*\*[^*\n]+?\*\*")


def _prose_lines(message):
    """The reply's prose lines: outside fenced blocks, not opening with a
    list marker, a numbered-list marker, `>` or `#`."""
    lines = []
    in_fence = False
    for line in message.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or _LIST_OR_STRUCTURE_LEAD.match(line):
            continue
        lines.append(line)
    return lines


def _prose_word_count(message):
    return sum(len(line.split()) for line in _prose_lines(message))


def _bold_runs_mid_line(message):
    """How many bold runs start anywhere but at the head of a line or of a
    list item, outside fenced blocks and blockquotes."""
    count = 0
    in_fence = False
    for line in message.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or stripped.startswith(">"):
            continue
        head = _LIST_HEAD.match(line).end()
        for match in _BOLD_RUN.finditer(line):
            if match.start() != head:
                count += 1
    return count


def _turn_length_owed(cwd, session_id, message):
    """The block reason where the reply's prose runs past the bound, else
    None. Once per session."""
    words = _prose_word_count(message)
    if words <= TURN_PROSE_BOUND:
        return None
    if _already_blocked(cwd, session_id, "turn-length"):
        return None
    return (
        "[Throughliner] This reply runs %d words of prose against a bound of "
        "%d. Lead with the decision; where more than two things are named, "
        "one item per line; reasoning on request, not front-loaded. Reply "
        "with a shorter correction of the same content, never a repeat. This "
        "is fed back once and passes on the next reply." % (
            words, TURN_PROSE_BOUND)
    )


def _bold_mid_line_owed(cwd, session_id, message):
    """The block reason where the reply carries bold runs mid-line, else
    None. Once per session."""
    count = _bold_runs_mid_line(message)
    if not count:
        return None
    if _already_blocked(cwd, session_id, "bold-mid-line"):
        return None
    return (
        "[Throughliner] This reply carries %d bold run%s inside a sentence. "
        "Bold leads the line or the list item, and a list carries one item "
        "per line — so where the bold marks separate things, write them one "
        "per line. Reply with the correction, never a repeat. This is fed "
        "back once and passes on the next reply." % (
            count, "" if count == 1 else "s")
    )


# --- The post-close tail offer ([post-close-tail-offer-enforced-once]) ---
#
# After this chat's /done, the always-loaded rule says to offer once to append
# later work to the session's record as a marked tail, at the end of a piece
# of work where a file changed. It failed repeatedly in practice. /done leaves
# `.throughliner/session-closed-<session-id>` carrying the record's filename;
# where a project file outside LOG/ was written after it (read from the safety
# check's decision log), a finished reply that carries neither the offer nor a
# tail is fed back once. The check sees only a reply after a write, so a change
# never reported in a reply is not reached, and it composes no tail.
SESSION_CLOSED_PREFIX = "session-closed-"
TAIL_MENTION = re.compile(r"\btail\b", re.IGNORECASE)
WRITE_TOOLS = ("Edit", "Write", "MultiEdit")


def _safe_id(session_id):
    return re.sub(r"[^A-Za-z0-9._-]", "_", session_id or "unknown")


def _session_closed_marker(cwd, session_id):
    """The closed marker's path for this session, or None."""
    safe = _safe_id(session_id)
    if safe == "unknown":
        return None
    path = os.path.join(cwd, ".throughliner", SESSION_CLOSED_PREFIX + safe)
    return path if os.path.isfile(path) else None


def _project_write_since(cwd, session_id, since):
    """True where the decision log shows an allowed edit-tool write by this
    session, to a project file outside LOG/, stamped after `since`."""
    safe = _safe_id(session_id)
    path = os.path.join(cwd, ".throughliner", "pre-tool-use.log")
    root = os.path.normcase(os.path.abspath(cwd)).replace("\\", "/")
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                cols = line.rstrip("\r\n").split("\t")
                if len(cols) < 6 or cols[5] != safe:
                    continue
                if cols[1] not in WRITE_TOOLS or cols[2] != "allow":
                    continue
                if cols[0] <= since:
                    continue
                target = cols[4]
                if os.path.isabs(target):
                    norm = os.path.normcase(target).replace("\\", "/")
                    if not norm.startswith(root + "/"):
                        continue
                    rel = norm[len(root) + 1:]
                else:
                    rel = os.path.normcase(target).replace("\\", "/")
                if rel.startswith("log/") or "/log/" in "/" + rel:
                    continue
                return True
    except OSError:
        return False
    return False


def _post_close_tail_owed(cwd, session_id, message):
    """The feedback reason where the tail offer is owed and absent, else ""."""
    marker = _session_closed_marker(cwd, session_id)
    if marker is None or TAIL_MENTION.search(message):
        return ""
    try:
        import datetime
        since = datetime.datetime.fromtimestamp(
            os.path.getmtime(marker)).strftime("%Y-%m-%d %H:%M:%S")
    except OSError:
        return ""
    if not _project_write_since(cwd, session_id, since):
        return ""
    if _already_blocked(cwd, session_id, "post-close-tail"):
        return ""
    return (
        "This chat has already closed — its record is written and committed "
        "— and a project file changed since. The offer to append that work "
        "to this session's record as a marked tail is owed once: name both "
        "routes, a yes here or running the done command again, which appends "
        "the same tail. This is fed back once and passes on the next reply."
    )


# --- The process-now offer ([process-now-offer-fixed-and-enforced]) ---
#
# In a planning chat — no build working file — a reply reporting a capture
# filed must have made the fixed offer, "Process this with you now, or file it
# for later? I'd take it now.", in this reply or one of the two assistant
# replies before it. The rule was present in plan.md and not reached for, so
# this is a mechanism. The limits, stated: it reaches a filing reported in a
# recognisable line, so one reported in other words passes; it cannot tell a
# recommendation to file from one to process now, so the direction stays
# wording; and a "file it" answered more than two assistant turns after the
# offer is a false block, bounded to one wasted turn by the once-per-session
# gate. A reply whose every claimed slug sits in Processed owes no offer
# ([process-now-offer-skips-processed-slugs]): an entry the user already
# agreed to is written without a filing question, and its place in Processed
# is what says so; a slug in Unprocessed, or in neither section, keeps the
# check. The limit: a reply naming no slug and reporting the filing in other
# words is still not reached.
PROCESS_NOW_FORMULA = "process this with you now"
FILED_LINE = re.compile(r"Filed at the bottom of Unprocessed", re.IGNORECASE)


def _build_working_file_present(cwd, session_id):
    safe = _safe_id(session_id)
    return safe != "unknown" and os.path.isfile(
        os.path.join(cwd, "_build-%s.md" % safe))


def _recent_assistant_texts(transcript_path, count):
    """The text of the last `count` assistant entries in the transcript,
    oldest first. Empty where the path is missing or unreadable."""
    if not transcript_path:
        return []
    texts = []
    try:
        with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    entry = json.loads(raw)
                except ValueError:
                    continue
                if entry.get("type") != "assistant":
                    continue
                content = (entry.get("message") or {}).get("content")
                if isinstance(content, str):
                    texts.append(content)
                elif isinstance(content, list):
                    texts.append("\n".join(
                        block.get("text", "") for block in content
                        if isinstance(block, dict) and block.get("type") == "text"))
    except OSError:
        return []
    return texts[-count:]


def _process_now_offer_owed(cwd, session_id, message, transcript_path):
    """The block reason where a planning chat's reply reports a filing with
    no process-now offer in reach, else None."""
    if _build_working_file_present(cwd, session_id):
        return None
    claimed = _claimed_slugs(message)
    if not (claimed or FILED_LINE.search(message)):
        return None
    if claimed:
        processed = _slugs_in_section(os.path.join(cwd, "QUEUE.md"),
                                      "Processed")
        if all(slug in processed for slug in claimed):
            return None
    in_reach = [message] + _recent_assistant_texts(transcript_path, 3)
    if any(PROCESS_NOW_FORMULA in text.lower() for text in in_reach):
        return None
    if _already_blocked(cwd, session_id, "process-now-offer"):
        return None
    return (
        "Your last message reports a capture filed, and neither it nor the "
        "two replies before it made the offer that comes before a filing in "
        "a planning chat: \"Process this with you now, or file it for later? "
        "I'd take it now.\" Make the offer in those words — the report of "
        "what landed, then the offer — and let the user answer. Saying the "
        "same phrase passes on the next reply; this is stopped once."
    )


# --- The checkpoint carries no clock and no stop offer
# ([checkpoint-narrates-clock-and-offers-to-stop]) ---
#
# A planning checkpoint carries the finished entry's outcome, a pointer to the
# next item, one bold question and the two counts — nothing else. Sessions
# were reading the clock into it and offering to end the session, neither of
# which anything asks for. The phrase lists match phrases only, so a rephrased
# narration or offer passes.
CHECKPOINT_MARKS = re.compile(r"Take this one next\?|left to process",
                              re.IGNORECASE)
CLOCK_NARRATION = re.compile(
    r"the clock reads|the session opened at|\bopened at \d{1,2}:\d{2}",
    re.IGNORECASE)
STOP_OFFER = re.compile(
    r"stop here|carry on, or stop|end the session|end here", re.IGNORECASE)


def _checkpoint_clock_or_stop_owed(cwd, session_id, message):
    """The block reason where a checkpoint reply narrates the clock or offers
    to stop, else None."""
    if _build_working_file_present(cwd, session_id):
        return None
    text = _strip_quoted(message, spans=True)
    if not CHECKPOINT_MARKS.search(text):
        return None
    if not (CLOCK_NARRATION.search(text) or STOP_OFFER.search(text)):
        return None
    if _already_blocked(cwd, session_id, "checkpoint-clock-or-stop"):
        return None
    return (
        "Your last message is a checkpoint, and it carries a clock reading "
        "or an offer to stop. A checkpoint carries four things: the outcome "
        "of the finished entry, the pointer to the next item, one bold "
        "question inviting the user into it, and the two counts — cleared "
        "to run, and left to process. Reply with the checkpoint again "
        "without the time and without the offer; this is stopped once."
    )


def _finish_with_shape_checks(cwd, session_id, message):
    """The last two checks on a reply every other check has passed: its
    prose length, then bold mid-line. They sit last so a reply that owes a
    correction of substance — a filing that never happened, a missing offer
    — is sent back for that and not for its shape. Always exits."""
    owed = _turn_length_owed(cwd, session_id, message) or \
        _bold_mid_line_owed(cwd, session_id, message)
    if owed:
        print(json.dumps({"decision": "block", "reason": owed}))
    sys.exit(0)


def project_root(data: dict) -> str:
    """The project root every path test runs against.

    The hook payload's `cwd` follows Claude: after a shell `cd` into a nested
    project's inner repository it is the inner folder, and every path test
    then refuses the outer's own files ([scope-lock-root-follows-shell-cwd]).
    `CLAUDE_PROJECT_DIR` is the folder the session started in, exported into
    every hook's environment, so it is the root where it is set and holds
    SPEC.md. The one exception: a `cwd` inside a `.claude/worktrees/` folder
    is kept, since a linked-worktree session's started-in folder is the main
    checkout and would be the wrong root there.

    Copied into each hook rather than shared — the hooks run standalone from
    a copied plugin cache and cannot import a module. Change one, change all.
    """
    cwd = data.get("cwd", "") or ""
    env_root = os.environ.get("CLAUDE_PROJECT_DIR", "") or ""
    if not env_root or not os.path.isfile(os.path.join(env_root, "SPEC.md")):
        return cwd
    norm_cwd = os.path.normcase(os.path.normpath(cwd)).replace("\\", "/")
    if "/.claude/worktrees/" in norm_cwd + "/":
        return cwd
    return env_root


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    message = payload.get("last_assistant_message") or ""
    if not message:
        sys.exit(0)

    cwd = project_root(payload) or os.getcwd()
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
        (p, s) for p, s in _unfounded_time_phrases(message)
        if not _already_blocked(cwd, session_id, "time-" + p.replace(" ", "-"))
    ]
    if fresh:
        listed = "; ".join('"%s" in: %s' % (p, s) for p, s in fresh)
        print(json.dumps({
            "decision": "block",
            "reason": (
                "Your last message says when something happened with no "
                f"source: {listed}. Keep the word and put the date it means "
                "beside it in the same sentence — \"since yesterday "
                "(2026-09-20)\" — read from the clock or the record; drop the "
                "word only where no date exists. Reply with the correction "
                "alone: one or two lines carrying the corrected sentence, "
                "with nothing from the earlier message repeated, since that "
                "message stays on screen, and no account of what the clock "
                "reads. A name written with a capital mid-sentence — a "
                "product's own page or feature — passes, so a block on one "
                "is a false positive to reword or ignore. This phrase is "
                "stopped once; it passes on the next reply."
            ),
        }))
        sys.exit(0)

    owed = _post_close_tail_owed(cwd, session_id, message)
    if owed:
        print(json.dumps({"decision": "block", "reason": owed}))
        sys.exit(0)

    owed = _checkpoint_clock_or_stop_owed(cwd, session_id, message)
    if owed:
        print(json.dumps({"decision": "block", "reason": owed}))
        sys.exit(0)

    claimed = _claimed_slugs(message)
    if not claimed:
        # The overwhelming majority of turns. No work done — unless the reply
        # carries the capture tool's own filed line, which the offer check
        # below still reads.
        owed = _process_now_offer_owed(cwd, session_id, message,
                                       payload.get("transcript_path") or "")
        if owed:
            print(json.dumps({"decision": "block", "reason": owed}))
            sys.exit(0)
        _finish_with_shape_checks(cwd, session_id, message)

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
        # The filing is real. In a planning chat it still owes the offer.
        owed = _process_now_offer_owed(cwd, session_id, message,
                                       payload.get("transcript_path") or "")
        if owed:
            print(json.dumps({"decision": "block", "reason": owed}))
            sys.exit(0)
        _finish_with_shape_checks(cwd, session_id, message)

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
        "may already be acting on the report. Reply with the correction "
        "alone: one or two lines saying the earlier report was wrong and "
        "what is filed now, with nothing from the earlier message repeated, "
        "since that message stays on screen. If the item genuinely lives "
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
