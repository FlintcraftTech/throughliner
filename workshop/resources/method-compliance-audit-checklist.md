# Routine method-compliance audit checklist

The standing criteria for a periodic compliance audit of the method's own procedure docs — `skill-nonspecific-rules.md`, `setup.md`, `plan.md`, the `next*` family, the `done*` family, and any procedure doc added later.

**What this is for, and how it differs from the authoring gate.** The rule gate — in this project's `CLAUDE.md` — is a per-rule check run *once, at authoring time* — you run it over a rule before that rule ships. This checklist is the *corpus-wide periodic sweep*: you run it over docs that already shipped, to catch what drifted or was never checked. The un-hardened tool-use rule that slipped past for so long (the subagent-cost incident, 2026-06-24) is exactly the gap this exists to close — an authoring-time check never re-examines old rules, so without a periodic sweep, a rule authored before a standard existed never gets held to it.

It is a dev artifact. It audits the method's own docs, so it is host-only — not shipped in the plugin package, no FAQ, no SPEC entry — the same status as the gate it builds on.

**What triggers an audit — the board's AUDIT-LAG check, since 2026-08-22.** `resources/rule_signals.py` fires when rule-bearing commits exist that no compliance audit has covered — the boundary is the most recent compliance-audit LOG entry, an artifact rather than a threshold. The check files one `[audit]` capture scoped to the changed files and stays quiet while it is open. (The earlier arrangement — a person deciding by judgment after the AUDITED ceiling was repealed — meant nothing ran the sweep, for the same reason the checks themselves once had no trigger. The count-based ceiling stays repealed: the 150–200 instruction figure it derived from was re-validated against the 5-series and found roughly an order of magnitude too tight, `research/instruction-ceiling-revalidated-for-5-series.md`, and a sweep every N sessions stays rejected as a bare number with no derivation.)

**The routine form is DELTA SCOPE: audit the rule files changed since the last audit, against every lens, at parent axis.** The corpus-wide sweep is not the standing shape — one full pass exists as its own separately filed item, and after it the delta is the unit. Delta scope is what keeps each audit small enough to actually run, which the full-sweep duty never was.

Run every lens over each doc in scope. One read of the doc serves them all. Findings route to Captures for a later /plan to scope — an audit produces findings, not edits to the docs it reads.

## State the axis before you start, and it is the parent axis

**An audit compares a doc against its parent; it compares siblings only for a rule one parent rule would replace.** Say which axis you are running on before the first read, and if it is not the parent axis, argue for the one you have chosen.

```
parent axis     done-build.md vs done.md; next-build.md vs next.md; any
                sub-doc vs skill-nonspecific-rules.md. Finds a child restating
                what its parent already carries — genuine duplication, because
                the child is loaded WITH the parent and the reader has both.

sibling axis    done-build.md vs done-plan.md.
                Finds the same RULE in two or more siblings where one rule at
                their common parent, conditioned, would replace the copies
                (Lens 8, Across siblings). WORDING similarity alone is not a
                finding: docs parallel by design phrase alike, and near-identical
                phrasing between them is the expected state.
```

**The worked instance, which is why this is not a stylistic preference.** An audit once reported `done-build.md` and `next.md` carrying the same rule in near-identical words. True as text, wrong as a finding: `next.md` guards *presenting* a run, `done-build.md` guards *writing a size cap into the note for the next session*, and no session reads both. Two holes, two plugs, one wording. The finding was refused at processing weeks later, with both docs untouched. On the parent axis it would never have been produced, since neither doc is the other's parent.

## Every finding names where each site fires

A finding gives the moment each site is read, not only the line it sits on. One sentence per site, and it is what catches a false duplication at the audit rather than weeks later at processing — two rules that read alike but fire at moments no single session reaches are not duplicates at all.

## The instruction count — run this first

The gate's binding limit is a **count of instructions**, not a word count, so a sweep that doesn't produce a number can only produce opinions: "evict what fails admission" has no target and no stopping rule without one. Count before disposing of anything.

