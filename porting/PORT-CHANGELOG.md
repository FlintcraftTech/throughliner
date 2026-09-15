# Port-facing changelog: v1.21.1..fb7c4ee

For anyone running Throughliner on a tool other than Claude Code. Every entry
below is a change inside the shipped plugin package; the development project's
own work is not listed.

Three limits this states about itself:

- it says WHAT changed, never how to map it — the translating stays yours;
- a change to a Python hook may have no equivalent on your side at all;
- a format-epoch bump means your own users' documents need migrating, which is
  yours to handle. It is flagged here and nothing more.

### beac9d2 — Build run: the Discord posting bot ships, 13 items built, 2 audits filed and four walk-throughs closed

No session record could be matched to this commit, so there is no behavioural summary for it. Read the diff.

### 4efdcff — Audit-only runs hear the rescan recommendation: the fourth close-naming site gains the clause

Shipped files: plugin/throughliner/docs/next-audit.md

next-audit.md's close step now recommends running the rescan before /done, worded to match the three sites [rescan-before-done] already reached. next-build.md's abort path stays excluded as the item directs — it names /done after a failure, a different moment.

Record: `LOG/2026-08-28-audit-close-missing-rescan-clause-build.md`

### 4efdcff — Audit-halt specimen leads with the recommendation, the doc-write as the named escape

Shipped files: plugin/throughliner/docs/next-audit.md

The specimen offered a flat two-option menu where the doc's own contract has a preference. It now recommends filing findings as captures and keeps the direct doc-write as the escape on the user's say-so; its lead-in changed from "Ask which the user wants" to "Lead with the recommendation". Closes the seventh and last finding of the 2026-08-27 compliance audit.

Record: `LOG/2026-08-28-ca-audit-halt-offers-menu-build.md`

### 4efdcff — next-audit.md's restated empty-Files-list rule replaced by a pointer at its parent

Shipped files: plugin/throughliner/docs/next-audit.md

Four lines of restatement became one clause naming next.md's self-scoping step, per the names-not-step-numbers cross-reference rule; next.md untouched. The eviction-debt signature the audit lens exists for, repaid.

Record: `LOG/2026-08-28-ca-audit-restates-files-rule-build.md`

### 4efdcff — Every commit step in the done family now carries [BRIEF, PROMPT]

Shipped files: plugin/throughliner/docs/done-build.md, done-plan.md, done-audit.md

done-build.md §2.4 and done-plan.md §2 gained the tag matching done.md's Commit core — and the build found a third untagged commit step the audit finding had not noticed, in done-audit.md §2.4. It was included because the item's own observable ("no untagged commit step remains in the done family") cannot be met without it; the file was added to the run's Files list before editing.

Record: `LOG/2026-08-28-ca-commit-steps-untagged-build.md`

### 4efdcff — feedback-and-inbox.md gains response-shape tags throughout, every send step [BRIEF, PROMPT]

Shipped files: plugin/throughliner/docs/feedback-and-inbox.md

The doc drove approval-gated sends in prose alone. Each section now carries its tags: the report routes [BRIEF, PROMPT] with one sentence stating every route ends in a full stop; the INBOX section's read, archive and send shapes stated per arm with conditions outside the brackets; the outbound rule itself tagged.

Record: `LOG/2026-08-28-ca-feedback-doc-untagged-build.md`

### 4efdcff — Reorder specimen reworded to the vocabulary rule's own shape

Shipped files: plugin/throughliner/docs/done-plan.md

done-plan.md's specimen — the line a session copies when narrating a reorder — showed bare slugs, modelling exactly the output the vocabulary rule forbids. It now leads each item with its heading's opening words, slug after, and says what the move achieves in the user's terms.

Record: `LOG/2026-08-28-ca-reorder-specimen-bare-slugs-build.md`

### 4efdcff — The do-not-reinstate block relocated out of the shipped close doc, as a citation of the repeal's own record

Shipped files: plugin/throughliner/docs/done-plan.md

done-plan.md's "everything else the close used to reorder is repealed" sentence and its fenced block left the shipped doc; the operative one-pass rule stands. The grep the item required found the repeal's own LOG entry already carries the full history — `2026-08-11-processed-reorder-mostly-unnecessary.md` (7c9922a) names both retired reorders with their reasoning, plus two more retired in the same run — so `resources/self-authoring-rules.md` gained a "Repeals recorded elsewhere" section carrying the do-not-reinstate instruction as a citation rather than a copy, with the reason it lives host-side: its audience is a future method author, which a consumer never is. Settled-stays-settled kept by relocation.

Record: `LOG/2026-08-28-ca-repeal-block-in-shipped-doc-build.md`

### 4efdcff — Both history passages evicted from feedback-and-inbox.md, their content already on record

Shipped files: plugin/throughliner/docs/feedback-and-inbox.md

The "earlier version of this doc rejected the return path" passage deleted whole, and the milder "every reply used to be a fresh lookup" clause with it — its purpose-clause defence lost to the reclassification test at processing. Both histories were verified on record before deletion: the return-path supersession opens `LOG/2026-08-15-unattributed-mail-has-no-recovery-route.md`, and the once-per-correspondent reasoning is in `LOG/2026-08-13-inbox-has-no-recipient-address-book.md`. Nothing had to be added; the operative rules are untouched.

Record: `LOG/2026-08-28-ca-superseded-version-narrated-build.md`

### 4efdcff — Capability claims get the reverse-direction check: verify the sentence before writing it

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md

The what-would-answer-this rule gained its other direction: a doc sentence asserting what a tool can do is a claim about the world — run the read that would verify it before writing it, and where no such read exists, write it as intended rather than as fact. Admitted on the one recorded, repaired failure: the bot-may-post-in-three-channels sentence came from a design discussion, was untrue when written, and reading the channels had proved nothing because read and post are separate grants in Discord. Generalises past the host case, since consumers write the same claims into their own TOOLS.md — and it was exercised twice later in this very session, holding the `.txt`-sidebar claim and the forum-deletion claim as unverified rather than acting on either.

