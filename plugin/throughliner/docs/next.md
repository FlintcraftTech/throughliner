---
name: next
docset: current
note: >
  /next procedure. This is the method's one docset — light, for the 5-series,
  originally authored by subtraction from the now-retired heavy docset.
  Register: structure in typed blocks, everything else in prose, tags inline.
---

# /next procedure

/next is where recorded intent becomes the built thing — the run executes what
the user already agreed, exactly as agreed, which is why it need not stop to
ask. You are building the cleared work from the queue. /next works the Processed
section top-down — building Claude-work items, walking the user through user-work
— scope-locked to the files that work touches.

## What a run is, stated once

**A run clears vetted work without confirming each item, and it does not run to
completion by itself.** Both halves are load-bearing, and the second is the one
this document used to get wrong by calling a run "unattended".

```
TRUE, and what every "do not interrupt this" rule below rests on:
    a run does not confirm each item, and moves faster than a person can
    follow — so stopping it to ask costs far more than the question is worth

FALSE, and no longer claimed anywhere:
    that it finishes on its own. A run pauses at three points and occupies
    the session while it goes:
      - a `[user]` item, walked through live, one step at a time
      - a `[freeform]` item, which halts it outright
      - the close, which is the user's command to run — so a run left alone
        finishes its builds and sits there uncommitted
```

**Say what happens instead of reaching for the shorter word "unattended".**

**"Unattended" stays correct wherever it means "do not interrupt this"**, which is
almost everywhere it appears below. Those uses lean on the true half, so
end-preferred placement, the readiness line as the run's bound, and the
no-blocking-ask rules are all sound and are not reopened.

**A run also occupies the only session there is**, so for as long as it runs the
user cannot capture anything. That is a real cost of the current shape rather than
a wording problem, and it is answered by concurrency work rather than here.

## What /next runs on

**A run reads SPEC, then the queue's cleared region whole** — each item's full
text, its reasoning inline, exactly as it stands in QUEUE.md. Nothing is
generated and nothing is extracted; the file the user reads is the file the run
reads.

**Read the reasoning to aim the work.** It says why the thing is worth building
and what it is for, which is what lets a build get the point right rather than
only the steps. **It is not itself part of what gets built.**

**Reasoning lands in a file this run writes only where that file is the record
of the decision — the session's own LOG entry — or where the item specifically
instructs it.** In every other file the run writes the action the reasoning
justifies, and not the reasoning. That boundary is what the earlier generated
view enforced structurally, by withholding the prose; it is stated here instead,
because withholding it also produced builds that inferred the wrong why.

**The cost is stated rather than hidden:** the run reads the whole cleared
region to build it, and the guard against reasoning reaching shipped documents
is this stated purpose rather than the prose being absent.

**The run does not edit QUEUE.md except to remove each item as it is ticked**
(Step 3), which is unchanged.

QUEUE.md holds two sections: **Unprocessed** (captured, not yet processed)
and **Processed** (agreed, ready). /next builds only from Processed, and only from
above the cleared-to-run marker.

```
run       = Processed[ top .. `--- Cleared to run above this line ---` )
flavor(item):
    (no tag)    ->  build   ->  next-build.md
    [audit]     ->  review  ->  next-audit.md
    [user]      ->  walk the user through it; never built
    [freeform]  ->  HALT — needs a session of its own; never built here
```

**Pick every item from above the marker, and only from there.** This is a
standing rule, not a branch condition — it holds at every step, on every path
through /next.

**A `Runs alone` line on an item is the run's second bound.** Walking the
cleared region top-down:

```
marker on an item, run has already built something
    ->  stop before it. The run ends there.
marker on the run's FIRST item
    ->  build it, then end the run after it.
marker on an item whose observable check finds ALL of it already satisfied
    ->  close the item and continue the run. The bound keys on this run
        performing the work; no paths moved, so there is nothing to protect.
```

Say plainly why the run stopped: this item must not be built alongside other
work, so it gets a run of its own — then recommend /done. Mechanical, no
judgment. It composes with the cleared-to-run line rather than replacing it:
whichever bound comes first ends the run. What the marker means and where it is
written are in plan.md's decision step, which is the authoring site.

The run includes any `[user]` items among the cleared work; Step 3 walks the user
through each *without ending the run*.

