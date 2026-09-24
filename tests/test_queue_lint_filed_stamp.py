#!/usr/bin/env python3
"""Regression tests for the queue lint's filed-stamp advisory.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_queue_lint_filed_stamp.py

[done-captures-filed-by-edit-without-server]: a capture in Unprocessed with
no `Filed <date>` line is flagged, naming the two filing routes that write
the stamp; a stamped capture draws nothing, and a work item in Processed
draws nothing whatever it carries.
"""

import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "post_tool_use.py")

spec = importlib.util.spec_from_file_location("post_tool_use", HOOK)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("  -- " + detail if detail else ""))
        _failures.append(name)


def queue(processed="", unprocessed=""):
    return ("# QUEUE\n\n## Processed\n\n" + processed
            + "--- Cleared to run above this line ---\n\n"
            "## Unprocessed\n\n" + unprocessed)


def stamp_warnings(content):
    return [w for w in mod.lint(content) if "carries no `Filed <date>` line" in w]


def main():
    print("filed-stamp advisory:")

    stamped = stamp_warnings(queue(unprocessed=(
        "#### Stamped capture [a-slug]\nRationale.\n"
        "Filed 2026-09-20 12:12, stamped by the capture tool.\n")))
    check("a stamped capture draws nothing", not stamped, repr(stamped))

    unstamped = stamp_warnings(queue(unprocessed=(
        "#### Hand-added capture [b-slug]\nRationale.\nFiled at /close 2026-09-20\n")))
    check("an unstamped capture draws the warning naming it",
          len(unstamped) == 1 and "'#### Hand-added capture [b-slug]'" in unstamped[0],
          repr(unstamped))
    check("the warning names both filing routes",
          unstamped and "file_capture" in unstamped[0]
          and "--append Unprocessed" in unstamped[0], repr(unstamped))

    work_item = stamp_warnings(queue(processed=(
        "#### Cleared build [c-slug]\nRationale with no stamp.\n\n")))
    check("an unstamped work item in Processed draws nothing",
          not work_item, repr(work_item))

    # The lint's split against HEAD classifies a standing unstamped entry as
    # pre-existing, so only a fresh hand-added one is named in full.
    content = queue(unprocessed="#### Old capture [d-slug]\nRationale.\n")
    new, old = mod._split_warnings(mod.lint(content), content)
    check("a standing unstamped capture is counted, not re-flagged as new",
          not [w for w in new if "Filed <date>" in w]
          and len([w for w in old if "Filed <date>" in w]) == 1,
          f"new={new} old={old}")

    if _failures:
        print(f"\n{len(_failures)} FAILURE(S)")
        return 1
    print("\nall passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
