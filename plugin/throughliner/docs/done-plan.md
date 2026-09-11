---
name: done-plan
docset: current
note: >
  Close-out for every no-build session. Reached from done.md's router when no
  build working file exists — /plan sessions, /setup sessions, method-doc-only
  sessions, a completed [user] item, and standalone handmade work.
---

# No-build close-out

Reached whenever there is no build working file. Three shapes arrive here and
they overlap freely — a planning session can also close a completed `[user]`
item, and either can carry hand edits.

```
queue managed, captures processed, readiness line moved, or a planning
    working file exists          ->  run every step below
a completed [user] item          ->  the Completed [user] items step, plus the
                                     LOG entry, commit and recommendation
the user made ad-hoc hand edits  ->  the Standalone handmade-work steps, plus
                                     the same three
```

The reorder, the marker placement and the `[user]`-placement step reach every
plan-type close — a /plan session, a /setup session, and a session that changed
only the method docs; none is /plan-only.

## Spec-sync gate  [SILENT] in sync; [PROMPT] on drift

**This is the only /done run that syncs SPEC.** A build session's /done runs a *check-against*
instead (done-build.md) — it reads what was built against SPEC and reports a
contradiction rather than editing SPEC to match. Audits land no product changes,
so an audit session's /done has neither.

**Read what the session changed, not what it remembers — two reads, stated as
commands:**

```
git diff HEAD -- SPEC.md '**/SPEC.md'   # every SPEC sentence written or changed
                                        # this session, in the root spec and in
                                        # every part's spec
git diff HEAD -- QUEUE.md               # every item kept or reshaped this session
```

In a nested project run the first read in the inner repository too. For every
SPEC sentence the first diff shows
written or changed, read the queue
item it was written for **as that item now stands**, and where the two have come
apart, correct the sentence. For every kept item the second diff shows, read its
final text for a product-truth change that has no sentence, applying the
spec-entry trigger test **in plan.md's own wording** — quote it from there rather
than keeping a copy here — and write the sentence
under the drift branch below. Where SPEC.md or QUEUE.md is gitignored, the diff
falls to the copy the safety check keeps in the project's snapshot folder, read
against the file as it stands.

If either read finds drift, **stop /done before committing.** Surface the drift in plain
words, naming which SPEC sentence the session made wrong, get approval to fix it,
then edit SPEC and commit it **in this same commit** rather than filing it as a
capture for a later session.

No scope-lock is active at any /done run reaching this doc, so edit SPEC.md directly
in-session. Editing SPEC to match a decision the user already made this session is
RECORDING, not re-planning. That covers all three shapes alike.

**The gate checks that every decision this session made had its SPEC sentence
written at the decision step, and that the sentence still matches the item at
/done.** By the time /done runs, the sentence either exists
or was missed, or was written correctly and made wrong when the same session
later reshaped its item; the two diffs are what catch both.

**A SPEC sentence describing decided-but-unbuilt behaviour is the designed lead,
not drift.** SPEC is read at build time, which is what requires it to lead: the
build is checked against the sentence, so the sentence has to be there first.
The lead is bounded by the cleared item that builds it — the sentence and the
work sit in the queue together, and the gap closes when that item runs.

A session that changed only queue ordering or captures touched no SPEC sentence
and passes silently.

## Standalone handmade-work close  [BRIEF, PROMPT]

Runs only where the user made ad-hoc edits by hand and wants them recorded.
**Runs on request only:** hand edits left uncommitted are simply swept into the
next /done that runs. This exists for when the user wants them logged and
committed as their own clean record.

**1. Read the edits as the user's own expected work.** Uncommitted changes
the session didn't make are most likely the user's expected work. Run `git status
--porcelain`, and where what changed isn't self-evident, look. Confirm with the
user that these are theirs and meant to be saved. **Read them as expected work
rather than a broken repo, and leave them intact.** Where a scope file
(`_freeform-<session-id>.md`) is present at /done with no queue item behind
it, read it as the record of what the user directed through the scope-lock's
door, and name those paths in the entry. **Read the door's uses from the safety
check's own log rather than from the scope file alone:** `.throughliner/pre-tool-use.log`
holds one line per decision, and every line whose branch reads `freeform scope
file` and whose last column is this session's id is a path the door admitted.
Name each such path in the entry under handmade work, one line per path; where
the log holds none, say nothing.

