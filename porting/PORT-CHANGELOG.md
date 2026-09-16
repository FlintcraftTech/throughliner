# Port-facing changelog: v1.22.0..HEAD

For anyone running Throughliner on a tool other than Claude Code. Every entry
below is a change inside the shipped plugin package; the development project's
own work is not listed.

Three limits this states about itself:

- it says WHAT changed, never how to map it — the translating stays yours;
- a change to a Python hook may have no equivalent on your side at all;
- a format-epoch bump means your own users' documents need migrating, which is
  yours to handle. It is flagged here and nothing more.

### 61789a7 — build — the buildability check gains one general limb keyed on the rests-on line, two clauses merged into it

Shipped files: plugin/throughliner/docs/plan.md

Built 2026-09-03 in the 2026-09-02 build run, from a consumer project's compliance report of 2026-09-01. A planning session there was about to keep a trademark-and-licence research question as a build item — it produces a file, which is a change to files — and the user stopped it. The rule crossed existed: research within planning's reach is done now. But the clause hung off the sentence about a limb that cannot be stated, so it was reached only when describing the build failed; an item describable without the answer passed on the check's own terms. Every kept item already writes what its design rests on with the date each fact was verified, and an unread fact cannot be dated, so an undated rest is the mechanical tell. Refused at planning: a third limb beside the two clauses (the gate's eviction step says an addition names what comes out, and both were instances of this one), and a lint on undated rests.

Record: `LOG/2026-09-03-buildability-check-misses-deferred-research.md`

### 61789a7 — build — setup's closing recap explains `/clear` before naming it and never stacks an instruction behind it

Shipped files: plugin/throughliner/docs/setup.md, plugin/throughliner/templates/faq-template.md

Built 2026-09-03 in the 2026-09-02 build run, from the beta-test audit of 2026-09-02. The tester's setup close ended "Run /done to save all this, then /clear", and his /done close ended "Run /clear when you're ready". He typed `/clear`, the screen blanked, the instruction after it went with it, and nothing had said what `/clear` does; most of the next session was recovery, and his own Claude then wrote him a commands reference. The one shipped site was setup.md's recap bullet, two commands bundled with the destructive one second and unexplained. The close's own final turn already forbids ending on a command, so the tester's close ending on one was a compliance miss answered by the content line kept this session. Refused at planning: a shipped commands reference, the FAQ entry being that.

**Why it was made** (from the record of the session that decided it, `LOG/2026-09-02-clear-recommended-without-explanation.md`): Processed 2026-09-02, the first of the tester's ten findings weighed. The one shipped site is setup.md's recap; the close doc never mentions /clear and already forbids ending on a command, so the tester's close was a compliance miss covered by the close's final-message content line kept this session. The recap gets two sentences and points at the FAQ entry on ending with /done; a shipped Commands.md was refused.

Record: `LOG/2026-09-03-clear-recommended-without-explanation.md`

### 61789a7 — [audit] delta compliance audit on the parent axis: eight findings, seven of them rationale inside operative text written in the last two days

Shipped files: plugin/throughliner/docs/done-build.md, done.md, next.md, plan.md, rescan.md, setup.md

Run 2026-09-03 as the last Claude-work item of the 2026-09-02 build run, from the audit-lag check's capture, processed the day before with the note that it should read the docs after the run's own edits. Scope recomputed on the day: one rule-bearing commit since `2026-09-01-compliance-audit-lag.md` (15b5f4d, the 2026-09-02 build run) plus this run's working-tree edits to the same eight docs, read as the delta of those docs against fb7c4ee — 144 added lines committed and roughly 250 more in the tree. Axis: parent, as the checklist requires. All nine lenses were run over the added text, one criterion at a time.

**Why it was made** (from the record of the session that decided it, `LOG/2026-08-31-compliance-audit-lag-plan.md`): Processed 2026-08-31, kept cleared as an [audit] on Claude's recommendation and the user's agreement. Two additions at the keep: the delta printed at filing is a floor, not the scope — the 2026-08-31 build run touched the rule docs again after it was filed, so the run recomputes rule-bearing commits since the most recent compliance-audit record from git on the day; and an ordering note written on both this and [maintenance-sweep] — whichever of the two checklist audits runs second gets cheaper, and the sweep's processing turn weighs whether one pass can satisfy both.

Record: `LOG/2026-09-03-compliance-audit-lag.md`

### 61789a7 — build — the build close removes a walk-through it recorded as done

Shipped files: plugin/throughliner/docs/done-build.md, plugin/throughliner/docs/done-plan.md

Built 2026-09-03 in the 2026-09-02 build run. Found by Claude at a planning opening: the previous build run's record for [ports-forum] ended "Outcome: done" with its observable met, yet the item was still cleared to run and had to be removed by hand. The cause, read from the close docs: the removal existed once, in done-plan.md's Completed `[user]` items step, which ran as a close of its own or inside a planning close — never inside a build close. done-build.md closed each walk-through on an outcome and stopped, and the shipped-slug cross-check reaches only items a build locked scope on, which a walk-through never is. Same shape as the two items above it in this run: the finding recorded, the action with no slot in that close.

Record: `LOG/2026-09-03-done-walkthrough-left-in-queue.md`

### 61789a7 — build — the close's final message names any due cycle, filed or not

Shipped files: plugin/throughliner/docs/done.md

Built 2026-09-03 03:10 in the 2026-09-02 build run (the session ran across 2026-09-02 and 2026-09-03). The complaint behind it was the user's: she waited through a session that crossed midnight to see whether the close would raise the release that had just fallen due, and it did not — the point of cycles being that things run like clockwork without her holding the triggers. The cause, read from done.md at planning: the wind-down's cycles check already named the due cycle in one line mid-close, but the Recommend-next turn's content line carried only the queue situation and the two continuations, and the advisory-filed arm shrank that message to one line naming the advisory. The wording was followed; the shape excluded it.

Record: `LOG/2026-09-03-due-cycle-produces-no-signal.md`

### 61789a7 — build — alternatives are delivered together and asked singly; a genuine open choice opens with "Your call, two ways:"

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md, plugin/throughliner/docs/plan.md

Built 2026-09-03 in the 2026-09-02 build run, from a consumer project's compliance report of 2026-09-02. Across one planning run there, several decisions were put as two-way questions in one sentence and three came back as the single word "yes", each costing a turn. The report's hypothesis held against the text at planning: the inversion rule says alternatives the user is choosing between are delivered together, and nothing said that delivering both leaves the ask single; the two rules sat in different documents. The user asked how a person is supposed to notice that one ask differs from the run of yeses around it, and asked for research; settled at planning by design instead — a departure is perceptible only against a constant, so the ordinary ask stays one formula and the genuine open choice gets one fixed lead-in of its own. Refused: a marker on two-way asks, and researching perception cues.

