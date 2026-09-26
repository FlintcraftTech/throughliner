# FAQ

Answers to questions about how this project's workflow operates.

This FAQ fills as Throughliner's features are announced: when a change ships and its announcement is posted, the matching entry is written here in the same move. A young FAQ is therefore short — that means little has been announced yet, not that there is nothing to ask. Until the entry you need exists, just ask in chat: Claude answers workflow questions in plain words, and the README covers what the plugin does.

## How do I install Throughliner?

Two routes, depending on where you're starting.

If you already have Claude Code, open a chat in it and ask, in plain English, for the marketplace `FlintcraftTech/throughliner#beta` to be added and the `throughliner@flintcraft` plugin installed from it. The `#beta` on the end is the tested weekly pick; the plugin's main line carries day-to-day development and can change under you mid-week. Claude Code runs both commands for you — you never type in a terminal. Then **fully quit** the app and reopen it, so the plugin loads. On Windows, "fully quit" means checking the process has actually exited, because a normal close can leave it running.

If you're new to Claude Code, or not sure, open a fresh chat at claude.ai in your browser and ask Claude to read the install guide at `https://github.com/FlintcraftTech/throughliner/raw/main/INSTALL.md` and walk you through it one step at a time. That guide covers installing Claude Code, setting up a paid plan, installing the plugin, and a quick test that it worked. No terminal experience is needed.

You do need a paid Claude plan — Pro is enough. Claude Code does not run on the free tier. And you need git installed: every session ends with a commit, so the guide checks `git --version` alongside Python and the GitHub tool, and tells you where to get it for your system.

## What happens in my first session?

Open your project folder in Claude Code and run `/setup`. Claude interviews you about what you're building and creates your project's documents: your spec, your queue, your session log and this FAQ.

Don't overthink the answers. Plain language is fine and nothing is locked in — your next step is a `/plan` session where you organise the work, so anything you miss gets sorted there.

The interview asks what you're building and who for, whether to keep Claude's replies short and decision-led, whether the repository is public or private (and if public, about a licence), and whether to keep your planning documents out of version control — those documents hold your reasoning, which is worth keeping private if the repository isn't. From your answers Claude then names the command-line tools your project's work will need, asks whether any are missing, checks each on your machine and writes what it found into `TOOLS.md`, so a later session never assumes a tool is absent that you already have.

**If your project has several distinct parts**, start with one project in the parent folder. When a part outgrows that queue, open its subfolder and run `/setup` there: Throughliner notices it's inside an existing project, reads the parent's spec, and asks which part this folder covers. The subfolder becomes a full project of its own. That's called a **pop-out**, and it's deliberately one-way — there's no scripted route back in. You don't need to decide any of this upfront.

The link back is deliberately simple: work in a subproject can hold up work in the parent — never the other way round — and anything crossing between the two travels as mail you approve, never as one project silently editing another.

**After a plugin update**, running `/setup` again on an older project migrates its documents to the current format rather than replacing them.

## What actually happens in a `/plan` session?

You talk. Describe what you want, raise ideas, answer Claude's questions. Claude does the organising — checking your queue for contradictions, asking the design questions a build would otherwise have to guess at, and filing everything. You can interrupt at any point to raise something new. There's no wrong order.

Your queue has two sections. **Unprocessed** is where new ideas land, as **captures** — rough is fine, just enough to remember what you meant. A capture can come from you at any moment in any chat, from Claude noticing something mid-build, or from `/rescan` sweeping up what was said but never filed.

**Processed** is work you and Claude have agreed on, and inside it a readiness line separates work that's ready to build from work that's still waiting on something. The part above that line is cleared to run, and it's what `/next` builds from. Work sits below the line for one of two reasons, written on the item itself: another named piece of work has to ship first, or a date hasn't passed yet.

A `/plan` run opens by checking the queue for problems — work marked ready that contradicts its own notes, items that name no files to change, work waiting on itself in a loop — and reports what it finds. Then it asks one question: is there anything you want to process first? Otherwise say go, and Claude takes them in the method's order, starting on the first item. After each item, Claude says where it landed and describes the next one in a plain sentence of its own, with the item's name in brackets, then asks whether to take it next.

You don't have to process everything in one sitting. `/plan`, `/close`, fresh chat, `/plan` again is a normal rhythm.

## What does `/next` do?

It builds the ready work. Claude takes the top item, reads what it's meant to change and which files it touches, and builds it — locked to those files, and never adding one without asking you first.

If several items are ready, `/next` builds them back to back without asking you to confirm each one. It's not a run that finishes on its own, though: it pauses to walk you through anything that's yours to do and then carries on, it halts on work marked as needing a session of its own and never builds that, it ends the run before work marked `Runs alone`, and it never closes itself.