**2. Decide LOG granularity by judgment.**

```
one coherent change     ->  a single entry: LOG/<YYYY-MM-DD>-handmade.md
                            (-2 if the name is taken)
several distinct        ->  a separate entry per logical change
logical changes             # better recall than one lumped entry
```

Write each entry's one-liner and rationale, then **report what landed.**

**3. Stage the hand-edited files explicitly** at the commit step. The commit
message is the approved entry; for several entries, the title names the
handmade-work close and the body carries each entry's summary. Unlike a planning
close, a handmade /done run **does** offer push when a remote exists — it's real
project work, not bookkeeping.

## Batch the human stops in Processed  [SILENT] when nothing moves; [BRIEF] when it does

**One pass, over Processed only: put `[user]` and `[audit]` lines at the end,
and a `[co-write]` line after them.** That is the whole of /done's reordering.

**`Blocks:` / `Depends on:` headers stay retired.** The one dependency
field that exists is `Blocked by:`, written on the item that is held and naming
one or more slugs — the item lifts only when every one of them resolves — and
it is lint-checked precisely so it can't go stale the way those headers did.
Its sibling `Not before: YYYY-MM-DD` holds an item until a date rather than
until another item, and is lint-checked the same way. Everything else stays
prose slug-references.

**Place `[user]` and `[audit]` lines end-preferred**, after contiguous blocks of
build work. Both flavors force /next to stop for the user — a step they must run,
an audit whose findings they must approve — so one sitting *inside* a contiguous
build run interrupts a sequence that would otherwise never stop to ask. Position
them at the **end** of the block so the stops that need the user batch together.
A `[co-write]` line goes after both, unless a build is held on it by slug.

**Two exceptions, and the default holds everywhere else:**

- leave a `[user]` item that names, by slug, the builds depending on it ahead of
  those builds — a build run walks it before building them, and every other
  build first;
- leave an `[audit]` that reads a tool item's output sitting immediately after
  that item.

The second dependency runs the other way from the first — the audit depends on
the build — and it carries no `Blocked by:` line, because placement is what
orders the pair. Moving the audit to the end separates it from the tool it runs,
and /done happens after /next, so the separation arrives in time to break the
*next* run rather than this one.

Order here is low-stakes and reversible, so the narration is the catch-point
where the user can redirect.

**Use the mechanical mover, passing it the desired order and nothing else** —
only the *decision* passes through you; the prose stays in the file.

```
locate:  scripts/reorder_queue.py under the PLUGIN ROOT

invoke:  python <plugin-root>/scripts/reorder_queue.py <QUEUE.md path> \
             <Processed|Unprocessed> <slug1> <slug2> …
         # give the section's full desired top-to-bottom slug order
         # for Processed, place the marker with:
         #     --marker-after <slug|TOP|BOTTOM>
         # omit it to keep the marker where it currently sits

trust the self-check:  exits non-zero -> NOTHING was written. A slug-set
                       mismatch usually means the queue changed under you —
                       re-read it, rebuild the order, re-run.
```

```
narration scales:
    changes what /next would pick next  ->  flag it clearly
        "Moved 'Rewrite the welcome email' [welcome-email-rewrite] above
         'Add a plan picker' [plan-picker], so the email lands first —
         say if not."
    a trivial tidy (no pick-order change)  ->  one line
    no reorder needed                      ->  say nothing
```

## Position the cleared-to-run line  [SILENT] when unchanged; [BRIEF] when it moves

Walk Processed top-down and put the `--- Cleared to run above this line ---`
marker just below the last item the user has agreed is ready to build.

```
every processed item greenlit  ->  the line goes at the BOTTOM of Processed
none greenlit                  ->  at the TOP
setup / method-doc-only session with no processed work
                               ->  no line to place, nothing to reorder.
                                   Say nothing.
```

