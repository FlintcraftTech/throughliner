# Write failures per item processed, before and after the state server's tools

From the `[audit]` [mcp-write-failures-before-after], run 2026-09-12 over this
project's own session transcripts and the safety check's decision log. Raised
by the user 2026-09-12 at planning: what she sees with the server is fewer
failed tool calls, and this is the measurement the token-cost audit
(`mcp-token-cost-before-after.md`) did not make. Every figure here is counted
from the transcripts; nothing is estimated.

## Method

- **Sessions.** The same sixteen planning sessions as the token-cost audit,
  matched by opening time (transcript UTC stamp plus ten hours, within ten
  minutes of the table's time), with that audit's items-processed figure per
  session; plus every build run opened on or after 2026-09-06 whose first
  command was `/throughliner:next` and which ticked at least one item, items
  being the count of `build_tick` calls plus queue-tool deletes. This build
  run is in the sample, counted up to the moment the script ran.
- **Five classes, per session.** A: refusals in
  `.throughliner/pre-tool-use.log` (deny lines carrying the session's id). B:
  tool results carrying an error. C: queue-tool refusals — `reorder_queue:`
  text in an errored result, or a server tool answer beginning "Refused". D:
  the queue lint's flagging message (the form that lists fresh flags after an
  edit). E: the same tool call, name and input identical, repeated within one
  turn (a turn being the span between two user messages that are not tool
  results).
- **Ratios** are each class divided by items processed.
- **The decision log's reach**, checked first as the item required: the log
  is pruned to its newest 500 lines on each append (`pre_tool_use.py`,
  `_DECISION_LOG_LINES`), and on 2026-09-12 its first line was stamped
  2026-09-11 10:38. So class A is unavailable for every planning session in
  both windows and for all but the two newest build runs; it is marked `n/a`
  where the log does not reach, and every other class is counted from the
  transcripts alone for every session.
- The counting script was a throwaway in the session scratchpad; this
  description is enough to write it again.

## Planning sessions

| window | opened | record | items | A log | B errored results | C queue refusals | D lint flags | E repeats | per item B / C / D / E |
|---|---|---|---|---|---|---|---|---|---|
| before | 08-30 22:56 | 08-31 (e04b514) | 13 | n/a | 6 | 0 | 12 | 0 | 0.46 / 0.00 / 0.92 / 0.00 |
| before | 08-31 15:14 | 08-31-2 (795f66e) | 38 | n/a | 1 | 1 | 160 | 0 | 0.03 / 0.03 / 4.21 / 0.00 |
| before | 09-01 02:03 | 09-01 (9fb3d9f) | 38 | n/a | 2 | 0 | 194 | 0 | 0.05 / 0.00 / 5.11 / 0.00 |
| before | 09-01 16:43 | 09-01-2 (9d420fa) | 23 | n/a | 1 | 0 | 4 | 0 | 0.04 / 0.00 / 0.17 / 0.00 |
| before | 09-02 14:22 | 09-02 (475ee4a) | 37 | n/a | 2 | 0 | 4 | 0 | 0.05 / 0.00 / 0.11 / 0.00 |
| before | 09-03 16:40 | 09-04 (a33f6a4) | 30 | n/a | 2 | 0 | 12 | 1 | 0.07 / 0.00 / 0.40 / 0.03 |
| before | 09-04 23:04 | 09-05 (05da2f6) | 30 | n/a | 3 | 0 | 2 | 0 | 0.10 / 0.00 / 0.07 / 0.00 |
| before | 09-05 22:45 | 09-06 (fa71866) | 16 | n/a | 3 | 0 | 2 | 0 | 0.19 / 0.00 / 0.12 / 0.00 |
| after | 09-06 11:44 | 09-06-2 (1aba748) | 37 | n/a | 0 | 0 | 0 | 0 | 0.00 / 0.00 / 0.00 / 0.00 |
| after | 09-06 19:09 | 09-06-3 (0c8c49a) | 22 | n/a | 2 | 1 | 16 | 2 | 0.09 / 0.05 / 0.73 / 0.09 |
| after | 09-06 22:26 | 09-07 (caa25ef) | 17 | n/a | 2 | 0 | 0 | 0 | 0.12 / 0.00 / 0.00 / 0.00 |
| after | 09-08 14:48 | 09-09 (a6a97a0) | 20 | n/a | 2 | 0 | 6 | 0 | 0.10 / 0.00 / 0.30 / 0.00 |
| after | 09-09 09:55 | 09-09-2 (9057c7e) | 15 | n/a | 2 | 0 | 90 | 0 | 0.13 / 0.00 / 6.00 / 0.00 |
| after | 09-09 17:05 | 09-10 (7d78b36) | 20 | n/a | 3 | 0 | 0 | 0 | 0.15 / 0.00 / 0.00 / 0.00 |
| after | 09-10 20:57 | 09-10-2 (1dae19b) | 21 | n/a | 3 | 0 | 0 | 0 | 0.14 / 0.00 / 0.00 / 0.00 |
| after | 09-10 23:27 | 09-11 (35b5835) | 17 | n/a | 2 | 0 | 15 | 0 | 0.12 / 0.00 / 0.88 / 0.00 |
| **before sum** | | | **225** | | **20** | **1** | **390** | **1** | **0.09 / 0.00 / 1.73 / 0.00** |
| **after sum** | | | **169** | | **16** | **1** | **127** | **2** | **0.09 / 0.01 / 0.75 / 0.01** |

## Build runs since 2026-09-06

| opened | items (ticks) | A log | B | C | D | E | per item B / C / D / E |
|---|---|---|---|---|---|---|---|
| 09-06 00:31 | 3 | n/a | 14 | 0 | 46 | 0 | 4.67 / 0.00 / 15.33 / 0.00 |
| 09-06 21:43 | 9 | n/a | 1 | 0 | 64 | 0 | 0.11 / 0.00 / 7.11 / 0.00 |
| 09-10 00:24 | 19 | n/a | 2 | 0 | 0 | 1 | 0.11 / 0.00 / 0.00 / 0.05 |
| 09-10 22:18 | 13 | n/a | 2 | 2 | 12 | 0 | 0.15 / 0.15 / 0.92 / 0.00 |
| 09-11 09:14 | 16 | n/a | 2 | 1 | 0 | 0 | 0.12 / 0.06 / 0.00 / 0.00 |
| 09-11 16:09 | 12 | 3 | 3 | 0 | 138 | 0 | 0.25 / 0.00 / 11.50 / 0.00 |
| 09-12 12:26 (this run, partial) | 8 | 0 | 0 | 0 | 8 | 0 | 0.00 / 0.00 / 1.00 / 0.00 |
| **sum** | **80** | | **24** | **3** | **268** | **1** | **0.30 / 0.04 / 3.35 / 0.01** |

Build runs use the tick tool from 2026-09-06 and have no before window of
their own in this sample; the table is the after side only, kept because the
item asked for it.

## What the classes show, and what they do not

- **Errored tool results per item: 0.09 before, 0.09 after.** The same. The
  per-session spread is 0.03 to 0.46 before and 0.00 to 0.15 after: the after
  window's worst session is better than the before window's worst, and its
  best is a session with no errored call at all, but the totals do not move.
  This is the class closest to what the user sees as "failed tool calls", and
  nothing in it is attributable to the server.
- **Queue-tool refusals: one in each window.** The refusals the server's tools
  exist to make at the door happened once in 225 items before and once in 169
  after. There was almost nothing here to remove.
- **Lint flags per item: 1.73 before, 0.75 after — and the class does not
  measure what it was meant to.** The lint's flagging message is emitted after
  a queue edit *and after every shell command* while a flag is outstanding (a
  deliberate change so a shell write cannot bypass the lint), so the count
  scales with how long a flag stood times how many commands ran meanwhile.
  Two sessions in each window carry nearly all of it (160 and 194 before; 90
  after), each a session that left one flag standing for a long stretch. It
  says something about flag persistence and nothing about write failures.
- **Repeated commands within a turn: one before, two after.** Noise.
- **The decision log cannot supply class A for any session in either
  window.** It keeps 500 lines, which on this project is under two days of
  tool calls, so the refusal count the item asked for first is the one count
  the audit could not make.

**No attributable difference was found.** The one class that fell (lint
flags) is not a write-failure measure, and the class that is (errored results)
did not move. The draft on [mcp-ships-no-separate-install-post] stands as
written, and no paragraph is added to it here.

## Limits

- One project, one machine, on Fable; the server registered here only.
- The items-processed figures are the token-cost audit's, with the 08-30
  session's known undercount (its record says roughly thirty entries; its
  hash carries 13 index lines), which inflates that session's per-item
  figures and nothing else.
- Class B counts every errored tool result, including a `git` command that
  exited non-zero on purpose or a grep that matched nothing; nothing separates
  a write that failed from a read that returned a non-zero status.
- Class E defines a turn by user messages; two identical calls across a tool
  result boundary in the same reasoning stretch are counted, and a genuinely
  repeated call in a later turn is not.
- Nothing separates the server from every other change of the same fortnight.

## Frame assessment

- **TIME RANGE** — a fortnight either side of 2026-09-06, plus build runs to
  2026-09-12; describes those sessions and drifts as the method changes.
- **PEOPLE** — measures Claude's tool calls in this project; says nothing
  about the tester's project, which has no server.
- **FRESHNESS** — perishable; re-measure after any change to the hooks, the
  lint's emission rule, or the decision log's retention.
- **RISK IF WRONG** — a claim to the tester that the server removes failed
  calls would be unsupported; none is made.
- **ALTERNATIVES** — a controlled comparison (the same items both ways) was
  refused at processing on cost and stands; counting tokens was done and found
  nothing attributable. A refusal count from a decision log with a longer
  reach is the one design not yet run, and it needs the retention changed
  first — filed as a capture.
