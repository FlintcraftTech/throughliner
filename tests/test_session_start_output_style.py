#!/usr/bin/env python3
"""Regression tests for session_start.py's brevity-style notice.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_session_start_output_style.py

[ship-brevity-output-style]: every session opening checks the project's
outputStyle setting — not enabled -> one short line; enabled -> nothing.
"""

import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "session_start.py")

_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("  -- " + detail if detail else ""))
        _failures.append(name)


def make_project(output_style=None):
    d = tempfile.mkdtemp(prefix="style-test-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8") as f:
        f.write("# QUEUE\n\n## Processed\n\n"
                "--- Cleared to run above this line ---\n\n## Unprocessed\n")
    if output_style is not None:
        settings_dir = os.path.join(d, ".claude")
        os.makedirs(settings_dir)
        with open(os.path.join(settings_dir, "settings.local.json"), "w",
                  encoding="utf-8") as f:
            json.dump({"outputStyle": output_style}, f)
    return d


def drive(cwd):
    payload = {"cwd": cwd, "session_id": "style-test"}
    proc = subprocess.run(
        [sys.executable, HOOK],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    try:
        out = json.loads(proc.stdout)
    except ValueError:
        return proc.stdout
    return json.dumps(out)


NOTICE = "brevity output style is not enabled"


def main():
    print("brevity-style notice:")

    check("no setting -> notice", NOTICE in drive(make_project(None)))
    check(
        "other style -> notice naming it",
        NOTICE in drive(make_project("Explanatory")),
    )
    check(
        "our style -> silence",
        NOTICE not in drive(make_project("Throughliner Brevity")),
    )
    check(
        "namespaced value -> silence",
        NOTICE not in drive(make_project("throughliner:Throughliner Brevity")),
    )

    if _failures:
        print(f"\n{len(_failures)} FAILURE(S)")
        return 1
    print("\nall passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
