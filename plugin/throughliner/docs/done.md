---
name: done
docset: current
note: >
  /done procedure. Routes to a per-flavor close-out and states the
  shared close core once; the sub-docs carry the flavor-specific steps.
---

# /done procedure

/done is what lets the next session start from nothing and still know why —
the record it writes is where this session's reasoning survives. Close the
current session — record what happened, update docs, commit.

## Declare /done  [SILENT]

**First action of every /done run: write an empty file named
`.throughliner-close-active` into the session scratchpad directory, and delete it
as the last action before /done finishes.** While it exists the scope-lock
permits the few files the method's own close obligations name — `README.md`
today. Outside /done those paths are denied exactly as before, and a /done run
that dies before removing the marker leaves it in the scratchpad, which clears
itself.

## Route by session shape  [SILENT]

**First arm: this chat has already closed** [BRIEF]. Where this conversation
already holds its own /done run — the entry written and the commit made — a second
`/done` is the post-close tail, not a second /done run: file what it finds through
the three-way triage, append what happened to this session's existing entry as
a marked tail, and commit nothing. The one line carries which files were
appended to, that nothing was committed, and where the fresh-chat route leads:
open a fresh chat and run `/done` there, where /done's no-build close-out commits
handmade work as a session of its own.

Otherwise check for **this session's** build working file,
`_build-<session-id>.md` — not any other session's, which belongs to a build
running in another chat. **The check is automatic: route on what you find,
silently.**

**Run every judgment step the routed sub-doc calls for, whatever the user says
about committing.** "Just commit" asks for /done to be quick, not for its
checks to be dropped.

**Read the build working file in full before /done's close-out runs, whatever you
remember of the session.** Conversation memory enriches the LOG entry — the
tradeoffs, the colour the file doesn't capture — and the read still happens in
full alongside it.

```
the build working file EXISTS  ->  read it, then route by the run's work-item flavors:
    build items (no tag)  ->  done-build.md
                              # a build that changed SPEC.md closes here like
                              # any other build — same steps, same commit core
    [audit] items         ->  done-build.md, applying its audit delta
    mixed run             ->  each item closes through its OWN flavor's
                              close-out, one LOG entry per item, sharing the
                              single end-of-session commit

NO build working file          ->  done-plan.md, which carries all three
                                   no-build shapes and picks between them:
    a planning session
        (queue managed, captures processed, readiness line moved)
    a completed [user] item
    standalone handmade work — the FREEFORM /done run
        (no planning either, and the tree holds uncommitted edits the
         session didn't make)
```

**The freeform /done run is this third shape.** A freeform session is work done by
hand rather than by /next, so most never pass through /plan at all and there is
no queue item and no build working file. **Read the edits as the user's expected
work, and split them across separate log entries by judgment where they cover
several distinct changes.**

A no-build /done run touches QUEUE.md, SPEC.md and LOG/ and nothing else, whichever
of the three it is.

Detect a completed `[user]` item from what the session can already see. The
detection rules and /done itself are in done-plan.md, which handles a
completed item and a planning session together, since the two can coincide.

**Record each `[user]` item the session touched under an outcome, and read that
outcome off the session's own trail, never off what the item's presence in the
queue suggests.** The values, and the arm for an outcome none of them fits, are
next.md's walk-through outcomes provision — stated there once and cited here.
A `[co-write]` item is recorded on the same terms — done, deferred or not
reached — with the path of its one file in the record.

The sub-doc runs /done's close-out. When it reaches its Commit step, run the commit
core below, then return to the sub-doc for the recommendation.

**There is no test close-out** — the test flavor is retired. A check Claude can
run is part of building, closed by done-build.md. A check only the user can run is
a `[user]` work item, which never enters a build working file — so /done doesn't close it
*as a build*, but once the user has run it, /done records its completion and
removes it from the queue through done-plan.md.

## /done's checks report as one narration  [BRIEF]

Several checks fire across a /done run — verify completion, the staleness sweep, the
red-flag lifecycle, the wind-down re-scan. Combine what they turn up into one
"here's what came up: …" rather than letting each speak in turn.

