---
name: migrate-checklist
docset: current
note: >
  Loaded on demand when a project's documents are on an older format than the
  plugin expects. A guided manual pass in an ordinary session, usually during
  /setup.
---

# Format migration checklist — older format → current

**This doc carries no response-shape tags** (the bracketed `[BRIEF]`-style
markers other procedure docs use); the prose in each step carries the behaviour
directly instead. **It stays tag-free**, for setup.md's reason: it runs during
/setup, where the rules defining those tags may not be loaded.

No new skill and no hook change: this is a guided manual pass, working item by
item, drafting the converted queue and **getting the user's approval before
writing, because a project being migrated may have been adopted moments ago and
may not be a committed git repo — so there may be nothing to recover.**

**When this applies.** A project's `QUEUE.md` format is the project doc that most
reliably falls behind as the method evolves, and most of what follows converts it.
LOG is already per-entry + index, CLAUDE.md is topped up by session_start, and
SPEC is format-agnostic — so they need little or nothing. **An epoch section may
also move a folder rather than convert a document**, where the method has changed
where something lives; each section says what it does.

```
recorded epoch below FORMAT_EPOCH  ->  convert with this checklist, running
                                       every epoch section from the recorded
                                       number upward
```

The oldest shape this reaches is the multi-section queue —
`## Red flags · ## Batches · ### Parked · ## Deferred tests · ## Captures` — but
which conversions run is decided by the recorded epoch, not by what the file
looks like.

**Plain-language guard.** A consumer reads whatever you say while migrating. Say
"your queue" not "QUEUE.md's parse structure"; "the ready-to-build line" not "the
cleared-to-run marker". **The structural terms below are for you to read, not to
narrate.**

## How to run it

**Run every epoch section from the project's recorded epoch up to the current
`FORMAT_EPOCH`, in order.** /setup reads the recorded number from
`.throughliner-format-epoch` and enters here; a project with no marker predates
it and starts at the beginning. Each section says which epoch it brings the
project to, so a project already past one skips it.

```
1. read the existing QUEUE.md; identify each old section and item
2. convert each item per the rules of each epoch section you are running
3. DRAFT the whole converted queue and show it for approval before writing
4. after writing, the post_tool_use lint confirms the new queue is well-formed
5. /setup writes the new epoch marker LAST, once the conversions have landed
```

## Epochs 1–3 — the two-section queue

Everything from here to "Preserve everything real" brings a project up to
**epoch 3**. Run it where the recorded epoch is below 3; a project already at 3
or above has a two-section queue and starts at Epoch 4 below.

### The target shape

The old sections all collapse into **two**: `## Processed` and `## Unprocessed`.

```
each work item becomes:
    a #### heading                 its one-line description
    a [slug] at the END of it      kebab-case, for LOG traceability
    rationale prose beneath
    an optional user-credit        "captured by you" — write the credit as the
                                   rules state (skill-nonspecific-rules.md,
                                   Captures, provenance)
    a red-flag marker              only if it carries a security/privacy risk:
                                   Red flag · State: cleared | uncleared
```

```
which section:
    Processed    vetted, agreed and ready (or designed and buildable).
                 Within it, --- Cleared to run above this line --- separates
                 greenlit-to-build (above) from not-yet-cleared (below).
    Unprocessed  captured but not yet fully processed (still needs thought).
```

The current header prose for each section is shipped in setup.md's scaffold —
**re-copy it rather than writing your own** (rule 3).

### The judgment rules a find-and-replace can't make

**1. Old red flags.**

```
work remains   ->  a work item carrying the Red flag · State: marker
it's done      ->  moves to LOG history
never          ->  left as a bare markerless line
```

**2. Old batch / parked / deferred-test items** → work items with a slug (and a
`captured by you` credit only where the user clearly raised it), placed **by
judgment**:

```
vetted and ready                      ->  Processed
still needs thought                   ->  Unprocessed
a deferred test ONLY THE USER can run ->  a [user] item with a described
                                          walkthrough
```

