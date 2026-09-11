# FAQ

Answers to questions about how this project's workflow operates.

This FAQ fills as Throughliner's features are announced: when a change ships
and its announcement is posted, the matching entry is written here in the same
move. A young FAQ is therefore short — that means little has been announced
yet, not that there is nothing to ask. Until the entry you need exists, just
ask in chat: Claude answers workflow questions in plain words, and the README
covers what the plugin does.

## How do I install Throughliner?

Two routes, depending on where you're starting.

If you already have Claude Code, open a chat in it and ask, in plain English,
for the marketplace `FlintcraftTech/throughliner#beta` to be added and the
`throughliner@flintcraft` plugin installed from it. The `#beta` on the end is
the tested weekly pick; the plugin's main line carries day-to-day development
and can change under you mid-week. Claude Code runs both
commands for you — you never type in a terminal. Then **fully quit** the app
and reopen it, so the plugin loads. On Windows, "fully quit" means checking the
process has actually exited, because a normal close can leave it running.

If you're new to Claude Code, or not sure, open a fresh chat at claude.ai in
your browser and ask Claude to read the install guide at
`https://github.com/FlintcraftTech/throughliner/raw/main/INSTALL.md` and walk
you through it one step at a time. That guide covers installing Claude Code,
setting up a paid plan, installing the plugin, and a quick test that it worked.
No terminal experience is needed.

You do need a paid Claude plan — Pro is enough. Claude Code does not run on the
free tier.

## What happens in my first session?

Open your project folder in Claude Code and run `/setup`. Claude interviews you
about what you're building and creates your project's documents: your spec,
your queue, your session log and this FAQ.

Don't overthink the answers. Plain language is fine and nothing is locked in —
your next step is a `/plan` session where you organise the work, so anything
you miss gets sorted there.

The interview asks what you're building and who for, whether to keep Claude's
replies short and decision-led, whether the repository is public or private
(and if public, about a licence), and whether to keep your planning documents
out of version control — those documents hold your reasoning, which is worth
keeping private if the repository isn't.

**If your project has several distinct parts**, start with one project in the
parent folder. When a part outgrows that queue, open its subfolder and run
`/setup` there: Throughliner notices it's inside an existing project, reads the
parent's spec, and asks which part this folder covers. The subfolder becomes a
full project of its own. That's called a **pop-out**, and it's deliberately
one-way — there's no scripted route back in. You don't need to decide any of
this upfront.

The link back is deliberately simple: work in a subproject can hold up work in
the parent — never the other way round — and anything crossing between the two
travels as mail you approve, never as one project silently editing another.

**After a plugin update**, running `/setup` again on an older project migrates
its documents to the current format rather than replacing them.

## What actually happens in a `/plan` session?

You talk. Describe what you want, raise ideas, answer Claude's questions. Claude
does the organising — checking your queue for contradictions, asking the design
questions a build would otherwise have to guess at, and filing everything. You
can interrupt at any point to raise something new. There's no wrong order.

Your queue has two sections. **Unprocessed** is where new ideas land, as
**captures** — rough is fine, just enough to remember what you meant. A capture
can come from you at any moment in any chat, from Claude noticing something
mid-build, or from `/rescan` sweeping up what was said but never filed.

**Processed** is work you and Claude have agreed on, and inside it a readiness
line separates work that's ready to build from work that's still waiting on
something. The part above that line is cleared to run, and it's what `/next`
builds from. Work sits below the line for one of two reasons, written on the
item itself: another named piece of work has to ship first, or a date hasn't
passed yet.

A `/plan` run opens by checking the queue for problems — work marked ready that
contradicts its own notes, items that name no files to change, work waiting on
itself in a loop — and reports what it finds. Then it asks one question: is
there anything you want to prioritise, or shall Claude order them the usual way?
"The usual way" means the standard order the method applies when nothing is
prioritised — you get told in one line which order was used.

You don't have to process everything in one sitting. `/plan`, `/done`, fresh
chat, `/plan` again is a normal rhythm.

## What does `/next` do?

It builds the ready work. Claude takes the top item, reads what it's meant to
change and which files it touches, and builds it — locked to those files, and
never adding one without asking you first.

If several items are ready, `/next` builds them back to back without asking you
to confirm each one. It's not a run that finishes on its own, though: it stops
to walk you through anything that's yours to do, it halts on work marked as
needing a session of its own, and it never closes itself.

Work can carry a tag saying how it runs:

- **`[audit]`** — Claude reads and reports without editing anything. What it
  finds becomes captures in your queue for a later `/plan`.
- **`[user]`** — work Claude genuinely can't do, like a check that needs your
  eyes. Claude walks you through it live, one step at a time, after all the
  building is finished.
- **`[freeform]`** — work `/next` must not run, because it's large or because
  it can't safely run inside a build. `/next` stops when it reaches one rather
  than skipping past it.
- **`[co-write]`** — a text you and Claude finish together, in one named
  file. Claude drafts it or takes the file as it stands, hands it to you as a
  link that opens it, and waits; you edit and save; Claude reads it back when
  you say to and asks whether there's anything else, until you say you're
  finished. Ask for one by saying you want to co-write something.

