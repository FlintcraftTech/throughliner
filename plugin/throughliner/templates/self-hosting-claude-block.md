<!-- THROUGHLINER SELF-HOSTING BLOCK — START -->
## Authoring rules your own sessions will follow

You are building something whose output is instructions — a method, a plugin, a port, a house style. That makes your own rule text a thing you maintain, and it has a failure mode ordinary work does not: **every rule you add degrades the rules already there.** Irrelevant and near-identical rules are optimal distractors for one another, so the cost of a new rule is paid in relevance, not in word count. No ceiling is stated here and none should be invented — a bare number nobody can derive is a number nobody dares change.

### The rule gate — run this before adding any rule to your own text

Four parts, in use order: admission, eviction, distribution, wording.

**1. Admission — does this rule get to exist?**

**First, name the parent: which existing rule does this amend?** An amendment competes with nothing; a freestanding rule competes with everything. A change that cannot name a parent is either new territory or, far more often, a refinement whose parent was never looked for. — and grep the sibling documents for the rule before writing it; where a sibling already carries it, the rule lifts to their common parent, conditioned on what the copies differ by, and those copies are what the eviction step names.

**Then write it as a subordinate unit of that parent, and ship it in that form if it holds.** Freestanding is the fallback, not the default. It is genuinely subordinate when all of these hold: at least two parallel units exist; each reads as a continuation of the parent's opening words; all share one grammatical function; every modifier points only at the opening words or at its own unit; none is a complete sentence. A complete sentence formatted as a nested bullet is a freestanding rule wearing a bullet, and spends a slot accordingly.

Then four questions:

1. Has this actually failed, in a way you can point to? A speculative rule
   stops here.
2. Does the model already do it unprompted?
3. Does it apply to every session, or only some?
4. Could something mechanical do it instead, at no attention cost? Escalate to
   a mechanism when the failure's cost justifies its standing friction — a
   cheap, self-correcting slip earns sharper wording instead.

**A limit your text declares states what it was derived from.** A proportion of the thing it governs, a figure from research, or an externally imposed constraint each qualify; a bare number does not. A stated derivation makes a limit traceable and revisable — it does not make it correct.

**An exception must survive the restatement test.** Before writing one, restate the rule so that it does not need one; an exception is admissible only where restatement was attempted and lost content. Where restatement genuinely fails, the exception requires a recorded instance of the bare rule producing a wrong outcome — not your belief that an edge case exists.

**2. Eviction — name what comes out.** Adding a rule names which rule it replaces or supersedes, and repeals it in the same move. A clearer restatement that leaves the old statement standing has doubled the text, not merged it. **Retiring a step retires the artifacts that step produced — name them and delete them in the same change**, and where a live doc describes the retired step's output, reword that too.

**3. Distribution — always-loaded, or fetched?** A session cannot fetch a rule it has never read, so a rule that must shape behaviour unprompted is always-loaded and pays the full admission cost. Reference material a session knows to go looking for can be fetched. Name your always-loaded file and make its name the admission test: a rule belongs there only if it fires everywhere, or in conversation with nothing running.

**4. Wording — state the action the rule requires.** Anything described in terms of what *not* to do means the rule of what TO do was never adequately described; a prohibition is a signal to go back and specify the action. Express a qualification as structure, not explanation: state the rule bare with the qualification in structure; main clause first, conditions after; multiple exceptions in their own subsection; short connectives (but, except that, unless, so long as) rather than explanations; one idea per provision; every exception at the same level as the rule it qualifies.

**Rationale lives outside the operative rule.** The operative statement stays bare. Why a rule is worded as it is — which alternative lost, what the trade-off was — goes to the session record that decided it. Decision history counts as rationale: a date, a "was tried and retired", an alternative's defeat narrated in rule syntax.

**Where a reason is needed to apply the rule, reclassify it — don't exempt it.** If a rule cannot be applied correctly without a sentence, that sentence is part of the rule and is written as operative text. The test, in reverse: **delete the sentence and read what remains — a complete instruction means what you deleted was rationale, an unfinished one means it was operative.**

### The disposition rides the queue item

**Write the gate's decision onto the queue item, at the planning step where the item is kept — not later.** A disposition written after the work is built can only describe what already exists; it has no power to refuse, because refusing would mean undoing finished work. Only planning can refuse, because at planning nothing has been built and refusing costs a conversation.

**A build transcribes the disposition it finds and never composes one.** Where a build finds itself authoring a rule and the item carries no disposition, it halts and says so.

**A session that authored or amended a rule in your own text cannot close until its session record carries a gate line** — what the gate decided, or that it was not needed and why:

```
Rule gate: run — <what it decided>
Rule gate: not needed — <why>
Retired: `<term>` — <what it was>     # only when this session retired something
```

Write the label plain, not bolded. "Not needed because X" is a claim a later reader can disagree with, and a missing line is a gap anyone can see.

**The honest limit, and state it wherever this is described: nothing can tell an honest disposition from a dishonest one.** A planning-sited gate can refuse, which a build-sited or close-sited one cannot. That is the whole gain. Do not describe it as making the gate trustworthy.

### Host and target

**Host** = your method as installed and running. **Target** = the editable source you are changing. They are the same thing at different stages, and a target change has no effect until it is packaged and installed as the new host.

**Ambiguous references must say which.** "The rules", "the hooks", "the procedure" — each names two different things, and a session that conflates them will test a change against code that does not contain it. Default assumption: discussion is about the target unless said otherwise.

**Verify a change by driving the new code directly, never by performing the guarded action for real.** Performing it exercises the *installed host*, which is the old code, so the guard never fires and the action completes. A write made to watch a guard refuse it is byte-for-byte a write meant to succeed — which is why nothing mechanical can separate them, and why the safe test and the destructive one look identical from the inside.

**A decided-but-unshipped rule is in force from the moment it is decided.** Your sessions read your queue and your records, not only the installed copy. "Not shipped yet" is never a reason to suspend decided reasoning.
<!-- THROUGHLINER SELF-HOSTING BLOCK — END -->
