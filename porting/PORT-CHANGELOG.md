# Port-facing changelog: v1.24.0..v1.25.0

For anyone running Throughliner on a tool other than Claude Code. Every entry
below is a change inside the shipped plugin package; the development project's
own work is not listed.

Three limits this states about itself:

- it says WHAT changed, never how to map it — the translating stays yours;
- a change to a Python hook may have no equivalent on your side at all;
- a format-epoch bump means your own users' documents need migrating, which is
  yours to handle. It is flagged here and nothing more.

### 9150f89 — FAQ entry and index line authored at the v1.24.0 release

No session record could be matched to this commit, so there is no behavioural summary for it. Read the diff.

### dfd0ea1 — Lean docset built on the `lean` branch: every shipped doc rewritten from scratch, the rule gate retired for a slip list, the queue cleared to twelve items, rezipped to 1.24.0-test1

Shipped files: throughliner/plugin/throughliner/.claude-plugin/plugin.json, porting/ports.md

Date: 2026-10-07 03:48

Record: `LOG/2026-10-07-lean-docset.md`

### 04f80b7 — Law prose restored as the register of the lean docset: eleven docs restyled to the wording standard, no rule added or removed

No session record could be matched to this commit, so there is no behavioural summary for it. Read the diff.

### 046d1ec — Session opening to stop naming LOG/backlinks.md as the user's edit when its only change is placeholders becoming commit hashes

Shipped files: throughliner/plugin/throughliner/hooks/session_start.py

Date: 2026-10-07 11:37, read from the clock at the moment of writing. The build ran in session ce956dd4 from 05:06; this record is written at its close.

Record: `LOG/2026-10-07-hash-fill-read-as-user-edit-build.md`

### 046d1ec — Self-hosting seed rewritten to the slip regime: the CLAUDE.md block cut to the slip list and the wording standard, the compliance-audit template deleted, setup.md repointed

Shipped files: throughliner/plugin/throughliner/templates/self-hosting-claude-block.md, throughliner/plugin/throughliner/templates/compliance-audit-checklist-template.md, throughliner/plugin/throughliner/docs/setup.md

Date: 2026-10-07 11:37, read from the clock at the moment of writing. The build run of session ce956dd4 opened 05:06 and its walk-through continued past 09:44; this record is written at its close.

Record: `LOG/2026-10-07-self-hosting-seed-rewritten-to-slip-regime-build.md`

### 0f7518b — plan — the rule that Claude does what it can itself restored to the always-loaded rules

Shipped files: throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md, throughliner/plugin/throughliner/docs/build.md

Recorded 2026-10-08 12:07, read from the clock, in the planning session of 2026-10-08 opened 04:46.

Record: `LOG/2026-10-08-claude-does-what-it-can-rule-restored.md`

### 0f7518b — plan — a completed item ticks its own task line, and co-written text is never a task

Shipped files: throughliner/plugin/throughliner/docs/close.md, throughliner/plugin/throughliner/docs/build.md, throughliner/plugin/throughliner/docs/plan.md, throughliner/plugin/throughliner/templates/faq-template.md

Recorded 2026-10-08 21:48, read from the clock, in the planning session of 2026-10-08 opened 04:46.

Record: `LOG/2026-10-08-cross-project-task-tick-and-cowrite.md`

### 0f7518b — plan — the hash fill to leave an uncommitted record alone

Shipped files: throughliner/plugin/throughliner/hooks/session_start.py

Recorded 2026-10-08 12:17, read from the clock, in the planning session of 2026-10-08 opened 04:46.

Record: `LOG/2026-10-08-hash-fill-stamps-uncommitted-record.md`

### 0f7518b — plan — planning tags no work the user's that Claude can do

Shipped files: throughliner/plugin/throughliner/docs/plan.md, throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md

Recorded 2026-10-08 12:32, read from the clock, in the planning session of 2026-10-08 opened 04:46.

Record: `LOG/2026-10-08-no-user-item-for-claude-doable-work.md`