Work can carry a tag saying how it runs:

- **`[audit]`** — Claude reads and reports without editing anything. What it
  finds becomes captures in your queue for a later `/plan`.
- **`[user]`** — work Claude genuinely can't do, like a check that needs your
  eyes. Claude walks you through it live, one step at a time, after all the
  building is finished.
- **`[freeform]`** — work `/next` must not run, because it's large or because
  it can't safely run inside a build. `/next` halts on one rather than
  skipping past it, and never builds it.
- **`[co-write]`** — a text you and Claude finish together, in one named
  file. Claude drafts it or takes the file as it stands, hands it to you as a
  link that opens it, and waits; you edit and save; Claude reads it back when
  you say to and asks whether there's anything else, until you say you're
  finished. Ask for one by saying you want to co-write something.

**If you ask for something mid-build that isn't part of the current job**, Claude files it as a capture and says why in one clause, rather than quietly widening the job. Ask a second time and a small change goes straight through.

## Why does every session end with `/close`, and why start a fresh chat?

`/close` records what happened in your session log — what was decided, what was built, what's still open — and commits. Until it runs, the work may exist in your files but the reasoning behind it isn't on the record anywhere. So finish every session with it.

Then start a fresh chat, either with `/clear` or a new conversation. `/clear` wipes the conversation on screen and touches none of your project's files — which is exactly why it is safe once `/close` has run. This isn't tidiness. Every message in a conversation takes up room in Claude's context window, and a long session fills it; once it's full, earlier details start slipping — instructions get fuzzy, scope drifts, mistakes creep in. A fresh chat gives the next session the whole window. It doesn't lose anything, because the next session learns what happened from your log and what's planned from your queue.

The order matters: **`/close` before `/clear`, always.** Clear first and the session's thinking is gone before it was written down.

Typing `/close` is the yes: the commit message appears on screen as the record of what is being committed, and the commit follows with no question in between. Where your repository has a remote, one plain question follows about pushing; where it has none, push is never mentioned. What tells you it committed is the commit hash written into the session record's heading.

`/close` also tells you what the next work is and then stops, naming the command that starts it in words, mid-sentence — the plan command for more planning, the build command for building — so nothing runs by accident. It won't invite you into another build in the same chat. Where a build run ended at work still held, the closing message says in plain terms what part of your change is not in the product yet.

## What is `/rescan` for?

It reads back over the conversation — what you said, what Claude thought while working — and files anything that never made it into a file. A shortened version runs inside `/close` as a safety net, but you can run `/rescan` yourself at any moment.

The reason to run it mid-session is that `/close` is too late for some things. If you've been freewheeling in a `/plan` session, running `/rescan` sweeps what was said into captures right then — so they can be processed in that same session and be cleared to run in time for your very next `/next`.

It also reads Claude's own working-out, not just your messages, so ideas that came up while Claude was actually working with your project get filed rather than lost.

What it finds is routed by where it belongs: work still to do becomes a capture, while something that already *happened* is added to this session's record as a marked tail. That second half is what makes `/rescan` the one-word way to record work you did after /close.

Two limits worth knowing. It reaches only as far back as Claude can still see in the conversation. And it stops at the last `/rescan` in that chat, so running it twice doesn't comb the same ground again.

## Does `/plan` know what happened in my other sessions?

Yes. When you run `/plan`, Claude opens by reading your session history — not all of it, just everything recorded since the last time you sat down to plan.

It isn't a summary, and it won't recite your history back at you. What it does is check for an overlap: did something built last week name a file, or a piece of work, that's about to come up today? If yes, you hear about it before you start deciding.

Where something overlaps, the opening says what was read and what it touched. Where nothing does, the read folds into the opening's one quiet clause with the other checks that found nothing — so the opening stays short enough to read, and you can still see the check ran.

The window comes from your own records rather than a fixed number of sessions, so it stretches to cover however long it has been. It matters most if you plan every week or two and build in between: all that building lands in the record, and the next planning session walks in having read it.

## How do I update Throughliner, and which build should I be on?

Be on the newest release listed on the plugin's Releases page on GitHub. Each one has been used for real work before it was published, and its notes say what changed. They are all marked "pre-release" — that describes the stage the plugin is at, not a warning against installing it. The newest is the one to have.

Updating is one ask away. In a chat in Claude Code, ask Claude to update the plugin — it runs the command for you. Then **fully quit** Claude Code and reopen it, because plugins load when the app launches; a new chat is not enough. On Windows, check the process has actually exited, since a normal close can leave it running.

