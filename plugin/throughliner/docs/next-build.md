---
name: next-build
docset: current
note: Execution procedure for build-flavor work items. Reached from next.md.
---

# Build procedure

next.md routes here for each build item (a work item with no flavor tag).

## Execute  [SILENT]

The silence governs the **success path** — making changes and ticking the item
when things go fine. It is not a gag on the moments that must speak: reporting a
failure, asking before scope grows, and revealing a readable edit's new text all
speak. A tag on one of those overrides this step's silence.

**Make the edit, then say what changed.** The work was already agreed in /plan,
so an edit goes straight in — no point-form list of what you are about to change
before it lands. Holds for every edit, readable or code.

**Readable edits reveal their new text** — informational, not an ask.

```
readable content (a doc, copy, a spec section — anything a person READS)
    ->  surface the actual new wording AFTER the edit
    ->  no approval ask; the change was already agreed in /plan

code
    ->  no reveal. A no-code developer can't review code text the same way.
    ->  success path stays silent (still no preview)
```

**How the reveal renders** follows the view-in-doc rule (skill-nonspecific-rules.md). The
text is now doc-resident, so: a plain link to the edited file with the line named
in the prose ("around line 40"), falling
back to an inline excerpt if the link won't resolve. Either
way, only after the write is confirmed.

Note what this is not: showing an edit is **visibility**, not approval. The item
was already agreed at /plan and stop is always available, so displaying an edit
waits on nothing and the run stays unattended. Show-before-write is the thing
that gates, and it is a separate switch in the rules file.

**A small mid-build tweak to a just-surfaced readable edit is in scope**
[PROMPT]. Once the new text is visible the user may ask to change one bit. That
refines the build's already-agreed work product, so: make it, reveal the updated
text, and record it in the build working file Changes so it folds into the LOG entry /done
writes. No separately logged object, no /plan round-trip. A request that's
actually new scope — a different feature, or a change to something that already
worked — routes out via Scope management below.

## Build the item

**What this item's instructions are.** The item's own text in QUEUE.md, read
whole: which files change, what changes inside them, the observation that shows
it landed, and any option already refused. An item that does not say what
changes inside the files it names is underspecified and halts, per next.md's
self-scoping step.

**Read the item's reasoning to aim the work, and write the action rather than
the reasoning.** Why the work is worth doing tells you what the change is for;
it belongs in what this session records, not in the documents this session
edits — unless the item specifically instructs otherwise. next.md's opening
carries the full statement.

**Treat a recorded refusal as settled.** It names an option already rejected and
why it lost. Proposing it again, or stopping to ask about it, is the interruption
the record exists to prevent.

**Check the work against what the item says would show it landed before
ticking**, and let that decide which
of the two tick forms is true.

```
1. read relevant existing code or context
2. make the changes                        # no point-form preview first
3. if readable content -> reveal the new text (informational, no ask)
   if code             -> stay silent
4. check what was built against SPEC       # SILENT unless it contradicts
5. tick it, in whichever of the two forms is true (see below)
```

**The tick takes two forms, and choosing between them is not optional.**

```
built AND confirmed      ->  - [x] item description — done, confirmed
                             # something ran and passed: a suite, a command, a
                             # read-back, an inspection of the output

built, NOT confirmed     ->  - [x] item description — done, UNCONFIRMED:
                                   <what still needs running>
                             # name the check, the command, or the observation
                             # nobody has made yet
```