### 0f7518b — plan — captures sent from another project no longer read as the user's edit

Shipped files: throughliner/plugin/throughliner/hooks/session_start.py

Recorded 2026-10-08 21:59, read from the clock, in the planning session of 2026-10-08 opened 04:46; surfaced by the rescan at its end and processed at once on your "Ok process both now".

Record: `LOG/2026-10-08-sent-captures-read-as-user-edits.md`

### 0f7518b — plan — the slip list made writable in a planning session, through the hook

Shipped files: throughliner/plugin/throughliner/hooks/pre_tool_use.py, throughliner/plugin/throughliner/docs/plan.md

Recorded 2026-10-08 12:08, read from the clock, in the planning session of 2026-10-08 opened 04:46.

Record: `LOG/2026-10-08-slip-list-not-writable-at-planning.md`

### 0f7518b — plan — an unsure step is checked on the web before it goes out

Shipped files: throughliner/plugin/throughliner/docs/build.md

Recorded 2026-10-08 21:44, read from the clock, in the planning session of 2026-10-08 opened 04:46.

Record: `LOG/2026-10-08-web-search-when-unsure.md`

### 0f7518b — build run of 2026-10-08 to 10: seven builds, three user steps blocked, rezip to test5

Shipped files: throughliner/plugin/throughliner/.claude-plugin/plugin.json, throughliner/plugin/throughliner/templates/faq-template.md

Date: 2026-10-10 04:53, read from the clock at the moment of writing. The run opened 2026-10-08 22:50 by the opening's clock line, the builds and walk-through fell on 2026-10-08, the rezip's restart on 2026-10-09 and its post and this close on 2026-10-10.

Record: `LOG/2026-10-10-build.md`

### 2c82289 — INBOX retired: the register and address book into .throughliner/, every mail step out, the epoch to 7

Shipped files: throughliner/plugin/throughliner/hooks/session_start.py, hooks/pre_tool_use.py, mcp/server.py, scripts/send_capture.py, docs/setup.md, docs/migrate-checklist.md, retired-artifacts.md, docs/plan.md, docs/build.md, docs/close.md, docs/catchup.md, docs/feedback-and-inbox.md, templates/CLAUDE-TEMPLATE.md, templates/faq-template.md, templates/faq-index-template.md

Date: 2026-10-10 06:54, read from the clock at the moment of writing, in the build run opened 06:15.

**FORMAT EPOCH -> 7.** Your own users' documents need migrating; that is yours to handle.

Record: `LOG/2026-10-10-inbox-folder-retired-register-moves.md`

### f8d402a — build — the Rule gate line re-seated on the queue item and accepted by the tick tool

Shipped files: throughliner/plugin/throughliner/mcp/server.py, throughliner/plugin/throughliner/docs/plan.md

Date: 2026-10-13 16:03, read from the clock at the moment of writing. Built second in the build run of 2026-10-13, out of queue order: the first item's tick was refused by the installed tool for opening with `slips`, the very form this item teaches it, so this one was built next and both ticks then ran through the source tree's server.

Record: `LOG/2026-10-13-build-tick-rule-gate-field-refused-for-doc-changing-items.md`

### f8d402a — build — the close's clear-all offer leaves a named attachment alone

Shipped files: throughliner/plugin/throughliner/docs/close.md

Date: 2026-10-13 16:03, read from the clock at the moment of writing. Built in the build run of 2026-10-13.

Record: `LOG/2026-10-13-capture-attachments-need-safe-home-build.md`

### f8d402a — build — the close's look-back sends a candidate to the project it belongs to

Shipped files: throughliner/plugin/throughliner/docs/close.md

Date: 2026-10-13 16:03, read from the clock at the moment of writing. Built in the build run of 2026-10-13.

Record: `LOG/2026-10-13-close-cross-project-filing-build.md`

### f8d402a — build — unmapped paths listed at the opening and settled at the close