Once a week, where GitHub's `gh` tool is installed and signed in, a session's opening lines say when a newer version is on your channel, naming it beside the one installed. The next planning session opens by offering the update: say yes and Claude runs the two commands, then asks you to fully quit and reopen the app. What tells you it took is the opening's installed-version line in the next chat. Without `gh` the opening says nothing and the project falls behind, which setup tells you once.

Beyond that, a new version existing will never nag you. Your project hears about the plugin only when something actually needs your attention: a document your project is missing, a newer setting it hasn't been offered, or a change to the document format that needs migrating. Each of those says so plainly at the start of a session and tells you what to run. Silence means there is nothing to do. A format change is the strongest of the three: the session opens by saying the documents are on an older format and points you at `/setup`, which migrates them in place rather than replacing them, and never overwrites anything you wrote. The format number is deliberately separate from the version number, so it cannot cry wolf at every release.

If you want to know when a new version lands, the plugin's GitHub page has a **Watch** button: choose Custom, tick Releases, and you get an email each time.

## How do I report a problem, and how does the answer get back to me?

Start by saying which thing is misbehaving — Claude asks if it can't tell.

**Your own app** is ordinary work: it becomes an item in your queue like anything else.

**Throughliner itself** — a command doing something odd, a step that confused you, a rule with a bad result — goes to the plugin's author. Claude offers to file it as an issue on the Throughliner repository, drafts it, and shows you the exact words. Nothing is sent until you say yes, and the offer tells you plainly that an issue is public and sits under your own GitHub account. If you would rather keep it private, there is a web form instead, and it is a proper route rather than a lesser one.

**Claude Code itself** — the app, its viewer, its links — is Anthropic's, and goes to an issue on their own repository the same way.

Answers find you rather than the other way round. Every planning session opens by checking your correspondence — mail from your other projects, replies on issues you filed, new issues on your own repository — and files anything new into your queue. So you don't have to remember to go and look.

If you want a reply to something you sent, say so when it goes: Claude files a dated reminder in your queue, and it surfaces in a planning session once that date passes.

One optional thing worth having: `gh`, GitHub's command-line tool. Everything works without it — Claude writes the report out and you post it yourself. What you'd miss is the two-way channel, where Claude both files the report and reads the answer back.

## What does a red flag mean in my queue?

Claude watches every chat for anything that could expose your data or your users' data, and when it spots something, it says so in plain English and marks the piece of work that carries it. That mark is the red flag.

The flag rides the work rather than sitting in a list of its own, because the item *is* what gets done about the risk.

A flag clears one of two ways, and both leave a record. Either the risk is designed out, and your session log says how. Or you are told plainly what the risk is and you choose to go ahead anyway, and the log records that you were told and what you decided.

Flagged work cannot reach the ready-to-build region while its flag is uncleared, so a build never quietly ships past a security concern.

The honest limit, which matters more than the feature: Claude cannot anticipate every exposure or breach. It catches what is in view, and there is no way to know what it missed. So Throughliner will never tell you a project is secure — it shows you what it sees and hands you the decision.

## Can I use this method with a tool other than Claude Code?

Yes, by porting it — and people are already doing that. Throughliner is a plugin for Claude Code, so it will not simply run elsewhere, but what it actually consists of is plain documents plus a handful of small Python scripts that fire at certain moments in a session. Everything is public in the project's repository and readable without knowing how to code.

What a port takes on is the mapping: your tool has its own way of starting a session and running commands, and someone has to decide which of Throughliner's moments correspond to which of yours. That part is judgement, and nobody can do it for you from here.

Two kinds of port are emerging, and both are welcome. One follows this project closely and carries as many of its features as the other tool allows. The other takes the idea somewhere of its own — its own name, its own decisions, adopting only the changes it wants. Neither is the right answer; what matters is being able to say which one a given port is, so people know what they are installing.

If you are considering it, the project's Discord server is where the people already porting are, and there is a showcase channel for ports and for projects built with the method. More support for porters is being written; ask there rather than working it out alone.

## Why did my build run stop before finishing the list?

Two deliberate stops exist, and both are yours. A build run works down your queue from the top and builds only what sits above the `--- Cleared to run above this line ---` line — that line is placed at the end of each planning session, just below the last item you agreed was ready, so the run never builds anything you didn't sign off. And an item marked `Runs alone` ends a run before it: that marker is for work that moves files or folders other work depends on, so it always gets a run of its own. If a run stops earlier than you expected, check where your line sits and whether the next item carries that marker — both stops are the system honouring what was set up, not a fault.

## Can I keep my planning documents out of the repository, and does undo still work?

