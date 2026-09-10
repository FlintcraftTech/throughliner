# Self-authoring rules — the record behind the rule gate

**The operative gate lives in this project's `CLAUDE.md`, and that is what you run.** This file is the record behind it: the repeal histories, the defeated proposals, the measurements, and why each test is shaped as it is. Open it when something settled is about to be re-proposed — not while authoring, where the always-loaded gate is already in front of you.

**How to reach the why behind an existing rule, when the gate is run against one whose reasoning lives elsewhere:** search `LOG/index*.md` for the rule's distinctive words and open the matched entry — the index line ends with its filename; where the index misses, `git log -S` over the rule's own shipped file finds the commit that added it, whose message names the session. Retrieving the why is what stops an author re-deriving the reasoning or re-proposing something already refused.

**Why the operative half moved (2026-08-14).** A build amending fifteen rules in the always-loaded file wrote a `Rule gate: run — …` disposition without this document ever having been opened, reasoning from `CLAUDE.md`'s summary of the gate and recording the result in the gate's format. Re-run properly at /done, the gate produced three findings the first pass had missed. The trigger had been in front of that session twice and neither pointer produced the read — which is this document's own §3 test answered against itself: a session cannot fetch a rule it has never read, and nothing announces the moment the gate applies. The remainder has an unmistakable trigger and can be fetched; the gate has no trigger at all and cannot.

**Where the gate runs (2026-08-14).** At /plan's keep-step, as each rule is designed, with the disposition written into the queue item. The earlier requirement — at the moment of authoring, into the build working file — is superseded: a planning session has no build working file, and a build-time disposition is still written after that item's rules were designed, so it can describe but not refuse. Refusing costs a conversation at /plan and finished work anywhere later, which is the whole argument.

**What did not change: loading the gate does not make a disposition honest.** `CLAUDE.md` already records that neither board signal can tell an honest `run` from a dishonest one. Migration raises the odds the gate is applied; it cannot verify that it was.

## Additions are not free

**The binding constraint is relevance, not a count.** Content that merely doesn't apply this session does not get filtered out selectively — irrelevant instructions cause wholesale dismissal of the set, and semantically similar but inapplicable rules are the principal mechanism of that interference. Near-identical rules are optimal distractors for one another. A large body of same-sounding behavioural rules is exactly that shape.

So every rule admitted degrades the rules already there. That is the cost this document exists to charge, and the reason it opens by stating it: each individual addition looks free, which is how the predecessor to this document was honestly applied all the way from 6,162 words to 21,445.

**No ceiling is stated here, and the omission is the finding rather than a gap.** This section used to open by declaring a count of 150–200 instructions as the binding limit. That figure was re-validated against the 5-series on 2026-08-12 and found roughly an order of magnitude too tight ([instruction-ceiling-revalidated-for-5-series.md](research/instruction-ceiling-revalidated-for-5-series.md)), and `resources/rule_signals.py` removed the ceiling derived from it the same day, replacing it with a growth report carrying no threshold. **No replacement number is introduced**, here or anywhere: this project has now banned inventing one twice, and a second unbacked figure in the gate would restore by hand what was removed by code. The charging argument never depended on the number — relevance is stated in the same breath and survives the research untouched.

Sources: [instruction-file-bloat-and-subtraction.md](research/instruction-file-bloat-and-subtraction.md), [legal-drafting-for-tight-rules.md](research/legal-drafting-for-tight-rules.md), [legislative-prose-syntax.md](research/legislative-prose-syntax.md).

## 1. Admission — the record

**Where the parent-naming rule comes from.** Legislation distinguishes an amendment from a *freestanding* provision, and that distinction maps onto the cost above exactly: a freestanding rule adds another statement competing for relevance with every other; an amendment adds none, because it changes a rule already there.

**On the subordination test.** It runs both directions: writing, try the fragment before the sentence; auditing, hunt for standing rules that should have been subordinate. A unit that won't convert without losing content is genuinely freestanding — forcing it is how a subordination pass deletes a rule.

**On the hook question.** Every hook adds friction every session forever. The cost of the failure decides, not the fact that a rule slipped.

**Question 1's "more than once" count was repealed on 2026-08-24.** The question now reads "Has this actually failed, in a way you can point to?" — one pointable failure admits, and speculation still stops at the same clause. The count fell because two same-day amendments were each admitted on a single recorded instance, and each also satisfied the outgoing test on its own terms — the count was neither what admitted them nor what stops a speculative rule, which the pointable-instance clause does alone. The clause the question keeps is the guard; the count was a bare number riding it.

### Declaring a limit — the record

An absolute number is not the defect. The worked example is the **10,000-character hook output cap**: it is imposed by Claude Code, the derivation is one sentence, and anyone can check it against the tool. What is banned is the undeclared derivation, because a limit nobody can trace is a limit nobody dares change, and it fires against correct work.

