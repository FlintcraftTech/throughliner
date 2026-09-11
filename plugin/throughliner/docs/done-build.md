---
name: done-build
docset: current
note: >
  Close-out for build-flavor work items. Reached from done.md's router for the
  run's build items (work items carrying no flavor tag), and — through the
  audit delta at the end — for its [audit] items.
---

# Build close-out

A build that changed SPEC.md — because a build item listed it as a large SPEC
rework — closes here like any other build. There is no separate spec-edit close.
A build cannot reach SPEC any other way: the grow-scope-and-edit-inline route is
repealed, and a build that finds SPEC owes a sentence files it instead.

```
a run may contain SEVERAL build items:
    per built item  ->  the judgment and record steps, one LOG entry each
    once per close  ->  the staleness sweep, the commit, the recommendation
```

## Phase 1: Judgment (while context is fresh)

Captures meaning that would be lost after compaction.

### Mid-close directive — new scope vs build-completing fix  [PROMPT]

If a new directive arises during /done — the user raises a change, or
verification turns one up — decide by one line: **does it complete the just-built
work's own verification, or is it new scope?**

```
a fix to a genuine bug in what this build was meant to deliver
    ->  FOLDS IN. Finish it, tick it — it's part of the build.
new scope (a redesign, a new feature, a change to something that already worked)
    ->  ROUTES OUT: a fresh /next, or a capture to Unprocessed if not urgent.
        Even if it looks small. Even if the user raises it here.
```

/done records and commits; it doesn't take on new build scope.

### 1.1 Verify completion  [SILENT] when every item is ticked; [PROMPT] when any is not

Read the build working file. Is every item ticked — each build item done?

```
yes             ->  proceed
some unticked   ->  [PROMPT] ask: finish the rest (/next), or close partial?
                    Wait for the user's call.
```

**Close partial by deleting the build working file and leaving the queue alone.**
An item is removed from QUEUE.md only as it is ticked, so an unticked item is
still sitting in Processed exactly where it was — there is no copy-back step and
no count to reconcile.

Before deleting the build working file, confirm the two halves agree: every
ticked item is gone from QUEUE.md, and every unticked one is still there. A
mismatch means an interruption landed between the tick and the removal — say
what you found and fix that one item, rather than proceeding.

**Reconcile against memory.** Where the session is still remembered, reconcile
the build working file against what you recall. If the file and memory disagree
— work that happened but went unticked, a Changes note missing something memory
knows was done — **that mismatch is itself a finding about build discipline**,
and it routes to Unprocessed per 1.2. It's the only routine check the build
working file's accuracy gets before a fresh session has to rely on it.

### 1.2 Route findings to Unprocessed  [PROMPT]

Each finding is written to Unprocessed first, then reported — the whole set as
one numbered report.

```
the RECORD this step sweeps:
    the build working file's notes, its Run-level section included — the
        writes belonging to the run rather than to any item (mid-run
        captures, live-opened records), which reach the session record
        from there. A working file from before the section existed lacks
        it; fall back to memory as before.
    any captures already appended at the moment of noticing
conversation memory  ->  a same-session BONUS pass, never a source the step
                         depends on
```

Append each finding to Unprocessed, placed per the Captures placement rule
(narrate the placement). Append any fix a build check surfaced too.

### 1.3 Spec check-against  [SILENT] when the run agrees with SPEC; [PROMPT] on a contradiction

**The build session's /done checks the run's work against SPEC. It does not sync SPEC to
match it.** Each item was already checked as it was built (next-build.md, step 4);
this is the run-level look, over work that has accumulated.

```
run agrees with SPEC   ->  silent; nothing to report
run CONTRADICTS SPEC   ->  name the SPEC sentence and the work that contradicts
                           it, in plain words, and let the user decide which is
                           wrong. Do NOT rewrite SPEC to fit what was built.
```

**Where the build found that SPEC owes a sentence, it filed a capture and wrote
nothing** (next-build.md, Scope management). Confirm the capture exists and say
in one line that SPEC lags that sentence until the next planning run. **Do
not write it here:** /done is the same session as the build, so writing it
now moves the self-certification later rather than crossing the session boundary
the rule exists for.