Yes to both. Setup proposes keeping your spec, your queue and your session records out of the repository — they hold your plans, your reasoning and your history, which is the most personal material the method produces, and keeping them untracked is the only complete protection if the project is ever published. You accept that, or choose to track them instead, and the choice is per document. What still works: Claude writes to those files first and tells you what landed, exactly as before, because before each change the plugin saves a copy of the previous version into a local folder that is itself kept out of the repository. A deleted queue item can be put back from there. What changes: /close cannot read its own work back from the file's history, so it records the session from what it remembers, and those saved copies live on this machine only — a lost disk loses them.

## What is a checklist, and how is it different from a cycle?

Both live in your cycles doc. A cycle is recurring work with a rhythm — a weekly release, a posting cadence — and the method works out when its next turn is due and puts that turn into your queue. A checklist is a step list with no rhythm: you save a procedure you repeat, give it a firing word, and it runs when you say the word and never otherwise. Your session opening names each checklist you have with its word. Ask in planning to save a repeated procedure as a checklist and it is written down with you there — or Claude offers it, once, where it has noticed you asking for the same sequence more than once; if it later turns out to have a rhythm, it becomes a cycle by gaining a cadence. A checklist whose steps write somewhere outside the usual project documents lists those paths in its definition, and they stay writable whenever the project is open, not only while the checklist runs — so the list is kept narrow.

## What does planning tell me when held work comes back?

A planning session's opening lines name the work that is waiting — a line like "Held until a date: … not before …", or an item waiting on another item — and planning checks each one at its opening. When a wait ends and the item is offered again, that offer says what the item's design was assuming when it was written and whether anything has confirmed it since — read from the item's own note of the outside facts it rests on, or said plainly where it recorded none. A captured idea set aside until a date gets the same treatment when the date passes. The point: the wait being over says nothing about whether the thing waited for turned out as assumed, and this is the one moment anyone looks.

## Can I move a queue item while a build is running?

Yes, by saying so. A build run never rearranges your queue on its own initiative, but an instruction from you goes through: tell it to skip an item, hold one until something else lands, or move one to the bottom, and Claude makes the move with the queue tool, says so in one line, and carries on building. Nothing pauses and nothing is re-confirmed, because the instruction was yours. You can check by opening QUEUE.md and finding the item where you sent it, and the move is written into the session's record at /close. Two limits: Claude never guesses a move you did not ask for and never offers one mid-run — that waits for planning — and deleting an item is a separate decision a run will not make on the fly, so ask for a delete at planning instead.

## What are my project's parts, and where does a new file go?

Setup works the structure out with you before it creates anything. From what you said the project is, Claude looks up what documents a person doing that kind of work actually uses, in that field's own words, and shows you one numbered list: the smallest set of folders and documents that defines the project, each with who uses it and when, and which repository it sits in where there are two. You cut or add by number, and setup creates exactly what you approved — no placeholder folders, nothing the list does not name. That list becomes `MAP.md`, the file that says what each folder and document is for and who uses it, and a session reads the map when it creates a file: it picks the folder from the map's lines and says where it put the file. The root `SPEC.md` stays the one spec for the whole project. An existing project is offered the same conversation over its existing tree once when setup runs again, proposing what to add and never deleting anything. Two other folders arrive with this: `temp/`, ignored by git, for what the project does not keep — a draft you edit, a fetched transcript — and `workshop/`, for what it works with and keeps. Inside `workshop/resources/`, `supplied/` is the committed home for text you wrote or a file you attached: a planning session may write it there unchanged, with a line naming who supplied it and when, so your own material never has to be pasted into a queue entry to survive.

## The safety check refused my edit — how do I get it through?

In a session with no build running, the safety check lets Claude write only the planning documents, and refuses anything else with a message naming the path. That is deliberate: other files are work, and work is queued and built. Where you genuinely want the edit now, ask for the same change again in your own words. Claude then declares that one path in a small scope file, says so in one line, and makes the edit; the close command names it in the session's record. The door opens one path at a time, only after a refusal on that path in the same session, and it never widens what a planning session may write. The check also keeps a log of every decision — allowed and refused — in the project's `.throughliner/` folder, so a write that went through with no line there is a check that never ran, which is the first thing to look at before blaming a rule.

## A command says the plugin's checks aren't running — what do I check?

