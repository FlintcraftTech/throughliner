#!/usr/bin/env python3
"""Regression tests for session_start.py's cycles facts line.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_session_start_cycles_facts.py

No test framework, matching the suites alongside it: this project has no test
runner, and `python` on the author's machine resolves to an application's
bundled interpreter that has no pytest.

What this pins is the artifact the due-ness check keys on. The check exists at
three sites and fired at none of them, because nothing in a session opening
said a cycles doc was there — so the absence of this line is exactly the
failure, and a project with no doc getting no line is the other half of it.
"""

import datetime
import importlib.util
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "session_start.py")

_spec = importlib.util.spec_from_file_location("session_start", HOOK)
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)

_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        _failures.append(name)


def project(cycles_doc=None):
    d = tempfile.mkdtemp(prefix="session-start-cycles-")
    if cycles_doc is not None:
        with open(os.path.join(d, "CYCLES.md"), "w", encoding="utf-8") as f:
            f.write(cycles_doc)
    return d


DEMO = """# CYCLES

## Weekly release [weekly-release]
Steps: bump, sweep, package, publish the pre-release.
Cadence: weekly, declared by the user.
Observable: the newest GitHub release's date — last turn 2026-07-01.

## Posting rhythm [posting-rhythm]
Steps: draft, approve, post, write the register line.
Cadence: fortnightly, derived from the sent register.
Observable: the newest line in INBOX/sent.md
"""


def test_a_doc_produces_a_definition_per_cycle():
    d = project(DEMO)
    facts = hook.cycles_facts(d)
    shutil.rmtree(d, ignore_errors=True)
    check("both definitions are read", facts is not None and len(facts) == 2,
          repr(facts))
    if not facts:
        return
    slugs = [row[0] for row in facts]
    check("the slugs come off the headings",
          slugs == ["weekly-release", "posting-rhythm"], repr(slugs))
    check("the cadence line travels as written",
          facts[0][2] == "weekly, declared by the user.", repr(facts[0][2]))
    check("the observable travels as written",
          facts[0][3].startswith("the newest GitHub release's date"),
          repr(facts[0][3]))
    check("a date inside the observable is surfaced as the last turn",
          facts[0][4] == "2026-07-01", repr(facts[0][4]))
    check("an observable with no date reports none",
          facts[1][4] is None, repr(facts[1][4]))


WRAPPED = """# CYCLES

## Weekly release [weekly-release]

**Cadence:** weekly, Wednesday — declared by the user
(decision of 2026-08-22), rather than derived from the record.

**Observable:** the published date of the latest GitHub release,
read with `gh release list` — last turn 2026-08-27.

**Steps of one turn.**
1. Check the branch is `main`.
"""


def test_a_wrapped_field_reads_whole():
    """The live instance that found this: the first draft wrapped both fields.

    Before the continuation, the cadence was cut at the line break and reported
    as "weekly, Wednesday — declared by the user" with a trailing comma — which
    still reads like a cadence, so nothing downstream could tell it was cut.
    """
    d = project(WRAPPED)
    facts = hook.cycles_facts(d)
    shutil.rmtree(d, ignore_errors=True)
    check("one definition is read", facts is not None and len(facts) == 1,
          repr(facts))
    if not facts:
        return
    check("a wrapped cadence continues to the end of its sentence",
          facts[0][2].endswith("rather than derived from the record."),
          repr(facts[0][2]))
    check("a wrapped observable continues too",
          "last turn 2026-08-27" in (facts[0][3] or ""), repr(facts[0][3]))
    check("the date in the wrapped continuation is still found",
          facts[0][4] == "2026-08-27", repr(facts[0][4]))
    check("a following field line ends the continuation",
          "Steps of one turn" not in (facts[0][3] or ""), repr(facts[0][3]))


def test_a_blank_line_ends_a_field():
    """The ordinary case, unchanged: a field followed by prose stops at the blank."""
    d = project("# CYCLES\n\n## Thing [thing]\nCadence: weekly.\n\n"
                "Loose prose about the cycle that is not part of the field.\n")
    facts = hook.cycles_facts(d)
    shutil.rmtree(d, ignore_errors=True)
    check("prose after a blank line stays out of the cadence",
          facts and facts[0][2] == "weekly.", repr(facts))