Record: `LOG/2026-09-03-either-or-asks-answered-yes.md`

### 61789a7 — build — dead hooks become a stated failure: every skill opens by checking for the session-start lines, and the install guide names Python

Shipped files: plugin/throughliner/skills/{setup,plan,next,rescan,done}/SKILL.md

Built 2026-09-03 in the 2026-09-02 build run, from the beta-test audit of 2026-09-02. After a clean install, all four hooks ran `python` against the Windows Store placeholder, which prints "Python was not found" and exits; the plugin reported success while the queue lint, the scope-lock, the session-start facts and the stop check did nothing, and the installing session caught it only by inspection. A dead hook writes nothing, but the harness reads skills as files whatever the hooks do, so the skill is the one place that always runs, and the one thing a live session start always leaves is its opening lines, whose absence the model can check with no tool. Refused at planning: a hook self-check (a hook that does not run cannot check anything), and changing the command line to try `py` first, filed separately as [hook-interpreter-fallback-on-windows] pending a second-machine test.

Record: `LOG/2026-09-03-hooks-silent-under-python-stub.md`

### 61789a7 — build — the capability-sentence rule reaches chat guidance: a claim about a surface is verified or said as a guess with the fallback beside it

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md

Built 2026-09-03 in the 2026-09-02 build run, from the beta-test audit of 2026-09-02. Told to hover a chat's file card for a save option, the tester found only two unrelated menu items; the working answer — a copy on his desktop — had already been given, so the invented route added nothing but a wild goose chase. The rule's trigger was a sentence written into a document, naming the walk-through as where it bites hardest; chat guidance was neither, so the sentence sat outside the rule while being exactly the case it describes. Refused at planning: a separate rule for chat guidance, the near-duplicate the gate refuses.

Record: `LOG/2026-09-03-invented-ui-affordance-in-guidance.md`

### 61789a7 — build — setup's keep-private offer opens on four lines, the rest held for the yes

Shipped files: plugin/throughliner/docs/setup.md

Built 2026-09-03 in the 2026-09-02 build run, from the beta-test audit of 2026-09-02. The offer reached the tester as three files, a three-point trade, a git explanation, a note about his folder's contents and an aside about the mailbox; his whole reply was that he could not see a question in it. The session restated it in four lines with a recommendation and got "yes". The doc produced the first form: tagged brief, then requiring the fork, two configurations, three documents, the one-question-three-answers instruction, the trade and the kept-changed-limit block "in one short exchange", with the method's one-bold-ask-last shape not applied. The recovery is the specimen. Refused at planning: cutting the trade, and asking three questions.

Record: `LOG/2026-09-03-keep-private-question-overwhelms-beginner.md`

### 61789a7 — build — the shipped ports doc says a flavour describes what a port does now and can be re-declared

Shipped files: plugin/throughliner/docs/ports.md

Built 2026-09-03 in the 2026-09-02 build run, from the /rescan of the day before. Post 4 in the how-ports-work forum states that changing flavour later is allowed and needs no permission, an inference from the design flagged as such at drafting and approved by the user, and names `ports.md` as the canonical wording — which did not say it. A porter who reads the post and opens the doc to quote it finds the doc says less. The doc already says no register of flavours is kept and the flavour is something a port declares about itself, so the sentence follows. Refused at planning: cutting the sentence from the post, since it is true and the doc was the thing that was short.

Record: `LOG/2026-09-03-ports-doc-silent-on-changing-flavour.md`

### 61789a7 — build — the scope-lock's no-build refusal gains the user's door: asked again in their own words, the session declares that one path and makes the edit

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md, plugin/throughliner/hooks/pre_tool_use.py, plugin/throughliner/docs/done-plan.md

Built 2026-09-03 in the 2026-09-02 build run, from the beta-test audit of 2026-09-02. After /done, an agreed one-line edit to the tester's own CLAUDE.md was refused as work rather than planning and queued; the beta record he asked for could not be written into his project and went to a temporary folder. The denial itself is the user's decision, argued over weeks and not reopened: a no-build session is denied rather than asked, because an ask waved through is not consent. What the design lacked was a door the user opens. The direct-request rule already says a request against a method rule is warned once and done on their next word, and the only mechanism that extends the standing list — the freeform scope file — was tied by the docs to a queued item though the hook reads only the file's Files list (checked at planning). Refused: widening the standing list, and reverting to ask-and-approve.

Record: `LOG/2026-09-03-post-close-lock-blocks-user-work.md`

### 61789a7 — build — the session opening's queue facts line gains the count of captures waiting to be planned

Shipped files: plugin/throughliner/hooks/session_start.py, plugin/throughliner/docs/plan.md

Built 2026-09-03 in the 2026-09-02 build run, from the beta-test audit of 2026-09-02. The tester opened a session the day after setup and asked where everything had gone: "0 items cleared to run" read as an empty slate when it meant his three captured items had not been through planning. The zero is emitted on purpose so a computed zero cannot be mistaken for a check that never ran, and that stands; the loss reading came from the only non-zero fact being left out. Refused at planning: a reassuring sentence on the line, since a sentence true only sometimes is what facts-only keeps out.

Record: `LOG/2026-09-03-queue-facts-zero-reads-as-empty.md`

### 61789a7 — build — the rescan hand-back gains a content line; the rules file's count of governed turns goes to six

Shipped files: plugin/throughliner/docs/rescan.md, plugin/throughliner/docs/skill-nonspecific-rules.md

Built 2026-09-03 in the 2026-09-02 build run. Raised by the user the day before and processed the same turn on her word: the turn after a rescan was not clear — it said "the close" and hinted at /done without naming it, and it would confuse new users. The instance, read from that morning's transcript at planning: after her "go" the hand-back said nothing was committed and where the work had got to, named no command and ended on no ask. The step's text said to name what the captures wait for, resume, and recommend nothing else; nothing said what the message must contain — the same gap the close's final turn had, the seventh in the family of turns fixed by a content line.

Record: `LOG/2026-09-03-rescan-handback-names-done.md`

### 61789a7 — build — the close's router gains an already-closed first arm: a second `/done` is the post-close tail

Shipped files: plugin/throughliner/docs/done.md, plugin/throughliner/docs/rescan.md

Built 2026-09-03 in the 2026-09-02 build run, from the beta-test audit of 2026-09-02. The tester's session closed, real work followed, and he ran `/done` again; the second close said the method expects one commit per session and that it would note the discrepancy, reasoning about the conflict unaided where a rule should have been. done.md was unambiguous — one commit per session, the tail makes none, no second close — so the rule was not reworded; what was missing was an arm for the command being typed anyway. Refused at planning: a hook refusing a second close (a refusal with no route is what this replaces), and a delta commit.

Record: `LOG/2026-09-03-second-done-makes-a-second-commit.md`

