---
name: setup
docset: current
note: >
  /setup procedure. It runs on two kinds of session: a fresh adoption, where the
  always-loaded behaviour rules are absent, and a migration or top-up inside an
  already-adopted project, where they are present. It states its own
  plain-language guard, so that it holds on the run where nothing else governs
  it, and each step's prose carries its behaviour in full so a tag never has to
  be read to follow the step.
---

# /setup procedure

/setup is where the project gains the documents that will carry the user's
intent across every session to come. You are setting up a project folder with
the Throughliner method.

**Each step's prose carries its behaviour in full, and the response-shape tags
are a summary of it.** /setup runs on two kinds of session: a fresh adoption,
where the rules defining those tags are not loaded, and a migration or top-up
inside an already-adopted project, where they are. So a step is followed from
its prose on either run, and a tag never carries anything the prose does not
already say.

**Plain-language guard.** Everything you say during /setup is read by a no-code developer
who may be brand new to all of this. Keep internal terms out of what they see — no
hook filenames, no working-file names, no "scope-lock," "method docs," or "Case B"
labels. Say "your project's files," not "method docs"; say "I'll set this up as a
migration," not "this is Case B."

## Step 0: Is a build running right now?  [SILENT] when no build and no planning session; [BRIEF] when refusing a build; [BRIEF, PROMPT] when describing a planning session

Look for a file named `_build-<session-id>.md` in the project folder. That file
means a build is in progress — either in this chat or another one — and /setup
must not run alongside it.

**Say so plainly and stop.** /setup creates and rewrites a lot of the project's
files, and while a build is running the safety check refuses every write outside
that build's own list. Starting anyway would not be blocked cleanly at the door;
it would fail partway, file by file, leaving the setup half-finished. So:

> There's a build running in this project at the moment, and setting up while it
> runs would leave things half-changed. Finish it, or run the done command to
> close it, and then start me again — I'll pick up from there.

Then stop there — no scaffolding, no continue-anyway question, no workaround.

**A planning session is different — it is not refused.** There is no build file
there, and /setup's own marker (Step 0.5 below) is what lets its writes
through. What /setup owes that situation is a description rather than a
refusal, because the failure to avoid is silence, not permission. Say what is
about to happen and let the user choose:

> You've got a planning session going here. I can set up now — setting up
> changes a few files outside the usual ones, which is fine and expected. Worth
> knowing that the planning work in this chat isn't saved yet; the done command
> is what records it. Set up now, or close first?

Then wait for their answer, and do what they say.

## Step 0.5: Declare the run  [SILENT]

Before writing anything, create an empty file named
`.throughliner-setup-active` in this session's scratchpad directory. Delete it
when the run ends — including on every path that ends early: the user declining
above, a stop partway through, an error.

It is what tells the safety check that this session is a setup run rather than a
planning one. Without it, every write /setup makes outside QUEUE.md, SPEC.md,
LOG/ and FAQ/ is refused: the version marker, the format-epoch marker, the
`.gitignore` lines, the managed block in CLAUDE.md, and any scaffold file the
run finds missing.

The scratchpad is used because it is writable in every session type — so the
marker can always be created — and because it clears itself, so a run that dies
partway leaves nothing to tidy up by hand.

## Step 1: Detect folder state  [SILENT] while detecting; [BRIEF, PROMPT] when the project is already up to date

```
Case A  no content            the folder is empty or nearly so. Fresh start.
Case B  content, no SPEC.md   the user's own files exist but no method docs.
                              Either a true fresh start OR a MIGRATION.
Case C  already set up        SPEC.md exists.
Case D  inside another        no SPEC.md here, but walking up the folders
        project               finds one. A POP-OUT — see below.
```

**Case D takes precedence over B for a folder inside an adopted project**: walk
up from this folder looking for a project marker before treating its contents as
a migration.

**On Case B, treat existing planning or spec documents as a possible migration**
and follow the migration framing below. Recognise a migration **by what the docs
do, not by a fixed list of old names** — the source could be anything.

For Case C, check `.throughliner-version`:

```
version matches current plugin   ->  fully up to date. Say so in a sentence,
                                     offer /plan instead, then STOP and wait.
version missing or outdated      ->  Step 2C (migration scaffolding)
```

## Case D: popping a subpart out into its own project

This folder sits inside a project that is already set up, and the user is
adopting it separately. That is a **pop-out**: a subpart that has outgrown the
parent — one unmanageable piece of a large differentiated project — becoming a
project of its own.

**Read the parent's SPEC, infer which subpart this folder covers, and put it to
the user in clarifier form**  [PROMPT] — inviting their answer rather than
proposing one, exactly as Case B's peek does.

**State the irreversibility in that same confirmation, plainly: there is no
scripted way back in.** Popping out is a one-way move; folding the work back
into the parent later is hand work nobody has written a path for.

Then run the ordinary interview with that context, and write the ordinary docs.
**The new project is an ordinary project in every respect and never reads
outward** — it does not consult the parent's queue, spec or records while it
runs.