**What the narration carries: every subject named outright, never a referring
expression only the scrollback resolves** — "the item above", "that fix", "the
same file" name nothing to a reader who is not holding the messages before
this one, and the user is deciding whether to let the commit happen on this
report alone.

**The wind-down re-scan's numbered set is its own message**, being something the
user must act on.

## Staleness sweep  [SILENT] when clean; [BRIEF] when flagging

The build and audit close-outs point here. Quick check of the remaining work items
— any staleness from any cause, not just what this session changed:

```
do any remaining items reference files since renamed or deleted?
do any reference behaviour or rules a shift since has moved past?
are any sitting long enough that surrounding code or rules have drifted away?
```

If so, flag it — and **split by fix path**:

```
a fate decision (drop / rewrite / keep)  ->  /plan's. Defer it.
a pure pointer drift                     ->  mechanical. Fix it HERE, report in
    (a file reference whose target             one line, riding this commit,
     content is unchanged)                     with no approval ask. At a build
                                               close the route is the queue
                                               tool's literal replace —
                                               reorder_queue.py --replace-in
                                               <slug> --old <literal> --new
                                               <literal> — which edits one
                                               entry, refuses a non-unique
                                               match, and passes the
                                               scope-lock.
```

## LOG entry files

Every sub-doc's entry-writing step points here.

**Run the scrub checklist before writing** (skill-nonspecific-rules.md, Scrub before
writing). A LOG entry gets committed, and a session that ran on someone's real
situation is where a name or a case detail arrives without anyone noticing. Fix
what you find at the same level of usefulness rather than dropping the fact.
Describe the entry afterwards as checked against that checklist and the
credential scan, and as nothing more.

**Read the entry and its index line for whether they carry their own weight**
(skill-nonspecific-rules.md, Authoring standard), subject to the length rules
below. It rides the scrub's read, since both look at the same text at the same
moment.

**How long an entry or an index line runs — one subject, four provisions.**

- an entry splits per unit of work, not by length: per item built in a build
  session, per item processed in a planning session;
- where one decision settles several items, one entry carries the reasoning and
  its siblings cite it rather than restating it — each still named for its own
  slug, so `<date>-<slug>.md` resolves for every one of them;
- an index line carries enough to decide open-or-skip;
- an index line that restates the entry it points at is wrong at any length;
- no figure decides any of it — the requirement in the behaviour rules' Index
  entries section is the whole bound.

**One text, several positions.** The session authors **two** texts, not four:

```
the one-liner  ->  the entry heading's summary
                   the index line's body
                   the commit title
the rationale  ->  the entry body
                   the commit body
```

The user approves both once, at the entry-writing step, and the commit step reuses
them verbatim — nothing new to read.

**Entry template** (placeholder hash — this /done run replaces it with the real
hash right after the commit, when the hash first exists):

````markdown
# [HASH] — [one-line summary]

[Prose rationale — re-authored from the work's rationale in the build working file (or, for a
planning session, what motivated these queue changes), expanded with what was
learned along the way. Inline prose, no `Why:` label. Re-authoring is where
reasoning gets re-attributed by accident (skill-nonspecific-rules.md, rationale
provenance).]

[per-flavor body fields]
````

```
per-flavor body fields — the only delta between flavors:

plan/setup  **Queue changes:**       work processed, reordered, or modified
                                     (for setup: the first rough build item and
                                     the docs scaffolded)
            **Work processed:**      kept / deleted, with slugs, or "none"

build and audit body fields live in done-build.md, beside the entry-writing
steps that use them.
```

**The forward-recommendation advisory — one field on every flavor, and five
provisions under it.**

- write the disposition into this /done run's entry, in one of two forms:

```
Advisory: filed — <slug>
Advisory: not needed — <why>
```

- write the label plain, matching the other /done obligations that produce a
  recorded line;
- complete /done only once the line is written;
- file the advisory itself as a capture at the top of Unprocessed, worded as
  advice, where the Recommend-next step made a *concrete* recommendation — a
  generic one files nothing, and the disposition line says which;
