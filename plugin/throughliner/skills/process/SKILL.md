---
name: process
description: Work through the captures waiting in the queue, one at a time — each is discussed, then kept as agreed work or deleted. No building happens here.
disable-model-invocation: true
user-invocable: true
---

# /process

The user wants to work through the captures waiting in the queue, one at a time, deciding for each whether it is kept as work or deleted.

Rules that apply whatever is running are at `${CLAUDE_PLUGIN_ROOT}/docs/skill-nonspecific-rules.md`, and they govern this skill at a level above the procedure below.

**First, check this conversation for the `[Throughliner]` session-start lines.** Where none are present, the hooks did not run — usually because `python` is missing from the machine, or is the Windows Store placeholder that prints "Python was not found" and exits. Say so plainly, give the check (typing `py --version` or `python --version` — either printing a version number means Python is there, and "Python was not found" from both means the hooks did not run), and carry on with this skill: the procedure docs still govern, and only the safety checks and the session-start facts are absent.

Read and follow the procedure at `${CLAUDE_PLUGIN_ROOT}/docs/process.md`. The file may be longer than one read returns; the read is complete only when the tool reports no further page.
