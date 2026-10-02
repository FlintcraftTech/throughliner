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


if __name__ == "__main__":
    print("test_session_start_cycles_facts.py")
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
