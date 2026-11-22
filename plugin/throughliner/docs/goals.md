---
name: goals
docset: current
note: The /goals procedure. One discussion across every project in the vault, one project per message, ending in two notes written on the user's yes: goals.md, which /tasks sorts by, and strategy.md, which the user reads and shares.
---

# /goals

**/goals settles which of the user's projects come first, and in what order they mean to work on or finish them.** It is one discussion, one project per message, and it writes two notes, only on the user's yes, in the folder holding the note the project's `Task list:` line names:

- `goals.md` is for `/tasks` to read. Its format is the one `tasks.md` reads under "Project priority": a numbered list of project names under `## Priority`, the first ranking first, and an optional `## Held` section listing held projects. Nothing else in it is read.
- `strategy.md` is for the user to read and share. It gives the order at the level of months to years: when they intend to work on or finish each project in relation to the others, written as "this comes after that". It carries no deadlines. A goal may name a date, and nothing enforces it.

It is run in the project that keeps the task-list note. Where the project's `Task list:` line reads `none` or is missing, or no folder above the note holds `.obsidian/`, say so in one line and stop.

## Step 1: Read

**Read the clock first**, with the state server's `clock` tool or a shell command.

**Read, without reporting yet:**

- Every Throughliner project in the vault. The vault is the folder holding `.obsidian/`, found by walking up from the task-list note. A project is a folder holding `SPEC.md` and `QUEUE.md`; folders named `.git`, `node_modules` and `.throughliner` are skipped. For each project read the `#goal` lines in its `SPEC.md` (`- [ ] <goal>, reached when <the test> (<project>) 🆔 <slug> #goal`), the Processed section of its `QUEUE.md`, and the newest line of its `LOG/index.md`.
- `goals.md` and `strategy.md` in the task-list note's folder, where they exist.
- This project's Unprocessed section, for a capture describing a project not yet set up.

**On a later run, take up only the projects whose goals, queue or newest record changed since `goals.md` was last written**, read from its `Written:` line, and any new project. Say in one line which projects are unchanged and left as they stand.

**Then one short message**: how many projects there are, and which ones `goals.md` does not yet list. A project that exists only as a capture is listed separately, one line each.

## Step 2: One project per message

**Take the projects in the order the existing `goals.md` gives, then any it does not list; on a first run, in the vault's folder order.** For each, write a few lines on where it stands: its goals, what is cleared in its queue, and what its last session did. Then ask whether it is still alive, and what finishing it would give the user. Wait for the answer before the next project.

**A project with no `#goal` line gets a goal drafted in the user's words from the conversation.** Show it in a blockquote, and on their yes send it to that project as a capture with `send_capture`. Where the project is not in the address book, say so and leave the draft in the session.

## Step 3: Sort into three groups

**As each project is discussed, put it in one of three groups, saying which in one clause:**

```
must-do            has real-world consequences if it slips
building towards   matters, and its timing is the user's
held               alive but not now; listed under ## Held
```

## Step 4: Order where it is unclear

**Within each group, ask "this one or that one first?" only for a pair whose order is not clear from what the user has said**, one pair per message. Note a dependency as it comes up ("the shop needs the website live first") and order by it without asking. The user is never asked to rank the whole list unaided, and Claude never ranks it alone.

## Step 5: Show and write

**Show the whole order on one screen**: the numbered list, the held projects, and two or three lines of strategy prose. Ask whether to write it. On the user's yes, write both notes.

`goals.md`:

```markdown
# Goals

Written: YYYY-MM-DD, by /goals. Read by /tasks; written only by /goals.

## Priority

1. <project name as its queue lines write it in brackets>
2. ...

## Held

- <project>
```

`strategy.md`: a short heading per group, then the order as plain sentences ("the plugin comes before the shop, because…"), the dates the goals name given as intentions, and the dependencies noted. Date it from the clock.

Then link both notes, `strategy.md` first.

**Out by rule:** writing into any other project's files except through `send_capture` on the user's yes; editing the task-list note; ranking the whole list without the user.
