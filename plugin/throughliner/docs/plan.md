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
  `workshop/resources/research/`, `workshop/resources/supplied/`, the
  scratchpad, the memory directory, and the
  two FAQ templates (`faq-template.md`, `faq-index-template.md`). Everything
  else is work — including any other template, whose edit reaches every future
  consumer — and work is queued rather than done here. When the lock refuses a
  write, say in plain words what you were about to change and file it as a
  capture.
- **A recommendation is not a decision.** Whether an item is kept or deleted is
  still the user's call, and a written line is not an agreed one — the user can
  reject what was written, and it is reverted.
- **SPEC is a normal doc.** When a planning decision changes what SPEC says — a
  new capability, a scope change, a reworded rule (**the test: does any SPEC
  sentence go wrong or incomplete?**) — edit SPEC in that same /plan run, with
  the user present and approving. When a change touches no SPEC sentence, none of this
  applies. One other route exists: a large SPEC rework is its own piece of work,
  naming SPEC.md among its files like any other build.

  **Product truth is written here, at planning time** — the sentence is written
  ahead of the build.

  **So the decision step asks, on every item: does this change what SPEC says?** If
  yes, write the sentence now, with the user present, into the root
  `SPEC.md` — and before the new sentence is written, search the old
  sentence's distinctive words across `SPEC.md` and every document the
  project owns outside `LOG/`, the same search the decision step's
  repeal-trace limb already runs, and file one capture per document still
  saying the old thing, named by file; a search reaches documents carrying
  the words tried, and a sentence saying the old thing in other words is
  missed — and a goal whose "reached when" test now holds is rewritten or
  removed in the Goals section at the same turn.

  **Write a queued item so that a build reading SPEC alongside it finds the two
  in agreement.**

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

- **The one move, Unprocessed → Processed, is made here by discussing an entry
  and agreeing to move it.**
- **When placing an item into Processed — at the decision step, or when lifting one
  from below the line — keep `[user]` and `[audit]` lines end-preferred, as
  close-plan.md's reorder step requires.**
- **A user-credit stays on the item after processing** — see the provenance rule
  in skill-nonspecific-rules.md for what earns one.
- **Who does the work, and how.** Work is Claude's to build by default, and the
  flavor tags are in skill-nonspecific-rules.md. A `[co-write]` item — a text
  the user and Claude finish together, which the user asks for by saying they
  want to co-write something — names the one file the text lives in and says
  whether the text exists yet, and who leads — where the text already exists
  it is the user's, so Claude reads and responds, editing, questioning and
  continuing only where asked; where it does not, the decision step asks who
  drafts and writes the answer on the item — and sits last in the cleared region after every
  `[user]` item, unless a build is held on it by slug. A `[user]` item must carry a
  DESCRIBED walkthrough, settled here at the decision step — including that each step
  names the thing to click or type and the thing to look for, not just where to
  go. The requirement is stated in full in skill-nonspecific-rules.md; this is the
  moment it is applied.

- **`[freeform]` placement, for the uncommon case where one reaches the queue at
  all.** Either the user or Claude may designate it,
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
  run bound and ends the run before it — except that an item the run finds already done,
  its observable check satisfied before any step is driven, closes and the run
  continues, since the bound keys on the run performing the work; the marker
  binds /next and nothing else, so it does
  not stop the work being done alongside other work by hand.

- **Assign an uncommon execution marker only after re-reading its definition in
  that same turn, and name in the recommendation why this work matches it.**
  `[freeform]` and `Runs alone` are the two: rare enough that nothing keeps
  their difference fresh, close enough in shape to be reached for
  interchangeably, and each carries a consequence the other does not. The common
  markers — no tag, `[audit]`, `[user]` — are exempt.


## Step 1: Read state and entry question

**Where the session opening's lines say a newer version is on the user's
channel, offer the update here, once** [BRIEF, PROMPT].

**What the update turn carries.** The version named and the one installed; that the update is
the install guide's two commands — the marketplace refresh, then the plugin
update — run by Claude in this chat on the user's yes, and a full restart of
the app, which is theirs; and the one ask. Nothing runs without the yes, and a
no is taken once, with the check returning at its own weekly rhythm. Where the
opening's line says the install tracks a local folder, the turn offers nothing
and says so.

**Run the queue digest, then read QUEUE.md whole, then read SPEC.md.** Both, in
that order — the digest for the facts only a script can compute, then the file
for the reasoning it deliberately omits.

```
python <plugin-root>/scripts/queue_digest.py <QUEUE.md path>
```

**Read the runs-alone count as recession, not as staleness.** /next stops *before*
such an item, so every planning run that adds ready work pushes it further
back. It is a fact like every other digest line, and moving the item is the
user's decision.

**The rationale prose the digest omits comes from the read of the file** — an
instruction one item carries about another's ordering sits in that prose and
appears on no digest line.

**A cited slug that has a LOG entry means a record exists, and the record's KIND
says whether that work was built or only agreed.** The kinds print separately, and they carry different weight:

```
Cites shipped:    the record is a build's — that work is done. The citing
                  item's premise names finished work and is worth re-reading.
Cites processed:  the record is a planning session's — that work was discussed
                  and kept, and has not been built. A weaker premise still.
record kind       an older-format record, carrying neither marker. Reported as
  unknown         found and unclassified rather than guessed at.
```

**Tell the two apart by reading the record.**

**Read a cited-shipped flag as a premise worth re-reading; the ladder still sets
the order.**

**The files-named block lists merge candidates** — two items naming the same file
can often be settled together.

**Name the held work in the opening narration as a count plus changes: each
item whose hold changed since the most recent planning record — lifted,
re-dated, newly held — with what cleared or holds it, and the rest as one
count; and a passed-over capture that other captures wait on, named with what
it holds and how many wait on it.** The digest supplies the hold fields per
item, including the held-since date; where that date could not be attributed
the digest prints none, and the narration says the item is held without
claiming to know since when; and where the digest prints `by` a date, the
narration says the record's earliest sighting is that date rather than that
the hold was written then.

