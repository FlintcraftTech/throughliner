# Compliance audit checklist

The standing criteria for a periodic sweep of your own rule text — the files your sessions actually load.

**How this differs from the rule gate.** The gate is a per-rule check run once, at authoring time, before a rule ships. This is the corpus-wide sweep: you run it over rules that already shipped, to catch what drifted or was never checked. An authoring-time check never re-examines old rules, so without a periodic sweep a rule written before a standard existed is never held to it.

**Scope it as a delta: the rule files changed since the last audit.** A corpus-wide pass is its own separate piece of work, done once. After that the delta is the unit, and it is what keeps each audit small enough to actually run.

**Findings become captures, not edits.** An audit reads and reports. Each finding goes to your queue for a planning session to weigh, carrying a line saying it is unreviewed audit output.

## State the axis before you start, and it is the parent axis

**Compare a doc against its parent, never against its sibling.** A child doc is loaded *with* its parent, so a child restating what its parent already carries is genuine duplication — the reader has both. Two siblings saying the same thing are not duplicating anything, because no session ever loads both, and "consolidating" them produces a rule neither reader needed in full.

Say which axis you are running on before the first read. If it is not the parent axis, argue for the one you chose.

## The four lenses

Run all four over each doc in scope. One read serves all four.

**1. Self-authoring compliance.** Hold each rule to the gate it should have passed. Does it name a parent, or stand freestanding for no reason? Is it stated as an action rather than a prohibition? Does it declare a limit with no stated derivation? Look especially for **eviction debt** — a rule that restates or supersedes an earlier one without repealing it, so both stand.

**2. Response-shape placement.** Where your method has tags, markers or shape conventions governing how a step behaves, check each step carries the one it needs — and that a step whose shape depends on what it finds tags every arm. The failure to look for is **prose where a marker belongs**: a step describing in sentences the behaviour a marker exists to declare.

**3. Narration drift.** Read every specimen — the example outputs a session copies. A specimen is stronger than a rule, because it is what gets imitated. Two drifts to catch: a specimen using vocabulary the rules tell sessions to translate away, and **a flat menu where a recommendation was due**, handing the reader a choice the doc itself has already taken a position on.

**4. Decision history in operative text.** Apply the delete-and-read test to any passage that narrates why something is the way it is: delete it and read what remains. A complete instruction means what you deleted was history, and history belongs in the record. An unfinished one means it was operative and stays.

Two traps here. A **purpose clause** — a sentence a rule cannot be applied correctly without — passes the test legitimately; do not evict it. And history addressed to a *future author of the method* is in the wrong document rather than merely surplus: it belongs wherever your own maintenance notes live, not in text that ships to people who never author rules.

## Closing an audit

Record the audit in your session log under its own name, listing every doc read and every finding filed — including the docs that produced nothing. A doc that was read and came back clean is a fact worth having; a doc missing from the list is indistinguishable from one nobody looked at.
