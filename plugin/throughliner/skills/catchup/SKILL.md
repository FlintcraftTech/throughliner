---
name: catchup
description: A brief for coming back to the project after time away — one line per feature with where it stands, then what a build would do next, what waits on you, and what is held on a date. Files nothing, moves nothing.
disable-model-invocation: true
user-invocable: true
---

# /catchup

The user is coming back to this project after time away and wants to know where its important features stand, in a few lines, and nothing else. It runs at any time, and runs best after a planning or build session has opened, since it reuses that opening's reads.

Rules that apply whatever is running are at `${CLAUDE_PLUGIN_ROOT}/docs/skill-nonspecific-rules.md`, and they govern this skill at a level above the procedure below.

**First, check this conversation for the `[Throughliner]` session-start lines.** Where none are present, the hooks did not run — usually because `python` is missing from the machine, or is the Windows Store placeholder that prints "Python was not found" and exits. Say so plainly, give the check (typing `py --version` or `python --version` — either printing a version number means Python is there, and "Python was not found" from both means the hooks did not run), and carry on with this skill: the procedure docs still govern, and only the safety checks and the session-start facts are absent.

Read and follow the procedure at `${CLAUDE_PLUGIN_ROOT}/docs/catchup.md`. The file may be longer than one read returns; the read is complete only when the tool reports no further page.
