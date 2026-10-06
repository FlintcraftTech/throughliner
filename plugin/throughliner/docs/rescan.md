---
name: rescan
docset: current
note: The /rescan procedure. Looks back over the chat for anything decided, noticed or asked for that was never written to a file, and files it. Commits nothing.
---

# /rescan

**/rescan looks back over the chat for things decided, noticed or asked for that never reached a file, and files them by the three-way triage**: work still to do becomes a capture in Unprocessed; what already happened is appended to this chat's LOG entry as a marked tail; evidence a future chat must re-read verbatim goes under `workshop/resources/`. It files and stops there: routing (keep or delete) is /plan's, building is /build's, and the tail rides the next /close's commit. It can run as often as wanted.

**Scan back only as far as the last /rescan in this chat**, or the whole conversation on the first run; where the conversation has been summarised, use the captures filed earlier today as the boundary. First say one sentence on what the files prove ran that is no longer in view (a queue diff for a planning run, a working file's ticks for a build run); the sentence makes no claim that nothing was lost.

**Work still to do.** Show the candidate set as one numbered message before anything is written, ending with what each answer does: "Say go to file it, or say no" for one, "Say go to file both, or contest by number" for two, "Say go to file them all, or contest by number" for more. Then write them as captures, appended to the bottom of Unprocessed. Where /plan was invoked earlier in this chat, the same message offers to process the surfaced items with the user now, one at a time, through plan.md's interview, with Claude's call per item in one clause: process now where it bears on cleared work, settles in one turn, or touches a queued entry; file for later otherwise. An item answered "process now" is written once, as a work item, after the interview.

**What already happened.** Append to this chat's LOG entry, with the state server's `append_tail` tool, under:

```
## After /close

<what was done, and why>
```

Where this chat has no LOG entry yet, say that /close will record it and file only the captures. A candidate that is both gets both halves. Nothing found takes one line: "Read back over our discussion — nothing came up that isn't already captured."

**Then hand back.** Say what was filed, that running /close is what records and commits it, and put the resumed work's own pending question back in bold as the last line; where nothing was running, the last line is that sending the close command records the session. Where the user said something outcome-shaped that no goal in SPEC names, propose it as a goal in one line in their words, written on their yes. That is the whole hand-back.