## Step 1: Pre-flight

**Whatever these checks surface folds into ONE narration** [BRIEF], carried with
the run at step 4 rather than trickling out check by check.

### 1. Active build check

```
exists(this session's build working file)
                   ->  [BRIEF]   offer to resume; read it for state
otherwise          ->  [SILENT]  no output; continue
```

The build working file holds an interrupted build's progress and remaining work,
so resuming picks up where it stopped instead of starting over.

**It is per session, not per project: `_build-<session-id>.md`.** Check for the
one belonging to *this* session and no other, matching that exact name — a
pattern written for the retired bare `_build.md` matches only the old name and
can never find a current one, which makes the check report "no interrupted
build" every time, silently, forever. A build running in another chat has its
own, and its file list is not this session's scope — a planning run that
read another session's working file used to conclude it was inside that build.

**Before creating any file at the project root, read the untracked list in the
session's opening snapshot.** A file listed there exists but has never been
committed, so git holds no copy and overwriting it destroys the only version.
The editing tool will not stop you: it reports the write as creating a new file,
because from its point of view there was nothing there to protect. This is a
habit, not a rule with machinery behind it.

### 2. Find the run, and read SPEC  [SILENT]

**Read the root SPEC.md once here, at run start** — not per item. It is the
product truth each item is built against, and a build that never reads it cannot
be checked against it. Reading it once per run is what makes the per-item check
below cost almost nothing.

**Per item, read the specs of the parts the item's files sit in.** Where the
project CLAUDE.md carries a `## Parts` block, the run derives each part from the
folders on the item's Files line and reads that part's own `SPEC.md`, in the
part's folder — two parts, two specs; files in no part, the root alone. The
contradiction halt and the filed-gap rule in next-build.md apply to whichever
spec was read.

Then read QUEUE.md's cleared region top-down, each item whole. That is the run.

```
early exits:
    Processed[top] == marker      ->  NOTHING_CLEARED
    an item in the run carries
      `Red flag · State: uncleared` ->  UNCLEARED_FLAG
    Processed[top] is `[freeform]`  ->  FREEFORM_HALT (nothing has started)
    run has no build/[audit] item ->  ALL_WALKTHROUGHS
```

**On NOTHING_CLEARED** [BRIEF] — tell the user the next work isn't cleared to run
yet, recommend /plan to vet it, and stop.

**On UNCLEARED_FLAG** [BRIEF, PROMPT] — stop, leaving the item and the rest of
the run unbuilt. Name the risk in plain English, say the item
reached the ready region with its flag still uncleared, and recommend /plan to
clear it. Then wait.

This should be impossible: a flag is cleared at processing, so an item only
reaches Processed with a cleared flag, and the cleared region is red-flag-safe by
construction. That is exactly why the check is here.

**On FREEFORM_HALT** [BRIEF, PROMPT] — say plainly what the item is and that it
needs a session of its own where the work is done by hand rather than built from
the queue, and stop there rather than skipping to the next item.

A `[freeform]` item is placed at one end of the cleared region rather than the
middle, so the halt is always cheap: met first, nothing has started; met last,
everything else is already finished. When one sits at the *end* of the run, Step 3
builds everything above it and then halts on it, which is the same stop reached
from the other side.

**On ALL_WALKTHROUGHS** [PROMPT] — there's nothing to build, so skip Step 2's
build scaffolding entirely and go straight to Step 3's walk-through branch.

**Before handing any step of a `[user]` item over, run the LIGHT capability
check — per step, not per item.** Name the tool that would do that step and
confirm it is absent or unauthenticated (the over-tag guard,
skill-nonspecific-rules.md). Perform the steps Claude can perform — where a
step's file is outside the run's list, offer the scope addition in the same
message — and hand over only what needs the user's eyes, decision, or hands.
This is the last line of defence
against a wrong tag, and it's nearly free — the run is about to act on that tag.
If the check finds every step is Claude's, do the work as ordinary work and note
the correction for the close; a wrong `[user]` item otherwise stops an unattended
run dead for work nobody needed the user to do.

**Light, not thorough — no reframe, no search, no trying the tool.** The heavy
version belongs at /plan's decision step, where the user is in the room. Here the
user is not, and a run should not stop to explore.

### 3. Open waiting mail  [SILENT] when the mailbox is empty; [BRIEF] when it isn't