MIXED = """# CYCLES

## Weekly release [weekly-release]
Cadence: weekly, declared by the user.
Observable: the newest GitHub release's date — last turn 2026-07-01.

## Rezip [rezip]
Steps: bump, sweep, install, archive.
Trigger: the word "rezip".
"""


def test_checklists_are_read_and_kept_out_of_the_cycles():
    """A checklist has a trigger and no cadence, so the two never mix.

    The discriminator is what the definition carries, which is what makes the
    format additive: every existing cycles doc has cadences and stays valid.
    """
    d = project(MIXED)
    cycles = hook.cycles_facts(d)
    checklists = hook.checklists_facts(d)
    shutil.rmtree(d, ignore_errors=True)
    check("the checklist is not reported as a cycle",
          cycles is not None and [row[0] for row in cycles] == ["weekly-release"],
          repr(cycles))
    check("the checklist is reported on its own",
          checklists is not None and len(checklists) == 1
          and checklists[0][0] == "rezip", repr(checklists))
    if checklists:
        check("the trigger word travels as written",
              checklists[0][2] == 'the word "rezip".', repr(checklists[0][2]))


def test_a_doc_of_only_cycles_has_no_checklists():
    d = project(DEMO)
    checklists = hook.checklists_facts(d)
    shutil.rmtree(d, ignore_errors=True)
    check("a doc with no checklists reports an empty list, not None",
          checklists == [], repr(checklists))


def test_no_doc_is_silent():
    """A project with no cycles pays nothing — the whole point of the trigger."""
    d = project(None)
    facts = hook.cycles_facts(d)
    shutil.rmtree(d, ignore_errors=True)
    check("no cycles doc returns None rather than an empty report",
          facts is None, repr(facts))


def test_a_doc_with_no_definitions_reports_empty():
    """Present but unparseable is its own case, and must not read as 'no cycles'."""
    d = project("# CYCLES\n\nNotes with no headings carrying a slug.\n")
    facts = hook.cycles_facts(d)
    shutil.rmtree(d, ignore_errors=True)
    check("a doc with no slug headings returns an empty list, not None",
          facts == [], repr(facts))


CHAINED = """# CYCLES

## Weekly release [weekly-release]

**Cadence:** weekly on Wednesday, declared by the user.

**Anchor:** Wednesday morning. Every lead below counts back from it.

**Chain:** the checklists of one turn, in order, each with its lead:
1. **Maintenance sweep [maintenance-sweep]** — due by the first session on or
   after Monday (two days before the anchor). Its findings land in Unprocessed.
2. **Findings processed and built** — by Tuesday's sessions. No checklist of its
   own.
3. **Rezip [rezip]** — the build that carries the subtraction.
4. **Release [release]** — the anchor. Refuses while step 2 is incomplete.

**Observable:** the published date of the latest GitHub release.

## Rezip [rezip]
Trigger: the word "rezip".

## Release [release]
Trigger: the word "release".
"""


def test_a_chain_is_computed_for_each_weekday():
    """The live chain: sweep Monday, release Wednesday, nothing any other day.

    Dates only — the hook never says whether a checklist whose date arrived still
    needs running; the skill reads the record for that.
    """
    import datetime
    d = project(CHAINED)
    chains = hook.cycle_chains(d, datetime.date(2026, 9, 3))  # a Thursday
    check("one chained cycle is read", chains is not None and len(chains) == 1,
          repr(chains))
    if chains:
        chain = chains[0]
        check("the anchor's next date is the coming Wednesday",
              chain["anchor_date"] == "2026-09-09", repr(chain))
        checklists = dict(chain["checklists"])
        check("the sweep is due two days before the anchor",
              checklists.get("maintenance-sweep") == "2026-09-07", repr(checklists))
        check("the release is due on the anchor",
              checklists.get("release") == "2026-09-09", repr(checklists))
        check("a checklist with no lead reports none rather than a guess",
              "rezip" in checklists and checklists["rezip"] is None, repr(checklists))
        check("the step naming no checklist is not listed",
              len(chain["checklists"]) == 3, repr(chain["checklists"]))
    expected = {0: ["maintenance-sweep"], 1: [], 2: ["release"], 3: [], 4: [],
                5: [], 6: []}
    monday = datetime.date(2026, 9, 7)
    for offset in range(7):
        day = monday + datetime.timedelta(days=offset)
        due = [checklist for _cycle, checklist in hook.checklists_due_on(d, day)]
        check("due on %s: %s" % (day.strftime("%A"), expected[offset] or "nothing"),
              due == expected[offset], repr(due))
    plain = hook.cycle_chains(project(DEMO), datetime.date(2026, 9, 3))
    check("a cycle with no chain is not listed", plain == [], repr(plain))
    shutil.rmtree(d, ignore_errors=True)


