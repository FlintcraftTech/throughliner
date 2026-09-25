---
name: catchup
docset: current
note: >
  /catchup procedure. A returning user's brief: where each feature stands,
  read mechanically off SPEC, the queue and the record's recent index lines.
  Register: structure in typed blocks, everything else in prose, tags inline.
---

# /catchup procedure

/catchup is for a user coming back to the project after time away — a chat
picked up days later as much as a fresh one. It says where the project's
important features stand, in a few lines, and re-runs the return checks a
fresh opening runs. **It moves nothing in the queue, and it files only what
those checks file:** a due cycle's capture under the cycle's slug where no
open capture carries it, and waiting mail read and routed through the
three-way triage as the openings route it. The brief is chat only.

## What it reads  [SILENT]

```
SPEC.md                    the Goals section, where the project has one —
                           each goal with its "reached when" line — and
                           the feature set: every section under "How it
                           works", and the Parts where the project has them.
                           Each section heading is one feature.
QUEUE.md, both sections    where each feature's work sits
the record's window        LOG/index.md — and LOG/index-<previous month>.md
                           too where the current month's index does not yet
                           reach back to the most recent planning session's
                           record, the same window a planning opening reads.
                           The split by month is the derivation: the window
                           is one or two index files, never the whole
                           archive.
the cycles doc             every definition with what its observable reads
                           — the state server's cycles_state tool where the
                           server is registered — and due-ness computed from
                           it as plan.md's cycles due-ness check computes it
the mailbox                INBOX/, read and routed as plan.md's waiting-mail
                           step routes it
the installed version      the plugin version this chat opened on, from the
                           opening's `[Throughliner]` lines, against the
                           version installed now; pre_tool_use's
                           once-per-session notice is the other site
the clock                  read now — the state server's clock tool where
                           the server is registered, a shell clock command
                           otherwise — against the opening's date line
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

A goal gets one of two: **reached**, where its "reached when" line names
something the record, the cycles doc's observable or the queue shows holding;
**heading** otherwise.

## What the brief carries  [BRIEF]

**What the catchup turn carries.** It opens on the first goal's line, with
nothing before it — no line about what was read or reused. One line per goal
first, in SPEC's order: the goal, reached or heading, and what its test shows
now in plain words — "heading: the last release was on the second, and the
cycle wants one every Wednesday". Then one line per feature, in SPEC's order:
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

Then one line per return check that found something, in the opening's own
words, and no line for a check that found nothing:

```
a cycle due now       "[weekly-release] is due: the last release was on the
                      sixteenth, and its capture is filed"
a message waiting     "one message waits in INBOX/, from <project>: <subject>"
a version change      "the plugin under this chat changed, from 1.23.0-test4
                      to 1.23.0-test5 — a fresh chat carries the new one"
the date moved        "the chat opened on the twenty-second; it is now the
                      twenty-fifth (2026-09-25)"
```

It ends on those lines. No ask is manufactured: the user asked for a
brief, and the brief is the answer. The shape, with a project that has one
goal and two features:

> **Weekly release every Wednesday** — heading: the last release was on the
> second, and nothing has shipped on the two Wednesdays since.
>
> **Dark theme** — shipped, it went in on the twelfth.
> **Search** — ready, the next build run starts on it.
>
> Next build: search across notes. Waiting on you: nothing. Held on a date:
> the launch post, until the sixteenth.
>
> [weekly-release] is due: the last release was on the second, and its
> capture is filed.

Where SPEC has no Goals section, the brief opens on the first feature line
instead.

**Out by rule:** slugs, rationale, counts beyond the three lines, the
reasoning that led to any stage, and anything the user did not ask about. A
feature's line names the feature by its SPEC heading's words, never by a queue
slug.
