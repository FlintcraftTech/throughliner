#!/usr/bin/env python3
"""The epoch-marker skip path stays pinned in setup.md.

The marker write is performed by Claude following the doc, not by a script, so
what can regress silently is the doc text itself: the conditional write and its
skip branch. This pins both — a rewrite that drops either fails here.

Run as a plain script: py tests/test_setup_epoch_marker_skip.py
(never through pytest — see CLAUDE.md's scripting constraints).
"""

import io
import os
import sys

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SETUP = os.path.join(ROOT, "plugin", "throughliner", "docs", "setup.md")

failures = []


def check(name, cond):
    if cond:
        print("PASS  " + name)
    else:
        failures.append(name)
        print("FAIL  " + name)


def main():
    with io.open(SETUP, encoding="utf-8") as f:
        text = f.read()

    check("epoch write is conditional on the conversion completing",
          "only when the conversions for" in text
          and "ran to completion" in text)
    check("skip branch leaves the marker at its old value",
          "leave the marker at its old value" in text)
    check("skip branch says the halt will recur",
          "the halt will fire again next" in text)

    if failures:
        print("\n%d failure(s)" % len(failures))
        sys.exit(1)
    print("\nall passed")


if __name__ == "__main__":
    main()