### 61789a7 — build — MCP slice three: `append_sent_line` composes a register line and appends it at the end of `INBOX/sent.md`

Shipped files: plugin/throughliner/mcp/server.py, plugin/throughliner/docs/feedback-and-inbox.md

Built 2026-09-03 in the 2026-09-02 build run, from the /rescan of the day before, processed as the MCP umbrella's third slice. The register is append-only by design and the one file with no history to restore from, and nothing appended to it by construction: every session wrote a new line with an edit anchored on whatever it last read, and one morning's line for the first ports-forum post landed a row above the end and took four turns to fix, a scripted rearrangement being correctly refused by the runtime-target guard. The cost recurred at every send, at the turn already carrying the user's attention, and an out-of-order line is invisible afterwards. The message-id field was added on the user's question about the forums.

Record: `LOG/2026-09-03-sent-register-has-no-append-path.md`

### 61789a7 — build — setup's nested conversion gains the wrap arm for a flat repository that already has a remote

Shipped files: plugin/throughliner/docs/setup.md

Built 2026-09-03 in the 2026-09-02 build run. Raised by Claude at planning while tracing this project's own conversion ([this-project-nested-conversion-decision]): the shipped offer said converting means creating an inner repository and moving the product's files into it — right for a flat project whose repository was never a product repository, wrong for one already published, where the remote, the marketplace manifest, the releases and the porters' pins all point at the existing repository and published history cannot be unpublished. The presence of a remote is the mechanical tell between the two, and a consumer who published a flat project meets the same case.

Record: `LOG/2026-09-03-setup-conversion-wraps-existing-remote.md`

### 61789a7 — build — the read directives say a doc may exceed one read and is finished only when the tool reports no further page

Shipped files: plugin/throughliner/hooks/session_start.py, plugin/throughliner/skills/{setup,plan,next,rescan,done}/SKILL.md, plugin/throughliner/docs/skill-nonspecific-rules.md

Built 2026-09-03 in the 2026-09-02 build run. Captured by the user from a "too large for one go" message at a planning opening in another of her projects, the first session there on Fable 5.1, and confirmed here the same day: plan.md and skill-nonspecific-rules.md each came back cut at roughly two-thirds on a single read. The directive says read in full and the method's own rule says a read that stopped short is named rather than reasoned from — but nothing told a session the file was longer than what came back. This very run met the cut on both files at its opening and paged. Size is the honest fix and now has a derived target, written into the maintenance sweep's criteria at planning: what one read returns, re-measured each turn. Refused at planning: splitting the two docs (a second file is a second read a session can skip), and widening the harness's read.

Record: `LOG/2026-09-03-skill-docs-exceed-one-read.md`

### 61789a7 — build — setup's brevity-style step gains a refused-write arm: say the app is asking permission, retry once, then fall back

Shipped files: plugin/throughliner/docs/setup.md

Built 2026-09-03 in the 2026-09-02 build run, from the beta-test audit of 2026-09-02. The step reported it was blocked from writing the project's settings file, told the tester he could turn it on later or ask again, and moved on; he said "try again" and it worked at once — a permanent-sounding failure for a one-time approval prompt. setup.md had an accept arm and a decline arm and none for a refused write, so the hand-back was improvised; on the desktop app a permission prompt for a first write to the settings file is the ordinary case. Refused at planning: treating the refusal as a decline, and treating it as a session-ending fault.

Record: `LOG/2026-09-03-style-write-refused-then-retried.md`

### 61789a7 — build — a walk-through's Files line joins the run's scope when its drive starts; a co-authored draft lives in the scratchpad by default

Shipped files: plugin/throughliner/docs/next.md, plugin/throughliner/docs/skill-nonspecific-rules.md, plugin/throughliner/docs/plan.md

Built 2026-09-03 in the 2026-09-02 build run, from the /rescan of the day before on two instances in one run. The ports-forum drive needed to write a post draft to a `.txt` the user could edit in the side panel, and the scope-lock refused it twice, each refusal a mid-drive turn asking her to approve a path while she waited on a step. The mechanism, read at planning: the lock reads one list, the working file's Files section, and a `[user]` item never enters that file, so its paths are structurally absent; a freeform session gets its list in by writing a scope file the lock also reads. The scratchpad and `LOG/` are exempt, which is why the record was writable while the artifact was not.

Record: `LOG/2026-09-03-walkthrough-drafts-outside-run-scope.md`

### 865ecce — eight compliance-audit sites subtracted: each why-clause tested against a consumer session's need, removed where the instruction stands complete; the close router's already-closed arm gains its tag and content line

Shipped files: plugin/throughliner/docs/next.md, plugin/throughliner/docs/done.md, plugin/throughliner/docs/setup.md, plugin/throughliner/docs/plan.md, plugin/throughliner/docs/next-build.md

Built 2026-09-04. From the queue text: the eight findings of the compliance-audit-lag audit run on 2026-09-02, processed 2026-09-03 as one set on Claude's recommendation and the user's agreement — a deterministic result set under the checklist's criteria. The test the build applied at every site, written onto the item on the user's rule of 2026-09-03: delete the clause and read what a session in a consumer project would do with what remains; a complete instruction means the clause was this project's history and comes out; an instruction that would be applied wrongly means the clause is part of the rule and stays, rewritten as what to do. Her distinction, not to be confused: the reasoning behind a rule's creation, held in this project's record, is not the reasoning a consumer's session needs to apply it.

Record: `LOG/2026-09-04-audit-2026-09-02-eight-sites-build.md`

### 865ecce — the buildability check's second limb asks whether a build may write each named file, and routes a queue-entry amendment to the decision step instead of a run

Shipped files: plugin/throughliner/docs/plan.md

Built 2026-09-04. From the queue text: from a defect report received by mail 2026-09-02 from another project running the plugin (archived at `INBOX/archive/2026-09-02-buildability-check-ignores-write-permission.md`); processed 2026-09-03 on Claude's recommendation and the user's agreement — her first reading was "I do not understand", and the plain-words restatement is what she agreed to. The failure: a planning session there kept an item whose only work was amending another queue item's prose; both limbs passed, and a run could not build it, since a run edits QUEUE.md only to remove each item as it is ticked. The item sat cleared and was skipped by every run with nothing reporting why.

Record: `LOG/2026-09-04-buildability-check-asks-write-permission-build.md`

### 865ecce — the checkpoint-counts tool reports the raw capture count and the presentable count side by side, the second from the digest's own pass-over code

Shipped files: plugin/throughliner/mcp/server.py, plugin/throughliner/scripts/queue_digest.py

Built 2026-09-04. From the queue text: noticed by Claude at the 2026-09-02 checkpoints and processed 2026-09-03 on Claude's recommendation and the user's agreement. The instance: the tool returned 63 where the checkpoint's own definition ([close-narration-counts-dated-out-captures], built 2026-09-02) gave about 32 — the tool was built the day before the definition and never learned it.