**If you ask for something mid-build that isn't part of the current job**,
Claude files it as a capture and says why in one clause, rather than quietly
widening the job. Ask a second time and a small change goes straight through.

## Why does every session end with `/done`, and why start a fresh chat?

`/done` records what happened in your session log — what was decided, what was
built, what's still open — and commits. Until it runs, the work may exist in
your files but the reasoning behind it isn't on the record anywhere. So finish
every session with it.

Then start a fresh chat, either with `/clear` or a new conversation. `/clear`
wipes the conversation on screen and touches none of your project's files —
which is exactly why it is safe once `/done` has run. This isn't
tidiness. Every message in a conversation takes up room in Claude's context
window, and a long session fills it; once it's full, earlier details start
slipping — instructions get fuzzy, scope drifts, mistakes creep in. A fresh
chat gives the next session the whole window. It doesn't lose anything, because
the next session learns what happened from your log and what's planned from
your queue.

The order matters: **`/done` before `/clear`, always.** Clear first and the
session's thinking is gone before it was written down.

`/done` also tells you what the next work is and then stops. It won't invite you
into another build in the same chat.

## What is `/rescan` for?

It reads back over the conversation — what you said, what Claude thought while
working — and files anything that never made it into a file. A shortened
version runs inside `/done` as a safety net, but you can run `/rescan` yourself
at any moment.

The reason to run it mid-session is that `/done` is too late for some things.
If you've been freewheeling in a `/plan` session, running `/rescan` sweeps what
was said into captures right then — so they can be processed in that same
session and be cleared to run in time for your very next `/next`.

It also reads Claude's own working-out, not just your messages, so ideas that
came up while Claude was actually working with your project get filed rather
than lost.

What it finds is routed by where it belongs: work still to do becomes a
capture, while something that already *happened* is added to this session's
record as a marked tail. That second half is what makes `/rescan` the one-word
way to record work you did after /done.

Two limits worth knowing. It reaches only as far back as Claude can still see
in the conversation. And it stops at the last `/rescan` in that chat, so
running it twice doesn't comb the same ground again.

## Does `/plan` know what happened in my other sessions?

Yes. When you run `/plan`, Claude opens by reading your session history — not
all of it, just everything recorded since the last time you sat down to plan.

It isn't a summary, and it won't recite your history back at you. What it does
is check for an overlap: did something built last week name a file, or a piece
of work, that's about to come up today? If yes, you hear about it before you
start deciding.

You get one line either way — including when nothing overlaps. That's
deliberate: a check that only speaks when it finds something is impossible to
tell apart from a check that never ran.

The window comes from your own records rather than a fixed number of sessions,
so it stretches to cover however long it has been. It matters most if you plan
every week or two and build in between: all that building lands in the record,
and the next planning session walks in having read it.

## How do I update Throughliner, and which build should I be on?

Be on the newest release listed on the plugin's Releases page on GitHub. Each
one has been used for real work before it was published, and its notes say what
changed. They are all marked "pre-release" — that describes the stage the plugin
is at, not a warning against installing it. The newest is the one to have.

Updating is one ask away. In a chat in Claude Code, ask Claude to update the
plugin — it runs the command for you. Then **fully quit** Claude Code and reopen
it, because plugins load when the app launches; a new chat is not enough. On
Windows, check the process has actually exited, since a normal close can leave
it running.

A new version existing will never nag you. Your project hears about the plugin
only when something actually needs your attention: a document your project is
missing, a newer setting it hasn't been offered, or a change to the document
format that needs migrating. Each of those says so plainly at the start of a
session and tells you what to run. Silence means there is nothing to do.

If you want to know when a new version lands, the plugin's GitHub page has a
**Watch** button: choose Custom, tick Releases, and you get an email each time.

## How do I report a problem, and how does the answer get back to me?

Start by saying which thing is misbehaving — Claude asks if it can't tell.

**Your own app** is ordinary work: it becomes an item in your queue like
anything else.

**Throughliner itself** — a command doing something odd, a step that confused
you, a rule with a bad result — goes to the plugin's author. Claude offers to
file it as an issue on the Throughliner repository, drafts it, and shows you the
exact words. Nothing is sent until you say yes, and the offer tells you plainly
that an issue is public and sits under your own GitHub account. If you would
rather keep it private, there is a web form instead, and it is a proper route
rather than a lesser one.

**Claude Code itself** — the app, its viewer, its links — is Anthropic's, and
goes to an issue on their own repository the same way.

Answers find you rather than the other way round. Every planning session opens
by checking your correspondence — mail from your other projects, replies on
issues you filed, new issues on your own repository — and files anything new
into your queue. So you don't have to remember to go and look.

If you want a reply to something you sent, say so when it goes: Claude files a
dated reminder in your queue, and it surfaces in a planning session once that
date passes.

One optional thing worth having: `gh`, GitHub's command-line tool. Everything
works without it — Claude writes the report out and you post it yourself. What
you'd miss is the two-way channel, where Claude both files the report and reads
the answer back.

