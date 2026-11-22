# Throughliner

![Throughliner](throughliner-icon-badge.png)

A Claude Code plugin for people who build things without writing code. You say what you want, Claude builds it, and Throughliner keeps everything organized across sessions so context never drifts or gets lost.

## What makes it different

Every project keeps a written record of *why* things are built a certain way (`SPEC.md`, `QUEUE.md`, `LOG/`). Claude reads this record before planning or building — even in a fresh session with no prior memory — ensuring your original intent is always preserved.

- **Settled decisions stay settled:** rejected ideas retain their reasoning so they don't resurface.
- **Silent regressions are caught:** historical context prevents unwanted changes.
- **Seamless handoffs:** easily pick up where you left off after a break, or hand the project to someone else.
- **Checked writes:** a small local server, connected when the plugin is installed, files captures and moves queue work with every field checked before anything lands.
- **One task list across projects:** each step of yours that needs no walkthrough carries one checkbox line inside its own queue item, in the Obsidian Tasks plugin's marks, and the note your `Task list:` line names holds the queries that gather them across every project; tick the line and the next planning session closes the item. Any markdown editor shows the lines as plain checkboxes.
- **Your own edits are noticed:** change a draft, a project file or a post by hand and the next session that reads it sorts the change — a plain fix is accepted and noted, while an edit that reverses a decision or contradicts something is asked about, with every place it now disagrees with named.
- **Recurring work on a cycle:** ask for something you do repeatedly — a release, a posting rhythm, a review — to go on a cycle, and every session's opening says when a turn is due; a named step list runs when you say its name.
- **Work tagged by how it runs:** an item is a build Claude does alone, an `[audit]` that reads and reports, a `[user]` step walked through with you, `[co-write]` text finished together, or `[freeform]` work done by hand with Claude in a chat of its own, which a build run stops at, so you know before a run what each item will ask of you.
- **A line that bounds the run:** the queue carries a cleared-to-run line and a build run builds only what sits above it, so what is agreed and ready is separate from what is agreed and waiting.
- **Projects kept current:** once a week the session opening checks for a newer plugin and a planning session offers the update, and where a project's files need to change shape the session halts and points you at setup, which migrates them, instead of running on a stale layout.

## Installation

### New to Claude Code?

1. Open a fresh chat at [claude.ai](https://claude.ai).
2. Paste this link: `https://github.com/FlintcraftTech/throughliner/raw/main/INSTALL.md`
3. Ask Claude to **read the guide and walk you through it step by step**.

The guide verifies Python, Git, the `claude` tool, and GitHub's `gh` tool before running the installation commands.

### Already have Claude Code?

Run these two commands in your terminal:

```
claude plugin marketplace add FlintcraftTech/throughliner#stable
claude plugin install throughliner@flintcraft
```

Fully restart Claude Code to load the plugin. To update later, run `claude plugin marketplace update flintcraft` and then `claude plugin update throughliner@flintcraft`, and restart again.

## Core workflow and slash commands

The plugin splits your project into a structured build queue managed by ten main commands:

- **`/setup`** — interviews you about your project, works out with you the smallest set of folders and documents your work actually uses before creating any of them, scaffolds text documents (`SPEC.md`, `QUEUE.md`, etc.), checks your machine for the command-line tools your project's work will need and records what it finds in `TOOLS.md`, and offers two styles for Claude's replies: Throughliner Brevity, which keeps them short, and Throughliner Code Notes, which adds a short note after each piece of work on why the code is the way it is.
- **`/plan`** — an open planning session: it reports where the queue stands, then takes up whatever you raise, capturing new ideas and resolving design questions. Its opening also reads the signs that a project has outgrown one queue and names moving a part out where one holds.
- **`/process`** — works through the captures waiting in the queue one at a time; each is discussed, then kept as agreed work or deleted on your word.
- **`/build`** — builds the cleared work from the top, several items in one run, walks you through any steps that are yours, and stays locked to the files that work names.
- **`/rescan`** — reviews past conversation history to capture unrecorded decisions or notes into the queue.
- **`/close`** — records session outcomes, commits changes to Git, and tees up next steps. Always run this before `/clear`.
- **`/catchup`** — a brief for returning after time away: one line per goal with where you stand against it, then the few changes you will notice from the last fourteen days, then what a build would do next, what waits on you, and what is held on a date. It also re-runs the return checks a fresh chat runs: a cycle due now, the plugin version changed under the chat, the date moved.
- **`/tasks`** — works your own tasks one at a time, most urgent first: every step of yours that any project in your vault keeps as a task line, read through the Obsidian Tasks note your `Task list:` line names. Run it in the project that keeps that note; a task you finish goes back to its project as a capture.
- **`/memory-setup`** — builds one memory about you that every project on your machine reads: small notes in a folder in your home `.claude` folder, filled from a prompt you run in Claude chat, loaded by every session through one index. Run it again whenever chat has learned more. The memory stays on your machine.
- **`/goals`** — one discussion across every project in your vault, one project at a time, that settles which come first: must-do, building towards, or held. On your yes it writes `goals.md`, the ranked list `/tasks` sorts by, and `strategy.md`, the order in plain sentences for you to read and share. Run it in the project that keeps your task-list note.

A chat with no command is a normal way to work too: talk, think and make changes by hand, and the close command records it.

## Project structure

Setup adds plain-text documentation and folders to your repository:

- **`SPEC.md` / `QUEUE.md`** — what you are building, and what to work on next.
- **`LOG/` and `workshop/`** — historical session records, research, and testing drafts. Each record carries its own one-line summary, and the index is generated from those at every close.
- **`MAP.md`** — a map of what the project's folders and human-used files are for, written for Claude to read first each session, so nothing sits in a folder it never opens.
- **`TOOLS.md`** — persistent memory of what Claude has learned about your machine.
- **`temp/`** — the project's disposable working files, drafts handed over for editing among them, cleared at the close on your yes and kept out of git.
- **`.throughliner/`** — the plugin's working folder, kept out of git. It holds the register of everything the project has sent; projects send each other captures, added straight to the other project's queue on your yes.

## Getting started

1. Open any project folder in Claude Code.
2. Run `/setup` to scaffold your project docs.
3. Run `/process` to turn your first capture into agreed work.
4. Run `/build` to start building!

## Community and support

Throughliner has a [Discord server](https://discord.gg/8qmuEwTy8u). It is where new versions are announced and where you can say so if something breaks.

### New to the plugin?

The **how-to** posts on the Discord walk you through the plugin one feature at a time, written for people who have never used a terminal. Start there before reading anything else.

The [FAQ site](https://flintcrafttech.github.io/throughliner/) holds every question the plugin's own FAQ answers, one page each, with a search box across all of them.

### Porting the plugin?

Running the method on a tool other than Claude Code is supported. The Discord is where porters compare notes and where port-facing news lands. The repository's [porting/](porting/) folder holds the changelog written for ports and a paste-ready prompt for porting with Claude's help.

### Companion skills

Separate skills built to run alongside Throughliner, each needing it installed and none part of it.

- [Email processing](https://github.com/its-coughfee/email-processing) — works through your Gmail inbox oldest first, one email at a time, with a short summary and one suggested action each, acted on only on your yes. Tested only with Gmail.

## License

See [LICENSE](LICENSE).