- **where this is a planning session's /done and its wind-down look-back filed one
  or more captures, the advisory names them by slug as what to open on**, in
  addition to any recommendation it carries — so the next planning session
  opens on them rather than meeting them in queue order; the disposition line
  above is unchanged;
- **where the reserved slot already holds a spent advisory, replace it**: delete
  the spent note and file this /done run's own in the freed slot, with the new note
  saying it replaced one. The reserved slug must be unique — filing alongside a
  spent note stops the queue mover dead;
- head the capture with the fixed, reserved slug, always that literal string:

```
#### Last session advises processing <slug> next [forward-advisory]
```

- state conditions in the prose beneath it, rather than counts.

```
write:      a /next run will halt on this item and build nothing past it
never:      it sits ninth, with eight items ahead of it
```

**The advisory is a transient orientation handoff, not work.** It is read and
cleared at the next /plan's opening (plan.md), so the only one this /done run clears
is one it is replacing. It is never processed and never reaches Processed,
living in QUEUE.md rather than in a file of its own.

**One more section, on every flavor: what the chat did outside its work items.**

```
**Also in this chat:**   corrections the user gave, decisions reached in
                         conversation, errors made and fixed, work done by hand
                         between runs — anything real that belongs to no work
                         item. Omit the section when there is nothing.
```

`/rescan` covers the same class on demand; this section covers it arriving at
/done, which always runs.

**Where the section goes depends on how many entries this /done run writes**, which
/done already knows:

```
close writes ONE entry      ->  `Also in this chat:` stays inline, unchanged.
                                Every planning session's /done is this case.
close writes SEVERAL        ->  the chat-level record becomes its OWN entry,
  entries                       named for the chat rather than for a slug, with
                                its own line in LOG/index.md.
```

**The frame, identical for every flavor.** Write the entry, then report in one
line what landed and where. A revert undoes a LOG entry, so it doesn't wait on
approval — the commit message does, because a commit is harder to unwind and
its message lands in no file.

```
run shipped ONE item     ->  the commit message derives from this entry: title
                             from the one-liner, body from the rationale. Show
                             that message at the commit step — short, and the
                             user has the entry to read behind it
run shipped SEVERAL      ->  the commit message is a one-line summary of the
                             whole run, shown and approved at the commit step;
                             each item's entry still stands on its own
```

This entry is the session's summary — **there is no separate chat recap.** Before
writing it, check whether this session raised and resolved a concern or weighed an
alternative that lost; if so, carry it with why it lost.

**Reuse the item's candidate.** A ticked build item always carries one, written
at its tick and so describing what the build actually did rather than predicting
it — reuse it. Planning sessions have no candidate; author fresh against the same
rule.

Prepend to `LOG/index.md` after the header, ending with the entry's filename:

```
- [HASH] — [index entry] → [entry filename]
```

**Month rollover, checked here because this is the step that touches the
index:** where `LOG/index.md` holds lines from a month that has ended, move
that month's lines into `LOG/index-YYYY-MM.md` (creating it if absent, newest
first like the main index), leaving the current month's lines where they are.
Retrieval searches `LOG/index*.md`, so nothing is lost to the move; the main
index stays the short file a planning opening reads from, back as far as the
most recent planning session's record.

**Each entry is its own file under `LOG/`, date-prefixed** so the folder sorts
newest-first on a name sort, each in its own file rather than a shared log:

```
session closing work items    ->  LOG/<YYYY-MM-DD>-<slug>.md
    (build, audit)                # one entry file per item, all sharing the date
session with no slug          ->  LOG/<YYYY-MM-DD>-<type>.md
    (planning, setup, handmade)   # e.g. 2026-06-09-plan.md
name already taken            ->  LOG/<YYYY-MM-DD>-<slug>-<kind>.md
                                  # -plan / -build
that name taken too           ->  append -2, -3, …
```

**A record about a queue item carries that item's full slug in its filename,
never shortened or reworded.** Where the bare name is taken, the record's kind
is what distinguishes it.

