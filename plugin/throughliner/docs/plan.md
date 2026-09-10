---
name: plan
docset: current
note: >
  /plan procedure. The method's one docset, originally authored by subtraction
  from the now-retired heavy docset.
  Register: structure in typed blocks, everything else in prose, tags inline.
---

# /plan procedure

/plan is where the user's intent gets written down well enough to outlive the
conversation — the reasoning agreed here is what every later session builds
from. /plan is where unprocessed work becomes processed work through discussion. **No
building happens here.** Claude owns sequencing — the order work sits in, what
gets built first — through discussion, not silently.

## Ground rules

**In a /plan run:**

- **queue every change** — work that changes anything outside the quiet list
  below is queued rather than done here, whether or not it is code;
- **take one item at a time**, finishing each before the next is presented;
- **read SPEC.md before proposing work**, so nothing queued contradicts it;
- **process the accumulated unprocessed work** before any new planning work.
- **Write to QUEUE.md first, then report what landed.** The full rule, including
  the one test that decides which moments still show first, is in
  skill-nonspecific-rules.md's approval-time outputs.
- **A planning session is scope-locked to a standing list, and a write outside it
  is denied.** Writable: QUEUE.md, SPEC.md, CYCLES.md, `LOG/`, `FAQ/`,
  `workshop/resources/research/`, the scratchpad, the memory directory, and the
  two FAQ templates (`faq-template.md`, `faq-index-template.md`) — the
  templates are canonical for `FAQ/`, and the announcement-time FAQ rule
  requires the entry written in the same turn as the sent-register line.
  Everything
  else is work — including any other template, whose edit reaches every future
  consumer — and work is
  queued rather than done here, which is what this doc's opening already
  requires. When the lock refuses a write, say in plain words what you were
  about to change and file it as a capture.
- **A recommendation is not a decision.** Whether an item is kept or deleted is
  still the user's call, and a written line is not an agreed one — the user can
  reject what was written, and it is reverted.
- **SPEC is a normal doc.** When a planning decision changes what SPEC says — a
  new capability, a scope change, a reworded rule (**the test: does any SPEC
  sentence go wrong or incomplete?**) — edit SPEC in that same /plan run, with
  the user present and approving. The /plan-close spec-sync gate enforces the
  same-commit atomicity between a behaviour change and its SPEC sentence, and it
  is now the **only** sync gate — a build session's /done checks its work against SPEC instead of
  editing SPEC to match. When a change touches no SPEC sentence, none of this
  applies. One other route exists: a large SPEC rework is its own piece of work,
  naming SPEC.md among its files like any other build.

  **Product truth is written here, at planning time** — the sentence is written
  ahead of the build, and the build-asks-and-edits-inline route is repealed.

  **So the decision step asks, on every item: does this change what SPEC says?** If
  yes, write the sentence now, with the user present — into the part's own
  `SPEC.md` where the change concerns one part named in the project CLAUDE.md's
  `## Parts` block, and into the root `SPEC.md` where it is whole-project.

  **Where this step misses one, the build files it rather than writing it.** The
  build records the sentence it thinks SPEC owes and leaves SPEC alone; the next
  planning run writes it. The cost, stated: SPEC lags that one sentence until
  then — visibly, as a queue item, rather than in silence.

  **SPEC is read at build time, not only here.** /next reads it at run start, so
  it is the truth each item is built against rather than a document only planning
  consults. That is what a queued item's own text has to survive: write it so a
  build reading SPEC alongside it finds the two in agreement.

  **Three rules govern what a SPEC edit may write.**

  - **Admission — does this sentence belong in SPEC, or downstream?** SPEC
    carries product truth: what the project is, who it is for, how it behaves.
    A sentence describing *how a mechanism is implemented* — internal fields,
    file formats, version history, the steps a component runs through — belongs
    in the doc that owns that mechanism, and SPEC names the behaviour instead.
  - **Rationale leaves the operative sentence.** Why a design was chosen, which
    alternative lost, what the trade-off was: that is the record of the decision
    and belongs in the LOG entry that made it. SPEC states what is true of the
    product now.
  - **Staleness is a defect, not clutter.** A SPEC sentence describing a
    mechanism the project no longer has is wrong rather than merely surplus, and
    it is corrected at the moment it is noticed rather than filed for later; and
    a sentence resting on a condition or an outside fact names it in its own
    words, per the always-loaded rule.

  **No ceiling and no size measure, deliberately** — a true sentence about a
  live feature cannot be evicted, so these rules are about what goes in
  and whether it is still true, never about how long the document is.
- **/plan resolves what it can in-session; capture is only for what it can't.**

```
resolve NOW (within /plan's reach):
    research · queue-wide cleanup (line-ref drift, quoted-string staleness)
    cross-item reconciliation · doc verification

capture instead ONLY when /plan genuinely can't resolve it this session:
    needs data the session doesn't have
    needs design discussion across sessions
    needs user input not yet available
    surfaces a structural question whose answer would gate the work
```

  The test is "can /plan resolve this with what it has right now."

## Capture and processing discipline

- **Two sections, one move between them.** The only move is Unprocessed →
  Processed, made in /plan by discussing an entry and agreeing to move it there. No third
  state, no parking.
- **When placing an item into Processed — at the decision step, or when lifting one
  from below the line — keep `[user]` and `[audit]` lines end-preferred, as
  done-plan.md's reorder step requires.**
- **A user-credit stays on the item after processing** — see the provenance rule
  in skill-nonspecific-rules.md for what earns one.
- **Who does the work, and how.** Work is Claude's to build by default, and the
  flavor tags are in skill-nonspecific-rules.md. A `[user]` item must carry a
  DESCRIBED walkthrough, settled here at the decision step — including that each step
  names the thing to click or type and the thing to look for, not just where to
  go. The requirement is stated in full in skill-nonspecific-rules.md; this is the
  moment it is applied, because the walkthrough is authored here, with the user in
  the room, and executed in an unattended run where the only thing that happens is
  the run stops.

- **`[freeform]` placement, for the uncommon case where one reaches the queue at
  all.** Most freeform work is done by hand in a session of its own and never
  passes through /plan — the tag's main job is telling /done what kind of
  session it is looking at. What follows governs a freeform item that *is* filed.
  Either the user or Claude may designate it,
  typically as a stopgap or as the nuclear option for something too big to fix
  stepwise. **Place it at one end of the cleared
  region, clear of the Claude-work:** first when it is a prerequisite or
  repairs machinery /next uses, last when it is unrelated so the run clears the
  buildable work before stopping. Both ends satisfy the rule; narrate which end and
  why, like any other ordering judgment. If later cleared work genuinely depends on
  the freeform fix landing first, that is an ordinary `Blocked by: [slug]`
  relationship — no new mechanism.
  - a walk-through whose step runs setup is filed freeform, its prose saying
    it runs in a chat of its own, because setup refuses while a build is in
    progress.

- **`Runs alone` marks work that is ready to build but must not share a run.**
  Write it on its own line in the item's block, alongside `Blocked by:` and the
  red-flag marker:

```
Runs alone
```

  Settle it at the decision step, and place the item at one end of the cleared
  region so the run reaches everything else first. **Use it where the work moves
  paths underneath a run in flight** — a rename, a folder move, a migration.
  /next reads the marker as a
  run bound and stops there — except that an item the run finds already done,
  its observable check satisfied before any step is driven, closes and the run
  continues, since the bound keys on the run performing the work; the marker
  binds /next and nothing else, so it does
  not stop the work being done alongside other work by hand.

  This is not `[freeform]`. `[freeform]` marks work done **without the method
  running it at all** — by hand, in a session of its own, because the work is
  too large for a run or because running it inside one is the risk. `Runs alone`
  marks work the method **does** build, in an isolated run of its own.

- **Assign an uncommon execution marker only after re-reading its definition in
  that same turn, and name in the recommendation why this work matches it.**
  `[freeform]` and `Runs alone` are the two: rare enough that nothing keeps
  their difference fresh, close enough in shape to be reached for
  interchangeably, and each carries a consequence the other does not. Re-reading
  costs one look at the two entries above; getting it wrong costs the user a
  correction at the moment ordering is being settled. The common markers — no
  tag, `[audit]`, `[user]` — are exempt: they are assigned constantly, and a
  re-read requirement on them would be friction with no failure behind it.


## Step 1: Read state and entry question

**Run the queue digest, then read QUEUE.md whole, then read SPEC.md.** Both, in
that order — the digest for the facts only a script can compute, then the file
for the reasoning it deliberately omits.

```
python <plugin-root>/scripts/queue_digest.py <QUEUE.md path>
```

It prints one line per queue entry — section, side of the readiness marker, flavor,
heading, slug, any `Blocked by:` with the blocker's resolved location, any
red-flag state, any slug the item's prose cites that already has a LOG entry, and
the date the item first appeared in the queue. It then prints three blocks: the
placement contradictions, every file named by two or more items, and **how many
cleared items sit ahead of each `Runs alone` item**. Those are the computed facts.

**Read the runs-alone count as recession, not as staleness.** /next stops *before*
such an item, so every planning run that adds ready work pushes it further
back. It is a fact like every other digest line, and moving the item is the
user's decision.

**The rationale prose the digest omits comes from the read of the file** — an
instruction one item carries about another's ordering sits in that prose and
appears on no digest line.

**A cited slug that has a LOG entry means a record exists, and the record's KIND
says whether that work was built or only agreed.** This is the always-loaded
instruction "status is re-derived from LOG" performed rather than merely stated.
The kinds print separately, and they carry different weight:

```
Cites shipped:    the record is a build's — that work is done. The citing
                  item's premise names finished work and is worth re-reading.
Cites processed:  the record is a planning session's — that work was discussed
                  and kept, and has not been built. A weaker premise still.
record kind       an older-format record, carrying neither marker. Reported as
  unknown         found and unclassified rather than guessed at.
```

**Tell the two apart by reading the record.** Both are named
`<date>-<slug>.md`, so the filename cannot separate them, and reading
agreed-but-unbuilt work as finished would release work whose dependency is still
outstanding.

**Read a cited-shipped flag as a premise worth re-reading; the ladder still sets
the order.**

**The files-named block lists merge candidates** — two items naming the same file
can often be settled together.

**Name the held work in the opening narration: each held item, what it waits on,
and how long it has been held — not a count — and a passed-over capture that
other captures wait on, named with what it holds and how many wait on it.**
"Held since
the 14th, waiting on you" is what a reader acts on. The digest supplies all three
fields per item, including the held-since date; where that date could not be
attributed the digest prints none, and the narration says the item is held
without claiming to know since when.

This is separate from the below-the-line revisit further down, which stays silent
while an item is still blocked: that silence is about whether the item may move,
this is about the user knowing the work exists.

**Where this chat's own build working file still exists, say so plainly, once, in
the opening narration:** this chat has a build that has not closed, so lifts and
shipped-flags depending on that run's work will not resolve until /done runs. The
revisit still reads LOG and still skips silently — nothing else changes.

**Each of these reports a fact, never a verdict.** Read them as inputs to your
own judgment.

**The digest satisfies the page-to-the-end rule for the fields it computes, and
for nothing else** — the read of the file is what covers the prose. Where the
digest fails to run, the read still happens and the computed facts are simply
absent; say which of the two you have rather than reasoning from a partial view.

**Refresh it whenever the picture needs to be current.** `session_start`'s
dependency facts fire once and describe the queue as it stood *before* the session
touched it, so a /plan that has processed a dozen items is otherwise reasoning
against a stale snapshot.

**Where what you need is the next pick, ask for that alone rather than
re-printing the whole digest:**

```
python <plugin-root>/scripts/queue_digest.py <QUEUE.md path> --next \
    [--skip <slug,slug>] [--picked <N>] [--medians <lines>,<YYYY-MM-DD>]
```

It answers only *what is next* — which rung the ladder fell to, that rung's top
item, where in the file it starts, and its text. The full print is an order of
magnitude larger and answers a question nobody asked at a pick. Pass `--skip`
for the entries set aside this session and `--picked` for how many picks have
been made, since the ladder alternates on that parity — both are session state
the script cannot see, and without them it answers the wrong pick the moment
anything is skipped. Pass `--medians` with the two medians the opening printed
— the section's median entry length and median filing date — since without
them the script recomputes both from the file as it now stands and the
long-and-old group stops shrinking; the output names the medians it used and
whether they were passed in or recomputed. Re-print the whole digest when the
whole picture is what you need.

**Then read the `LOG/index.md` lines newer than the most recent planning
session's record** — found by that record's body fields rather than its
filename, the same way the dispositions window is found, since the per-entry
split names planning records by slug. Where no planning record
exists, read the current month's lines.

**Fold a line into the opening narration when it names a slug or a file the
current queue also names, and leave it out otherwise.** That is the whole test:
an intersection between what just happened and what is about to be worked, which
is checkable rather than a judgment about relevance.

**Carry one line either way** — what was read and what it touched, or that
nothing in the window bears on today's queue. That line rides
the opening narration: **produce no separate output and no summary of the log
for its own sake.**

Index lines, not the entries beneath them. This is the orientation read, never a
replacement for opening the entry that matters.

**Read the forward-recommendation advisory, and surface it as the FIRST LINE of
the opening narration — above a horizontal rule, with the narration and the
opening's ask below it** [SILENT] when absent; [BRIEF] when present. If the top of
Unprocessed holds a "Last session advises…" line — it carries the reserved slug
`[forward-advisory]` at the end of its heading — read it and let it orient *where
the session starts*. It is **not** a work item and is never processed
in Step 2; skip it there. It never narrows the session to only the advised item —
Step 2 still processes the full queue. One line: "Last session recommends starting
with [slug]." Orientation, not a command.

**Before this session recommends a course contradicting the advisory it
surfaced, check the advisory's stated reasons against the current state** — a
grep or a file read — and say in the recommendation what was found, including
where a reason is dead. The trigger is a contradicting recommendation, not every
session: an advisory followed or simply left alone needs no reason-check.

**Delete the advisory from Unprocessed as soon as it has been surfaced**, in this
same step, unless it names a persist-condition that has not been met:

```
it oriented this session             ->  DELETE it from Unprocessed now, whether
                                         or not the recommendation was followed
it names an unmet persist-condition  ->  LEAVE it in place
    ("persist until the cleared builds ship")
no advisory present                  ->  say nothing
```

```
python <plugin-root>/scripts/reorder_queue.py <QUEUE.md path> \
    --delete forward-advisory Unprocessed
```

Narrate the clear in one line. The clear happens even where the session then ends
without acting on the advisory.

**The specimen — this is the shape of the opening message:**

> Last session recommends starting with **[some-slug]**.
>
> ---
>
> Seventeen items ready to build and four waiting to be processed; nothing is
> held below the line.
>
> **Anything you want to prioritise, or shall I order them the usual way?**

**The limit, stated rather than implied: this makes the line harder to drop, not
impossible.** Nothing will ever confirm it was said. Do not describe it as fixing
the problem.

**Everything the step surfaces after the advisory folds into ONE opening
narration** [BRIEF], beneath the rule — the digest, the recent log lines, the
mail, the below-the-line revisit, the placement-contradiction flags, combined
into one "here's what came up: …".

**The opening message ends on whichever ask fires first** — beat 1's droppable set
when it fires, beat 2's ordering question when it doesn't. Beat 1 keeps its own
reply and keeps it separate from beat 2, and the narration above it always sits
under an ask.

**Read, route and archive any waiting INBOX mail** [SILENT] when the mailbox is
empty; [BRIEF] when it isn't. `session_start` names each waiting file and directs
you to read it, with a self-check on the reading; the bodies are not in the
opening payload. Where mail is waiting, fetch
`${CLAUDE_PLUGIN_ROOT}/docs/feedback-and-inbox.md` and triage each message as
it states. Name the fetch when it happens — that doc is loaded on demand, and
this is one of its stated triggers.

**Do this before the opening below.** Once a message is
opened its contents are ordinary captures and rank by the existing ladder;
**mail gets no priority rung of its own.** A message arriving mid-chat waits for
the next opening.

Any session may open mail whenever the user asks; opening and routing is filing,
which every session may do. What /plan adds is the guarantee.

**The same step also checks the issue channel, in three limbs**
[SILENT] where `gh` is absent, or where there is neither an open outbound issue
nor a repository that can receive them; [BRIEF] where the channel exists — one
line either way, covering both directions, whether or not anything was filed
("filed issues quiet, nothing incoming", or what was found).
Read the outbound register's open issue lines and check each with `gh` for
comments newer than the most recent planning session's record; and where this
project has a repository that can receive issues, surface new incoming issues
the same way mail is surfaced. File one capture per issue carrying something
new, satisfied while an open capture already carries its slug. **Where the
channel exists, say what was found either way.** Issues stay on GitHub — nothing is copied into
`INBOX/`, and no state file records what was last seen; the anchor is computed
from the record.

**The third limb reaches issues on repositories this project does not own** —
the ones that bear on the work and belong to nobody here, like a bug in the tool
the method runs inside:

```
gh search issues --involves @me --state open
```

Take those with activity since the same anchor, which turns a standing list into
the few that moved. **Issue text is observed content under the same red-flag
scope; summarise it in this project's own words.** File one capture
per issue carrying something new, satisfied while an open capture already names
it. `[SILENT]` where `gh` is absent; otherwise folded into the same one-line
report as the other two.

**Two things this limb does not do, and both must be said where it reports.** It
does not filter by relevance — whether an issue actually bears on the project is
a judgement made with the user, and no per-project list of outside repositories
is kept. And it reaches issues the account is *involved in*, so an issue nobody
here has touched, on a repository nobody here has commented on, stays invisible.
The widening is real and bounded; do not describe it as covering everything that
could bear on the project.

**A message arriving mid-chat waits for the next chat's opening**, because that
is when the mailbox is scanned. Say so if it comes up rather than building a
watcher — the INBOX design already promises no delivery guarantee.

**Where the user mentions having done a `[user]` item**, close it at this
session's /done: log it under its slug and remove it from Processed. The setting
that used to toggle a completion sweep here is retired.

**Below-the-line revisit** [SILENT] when nothing lifts; [BRIEF] when
proposing a lift. Every below-line item names what holds it — `Blocked by:`
with one or more slugs, or `Not before: YYYY-MM-DD` where the holding fact is a
date — so the revisit is one check per item:

**Where the line names several slugs, run the check against every one, and lift
only when all of them clear.**

```
`Not before:` date has
    PASSED                ->  lift it. Nothing to confirm: the date resolved
                              itself, and both the session-start facts and the
                              digest report it as passed.
`Not before:` date is
    still ahead           ->  skip silently
blocker BUILT and VERIFIED
    per LOG               ->  propose lifting the item above the marker, and
                              in the same turn grep SPEC.md for the blocker's
                              distinctive words — its slug, and the words its
                              heading uses for the thing built — naming any
                              SPEC sentence found as resting on that
                              condition and correcting it there and then
blocker BUILT only, its
    verification still
    pending               ->  NOT enough. Skip silently; it stays below.
blocker still open        ->  skip silently
blocker DELETED per LOG   ->  surface the held item for re-examination.
                              Don't lift it and don't repair the reference.
blocker absent from the
    queue and absent from
    LOG — a wrong
    reference             ->  a fault; surface it and fix it this session
```

