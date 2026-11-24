---
name: goals
docset: current
note: The /goals procedure. One discussion across every project in the vault, one project per message, ending in two notes written on the user's yes: goals.md, which /tasks sorts by, and strategy.md, which the user reads and shares.
---

# /goals

**/goals settles which of the user's projects come first, and in what order they mean to work on or finish them.** It is one discussion, one project per message, and it writes two notes, only on the user's yes, in the folder holding the note the project's `Task list:` line names:

- `goals.md` is for `/tasks` to read, and for the next goals run. It holds one numbered list of project names under `## Priority`, the first ranking first, each project's lines indented beneath its name; it holds no list of held projects. A line is one of three kinds, one link per line and one direction per line, a pair of projects carrying as many as hold:

```
<project> waits on <project> until <what; a goal's [slug] where one exists>
<project> supports <project>: <how, in the user's words>
all of it waits until <what>
```

  Beneath its own project a line drops the leading name, and a wait of one step names the step: `first video waits on Throughliner until its goal [helps-with-adhd] is reached`. An optional `## No project yet` section at the bottom holds the goals that belong to no project. `/tasks` reads the numbered names and each `all of it waits` line, and nothing else in the note.
- `strategy.md` is for the user to read and share. It gives the order at the level of months to years: when they intend to work on or finish each project in relation to the others, written as "this comes after that". It carries no deadlines. A goal may name a date, and nothing enforces it.

It is run in the project that keeps the task-list note. Where the project's `Task list:` line reads `none` or is missing, or no folder above the note holds `.obsidian/`, say so in one line and stop.

**A run on named projects.** Where the user names one or more projects when starting the run, take up those alone: show each one's entry, its place, goals and lines, and confirm it as Step 2 does. On the user's yes rewrite only those entries, and a line under any other project the change touches, shown first.

## Step 1: Read

**Read the clock first**, with the state server's `clock` tool or a shell command.

**Read, without reporting yet:**

- Every Throughliner project in the vault. The vault is the folder holding `.obsidian/`, found by walking up from the task-list note. A project is a folder holding `SPEC.md` and `QUEUE.md`; folders named `.git`, `node_modules` and `.throughliner` are skipped. For each project read the `#goal` lines in its `SPEC.md` (`- [ ] <goal>, reached when <the test> (<project>) 🆔 <slug> #goal`), the newest line of its `LOG/index.md` for its date only, and its `QUEUE.md` for a `Blocked by:` line naming another project's item and for nothing else.
- `goals.md` and `strategy.md` in the task-list note's folder, where they exist: the list, the lines beneath each project, and the `## No project yet` section.
- This project's Unprocessed section, for a capture describing a project not yet set up and for a capture carrying a goal that belongs to no project.

**On a later run, take up only the projects whose goals or newest record's date changed since `goals.md` was last written**, read from its `Written:` line, and any new project. A project holding an unticked `#goal` line whose "reached when" clause rests on the user's own feeling or judgement is taken up on every run. Say in one line which projects are unchanged and left as they stand.

**Then one short message**: how many projects there are, and which ones `goals.md` does not yet list. A project that exists only as a capture is listed separately, one line each.

## Step 2: One project per message

**Take the projects in the order the existing `goals.md` gives, then any it does not list; on a first run, in the vault's folder order.** Each project's message quotes its goals and the sentence about it from `strategy.md`, in the user's words from the last run, and asks whether that is still true. A project with no earlier words gets a reason drafted from its own `SPEC.md` purpose statement, shown in a blockquote and confirmed the same way. A no is followed by one question asking what changed. Wait for the answer before the next project. The count of work cleared in the project's queue is given where the user asks.

**The message also shows every link naming the project**, read from the lines beneath each project in `goals.md`, each quoted and confirmed with the same question. A `Blocked by:` line in one project's queue naming another project's item, not already a link, is offered once as one and written on the user's yes. A waits-on link whose "until" is met, a goal reached being read from its ticked line, is asked about once: whether to remove the line. A supports link leaves only on the user's word. Where the user would hold or drop a project that supports another, say what it supports before they decide.