Shipped files: throughliner/plugin/throughliner/hooks/session_start.py, throughliner/plugin/throughliner/docs/close.md, throughliner/plugin/throughliner/templates/MAP-TEMPLATE.md

Date: 2026-10-13 16:03, read from the clock at the moment of writing. Built in the build run of 2026-10-13.

Record: `LOG/2026-10-13-close-leaves-other-sessions-scope-file-build.md`

### f8d402a — build — freeform sessions made a way of working equal to planning and build runs

Shipped files: throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md, throughliner/plugin/throughliner/docs/close.md

Date: 2026-10-13 16:03, read from the clock at the moment of writing. Built in the build run of 2026-10-13.

Record: `LOG/2026-10-13-freeform-as-a-default-way-of-working-build.md`

### f8d402a — build — the freeform door opens once per session

Shipped files: throughliner/plugin/throughliner/hooks/pre_tool_use.py, throughliner/plugin/throughliner/mcp/server.py, throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md

Date: 2026-10-13 16:03, read from the clock at the moment of writing. Built in the build run of 2026-10-13.

**Why it was made** (from the record of the session that decided it, `LOG/2026-10-13-freeform-scope-lock-one-block-per-file-and-planning-session-wording.md`): summary: plan — [freeform-scope-lock-one-block-per-file-and-planning-session-wording] kept as a build on the user's "Ok": the no-skill session's door opens once per session rather than once per path, the block message names a no-skill session and its scope file instead of "planning sessions", the rules sentence aligned with the hook; the build run's branch named as untouched on her challenge; SPEC's door sentence amended at the keep (build, cleared) --- # f081ef6 — plan — the freeform door opens once per session

Record: `LOG/2026-10-13-freeform-scope-lock-one-block-per-file-and-planning-session-wording-build.md`

### f8d402a — build — subagents on Haiku or Sonnet by a fixed table, the gate letting both through

Shipped files: throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md, throughliner/plugin/throughliner/hooks/pre_tool_use.py

Date: 2026-10-13 16:03, read from the clock at the moment of writing. Built in the build run of 2026-10-13.

Record: `LOG/2026-10-13-haiku-subagents-facts-only-with-brief-standard-build.md`

### f8d402a — build — handmade builds ticked into the scope file, removed only on a confirmed tick

Shipped files: throughliner/plugin/throughliner/mcp/server.py, throughliner/plugin/throughliner/docs/close.md, throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md

Date: 2026-10-13 16:03, read from the clock at the moment of writing. Built in the build run of 2026-10-13.

Record: `LOG/2026-10-13-handmade-builds-leave-queue-unconfirmed-build.md`

### f8d402a — build — the nested shape required at setup, the keep-private route retired

Shipped files: throughliner/plugin/throughliner/docs/setup.md, throughliner/plugin/throughliner/hooks/session_start.py, throughliner/plugin/throughliner/templates/CLAUDE-TEMPLATE.md, throughliner/plugin/throughliner/templates/faq-template.md, throughliner/plugin/throughliner/templates/faq-index-template.md

Date: 2026-10-13 16:03, read from the clock at the moment of writing. Built in the build run of 2026-10-13.

Record: `LOG/2026-10-13-nested-shape-required-flat-gitignore-retired-build.md`

### f8d402a — build — every queue entry carries a derived checkbox line the tools keep

Shipped files: throughliner/plugin/throughliner/scripts/reorder_queue.py, throughliner/plugin/throughliner/scripts/queue_digest.py, throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md, throughliner/plugin/throughliner/docs/setup.md, throughliner/plugin/throughliner/docs/migrate-checklist.md, throughliner/plugin/throughliner/templates/faq-template.md, throughliner/plugin/throughliner/templates/faq-index-template.md

Date: 2026-10-13 16:03, read from the clock at the moment of writing. Built in the build run of 2026-10-13, the first slice of the SPEC goal written 2026-10-12.

Record: `LOG/2026-10-13-queue-entry-task-line-written-by-tools-build.md`

