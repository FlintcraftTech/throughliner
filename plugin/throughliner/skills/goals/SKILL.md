---
name: goals
description: Decide which of your projects come first — one discussion across every project in your vault, one project at a time, ending in a ranked list your task sessions sort by and a short plain-English strategy note you can read and share. Run it in the project that keeps your task-list note.
disable-model-invocation: true
user-invocable: true
---

# /goals

The user wants to review their goals across all their projects and settle the order they come in. It is run in the project that keeps the note their `Task list:` line names.

Rules that apply whatever is running are at `${CLAUDE_PLUGIN_ROOT}/docs/skill-nonspecific-rules.md`, and they govern this skill at a level above the procedure below.

**First, check this conversation for the `[Throughliner]` session-start lines.** Where none are present, the hooks did not run — usually because `python` is missing from the machine, or is the Windows Store placeholder that prints "Python was not found" and exits. Say so plainly, give the check (typing `py --version` or `python --version` — either printing a version number means Python is there, and "Python was not found" from both means the hooks did not run), and carry on with this skill: the procedure docs still govern, and only the safety checks and the session-start facts are absent.

Read and follow the procedure at `${CLAUDE_PLUGIN_ROOT}/docs/goals.md`. The file may be longer than one read returns; the read is complete only when the tool reports no further page.
