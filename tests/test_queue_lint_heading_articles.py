#!/usr/bin/env python3
"""Regression tests for the queue lint's article-first heading advisory.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_queue_lint_heading_articles.py

[heading-rule-did-not-fire-on-a-fresh-capture]: a `#### ` heading whose first
word is The/A/An is flagged, article case only; pre-existing headings are not
re-flagged (the lint's new-vs-HEAD split).
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


def queue(*headings):
    items = "\n\n".join(f"{h}\nSome rationale." for h in headings)
    return ("# QUEUE\n\n## Processed\n\n"
            "--- Cleared to run above this line ---\n\n"
            f"## Unprocessed\n\n{items}\n")


def article_warnings(content):
    return [w for w in mod.lint(content) if "starts \nwith an article" in w
            or "starts with an article" in w]


def main():
    print("article-first heading advisory:")

    flagged = article_warnings(queue("#### The lint misses articles [a-slug]"))
    check("article heading flagged", len(flagged) == 1, repr(mod.lint(
        queue("#### The lint misses articles [a-slug]"))))

    clean = article_warnings(queue("#### Lint misses articles [a-slug]"))
    check("non-article heading passes", not clean, repr(clean))

    tagged = article_warnings(queue("#### [user] A step for you [b-slug]"))
    check("article after a flavor tag flagged", len(tagged) == 1)

    # Pre-existing split: the same warning body computed against HEAD content
    # is classified pre-existing, not new.
    content = queue("#### The old heading [c-slug]")
    new, old = mod._split_warnings(mod.lint(content), content)
    art_new = [w for w in new if "article" in w]
    art_old = [w for w in old if "article" in w]
    check("pre-existing article heading not re-flagged as new",
          not art_new and len(art_old) == 1, f"new={art_new} old={art_old}")

    if _failures:
        print(f"\n{len(_failures)} FAILURE(S)")
        return 1
    print("\nall passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
