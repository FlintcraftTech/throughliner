#!/usr/bin/env python3
"""Regression test: the queue lint finds sections by name only.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_queue_lint_h2_lines.py

Why this exists ([queue-tool-splits-on-any-h2-line]): the lint's line
annotator took every `## ` line as a section change, so an item carrying a
quoted document heading put every line after it outside both sections and
the lint reported the item's own tail as orphaned prose. A section is now
`## Processed` or `## Unprocessed` by name.

Assertions: an item carrying `## ` lines produces no orphan flag and no
section flag; a genuinely orphaned line still does.
"""

import os
import sys

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = os.path.join(ROOT, "plugin", "throughliner", "hooks")
sys.path.insert(0, HOOKS)
import post_tool_use  # noqa: E402

MARKER = "--- Cleared to run above this line ---"
_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        _failures.append(name)


QUEUE = (
    "# QUEUE\n\nIntro.\n\n"
    "## Processed\n\n"
    "#### First cleared thing [first]\nRationale.\n\n"
    + MARKER + "\n\n"
    "## Unprocessed\n\n"
    "#### Style rewritten to the user's text [style-rewrite]\n"
    "The file becomes the text below.\n\n"
    "```\n## Length\n- eight lines\n## Structure\n```\n"
    "## 2026-09-13 — a record title\n"
    "Filed 2026-09-14 12:02, stamped by the capture tool.\n\n"
    "#### Next one after it [after]\nStill visible?\n"
    "Filed 2026-09-14 12:03, stamped by the capture tool.\n"
)


def main():
    print("queue lint and `## ` lines inside items:")
    warnings = post_tool_use.lint(QUEUE)
    joined = "\n".join(warnings)
    check("no orphaned-prose flag for the item's tail",
          "orphan" not in joined.lower(), joined)
    check("no missing-section flag",
          "section" not in joined.lower() or "Processed" in joined and False, joined)
    check("no warning names the item after it",
          "[after]" not in joined, joined)

    orphaned = QUEUE.replace("## Unprocessed\n\n", "## Unprocessed\n\nA stray line with no item.\n\n")
    warnings2 = post_tool_use.lint(orphaned)
    check("a genuinely orphaned line is still flagged",
          any("orphan" in w.lower() or "stray" in w.lower() or "prose" in w.lower()
              for w in warnings2), "\n".join(warnings2))

    if _failures:
        print(f"\n{len(_failures)} FAILURE(S)")
        return 1
    print("\nall passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