Triage anything waiting in this project's `INBOX/` as
`${CLAUDE_PLUGIN_ROOT}/docs/feedback-and-inbox.md` states, before the run is
presented. That ordering is the point: mail can block work, so it is read while
the run can still change rather than after scope is locked.

```
/next OPENS, FILES and DEFERS. It never processes.
    anything a message raises   ->  a capture in Unprocessed
    a message bearing on an     ->  name it at the present-the-run beat and
      item in the cleared           recommend dropping that item FROM THIS
      region                        RUN ONLY. Leave the queue untouched.
```

A reply, where one is owed, is drafted at the close.

### 3b. Cycles due-ness check  [SILENT] when no cycles doc exists; [BRIEF] whenever one does

Run the cycles due-ness check as plan.md's Step 1 states it ("Cycles due-ness
check"), filing only — what to do with the capture stays planning work. It
folds into the pre-flight's single narration like every other check here.

### 4. Present the run and offer the off-ramp  [BRIEF, PROMPT]

Put the run in front of the user and invite a last-glance change **in the same
message** — presenting and offering the off-ramp are one beat, not two.

**Frame the pause as what it is for: a last chance to change scope or reorder**
before /next runs unattended-in-practice. Invoking /next already signalled
readiness, so a permission-to-start question asks for something already given.

```
render(run):                        # full rule: skill-nonspecific-rules.md, view-in-doc
    one-line pointer naming the items, linking to QUEUE.md
```

The pointer is the unprompted default — the token-saving path. The one departure
is the spoken one in skill-nonspecific-rules.md's view-in-doc rendering: where
the user has said they cannot open the file, the text comes into the message.
These items already exist in QUEUE.md, so
confirm the link resolves before sending it.

**Present the whole cleared region.** The cleared-to-run line is the run bound
and the user set it at /plan; a softer cap proposed here — the run looks large,
stop after the first few — is a guess dressed as prudence, because Claude has no
gauge of context filling at all, and a previous session's advisory to that
effect is not inherited either. A run stops early only on observed behaviour —
the no-progress halt — not on a number chosen up front.

**Two things may drop an item from the run, and neither is a cap** [BRIEF]. Both
rest on something specific and checkable rather than on a guess about how large a
run should be. In each case, recommend dropping that item from **this run only** —
the queue is left untouched and /plan decides its fate.

```
1. WAITING MAIL bearing on a cleared item
       a message read at the step above says something about work in this run
       -> name it and recommend dropping that item

2. /setup OUTSTANDING and an item it would overtake
       session_start reports the project's format epoch behind the plugin's,
       or names a document or setting the project is missing, AND an item in
       this run names a file /setup rewrites from a template
       -> name it and recommend dropping that item
```

**The second trigger is a read of the item's Files line, not a judgment about
what counts as plugin-managed content.** Does this item name a file /setup
rewrites? That is all it asks.

**It fires only on that collision, not on every run in a behind project** — a
warning that appears whether or not it applies is one people learn to read past.

**Pointing the user at /setup is safe**: /setup refuses cleanly while a build is
in progress rather than failing file by file against the scope-lock.

Close that same message with the off-ramp, e.g. **"Say go and I'll start — or say
the word to change scope or reorder first."** The affirmative first, the exception
second.

```
user wants a change  ->  route to /plan
user says go         ->  Step 2: lock scope, build begins
```

There is no blocker gate, push marker, or unpark/staleness scan — those belonged
to the old model and are gone. Ordering and readiness are settled in /plan before
work reaches the cleared region.

## Step 2: Lock scope  [SILENT]

