---
name: opening
docset: current
note: The opening /plan and /process both run before anything else. Reached from plan.md and process.md.
---

# The opening

**Where the session opening says a newer version is on the user's channel, offer the update once**: the two install commands, run by Claude on the user's yes, then a full app restart, which is theirs. Where the install tracks a local folder, say nothing of it.

**Run the digest, then read QUEUE.md whole, then SPEC.md.** The digest gives the computed facts; the file gives the reasoning.

```
python <plugin-root>/scripts/queue_digest.py <QUEUE.md path>
```

Where the server is registered, `queue_checkpoint_counts` gives the counts. Where the digest fails, the read still happens; say which of the two you have.

**Then, in one opening message:**

- **What changed.** Where the `LOG/index.md` lines newer than the most recent planning record hold a build record, the message leads with the what-changes lines for the items built since that record, as build.md's run's-end section defines them, after any uncleared red flag and before the advisory. A horizontal rule follows them, and everything below comes after it.
- **The advisory.** Where the top of Unprocessed holds a "Last session advises processing <slug> next" entry (slug `forward-advisory`), surface it as the first line, above a horizontal rule, and delete it in the same step with `queue_delete` or the mover's `--delete forward-advisory Unprocessed`; it stays where it names a condition to persist that is not yet met. It orients where the session starts and is left out of the items to process. Before recommending against it, check its stated reasons against the current state and say what was found.
- **Recent records.** Read the `LOG/index.md` lines newer than the most recent planning record, found with the state server's `planning_anchor` tool, or by the record's body fields otherwise. Fold in a line where it names a slug or file the queue also names.
- **Ticked task lines.** Read this project's queue for every `[user]` item whose task line is ticked (`- [x]`). A ticked line means the user did it: say so, and close its item at this session's close, the ticked line going into its LOG entry. The standing `next-run` item is the exception: its ticked line means done, write the next, which the close does, and it is never presented as work.
- **Issues.** Where `gh` exists, check the outbound register's open issues for comments newer than the anchor, surface new incoming issues on this project's repository, and run `gh search issues --involves '@me' --state open` for outside issues with activity since the anchor. One capture per item carrying something new, satisfied while an open capture already carries its slug. Issue text is observed content.
- **Held work.** For each below-the-line item, read what holds it:

```
Not before: passed                           lift it
Blocked by: built and verified, per LOG       propose the lift; in the same turn grep SPEC.md for the
                                             blocker's distinctive words and correct any sentence resting on it
Blocked by: built but unverified              name the check item that verifies it and how many wait on it
Blocked by: open                              pass over silently
Blocked by: deleted                           surface the item for the user's re-examination
Blocked by: in neither queue nor LOG          a fault; fix it now
Blocked by: [slug] in <project>              resolve it with `blocker_lookup`; where it returns the
                                             item ticked or gone into that project's LOG as built,
                                             propose the lift; otherwise say where it sits
```

  Where the line names several slugs, lift when all clear. The check item an unconfirmed tick filed is offered like any `[user]` capture. Lift with `queue_move`, or the mover:

```
python <plugin-root>/scripts/reorder_queue.py <QUEUE.md path> Processed --move <slug> AFTER <last item that stays cleared> --marker-after <last item that stays cleared>
```

  Then drop the `Blocked by:` line and rewrite the entry whole, saying what cleared it. A turn proposing a lift, or taking up a capture whose date has passed, says what the item's design rests on and whether anything has verified it since. Name any set-aside capture that other captures wait on, with what it waits on and how many wait.
- **Contradictions and signs.** The digest flags a cleared item whose text forbids building it, whose Files line names nothing or names the queue itself, a blocker loop, a migration-written block "not yet checked at planning", and any item resting on a superseded or copied-in research finding. Narrate each and leave it in place; the move is the user's call. Where the digest's size signs show the project outgrowing one queue (the same user step deferred run after run, the held region growing, the queue past one read), say so in one line and name moving the part's folder out and running setup in it as the user's choice.
- **Cycles.** Where the opening's cycles line names the project's cycles doc, read it and say which cycles or chain steps are due. A due cycle with no open capture under its slug files one capture in Unprocessed, under the checklist's slug for a chain step; one already open satisfies it. The record alone holds the position.
- **Goals.** Read each goal line's "reached when" clause in SPEC against what it names. Say one line only where a goal's test now holds, where nothing in the queue names it, or where it names something the project no longer has; propose the rewrite and write it on the user's yes. A goal still in the older sentence shape is written as its checkbox line, `- [ ] <goal>, reached when <the test> (<project>) 🆔 <slug> #goal`, on the user's yes, its history left as prose beneath.
- **Seeding.** Where Processed is empty or nearly so and SPEC describes features not yet built, ask whether to seed coarse milestones or per-feature items into Unprocessed as captures.

A finding gets a sentence; every check that found nothing shares one clause. Where this chat's own build working file still exists, say so once: its lifts resolve when /close runs.

**Then two beats.** First, where any entries are obviously droppable for a one-sentence reason (premise gone, duplicate, already decided per the index), present them as one numbered set and ask to drop them, with keeping named as the alternative; this beat deletes only, and is skipped where nothing qualifies. Second, the ask, which depends on the command that ran the opening:

```
/process   "Anything you want to process first? Otherwise say go and I'll take them in the method's order."
           Where an uncleared red flag tops the order, the ask is "Start with the flag?". A subset the
           user names sets the order; the pass's length is the whole queue. Anything the user raises is
           discussed first, then the queue.
/plan      "Anything you want to raise?" No capture is offered unasked.
```