A chat in a set-up project normally opens with a few lines starting `[Throughliner]`: the project is set up, the date, the version installed, what the queue holds. Every command looks for those lines before doing anything else. Where they are missing, the plugin's small scripts never ran, and Claude says so, names the usual cause and carries on with the command — the procedure still governs, but the safety checks and the opening's facts are absent. The usual cause is Python: it is missing from the machine, or Windows has put a placeholder in its place. In a terminal, `py --version` or `python --version` must print a version number — the hooks use the py launcher where it exists and python otherwise, so either one printing a version is enough; the placeholder prints "Python was not found" instead. Install Python from python.org with "Add python.exe to PATH" ticked, close the terminal, then close and reopen the desktop app. A new chat then shows the `[Throughliner]` lines again. Without Python the plugin fails silently and reports success anyway, which is why the commands look for the lines rather than trusting that the checks ran.

## How do I hold work back until something else happens?

In a planning session, say what the work is waiting for. Claude writes it on the item itself, one of two ways: `Blocked by:` naming another queue item, or `Not before:` naming a date. The item then sits below the `--- Cleared to run above this line ---` line, where a build run never reaches it. Where the thing it waits for isn't in the queue yet — a reply, a site going live — Claude files that as its own item first and holds yours on it, so the wait is a piece of work someone can see rather than a sentence buried inside another item.

You never have to remember any of it. Every planning session opens by checking each held item: has its blocker shipped, has its date passed? Where yes, Claude proposes lifting it and moves it on your word. A date lifts by itself. When several become ready at once, they are cleared one move each, and what you see is the queue tool's line naming each item as cleared and nothing else crossing the line.

## What happens at planning when a cycle's turn is due?

Recurring work — a weekly release, a posting rhythm, a maintenance pass — can be put on a cycle: defined once in your cycles doc with its steps, its cadence and the observable that marks a completed turn. From then on the openings of `/plan` and `/next` compute whether a turn is due and file it into your queue as an ordinary item.

At the planning opening, due cycle work is presented first, ahead of everything else — timing work loses its value waiting in the pack. Nothing is stored between sessions: each opening recomputes from the observable, so skipping a week drifts nothing. What tells you it worked is the opening's line naming the due cycle, and the item for its turn at the top of what Claude presents. A project with no cycles has no doc and pays nothing.

## What is TOOLS.md for?

A file at your project root holding facts about your machine that are expensive to learn twice — a tool installed at a known path, a command that fails from Claude's shell but runs from your terminal, which channel you installed the plugin from. Setup writes the first lines: after the interview it names the command-line tools your project's work plausibly needs, asks once whether any are missing, runs each tool's own version check and writes one line per tool — present with its version or absent, and the date. Where a tool is absent and the first piece of work you described needs it, setup offers the install then; otherwise the absent line stands. Any session adds a fact the moment it learns one.

Where it matters: before Claude hands you a manual walkthrough because it assumes a tool is missing, it reads this file. The failure it fixes is one you feel directly — being talked through by hand something your project had already proved works. Open the file to see what Claude currently believes about your machine, and correct a line if it is wrong.

## Can Claude turn my spec into queue items?

Yes. Ask in a planning session to seed the queue from the spec, and Claude reads your SPEC for features that exist on paper but not in the queue, proposes how coarse to cut them — a few milestones or one item per feature — and writes them into Unprocessed as ordinary captures. Claude offers this itself only when your queue is nearly empty while SPEC still describes unbuilt features. Nothing goes straight into ready work: each capture is weighed like any other, so seeding never green-lights a build. What tells you it worked is the new captures at the bottom of Unprocessed, each naming the spec sentence it came from.

## Why does Claude write to my files before asking, and how do I get it to show me first?

Because the previous version is recoverable without you. Queue items, captures, session records, spec edits and ordinary build edits are written first and then reported in one line naming what landed and where, with a link to open it. Three things are always shown before they happen: a commit message, anything that leaves the machine — a report, a post, a message to another project — and a wholesale conversion of a document git doesn't hold yet. The trade is stated plainly: a file briefly holds text you haven't agreed to, which is cheap in a repository, and the real risk is not noticing — so the report names the artifact precisely enough to open.

To get the opposite, say so: ask to be shown text before it is written, and Claude does that for the rest of the chat. The switch only ever moves toward more showing, and nothing is stored — a fresh chat starts at the default.

## Does Throughliner scrub my documents, and are they safe to publish?

Two things run, and neither promises what people hope. A check scans your queue, spec and session records for things shaped like credentials — keys, tokens, email addresses. And Claude reads what it is about to write against a checklist — personal names, case details, third-party data, identifying paths — at the moments text enters a committed document.

The limit is the point: no pattern can tell whether a sentence quietly identifies a real person, so Throughliner never tells you your documents are scrubbed or safe to publish. For a repository that will be public, the only complete protection is not publishing these documents at all, which is what setup's keep-private question is for.

In a project whose documents live in a repository with no remote — the default for a new nested project, read from the Visibility line in your CLAUDE.md — people are recorded as they are: a collaborator's name stays in a capture, and a risk you have accepted in your spec is not raised again. The scrub still runs on anything leaving the machine.

