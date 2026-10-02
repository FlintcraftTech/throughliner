---
name: setup
docset: current
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

**Say so plainly and stop.**

> There's a build running in this project at the moment, and setting up while it
> runs would leave things half-changed. Finish it, or run the close command to
> close it, and then start me again — I'll pick up from there.

Then stop there — no scaffolding, no continue-anyway question, no workaround.

**A planning session is different — it is not refused.** Say what is
about to happen and let the user choose:

> You've got a planning session going here. I can set up now — setting up
> changes a few files outside the usual ones, which is fine and expected. Worth
> knowing that the planning work in this chat isn't saved yet; the close command
> is what records it. Set up now, or close first?

Then wait for their answer, and do what they say.

## Step 0.5: Declare the run  [SILENT]

Before writing anything, create an empty file named
`.throughliner-setup-active` in this session's scratchpad directory. When the
run ends — including on every path that ends early: the user declining above,
a stop partway through, an error — create `.throughliner-setup-done` beside
it, an empty file written with the Write tool, and leave
`.throughliner-setup-active` where it is; no shell command touches either
marker. The safety check reads the done marker as the end of the run. It
stays until this chat's /close run deletes it as its last action: while it
stands beside that run's own marker, the safety check lets the /close run
correct the files setup scaffolded.

## Step 0.7: The GitHub CLI and git prerequisites  [SILENT] when every check passes; [BRIEF, PROMPT] otherwise

**What the prerequisite turn carries.** Which of the checks — the two CLI
checks, or the git check — failed and
what it printed; the one offer that answers it — the install page, or the
sign-in command — and what success looks like; and, on a refusal, the one
plain sentence about what the project will not receive. One ask, at the end.

After the Python check the wrapper names, confirm the GitHub CLI and git: run
`gh --version`, `gh auth status` and `git --version`, and all three must
succeed.

```
all succeed           ->  nothing to say. Write the channel line to TOOLS.md
                          (below) and carry on.
gh missing            ->  offer the install: the CLI's own install page,
                          https://cli.github.com, one command per operating
                          system; then close and reopen the terminal and
                          check again.
not signed in         ->  offer `gh auth login`, a browser flow the user
                          completes; then check again.
the user declines,    ->  say plainly, once: this project will not receive
  or cannot               Throughliner method updates, so it will fall behind
                          the environment it runs in — at minimum, the plugin
                          will not keep up with changes to Claude Code. Write
                          that answer to TOOLS.md and carry on.
git missing           ->  offer the install, one route per operating system
                          as INSTALL.md gives them — Git for Windows, which
                          also supplies Bash; `xcode-select --install` or
                          Homebrew on a Mac; the package manager on Linux;
                          then close and reopen the terminal and check again.
the user declines,    ->  say plainly, once: every session ends with a
  or cannot (git)         commit and cannot make one without git, so every
                          session's ending will fail until it is installed.
                          Write that answer to TOOLS.md and carry on.
```