**Scope the count to the always-loaded corpus.** That is `skill-nonspecific-rules.md` plus, in the dev project, `CLAUDE.md`. The skill docs (`plan.md`, `next.md`, `done.md`, `setup.md` and the flavor families) are excluded: they load only when their skill runs, and the ceiling is about what competes for attention in every session. Audit them under the three lenses below; don't count them against the ceiling.

**Counting rule.** One instruction per discrete directive Claude must follow — a bolded rule statement, a bullet, or a decision block. Descriptive prose, rationale and worked examples score zero. Count per section and record the section totals, not just the sum: the sum tells you whether there is a problem, and the section totals tell you where it is.

**Report the split by audience, not just the total.** A consumer loads only `skill-nonspecific-rules.md`; the dev project loads both. Those are two different numbers against the same ceiling, and collapsing them hides which one is actually over.

### Dispositions

Every rule the inventory touches gets one:

```
keep                    admissible today, correctly placed, correctly worded
recast                  amendments have accreted past legibility; repeal the
                        whole thing and replace with one new text
consolidate-and-repeal  merge the rules on a topic into one AND delete the
                        priors — the repeal is the essential half
evict                   delete outright: fails admission, or is stale
relocate-rationale      the rule stays; its why moves out (consumer-facing why
                        to the shipped FAQ, authoring decision to its LOG entry)
```

`relocate-rationale` saves no slot and is still worth doing: the ceiling counts instructions, but per-rule weight is the other half of what makes a corpus hard to follow.

**Redistribution is a disposition the gate deliberately does not list, and it needs its own justification each time.** Moving a rule to a fetched doc removes it from the count without removing it from the method, which is how bloat gets hidden rather than cut. It is legitimate only where the rule has a trigger a session cannot miss — a word the user says, a hook that surfaces something. Record that reasoning per rule, never once for a batch.

### Two things learned running this (2026-08-09, the first inventory)

- **The eviction list is the audit's output, and it goes to Captures like every other finding.** This document used to say the list went in as build work cleared to run, and separately that eviction had to happen inside the run — both were repealed on 2026-08-12 by the user's ruling that audits always file to Captures, made when the contradiction was surfaced at /plan. The ruling also restores agreement with the shipped contract, which says an `[audit]` reports findings instead of editing files; the checklist had been contradicting the plugin.
- **The concern those clauses carried is real and is rehomed rather than dropped.** An audit whose findings are never acted on reproduces the failure it exists to fix. What answers that is the queue, not the audit: findings are ordinary work, ordered by the ladder and counted toward the throughput floor, where ignoring them is visible. Filing an eviction list and never building it is a queue problem with a queue remedy — it is not a reason to let a review pass rewrite the corpus it is reading.
- **An `[audit]` item that names a document to write into contradicts the audit contract and must be surfaced, not followed.** This checklist is named as the criteria home, which reads as a doc-write. The resolution that worked: the *findings* went to the queue, and only the *method* — this section — was written here.

## Lens 1 — self-authoring compliance

Apply the four parts of the rule gate — admission, eviction, distribution, wording — to each doc. The gate in this project's `CLAUDE.md` is the single source of truth for the tests; read them there rather than re-listing them here, so the two never drift. [`self-authoring-rules.md`](self-authoring-rules.md) carries the record behind them — the repeals, the defeated proposals, the measurements — and is worth opening when a finding turns on why a test is shaped as it is.

Read corpus-wide, the gate asks things it can't ask one rule at a time:

