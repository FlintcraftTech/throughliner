# Retired terms

Mechanisms, settings and vocabulary the method has retired. Host-only.

**What this file is for.** Retiring a mechanism automatically puts every rule
that still mentions it into question. This list is what makes that mechanical:
`rule_signals.py`'s REPEALED signal reads it and reports live references, so
leaving a stale reference standing produces a visible signal rather than
silence. That is the sunset principle transferred — the default state does the
work — without a calendar, which does not transfer here.

**It is source data, not derived state.** A retirement is an event, recorded
once at the close that retires it. That is why storing it does not contradict
the rule that the board itself is always computed: derived state is computed,
recorded events are stored.

**How a term gets added.** The close that retires something appends a line
here, as part of the same disposition line the rule gate already requires. One
line, one place, carrying both what the gate decided and what was retired.

**Format** — the parser reads exactly this shape, so keep it:

```
- `term` — what it was, and when it was retired
```

**Retired artifacts are recorded here too, in their own section below.** A retired
step leaves behind the files it produced, and nothing else in the project holds a
list of outputs whose producer no longer exists — so a stale artifact can sit next
to a live one presenting itself as current. The parser reads only the term list, so
the artifact section is for a session to read rather than for the board to scan.

**The old queue's section names are deliberately NOT on this list, and the
attempt is recorded so it is not remade.** `Deferred tests`, `Parked` and the
`Build/Test/Audit` sub-headings are genuinely retired, and
[adopted-claude-md-describes-retired-structure] scoped them here on 2026-08-16.
Adding them was tried and reverted the same hour: the REPEALED signal scans the
whole repository and every hit was correct writing — `migrate-checklist.md` and
`resources/queue-two-section-migration-recipe.md` name the old sections because
their entire job is converting away from them, `setup.md` names them to
recognise the old shape, and `session_start.py`'s epoch history names them to
record what epoch 1 was. No string separates a stale use from a migration doc
quoting the same heading, so the term cannot be made to fire only on the
mistake. Same cry-wolf failure the `ceiling of 200` entry below records, and the
same resolution: **listing them would fire against correct work, which is worse
than not listing them at all.**

Detection for these three lives in `docs/setup.md`'s migration instead, which
carries its own small table and reads **one file** — the project's own
CLAUDE.md, where none of the migration prose above exists. A narrower scanner
over a narrower scope is what makes the check possible; a repo-wide term list is
what made it impossible.

**A term is removed from this list only when no live reference remains** and
the retirement is old enough that nobody will reintroduce it. Removing it
early turns the signal off while the problem stands.

## The list

