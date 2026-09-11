---
name: rescan
docset: current
note: >
  /rescan procedure. Split out of done.md's wind-down re-scan on 2026-08-15 so
  the step has its own trigger and can run repeatedly in one chat.
  Register: structure in typed blocks, everything else in prose, tags inline.
---

# /rescan procedure

/rescan exists because a conversation ends and takes everything unwritten with
it — filing is how a decision outlives the chat that made it. Look back over
the conversation for things decided, noticed or asked for that
were never written into a file, and file them.

## What it does, and the one thing it does not

**Route what it finds by the standard three-way triage**, rather than filing
everything as a capture:

```
reveals work still to do          ->  a capture in QUEUE.md Unprocessed
what already HAPPENED             ->  appended to THIS chat's LOG entry, as a
    — including work done after       marked tail
    /done
evidence a future chat must       ->  a durable file under workshop/resources/
    re-read word for word
```

```
/rescan  ->  FILES what it finds, by that triage
         ->  never ROUTES it (keep / delete / where it sits)
         ->  never BUILDS it
         ->  never COMMITS. The tail rides the next /done run's commit.
```

**The tail is what makes this the one-word route for post-close work**, which is
common and otherwise has to be asked for in prose every time. Mark it as a tail
rather than blending it in, so what was recorded at /done stays visible as
what /done recorded.

Filing is capture-making and is open to every skill. Routing and building are
/plan's and /next's, and this skill stays on the filing side of that line.

**It does not build, and the reason is worth keeping.** The complaint that
produced this skill is a real one: a finding about the machinery being used right
now waits for a /plan to process it, a /next to build it, and a reinstall before
it is live. Building on the spot would not answer that, because the installed
plugin is a frozen copy — a fix made now does not reach the chat that made it
until the plugin is reinstalled and the app restarted. And a skill that could
route and build would let any chat change the project without the user having
agreed to the work.

## Step 1: Find the stopping point  [SILENT]

Scan back only as far as the last /rescan in this chat, not to the beginning.
That is what lets the skill run several times in one chat without re-surfacing
what it already surfaced.

```
/rescan already ran in this chat  ->  scan back to where it stopped
first /rescan of the chat         ->  scan the whole conversation
can't tell (the conversation      ->  read the captures filed earlier today and
  has been summarised)                use those as the boundary
```

**The stopping point is held in the conversation, and nothing is written to a
file for it.** Where the conversation has
been summarised the memory of it is gone, so the fallback is the captures
already filed. A stretch that yielded nothing yields nothing again, so the cost
of re-reading it is re-reading, not duplicate items.

**Run the memory-limit machinery as done.md's wind-down re-scan states it —
that section is the canonical copy, and this skill applies it at this scan's
own depth.** It carries the runs-in-view check — which runs the files prove
happened, read against the runs still visible in the conversation — the one
sentence that reports what the check found, the asymmetry that keeps that
sentence from ever adding an all-clear, and the no-proxy rule. Read them there
and apply them here — the one difference is depth: this scan reaches back to
the stopping point above, which on a first run is the whole conversation.

## Step 2: File what you find  [BRIEF]

**Sort each candidate by the triage above before writing anything** — work still
to do, or something that already happened. Both get written; they go to different
files.

**Work still to do → Unprocessed** [PROMPT]. Show the candidate set as ONE
numbered message before anything is written, and wait. **End it with what each
answer does: "Say go to file them all, or contest by number."** A contested item
is then dropped or reworked one at a time.
**What happens then depends on the answer:**

```
answered FILE          ->  the capture is written, exactly as now
answered PROCESS NOW   ->  NOTHING is written. The item enters the planning
                           loop and is written once, as a work item, after
                           the interview — plan.md's process-now rule
```

  Writing a capture first and then processing it spends a write that is thrown
  away, and process-now is the common answer. The offer below is what asks.

Placement is the standing one — appended to the bottom of Unprocessed, no
judgment, no narration of the mechanics.

**Where /plan was invoked earlier in this chat, the same message also offers to
process the surfaced items with you now, one at a time** — entering plan.md's
ordinary present-and-interview loop on the user's yes. The offer says "with
you": processing is done together, and wording it as something Claude does alone
primes the user for the wrong interaction. In any other chat the offer is not
made and this skill files only.

**What already happened → this chat's LOG entry, as a marked tail.** Append rather
than rewrite, under a heading that says what it is:

```
## After /done

<what was done, and why — the same authoring standard as the entry above it>
```

**Where this chat has no LOG entry yet**, there is nothing to append to: the work
is recorded by /done when it runs, so say that and file only the captures.

Say so when reporting that nothing is committed here, so the user is not left
thinking the record is saved. A second
`/done` typed in a chat that has already closed reaches this same tail rather
than a second /done run — done.md's router carries that arm.

**Where a candidate is genuinely both** — work that was done AND revealed more to
do — write both, each carrying its own half: the tail records what happened, the
capture records what is left.

**State the limit sentence and the files-disagree wording as done.md's
wind-down re-scan gives them** — canonical there, applied here, per Step 1's
reference.

**Nothing found is a result, and it takes one line.**

> Read back over our discussion — nothing came up that isn't already captured.

## Step 3: Say what happens next, then hand back  [BRIEF]

Name what the captures are waiting for — **the planning run this chat is in,
where one is running, and otherwise the next one.** Processing a capture is
exactly what /plan does, so a session still open can settle what was just filed.
Say it once, plainly.

**Then resume whatever was running and carry on from where it was.** A scan run
inside a build or a planning run interrupts that work and returns it; the
hand-back is a return, not a /done run, and nothing has to be restarted — the skill's
instructions are still in the conversation.

**Content line for the hand-back turn — three things, in this order:** what was
filed, named; that running /done — named in words — is what records and commits
it; and the resumed work's own pending question, put back in bold as the
message's last line, so the message ends on the ask the user was in the middle
of. Where nothing was running, or the run has finished and not closed — the hand-back to the /done step —
the third part is running /done, named in words and clear of the sentence's
end, in bold as the last line, since that step is the pending one.

**Recommend nothing else.** This skill exists partly because close machinery
accumulating at the end of a chat pulls the whole chat toward ending. A /rescan
that finishes by suggesting /done would rebuild that pull at a new site.
Naming the command that commits the captures is a fact about where they go,
stated the way /done's own Recommend-next turn states its continuations,
and is not a recommendation.