- **Admission, retroactively.** Which rules here would not be admitted today? A rule with no pointed-to failure, one Claude follows unprompted, one that applies to only some sessions but is always loaded.
- **Eviction debt.** Where does a rule sit alongside the earlier version it was meant to supersede? Consolidation that never repealed its priors is the signature.
- **Distribution.** Which always-loaded rules are reference material that could be fetched on demand — and, the reverse error, which fetched material is a standing behavioural rule a session would never know to look for? Then the misplaced-rules question, run doc by doc with plan.md first, since it is the one that grew: for each rule in a procedure doc, name the moment it governs as a command and a step; where that moment belongs to a different command, file a finding naming the rule, the doc it sits in and the doc that owns its moment. Two limits: it reaches only a rule about another command's moment — a rule that genuinely governs planning's moment but was written as a fresh paragraph because plan.md was open is the unclaimed-parents test's, not this one's; and the read is judgment, since nothing mechanical knows which step a sentence governs.
- **Rationale placement.** Which operative statements still carry their why inline, and where should it go — the shipped FAQ if a consumer would want it, the deciding LOG entry if it's an authoring decision? When moving one, check the clause isn't *stating* a rule while arguing for it.
- **Consistency.** Is a rule held to its own standard across docs? Hardened in one doc but cited loosely in another is a finding even when each instance reads fine alone.
- **False subordination.** A nested unit that is a complete sentence is a freestanding rule wearing a bullet, and is read against the gate as one — admission, eviction, distribution and wording — rather than passing as part of its parent.
- **Exceptions, retroactively.** For each existing exception, restate the rule so that it does not need one; an exception that restates away without losing content is a finding.
- **Vacated rules.** For a rule carrying qualifications, list the cases its bare statement covers, take away each qualification's cases, and read what remains; a rule with no case left where it fires as written is a finding, since its qualifications were the rule all along and the bare statement is what to restate. A rule whose provisions have grown past what a reader holds when they reach its end is filed under the same test, naming the bare instruction and the count of provisions beneath it. The test above reads one exception at a time; this one reads their sum. Limit: a judgment read, since no count tells a qualification from a cancellation.
- **Unclaimed parents.** For each counted rule statement in a document, run the parent lookup against the rest of the corpus (`py throughliner/workshop/resources/rule_signals.py . --parent "<statement>"`), take the top hits as candidates, and read each pair by the gate's subordinate-unit test; a freestanding statement that reads as a refinement of another is a finding naming its parent, to be folded. One document per turn where the corpus is too large for one pass. Limit: the lookup ranks by shared words, so a refinement phrased in other words than its parent is not reached.

**Eviction does not happen in this run.** The sweep names what should go and why; the removal is separate work, filed to Captures like every other finding — see the dispositions note above for why the concern behind the older, opposite instruction is answered by the queue rather than by letting an audit edit.

## Lens 2 — tag placement

Each procedure step carries the response-shape tag that fits what it does (`[SILENT]` / `[BRIEF]` / `[DISCUSS]` / `[PROMPT]` / `[SEQUENCE]`, defined in skill-nonspecific-rules.md). Check each step for three failure modes:

- **Missing** — a step that produces output (or withholds it, or waits, or sequences) but carries no tag, so its output behaviour is left to chance.
- **Wrong** — a tag that fights what the step does: `[SILENT]` on a step that must ask the user, `[DISCUSS]` on pure internal bookkeeping, `[BRIEF]` on a genuine decision point that needs room.
- **Prose where a tag belongs** — a step that describes its output behaviour in a sentence ("keep this short," "don't say much here," "stop and wait") instead of carrying the tag that encodes it. The tag is the mechanism; prose substitutes are what the tags exist to replace.

## Lens 3 — narration drift

Check what the doc causes Claude to *say to the user* against the communication rules in skill-nonspecific-rules.md. Three drift patterns:

- **Background vocabulary in user-facing narration** — a structural or bookkeeping term from skill-nonspecific-rules.md's Vocabulary list (loop, Step N, gate, pre-flight, slug, "processed/unprocessed captures," "staleness sweep," "hash backfill," and the rest) leaking into text the user reads. Background terms belong in the procedure prose Claude reads, never in narration to the user.
- **Menu where a recommendation was due** — the doc steering Claude to lay out flat options ("file it, drop it, or commit now?") at a moment it actually has a preference, instead of leading with the recommendation and offering the alternatives as fallback (skill-nonspecific-rules.md Dependency ownership narration; the spectrum-not-flat-list rule).
- **Multi-finding openings that should consolidate** — a doc that fires several scans, watches, or narrations at one skill opening without consolidating them into one narration. The rule is stated per skill, in that skill's own opening step: plan.md's read-state, next.md's pre-flight, done.md's close.