def test_a_your_part_field_leaves_the_chain_dates_unchanged():
    """A step whose definition carries a `Your part:` field parses, and the
    chain's dates are what they are without it; nothing about a task line is
    carried on the chain."""
    import datetime
    doc = CHAINED.replace(
        '## Release [release]\nTrigger: the word "release".',
        '## Release [release]\nTrigger: the word "release".\n\n'
        '**Your part:** Send the plan command and say yes when it asks '
        'whether to release the beta\n')
    plain = project(CHAINED)
    d = project(doc)
    day = datetime.date(2026, 9, 3)
    chains = hook.cycle_chains(d, day)
    baseline = hook.cycle_chains(plain, day)
    shutil.rmtree(d, ignore_errors=True)
    shutil.rmtree(plain, ignore_errors=True)
    check("the chain is still read with the field present",
          chains is not None and len(chains) == 1, repr(chains))
    check("the chain's dates are unchanged by the field",
          chains == baseline, repr(chains))
    check("no task-line key rides the chain",
          bool(chains) and "task_lines" not in chains[0], repr(chains))


DATED = """# CYCLES

## Cohort delivery [cohort]

**Cadence:** per cohort, declared by the user 2026-09-26.

**Anchor:** 2026-11-03, the cohort's first day.

**Chain:** the calendar around one cohort:
1. **Go or no-go [go-no-go]** — two days before the anchor.
2. **Set-up [set-up]** — the anchor.
3. **Wrap [wrap]** — the day after the anchor.
4. **Delete recordings [delete-recordings]** — 7 days after the anchor.

**Observable:** the wrap record in LOG/.

## Go or no-go [go-no-go]
Trigger: its chain date.

## Set-up [set-up]
Trigger: its chain date.

## Wrap [wrap]
Trigger: its chain date.

## Delete recordings [delete-recordings]
Trigger: its chain date.
"""


def test_a_date_anchor_with_forward_leads_and_the_spent_state():
    """[event-anchored-checklist-chain]: a chain hung on one booked date
    computes its steps from that date, forward leads land after it, and once
    the last step's date has passed the chain is spent and files nothing."""
    import datetime
    d = project(DATED)
    chains = hook.cycle_chains(d, datetime.date(2026, 10, 1))
    check("the date-anchored chain is read", chains is not None
          and len(chains) == 1, repr(chains))
    if chains:
        chain = chains[0]
        due = dict(chain["checklists"])
        check("the anchor date is the booked date",
              chain["anchor_date"] == "2026-11-03", repr(chain))
        check("two days before lands before the anchor",
              due.get("go-no-go") == "2026-11-01", repr(due))
        check("the day after lands the day after",
              due.get("wrap") == "2026-11-04", repr(due))
        check("seven days after lands a week on",
              due.get("delete-recordings") == "2026-11-10", repr(due))
        check("ahead of the event the chain is not spent",
              chain.get("spent") is False, repr(chain))
    on_wrap = hook.checklists_due_on(d, datetime.date(2026, 11, 4))
    check("the wrap is due on its day",
          on_wrap == [("cohort", "wrap")], repr(on_wrap))
    later = hook.cycle_chains(d, datetime.date(2026, 11, 20))
    check("past the last step the chain reports spent",
          later and later[0].get("spent") is True, repr(later))
    check("a spent chain has no step due, even on a matching date",
          hook.checklists_due_on(d, datetime.date(2026, 11, 20)) == [],
          repr(later))
    shutil.rmtree(d, ignore_errors=True)


