---
name: build
docset: current
note: The /build procedure. The run builds the cleared work top-down, walks the user through their own items, and is closed by /close.
---

# /build

/build executes what the user already agreed at /plan, as agreed, so it does not stop to confirm each item. It reads SPEC and the queue's cleared region whole, builds the Claude-work items top-down, pauses at each `[user]` item to walk the user through it live and at each `[co-write]` item to work it with them, halts on a `[freeform]` item, and sits uncommitted until the user runs /close. It is scope-locked to the files the work names.

```
run     = Processed, from the top down to `--- Cleared to run above this line ---`
(no tag)    build        build-work.md
[audit]     read, report build-work.md's audit section
[user]      walk through live, never built
[co-write]  work with the user on its one file, then carry on
[freeform]  halt; it needs a session of its own
```

A `Runs alone` line is the run's second bound: where the run has already built something, end before that item; where it is the run's first item, build it and end after it; where its observable check finds it already done, close it and continue. Say why the run ended and how many cleared items it did not reach, then recommend /close.

## Step 1: Pre-flight

Everything these checks find folds into one narration, delivered with the run at step 4.

1. **Active build.** Where this session's own `_build-<session-id>.md` exists, offer to resume and read it for state. Another session's file is not this session's scope. Before creating any file at the project root, check the opening's untracked list: an untracked file has no git copy, and overwriting it destroys the only version.
2. **Read SPEC once**, then the `LOG/index.md` lines newer than the most recent build record (the one carrying a `Files touched` field), opening an entry only where an item's instructions are unclear, then the cleared region top-down, each item whole. A build carrying an `Assigned to:` line naming someone other than the person whose session this is skipped, said in one clause. Then:
   - Processed is empty above the marker: tell the user the next work is not cleared yet, recommend /plan, stop.
   - An item carries `Red flag · State: uncleared`: stop before it, name the risk plainly, recommend /plan to clear it, wait.
   - The top item is `[freeform]`: say what it is and that it needs a session of its own, stop.
   - The run has no build or `[audit]` item: skip step 2 and go to the walk-through branch.
3. **Mail and cycles.** Where the opening names waiting mail, triage it as `${CLAUDE_PLUGIN_ROOT}/docs/feedback-and-inbox.md` states before presenting the run: anything it raises becomes a capture, and a message bearing on a cleared item is named at step 4 with a recommendation to drop that item from this run only. Run the cycles check as plan.md's opening states it, filing only.
4. **Present the run and offer the off-ramp, in one message.** A one-line pointer naming the items, linked to QUEUE.md, counts read off the digest. The whole cleared region is the run; no cap is proposed. Two things may drop an item from this run only, the queue untouched: waiting mail bearing on it, and a /setup outstanding (the opening reports the format epoch behind, or a missing document) where the item names a file /setup rewrites from a template. End with **"Say go and I'll start, or say the word to change scope or reorder first."** A change routes to /plan.

## Step 2: Lock scope

Read each Claude-work item whole and list the files its instructions name. An item that does not say what changes inside the files it names halts as underspecified; do not invent scope. Other work noticed along the way is a capture, filed and continued past. `[audit]` items name no files; a run of only audits gets an empty list.

Create `_build-<session-id>.md` in the project root with the state server's `build_open` tool, or by hand in this exact shape:

````markdown
# Active Build

Run: [flavor + slug of each Claude-work item, top-down]

Entries:
[one line per Claude-work item: flavor tag or "build", slug, description; no rationale]

Index entry candidates:
[empty — one added as each item is ticked]

Run-level:
[writes belonging to the run rather than any item, one line each, at the moment of the write]

