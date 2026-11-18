#!/usr/bin/env python3
"""Tests for pre_tool_use.py's plans folder on the standing list.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_pre_tool_use_plans_folder.py

Why this exists ([plan-writes-plan-docs]): a planning session could not write
a long-term plan document into the project's plans folder, so decisions bound
for one became a cleared build made only to perform the write. A session with
no build running may now write `plans/` at the project root and
`workshop/plans/`, as it writes research notes. A path beside them stays
refused, and a build run's scope is still its working file's list.
"""

import json
import os
import subprocess
import sys
import tempfile

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "pre_tool_use.py")

failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        failures.append(name)


d = tempfile.mkdtemp(prefix="plans-folder-")
with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
    f.write("# SPEC\n")


def decide(relpath, session="plans-session", tool="Write"):
    payload = {"cwd": d, "tool_name": tool, "session_id": session,
               "tool_input": {"file_path": os.path.join(d, *relpath.split("/")),
                              "content": "x"}}
    proc = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                          capture_output=True, text=True, encoding="utf-8",
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    if not proc.stdout.strip():
        return "allow", ""
    hso = json.loads(proc.stdout).get("hookSpecificOutput") or {}
    return hso.get("permissionDecision", "allow"), hso.get("permissionDecisionReason", "")


print("test_pre_tool_use_plans_folder")
check("no build: plans/ at the project root is writable",
      decide("plans/google-play-launch.md")[0] == "allow")
check("no build: a file deeper in plans/ is writable",
      decide("plans/2027/store-listing.md")[0] == "allow")
check("no build: workshop/plans/ is writable",
      decide("workshop/plans/later-stage.md", tool="Edit")[0] == "allow")
decision, why = decide("planning/notes.md")
check("no build: a folder beside them stays refused", decision == "deny", why[:200])
check("the refusal names the plans folder",
      "plans/ at the project root or workshop/plans/" in why, why[:900])
check("no build: a file named like the folder stays refused",
      decide("plans.md")[0] == "deny")
check("no build: workshop/other/ stays refused",
      decide("workshop/other/plan.md")[0] == "deny")

# A build run's scope is its working file's list, plans folder or not.
with open(os.path.join(d, "_build-plans-build.md"), "w", encoding="utf-8") as f:
    f.write("# Active Build\n\nRun: build alpha\n\nFiles:\n- product.md\n\nProgress:\n")
check("build run: the plans folder is outside the run's list",
      decide("plans/google-play-launch.md", session="plans-build")[0] == "deny")

print()
if failures:
    print("%d check(s) FAILED: %s" % (len(failures), "; ".join(failures)))
    sys.exit(1)
print("all checks passed")