SEQUENTIAL = """# CYCLES

## Release chain [release-chain]

**Cadence:** on the user's word, declared by the user 2026-10-03.

**Chain:** the steps of one turn, in order, each firing on the one before it:
1. **Beta pick [beta-pick]** — on the user's word.
2. **Maintenance sweep [maintenance-sweep]** — after [beta-pick].
3. **Rezip [rezip]** — after [maintenance-sweep].
4. **Release [release]** — after [rezip]; **Condition:** one planning record
   and one build-run record dated after the chain's [rezip] record.

**Observable:** the published date of the latest GitHub release.

## Beta pick [beta-pick]
Trigger: the user's word.

## Maintenance sweep [maintenance-sweep]
Trigger: its place in the chain.

## Rezip [rezip]
Trigger: its place in the chain.

## Release [release]
Trigger: its place in the chain.
"""


def _record(d, name, when, kind=""):
    os.makedirs(os.path.join(d, "LOG"), exist_ok=True)
    body = "---\nsummary: x\n---\n# r\n\nRecorded %s, read from the clock.\n\n" % when
    if kind == "processed":
        body += "**Work processed:** kept — [x].\n"
    elif kind == "built":
        body += "**Files touched:** `x`.\n"
    with open(os.path.join(d, "LOG", name), "w", encoding="utf-8") as f:
        f.write(body)


def test_a_sequential_chain_reads_its_due_step_from_the_record():
    """[sequential-release-chain]: no dates; each step fires on the one
    before it, the first on the user's word, and a conditioned step waits
    until the record shows the condition holding."""
    d = project(SEQUENTIAL)
    state = hook.sequential_chains(d)
    check("a sequential chain is read", state is not None and len(state) == 1
          and state[0]["slug"] == "release-chain", repr(state))
    check("it is kept out of the dated chains",
          hook.cycle_chains(d, datetime.date(2026, 10, 4)) == [],
          repr(hook.cycle_chains(d, datetime.date(2026, 10, 4))))
    if state:
        check("with no records the chain waits on the user's word",
              state[0]["status"] == "waiting" and state[0]["due"] is None
              and "user's word" in state[0]["detail"], repr(state[0]))
        check("the steps parse with what fires them",
              [(s["slug"], s["fires"]) for s in state[0]["steps"]]
              == [("beta-pick", "word"), ("maintenance-sweep", "beta-pick"),
                  ("rezip", "maintenance-sweep"), ("release", "rezip")],
              repr(state[0]["steps"]))
        check("the condition clause travels on its step",
              state[0]["steps"][3]["condition"].startswith(
                  "one planning record"), repr(state[0]["steps"][3]))
    check("nothing is due while the chain waits",
          hook.checklists_due_on(d, datetime.date(2026, 10, 4)) == [],
          repr(hook.checklists_due_on(d, datetime.date(2026, 10, 4))))

    _record(d, "2026-10-01-beta-pick.md", "2026-10-01 12:21")
    state = hook.sequential_chains(d)[0]
    check("a pick record makes the next step due",
          state["status"] == "due" and state["due"] == "maintenance-sweep",
          repr(state))
    check("the due step is listed as due on any day",
          hook.checklists_due_on(d, datetime.date(2026, 10, 9))
          == [("release-chain", "maintenance-sweep")],
          repr(hook.checklists_due_on(d, datetime.date(2026, 10, 9))))

    _record(d, "2026-09-28-maintenance-sweep.md", "2026-09-28 10:00")
    state = hook.sequential_chains(d)[0]
    check("a step's record older than the chain's start does not count",
          state["due"] == "maintenance-sweep", repr(state))
    _record(d, "2026-10-02-maintenance-sweep.md", "2026-10-02 10:00")
    _record(d, "2026-10-03-rezip.md", "2026-10-03 09:43", "built")
    _record(d, "2026-10-03-some-item.md", "2026-10-03 00:46", "built")
    state = hook.sequential_chains(d)[0]
    check("with a rezip record and no later planning record the release is held",
          state["status"] == "held" and state["due"] is None
          and "a planning record" in state["detail"]
          and "a build-run record" in state["detail"], repr(state))
    _record(d, "2026-10-04-plan.md", "2026-10-04 17:34", "processed")
    state = hook.sequential_chains(d)[0]
    check("one later planning record alone still holds the release",
          state["status"] == "held" and "a build-run record" in state["detail"]
          and "a planning record" not in state["detail"], repr(state))
    _record(d, "2026-10-05-build.md", "2026-10-05 09:00", "built")
    state = hook.sequential_chains(d)[0]
    check("with both records after the rezip the release is due",
          state["status"] == "due" and state["due"] == "release", repr(state))
    _record(d, "2026-10-06-release.md", "2026-10-06 09:00")
    state = hook.sequential_chains(d)[0]
    check("every step recorded reads as complete, the next chain on the user's word",
          state["status"] == "complete" and state["due"] is None
          and "user's word" in state["detail"], repr(state))
    _record(d, "2026-10-07-beta-pick.md", "2026-10-07 09:00")
    state = hook.sequential_chains(d)[0]
    check("a new pick starts a new chain, the old records not counted",
          state["status"] == "due" and state["due"] == "maintenance-sweep",
          repr(state))

    both = project(SEQUENTIAL.replace(
        "**Chain:**", "**Anchor:** Wednesday.\n\n**Chain:**"))
    state = hook.sequential_chains(both)
    check("a chain with both an anchor and sequential items is malformed",
          state and state[0]["status"] == "malformed"
          and "Anchor" in state[0]["detail"], repr(state))
    check("a malformed chain files nothing",
          hook.checklists_due_on(both, datetime.date(2026, 10, 4)) == [])
    bad = project(SEQUENTIAL.replace("after [maintenance-sweep]",
                                     "after [release]"))
    state = hook.sequential_chains(bad)
    check("a step firing after a step not earlier in the chain is malformed",
          state and state[0]["status"] == "malformed"
          and "[rezip] fires after [release]" in state[0]["detail"],
          repr(state))
    anchored = project(CHAINED)
    check("a dated chain is not read as sequential",
          hook.sequential_chains(anchored) == [], repr(hook.sequential_chains(anchored)))
    for folder in (d, both, bad, anchored):
        shutil.rmtree(folder, ignore_errors=True)


