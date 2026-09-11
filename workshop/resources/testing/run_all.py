#!/usr/bin/env python3
"""Run every test suite in workshop/resources/testing/.

Host-only dev artifact — not shipped in the plugin package.

Run:  py workshop/resources/testing/run_all.py

Why this exists ([testing-suite-runner-discovers-all]): the release checklist named
three suites by hand. That list went stale the moment a fourth was written, and
nothing anywhere reported the omission — a suite left out of the list is
indistinguishable from a suite that passed. Discovery removes the list.

**What counts as a suite is a naming convention, not a list**: a `.py` file in
this folder named `test_*.py` or `*_check.py`, or a `test_*.py` beside the
shipped scripts in `plugin/throughliner/scripts/` — a script's own tests live
beside it, and a suite there went unrun for days because nothing here looked.
A new suite named that way is picked up with no edit here, which is the whole
point. Anything else in the folder is a fixture, a transcript, or a probe —
`statusline_probe.py` reads a status line off stdin and would hang a runner
that tried to execute it.

**Any `.py` file that matches neither is REPORTED as skipped rather than passed
over in silence.** A suite misnamed at birth would otherwise be invisible in
exactly the way the hand-written list was.

Suites are invoked as plain scripts through `py`, never through pytest — see
CLAUDE.md's scripting constraints: `python` on this machine resolves to an
application's bundled interpreter that has no pytest, and its error names that
application, which sends a session chasing the wrong cause.

Exits non-zero on the first failing suite, so the checklists that call it stop
rather than warn.
"""

import os
import subprocess
import sys

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
SELF = os.path.basename(os.path.abspath(__file__))

# This file sits at <project root>/workshop/resources/testing/, so the root is
# three levels up. Every suite computes its own root the same way, by walking a
# fixed number of levels from its own location.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
# What must exist under a correct root. The suites test the hooks, so a root
# with no hooks folder is not this project.
FOOTING = os.path.join("plugin", "throughliner", "hooks")
# The second place suites live: beside the shipped scripts they test. The
# repository cleanup's path grep repairs this with the rest when folders move.
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "plugin", "throughliner", "scripts")


def assert_footing():
    """Fail loudly where the computed project root is not this project.

    A suite's link to the code it tests is a PATH, so a rename or a folder move
    breaks every suite at once while touching no hook. Commit `e04b514` moved
    this testing folder under `workshop/`, every suite ended up one level short
    and pointed at a folder that does not exist, and the close-time trigger
    never fired because that commit staged no hook. The suites were dead from
    that commit onward with nothing reporting it.

    So the harness asserts its own footing before discovering anything: a dead
    harness then reports as dead, with no trigger needed anywhere.
    """
    if os.path.isdir(os.path.join(PROJECT_ROOT, FOOTING)):
        return True
    print("run_all: STOPPING — the computed project root does not look like "
          "this project.")
    print(f"run_all:   computed root: {PROJECT_ROOT}")
    print(f"run_all:   expected to find: {FOOTING}")
    print("run_all: this file walks three folders up from its own location, so "
          "a move or rename of the testing folder breaks that arithmetic and "
          "every suite with it. Fix the level count here and in each suite.")
    print("run_all: NOT a pass. No suite was run.")
    return False


def is_suite(name):
    if not name.endswith(".py") or name == SELF:
        return False
    return name.startswith("test_") or name.endswith("_check.py")


def main():
    if not assert_footing():
        return 1

    entries = sorted(
        n for n in os.listdir(HERE) if os.path.isfile(os.path.join(HERE, n))
    )
    # (folder, name) pairs: this folder's suites first, then the ones beside
    # the shipped scripts, each run from its own folder.
    suites = [(HERE, n) for n in entries if is_suite(n)]
    skipped = [
        n for n in entries
        if n.endswith(".py") and n != SELF and not is_suite(n)
    ]
    script_suites = []
    if os.path.isdir(SCRIPTS_DIR):
        script_suites = [
            (SCRIPTS_DIR, n) for n in sorted(os.listdir(SCRIPTS_DIR))
            if n.startswith("test_") and n.endswith(".py")
            and os.path.isfile(os.path.join(SCRIPTS_DIR, n))
        ]
    suites.extend(script_suites)

    if not suites:
        print("run_all: no suites found in workshop/resources/testing/ — that "
              "is itself a finding, not a pass.")
        return 1

    print(f"run_all: {len(suites) - len(script_suites)} suite(s) discovered in "
          f"workshop/resources/testing/, {len(script_suites)} beside "
          f"plugin/throughliner/scripts/")
    if skipped:
        print("run_all: not run (name matches neither test_*.py nor "
              "*_check.py): " + ", ".join(skipped))
    print()

    failed = []
    for folder, name in suites:
        path = os.path.join(folder, name)
        print(f"=== {name} ===")
        proc = subprocess.run(
            ["py", path],
            cwd=folder,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        sys.stdout.write(proc.stdout)
        if proc.stderr.strip():
            sys.stdout.write(proc.stderr)
        if proc.returncode == 0:
            print(f"--- {name}: PASSED\n")
        else:
            print(f"--- {name}: FAILED (exit {proc.returncode})\n")
            failed.append(name)
            break

    print("=" * 60)
    if failed:
        print(f"run_all: STOPPED at {failed[0]} — it failed. "
              "Nothing after it was run.")
        return 1
    print(f"run_all: all {len(suites)} suite(s) passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