**3. Method-shipped boilerplate is refreshed by re-copy rather than regenerated
from guesses.** FAQ files, the QUEUE.md header prose, CLAUDE-TEMPLATE scaffolding — copy
the *current shipped template* over the stale file rather than rewriting it from
the method docs.

```
per-file discriminator:
    the user's own work   ->  migrate by judgment
    method boilerplate    ->  re-copy the template
```

**4. Approval before write.** Draft, show, get the okay, then write.

**5. Drop empty section placeholders.** An empty old Red-flags / Deferred-tests /
Parked block just disappears — nothing carries over.

## Epoch 4 — cleared work says what it changes

**Every item cleared to run says what changes, in which files, and what would
show it landed.** A run reads each cleared item whole from QUEUE.md, so an item
that says none of that reaches the run with nothing to build from and halts it
as underspecified.

**Nothing is reformatted, and no delimiter is required.** The run reads the
item's own text, so **an existing project's build blocks need no conversion at
all**: they read as part of the item, exactly as prose does.

```
a cleared item's own prose already    ->  nothing to do. It already says it.
  says what changes and where
a cleared item that does NOT say      ->  it never passed the decision step. Move
  what changes inside its files           it below the readiness line and
                                          process it at the next /plan, rather
                                          than inventing instructions for it.
an item carrying an old delimited     ->  leave it. It reads as ordinary text
  build block                             now; rewriting it would be editing a
                                          record to match later vocabulary.
a held item, or a capture             ->  nothing. Neither is built until it is
                                          cleared.
a `[user]` or `[freeform]` item       ->  nothing. One is walked through, the
                                          other halts a run by design.
```

**Write the blocks with the user, not for them.** Telling instruction from
decision history is a judgment, which is the whole reason the split is authored
at the decision step rather than computed by a script. A migration doing it silently
would make exactly the call the design reserves for a moment the user is present.

**Any block a migration does write under an existing item carries one more
line beneath it:** `Build block written by the format migration on YYYY-MM-DD,
not yet checked at planning`, the date read from the clock. The queue digest
lists a cleared item still carrying that line among its placement
contradictions, and the decision step removes the line once the buildability
check has run on the item. A block written without the line is
indistinguishable from one the decision step checked — which is how one project
found six unbuildable items in a cleared region of seventeen, item by item, at
build time.

**Record a refusal where one was made.** A recorded "X was rejected because Y"
belongs in the item, because a build that cannot see why an option was rejected
proposes it again and stops to ask.

**Nothing is deleted.** An item's rationale stays inline and whole — that is
what the throughline requires.

**Check it landed:** run the queue digest and read each cleared item's line.
Every cleared build or `[audit]` item should be one you can say, from its own
text, which files it changes and what changes inside them. Any you cannot goes
below the readiness line.

Cleared `[user]` and `[freeform]` items are counted separately, on the same
line, as items that need no block — neither is built from one.

## Epoch 5 — `workshop/`, and `resources/` moves inside it

**This epoch moves a folder rather than converting the queue**, so nothing in
QUEUE.md changes here and none of the drafting-and-approval flow above applies to
it. It is still a migration step, because the project's research notes and testing
evidence sit at a path the scope-lock, the queue digest and the always-loaded
rules no longer name.

`workshop/` is where a project's working material lives — what the project works
with rather than what it ships. Keeping it in one folder is what lets someone
landing on the repository see the product and the method's own documents first.

**Look inside `resources/` before moving anything.** `resources/` is a common
folder name, and a project may keep product data under it — files the build
copies, the application loads by path, a generator writes into, or SPEC and
the README name. Moving those breaks the build and falsifies SPEC.