def test_the_opening_names_a_sequential_chain():
    """Driven whole: the cycles line carries the chain's steps and its state."""
    import json
    import subprocess
    d = project(SEQUENTIAL)
    for name in ("SPEC.md", "QUEUE.md"):
        with open(os.path.join(d, name), "w", encoding="utf-8") as f:
            f.write("# QUEUE\n\n## Processed\n\n## Unprocessed\n"
                    if name == "QUEUE.md" else "# SPEC\n")
    _record(d, "2026-10-01-beta-pick.md", "2026-10-01 12:21")
    proc = subprocess.run(
        [sys.executable, HOOK],
        input=json.dumps({"cwd": d, "session_id": "sequential-test"}),
        capture_output=True, text=True, encoding="utf-8", cwd=d, timeout=120)
    try:
        out = json.loads(proc.stdout) if proc.stdout.strip() else {}
        context = (out.get("hookSpecificOutput") or {}).get(
            "additionalContext") or out.get("additionalContext") or ""
    except ValueError:
        context = proc.stdout
    check("the cycles line names the chain as sequential with its due step",
          "[release-chain] chain — sequential" in context
          and "[maintenance-sweep] is due, after [beta-pick]" in context,
          context[-1500:])
    check("no anchor or date is reported for it",
          "anchor" not in context.split("[release-chain] chain")[1].split(";")[0]
          if "[release-chain] chain" in context else False, context[-1500:])
    shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    print("test_session_start_cycles_facts.py")
    test_a_sequential_chain_reads_its_due_step_from_the_record()
    test_the_opening_names_a_sequential_chain()
    test_a_chain_is_computed_for_each_weekday()
    test_a_your_part_field_leaves_the_chain_dates_unchanged()
    test_a_date_anchor_with_forward_leads_and_the_spent_state()
    test_a_doc_produces_a_definition_per_cycle()
    test_a_wrapped_field_reads_whole()
    test_a_blank_line_ends_a_field()
    test_checklists_are_read_and_kept_out_of_the_cycles()
    test_a_doc_of_only_cycles_has_no_checklists()
    test_no_doc_is_silent()
    test_a_doc_with_no_definitions_reports_empty()
    print()
    if _failures:
        print(f"{len(_failures)} failure(s): " + ", ".join(_failures))
        sys.exit(1)
    print("all passed")
