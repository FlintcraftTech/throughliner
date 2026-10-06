---
name: migrate-checklist
docset: current
note: Loaded from setup.md when a project's documents are on an older format than the plugin expects. A guided pass with approval before each write.
---

# Format migration checklist

**Run every epoch section from the project's recorded epoch up to the current `FORMAT_EPOCH`, in order.** A project with no marker starts at the beginning. Say "your queue" to the user; the structural terms here are for Claude to read.

```
1. read the existing QUEUE.md and identify each old section and item
2. convert each item by the rules of each epoch section you are running
3. draft the whole converted queue and show it for approval before writing;
   the project may have been adopted moments ago and have no history to recover from
4. after writing, the queue lint confirms the new queue is well-formed
5. setup writes the new epoch marker last, once the conversions have landed
```

## Epochs 1 to 3: the two-section queue

**The old sections (`## Red flags`, `## Batches`, `### Parked`, `## Deferred tests`, `## Captures`) collapse into `## Processed` and `## Unprocessed`**, with `--- Cleared to run above this line ---` inside Processed separating what is cleared from what is not. Each item becomes a `#### ` heading with a kebab-case `[slug]` at its end, rationale prose beneath, "captured by you" where the user clearly raised it, and `Red flag · State: cleared | uncleared` only where it carries a risk. Re-copy the section preambles from setup.md's scaffold.

**Judgment a find-and-replace cannot make:** an old red flag with work remaining becomes a marked work item, a done one goes to LOG, a bare line is left alone; batch, parked and deferred-test items become work items placed by judgment, vetted and ready into Processed, still needing thought into Unprocessed, a deferred test only the user can run into a `[user]` item with a walkthrough. Method boilerplate (queue preambles, the CLAUDE.md template block) is re-copied from the current template; a `FAQ/` folder an earlier version copied in is a retired artifact, named and left to the user. Empty old placeholders disappear.

## Epoch 4: cleared work says what it changes

**Nothing is reformatted.** A cleared item whose prose already says what changes and where needs nothing. One that does not never passed the decision step: move it below the readiness line for the next /plan. An old delimited build block is left as it is. Any block the migration does write under an existing item, with the user, gets one more line: `Build block written by the format migration on YYYY-MM-DD, not yet checked at planning`. Check it landed by running the queue digest and reading each cleared item's line.

## Epoch 5: `workshop/`, and `resources/` moves inside it

**Look inside `resources/` before moving anything**; a project may keep product data there. Move `resources/research/` and `resources/testing/` to `workshop/resources/research/` and `workshop/resources/testing/`, keeping relative paths, with `git mv` in a tracked project. List anything else found there and put the split to the user. With no `resources/`, create `workshop/resources/research/` empty. Then re-point any instruction (the project's CLAUDE.md, a queue item) that names the old path, leaving records alone.

## Epoch 6: the LOG index is generated from each record's summary field

**Each record now carries a front-matter block** (`---`, `summary: <the index line's text after the hash>`, `---`) above its `# <hash> — …` heading, and the close regenerates the index files from those fields. Show the user first that every record gains three lines at its top and the index files are rewritten, and where the records are untracked say the previous index is not recoverable; then run once:

```
python <plugin-root>/scripts/log_backlinks.py <project root> --backfill-summaries
```

Afterwards compare the regenerated `LOG/index.md` with the previous one and name any line that differs.

## At every epoch

**Prefix a plain-prose preamble under `## Processed` or `## Unprocessed` with `> `, wording untouched**; the lint otherwise reads it as an orphaned rationale. Keep everything the user wants kept: each item's rationale carried whole, old "captured by you" signals kept, old "by Claude" labels dropped, every red-flag risk kept as a marked item. When unsure whether something is the user's own work or boilerplate, ask.
