#!/usr/bin/env python3
"""Regression tests for reorder_queue.py's reporting.

Run: python plugin/throughliner/scripts/test_reorder_queue.py

Why this file exists, and why its sibling defect has no test. Three faults have
now been found in this script's OUTPUT rather than its writes — across every
use, the file operations were correct and every fault was in what the tool said
about them. That matters more than a cosmetic wrong message: the whole point of
the mover is that a session does not have to hand-verify queue structure, so its
messages are trusted and acted on without re-reading the file.

[mover-console-encoding-mangles-output] deliberately shipped without a test,
because the failure would not reproduce in any shell available here. This one
reproduces deterministically from a fixture, so it gets one.
"""

import os
import re
import subprocess
import sys
import tempfile

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reorder_queue.py")

# The fixture that reproduces the bug: a held item whose `Blocked by:` names the
# item being moved. That is not an exotic shape — it is exactly what exists
# whenever the move matters, because clearing an item that other work waits on
# is the case the report is most trusted in.
#
# TWO cleared items, deliberately. An item's block runs to the next heading, so
# "AFTER the last cleared item" spans the marker and legitimately lands the
# moved item below it — the positional ambiguity this report was written to
# surface in the first place. Anchoring to the FIRST of two puts the moved item
# unambiguously above the marker, which is what makes a wrong report wrong
# rather than merely surprising.
FIXTURE = """# QUEUE

## Processed

#### First cleared item [alpha]
Rationale for alpha.

#### Second cleared item [delta]
Rationale for delta.

--- Cleared to run above this line ---

#### A held item [gamma]
Rationale for gamma.
Blocked by: [beta]

## Unprocessed

#### The item being moved [beta]
Rationale for beta.
"""

failures = []


def check(name, condition, detail=""):
    if condition:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name} {detail}")
        failures.append(name)