**Step 4 checks the work against SPEC and leaves SPEC unedited.** SPEC was read
once at run start (next.md's pre-flight), so this costs almost nothing. **Silent
unless it finds something** — an unattended run narrates no passing check.

```
built work agrees with SPEC        ->  say nothing, tick, continue
built work CONTRADICTS SPEC        ->  [PROMPT] stop and name which SPEC sentence
                                       it contradicts, in plain words. The user
                                       decides whether the build is wrong or
                                       SPEC is.
build establishes NEW product      ->  FILE the sentence SPEC owes as a capture
  truth SPEC doesn't yet carry         and carry on. Never edit SPEC — see the
                                       scope-grow section below.
```

**A check Claude can run is part of building, not a separate test.** Run whatever
verification you can — read the code back, run a command, inspect output, check
file content — as part of getting the item right.

**Read a check's exit status from the tool itself — a bare invocation, or the
tool's own status captured explicitly — and trim its output separately.** A piped
command reports the last stage's status and not the tool's, so a compiler that
failed into a `head` that succeeded reports a pass.

```
a check Claude CAN run   ->  just building
a check needing the user ->  a [user] capture, which /plan would have kept as
                             its own item; /next walks the user through it
a check Claude can run   ->  it stays OUTSTANDING in the run's working file.
  but a circumstance of      Retry it before /done; if the circumstance
  the moment blocks          still hasn't cleared, /done files it as a
  (the app must be on        capture. No new state, no new tag.
  screen and stealing
  focus would interrupt
  the user)
```

If mid-build you discover the work needs a user-run check that isn't already a
`[user]` item, route it (see Course-correction) rather than inventing a deferral
here.

## File structure — split by independent unit

**Fires only when the build creates or grows the project's files and there's a
genuine choice about how to split the work across them.** A build that only edits
existing files raises no such choice, so it gets no file-structure recommendation.
When it does fire, this is guidance you offer, not a hard rule — file structure
stays case-by-case.

```
genuinely independent unit        ->  split into its own file
    (a self-contained tool, a standalone path through the app)
content reasoned across as one    ->  keep together, even when large
    connected whole
```

Splitting pays off **because the AI does the editing**: an edit's blast radius is
one file, the AI reasons over less at once, and a mistake is contained by the file
boundary. That contained blast radius is what makes it worth the cost.

The counter-force that bounds it: an AI reasons *less* well across files than
within one. So closely interdependent logic that's constantly reasoned about
together stays in a single file — splitting it would make the AI's job harder.

## Rules during build

Stay within the active run's described work. Growing past it needs approval first.

**The item's `Changes:` entry is one of the four per-item completion writes**
(next.md's per-item completion step) — written at the tick, never loosely along
the way, so /done needn't re-explore. (A write belonging to the run rather
than to any item — a mid-run capture, a live-opened record — goes to the
working file's `Run-level:` section at the moment of the write instead;
next.md carries that rule.) The Changes shape:

```
Changes:
- file1.ext: created new component, 45 lines
- file2.ext: added import + handler function
```

**Where the project's own instructions require a rule-gate disposition, it is
transcribed from the item, never composed here** — see next.md's per-item
completion step, which also says what to do when the item carries none.

## Scope management

**When a mid-build discovery is work only the user can run** — a rename you can't
do, an account action, a device step — **file it as a `[user]` item, never float
it as a live question.** The failure to avoid is waving it off as "separate work
you'd handle yourself" or asking a yes/no about it: that leaves real work living
only in chat. If you can't yet script every step, file it with a rough
walkthrough anyway.

### User raises something out of scope  [PROMPT]

```
1. write the capture into Unprocessed, placed per the Captures placement rule
2. report in one line what was filed and where it went, WITH one clause saying
   why it is being captured rather than done now
3. ask "anything else?" — repeat until no
4. resume the build
```

**The reason clause fires every time, not only when the user sounds impatient.**
It is one clause, not a lesson: the reason is given so the user can act on it.

What to say, drawn from what capturing actually buys: it protects the run from
drift; the item gets weighed against work still to come rather than against
whoever is in the room; and it is weighed at the decision step and given a file list before anything
is written, which is what stops a half-designed change landing mid-run.

**On a second ask for the same thing, yield** — the same intent counts, not the
same words, and Claude judges that rather than pretending a mechanical test
exists.

```
second ask, MINOR              ->  carry it through. Append any unlisted file
  (fits the run's existing         to the working file's Files: BEFORE editing.
   shape — Claude decides;
   typically a file or two)
second ask, SIGNIFICANT        ->  still propose the split. A repeated request
                                   does not make a large change small, and
                                   absorbing a many-file change mid-run is what
                                   the run bound exists to prevent.
QUEUE MOVE the user explicitly ->  perform it with the queue mover, narrate it
  directs mid-run                  in one line, and record it at /done.
                                   An inferred move is never made and never
                                   offered; a delete keeps its own rules.
```

**Coherence exception** (narrow, keyed to throughline coherence): if the item
would share the built item's log entry and index line, and folding it in makes the
work *easier to find later*, add it to the build working file as part of this item's work
(appending any files it names to `Files:`) and continue. Evaluate against the
coherence rules, not user convenience. **When uncertain, capture.**

### Scope grows during the build  [PROMPT]

The trigger is growth against **the described work**, not the Files: list. Name
the new work and the files it needs, decide which arm below applies, and ask the
one question that arm recommends — naming the other route only as the escape,
never as a second option of equal standing. A message offering both routes evenly
hands the user a menu and makes them supply the recommendation, which is the
decision this step owes them.

```
minor        ->  recommend adding it: "This needs [work], which means editing
(fits the        [file]. I'd add it to this run — or I can file it instead.
 run's shape     Add it?" Once approved, append any unlisted file to
 — Claude
 decides;
 typically a
 file or two)
                 the build working file's Files: BEFORE editing it — the scope-lock denies
                 edits to unlisted files.

significant  ->  recommend splitting: finish what's scoped, /done to close, then
(many files,     /plan to queue the rest. Carrying it in this run is the escape,
 design          not the alternative offered.
 uncertainty)
```

**A SPEC change the build discovers it needs is FILED, not written.** Record the
sentence you think SPEC owes, file it as a capture, and leave SPEC alone. Adding
SPEC.md to scope is a repealed route.

```
build finds SPEC owes a sentence
    ->  write the sentence into a capture in Unprocessed, naming this item's slug
    ->  say in one line what was filed and that SPEC lags until the next /plan
    ->  carry on building. The run does not stop.
```

**The reason is a session boundary, not a scope rule**: the session that made a
choice is not the session that certifies it in product truth.

**The cost, stated rather than discovered:** SPEC lags that one sentence until the
next planning run. It lags visibly, as a queue item, rather than in silence.

**The SPEC-contradiction halt above is not this and must not be softened to
match.** That branch is a genuine "something is wrong here" and stays alarming.

**What may be written into SPEC is governed by the three SPEC-maintenance rules —
admission, rationale-leaves-the-sentence, and staleness — in plan.md's "SPEC is a
normal doc" ground rule.** Read them there rather than restating them here, so the
two sites cannot drift.

## Mid-build course-correction

### Claude discovers user-runnable testing is needed  [PROMPT]

When something will need user-runnable testing beyond this build — a visual check,
physical-device behaviour, a subjective judgment you can't verify — and it isn't
already a `[user]` item:

```
1. append it to Unprocessed as a [user] capture (what needs checking, and why)
   write it, then report in one line what was filed
2. ask "anything else?" — repeat until no
3. resume the build
```

Leave the check to the user where it genuinely needs them, and leave this item's
scope as it stands.

**Before assuming a device or environment is absent, read `TOOLS.md` at the
project root, then ask whether the user has a route to it** — their own terminal,
their editor, another machine. A tool failing from Claude's shell establishes
that Claude cannot run it and not that the environment is absent, so that failure
triggers the ask rather than answering it: put the question before recording an
outstanding check or asking to proceed without one. A project with no such file
has no facts on record, which answers nothing and costs one look.

**Write a newly learned environment fact into `TOOLS.md` in the moment, one line
per fact** — a tool present and its path, or a failure mode such as "fails from
Claude's shell, runs from the user's terminal". The file is writable whatever the
run's scope-locked file list says, so this needs no scope addition and never
waits for /done.

**And confirm before connecting to or acting on the user's physical device or
external hardware** — adb against a connected phone, flashing firmware, driving
attached hardware. Ask — "May I use your connected device to test this?" — and
wait for a yes. A channel like adb reaches far past installing one app, into the
user's whole device, so using it silently is a consent surprise.

### Going in circles  [PROMPT]

/next is unattended in practice — it works faster than the user can follow — so an
item that silently thrashes wastes the run with no one watching.

```
signature of no progress on one item:
    the same error recurring
    an empty diff (an edit that changes nothing)
    an attempt fails the same way an earlier, DIFFERENT attempt
        already failed  ->  STOP. Don't keep trying.
```

Tell the user plainly what repeated — the exact error, or what wouldn't change —
and hand them the decision via Approach not working.

Judgment, not a counter: the point is to surface a stuck item.

### Approach not working  [DISCUSS, PROMPT]

```
1. STOP building — don't push through a broken approach
2. state the problem plainly: what you expected, what happened, why this
   approach won't work
3. propose a path forward
4. WAIT for the user's call — don't pick a path without confirmation
```

```
adjust scope      ->  drop the item, add a prerequisite, or change the approach.
                      Update the build working file to match.
abort and requeue ->  if the item is unsalvageable:
                        a. return it to QUEUE.md's Processed (placement is your
                           call — original position or top, by what was learned)
                        b. append any captures surfaced during the attempt
                        c. append the reshape direction, naming the item's slug
                        d. tell the user to run /done
```

The reshape-direction trigger is mechanical: *abort + item returned + a reshape
direction or learning the queue needs in conversation = capture needed.* Unrouted,
it survives only in the LOG entry, which /plan doesn't read at planning time, so
the item re-presents unchanged at the next /next.

the build working file stays in place so /done's router still fires the build's close-out. The
differences: the LOG entry describes the attempt and why it was aborted, and the
item returns to QUEUE.md rather than disappearing into the log.

## Context management

You can't sense the context window filling — you only learn a session is wearing
thin when the **user** says so. So this isn't a trigger to watch for; it's what to
do when the user reports the squeeze.

```
most of the run is ticked      ->  finish and /done. Short-term memory is enough.
significant work remains       ->  close partial: /done what's ticked, requeue
                                   the rest. The next session picks up cleanly
                                   from the build working file and QUEUE.md.
```

Either way, pair it with the fresh-session handoff offer.

## Completion  [BRIEF, PROMPT]

When this item is done, next.md moves to the run's next. When the whole run is
built (every Claude-work item ticked, any `[user]` item walked through):

**What the completion turn carries.** That the build is complete; what remains
— nothing recorded yet, and done work can be tightened before closing; and,
where a held item bounded the run and the run shipped its blocker, what of the
intended change is not yet on screen, in product terms — "part of the change
you asked for is not in the app yet", never "now unblocked". It ends on a
statement, naming any command in words and keeping it clear of the sentence's
end; the user reaches for /done themselves. It carries those things and
stops there.

Tightening means refining done work; anything new routes through the existing
paths.

**Leave the build working file in place** — deleting it is /done's job.

## Audit procedure — for an `[audit]` item

next.md routes here for each `[audit]` item. Nothing above applies to one; this
section is its whole procedure.

**The output contract defines an audit:** findings route to Unprocessed so /plan
can process them into normal work items — **no direct edits to the artifacts the
audit reads.**

What gets read varies — procedure docs, the user's spec, code, UI flows, workflow
output. The shape is the same regardless: **read many, propose many.**

Audit items contribute nothing to the run's `Files:` list — settled at next.md's
self-scoping step.

### If the audit item directs a write into a document, stop and ask  [PROMPT]

Before reading, check the item's wording against the contract.

```
item directs a write into a named document   ->  CONTRADICTS the contract
    ("append findings to MAP.md", or names        surface it; don't silently follow
     a findings doc to fill)
```

An item marked `[audit]` but pointed at a doc-write is a planning slip. Following
it silently writes unvetted findings straight into a durable doc — exactly what
the route-to-Unprocessed contract prevents.

Lead with the recommendation, then wait before reading:

> "This item is an audit, but it says to write findings into review-notes.md. An
> audit files findings to the queue so you can weigh them before anything lands
> in a document, so I'd file them as captures. If you'd rather have them written
> straight into review-notes.md, say so and I'll run it as a build instead."

### Read the target systematically against the criteria  [SILENT]

Read every artifact the item names. **Apply the criteria pass by pass — one
criterion across the whole target, then the next** — not all criteria per
artifact. A single criterion held across the whole target is applied more
consistently than re-deciding every criterion afresh for each artifact, and it
groups findings by criterion ready for the compile step. Reading each artifact
once against everything tends to collapse into a per-artifact skim.

Read each artifact through, since an audit's value is reading what is there.
Accumulate observations in a scratch file in the session scratchpad, with precise
references (file:line) so the user can verify each; the item's `Changes:` entry
is written from that file at the tick.

### Compile findings  [SILENT]

Group observations into discrete findings — **one finding per discrete
observation.** Phrase each as *observed + why it matters*, the shape a capture
takes, since that's where they'll land.

**Whether a finding is worth acting on is not decided here.** That is settled at
/plan, with the user present. A filter running in a silent step before the work
reaches them can only drop things and never surface them, and deciding what
counts as a finding within the audit's parameters is already discretion enough.

### File the findings to Unprocessed  [SILENT]

Append every finding to Unprocessed, each placed per the Captures placement rule
and written to the capture-authoring standard. Tick each in the build working
file Progress as `captured`. Then say in one line how many were filed and which
audit they came from.

**Each capture carries a prose line saying it is unreviewed audit output** —
"from the <name> audit, not yet reviewed" — written into the rationale like any
other provenance. Not a parsed field: /plan's decision step reads the line, and
nothing else needs to.

**Nothing waits for approval here.** A finding is a capture like any other, and a
capture is filed and then weighed at /plan — asking the user to accept a set of
findings before filing them makes them assess the same material twice, once with
no context and again when it is actually being decided.

The `dropped` tick form stays available for a finding that turns out to be
wrong on Claude's own re-reading before filing — it is not a route for the user
to reject one, which happens at /plan.

### Close  [BRIEF, PROMPT]

When the audit item is done, next.md moves to the run's next item. When the whole
run is done, tell the user how many findings were filed, and say: "We can run the
rescan first to catch anything decided but never written down, then the done
command to record this and commit — or keep reviewing."

Reviewing means re-examining what was already found — not raising new work.
Anything new routes through the existing paths: a discovery outside the audit's
target follows the discovery rule; thinking work goes to Unprocessed. No chat
summary of the routed findings — the LOG entry /done writes is the single session
record.