**What scope means here — two layers.** The **described work** is the test (its
definition is in skill-nonspecific-rules.md's Scope section); the `Files:` list
below is its mechanical approximation: pre_tool_use allows edits only
to listed files (plus the method docs, the user's memory dir,
`workshop/resources/research/`, the session scratchpad, and any project's `INBOX/`) and
denies the rest, as a backstop. **The two layers are not the same thing** — a build
can stay inside every listed file and still do more than the work describes. The
described work is the test; the `Files:` list is the guardrail.

/next **self-scopes**: it reads the Claude-work items it's about to build and
derives the scope from them. Work outside the described work is appended to
Unprocessed, not folded in.

Once the user confirms:

**1. Self-scope.** Read each Claude-work item whole and list the files its
instructions name. An item that does not say what changes inside the files it
names is underspecified below. `[audit]` items name no files —
an audit reads and reports — so a run of only audit items gets an empty Files
list, locking the session to method docs.

Two situations must not be conflated:

```
you CAN'T tell which files THIS item's       ->  underspecification
    described work would change,                 SURFACE IT. The only case
  OR you can name the files but the item        that halts — building it means
    doesn't say WHAT CHANGES INSIDE THEM         inventing scope the user never
                                                 agreed to.

you CAN scope it, but notice OTHER work      ->  adjacent-work discovery
    worth doing beyond it                        CAPTURE AND CONTINUE on the
                                                 decided scope. Never a blocking
                                                 scope-ask.
```

**A capture filed mid-run also gets one line in the working file's Run-level
section, written at the moment of the write** — it belongs to the run rather
than to any item, so no tick will ever record it, and after a crash the
working file would otherwise say it never happened. A working file from before
this section existed simply lacks it, and the close falls back to memory as it
always did.

**An item is buildable only when it says what changes *inside* the files it
names.** The same two-limb test runs at /plan's decision step, which carries the full
argument and is where an item like this should be stopped; meeting one here means
it got through.

**Both limbs halt.** A design question about the item in hand — "how should this
behave?" — is neither a question about which files change nor other work: **that
question IS underspecification** — the item did not say how — and it routes
through the mechanism that already exists rather than through a design-question
branch.

*Worked example, second limb.* An item names `plan.md` and says its ordering rule
should be "improved" without saying what the new rule is. The files are perfectly
clear and the item is still unbuildable — halt as underspecified rather than
choosing a rule the user never agreed.

*Worked example.* Building a terminology rename, self-scoping enumerates the docs
the item names. A doc silent on which sections change → underspecification,
surface it. Noticing the *hooks* also carry the old term when the item didn't
list them → adjacent-work discovery, capture it and continue.

**2. Create this session's build working file** — `_build-<session-id>.md`, in
the project root:

````markdown
# Active Build

Run: [flavor + slug of each Claude-work item, top-down]

Entries:
[One line per Claude-work item: its flavor tag (or "build"), its slug, and its
description. Rationale is NOT copied — it lives in QUEUE.md under that slug and is
read from there.]

Index entry candidates:
[empty — one added as each item is ticked]

Run-level:
[writes belonging to the run rather than to any item — a capture filed
mid-run, a LOG record opened live for a walkthrough — one line each, written
at the moment of the write]

Files:
- [each file the run's items will change — one bare path per line, nothing else]

Progress:
[empty — ticked as each item completes]

Changes:
[empty — accumulated as each item completes]
````

The `Files:` section feeds the scope-lock: pre_tool_use allows edits only to
those files plus the method docs, and denies everything else. **Lines must be
bare paths** — the hook matches each line as an exact path, so any annotation
becomes part of the path and silently breaks the match. Make sure no other line
in the file starts with `Files:`.

**Rationale is not copied here.** Each item's reasoning stays in QUEUE.md, which
is where the run reads it and where the close reads it back. Copying it into the
working file would put a second copy in a file scheduled for deletion. **The
safety that governs this is step 3 below** — each item stays in QUEUE.md until
the moment it is ticked, so no item's only copy ever sits in that file. **If
that copy-per-item ordering is ever changed, this must be revisited with it.**

**3. Leave QUEUE.md alone. Copy, never cut.**

```
Claude-work items  ->  COPIED into the build working file, and they STAY in QUEUE.md
[user] items       ->  STAY in QUEUE.md
```

Nothing is removed from QUEUE.md here. Each Claude-work item is removed **one at
a time**, at the moment it is ticked in the working file's Progress (Step 3) — so the queue
visibly shrinks as the run progresses, and an item still showing in QUEUE.md means
exactly one thing: not built yet.

A `[user]` item is walked through in Step 3, not built, and is closed later by
/done or /plan. It never enters the build working file, since the build working file is deleted at close.

**4. Narrate the lock** [BRIEF] — one sentence, in user-facing terms: the build working file is
the build's working file — it carries a copy of the run's work, lists the files the
safety check allows, tracks progress so an interrupted session can resume, and
holds the reasoning /done writes into the session record. The queue keeps its own
copy of everything not yet built, and each item drops out of it as it's finished.

```
progress format:
    build item  ->  - [x] item description — done, confirmed
                    - [x] item description — done, UNCONFIRMED: <what still
                          needs running>
    audit item  ->  - [x] Finding description — captured | dropped
```

The confirmed/UNCONFIRMED wording belongs to next-build.md's per-item completion
step, which says how to choose between the two forms; this block shows the shape
so a run writing the file has the correct specimen in front of it.

The build working file is the crash-recovery mechanism: if the session dies, the
session that resumes sees it and picks up from it. A working file left by a
session that never came back is surfaced at session start as a leftover — never
deleted, because it may hold the only record of what that session did.

## Step 3: Work the run

**Build every Claude-work item that depends on no `[user]` item first; then, in
queue order, walk each `[user]` item whose prose names builds by slug and build
the ones it names; then walk the `[user]` items naming nothing.** A build named
by a `[user]` item is skipped in the first pass and built after its walk. The
dependency is read from the `[user]` item's own prose — the known-ordering rule
already writes it there by slug — and nothing new is written on the item. This
is what lets a `[user]` item be walked through without terminating the run.

```
build item (no tag)  ->  read and follow next-build.md
[audit] item         ->  read and follow next-audit.md
```

Between build items, keep going autonomously — the user confirmed the whole run
at the Step 1 off-ramp, so there's no per-item re-confirmation.

**As each item completes, make four writes in the working file, then remove the
item:** tick it in Progress, record that item's depth field, write that item's
index-entry candidate, and write that item's `Changes:` entry — the files it
touched, one line each — then remove that one item from QUEUE.md with the
mechanical mover, addressed by its slug.

**Where the project's own instructions require a rule-gate disposition and the
item carries one, copy it across unchanged, keyed by slug like the depth field
beside it:**

```
Rule gate: <slug> — run, <what it decided>
Rule gate: <slug> — not needed, <why>
```

Where
the item is about to author or amend a standing rule and carries no disposition,
halt and say so: the gate's site is planning, and a disposition written now could
only describe what is already built.

**The slug binds this line to its item too**, for the reason the depth field
gives below: a bare positional line attaches to whichever tick it happens to sit
under, and a later tick written above it silently takes it. The LOG-entry
`Rule gate:` format is unchanged and stays slugless — that line describes the
session, not one item, and `workshop/resources/rule_signals.py` reads it as it is.

**The tick is the accumulation point for per-item writes.** `Progress:`,
`Index entry candidates:`
and `Changes:` all grow one item at a time, at the tick and never later, so the
working file only ever describes work that actually happened. The `Run-level:`
section is the one exception, written at the moment of its write rather than
at any tick, because what it records belongs to no item. The index candidate is artifact touched +
nature of change (skill-nonspecific-rules.md, Index entries), and written here it
*describes* the build rather than predicting it.

**The depth field is required, not optional, and it is written here rather than
loosely during the build.** One line per ticked item, under the Progress tick:

```
Depth: <slug> — short
Depth: <slug> — full, <which trigger: reasoning contested | alternative seriously weighed>
```

**The slug binds the line to its item.** A bare positional `Depth:` line attaches
to whichever tick it happens to sit under, so two written together silently
attach to the wrong items; the slug makes each line self-identifying, and the
close reads it by slug rather than by position.

Writing the field at the tick turns a silent omission into a visible one, which
is the required-artifact shape this method already trusts for the rule-gate
line.

```
python <plugin-root>/scripts/reorder_queue.py <QUEUE.md path> \
    --delete <slug> Processed
```

Where the project's state server is registered, make the four writes and the
removal with its `build_tick` tool, which writes the lines in the shapes above,
refuses a missing verdict, a full depth with no trigger or a gate line the item
does not carry, and removes the item in the same call.

Tick first, then remove. That order means an interruption between the two leaves
the item in both files, which a resume can see and settle — the reverse order
would leave it in neither.

### The `[user]` walk-through lifecycle

How a `[user]` item is run and closed. (What earns the tag is the matched pair in
skill-nonspecific-rules.md, Captures; the record check before walking — read any
LOG records under the item's slug and resume after what they show done — is that
file's lifecycle bullet.) Without the back half, a finished `[user]`
item strands in Processed and the next /next presents it again as if unbuilt.

- **/next leads with the walk-through and drives it live.** Name what's theirs to
  do, run whatever parts you can, give the **first** concrete step, and **wait**.
  One step at a time. This is a live drive, not an offer — you walk *beside* the
  user, you don't step back and hand off.
- **The close is named only after the walk-through finishes.** How completion gets
  recorded is told to the user *after* the last step is done or they defer.
- **One `[user]` item at a time**, each in its own message, led by its own live
  walk-through. Not a bulk-approval result set.
- **Completion is read as the always-loaded lifecycle states** —
  skill-nonspecific-rules.md's "Walk a `[user]` item through whenever it is
  reached" bullet; an item whose blocker visibly hasn't shipped is not complete.
- **A completed `[user]` item has a defined close:** log it under its slug and
  remove it from Processed. Lives in **both** /done (the user runs /done right
  after finishing) and /plan (they completed it async and mention it).
- **Re-clearing dependents** is the below-the-line revisit's job, not the close's.

### Walk-through branch — the `[user]` items  [SEQUENCE, PROMPT]

Once the Claude-work is built (or if the run had none), walk the user through each
`[user]` item still in the cleared region. **The steps come from the item's own
walkthrough in QUEUE.md**; where an item carries none, halt on it rather than
inventing steps. Walking one through does **not** end
the run — it's the last pass of a run whose Claude work is already done.

**Open the item's record, add the item's files to the run's scope, then give the
first concrete step and wait.** The record comes first: open the item's LOG
entry file under its slug when the drive starts, and append each action as it
happens — a reinstall run, a version bumped, a cache pruned. **Before the first
step is driven, append every path on the item's Files line to the working
file's Files section, and say so in one clause.** **Write one line in the
working file's Run-level section when the record is opened.** The item itself
stays in QUEUE.md untouched, so nothing is stranded, and a crash mid-walk-through
leaves a partial entry saying exactly what was done. The close then finds an
entry already started rather than writing one fresh.

**Present every `[user]` item the pass reaches.** No item is set aside before it
has had its own turn, and nothing is filtered out of the pass in advance on a
judgment about whether its moment has come.

**Test a precondition inside the item's own drive, never as an outside filter.**
Where a drive's first step cannot proceed — the thing it needs isn't there, the
build it assumes hasn't shipped — say so on that item's turn, in plain words,
and let the user's answer settle it. That keeps the decision in front of the
person who owns it, at the moment the item is actually in view.

**A precondition field the run could evaluate mechanically is refused**: it
recreates the outside filter with a schema, and this decision belongs in front
of the user rather than in a check.

**A step requiring action in another project is filed as a capture, never
driven.** No session writes another project's files, and walking the user out of
this project to do something in that one is where a drive stalls. File it,
continue the walk-through, and let the receiving project pick it up with its own
hands.

**One item at a time**, each in its own message, led by its own walk-through. Finish one fully — or record that the user deferred it — before
moving to the next. (This is *not* the [SEQUENCE] bulk-approval inversion: that's
for a deterministic result set the user reads and accepts in one pass. A
walk-through is an action driven live.)

**Where the item's record shows it was handed over for completion after a close
and names no observable this run can reach, replace the drive with the one
ask** — where did that land? Both facts together, read off the record, and one
ask rather than a walk-through of steps the user may already have finished days
ago. The carve-out and its reasoning are in skill-nonspecific-rules.md's
`[user]` lifecycle; this is where it fires.

This is a place to record, not a restriction on doing. The branch is *supposed*
to run whatever parts Claude can — that is what makes it a live drive. The record
goes to `LOG/` precisely because `LOG/` is writable whatever the scope-lock says,
so recording can never be what blocks the walk-through.

**Lead with the walk-through, and drive it live — one step, then wait.** Run
whatever parts you can, give the **first** concrete step the item records, and
**stop and wait** for the user to report back. Then the next step, and so on —
walking beside them, not dumping a list for them to work alone.

**What a step turn carries.** Where the step's reasoning is already agreed and on
the record, the step is the ask alone — what to do and what to look for, in the
standard ask shape. Full reasoning appears only for something not yet agreed.

```
reasoning agreed and recorded   ->  the ask alone
not yet agreed                  ->  the reasoning, then the ask
```

A step that restates why the work is being done hands the user a paragraph to
read past before they can find the instruction.

Open with the first step itself, and satisfy this branch only by driving the
steps — an offer to walk the user through it, or a statement that the item stays
open until they have done it, leaves the branch unrun.

**Every `[user]` item the run touched ends on a recorded outcome, and the record
carries which. Three named values cover the ordinary cases; where none of them
fits, the record says what actually happened in one plain sentence:**

```
done          walked to its end this session, or the user said they did it, or
              its walkthrough named an observable check and that check passed
deferred      the USER said to leave it — their word, never inferred
not reached   the run never presented it, or presented it and got no answer
anything else what actually happened, in one plain sentence, with the detail in
              the item's own record — "halted mid-drive: its walkthrough says to
              post into the existing topic, and re-homing needs a new one",
              "driven to the end of Claude's part; the final step is the user's"
```

**Write `deferred` only from the user's own word — given about that item, or
about the set it belongs to, with each item recorded separately and the word
quoted.** An item nobody put in front of them, and about which no word was
given, was not deferred by anyone; recording it that way tells the next session
a decision was made when none was, and the item then sits unpresented with a
record that explains why nobody need present it.

**`not reached` tells the next session to present the item fresh**, with no
deferral to honour and nothing to resume from.

**Where the user volunteers that an item is done, take them at their word:** skip
the walk-through and recommend /done to record it.

**Where the item's walkthrough names an observable check, run it**, and report
a failed one as what was found, leaving the item in place.

**Confirm the step can produce the observation the item names** — the light
form: check that the step names something which yields the evidence, and no
more. No experiment, no search, no stopping. (The heavy version, where the
command is actually run, belongs at /plan's decision step, where the walkthrough is
authored and the user is in the room.)

**A step that names a file for a stated property has that file checked against
the property before the step is given**; where the file no longer has it, the
step goes out with the property and no file, and the user picks one.

**Run the hand-over checkpoint before a step goes out** — the three-question
read-back in skill-nonspecific-rules.md: the words, whether a tool could do it
instead, and whether every file named is linked. The user is about to act on
these words with nobody to ask.

**Verify any command before handing it over to be pasted.** Run it where doing
so is safe — a scratch fixture — or read the tool's `--help`. The scope is
narrow on purpose: a command *Claude* runs with a wrong flag costs one turn and
self-corrects. The cost only lands when the command goes into a block for the
user to run: they are a no-code developer, they cannot tell a typo from a broken tool,
and the failure arrives in their hands rather than yours.

**Say nothing about /done until the walk-through is complete** — while driving
the steps, keep the close, "handing over" and recording out of the conversation
entirely.

**Once an item's walk-through is complete (or deferred), name its close.** A
`[user]` item stays in the queue for a later session, so it won't record or remove
itself:

```
run /done                ->  logs it under its slug, removes it from the queue
raise it at the next /plan  ->  if the user would rather mention it there
```

When every `[user]` item has been walked through or deferred, tell the user the
whole run is complete — Claude-work built, user steps addressed — and recommend
running the rescan first, to catch anything decided but never written down, then
/done.

**Copy discipline when the run is all `[user]` items.** Open with the item
itself: say plainly that the next ready item is a step for the user to run, say
why it's theirs, and start walking them through it. The silent active-build
check stays silent, and "there's nothing for me to build" stays unsaid — /next
helps either way.

## Ending before scope-lock

Any run end before Step 2 locks scope — a soft-stop at the marker, the user
calling it off:

**1. Route any reshape direction to Unprocessed** [PROMPT]. The trigger is
mechanical: *run ending + no scope locked + a reshape direction or learning
the queue needs in conversation = capture needed.* Append it naming the item's
slug; write it, then report what was filed. Unrouted, the direction survives only
in the LOG entry, which /plan doesn't read at planning time, so the work
re-presents unchanged at the next /next. Nothing reshape-shaped in conversation →
skip, no output.

**2. Name /done as the next step** [BRIEF]. Whatever the session did before
stopping gets recorded and committed only by /done. Other recommendations (run
/plan to vet the next work) ride alongside naming /done, which always happens.

No item returns to the queue, because none left it — scope was never locked.

## Resuming

When resuming an active build, read its working file for state rather than
re-exploring.