def run_move(queue_path):
    return subprocess.run(
        [sys.executable, SCRIPT, queue_path,
         "--move-section", "beta", "Unprocessed", "Processed",
         "--position", "AFTER", "alpha"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def test_side_of_marker_report():
    """The moved item lands above the marker, and the report must say so."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(FIXTURE)

        result = run_move(path)
        output = result.stdout + result.stderr

        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

        marker_i = next(i for i, l in enumerate(lines)
                        if "Cleared to run above this line" in l)
        beta_i = next(i for i, l in enumerate(lines)
                      if l.startswith("#### ") and l.rstrip().endswith("[beta]"))

        check("file places the item above the marker", beta_i < marker_i,
              f"(item at {beta_i}, marker at {marker_i})")
        check("report says ABOVE", "ABOVE" in output, f"got: {output.strip()}")
        check("report does not say BELOW", "BELOW" not in output,
              f"got: {output.strip()}")
        check("report does not call it waiting",
              "NOT cleared to run" not in output, f"got: {output.strip()}")
        check("the held item's Blocked by line survives the move",
              any(l.strip() == "Blocked by: [beta]" for l in lines))


def test_report_agrees_with_file():
    """The tool's claim and the file must never disagree — the real defect."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(FIXTURE)

        result = run_move(path)
        output = result.stdout + result.stderr

        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        marker_i = next(i for i, l in enumerate(lines)
                        if "Cleared to run above this line" in l)
        beta_i = next(i for i, l in enumerate(lines)
                      if l.startswith("#### ") and l.rstrip().endswith("[beta]"))

        said_above = "ABOVE" in output
        is_above = beta_i < marker_i
        check("report agrees with the file", said_above == is_above,
              f"(said ABOVE={said_above}, actually above={is_above})")


def test_move_section_marker_after_the_moved_item_is_refused():
    """Anchoring the marker to the item just placed, with a cleared item
    below it, is the drop guard's case: delta would be swept below the line
    with nothing saying why. Refused, and the file untouched.

    This case used to assert the opposite — that the call succeeds and the
    marker lands after beta — and predates the guard (added 2026-09-06).
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(FIXTURE)

        result = subprocess.run(
            [sys.executable, SCRIPT, path,
             "--move-section", "beta", "Unprocessed", "Processed",
             "--position", "AFTER", "alpha", "--marker-after", "beta"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        output = result.stdout + result.stderr

        check("the sweep behind the moved item is refused",
              result.returncode != 0, f"exit {result.returncode}: {output}")
        check("the refusal names the item it would drop",
              "DROP" in output and "[delta]" in output, f"got: {output}")
        check("nothing was written",
              open(path, "r", encoding="utf-8").read() == FIXTURE)


def test_move_section_applies_marker_after():
    """A cross-section move can place the readiness marker in the same call.

    Moving an item into Processed AND clearing it is the ordinary shape of
    keeping work at /plan, so it must be one command. It used to be two: this
    branch accepted --marker-after and silently ignored it, exiting 0 with the
    move applied and the marker untouched. `--marker-after` names the LAST
    item that should stay cleared — delta, not the item just placed.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(FIXTURE)

        result = subprocess.run(
            [sys.executable, SCRIPT, path,
             "--move-section", "beta", "Unprocessed", "Processed",
             "--position", "AFTER", "alpha", "--marker-after", "delta"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        output = result.stdout + result.stderr

        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        marker_i = next(i for i, l in enumerate(lines)
                        if "Cleared to run above this line" in l)
        beta_i = next(i for i, l in enumerate(lines)
                      if l.startswith("#### ") and l.rstrip().endswith("[beta]"))
        delta_i = next(i for i, l in enumerate(lines)
                       if l.startswith("#### ") and l.rstrip().endswith("[delta]"))

        check("the call succeeds", result.returncode == 0,
              f"exit {result.returncode}: {output.strip()}")
        check("the item landed in Processed above the marker", beta_i < marker_i,
              f"(item at {beta_i}, marker at {marker_i})")
        check("the marker sits after the last item that should stay cleared",
              beta_i < delta_i < marker_i,
              f"(beta {beta_i}, delta {delta_i}, marker {marker_i})")
        check("report says ABOVE", "ABOVE" in output, f"got: {output.strip()}")


def test_move_section_marker_failure_writes_nothing():
    """Both halves, or neither. A half-applied queue edit is worse than a refusal.

    The readiness marker decides how much work an unattended /next run may
    build with nobody present, so a move that lands while its marker placement
    fails is the dangerous outcome, not the tidy one.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(FIXTURE)

        result = subprocess.run(
            [sys.executable, SCRIPT, path,
             "--move-section", "beta", "Unprocessed", "Processed",
             "--position", "AFTER", "alpha", "--marker-after", "no-such-slug"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        output = result.stdout + result.stderr

        with open(path, "r", encoding="utf-8") as f:
            after = f.read()

        check("the call refuses", result.returncode != 0,
              f"exit {result.returncode}")
        check("the error names the bad marker slug", "no-such-slug" in output,
              f"got: {output.strip()}")
        check("the file is byte-for-byte unchanged", after == FIXTURE,
              "the move was applied despite the marker failing")


def _load_module():
    """Import reorder_queue.py by path so its helpers can be called directly."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("reorder_queue", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_delete_reports_only_what_landed():
    """The success line must mean the item really left the file.

    A --delete once printed its normal success line, exited zero, and left the
    item in place. /next reads that line as proof an item was built and
    removed, so a false success breaks the one guarantee the copy-per-item
    design rests on. This asserts the ordinary path genuinely lands.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(FIXTURE)

        result = subprocess.run(
            [sys.executable, SCRIPT, path, "--delete", "delta", "Processed"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        with open(path, "r", encoding="utf-8") as f:
            after = f.read()

        check("the delete succeeds", result.returncode == 0,
              f"exit {result.returncode}: {result.stderr.strip()}")
        check("the item is really gone from the file", "[delta]" not in after,
              "success was reported but the slug is still in the file")


def test_retitle_changes_the_heading_and_nothing_else():
    """--retitle rewrites one heading line; every other byte is identical
    ([queue-tool-no-heading-fix])."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(FIXTURE)
        result = subprocess.run(
            [sys.executable, SCRIPT, path, "--retitle", "gamma",
             "--heading", "Held item, distinguishing words first"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        with open(path, "r", encoding="utf-8") as f:
            after = f.read()
        expected = FIXTURE.replace(
            "#### A held item [gamma]",
            "#### Held item, distinguishing words first [gamma]")
        check("the retitle succeeds", result.returncode == 0,
              f"exit {result.returncode}: {result.stderr.strip()}")
        check("the heading changed and every other byte is identical",
              after == expected, "file differs beyond the heading line")
        check("old and new heading are reported",
              "old: #### A held item [gamma]" in result.stderr
              and "new: #### Held item, distinguishing words first [gamma]"
              in result.stderr, result.stderr.strip())


def test_retitle_refuses_a_bracketed_heading():
    """A heading carrying a bracket would read as a second slug: refused, and
    the file is untouched."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(FIXTURE)
        result = subprocess.run(
            [sys.executable, SCRIPT, path, "--retitle", "gamma",
             "--heading", "Held item [other]"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        with open(path, "r", encoding="utf-8") as f:
            after = f.read()
        check("a bracketed heading is refused", result.returncode != 0,
              "exit 0")
        check("the file is untouched", after == FIXTURE, "file changed")


def test_write_verified_refuses_a_write_that_did_not_land():
    """The verification itself fails loudly when the re-read disagrees.

    Simulated by asking write_verified to confirm the absence of a slug the
    written content still contains — which is exactly the state a write that
    silently did not land would leave behind.
    """
    mod = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        lines = FIXTURE.splitlines(keepends=True)
        raised = False
        try:
            mod.write_verified(path, lines, absent=[("alpha", "Processed")])
        except SystemExit as exc:
            raised = exc.code != 0
        check("a write that did not land exits non-zero", raised,
              "write_verified reported success for a slug still in the file")


def test_move_section_refuses_an_unnamed_sweep():
    """A marker relocation that would CLEAR held items the caller never named.

    The recorded failure: `--position BOTTOM --marker-after <the moved slug>`
    put the marker below four held items and swept every one of them into the
    cleared region, reporting only that the moved item was now cleared. Here
    gamma is held; placing beta at the bottom and anchoring the marker to it
    would clear gamma too.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(FIXTURE)
        before = open(path, "r", encoding="utf-8").read()

        result = subprocess.run(
            [sys.executable, SCRIPT, path,
             "--move-section", "beta", "Unprocessed", "Processed",
             "--position", "BOTTOM", "--marker-after", "beta"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        output = result.stdout + result.stderr

        check("the sweep is refused", result.returncode != 0,
              f"exit {result.returncode}: {output}")
        check("the refusal names the swept item", "[gamma]" in output,
              f"got: {output}")
        check("nothing was written",
              open(path, "r", encoding="utf-8").read() == before)


def test_named_move_across_the_line_still_reports_and_succeeds():
    """The behaviour the refusal must NOT take: a deliberate, named crossing.

    Moving an item across the line is a legitimate way to clear or shelve work.
    The original code reported rather than refused for exactly this case, and
    that reasoning is unchanged — only unnamed crossings are new. gamma lands
    after alpha, and `--marker-after` names delta, the last item that should
    stay cleared, so gamma crosses into the cleared region and nothing is swept.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(FIXTURE)

        result = subprocess.run(
            [sys.executable, SCRIPT, path, "Processed",
             "--move", "gamma", "AFTER", "alpha", "--marker-after", "delta"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        output = result.stdout + result.stderr

        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        marker_i = next(i for i, l in enumerate(lines)
                        if "Cleared to run above this line" in l)
        gamma_i = next(i for i, l in enumerate(lines)
                       if l.startswith("#### ") and l.rstrip().endswith("[gamma]"))

        check("the named move succeeds", result.returncode == 0,
              f"exit {result.returncode}: {output}")
        check("the crossing is reported",
              "crossed the readiness line" in output, f"got: {output}")
        check("the moved item sits above the marker", gamma_i < marker_i,
              f"(gamma {gamma_i}, marker {marker_i})")


def test_append_stamps_an_unstamped_capture():
    """A capture appended without a stamp gains one, read from the clock, as
    the last prose line — before any field lines.

    The capture tool stamped every capture it filed; this route stamped none,
    and a planning session that filed everything through it wrote 34 clock
    times by hand, each counted up from the opening ([invented-clock-times-in-
    planning-writes]).
    """
    mod = _load_module()
    body = ["#### A capture [zeta]\n", "Its rationale.\n",
            "Blocked by: [alpha]\n"]
    out = mod.stamp_filed_at(list(body))
    check("an unstamped body gains exactly one stamp line",
          len(out) == 4 and sum(1 for l in out if "stamped by the queue tool" in l) == 1,
          repr(out))
    check("the stamp lands before the field lines",
          out[2].startswith("Filed ") and out[3] == "Blocked by: [alpha]\n",
          repr(out))
    check("the stamp carries a clock time",
          re.match(r"^Filed \d{4}-\d{2}-\d{2} \d{2}:\d{2}, stamped by the queue tool\.\n$",
                   out[2]) is not None, repr(out[2]))

    # End to end through --append: the stamp is in the file.
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(FIXTURE)
        body_path = os.path.join(tmp, "body.md")
        with open(body_path, "w", encoding="utf-8") as f:
            f.write("#### Another capture [eta]\nRationale for eta.\n")
        result = subprocess.run(
            [sys.executable, SCRIPT, path, "--append", "Unprocessed",
             "--body", body_path],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        with open(path, "r", encoding="utf-8") as f:
            after = f.read()
        check("--append succeeds", result.returncode == 0, result.stderr.strip())
        check("the appended capture carries the queue tool's stamp",
              "Rationale for eta.\nFiled " in after and
              "stamped by the queue tool." in after, after[-300:])


def test_append_leaves_a_stamped_capture_alone():
    """A body already carrying the capture tool's stamp is unchanged."""
    mod = _load_module()
    body = ["#### A capture [zeta]\n", "Its rationale.\n",
            "Filed 2026-09-02 14:35, stamped by the capture tool.\n",
            "Cycle: [weekly-release]\n"]
    out = mod.stamp_filed_at(list(body))
    check("a body with the capture tool's stamp is returned as it is",
          out == body, repr(out))


if __name__ == "__main__":
    test_append_stamps_an_unstamped_capture()
    test_append_leaves_a_stamped_capture_alone()
    print("test_reorder_queue")
    test_side_of_marker_report()
    test_report_agrees_with_file()
    test_move_section_applies_marker_after()
    test_move_section_marker_failure_writes_nothing()
    test_move_section_marker_after_the_moved_item_is_refused()
    test_delete_reports_only_what_landed()
    test_retitle_changes_the_heading_and_nothing_else()
    test_retitle_refuses_a_bracketed_heading()
    test_write_verified_refuses_a_write_that_did_not_land()
    test_move_section_refuses_an_unnamed_sweep()
    test_named_move_across_the_line_still_reports_and_succeeds()
    print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
    sys.exit(1 if failures else 0)
