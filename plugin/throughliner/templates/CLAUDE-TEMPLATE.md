# CLAUDE.md

<!-- ▼ PLUGIN-MANAGED — do not edit between these markers. Refreshed by /setup's migration, which reports what it replaces. Your own rules belong below the end marker. ▼ -->

This project uses the Throughliner method.

## Project docs

- **SPEC.md** — product truth. What it is, who it's for, how it works.
- **QUEUE.md** — your work, in two sections. **Processed** work is vetted and ready to build, worked top-to-bottom; a `--- Cleared to run above this line ---` line marks how far down is greenlit (below it is decided but not ready yet). **Unprocessed** work is captured ideas and tasks not yet fully processed. Each piece of work is one line: a `#### ` heading naming the work, with a `[slug]` at the end of that heading line and a short rationale beneath it, plus a `captured by you` credit on items you personally raised (anything else is unmarked — Claude is the default author). A work item can carry a leading flavor tag: none means a build (Claude edits files), `[audit]` a review pass (Claude reads and reports), `[user]` a step only you can run. A security or privacy risk Claude surfaces becomes a work item carrying a `Red flag · State: cleared/uncleared` marker — surfaced first each session while uncleared, until it's cleared (either designed out, or you're told the risk plainly and choose to accept it).
- **LOG/** — session records: what was built, tested, decided. One file per session entry, plus index.md one-line summaries naming each entry file.
- **FAQ/** — workflow FAQ. Index loaded at session start; details in FAQ/faq.md.
- **INBOX/** — messages from other projects you run. Anything waiting is mentioned at session start; handled messages move to `INBOX/archive/`. A message going out to another project is always shown to you for approval first.

## Workflow

- `/setup` — scaffold project docs (done if you're reading this).
- `/plan` — queue management, captures, design questions.
- `/next` — execute the top piece of ready work (a build or an audit, by its flavor tag). It can work several cleared pieces of work back-to-back, top-down, stopping at the readiness line or when something genuinely needs you.
- `/rescan` — read back over the conversation and file anything decided or noticed but never written down. Run it whenever, as often as you like; it only looks back as far as the last time you ran it. It files things and leaves the deciding to /plan.
- `/close` — record, update docs, commit.

## Rules for Claude

- SPEC.md is a normal doc, and there's no separate spec-edit step — but **it changes during planning, not during a build**. When a planning decision changes what SPEC says, Claude writes that sentence in the /plan session, with you there. A build never writes product truth: if a build discovers SPEC is missing a sentence, it writes the sentence down as a new queue item and carries on, so SPEC is behind by at most that one sentence until your next planning session — and it's behind visibly, as an item you can see, rather than quietly. The reason is that the session which made a choice shouldn't be the one that certifies it as product truth. A large SPEC rework is ordinary build work that lists SPEC.md among its files, and the safety check still blocks a build from editing SPEC unless it does. Note spec issues for /plan as they come up.

## Visibility

<!-- Set at setup: which repository holds this project's documents, and whether
     they are published anywhere. Left blank until that is settled. In a
     nested project the line names both repositories and their roles, e.g.:
     "Visibility: nested — the outer repository (this folder) holds the
     method's documents and never gets a remote; the inner repository
     (<product subfolder>/) holds only the product and is the one that goes
     public when asked." -->

Visibility:

## Language

Language: English

## Task list

<!-- Optional. The full path of the one markdown task list you keep for every
     project in your notes app. When planning keeps a step of yours that needs
     no walkthrough, Claude appends one checkbox line there — the task, this
     project's name in brackets, and a due date where there is one — and
     reads the file at each planning opening for lines you have ticked. Claude
     only ever adds lines; it never removes or reorders one. Leave the line
     blank to keep no list. An absolute path, e.g.
     "Task list: C:\Users\you\Notes\Tasks.md" -->

Task list:

<!-- ▲ PLUGIN-MANAGED — do not edit above this line. ▲ -->

## Project rules

<!-- Add your own rules, conventions, and context below. This section is yours — the plugin won't touch it.
     If your project has specific ways of checking that things work — how to run its tests, what to look at,
     any setup needed first — add them here or point to where they live. Claude follows them as part of
     building, and where a check is one only you can make, it becomes a step in your queue for you to run.
     With more than one person on the project, one line in exactly this shape says whose an unassigned
     queue entry is — the queue lint reads this shape and no other:
     Unassigned work is <name>'s. -->