**Dependencies run upward only, one level deep.** Subproject work may hold
parent work; parent work may never hold subproject work — that is what makes a
cross-project loop structurally impossible. A child genuinely waiting on its
parent uses the ordinary outside-the-project pattern instead: name what would
show it done, or wait for the user to mention it.

**No session ever writes another project's queue.** A dependency crossing the
boundary travels as approval-gated mail, and the receiving project files it with
its own hands.

**At /done, draft the pop-out message to the parent's INBOX**  [PROMPT] —
shown to the user in full, sent only on an explicit yes, like any other outbound
mail.

## Case B: pre-existing content rules

**1. Peek before Q1.** Read the pre-existing content before the first interview
question, and use what you learn to *frame* that question rather than to
*pre-answer* it.

```
a clarifier INVITES the user's own answer:
    "I can see a tax brief in this folder — is that what this project is about,
     or something separate?"
pre-answering PROPOSES the answer for confirmation:
    "From the brief, this is a tax-prep project for your 2025 return — right?"
```

Ask cold and you miss context the folder already gave you; pre-answer and the spec
fills with your words instead of the user's.

**1b. Where the folder already holds more than one git repository — a clone, a
fork, or a `git init` in a subfolder — say so and ask which root this project
adopts** [PROMPT]. Name which repository would hold the method's documents under
each answer, and record the choice as the standing visibility line described at
the keep-private step. Without it, a fork splits the code from the documents and
nothing later says which repository the project is actually in.

**2. Leave it untouched; name it at close.** Pre-existing content is not edited,
moved, or reorganized during scaffolding — scaffolding only adds the method docs.
In the closing message, name that content explicitly as source material the user
can refer back to.

## Case B: migration framing

When the content is a migration, /setup maps it into Throughliner's docs. The mapping is
your judgment, not a fixed table; these guardrails keep it from importing the
source's shape wholesale.

- **State SPEC's purpose first.** Before mapping anything, say plainly what SPEC.md
  is for: product truth — what the app is, who it's for, how it works, why it
  exists. **It is not a UX spec or an implementation manual.** Map the source
  into that frame, with SPEC's purpose deciding the shape rather than the source.
- **Check role-fit before renaming.** A source doc and the Throughliner
  doc it seems to map to may not cover the same ground: the old one might be
  broader (a UX doc walking every screen) or narrower. If the roles don't match,
  say so plainly and let the user decide how to split or combine rather than
  silently renaming one into the other.
- **Scrub the source's self-description from the content.** Renaming the file isn't
  enough — the old framing hides inside the text. A line like "this describes every
  functionality and UI element as the user experiences it" silently re-mandates the
  exhaustive detail SPEC is meant to leave out. Rewrite or drop any purpose, intro,
  or self-description sentence that re-asserts the source's role, so SPEC describes
  **the product**, not the old doc.
- **Throughliner's docs live at the project root.** No path setting, no doc-location config. If
  the source used a path block or pointed its docs elsewhere, that doesn't carry
  over.

## Step 2C: Migration scaffolding  [SILENT] for the checks and file creation; [BRIEF] at /done

The plugin version changed since this project was last set up. Re-scaffold without
overwriting user content. Run the checks and file creation **silently**; keep the
close to a sentence or two.

**1. Check each doc/folder** from the Step 2 scaffold list. Exists → skip. Missing
→ create from the standard scaffold (empty structure, not interview-filled).

**1a. Run every document-format conversion the project is behind on**  [SILENT]
when the project is on the current epoch; [PROMPT] for each conversion shown
before writing. Read the
project's recorded epoch from `.throughliner-format-epoch` and compare it against
`FORMAT_EPOCH` near the top of `${CLAUDE_PLUGIN_ROOT}/hooks/session_start.py`:

```
recorded epoch < FORMAT_EPOCH
        ->  load ${CLAUDE_PLUGIN_ROOT}/docs/migrate-checklist.md and follow
            EVERY epoch section from the recorded number up to the current
            one, in order, drafting each conversion and getting approval
            before writing
recorded epoch == FORMAT_EPOCH
        ->  skip; open the checklist at all
no marker file
        ->  the project predates the marker: treat it as epoch 1 and run the
            whole checklist from the beginning
```

**Read the epoch from the marker rather than inferring it from the documents** —
inferring guesses about files users legitimately hand-edit.

**Where a conversion writes a build block — or any instruction text — under an
existing queue item, it writes one more line beneath it:**
`Build block written by the format migration on YYYY-MM-DD, not yet checked at planning`,
the date read from the clock. A migration runs hands-off, and the buildability check
needs the user present; the line is what lets the queue digest surface a
cleared item nobody has checked, and the decision step removes it once the
check is run.

Showing each conversion before writing it is the general write-first test
applied, not an exception to it: a project being adopted or migrated may not be
a committed git repo, so its old documents may not be recoverable once
overwritten.

**1b. Reconcile the settings attached to the scaffold list**  [SILENT] for the
settings added without an answer; [BRIEF, PROMPT] for the brevity-style offer
and for INBOX files already in git history. Step 1 restores
missing *files*. It does not re-run the *decisions* attached to them, so a
migrated project can end up with a file and none of the setup that goes with it.
Check each, and make it so if it isn't:

```
INBOX/ present          ->  `.gitignore` carries an `INBOX/` line
temp/ present           ->  `.gitignore` carries a `temp/` line
.gitignore present      ->  it carries a `.throughliner/` line
no outputStyle set in the project's .claude/settings.local.json
                        ->  make the brevity-style offer from Step 2, exactly
                            as a fresh setup would — this project was set up
                            before the style shipped
```

**Where the project has INBOX files already in git history, say so plainly.**
Adding an ignore line stops future commits; it does not untrack what is already
committed, and it cannot remove anything from history. Tell the user what is
there and that the line does not undo it — the line goes in only alongside that
plain statement, so nobody is left thinking the mail is now private.

**1c. Offer the nested conversion to a flat project**  [BRIEF, PROMPT] — an
offer, never a halt. Where the project is one flat repository, say in two or
three sentences what the nested shape is (the product in a subfolder with its
own clean repository, the method's documents tracked privately in the outer
one, /done committing both) and which of the two conversions this project
gets: where the repository has no remote, the product's files move into a new
inner repository (the **split**); where it already has one, that repository is
already the product's and is kept whole as the inner, the opened folder
becoming the private outer with the checkout's contents moved down into the
product subfolder (the **wrap**). On a yes, plan the conversion with the user
file by file, opening the plan by reading `git remote` to choose the arm; on
anything else, drop it — the flat shape keeps working exactly as before, and
the offer returns once more as the public-repository offer's first provision.

```
split  (no remote)   ->  create the product subfolder and its repository; move
                         the product's files in; the method's documents stay
                         where they are and are tracked by the outer
wrap   (has a remote) ->  keep the opened folder as the outer, with its own
                         repository and no remote; create the product
                         subfolder inside it; move every file and folder of
                         the checkout, `.git` included, down into that
                         subfolder BY EXPLICIT NAME — never a loop or a glob;
                         bring the method's documents and working material
                         back to the top and track them in the outer; leave
                         the inner's own ignore rules alone — the documents
                         were ignored there and are now absent
```

Any local path that pointed at the checkout — a marketplace registration, an
MCP registration, a permission rule — now points one level too high and is
re-pointed as part of the plan, read from the walk-through's ripple list
before the move.

Both arms then write the Visibility line the nested scaffold writes, naming
the opened folder as the outer.

**1d. Offer the parts question to an existing project**  [BRIEF, PROMPT] — an
offer, never a halt, and never forced. Where the project CLAUDE.md carries no
parts block, ask the interview's parts question (Step 3): roughly what the
project's moving parts are and which are the product, with a guessed answer
offered and a rough one accepted, an ambiguous part put to the user. On an
answer, plan the reorganisation with the user file by file — one folder per
part, product parts in the inner repository and process parts in the outer,
the looser split stated where the inner will never be public — and write the
parts block, with a stub `SPEC.md` in each part's folder and a `## Parts`
section in the root spec, as the scaffold's parts step writes them. On
anything else, drop it: the project keeps the workshop rule
as its default, and nothing runs at a later session opening for this. The
top-up does not carry it.

**2. Retire REGISTRY.md if present**  [SILENT] when it holds only what the old
setup put there; [BRIEF, PROMPT] when the user has written into it. No longer
one of the method's docs, but
**read it before deleting** — the user may have written real notes there.

```
holds ONLY what the old setup put there
    (a # REGISTRY heading, the "Components that exist…" line, and either the
     empty placeholder or an auto-generated file list)
        ->  remove it quietly as part of the migration
holds anything the user clearly added
        ->  LEAVE it. Tell them plainly what's in it and ask where that content
            should live now (usually SPEC.md) before removing the file.
```

Where their own content goes is the user's call, not yours.

**2a. Rewrite a plain-prose section preamble as a blockquote**  [SILENT]. Where the
paragraph directly under `## Processed` or `## Unprocessed` in the project's
QUEUE.md is ordinary prose, prefix each of its lines with `> ` so it becomes a
blockquote. Leave the wording alone — this changes the shape, not the text.

The queue lint reads any un-quoted, un-headed prose inside a section as an
orphaned rationale and warns that an item's heading may have been overwritten —
and a preamble legitimately has no heading.

```
preamble is already a blockquote  ->  nothing to do
preamble is plain prose           ->  quote it, wording untouched
no preamble under the heading     ->  nothing to do; the scaffold's own
                                      wording is not backfilled here
```

**3. Update `.throughliner-version`**  [SILENT] to the current plugin version.

If the project instead carries the pre-rename marker `.si-version`, write the
new file and delete the old one — the method was called Sovereign Implementer
until epoch 3 and both marker files were named for it. Do the same for
`.si-format-epoch` in step 3a. Leaving the old file behind means every later
session reads a marker the plugin no longer writes to, so the two names drift
apart silently.

**3a. Write `.throughliner-format-epoch`**  [SILENT] when the conversion ran to
completion; [BRIEF] when the user skipped it — the document-format number this migration
brings the project up to. Read it from `FORMAT_EPOCH` near the top of
`${CLAUDE_PLUGIN_ROOT}/hooks/session_start.py` and write that number, on its own,
into `.throughliner-format-epoch` at the project root.

