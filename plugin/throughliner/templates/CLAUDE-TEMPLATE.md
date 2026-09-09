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
- `/done` — record, update docs, commit.

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

## Parts

<!-- Set at setup from the interview's parts question: the project's moving
     parts, one line each naming the part, its folder and which repository
     holds it (a product part sits in the inner repository, a process part
     in the outer), and one last line for a file that belongs to no part.
     A session creating a new file reads this block, chooses the folder, and
     says where it put the file. Left blank where the question was not
     asked; a project with no parts keeps the workshop rule as its default.
     e.g.:
     - the app — `<product subfolder>/` — inner repository (product)
     - recipes and reference material — `research/` — outer repository (process)
     - a file belonging to no part — `workshop/` in the outer repository,
       or `temp/` where it is disposable -->

Parts:

## Language

Language: English

<!-- ▲ PLUGIN-MANAGED — do not edit above this line. ▲ -->

## Project rules

<!-- Add your own rules, conventions, and context below. This section is yours — the plugin won't touch it.
     If your project has specific ways of checking that things work — how to run its tests, what to look at,
     any setup needed first — add them here or point to where they live. Claude follows them as part of
     building, and where a check is one only you can make, it becomes a step in your queue for you to run. -->