**Every date written at /done is the date /done runs** — today's date, at the moment
you are closing. That covers the filename prefix and every date written into the
words of a session record or a queue item alike ("processed 2026-08-12",
"cleared 2026-08-12"). It is not the commit date, and the filename prefix is not
a second copy of the hash; its only job is the name sort. **The record's own
date field carries date and time, read from the clock at the moment of
writing, never recalled** — a bare date leaves same-day relative-time claims
with no source finer than a day. The filename prefix stays date-only.

**Where a session ran across more than one calendar day, say so in one plain
sentence in its record, and change no filename or datestamp:**

> This session ran across 2026-08-11 and 2026-08-12.

**Write the hash into the entry heading and the index line only** — the commit
hash doesn't exist yet when the file is written, which is why the placeholder
pattern exists, and the filename carries the date instead. /done itself
fills the placeholder right after the commit (the commit step below says how).

**Write the literal placeholder token in hash position only**, where the
automatic backfill treats any match mechanically, so a prose mention is one
find-replace away from corrupting the entry. Describe the mechanism indirectly
where an entry needs to ("the placeholder", "the unfilled hash").

Pre-split entries live in `LOG/log.md` and `LOG/log-v*.md` — untouched, found by
hash or title search.

**Captures filed after the commit.** When a capture comes up in the post-commit
tail, the same move that appends it to QUEUE.md also updates this session's
just-written entry — edit its "Routed to Captures:" line to include it, as a
working-tree edit with no separate commit.

## Checks the closing session couldn't run

The deferred-tests section is retired — there is no separate test queue.

```
a verification only the user can run  ->  a [user] capture
a check Claude can run                ->  just part of building
```

So the only thing /done does with a check it couldn't run is the ordinary capture
move: if the closing session discovers a needed verification that isn't already a
`[user]` item, file it as a `[user]` capture appended to Unprocessed. Nothing
tracks it in a dedicated section, and **no LOG-only prose stands in for the queue
line** — an unrun check recorded only in a log entry never surfaces again.

## Triage any waiting mail  [SILENT] when the mailbox is empty; [BRIEF] when mail is triaged with nothing to send; [PROMPT] where a reply is drafted

Triage anything still sitting in this project's `INBOX/` as
`${CLAUDE_PLUGIN_ROOT}/docs/feedback-and-inbox.md` states — filing, not
processing: deciding what a message raises stays /plan's.

**Where a reply is owed, draft it here** and show the exact wording before
anything is sent. This is the moment that draft belongs to — a run is unattended
in practice, so mid-run is the wrong place for text that leaves the machine.

## Wind-down re-scan (file-only)  [BRIEF, PROMPT]

Commit core points here, so it runs at **every** /done close regardless of session
type. **This section is the canonical statement of the memory-limit machinery —
the limit sentence, the artifact cross-check, the asymmetry, the no-proxy rule
— and rescan.md applies it by reference at its own depth.**

**Look back only as far as the last /rescan in this chat.** /rescan is the same
step with its own trigger, and it can be run as often as the user likes; the
close picks up whatever came after the last one. Invoke it shortly before
closing and this costs a line. With no /rescan run, /done does the full job,
scanning the whole chat.

**Where nothing has happened since that rescan — no work, no decisions, only the
close being invoked — perform no second pass, and write one line into the record:
"covered by the rescan just run."** Conversation
between the rescan and /done is still scanned under the window rule above,
so this arm reaches only the case where the window is genuinely empty.

**Cycles due-ness check first** [SILENT] when no cycles doc exists; [BRIEF]
whenever one does. Run the cycles due-ness check as plan.md's Step 1 states it
("Cycles due-ness check"), filing only — routing stays planning work — with
one limb of this site's own: **read the project root for `CYCLES.md` here as
well**, because a doc created this session carries no opening line and would
otherwise be invisible to its own /done run.

Before committing, re-read that stretch of the chat and surface candidate
captures — things the user thought out loud but never flagged.