## What is the "Last session advises" note at the top of my queue?

Advice, not work. When `/close` closes a session with a concrete recommendation for what to do next, it writes that as a note at the top of Unprocessed. The next `/plan` reads it aloud in its opening and deletes it in the same breath — surfacing it is what consumes it. It never moves into Processed and never becomes an item. If you see one, the last session had a view; if it is gone, a planning session has already read it.

## How do my projects send each other mail?

Each project set up with Throughliner has an `INBOX/` folder, kept out of git. To send, tell a session what to say to your other project. Claude checks the recipient has a mailbox and that its ignore rule covers it, shows you the exact text, and on your yes copies it byte for byte into that project's INBOX, printing one line and no path. The first time, it asks for the other project's folder and remembers it inside your INBOX, so you never retype it.

What you see on the other side: the next session there opens with a line naming the waiting message. A planning or build session reads it in full and files what it asks for as a capture in that project's own queue — one project never edits another's files. Your own project's `INBOX/sent.md` keeps a line per message sent, which is how a later change can be checked against what was said.

## What does a build run do with my spec?

It reads SPEC.md once at the start of the run, and checks each item it builds against it. Where the work would contradict a sentence in your spec, the run halts and names the sentence in plain words, and you decide which is wrong — the build or the spec. A build never rewrites your spec: where it finds the spec owes a sentence for something new, it files that sentence as a capture and carries on, so the spec lags visibly, as a queue item, until the next planning session writes it with you there.

## Which command do I run now?

Every piece of work travels one loop. Anything noticed, by you or by Claude, in any chat, becomes a capture in Unprocessed. `/plan` turns captures into agreed work and clears it to run. `/next` builds the cleared work, top down. `/close` records what happened and commits. Then a fresh chat, which learns what happened from the record rather than from memory.

Two things come back to the start. An audit edits nothing: what it finds becomes captures, weighed at the next `/plan`. A build that discovers something files a capture and keeps building. And a step that is yours leaves the loop only when you have done it — a run walks you through it and then leaves it in the queue until you say it is done.

## Why did an old queue item come up before a newer one?

Because planning works through Unprocessed in a fixed order rather than the order things were filed, and the order is built so nothing gets skipped forever. A risk to your data comes first. Then the turn of a cycle that has fallen due. Then whatever the most other entries are waiting on. Then the entries that are both long and old, oldest first. Then everything else, oldest first, alternating so the long ones keep their turn. Where an item keeps being presented before things you filed later, that is the order doing its job. Name the items you want first at the opening's question and they come first; naming three sets the order, not the length of the session.

## Why are my queue items in the order they are?

Because file order records when things landed, and that is more useful than a ranking that goes stale. The planning close makes exactly one pass over the ready section: it moves the steps that are yours and the audits to the end, so the moments needing you sit together after the builds. A step of yours that names builds depending on it stays ahead of them, so a run walks you through it before building them. Everything else reads in the order it was agreed. Open QUEUE.md and you will see the builds first, then the human stops grouped at the bottom.

## Why does my project have two repositories?

A new project is set up nested: the product sits in a subfolder with a clean repository of its own — the one that goes public when you ask — and the folder around it holds your planning documents in a private repository that never gets a remote. Someone landing on the published repository sees the product, not your reasoning. `/close` commits both.

An existing flat project is never forced across. Setup offers the conversion, and offers it again at the moment the project goes public, telling the two shapes apart by whether your repository already has a remote. Where it does, the wrap keeps that repository whole as the inner one and creates the outer around it, moving the planning documents up and changing nothing that points at the published repository. What tells you it worked is the Visibility line in your project's CLAUDE.md naming both repositories.

## I typed /close twice — what did the second one do?

A session makes one commit, at its close. Work you do after that rides the next session's commit. So a second `/close` in the same chat files anything it finds, appends what happened to the session's record under an `## After /close` heading, commits nothing, and says so in one line. Where you want a real second commit now, open a fresh chat and run `/close` there.

The same idea covers a change you make after closing: change a file after `/close` and Claude offers, once, to add what happened to the session's record as that marked tail. Say yes or ignore it — nothing is committed either way, and the tail rides the next close.

## A step of mine says other items are waiting on it — what does that mean?

When a build run or a planning session hands you a step that is yours, it says how many other queue items are blocked on it, read off their `Blocked by:` lines, and names them only where you need to know. Where nothing waits, it says nothing. The count is there so you can weigh the step without holding a list in your head. A step that hands work to another of your projects for completion ends at the send, with anything depending on the outcome filed as its own item first.

