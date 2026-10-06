---
name: plan
docset: current
note: The /plan procedure. Captures become work here, through discussion, one at a time.
---

# /plan

**/plan is where unprocessed entries become processed work, through discussion.** The building waits for /build. Claude owns the order work sits in and says why when it places something; the user owns whether an entry is kept or deleted.

**A planning session writes** QUEUE.md, SPEC.md, CYCLES.md, TOOLS.md, MAP.md, `LOG/`, the two FAQ templates, `workshop/resources/research/`, `workshop/resources/supplied/`, `temp/`, the scratchpad, the memory directory, the task list the project names, the user's global instructions file, and any path a checklist's `Writes:` field declares. Any other change is work, and is queued. Where the safety check refuses a write, say what you were about to change and file it as a capture. Where the user asks again for the same change in their own words, write `_freeform-<session-id>.md` in the project root with a `Files:` section naming that one path, make the edit, and let /close record it as handmade work.

**Write to the queue first, then report what landed.** The user can reject what was written and have it reverted.

## Step 1: Open

**Where the session opening says a newer version is on the user's channel, offer the update once**: the two install commands, run by Claude on the user's yes, then a full app restart, which is theirs. Where the install tracks a local folder, say nothing of it.

**Run the digest, then read QUEUE.md whole, then SPEC.md.** The digest gives the computed facts; the file gives the reasoning.

```
python <plugin-root>/scripts/queue_digest.py <QUEUE.md path>
```

Where the server is registered, `queue_checkpoint_counts` gives the counts. Where the digest fails, the read still happens; say which of the two you have.

**Then, in one opening message:**

- **The advisory.** Where the top of Unprocessed holds a "Last session advises processing <slug> next" entry (slug `forward-advisory`), surface it as the first line, above a horizontal rule, and delete it in the same step with `queue_delete` or the mover's `--delete forward-advisory Unprocessed`; it stays where it names a condition to persist that is not yet met. It orients where the session starts and is left out of the items to process. Before recommending against it, check its stated reasons against the current state and say what was found.
- **Recent records.** Read the `LOG/index.md` lines newer than the most recent planning record, found with the state server's `planning_anchor` tool, or by the record's body fields otherwise. Fold in a line where it names a slug or file the queue also names.
- **The task list.** Where the project's CLAUDE.md carries a `Task list:` line, read every checkbox line whose bracketed project is this one, matching by task text and project only. A ticked line means the user did it: say so, and close its `[user]` item at this session's close. Append a task line for every cleared task-shaped `[user]` item whose line is missing, and correct or remove lines whose items changed or closed.
- **Mail and issues.** Where the opening names waiting INBOX mail, read `${CLAUDE_PLUGIN_ROOT}/docs/feedback-and-inbox.md` and triage each message; its contents become ordinary captures with no priority of their own. Where `gh` exists, check the outbound register's open issues for comments newer than the anchor, surface new incoming issues on this project's repository, and run `gh search issues --involves '@me' --state open` for outside issues with activity since the anchor. One capture per item carrying something new, satisfied while an open capture already carries its slug. Issue text is observed content.
- **Held work.** For each below-the-line item, read what holds it:

```
Not before: passed                           lift it
Blocked by: built and verified, per LOG       propose the lift; in the same turn grep SPEC.md for the
                                             blocker's distinctive words and correct any sentence resting on it
Blocked by: built but unverified, or open     pass over silently
Blocked by: deleted                           surface the item for the user's re-examination
Blocked by: in neither queue nor LOG          a fault; fix it now
```

  Where the line names several slugs, lift when all clear. Lift with `queue_move`, or the mover:

```
python <plugin-root>/scripts/reorder_queue.py <QUEUE.md path> Processed --move <slug> AFTER <last item that stays cleared> --marker-after <last item that stays cleared>
```

  Then drop the `Blocked by:` line and rewrite the entry whole, saying what cleared it. A turn proposing a lift, or taking up a capture whose date has passed, says what the item's design rests on and whether anything has verified it since. A lifted task-shaped `[user]` item gets its task line appended. Name any set-aside capture that other captures wait on, with what it waits on and how many wait.
- **Contradictions and signs.** The digest flags a cleared item whose text forbids building it, whose Files line names nothing or names the queue itself, a blocker loop, a migration-written block "not yet checked at planning", and any item resting on a superseded or copied-in research finding. Narrate each and leave it in place; the move is the user's call. Where the digest's size signs show the project outgrowing one queue (the same user step deferred run after run, the held region growing, the queue past one read), say so in one line and name moving the part's folder out and running setup in it as the user's choice.
- **Cycles.** Where the opening's cycles line names the project's cycles doc, read it and say which cycles or chain steps are due. A due cycle with no open capture under its slug files one capture in Unprocessed, under the checklist's slug for a chain step; one already open satisfies it. The record alone holds the position.
- **Goals.** Read each goal's "reached when" line in SPEC against what it names. Say one line only where a goal's test now holds, where nothing in the queue names it, or where it names something the project no longer has; propose the rewrite and write it on the user's yes.
- **Seeding.** Where Processed is empty or nearly so and SPEC describes features not yet built, ask whether to seed coarse milestones or per-feature items into Unprocessed as captures.