Record: `LOG/2026-09-04-checkpoint-counts-tool-reports-presentable-count-build.md`

### 865ecce — the co-authored draft rule gains a remote arm: where the user says they cannot open or edit the file, the draft is shown in full and their changes come back as chat text

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md

Built 2026-09-04. From the queue text: a method observation from the 2026-09-03 walk-through pass, filed by the /rescan and processed 2026-09-04 on Claude's recommendation and the user's agreement. The instance: driving the session from a phone, the user received the law-prose article, the two video scripts and the orientation post as one-way downloads; her edits had nowhere to land, and the session improvised.

Record: `LOG/2026-09-04-coauthored-draft-no-remote-route-build.md`

### 865ecce — cycle chains are computed: the opening reports each chained cycle's anchor date and per-ritual due dates, and the three due-ness checks file the ritual whose date has come

Shipped files: plugin/throughliner/hooks/session_start.py, plugin/throughliner/mcp/server.py, plugin/throughliner/docs/plan.md, plugin/throughliner/docs/next.md, plugin/throughliner/docs/done.md

Built 2026-09-04 18:47 in the run that closed the 2026-09-03/04 planning session's cleared region. The item's reasoning, read from the queue at the run's start (the queue is untracked, so this is the record of it): a cycle may chain several rituals anchored on a date, each earlier ritual with a lead before the anchor — `CYCLES.md` was rewritten to that shape on 2026-09-03 on the user's split of cycles from rituals — but the chain was followed only by a planning session reading the file, and nothing reported which ritual was due. The user's challenge behind it ([maintenance-cycle-shows-no-evidence-of-running]): no cycle visibly runs without her reminder. Her words on the outcome wanted: the release refuses to run while maintenance findings sit unbuilt, and the sweep is triggered in time to release on Wednesday morning rather than scrambling all day.

Record: `LOG/2026-09-04-cycle-chains-compute-due-rituals-build.md`

### 865ecce — the delete ask names what survives it: related items that stay, content already living elsewhere, or "nothing else is affected"

Shipped files: plugin/throughliner/docs/plan.md

Built 2026-09-04. From the queue text: captured on the user's observation 2026-09-02 and processed 2026-09-03 on Claude's recommendation and her agreement. Her instance: the delete ask for [setup-asks-if-first-time] read "drop this, with the finding recorded in this session's record", and she read it as the ten beta-tester captures going with it, when all ten stayed and each got its own turn. A delete is the one terminal outcome; what is lost is only readable against what stays.

Record: `LOG/2026-09-04-delete-ask-names-what-survives-build.md`

### 865ecce — a walkthrough step for a GUI app names something visible to click or a menu path; a shortcut is the instruction only where no visible route exists

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md

Built 2026-09-04. From the queue text: from the Hexboard project's mail of 2026-09-02, raised there by the user; the rule's wording is Claude's, with the user's correction at processing 2026-09-03 that "never as the instruction" was too strong where a shortcut is the only route — restated so no exception is needed. The instance: a step said to press Shift twice in Android Studio; nothing opened, and a misfired keypress leaves nothing on screen to describe. Reissued as clicks down a tree it worked first time, each expansion confirming itself.

Record: `LOG/2026-09-04-gui-steps-name-something-visible-build.md`

### 865ecce — the queue script's append stamps the clock on a capture arriving without a time, and the time-statements rule says a written clock time is read at the moment of writing

Shipped files: plugin/throughliner/scripts/reorder_queue.py, plugin/throughliner/scripts/test_reorder_queue.py, plugin/throughliner/docs/skill-nonspecific-rules.md

Built 2026-09-04. From the queue text: found by Claude at the 2026-09-02 close and processed 2026-09-03 on Claude's recommendation and the user's agreement. The failure: the 2026-09-02 planning session wrote 34 clock times, none read from a clock — each was the opening's 14:32 plus a guess, while the close's own clock read said 17:38. The capture writer stamps mechanically, but that session filed everything through `reorder_queue.py --append`, the route the always-loaded rules name, which stamped nothing.

**Why it was made** (from the record of the session that decided it, `LOG/2026-09-04-invented-clock-times-in-planning-writes.md`): Processed 2026-09-04 from Claude's finding at the 2026-09-02 close. The script route (`reorder_queue.py --append`) gains the stamp the MCP capture writer already has, so the two routes agree; the always-loaded time-statements rule gains the clause that a clock time in a record is read from the clock by a command at the moment of writing, and the opening's time line is a source for the date and a same-day relative claim, never a base to count up from. Refused: a hook checking written times against the clock (a stamp a minute late is indistinguishable from a right one); stamping kept items' "Processed" lines (prose the rule clause reaches).

Record: `LOG/2026-09-04-invented-clock-times-in-planning-writes-build.md`

### 865ecce — the look-back's memory check reads the runs the files prove against the runs still in view, and says one sentence reporting what it found; the "I can't tell" hedge retired

Shipped files: plugin/throughliner/docs/done.md, plugin/throughliner/docs/rescan.md

Built 2026-09-04. From the queue text: raised by the user 2026-09-04 from a Taskflow /rescan that said "I can't tell whether any of our earlier conversation has dropped out of view" and, in the same message, "the files and my memory disagree" — the second sentence proving the first false. Her tell, in her words: "there is a strong tell of whether something has dropped out of view, and that's if the evidence of next or plan having been run is there or not." Her position on the hedge: "it can always tell." Kept on her direction and Claude's agreement; the session in the screenshot followed done.md as written, so the defect was the document's.

Record: `LOG/2026-09-04-lookback-reads-runs-in-view-build.md`

### 865ecce — MCP slice four: `hold_entry` writes a `Blocked by:` or `Not before:` hold through the queue tool, refusing a dangling slug or a spent date at the door

Shipped files: plugin/throughliner/mcp/server.py, plugin/throughliner/docs/plan.md

Built 2026-09-04. From the queue text read at the run's start: the fourth slice of [mcp-server-standing-intent], processed 2026-09-03 on Claude's recommendation and the user's agreement — her word was to design something now rather than wait for the chain build. The structured-writes purpose, and the recorded harm: an unbracketed `Blocked by:` slug once made a consumer's item permanently unliftable with nothing reporting it ([unbracketed-blocker-invisible]).

Record: `LOG/2026-09-04-mcp-hold-entry-tool-build.md`

### 865ecce — the format migration marks every build block it writes as unchecked, and the digest surfaces a cleared item carrying the mark

Shipped files: plugin/throughliner/docs/setup.md, plugin/throughliner/docs/migrate-checklist.md, plugin/throughliner/scripts/queue_digest.py, plugin/throughliner/docs/plan.md