## The safety check refused a time from the future — what do I do?

The check refuses, once, a clock time written into a record, the queue or the spec that is later than the clock reads right now. That is the shape a time takes when it was counted up from an earlier reading instead of read. The message names the time and what the clock reads. What Claude should do is read the clock by a command and write what it says; a real past time carries its date in front of it, and a video runtime or an excerpt bound written the same way passes when the sentence says what it times. The same time passes on the next attempt, so it costs one turn. The limit, plainly: a wrong time behind the clock is not caught.

## What do the numbers after a queue edit mean?

After every edit to QUEUE.md a note prints one line per item that grew or shrank, like `+119 words, now 916; work items median 525`. The first number is the change, the second the item's total, the third the median of its section as the queue stands now. It is a fact, not a threshold: an item well above the middle has usually accumulated history that belongs in the session record, leaving the item with its instructions. Nothing is enforced.

## A note says a heading is wrong — how is it fixed?

The queue lint warns when a heading starts with The, A or An, because the outline view truncates headings and the distinguishing words need to come first. Ask for the new heading in words and Claude rewrites it with the queue tool's retitle, keeping the slug and touching nothing in the body. What tells you it worked is the item in QUEUE.md under its new heading with the same `[slug]` at the end.

## What does /catchup show me?

A brief for coming back after time away. Type the catchup command in a chat that has opened, and you get one line per goal in your spec's Goals section — reached, or still the direction, with what the test shows now — then one line per feature with its stage: shipped, cleared to run, waiting, still an idea, or untouched. Then three lines: what a build run would do next, what is waiting on you, and what is held on a date. It also runs the checks a fresh chat runs at its opening, which matters in a chat you picked up days later: one line each where a cycle is due now, a message is waiting, the plugin changed version under the chat, or the date has moved, and nothing where none of those holds — it files a due cycle's capture and reads waiting mail exactly as an opening would, and moves nothing in your queue. Setup asks for the goals — where the project is heading and how you would know it got there — and an existing project is asked once by the top-up.

## A draft I'm asked to edit — where is it and how do I hand it back?

A piece of writing you and Claude finish together is agreed at planning with who drafts first: Claude, with you editing, or you, with Claude reading your text back and responding only where you ask. You can ask for it by saying you want to co-write something, and planning also offers it where the file an item names is one your project's map says a person reads; an ordinary no declines. Where Claude drafts — a post, an article, a message — the draft is written to a `.txt` file in your project's `temp/` folder, which git ignores, and handed to you as a link. Clicking it opens the file in the desktop app's side panel with a save button. Edit, save, and say done; Claude reads it back only then, asks whether there is anything else, and repeats until you say you are finished. On a phone or over remote control the link does not open, so say so and Claude shows the text inline instead. A markdown reader such as Obsidian is recommended for editing drafts outside the app — say the word and the chat hands over `.md` files instead — and the side panel's `.txt` is the fallback, since it is the one file type the panel edits and saves. The folder does not pile up: at the close, a draft whose send is already on the register in `INBOX/sent.md` is deleted, since the register line and the recipient's copy are the record, and everything else in `temp/` is listed with its date and cleared only on your once-asked yes — a file you co-wrote or edited never without it.

## Why is the planning opening so short?

Because a long opening was not getting read. A planning session's first message is a finding sentence or two: how much work is cleared to run and waiting to be processed, held work as a count plus only the items whose hold changed, and one clause — "mail, issues, replies, cycles and the rule checks: nothing" — for every check that found nothing, so you can see the checks ran without reading a list. The one question follows on its own line. The limit: a session that skipped a check could write the same clause.

## Two of us share one queue — whose is what?

