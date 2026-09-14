# SPEC use in this project's build runs, the week before and the week after the product-truth rewrite

Audit run 2026-09-14 inside the build run, from [spec-read-removal-scored]. The term was set by the user 2026-09-06: try the rewritten SPEC for a week, then audit whether builds are actually using it. The comparison is this project against itself, before and after, which holds the prompting constant — this project was excluded from the first audit (`spec-usage-versus-maintenance.md`) because building the method here prompts SPEC reads in itself, and that exclusion reason is carried here as the finding's limit.

## Selection

Every build run in this project's transcript folder under the Claude projects directory whose first message falls in the seven days before the rewrite's commit (`9bc4e8d`, 2026-09-06 22:23 local, 12:23 UTC — transcript timestamps are UTC) and in the seven days after it. A session's kind is the first method command its transcript invokes, `next` meaning a build; sessions that opened on `/clear` were classified by the first `next` or `plan` after it. Ten builds before, nine after; one after-window transcript (`bfcd08b3`) opens at the same minute as `34d6047d` with the same first replies and is read as a fork of it, so eight after-window builds are scored.

## Method

A script in the session scratchpad (`spec_events.py`, rewritten from the first audit's description) stripped each `.jsonl` to its SPEC events — every tool call naming `SPEC.md`, every assistant reply naming SPEC with 300 characters either side — and counted thinking blocks without printing them. Each session's SPEC reads were scored by hand at their highest on the agreed scale: **0** opened and never referred to again; **1** referred to in reasoning, nothing decided on it; **2** a decision, halt or filed gap citing a SPEC sentence. Replies and tool calls are the channel, per CLAUDE.md's transcript-reading rule. One scoring rule carried from the first audit: a completion line saying "the work agrees with SPEC" and no more scores 0; one naming the sentences it checked against scores 1.

## Per-session table — before the rewrite (2026-08-30 12:23 to 2026-09-06 12:23 UTC)

| Session | First message (UTC) | SPEC tool calls | Reply hits | Score | What scored |
|---|---|---|---|---|---|
| 63060348 | 2026-08-31 00:19 | 8 | 4 | 1 | setup.md edited to say a personal fact enters SPEC only where supplied; SPEC named as the tester's document, nothing decided on a sentence of this project's |
| 2444e519 | 2026-08-31 07:01 | 5 | 9 | 2 | filed [spec-lift-states-the-premise]: "SPEC describes the lift check as one question and it now carries two"; two more captures filed on the ground that the change is product truth a build does not write |
| f0716ea8 | 2026-09-01 02:55 | 18 | 3 | 1 | completion line names three sentences the work was checked against |
| ef55ea72 | 2026-09-01 13:51 | 2 | 1 | 0 | pre-flight mention only |
| fb712eab | 2026-09-02 13:02 | 3 | 0 | 0 | opened at run start |
| 24d10642 | 2026-09-04 02:42 | 4 | 0 | 0 | opened at run start |
| 543c5a15 | 2026-09-05 11:23 | 3 | 0 | 0 | opened at run start |
| 46195a4c | 2026-09-05 14:31 | 3 | 8 | 0 | every hit names the SPEC-usage audit as a piece of work, not the document |
| 9b376f96 | 2026-09-06 06:02 | 8 | 5 | 2 | candidate capture: "SPEC says those paths are writable whenever the project is open, so the hook's build branch contradicts it" |
| aad82da3 | 2026-09-06 11:43 | 18 | 19 | 2 | the run that built the rewrite; filed the read-back walk-through and named a phrasing regression the rewrite introduced |

Usage before: **3 of 10** builds scored 2; two scored 1; five scored 0.

## Per-session table — after the rewrite (2026-09-06 12:23 to 2026-09-13 12:23 UTC)

| Session | First message (UTC) | SPEC tool calls | Reply hits | Score | What scored |
|---|---|---|---|---|---|
| 52710f14 | 2026-09-07 23:54 | 1 | 2 | 0 | pre-flight; "the SPEC read-back" named as a walk-through |
| 34d6047d | 2026-09-08 14:28 | 24 | 13 | 1 | walked the SPEC read-back: the old and new section lists compared and presented; built per-part specs; no decision cited a sentence |
| ebbf7f9f | 2026-09-09 03:22 | 4 | 4 | 1 | completion line: "the four SPEC sentences were written at planning ahead of the build, and nothing built contradicts one" |
| 5200c46d | 2026-09-09 14:24 | 21 | 3 | 0 | "the work agrees with SPEC" and staging lines only |
| 4c4c31d6 | 2026-09-10 12:18 | 1 | 2 | 2 | filed the sentence SPEC owes for the digest's cited-by count |
| 6e568760 | 2026-09-10 23:14 | 3 | 1 | 0 | "nothing built contradicts SPEC" |
| c0dba944 | 2026-09-11 06:09 | 11 | 2 | 0 | staging lines only |
| 37b24581 | 2026-09-12 02:26 | 1 | 0 | 0 | opened at run start |

Usage after: **1 of 8** builds scored 2; two scored 1; five scored 0.

## The two ratios

| Window | Builds scoring 2 | Builds scoring 1 | Builds scoring 0 |
|---|---|---|---|
| Before | 3 of 10 | 2 of 10 | 5 of 10 |
| After | 1 of 8 | 2 of 8 | 5 of 8 |

Usage did not rise. Read with care: of the three before-window 2s, one is the run that wrote the rewrite, whose SPEC reads were the work itself; the other two are a filed gap and a contradiction found, which is the shipped rule performed. The after window's one 2 is the same shape — a filed gap. Half the builds in both windows opened SPEC at run start and never referred to it again.

## The consumer zeros — did SPEC have a sentence bearing on them?

The first audit left this open for its four zero-scoring consumer builds. Each was read against its items (from the build working file its transcript wrote) and its SPEC's section headings (from the run-start read in the same transcript).

| Project | Session | Items built | SPEC sections bearing on them |
|---|---|---|---|
| Hexboard | 340d0d6b | no build working file found in the transcript; the items could not be read | SPEC has four sections (what it is, who it is for, how it works, principles); not determinable |
| Taskflowapp | 91c12720 | ten builds: dark theme, back gesture, Yesterday page, search and completed history, Strategy on the spine, Notes out of the edit dialogue, date strip, and three infrastructure items | "Light and dark", "Yesterday page", "Search and completed history", "Strategy doc", "Edit a task", "Date picker — side-scrolling date strip", "Side menu" — at least six of the ten items had a SPEC section on their subject |
| Taskflowapp | 6008c631 | Supabase schema and RLS, Strategy page double header, LOG index split, two TOOLS.md facts, a digest report, one audit | "Claude integration via remote MCP", "Strategy doc" — two of the seven |
| Taskflowapp | ace4cfb7 | subtask lines discarded on creation, date-picker tiles clipping, a TOOLS.md fact, one audit | "Edit dialogue: outliner-style typing for subtasks", "Date picker — side-scrolling date strip" — both defect items had a section on their subject |

So for three of the four, SPEC did carry sentences on what was being built, and the build did not cite them. The zeros are not builds SPEC had nothing to say about.

## What the sample says

The usage figures describe a late-development project, where product truth lives in the code, the queue and the record as much as in SPEC; the rewrite did not change how often a build here decided something on a SPEC sentence. On this evidence the shape question — whether SPEC's rewritten product-truth form earns its run-start read — is not settled in the rewrite's favour, and the consumer sample from the first audit (two early-to-mid projects, builds 3 of 8 at score 2) is the nearer evidence for what a fresh project's SPEC does. The verdict is the user's; the findings filed as captures name both routes the item wrote down.

## Frame assessment

- **TIME RANGE** — seven days either side of one commit in one project; nothing says what a longer window would show, and the after window overlaps a week in which most builds were method-doc and hook work rather than product features.
- **PEOPLE** — one user, this project; the sessions are Claude's, so this measures Claude's use of SPEC under the method in the self-hosting case.
- **FRESHNESS** — transcripts are fixed; the method's SPEC rules did not change inside the two windows, so the two are comparable in a way the first audit's sample was not.
- **RISK IF WRONG** — a wrong "unchanged" verdict keeps a run-start read that costs about 25,000 tokens per run for nothing; a wrong "risen" verdict would have kept SPEC's shape on evidence of one week. Neither warrants a red flag; the numbers are small and the scoring is one reader's.
- **ALTERNATIVES** — scoring planning sessions too was not asked for and not done; reading every transcript whole was refused by the first audit's precedent; the fork transcript was excluded rather than double-counted, stated above.