**The 150–200 instruction ceiling used to stand here as a second example, and it is now the counter-example.** It came from research, which is a qualifying derivation, and it was still wrong: re-validated against the 5-series it proved roughly an order of magnitude too tight, and it had already propagated into a constant, a board signal, and the framing of several queue items. So a stated derivation makes a limit **traceable and revisable**; it does not make it correct. A number sourced from research about one generation of models is a number with an expiry date, and this rule is what makes the expiry findable.

### Admitting an exception — the record

Before the restatement test existed, nothing decided whether an exception got to exist, so exceptions were admitted on the author's say-so. Every author believes their own rule is the edge case; that belief is what the purpose-clause test was rebuilt to stop counting as evidence, and the exception test mirrors its shape on purpose — same bar, same reason.

**The worked case, which is the evidence for the test.** [derivation-required-for-limits] was drafted as *a bare number is banned, except where it derives from a proportion, from research, or from an external constraint*. It restates without loss as **a limit must state what it was derived from** — the same rule, with no exception in it. The first test disposed of the case that produced the block.

**No count is written, deliberately.** "More than N exceptions means the rule was never worked out" would itself be a bare limit needing its own derivation, with nothing to derive it from. The restatement test does that work without counting: a rule accreting exceptions is one whose exceptions each failed restatement, which is visible on the face of it.

## 2. Eviction — the record

**Why the scan clause exists.** A skill opening — /plan's Step 1, /next's pre-flight, /done's close — is the one place the method accretes without any addition looking like a rule: each scan is individually small, individually tagged, and folded into one consolidated narration, so nothing anywhere counts them. /plan's Step 1 now fires eight, and the most recent was added with nothing objecting. A rule that permits unlimited additions so long as each is small has no stopping condition, which is what that clause supplies.

No cap and no number. Any figure would be invented, which the derivation rule bans; and each part being bounded is precisely what fails to bound the sum. Naming the displaced scan is what forces the sum to be looked at.

The evidence is one realised instance, not a pattern: an advisory read at Step 1 and not surfaced for three hours. Recorded at that strength deliberately, so a later auditor can weigh it honestly — the claim is that the opening keeps growing and has dropped something once, not that it drops things routinely.

## 3. Distribution — the record

Without the fetch constraint, distribution becomes a way of hiding bloat rather than removing it. The limit is recorded in [`LOG/2026-08-03-docset-b-progressive-disclosure.md`](../LOG/2026-08-03-docset-b-progressive-disclosure.md).

**On the always-loaded file's name.** It is deliberately defined by negation, and the trade is worth stating because it was argued out and settled. A negative name is a good test at *authoring* time — it repels a rule that cannot pass — and a poor signal at *run* time, since a session inside /next could read "skill-nonspecific" as "not about the skill I'm running". The two risks are not symmetrical: the dumping-ground failure is evidenced, at 6,162 words growing to 21,445, while the run-time misread is hypothetical and has not been observed. So the name guards the evidenced failure, and making the file actually get read is left to a mechanism, which is the right tool for forcing in any case.

The residual weakness, stated rather than left to be discovered: a filename is soft steering, and nothing produces evidence the test was applied. The file's own first line restates the test, which improves on a filename because an editing session has necessarily read its first page — but it is still steering, not enforcement.

## 4. Wording — the record

**The source of the prohibition rule**, in the user's words, 2026-08-09: anything that is described in terms of what not to do only means the rule of what TO do was never adequately described in the first place. Where no action can be stated, that is the finding: the rule was never worked out.

**On the drafting devices.** A rule followed by a swelling "provided that" is the habit the bare-statement device exists to break. Main-clause-first matters most where the conditions are long, since a reader needs a sentence's principal parts before it can place the rest. `subject to <X>` beats restating an exception because a restatement costs a paragraph and creates a second copy that drifts. Those devices *place* an exception that has already earned its place; whether it earns one at all is the restatement test.

## Rationale lives outside the operative rule — the record

Legislation states the binding rule bare and puts the reasoning in recitals and explanatory memoranda — published alongside, aiding interpretation, but not the law. The method has done the opposite, and that habit is the single largest contributor to per-rule weight. It is settled, not open: [opus-5-instruction-compliance.md](research/opus-5-instruction-compliance.md) records that why-clauses travelling with every rule are exactly the over-prescription the 5-series guidance says degrades output, and [fable-5-instruction-compatibility.md](research/fable-5-instruction-compatibility.md) resolves it — keep the throughline; stop treating why-attachment as a compliance requirement.

**Why the FAQ is barred as an eviction destination.** This is narrower than "the FAQ is not a rationale home", deliberately: an FAQ legitimately answers *why does the method behave this way* when a user asks, which is what an FAQ is for, and the FAQ-sync rule requiring an entry when a user-facing change lands stands untouched. What is repealed is the routing of *relocated rationale* into it. Sessions kept proposing that routing because this document used to supply the argument for it — the plugin ships neither `LOG/` nor `resources/`, so a consumer-facing why sent to the LOG is deleted rather than moved. The reasoning was sound on its premise; the premise is what is rejected, since an evicted why needs no home at all.

