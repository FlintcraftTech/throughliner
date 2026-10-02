#!/usr/bin/env python3
"""Regression tests for post_tool_use.py's per-item word-growth counting.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_queue_lint_word_growth.py

Why this exists ([lint-word-growth-misattribution]): the readiness marker is not
part of any item — it sits between them — but it fell inside the span of
whichever item it happened to follow, so moving the line alone changed that
item's word count and the growth report named an item the edit never touched.
A report that points at unchanged work is worse than no report, because the
reader goes and reads the wrong item.

These cases call `_item_word_counts` directly and compare two snapshots, which
is exactly what `_growth_report` does between the committed queue and the
current one — without needing a git repository to stand one up.
"""

import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "post_tool_use.py")

_spec = importlib.util.spec_from_file_location("post_tool_use", HOOK)
lint = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lint)

MARKER = "--- Cleared to run above this line ---"

failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        failures.append(name)


def queue(body):
    return "# QUEUE\n\n## Processed\n\n" + body + "\n## Unprocessed\n\nNothing.\n"


def deltas(before_text, after_text):
    """The report `_growth_report` would print, without needing git."""
    before = lint._item_word_counts(before_text)
    after = lint._item_word_counts(after_text)
    out = {}
    for slug, count in after.items():
        was = before.get(slug)
        if was is not None and count != was:
            out[slug] = count - was
    return out


ALPHA = "#### Do the thing [alpha]\nProse about the thing.\n"
BETA = "#### Do the other thing [beta]\nProse about the other thing.\n"

# --- the defect: a marker move, and nothing else ------------------------------

before = queue(ALPHA + "\n" + MARKER + "\n\n" + BETA)
after = queue(ALPHA + "\n" + BETA + "\n" + MARKER + "\n")

got = deltas(before, after)
check(
    "moving the readiness marker alone produces no per-item delta",
    got == {},
    f"got {got!r}",
)

# The reverse move, so the fix is not merely a happy accident of direction.
got = deltas(after, before)
check(
    "moving it back produces no per-item delta either",
    got == {},
    f"got {got!r}",
)

# An item directly above the marker is the one that carried the miscount: the
# marker sat inside its span. Pin it on its own.
before = queue(ALPHA + "\n" + MARKER + "\n")
after = queue(ALPHA + "\n")
got = deltas(before, after)
check(
    "an item directly above the marker is unaffected when the marker goes",
    got == {},
    f"got {got!r}",
)

# --- the report still works: a real edit is still counted ---------------------

before = queue(ALPHA + "\n" + MARKER + "\n\n" + BETA)
after = queue(
    "#### Do the thing [alpha]\nProse about the thing, now with four more words.\n"
    + "\n" + MARKER + "\n\n" + BETA
)
got = deltas(before, after)
check(
    "a genuine edit to an item is still reported",
    got == {"alpha": 5},
    f"got {got!r}",
)

# A real edit AND a marker move together: the delta must be the edit alone.
after = queue(
    "#### Do the thing [alpha]\nProse about the thing, now with four more words.\n"
    + "\n" + BETA + "\n" + MARKER + "\n"
)
got = deltas(before, after)
check(
    "an edit made alongside a marker move reports only the edit",
    got == {"alpha": 5},
    f"got {got!r}",
)

# An untouched item never appears, marker moving or not.
check(
    "the untouched item is absent from the report",
    "beta" not in got,
    f"got {got!r}",
)

# --- the growth line carries the change and the item's total, no median -------
# ([length-bound-by-content-not-median]).

GAMMA = "#### Do a third thing [gamma]\nOne two three four five six seven eight nine ten eleven twelve.\n"
before = queue(ALPHA + "\n" + BETA + "\n" + GAMMA)
after_text = queue(
    "#### Do the thing [alpha]\nProse about the thing, now with four more words.\n"
    + "\n" + BETA + "\n" + GAMMA
)
lines = lint._growth_lines(lint._item_word_counts(before),
                           lint._item_word_counts(after_text))
# The counter splits the heading line too, `####` included: alpha is 5 + 9 =
# 14 words.
check(
    "the growth line names the change and the item's total, with no median",
    lines == ["[alpha] +5 words, now 14"],
    f"got {lines!r}",
)

# A capture in Unprocessed gets the same line shape.
mixed_before = ("# QUEUE\n\n## Processed\n\n" + ALPHA + "\n" + GAMMA
                + "\n## Unprocessed\n\n" + BETA)
mixed_after = ("# QUEUE\n\n## Processed\n\n" + ALPHA + "\n" + GAMMA
               + "\n## Unprocessed\n\n"
               + "#### Do the other thing [beta]\nProse about the other thing, longer.\n")
lines = lint._growth_lines(lint._item_word_counts(mixed_before),
                           lint._item_word_counts(mixed_after))
check(
    "a capture's growth line carries no median either",
    lines == ["[beta] +1 words, now 12"],
    f"got {lines!r}",
)

print()
if failures:
    print(f"{len(failures)} failure(s):")
    for name in failures:
        print(f"  {name}")
    sys.exit(1)
print("all cases passed")