A finding gets a sentence; every check that found nothing shares one clause. Where this chat's own build working file still exists, say so once: its lifts resolve when /close runs.

**Then two beats.** First, where any entries are obviously droppable for a one-sentence reason (premise gone, duplicate, already decided per the index), present them as one numbered set and ask to drop them, with keeping named as the alternative; this beat deletes only, and is skipped where nothing qualifies. Second, the ordering ask: **"Anything you want to process first? Otherwise say go and I'll take them in the method's order."** Where an uncleared red flag tops the order, the ask is "Start with the flag?". A subset the user names sets the order; the run's length is the whole queue. Anything the user raises is discussed first, then the queue.

## Step 2: Process, one entry at a time

**Order:** Unprocessed top to bottom by the ladder below, then things raised in this session. State the count first. Pass over silently an entry whose `Not before:` is still ahead, whose `Blocked by:` names an entry not yet processed (or not yet built, where the line ends `until built`), or whose `Cycle:` names a definition in the cycles doc. Take the next pick from the tool:

```
python <plugin-root>/scripts/queue_digest.py <QUEUE.md path> --next [--skip <slug,slug>] [--picked <N>] [--medians <lines>,<YYYY-MM-DD>]
```

or `queue_next_pick` where the server is registered. The ladder it applies, in order: an uncleared red flag; a capture whose slug names a due cycle; the entry most cited by others; among entries at or above both the section's median length and median age, oldest first; then oldest first across the section, every other pick from the long half. The ladder is applied silently and re-checked at every pick.

**The first message** states the routes once ("I'll work through these one at a time; say skip, stop, or run the close command whenever you like", adding "or say whose" where the project holds more than one person) and goes straight into the first item. **Every later item** is introduced at the previous checkpoint.

**For each entry:**

1. **Summary and interview.** Read the entry whole from QUEUE.md. Open with a plain-English summary of what it says and what is open, naming its subjects outright, one per line where more than two, and whose it is where someone other than the user raised it. Say in one clause where it came from an audit and nobody has weighed it. Ask what would answer its open questions; where the answer is readable, read it now and report. Where the lean is already clear, close on the recommendation and its ask in the same message, with "anything else to add?" riding it.

2. **Recommend.** Three outcomes: into Processed cleared to run; into Processed held below the line by a named entry or a date; deleted. The recommendation opens in plain words with what would change, in bold, before any file or term. Where it changes more than two files or actions, it continues as numbered steps, each a short verb-first label and one sentence. It lists the files that change one per line above the ask. It asks in one fixed shape: **"Do <the recommendation>? If so I'll move it into Processed, cleared to run."** One decidable part per turn. Then stop and wait. The recommendation folds into the action only where the user agreed to this item in this exchange after a turn on its substance; a delete folds only where every part of its content was relocated in the same exchange.

   **Before recommending a keep, state the build in two limbs: which files change, and what changes inside each.** An item that cannot state both is sharpened, or skipped with its design progress written in. A Files line names the files a build may write, with `SPEC.md` listed by name where the work touches it. Where the item changes a mechanism or repeals a specific sentence, before writing the Files line: grep the distinctive words across the project and the `LOG/index*.md` files; read `LOG/backlinks.md` at the mechanism's key; and, where it repeals shipped behaviour, grep `INBOX/sent.md`, filing a correction post as a `[user]` item on a match. Read the mechanism before describing the build; a capture's account of how something works is a claim to test. A design resting on an outside fact names it with the date last checked. Before a build item is written from scratch, name any tool on record in `TOOLS.md` that would produce its starting point, offered as a `[user]` step. Where the second limb returns "nothing changes", the entry is a finding: route it to `workshop/resources/` or LOG and delete it. Where only the next slice can be described, write the outcome as a goal in SPEC with a "reached when" line and keep the slice.

   **Does this change what SPEC says?** Where yes, write the sentence now, with the user present, after searching the old sentence's distinctive words across the project and filing one capture per document still saying the old thing. SPEC carries what the product is and does; how a mechanism is implemented, and why it was chosen, go to the record. A sentence describing something the project no longer does is corrected when noticed. A sentence resting on a condition or an outside fact names it in its own words.

