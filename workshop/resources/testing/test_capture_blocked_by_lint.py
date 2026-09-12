#!/usr/bin/env python3
"""Fixture suite for `Blocked by:` on a capture.

Run: py resources/testing/test_capture_blocked_by_lint.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

Why this exists ([capture-blocked-by]): the field used to belong to the held
region alone, so the lint skipped every Unprocessed entry before it ever looked
at a `Blocked by:` line. Captures may now carry it, meaning "do not offer this
again while the named entry is open".

The bad-slug case is the one that matters. On a work item a broken reference is
at least visible — the entry sits below the cleared-to-run line where the
placement checks look at it. On a capture there is no position to give the
mistake away: the entry just stops being offered, silently, for good. So the
resolution check has to reach Unprocessed, and this suite is what says it does.

The accept-and-stay-quiet cases are the other half. A check that fires on
correct input is worse than no check.
"""

import importlib.util
import os
import sys

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

HOOK = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))),
    "plugin", "throughliner", "hooks", "post_tool_use.py",
)

failures = []


def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


def load_lint():
    spec = importlib.util.spec_from_file_location("post_tool_use", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.lint


BASE = """# QUEUE

## Processed

#### Perfectly ordinary work item [alpha]
Filed by Claude. Rationale for alpha.

--- Build block ---
Changes: `somefile.md` — the thing the item describes.
Acceptance: the suite passes.
--- End build block ---

--- Cleared to run above this line ---

## Unprocessed

#### Capture waiting on queued work [beta]
Filed by Claude. Rationale for beta.
{beta_hold}
#### Capture nothing is waiting on [gamma]
Filed by Claude. Rationale for gamma.
"""


def queue(beta_hold=""):
    return BASE.format(beta_hold=(beta_hold + "\n") if beta_hold else "")


def test_clean_queue_is_silent():
    """The control. A suite that fires on correct input proves nothing."""
    lint = load_lint()
    warnings = lint(queue())
    check("a queue with no capture-side blocker produces no warnings",
          not warnings, f"got: {warnings}")


def test_capture_blocked_by_a_real_entry_is_accepted():
    lint = load_lint()
    warnings = lint(queue("Blocked by: [alpha]"))
    check("a capture blocked by a real queue entry is accepted silently",
          not warnings, f"got: {warnings}")


def test_capture_blocked_by_another_capture_is_accepted():
    """The blocker may sit in Unprocessed — that is the recommended shape."""
    lint = load_lint()
    warnings = lint(queue("Blocked by: [gamma]"))
    check("a capture blocked by another capture is accepted silently",
          not warnings, f"got: {warnings}")


def test_capture_with_several_blockers_is_accepted():
    lint = load_lint()
    warnings = lint(queue("Blocked by: [alpha], [gamma]"))
    check("a capture naming several real blockers is accepted silently",
          not warnings, f"got: {warnings}")


def test_until_built_is_accepted_on_a_capture_and_flagged_on_a_work_item():
    """The trailing words hold a capture until its blockers are BUILT; on a
    work item they add nothing, so the lint says so
    ([capture-hold-says-designed-or-shipped])."""
    lint = load_lint()
    warnings = lint(queue("Blocked by: [alpha] until built"))
    check("`until built` on a capture is accepted silently",
          not warnings, f"got: {warnings}")
    text = queue().replace(
        "#### Perfectly ordinary work item [alpha]\nFiled by Claude. Rationale for alpha.\n",
        "#### Perfectly ordinary work item [alpha]\nFiled by Claude. Rationale for alpha.\n"
        "Blocked by: [gamma] until built\n")
    warnings = lint(text)
    hit = [w for w in warnings if "until built" in w and "adds nothing" in w]
    check("`until built` on a work item is flagged as adding nothing",
          len(hit) == 1, f"got: {warnings}")


def test_capture_blocked_by_a_missing_slug_is_flagged():
    """The case the whole change turns on."""
    lint = load_lint()
    warnings = lint(queue("Blocked by: [nowhere]"))
    hit = any("[nowhere]" in w and "not in the queue" in w for w in warnings)
    check("a capture blocked by a slug that resolves to nothing is flagged",
          hit, f"got: {warnings}")


def test_one_bad_slug_among_good_ones_is_flagged():
    lint = load_lint()
    warnings = lint(queue("Blocked by: [alpha], [nowhere]"))
    hit = any("[nowhere]" in w and "not in the queue" in w for w in warnings)
    check("a bad slug beside a good one is still flagged", hit,
          f"got: {warnings}")


def test_capture_naming_itself_is_flagged():
    lint = load_lint()
    warnings = lint(queue("Blocked by: [beta]"))
    hit = any("names itself" in w for w in warnings)
    check("a capture naming itself as its own blocker is flagged", hit,
          f"got: {warnings}")


def test_capture_blocker_is_not_read_as_misplacement():
    """It must not be reported as a field in the wrong section.

    The above-the-marker warning is scoped to Processed, and a capture is not
    in Processed — so nothing here should mention the cleared-to-run marker.
    """
    lint = load_lint()
    warnings = lint(queue("Blocked by: [alpha]"))
    hit = any("cleared-to-run" in w for w in warnings)
    check("a capture's blocker is never reported against the readiness marker",
          not hit, f"got: {warnings}")


def test_processed_ordering_check_still_only_reads_processed():
    """The blocker-sits-below warning reads build order, so it stays scoped.

    A capture blocked by an entry further down Unprocessed is fine: order in
    Unprocessed is processing order, not build order, and the capture lifts
    whenever its blocker is settled.
    """
    lint = load_lint()
    warnings = lint(queue("Blocked by: [gamma]"))
    hit = any("BELOW it in Processed" in w for w in warnings)
    check("a capture blocked by a later capture is not an ordering fault",
          not hit, f"got: {warnings}")


for fn in [
    test_clean_queue_is_silent,
    test_capture_blocked_by_a_real_entry_is_accepted,
    test_capture_blocked_by_another_capture_is_accepted,
    test_capture_with_several_blockers_is_accepted,
    test_until_built_is_accepted_on_a_capture_and_flagged_on_a_work_item,
    test_capture_blocked_by_a_missing_slug_is_flagged,
    test_one_bad_slug_among_good_ones_is_flagged,
    test_capture_naming_itself_is_flagged,
    test_capture_blocker_is_not_read_as_misplacement,
    test_processed_ordering_check_still_only_reads_processed,
]:
    fn()

print()
if failures:
    print(f"{len(failures)} failure(s):")
    for name in failures:
        print(f"  {name}")
    sys.exit(1)
print("all cases passed")