**Not a target: a purpose clause.** Where a sentence is welded into a rule's operative text because the rule cannot be applied correctly without it, that sentence *is* the rule, not rationale riding it. An eviction sweep must leave it alone. The test in reverse: delete it and read what remains — a complete instruction means it was rationale, an unfinished one means it was operative.

## Lens 4 — decision history in operative text

**The detector is the delete-and-read test, run sentence by sentence over operative text.** Delete the sentence and read what remains: a complete instruction means what was deleted was rationale or history, and it belongs in the record — the deciding LOG entry, or git history — not in the rule. An unfinished instruction means the sentence was operative and stays.

**Where the reasoning went, and how to check it arrived:** search `LOG/index*.md` for the rule's distinctive words and open the matched entry — the index line ends with its filename; where the index misses, `git log -S` over the rule's own shipped file finds the commit that added it, whose message names the session. Evicted rationale goes to that record, and an eviction is complete only when the reasoning is reachable there.

This lens catches **disguised rationale**: decision history written in the syntax of a rule — a dated "reinstated by the user's decision of…", a "was tried and retired on measured grounds", an alternative's defeat narrated inside the operative statement. The SPEC output-style paragraph found and rewritten on 2026-08-22 is the founding instance: it survived every earlier audit because the earlier lenses looked for rationale *clauses* riding rules, and this was history wearing a whole paragraph's worth of rule syntax. No "because" is required for a sentence to fail this lens — history is rationale whatever conjunction it travels under.

## Lens 5 — underived numbers

**Grep the corpus for digits, then read each hit that functions as a limit or threshold** — a cap, a count, a depth, a cadence. A hit passes only where its derivation is stated in the same or an adjacent sentence: a proportion of the thing governed, a figure from named research, or an externally imposed constraint.

Out of scope, because they state facts rather than limits: dates, version numbers, message ids, and worked examples.

**The limit-or-threshold call is this lens's one reading step**, stated as such so a turn is not mistaken for a mechanical pass. Each failure files one capture quoting the sentence and naming the file.

## Lens 6 — negatives

**Grep for sentence-leading prohibition forms** — "Never", "Do not", "Don't", "No &lt;x&gt; may" — and read each hit for whether the action wanted is stated anywhere in the same provision. A prohibition whose positive action sits beside it passes; one standing alone files a capture quoting it.

**Stated coverage limit:** sentence-leading forms only. Mid-sentence prohibitions — around 151 at the 2026-08-21 count, most of them legitimate — go unread, so a turn says what it covered rather than implying the corpus is clean.

## Lens 7 — contradictions

One lens, two steps.

**Parent–child.** For every subordinated unit — a nested bullet, an amendment naming its parent — read it against the parent's opening words. File a capture where the child is quietly wider or narrower than the rule it amends, or where it reads as a complete freestanding sentence. This is the gate's subordination test applied after the fact.

**In-document.** Within each file, read provisions sharing a subject, found by grepping the file for repeated key nouns. File a capture where two of them command different things for the same case.

**Stated limit:** the second step reaches provisions that share vocabulary. Two contradicting rules phrased with no common noun stay unread — the same limit the retrieve ladder documents for searches.

## Lens 8 — duplication

Covers what the mechanical near-duplicate matcher cannot see: **content stated at more than one site when one site owns it.**

**First, name the owner.** For each mechanism the turn meets — a rule, a check, a field, a limit — name its owning site: the one place its content is stated. Then read every other mention against that owner. A non-owner site carrying the mechanism's content is a finding; a non-owner site pointing at the owner is not. `method-map.md` maps documents, not mechanisms, so the owner is named per finding rather than read from a register, and the finding says which site it named as owner and why. Where the planning session confirms a multiplication or restatement as designed, its owner-map entry here records the confirmation with the date and the sites, and a later turn reads the mark and files nothing for those sites — the scrub-limit entry under the say-it-everywhere relationship below is the first instance; an artifact deliberately outside the sweep's list records its reason at the list.