### f8d402a — build — the state server refuses an argument no tool declares

Shipped files: throughliner/plugin/throughliner/mcp/server.py

Date: 2026-10-13 16:03, read from the clock at the moment of writing. Built in the build run of 2026-10-13.

Record: `LOG/2026-10-13-queue-move-tools-ignore-anchor-silently-build.md`

### f8d402a — build — the queue's states and transitions as one table with one owner each

Shipped files: throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md, throughliner/plugin/throughliner/docs/plan.md

Date: 2026-10-13 16:03, read from the clock at the moment of writing. Built in the build run of 2026-10-13, after the two items that added rows to it.

Record: `LOG/2026-10-13-queue-state-table-owns-every-transition-build.md`

### f8d402a — build — the Runs alone marker retired

Shipped files: throughliner/plugin/throughliner/docs/build.md, throughliner/plugin/throughliner/docs/close.md, throughliner/plugin/throughliner/docs/plan.md, throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md, throughliner/plugin/throughliner/scripts/queue_digest.py, throughliner/plugin/throughliner/scripts/reorder_queue.py

Date: 2026-10-13 16:03, read from the clock at the moment of writing. Built in the build run of 2026-10-13.

Record: `LOG/2026-10-13-runs-alone-retired-for-cleared-line-and-blocked-by-build.md`

### f8d402a — build — the session-start hash backfill asks git once, not once per record

Shipped files: throughliner/plugin/throughliner/hooks/session_start.py

Date: 2026-10-13 16:03, read from the clock at the moment of writing. Found, filed and built in the build run of 2026-10-13, after the rezip's first restart.

Record: `LOG/2026-10-13-session-start-hash-backfill-one-git-call-per-record.md`

### f8d402a — build — the stop check against the close nag after the user said to keep the chat open

Shipped files: throughliner/plugin/throughliner/hooks/stop.py

Date: 2026-10-13 16:03, read from the clock at the moment of writing. Built in the build run of 2026-10-13.

Record: `LOG/2026-10-13-stop-check-close-ask-after-keep-open-build.md`

### f8d402a — build — an unconfirmed tick names its check item

Shipped files: throughliner/plugin/throughliner/mcp/server.py, throughliner/plugin/throughliner/docs/build.md, throughliner/plugin/throughliner/docs/plan.md

Date: 2026-10-13 16:03, read from the clock at the moment of writing. Built in the build run of 2026-10-13.

Record: `LOG/2026-10-13-unverified-blocker-never-surfaced-build.md`

### f8d402a — build — the task line lives in the queue item, the shared task list retired

Shipped files: throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md, throughliner/plugin/throughliner/docs/plan.md, throughliner/plugin/throughliner/docs/build.md, throughliner/plugin/throughliner/docs/close.md, throughliner/plugin/throughliner/docs/setup.md, throughliner/plugin/throughliner/hooks/pre_tool_use.py, throughliner/plugin/throughliner/templates/CLAUDE-TEMPLATE.md, throughliner/plugin/throughliner/templates/faq-template.md, throughliner/plugin/throughliner/templates/faq-index-template.md

Date: 2026-10-13 16:03, read from the clock at the moment of writing. Built in the build run of 2026-10-13.

Record: `LOG/2026-10-13-user-task-line-lives-in-queue-with-tasks-marks-build.md`

### e2bd5d4 — build — the build run lifts what its own ticks clear

Shipped files: throughliner/plugin/throughliner/docs/build.md, throughliner/plugin/throughliner/docs/close.md, throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md

Date: 2026-10-19 11:20, read from the clock at the moment of writing. Built in the build run of 2026-10-19.

Record: `LOG/2026-10-19-build-run-lifts-built-blockers-mid-run-build.md`

### e2bd5d4 — build — the close deletes a dead session's close marker

Shipped files: throughliner/plugin/throughliner/docs/close.md, throughliner/plugin/throughliner/hooks/session_start.py

