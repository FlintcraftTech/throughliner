#!/usr/bin/env python3
"""Regression tests for session_start.py's queue dependency facts.

Host-only dev artifact — not shipped in the plugin package.

Run:  py resources/testing/test_session_start_queue_facts.py

No test framework, matching the suites alongside it: this project has no test
runner, and `python` on the author's machine resolves to an application's
bundled interpreter that has no pytest.

The hook is imported directly rather than run as a subprocess, because what
needs pinning is what the counting function computes, not the payload wrapper.
"""

import importlib.util
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "session_start.py")

_spec = importlib.util.spec_from_file_location("session_start", HOOK)
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)

MARKER = "--- Cleared to run above this line ---"

_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        _failures.append(name)


def queue_file(processed="", unprocessed=""):
    d = tempfile.mkdtemp(prefix="session-start-test-")
    path = os.path.join(d, "QUEUE.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(
            "# QUEUE\n\nIntro prose mentioning the "
            + MARKER
            + " marker.\n\n## Processed\n\n"
            + processed
            + "\n" + MARKER + "\n\n## Unprocessed\n\n"
            + unprocessed
        )
    return d, path


def test_marker_text_in_prose_does_not_move_the_line():
    """An item may quote the marker text while describing how the queue works.

    session_start once matched that text as a substring, so such a sentence
    became the readiness line for everything below it — and the cleared/held
    counts it reports open every session. The counts must not move.
    """
    quoting = (
        "#### An item that describes the queue [talker]\n"
        "This explains that /next builds from above the\n"
        + MARKER + " marker, which is what bounds a run.\n"
    )
    plain = "#### An ordinary second item [quiet]\nRationale.\n"

    d1, p1 = queue_file(processed="#### First [one]\nRationale.\n" + plain)
    baseline = hook._queue_dependency_facts(p1)
    shutil.rmtree(d1, ignore_errors=True)

    d2, p2 = queue_file(processed=quoting + plain)
    facts = hook._queue_dependency_facts(p2)
    shutil.rmtree(d2, ignore_errors=True)

    check("a queue whose prose says nothing reads as 2 cleared, 0 held",
          baseline is not None and baseline[0] == 2 and baseline[1] == 0,
          repr(baseline))
    check("prose quoting the marker leaves both items cleared",
          facts is not None and facts[0] == 2,
          repr(facts))
    check("prose quoting the marker holds nothing below the line",
          facts is not None and facts[1] == 0,
          repr(facts))


def test_the_real_marker_still_splits_the_section():
    """The anchored predicate must still find the marker it is looking for."""
    d, path = queue_file(
        processed=(
            "#### Ready work [ready]\nRationale.\n"
        ),
        unprocessed="#### A capture [cap]\nRationale.\n",
    )
    # Rewrite with one item below the marker.
    with open(path, "w", encoding="utf-8") as f:
        f.write(
            "# QUEUE\n\n## Processed\n\n"
            "#### Ready work [ready]\nRationale.\n\n"
            + MARKER + "\n\n"
            "#### Held work [held]\nRationale.\nBlocked by: [cap]\n\n"
            "## Unprocessed\n\n#### A capture [cap]\nRationale.\n"
        )
    facts = hook._queue_dependency_facts(path)
    shutil.rmtree(d, ignore_errors=True)
    check("the real marker separates cleared from held",
          facts is not None and facts[0] == 1 and facts[1] == 1,
          repr(facts))


def test_waiting_to_be_planned_is_the_fourth_number():
    """[queue-facts-zero-reads-as-empty]: a project whose whole queue is
    unprocessed read as an empty slate because the line named cleared, held
    and blockers only. The count of Unprocessed entries is the fourth number,
    emitted even when zero, and takes no part in the floor derivation."""
    # The tester's shape: 0 cleared, 0 held, 3 waiting.
    d, path = queue_file(
        processed="",
        unprocessed=("#### One [one]\nR.\n#### Two [two]\nR.\n"
                     "#### Three [three]\nR.\n"),
    )
    facts = hook._queue_dependency_facts(path)
    shutil.rmtree(d, ignore_errors=True)
    check("0 cleared, 0 held, 3 waiting to be planned",
          facts is not None and facts[0] == 0 and facts[1] == 0
          and facts[-1] == 3,
          repr(facts))

    # All zero: the count is still a computed zero, never absent.
    d, path = queue_file(processed="", unprocessed="")
    facts = hook._queue_dependency_facts(path)
    shutil.rmtree(d, ignore_errors=True)
    check("an empty queue reads 0 waiting, not a missing field",
          facts is not None and len(facts) == 8 and facts[-1] == 0,
          repr(facts))


def test_qualified_blocked_by_line_still_parses():
    """A held item's `Blocked by:` may carry trailing words (`until built` is
    a capture's, but a line is read as a line): the slug is still read out
    and the blocker counted ([capture-hold-says-designed-or-shipped])."""
    d, path = queue_file(
        processed=("#### Cleared [one]\nR.\n" + MARKER + "\n"
                   "#### Held [two]\nR.\nBlocked by: [three] until built\n"),
        unprocessed="#### Three [three]\nR.\n",
    )
    facts = hook._queue_dependency_facts(path)
    shutil.rmtree(d, ignore_errors=True)
    check("1 cleared, 1 held, its blocker read despite the trailing words",
          facts is not None and facts[0] == 1 and facts[1] == 1
          and facts[2] == 1 and ("two", "three") in facts[3],
          repr(facts))


if __name__ == "__main__":
    print("test_session_start_queue_facts.py")
    test_qualified_blocked_by_line_still_parses()
    test_marker_text_in_prose_does_not_move_the_line()
    test_the_real_marker_still_splits_the_section()
    test_waiting_to_be_planned_is_the_fourth_number()
    print()
    if _failures:
        print(f"{len(_failures)} failure(s): " + ", ".join(_failures))
        sys.exit(1)
    print("all passed")