Record: `LOG/2026-08-28-claude-md-asserted-bot-posting-channels-unchecked-build.md`

### 4efdcff — content_stamp() normalises CRLF to LF and excludes .orphaned_at, so a commit and its installed build can stamp equal

Shipped files: plugin/throughliner/hooks/session_start.py

With `core.autocrlf=true` and no `.gitattributes`, a commit's LF blobs could never stamp equal to the CRLF installed build, defeating the one mechanical answer to "is this build the build I think it is" — including the new release ritual's archive check, which compares against `git archive` output. The fix is in-function: bytes normalised before hashing, `.orphaned_at` joining the exclusions. A `.gitattributes` was refused as recorded — it renormalises the whole tree where this touches nothing else. Every stamp moves once on this build; the docstring says so, so the first fresh-stamp session reads it as expected rather than as a fault.

Record: `LOG/2026-08-28-content-stamp-normalises-line-endings-build.md`

### 4efdcff — The candidate-set ask states what "go" does: "Say go to file them all, or contest by number"

Shipped files: plugin/throughliner/docs/done.md, plugin/throughliner/docs/rescan.md

Both grep-found sites reworded — done.md's wind-down re-scan and rescan.md's candidate-set ask — with the asymmetry named in the rule: numbering explains contesting on its own, while "go" explains nothing unless the sentence says it files the whole set. The other "says go" hits in the corpus are unrelated (the run off-ramp, an INBOX check, the show-first hold) and were left alone.

Record: `LOG/2026-08-28-contest-by-number-ask-unexplained-build.md`

### 4efdcff — Cycles parser reads wrapped Cadence and Observable fields whole, removing the constraint instead of documenting it

Shipped files: plugin/throughliner/hooks/session_start.py

`cycles_facts()` matched both fields with single-line regexes, so a naturally wrapped field was silently cut at the line break — and a truncated cadence still reads like a cadence, so nothing downstream could tell. The parser gained a continuation state ending a field at a blank line or the next field line (`CYCLE_FIELD_START_RE`). The kept disposition's reasoning held: a format note in every cycles doc would guard a limitation that can simply be deleted. The suite gained the live instance that found this — the first draft's wrapped definition now parses whole — plus a case proving prose after a blank line stays out of the field.

Record: `LOG/2026-08-28-cycles-fields-are-single-line-build.md`

### 4efdcff — Disposition ask rebuilt to the user's two-part form: agreement to the recommendation, the move as its consequence

Shipped files: plugin/throughliner/docs/plan.md

The recommend step's ask rule and specimens now carry her form — "Would you agree with that? If so I'll move it into Processed, cleared to run." — with the reason operative: an ask about the mechanics turns a natural "agreed" into consent to a write rather than a readable verdict on the substance. Her clarification travelled too: the recommendation is never the move itself, and where agreement doesn't land, processing simply continues. The delete ask is unchanged, since it already asks the fate question directly.

Record: `LOG/2026-08-28-disposition-ask-two-part-form-build.md`

### 4efdcff — The FAQ templates join the planning writable list, and the three owed entries land

Shipped files: plugin/throughliner/hooks/pre_tool_use.py, plugin/throughliner/templates/faq-template.md, faq-index-template.md

The scope-lock's `_is_plan_quiet_path()` admits exactly the two FAQ template paths and nothing else in templates/ — the literals written lowercase with forward slashes to match how the relative path is built, since normcasing them would swap in backslashes on Windows and never match, the same inversion the file already records for QUEUE.md. The templates-are-denied comment carries the exception and its ground: the FAQ template is canonical, FAQ/ is a copy of it, and the announcement-time rule could not be obeyed without the write — the twice-in-two-days collision. Three entries written and re-copied to FAQ/ byte-identical: updating and which build to be on; reporting a problem and how the answer returns; what a red flag means, ending on the honest limit in the user's own framing. The suite's template case was updated, and a CLAUDE-TEMPLATE.md case added — the one that proves the widening went no further than the pair.

Record: `LOG/2026-08-28-faq-writes-at-announcement-unblocked-build.md`

### 4efdcff — The stored-texts limb written into the hand-over checkpoint's own question

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md

The reclassify-don't-exempt rule applied on its recorded misapplication: the cross-reference to the walkthrough rules is what did not fire when a hand-over said "the quoted install line" against a post holding two quotes. Question 1 of the read-back block now carries the limb in its own text — where the message touches more than one stored text, does each step name which one it means and where it lives? The full statement in the `[user]` walkthrough rules stays canonical; the checkpoint carries the question form.

Record: `LOG/2026-08-28-handover-named-neither-of-two-quotes-build.md`

### 4efdcff — The two retired-term references reworded out of hook comments, and the checks run clean

Shipped files: plugin/throughliner/hooks/pre_tool_use.py, plugin/throughliner/hooks/session_start.py

Both sites were comments, as processing settled: `pre_tool_use.py`'s docstring "keep-step" (three occurrences, not the one the check named — the check reports one line per term) became "the decision step", and `session_start.py`'s epoch entry 4 kept its dated record while gaining the 2026-08-27 retirement and the deliberate no-bump reasoning, phrased so the literal marker string no longer appears. Comment-only, no behaviour change. While here, the checks' one finding — rule-bearing commits uncovered by a compliance audit — was filed as `[compliance-audit-lag]`, the slug open in neither section.

**Why it was made** (from the record of the session that decided it, `LOG/2026-09-01-live-rules-name-retired-terms-plan.md`): The judgment the capture asked for, performed at processing: the live rule corpus (shipped docs, templates, CLAUDE.md, SPEC) was scanned directly against the retired-terms list, and every hit there names its term as retired — the recognition rules doing their job, which the check's paragraph filter already tolerates. The 42 reported hits sit in archival files, and the mechanism was read rather than guessed: `rule_signals.py`'s ARCHIVAL_PATHS still carries pre-move paths (`resources/research/`, `resources/testing/`, `resources/plugin-behaviour-retired.md`, and the script itself), so since the workshop move the startswith test matches nothing and the whole exclusion is dead. The [rule-signals-retired-terms-path-stale] build fixed the term-list path and the scan root and missed this sibling constant. Kept as a build: the four entries re-pointed, plus a sweep for any other pre-move `"resources/` literal, since one sweep already missed this one. The capture's exclusion-for-the-archive question dissolves — the exclusion exists and points one folder short.