Date: 2026-10-19 11:20, read from the clock at the moment of writing. Built in the build run of 2026-10-19.

Record: `LOG/2026-10-19-close-deletes-dead-session-close-marker-build.md`

### ba84184 — rezip — 1.24.0-test8 installed and posted, test7 backfilled

Shipped files: throughliner/plugin/throughliner/.claude-plugin/plugin.json, throughliner/plugin/throughliner/templates/faq-template.md

Date: 2026-10-20 08:46, read from the clock at the moment of writing. Run in session 0a93903a after its build run and after its close, on the user's "Ok" to the close's offer on 2026-10-19; the full restart and the posts fell on 2026-10-20 by the opening's date line.

Record: `LOG/2026-10-20-rezip.md`

### 92dcfb7 — FAQ entry on Claude Code's auto-mode screen refusing an approved step, with its index line

No session record could be matched to this commit, so there is no behavioural summary for it. Read the diff.

### 8f5a8b9 — build — the opening no longer reads a date in an observable as the last turn

Shipped files: throughliner/plugin/throughliner/hooks/session_start.py, throughliner/plugin/throughliner/mcp/server.py

Date: 2026-11-03 10:50, read from the clock at the moment of writing. Built in the build run of 2026-11-03.

Record: `LOG/2026-11-03-cycle-observable-date-in-sentence-read-as-last-turn-build.md`

### 8f5a8b9 — build — freeform is a session type, and the halt hands over its prompt

Shipped files: throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md, throughliner/plugin/throughliner/docs/build.md, throughliner/plugin/throughliner/docs/close.md

Date: 2026-11-03 10:50, read from the clock at the moment of writing. Built in the build run of 2026-11-03.

Record: `LOG/2026-11-03-freeform-is-a-session-type-build.md`

### 8f5a8b9 — build — the keep-open check arms on a marker Claude writes

Shipped files: throughliner/plugin/throughliner/mcp/server.py, throughliner/plugin/throughliner/hooks/stop.py, throughliner/plugin/throughliner/docs/plan.md, throughliner/plugin/throughliner/docs/close.md, throughliner/plugin/throughliner/templates/faq-template.md

Date: 2026-11-03 10:50, read from the clock at the moment of writing. Built in the build run of 2026-11-03.

Record: `LOG/2026-11-03-keep-open-check-arms-on-marker-not-phrases-build.md`

### 8f5a8b9 — build — finished work is shown with a link, not described

Shipped files: throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md, throughliner/plugin/throughliner/docs/build.md, throughliner/plugin/throughliner/docs/close.md

Date: 2026-11-03 10:50, read from the clock at the moment of writing. Built in the build run of 2026-11-03.

Record: `LOG/2026-11-03-made-file-linked-in-the-reply-build.md`

### 8f5a8b9 — build — a rule that has slipped twice may carry one purpose clause

Shipped files: throughliner/plugin/throughliner/templates/self-hosting-claude-block.md

Date: 2026-11-03 10:50, read from the clock at the moment of writing. Built in the build run of 2026-11-03.

Record: `LOG/2026-11-03-purpose-clause-on-a-rule-that-slips-build.md`

### 8f5a8b9 — build — setup records how each person is referred to

Shipped files: throughliner/plugin/throughliner/docs/setup.md, throughliner/plugin/throughliner/templates/CLAUDE-TEMPLATE.md, throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md

Date: 2026-11-03 10:50, read from the clock at the moment of writing. Built in the build run of 2026-11-03.

Record: `LOG/2026-11-03-refer-by-github-username-build.md`

### 8f5a8b9 — build — rescan's ask names the choice it recommends

Shipped files: throughliner/plugin/throughliner/docs/rescan.md

Date: 2026-11-03 10:50, read from the clock at the moment of writing. Built in the build run of 2026-11-03.

Record: `LOG/2026-11-03-rescan-ask-offers-process-now-build.md`

### 8f5a8b9 — build — a task-shaped [user] item is offered, not stepped past