Do this **last among the migration edits**, and **only when the conversions for
that epoch ran to completion**. It is what clears the session-start halt that
sent the user here, so writing it early would silence the warning while the
project was still on the old shape — and nothing else would ever raise it again.

```
conversion ran to completion   ->  write the new epoch number
user skipped the conversion    ->  leave the marker at its old value, and say
                                   plainly that the halt will fire again next
                                   session because the conversion is still owed
```

**3b. Read the project's own CLAUDE.md for retired terms, and report what you
find**  [SILENT] when clean; [BRIEF] when reporting.

A project's CLAUDE.md was written when it was set up and is read at the start of
every session since; where it describes a piece of the method that has since
been retired, every session reads that description as current.

Search the file for each retired term the method carries, and for each hit say
plainly what the term was and what replaced it.

```
retired terms to search for, with their replacements:
    "batch", "Build/Test/Audit"  ->  a work item is a single `#### ` heading
                                     with a flavor tag; there are no batches
                                     and no sub-headings inside one
    "Deferred tests"             ->  deferred verification is a `[user]` work
                                     line, revisited each planning run
    "Parked:"                    ->  work is held below the cleared-to-run line
                                     by `Blocked by:` or `Not before:`
```

**Also read the project's SPEC.md for a "Project docs" section** — the old
scaffold wrote one describing the method's own machinery into the user's
product truth, and it goes stale in a way no refresh repairs, because SPEC is
the user's document and is never rewritten by a migration. Report it the same
way: say the section describes the method rather than their product, that the
same description now lives in the managed block of their CLAUDE.md, and edit
nothing — removing it is their call.

**Report only — edit nothing.** The file is the user's, and reconciling its
wording against the current template would clobber whatever they wrote into it.
Tell them what is stale, what it means now, and leave the change to them.

```
no hits    ->  say nothing; carry on
one hit    ->  name the term, what it was, what replaced it
several    ->  one message listing all of them, then carry on
```

**3c. Refresh the plugin-managed block in the project's CLAUDE.md**  [SILENT]
when the regions match; [BRIEF] when replacing the region or reporting a missing
one.

Compare the region between the PLUGIN-MANAGED markers in the project's CLAUDE.md
against the same region in the installed `templates/CLAUDE-TEMPLATE.md`.

```
regions match          ->  nothing to do; say nothing
regions differ         ->  say what will be replaced, then:
                           1. any text inside the block that is not the
                              template's — user-authored lines — moves below
                              the end marker, and the narration says so
                           2. the region is replaced with the template's
                              current text
no markers found       ->  report it like a retired term (3b): say the managed
                           block is missing and what it is, edit nothing
```

This is the one deliberate exception to the add-only rule below: the
block's own marker promises it is updated on /setup, and the method-owned text
between the markers is exactly what goes stale as the method evolves — a stale
queue model there is read as current at the start of every session. The move-
then-replace order is what keeps the exception safe: nothing the user wrote is
deleted, only relocated below the marker, and the narration names it.

**4. Skip the interview**  [SILENT] — the project is already described in SPEC.md.

**5. Close state-aware**  [BRIEF].

```
a leftover build working file    ->  an earlier build was interrupted: name it
    is present
                                     and recommend resuming with /next. The
                                     migration's new files get recorded when
                                     that build closes.
otherwise                        ->  tell the user what was created or updated
                                     and recommend /done
```

**Add only — existing files stay as they are.** The goal is to add what a newer
plugin version introduced, not to refresh content. The one carve-out is the
plugin-managed block in CLAUDE.md (3c), which is method-owned text the marker
promises is kept current — and even there, user-authored lines are moved rather
than deleted.

## Step 2: Scaffold the docs  [SILENT] for the file creation; the tagged offers inside it govern their own turns

Create these files (empty structure; content comes from the interview),
**silently** — the Step 4 close-out reports the full list.

**SPEC.md:**

````markdown
# SPEC — [Project Name]

## What this is
[filled by Q1]

## Who it's for
[filled by Q1]

## How it works
[filled by Q2]

## Principles
[filled by Q3]
````

**QUEUE.md:**

````markdown
# QUEUE

## Processed

> Vetted work, ready to build — worked top to bottom. Each piece of work is one
> item: a `#### ` heading naming it, a short name in square brackets at the end of
> that heading line, and a short rationale beneath. **That bracketed name is a
> handle, so you and Claude can refer to a piece of work without retyping its whole
> description — "let's do the login one" works too, and Claude never asks you to
> write one.** A leading flavor tag names how it runs — none for a
> build (Claude edits files), `[audit]` for a review pass, `[user]` for a step only
> you can do. A security or privacy risk Claude surfaces lives here too, as a work
> item carrying a `Red flag · State: cleared/uncleared` marker. The line below marks
> how far down is cleared to build; anything below it is decided but not ready yet.

--- Cleared to run above this line ---

## Unprocessed