**A goal whose test is the user's own feeling or judgement gets one plain question in the goal's own words** ("Have you gone two weeks without that fear?"), in its project's message. On the user's yes: where the run is in the goal's own project, tick the line in its `SPEC.md`; for any other project, send a capture with `send_capture` saying the user reached the goal, in their words and with the date from the clock, shown first. Where that project is not in the address book, say so and leave the yes in the session. On a no, write nothing; the goal is asked again at the next run.

**A project with no `#goal` line gets a goal drafted in the user's words from the conversation.** Before a goal is sent to a project the address book does not hold, add its row, the name and the folder the vault walk found, in the shape `feedback-and-inbox.md`'s address-book paragraph gives, and say so in one clause naming the project and not the path. Then show the goal in a blockquote, and on the user's yes send it to that project as a capture with `send_capture`. The run writes `.throughliner/address-book.md` in the project it runs in and no other.

## Step 3: Sort into two groups

**As each project is discussed, put it in one of two groups, saying which in one clause:**

```
must-do            has real-world consequences if it slips
building towards   matters, and its timing is the user's
```

**Then ask "what about this project has to wait?"**

```
all of it    the project takes the line `all of it waits until <what>`
one step     the project stays in its group; the step is named in a waits-on line,
             `<project>'s <step> waits on <project> until <what>`; and the project is
             sent a capture with `send_capture`, shown first, asking it to hold that
             step until the goal named is reached
nothing      no line
```

## Step 4: Order where it is unclear

**Work the order out from the waits-on links first**, and ask "this one or that one first?" only for a pair no link decides, one pair per message. A supports link is named when its project is placed and sets no place. A link the user states is written as a line, shown first. The user is never asked to rank the whole list unaided, and Claude never ranks it alone.

## Step 5: Goals with no project

**A capture in this project's Unprocessed carrying a goal that belongs to no project is moved onto the `## No project yet` list on the user's yes, and the capture deleted.**

**Each listed goal then gets one question, one goal per message:**

```
join a project          sent there as a goal with `send_capture`, shown first, on the
                        user's yes, and taken off the list
become a project        named for the setup command, and left on the list until that
                        project exists
stay                    left as it is
```

A listed goal whose test is the user's own feeling or judgement is also asked whether it has been reached, and ticked on the list on a yes.

## Step 6: Show and write

**Show the whole order on one screen**: the numbered list with each project's lines beneath it, the goals with no project, and two or three lines of strategy prose. Ask whether to write it. On the user's yes, write both notes. Every rewrite carries each project's lines and the `## No project yet` section through.

`goals.md`:

```markdown
# Goals

Written: YYYY-MM-DD, by /goals. Read by /tasks; written only by /goals.

## Priority

1. Throughliner
   - supports YouTube: its log gives stories, and topics are sent over as captures
2. YouTube
   - first video waits on Throughliner until its goals [helps-with-adhd] and [ship-through-youtube] are reached
   - supports Throughliner: it promotes the plugin, and may bring voluntary support as income
3. Old shop
   - all of it waits until I decide whether to reopen

## No project yet

- [ ] <goal>, reached when <the test> 🆔 <slug> #goal
```

A project's name is written as its queue lines write it in brackets. The `Written:` line carries the date of the last full run; a run on named projects appends `Named run YYYY-MM-DD: <names>.` to it, and a full run reads change in a named project from that later date.

`strategy.md`: a short heading per group, then the order as plain sentences ("the plugin comes before the shop, because…"), the dates the goals name given as intentions, and the links drawn from the lines in `goals.md`, a project all of which waits said so. Date it from the clock.

Then link both notes, `strategy.md` first.

**Out by rule:** writing into any other project's files except through `send_capture` on the user's yes; editing the task-list note; ranking the whole list without the user; in a run on named projects, rewriting the entry of a project not named, beyond a line the change touches.