```
/done  ->  may FILE the surfaced captures
       ->  may AMEND an existing work item, on the user's direction given
           this session, recording the amendment in the LOG entry under
           that item's name
       ->  never ROUTES them (keep / delete)
# filing is capture-making, allowed in any session;
# amending is carrying out a direction the user has already given;
# routing is planning, /plan's alone
```

**Where the defect in a cleared item is one you noticed rather than one the
user directed, file it as a capture AND name the collision**: that item runs
before the next planning session unless the user directs the amendment now.
Saying so is what gives them the chance to; a capture alone leaves the item to
be built as it stands.

**Show the candidate set as ONE numbered message before anything is written**
[PROMPT], **opening by naming itself as /done's standing look-back over the
conversation** — in the user's words, before what it found — so the step reads
as the rule it is rather than as an improvised idea.
**End the message with what each answer does: "Say go to file them all, or
contest by number."** Numbering explains contesting on its own; "go" explains
nothing unless the sentence says it files the whole set. The writes then land,
and a contested item is dropped or reworked one at a time. The set
holds writes only — captures and record edits — and a candidate deletion is
presented after it as its own ask, under the session-file cleanup step's own
rules.

Add them to this session's LOG entry's "Routed to Captures:" line as a
working-tree edit riding this commit.

**Run the memory check first, and say one sentence — never two — reporting what
it found.** The check reads what the artifacts prove ran: a queue diff (`git
diff HEAD -- QUEUE.md`, or the snapshot folder where the queue is untracked)
showing entries deleted, moved or kept means a planning run; a build working
file's ticks mean a build run. It then looks for each such run's invocation and
opening lines in the conversation.

```
a run the files prove happened is    ->  "Earlier parts of our conversation have
  missing from the conversation          dropped out of view — the files show a
                                         <planning | build> run I can no longer
                                         see."
every run the files record is        ->  "Every run the files record is still in
  still in view                          view."
```

**The asymmetry is a rule for Claude, not a sentence for the user.** A run
missing from view is positive evidence that earlier material dropped out; a run
still in view proves only that stretch, and a discussion that touched no file
leaves nothing to check against. So the report says what the check found and
never adds that nothing was lost.

**Name no proxy.** Session length, duration and message count are observable
proxies for compaction rather than the thing itself, and each invites the user
to discount the result by a factor that is fictional.

One thing to state, not fix: a fresh-chat /done has none of the session's
thinking in view, so there is nothing to re-scan.

**The only other re-scan in the method is /rescan, coordinated with by the
look-back window above. /plan has none, and gains none.**

> "Re-read our discussion — nothing came up that isn't already captured."

## Session-file cleanup (throwaway artifacts)  [BRIEF, PROMPT]

Commit core points here, so it runs at every /done run. The build working file is
deleted by /done already; this generalises that lifecycle to *other* throwaway
files this session created.

Offer to delete only files meeting **all** of these:

```
Claude created or wrote them THIS session
    # established from the build working file Changes and this session's own edits.
    # A file Claude did not create this session is NEVER presumed rubbish —
    # uncommitted changes the session didn't make are the user's own work.
they have NO future use
    # not a deliverable, not a research finding, not evidence a later session
    # must re-read. Purely throwaway.
```

```
one at a time, user approves each  [PROMPT]  ->  never auto-delete
git-tracked file                             ->  recoverable from history;
                                                 say so plainly (low stakes)
untracked, or outside the repo               ->  NOT recoverable. Give a clear
                                                 warning before removing it.
```

If nothing session-created looks throwaway, say so in one line and move on.

## Commit core  [BRIEF, PROMPT]

Every sub-doc's Commit step points here.

**Run the mail triage before staging** — anything it files, and the archive
moves it makes, belong in this same commit.

**Run the wind-down re-scan before staging** — it files any un-flagged captures
from this session's discussion so they land in this same commit. File-only.

**Run the session-file cleanup before staging too**, so any deletions the user
accepts fold into this same commit.

