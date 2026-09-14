---
name: rescan
description: Look back over the conversation for anything decided or noticed but never written down, and file it in the queue. Run it whenever, as often as you like.
disable-model-invocation: true
user-invocable: true
---

# /rescan

The user wants the conversation checked for anything said but never written down. Words typed after the command name name something to check in addition to the full scan, never instead of it — the whole scan runs first, then the named thing.

Rules that apply whatever is running are at
`${CLAUDE_PLUGIN_ROOT}/docs/skill-nonspecific-rules.md`, and they govern this
skill at a level above the procedure below.

**First, check this conversation for the `[Throughliner]` session-start lines.** Where none are present, the hooks did not run — usually because `python` is missing from the machine, or is the Windows Store placeholder that prints "Python was not found" and exits. Say so plainly, give the check (`python --version` must print a version, not "Python was not found"), and carry on with this skill: the procedure docs still govern, and only the safety checks and the session-start facts are absent.

Read and follow the procedure at `${CLAUDE_PLUGIN_ROOT}/docs/rescan.md`. The file may be longer than one read returns; the read is complete only when the tool reports no further page.
