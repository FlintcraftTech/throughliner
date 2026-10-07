---
name: setup
docset: current
---

# /setup

**/setup gives a project the documents that carry the user's intent across every session.** Everything said here is read by a no-code developer who may be new to all of it: say "your project's files", and keep hook filenames, working-file names and internal labels out of what is said.

## Step 0: Is a build running?

**Where `_build-<session-id>.md` (or an older bare `_build.md`) exists in the project folder, a build is in progress, and setup stops here:**

> There's a build running in this project at the moment, and setting up while it runs would leave things half-changed. Finish it, or run the close command to close it, and then start me again.

A planning session is admitted: say that setting up changes a few files outside the usual ones and that the planning work is not saved until the close command runs, then ask "Set up now, or close first?" and do what they say.

**Before writing anything, create an empty `.throughliner-setup-active` in this session's scratchpad.** When the run ends, on every path including a decline or an error, create `.throughliner-setup-done` beside it with the Write tool and leave the active marker in place; the safety check reads the done marker as the end of the run, and this chat's close deletes it last.

**Prerequisites.** Run `gh --version`, `gh auth status` and `git --version`. Where `gh` is missing, offer the install page at https://cli.github.com; where it is not signed in, offer `gh auth login`; where git is missing, offer the install for their operating system. Where the user declines or cannot, say once what follows (without `gh`, no method updates reach this project; without git, no session can end with a commit), write that to `TOOLS.md`, and carry on. Write one line to `TOOLS.md` naming the install channel: `Throughliner channel: local` where the marketplace's source in `~/.claude/plugins/known_marketplaces.json` is a directory, otherwise `stable` or `beta` from the install command, asked once where unknown. For a channel that is not local, say once that the opening will ask GitHub once a week for the newest version.

## Step 1: Detect folder state

```
A  the folder is empty or nearly so            fresh start
B  content exists, no SPEC.md                  fresh start, or a migration of existing planning docs
C  SPEC.md exists                              bring it up to date: version matches -> say so, offer /plan, stop;
                                               version missing or outdated -> the top-up below
D  no SPEC.md here, but a folder above has one  say the line below, then proceed as A
```

**For D:** "This folder sits inside another Throughliner project. It works best moved out to stand by itself; if it stays, that project needs this folder in its .gitignore, or its close will commit these files as its own."

**For B:** read the existing content before the first question and use it to frame the question, with the answer left to the user. Where the folder holds more than one git repository, ask which root this project adopts and record the answer as the Visibility line. Leave existing content untouched and name it at the close as source material. A planning document being migrated is mapped into SPEC's frame (product truth, in place of a UX spec), with any sentence restating the old document's purpose dropped.

## The top-up (state C, outdated)

**Add what a newer version introduced; existing content stays as it is.** Silently, for each item of the scaffold list below: exists, skip; missing, create empty.

**Format migration.** Read the project's recorded epoch from `.throughliner-format-epoch` and compare it with `FORMAT_EPOCH` near the top of `${CLAUDE_PLUGIN_ROOT}/hooks/session_start.py`. Where the recorded epoch is lower, or there is no marker (treat as epoch 1), load `${CLAUDE_PLUGIN_ROOT}/docs/migrate-checklist.md` and follow every epoch section from the recorded number up to the current one, in order, drafting each conversion and getting approval before writing. Where equal, leave it unopened. Any build block a conversion writes under an existing item gets one more line: `Build block written by the format migration on YYYY-MM-DD, not yet checked at planning`.

Write `.throughliner-format-epoch` last among the migration edits, and only when the conversions for that epoch ran to completion. Where the user skipped a conversion, leave the marker at its old value and say plainly that the halt will fire again next session because the conversion is still owed.

**Settings to reconcile:** `.gitignore` carries `INBOX/`, `temp/` and `.throughliner/`; an `INBOX/.address-book.md` with content parses to at least one correspondent (a table row `| name | path |` or a bullet `- name — path`), else report the two shapes; no output style set in `.claude/settings.local.json` gets the style offer below; a SPEC with no `## Goals` heading gets the goals question once, add-only; a CLAUDE.md with no `Task list:` line gets this ask once: "Next: do you already have the Throughliner unified to-do list? If so please share the file's path. Otherwise I can tell you more about how it works." Write `Task list: <absolute path>` or `Task list: none`. Where INBOX files are already in git history, say that the ignore line leaves them tracked.