> Captured ideas and tasks not yet fully processed. The next /plan run goes
> through these with you and decides each one's fate — keep it (move it up to
> Processed) or drop it. Each is filed as its own `#### ` heading, so the list shows
> up in an editor's outline.

[filled by Q4]
````

**LOG/ folder** — create the directory with one file in it, `LOG/index.md`:

````markdown
# LOG Index

One-line summaries of each session. Newest first. Each line names the session's
full entry file in this folder.
````

Session entries are written by /done, each as its own file in LOG/ — nothing else
to scaffold.

**FAQ/ folder** — create the directory **first**, then copy the templates in (the
folder must exist before the copies, or they fail):

```
FAQ/faq.md    <-  ${CLAUDE_PLUGIN_ROOT}/templates/faq-template.md
FAQ/index.md  <-  ${CLAUDE_PLUGIN_ROOT}/templates/faq-index-template.md
```

**workshop/ folder, with `workshop/resources/research/` inside it** — create them
empty. `workshop/` is where the project's working material lives — what it works
with rather than what it ships — so someone landing on the repository sees the
product and the method's own documents first, and everything they merely refer to
sits in one folder that can be skipped. `workshop/resources/research/` is the home
for research notes (`workshop/resources/research/<topic>.md`), and
`workshop/resources/testing/` is the home for re-read-later testing evidence,
created when there is something to put in it. Creating the research folder at setup
means research notes have a place from day one rather than the folder being
conjured on first use.

**temp/ folder** — create it empty, and add `temp/` to `.gitignore` beside the
`INBOX/` line. It is where a session puts what the project does not keep: a
fetched transcript, a file downloaded to read once, a draft that never became a
deliverable. Everything in it is disposable by definition, so nothing records
when it should be deleted.

**INBOX/ folder** — create it empty, with an `INBOX/archive/` inside it. It's this
project's mailbox: another project you run can drop a message file in here, and
session_start surfaces anything waiting in one line. A project only ever reads its
own INBOX — it never goes looking through other projects for mail.

Add `INBOX/` to `.gitignore`, and say so in one line  [BRIEF] — that mail from other
projects stays out of the repository, and they can remove the line if they want it
committed. No question is asked.

Why it isn't asked: anything committed is published, an un-ignored mailbox
accumulates another project's raw text in the repository forever, and the safe
outcome must not depend on a question being asked, because a question is
skippable.

**CLAUDE.md:**

```
no CLAUDE.md exists  ->  scaffold from
                         ${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE-TEMPLATE.md
one already exists   ->  APPEND the method block; never overwrite
```

The template carries no rendering settings — how doc-bound text is surfaced is a
default plus a session-opening offer, not a stored field (skill-nonspecific-rules.md,
view-in-doc rendering).

**.throughliner-version** — write the current plugin version (from
`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`). session_start reads it to
detect when the plugin has been updated.

**.throughliner-format-epoch** — write the document-format number, read from `FORMAT_EPOCH`
near the top of `${CLAUDE_PLUGIN_ROOT}/hooks/session_start.py`. Separate from the
version on purpose: the version changes at every release, the format number only
when a change makes older projects' documents structurally wrong. session_start
compares the two and halts the session when the project is behind, so a project
on an old shape finds out instead of quietly running on stale scaffolding.

**.gitignore** — create it if absent, and make sure it carries an entry for
`.throughliner/`, added only where it is missing.

That folder holds the editing-state signal: while Claude is writing a file, the
hooks drop a small file in there saying so, so a Markdown reader or editor open
on the same document can hold off rather than the two of you typing over each
other. It is transient state about the session running right now, so it stays
out of the repository.

**Git repositories — the nested shape.** A new project is set up nested: the
top folder is the larger project — the method's documents and working material
— and the product sits in a subfolder. Name the product subfolder with the
user in one line (their own word for the thing they are building is usually
its name), create it where absent, and run `git init` twice where either
repository is missing: once at the project root, once in the product
subfolder. The inner repository holds only the product, displayed cleanly,
and is the one that goes public when the user asks; the outer one never gets
a remote, so the method's documents are tracked there — privately — and undo,
history and /done's read-back all work from ordinary git. /done
commits both, the product commit into the inner repository and everything
else into the outer. One product subfolder per project; a project with
several outgrowing parts uses the subproject pop-out, which exists for that.

**Write the shape into the project CLAUDE.md's Visibility line as part of the
scaffold**: which two repositories exist, which holds the product and goes
public, which holds the documents and never gets a remote. The template's
Visibility slot carries the pattern. This is the standing line every later
session reads when weighing a git operation, so a nested scaffold that leaves
it blank leaves "which repository am I in" unanswered.

**One folder per part, in the right repository.** The interview's parts
answer (Step 3) names the project's moving parts and which are the product.
Create one folder per part: a product part inside the inner repository, a
process part in the outer. Write the parts block into the project CLAUDE.md —
the template's `## Parts` slot carries the pattern — one line per part naming its
folder and its repository, and one line saying where a file belonging to no
part goes. Where the inner repository will never be public, say so in one
line and let the split be looser: more may sit alongside the product there.

