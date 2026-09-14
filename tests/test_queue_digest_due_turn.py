#!/usr/bin/env python3
"""Regression test: a due-turn capture ranks at rung 2 whatever field it carries.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_queue_digest_due_turn.py

Why this exists ([due-turn-capture-passed-over-by-cycle-field]): the
maintenance sweep's due-turn capture was filed with the capture tool's
`cycle` field set, so it carried `Cycle: [maintenance-sweep]`; the ladder's
pass-over for cycle material then hid the due turn itself and the next pick
reported nothing offerable. A capture whose own slug names a cycle definition
is that cycle's due turn and is offered at rung 2 even where it carries the
field; ordinary material carrying the field is still passed over.
"""

import importlib.util
import os
import sys
import tempfile

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "plugin", "throughliner", "scripts", "queue_digest.py")
_spec = importlib.util.spec_from_file_location("queue_digest", SCRIPT)
digest = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(digest)

MARKER = "--- Cleared to run above this line ---"
_failures = []

CYCLES = (
    "# CYCLES\n\n## Maintenance sweep [maintenance-sweep]\n\n"
    "**Artifact:** the rule corpus.\n\n**Cadence:** weekly.\n\n"
    "**Observable:** the newest sweep record.\n\n"
    "**Steps of one turn.**\n1. Read. Fires on: the turn is due; performed by Claude.\n"
)

QUEUE = (
    "# QUEUE\n\n## Processed\n\n" + MARKER + "\n\n## Unprocessed\n\n"
    "#### Ordinary material for the sweep [some-material]\nDrawn by the sweep.\n"
    "Cycle: [maintenance-sweep]\n\n"
    "#### [audit] Maintenance sweep due 2026-09-14 [maintenance-sweep]\n"
    "Filed by the cycles check.\nCycle: [maintenance-sweep]\n\n"
    "#### Some other capture [other]\nNothing special.\n"
)


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        _failures.append(name)


def main():
    print("due-turn capture with a Cycle: line:")
    d = tempfile.mkdtemp(prefix="due-turn-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    with open(os.path.join(d, "CYCLES.md"), "w", encoding="utf-8") as f:
        f.write(CYCLES)
    qpath = os.path.join(d, "QUEUE.md")
    with open(qpath, "w", encoding="utf-8", newline="") as f:
        f.write(QUEUE)

    items = digest.parse(qpath)
    pool = digest.offerable(items, d)
    slugs = [i["slug"] for i in pool]
    check("the due turn is offerable despite its Cycle: line", "maintenance-sweep" in slugs, str(slugs))
    check("ordinary material carrying the field is still passed over", "some-material" not in slugs, str(slugs))

    rung, name, item = digest.whats_next(items, d, qpath) if hasattr(digest, "whats_next") else (None, "", None)
    if item is not None:
        check("the pick falls to rung 2 on the due turn",
              rung == 2 and item["slug"] == "maintenance-sweep", f"{rung} {name} {item and item['slug']}")

    if _failures:
        print(f"\n{len(_failures)} FAILURE(S)")
        return 1
    print("\nall passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