Shipped files: throughliner/plugin/throughliner/docs/build.md, throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md, throughliner/plugin/throughliner/templates/faq-template.md

Date: 2026-11-03 10:50, read from the clock at the moment of writing. Built in the build run of 2026-11-03.

Record: `LOG/2026-11-03-task-line-user-items-unwalked-build.md`

### 8f5a8b9 — build — the user's own task lines carry #user

Shipped files: throughliner/plugin/throughliner/scripts/reorder_queue.py, throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md, throughliner/plugin/throughliner/docs/setup.md, throughliner/plugin/throughliner/templates/CLAUDE-TEMPLATE.md, throughliner/plugin/throughliner/templates/faq-template.md

Date: 2026-11-03 10:50, read from the clock at the moment of writing. Built in the build run of 2026-11-03.

Record: `LOG/2026-11-03-tasks-query-filter-user-lines-build.md`

### 8f5a8b9 — build — the [user] provision says when a task line and when a walkthrough

Shipped files: throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md, throughliner/plugin/throughliner/docs/plan.md

Date: 2026-11-03 10:50, read from the clock at the moment of writing. Built in the build run of 2026-11-03.

Record: `LOG/2026-11-03-user-item-walkthrough-or-task-line-criterion-build.md`

### 1e6918f — Planning close of 2026-11-05: plugin.json at 1.24.0-test9, the FAQ templates refreshed by the tips turn of 2026-11-04

No session record could be matched to this commit, so there is no behavioural summary for it. Read the diff.

### 4f073cd — build — `/tasks` joins the plugin as its seventh skill

Shipped files: throughliner/plugin/throughliner/skills/tasks/SKILL.md, throughliner/plugin/throughliner/docs/tasks.md, throughliner/plugin/throughliner/docs/setup.md, throughliner/plugin/throughliner/templates/faq-template.md, throughliner/plugin/throughliner/templates/faq-index-template.md, throughliner/plugin/throughliner/.claude-plugin/plugin.json

Date: 2026-11-05 22:52, read from the clock at the moment of writing.

Record: `LOG/2026-11-05-tasks-skill-joins-the-plugin-build.md`

### fa50fae — build — look before asking another project

Shipped files: throughliner/plugin/throughliner/docs/feedback-and-inbox.md, throughliner/plugin/throughliner/templates/faq-template.md, throughliner/plugin/throughliner/templates/faq-index-template.md

Date: 2026-11-06 14:42, read from the clock at the moment of writing.

Record: `LOG/2026-11-06-check-tasks-before-cross-project-query-build.md`

### fa50fae — build — drafts default to .md

Shipped files: throughliner/plugin/throughliner/docs/plan.md, throughliner/plugin/throughliner/docs/setup.md, throughliner/plugin/throughliner/templates/faq-template.md, throughliner/plugin/throughliner/templates/faq-index-template.md

Date: 2026-11-06 14:42, read from the clock at the moment of writing.

Record: `LOG/2026-11-06-cowrite-default-md-build.md`

### fa50fae — build — the epoch-7 register move passes the safety check

Shipped files: throughliner/plugin/throughliner/hooks/pre_tool_use.py

Date: 2026-11-06 14:42, read from the clock at the moment of writing.

Record: `LOG/2026-11-06-epoch7-sent-register-move-blocked-build.md`

### fa50fae — build — goals as checkbox lines in Tasks marks

Shipped files: throughliner/plugin/throughliner/hooks/post_tool_use.py, throughliner/plugin/throughliner/mcp/server.py, throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md, throughliner/plugin/throughliner/docs/setup.md, throughliner/plugin/throughliner/docs/plan.md, throughliner/plugin/throughliner/docs/rescan.md, throughliner/plugin/throughliner/docs/catchup.md, throughliner/plugin/throughliner/templates/faq-template.md, throughliner/plugin/throughliner/templates/faq-index-template.md

