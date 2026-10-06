---
name: close
docset: current
note: The /close procedure. Records what the chat did, cleans up, commits once, and says what comes next.
---

# /close

/close records everything the chat did, cleans up, commits once, and recommends what comes next. It takes on no new build scope; a fix completing the just-built work's own verification folds in, and anything else routes out as a capture.

## Declare and route

**First action:** write an empty file `.throughliner/close-active-<session-id>`, and delete it as the last action, together with `.throughliner-setup-done` in the scratchpad where setup ran in this chat. While it stands the safety check permits the files close itself must write.

**Already closed?** Where `.throughliner/session-closed-<session-id>` exists, this is the post-close tail, not a second close: file what it finds by the three-way triage, append what happened to this session's existing entry as a marked tail under a `## After /close` heading with the state server's `append_tail` tool, commit nothing, and say so in one line, naming the fresh-chat route where handmade work would be committed as a session of its own.

Otherwise check for **this session's** `_build-<session-id>.md`, no other session's, and route silently:

```
working file exists   ->  the build close below, one LOG entry per item, build and [audit] alike
no working file       ->  the no-build close: a planning session, a completed [user] item,
                          or standalone handmade work, which overlap freely
```

Read the working file whole before anything else. Record every `[user]` or `[co-write]` item the session touched under build.md's outcome values, read off the session's own trail. Where the opening named waiting mail, triage it as `${CLAUDE_PLUGIN_ROOT}/docs/feedback-and-inbox.md` states, filing only; where a reply is owed, draft it and show the exact wording.

## The build close

1. **Verify completion.** Where some items are unticked, ask: finish the rest with /build, or close partial, which deletes the working file and leaves the queue alone. Before deleting, confirm every ticked item is gone from QUEUE.md and every unticked one is still there, and fix any mismatch. Where memory and the file disagree, file that as a finding.
2. **Route findings** from the working file's notes and `Run-level:` section to Unprocessed as captures, each written then reported, the set as one numbered report.
3. **Check the run against SPEC** and leave SPEC unedited: where the run contradicts a sentence, name it and let the user decide which is wrong; where the build filed a capture for a sentence SPEC owes, say SPEC lags until the next planning run.
4. **Red flags.** For each built item carrying a marker, carry "cleared" into its entry; a marker still reading `uncleared` is a stop. An audit never clears a flag.
5. **Write one LOG entry per built item**, named after its slug, by the entry rules below, with the build fields `Files touched` (from `Changes:`) and `Routed to Captures` (or "none"), and for an audit `Findings routing` (filed, and any dropped on re-reading, with why). Read each item's reasoning from the queue as it stood before the run, `git show HEAD:QUEUE.md`, taking its whole block from its `#### ` heading to the next; where QUEUE.md is untracked, write from `Changes:` alone and say the history could not be recovered. Read each item's `Depth:` and `Rule gate:` lines by slug; a slug with no depth line is short, noted as a slip. Transcribe the tick form verbatim and announce every `UNCONFIRMED` item in the close narration. Where one decision settled several items, one entry carries the reasoning and the others cite it, each still named for its slug. A `[user]` entry the walk-through opened is continued, not duplicated; on the done arm, run any observable check the item names and remove it from Processed with the mover.
6. **Staleness sweep**, below. Then delete the working file, silently, only after everything above.
7. **Commit core**, below. Then recommend next.

## The no-build close

