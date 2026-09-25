---
name: plan
description: All thinking work — manage the queue, handle ideas and questions, detect drift, read back test results. No building happens here.
disable-model-invocation: true
user-invocable: true
---

# /plan

The user wants to do planning work — managing the queue, adding ideas, resolving questions, or checking for drift.

Rules that apply whatever is running are at `${CLAUDE_PLUGIN_ROOT}/docs/skill-nonspecific-rules.md`, and they govern this skill at a level above the procedure below.

**First, check this conversation for the `[Throughliner]` session-start lines.** Where none are present, the hooks did not run — usually because `python` is missing from the machine, or is the Windows Store placeholder that prints "Python was not found" and exits. Say so plainly, give the check (typing `py --version` or `python --version` — either printing a version number means Python is there, and "Python was not found" from both means the hooks did not run), and carry on with this skill: the procedure docs still govern, and only the safety checks and the session-start facts are absent.

Read and follow the procedure at `${CLAUDE_PLUGIN_ROOT}/docs/plan.md`. The file may be longer than one read returns; the read is complete only when the tool reports no further page.