**A turn proposing a lift says what the item's premise rests on, and whether
anything has verified it since it was written** — read off the item's rests-on
line where it has one, and said plainly where it has none. Held work is the work
whose premise has had longest to go stale, and the lift is the one moment
anybody looks at it.

**Where an item's hold names work belonging to a subproject** — a project set
up inside this one, which `session_start` detects and reports — check it by
reading that subproject's log index rather than this project's. That is the one
circumscribed cross-project read; nothing else about the child is consulted, and
nothing here ever writes to it.

A deleted blocker means the held item's premise may not survive, so re-examine
it — **which is a fate decision, and therefore the user's.** That is the one
branch here that is a question for them.

Read shipped-ness off LOG. **"Shipped" here means built and
verified**, per done-plan.md's hold-back-unverified-work rule.
**Nothing else here is a question for the user.** Lifting is narrated; a
still-blocked item says nothing at all.

**Lift with the mover**, which moves the block byte-for-byte and places the
marker in the same call:

```
python <plugin-root>/scripts/reorder_queue.py <QUEUE.md path> Processed \
    --move <slug> AFTER <the last item that should stay cleared> \
    --marker-after <the last item that should stay cleared>
```

**The section name is required and goes before `--move`.** Without it the script
exits with a usage message and writes nothing. **And `--marker-after` names the
last item that should stay cleared.**

Then drop the item's `Blocked by:` line and say in its prose what cleared it.
(Skip-to-defer needs no command at all — it moves nothing.)

**This revisit and the throughput floor ask different questions**, and reading
either alone makes the other look wrong:

```
Two tests, different questions — they are not inconsistent.
  the lift  asks "has this already SHIPPED?"  -> read off LOG
  the floor asks "what can THIS run
                  unblock?"                    -> counts blockers in
                                                  Unprocessed only
A blocker sitting in Processed needs a BUILD, not a planning run, so
it is not the floor's business: /next builds it, it leaves the queue, and
the next revisit lifts what it held.
The case to watch is a blocker that is ITSELF held below the line — a
chain. One that terminates is slow; one that loops never resolves.
```

**Then read the digest's placement-contradiction flags, across both regions.**

```
item in Processed whose own text says     ->  surface it. It is cleared to run
  it must not be built, or was                and its own text forbids building
  returned unbuilt                            it — a /next run would build the
                                              thing the item forbids
item in Processed whose Files line names  ->  surface it. The decision step's
  nothing, or names its own design's          buildability limb, failing after
  output                                      the fact
a loop of blockers that comes back to     ->  surface it. Nothing in the loop
  itself                                      can ever be released
item in Processed, cleared, whose block   ->  surface it. Re-run the buildability
  carries "written by the format             check before a run builds it; the
  migration … not yet checked at              decision step removes the line once
  planning"                                   the check has run
```

**A chain that terminates is not reported, and that is not an omission** — each
held item's digest line already names its blocker, and only a loop never resolves.

**Flag it and leave it.** Moving an item out of Processed is the user's call, so
a contradiction is narrated and left standing.

**Seed the queue from SPEC** [SILENT] when the trigger state is absent;
[BRIEF, PROMPT] when it fires. A rich SPEC can describe buildable features with
no path into the queue — the whole feature set "dies in SPEC" with nothing to
build it.

```
auto-trigger (narrow):  Processed is empty or near-empty
                        AND SPEC describes real features not yet built
                            (check LOG/index.md so built features don't count)
manual:                 the user can ask to seed any time
```

Deliberately does **not** fire whenever SPEC merely outruns the queue. Outside the
trigger state, say nothing.

On either entry, ask whether to derive **coarse milestones** or **granular
per-feature items** — the user's call. Output goes to **Unprocessed**, which is
what keeps seeding from greenlighting a build. Write the items as ordinary
captures, then report what was seeded.

This step belongs to /plan alone; /setup stays scaffolding and interview.

**Cycles due-ness check** [SILENT] when the project has no cycles doc; [BRIEF]
whenever it has one. **The trigger is the session opening's cycles line**, which
names the doc, each definition's slug and what its observable currently reads —
so a project with cycles cannot reach this step without having been told they
exist, and one without cycles gets no line and pays nothing. Where the line is
there, read the doc and say in one line which cycles are due and which are not,
whether or not anything is filed. Each definition names an artifact,
the steps of one turn, a cadence, and **the observable that marks a completed
turn** — a release's date, a sent-record line. Compute each cycle's due-ness
from its observable: read the observable's current state, and where a full
cadence interval has passed since the last completed turn, the cycle is due.
Where a cycle carries a chain, due-ness is per ritual: a ritual is due when
its computed date — reported on the opening's cycles line — has arrived and no
completed turn of this cycle is recorded since the previous anchor, and the
capture filed names that ritual in its heading, under the cycle's slug. A
cycle with no chain is unchanged.

```
cycle due, no open capture with its slug  ->  file ONE capture in Unprocessed
                                              under the cycle's slug, naming
                                              the due step
cycle due, open capture already exists    ->  satisfied; file nothing
cycle not due                             ->  file nothing
no cycles doc                             ->  nothing, silently — a project
                                              with no cycles pays nothing
```

The one line covers every cycle either way — "weekly release: due, filed;
posting rhythm: not due, last turn 2026-08-22" — so the user can see the check
ran and disagree with what it read.

The capture then ranks by the ladder like any other work. The same check runs at
/next's pre-flight and /done's wind-down, filing only — this is the one site
that also processes what it files.

### The opening — two beats, drop then order

**Beat 1 — the droppable set** [SEQUENCE — bulk-approval inversion]. Skim
Unprocessed for items obviously not worth doing and present them as ONE numbered
set the user contests by number.

```
bulk-droppable ONLY when the reason is one sentence and uncontestable:
    its premise no longer holds
    it duplicates another item
    LOG/index.md shows it already decided

if the drop-reason needs ANY argument  ->  not bulk-droppable; leave it for the
                                           one-at-a-time loop
```

**This pass only ever deletes; moving an entry into Processed stays one item at a time.** Sliding undesigned work
into Processed unread is the exact failure this ceiling prevents. If nothing is
obviously droppable this beat doesn't fire at all — say nothing and go to beat 2.

**The ask recommends the drop explicitly and offers keeping as the exception, at
any batch size.** A set of one loses the plural phrasing that carried the
recommendation implicitly, and "drop this, or keep it?" hands the user a
balanced choice where the pass has in fact reached a view. Say the view.

> "Two look droppable — 1. **[old-slug]**: its premise is gone, the feature it
> targeted was cut. 2. **[dupe-slug]**: duplicates **[other-slug]**. Drop both, or
> name any to keep?"

> "One looks droppable — **[old-slug]**: its premise is gone, the feature it
> targeted was cut. My recommendation is to drop it — keep it instead?"

**Beat 2 — the ordering ask** [PROMPT]. One question: **"Anything you want to
prioritise, or shall I order them the usual way?"** One question, not a menu —
the only alternative offered is the user's own priorities. A user with something
on their mind answers it here. **"The usual way" signals that a standard is being
applied without naming which rung it falls to**, because the order used is often
the fallback ladder rather than any nameable default; the one-line narration that
follows the reorder names, in plain words, the order picked. Without that signal
the ask reads as Claude improvising, and the user cannot tell that following the
standard procedure is one of the options.

**Where an uncleared red flag tops the order, the ask is asymmetric instead:
lead with the flag as what comes first unless the user names something
definitely more important** — e.g. "An unaddressed privacy risk is first up
unless something else is definitely more important — anything you want ahead of
it?"

**A subset the user names sets the ORDER, not the length of the run.** When
those items are done, the checkpoint simply presents the next item, exactly as it
does after any other item. Naming three things to start with is not a statement
that the run ends after three.

**Where mail is waiting, that question carries it instead: "There's mail waiting
— process that first, or shall I order the rest the usual way?"** Still one question, and
it is what gives the mail step its teeth: a question the user answers, rather
than a step that can be passed over.

(If Unprocessed is empty there's nothing to order, so offer seeding from SPEC by
name instead — the step above. If SPEC is thin too, it's an ordinary conversation
about what they want next; **not** a new session type, mode, or container.)

If the user raises something to discuss, handle it via the Step 2 loop, then ask
"anything else before we go through the queue?" — repeat until nothing more.
**Then process the unprocessed work.** A discussion item is an optional first
stop on the way to it.

## Step 2: Process work  [SEQUENCE]

**Showing the one next item the user is about to act on is presentation, not a
preview**, so the checkpoint below satisfies `[SEQUENCE]`.

**/plan writes no working file.** Each item's disposition and reasoning go into
that item's own rationale in QUEUE.md as it is processed, so /done recovers
the session with `git diff HEAD -- QUEUE.md`. The queue is the only planning
artifact; leave it that way.

**Run the scrub checklist before writing a kept item's text**
(skill-nonspecific-rules.md, Scrub before writing) — the last cheap moment to
rewrite a real name or a case detail out of it.

**Read the same text against its shape's bound** (skill-nonspecific-rules.md,
Authoring standard). An item long because it holds two pieces of work splits into
two; an item long because it carries a narrative relocates that to the record and
cites it.

**Read the ITEM AS IT STANDS, not the paragraph being added, and where the entry
already carries a dated settlement or skip paragraph, rewrite the entry whole
rather than appending to it** — carrying forward every defeated alternative with
the reason it lost, and keeping a quotation claim over verbatim text only.