**Shipped-slug cross-check (work-item closes).** When this session shipped work
items, cross-check each shipped slug named in this session's LOG entries against
Processed and confirm it's been removed. A work item is normally removed when
/next locks scope, so the slug should already be gone — this is the safety net. If
a shipped slug is still sitting in Processed as active work, surface it in one line
and remove it (or halt and ask) before committing.

A planning session's /done names no shipped slug, so there's nothing to check. **Silent
unless a stray slug is found.**

**1. Stage explicitly — name each path:** files this session changed (from
the build working file Changes), method docs updated during the session or close-out (QUEUE.md,
SPEC.md, LOG/), and the build working file's deletion where one was removed.

**2. Detect out-of-scope dirty paths.** Run `git status --porcelain` and compare
against the active build's file list. Any dirty path outside it is a user edit no
build staged.

```
RECOGNISE THE INHERITED TAIL FIRST — and skip the investigation:
    a dirty LOG entry from a PREVIOUS session carrying a marked tail section,
    or a capture at the bottom of Unprocessed that no session here filed
        -> the previous session's post-commit tail, which by design commits
           nothing and rides into this commit
        -> fold it in with at most a one-line note

RECOGNISE THE HASH-BACKFILL SIGNATURE TOO — and skip the investigation:
    a dirty LOG/index.md or LOG/<slug>.md whose ONLY change is a placeholder
    hash becoming a real hash, in an entry heading or the start of an index line
        -> the previous /done run's own post-commit hash write (or, in a tracked
           project, the session-start backfill's safety-net fill)
        -> fold it in with at most a one-line note, no diff opened

any OTHER out-of-scope dirty path
        -> full treatment: surface it in a one-line summary and offer to stage
           it, investigating where the change isn't self-evident
```

**Where the staged paths include a method doc, name them in one line before
committing** — "staging QUEUE.md, SPEC.md and two log entries". One sentence, no
diff, no file-by-file account. The check above compares dirty paths against the
build's file list, so it cannot see anything inside a file the session already
owns — and QUEUE.md is the file a planning run edits by design.

**Two limits, and neither may be softened.** Naming the staged files makes a
swept edit **visible**, not **detected** — nothing cheap will ever tell the user
that a particular line inside QUEUE.md was theirs rather than Claude's. And
against the worst case it does almost nothing: where another session has already
*committed* this session's in-progress work under its own message, this line
produces the word "QUEUE.md" — true, useless, and silent about whose work is
inside. Describe it as making a swept edit visible, and as nothing further.

**3. The commit message is not drafted fresh** — it derives from the LOG entry
already written at the entry step. It is shown before the commit either way.

```
ONE work item shipped        ->  the message IS that entry:
(and plan/setup closes)          title = the index line's one-liner, verbatim
                                 body  = the written rationale, verbatim
                                 # show it, stating that identity plainly

SEVERAL work items shipped   ->  title = a one-line summary of what the run
(a multi-item /next run)                 shipped across all its items
                                 body  = each shipped item's one-liner, one
                                         per line
                                 # this roll-up IS genuinely new text — show
                                 # it for approval

staged extras (backfills,    ->  the body appends ONE line naming them
sweep edits, rolled-in user
edits from step 2)
```

**Show the message itself, verbatim, and nothing else about it.**

**4. Commit without a further ask.** The commit always happens at /done and its
message was already approved, so there's nothing new to confirm. Only the push is
optional.

**Where the session held more than one person, the commit may add a
`Co-authored-by:` trailer for a roster participant whose recorded consent
covers it** — using only the name and email details they chose to share, never
details looked up on their behalf. No roster, or no consent recorded: no
trailer.

```
commit first (the safe, local action), THEN gate the outward push on consent:
    run one `git remote` check
        remote exists  ->  "Committed. Also push to the remote?"  (plain yes/no)
        no remote      ->  say it's committed; offer no push
```

A sub-doc may override to fit its session shape — done-plan.md commits and doesn't
offer push — but these commit-first mechanics stay canonical.

