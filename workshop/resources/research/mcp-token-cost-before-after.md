# Token cost of planning sessions before and after the state server's queue tools

From the `[audit]` [mcp-token-cost-before-after], run 2026-09-11 over this
project's own session transcripts. Raised by the user 2026-09-10 to communicate
the state server's benefit to the one tester in plain words backed by a
measurement. Every figure here is read from the transcripts' `usage` blocks and
the LOG index; nothing is estimated.

## Method

- **Source.** Every transcript under the Claude projects folder for this
  project (224 files on 2026-09-11). A transcript is a planning session where
  it invoked `/throughliner:plan` and its first command was not `/next`; four
  sessions opened with `/clear` before the plan command and are included. The
  scan was a short throwaway script, not kept; this description is what it did
  and is enough to write it again.
- **Windows.** The seven days before 2026-09-06 (2026-08-30 to 2026-09-05 by
  the session's opening time) and the seven days from it (2026-09-06 to
  2026-09-12; the last session opened 2026-09-10). The boundary is the day the
  three queue-move tools landed (`LOG/index.md`, [mcp-queue-move-tools]); the
  hold tool landed 2026-09-04 and the capture, counts and next-pick tools
  earlier, so the "before" window already carries some server use — stated
  rather than hidden.
- **Times.** Transcripts stamp UTC; the times below are local (UTC+10), which
  is what matched each session to its planning record.
- **Figures per session.** The four usage numbers summed over every assistant
  turn; the whole-session total is their sum. Items processed is the count of
  `— plan —` index lines under the session's commit hash (one per item; the
  chat-level record excluded). Tool calls is every `tool_use` block. Queue
  operations are classified by tool name (the server's `queue_move`,
  `queue_move_section`, `queue_delete`, `hold_entry`, `file_capture`) or by
  the flag on a Bash call to `reorder_queue.py` (`--move-section`, `--move`,
  `--delete`, `--append`), the same tool-and-command method as
  `run-cost-measurements-2026-08-28.md`.
- **Out of the sample.** Build runs (one tick per item; noise), a session with
  no assistant turns, and this audit's own build run.

## Before: eight planning sessions, 2026-08-30 to 2026-09-05

| session opened | record (hash) | items | input | cache write | cache read | output | total | per item | tool calls | queue writes: script / server |
|---|---|---|---|---|---|---|---|---|---|---|
| 08-30 22:56 | 08-31 (e04b514) | 13 | 1,218 | 5,361,846 | 242,966,397 | 435,154 | 248,764,615 | 19.1M | 266 | 54 / 0 |
| 08-31 15:14 | 08-31-2 (795f66e) | 38 | 708 | 1,123,061 | 159,469,876 | 381,388 | 160,975,033 | 4.2M | 155 | 35 / 0 |
| 09-01 02:03 | 09-01 (9fb3d9f) | 38 | 898 | 2,693,638 | 226,480,512 | 449,071 | 229,624,119 | 6.0M | 230 | 40 / 0 |
| 09-01 16:43 | 09-01-2 (9d420fa) | 23 | 768 | 1,822,776 | 143,886,812 | 433,641 | 146,143,997 | 6.4M | 204 | 0 / 6 |
| 09-02 14:22 | 09-02 (475ee4a) | 37 | 38,557 | 3,542,171 | 322,241,414 | 2,002,248 | 327,824,390 | 8.9M | 382 | 47 / 0 |
| 09-03 16:40 | 09-04 (a33f6a4) | 30 | 27,917 | 3,664,075 | 160,945,326 | 848,221 | 165,485,539 | 5.5M | 225 | 29 / 8 |
| 09-04 23:04 | 09-05 (05da2f6) | 30 | 8,922 | 5,789,366 | 187,717,369 | 1,084,490 | 194,600,147 | 6.5M | 252 | 38 / 0 |
| 09-05 22:45 | 09-06 (fa71866) | 16 | 8,522 | 1,434,468 | 133,359,718 | 587,904 | 135,390,612 | 8.5M | 210 | 22 / 0 |
| **sum** | | **225** | | | | 6,222,117 | **1,608,808,452** | **7.15M** | 1,924 | 265 / 14 |

## After: eight planning sessions, 2026-09-06 to 2026-09-10