Narrate where it lands **only when it actually moves** — one plain line:
"Everything processed this session is cleared to run; the line sits at the
bottom." When your walk confirms it's already correct, confirm silently.

**Hold back an item that depends on unverified work.** A processed item must not be
cleared if it depends — by a slug reference in its prose — on another item that has
been **built but whose verification is still pending** (a host-side item shipped
but not confirmed live after reinstall, or an observed check simply not run yet).

```
dependency BUILT only            ->  NOT enough. Keep the dependent below.
dependency BUILT and VERIFIED    ->  no hold; it may clear.
```

**Except where the held item is itself the only verification of its blocker.**
There the hold is not written: the item clears, its walkthrough IS the
verification, and its prose says so.

The deadlock without it, from a consumer project that met it: a build produced a
script whose first real run happens inside a `[user]` walkthrough, so the blocker
could not resolve until the held item ran, and the held item could not run until
the blocker resolved. Two mechanisms both reported it as fine by construction —
the digest reads an absent-and-built blocker as resolved, and the loop check
covers only blockers that are queue items, while this loop runs through a
verification. It surfaced only because someone read the record behind the slug
by hand.

Restatement was attempted first and lost content: rewording the rule to hold only
unattended work would also clear attended walkthroughs that do not verify their
foundation, which is a hold the rule genuinely wants. A walkthrough is driven
live with the user present, so a failure here is seen as it happens.

Narrate it when it holds an item back — one line naming which item waits on
which.

**Re-derive prerequisite state from LOG, not from memory, by reading the
dependency entry's transcribed tick.** Every built item's entry carries either
`done, confirmed` or `done, UNCONFIRMED: <what still needs running>`, written into
the build working file at the moment the work happened and copied into the entry
at /done (next-build.md, done-build.md). Read that field. This rule and the
`[user]`-placement rule below both depend on the answer, and a fresh short session
has no memory to fall back on.

**Read the field rather than inferring the answer from the entry's prose.** An
entry with no such field predates the mechanism — treat it as unconfirmed and say
so, rather than reading its prose for a claim it may never make.

**Name the holding fact when placing any item below the marker.** One line in
the item's block, whichever holds it:

```
Blocked by: [slug]
Blocked by: [slug], [slug]      # a group: lifts only when ALL resolve
Not before: YYYY-MM-DD
```

Every slug must resolve to a real work item in this queue, and a date must be a
real `YYYY-MM-DD` — the queue lint checks both. Below the line means held by a named
queue item or by a date, and nothing else.

```
a date is what it waits for      ->  write the date. No blocker item: the date
                                     resolves itself, so nobody confirms it
nothing holds it                 ->  it goes ABOVE the marker, not below
it waits on something else in    ->  file that as its own item in Unprocessed
    the world (a restart, a          first, then name it here. /plan will
    reply, a site going live)        process it like any other work.
you can't yet say what it        ->  Unprocessed — it still needs thought
    would build
```

**Place ready `[user]` walk-through work above the marker.** The marker is the
single gate for walk-throughs as well as builds — /next walks a `[user]` item
through only when it sits above the marker.

```
prerequisite work shipped (built, and verified where a live check was needed)
    ->  place the [user] item ABOVE the marker
prerequisite still pending
    ->  it stays BELOW, exactly like any other not-yet-ready item
```

**Being a `[user]` item is not a reason to shelve it** — only a pending
prerequisite keeps it below the marker. This lives in the /plan close rather than
/next so the marker stays one positional gate, instead of /next growing a second
readiness check of its own. Narrate it when a `[user]` item moves above the marker
— one line naming which is now ready.

## Completed `[user]` items  [SILENT] when none; [BRIEF] when closing one

A `[user]` item never entered a build working file, so it isn't ticked and closed
like a build. This is /done that records it and removes it from Processed, so
a finished item doesn't strand in the queue and get re-presented by the next
/next. It runs as a /done run of its own, inside a planning session's /done, and — for the
removal — inside a build session's /done.

