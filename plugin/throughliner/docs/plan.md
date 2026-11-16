---
name: plan
docset: current
note: The /plan procedure. An open planning session: the opening, then whatever the user or Claude raises.
---

# /plan

**/plan is an open planning session: it runs the opening and then takes up what the user or Claude raises.** The entry-by-entry pass over captures is /process. The building waits for /build. Claude owns the order work sits in and says why when it places something; the user owns whether an entry is kept or deleted.

**A planning session writes** QUEUE.md, SPEC.md, CYCLES.md, TOOLS.md, MAP.md, `LOG/`, the two FAQ templates, `workshop/resources/research/`, `workshop/resources/supplied/`, `temp/`, the scratchpad, the memory directory, the user's global instructions file, the slip list, and any path a checklist's `Writes:` field declares. Any other change is work, and is queued. Where the safety check refuses a write, say what you were about to change and file it as a capture. Where the user asks again for the same change in their own words, write `_freeform-<session-id>.md` in the project root with a `Files:` section naming that one path, make the edit, and let /close record it as handmade work.

**Write to the queue first, then report what landed.** The user can reject what was written and have it reverted.

## Step 1: Open

**Run the opening at `${CLAUDE_PLUGIN_ROOT}/docs/opening.md`**, read to its end. It closes on "Anything you want to raise?" and waits.

## Step 2: The open session

**Anything the user or Claude raises is taken into the interview in the reply that meets it**, and written once the user agrees what would be written: as a kept item, by the steps `${CLAUDE_PLUGIN_ROOT}/docs/process.md` gives for each entry (Recommend, Execute with its settle-who and place-it parts, Checkpoint's re-read of the headings), or as a capture. Its disposition goes in a later message than the one that introduced it. A capture already in the queue is taken up on the user's ask, by the same steps; no capture is offered unasked. A cycle or checklist the user asks for is authored as process.md's "Cycles and checklists" paragraph says.

## Ending the session

**The session ends on the user's word.** Say what is cleared by kind from the digest ("N builds, N audits and N steps of yours") and which entries filed this session bear on cleared work, then:

> Two commands close a session. Send the rescan command first if you want a check that nothing said here was left out of the files. Then send the close command, which records the session and commits it. Sending close on its own runs the same check.
>
> **Is there anything else to capture or discuss first?**

Where rescan already ran, the paragraph is "One command closes the session now: send the close command, which records the session and commits it." Where the user says, in any words, to keep the chat open for capturing, write the keep-open marker with the state server's `keep_open_mark` tool, then stop asking.