Built 2026-09-04. From the queue text: from a defect report received by mail 2026-09-03 from the Taskflow project (archived at `INBOX/archive/2026-09-03-from-taskflow-migration-wrote-build-blocks.md`); processed 2026-09-03 on Claude's recommendation and the user's agreement. The failure: their format 3→4 migration wrote build blocks under seventeen already-cleared items in one pass; six could not be started by a build, and a run discovered that item by item. A migration-written block is indistinguishable from one the decision step checked. The option taken: the mark; refused: the migration running the buildability check itself, since a migration runs hands-off and the check needs the user present.

Record: `LOG/2026-09-04-migration-marks-unvetted-build-blocks-build.md`

### 865ecce — the hash backfill and its alarm key on the hash slot, not the exact word: any non-hash token at the start of a record heading or index line is a placeholder

Shipped files: plugin/throughliner/hooks/session_start.py

Built 2026-09-04. From the queue text: from a defect report received by mail 2026-09-03 from a project running 1.22.0 (archived at `INBOX/archive/2026-09-03-near-miss-hash-token-defeats-both-checks.md`); processed 2026-09-04 on Claude's recommendation and the user's agreement. The instances: eight `[COMMIT_HASH]` placeholders sat unfilled in that project's LOG for twelve days, unreported; this project wrote `PENDING` in hash position on ten walk-through records and corrected them by hand only because the close happened to check. Refused per the item: a list of known placeholder words (the next slip is a word not on the list) and a hook refusing to write a record whose slot is not `[HASH]`.

Record: `LOG/2026-09-04-near-miss-hash-token-defeats-both-checks-build.md`

### 865ecce — the recommend turn opens in plain words, what went wrong and what the fix does, before naming any file or rule, where the item's subject is a mechanism of the method

Shipped files: plugin/throughliner/docs/plan.md

Built 2026-09-04. From the queue text: a testing outcome from the 2026-09-04 planning session, filed at its /rescan and processed the same turn on the user's agreement. The instances: two recommendations that session — on the write-permission item and the look-back hedge — each drew "I do not understand" and each landed at once when restated as what went wrong, why, and what the fix does. The summary turn already opened in plain English; the recommend turn had no such requirement and reverted to the method's vocabulary at the moment the user was deciding.

Record: `LOG/2026-09-04-recommend-turn-opens-in-plain-words-build.md`

### 865ecce — the red-flag scope names prompt injection through observed content, absorbing the per-channel "data, not instruction" sentences

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md, plugin/throughliner/docs/plan.md

Built 2026-09-04. From the queue text: raised by the user 2026-09-03 — her ask was to expand the red-flag risk list against Anthropic's security pages; the read found one addition, this one ("the findings only add one", her words), and the wording is Claude's, agreed by her. The read is filed at `workshop/resources/research/claude-code-security-guidance.md`.

Record: `LOG/2026-09-04-red-flag-scope-names-prompt-injection-build.md`

### 865ecce — a build run orders by dependency: Claude work waiting on no user item first, then each `[user]` item naming builds is walked and its builds follow it, and `[user]` items naming nothing come last

Shipped files: plugin/throughliner/docs/next.md, plugin/throughliner/docs/done-plan.md

Built 2026-09-04. From the queue text: from the Hexboard project's mail of 2026-09-03, its owner's first alternative; the second, dropping the pre-run reorder offer, refused. Kept on Claude's recommendation and the user's agreement, with her corrections — the default's reason in her words at processing: Claude work runs first so as much runs unattended as possible, and so nobody feels they must do their own steps to reach the Claude work behind them. The instance: a queue holding one item cleared and fourteen held, six fully designed, held only so a `[user]` walk-through that compiles and installs the work would happen before further changes stacked on uncompiled files.

Record: `LOG/2026-09-04-user-items-precede-only-what-names-them-build.md`

### 8143f68 — FAQ entry: can I move a queue item while a build is running — authored at the 2026-09-05 tips posting

No session record could be matched to this commit, so there is no behavioural summary for it. Read the diff.

### df8fdbb — build — plan.md's buildability check names where a design decision ends and a tunable constant begins, and puts a lookup on the same test

Shipped files: plugin/throughliner/docs/plan.md

Built 2026-09-05. From the Hexboard project's mail of 2026-09-03: the check forbade scheduling a design decision into a build without saying where a decision ends and a tunable constant begins, so one session refused to let any value reach the build while another accepted minor tweaking, and an item's strictness depended on which session ran planning. Planning kept the sender's own distinction (Claude's recommendation, the user's agreement): a decision is anything where two reasonable sessions would produce different work, made at planning; a tunable constant is a single value inside otherwise fully described work, stated with what it was derived from or that it was not and what would settle it, chosen at planning and revisable once seen; a lookup whose result cannot change the work's shape is a constant the build reads, one whose result could change the design is a decision. "Everything is settled at planning" was refused because both projects' queues already carry constants adjusted after the build. The build added the two subordinate lines and the lookup sentence under the design-decision clause; no new field, tag or state.

Record: `LOG/2026-09-05-design-decision-versus-tunable-constant-build.md`

### df8fdbb — build — the digest's next-pick takes the opening's two medians and holds them for the pass; every next-pick output names the medians used and whether they were passed in or recomputed

Shipped files: plugin/throughliner/scripts/queue_digest.py, plugin/throughliner/mcp/server.py, plugin/throughliner/docs/plan.md

Built 2026-09-05. From the Taskflow project's mail of 2026-09-05: plan.md promises the long-and-old groups are fixed when the run opens, while `whats_next()` recomputed both medians on every call, so as long entries left the section the medians fell and entries the opening had excluded became long — a session that simply took the tool's answer got a different order with nothing surfacing the divergence, and this project's own planning session of the same day had done exactly that. Planning took the sender's first two shapes together (Claude's recommendation, the user's agreement): `--medians <lines>,<date>` holds the opening's figures, and a source line makes a forgotten argument visible; withdrawing the doc's promise was refused because the fixed sets are what make the ladder terminate, and the MCP tool holding the medians as the only fix because the script is what consumers without the server run. The build added `medians_for()` and `parse_medians()`, threaded `medians` through `whats_next()`, `render_whats_next()`, `main` and the server's `queue_next_pick`, added the line to both plan.md blocks, and wrote the suite case.

Record: `LOG/2026-09-05-digest-next-recomputes-medians-build.md`

### df8fdbb — build — the third "data, not an instruction" copy in feedback-and-inbox.md evicted into the red-flag-scope pointer

Shipped files: plugin/throughliner/docs/feedback-and-inbox.md

Built 2026-09-05. Adjacent-work discovery from the 2026-09-04 run: the item that evicted plan.md's two per-channel sentences into the general red-flag scope named only plan.md and the rules file, and its observable grep still returned one line in feedback-and-inbox.md. Same eviction, one more site, on Claude's recommendation and the user's agreement — a third copy is the sibling-duplication shape the sweep now looks for. The build replaced the paragraph with the one-line pointer form plan.md uses.