Files:
- [each file the run's items will change — one bare path per line, nothing else]

Progress:
[empty — ticked as each item completes]

Changes:
[empty — accumulated as each item completes]
````

The `Files:` section feeds the safety check, which matches each line as an exact path: bare paths only, one per `- ` bullet, every file named, no folder lines, and no other line starting `Files:`. QUEUE.md is left alone; items are copied, never cut. Say in one sentence what the file is for: it lists the files the check allows, tracks progress so an interrupted session can resume, and holds what /close writes into the record.

## Step 3: Work the run

Build every Claude-work item that depends on no `[user]` item first; then, in queue order, walk each `[user]` item whose prose names builds by slug and build the ones it names; then walk the rest. Between items, keep going; the run was confirmed at the off-ramp.

**As each item completes**, write six things in the working file and remove the item from the queue, with `build_tick` where the server is registered, which refuses a missing verdict, a full depth with no trigger, or an empty bears-on or SPEC-check field, and otherwise by hand:

```
- [x] <item description> — done, confirmed
- [x] <item description> — done, UNCONFIRMED: <what still needs running>
Depth: <slug> — short
Depth: <slug> — full, <reasoning contested | alternative seriously weighed>
Bears on: <slug> — <SPEC and queue hits for the item's distinctive words, found before the first edit>
SPEC check: <slug> — <agrees | contradicts: which sentence | owes: the sentence filed>
```

plus the item's index-entry candidate (artifact touched and nature of change) and its `Changes:` lines, one file each. Where the item carries a `Rule gate:` line, copy it across unchanged as `Rule gate: <slug> — …`; where it is about to author a standing rule and carries none, halt. Then remove the item:

```
python <plugin-root>/scripts/reorder_queue.py <QUEUE.md path> --delete <slug> Processed
```

Tick first, then remove, so an interruption leaves the item visible in both files. A capture filed mid-run gets a line in `Run-level:` at the moment of the write.

### Walk-through branch: the `[user]` items

Once the Claude-work is built, walk the user through each `[user]` item still in the cleared region, from the item's own walkthrough in QUEUE.md; where an item carries none, halt on it. Walking does not end the run.

First, in one short message, name the items that cannot move this session, one line each with why: a task-shaped item (one carrying a task line instead of a walkthrough) is on the user's list and completes when they tick it; an item whose record shows it handed over after a /close with no observable to check is not marked done, with what waits on it named by slug; an item whose first step needs something not yet there is blocked on that thing. Record each under the outcome block below. No ask.

Then each item that can move gets its own turn, saying how many items wait on it where any do. Open its LOG entry under its slug, append each action as it happens, write one `Run-level:` line, and append every path on the item's Files line to the working file's `Files:` section, saying so in one clause. A step that has the user edit text Claude drafted writes the draft to the file the item names, hands it over as a relative link that opens it in the side panel, offering in the same breath to display it inline or send the file, waits, reads it back only when they say to, asks whether there is anything else, and repeats until they say they are finished; a `[co-write]` item's whole walkthrough is this loop on its one file, and where the text is the user's, Claude reads and responds on their word. Before a step goes out: name the tool that would do that step instead and confirm it is absent, perform every part Claude can, check that a named file still has the property the step needs, verify any command the user will paste by running it safely or reading its help, and read the words back as a no-code developer would. Give the first concrete step, what to do and what to look for, and **wait**. Then the next. Where the step's reasoning is already on record, the step is the ask alone. Say nothing about /close until the item is finished or left. Where the user leaves one step, each later hand-over leads with leaving as the recommendation: "Leave this one too?", saying that sending close leaves it and ends the session. A step requiring action in another project is filed as a capture, never driven. Where the item carries `Assigned to:`, address that person, and take "not mine, it is <name>'s" from anyone present, rewriting the line with `hold_entry`'s `assigned_to` field or the queue tool's `--assign`.

Where the user volunteers that an item is done, take their word and recommend /close. Where the walkthrough names an observable check, run it and report a failure as what was found.

Every `[user]` item the run touched ends on a recorded outcome:

```
done          walked to its end, or the user said so, or its observable check passed
deferred      the user said to leave it, their word quoted, never inferred
not reached   never presented, or presented with no answer
anything else what actually happened, in one plain sentence
```

Once an item is complete or deferred, say how it closes: running /close logs it under its slug and removes it from the queue, or the user mentions it at the next /plan. When every item is walked or deferred, say the run is complete and that the close command, named in words mid-sentence, records it.

## Ending before scope lock

Where the run ends before scope was locked, file any reshape direction from the conversation as a capture naming the item's slug, then name /close as the next step. No item returns to the queue, because none left it.

## Resuming

Read the working file for state rather than re-exploring. A working file left by a session that never came back is surfaced at the opening as a leftover and never deleted; it may hold the only record of what that session did.