```
project has resources/ at its root  ->  create workshop/, then discriminate on
                                        contents: MOVE the research and testing
                                        material (resources/research/,
                                        resources/testing/), keeping relative
                                        paths — resources/research/x.md becomes
                                        workshop/resources/research/x.md. For
                                        ANYTHING ELSE found inside resources/,
                                        list it and put the split to the user
                                        rather than moving it.
project has no resources/ folder    ->  create workshop/ with an empty
                                        workshop/resources/research/ inside it
project already has workshop/       ->  nothing to do
```

**Move, never copy.** Two copies of a research finding is the failure this
folder exists to avoid — a later session reads the stale one and cannot tell.

**Use a real move that git can follow** (`git mv` in a tracked project), so the
files keep their history rather than arriving as new files with none.

**Anything else the project keeps but does not publish may go in `workshop/` too**
— post drafts, article drafts, reference material. That is the user's call, item
by item, and nothing is moved there without asking. Only the research and
testing material moves automatically, because the method's own tools name that
path.

**Check it landed:** `workshop/resources/` exists and holds the research and
testing material, whatever remains at the root under `resources/` is what the
user chose to keep there, and a research note the queue cites still opens from
the path the digest reports. A partial move the user directed is a correct
outcome, not a failure.

**Then re-point what named the old path.** A project's own `CLAUDE.md`, and any
queue item or session record that gives a `resources/…` path as an instruction to
follow, now name a folder that has moved. Fix the instructions; leave the records
alone — a record written before the move correctly says where the file was then.

## Epoch 6 — the LOG index is generated from each record's summary field

**This epoch changes the records, not the queue.** Each session record now
carries its own one-line summary in a front-matter block at the top of the
file — `---`, `summary: <the index line's text after the hash>`, `---`, then
the `# <hash> — …` heading — and the close regenerates `LOG/index.md` and the
monthly `LOG/index-YYYY-MM.md` files from those fields with the backlinks
script, never by hand. An existing project's records carry no field, so its
index would regenerate empty; the one-time backfill writes each record's
existing index line into its record first.

```
run once, from the project root:
    python <plugin-root>/scripts/log_backlinks.py <project root> --backfill-summaries

what it does:
    every per-entry record with no front matter   ->  gains a summary field
                                                      from its index line, or
                                                      from its heading where
                                                      no line names it
    LOG/index.md and LOG/index-YYYY-MM.md          ->  regenerated from the
                                                      records; a line pointing
                                                      at a pre-split combined
                                                      log is carried over
                                                      after its month's lines
    LOG/backlinks.md                               ->  regenerated as at every
                                                      close
```

**Show the user, before running it, what will change:** every record file
gains three lines at its top and the index files are rewritten; nothing else
in any record is touched. Where the project's records are kept out of git,
say that the previous index files are not recoverable from history once
rewritten, and get the okay first. After the run, compare the regenerated
`LOG/index.md` with the previous one and name any line that differs — order
within a day follows each record's own date field, which is the one
difference a hand-written index may show.

## Section preambles — run this at every epoch

**Quote a plain-prose section preamble.** Where the paragraph directly under
`## Processed` or `## Unprocessed` is ordinary prose, prefix each of its lines
with `> `. The wording is left exactly as it is.

The lint reads un-quoted, un-headed prose inside a section as an orphaned
rationale and warns that a heading may have been overwritten — and a preamble
legitimately has no heading.

```
already a blockquote  ->  nothing to do
plain prose           ->  quote it, wording untouched
no preamble at all    ->  nothing to do
```

**Check it landed:** the lint reports no "prose belongs to no entry" warning for
either section heading.

## Preserve everything real

**Migration must lose no content the user wants kept.**

```
each item's full rationale prose  ->  carried across verbatim (re-authored only
                                      to fit the new shape, NEVER truncated)
an old "captured by you" signal   ->  kept
an old "by Claude" label          ->  just drops (AI is the default now)
any red-flag risk                 ->  kept as a marked work item
```

**When unsure whether something is the user's own work or method boilerplate,
ask** rather than guessing and overwriting.