Date: 2026-11-06 14:42, read from the clock at the moment of writing.

Record: `LOG/2026-11-06-goal-lines-in-tasks-marks-build.md`

### fa50fae — build — host_currency reads the build it runs from

Shipped files: throughliner/plugin/throughliner/mcp/server.py

Date: 2026-11-06 14:42, read from the clock at the moment of writing.

Record: `LOG/2026-11-06-host-currency-reads-stale-install-build.md`

### fa50fae — build — every close leaves a next-run line

Shipped files: throughliner/plugin/throughliner/mcp/server.py, throughliner/plugin/throughliner/scripts/queue_digest.py, throughliner/plugin/throughliner/scripts/reorder_queue.py, throughliner/plugin/throughliner/hooks/post_tool_use.py, throughliner/plugin/throughliner/docs/close.md, throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md, throughliner/plugin/throughliner/docs/build.md, throughliner/plugin/throughliner/docs/plan.md, throughliner/plugin/throughliner/templates/faq-template.md, throughliner/plugin/throughliner/templates/faq-index-template.md

Date: 2026-11-06 14:42, read from the clock at the moment of writing.

Record: `LOG/2026-11-06-next-run-line-at-close-build.md`

### fa50fae — build — a projectless task goes to the task-list project's queue

Shipped files: throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md, throughliner/plugin/throughliner/docs/setup.md, throughliner/plugin/throughliner/docs/tasks.md, throughliner/plugin/throughliner/templates/faq-template.md, throughliner/plugin/throughliner/templates/faq-index-template.md

Date: 2026-11-06 14:42, read from the clock at the moment of writing.

Record: `LOG/2026-11-06-projectless-task-sent-to-task-list-project-build.md`

### fa50fae — build — setup's first-capture sentence loses the retired append

Shipped files: throughliner/plugin/throughliner/docs/setup.md

Date: 2026-11-06 14:42, read from the clock at the moment of writing.

Record: `LOG/2026-11-06-setup-first-capture-names-retired-task-list-append-build.md`

### fa50fae — build — the owner warning is silent in a one-person project

Shipped files: throughliner/plugin/throughliner/hooks/post_tool_use.py

Date: 2026-11-06 14:42, read from the clock at the moment of writing.

Record: `LOG/2026-11-06-solo-project-owner-lint-noise-build.md`

### fa50fae — build — /tasks sorts by project priority

Shipped files: throughliner/plugin/throughliner/docs/tasks.md, throughliner/plugin/throughliner/templates/faq-template.md, throughliner/plugin/throughliner/templates/faq-index-template.md

Date: 2026-11-06 14:42, read from the clock at the moment of writing.

Record: `LOG/2026-11-06-tasks-sort-by-project-priority-build.md`

### fa50fae — build — task ownership in a shared project

Shipped files: throughliner/plugin/throughliner/scripts/reorder_queue.py, throughliner/plugin/throughliner/hooks/post_tool_use.py, throughliner/plugin/throughliner/mcp/server.py, throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md, throughliner/plugin/throughliner/docs/build.md, throughliner/plugin/throughliner/docs/plan.md, throughliner/plugin/throughliner/docs/tasks.md, throughliner/plugin/throughliner/templates/faq-template.md, throughliner/plugin/throughliner/templates/faq-index-template.md

Date: 2026-11-06 14:42, read from the clock at the moment of writing.

Record: `LOG/2026-11-06-two-person-chagora-and-task-ownership-build.md`

### 5cbd6c7 — [checklists-lose-word-triggers] built: the registered firing word retired

Shipped files: throughliner/plugin/throughliner/docs/plan.md, throughliner/plugin/throughliner/mcp/server.py, throughliner/plugin/throughliner/hooks/session_start.py, throughliner/plugin/throughliner/templates/faq-template.md, throughliner/plugin/throughliner/templates/faq-index-template.md

Date: 2026-11-06 22:36

Record: `LOG/2026-11-06-checklists-lose-word-triggers-build.md`