**Completion is read as the always-loaded `[user]` lifecycle states**
(skill-nonspecific-rules.md, "Walk a `[user]` item through whenever it is
reached"); anything else stays in Processed, silently. Where the item's
walkthrough names an observable check, **run it before recording completion**,
and report a failed one as what was found, leaving the item in place.

```
1. take the completed item(s) from what the session can see  [SILENT]
   # don't list the other [user] items still sitting in Processed — an item
   # whose completion isn't visible simply stays where it is
2. write a LOG entry per completed item, named after its slug
   # records what the user did and its outcome; write it, then report it
   # if it carried a red-flag marker -> carry the cleared flag into the entry;
   # a marker still reading uncleared is the impossible case — stop and surface it
3. remove each completed item from Processed
   # this is what stops it being re-presented
```

Fold each entry into this session's records alongside any planning entry, and its
slug into the commit. When nothing was mentioned and nothing was walked through,
say nothing. A remote-gated push offer applies as normal — a completed `[user]`
item is real project progress, not bookkeeping.

## 1. Write LOG entry  [DISCUSS, PROMPT]

Follow done.md's **LOG entry files** section, using its **Plan / setup** body
fields (`Queue changes`; `Work processed`). Planning sessions carry no
index-entry candidate — author the index entry fresh.

If a red flag was cleared this session, record **how** in the session's LOG
entry. Clearing happens at processing, so /plan is where this record is written
— /done **records** and does not re-decide:

```
designed out / fixed  ->  how the risk was removed
consciously accepted  ->  the informed-consent trail: what the user was warned
                          about, and that they chose to proceed
```

The LOG is where the how-it-cleared lives; the marker on the work item carries
only `State: cleared`. **Recording is unconditional once a flag clears** — the
record lands in the LOG, because chat and the marker are the only other homes
and no later session re-reads either for clearing history.

**Read what this session did off the queue itself, not off memory:**

```
git diff HEAD -- QUEUE.md
```

That is the mechanical record — every item kept, every item deleted, and the
reasoning written into each one as it was processed — so the entry's Queue
changes and Work processed lines are filled from the artifact rather than
reconstructed.

**Skipped items are the one thing the diff cannot see, and they are deliberately
not recorded anywhere.** Skipping moves nothing and edits nothing, so it leaves no
trace; a skipped item simply returns next session, and no file is reintroduced to
hold them.

## 2. Commit  [BRIEF, PROMPT]

Run the commit core in done.md. Staged paths are the changed method docs
(QUEUE.md, SPEC.md, LOG/), plus the hand-edited files where this was a handmade
close — planning sessions touch nothing else.

**The push offer differs by which shape closed, so decide it before running the
core:**

```
planning / setup / method-doc-only  ->  commit, and DON'T offer push. Planning
                                        state is local bookkeeping, and push is
                                        reserved for shipping — in a
                                        self-hosting project a push fires the
                                        full checklist off a commit that shipped
                                        nothing. A default, not a prohibition:
                                        push stays available when the user asks
                                        or is deliberately backing up.
completed [user] item / handmade    ->  offer push as the commit core does.
                                        Both are real project progress.
```

**An isolated session names its branch and warns about "remove"** [BRIEF].
Fires only where session_start reported this session is in its own worktree; in
a shared tree, say nothing. After committing, say plainly which branch the work
is on and that **it is not merged back** — the harness never merges a session
worktree, and choosing **remove** at exit deletes the worktree and the branch
with all the work in them. Use that word, because it is the word the exit prompt
uses and a user reads it as tidying up.

**Leave the merge to a main-checkout session's start**, where session_start
reports worktrees carrying unmerged commits — git refuses to update a branch
checked out in another working tree. Say that too, so the user knows the work
has somewhere to go. (The always-loaded rules carry this same instruction for
every session shape, so a build or audit session's /done in a worktree is covered there.)

## 3. Recommend next  [BRIEF, PROMPT]

Run done.md's **Recommend next** and apply its **Plan / setup close** delta: a
fresh setup session whose only work item is the rough first build item recommends
/plan to scope it rather than /next; otherwise the shared overlap scan + ladder
apply.