Record: `LOG/2026-08-28-live-rules-name-retired-terms-build.md`

### 4efdcff — The ordering ask signals a standard exists: "shall I order them the usual way?"

Shipped files: plugin/throughliner/docs/plan.md, plugin/throughliner/docs/feedback-and-inbox.md, plugin/throughliner/templates/faq-template.md

Beat 2's question and specimen reworded, the mail-carrying variant matching, with one operative clause: "the usual way" signals a standard is being applied without naming which rung, since the order used is often the fallback ladder rather than any nameable default — the bare "shall I pick" read as improvising. The variant quoted in feedback-and-inbox.md was found by grep and updated too, and the FAQ's description of the ask was still quoting the old wording — updated with a sentence explaining the phrase for a reader who has never seen the ladder. SPEC's sentence was updated at processing.

Record: `LOG/2026-08-28-ordering-ask-hides-the-default-build.md`

### 4efdcff — Process-now offers say "with you", so the offer primes for collective processing

Shipped files: plugin/throughliner/docs/plan.md, plugin/throughliner/docs/rescan.md

The user's wording built as captured, with her reason travelling: an offer reading as something Claude goes away and does primes the user for the wrong interaction. Both offer sites reworded — plan.md's specimen and Claude-raised branch, rescan.md's end-of-scan offer — each with one clause saying why. Descriptive uses of the phrase left alone as the item directs: they describe the user's answer, not Claude's offer.

Record: `LOG/2026-08-28-process-now-offer-says-with-you-build.md`

### 4efdcff — Decision step reads the cycles doc before recommending, so cycle-owned artifacts stop being shaped as one-offs

Shipped files: plugin/throughliner/docs/plan.md

The user's learning from a live miss minutes before filing: Claude recommended a one-off announcement draft when the artifact belonged to the release cycle as a template. The clause landed as a continuation of plan.md's existing cycle rules — read the cycles doc for a definition whose artifact the item touches; where one covers it, shape the work as part of that cycle's turn. The wide form (every recommendation in every skill) stayed refused as processed: it would need an always-loaded home for moments with no recorded failure.

Record: `LOG/2026-08-28-recommendation-checks-cycles-first-build.md`

### 4efdcff — Rituals built: named step lists with a trigger word, offered on procedure-shaped work, promoted to cycles when they gain a cadence

Shipped files: plugin/throughliner/docs/plan.md, plugin/throughliner/hooks/session_start.py

The user's structural read shipped as designed: a ritual is the turn-steps component of a cycle standing alone — no cadence, fired on the user's word — living in the same cycles doc. plan.md's decision step gained the authoring arm, a two-armed offer block (recurring-shaped → cycle, procedure-shaped → ritual, each offered once in the message already discussing the work), and the promotion clause. The parser split into `_parse_cycles_doc()` feeding `cycles_facts()` and a new `rituals_facts()`; the discriminator is what a definition carries (trigger and no cadence), so the format grows additively, every existing doc stays valid, and no epoch bump is owed. Session start reports rituals by name and trigger only — no due-ness exists to compute, and no capture is ever filed for one.

Record: `LOG/2026-08-28-ritual-definitions-and-offers-build.md`

### 4efdcff — The self-hosting seed built: /setup offers the self-authoring discipline to method builders, add-only

Shipped files: plugin/throughliner/docs/setup.md; plugin/throughliner/templates/self-hosting-claude-block.md, retired-terms-template.md, compliance-audit-checklist-template.md

setup.md gained the section with both entry points — a question at fresh setup for someone building a method, plugin or port, and an on-request path on an adopted project — under the top-up's never-overwrite discipline, with an explicit statement of what is deliberately not seeded and why (the release rituals and rule scripts are one repository's machinery; the discipline generalises, the tooling does not). Three templates authored by generalisation from the named host sources: the self-hosting CLAUDE.md block carrying the rule gate, the disposition-on-the-item pattern with its record line, and host-versus-target — with the honest limits kept in rather than smoothed away (nothing tells an honest disposition from a dishonest one) — plus the retired-terms register and compliance-audit checklist templates.

Record: `LOG/2026-08-28-setup-self-hosting-seed-build.md`

### 4efdcff — Stop hook ignores placeholder slugs, with the boundary derived from the specimen vocabulary

Shipped files: plugin/throughliner/hooks/stop.py

A `PLACEHOLDER_SLUG` pattern drops a claimed slug containing "slug" as a word before the check runs. The derivation is in the comment: it is the shipped docs' own specimen vocabulary — [slug-a], [some-slug], [work-slug], [old-slug] — while no real slug in this queue's history contains the word, because a real slug names its work. The residual stays stated: an item deliberately named `something-slug` slips the check, which is now also a reason never to name one that way. The suite gained both directions — a specimen does not block, a genuinely absent real slug still does.

Record: `LOG/2026-08-28-stop-hook-placeholder-slugs-build.md`

### 7b751b6 — Planning session 2026-08-29: ~30 entries processed, cleared region 2→28, ports made the top priority, one announcement posted and edited twice, two false records corrected

No session record could be matched to this commit, so there is no behavioural summary for it. Read the diff.

### 819f7f1 — The planning checkpoint carries both numbers again

Shipped files: plugin/throughliner/docs/plan.md

The user asked for a ready count to be displayed and the other number disappeared; her words at this run's processing were that she meant both. The record proves it rather than resting on memory: the 2026-08-27 entry quotes the wording that produced the current rule, and that wording is two numbers.

Record: `LOG/2026-08-29-checkpoint-count-dropped-ready-number-build.md`

### 819f7f1 — A draft the user edits is handed over as a file, not as chat text

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md