### 102370e — build — cross-project holds and the blocker lookup

Shipped files: mcp/server.py, scripts/queue_digest.py, scripts/reorder_queue.py, hooks/post_tool_use.py, hooks/session_start.py, docs/skill-nonspecific-rules.md, docs/build.md, docs/process.md, docs/opening.md, docs/tasks.md

Date: 2026-11-16 14:46, read from the clock at the moment of writing.

Record: `LOG/2026-11-16-cross-project-holds-in-task-marks-build.md`

### 102370e — build — the freeform way of working named, and a capture is for later

Shipped files: throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md, throughliner/plugin/throughliner/templates/faq-template.md, throughliner/plugin/throughliner/templates/faq-index-template.md

Date: 2026-11-16 14:46, read from the clock at the moment of writing.

Record: `LOG/2026-11-16-freeform-named-and-captures-for-later.md`

### 102370e — build — the opening's index backfill no longer writes the root commit's hash

Shipped files: throughliner/plugin/throughliner/hooks/session_start.py

Date: 2026-11-16 14:46, read from the clock at the moment of writing.

Record: `LOG/2026-11-16-index-hash-backfill-undone-by-regeneration.md`

### 102370e — build — the plan skill split into plan and process

Shipped files: throughliner/plugin/throughliner/docs/opening.md, docs/plan.md, docs/process.md, docs/skill-nonspecific-rules.md, docs/build.md, docs/build-work.md, docs/close.md, docs/rescan.md, docs/setup.md, docs/feedback-and-inbox.md, docs/migrate-checklist.md, docs/catchup.md, skills/plan/SKILL.md, skills/process/SKILL.md, hooks/pre_tool_use.py, hooks/session_start.py, mcp/server.py, templates/faq-template.md, templates/faq-index-template.md

Date: 2026-11-16 14:46, read from the clock at the moment of writing.

**Why it was made** (from the record of the session that decided it, `LOG/2026-11-08-plan-split-into-plan-and-process.md`): summary: plan — [plan-split-into-plan-and-process] kept as a build on the user's "As you recommend": `/plan` keeps the opening and becomes an open planning session, the entry-by-entry pass moves whole into a new `/process` skill, the opening lives once in a shared doc both read, and plan, process and a freeform chat may keep a capture while a build run and its close only file (build, cleared) --- # 45db6a5 — plan — the plan skill splits into plan and process

Record: `LOG/2026-11-16-plan-split-into-plan-and-process.md`

### 102370e — build — FAQ and README wording pass from the maintenance sweep

Shipped files: throughliner/plugin/throughliner/templates/faq-template.md

Date: 2026-11-16 14:46, read from the clock at the moment of writing.

Record: `LOG/2026-11-16-sweep-faq-first-session-names-retired-setup-questions.md`

### 102370e — build — build doc: a step of the user's is sought before it is named unable to start, from three slip lines

Shipped files: throughliner/plugin/throughliner/docs/build.md

Date: 2026-11-16 14:46, read from the clock at the moment of writing.

Record: `LOG/2026-11-16-sweep-slips-build-doc-2026-11-06.md`

### 102370e — build — rules doc: two purpose clauses and a widened filing sentence, from six slip lines

Shipped files: throughliner/plugin/throughliner/docs/skill-nonspecific-rules.md

Date: 2026-11-16 14:46, read from the clock at the moment of writing.

Record: `LOG/2026-11-16-sweep-slips-rules-doc-2026-11-06.md`

### 98974ce — build — the session opening's .gitignore check reads past a byte-order mark

Shipped files: throughliner/plugin/throughliner/hooks/session_start.py

Date: 2026-11-19 10:10, read from the clock at the moment of writing. Built 2026-11-17 in a run that closed 2026-11-19.

Record: `LOG/2026-11-19-gitignore-check-bom.md`

### e858498 — Bump to v1.25.0 and repackage

No session record could be matched to this commit, so there is no behavioural summary for it. Read the diff.