**Offers, which the run continues past:** to a flat repository, the nested conversion (the split where there is no remote: product files move into a new inner repository; the wrap where there is one: the checkout moves down into a product subfolder by explicit name, `.git` included, and the method's documents come back up), planned file by file on a yes; and, where `MAP.md` names no folder's repository, the structure conversation from the interview over the existing tree.

**Also:** retire `REGISTRY.md` where it holds only what an old setup wrote; prefix a plain-prose preamble under `## Processed` or `## Unprocessed` with `> `; write `.throughliner-version` (renaming an old `.si-version`); report, leaving the text as it is, each retired term found in the project's CLAUDE.md and any "Project docs" section in SPEC:

```
"batch", "Build/Test/Audit"  ->  a work item is one `#### ` heading with a flavor tag
"Deferred tests"             ->  a [user] work line, revisited each planning run
"Parked:"                    ->  held below the cleared-to-run line by Blocked by: or Not before:
"## Parts", "Parts block"    ->  MAP.md says what each folder is for; a part's own SPEC.md is read by nothing
"/next"                      ->  the command that builds the cleared work is /build
```

**Refresh the plugin-managed block in CLAUDE.md** against `${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE-TEMPLATE.md`: where the regions differ, move user-authored lines inside the block below the end marker, replace the region, and say so; where the markers are missing, report it. Skip the interview. Close by naming what was created or updated and recommending /close, or /build to resume where a leftover working file exists.

## Step 2: Scaffold

**Create silently; the close reports the list.**

**SPEC.md:**

````markdown
# SPEC — [Project Name]

## What this is
## Who it's for
## How it works
## Principles
## Goals
[one sentence per goal, each with a "Reached when:" line naming something checkable]
````

**QUEUE.md:**

````markdown
# QUEUE

## Processed

> Vetted work, ready to build — worked top to bottom. Each piece of work is one item: a `#### ` heading naming it, a short name in square brackets at the end of that heading line, and a short rationale beneath. That bracketed name is a handle, so you and Claude can refer to a piece of work without retyping its whole description. A leading flavor tag names how it runs — none for a build, `[audit]` for a review pass, `[user]` for a step only you can do. A security or privacy risk Claude surfaces lives here too, as a work item carrying a `Red flag · State: cleared/uncleared` marker. The line below marks how far down is cleared to build; anything below it is decided but not ready yet.

--- Cleared to run above this line ---

## Unprocessed

> Captured ideas and tasks not yet fully processed. The next /plan run goes through these with you and decides each one's fate — keep it (move it up to Processed) or drop it. Each is filed as its own `#### ` heading, so the list shows up in an editor's outline.
````

**LOG/index.md:** a `# LOG Index` heading and one line saying each line names a session's entry file; the close regenerates it.

**Also:** `MAP.md` from `${CLAUDE_PLUGIN_ROOT}/templates/MAP-TEMPLATE.md` after the interview, one line per approved folder and document and per human-used file already in the tree, each carrying who uses it and when, and which repository holds it; `workshop/resources/research/` and `workshop/resources/supplied/`, empty; `temp/`, gitignored; `INBOX/` with `INBOX/archive/`, gitignored, said in one line; `CLAUDE.md` from `${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE-TEMPLATE.md`, or the method block appended where one exists, with the task-list question asked once; `.throughliner-version` from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`; `.throughliner-format-epoch` from `FORMAT_EPOCH`; `.gitignore` with `.throughliner/`.

**Repositories, the nested shape.** Name the product subfolder with the user in one line, create it, and `git init` at the project root and in the subfolder where either is missing. The inner holds the product alone and is what goes public; the outer stays without a remote and tracks the method's documents privately. Write this into the CLAUDE.md Visibility line. Create exactly the set the structure conversation approved, product folders in the inner and process folders in the outer. The project's one SPEC.md sits at its root.

**Keep-private.** The first message is these lines and nothing else: in a nested project, that the planning documents are tracked in the outer repository, which stays without a remote, keeping them out of anything published; in a flat one, that the spec, the queue and the session records stay out of the repository, because they hold the project's plans, reasoning and history and keeping them out is the only complete protection if the project is ever published. Then **Keep them private?** The yes takes SPEC.md, QUEUE.md and LOG/ together; a user naming a document gets that combination. After the yes in a flat project, report which paths went into `.gitignore`, and say what the choice keeps (Claude writes first and reports; the plugin saves a copy of each previous version into a local folder outside the repository), what it changes (close records the session from memory rather than history), and its limit (the copies live on this machine with no history). Write the answer as the Visibility line.

**Said once, scaffolding only:** where the project's path contains `OneDrive`, `My Drive`, `Google Drive`, `Dropbox`, `iCloud Drive` or `iCloudDrive`, that generated output and a sync client can collide, that on Windows the sync root eats path length, and that mirroring files locally reduces it; and that a markdown reader is recommended for editing drafts outside the app, with the side panel's `.txt` as the fallback.

**The style offer**, once, acceptance the default: Throughliner Brevity, recommended, keeps replies short and decision-led in this project; Throughliner Code Notes adds a short note after each piece of work on why the code is as it is. Name any style already set. Say the reason (a verbose model buries the one thing the user must see), the scope (this project only), and write the choice as `"outputStyle"` in the project's `.claude/settings.local.json`, creating or merging; where the app refuses the write, retry once on the user's word; on a decline, the subject is closed. The style applies from the next message.

**A public repository, only when asked:** re-offer the nested conversion to a flat project; ask what licence the project carries; run `scripts/scrub_sweep.py` under the plugin root with each name the user gives as `--name`, and search `git log -p --all` for those names and email shapes, saying what was found, that removing text leaves it in history, and offering a fresh copy with no history; set it up; say the contents are unscreened and that keeping the documents unpublished is the only complete protection. "Not now" ends it.

## Step 3: Interview

**An adaptive discovery, one question per message, in the user's words, recommending an answer they can accept or correct.** Read what already exists first. Cover: what the project is and who it is for; the core it produces or does; principles or constraints; the documents the person's own work uses; the first thing to build; where the project is heading and how they would know it got there (Goals, each with a "Reached when:" line); anything else. Tell them early they can say **"build from what we have"** at any time. Where the project has more than one person, offer once the line `Unassigned work is <name>'s.` for their own section of CLAUDE.md.

**The structure conversation, three moves, with the creating in the third:** research what documents a person doing this work uses, in the field's own terms; show the smallest defensible set as one numbered list, each a folder or `.md` with who uses it and when and which repository, a folder neither clearly product nor process put to the person, asking "Cut or add by number, or is this the set?"; create exactly the approved set at Step 4.

**The first capture:** file the first-thing-to-build answer as one rough capture with `file_capture`, or the queue tool's `--append Unprocessed`, the heading in the user's own words, a kebab-case slug, a "captured by you" note as the body. A task of the user's own named in any answer is filed as a `[user]` capture with its task line and appended to the task list in the same turn.

**Tools:** name in one line the command-line tools the project's work plausibly needs, ask whether any are missing, then run each tool's version check and write one line per tool to `TOOLS.md`: present with version or absent, and the date. Offer an install where an absent tool is needed by the first capture.

## Step 4: Write

**Write a personal fact into a document only where the user supplied it**; use "they" where no pronoun was given. Fill SPEC.md; create the approved set and MAP.md; file the one capture; show what was created, one line per file, saying the state server's tools are available where it is registered; create `.throughliner-setup-done`; recommend /close; and teach the rhythm in plain words: /setup is run again when an opening says the project has fallen behind; /plan thinks and organises, /build builds everything cleared; every session ends with /close, after which /clear wipes the screen and touches no files.

**The self-hosting seed**, for a user building something that carries its own rules (a method, a plugin, a port): asked once at a fresh setup, or run when the user says so. Add-only. It appends the block from `${CLAUDE_PLUGIN_ROOT}/templates/self-hosting-claude-block.md` to the project's CLAUDE.md between its own markers, and where the project keeps its notes places a retired-terms register from `${CLAUDE_PLUGIN_ROOT}/templates/retired-terms-template.md` and an empty `slips.md` whose one header line says what a line is (the date, what happened, which document governs it), on a yes.