**5. Pass the message shell-agnostically.** Write it to a file in the session
scratchpad (e.g. `COMMIT_MSG.tmp` there), commit with
`git commit -F <scratchpad>/COMMIT_MSG.tmp`, then delete the file. One mechanism
on every machine — it sidesteps inline-quoting fragility, and the scratchpad is
on the scope-lock's standing list, so the write passes in every session type.

**5a. A staging step that partly failed is a STOP, not something to commit
around** [BRIEF, PROMPT]. Check that every path this /done run meant to stage is
actually staged — `git status --porcelain` and read what is in the index — before
running the commit. Where anything intended is missing, say plainly what did not
stage and why, and **hold the commit** until the staging is fixed and re-checked,
or the user decides.

**6. Commit with `git commit -F`.** No fresh okay needed. Then offer push only
when a remote exists, and push only if the user accepts.

**In a nested project /done commits both repositories** — the product's
changes as a commit in the inner repository (the product subfolder's own), and
everything else, the method documents included, in the outer. Same message
mechanics for each, the inner commit's message covering the product work
alone. A session that touched only one side makes only that side's commit. A
flat project — one repository — is unchanged by all of this.

**Then write the commit hash into the headings and index lines this /done run just
wrote** — /done is the one moment the hash exists and the files are at
hand, and it is one convention for tracked and untracked projects alike (an
untracked log never appears in any commit, so nothing later can attribute it
from git). Read the hash from the commit just made, replace each placeholder
this session wrote, and stop there. In a tracked project the
session-start backfill remains as the safety net for a fill this step missed.

## Recommend next  [BRIEF, PROMPT]

Every sub-doc's final step points here, adding only its flavor delta.

**Content line for this turn: it states the queue situation as the next
planning session would present it, any cycle whose turn is due — named whether
or not a capture was filed for it — and the continuations — more planning, or a
build — as statements of fact, and where the run this /done run records stopped at
a held item whose blocker it shipped, what of the intended change is
not yet on screen, in product terms, and nothing else.** Neither continuation is
assumed or recommended over the other: a user may plan as many times as they
want until enough is queued to justify a build, so which comes next is theirs,
and this turn's job is to leave them holding the facts that decide it.

**Two arms, decided by whether this /done run filed a concrete advisory:**

```
advisory FILED       ->  the closing message carries ONE line naming it and
                         pointing at the queue, plus any due cycle by name,
                         and nothing else from the ladder below. The advisory
                         already says what to do
                         next; restating it in chat duplicates the record.
                         The overlap scan still runs — and what it finds is
                         written INTO the advisory before it is filed rather
                         than narrated alongside it.
no advisory filed    ->  the full narration below, unchanged.
```

**Narrate the queue situation in everyday words**, and say how much work is
waiting to be sorted wherever any is — counting only what the next planning
session would actually present, which is the same set plan.md's own pass-overs
leave in play: a capture dated out, one bowed out behind an open blocker, and
cycle-owned material are not waiting, and are not counted or described as
available.

**Overlap scan.** Before recommending, scan the still-unprocessed work for overlap
with the top processed item — work that contradicts, invalidates, or would benefit
it if sorted first. It runs in both arms. **State the result either way, not only
when it blocks** (in the advisory-filed arm, state it inside the advisory):

```
nothing unprocessed              ->  say nothing's waiting for /plan
unprocessed but no overlap       ->  name what's waiting, give the plain verdict
                                     that nothing blocks it
overlap found                    ->  recommend /plan first, and name the overlap
```

Give the clean case as a plain assessment — "Three items are waiting to be
sorted; none touches the next piece of work, so nothing blocks it" — rather than
as a hedge.

**Queue-state ladder.** When nothing blocks:

```
1. captures appended this session that affect the next work
       ->  recommend /plan, name the blocker
2. work sits ABOVE the readiness marker
       ->  state the situation and both continuations as facts: the next
           cleared item by name, and how much work is waiting to be sorted
           (counted as the narration above defines). Where the build route is
           stated, the statement includes that a build runs best in a fresh
           session — information about that route, never the assumed next
           step. End the message on a statement that names each
           continuation's command in words, mid-sentence — the plan command
           for more planning, the next command for a build — with no command
           string at its end
2b. Processed holds work but the cleared region is EMPTY (the marker is at
    the top)
       ->  say the next work still needs vetting, and that running the plan
           command is what vets it. A build run would soft-stop here, costing
           a round trip.
3. Processed empty
       ->  say the queue is clear and that running the plan command is where
           more work comes from.
```

**A build runs best in a fresh session — a fact about the build route, not the
assumed next step.** What comes next is the user's decision, planning again as
much as building, which is why rung 2 states both continuations rather than
inviting either.

**A session makes exactly one commit, and the tail makes none.** That is the
whole shape, and everything below follows from it. /done commits; work
arriving afterwards is written to the working tree and left there, to be carried
by the next /done run. No amendment commit, no delta commit, no second /done run — and
a second `/done` is the tail, not a /done run.

```
/done                ->  ONE commit. Everything the session did.
the post-commit tail     ->  writes files, commits NOTHING:
                               a capture appended to QUEUE.md
                               an append to this session's LOG entry
                               the hash this /done run wrote in after its commit
                             all of it rides into the NEXT /done run's commit
/rescan                  ->  the one-word route to the same tail. Files by the
                             three-way triage — work to Unprocessed, what
                             HAPPENED to this session's entry as a marked tail
                             — and commits nothing, so it is not a second /done run
                             under another name. Repeatable, so nothing has to
                             judge when the tail has ended.
```

**The cost, stated rather than discovered: the tree is dirty between one /done run
and the next, always.** That is accepted, and it is what makes the dirt
*legible* — uncommitted changes at a session's opening mean one thing, the
previous session's tail plus its post-commit hash write, so a session
recognises the signature instead of investigating it.

**Read tail-shaped dirt as the previous session's LOG entry, a capture at the
bottom of Unprocessed, or a filled-in hash, and give anything else the full
treatment** — which is what keeps /done's staging check its teeth.

**In a tail, route an urge to run or drive testing or verification into a skill
rather than doing it here** — a quick /plan to structure the work, or /next to
hand over a `[user]` item that already exists. This fires hardest where the
verification is *already* a `[user]` item, because then the work has a home and
the tail is bypassing it.

**The limit, stated rather than found later:** the urge is not confined to a tail.
It happened in one, and nothing says it only happens there. Siting the clause here
covers the recorded instance and not the general case; a second instance occurring
outside a tail is what would reopen this.

**Announce a `[freeform]` item if Processed holds one.** /next halts on one rather
than building it, so say plainly what the item is and that it needs a session
where the work is done by hand rather than run from the queue.

**Hand over the words to start it.** With the announcement, give this starter
prompt verbatim in a fenced block — a paste target, rendered per the view-in-doc
rules — substituting only the item's slug for `<slug>`:

```
We're doing the freeform work item [<slug>] by hand in this chat — it's work
done by hand rather than run from the queue. Its entry is in QUEUE.md (in this
project's root folder), at the end of the cleared-to-run region of the
Processed section; read that entry first — it says what the work is and where
its recipe lives. When we're finished, the done command records and commits it.
```

Verbatim, not a template to adapt: fresh composition by an immersed session is
the recorded failure — every referring word must resolve inside the prompt
itself, because the session it's pasted into knows the queue exists and nothing
else about this conversation.

**Whether this step's recommendation was concrete decides the forward-advisory
disposition**, which is written in the LOG entry files section above, along with
the advisory's own wording and reserved slug. A concrete recommendation is filed;
a generic one is not, and the entry says which.

```
flavor deltas:
    build session ->  the shared ladder is the whole recommendation
    audit session ->  findings appended this session sit unprocessed, so the
                      DEFAULT is /plan, to sort them into work — name the count.
                      Only when nothing was appended does the overlap scan run
                      and the ladder apply (steps 2–3).
    plan/setup    ->  a fresh setup session whose only work item is the rough
                      first build item recommends /plan to scope it, NEVER
                      /next — the interview wrote that item deliberately
                      unscoped. Otherwise the shared scan + ladder apply.
```