Eight relationships produce restatement. Each carries its test.

**Across levels.** For each rule in the always-loaded files, ask which lower-level doc owns the same ground — the parent-axis method the 2026-08-22 style-dedup audits used — and file a capture where both state the rule rather than one stating and the other pointing.

**Within one file.** The merge rule's own test applies: two accounts of the same thing under different headings file as a merge candidate.

**Across siblings.** Where the same rule appears in two or more sibling documents, or a finding or report proposes it for another sibling, the finding proposes one rule at the lowest common parent, conditioned on what the copies differ by, and names every copy it repeals. The where-each-site-fires sentence is what separates this from the parallel-by-design case: copies guarding different moments that no single session reaches are two plugs, not one rule. The instance: the rests-on requirement lived in plan.md's decision step and in next.md, and a report proposed it for SPEC sentences as a third sibling; the always-loaded claim-about-the-world rule was the common parent, and one conditioned rule there replaced the copies.

**A pointer that restates.** A cross-reference sentence that carries the rule's content beside the pointer — "see X, which says that a capture is appended to the bottom of Unprocessed" — has stated the rule a second time under cover of pointing. The test: delete everything after the pointer's target and read what remains; where the sentence still points, what was deleted was a restatement.

**Prose beside a typed block or specimen.** A sentence saying what an adjacent block, table or specimen already shows — the block lists three states and the sentence says there are three states, named so. The test: cover the block and read the prose, then cover the prose and read the block; where either alone carries the content, the other is the restatement, and the block is the owner.

**Host versus shipped.** A rule in this project's CLAUDE.md that restates a rule the shipped docs carry, rather than pointing at the shipped rule and stating only the host-side difference. The test: does the CLAUDE.md passage say anything a consumer's session would not already read from the shipped file? Where the answer is only the host difference, the rest is a restatement.

**A limit restated under a "say it wherever this is described" instruction.** A caveat or coverage limit stated at every mention of its mechanism because the owning site instructs that it be — "state the limit whenever this comes up". Each mention is a restatement, and the finding names the instruction that multiplies it, so planning decides whether the multiplication is designed (the limit must travel with every description of the mechanism) or is copies to be replaced by pointers to one owner. The lens does not decide that; it names the instruction. Confirmed designed at planning on 2026-09-06: the scrub gate's limit (owner: the always-loaded "Scrub before writing, and state the limit") at its six sites — done.md's LOG-entry description, setup.md's keep-private and public-repository offers, feedback-and-inbox.md's report route, and SPEC.md twice — each being a moment a user could otherwise be told their artifacts are screened; a later turn reads this confirmation and does not re-file those sites.

**A drifted pointer.** A cross-reference whose target no longer says what the pointer claims — the target was reworded, moved or repealed and the pointer was not. Not a restatement but a defect found by the same read: the owner-map step opens every pointer's target, and this is what it finds when the target has moved. The test: open the target and read it against the pointer's claim about it.

**Stated limit:** the lens compares sites naming the same mechanism. A restatement paraphrased past shared vocabulary stays unread — the same residual the contradictions lens states.

**How a found restatement is taken out** is in [`rule-maintenance.md`](rule-maintenance.md) — codification, consolidation and recasting, and how a near-duplicate flag is resolved. This lens finds; that file removes.

## Lens 9 — turns

Each sweep turn extracts every tagged turn fresh by grep — the five response-shape tags are grep-able, so the extraction is exhaustive over the tagged set — and asks of each turn whether a content rule governs what the turn must *say*, not only its shape. A tag settles length and waiting; a turn a user acts on also needs its content settled, or the script decays silently as edits around it change what the turn carries. One capture per ungoverned turn worth governing, satisfied while an open capture carries it.

**Stated limit, by the turns inventory's own floor paragraph** (`workshop/resources/research/scripted-turns-inventory.md`): untagged turns are mechanically unreachable — nothing marks them, so no grep can enumerate them — which makes this lens a floor, recomputed fresh each turn rather than read from the stored map.