**Write one line to `TOOLS.md`** — created where the project has none —
naming the channel the user installed from. First read the marketplace's
source from the registry file the opening's update check reads
(`~/.claude/plugins/known_marketplaces.json`, the entry named by the folder
above the plugin's own in its cache path): where its source is a directory,
write `Throughliner channel: local` and ask nothing — a folder install is on
no channel. Otherwise write `Throughliner channel: stable` or
`Throughliner channel: beta`, read from the install command they ran
(`#stable` or `#beta` on the marketplace line), asked once only for an
install from GitHub whose command line is unknown. The weekly check reads
that line; a project with none is treated as stable, and a `local` line means
no check runs.

**Told once, here, and not for a `local` line:** the session opening will call
GitHub once a week to read the newest version on that channel, and what that
tells GitHub is that this machine asked for the plugin's release list.

## Step 1: Detect folder state  [SILENT] while detecting; [BRIEF, PROMPT] when the project is already up to date

```
Case A  no content            the folder is empty or nearly so. Fresh start.
Case B  content, no SPEC.md   the user's own files exist but no method docs.
                              Either a true fresh start OR a MIGRATION.
Case C  already set up,       SPEC.md exists.
        bring it up to date
Case D  inside another        no SPEC.md here, but walking up the folders
        project               finds one. Say the one line below, then
                              proceed as Case A.
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

## Case D: a folder inside an adopted project

"This folder sits inside another Throughliner project. It works best moved out
to stand by itself; if it stays, that project needs this folder in its
.gitignore, or its close will commit these files as its own."

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

**1b. Where the folder already holds more than one git repository — a clone, a
fork, or a `git init` in a subfolder — say so and ask which root this project
adopts** [PROMPT]. Name which repository would hold the method's documents under
each answer, and record the choice as the standing visibility line described at
the keep-private step.

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

## Step 2C: Migration scaffolding  [SILENT] for the checks and file creation; [BRIEF] at /close

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
        ->  skip; the checklist is not opened
no marker file
        ->  the project predates the marker: treat it as epoch 1 and run the
            whole checklist from the beginning
```

**Read the epoch from the marker rather than inferring it from the documents.** The epoch-6
section runs the LOG summary backfill through the backlinks script, once,
shown before it runs.

**Where a conversion writes a build block — or any instruction text — under an
existing queue item, it writes one more line beneath it:**
`Build block written by the format migration on YYYY-MM-DD, not yet checked at planning`,
the date read from the clock.

**1b. Reconcile the settings attached to the scaffold list**  [SILENT] for the
settings added without an answer; [BRIEF, PROMPT] for the brevity-style offer
and for INBOX files already in git history.
Check each, and make it so if it isn't:

```
INBOX/ present          ->  `.gitignore` carries an `INBOX/` line
temp/ present           ->  `.gitignore` carries a `temp/` line
.gitignore present      ->  it carries a `.throughliner/` line
INBOX/.address-book.md  ->  it parses to at least one correspondent, in
  present, with content     either shape the send script reads — a table
                            row `| name | path |` or a bullet `- name — path`;
                            a book that parses to none is reported in one
                            line naming the two shapes, and nothing is
                            rewritten
no outputStyle set in the project's .claude/settings.local.json
                        ->  make the brevity-style offer from Step 2, naming
                            both styles (Throughliner Brevity and Throughliner
                            Code Notes) exactly as a fresh setup would — this
                            project was set up before the style shipped
SPEC.md has no `## Goals` heading
                        ->  ask the interview's goals question once (Step 3),
                            in one line, and write the answer as the section,
                            add-only; "none" writes nothing
CLAUDE.md has no `Task list:` line, or a blank one
                        ->  ask once, in one line, in this shape: "Next: do
                            you already have the Throughliner unified to-do
                            list? If so please share the file's path.
                            Otherwise I can tell you more about how it
                            works." The ask names the list as the one
                            Throughliner appends the user's own steps to as
                            checkbox lines, asks for its full path where one
                            exists, and offers to say more otherwise — the
                            list is read best in Obsidian with the Tasks plugin,
                            whose fields the task line uses, and any markdown
                            editor works; write
                            the answer as `Task list: <absolute path>` in the
                            managed block's Task list section, or at the end
                            of the file where CLAUDE.md carries no managed
                            block. A relative path is refused, since the list
                            sits outside the project and the safety check
                            reads the line for the one file it permits there;
                            "none" writes `Task list: none` and is not asked again
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
one, /close committing both) and which of the two conversions this project
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

**1d. Offer the structure conversation to an existing project**  [BRIEF,
PROMPT] — an offer, never a halt, and never forced. Where the project's
`MAP.md` carries no line naming a folder's repository, offer the interview's
structure conversation (Step 3) over the existing tree: research what a
person doing this work uses, and show one numbered list proposing what to
add, naming what the tree already holds that no line covers, and which
repository each folder sits in — product in the inner, process in the outer,
the looser split stated where the inner will never be public. Nothing is
deleted. On the person's yes, plan the reorganisation with them file by file
and write each folder's map line as the scaffold's structure step writes
them. The map is written from the existing tree either way, each folder's
line as the scaffold writes them; what a no declines is the reorganising
conversation, and the project then keeps the workshop rule as its default,
with nothing running at a later session opening for this. The top-up does
not carry the conversation.

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

```
preamble is already a blockquote  ->  nothing to do
preamble is plain prose           ->  quote it, wording untouched
no preamble under the heading     ->  nothing to do; the scaffold's own
                                      wording is not backfilled here
```

**3. Update `.throughliner-version`**  [SILENT] to the current plugin version.

If the project instead carries the pre-rename marker `.si-version`, write the
new file and delete the old one. Do the same for
`.si-format-epoch` in step 3a.