**Where this chat's own build working file still exists, say so plainly, once, in
the opening narration:** this chat has a build that has not closed, so lifts and
shipped-flags depending on that run's work will not resolve until /close runs. The
revisit still reads LOG and still skips silently — nothing else changes.

**Each of these reports a fact, never a verdict.** Read them as inputs to your
own judgment.

**Where the digest's size-signs block holds any sign — the same step of the
user's deferred run after run, the held region growing or a runs-alone item
with a rising count ahead of it, one part's work cleared while another's
waits, a part whose items cite only each other, the queue past one read, or
successive planning records ending with the same number left to process —
name it in one line of the opening narration, folded in the shape the other
checks use, and name the pop-out — setup run inside the part's folder — as
the thing the user may choose; quiet otherwise.** The FAQ's entry on project
size carries the signs only a person can read.

**Where the digest fails to run, the read still happens and the computed facts
are simply absent; say which of the two you have rather than reasoning from a
partial view.**

**Refresh it whenever the picture needs to be current.**

**Where what you need is the next pick, ask for that alone rather than
re-printing the whole digest:**

```
python <plugin-root>/scripts/queue_digest.py <QUEUE.md path> --next \
    [--skip <slug,slug>] [--picked <N>] [--medians <lines>,<YYYY-MM-DD>]
```

It answers only *what is next* — which rung the ladder fell to, that rung's top
item, where in the file it starts, and its text. Pass `--skip` for the entries
set aside this session and `--picked` for how many picks have been made. Pass
`--medians` with the two medians the opening printed — the section's median
entry length and median filing date; the output names the medians it used and
whether they were passed in or recomputed. Re-print the whole digest when the
whole picture is what you need.

**Then read the `LOG/index.md` lines newer than the most recent planning
session's record** — read with the state server's `planning_anchor` tool
where the server is registered, and otherwise found by that record's body
fields rather than its filename, since the per-entry split names planning
records by slug. Where no planning record exists, read the current month's
lines.

**Fold a line into the opening narration when it names a slug or a file the
current queue also names, and leave it out otherwise.**

What was read and what it touched rides the opening narration, and where
nothing in the window bears on today's queue the read joins the quiet clause:
**produce no separate output and no summary of the log for its own sake.**

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

Narrate the clear in one line.

**The specimen — this is the shape of the opening message:**

> Last session recommends starting with **[some-slug]**.
>
> ---
>
> Seventeen items cleared to run and four waiting to be processed. Three are
> held below the line, one of them lifted since the last planning record: its
> blocker shipped on 2026-09-14, per its record. Mail, issues, replies, cycles
> and the rule checks: nothing.
>
> **Anything you want to process first? Otherwise say go and I'll take them in
> the method's order.**