## What does a red flag mean in my queue?

Claude watches every chat for anything that could expose your data or your
users' data, and when it spots something, it says so in plain English and marks
the piece of work that carries it. That mark is the red flag.

The flag rides the work rather than sitting in a list of its own, because the
item *is* what gets done about the risk.

A flag clears one of two ways, and both leave a record. Either the risk is
designed out, and your session log says how. Or you are told plainly what the
risk is and you choose to go ahead anyway, and the log records that you were
told and what you decided.

Flagged work cannot reach the ready-to-build region while its flag is
uncleared, so a build never quietly ships past a security concern.

The honest limit, which matters more than the feature: Claude cannot anticipate
every exposure or breach. It catches what is in view, and there is no way to
know what it missed. So Throughliner will never tell you a project is secure —
it shows you what it sees and hands you the decision.

## Can I use this method with a tool other than Claude Code?

Yes, by porting it — and people are already doing that. Throughliner is a
plugin for Claude Code, so it will not simply run elsewhere, but what it
actually consists of is plain documents plus a handful of small Python scripts
that fire at certain moments in a session. Everything is public in the
project's repository and readable without knowing how to code.

What a port takes on is the mapping: your tool has its own way of starting a
session and running commands, and someone has to decide which of Throughliner's
moments correspond to which of yours. That part is judgement, and nobody can do
it for you from here.

Two kinds of port are emerging, and both are welcome. One follows this project
closely and carries as many of its features as the other tool allows. The other
takes the idea somewhere of its own — its own name, its own decisions, adopting
only the changes it wants. Neither is the right answer; what matters is being
able to say which one a given port is, so people know what they are installing.

If you are considering it, the project's Discord server is where the people
already porting are, and there is a showcase channel for ports and for projects
built with the method. More support for porters is being written; ask there
rather than working it out alone.

## Why did my build run stop before finishing the list?

Two deliberate stops exist, and both are yours. A build run works down your
queue from the top and builds only what sits above the
`--- Cleared to run above this line ---` line — that line is placed at the end
of each planning session, just below the last item you agreed was ready, so
the run never builds anything you didn't sign off. And an item marked
`Runs alone` ends a run before it: that marker is for work that moves files or
folders other work depends on, so it always gets a run of its own. If a run
stops earlier than you expected, check where your line sits and whether the
next item carries that marker — both stops are the system honouring what was
set up, not a fault.

## Can I keep my planning documents out of the repository, and does undo still work?

Yes to both. Setup proposes keeping your spec, your queue and your session
records out of the repository — they hold your plans, your reasoning and your
history, which is the most personal material the method produces, and keeping
them untracked is the only complete protection if the project is ever
published. You accept that, or choose to track them instead, and the choice is
per document. What still works: Claude writes to those files first and tells
you what landed, exactly as before, because before each change the plugin
saves a copy of the previous version into a local folder that is itself kept
out of the repository. A deleted queue item can be put back from there. What
changes: /done cannot read its own work back from the file's history, so
it records the session from what it remembers, and those saved copies live on
this machine only — a lost disk loses them.

## What is a checklist, and how is it different from a cycle?

Both live in your cycles doc. A cycle is recurring work with a rhythm — a
weekly release, a posting cadence — and the method works out when its next
turn is due and puts that turn into your queue. A checklist is a step list with
no rhythm: you save a procedure you repeat, give it a firing word, and it runs
when you say the word and never otherwise. Your session opening names each
checklist you have with its word. Ask in planning to save a repeated procedure as
a checklist and it is written down with you there — or Claude offers it, once,
where it has noticed you asking for the same sequence more than once; if it
later turns out to have a rhythm, it becomes a cycle by gaining a cadence. A
checklist whose steps write somewhere outside the usual project documents lists
those paths in its definition, and they stay writable whenever the project is
open, not only while the checklist runs — so the list is kept narrow.

## What does planning tell me when held work comes back?

Work waits below the ready line for one of two reasons, another queue item or
a date, and planning checks each one at its opening. When something lifts, the
turn offering it says what that work's design was assuming and whether
anything has confirmed it since — read from the item's own note of the outside
facts it rests on, or said plainly where it recorded none. A capture that was
set aside until a date gets the same treatment when the date passes. The
point: the wait being over says nothing about whether the thing waited for
turned out as assumed, and this is the one moment anyone looks.

## Can I move a queue item while a build is running?

Yes, by saying so. A build run never rearranges your queue on its own
initiative, but an instruction from you goes through: tell it to skip an item,
hold one until something else lands, or move one to the bottom, and Claude
makes the move with the queue tool, says so in one line, and carries on
building. Nothing pauses and nothing is re-confirmed, because the instruction
was yours. You can check by opening QUEUE.md and finding the item where you sent
it, and the move is written into the session's record at /done. Two limits:
Claude never guesses a move you did not ask for and never offers one mid-run —
that waits for planning — and deleting an item is a separate decision a run
will not make on the fly, so ask for a delete at planning instead.