**3a. Write `.throughliner-format-epoch`**  [SILENT] when the conversion ran to
completion; [BRIEF] when the user skipped it — the document-format number this migration
brings the project up to. Read it from `FORMAT_EPOCH` near the top of
`${CLAUDE_PLUGIN_ROOT}/hooks/session_start.py` and write that number, on its own,
into `.throughliner-format-epoch` at the project root.

Do this **last among the migration edits**, and **only when the conversions for
that epoch ran to completion**.

```
conversion ran to completion   ->  write the new epoch number
user skipped the conversion    ->  leave the marker at its old value, and say
                                   plainly that the halt will fire again next
                                   session because the conversion is still owed
```

**3b. Read the project's own CLAUDE.md for retired terms, and report what you
find**  [SILENT] when clean; [BRIEF] when reporting.

Search the file for each retired term the method carries, and for each hit say
plainly what the term was and what replaced it.

```
retired terms a consumer's CLAUDE.md could carry, with their replacements in
the consumer's words — kept separately from the host register on purpose:
    "batch", "Build/Test/Audit"  ->  a work item is a single `#### ` heading
                                     with a flavor tag; there are no batches
                                     and no sub-headings inside one
    "Deferred tests"             ->  deferred verification is a `[user]` work
                                     line, revisited each planning run
    "Parked:"                    ->  work is held below the cleared-to-run line
                                     by `Blocked by:` or `Not before:`
    "## Parts", "Parts block"    ->  MAP.md's lines say what each folder is
                                     for and which repository holds it; a
                                     part's own SPEC.md is read by nothing
    "/next"                      ->  the command that builds the cleared work
                                     is `/build`; what it does is unchanged
```

**Also read the project's SPEC.md for a "Project docs" section.** Report it the same
way: say the section describes the method rather than their product, that the
same description now lives in the managed block of their CLAUDE.md, and edit
nothing — removing it is their call.

**Report only — edit nothing.**
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

**4. Skip the interview**  [SILENT] — the project is already described in SPEC.md.

**5. Close state-aware**  [BRIEF].

```
a leftover build working file    ->  an earlier build was interrupted: name it
    is present
                                     and recommend resuming with /build. The
                                     migration's new files get recorded when
                                     that build closes.
otherwise                        ->  tell the user what was created or updated
                                     and recommend /close
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