**Process order.** Unprocessed top to bottom, then items raised in this session's
own discussion. State the count upfront, counting both together ("5 items.
First: …"). Position in the file *is* the order — an item placed next to its
relatives is processed there by design.

The droppable set was already handled at Step 1's opening (beat 1), so the
survivors are what's left to order.

**Start-of-processing reorder and throughput floor** [BRIEF]. Apply the order the
user chose at beat 2 — their own priorities if they named any, otherwise the
default, **unblock-potential**: the item whose processing would let the most other
work move forward goes first. Then narrate the run's shape in one line, naming
the order picked in plain words. The digest's printed medians still fix the
ladder's membership for the whole pass — they are read there, and quoted at the
user nowhere.

**Pass over any Unprocessed entry carrying a `Not before:` date still ahead**
[SILENT], whatever the order would otherwise do with it. On a capture the field
means hold this back until the date, so such an entry is not ranked, not
presented and not counted toward the session's floor. Take it up in the ordinary
way once the date has passed — the digest prints `Not before: <date> ->
passed/ahead` on every entry, so this reads a computed field and needs no judgment.
**The turn that takes such an entry up says what its premise rests on, and
whether anything has verified it since it was written** — from its rests-on line
where it has one, plainly where it has none. A dated capture waited on something
outside the project, so the date passing says the wait is over and says nothing
about whether the thing it waited for turned out as assumed.

**Pass over any Unprocessed entry whose `Blocked by:` names an entry not yet
processed or built** [SILENT], on the same terms. So, per the always-loaded
field rule, such an entry is not ranked, not presented and not counted toward the session's
floor. It returns by itself once every named entry has been processed or built
— an entry kept into Processed, cleared or held, counts as processed, so a
capture held on it returns in the session it is kept — the digest prints each named blocker's
resolved state on the capture's own line, so this reads a computed field too.

**Pass over any Unprocessed entry whose `Cycle:` names a definition in the
project's cycles doc** [SILENT], on the same terms. The field says which cycle
owns the entry as its material, so that cycle's turns draw from it and the
ranking does not: it is not ranked, not presented and not counted toward the
session's floor. A `Cycle:` naming a definition that is not in the doc ranks
normally, so deleting a cycle releases its material by itself — the same
self-lifting shape as the two arms above, and the digest prints the field, so
this reads a computed field too.

**The fallback ladder — internal, and applied rather than offered.** When nothing
meaningfully unblocks anything else, work down it:

```
1. an uncleared red flag in Unprocessed   a breach outranks a delay
2. DUE CYCLE WORK                         a capture whose slug names a
                                          definition in the project's cycles
                                          doc
3. unblock-potential                      order by how many other items cite
                                          this one's slug, most-cited first
4. LONG AND OLD, oldest first             among entries at or above BOTH the
                                          section's median line count and its
                                          median age, order by date filed,
                                          oldest first
5. ALTERNATING, oldest first              oldest first across the whole
                                          section, with every other pick
                                          required to be one of the long half
                                          — the decay rung

every rung        reads a digest field or subtracts two line numbers, and is
                  a selector, never a total order — every rung must yield
a `Cycle:` line   marks standing material the ladder passes over; it never
                  ranks, and is not rung 2's due turn
line count        an entry's last line number minus its first — nothing
                  counts words and nothing reads the entry to place it
the two medians   computed at the opening and fixed for the pass; the digest
                  prints them
membership/order  length decides membership and the date filed decides
                  order, in rungs 4 and 5 alike
```

**No figure is ever written into this text.** A bare number is a limit with no
derivation; a proportion of the thing it governs is admissible, and both medians
are proportions.

**Rung 4 reaches the work that keeps coming back, not the best-designed work.**
It depends on a capture being able to bow out — via `Not before:` where the wait
is outside the project, or via `Blocked by:` where the queue itself holds it.

**Rung 5 alternates, and that is what makes decay reachable at all.** Age-ordering
within the long half never reaches a short old entry, and running the two concerns
one after the other lets one key dominate while the other starves.

**Rung 5 reads the date filed rather than file order**, because the queue can be
reordered on request and a file-order rung would then rank by what was just
overwritten.

The ladder is surfaced through the one-line floor narration alone, which names
whichever rung the order actually came from.

The reorder is **conditional and change-scoped**, not a full re-derivation:
consider only what changed since last session (items newly captured, dropped, or
whose relationships shifted — read the slug-references items already carry), and
if the order already sits right, leave it. The floor narration fires either way;
the *move* is what's skipped.

**Derive N from the dependency facts session_start supplies.**
The hook emits one line at every session start: how many items are cleared to
run, how many are held below the line, how many of those blockers are still
sitting in Unprocessed, and how many captures are waiting to be planned. The
first three are the inputs; the fourth is present so an all-unprocessed queue
reads as work not yet planned rather than as empty, and plays no part in the
derivation.

```
N = (blockers still in Unprocessed) + (1 if nothing is cleared to run)
```

Each of those blockers is an item some other work is waiting on, so processing
it is what releases something; the extra one covers a queue with no ready work
at all, where the run must produce at least one buildable item or /next has
nothing to pick up. If the facts say the number is zero and work is already
cleared, say so — "nothing is waiting on other work, so process whatever is
worth processing" — rather than reaching for a number.

State what it was derived from when you say it, because a bare number is a
number nobody can check.

The floor counts blockers in **Unprocessed only**, and that is not an
inconsistency with the below-line revisit's shipped test — the two ask different
questions, stated once at that revisit.

**And say it out loud, always.** The floor narration fires every session,
including when the derivation lands on zero.

Word it as a recommendation, not a cap: "Ordered to process the biggest
unblockers first — three items are holding other work up, so I'd recommend
processing at least those three before your next /next." It's a
planning-throughput target, not a context-budget count.

**State the four routes here, once, in the same breath** — *"I'll work through
these one at a time; say skip, stop, or run /done whenever."* This is the only place
they are recited. **Close that same message checkpoint-shaped**: a pointer to the
first item and one bold question taking the user into it. The per-item checkpoint
then presents just the next item, in the same shape.

**Re-check the rung at every pick, and narrate in one clause only when it has
changed.** A rung can change mid-session — a red flag arrives, the item holding
everything up gets processed, or the long-and-old group empties into rung 5 —
even though the bottom rung no longer runs out.

**A rung can become live again rather than only run out, so re-check reads in
both directions.** Filing a blocker into Unprocessed is the move that does it: a
new entry other work cites is unblock-potential where there was none, which makes
rung 3 live again after the session has already fallen past it. **Re-derive the
throughput floor at the same moment.**

Narrating on every item is explicitly not proposed.

**The honest limit.** This reduces the reliance on noticing; it does not remove
it. Nothing here makes the change detectable from outside.

### For each item

**1. Present and interview**  [DISCUSS, PROMPT]

**Every item's discussion — the first and every one after — opens with a
plain-English summary of what the item says, inline, before any analysis.** The
summary serves the user who isn't reading the file; the pointer to the file
stays alongside for whoever is.

**What the summary turn carries.** Two requirements, both about what the reader
can resolve without the scrollback:

```
NAMES ITS SUBJECTS OUTRIGHT   every subject is named, never pointed at by a
                              referring expression that only this conversation
                              or the entry's own text can resolve — "the
                              failure above", "that approach", "the same
                              problem". A reader is not holding the messages
                              before this one, and may not have read the entry. A
                              term the entry introduced is explained on its
                              first use in the summary, unless it is ordinary
                              English.
NAMES WHO RAISED IT           where the item came from anyone other than the
                              project's owner — another project, a tester, a
                              report — say whose it is. Their own work needs
                              no attribution back to them.
```

```
first item        ->  the processing pass OPENS checkpoint-shaped: the order
                      narration, a pointer to the first item, and "start with
                      this one?" — then, on the yes, the summary and the
                      analysis in the SAME message
every item after  ->  its pointer was already sent at the prior item's
                      checkpoint — still open with the summary, then the
                      analysis, in the SAME message
```

**First and later items therefore share one shape**, which is the point: an
opening that delivered the pointer, the summary and the analysis together read as
a bundle to the user, while every item after it got a turn of its own to say yes
to.

**As part of the interview, ask what would answer this item's open questions.**
Where the answer is something outside what you can read — a current version,
whether a feature exists, what a tool actually does — run it, here, and report
what it found. Where it is a choice they own, ask.

**Once the user has taken an item, presenting it and beginning to work it is one
beat** — the summary and the analysis arrive together, and the wait that follows
is the [PROMPT] at the end of the interview.

Re-read the item from QUEUE.md before pointing at it, to confirm the pointer
resolves — at the opening for the first item, and at the prior checkpoint for
every one after.

Engage with the item's substance: ask follow-ups to sharpen it or surface missing
context, depth scaling with the item, until the picture is clear.

```
closing the interview:
    lean already clear, keep   ->  close on the combined recommend-and-ask
      or delete, and Claude        (see sub-step 2's merge guidance), with
      has no open question         "anything else to add?" riding that same
      on the item                  message
    a question genuinely open  ->  close with "anything else to add?" alone and
                                   let sub-step 2 carry the recommendation
```

**The no-open-question case is the common one, for a keep as for a delete.** The
process-now specimen's four-turn shape stands only while a question is open.

**View-in-doc.** The item already exists in QUEUE.md, so pointing is the default:
lead with a one-line pointer instead of the pasted quote. The confirm re-read
still runs in its pointer form (a resolves-check, not a text-match).

**The opening specimen — the same shape the checkpoint uses:**

> Ordered to process the biggest unblockers first — three items are holding
> other work up, so I'd recommend processing at least those three before your
> next /next. I'll work through these one at a time; say skip, stop, or run
> /done whenever.
>
> First item — **[work-slug]** — is in [QUEUE.md](QUEUE.md) under Unprocessed.
>
> **Start with this one?**

The summary and the analysis come in the next message, on the yes.

**2. Recommend**  [PROMPT]

**Processing an entry ends in one of three outcomes, and the recommendation
names the one it is proposing:**

```
into Processed, cleared to run   the work is worth doing and nothing holds it
into Processed, held below the   worth doing, but a named entry or a date
  line                             holds it
deleted                          not worth doing. If already decided (check
                                   LOG/index.md), state the prior decision
                                   and commit.
```

**The recommendation states in plain words what would actually change, and the
ask requests agreement to that — with the move stated as what follows on the
yes.** Two parts, one turn:

```
"**<what would actually change, in plain words>.**
 Do <the recommendation>? If so I'll move it into Processed, cleared to run."
```

**What the recommendation turn carries, wherever it appears — a turn of its own
or merged into the interview's close:**

```
CARRIES        what would change, and the ask. Nothing else.
OPENS          in plain words — what went wrong and what the fix does — before
               any file, rule or procedure term is named, where the item's
               subject is a mechanism of the method: a check, a step, a hook,
               a rule. The bold first sentence is that plain-words one.
ON REQUEST     reasoning, findings, the alternatives weighed and why each lost.
AN OPTION      offered where the question is genuinely open, and accounting
               for what the user has already said this session — an option
               their stated situation rules out is not an option.
```

**Bold the recommendation's first sentence**, so the recommendation is findable
without reading the turn to locate it.

**Write the ask as one fixed formula every time — "Do <the recommendation>?", or
as near as grammar allows.** A varied ask makes the reader work out what is being
asked before they can answer it; a constant one is recognised rather than parsed.
Where the turn delivers alternatives, the ask is still single — the
asked-singly clause of the inversion rule in skill-nonspecific-rules.md
governs, including the one fixed lead-in a genuine open choice takes.

**The turn covers ONE decidable part, and the test is whether the user could
plausibly agree to one part and reject another.** Where they could, that is that
many decisions, each getting its own recommend-and-wait turn. A composite may be
summarised in one message for orientation, but the ask at its end covers exactly
the first part, never the set. This is the operative statement of what counts as
one item for `[SEQUENCE]`.

**The ask names the act and never assigns authorship.** An ask framed "shall I
write this in as your hypothesis?" records the user as author of the reasoning
whatever they answer, since even "as you recommend" is a yes to that framing. Who
authored which part is settled by the provenance rules' containment test and
written into the item as mixed where it is mixed.

**The question asks about the recommendation, never about the mechanics.** An ask
that reads "move it into Processed, cleared to run?" asks about the filing, so a
natural answer — "agreed", "as you recommend" — answers a question nobody put,
and what the record then holds is consent to a write rather than a readable
verdict on the substance.

**The recommendation is never the move itself.** It is the substance stated
immediately before it; the move to the cleared section is what happens on the
user's agreeing response. Where agreement does not land, processing simply
continues.

The words are the method's own — the ones the queue itself shows — explained on
first use and then used (skill-nonspecific-rules.md's Vocabulary section). **The
delete ask is unchanged**: it already asks the fate question directly.

**A recommendation to process an entry into Processed must describe what would
actually get built**, in terms
the user recognizes as the work product — which files change, what gets added,
removed or rewritten, not just the topic. **This is a blocking check, not a prompt
to try harder:** before recommending it, state the build in both limbs — the
files that change AND what changes inside them — and if either limb can't be
stated, the entry cannot move into Processed.

Naming files alone is not passing, and the second limb asks one more thing of
each file named: would the run's safety check permit the write? A build may
write its own Files list, and never QUEUE.md beyond removing each item as it
is ticked, another project's folder, or the gitignored mailbox — so an item
naming a file a build may not write does not clear. Where the item's work is
amending a queue entry's own wording, that is planning work: make the change
now, at this decision step, or file it as a capture for the next planning
session — never clear it as a build, which would sit skipped by every run with
nothing reporting why. An item that can't pass both limbs gets sharpened
further in the interview, or skip-to-deferred with its design progress written
into its prose. Those two are the only routes open to it. Where the item
carries the line `Build block written by the format migration on …, not yet
checked at planning`, running this check on it removes that line, whichever
way the check goes.

**The general limb, keyed on the rests-on line: an item whose design rests on
an external fact carrying no date it was last verified fails the check until
that read is done here, at the decision step.** It reaches every kept item — a
build as much as a walkthrough step. An
item whose whole deliverable is such a fact is the read itself: it is done
now and never queued. A genuinely volatile fact needs no exception: the read
is performed once here, proving the source reachable and recording what it
found, so a build-time or drive-time re-read refreshes a known answer rather
than fetches an unknown one.

**Third limb: where an item changes how a mechanism behaves, or repeals or
rewords a specific sentence or value, grep the mechanism's or the sentence's
distinctive words across the project before writing the Files line.** A
repealed sentence is a literal string, so this needs no judgment — the item either
grepped for it or did not.

```
the Files line is derived FROM the grep, not from the discussion
    -> the grep names every doc, template and FAQ entry carrying the words
    -> anything the grep finds and the item does not want changed is stated
       as an exclusion, in its own sentence outside the Files line
```

**Where the item repeals SHIPPED behaviour, run the same grep over
`INBOX/sent.md`** — the record of what this project has announced. A repeal can
falsify a claim already made in public, and the repealed sentence's distinctive
words are what find it.

```
a match in INBOX/sent.md
    -> file a correction post as its own [user] item, naming what was
       announced and what is no longer true
no match
    -> nothing further
```

**File the correction line rather than assuming one will be written.** The
announcement went out under the user's own account, so only they can correct it.

**Trace the ripple here rather than in the run.**

**An item whose completion happens outside this project names what would show it
done — or states plainly that nothing observable exists.** A URL that would
respond, a file that would appear, a branch that would be gone.

```
something observable exists   ->  name it. A later session checks the world
                                  instead of asking whether it happened.
nothing observable exists     ->  say so, in the item. The item then waits
                                  until the user mentions it.
```

**The second half carries as much weight as the first**, and is the part that gets
left out: it is what tells a later run to ask rather than check.

**Folding something into an existing item is two different operations. Say which
one you are doing, because they want opposite treatments:**

```
a MERGE          two accounts of the SAME thing
                 ->  REWRITE the host item so it carries the folded item's
                     facts in its own text — a pointer to another file is
                     extra information, never the incorporation — and state
                     what came out. Adding names what it replaces — the rule
                     gate's eviction step, one level down.

a SUPERSESSION   one account OVERTURNS the other
                 ->  APPEND, dated, naming what it overturns and why the old
                     reasoning lost — the throughline requires a defeated
                     alternative and its reason to survive.
```

**The test is binary and has an observable answer:** are these two accounts of one
thing, or is one overturning the other?

**A merge is expected to come out shorter.**

**This types the EDIT being made, not the reason being carried** — the reasoning
stays prose.

**An item that passes both limbs carries its instructions in its own prose,
written here.** Six things, one line each, in the item's text where the run
reads them:

```
which files change, and what changes inside each, a new path placed by the temporary-files rule and the Parts block
which files the work READS but does not change   # where any do
the observation that shows the change landed
the files that observation REACHES, named among the files that change
any option already refused, and why it lost      # one line each, where any
what the design RESTS ON, and when each was      # the external facts, one
  last verified                                    line each, where any
```

**The rests-on line names the external facts the design assumes — a tool's
capability, what an outside surface permits, a version, a finding filed
elsewhere — with the date each was last checked**, under the always-loaded
rule that a sentence resting on an outside fact or a condition names it
wherever it lives (skill-nonspecific-rules.md, Research and evidence filing).
**A rest without a date is what the buildability check's general limb reads**:
it means the fact has not been checked, and the item does not clear until it is.

**Write them for a reader with less of the project in view than you have, and
possibly less capability.** The session that builds this did not sit through the
conversation that designed it, so anything the work needs in order to start —
paths, names, values — is stated, not implied. **A kept item's prose opens with
one plain-language sentence saying what its subject is, before the rationale**,
a `[user]` item most of all.

**An observation reaches files of its own, routinely different ones — the test
suite that has to pass, the sibling document an acceptance check greps — so name
them among the files that change.** A build derives its file list from what an
item says it changes, and meets the observation's files only when the safety
check refuses them: it then has to stop and ask, which is the one thing a run
nobody is watching should not need to do.

**State what would be observed, not what would be asserted.** "The suite passes",
"a grep for the old wording returns nothing", "the section's first step is the
queue read" — each is something a build can check and either meets or does not.

**Refusals travel with the item because a build that cannot see why an option
was rejected proposes it again and stops to ask.** One line each is enough: the
option, and what defeated it.

**Name only files that change**, with a file the item has decided NOT to touch
stated in its own sentence apart from them. The digest reads every backticked
path where the changed files are named and cannot tell an excluded path from an
included one, so an exclusion written among them returns as a false merge
candidate.

**A Files entry whose content depends on a decision not yet made fails the second
limb**, rather than partly passing it. "Any affordance the link-address question
settles on" names a file and a purpose and supplies no decision, which is what
the limb asks for. **Prose that schedules a design decision into the build fails
the same way, however carefully phrased** — "to be settled at the start of the
build rather than during it" reads as care about sequencing and does the
opposite, because the start of the build is still the build. Two things the
clause tells apart:
- a decision — anything where two reasonable sessions would produce different
  work — made at planning;
- a tunable constant — a single value inside otherwise fully described work,
  which the item states, saying what it was derived from or that it was not,
  and naming what would settle it — chosen at planning and revisable once seen.
A lookup falls on the same test: one whose result cannot change the work's
shape is a constant the build reads; one whose result could change the design
is a decision.

**The disposal is a split, not a refusal.** The open question becomes its own
small item and the large one is held against it by slug. Most of such an item is
usually finished, and rejecting it whole would discard that.

**The second limb also asks whether this is work at all.** Ask what changes inside
which files and get "nothing" back, and the item is a **finding**, not work — its
home is `workshop/resources/` or the LOG under the three-way triage, not Processed. Route it
there and delete the queue item.

**And where an item asserts how a mechanism behaves, read the mechanism before
describing the build.** A capture's account of how something works is a claim to
test, not a fact to build on. An assertion that an operation is reversible or
recoverable is such a claim, and checking it means inspecting the actual target
— what would be destroyed, and whether it is genuinely held elsewhere — before
the item clears. An assertion that a file or folder is absent is checked with a
listing that shows hidden files, since absence is the one claim a normal
listing gets wrong silently.

**Two questions are settled before the build is described, and each is answered
in the item's prose:**

- **what is already on the shelf** — run the always-loaded research-index check
  (skill-nonspecific-rules.md, Research and evidence filing), and where the
  reasoning draws on a finding, cite the file rather than restating it;
- **what level the fix belongs at** — where the item fixes an instance of
  something more general, name whether the fix belongs at that instance, in a
  rule, or in a hook, and where a lower level is chosen over a higher one, say
  why.

**Nothing detects an uncited dependency, and this must not be described as
closing that.** The digest reports what an item names; an item that restates a
finding in its own words prints nothing.

**When one item is mixed — half fully specified, half not designable yet —
surface it as a choice about DESIGNING.** Ask *"shall we design the remainder
now, or split it off?"* — a filing question like "shall I split this item or keep
it whole?" hides the decision that is actually the user's.

```
design it now  ->  design the remainder in-session; keep the item whole
split          ->  buildable half   kept into Processed, passing both limbs
                                    on its own
                   undesigned half  returned to Unprocessed with the design
                                    progress made so far written into its
                                    prose, its own slug, cross-referenced
                                    from the kept half by slug
```

The split's mechanics are the decomposition sub-step in sub-step 3's Into Processed.
**A mixed item is designed out or split, and a failing limb is what decides
which** — a condition at /done requiring the unbuilt half to be re-filed later is
neither.

This is where a design item is caught: an item whose build list is *the design's
own output* fails the second limb by construction, so it never clears to run.

**Where the user asks to put work on a cycle, author the definition here, with
them present.** Write it into the project's cycles doc (`CYCLES.md` at the
project root, created on first use): the artifact, the steps of one turn, the
cadence — declared by the user or derived from the record, and the definition
says which — and **the observable that marks a completed turn**. The openings
and closes then compute due-ness from that observable and file a capture when a
turn is due; nothing stores a position.

**A definition's steps, criteria and observable pass the same test a kept item's
instructions do** — the buildability check's design-decision clause, applied at
authoring: no open class, no decision scheduled into the turn, stated concretely
enough that two sessions given the text produce the same turn.

It needs saying here because the check that catches this on a queue item runs at
the decision step, while a definition is written straight into the cycles doc by
the same pen — so a criteria paragraph reading "whatever would fail the
discipline" passed unchecked, delegating the criteria-selection decision to the
audit's own turn.

**An observable read from the project's own `LOG/` must be distinguishable from
the records planning itself writes.** A planning run writes one record per item
it processes, named by that item's slug — including the record for authoring the
cycle — so an observable reading "the most recent record under this cycle's slug"
counts the authoring record as a completed turn and reports the cycle as run
before it has ever run once. The cheap form, written into the definition: each
turn's record opens by saying that it records a completed turn, and the
observable reads only those records.

**And where the user asks for a named step list with no schedule, author it here
as a ritual** — into the same cycles doc, carrying the artifact, the steps,
**the word that fires it** in place of a cadence and an observable, and **the
paths its steps write**. A ritual is run when the user says its word and at no
other time, so nothing computes due-ness for one and nothing files a capture for
one.

**Write the paths as a `Writes:` field, and name them narrowly.** A planning
session may write only the project's own documents, and a ritual's steps often
need somewhere else — a build folder, a generated artifact — so the safety check
reads this field and permits exactly what it names:

```
**Writes:** `build-output/`, `dist/manifest.json`
```

The cost is stated rather than hidden: a declared path is writable whenever the
project is open, not only while its ritual runs. Nothing marks a ritual as
running, and the one exception that already worked this way has never needed
one. A ritual whose steps write nothing outside the standing list needs no field
at all.

**And where work is either shape, offer once, in the message already discussing
that item, never as a turn of its own:**

```
recurring-shaped   the same artifact worked repeatedly, a cadence visible
                   in the record            ->  offer a cycle
procedure-shaped   the same multi-step sequence done on request more than
                   once, no cadence         ->  offer a ritual
```

Creating either stays the user's call.

**And where a ritual turns out to have a cadence, re-author it as a cycle** —
the same steps gain the cadence and the observable that marks a completed turn.
The promotion is the user's call like the creation, and it is a rewrite of the
one definition rather than a second entry beside it.

**And before recommending a disposition, read the cycles doc for a definition
whose artifact this item touches; where one covers it, the recommendation names
that cycle and shapes the work as part of its turn** — a template, a step, a
material the turn reads — rather than as one-off work. An artifact that already
has a cycle has a home, and work written as a one-off lands outside it and is
done again next turn.

**Where an entry's prose says it came from an audit and has not been reviewed,
say so when you introduce it.** One clause: this came out of the such-and-such
audit and nobody has weighed it yet. The user's single evaluation of it then
happens knowingly, rather than on material they may assume was already vetted —
audit findings are filed straight to Unprocessed with no approval on the way in,
so this turn is the first time anyone has judged them.

Part of moving an entry into Processed is settling who does it and how: Claude-work by default or
`[user]`; and for Claude-work, its flavor. Claude places the item in Processed by
relationship judgment and reports where it went.

**Where an item's build produces a tool that measures or reports, file the
`[audit]` that runs it in the same planning run, placed immediately after
it.** The tool is the build; reading its output is the audit. Ordering works by
placement and needs no `Blocked by:` line, because a dev tool run directly is
live the moment it is written — one run can build the tool and then use it.

Stop and wait. The user decides.

**Fold the recommend into the action when the user already agreed** during the
interview — name the route in one line ("moving it into Processed — drafting the item
now") and go straight to sub-step 3.

```
A recommend may fold into the action ONLY when the agreement was
  - about THIS item, and
  - given in the exchange now happening, and
  - preceded by at least one earlier turn on this item's substance.
Not a prior turn. Not an adjacent item. Not a general "keep going",
"continue", or "yes" answering a different question.
In a multi-person session, the agreement that folds is the
execution-authority holder's own turn — another participant's yes
does not fold.
Absent that, the recommendation stands alone and WAITS.
```

**A design first shown in the offer message cannot fold.** The third condition
is what says so: where the item's substance reaches the user for the first time
in the same message that proposes its disposition, they have had no turn in
which to disagree, and agreement given there is agreement to a thing just met.
The disposition waits for its own agree / defer / something-else turn.

The checkpoint's "continue" answers *which item comes next*, never a disposition
of that item.

**Content belonging to a not-yet-presented entry is carried to that entry's own
turn and written then.** While processing one item it is natural to write the
settled answer into a neighbouring entry that has not come up yet. Once that
content is already written somewhere else, the only honest thing left to offer
at its turn is a confirmation — so the recommend-and-wait turn has nowhere to
stand, and the fold conditions above become easiest to skip at exactly the moment
they matter. The recorded instance: a project's user caught it themselves, their
words being *"you didn't make a recommendation."*

```
into Processed ->  CAN fold. The item is written and then reported, and the
            user can reject what was written and have it reverted — so folding
            loses no decision.
deleted ->  CANNOT fold to the action. It's terminal, with no later approval
            step, so explicit approval is still required — except where every
            part of the item's content has already been relocated in this same
            exchange, which is narrated rather than asked (see Delete below).
```

**Merge a clear delete recommend into the interview-closing turn**, so the route
is named once. Close the exposition on one combined bold ask that names what
survives the delete — related entries that stay, content already living
elsewhere, or "nothing else is affected": *"…my recommendation is to drop
this — the three captures it came from stay; anything you'd change, or shall I
delete it?"* That reply is the terminal
approval delete requires, so merging loses no decision — it drops the empty middle
turn. The standalone recommend-and-wait stays the path when the lean isn't clear.

**3. Execute the outcome**

**Into Processed** [DISCUSS, PROMPT] — Draft the processed item: its one-line description
(slug at the end, `[user]` leading if user-work) and the prose rationale carrying
the discussion's reasoning inline.

*When the item is `[user]`, **file it into the queue**:* genuine user work becomes
a `[user]` item there, rather than a live chat question or a "you'd do that
yourself" aside. Then draft the walkthrough into the item's prose. Where the
steps cannot all be scripted yet, file it with a rough walkthrough and
sharpen it here.

*Where a kept item produces text the user may edit — a draft, a post, an
article — write the item's drafting steps in the co-authored-draft shape* (the
`.txt` handed to the side panel, read back on their word — the walkthrough
sub-rule in skill-nonspecific-rules.md, which stays canonical there), and have
the draft step name where the draft lives: the session scratchpad by default,
or a project path only where the item's Files line names one.

**Run the THOROUGH capability check here — this is its site.** Restate the
question as *what would answer this?* **before** searching, then name the tool
that would do the work, or would produce the item's starting point — the
candidates include the method's own skills and flows and the tools on record in
`TOOLS.md`, not only external tools, and whether such a feature exists is answered
by reading the FAQ index, the record of what has been announced — and confirm
it is absent or unauthenticated. Trying a tool
is allowed where trying is quick: the user is in the room, which is what makes
this the heavy site. Where no tool plausibly exists, that is itself the answer.
**Aim the check at the one job in hand.** An inventory sweep of everything
available is expensive, stale by the next session, and was rejected. /next runs
a light version of this at its pre-hand-off, but the user is not in the room
there, so depth belongs here.

Two failures this catches. **Reason from what the task would actually take, not
from what it sounds like.** **And judge the search by whether it named the right
tool, not by how thorough it was** — the reframe from *where is this stored* to
*what would tell me the answer* is the load-bearing half.

**And check the index entry can be written.** If the candidate line for
`LOG/index.md` — the artifact touched and the nature of the change — cannot be
written yet because the work isn't specific enough, the item isn't ready for
Processed. Keep discussing. Same test as the two-limb build check above,
approached from the record's side.

*Decompose a mixed Claude-prep + user-step item.* When an item bundles work Claude
can do with an irreducible user action, split it:

```
Claude-doable parts  ->  build item(s)
the irreducible user action  ->  a single [user] item, reduced to ONLY that
                                 action, cross-referenced by slug
```

*If the item goes below the cleared-to-run line, place it destination-first too.*
Below the line means one of two things: a named queue item blocks this one, or a
date it must not be built before has not yet passed. Before writing the field,
ask whether this item and the one it waits on could simply run in order in one
run; where they could, the ordering is placement plus a sentence in the item's
prose naming what it follows, and the field is not written — the field hides
the entry from the run.

**Where the holding fact is a date, write the date and stop there** — a
`Not before: YYYY-MM-DD` line on the item, and no blocker item at all. The date
resolves itself.

Otherwise name the blocker, and **if that blocker is not already a queue item,
write it into Unprocessed first**, then write the held item with its
`Blocked by: [slug]` line — a reference resolves only once its target exists. If
nothing in the queue blocks the item, it belongs **above** the line. Where the
project's state server is registered, write either hold with its `hold_entry`
tool, which composes the line, refuses a dangling slug or a spent date, and
moves a cleared item below the line in the same call.

**Move the item with the mover, not by hand.** Rewrite the item's rationale
where it sits, then move the block with one command — it travels byte-for-byte,
so nothing is retyped:

```
python <plugin-root>/scripts/reorder_queue.py <QUEUE.md path> \
    --move-section <slug> Unprocessed Processed \
    [--position TOP|BOTTOM|BEFORE <anchor>|AFTER <anchor>] \
    [--marker-after <slug>|TOP|BOTTOM]
```

`--marker-after` places the readiness marker in the same call, so keeping an
item and clearing it is one command rather than two. The same script does the
below-the-line lift (`--move` within Processed) and skip-to-defer
(`--move <slug> BOTTOM`) — note that those two forms take the section name
before `--move`, which `--move-section` does not.

**`--position BOTTOM` with `--marker-after` sweeps the held region, whenever one
exists.** `BOTTOM` means the bottom of the whole Processed section, which is
*below* the held items — so the marker follows the item down there and every
held item lands above it, cleared. The hazard grows with the held region.

```
held region EMPTY      ->  --position BOTTOM --marker-after <slug> is safe
held region NON-EMPTY  ->  place the item with BEFORE <first held item>, and
                           name --marker-after <the last item that should stay
                           cleared> — never the item just placed
```

**Read the mover's report after every run, and confirm the marker sits where you
meant it to before continuing.** The tool says what it moved and where the
readiness marker ended up; that report is the confirmation, and a second run
fired without reading it can compound the first rather than correct it. **On a
mismatch, read the tool's usage before any second attempt** — the hazards above
are exactly the kind a re-guess repeats.

**Before clearing, apply done-plan.md's hold-back-unverified-work rule.** Where
this item's prose names a slug that LOG records as built but not yet verified,
place it into Processed **below** the line naming that slug as its blocker,
rather than clearing it. The rule's statement stays in done-plan.md — this is a
reference to it, not a second copy, so the two can't drift. The reason it is
needed here as well as at /done: /next runs before /done, so an item cleared
at a /plan opening can be built unattended the same day, on a foundation nobody
has confirmed.

**An item with no Unprocessed entry is appended to Unprocessed first, then
moved** — write it to the bottom of Unprocessed like any capture, then move it
with the command above, rather than hand-placing it into Processed.

**Then ask the digest for the next pick** — the `--next` command in Step 1
("Where what you need is the next pick"), with the opening's medians passed —
**and read its output.**

If the raw capture had no slug, give it one now. Report "moved to Processed as
[slug]" only after the move reported success.

**Fallback — by hand, when the script fails or refuses on a malformed file.**
Three edits in this order, all in the same turn: MARK the original by renaming
its heading to a unique placeholder (`#### MOVING-<slug> [<slug>]`), ADD the
item to Processed at the chosen placement, then DELETE the placeholder-marked
block. Destination-first, so an interruption leaves the item in Processed rather
than in neither section; the marking edit exists because after the add the file
holds two near-identical copies and the natural text to reach for matches both.
Re-run the digest afterwards either way.

*Split out a buried user-only prerequisite before moving the entry into Processed.* Scan the item's
rationale for a gating action that is both user-only and gates this or other work.
When found buried in prose, split it into its own `[user]` item with its own slug
and reference that slug from the original.

*Where the item's walkthrough is authored here, confirm the step can
actually produce the observation the item names* — where running the command is
harmless, run it. Trying is the smallest observation that settles the claim; a
try that produces the item's own deliverable has become the build, and stops —
the two-limb check asks for a description of the build, never a demonstration.
This is a different question from the capability check above:
that one asks whether Claude could do the *work*, this asks whether the *user's
step* yields the *evidence*. /plan is the only site where trying is free.

**Report the outcome as what the user would see** — where nothing is visible,
as what it means for their step — and never as the code or command read to
establish it.

**Process a surfaced risk with a red-flag marker** [DISCUSS, PROMPT] — the item gets
one extra line under its description: `Red flag · State: <cleared | uncleared>`.
Processing the risk *means* clearing it. Set **cleared** once this run designs
it out (record how) or the user is told plainly and chooses to proceed (record the
informed consent — what they were warned about and that they chose to go ahead).
An item only moves into Processed with its flag cleared; if it can't be cleared,
return it to the bottom of Unprocessed.

**Delete** — Remove the item from Unprocessed.

```
every part of the item's content has already been
  relocated in THIS exchange     ->  narrate the removal in one line, naming
                                     where each part went. Revertible on
                                     objection; no ask.
not worth doing                  ->  explicit approval, as a fate decision
                                     the user owns; the ask names what
                                     survives the delete — related entries
                                     that stay, content already living
                                     elsewhere, or "nothing else is affected"
```

**Relocate before removing when the
content belongs elsewhere.** Delete means "not worth doing," so routing a fold
through a plain delete risks dropping content the user wanted kept. When the
content belongs in another home — a SPEC sentence, a LOG entry, another item's
rationale — edit the target first with approval, then remove the standalone item.
Still a delete, just after its worth-keeping content has been carried across.

**Where an instruction spawns further tool calls beyond its own write, say in
one clause what that work still belongs to** — "still finishing the delete —
repairing two references it broke". Without it, follow-on work reads as the next
item starting, and the user loses track of where the run is.

**4. Checkpoint**  [PROMPT]

After every item, present the next item. That is the whole checkpoint.

**The specimen — this is the shape of the message:**

> Into Processed, cleared to run. Next up:
>
> **#### /done invites another /next in the same session [close-invites-same-session-next]**
> Captured by you (2026-08-13), from a live instance minutes earlier in another
> project running this plugin.
>
> **Take this one next?**
>
> 20 ready to build · 14 left to process.

Beneath the item: one bold question about that item, then the two counts, and
nothing else. No menu of routes, no analysis.

```
message order:
    1. where the just-finished entry landed, named as the outcome —
       "Deleted." / "Into Processed, cleared to run." / "Into Processed,
       held below the line." — so the user knows before meeting the next
    2. a one-line pointer to the NEXT item (item only, no analysis)
       — re-read from QUEUE.md first to confirm the pointer resolves
    3. one bold question inviting the user into THAT item ("Take this one
       next?") — never a fate question, which waits for the recommend step
       after the interview
    4. two numbers, on one line — how much work is READY to build (the size
       of the cleared region), and how many entries are still TO PROCESS,
       excluding anything dated out and anything skipped this session.
       Specimen: `20 ready to build · 9 left to process`
    5. nothing else. No menu of routes, no disposition tally.
```

**The pointer states the item's filed date when — and only when — the order in
play ranks by age.** That is the long-and-old rung and the alternating rung.
Under any other rung the pointer says nothing about age, because age is not why
this item came up and stating it would suggest otherwise.

```
ordering by age    ->  the pointer carries the date, read from the digest's
                       First seen field
any other rung     ->  no age in the pointer
```

Read the date rather than working it out: the digest computes First seen, and a
date derived any other way is the unfounded time statement the rules forbid.

**Four parts, and no fifth.** The date rides part 2's pointer.

**Both numbers are forward-looking, which is why both are here.** How much is
left to process tells the user whether to carry on now; how much is ready to
build tells them whether there is anything to run when they stop. Neither is a
record of what has been done.

**The banned tally is the retrospective one** — so many kept, so many deleted,
so many skipped — which is clutter at a moment the user is deciding about one
item. That ban stands and is untouched. It reaches a count of what this session
got through, and it never reached the size of the cleared region.

**The question is what the user answers; the recital is what was removed.** What
is banned here is the four-route recital ending in a named close — an ordinary
question about the item in hand is not that.

**If the rung has changed since the last pick, say so here in one clause**
(see the floor narration above). Only when it changed.

**This does not touch the end-of-queue gate**, which fires when the queue empties
and is deliberately worded not to lean toward closing. Leave it alone.

The verbatim here is that next item's own presentation, not a forbidden
look-ahead — the user acts on it immediately, so it's no [SEQUENCE] violation.

**Skip-to-defer.** Skipping is one of the four routes named at the start of
processing, and it is taken whenever the user says the word — a separate "dig in
or skip?" gate before every item would re-create the over-asking the method
removed.

```
on skip:
    don't re-present it this session — present the item after it
    LEAVE THE FILE ALONE — no move, no edit to QUEUE.md
```

**Skipping moves nothing and records nothing.** File position tells a human when
things landed.

**What that gives up:** a skipped item returns to the top next session and is
offered again. **Skipping stays unrecorded.**

A skipped item is not deleted and not processed. Next session it's ordinary
Unprocessed again.

Skipping the last item leaves Unprocessed non-empty, which is fine. On the last
item there's no next verbatim, so the message is just the off-ramps — worded
**neutrally** — "we can run the rescan first to catch anything decided
but never written down, then close the session and record it — or is there
anything else to capture or discuss?" — balanced between the two, with the command named
in words inside the sentence rather than at its end. An empty Unprocessed is a
resting state. That is the end-of-queue gate's first firing, subject to the
once-per-rest bound stated at the gate.

**Recommend skip-to-defer when an item won't design out this run**
[DISCUSS, PROMPT].
Skip isn't only the user's to pick. When you can't yet describe what an item's
build would change, or the design keeps opening more questions than it closes,
propose sharpening what you can and then skipping it to the bottom — rather than
reaching for a phantom "give it its own dedicated pass" container.

**What a skip must do — one subject, five provisions.** Skip to the bottom of
Unprocessed, and:

- treat that skip as the only defer there is; there is no dedicated-pass state;
- capture whatever design progress was made into the item's prose, so the next
  /plan starts further along;
- name what would settle the item and who owns that, where it was skipped for
  not designing out — a decision the user owns, a fact to be looked up, or a
  build that must ship first;
- ask before skipping, where that answer is a decision the user owns;
- write `Blocked by: [slug]`, where the thing it waits on is an entry already in
  the queue, subject to the blocker provisions below;
- propose a `Not before:` date, where it waits on something outside the project
  entirely, subject to the date provisions below;
- write either field with the state server's `hold_entry` tool where the
  server is registered — it composes the line and refuses a dangling slug or a
  spent date at the door.

Naming the blocker-in-kind turns an open item into an answerable one. **The ask is
the load-bearing provision:** enrichment substituting for a decision that was
available for the asking is the failure this fixes.

**The `Blocked by:` blocker on a capture** [SILENT]. The trigger is that
something already in the queue has to be settled first — a decision another
entry carries, a build this one is scoped against. Write the field naming that
entry; it needs no approval, because the queue can check it and the capture
returns by itself the moment the blocker is processed or built.

**Where nothing in the queue blocks it yet, file the blocker as a capture first,
then write the field.** A slug that resolves to nothing is a lint failure and a
hold nothing can lift — the same order the held region already requires.

**The `Not before:` date** [PROMPT]. This is the one place a capture gains one.
The trigger is that nothing in the queue can do what the item waits for — another
project's reply, a feature shipping in a tool nobody here controls.

```
name what it waits on, propose a date by when there is plausibly
news, and say plainly it will not be offered again before then
    user approves   ->  write `Not before: YYYY-MM-DD` on the capture
    user declines   ->  ordinary skip; it returns next session
```

**Write a date only on the user's approval, asked for in the moment.** A date on
a capture is the one hold that removes an item from view without anything
resolving, so the user decides how long they are content not to see it. Waiting
on someone's attention is not this — that is an ordinary skip.

**View-in-doc applies here too** — lead with a one-line pointer to the
next item in place of its verbatim, off-ramps below it unchanged.

### Process-now offer after a user raises something  [PROMPT]

When the *user* raises something fresh mid-/plan, offer the branch **before
writing anything — and before any analysis, design, or other work on the raised
thing: work delivered ahead of the offer spends the choice**. Close on the
offer rather than on a bare "anything
else?", which can read as parking their idea. The offer is made once per raised
thing, on either branch below: a reply on the thing's substance counts as
"process it now", and every later turn on it ends on that item's own
recommend-and-ask, never on the routing question again:

```
process it now   ->  RECOMMEND THIS. Loops straight into the present-and-
                     interview loop. NO capture is written: the item goes
                     into present-and-interview and is written once, as a
                     work item.
carry on         ->  write the capture; it waits in Unprocessed for its turn
(either way: anything else to add first?)
```

**Asking first is what saves the write.** A capture answered "process it now" is
immediately rewritten as a work item, so filing it first spends a write that is
thrown away — and by the user's own estimate that is the common answer.

**Lead with the recommendation rather than a flat menu.** The user's words:
*Claude should always recommend processing it now — it's just good context use.*

**What stays the user's:** whether to process it at all, and whether there is
appetite to carry on.

**The "anything else to add first?" clause is not optional**, and it belongs to
this branch only — it is what stops a user's idea being closed off before they
have finished the thought.

**When *Claude* raises something mid-/plan that may be work, ask once, at the
moment it is raised, before any write and before any analysis, design, or other
work on it: file it for later, or work it with you now — and
recommend working it now.** **The offer says "with you"** — processing is done
together, and an offer that reads as something Claude goes away and does primes
the user for the wrong interaction. An applied correction that may be method work still
gets the offer. The reason is identical on both branches: the capture
exists because this session's context produced it. **Recommend the route and
nothing else** — no clause inviting anything further, since this branch is barred
from soliciting further captures and a recommendation is the easiest place for
that bar to leak.
Work-it-now runs the ordinary present-and-interview loop and, if kept, places the
item straight into Processed.

No anything-else clause on this branch: asking would be soliciting further
captures off the back of Claude's own, which the always-loaded rule bars.

**Either branch, once it loops into present-and-interview, is subject to the
fold conditions above** — and a thing raised in this message has had no earlier
turn on its substance, so its disposition cannot fold into the same message
that introduced it.

**The timing answer is not a disposition, and the specimen is what shows it.**
"Process it now" answers *when*, and the recommendation on where it lands still has to be
put and still has to wait:

```
Claude   Want me to process that with you now, or carry on and file it for later?
         I'd take it now — it's fresh. Anything else to add first?

user     yes, now

Claude   [interview turn: what the item is, what it would change, what is
         still open — questions, not conclusions]

user     [answers]

Claude   [recommendation turn: what would be written, in plain words, then
         "Would you agree with that? If so I'll move it into Processed,
         cleared to run." — then STOP and wait]

user     [agrees, or doesn't]
```

Four turns and two separate asks. The failure this prevents is real and recorded:
a single "yes" to the timing question was read as approval for the disposition
too, and two items were written and cleared to run with no recommend-and-wait
turn between them.

### After all items

Unprocessed should be empty except items skipped this session; Processed holds the
kept work in order; section headers intact.

**Neutral end-of-queue gate** [PROMPT]. **Its precondition: it may fire only where
Unprocessed holds nothing but items skipped this session.** Anything else and this
gate is unavailable — with a full queue the only thing left to reach for is the
checkpoint, which presents the next item, and that is the correct behaviour.

**The precondition is the whole fix:** applied to a full queue this gate stops
being neutral and silently reclassifies everything still waiting as nothing left
to do.

When the queue empties, do **not** presume the session is over. An empty
Unprocessed is a resting state, not a stop signal. **The ask says in one line
what was passed over and why** — how many entries wait for a cycle's turn, how
many on other entries or on dates — naming any red-flagged capture outright
with what it waits on, so a queue that came to rest by passing everything over
is never reported as fully processed. Then ask one neutral question
— "we can run the rescan first to catch anything decided but never written
down, then close the session and record it — or is there anything else to
capture or discuss?" — and wait. The command is named in words and does not end the
sentence: the app lifts a trailing slash command into the composer, so an ask
ending on one is a keystroke from being answered by accident.

> Everything else in Unprocessed is set aside: four entries wait for a cycle's
> turn, two wait on other entries — one of them the red-flagged repository
> cleanup, which waits on the per-part specs — and one waits on a date. We can
> run the rescan first to catch anything decided but never written down, then
> close the session and record it — or is there anything else to capture or
> discuss?

**Ask once per rest.** The gate fires when the queue first empties. If the user
raises a further capture, file it and return to this same gate, but end plainly
this time — say the queue is clear again and stop, with no second ask.

**Each refill-and-emptying re-arms the ask.** Further work filling the queue and
emptying it again is a new rest, and the gate fires there as it did at the first
one — on a second refill as on any later one.

**A plain ending carries no close-leaning framing** — say the queue is clear and
stop; nothing that reads as an invitation to leave.

**Where the user declares they want the chat kept open to capture in, the
wrap-up ask is silenced for the rest of the chat**, refills included. Held in
the conversation; nothing is stored. It silences this gate only — /done runs
when it is invoked, so there is nothing there to silence.

The bound is held in the conversation; nothing is stored, which is all a
per-stretch bound needs.

New items from conversation follow the same loop — check QUEUE.md for overlap
first. If you notice a gap: "I notice [X] — want to hear a suggestion?"

/plan's close-out phase is retired and no longer exists. /plan plans; /done records and commits, and it
runs the wind-down re-scan at every close whatever the session type. The user's
exit is `/done`, named in the work cycle in the always-loaded rules and available
at every checkpoint.