Co-authoring kept being shaped as Claude work the user writes into, and the painstaking part is explaining a change to Claude when it is much easier to go in and edit the text yourself. That is the user's framing and it is the whole reason for the rule.

Record: `LOG/2026-08-29-co-authoring-txt-draft-loop-build.md`

### 819f7f1 — The look-back stops claiming compaction is undetectable, and warns when the files disagree with the conversation

Shipped files: plugin/throughliner/docs/rescan.md, plugin/throughliner/docs/done.md

`rescan.md` said that where a conversation has been summarised the memory of it is gone, "and that is undetectable from the inside". The user's observation falsified it: a run leaves structurally recognisable traces, and a session that can still see them has not had them summarised away. The stronger version, which is what makes it mechanical rather than introspective, cross-checks the conversation against durable artifacts on disk — the build working file lists exactly which items were ticked, and thirty listed against six visible is two counts disagreeing rather than a judgement about memory.

Record: `LOG/2026-08-29-compaction-has-a-designable-tell-build.md`

### 819f7f1 — A finding another project owns is copied in, and the work resting on it is flagged as a snapshot

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md, plugin/throughliner/scripts/queue_digest.py

A consumer project reported that the method files and indexes research per project and has no shape for a finding one project owns and another's work depends on. Both available answers were poor: an absolute path that breaks silently, or a copy with no link to the original.

Record: `LOG/2026-08-29-cross-project-research-citation-build.md`

### 819f7f1 — The queue digest answers "what is next" without printing everything

Shipped files: plugin/throughliner/scripts/queue_digest.py, plugin/throughliner/docs/plan.md

Re-deriving the ladder's rung and its top item by hand cost about 350 tokens a pick, most of it Claude emitting the script rather than running it; re-running the whole digest instead — the route the procedure sanctioned — produces around 3,600. The sanctioned route was the expensive one, and the cost recurs at every pick because the queue changes underneath the answer.

Record: `LOG/2026-08-29-digest-answers-whats-next.md`

### 819f7f1 — The issue check reaches repositories this project does not own

Shipped files: plugin/throughliner/docs/plan.md

The planning opening's issue check had two limbs — comments on issues the register records, and new issues on a repository the project owns — and nothing else was in view. Issues on other repositories, including the tool the method runs inside, bear directly on the work and no limb reached them.

Record: `LOG/2026-08-29-issue-check-foreign-repos-build.md`

### 819f7f1 — A port can survey what changed in the shipped package since the version it ported from

Shipped files: plugin/throughliner/scripts/port_changelog.py

**The record for this change discusses host-only reasoning.** Read it before porting: part of what it describes may belong to the development project rather than to the plugin.

The question behind this was whether a port's own sessions can read this repository's changelogs and apply what changed. They can, conditional on what the changelog carries: a human release note names no file, no rule and no wording, while this project's session records already carry exactly the right shape. Only a port-facing view of them per release was missing.

Record: `LOG/2026-08-29-port-facing-changelog-build.md`

### 819f7f1 — The two port flavours get names: tracking and independent

Shipped files: plugin/throughliner/docs/ports.md

Two flavours of port were already recognised and neither had a name, so nobody could say what a given port promised — including this project. A user choosing between ports could not tell whether the one they installed would follow the method or had gone its own way; a porter had no way to signal it; and this project could not tell which ports its changelog was even for.

Record: `LOG/2026-08-29-port-flavours-named-build.md`

### 819f7f1 — Pointing stays the default, and a reader who cannot open the file can say so

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md, plugin/throughliner/docs/next.md

The render rule was unconditional and deliberately so, on the reasoning that a reader away from the file is served by the plain-English summary opening each item's discussion. That reasoning assumes the reader *could* open the file if they wanted to. On remote control there is no filesystem to open, so the pointer resolves to nothing — fine for one queue item, not fine for a fourteen-part deliverable being approved item by item.

Record: `LOG/2026-08-29-rendering-for-a-reader-away-from-the-files-build.md`

### 819f7f1 — Retired artifacts are named in a shipped list, so an orphan explains itself

Shipped files: plugin/throughliner/retired-artifacts.md, plugin/throughliner/hooks/session_start.py

**The record for this change discusses host-only reasoning.** Read it before porting: part of what it describes may belong to the development project rather than to the plugin.

A consumer project ran a migration that generated `BUILD-VIEW.md` at its root, the generated view was retired four days later, and their version top-up then reported nothing to do with the 15KB orphan still sitting there. A retirement removes the code that writes an artifact; it never removes the artifact from projects that already ran it.

Record: `LOG/2026-08-29-retired-feature-leaves-orphan-build.md`

### 819f7f1 — The scope-lock lets the rezip write its own archive

Shipped files: plugin/throughliner/hooks/pre_tool_use.py

**The record for this change discusses host-only reasoning.** Read it before porting: part of what it describes may belong to the development project rather than to the plugin.

The archive step was denied on its first ever run. A rezip runs after a close, so no build working file exists and the scope-lock classifies the session as planning — and `plugin/rezip-archive/` was not on the planning session's standing list. There was no chat shape in which the step could run at all, which is the same failure the `plugin.json` carve-out already answers one path over.

Record: `LOG/2026-08-29-rezip-archive-blocked-by-scope-lock-build.md`

### 819f7f1 — A ritual names the paths its steps write, instead of the lock accumulating carve-outs

Shipped files: plugin/throughliner/hooks/pre_tool_use.py, plugin/throughliner/docs/plan.md

The same failure had happened twice — a ritual step needing to write somewhere the session running it may not — so it is a class rather than a case. A ritual definition now carries a `Writes:` field, and the planning branch of the scope-lock reads the project's own `CYCLES.md` and permits exactly what it names.

Record: `LOG/2026-08-29-ritual-declares-writable-paths-build.md`

### 819f7f1 — A kept item names the files its observation reaches, not only the files it changes

Shipped files: plugin/throughliner/docs/plan.md