## Goals
[filled by the goals question: one sentence per goal, each with a "Reached
when:" line naming something checkable]
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

Session entries are written by /close, each as its own file in LOG/ carrying its
own summary field, from which the close regenerates this index — nothing else
to scaffold.

**MAP.md** — written from `${CLAUDE_PLUGIN_ROOT}/templates/MAP-TEMPLATE.md`
after the interview, at Step 4: one line per folder and per `.md` document of
the approved set, and one per folder or human-used file already in the adopted
tree — documents, slides, spreadsheets, PDFs, images — with a set of like
files summarised as one line and machinery left out, each line one judgment
under the criterion the template's preamble states. A line for a human-used
file carries two more facts, who uses it and when — its audience and its use
time — and the preamble says so, so a line written later at a file's creation
carries the same two facts. The migration path and the top-up add the map to
an existing project the same way.

**FAQ/ folder** — create the directory **first**, then copy the templates in (the
folder must exist before the copies, or they fail):

```
FAQ/faq.md    <-  ${CLAUDE_PLUGIN_ROOT}/templates/faq-template.md
FAQ/index.md  <-  ${CLAUDE_PLUGIN_ROOT}/templates/faq-index-template.md
```

**workshop/ folder, with `workshop/resources/research/` and
`workshop/resources/supplied/` inside it** — create them
empty, and the top-up adds them to an existing project. `workshop/` is where the project's working material lives — what it works
with rather than what it ships. `workshop/resources/research/` is the home
for research notes (`workshop/resources/research/<topic>.md`),
`workshop/resources/supplied/` is the home for material the user wrote or
attached, written unchanged, and
`workshop/resources/testing/` is the home for re-read-later testing evidence,
created when there is something to put in it.

**temp/ folder** — create it empty, and add `temp/` to `.gitignore` beside the
`INBOX/` line. It is where a session puts what the project does not keep: a
fetched transcript, a file downloaded to read once, a draft that never became a
deliverable. Everything in it is disposable by definition, so nothing records
when it should be deleted. Adding it is where the top-up says the "Markdown
reader, said once" note from scaffolding, once: a markdown reader is
recommended for editing the drafts Claude hands over outside the app, and the
side panel's `.txt` is the fallback.

**INBOX/ folder** — create it empty, with an `INBOX/archive/` inside it. It's this
project's mailbox: another project you run can drop a message file in here, and
session_start surfaces anything waiting in one line. A project only ever reads its
own INBOX — it never goes looking through other projects for mail.

Add `INBOX/` to `.gitignore`, and say so in one line  [BRIEF] — that mail from other
projects stays out of the repository, and they can remove the line if they want it
committed. No question is asked.

**CLAUDE.md:**

```
no CLAUDE.md exists  ->  scaffold from
                         ${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE-TEMPLATE.md
one already exists   ->  APPEND the method block; never overwrite
```

**Where CLAUDE.md was scaffolded here from the template, ask the task-list question once, in the words the top-up's row gives, and write the answer on the template's `Task list:` line** [BRIEF, PROMPT] — the absolute path, or `none`.

**.throughliner-version** — write the current plugin version (from
`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`). session_start reads it to
detect when the plugin has been updated.

**.throughliner-format-epoch** — write the document-format number, read from `FORMAT_EPOCH`
near the top of `${CLAUDE_PLUGIN_ROOT}/hooks/session_start.py`.

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
history and /close's read-back all work from ordinary git. /close
commits both, the product commit into the inner repository and everything
else into the outer. One product subfolder per project; a project with
several outgrowing parts is split by moving a part's folder out and running
setup in it.

**Write the shape into the project CLAUDE.md's Visibility line as part of the
scaffold**: which two repositories exist, which holds the product and goes
public, which holds the documents and never gets a remote. The template's
Visibility slot carries the pattern.

**Only the approved set, in the right repository.** The structure
conversation (Step 3) ends on a list the person approved: folders and `.md`
documents, each with its audience, its use time and its repository. Create
exactly that set — a product folder inside the inner repository, a process
folder in the outer, an empty or stub `.md` only where the list names one —
and no folder or placeholder the list does not name. Each line in `MAP.md`
(Step 4) carries which repository the folder sits in — "inner repository" or
"outer repository" — where the project has two, so a session choosing a
folder for a new file reads the repository off the same line. Where the inner
repository will never be public, say so in one line and let the split be
looser: more may sit alongside the product there. No part gets a `SPEC.md` of
its own: the project has one spec, the root, and a build reads it once at run
start.

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
outer repository, which never gets a remote, and the second says that an outer
repository that never gets a remote
keeps them out of anything published while keeping their history.
Nothing else goes in that message:
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
all three; a user who names a document gets just that combination. The
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
CHANGED  /close cannot read its own work back from the file's history, so
         it records the session from what it remembers.
LIMIT    those saved copies live on this machine and carry no history, so a
         lost disk loses them. Say this rather than describing the net as an
         equal replacement for git.
```

They also do not travel with a clone.

**Nothing here is asserted again later as a fault.** Every session opening
reports which of the three are untracked and what follows.

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
"The public-repository offer — one subject, six provisions", below.

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

**Markdown reader, said once**  [BRIEF]. Say in one sentence that a markdown
reader is recommended for editing the drafts Claude hands over outside the
app, and that the side panel's `.txt`, the one file type it edits and saves,
is the fallback. A note, not a rule: it asks nothing and stores nothing. Said
once here at scaffolding, and once by the top-up step that adds `workshop/`
and `temp/` to an existing project.

**Whichever arm the fork lands in, the proposed configuration is what a user
who says nothing about it ends up with — private via the ignore in a flat
project, private by architecture in a nested one.** Acceptance is the default
here and at the style offer: the material is the most personal the
method produces.

**The brevity-style offer**  [BRIEF, PROMPT]. The plugin ships two output
styles, and the offer names both in one message: Throughliner Brevity,
recommended, which keeps Claude's replies short and decision-led in this
project; and Throughliner Code Notes, which is the same plus a short note
after each piece of work on why the code is the way it is, read afterwards,
with builds running the same and taking longer. Offer once, as part of
scaffolding, opt-out with acceptance as the default.

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
user accepts (the default)  ->  write whichever was chosen as "outputStyle" —
                                "Throughliner Brevity" where the user accepts
                                without choosing, "Throughliner Code Notes"
                                where they chose it — into the project's
                                .claude/settings.local.json (creating the
                                file if absent, merging if not)
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

**The public-repository offer — one subject, six provisions** [DISCUSS,
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

- before the repository is set up, search what will be published —
  `scripts/scrub_sweep.py` over the repository's root, with each name the user
  gives passed as `--name`, and `git log -p --all` searched for those names
  and for email-address shapes; say what was found, that removing text from a
  file does not remove it from history, and offer a fresh copy with no history
  as the alternative to publishing the history as it stands;
- set up the repository;
- describe the contents as unscreened, and say what the only complete protection
  is — not publishing these documents, which is what the keep-everything-private
  option above does;
- treat "not now" as a plain answer that ends it, with the offer not repeated
  and nothing set aside for later.

The method scans for things shaped like credentials and reads its own writing
against a checklist, and neither can tell whether a sentence quietly identifies
a real person — so this offer may set up the repository and may say nothing
about the documents being checked, clean, or safe to publish.

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
before acting.**

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
  personal use rather than a team — is that right?").
- **Cover these topics** — a bank to draw on, not a checklist to recite:

```
what the project is, and who it's for   ->  What this is / Who it's for
the core — the main thing it produces,  ->  How it works
    organises, or does
principles or constraints               ->  Principles
    ("must work offline", "no accounts", "everything in plain text")
the documents the person's own work     ->  the structure conversation (below):
    uses, and which are the product         only the approved set is created
the first thing to build today          ->  becomes the first capture
where the project is heading, and how   ->  Goals — one sentence per goal,
    the user would know it got there        each with a "Reached when:" line
                                            naming something checkable; asked
                                            after the five topics above
anything else worth knowing
```

  **The goals question is asked once in an existing project too:** the top-up,
  meeting a SPEC with no `## Goals` heading, asks it in one line and writes the
  answer as the section, add-only; a project that answers "none" gets no
  section and is not asked again. A recurring need or a task named in the
  answer is filed at that turn as a `[user]` capture carrying its task line,
  appended to the user's task list where the project names one, per the
  task-line provision in skill-nonspecific-rules.md — never noted for
  planning.

  **Where the interview, or the top-up on the user's word, learns the project
  has more than one person, offer the default line once:** one line in the
  user's own section of the project's CLAUDE.md, in exactly this shape —
  `Unassigned work is <name>'s.` — naming whose an entry with no
  `Assigned to:` line is. The queue lint reads that shape and no other, so
  the offer shows the line as it will be written; a project of one person is
  not asked.

  **The parts question is the structure conversation, in three moves, and
  nothing is created until the third.** The project's structure is worked out
  with the person before any folder exists, so what lands in the tree is what
  they use and nothing that would later read as the product.

  1. **Research what documents a person doing this work uses.** From what the
     interview says the project is, run a bounded read — under the research
     rule in skill-nonspecific-rules.md, run rather than offered — of what
     that field's own practice calls its documents, in the field's own terms,
     and infer from those the folders needed to reach them. The limit: the
     research reaches what the field has written down about its own
     documents; a person's unusual practice is what the next move is for.
  2. **Show the smallest defensible set inline, as one numbered list**, each
     line a folder or a `.md` document with who uses it and when, and which
     repository it sits in where the project has two — product in the inner,
     process in the outer, and a folder that is neither clearly one nor the
     other put to the person rather than decided. The person cuts or adds by
     number; the ask is whether the list is right.

     > 1. `programme/` — the workshop programme, one folder per day — outer
     > 2. `programme/day-1/handout.md` — the participants' handout, read by
     >    them on the day — outer
     > 3. `app/` — the booking app, the product — inner
     >
     > **Cut or add by number, or is this the set?**

  3. **Create exactly the approved set** at Step 4: the folders and the
     empty-or-stub `.md` files the list names, no placeholders beyond it, and
     `MAP.md` written from the list with each line carrying the audience and
     use time the list gave it.

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

**The first capture** — whichever answer names the first thing to build — files
**one rough capture** in Unprocessed through the state server's `file_capture`
tool where the server is registered, and the queue tool's
`--append Unprocessed` otherwise, the same way every other capture is filed:
the tool is given the heading **in the user's words**, a kebab-case slug and a
"captured by you" note as the body, and it stamps the entry itself. Where the
answer names a task of the user's own — a recurring one among them — it is
filed as a `[user]` capture carrying its task line and appended to the user's
task list in the same turn, under the same provision as the goals question
above.

**Write the heading in the user's own words, and stop there.** Their words are
the whole content of the item.

Scope decisions belong in /plan, which is where this item gets processed. If
examples would clarify scope, ask a follow-up rather than smuggling them in.

## Step 3.5: The project's own tools  [BRIEF, PROMPT] for the ask; [SILENT] for the probe

**What the tools turn carries.** The command-line tools the project's work
plausibly needs, named from the interview's answers, in one line; the one
ask, whether any are missing; then, with no further asks, the result of each
tool's own version check written to `TOOLS.md`.

From the interview's answers, name the command-line tools the project's work
plausibly needs. The kind of thing the work produces decides them: a website
wants a static-site builder and its host's command-line tool; documents want
a converter; data wants the interpreter and its libraries. Say the list in one
line and ask whether any are missing, then stop and wait.

On the answer, run each tool's own version check, and write one line per
tool to `TOOLS.md` — created where the project has none — in the file's
existing shape: the tool, present with its version or absent, and the date
checked, read from the clock.

```
a tool is absent, and the first piece of  ->  offer the install, in the
  work captured at the interview needs it     shape of Step 0.7's offers;
                                              a decline is written as the
                                              fact it is
a tool is absent, and nothing captured    ->  the absent line alone; no
  yet needs it                                offer
the project's work needs no               ->  write nothing, and say so in
  command-line tool                           one clause
```

The top-up
does not carry this step: an existing project's `TOOLS.md` fills as sessions
learn facts, any of which may write one the moment it is learned.

## Step 4: Write the docs  [BRIEF, PROMPT]

Once discovery reaches a buildable understanding (or the user says "build from what
we have"), write the docs, then close in a sentence or two and **stop and wait**.

**Write a personal fact into SPEC or any scaffolded document only where the user
supplied it in the interview's own answers.** A name and pronouns above all —
where no pronoun was supplied, the documents use "they". The machine
carries plenty that looks like the user — the git `user.name`, the folder path,
the account the session runs under — and none of it is an answer they gave. Where
a personal fact would improve a document and nobody supplied it, leave it out;
where it is genuinely needed, ask for it as a question like any other.

```
1.  fill SPEC.md from the interview answers; create the approved set from
    the structure conversation and nothing beyond it; write MAP.md from the
    template — one line per approved folder and document carrying its
    audience and use time, one judgment per folder and per human-used file
    already in the adopted tree, sets summarised, machinery left out
2.  file ONE capture in Unprocessed from the first-thing-to-build answer,
    # through the state server's file_capture tool where the server is
    # registered and the queue tool's --append Unprocessed otherwise:
    # the user's words as the heading, a slug, a "captured by you" note.
    # Not multiple scoped entries, and never written by hand.
3.  show the user what was created (file list + one line each), and say in
    one line that the state server's tools are available from here, where
    the server is registered — so a chat that falls to the scripts does
    not do so silently
4.  create an empty `.throughliner-setup-done` in the session scratchpad
    with the Write tool, leaving `.throughliner-setup-active` where it is —
    the safety check reads the done marker as the end of the run, and it
    says setup ran in this chat
5.  recommend /close to record this setup and commit the new files
6.  teach the working rhythm (below)
```

The file list shows what appeared in the folder; the session's single summary is
the LOG entry /close writes at close.

**Teach the working rhythm in plain words** — a few short sentences:

- **/setup** you've now run once; you'll run it again only when a session's opening says the project has fallen behind the method.
- From here, two commands carry the work: **/plan** to think and organise, and
  **/build** to build the next thing on the list. Run /plan whenever planning is
  needed, and /build to work through everything cleared, several items in one run.
- However a session goes, end it with **/close**, which records what happened
  and saves it. After that the conversation can be cleared: **/clear** wipes
  the conversation on screen and touches none of the project's files, which is
  what makes it safe once /close has run — the next session starts fresh and
  reads everything back from the files. Say the order in words rather than
  stacking the two commands in one sentence, and point at the FAQ entry on why
  every session ends with /close for the longer answer.

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