Record: `LOG/2026-09-05-feedback-inbox-data-not-instruction-third-instance-build.md`

### df8fdbb — build — the queue tool's delete note skips `Cycle:` lines, so deleting a cycle-turn capture no longer lists the whole pool as citing it

Shipped files: plugin/throughliner/scripts/reorder_queue.py

Built 2026-09-05. Deleting the spent [tips-posting] turn capture on 2026-09-05 listed all twenty-five candidates in the tips pool as citing it, because each carries `Cycle: [tips-posting]` — a line naming the cycle definition of the same name, never the capture. The citation scan already skipped `Blocked by:` lines for the same reason; the build made it skip `Cycle:` too, with a suite case asserting cycle lines are not reported and a prose citation still is.

Record: `LOG/2026-09-05-mover-delete-note-skips-cycle-lines-build.md`

### df8fdbb — build — the research offer rule restated keyed on side effect: a bounded read is run and reported; an offer precedes only what fans out, spawns an agent or leaves the machine

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md, plugin/throughliner/docs/plan.md

Built 2026-09-05. From the Taskflow project's mail of 2026-09-05: Claude ended an interview turn with "Shall I look that up now?" for a lookup that was two web searches and a documentation fetch, and the user asked why she had been asked at all. Three passages pointed three ways — run what you can, offer readily, trying a tool is allowed where quick — and the one that said offer was the bold heading in the always-loaded file, which is why it won; this project's own session had offered the forum-sort search the same way, the second instance. Planning restated the rule keyed on side effect rather than cost (Claude's recommendation, the user's agreement): an estimate drifts, side effect is checkable. The build replaced the "Offer readily" heading with the restated bold-led paragraph, turned "offer the search" and the CLI-tool rule's "offer a search" into run-and-report, and reworded plan.md's interview line; the read-me-first index check and the frame assessment were left as the item said. One leftover the rescan then caught: that index check still opens "Before offering a search", filed as [research-index-check-still-says-offering].

Record: `LOG/2026-09-05-offer-readily-manufactures-over-asking-build.md`

### df8fdbb — build — a planning close whose look-back filed captures names them in its forward advisory, and the wind-down's numbered-set message opens by naming itself as the close's standing look-back

Shipped files: plugin/throughliner/docs/done.md

Built 2026-09-05. From a feature request mailed 2026-09-04: at a planning close the wind-down's captures strand, because the session that could process them is the one shutting down, while everything cleared in that session goes off to be built without them — their live instance a defect in an item the same session had just cleared. Planning took the sender's second shape and refused the first (Claude's recommendation, the user's agreement): the advisory names the captures by slug as what to open on, so the next planning session meets them first; processing at the close would be planning inside the close, and the rescan-before-close route already exists for the user who wants that. The mail's second datum — the owner taking the specified look-back for an improvised idea — got the second edit: the numbered-set message names itself as the close's standing step. Both edits in done.md; done-plan.md carries no advisory step of its own, so nothing to point.

**Why it was made** (from the record of the session that decided it, `LOG/2026-09-05-planning-close-rescan-output-strands.md`): Planning record for `[planning-close-rescan-output-strands]`, kept cleared to run. Written 2026-09-05.

Record: `LOG/2026-09-05-planning-close-rescan-output-strands-build.md`

### df8fdbb — build — the ask clause restated keyed on the offer: a message offering something or needing a decision makes that its one bold ask at the end, one with nothing to decide ends on its outcome, the close's recommend-next step named as the exception

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md

Built 2026-09-05. From the Taskflow project's mail of 2026-09-05: after a close, Claude wrote "One command fixes it if you want it done" mid-paragraph and ended on another subject, and the user saw the offer only by scrolling back; her proposal there was an ask with a recommendation at the end of every turn. Planning keyed the rule on the offer rather than the turn (Claude's recommendation, the user's agreement): the old clause presumed a message had one ask, which is how a mid-paragraph offer escaped it; an every-turn ask would manufacture asks where nothing is to be decided, the nagging shape the method has repealed twice. The build rewrote the sub-bullet under "Shape every message" with the close's recommend-next step as a subject-to exception by cross-reference. done.md's no-command constraint does not restate the ask rule, so it stands unchanged.

Record: `LOG/2026-09-05-post-close-turns-have-no-ask-build.md`

### df8fdbb — build — plan.md's freeform placement gains the case: a walk-through whose step runs setup is filed freeform, since setup refuses inside a build run

Shipped files: plugin/throughliner/docs/plan.md

Built 2026-09-05. Filed by the 2026-09-04 rescan after the nested-conversion walk-through halted at its second step: the user runs setup, and setup refuses outright while a build is in progress, while a walk-through is only ever reached inside a build run. The freeform tag already names work done in a session of its own because it cannot run inside a run, and the run already halts on it; what was missing was the assignment at the decision step. One subordinate line under the freeform placement bullet (Claude's recommendation, the user's agreement); a hook was refused because the step is prose, and a halt rule in next.md because the run already halts on the tag. The conversion item itself was not re-tagged, its setup step being done.

Record: `LOG/2026-09-05-setup-step-unreachable-inside-a-run-build.md`

### df8fdbb — build — setup says once, at scaffolding, when the adopted folder sits inside a cloud-sync tree: output collides with the sync client, Windows path depth shrinks, mirroring beats streaming

Shipped files: plugin/throughliner/docs/setup.md

Built 2026-09-05. From the Hexboard project's mail of 2026-09-03: a build there failed with permission errors from its own output folder inside a synced tree, another project hit Windows's path ceiling under a sync root, and switching the client from streaming to mirroring helped; nothing in the errors says "sync", so a no-code developer has no route from them to the cause. Planning kept the sender's shape (Claude's recommendation, the user's agreement): checkable from the path alone, silent where it does not apply, worded as what to be aware of and never what to fix, and not carried to existing projects by the top-up, since an owner weeks in has met the problem or not. The build added one step beside the keep-private offer, reading the absolute path for six folder names case-insensitively, saying the three things in one short paragraph where one matches.

Record: `LOG/2026-09-05-setup-warns-on-cloud-sync-folder-build.md`

### df8fdbb — build — setup's wrap arm rewritten to the shape that worked: the opened folder stays the outer, the checkout's contents move down into the product subfolder by explicit name, local paths re-pointed from the ripple list

Shipped files: plugin/throughliner/docs/setup.md