A /next run derives its file list from what an item says it changes, which in practice means the Changes line. An observation routinely reaches others — the suite that has to pass, the sibling doc an acceptance check greps — and twice in one run those went missing, so the run stopped mid-flight to ask for a scope addition it should never have needed.

Record: `LOG/2026-08-29-self-scoping-misses-observable-files-build.md`

### 819f7f1 — The outbound register cannot be overwritten or deleted through Claude's tools

Shipped files: plugin/throughliner/hooks/pre_tool_use.py

`INBOX/sent.md` is the index of everything this project has sent or posted, and it is what the repeal check greps for claims already announced. Its folder is gitignored on every path, so unlike every other project document it has no history, no backup, and one accidental deletion ends it.

Record: `LOG/2026-08-29-sent-register-untracked-build.md`

### 819f7f1 — The capability-claim rule reaches what an outside surface permits, not just what a tool can do

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md

A `[user]` walkthrough halted mid-drive on two assumptions about Discord nobody had checked, and both were load-bearing. The rule built the previous day covers a sentence asserting what a *tool* can do; a step asserting what an outside *surface* permits is the identical failure at a site that rule did not reach — and worse there, because a walkthrough is handed to a non-coder to perform with nobody to ask.

Record: `LOG/2026-08-29-walkthrough-asserts-unchecked-surface-build.md`

### 778d6a3 — Audit findings always route to the queue, and the actionable filter comes out

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md, plugin/throughliner/docs/next-audit.md

Two rewordings from one ruling the user gave on 2026-08-29, after a live instance the same day: Claude read the always-loaded triage's middle arm ("a finding → the observing chat's LOG entry") over the audit procedure's "findings route to Unprocessed", and recommended routing a repository inventory out of the queue. Her words: findings of audits always belong in the queue — it's work (planned writing) that doesn't.

**FORMAT EPOCH -> 5.** Your own users' documents need migrating; that is yours to handle.

Record: `LOG/2026-08-30-audit-findings-always-queue-build.md`

### 778d6a3 — Co-writing settles as two rule amendments, not a new flavour

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md

Raised by the user on 2026-08-28 mid-walk-through of the law-prose article: co-authoring is both her work and Claude's, works slightly differently each time, and — her words — "we always have to just kind of shove it in there somehow". The lived instance was that article's fourteen-claim list, planning-type work performed inside a walkthrough and delivered as fourteen approval turns.

**FORMAT EPOCH -> 5.** Your own users' documents need migrating; that is yours to handle.

Record: `LOG/2026-08-30-co-writing-flavour-build.md`

### 778d6a3 — A `Cycle:` field bows a capture out of the planning ladder

Shipped files: plugin/throughliner/docs/plan.md, plugin/throughliner/scripts/queue_digest.py, plugin/throughliner/hooks/post_tool_use.py

Filed at the authoring of the tips-posting cycle, which was created to stop eighteen near-identical tip candidates being met one at a time. Those eighteen became material a cycle's turns draw from, and the definition said so — but nothing told the planning ladder, which would rank them as ordinary captures and present them one by one again. The exact tedium the cycle was created to end, in the user's own words: the interaction was long and probably too tedious.

**FORMAT EPOCH -> 5.** Your own users' documents need migrating; that is yours to handle.

Record: `LOG/2026-08-30-cycle-material-captures-still-ranked-build.md`

### 778d6a3 — A LOG-based cycle observable must be distinguishable from planning's own records

Shipped files: plugin/throughliner/docs/plan.md

Found live on 2026-08-30, in the first session to compute the defective observable. The announced-claims sweep's observable was "the most recent LOG entry under this cycle's slug" — and the planning session that *authored* the cycle wrote a record under that slug, as the shipped procedure has it do for every item processed. The due-ness check read the authoring record as a completed turn, and that session's opening reported the claims sweep as having run today. It had never run once.

**FORMAT EPOCH -> 5.** Your own users' documents need migrating; that is yours to handle.

Record: `LOG/2026-08-30-cycle-observable-slug-collision-build.md`

### 778d6a3 — Audit close's `Approval outcomes` field becomes `Findings routing`

Shipped files: plugin/throughliner/docs/done-audit.md

From the compliance audit of 2026-08-29. This entry carries the reasoning for the five findings that audit produced and that this run built; the sibling entries cite it rather than restating it.

**FORMAT EPOCH -> 5.** Your own users' documents need migrating; that is yours to handle.

Record: `LOG/2026-08-30-done-audit-records-a-repealed-approval-step-build.md`

### 778d6a3 — Build close drops the walk-through outcome definitions it restated after citing them

Shipped files: plugin/throughliner/docs/done-build.md

From the compliance audit of 2026-08-29, lens 1 on the parent axis. Common reasoning for this run's five compliance fixes is in `2026-08-30-done-audit-records-a-repealed-approval-step-build.md`.

**FORMAT EPOCH -> 5.** Your own users' documents need migrating; that is yours to handle.

Record: `LOG/2026-08-30-done-build-restates-cited-outcomes-build.md`

### 778d6a3 — Shared mail-triage step gains the stop-and-wait arm its own child carried

Shipped files: plugin/throughliner/docs/done.md

From the compliance audit of 2026-08-29, lens 2. The reasoning common to this run's five compliance fixes is carried in `2026-08-30-done-audit-records-a-repealed-approval-step-build.md`; this entry adds only what is particular to this one.

**FORMAT EPOCH -> 5.** Your own users' documents need migrating; that is yours to handle.

Record: `LOG/2026-08-30-done-mail-triage-missing-prompt-arm-build.md`

### 778d6a3 — The mis-sited second statement of the scrub rule is evicted from `done.md`

Shipped files: plugin/throughliner/docs/done.md

From the compliance audit of 2026-08-29, lens 1. Common reasoning for this run's five compliance fixes is in `2026-08-30-done-audit-records-a-repealed-approval-step-build.md`.

**FORMAT EPOCH -> 5.** Your own users' documents need migrating; that is yours to handle.

Record: `LOG/2026-08-30-done-md-states-the-scrub-rule-twice-build.md`