This step exists for contradictions between the built work and SPEC as it
stands — a different thing from a sentence SPEC does not yet carry.

### 1.4 Red-flag close  [SILENT] when no flag; [PROMPT] when an item carries one

Per built item carrying a `Red flag · State: …` marker, before the item leaves
the queue. Its flag was cleared at an earlier /plan run, so two things:

```
1. carry the cleared flag into this item's LOG entry (2.1)
   # note it carried a red flag and that it was cleared. The substantive
   # how-it-cleared record was written at the /plan close that cleared it.
2. BACKSTOP [PROMPT]: marker still reads State: uncleared?
   # should be impossible. STOP and surface it rather than committing — an
   # uncleared flag at a build session's /done run means the model was bypassed.
```

Silent when no built item carries a flag.

### 1.5 Reply to mail the run opened  [SILENT] when no mail arrived; [PROMPT] when it did

Where /next's pre-flight opened a message that asked a question, a reply is owed:
draft it now and show it. A defect report is owed nothing by default. /done is the moment the user is reliably present, which
mid-run is not — and a reply leaves the machine, so it goes out only on their
explicit yes to the exact wording, with the draft put in front of them unprompted.

## Phase 2: Record

### 2.1 Write LOG entry  [DISCUSS, PROMPT]

**Narrate first** [BRIEF]: one sentence noting the work's reasoning is being
carried from the build working file into the LOG entry — the file's last job before /done
deletes it.

Write **one LOG entry file per built item**, each named after that item's slug.
Follow done.md's **LOG entry files** section, with the build body fields:

```
Files touched       from the build working file Changes
Routed to Captures  items added, or "none"
```

**Read each built item's reasoning back, one entry at a time** [SILENT]. The run
read it to aim the work, but it is the record that has to carry it forward — a
LOG entry written from the working file's Changes alone records what happened
with the *why* stripped out, which is the failure the throughline exists against.

**Read it from the queue as it stood before the run**, because the run has already
removed each item as it ticked:

```
git show HEAD:QUEUE.md
```

The run has not committed yet — /done is what commits — so every item this run
built is still in the last commit's copy, whole. **Take the item's whole block —
from its `#### ` heading to the next heading, or the section's end** — and
nothing else; a read of the whole file is not needed to answer one slug. A hand-sized grep or line window is not used:
a window shorter than the item once truncated the read twice in one /done run, and
both outputs reasoned from the cut-off text, one reaching the user.

**Where the fetched item's own text already dispositions a question /done is
about to put to the user, transcribe the disposition instead of asking** — and
an ask that deliberately re-opens one names the recorded decision it re-opens.

**Where QUEUE.md is untracked, git holds no copy and this route is closed.** Say
so plainly in the entry rather than implying the reasoning was carried: write the
entry from the working file's Changes alone, and record
that the decision history could not be recovered. That is one of the consequences
of an untracked queue, and it is stated rather than discovered.

**One entry per built item is unconditional in COUNT, not in content**, however
long the run. A work item's queue text is *consumed* when it builds — /next
removes it — so after the build the LOG entry is the only surviving record of
what the work was for. The count rule never forbids done.md's sibling-citation
provision: where one decision settled several of the run's items, one entry
carries the reasoning and the sibling entries cite it, each still named for its
own slug. /done sees the grouping from what it already reads — each built
item's queue text, read back one at a time — so items whose text records the
same settlement are the siblings.

**Each item's depth field says which form its entry takes — read it, don't judge
it.** The field is defined at its authoring site, next.md's per-item completion
step, and is slug-bound: `Depth: <slug> — short|full`. Read each built item's
depth line **by its slug** rather than by its position under a tick, and
whatever the run's size — a twelve-item run can still contain the session's most
contested decision.

**Read each item's rule-gate disposition from the working file by its slug too**
— `Rule gate: <slug> — run, …` — for the same reason and in the same pass. The
line /done then writes into the session's LOG entry stays slugless: it
describes the session rather than one item, which is the form
`workshop/resources/rule_signals.py` reads.