**Each part gets its own spec.** Write a stub `SPEC.md` into each part's folder
— a heading and one line saying what the part is — and a `## Parts` section
into the root `SPEC.md`: one line per part, what it is, and a link to that
part's spec. The root spec stays the whole-project layer; a build reads a
part's spec only for the items whose files sit in that part, and planning
writes a decision's sentence into the part's spec where it concerns that part.

**A folder that is already a flat repository is never restructured here.** The
conversion is an offer — at the migration path, and again as the
public-repository offer's first provision — and declining leaves the flat shape
working exactly as before. **A conversion that
is accepted writes the same Visibility line the scaffold writes**, replacing
whatever the flat answer was.

**Keep-private option**  [BRIEF, PROMPT]. Offer once, as part of scaffolding.

**SAID FIRST — the whole of the first message is these four lines**, in this
shape, with the ask in the fixed formula:

```
The planning documents — the spec, the queue and the session records — stay
out of the repository.                                 # the recommendation, as
                                                       # a statement
They hold the project's plans, reasoning and history — the most personal
material the method produces — and keeping them out is the only complete
protection if the project is ever published.           # one sentence of why
**Keep them private?**                                 # the bold ask, last
```

In a nested project the first line says instead that they are tracked in the
outer repository, which never gets a remote. Nothing else goes in that message:
not the per-document combinations, not what the choice keeps and changes, not
the mailbox. Those are HELD below — what Claude reads to answer, and what it
says after the yes.

**HELD — Claude's own reading, and what follows the answer.**

**The offer forks by project shape, and the fork is the first thing Claude
reads:**

```
NESTED project   ->  propose TRACKED-IN-THE-OUTER: the documents are tracked
                     in the outer repository, the shape stated under "Git
                     repositories — the nested shape" above. The per-document
                     `.gitignore` remains available for a document the user
                     wants out of even the local history, with the same costs
                     stated below.
FLAT project     ->  propose PRIVATE-via-gitignore, as follows.
```

**For a flat project there are two named configurations, and the private one is
what setup proposes** — the same acceptance-default shape the brevity-style
offer uses: describe it, say why it is preferable, and let the user accept it
or choose the alternative.

```
PRIVATE (proposed)  the project's Throughliner documents go in `.gitignore` and
                    stay out of the repository entirely
TRACKED             they are committed with the rest of the project
```

**The choice is per document, so any combination is reachable:**

```
SPEC.md    what the project is
QUEUE.md   what to work on next, and the reasoning behind each piece
LOG/       what happened, session by session
```

**It is ONE question with three answers, never three questions.** The yes takes
all three; a user who names a document gets just that combination — a private
queue with a public history is the one someone most plausibly wants, and a
bundled choice would make it unreachable rather than merely un-defaulted. The
combinations are said only when the user names a document.

**The trade is stated once, in the one sentence of why above**, never once per
document.

**After the yes, the report is one line naming which paths went into
`.gitignore` — and then what the private configuration keeps, what it changes
and its limit**, which describe what the choice does rather than what to choose:

```
KEPT     Claude still writes to these first and reports what landed. Before
         each change the plugin saves a copy of the previous version into a
         local folder that is itself kept out of the repository, so an
         unwanted change — a deleted queue item included — can be put back.
CHANGED  /done cannot read its own work back from the file's history, so
         it records the session from what it remembers.
LIMIT    those saved copies live on this machine and carry no history, so a
         lost disk loses them. Say this rather than describing the net as an
         equal replacement for git.
```

They also do not travel with a clone.

**Nothing here is asserted again later as a fault.** Every session opening
reports which of the three are untracked and what follows, because this state
can also arrive from an ignore file the user wrote themselves, or from a choice
made weeks ago in a project nobody has looked at since.

```
user accepts, or names   ->  add exactly those paths to `.gitignore`, say in one
  some                       line which went in and which stayed tracked
user chooses tracked     ->  state plainly what results: these documents are
                             tracked in this folder's history and readable
                             nowhere else until the project has an online home,
                             which is set up whenever they ask. Not asked again
                             at any later setup run.
```

**Write the visibility answer as a standing line in the project's own
CLAUDE.md**, in the slot the template carries for it, so every later session
reads it — not only the setup session's record.

**A public repository is set up only when the user asks** — the offer itself is
"The public-repository offer — one subject, five provisions", below.

**Cloud-sync folder, said once**  [SILENT] when no name matches; [BRIEF] when
one does. Read the project's absolute path for these folder names,
case-insensitive: `OneDrive`, `My Drive`, `Google Drive`, `Dropbox`,
`iCloud Drive`, `iCloudDrive`. Where one is present, say three things in one
short paragraph, as things to be aware of and never as things to fix:
generated output and a sync client can collide — a build tool unable to delete
files it just wrote is the shape; on Windows the sync root's added depth eats
the 260-character path budget; and setting the client to mirror files locally
rather than stream them on demand reduces the collision without removing it.
The path alone is the check — no environment variable is read — and the step
says nothing where no name matches. Scaffolding only; the top-up does not carry
it to existing projects.