### 778d6a3 — A defeated position written in rule syntax is deleted from the INBOX doc

Shipped files: plugin/throughliner/docs/feedback-and-inbox.md

From the compliance audit of 2026-08-29, lens 4. Common reasoning for this run's five compliance fixes is in `2026-08-30-done-audit-records-a-repealed-approval-step-build.md`.

**FORMAT EPOCH -> 5.** Your own users' documents need migrating; that is yours to handle.

Record: `LOG/2026-08-30-inbox-doc-narrates-a-superseded-refusal-build.md`

### 778d6a3 — Digest flags a capture whose prose names an item already cleared to run

Shipped files: plugin/throughliner/scripts/queue_digest.py

Raised by the user at the end of a /rescan on 2026-08-29: should there be a rule checking that what a scan files blocks nothing in the cleared region? Filed as the reworded version of that, on Claude's recommendation and her agreement.

**FORMAT EPOCH -> 5.** Your own users' documents need migrating; that is yours to handle.

Record: `LOG/2026-08-30-newly-filed-work-invalidates-cleared-work-build.md`

### 778d6a3 — Queue lint flags a field marker written anywhere but the start of a line

Shipped files: plugin/throughliner/hooks/post_tool_use.py

The instance, from 2026-08-29: an item's red-flag marker sat at the end of a prose sentence, the digest's pattern is anchored to the start of a line, and so the digest never reported the flag. Rung 1 of the ordering ladder — an uncleared red flag outranks everything — fired by luck rather than by machinery, because someone happened to grep more loosely than the tool does.

**FORMAT EPOCH -> 5.** Your own users' documents need migrating; that is yours to handle.

Record: `LOG/2026-08-30-red-flag-marker-silent-shape-failure-build.md`

### 778d6a3 — Research filings carry an assessment of their own frame

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md

Raised by the user on 2026-08-30, correcting the risk-classes finding. Her costly instance was not a premise going stale but research that was never valid — it answered the questions asked without asking whether the approach fitted the situation at all. Her words: *"the user's questions notwithstanding, is the approach itself valid for the given situation?"* The stakes in that instance: the work concerned a child's whole life, and the approach researched addressed only weeks of it.

**FORMAT EPOCH -> 5.** Your own users' documents need migrating; that is yours to handle.

Record: `LOG/2026-08-30-research-validity-criteria-build.md`

### 778d6a3 — Kept items name the external facts their design rests on, and when each was checked

Shipped files: plugin/throughliner/docs/plan.md

A candidate rule from the proactive-research-offers finding, ranked strongest there and gated in-session with the user present on 2026-08-30. The decision step's kept-item enumeration goes from five entries to six: an item now names the external facts the design rests on and, for each, when it was last verified.

**FORMAT EPOCH -> 5.** Your own users' documents need migrating; that is yours to handle.

Record: `LOG/2026-08-30-rests-on-line-at-decision-step-build.md`

### 778d6a3 — Terminal steps in a walkthrough supply the commands that come before the run

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md

