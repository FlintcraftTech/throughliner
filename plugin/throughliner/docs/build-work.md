---
name: build-work
docset: current
note: How one build item is built, and how an [audit] item is run. Reached from build.md.
---

# Building one item

The item's own text in QUEUE.md, read whole, is the instruction: which files change, what changes inside them, the observation that shows it landed, and any option already refused. Read the reasoning to aim the work, and write the action, not the reasoning, into the files the build edits. A recorded refusal is settled; do not propose it again.

```
1. search SPEC.md and QUEUE.md for the item's heading's distinctive words before the first edit,
   noting the hits for the tick's Bears on field; a hit that contradicts the item fires step 4
2. make the changes, with no preview
3. readable content: link the edited file and name the line, after the write; code: say nothing
4. check the work against SPEC
5. tick it in whichever form is true
```

**The tick:** `done, confirmed` where something ran and passed (a suite, a command, a read-back, an inspection); `done, UNCONFIRMED: <what still needs running>` otherwise. A check Claude can run is part of building. Read a command's exit status from the tool itself, not from a pipe's last stage. A check Claude can run but a circumstance of the moment blocks stays outstanding in the working file and is retried before /close.

**The SPEC check:** where the built work agrees, say nothing and tick. Where it contradicts a SPEC sentence, stop, name the sentence in plain words, and let the user decide whether the build or SPEC is wrong. Where the build establishes product truth SPEC does not yet carry, file the sentence SPEC owes as a capture naming this item's slug, say so in one line, and carry on. The build never edits SPEC.

**A small tweak the user asks for after seeing a readable edit** is in scope: make it, link the updated text, record it in `Changes:`. Anything that is new scope routes below.

**Before assuming a tool or device is absent, read `TOOLS.md`**, then ask whether the user has a route to it. A tool failing from Claude's shell shows only that Claude cannot run it. Write a newly learned environment fact into `TOOLS.md` in the moment, one line per fact; it is writable whatever the scope says. Ask before connecting to the user's physical device or external hardware.

## Scope

Stay within the item's described work. Where the user raises something out of scope: file it as a capture, report in one line what was filed and why it is captured rather than done now, ask "anything else?", and resume. On a second ask for the same thing, carry a minor change through, appending any unlisted file to the working file's `Files:` before editing it, and still propose a split for a significant one. A queue move the user directs is done with the mover and narrated in one line; an inferred move is never made or offered.

Where the build itself finds it needs more: for a minor addition, recommend adding it and ask ("This needs [work], which means editing [file]. Add it?"), appending the file to `Files:` on the yes; for a significant one, recommend finishing what is scoped, closing, and planning the rest. A discovery only the user can act on is filed as a `[user]` capture with a rough walkthrough, never floated as a question. A user-runnable check the build turns out to need is filed the same way.

## Stuck

Stop where the same error recurs, an edit changes nothing, or an attempt fails the way a different attempt already failed. Say plainly what repeated, propose a path, and wait: adjust scope (drop the item, add a prerequisite, change approach, and update the working file), or abort and requeue (return the item to Processed with the mover, file any captures and the reshape direction naming its slug, and tell the user to run /close). The working file stays in place either way.

Where the user reports the session degrading, finish and close if most of the run is ticked, or close partial and requeue the rest, and offer a fresh-session handoff.

## Completion

When every Claude-work item is ticked and every `[user]` item walked, say the build is complete, that nothing is recorded yet, and that done work can be tightened before closing. Where a held item bounded the run and the run shipped its blocker, say in product terms what is not yet on screen. Name /close in words mid-sentence, and leave the working file in place for it.

# Running an `[audit]` item

An audit reads and reports. Findings go to Unprocessed as captures, and the audit edits nothing it reads. Where the item directs a write into a named document, stop and say so before reading: an audit files captures so the user can weigh them first, and the user can have it run as a build instead.

Read every artifact the item names, one criterion across the whole target at a time, accumulating observations with `file:line` references in a scratch file. Compile one finding per discrete observation, phrased as what was observed and why it matters. Whether a finding is worth acting on is decided at /plan, not here. Append every finding to Unprocessed, each carrying the line "from the <name> audit, not yet reviewed", tick each as `captured` in the working file (or `dropped` where Claude's own re-read shows it wrong), and say in one line how many were filed. Nothing waits for approval.