- `plugin-behaviour.md` — the old always-loaded behaviour document, split into skill-nonspecific-rules.md and the per-skill docs on 2026-08-10
- `docset A` — the heavier per-model docset, retired 2026-08-09; the method runs one docset
- `Working mode:` — a project CLAUDE.md field recording how much text to paste inline, retired 2026-08-09
- `Completion mode:` — a project CLAUDE.md field toggling a planning-time sweep for finished user work, retired 2026-08-09
- `Editor:` — a project CLAUDE.md field naming an editor, retired 2026-08-09; the desktop app opens .md in its own viewer regardless
- `authoring-heuristic.md` — the predecessor to the self-authoring gate, retired when that gate replaced it
- `spec-edit batch` — a batch type for SPEC changes, retired; SPEC is a normal doc any batch can list
- `test flavor` — a work-item flavor for test entries, retired; a check Claude can run is part of building and a check only the user can run is a `[user]` item
- `merge cycle` — branch/blitz/soak/differential-audit/reconcile/merge, retired after failing persistently
- `--- Push required before continuing ---` — a positional queue marker, retired with the old readiness model
- `--- Plan session here: ` — a positional queue marker, retired with the old readiness model
- `Blocks:` — a queue field, retired in favour of `Blocked by:` on the held item
- `Depends on:` — a queue field, retired in favour of `Blocked by:` on the held item
- `Rezip entry:` — the close's required line with its three arms (ready / not yet / none), retired 2026-09-04; the test-rezips entry posts at the Rezip ritual's steps 11 to 15, and the close keeps one arm for an archived entry never posted
- `session-break line` — a manual run bound, retired 2026-08-11; the readiness line is the run bound
- `Wind-down re-scan (/plan's)` — /plan's own full re-scan, retired 2026-08-12; done.md's file-only version runs at every close whatever the session type
- `Step 3: Close out` — /plan's close-out phase, retired 2026-08-12; /done is the only close, and the work-cycle block at plan.md's opening is what now names it
- `Spec-sync gate (build close)` — the build close's sync obligation, retired 2026-08-12; it became a check-against, and the /plan close carries the only sync gate
- `ceiling of 200` — the rule-corpus ceiling in `resources/rule_signals.py`, retired 2026-08-12; the 150–200 instruction figure it derived from was re-validated against the 5-series and found roughly an order of magnitude too tight, so the board reports growth with no threshold and no verdict. **Listed by the phrase naming the number, not as the bare word `CEILING`, which was tried first and fired on the ordinary English word — `plan.md` uses "this ceiling" about an unrelated queue guard. A term that matches correct writing is the cry-wolf failure this list exists to avoid.** The live prose references to the old figure are tracked as [gate-still-declares-the-old-ceiling] rather than by this entry.
- `Completed [user]-item close (in done.md)` — a section of `done.md`, retired 2026-08-12; the close still exists but lives in `done-plan.md`, which now carries every no-build shape
- `Standalone handmade-work close (in done.md)` — a section of `done.md`, retired 2026-08-12; same relocation to `done-plan.md`
- `Planning state:` — a required line in a planning session's LOG entry naming its working file, retired 2026-08-14 with the file itself; the close reads `git diff HEAD -- QUEUE.md` instead
- `close-out phase` — a phase of /plan, retired 2026-08-12 and listed 2026-08-14; /done owns that work and always did, so a user-facing sentence offering to "close out" offers something they cannot do. Every internal use — the build close-out, the audit close-out, the sub-doc headings in `done.md` and its family — is procedure-internal vocabulary and correctly named, so this term is the two-word phrase and never the bare word `close-out`.
- `why-pipeline` — the name of the rationale-carrying mechanism, retired 2026-08-13; it is now **the throughline**, and the plugin is named for it. The mechanism is unchanged; only the name moved, so a live doc still saying `why-pipeline` is stale rather than wrong.
- `the ready list` — the standing plain-English name for the queue's cleared region, retired 2026-08-27. Superseded by the shared-vocabulary rule: the method's own words are what is spoken with the user, each explained once, and no alias is minted for something the method already names. Say **cleared to run**, or the cleared region.
- `keep-step` — the name of /plan's disposition step, retired 2026-08-27; it is **the decision step**. Listed as the hyphenated compound and never as the bare word `keep`, which has many correct live uses here — keep-private, "keeps its own reply", "keep discussing". A term that matches correct writing is the cry-wolf failure this list exists to avoid, as the `CEILING` entry above records.
- `keep/delete` — the name of the two-outcome disposition, retired 2026-08-27. An entry is **processed**, ending in one of three named outcomes: into Processed cleared to run, into Processed held below the line, or deleted. Same cry-wolf caution as the entry above: the compound, never the bare verb.
- `keep-check` — the name of the two-limb buildability check at that step, retired 2026-08-27 with the step's name. The check itself is unchanged.
- `` `[user]` line `` — the name for a `[user]` work item, retired 2026-08-27; it is a `[user]` **item**. Listed as the two-word phrase and never as the bare word `line`, which is load-bearing elsewhere in correct writing — the readiness line, the cleared-to-run line, an index line, "one line either way".
- `--- Build block ---` — the delimited region inside a cleared work item holding what changes in which files, how to tell it worked, and any refusal, retired 2026-08-27. A run reads the item's own text now, so an item's instructions are ordinary prose. **Old delimiters left in existing items are not stale and are not to be swept**: they read as part of the item, which is exactly how the new model treats them.
- `the close` — the docs' name for the /done step, retired 2026-09-10. The step is named by its command, `/done` (or "the /done step" where a noun is needed); "closes the session" and "closing" stay as ordinary English verbs, and "close-out" names the sub-doc's procedure, not the step. The noun is retired under any determiner — "this close", "every close", "an isolated close" — not only after "the".
- `done-audit.md` — the audit-flavour close-out doc, retired 2026-09-10; folded into `done-build.md` as its audit delta.
- `next-audit.md` — the audit-flavour procedure doc, retired 2026-09-10; folded into `next-build.md` as its audit section.

## Retired artifacts

Files a retired step produced, deleted when the step was retired. Recorded so a
later session meeting a reference to one knows it is gone rather than missing.

Retired 2026-08-27 with the build-view architecture
([builds-read-the-queue-again]), and these are the section's first entries:

- `plugin/throughliner/scripts/generate_build_view.py` — the generator that
  assembled the view a run read. Deleted.
- `BUILD-VIEW.md` — the file it wrote beside the queue, regenerated every run
  and deleted at each close. Deleted, and its `.gitignore` line removed from this
  project and from what `/setup` scaffolds.
- `resources/testing/test_build_view.py` and
  `resources/testing/test_build_view_gate_disposition.py` — the generator's
  suites. Deleted; the suite count went 29 → 27.

A consumer project may still have a `BUILD-VIEW.md` line in its own
`.gitignore`. It is harmless — an ignore rule for a file that is never created
again — and is left alone rather than swept.

**Before this, the section was empty.** It was created on 2026-08-14 with the
eviction rule that fills it, and the first two candidates were withdrawn the
same day — see below.

**The withdrawn pair, recorded because the mistake is instructive.**
`plugin/throughliner.zip` and `plugin/zip-archive/` were deleted as a retired
step's leftovers and then restored, because they are not leftovers: the **rezip**
stopped building a zip, but the **release** still packages one and attaches it to
the GitHub Release, and `resources/release-ritual.md` moves, prunes and rebuilds
both paths. So a live release artifact can wear the appearance of a dead one, and
a frozen modification date is consistent with both readings. Before listing
anything here, grep for the path across `resources/` and the shipped package —
the producer that still writes it may not be the one you have in mind.

**The identity strings retired on the same day — `sovereign-implementer`, `si-plugin`, `.si-version`, `.si-format-epoch` — are deliberately NOT listed here, and the reason is this list's own cry-wolf rule.** Every one of them has a correct, permanent live use: the marketplace `renames` map must carry the old slug forever or consumers' settings stop migrating, and `session_start.py` and `setup.md` name both old marker files on purpose, as the fallback that recognises a pre-rename project. Listing them would make REPEALED fire on machinery that is working exactly as designed — the same failure the bare word `CEILING` produced. `throughliner` is now the only correct name in new writing; that is enforced by reading, not by this list.
