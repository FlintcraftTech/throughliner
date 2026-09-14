---
name: catchup
docset: current
note: >
  /catchup procedure. A returning user's brief: where each feature stands,
  read mechanically off SPEC, the queue and the record's recent index lines.
  Register: structure in typed blocks, everything else in prose, tags inline.
---

# /catchup procedure

/catchup is for a user coming back to the project after time away. It says
where the project's important features stand, in a few lines, and does
nothing else: **it files nothing, moves nothing and writes nothing.** The brief
is chat only.

## What it reads  [SILENT]

```
SPEC.md                    the feature set — every section under "How it
                           works", and the Parts where the project has them.
                           Each section heading is one feature.
QUEUE.md, both sections    where each feature's work sits
the record's window        LOG/index.md — and LOG/index-<previous month>.md
                           too where fewer than seven days of the current
                           month have passed, so the window never runs
                           nearly empty at a month's start. The split by
                           month is the derivation: the window is one or two
                           index files, never the whole archive.
```

Where a planning or build session has already opened in this chat, those
reads are in front of you; read only what is missing.

## The stage rule  [SILENT]

Each feature gets exactly one of five stages, read mechanically and never
judged. Apply the first that matches, top-down:

```
shipped     a build record in the window names the feature — an index line
            whose entry is a build (not a planning entry) and whose words
            name the feature or a queue slug the feature's item carried
ready       a work item for the feature sits in Processed ABOVE the
            cleared-to-run line
waiting     a work item for the feature sits BELOW the line — carry the date
            it waits for, or the item it waits on, in plain words
an idea     the feature is named only by a capture in Unprocessed
untouched   nothing in the queue or the window names it
```

Match a feature to queue entries and index lines by its heading's words and by
any slug its SPEC section cites. A feature matched by more than one entry takes
the highest stage in the list above.

## What the brief carries  [BRIEF]

**What the catchup turn carries.** One line per feature, in SPEC's order:
the feature's name, its stage, and one plain clause saying what that means
for it — "shipped, the weekly update check went in on the twelfth", "waiting
on the repository cleanup". Then three lines a returning user acts on:

```
what a build would do next   the top cleared item, in plain words — "nothing
                             is cleared" where the region is empty
what is waiting on you       the [user] items, each in one clause — "nothing"
                             where there are none
what is held on a date       each dated item and its date — "nothing" where
                             there are none
```

It ends on those three lines. No ask is manufactured: the user asked for a
brief, and the brief is the answer.

**Out by rule:** slugs, rationale, counts beyond the three lines, the
reasoning that led to any stage, and anything the user did not ask about. A
feature's line names the feature by its SPEC heading's words, never by a queue
slug.

**Every date in the brief is read from a record's own date field or an index
line, never recalled** — the skill-nonspecific rule on time words governs
here as everywhere.
