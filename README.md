# Throughliner

![Throughliner](throughliner-icon-badge.png)

A Claude Code plugin for people who build things without writing code. You say what you want, Claude builds it, and Throughliner keeps everything organized across sessions so context never drifts or gets lost.

## What makes it different

Every project keeps a written record of *why* things are built a certain way (`SPEC.md`, `QUEUE.md`, `LOG/`). Claude reads this record before planning or building — even in a fresh session with no prior memory — ensuring your original intent is always preserved.

- **Settled decisions stay settled:** rejected ideas retain their reasoning so they don't resurface.
- **Silent regressions are caught:** historical context prevents unwanted changes.
- **Seamless handoffs:** easily pick up where you left off after a break, or hand the project to someone else.

## Installation

### New to Claude Code?

1. Open a fresh chat at [claude.ai](https://claude.ai).
2. Paste this link: `https://github.com/FlintcraftTech/throughliner/raw/main/INSTALL.md`
3. Ask Claude to **read the guide and walk you through it step by step**.

The guide verifies Python, the `claude` tool, and GitHub's `gh` tool before running the installation commands.

### Already have Claude Code?

Run these two commands in your terminal:

```
claude plugin marketplace add FlintcraftTech/throughliner#stable
claude plugin install throughliner@flintcraft
```

Fully restart Claude Code to load the plugin. To update later, run `claude plugin marketplace update flintcraft` and then `claude plugin update throughliner@flintcraft`, and restart again.

## Core workflow and slash commands

The plugin splits your project into a structured build queue managed by six main commands:

- **`/setup`** — interviews you about your project, scaffolds text documents (`SPEC.md`, `QUEUE.md`, etc.), and sets a brevity style for Claude's replies.
- **`/plan`** — organizes the queue, captures new ideas, and resolves design questions.
- **`/next`** — builds the next piece of ready work, staying locked to relevant files.
- **`/rescan`** — reviews past conversation history to capture unrecorded decisions or notes into the queue.
- **`/done`** — records session outcomes, commits changes to Git, and tees up next steps. Always run this before `/clear`.
- **`/catchup`** — summarizes feature statuses (shipped, ready, waiting) when returning after time away.

## Project structure

Setup adds plain-text documentation and folders to your repository:

- **`SPEC.md` / `QUEUE.md`** — what you are building, and what to work on next.
- **`LOG/` and `workshop/`** — historical session records, research, and testing drafts.
- **`TOOLS.md`** — persistent memory of what Claude has learned about your machine.
- **`INBOX/`** — messaging hub if you run multiple connected projects.

## Getting started

1. Open any project folder in Claude Code.
2. Run `/setup` to scaffold your project docs.
3. Run `/plan` to organize your first piece of work.
4. Run `/next` to start building!

## Community and support

Throughliner has a [Discord server](https://discord.gg/Z7ftKnSjR). It is where new versions are announced and where you can say so if something breaks.

### New to the plugin?

The **how-to** posts on the Discord walk you through the plugin one feature at a time, written for people who have never used a terminal. Start there before reading anything else.

### Porting the plugin?

Running the method on a tool other than Claude Code is supported. The Discord is where porters compare notes and where port-facing news lands. The repository's [porting/](porting/) folder holds the changelog written for ports and a paste-ready prompt for porting with Claude's help.

## License

See [LICENSE](LICENSE).
