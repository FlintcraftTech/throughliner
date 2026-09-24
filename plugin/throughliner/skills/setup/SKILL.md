---
name: setup
description: Set up a project folder with the Throughliner method. Scaffolds SPEC.md, QUEUE.md, and LOG/ then interviews the user to populate them.
disable-model-invocation: true
user-invocable: true
---

# /setup

The user wants to bring this folder under the Throughliner method.

**First, check this conversation for the `[Throughliner]` session-start lines.** Where none are present, the hooks did not run — usually because `python` is missing from the machine, or is the Windows Store placeholder that prints "Python was not found" and exits. Say so plainly, give the check (`python --version` must print a version, not "Python was not found"), and carry on with this skill: the procedure docs still govern, and only the safety checks and the session-start facts are absent.

**Second and third prerequisites, after Python: the GitHub CLI, and git.** `gh --version` and `gh auth status` must both succeed, and `git --version` must print a version; the procedure's Step 0.7 says what to offer where any fails, and what a refusal costs — without the CLI the project will not receive method updates, and without git no session close can commit.

Read and follow the procedure at `${CLAUDE_PLUGIN_ROOT}/docs/setup.md`. The file may be longer than one read returns; the read is complete only when the tool reports no further page.

Before writing anything, create an empty `.throughliner-setup-active` file in
this session's scratchpad directory, and when the run ends — including on the
paths that end early — rename it to `.throughliner-setup-done`. The first tells
the safety check this is a setup run; without it, the files setup exists to
write are refused. The second says setup ran in this chat, so this chat's /close
run may correct the files setup scaffolded; /close deletes it.