**Everything the step surfaces after the advisory folds into ONE opening
narration** [BRIEF], beneath the rule — the digest, the recent log lines, the
mail, the below-the-line revisit, the placement-contradiction flags, combined
into one "here's what came up: …", in this shape:
  - a finding gets a sentence;
  - every check that found nothing shares one clause ("mail, issues, replies,
    cycles and the rule checks: nothing");
  - the ask is the second line where nothing was found, the last line
    otherwise.

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

**The same step also checks the issue channel, in three limbs**
[SILENT] where `gh` is absent, or where there is neither an open outbound issue
nor a repository that can receive them; [BRIEF] where the channel exists —
what was found in either direction, or the quiet clause where nothing was.
Read the outbound register's open issue lines and check each with `gh` for
comments newer than the most recent planning session's record — its date
read with the state server's `planning_anchor` tool where the server is
registered, and computed from the record by hand otherwise; and where this
project has a repository that can receive issues, surface new incoming issues
the same way mail is surfaced. File one capture per issue carrying something
new, satisfied while an open capture already carries its slug. Issues stay on GitHub — nothing is copied into
`INBOX/`, and no state file records what was last seen; the anchor is computed
from the record.

**The third limb reaches issues on repositories this project does not own** —
the ones that bear on the work and belong to nobody here, like a bug in the tool
the method runs inside:

```
gh search issues --involves '@me' --state open
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

**Where the user mentions having done a `[user]` item**, close it at this
session's /close: log it under its slug and remove it from Processed.

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
line where it has one, and said plainly where it has none.

**Where an item's hold names work belonging to a subproject** — a project set
up inside this one, which `session_start` detects and reports — check it by
reading that subproject's log index rather than this project's. That is the one
circumscribed cross-project read; nothing else about the child is consulted, and
nothing here ever writes to it.

A deleted blocker means the held item's premise may not survive, so re-examine
it — **which is a fate decision, and therefore the user's.** That is the one
branch here that is a question for them.

Read shipped-ness off LOG. **"Shipped" here means built and
verified**, per close-plan.md's hold-back-unverified-work rule.
**Nothing else here is a question for the user.** Lifting is narrated; a
still-blocked item says nothing at all.

**Lift with the state server's `queue_move` tool where the server is
registered** — it moves the block byte-for-byte and places the marker in the
same call — and otherwise with the mover, which does the same:

```
python <plugin-root>/scripts/reorder_queue.py <QUEUE.md path> Processed \
    --move <slug> AFTER <the last item that should stay cleared> \
    --marker-after <the last item that should stay cleared>
```

**The section name is required and goes before `--move`.** Without it the script
exits with a usage message and writes nothing. **And `--marker-after` names the
last item that should stay cleared.**

Then drop the item's `Blocked by:` line and rewrite the entry whole, per the
decision step's rewrite-whole rule, saying what cleared it.
(Skip-to-defer needs no command at all — it moves nothing.)

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

**Cycles due-ness check** [SILENT] when the project has no cycles doc; [BRIEF]
whenever it has one. **The trigger is the session opening's cycles line**, which
names the doc, each definition's slug and what its observable currently reads.
Where the line is there, read the doc and say which cycles are due, whether or
not anything is filed. Compute each cycle's due-ness from its observable: read the observable's current state, and where a full
cadence interval has passed since the last completed turn, the cycle is due.
Where a cycle carries a chain, due-ness is per checklist: a checklist is due when
its computed date — reported on the opening's cycles line — has arrived, today's
date read from the state server's `clock` tool where the server is registered
and a shell clock command otherwise, and no
completed turn of this cycle is recorded since the previous anchor, and the
capture filed names that checklist in its heading, under the cycle's slug. A
cycle with no chain is unchanged.

```
cycle due, no open capture with its slug  ->  file ONE capture in Unprocessed
                                              under the cycle's slug, naming
                                              the due step, and carrying no
                                              `Cycle:` line — the slug is what
                                              ranks it; the line marks
                                              standing material the ladder
                                              passes over
cycle due, open capture already exists    ->  satisfied; file nothing. Where
                                              the turn was deferred to a
                                              date, the capture carries that
                                              date as `Not before:` on the
                                              user's yes, so the ladder
                                              passes it over until the day
                                              while it still holds the check
                                              satisfied by existing
cycle not due                             ->  file nothing
no cycles doc                             ->  nothing, silently — a project
                                              with no cycles pays nothing
```

A due cycle gets its sentence ("weekly release: due, filed"); cycles with
nothing due join the opening's quiet clause.

The capture then ranks by the ladder like any other work. The same check runs at
/next's pre-flight and /close's wind-down, filing only — this is the one site
that also processes what it files.

**Goals check** [SILENT] when nothing fires; [BRIEF] when something does. Read
each goal's "reached when" line in SPEC's Goals section against what it names —
the record, the cycles doc's observable or the queue — and say one line only
where a goal's test now holds, or where no entry in either queue section names
the goal's words; and where a goal's "reached when" names something the record
no longer has, or names work now cleared or built that would satisfy it, the
check proposes a rewrite of that goal in one line, written on the user's yes at
that turn; quiet otherwise, folded into the opening's quiet clause. The
limit: the check cannot tell that a goal is no longer wanted; that stays the
user's read.

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

**This pass only ever deletes; moving an entry into Processed stays one item at a time.** If nothing is
obviously droppable this beat doesn't fire at all — say nothing and go to beat 2.

**The ask is the drop itself, at any batch size, with keeping named as the
alternative in the sentence before it.**

> "Two look droppable — 1. **[old-slug]**: its premise is gone, the feature it
> targeted was cut. 2. **[dupe-slug]**: duplicates **[other-slug]**. Say which to
> keep, if any. Drop both?"

> "One looks droppable — **[old-slug]**: its premise is gone, the feature it
> targeted was cut. Say so if you would rather keep it. Drop it?"

**Beat 2 — the ordering ask** [PROMPT]. One question: **"Anything you want to
process first? Otherwise say go and I'll take them in the method's order."**
One question, not a menu —
the only alternative offered is the user's own priorities. A user with something
on their mind answers it here.

**Where an uncleared red flag tops the order, the flag is the recommendation
and the ask is "Start with the flag?"**, with naming something definitely more
important stated as the alternative before it — e.g. "An unaddressed privacy
risk is first up. Name something else only if it is definitely more important.
Start with the flag?"

**A subset the user names sets the ORDER, not the length of the run.** When
those items are done, the checkpoint simply presents the next item, exactly as it
does after any other item. Naming three things to start with is not a statement
that the run ends after three.

**Where mail is waiting, that question carries it instead: "There's mail waiting
— process that first, or say go and I'll take the rest in the method's
order."** Still one question, and
it is what gives the mail step its teeth: a question the user answers, rather
than a step that can be passed over.

(If Unprocessed is empty there's nothing to order, so offer seeding from SPEC by
name instead — the step above. If SPEC is thin too, it's an ordinary conversation
about what they want next.)

If the user raises something to discuss, handle it via the Step 2 loop, then ask
"anything else before we go through the queue?" — repeat until nothing more.
**Then process the unprocessed work.** A discussion item is an optional first
stop on the way to it.

## Step 2: Process work  [SEQUENCE]

**Showing the one next item the user is about to act on is presentation, not a
preview**, so the checkpoint below satisfies `[SEQUENCE]`.

**/plan writes no working file.** Each item's disposition and reasoning go into
that item's own rationale in QUEUE.md as it is processed, and into the
session's record, one entry per item.

**Run the scrub checklist before writing a kept item's text**
(skill-nonspecific-rules.md, Scrub before writing).

**Read the same text against its shape's bound** (skill-nonspecific-rules.md,
Authoring standard). An item long because it holds two pieces of work splits into
two; an item long because it carries a narrative relocates that to the record and
cites it.

**Read the ITEM AS IT STANDS, not the paragraph being added, and where the entry
already carries a dated settlement or skip paragraph, rewrite the entry whole
rather than appending to it** — carrying forward every defeated alternative with
the reason it lost, and keeping a quotation claim over verbatim text only. It
fires at three moments:
- the decision step, where an entry is kept;
- a lift or re-hold at the opening's revisit of held work;
- a skip that writes design progress, at the checkpoint or at this step's
  skip-to-defer.
Where history is relocated, it goes to the session's record and the entry cites
the record by filename.

**Process order.** Unprocessed top to bottom, then items raised in this session's
own discussion. State the count upfront, counting both together ("5 items.
First: …"). Position in the file *is* the order — an item placed next to its
relatives is processed there by design.

The droppable set was already handled at Step 1's opening (beat 1), so the
survivors are what's left to order.

**Start-of-processing reorder** [SILENT]. Apply the order the
user chose at beat 2 — their own priorities if they named any, otherwise the
default, **unblock-potential**: the item whose processing would let the most other
work move forward goes first. The digest's printed medians fix the
ladder's membership for the whole pass — they are read there, and quoted at the
user nowhere.

**Pass over any Unprocessed entry carrying a `Not before:` date still ahead**
[SILENT], whatever the order would otherwise do with it. On a capture the field
means hold this back until the date, so such an entry is not ranked, not
presented and not counted toward the session's floor. Take it up in the ordinary
way once the date has passed — the digest prints `Not before: <date> ->
passed/ahead` on every entry.
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
capture held on it returns in the session it is kept — except that a line
ending `until built` passes the capture over until every named entry has a
build record; the digest prints each named blocker's
resolved state on the capture's own line.

**Pass over any Unprocessed entry whose `Cycle:` names a definition in the
project's cycles doc** [SILENT], on the same terms. The field says which cycle
owns the entry as its material, so that cycle's turns draw from it and the
ranking does not: it is not ranked, not presented and not counted toward the
session's floor. A `Cycle:` naming a definition that is not in the doc ranks
normally, so deleting a cycle releases its material by itself — the same
self-lifting shape as the two arms above, and the digest prints the field. All
three pass-overs read a field the digest prints, so none needs judgment.

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

The ladder is never surfaced to the user.

The reorder is **conditional and change-scoped**, not a full re-derivation:
consider only what changed since last session (items newly captured, dropped, or
whose relationships shifted — read the slug-references items already carry), and
if the order already sits right, leave it.

**State the four routes here, once** — *"I'll work through
these one at a time; say skip, stop, or run the close command whenever you like — or, where an item is someone else's to do, say whose."* This is the only place
they are recited; the last route is spoken only where the project holds more
than one person, and it rewrites the entry's `Assigned to:` line in one line. **Close that same message on the first item itself**: a pointer
to it, its plain-English summary and its analysis, ending on the interview's own
ask — the ordering answer was the yes, so no "start with this one?" is asked. The
per-item checkpoint then presents just the next item.

**Re-check the rung at every pick.** A rung can change mid-session — a red
flag arrives, the item holding
everything up gets processed, or the long-and-old group empties into rung 5 —
even though the bottom rung no longer runs out.

**A rung can become live again rather than only run out, so re-check reads in
both directions.**

### For each item

**1. Present and interview**  [DISCUSS, PROMPT]

**Every item's discussion — the first and every one after — opens with a
plain-English summary of what the item says, inline, before any analysis.**

**What the summary turn carries.** Four requirements, about what the turn
carries and what the reader can resolve without the scrollback:

```
CARRIES                       what the item is and what is open, and nothing
                              else. A defeated alternative, a not-blocking
                              note and the reasoning behind the entry stay in
                              the entry for a later session and come out on
                              request.
ONE PER LINE                  where the summary names more than two things,
                              they are written one item per line, never bold
                              fragments inside a paragraph.
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
first item        ->  the processing pass OPENS on the ordering answer: the
                      order narration and the floor line, the four routes, a
                      pointer to the first item, its summary and its analysis,
                      in ONE message ending on the interview's ask
every item after  ->  its pointer was already sent at the prior item's
                      checkpoint — still open with the summary, then the
                      analysis, in the SAME message
```

**What the first-item turn carries.** The four routes, the pointer to the
first item, that item's summary and its
analysis, and the interview's own ask at the end — whether the ordering answer
was go or the user's own named priorities, since either is an
instruction to proceed.

**As part of the interview, ask what would answer this item's open questions.**
Where the answer is something outside what you can read — a current version,
whether a feature exists, what a tool actually does — run it, here, and report
what it found. Where it is a choice they own, ask.

**Once the user has taken an item, presenting it and beginning to work it is one
beat** — the summary and the analysis arrive together, and the wait that follows
is the [PROMPT] at the end of the interview.

Read the item's entry whole from QUEUE.md before its summary is written, and
write the summary from that read — at the opening for the first item, and at
the prior checkpoint for every one after. The whole read is what confirms the
pointer resolves.

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
lead with a one-line pointer instead of the pasted quote.

**The opening specimen — the first item folded into the ordering answer:**

> I'll work through these one at a time; say skip, stop, or run the done
> command whenever you like.
>
> First item — **[work-slug]** — is in [QUEUE.md](QUEUE.md) under Unprocessed.
> It says <plain-English summary of the entry>. <The analysis: what would
> change, and what is open.>
>
> **<The interview's own ask — the combined recommend-and-ask where nothing is
> open, or the open question where one is.>**

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
NAMES          any earlier build or decision on the same mechanism found by
               the decision step's grep of the index, with what it did and
               why it was changed or undone, read from the entry rather than
               the line — or that the index holds nothing, said in one clause.
SHAPE          where the change names more than two files or actions, a
               numbered list — each item a bold verb-first label and one
               plain sentence saying what happens to which file — with the
               plain-words opening still first.
FILES          the turn ends, above its ask, with the files that change, one
               per line, names only, read off the item's Files line.
```

A search reaches lines carrying the words tried, so an earlier attempt indexed
under other phrasing is missed, and this narrows the repeat rather than
closing it.

**Bold the recommendation's first sentence**, so the recommendation is findable
without reading the turn to locate it. The shape, for a change touching three
things:

> **The close would empty the temp folder of drafts already sent, so the pile
> stops growing.**
>
> 1. **Delete** each draft whose send is on the register, at the close.
> 2. **List** whatever else the folder holds, and ask once before clearing it.
> 3. **Say** in the FAQ that the close does this.
>
> close.md
> faq-template.md
>
> **Do that?**

**Write the ask as one fixed formula every time — "Do <the recommendation>?", or
as near as grammar allows.** Where the turn delivers alternatives, the ask is still single — the
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
whatever they answer. Who authored which part is settled by the provenance rules' containment test and
written into the item as mixed where it is mixed.

**The question asks about the recommendation, never about the mechanics.** An ask
that reads "move it into Processed, cleared to run?" asks about the filing, so a
natural answer — "agreed", "as you recommend" — answers a question nobody put.

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
removed or rewritten, not just the topic — and where the answer is only the
next slice and never the whole, the entry is not returned to Unprocessed to
come back: its outcome is written as a goal with a "reached when" line at
that turn, with the user present, and the next slice alone is kept as work. **This is a blocking check, not a prompt
to try harder:** before recommending it, state the build in both limbs — the
files that change AND what changes inside them — and if either limb can't be
stated, the entry cannot move into Processed.

Naming files alone is not passing, and the second limb asks one more thing of
each file named: would the run's safety check permit the write? A build may
write its own Files list, and never QUEUE.md beyond removing each item as it
is ticked, another project's folder, or the gitignored mailbox — so an item
naming a file a build may not write does not clear, and an item whose
described work touches `SPEC.md` — the root's or a part's — clears only where
`SPEC.md` stands in its Files line itself, since a sentence saying it does is
not the line the safety check reads. Where the item's work is
amending a queue entry's own wording, that is planning work: make the change
now, at this decision step, or file it as a capture for the next planning
session — never clear it as a build, which would sit skipped by every run with
nothing reporting why. An item that can't pass both limbs gets sharpened
further in the interview, or skip-to-deferred with its design progress written
in by rewriting the entry whole, per the rewrite-whole rule above. Those two
are the only routes open to it. Where the item
carries the line `Build block written by the format migration on …, not yet
checked at planning`, running this check on it removes that line, whichever
way the check goes.

**The general limb, keyed on the rests-on line: an item whose design rests on
an external fact carrying no date it was last verified fails the check until
that read is done here, at the decision step.** It reaches every kept item — a
build as much as a walkthrough step. An
item whose whole deliverable is such a fact is the read itself: it is done
now and never queued.

**Third limb: where an item changes how a mechanism behaves, or repeals or
rewords a specific sentence or value, grep the mechanism's or the sentence's
distinctive words across the project before writing the Files line, and
across the `LOG/index*.md` files, opening any matching entry — and open
`LOG/backlinks.md` at the mechanism's key and the item's cited slugs, where
the file exists, reading the records it lists; a record naming the mechanism
by neither its slug nor its package name is still missed.**

```
the Files line is derived FROM the grep, not from the discussion
    -> the grep names every doc, template and FAQ entry carrying the words
    -> anything the grep finds and the item does not want changed is stated
       as an exclusion, in its own sentence outside the Files line
    -> the index's matching lines name what was done to this mechanism
       before; the entry says why, and the recommendation carries it
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

**File the correction line rather than assuming one will be written.**

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

**A merge is expected to come out shorter.**

**An item that passes both limbs carries its instructions in its own prose,
written here.** Six things, one line each, in the item's text where the run
reads them:

```
which files change, and what changes inside each, a new path placed by the temporary-files rule and MAP.md where the project has one
which files the work READS but does not change   # where any do
the observation that shows the change landed
the files that observation REACHES, named among the files that change
any option already refused, and why it lost      # one line each, where any
what the design RESTS ON, and when each was      # the external facts, one
  last verified                                    line each, where any
```

**The rests-on line names the external facts the design assumes — a tool's
capability, what an outside surface permits, a version, a finding filed
elsewhere — with the date each was last checked** (skill-nonspecific-rules.md,
Research and evidence filing).
**A rest without a date is what the buildability check's general limb reads**:
it means the fact has not been checked, and the item does not clear until it is.

**Write them for a reader with less of the project in view than you have, and
possibly less capability.** The session that builds this did not sit through the
conversation that designed it, so anything the work needs in order to start —
paths, names, values — is stated, not implied, and a command that runs in one of
a nested project's repositories names only commits from that repository's log. **A kept item's prose opens with
one plain-language sentence saying what its subject is, before the rationale**,
a `[user]` item most of all.

**An observation reaches files of its own, routinely different ones — the test
suite that has to pass, the sibling document an acceptance check greps — so name
them among the files that change.**

**State what would be observed, not what would be asserted.** "The suite passes",
"a grep for the old wording returns nothing", "the section's first step is the
queue read" — each is something a build can check and either meets or does not.

**One line each is enough for a refusal: the option, and what defeated it.**

**Name only files that change**, with a file the item has decided NOT to touch
stated in its own sentence apart from them.

**A Files entry whose content depends on a decision not yet made fails the second
limb**, rather than partly passing it. **Prose that schedules a design decision
into the build fails the same way, however carefully phrased** — "to be settled
at the start of the build rather than during it" reads as care about sequencing
and does the opposite. Two things the clause tells apart:
- a decision — anything where two reasonable sessions would produce different
  work — made at planning;
- a tunable constant — a single value inside otherwise fully described work,
  which the item states, saying what it was derived from or that it was not,
  and naming what would settle it — chosen at planning and revisable once seen.
A lookup falls on the same test: one whose result cannot change the work's
shape is a constant the build reads; one whose result could change the design
is a decision.

**The disposal is a split, not a refusal.** The open question becomes its own
small item and the large one is held against it by slug.

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
listing gets wrong silently. An item that names something inside a file — a
section, a block, a heading it will edit — has that file opened here and the
named thing confirmed in it, and does not clear where it is not there.

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
which.**

**Where the user asks to put work on a cycle, author the definition here, with
them present.** Write it into the project's cycles doc (`CYCLES.md` at the
project root, created on first use): the artifact, the steps of one turn, the
cadence — declared by the user or derived from the record, and the definition
says which — and **the observable that marks a completed turn** — written with
the state server's `cycle_define` tool where the server is registered, which
refuses a taken slug, a cadence with no derivation and a chain naming an
undefined checklist at the door, and with the editing tools otherwise. The
openings and closes then compute due-ness from that observable and file a
capture when a turn is due; nothing stores a position.

**A definition's steps, criteria and observable pass the same test a kept item's
instructions do** — the buildability check's design-decision clause, applied at
authoring: no open class, no decision scheduled into the turn, stated concretely
enough that two sessions given the text produce the same turn. Three things the
test reads for, subordinate to it:
  - the due rule, named as one of two — **time-based**, a cadence, or
    **condition-based**, an observable read against a condition — with the
    record that closes a turn named as such;
  - for every step, what fires it — a date, a word, or the step before it —
    and who performs it, Claude or the user; a step naming neither is refused
    at authoring, and a default stated once for the definition ("each step
    fires on the one before it and is Claude's unless the step says
    otherwise") names both for every step it covers;
  - where a cycle chains checklists, the chain written as a **close calendar**
    — each earlier checklist counted back from the anchor with its lead, "two
    days before, the day before, the day".

**An observable read from the project's own `LOG/` must be distinguishable from
the records planning itself writes.** The cheap form, written into the
definition: each turn's record opens by saying that it records a completed
turn, and the observable reads only those records.

**And where the user asks for a named step list with no schedule, author it here
as a checklist** — into the same cycles doc, carrying the artifact, the steps,
**the word that fires it** in place of a cadence and an observable, and **the
paths its steps write**. A checklist is run when the user says its word and at no
other time, so nothing computes due-ness for one and nothing files a capture for
one.

**Write the paths as a `Writes:` field, and name them narrowly.** A planning
session may write only the project's own documents, and a checklist's steps often
need somewhere else — a build folder, a generated artifact — so the safety check
reads this field and permits exactly what it names:

```
**Writes:** `build-output/`, `dist/manifest.json`
```

The cost is stated rather than hidden: a declared path is writable whenever the
project is open, not only while its checklist runs. A checklist whose steps
write nothing outside the standing list needs no field at all.

**And where work is either shape, offer once, in the message already discussing
that item, never as a turn of its own:**

```
recurring-shaped   the same artifact worked repeatedly, a cadence visible
                   in the record            ->  offer a cycle
procedure-shaped   the same multi-step sequence done on request more than
                   once, no cadence         ->  offer a checklist
material-shaped    many entries of one kind arriving over time for a
                   cycle's or checklist's turns
                                            ->  offer a pool file, named in
                                                the definition's material
                                                paragraph and its `Writes:`
                                                field, so the queue carries
                                                only the due turn
```

Creating any of the three stays the user's call. The `Cycle:` field stays for a
definition's few standing entries; the pool file is for the accumulating kind.

**And where a checklist turns out to have a cadence, re-author it as a cycle** —
the same steps gain the cadence and the observable that marks a completed turn.
The promotion is the user's call like the creation, and it is a rewrite of the
one definition rather than a second entry beside it.

**And before recommending a disposition, read the cycles doc for a definition
whose artifact this item touches; where one covers it, the recommendation names
that cycle and shapes the work as part of its turn** — a template, a step, a
material the turn reads — rather than as one-off work.

**Where an entry's prose says it came from an audit and has not been reviewed,
say so when you introduce it.** One clause: this came out of the such-and-such
audit and nobody has weighed it yet.

Part of moving an entry into Processed is settling who does it and how: Claude-work by default or
`[user]`; where the project holds more than one person, whose it is to do,
written as the entry's `Assigned to:` line; and for Claude-work, its flavor — a capture asking for a check is a
build where every hit has one fix and the search is written into the item, so
the build derives its sites from it, and an `[audit]` otherwise. Claude places the item in Processed by
relationship judgment and reports where it went.

**Where an item's build produces a tool that measures or reports, file the
`[audit]` that runs it in the same planning run, placed immediately after
it.** The tool is the build; reading its output is the audit. Ordering works by
placement and needs no `Blocked by:` line.

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

The checkpoint's "continue" answers *which item comes next*, never a disposition
of that item.

**Content belonging to a not-yet-presented entry is carried to that entry's own
turn and written then.**

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
delete it?"* The standalone recommend-and-wait stays the path when the lean
isn't clear.

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
article, a deck, a form's wording — write the item's drafting steps in the
co-authored-draft shape* (the `.txt` handed to the side panel, read back on
their word — the walkthrough sub-rule in skill-nonspecific-rules.md, which
stays canonical there). Before the draft's home is named, choose the medium:
ask whether the user will be editing this somewhere Claude cannot reach, and
whether an equally good medium exists where Claude can; choose by three tests
in order — the user can write in it, otherwise it is not co-writing; Claude
can write in it across as many stages as possible; it is the right final
form for delivery — and write the chosen medium on the item. Then have the
draft step name where the draft lives: for plain text, a `.txt` in the
project's `temp/` folder by default, or a project path only where the item's
Files line names one.

**Run the THOROUGH capability check here — this is its site.** Restate the
question as *what would answer this?* **before** searching, then name the tool
that would do the work, or would produce the item's starting point — the
candidates include the method's own skills and flows and the tools on record in
`TOOLS.md`, not only external tools, and whether such a feature exists is answered
by reading the FAQ index, the record of what has been announced — and confirm
it is absent or unauthenticated; and ask whether a permission or a rule, rather
than incapability, keeps Claude out — where it does, the step's text opens
with the say-so offer the always-loaded rule's third answer names. Trying a tool
is allowed where trying is quick: the user is in the room, which is what makes
this the heavy site. Where no tool plausibly exists, that is itself the answer.
**Aim the check at the one job in hand.**

Two failures this catches. **Reason from what the task would actually take, not
from what it sounds like.** **And judge the search by whether it named the right
tool, not by how thorough it was** — the reframe from *where is this stored* to
*what would tell me the answer* is the load-bearing half.

**And check the index entry can be written.** If the candidate line for
`LOG/index.md` — the artifact touched and the nature of the change — cannot be
written yet because the work isn't specific enough, the item isn't ready for
Processed. Keep discussing.

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
nothing in the queue blocks the item, it belongs **above** the line. Write
either hold with the state server's `hold_entry` tool, which composes the line,
refuses a dangling slug or a spent date, and moves a cleared item below the
line in the same call; a project with no server registered writes the line
with the editing tools and moves the item with the mover below.

**Move the item with the state server's `queue_move_section` tool where the
server is registered, and otherwise with the mover — never by hand.** Rewrite
the item's rationale where it sits, then move the block with one call — it
travels byte-for-byte, so nothing is retyped. The mover's form, for a project
with no server:

```
python <plugin-root>/scripts/reorder_queue.py <QUEUE.md path> \
    --move-section <slug> Unprocessed Processed \
    [--position TOP|BOTTOM|BEFORE <anchor>|AFTER <anchor>] \
    [--marker-after <slug>|TOP|BOTTOM]
```

`--marker-after` places the readiness marker in the same call, so keeping an
item and clearing it is one command rather than two. The below-the-line lift
and skip-to-defer are the server's `queue_move` tool where it is registered;
the same script does both otherwise (`--move` within Processed, and
`--move <slug> BOTTOM`) — note that those two forms take the section name
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

**Before clearing, apply close-plan.md's hold-back-unverified-work rule.** Where
this item's prose names a slug that LOG records as built but not yet verified,
place it into Processed **below** the line naming that slug as its blocker,
rather than clearing it.

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
block. Re-run the digest afterwards either way.

*Split out a buried user-only prerequisite before moving the entry into Processed.* Scan the item's
rationale for a gating action that is both user-only and gates this or other work.
When found buried in prose, split it into its own `[user]` item with its own slug
and reference that slug from the original.

*Where the item's walkthrough is authored here, confirm the step can
actually produce the observation the item names* — where running the command is
harmless, run it. A try that produces the item's own deliverable has become the
build, and stops — the two-limb check asks for a description of the build,
never a demonstration.

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

**Delete** — Remove the item from Unprocessed, with the state server's
`queue_delete` tool where the server is registered and otherwise with the
mover's `--delete <slug> Unprocessed`.

```
every part of the item's content has already been
  relocated in THIS exchange     ->  report it as the outcome word followed by
                                     a link to each file a part went to —
                                     "Deleted — [QUEUE.md](QUEUE.md),
                                     [SPEC.md](SPEC.md)." — an entry's slug
                                     after a link only where the destination
                                     needs telling apart, and no sentence
                                     describing the relocation. Revertible on
                                     objection; no ask.
not worth doing                  ->  explicit approval, as a fate decision
                                     the user owns; the ask names what
                                     survives the delete — related entries
                                     that stay, content already living
                                     elsewhere, or "nothing else is affected"
```

**Relocate before removing when the content belongs elsewhere.** When the
content belongs in another home — a SPEC sentence, a LOG entry, another item's
rationale — edit the target first with approval, then remove the standalone item.

**Where an instruction spawns further tool calls beyond its own write, say in
one clause what that work still belongs to** — "still finishing the delete —
repairing two references it broke".

**4. Checkpoint**  [PROMPT]

After every item, present the next item. That is the whole checkpoint.

**The specimen — this is the shape of the message:**

> Into Processed, cleared to run. Next up:
>
> **#### /close invites another /next in the same session [close-invites-same-session-next]**
> Captured by you (2026-08-13), from a live instance minutes earlier in another
> project running this plugin.
>
> **Take this one next?**
>
> 20 cleared to run · 14 left to process.

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
    4. two numbers, on one line — how much work is CLEARED to run (the size
       of the cleared region), and how many entries are still TO PROCESS
       counting the one just presented, which is the `Left to process, this
       one included` line the next-pick tool prints, and is never counted by
       hand — so a last item reads `1 left to process`, never 0.
       Specimen: `20 cleared to run · 9 left to process`
    5. nothing else. No menu of routes, no disposition tally.
```

**The pointer states the item's filed date when — and only when — the order in
play ranks by age.** That is the long-and-old rung and the alternating rung.
Under any other rung the pointer says nothing about age.

```
ordering by age    ->  the pointer carries the date, read from the digest's
                       First seen field
any other rung     ->  no age in the pointer
```

**Skip-to-defer.** Skipping is one of the four routes named at the start of
processing, and it is taken whenever the user says the word.

```
on skip:
    don't re-present it this session — present the item after it
    LEAVE THE FILE ALONE — no move, no edit to QUEUE.md
```

A skipped item is neither deleted nor processed, and returns as ordinary
Unprocessed next session.

Skipping the last item leaves Unprocessed non-empty, which is fine. On the last
item there's no next verbatim, so the message is just the off-ramps — worded
**neutrally** — the closing paragraph as the end-of-queue gate's specimen
states it, ending on its standalone bold ask, with each command named in words
inside the sentence rather than at its end. An empty Unprocessed is a
resting state. That is the end-of-queue gate's first firing, subject to the
once-per-rest bound stated at the gate.

**Recommend skip-to-defer when an item won't design out this run**
[DISCUSS, PROMPT].
Skip isn't only the user's to pick. When you can't yet describe what an item's
build would change, or the design keeps opening more questions than it closes,
propose sharpening what you can and then skipping it to the bottom.

**What a skip must do — one subject.** Skip to the bottom of
Unprocessed, and:

- write whatever design progress was made into the item by rewriting it whole,
  per the decision step's rewrite-whole rule, so the next /plan starts further
  along;
- name what would settle the item and who owns that, where it was skipped for
  not designing out — a decision the user owns, a fact to be looked up, or a
  build that must ship first;
- ask before skipping, where that answer is a decision the user owns;
- write `Blocked by: [slug]`, where the thing it waits on is an entry already in
  the queue, subject to the blocker provisions below — on a capture, ending the
  line `until built` where it waits for that entry to ship rather than to be
  designed, so the hold says which of the two it waits for;
- propose a `Not before:` date, where it waits on something outside the project
  entirely, subject to the date provisions below;
- write either field with the state server's `hold_entry` tool — it composes
  the line and refuses a dangling slug or a spent date at the door — and with
  the editing tools only in a project with no server registered.

**The `Blocked by:` blocker on a capture** [SILENT]. The trigger is that
something already in the queue has to be settled first — a decision another
entry carries, a build this one is scoped against. Write the field naming that
entry; it needs no approval, because the queue can check it and the capture
returns by itself the moment the blocker is processed or built. Say which of
the two it waits for: a capture waiting on the decision another entry carries
is written bare and returns when that entry is kept; one waiting on the build
ends its line `until built` and returns when the entry has a build record.

**Where nothing in the queue blocks it yet, file the blocker as a capture first,
then write the field.**

**The `Not before:` date** [PROMPT]. This is the one place a capture gains one.
The trigger is that nothing in the queue can do what the item waits for — another
project's reply, a feature shipping in a tool nobody here controls.

```
name what it waits on, propose a date by when there is plausibly
news, and say plainly it will not be offered again before then
    user approves   ->  write `Not before: YYYY-MM-DD` on the capture
    user declines   ->  ordinary skip; it returns next session
```

**Write a date only on the user's approval, asked for in the moment.** Waiting
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
Claude's lean decides, and the lean is stated:
process it now   ->  where processing it would change this session's work,
                     or the thing is not yet complete: PROCEED with no ask.
                     The interview opens on it in the same reply. NO capture
                     is written: the item goes into present-and-interview
                     and is written once, as a work item. The user can add
                     to it during processing, so nothing asks first.
file it          ->  where the thing already seems complete: write the
                     capture, then offer filing with the recommendation in
                     the ask — "I would file this one for later, since it
                     already seems complete; say process now to take it
                     now. File it for later?" It waits in Unprocessed for
                     its turn; "process now" enters the interview.
```

**The ask, where one is made, is one fixed formula: "File it for later?"**,
with the recommendation and the process-now alternative in the sentence
before it. Where the lean is to process now there is no ask: processing
proceeds.

**The turn that reports a filing in a planning session ends on the same
formula**, where the thing filed was not already agreed: the one-line report
of what landed, the recommendation, then "File it for later?" — so the two
moments a raised thing passes through, before the write and after it, both
end on the same sentence.

**What stays the user's:** whether to process it at all, and whether there is
appetite to carry on.

**When *Claude* raises something mid-/plan that may be work, decide once, at
the moment it is raised, before any write and before any analysis, design, or
other work on it, by the same lean — and lean to working it now.** **Processing
is done with the user** — together, never as something Claude does alone. An
applied correction that may be method work gets the same decision.
Work-it-now runs the ordinary present-and-interview loop and, if kept, places the
item straight into Processed.

No anything-else clause on either branch: asking would be soliciting further
captures, which the always-loaded rule bars, and the user can add to a thing
while it is being processed.

**Either branch, once it loops into present-and-interview, is subject to the
fold conditions above** — and a thing raised in this message has had no earlier
turn on its substance, so its disposition cannot fold into the same message
that introduced it.

**The timing answer is not a disposition, and the specimen is what shows it.**
Proceeding answers *when*, and the recommendation on where it lands still has
to be put and still has to wait:

```
Claude   Taking this one now, since it would change what the cleared build
         does. [interview turn: what the item is, what it would change, what
         is still open — questions, not conclusions]

user     [answers]

Claude   [recommendation turn: what would be written, in plain words, then
         "Do that? If so I'll move it into Processed, cleared to run." —
         then STOP and wait]

user     [agrees, or doesn't]
```

Four turns and two separate asks.

### After all items

Unprocessed should be empty except items skipped this session; Processed holds the
kept work in order; section headers intact.

**Neutral end-of-queue gate** [PROMPT]. **Its precondition: it may fire only where
Unprocessed holds nothing but items skipped this session.** Anything else and this
gate is unavailable — with a full queue the only thing left to reach for is the
checkpoint, which presents the next item, and that is the correct behaviour.

When the queue empties, do **not** presume the session is over. An empty
Unprocessed is a resting state, not a stop signal. **The ask opens with the
ready work counted by kind, read from the digest — "N builds, N audits and N
steps of yours are cleared to run" — and then says in one line what was
passed over and why** — how many entries wait for a cycle's turn, how
many on other entries or on dates — naming any red-flagged capture outright
with what it waits on, so a queue that came to rest by passing everything over
is never reported as fully processed. The count is the count, not the list:
the close command's closing message is what lists the cleared items. Then, over
the entries filed or skipped this session that remain in Unprocessed, name by
slug the ones worth processing before the next build run, one clause each
saying why — a capture that would change what a cleared build does, or that
blocks one — or say that none bears on the cleared work; read off the digest's
capture-bears-on-cleared flags and the cleared region, with the limit that a
flag reaches a capture naming the cleared slug, and one that bears without
naming is this turn's own judgment. Then the closing paragraph exactly as
the specimen below has it, in the arm that fits this chat, ending on its
standalone bold ask — and wait. Each
command is named in words and does not end the sentence. **The specimen is the one statement
of the closing paragraph; the other sites that offer it point here and copy
it.**

Where the rescan command has not run in this chat:

> Eleven builds, one audit and three steps of yours are cleared to run.
> Everything else is set aside: four entries wait for a cycle's turn, two wait
> on other entries — one of them the red-flagged repository cleanup, which
> waits on the folder move — and one waits on a date. Two of the entries
> filed this session bear on cleared work: [x], which would change what [y]
> builds, and [z], which blocks [w].
>
> Two commands close a session. Send the rescan command first if you want a
> check that nothing said here was left out of the files. Then send the done
> command, which records the session and commits it. Sending done on its own
> runs the same check.
>
> **Is there anything else to capture or discuss first?**

Where it has, the closing paragraph reads instead, the counts above it and
the bold ask beneath it unchanged:

> One command closes the session now: send the close command, which records
> the session and commits it.

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
the conversation; nothing is stored. It silences this gate only — /close runs
when it is invoked, so there is nothing there to silence.

New items from conversation follow the same loop — check QUEUE.md for overlap
first. If you notice a gap: "I notice [X] — want to hear a suggestion?"