## The doubled communication rules — what this project's own narration cannot test

**Read this before treating anything about this project's narration as evidence the method works.** Three layers assert the method's communication rules in every session here, and only one of them is the method. Where a rule is doubled, no session can tell which layer it followed — so a rule that is weak, badly worded, or missing from `skill-nonspecific-rules.md` still produces correct behaviour in this project, supplied by a layer consumers do not have. The defect then ships and this project never sees it.

**Three layers, and the third is switched on in this project.** They are: **(G)** the user's global `~/.claude/CLAUDE.md`, loaded in every session on this machine and in every project; **(M)** the method's own `plugin/throughliner/docs/skill-nonspecific-rules.md`; and **(B)** the shipped output style `plugin/throughliner/output-styles/brevity.md`, named **Throughliner Brevity**, which asserts the method's communication shape at system-prompt priority. Only M and B ship; G is personal and reaches every project.

**B's rows are conditional, and the table marks them so.** The style is opt-in — offered at /setup and written into a project's own settings file with the user's consent — so a consumer project may not have it, and a row it covers is doubled *here* while being M working alone *there*. **This project has it enabled**: `.claude/settings.local.json` carries `"outputStyle": "Throughliner Brevity"`. So every `yes*` below is a layer this project's narration is being supplied by and a consumer's may not be.

**The retired style is history, not the current state.** `concise-throughliner.md` — a different file, auto-applied with no consent — was deleted on 2026-08-14 and its three unique rules migrated into M. B is the successor and is a distinct thing: opt-in, per project, consented. Reading the 2026-08-14 deletion as "there is no third layer now" is the error this section carried until 2026-08-31, and the 2026-08-29 compliance audit inherited it.

| Rule | G | M | B\* |
|---|---|---|---|
| One item per message when the next action depends on the last | yes | yes | yes\* |
| State the count upfront before a multi-part exchange | yes | yes | yes\* |
| Never preview later items | yes | yes | yes\* |
| Alternatives the user is choosing between are shown together | yes | yes | yes\* |
| Lead with the decision; don't front-load reasoning | yes | yes | yes\* |
| Skip recaps of what the user can already see | yes | — | yes\* |
| The single user-facing ask goes in bold, as a question, at the end | yes | yes | yes\* |
| Offer a web search rather than guessing at an external fact | yes | yes | — |
| Plain English for a non-coder; no unexplained jargon | yes | yes | yes\* |
| Gate detail behind an explicit request | — | yes | yes\* |
| How often to speak while working (narration cadence) | — | yes | yes\* |
| A written file's length matches what the task needs | — | yes | — |

\* Present only where the project has the Brevity style enabled. This one does.

**How to read it.** With B counted, **eleven of the twelve rows are asserted by two or more layers here**, so this project's behaviour on them is unattributable and its good behaviour on them is not evidence about M. **Exactly one row is M working alone**: a written file's length matching what the task needs. The web-search row is G and M with no B. The two rows that used to read as M-only — gating detail behind a request, and narration cadence — are not M working alone in this project, because B asserts both; they *are* M working alone in a consumer project that declined the style. The row that used to read as carried by nothing the method ships — skipping recaps — is now carried by B, conditionally.

**So this project tests M on one row of twelve.** That is the number to hold when anyone reaches for this project's narration as evidence. Testing the communication rules in a consumer project with the style declined and no global overrides is the real answer, and it is separate work.

**What was rejected, and why it is not reopened.** Stripping the duplicated rules out of G was refused: those instructions serve the user across every other project, and removing them to improve one project's test fidelity trades real everyday benefit for a diagnostic. Testing the communication rules in a consumer project without the global overrides is the real answer and is separate work. Making the overlap visible — this table — costs nothing and loses nothing, which is why it is what was built.

## Output

Findings to Captures, one per drifted spot — name the doc, the step or rule, the lens, **the moment each site fires**, and what drifted. No edits to the audited docs; the fixes get scoped in a later /plan that processes the findings.
