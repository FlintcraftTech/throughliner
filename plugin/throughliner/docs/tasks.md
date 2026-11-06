---
name: tasks
docset: current
note: The /tasks procedure. The user's own tasks from every project in the vault, read through the note their Task list: line names, worked one at a time; a done task goes back to its project as a capture.
---

# /tasks

**/tasks works the user's own tasks, one at a time, most urgent first.** A task is a `#user` task line inside a queue item, in whichever project's queue it lives; the note the project's `Task list:` line names holds the Obsidian Tasks queries that gather them, and that note defines the list. The skill reads the queries and resolves them itself, since a session sees the query text and not the rendered view. It keeps no file of its own and writes to no other project's queue: a done task becomes a capture to the project that owns it, and that project's planning closes the item. It is run in the project that keeps the note; run elsewhere, it says so and stops.

## Step 1: Read the list

**Read the clock first**, with the state server's `clock` tool or a shell command. Every date below is measured against it.

**Read the note the `Task list:` line names, whole.** Where the line reads `none` or is missing, say that this project keeps no task-list note and stop. Collect every ```` ```tasks ```` block in it. Where the note holds none, say so in one line, offer the two-line query `not done` and `tags include #user` for this session only, and run on it; nothing is written into the note. `tags include #user` gathers a `#user/<name>` line too, so in a shared project a person's own note filters with `tags include #user/<name>`.

**Resolve each query over the vault.** The vault is the folder holding `.obsidian/`, found by walking up from the note. The lines a query runs over are every `- [ ]` and `- [x]` line carrying `#user` in every `QUEUE.md` under the vault, folders named `.git`, `node_modules` and `.throughliner` skipped. The filter lines read are: `done` and `not done`; `tags include` and `tags do not include`; `path includes` and `path does not include`; `due`, `scheduled` and `starts` with `before`, `after` or `on` and a date; `has due date` and `no due date`; `description includes` and `description does not include`. A filter line not on that list is named in one line as left unread and dropped, so the session shows more rather than less. `sort by`, `group by`, `limit`, `hide` and `show` lines are ignored: the order is this procedure's own. The tasks of the session are the union of every block's results.

**A task's fields** are the Tasks plugin's marks on its line: `📅` due, `⏳` scheduled, `🛫` start, `🔁` recurrence, `🆔` its slug, `⛔` the slugs it waits on, `✅` the tick date, and the project name in brackets. Its owning project is the folder holding the queue it was read from. Subtasks indented beneath a line travel with it and are not ranked on their own.

## Step 2: Open

**First ask "Any tasks to add?"** and wait. A task the user names is filed at once as a `[user]` capture carrying its task line: into this project's queue with `file_capture` where it names no project or names this one, otherwise sent to the project it names with `send_capture` on the user's yes to the exact text. A capture filed into this project joins the session's ranking at once; one sent elsewhere is read at that project's planning. The project this skill runs in is also where every other project sends a task that belongs to no project, so its queue holds the user's general tasks beside its own.

**Then the waiting-first questions.** For each task whose line carries "waiting on", one per message, ask whether the reply has come, naming who and since when as the line gives them. A yes makes the task ordinary for the rest of the session; a no leaves it, with nothing written.

**Then the opening line**, stating as facts: how many tasks are up for this session; how many are held back, with the three reasons folded into one count; and how many are waiting. Held back and never presented: a task whose `📅` or `⏳` date is more than seven days after the clock's date; a task whose `🛫` date has not come; and a task whose `⛔` names a line not yet ticked, or whose wording says it waits on something ("once …", "after …"). Undated tasks are up.

## Step 3: Work the tasks

**The order**, each rule breaking only the ties the one above leaves: overdue, oldest due date first; then due within seven days of the clock's date, soonest first; then the task that unblocks the most others, read from the `⛔` marks of unticked lines naming its `🆔`; then project priority; then the order the tasks hold in their project's queue. Priority marks are not read.

**Project priority** is read from a `goals.md` note in the folder that holds the task-list note, written by the user's own goals skill: a numbered list of project names under a `## Priority` heading, the first name ranking first, a project not listed ranking after every listed one. Where the note carries a `## Held` section, the projects it lists sink to the bottom of the session's order, after every other task, and the opening line says in one clause which projects are held. No session writes to the note. Where the note, the heading or the list is absent, nothing changes and the order falls through to queue order.

**Before a task is presented, check whether it is already done or changed**: read the owning project's `QUEUE.md` for its item and for a capture naming the task's slug as done, and the owning project's `LOG/index.md` for a record under the slug. A task found done or changed is presented as that finding and a one-line ask to confirm it, and nothing else; the user's yes sends the done capture as below.

**Present one task per message and wait.** The message quotes the task line, says in one sentence why it is up now (overdue by how many days, due when, what it unblocks), names what Claude can do towards it from the machine and offers it, and ends on one bold question asking how the user wants to handle it. From there, in any mix: discuss it; walk it, one step per message, the rules doc's hand-over sentence applying to each step; split it; or skip it. Nothing is sent, bought, submitted or posted without the user's yes to that one action, and a message Claude drafts for a task is shown first.

**What the skill writes:**

- **Done** — the task's owning project gets one capture through `send_capture`, on the user's yes to the exact text: heading `<the task> done`, slug `<the task's slug>-done`, body saying the date it was done, how it went in two or three sentences and anything learned, the register line's intent `for completion`. The owning project's planning ticks the line and closes the item; until then the line stays unticked in the user's view, and the user may tick it in Obsidian at any time, which the owning project's planning reads the same way. A task owned by this project gets the same capture through `file_capture` into this queue instead. Where the owning project is not in this project's address book, say so and offer to record its folder there as `feedback-and-inbox.md`'s address-book paragraph allows, the task left open until the send goes.
- **Split** — each subtask is a line in the done capture's body, or, where the task stays open, in a capture to the owning project headed `<the task> split`, carrying the subtasks as checkbox lines for that project's planning to write under the item.
- **Learned something, task still open** — one capture to the owning project headed `<the task> — <the note>`, carrying the note; one capture per task per session, gathering every note.
- **Skipped** — nothing. The task comes up again next session.

After each write, one line naming what landed, from the tool's own return.

## Step 4: End

**When the user says they are done, or no task is left**, ask "Any tasks to add?" once more and file any as at the opening. Then say how many were done, split and skipped, and that running the close command, named in words, records the session. The project's own `CLAUDE.md` may carry habits of the user's for the end of a task session; they run as written there.

**Out by rule:** writing into any other project's queue or records, or into the goals note; ticking a line anywhere; editing the task-list note; reading a project's queue beyond the task's item, its done captures and its record index; ranking by priority marks, or by project other than through the goals note's list.