Anyone present may file captures. An entry names whose it is to do in an `Assigned to:` line; a line you write in your project's CLAUDE.md, `Unassigned work is <name>'s.`, says whose the rest is. When a step is handed over, Claude names who it is for, and whoever is present can say "not mine, it's hers" — the line is rewritten and the session carries on. A build with someone else's name on it is skipped in one clause in your session. The decisions the method gives "the user" — keeping or deleting work, clearing a risk, approving a send — belong to the one person holding authority.

Two more things you will see. When a teammate has pushed while you were away, your opening carries a line saying the remote has commits this checkout does not, and asks you to pull before working the queue — nothing pulls for you. And where a pull leaves conflict markers in the queue, every queue tool and the close command refuse the file and name the marker's line; two captures appended at the same spot are kept both.

## Claude refused to put my work on a cycle — why?

Because the definition would not have been readable. A cycle or a checklist is written into your cycles doc with fixed fields, and the session opening reads them back; a definition with a field wrong would be silently dropped from every later opening. So the write is checked at the door: a name already defined, a cadence that does not say who declared it or what it was derived from, a chain naming a checklist that does not exist. The refusal says which field and why. Answer its one question and the definition is written. What tells you it worked is the next chat's opening listing the new cycle with what its observable reads. The same check guards the file itself: a definition written by hand with the firing word under the wrong label is refused at the edit, and one already there is named at the opening as carrying neither a cadence nor a trigger, so it never fires nothing silently.

## Claude's reply was sent back for being too long — what happened?

You read a reply and, a moment later, a shorter one arrives saying the same thing. That is the stop check: it counts the prose in a finished reply — list lines, code blocks, quotes and headings left out — and where it runs past 175 words it sends the reply back once with the count and the fix, and Claude answers again shorter. The same check sends back, once, a reply with bold inside a sentence, since bold is meant to lead a line or a list item. Each fires once per chat and then stays quiet, so a second long reply passes; the figure came from measuring the project's own chats, the 90th percentile of reply length, and is a constant in the hook rather than anything you set. Nothing to do on your side: read the shorter reply, which is the one that stands.

## What is LOG/backlinks.md, and should I edit it?

No — it is generated. Every session close rebuilds it from your records: one heading per queue slug and per plugin name (a hook, a skill, a server tool), and under each, one line per record that names it, with the record's filename and the opening words of its index line. Claude opens it at the planning decision step before recommending, at the slug or the name in hand, so an earlier decision about the same thing is found even when it was written up in other words. What it cannot reach is a record that names a thing by neither its slug nor its plugin name. Its first line says it is generated and never edited by hand; an edit would be overwritten at the next close.

## When has my project grown too big for one queue, and when is Throughliner the wrong tool?

Some signs Claude reads for itself, at the start of every planning session, from your queue and your records: the same step of yours put off run after run; the held part of your queue growing while the ready part does not; a piece of work marked as needing a run of its own with more and more ready work piling up ahead of it; a queue too long for one read; or planning sessions that keep ending with the same number of things still to sort. Where one of those holds, the planning opening says so in one line and names the way out: open the part's own subfolder and run `/setup` there, which pops that part out into a project of its own with its own queue (the first-session entry above says how a pop-out works). Nothing moves unless you choose it.

Some signs only you can read, and they say the method may no longer fit at all rather than that the project needs splitting: a queue holding nothing but steps of yours, with no building in it, where the method has become a to-do list with ceremony; several people needing to work on it at once; a thing that has to run continuously rather than in sessions; and you no longer reading the records, since approving them is the whole point. None of these is something Claude can check, so none is reported; they are what to look for in yourself.

## I typed /done and nothing happened — where did it go?

The command that closes a session is `/close` now, or `/throughliner:close` where the short name does not register. Type it where you typed `/done`: at the end of a session, after the building or the planning is finished. What it does is unchanged — it records what happened in your session log, commits, and names the next command in words. What tells you it worked is the commit hash written into the session record's heading, exactly as before. If `/done` still works for you, the plugin under your app is an older build; update it, fully quit and reopen the app, and the new name is there.

## What is MAP.md, and do I write it?

A map of your project, written for Claude to read first in every session: one line per folder and per file a person uses — a document, a slide deck, a spreadsheet, a PDF, an image — saying what it is for, with a set of like files summarised as one line and machinery left out. Setup writes it from the folders it adopts, and an existing project gains it through the top-up. From then on a session writes a line when it creates such a file, and the close names any new or moved path that has no line, so you rarely touch it yourself. Open it when you want to see what Claude believes each folder is for, and correct a line where it is wrong. A folder's files can sit indented beneath its line by their own names, so a path is written once. It puts a folder in view; it does not decide what belongs there.

## Can my steps go onto the task list I already keep?

Yes, where you keep one markdown task list for every project in your notes app. Tell Claude its full path once per project — the top-up asks for it, and it is written as a `Task list:` line in the project's CLAUDE.md; a relative path is refused, since the list sits outside the project. At planning, when a step of yours is kept, Claude recommends whether it needs a walkthrough or is a plain task, and a task gets one line on your list in the same turn: `- [ ] <the task> (<project name>) 📅 <date where there is one>`, with subtasks indented beneath it where they help. Tick the line in your notes app when it is done; the next planning session reads the list, says which of this project's tasks you ticked, and closes each item at its close. A build run reaching such an item says it is on the list and carries on. Claude only ever adds lines — never removes, rewords or reorders one, and the safety check refuses anything else — so the file stays yours to arrange. The date is written the way the Tasks plugin for Obsidian reads it, and what the plugin appends on a tick is ignored on the read-back.