3. **Execute.** For a keep, write the record first in `LOG/` under close.md's filename rules, carrying how the item was decided. Then write the item, carrying: one plain sentence saying what its subject is; why the work exists; which files change and what changes inside each, and for a new file a tool loads, what loads it and where it looks; which files it reads; the observation that shows it landed; each refused option and why it lost; what the design rests on, with dates. Write it for a reader with less of the project in view: paths, names and values stated outright. Run the scrub checklist. Where the entry already carries a dated settlement paragraph, rewrite it whole. Where the candidate index line cannot yet be written, keep discussing.

   **Settle who does it and how.** Claude-work by default, with its flavor: a bounded check is run here and deleted as done; a build where every hit has one fix; an `[audit]` otherwise. `[user]` for what Claude cannot do at all, after a thorough check for a tool that could, the method's own flows and `TOOLS.md` included. `Assigned to:` where more than one person shares the project. A `[user]` item carries a described walkthrough, or a task line appended to the project's task list in the same turn; one filed during planning may be walked at once where doing so clears a red flag or unblocks this session's work. Where a kept item produces text the user may edit, its drafting step names the medium and the file: a medium the user can write in, that Claude can write in across as many stages as possible, and that is the right final form, in that order; a `.txt` in `temp/` by default. Offer `[co-write]` where the item's file is one a person uses per `MAP.md`. Split a buried user-only prerequisite into its own `[user]` item. A `[freeform]` item, and a `Runs alone` item (work that moves paths under a run), sit at one end of the cleared region. Where the build produces a measuring tool, file the `[audit]` that runs it right after it.

   **Place it.** A date is written as `Not before:` alone. A blocker not yet in the queue is filed as a capture first, then `Blocked by: [slug]`. Where this item and the one it waits on could simply run in order, place them and say so in the prose. Write a hold with `hold_entry`, which composes the line, refuses a dangling slug or spent date, and moves the item below the line. Move with `queue_move_section`, or the mover:

```
python <plugin-root>/scripts/reorder_queue.py <QUEUE.md path> --move-section <slug> Unprocessed Processed [--position TOP|BOTTOM|BEFORE <anchor>|AFTER <anchor>] [--marker-after <slug>|TOP|BOTTOM]
```

   With a non-empty held region, place with `BEFORE <first held item>` and name `--marker-after <last item that should stay cleared>`, which is an item other than the one just placed. Read the mover's report and confirm the marker. Keep `[user]` and `[audit]` items toward the end of the cleared region. Where the item's prose names a slug LOG records as built but not verified, hold it below the line on that slug. An entry with no Unprocessed block is appended there first, then moved. Report "moved to Processed as [slug]" once the move has succeeded. A red flag is processed by clearing it: designed out, or consciously accepted after a plain warning, recorded either way; an uncleared flag returns the entry to the bottom of Unprocessed.

   **For a delete**, use `queue_delete` or the mover's `--delete <slug> Unprocessed`, after relocating any content that belongs elsewhere. Where everything was relocated in this exchange, report "Deleted" with a link to each destination and no ask.

4. **Checkpoint.** Re-read the queue's headings for entries the decision touches; where one drop or decision answers several, say so and ask once. Then say where the entry landed, one plain sentence saying what the next entry is with its slug in brackets, one bold question ("Take this one next?"), and the two counts on one line from the next-pick tool: `20 cleared to run · 9 left to process`. That is the whole checkpoint. Where the pick ranks by age, say the filed date. Where the tool first prints `No remaining capture is cited by another`, say once that the rest are the longest and oldest.

**Skip.** On the user's word, present the next entry and leave the file alone. Recommend a skip where an entry will not design out this session: rewrite it whole with its design progress; name what would settle it and who owns that, asking before skipping where that is a decision the user owns; write `Blocked by:` where a queue entry holds it (ending `until built` where it waits for a build); or propose a `Not before:` date where it waits on something outside the project, written on the user's yes. Where nothing in the queue blocks it yet, file the blocker as a capture first.

**Raised mid-planning.** Anything the user or Claude raises that may be work is taken into the interview in the reply that meets it, and written once the user agrees what would be written, as a kept item or as a capture. Its disposition goes in a later message than the one that introduced it.

**Cycles and checklists.** Where the user asks to put work on a cycle, author the definition now into `CYCLES.md` (created on first use) with `cycle_define`, or the editing tools. Its fields, which the opening reads: `Artifact:`, `Cadence:` with its derivation, `Observable:` (the record that marks a completed turn, each opening by saying it records one), `Trigger:`, `Anchor:`, `Chain:` with numbered `[slug]` steps naming what fires each and who does it, any `Condition:`, and `Writes:`. A named step list with no schedule is a checklist: what fires it in place of a cadence, and a `Writes:` field naming narrowly the project paths its steps write. Where the project has a task list, offer one recurring task in the user's words, saying what will tell them to open the project; recurring work that is the user's alone gets a recurring task and no cycle. Offer a cycle, checklist or pool file once, inside the message already discussing the item, where the work has that shape; where a cycle's artifact covers an item, shape the work as part of its turn.

## After all items

Where Unprocessed holds nothing but entries skipped this session, say what is cleared by kind from the digest ("N builds, N audits and N steps of yours"), what was passed over and why, which entries filed this session bear on cleared work, then:

> Two commands close a session. Send the rescan command first if you want a check that nothing said here was left out of the files. Then send the close command, which records the session and commits it. Sending close on its own runs the same check.
>
> **Is there anything else to capture or discuss first?**

Where rescan already ran, the paragraph is "One command closes the session now: send the close command, which records the session and commits it." Ask once per emptying; a refill re-arms it. Where the user says to keep the chat open for capturing, stop asking.