**Whichever arm the fork lands in, the proposed configuration is what a user
who says nothing about it ends up with — private via the ignore in a flat
project, private by architecture in a nested one.** Acceptance is the default
here and nowhere else in scaffolding: the material is the most personal the
method produces.

**This adds no sixth interview question.** It is part of scaffolding, where the
files are being created, and it is answerable without knowing anything about the
project.

**The brevity-style offer**  [BRIEF, PROMPT]. The plugin ships an output style
called Throughliner Brevity — a setting that keeps Claude's replies short and
decision-led in this project. Offer it once, as part of scaffolding, opt-out
with acceptance as the default.

**What the brevity-offer turn carries.** The offer itself, the reason it is
preferable, its scope, and the invitation to discuss — where the reason argues
from what the method will generate as the user works, never from a property of
a project that does not exist yet.

1. Check whether the project (or the user's own settings) already sets an
   output style. Where one is set, name it and say plainly where it and the
   brevity style would pull in different directions.
2. Give the reason acceptance is strongly preferable: the method's documents
   accumulate as the user works, and a model that runs verbose buries the one
   thing the user must see under narrative — a style is the strongest lever
   there is against that.
3. State the scope: this applies to this project only — nothing outside it
   changes, and the user's own style file is never edited.
4. Invite discussion, then act on the answer:

```
user accepts (the default)  ->  write "outputStyle": "Throughliner Brevity"
                                into the project's .claude/settings.local.json
                                (creating the file if absent, merging if not)
the write is refused        ->  say in one line that the app is asking
                                permission for that file, and retry once on
                                the user's word; refused again -> the decline
                                outcome below. A first write to a project's
                                settings file ordinarily prompts, so a refusal
                                is common and is not a decline.
user declines               ->  say nothing further; every session opening
                                will carry one short line noting the style is
                                not enabled
```

Say once that the style takes effect at the next session or /clear — styles
never apply mid-conversation.

**The public-repository offer — one subject, five provisions** [DISCUSS,
PROMPT]. Make it only where the user asks for a public repository, and then:

- where the project is flat, re-offer the nested conversion first — going
  public is the moment a flat layout starts to matter, since a nested
  project's inner repository is what goes public while the method's documents
  stay in the private outer one. Declining keeps the flat shape and the offer
  proceeds on it;

- ask what licence the project should carry, and why it is being asked now:

```
a licence is what says who may use the code and on what terms, and it only
becomes a real question once the code is going somewhere public
```

- set up the repository;
- describe the contents as unscreened, and say what the only complete protection
  is — not publishing these documents, which is what the keep-everything-private
  option above does;
- treat "not now" as a plain answer that ends it, with the offer not repeated
  and nothing set aside for later.

The method scans for things shaped like credentials and reads its own writing
against a checklist, and neither can tell whether a sentence quietly identifies
a real person — so this offer may set up the repository and may say nothing
about the documents being checked, clean, or safe to publish. Any wording
implying they have been checked contradicts a shipped rule, and it is the
sentence most likely to slip in here.

## Step 3: Interview (adaptive discovery)  [SEQUENCE, PROMPT]

The interview is an **adaptive discovery, not a fixed script.** Its job is to reach
a shared, buildable understanding — enough to fill SPEC's What / Who / How /
Principles and capture a first piece of work — by reading each answer and asking
the next question that actually matters.

**Write the project's files once discovery has covered** what the project is, who
it's for, its core, and a first thing to build. Principles and the free-form
"anything else" are optional and don't hold the writing up.

**Where a scaffolding choice is the user's — which folder to adopt, whether
existing content is a doc to leave alone, how to read an ambiguous answer — ask
before acting.** The question costs one turn; a wrong guess makes the user undo a
scaffold.

**The framing throughout is "adopt the folder":** the method is being applied to
their project, not their project reorganised to suit the method.

**Ask one question per message and stop after each, however short the questions
are** — two in one message is bundling.

- **Use the user's own language.** Ask in their words and record their answers in
  their words, rather than rephrasing into the method's vocabulary.
- **Where an answer is vague, ask a follow-up** — subject to the stopping rule
  below, which bounds how far probing goes.
- **Read each answer, then reason about what's still unclear** before choosing the
  next question. Walk the design one branch at a time. The next question is
  generated from what's missing, not from a fixed position in a script.
- **Recommend an answer to each question** rather than asking cold — offer a
  plausible answer the user can accept, correct, or replace ("My guess is this is for
  personal use rather than a team — is that right?"). A no-code developer finds it far
  easier to react to a proposal than to fill a blank.
- **Cover these topics** — a bank to draw on, not a checklist to recite:

```
what the project is, and who it's for   ->  What this is / Who it's for
the core — the main thing it produces,  ->  How it works
    organises, or does
principles or constraints               ->  Principles
    ("must work offline", "no accounts", "everything in plain text")
the project's moving parts, and which   ->  the parts block in CLAUDE.md, and
    of them are the product                 one folder per part (Step 2)
the first thing to build today          ->  becomes the first capture
anything else worth knowing
```

  **The parts question is asked roughly, and a rough answer is accepted.** Offer
  a guess like every other question — "I'd say this has two parts: the app,
  which is the product, and the recipes you're collecting for it, which are
  process — is that right?" — and take what comes back. Where a part is
  neither clearly product nor clearly process, ask which it is rather than
  deciding.

  Skip what an earlier answer or the existing content already settled; probe deeper
  wherever the picture is thin.
- **Explore whatever already exists first.** There may be an old doc, a sketch, a
  notes file, or a running app. Use it to inform your questions rather than asking
  things the existing content already answers. Where there's genuinely nothing,
  interview from a blank slate.

**The stopping rule (the anti-overwhelm guard).** Keep probing only until the
answers bottom out into something concrete enough to build from — you're done when
the Whys are answered, not when every branch is exhausted.
Tell the user plainly, early on, that they can end it any
time by saying **"build from what we have"**, at which point you stop asking and
write the docs from whatever's been gathered.

**The first capture** — whichever answer names the first thing to build — creates
**one rough capture** in Unprocessed: a `#### ` heading **in the user's words**,
with a kebab-case `[slug]` at the end and a "captured by you" note beneath.

**Write the heading in the user's own words, and stop there.** Their words are
the whole content of the item — anything added is Claude's scope decision wearing
the user's voice, and the tempting case is a parenthetical example drawn from
what they said, which reads as a commitment they agreed to.

Scope decisions belong in /plan, which is where this item gets processed. If
examples would clarify scope, ask a follow-up rather than smuggling them in.

Discovery ends where it ends; there is no settings round after it.

The editor and working-mode questions that used to sit here are **gone**,
replaced by one default: point at the doc, with a plain-English summary inline
where a discussion needs one.

## Step 4: Write the docs  [BRIEF, PROMPT]

Once discovery reaches a buildable understanding (or the user says "build from what
we have"), write the docs, then close in a sentence or two and **stop and wait**.

**Write a personal fact into SPEC or any scaffolded document only where the user
supplied it in the interview's own answers.** A name above all. The machine
carries plenty that looks like the user — the git `user.name`, the folder path,
the account the session runs under — and none of it is an answer they gave. Where
a personal fact would improve a document and nobody supplied it, leave it out;
where it is genuinely needed, ask for it as a question like any other.

```
1.  fill SPEC.md from the interview answers
2.  write ONE capture in Unprocessed from the first-thing-to-build answer
    # the user's words, a [slug] at its end, a "captured by you" note.
    # Not multiple scoped entries.
3.  show the user what was created (file list + one line each)
4.  delete `.throughliner-setup-active` from the session scratchpad — the run
    is over, so the declaration from Step 0.5 comes down with it
5.  recommend /done to record this setup and commit the new files
6.  teach the working rhythm (below)
```

The file list shows what appeared in the folder; the session's single summary is
the LOG entry /done writes at close.

**Teach the working rhythm in plain words** — a few short sentences:

- **/setup** you've now run once; you won't run it again for this project.
- From here, two commands carry the work: **/plan** to think and organise, and
  **/next** to build the next thing on the list. Run /plan whenever planning is
  needed, and /next once per item as you work down the queue.
- However a session goes, end it with **/done**, which records what happened
  and saves it. After that the conversation can be cleared: **/clear** wipes
  the conversation on screen and touches none of the project's files, which is
  what makes it safe once /done has run — the next session starts fresh and
  reads everything back from the files. Say the order in words rather than
  stacking the two commands in one sentence, and point at the FAQ entry on why
  every session ends with /done for the longer answer.

## The self-hosting seed  [BRIEF, PROMPT]

For a user building something whose output is instructions — a method, a plugin,
a port, a house style — the discipline for authoring rules their own sessions
will follow can be seeded into the project.

**Two entry points, one seed.**

```
at a fresh setup    ->  one question during the interview: are you building
                        something that will carry its own rules — a method,
                        a plugin, a port?
on an adopted       ->  the user says so at any time ("I want to self-host").
  project               Run the same seed against the project as it stands.
```

**The seed is add-only, in the top-up's never-overwrite discipline.** Nothing the
user wrote is rewritten, and where a file it would create already exists, say so
and leave it alone.

**What it places.**

```
the project's CLAUDE.md   ->  a self-hosting block, appended between its own
                              start and end markers, from
                              ${CLAUDE_PLUGIN_ROOT}/templates/self-hosting-claude-block.md
a retired-terms register  ->  from templates/retired-terms-template.md
a compliance-audit
  checklist               ->  from templates/compliance-audit-checklist-template.md
```

The block carries the rule gate (admission, eviction, distribution, wording), the
disposition-on-the-queue-item pattern with its session-record line, and the
host-versus-target framing. Put the two files where the project keeps its own
notes rather than at a fixed path, and say where they went.

**What is deliberately not seeded, and it is worth saying to the user:** this
project's own release and packaging checklists, and its rule-checking scripts. They
are shaped around one repository's layout, and shipping them would mean
maintaining a tool before anyone has proven they need it. The discipline
generalises; the machinery does not.

**Say what the block is for in one sentence, in the user's own terms** — that
their rule text is a thing they now maintain, and these are the checks that keep
it from growing past what a model will follow. Then get an explicit yes before
writing anything.