Captured by the user on 2026-08-30 from a live walkthrough in another of her projects, with a screenshot as the evidence. The step said a separate terminal was needed "sitting in the project folder" and then gave only the command to run. Pasted as instructed, it would have run from `C:\` and failed, because nothing ever supplied the `cd` that gets the terminal there.

**FORMAT EPOCH -> 5.** Your own users' documents need migrating; that is yours to handle.

Record: `LOG/2026-08-30-terminal-steps-include-preconditions-build.md`

### 778d6a3 — `workshop/` becomes a method folder and `resources/` moves inside it, epoch 4→5

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md, plan.md, setup.md, migrate-checklist.md, next.md, done-build.md, rescan.md, feedback-and-inbox.md, plugin/throughliner/hooks/pre_tool_use.py, session_start.py, post_tool_use.py, stop.py, plugin/throughliner/scripts/queue_digest.py, measure_written_shape_length.py

Working material stops sitting at the repository root. The user's reason, in her own framing at the decision step: only what is part of Throughliner stays in view, so someone shopping online for a method sees the method rather than the workshop. The method's own documents stay visible because they demonstrate it; everything they merely refer to does not.

**FORMAT EPOCH -> 5.** Your own users' documents need migrating; that is yours to handle.

Record: `LOG/2026-08-30-workshop-becomes-a-method-folder-build.md`

### e04b514 — Planning session 2026-08-30/31: ~30 entries processed, cleared region 8->33 — the gitignore decision with snapshots and a private default, the MCP umbrella refiled with five purposes, the maintenance-sweep cycle authored, three red flags cleared, a tips turn posted terminal-free, and the epoch-5 migration run

No session record could be matched to this commit, so there is no behavioural summary for it. Read the diff.

### c5a62a7 — the session opening names the commands in the form that always works

Shipped files: plugin/throughliner/hooks/session_start.py, plugin/throughliner/docs/skill-nonspecific-rules.md

`session_start.py`'s ready line now names `/throughliner:plan` and `/throughliner:next`, with one clause saying the bare forms work on some installs and not others. `skill-nonspecific-rules.md`'s command-arrived-as-text arm gained the second suggestion: where the app answered that a command is not available, ask the user to retype it with the plugin's name in front.

Record: `LOG/2026-08-31-bare-command-name-fails-before-rules-load.md`

### c5a62a7 — the tick specimen a run actually reads now shows the confirmed form

Shipped files: plugin/throughliner/docs/next.md

`next.md`'s progress-format block showed `- [x] item description — done`, while `next-build.md`'s per-item completion step carries the real requirement: `done, confirmed` or `done, UNCONFIRMED: <what still needs running>`. Two statements of one format, one of them incomplete. The block now shows both forms and names next-build.md as the wording's home, so the copies agree and one is marked as the citation.

Record: `LOG/2026-08-31-build-ticks-omit-the-confirmed-form.md`

### c5a62a7 — the `Cycle:` field is now shown where a session learns the entry shape

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md

`skill-nonspecific-rules.md`'s Captures line-format fence lists every field an entry may take, and `Cycle:` was absent from it while three tools already read the field — plan.md's pass-over arm, the queue digest's parse-and-print, and the lint's mid-line marker guard — and SPEC described it as product truth. A field readable by three tools and shown by none is one nothing will ever produce unprompted: the write-path-with-no-read-path failure the research-index rule names, running in the other direction.

Record: `LOG/2026-08-31-cycle-field-missing-from-line-format.md`

### c5a62a7 — a cycle or ritual definition now passes the test a kept work item passes

Shipped files: plugin/throughliner/docs/plan.md

`plan.md`'s cycle-authoring step gained the clause that a definition's steps, criteria and observable pass the same test a kept item's instructions do: no open class, no decision scheduled into the turn, stated concretely enough that two sessions given the text produce the same turn. Its parent is the buildability check's design-decision clause, extended to the definitions the same step authors.

Record: `LOG/2026-08-31-definitions-pass-the-buildability-test.md`

### c5a62a7 — the method documents leave git, and the plugin supplies the undo git was providing

Shipped files: plugin/throughliner/hooks/pre_tool_use.py, plugin/throughliner/hooks/session_start.py, plugin/throughliner/docs/skill-nonspecific-rules.md, plugin/throughliner/docs/setup.md

The decision behind this and its sibling `[untrack-method-files-here]` is the user's, from her position that the privacy headaches of public method files are not worth it. This entry carries the reasoning for both; the sibling's cites it.

Record: `LOG/2026-08-31-gitignore-choice-with-snapshots-build.md`

### c5a62a7 — the hold-back rule gained its one exception, and the restatement test is why

Shipped files: plugin/throughliner/docs/done-plan.md

`done-plan.md`'s hold-back-unverified-work rule now carries a clause: where the held item is itself the only verification of its blocker, the hold is not written — the item clears, its walkthrough is the verification, and its prose says so.

Record: `LOG/2026-08-31-held-item-is-its-own-verification.md`

### c5a62a7 — the date rule widened to every time expression, chat included

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md

`skill-nonspecific-rules.md`'s computed-date paragraph now governs every statement of when something happened or will happen — a date, "yesterday", "this morning", "twenty minutes ago" — rather than date decisions alone. One paragraph, widened scope, no second rule, which is what kept it an amendment costing no slot.

Record: `LOG/2026-08-31-no-underived-time-statements-build.md`

### c5a62a7 — a run that changes a hook may now write that hook's test suites

Shipped files: plugin/throughliner/hooks/pre_tool_use.py

`pre_tool_use.py` permits `workshop/resources/testing/` (and its pre-move path) to any run whose agreed file list names something under `plugin/throughliner/hooks/`. Bounded to exactly that pairing: a run touching no hook is still refused, and a hook-touching run is still refused everything outside the testing folder. Both directions are asserted in the new suite, because without the second the rule would be a general widening wearing a narrow description.

Record: `LOG/2026-08-31-observation-files-named-by-folder-stop-the-run.md`

### c5a62a7 — a question deliberately left open now becomes a capture at the moment it is left open

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md

`skill-nonspecific-rules.md`'s "Nothing unrouted survives a chat" rule gained one arm: a want set aside for a winning alternative, a rejection repealed, a resolution ending in "may be re-proposed later" — each routes to a capture, credited to whoever wants it. It may carry `Not before:` or `Blocked by:` under their existing provisions; what it may not do is exist only as prose in a record or a rules file, which is read on demand while the queue returns things by itself.

Record: `LOG/2026-08-31-open-question-files-a-capture.md`

### c5a62a7 — four decision turns now say what they carry, where only length and count were governed before

Shipped files: plugin/throughliner/docs/plan.md, plugin/throughliner/docs/next.md, plugin/throughliner/docs/skill-nonspecific-rules.md

The diagnosis this transcribes, shared by five captures filed within two days: the response-shape tags govern how many messages and how long, and nothing governed *what belongs in a particular turn*. A content-selection failure, not a length one. Each of the four turns named in the item gained one operative line, and `skill-nonspecific-rules.md`'s message-shape bullet now points at those lines as the governing specification at those sites rather than restating the general principle a fifth time.

Record: `LOG/2026-08-31-per-turn-content-rules-build.md`

### c5a62a7 — the lint speaks when the flag set changes, and is silent otherwise

Shipped files: plugin/throughliner/hooks/post_tool_use.py

`post_tool_use.py` no longer prints a count of standing flags after every edit and every unrelated shell command. It emits when a flag appears, and now also when one clears, naming the changed flags either way; an unchanged set emits nothing, so silence carries the meaning the constant line pretended to. Computed against the committed file every time, so nothing is stored and no state file can go stale.

Record: `LOG/2026-08-31-queue-lint-narrates-on-every-bash.md`

### c5a62a7 — the harness's plan-mode folder permitted, on the scratchpad's ground

Shipped files: plugin/throughliner/hooks/pre_tool_use.py

`pre_tool_use.py` now permits the harness's plan-mode plans directory in both the planning branch and the shell-write check, alongside the scratchpad and for the same reason: it sits outside the repository, so nothing the scope-lock protects lives there.

Record: `LOG/2026-08-31-scope-lock-blocks-harness-plan-file.md`

### c5a62a7 — setup writes a personal fact only where the user supplied it, and this rule shipped without a gate

Shipped files: plugin/throughliner/docs/setup.md

`setup.md`'s Step 4 now carries the rule that a personal fact — a name above all — reaches SPEC or any scaffolded document only where the user supplied it in `/setup`'s own answers, with the machine's own sources named as the things that are not answers: the git `user.name`, the folder path, the account the session runs under. Where such a fact would help and nobody supplied it, it is left out; where it is genuinely needed, it is asked for like any other question.

Record: `LOG/2026-08-31-setup-infers-a-name-into-spec-build.md`

### c5a62a7 — a blocker written without brackets is now visible at both ends

Shipped files: plugin/throughliner/scripts/queue_digest.py, plugin/throughliner/hooks/post_tool_use.py

Two guards on one defect reported by a consumer project running 1.21.1-test2. The digest treats a `Blocked by:` line naming no bracketed slug as a placement contradiction, printed in the block that already exists for exactly that; and the lint flags the same shape at write time, in the same family as its mid-line marker guard and for the same reason — one canonical shape, checked where it is written.

Record: `LOG/2026-08-31-unbracketed-blocker-invisible.md`

### c5a62a7 — content belonging to an unpresented entry now waits for that entry's turn

Shipped files: plugin/throughliner/docs/plan.md

`plan.md`'s one-at-a-time pass gained the clause that content belonging to a not-yet-presented entry is carried to that entry's own turn and written then. Stated as the action rather than as a bar, per the wording rule.

Record: `LOG/2026-08-31-unpresented-item-content-relocated-early.md`

### c5a62a7 — walk-through outcomes gained a fourth arm rather than a fourth box

Shipped files: plugin/throughliner/docs/next.md, plugin/throughliner/docs/done.md

`next.md`'s outcome-values provision now reads: done, deferred, not reached — or, where none fits, what actually happened in one plain sentence, with the detail in the item's own record. `done.md` carried a duplicate of the value list and now cites next.md instead; its two paragraphs restating the `deferred` and `not reached` rules came out with it, so the subject is stated once and pointed at everywhere else.

Record: `LOG/2026-08-31-walkthrough-outcomes-miss-halted-and-partly-walked.md`

### c5a62a7 — a walkthrough step carries at most three instructions

Shipped files: plugin/throughliner/docs/skill-nonspecific-rules.md

The walkthrough-authoring requirements in `skill-nonspecific-rules.md` gained the ceiling, as a subordinate clause of the parent line that already says each step names the thing to click or type and the thing to look for. Anything beyond three splits into further steps, each carrying its own look-for.

Record: `LOG/2026-08-31-walkthrough-steps-two-actions-max.md`

### fb7c4ee — whose idea a thing was now survives the mailbox, as a role rather than a name

Shipped files: plugin/throughliner/docs/feedback-and-inbox.md

Raised by the user while correcting exactly this failure live. The per-turn content proposal built into `[per-turn-content-rules]` is hers, but the two inbound INBOX reports carrying it had anonymised the proposer to "their user" — so it arrived here creditless and was within a sentence of being recorded as another project's user's idea.

Record: `LOG/2026-09-01-correspondence-preserves-provenance.md`

### fb7c4ee — the MCP helper's first slice: four read-only tools, registered for this project alone

Shipped files: plugin/throughliner/mcp/server.py

Slice one of the MCP umbrella, deliberately read-only. It opens no file for writing and runs no command that changes anything, so it proves the plumbing — a server registered, trusted, connected, its tools reachable — without any risk that a bug in the plumbing costs a file. The writing slice is designed only once this one is proven in real sessions. Dogfood-first is the user's agreed shape: consumers get nothing until promotion.

Record: `LOG/2026-09-01-mcp-slice-one-readonly-server.md`

### fb7c4ee — a lift now says what the item's premise rests on, at the two moments held work comes back

Shipped files: plugin/throughliner/docs/plan.md

A candidate rule from `workshop/resources/research/eliciting-proactive-research-offers.md`, ranked second there, whose hold lifted when `[rests-on-line-at-decision-step]` shipped — that line being the thing this re-check reads.

Record: `LOG/2026-09-01-premise-recheck-at-re-offer.md`

### fb7c4ee — every scripted turn in the shipped docs inventoried, and the item's own premise turns out to be half wrong

Shipped files: plan.md, setup.md

Raised by the user and processed on the spot, on her framing that the per-turn content rules built 2026-08-31 covered planning-session turns only. She chose the sweep over spot-fixes — *"happy to take the slower pacing"* — in the inventory-first shape the recorded-states audit proved.

Record: `LOG/2026-09-01-scripted-turns-inventory.md`

### fb7c4ee — the instance paragraph comes out of setup.md's personal-fact rule, its story left to the record

Shipped files: plugin/throughliner/docs/setup.md

`setup.md`'s Step 4 carries a rule admitted at the gate on 2026-08-31: a personal fact reaches SPEC or any scaffolded document only where the user supplied it in /setup's own answers. Beneath it sat an eight-line paragraph beginning "The instance this comes from", telling the story of a first-time user whose name reached SPEC.md without anyone asking him for it.

Record: `LOG/2026-09-01-setup-name-rule-instance-paragraph-evicted.md`

### fb7c4ee — the stop hook's hedge filter scoped to the claim's own sentence, and the suite widened so it can fire in a test at all

Shipped files: plugin/throughliner/hooks/stop.py

From the `[stop-hook-missed-an-unfiled-claim]` audit, with `[stop-hook-suite-fixtures-have-no-surrounding-prose]` merged in — its fixture finding rode whatever this settled, by its own text.

**Why it was made** (from the record of the session that decided it, `LOG/2026-08-31-stop-hook-negation-window-eats-real-claims-plan.md`): Processed 2026-08-31, kept cleared, with [stop-hook-suite-fixtures-have-no-surrounding-prose] merged in (its fix rode this by its own text). The audit's driven finding: detection works, but the hedge filter scans 60 characters before a claim and the method's own required capture-report wording ("captured rather than done now") feeds it its trigger words — three real replies went undetected, all with the hedge in the previous sentence. The design: the filter fires only when the hedge shares the claim's sentence — a past-tense claim standing alone is a claim whatever precedes it, while genuine hedges ("I would file", "once the build lands") share their claim's sentence and stay suppressed. Dropping the filter refused: it was added because the check fired on planning talk. The merged fixture finding travels to the build: every suite fixture is a bare sentence so the filter never fires in a test — the three recorded misses become catch cases and a same-sentence hedge a pass case; the general lesson (a fixture that isolates the unit can isolate away the interaction that breaks it) belongs to this record.

Record: `LOG/2026-09-01-stop-hook-negation-window-eats-real-claims.md`
