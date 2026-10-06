---
name: recovery
docset: current
note: Reference for after a large rollback. Read when the user asks to undo a lot of work at once, or when a session opens into the aftermath of one.
---

# After a big rollback

**The queue will keep asking for work that is already done.** A rollback restores the files and leaves the correspondence between the queue and reality broken: work that shipped before the rollback point stays shipped, and the queue items describing it come back as ordinary ready work. Before building anything in the first sessions after a rollback, search LOG for the item's slug; where the work shipped, remove the item and say so. Shipped work survives in its LOG entry alone; unbuilt work lives in the queue alone.

**Restore first, diagnose second.** Bring back immediately everything that could not have caused the problem: tests, research notes, records, tooling.

**Check what depended on this project.** Another project or a published format built against it may now be broken without saying so. This is the one time-critical item.

**A rollback undoes deletions too.** A retired setting comes back, a deleted file returns. Read the changes in both directions. Restoring an old state by checking out an old file list leaves orphaned files on disk, and renamed files do not show as deletions.

**The LOG index is the instrument.** Decide which entries to open from the one-line summaries, and check dates against the history rather than the index.

**Verify with checks that can fail:** compare the restored state against the target (no difference), measure what prompted the rollback (the expected number), compare content stamps where a tool loads these files, and run the thing that was broken. A restored file is not a restored behaviour.