**A built slug with no depth line is read as short**, and noted at /done as
a discipline slip rather than passing silently: the field is required, so a
missing one means the build skipped a step, and saying so is what keeps it from
decaying back into an optional line.

**Transcribe each item's tick form into its LOG entry, and announce every
unconfirmed item at /done** [BRIEF]. The tick reads either `done, confirmed`
or `done, UNCONFIRMED: <what still needs running>` (next-build.md). Carry
whichever it says into the entry verbatim — transcribed, not composed — and where any item
is unconfirmed, say so plainly in /done's narration, naming the item and what
has not been run.

**The announcement is required rather than left to judgment.** `done-plan.md`'s
hold-back rule reads this field to decide whether dependent work may clear, so an
entry that omits it silently weakens a safety rule one document away.

**If a `[user]` item's entry was already started**, the walk-through opened it live
and appended as it went (next.md). Continue that file rather than writing a fresh
one — the existing entry is the record, not a duplicate.

**Close each `[user]` item on one of the three outcomes — done, deferred, or not
reached — read off the run's own trail** (done.md's outcome block, and next.md's
walk-through branch, carry the definitions). **On the done arm, remove the item
from Processed with the queue mover**, running first the observable check that
done-plan.md's Completed `[user]` items step names; deferred and not reached
leave the item in place.

If a built item carried a red flag, note in this entry that it carried one and
that it was cleared — the carry-through, since the substantive clearing record was
written at the /plan close that cleared it.

### 2.2 Staleness sweep  [SILENT] when clean; [BRIEF] when flagging

Run done.md's **Staleness sweep**.

### 2.3 Delete the build working file  [SILENT]

Routine bookkeeping — delete the file, no narration. Unlocks future builds. **Only
after everything above is complete.**

### 2.4 Commit  [BRIEF, PROMPT]

Run the commit core in done.md.

## Phase 3: Recommend next  [BRIEF, PROMPT]

Run done.md's **Recommend next** and apply its build delta: the shared
overlap scan + queue-state ladder are the whole recommendation.

**Leave the next run's size to the cleared-to-run line**, in the recommendation
and in the forward advisory alike. That line already *is* the run bound and the
user sets it at /plan; a second, softer cap downstream of it is a guess with no
measurement behind it, since Claude has no gauge of context filling at all.
Where a run genuinely needs to stop early, the no-progress halt is what stops
it — a behaviour-based stop rather than a number.

## Audit delta — for a run's `[audit]` items

Run the phases above and apply this delta, the shape done-plan.md uses. Audits
edit no source files — **the session's product is the captures it appended to
Unprocessed** — and only what follows differs for an `[audit]` item.

**1.1 Verify completion** asks whether every *finding* is ticked — captured or
dropped — in place of every item built. Close partial the same way. An audit
item carries **no** memory-reconcile delta: a finding is ticked when captured or
dropped.

**1.2 Route stragglers.** The findings themselves were appended during the
audit; this step sweeps anything *else* flagged along the way — observations
outside the audit's criteria, process issues — from the same record the build
step sweeps.

**2.1 Write LOG entry** — one per audit item, named after its slug, using
done.md's **Audit** body fields:

```
Files touched       the target artifacts READ — the audit edited nothing
Routed to Captures  findings captured, or "none"
Findings routing    how many were filed as captures, and any dropped on
                    Claude's own re-reading before filing, with the reason
```

**An audit doesn't clear red flags** — clearing happens at processing. A
security, privacy or breach risk this audit surfaces is filed as an ordinary
**uncleared** capture in Unprocessed (`Red flag · State: uncleared`), which a
later /plan clears; note in the entry that the audit surfaced it. An audit item
that itself carries a marker is closed by 1.4 above like any built item.

**2.4 Commit.** No source-file edits are staged because the audit produced none
— the staged paths are the QUEUE.md capture additions, the LOG/ changes, and the
build working file's deletion.

**Phase 3** applies done.md's audit-session delta.
