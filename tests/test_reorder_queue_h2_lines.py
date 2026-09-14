#!/usr/bin/env python3
"""Regression test: the queue tool finds sections by name only.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_reorder_queue_h2_lines.py

Why this exists ([queue-tool-splits-on-any-h2-line]): the mover collected
every line starting `## ` as a section boundary, so an item quoting a
document heading — a record entry's `## <date> — <title>`, or `## Length`
inside a fenced block — split at that line on the keep-move, stranding the
rest of its text and hiding every item after it from the parser. A section
is now `## Processed` or `## Unprocessed` by name; any other `## ` line is
item text.

Assertions: an item carrying a `## ` line at line start moves across
sections intact, and deletes intact; the items after it stay visible to the
mover; the digest reads such an item whole.
"""

import json
import os
import subprocess
import sys
import tempfile

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "plugin", "throughliner", "scripts", "reorder_queue.py")
DIGEST = os.path.join(ROOT, "plugin", "throughliner", "scripts", "queue_digest.py")
MARKER = "--- Cleared to run above this line ---"

_failures = []

ITEM = (
    "#### Style rewritten to the user's text [style-rewrite]\n"
    "The file becomes the text below.\n\n"
    "```\n"
    "## Length\n"
    "- eight lines\n"
    "## Structure\n"
    "```\n"
    "And a quoted record heading at line start:\n"
    "## 2026-09-13 — a record title\n"
    "Filed 2026-09-14 12:02, stamped by the capture tool.\n"
)

QUEUE = (
    "# QUEUE\n\nIntro.\n\n"
    "## Processed\n\n"
    "#### First cleared thing [first]\nRationale.\n\n"
    + MARKER + "\n\n"
    "## Unprocessed\n\n"
    + ITEM + "\n"
    "#### Next one after it [after]\nStill visible?\n"
)


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        _failures.append(name)


def run(text, *args):
    d = tempfile.mkdtemp(prefix="h2-test-")
    path = os.path.join(d, "QUEUE.md")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    proc = subprocess.run([sys.executable, SCRIPT, path] + list(args),
                          capture_output=True, text=True, encoding="utf-8")
    with open(path, "r", encoding="utf-8", newline="") as f:
        return proc.returncode, proc.stderr, f.read(), path


def main():
    print("queue tool and `## ` lines inside items:")

    rc, err, out, _ = run(QUEUE, "--move-section", "style-rewrite", "Unprocessed",
                          "Processed", "--position", "AFTER", "first")
    check("keep-move across sections succeeds", rc == 0, err)
    check("the item arrives in Processed intact, `## ` lines and all",
          ITEM in out.split("## Unprocessed")[0], out)
    check("the item is gone from Unprocessed",
          "[style-rewrite]" not in out.split("## Unprocessed")[1])
    check("the item after it is still where it was",
          "#### Next one after it [after]" in out.split("## Unprocessed")[1])

    rc, err, out2, _ = run(out, "--delete", "style-rewrite", "Processed")
    check("delete of the moved item succeeds", rc == 0, err)
    check("delete removes the whole item, its `## ` lines with it",
          "## Length" not in out2 and "[style-rewrite]" not in out2, out2)
    check("nothing else was touched by the delete",
          "#### First cleared thing [first]" in out2
          and "#### Next one after it [after]" in out2)

    rc, err, _, path = run(QUEUE)
    proc = subprocess.run([sys.executable, DIGEST, path, "--json"],
                          capture_output=True, text=True, encoding="utf-8")
    if proc.returncode == 0 and proc.stdout.strip():
        try:
            data = json.loads(proc.stdout)
            slugs = [i.get("slug") for i in data.get("items", data if isinstance(data, list) else [])]
        except (json.JSONDecodeError, AttributeError):
            slugs = None
    else:
        slugs = None
    if slugs is None:
        # The digest's --json shape is not asserted here; fall back to the
        # plain report naming both slugs.
        proc = subprocess.run([sys.executable, DIGEST, path],
                              capture_output=True, text=True, encoding="utf-8")
        check("digest reads the item and the one after it",
              "style-rewrite" in proc.stdout and "after" in proc.stdout, proc.stdout[:400])
    else:
        check("digest reads the item and the one after it",
              "style-rewrite" in slugs and "after" in slugs, str(slugs))

    if _failures:
        print(f"\n{len(_failures)} FAILURE(S)")
        return 1
    print("\nall passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