- **Spec-sync gate.** This is the only close that syncs SPEC. Read `git diff HEAD -- SPEC.md '**/SPEC.md'` (in the inner repository too, in a nested project) and `git diff HEAD -- QUEUE.md`; where a file is gitignored, read the safety check's snapshot copy. For every SPEC sentence written this session, read the item it was written for as it now stands and correct the sentence where they came apart; for every kept item, check for a product-truth change with no sentence. On drift, stop before committing, name the sentence, and fix it in this same commit on the user's yes. A sentence describing decided-but-unbuilt behaviour is the designed lead, not drift.
- **Handmade work.** Uncommitted changes the session did not make are the user's own expected work: confirm they are theirs, leave them intact, and record them, one entry for a coherent change (`LOG/<date>-handmade.md`) or one per logical change. Where they add, rename or remove product folders, record the move as the user's structural decision, grep SPEC.md and MAP.md for the old names, and correct them on the user's yes. Where a scope file `_freeform-<session-id>.md` exists with no queue item behind it, name the paths the safety check's log shows the door admitted (`.throughliner/pre-tool-use.log`, branch `freeform scope file`, this session's id).
- **Batch the human stops.** One pass over Processed: `[user]` and `[audit]` items go after contiguous build work, ahead of any `Runs alone` item, which stays last, with `[co-write]` after them. Leave a `[user]` item that names dependent builds by slug ahead of them, and an `[audit]` that reads a tool's output right after that tool. Use the mover with the full desired order:

```
python <plugin-root>/scripts/reorder_queue.py <QUEUE.md path> <Processed|Unprocessed> <slug1> <slug2> … [--marker-after <slug|TOP|BOTTOM>]
```

  A non-zero exit means nothing was written; re-read and re-run. Narrate a change to what /build would pick next; say nothing where nothing moved.
- **Position the cleared-to-run line** just below the last item the user agreed is ready. Hold back an item whose prose depends by slug on work built but not verified, read from that entry's transcribed tick, with an entry carrying no tick field treated as unconfirmed; the one exception is an item that is itself its blocker's only verification. Every item below the line names what holds it: `Blocked by:`, `Not before:`, with `Assigned to:` carried beside. Ready `[user]` work goes above the line. Narrate only what moves.
- **Completed `[user]` items.** Where the session saw one completed (the user said so, its observable check passes, or its task line was ticked at the opening), write a LOG entry under its slug and remove it from Processed with the mover. Say nothing about the others.
- **Write the LOG entry** with the fields `Queue changes:` and `Work processed:` (kept and deleted, with slugs, or "none"), read off `git diff HEAD -- QUEUE.md`, not memory; skipped items leave no trace and are not recorded. Where an item's record was written at its keep, complete that record by edit rather than writing a second. Where a red flag was cleared this session, record how: designed out, or the informed-consent trail.
- **Commit core**, then recommend next. A fresh setup session whose only item is the rough first build recommends /plan to scope it, never /build.

## Staleness sweep

Check the remaining work items for references to files since renamed or deleted, or to behaviour since moved past. A fate decision (drop, rewrite, keep) is /plan's: defer it. A pure pointer drift is fixed here in one line, with the queue tool's literal replace in a build close: `reorder_queue.py --replace-in <slug> --old <literal> --new <literal>`.

## LOG entry files

Run the scrub checklist on the text. The session authors two texts: the one-liner, which is the entry heading's summary, the index line and the commit title; and the rationale, which is the entry body and the commit body. One file per entry under `LOG/`:

```
work item closed          ->  LOG/<YYYY-MM-DD>-<slug>.md      (full slug, never shortened)
session with no slug      ->  LOG/<YYYY-MM-DD>-<type>.md      (plan, setup, handmade)
name taken                ->  LOG/<YYYY-MM-DD>-<slug>-<kind>.md  (-plan / -build), then -2, -3
```

```
---
summary: <the index line: the artifact touched and the nature of the change, enough to decide open-or-skip>
---
# [HASH] — <one-line summary>

Date: <YYYY-MM-DD HH:MM, read from the clock at the moment of writing>

<prose rationale, re-authored from the work's reasoning, carrying any concern raised and resolved and any alternative that lost, with why>

<the flavor's body fields>

Advisory: filed — <slug>        or   Advisory: not needed — <why>

**Also in this chat:** <corrections, decisions reached in conversation, errors made and fixed, work done by hand; omitted when empty, and its own entry named for the chat where the close writes several entries>
```

Every date written at close is today's, read from the clock; where the session ran across more than one day, say so in one sentence. Write the literal placeholder in hash position only. Then regenerate `LOG/index.md`, each `LOG/index-YYYY-MM.md` and `LOG/backlinks.md` with `python <plugin-root>/scripts/log_backlinks.py <project root>`; none is edited by hand. Report in one line what landed. A check only the user can run is filed as a `[user]` capture, never left as LOG prose.

**The advisory.** Where recommend-next makes a concrete recommendation, file it as a capture at the top of Unprocessed with the heading `Last session advises processing <slug> next`, the tool appending the reserved slug `forward-advisory`, conditions stated in prose; where a planning close's look-back filed captures, the advisory names them as what to open on. A spent advisory already in the slot is deleted first. A generic recommendation files nothing, and the entry's line says which.

## Wind-down look-back

Before committing, look back over the chat only as far as the last /rescan, and surface candidate captures: things the user thought out loud but never flagged. An amendment to a work item the user directed this session is made to the item and recorded under its name; a problem Claude noticed in a cleared item stays a capture, with the collision named. Where nothing happened since a rescan, write "covered by the rescan just run". Run the cycles check as plan.md states it, reading the project root for a `CYCLES.md` created this session. First say one sentence on what the files prove ran that is no longer in view (a queue diff, a working file's ticks), and never add that nothing was lost. Show the candidate set as one numbered message, opening by naming itself as the close's look-back, ending "Say go to file it, or say no" (one), "Say go to file both, or contest by number" (two), or "Say go to file them all, or contest by number" (more). Write them on the yes and add them to the entry's `Routed to Captures` line.

## Session-file cleanup

Delete the working file and this session's scope file. Offer to delete, one at a time, only files Claude created this session with no future use, warning where one is untracked. In `temp/`: delete each file a line in `INBOX/sent.md` points at, saying so; remove an attachment no open capture names; list the rest with dates and offer once to clear them, never deleting a `[co-write]` file or one the user edited without a yes.

## Commit core

Run the mail triage, the look-back and the cleanup first so their writes ride this commit. Where `MAP.md` exists, grep this session's new folders and human-used files against it and write missing lines on the user's yes. Where work items shipped, confirm each shipped slug is gone from Processed.

1. **Stage explicitly by path:** the files `Changes:` names, the method docs, the working file's deletion. Where another chat is open on the same project, stage only what this session wrote and leave the other's changes to it. The safety check refuses a commit while any tracked file carries a conflict marker.
2. **Read `git status --porcelain` for dirty paths outside the run's list.** The previous session's tail (a marked tail section, a capture at the bottom of Unprocessed) and a hash backfill fold in with at most a one-line note; any other path is named in one line and offered for staging. Name the staged method docs in one sentence; this makes a swept edit visible, not detected.
3. **The commit message derives from the entry:** one item shipped, the title is the index line and the body the rationale verbatim; several, a one-line summary of the run with each item's one-liner as the body; staged extras get one appended line. Show it verbatim as the record and commit in the same turn: running close was the consent. Write it to a scratchpad file and commit with `git commit -F <that file>`. Check every intended path is staged first; a partial staging holds the commit.
4. **In a nested project commit both repositories**, the product's changes in the inner and everything else in the outer. Before a commit to a repository with a remote, read `git diff --cached` there against the scrub checklist and anything shaped like an email address; on a find, hold that repository's commit, name the file and kind, and ask whether to rewrite it. A `Co-authored-by:` trailer only for a roster participant whose recorded consent covers it.
5. **Offer the push only where `git remote` shows one:** "Committed. Also push to the remote?" With no remote, say nothing about pushing.
6. **Write this session's record filename into `.throughliner/session-closed-<session-id>`**, then write the commit hash into the headings this close wrote and regenerate the index files.

A session makes one commit; the tail makes none. Work arriving after the close is written to the tree and carried by the next close.

## Recommend next

Five things, each from a computed fact: the commit hash and the record's link; the cleared count and the first few cleared items by name, from the digest or `queue_checkpoint_counts` run after the last queue write; the count waiting to be sorted, counting only what the next planning session would present; the run-alone announcement where a `[freeform]` item or a `Runs alone` item with zero cleared items ahead sits in Processed; and one recommendation, naming a fresh session as where it runs and the command in words mid-sentence. Where the run stopped at a held item whose blocker it shipped, say in product terms what of the intended change is not yet on screen. Where this close filed a concrete advisory, the closing message is one line naming it, plus any due cycle, and nothing else.

Where a held item's every blocker was built in this run with its tick confirmed, lift it above the line with `queue_move` or the mover, drop its `Blocked by:` line, rewrite it whole, append its task line where it is task-shaped, and say so in one line; a blocker built but unconfirmed leaves the item held.

Scan the still-unprocessed work for overlap with the top cleared item and state the result either way. Then: captures filed this session that affect the next work, work needing vetting, or an empty Processed: recommend /plan. Work above the marker: name the next cleared item and recommend /build. An audit session with findings appended recommends /plan, naming the count.

For a run-alone item, hand over the starter prompt verbatim in a fenced block, filling `<slug>` and `<heading>` from `queue_next_pick` or the digest:

```
We're doing the freeform work item [<slug>] by hand in this chat — it's work done by hand rather than run from the queue. Its entry is in QUEUE.md (in this project's root folder), at the end of the cleared-to-run region of the Processed section; read that entry first — it says what the work is and where its recipe lives. When we're finished, the close command records and commits it.
```

```
Run the build command. The top cleared item is "<heading>" [<slug>], marked Runs alone, so this run builds that item and nothing else — the run ends after it. Its entry is in QUEUE.md (in this project's root folder), at the top of the cleared-to-run region of the Processed section; read that entry first — it says what changes and where. When it is built, the close command records and commits it.
```