| session opened | record (hash) | items | input | cache write | cache read | output | total | per item | tool calls | queue writes: script / server |
|---|---|---|---|---|---|---|---|---|---|---|
| 09-06 11:44 | 09-06-2 (1aba748) | 37 | 8,218 | 1,718,898 | 158,110,513 | 1,286,211 | 161,123,840 | 4.4M | 233 | 38 / 0 |
| 09-06 19:09 | 09-06-3 (0c8c49a) | 22 | 9,606 | 1,589,601 | 161,462,724 | 925,384 | 163,987,315 | 7.5M | 207 | 0 / 46 |
| 09-06 22:26 | 09-07 (caa25ef) | 17 | 6,274 | 2,173,609 | 85,624,922 | 486,439 | 88,291,244 | 5.2M | 157 | 1 / 26 |
| 09-08 14:48 | 09-09 (a6a97a0) | 20 | 7,986 | 1,658,128 | 119,810,579 | 415,177 | 121,891,870 | 6.1M | 174 | 23 / 0 |
| 09-09 09:55 | 09-09-2 (9057c7e) | 15 | 718 | 758,867 | 129,377,287 | 306,952 | 130,443,824 | 8.7M | 181 | 17 / 0 |
| 09-09 17:05 | 09-10 (7d78b36) | 20 | 10,788 | 2,311,165 | 199,143,352 | 889,956 | 202,355,261 | 10.1M | 285 | 2 / 67 |
| 09-10 20:57 | 09-10-2 (1dae19b) | 21 | 7,054 | 923,011 | 102,452,752 | 448,971 | 103,831,788 | 4.9M | 180 | 20 / 4 |
| 09-10 23:27 | 09-11 (35b5835) | 17 | 6,374 | 1,468,036 | 89,065,848 | 548,826 | 91,089,084 | 5.4M | 160 | 20 / 0 |
| **sum** | | **169** | | | | 5,307,916 | **1,063,014,226** | **6.29M** | 1,577 | 121 / 143 |

Queue writes count moves, section moves, deletes, captures and holds; the
server's read-only tools (next-pick, counts, cycles, host, sent) are excluded
from that column.

## The two ratios, and what they do and do not show

- **Per item processed:** 7.15M tokens before, 6.29M after — a fall of 12%.
  The spread inside each window is far wider than that: 4.2M to 19.1M before,
  4.4M to 10.1M after. The 12% is smaller than the difference between any two
  adjacent sessions, so it cannot be attributed to the server.
- **Per session:** 201M before, 133M after — a fall of 34%, but the sessions
  after processed fewer items each (21 against 28), which is what a
  whole-session total measures.
- **Cache reads are 97% of every total.** The bill is the conversation being
  re-read at each turn, so a session's cost is its turn count times its
  length; a queue operation's transport changes neither much.
- **Tool calls per item did not fall:** 8.6 before, 9.3 after.
- **Only half the after-window queue writes went through the server** (143 of
  264). Four of the eight sessions after the tools landed used the script for
  every write. The two most server-heavy sessions (09-06 19:09 and 09-09
  17:05) sit at 7.5M and 10.1M per item, above the window's median — inside
  the after window, using the server did not make a session cheaper per item.
- **Output tokens per item rose** from 27.7k to 31.4k; a server call's
  arguments are typed where a script's body file was written with the editing
  tool, so this is not a saving either.

## Limits

- One project, one machine, on Fable, with the server registered for this
  project only.
- Items processed is read from index lines under the commit hash; the 08-30
  session's record says roughly thirty entries were processed while its hash
  carries 13 index lines, because the session spanned a restart and a
  migration — its 19.1M per item is inflated by that count, and without it the
  before figure is 6.60M per item, still above the after figure by 5%.
- Nothing here separates the server from every other change in the same
  fortnight (the ladder, the digest, the docs shrinking).
- The classifier reads the invoked command; a chat that ran /plan after a
  /next is counted as a build run and left out.

## Frame assessment

- **TIME RANGE** — a fortnight either side of one landing date; the figures
  describe those sixteen sessions and drift as the method changes.
- **PEOPLE** — measures Claude's usage in this project; says nothing about a
  tester's project, which has no server.
- **FRESHNESS** — perishable; re-measure after any change to what a planning
  session loads.
- **RISK IF WRONG** — a claim to the tester that the server saves tokens would
  be unsupported; the closing paragraph makes none.
- **ALTERNATIVES** — a whole-session total alone and build runs in the sample
  were refused at processing; a controlled comparison (the same items
  processed both ways) was not run and is the only design that could attribute
  a difference.

## For a reader outside this project

We measured what a planning session costs in tokens for the week before and
the week after the state server's queue-writing tools arrived, eight sessions
each side, reading the numbers from the session transcripts. Per work item
processed, a session cost about 7.2 million tokens before and 6.3 million
after, a difference of about 12 percent, and the sessions vary far more than
that from one to the next, so we cannot say the server caused it. Almost all
of the cost, about 97 percent, is the conversation being re-read at every
turn, which no tool changes. The number of tool calls per item did not fall.
Half the queue writes after the tools arrived still went through the older
script. So the honest statement is that the server has not been shown to save
tokens; what it does is refuse a malformed write at the door, which is a
correctness gain rather than a cost one. This was measured in one project, on
one machine, on one model, and the server is not part of what you have
installed.