Built 2026-09-05. On the first run of the wrap, 2026-09-04, the arm as written failed: it created the outer one level up and tried to move the checkout into it, but the checkout is the folder the app session is open on and Windows refuses to rename a folder a running process holds. What worked was the reverse — keep the opened folder as the outer, create the product subfolder inside it, move every file and folder of the checkout down by explicit name (the bulk forms were blocked twice by the app's safety classifier), bring the method's documents back to the top. Better as well as workable: the folder the app opens, its memory and any folder-level CLAUDE.md above it stay valid, and only the marketplace path changes. Planning refused keeping the create-one-level-up shape with a close-the-app step, since a walk-through the app is running cannot have the user close the app mid-step. The build rewrote step 1c's wrap line, added the sentence on re-pointing local paths from the ripple list, and reworded the 1c prose and the Visibility sentence to name the opened folder as the outer.

Record: `LOG/2026-09-05-setup-wrap-arm-moves-contents-not-folder-build.md`

### df8fdbb — build — one always-loaded rule replaces the rests-on copies: a sentence resting on an outside fact or a condition names it, dated, wherever it lives; plan.md's copy shrinks to the field plus a pointer

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md, plugin/throughliner/docs/plan.md

Built 2026-09-05, the first application of the sibling limb built alongside it. The Hexboard mail of 2026-09-05 reported a SPEC sentence deferring a subject until a condition that had lapsed two days earlier, re-asserted for two sessions because nothing pointed from the change back to the sentences depending on it, and offered the rests-on line for SPEC sentences — a third copy after plan.md's and next.md's. Planning refused the copy and lifted the rule to the common parent instead (Claude's recommendation, the user's agreement), the SPEC sentence written there. The build added the general rule as a bold-led paragraph after the claim-about-the-world rule in the always-loaded file; shrank plan.md's rests-on paragraph to the field's shape plus a pointer, its rationale sentences coming out; and gave the SPEC staleness bullet its one clause. next.md turned out to carry no rests-on mention that reads the field — its two "rests on" phrases are ordinary prose about the method — so nothing there changed; the item's Files line had assumed otherwise.

Record: `LOG/2026-09-05-spec-sentences-lack-rests-on-build.md`

### df8fdbb — build — the stop check blanks blockquoted lines and fenced blocks before matching, so a quoted draft's example slug is not read as a filing report

Shipped files: plugin/throughliner/hooks/stop.py

Built 2026-09-05. Found at the planning session's tips turn: a bracketed example name inside a quoted post draft — "moved [login-form] below the cleared line", shown in a blockquote — matched the filing-claim patterns and blocked the turn for an item that does not exist. A capture report is never inside a blockquote or a code fence; a quoted draft, a specimen or a pasted post always is. Widening the placeholder guard to any bracketed name in a message that also contains a blockquote was refused as too coarse. The build added `_strip_quoted()`, applied in `_claimed_slugs()` before the patterns run, with lines blanked rather than removed so nothing shifts; the placeholder and hedge guards are untouched. Two suite cases: the same claim blocks as prose, not in a blockquote, not in a fence.

Record: `LOG/2026-09-05-stop-check-ignores-quoted-text-build.md`

### df8fdbb — build — the frame assessment's TIME RANGE line rewritten condition-first: where the product addresses a period, does the finding cover it; no period answers "not applicable"; the SPEC-gap clause fires only for a product with an unstated period

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md

Built 2026-09-05. From an observation mailed 2026-09-04: for a desktop application the criterion produced nothing but the declaration that the product's specification lacks a range, three findings running — a rule generating work rather than catching a problem — and this project's own security-guidance finding of 2026-09-03 had answered it "not applicable" too. Planning held the restatement without an exception (Claude's recommendation, the user's agreement): main clause first, condition after, the spec-gap signal surviving for the products it was written for. TIME RANGE and FRESHNESS stay two lines, one being the period the product is about and the other how recently the source moved; dropping one into the other was refused. The build rewrote the one line in the block's register; the four other criteria and every filed finding are untouched.

Record: `LOG/2026-09-05-time-range-criterion-may-not-distinguish-build.md`

### df8fdbb — build — the time-statements rule restated: a relative time word is derived from the clock read in the turn that says it, or the newest stamp in view, or left out; the opening line is one reading, current at the opening only

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md

Built 2026-09-05. The user's words at planning: "I am fine with those words but they need to be derived from actual times or not said at all because they can end up muddying up the log." The two failing derivations she named were tone (Claude saying "tonight" from how tired she sounds) and session position ("this morning" early in a chat, "tonight" late in one). The rule as written named the session opening's date-and-time line as the source for a same-day relative claim, "finer than a day" — one reading of the clock that aged for the whole chat, and a list of sources that never said what a time word is not derived from. The build rewrote the sources sentence: dates from the digest's figures, a record's date field or the clock; a relative time word from the clock read in the turn that says it, or the newest timestamp in view, with the opening's line one such reading and never a base to count up from. The source block gained the positive action: read the clock in this turn, then say it; no reading, state the event without a time.

Record: `LOG/2026-09-05-time-words-read-the-clock-in-the-turn-build.md`

### df8fdbb — build — a walkthrough step that needs a fixture states the property it must have, and the drive checks a named file against that property before giving the step

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md, plugin/throughliner/docs/next.md

Built 2026-09-05. From a mailed defect report of 2026-09-03: a planning run named one of the project's own documents as the fixture for a step needing thirty headings, a build run in the same chat processed most of that document away, and the step could not be performed when driven later by a no-code developer with nobody to ask — a gap between runs, not a lapse by either. Planning took both of the sender's fixes as halves of one line (Claude's recommendation, the user's agreement): naming the property alone hands the choosing to the user; checking alone needs the property stated. The build added one subordinate line to the walkthrough requirements in the always-loaded file and one bold-led paragraph in next.md's walk-through branch, before the hand-over checkpoint: a file named for a stated property is checked against it first, and where it fails the step goes out with the property and no file.

Record: `LOG/2026-09-05-walkthrough-fixture-invalidated-by-own-run-build.md`

### 6801258 — session_start.py's hash backfill reads a record's hash from its index line first, and leaves a placeholder unfilled where git's only match is the root commit, reporting it as an import (build)

Shipped files: plugin/throughliner/hooks/session_start.py

Built 2026-09-06 11:31, read from the clock, in the 2026-09-06 build run. At the 2026-09-05 opening the backfill filled seventeen August records with the outer's first commit, which had imported the whole LOG folder on 2026-09-04 — the oldest commit in which each title appears, which was the only test. `backfill_log_hashes` gains two guards: `_hash_from_index()` reads the index files for a line whose pointer names the record and whose slot holds a real hash, and fills from that first; otherwise, where `_oldest_commit_for` returns a commit with no parent, the placeholder stays and the record is named in a new report line saying it predates the repository's history. Index-file placeholders keep the git route. Refused at planning: a date test and a commit-subject match, neither of which separates a close from an import. Stated cost, unchanged: a flat project whose first close is its first commit leaves that one record unfilled and reported — which is why the suite's first case, a single-commit fixture, gained a baseline commit rather than being read as a regression. Two cases added: an index line whose hash git would disagree with wins, and a root-commit record stays unfilled while the index file's own placeholder still fills.

Record: `LOG/2026-09-06-backfill-attributes-pre-wrap-records-to-outer-commit-build.md`

### 6801258 — the page-the-whole-file rule gains "paged to its end silently, with no narration of the turning" (build)

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md

Built 2026-09-06 11:31, read from the clock, in the 2026-09-06 build run. Raised by the user on 2026-09-05: a session narrated that a document was too long for one read and that it was reading the rest, which she found concerning to see. The unlabelled-step rule already makes a page-turn silent, so this is sharper wording at the site of a self-correcting slip rather than a new rule. The "Reading a whole file before reasoning over it" section's first bold sentence in `skill-nonspecific-rules.md` gains the clause after "a read of one is finished only when the tool reports no further page"; the sentence that a read which stopped short is named plainly is unchanged. The five skill wrappers, which state completeness and not narration, were not touched, per the planning grep.

Record: `LOG/2026-09-06-paging-a-long-file-is-not-narrated-build.md`

### 6801258 — port_changelog.py gains `--log-root` so git reads and record reads take different roots; the release ritual's command carries it; CLAUDE.md's routine push names the inner (build)

Shipped files: plugin/throughliner/scripts/port_changelog.py

Built 2026-09-06 11:31, read from the clock, in the 2026-09-06 build run, due before the Wednesday release turn. Since the wrap the changelog script's one root found the commits in the inner and none of the deciding records, which sit in the outer's LOG. `port_changelog.py`: `log_entries_for`, `deciding_record` and `build` take a `log_root` (default the project root, so a flat project is unchanged), and `main` gains the `--log-root PATH` argument. `test_port_changelog.py`: a case with the roots apart — a separate folder holding LOG with a build record and a planning record — asserting both are found and the repository's own records are not read, plus a default-unchanged check. `CYCLES.md`: the release ritual's step 11 command carries `--log-root .` and the sentence saying the command was known to be wrong is replaced by one saying where each read goes. `CLAUDE.md`: the Push section's one step says the push runs in the inner with `git -C throughliner push`, since the outer has no remote.

Record: `LOG/2026-09-06-release-ritual-commands-target-outer-repo-build.md`

### 6801258 — the research-index paragraph reworded to open "Before running a search", matching the restated offer rule (build)

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md

Built 2026-09-06 11:31, read from the clock, in the 2026-09-06 build run. Found by the 2026-09-05 build run's rescan: [offer-readily-manufactures-over-asking] restated the research rule so a bounded read is run and reported, and the read-the-index-first paragraph a few lines away still opened "Before offering a search", so two paragraphs disagreed on the verb. One word changed in `skill-nonspecific-rules.md`; the check's substance stands. The planning grep found the phrase at that one site only.

Record: `LOG/2026-09-06-research-index-check-still-says-offering-build.md`

### 6801258 — the scope-lock's research exemption accepts the nested layout, and the first-step drive found no branch that admitted the two 2026-09-05 passes (build)

Shipped files: plugin/throughliner/hooks/pre_tool_use.py

Built 2026-09-06 11:31, read from the clock, in the 2026-09-06 build run. The planning session of 2026-09-05 was refused an Edit to a research file in the inner's workshop, though research notes are on the planning standing list, because `_is_research_dir` matched `<root>/workshop/resources/research/` only; minutes earlier a Write creating a new research file there and an Edit to its index had passed, which the code did not explain. The item's first step was to drive the hook against all three paths and record which branch admitted the two that passed.

Record: `LOG/2026-09-06-scope-lock-research-exemption-flat-path-only-build.md`

### 6801258 — the co-authored-draft sub-rule hands the `.txt` draft over as a link under the folder's full path, the short-name form named as the one that does not open (build)

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md

Built 2026-09-06 11:31, read from the clock, in the 2026-09-06 build run. Two accounts of one failure, merged at planning: the user's observation that sessions name a `.txt` draft or its path without linking it, so the co-writing step stalls, and Claude's from the 2026-09-05 walk-through, where a link under Windows' short folder name (`~1` in the path, the way the harness names the session scratchpad) did not open in the side panel while the full path opened at once. The walkthrough requirements' co-authored-draft bullet in `skill-nonspecific-rules.md` now says the draft is handed over as a link under the folder's full path, naming the short-name form as the one that does not open; nothing else in the bullet changed. Refused at planning and not revisited: resolving the scratchpad path in the hook, and a clause on the read-back's LINKS question.

Record: `LOG/2026-09-06-scratchpad-short-path-links-do-not-open-build.md`

### 6d912d5 — Build run of 2026-09-06 (second): the state server gains the queue tool's three moves as door-checked tools plus nested host currency and a digit-only message id, the safety check logs every decision, the queue lint says a cleared flag's gone notice once, the queue tool names the one-move-per-item clearing route, and the docs state the cycles check, mail triage, [user] completion and explicit-yes rule once each — v1.22.0-test2

No session record could be matched to this commit, so there is no behavioural summary for it. Read the diff.

### d6e654a — Build run of 2026-09-06 (third): the user's door narrowed to a logged refusal, time words caught by both hooks, the spec-sync gate reading its diffs, and MCP slice six

No session record could be matched to this commit, so there is no behavioural summary for it. Read the diff.

### 412f7e5 — Build run of 2026-09-08: the rule checks gain a parent lookup, a wider duplicate check, a per-file size line and inner-commit attribution; setup asks what the project's parts are; the queue tool writes atomically and guards the line both ways; a hook token stops crying wolf

No session record could be matched to this commit, so there is no behavioural summary for it. Read the diff.

### d39cd7d — FAQ template: the ritual entry refreshed at the tips-posting turn of 2026-09-08 — Claude's unprompted offer where it notices repetition, and the write-paths note

No session record could be matched to this commit, so there is no behavioural summary for it. Read the diff.

### e0d15e6 — Build run of 2026-09-09: per-part specs across the hook and four docs, four plan.md amendments, the compliance wording pass, accepted pairs and stop words in the rule checks

No session record could be matched to this commit, so there is no behavioural summary for it. Read the diff.

### 6fd00a4 — Build run of 2026-09-09 (the day's second): the rules-file eviction pass, the future-clock-time refusal, the line-level placeholder check, the link shape, temp/, the for-completion hand-over, the brevity offer's contract, a sixth rule check and an accepted pair

No session record could be matched to this commit, so there is no behavioural summary for it. Read the diff.

### 0cabcbd — Build run of 2026-09-10: nineteen items — the rule checks widened to the gate's trigger set, eleven decision-step and rules-file amendments, two lint-hook changes, the sweep's three new tests, three /done turn rewordings, "the close" retired from the docs, the audit docs folded into their build siblings

No session record could be matched to this commit, so there is no behavioural summary for it. Read the diff.