**The surviving destination is provisional, and this is an open question rather than a caveat.** Routing authoring-why to the LOG entry that decided it is fine for now, but it may not survive applying law-writing style to our own prose. The model this section cites puts reasoning in recitals and explanatory memoranda **published alongside** the instrument; our LOG is a development record that does not ship at all. So the LOG is where authoring-why goes because no published-alongside artifact exists, not because it is the right home.

### Where a reason is needed to apply the rule — the purpose-clause test

The old narrow exception — *a rule whose reason is genuinely needed to apply it correctly at its edges keeps one short clause* — is **repealed**. It is not consistent with the legislation this section derives from, which states the binding rule bare with no "unless the reason helps" carve-out; and an exception phrased as a judgment is decided by whoever is authoring, every one of whom believes their own rule is the edge case. That is the shape under which the predecessor document grew from 6,162 to 21,445 words while being honestly applied.

But some sentences genuinely must travel with a rule for the rule to be applied correctly, and repealing the exception with nothing in its place strips them. The replacement is **reclassification, not exemption**. Law does this as a purpose or objects clause: inside the instrument, shipping with it, guiding application, neither recital nor memorandum. Reclassification asks a question with an answer — *can this rule be applied correctly without this sentence?* — where the repealed exception asked how special a rule is.

**Why the order of the three parts is the safeguard.** A marker or tag was rejected for the protection step: a fresh short session may not know a convention and will strip it while skimming, whereas broken grammar is visible at the moment of the cut. The review step exists because without it the category would be permanently immune to the staleness test.

**Three proposals were defeated on the way to that order, recorded so they are not re-proposed.** (a) Grammar as the *admission* test — rejected: necessity is not decided by syntactic validity, and using it that way inverts into a bloat vector, since welding any sentence into the operative clause would make it permanently unstrippable. Syntax protects; it never admits. (b) Weld-first, justify after — that is exactly the failure the order above prevents; gate-then-weld is the same two steps in the order that works. (c) Shipping the admitting instance alongside the clause — rejected, because that ships history with the rules, which is the bloat being fought. **The instance never ships.** What ships is the purpose clause alone, bare and operative.

**Why the unshipped evidence leaves no gap.** Protection is readable from the shipped text alone, since inseparability is visible in the sentence. The instance is needed only to re-test an admission, and re-testing is maintenance, which happens only in the repo where the LOG is — consumers never audit method rules. Net effect: the shipped docs get *shorter* than under the repealed exception, which licensed a short clause of reasoning; this licenses none, only operative text.

**The honest limit.** This protects against accidental stripping, which is the failure that has actually happened. It cannot stop a pass that deliberately rewrites a rule to remove the dependency; nothing short of a hook that understands meaning could. What the form guarantees is that doing so is a visible rewrite rather than a quiet deletion.

**Moving a why out is a subtraction-pass move, and its hazard — taking an operative statement with it — is covered in [`rule-maintenance.md`](rule-maintenance.md).**

## Repeals recorded elsewhere

**The planning close's reorders — do not reinstate.** Build-order re-derivation
across Processed and the Unprocessed reorder by unblock-potential were both
repealed on 2026-08-11. The reasoning, and the two further reorders retired in
the same run, are in `LOG/2026-08-11-processed-reorder-mostly-unnecessary.md`
(commit `7c9922a`) — read it before proposing any of the four again.

This note lives here rather than in `done-plan.md` because its audience is a
future method author, which a consumer never is, and that doc ships.

## This document's own limits

It is subject to its own admission test. Per-rule worked examples are deliberately excluded: they are the growth engine, and they are how its predecessor justified its own length.

**It declares no maximum size, and the omission is deliberate.** A 1,200-word ceiling stood here until 2026-08-11 and was repealed under the derivation rule above: it was a bare number, stated in the same commit that created the file, at one draft's length plus a margin. Growth pressure on this document is handled by the same eviction and audit machinery as everything else. If it does bloat, the answer is a derived measure — a proportion of something that varies with it, or the instruction count this document already endorses — never another guess.

**There is no per-model authoring pass, and that is deliberate.** This document used to carry one for Opus 4.8. Docset A retired on 2026-08-09 and 4.8 is no longer a supported model, so the checklist was deleted rather than marked historical — a document that reads as live gives live instructions, and its model-specific checks were all prescription-*adding*, the opposite of what the 5-series wants. The honest cost: there is now no written account of what the current models steer on. There hasn't been one since the retirement; this only stops the document pretending otherwise. A 5-series pass gets written if something shows one is needed.
