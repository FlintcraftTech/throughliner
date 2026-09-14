#!/usr/bin/env python3
"""Regression test for pre_tool_use.py's decision-log rotation.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_pre_tool_use_decision_log_rotation.py

Why this exists ([decision-log-retention-too-short-for-audits]): the live
decision log `.throughliner/pre-tool-use.log` keeps its newest 500 lines, which
is what the user's freeform door reads, and on this project that covered under
two days — so no audit could count refusals further back. The fix is a
rotation, not a longer cap: every line the prune drops is appended, in order,
to `.throughliner/pre-tool-use-YYYY-MM.log` beside it, which nothing prunes.

Two assertions: writing past 500 lines leaves the live file at exactly 500 and
the overflow, in order, in the month's archive; and a log under the cap
creates no archive.
"""

import datetime
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
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "pre_tool_use.py")

SESSION = "rotation-test"
CAP = 500

_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("  -- " + detail if detail else ""))
        _failures.append(name)


def make_project():
    d = tempfile.mkdtemp(prefix="rotation-test-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    return d


def drive_edit(cwd, filepath):
    payload = {
        "cwd": cwd,
        "tool_name": "Edit",
        "tool_input": {"file_path": filepath},
        "session_id": SESSION,
    }
    subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                   capture_output=True, text=True, encoding="utf-8")


def main():
    print("decision-log rotation:")
    month = datetime.datetime.now().strftime("%Y-%m")

    # 1. Under the cap: no archive appears.
    d = make_project()
    drive_edit(d, os.path.join(d, "QUEUE.md"))
    folder = os.path.join(d, ".throughliner")
    archive = os.path.join(folder, "pre-tool-use-" + month + ".log")
    check("a log under the cap creates no archive", not os.path.exists(archive))

    # 2. Past the cap: seed the live file with CAP synthetic lines, then one
    # real decision pushes the oldest line out into the archive, in order.
    live = os.path.join(folder, "pre-tool-use.log")
    seeded = ["2026-01-01 00:00:%02d\tEdit\tallow\tseed\tline-%d\tseed\n" % (i % 60, i)
              for i in range(CAP)]
    with open(live, "w", encoding="utf-8", newline="") as f:
        f.write("".join(seeded))
    drive_edit(d, os.path.join(d, "QUEUE.md"))
    with open(live, encoding="utf-8") as f:
        live_lines = f.read().splitlines(keepends=True)
    check("the live file holds exactly the cap after a prune",
          len(live_lines) == CAP, str(len(live_lines)))
    check("the archive exists after a prune", os.path.exists(archive))
    with open(archive, encoding="utf-8") as f:
        arch_lines = f.read().splitlines(keepends=True)
    check("the dropped line is the oldest, and it is in the archive",
          arch_lines == seeded[:1], repr(arch_lines[:2]))

    # 3. A second prune appends, in order, after the first.
    drive_edit(d, os.path.join(d, "QUEUE.md"))
    drive_edit(d, os.path.join(d, "QUEUE.md"))
    with open(archive, encoding="utf-8") as f:
        arch_lines = f.read().splitlines(keepends=True)
    check("later prunes append in order",
          arch_lines == seeded[:3], repr(arch_lines))
    with open(live, encoding="utf-8") as f:
        check("the live file stays at the cap",
              len(f.read().splitlines()) == CAP)

    if _failures:
        print(f"\n{len(_failures)} FAILURE(S)")
        return 1
    print("\nall passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
