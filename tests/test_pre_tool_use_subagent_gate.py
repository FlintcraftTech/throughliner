#!/usr/bin/env python3
"""Regression tests for pre_tool_use.py's subagent cost ask-gate.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_pre_tool_use_subagent_gate.py

Why this exists ([haiku-subagents-facts-only-with-brief-standard]): the
always-loaded rules carry a fixed table of task kinds, each naming Haiku or
Sonnet, so a spawn naming one of the two in the Agent tool's `model` field is
let through with no prompt, and any other model — or none named — still asks.
The rule steers which row a task is on; the gate guarantees the model.

Three assertions: a Sonnet spawn is admitted, a Haiku spawn is admitted, and
an Opus spawn (and a spawn naming no model) is asked.
"""

import json
import os
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "pre_tool_use.py")

_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("  -- " + detail if detail else ""))
        _failures.append(name)


def drive(cwd, tool_input):
    payload = {
        "cwd": cwd,
        "tool_name": "Agent",
        "tool_input": tool_input,
        "session_id": "test-session",
    }
    proc = subprocess.run(
        [sys.executable, HOOK],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if not proc.stdout.strip():
        return {}
    return json.loads(proc.stdout).get("hookSpecificOutput", {})


def decision(result):
    return result.get("permissionDecision", "allow")


def main():
    print("subagent cost gate:")
    d = tempfile.mkdtemp(prefix="subagent-gate-test-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")

    r = drive(d, {"prompt": "read x", "model": "sonnet"})
    check("a Sonnet spawn is admitted with no prompt", decision(r) == "allow",
          repr(r))
    r = drive(d, {"prompt": "read x", "model": "Haiku"})
    check("a Haiku spawn is admitted, case ignored", decision(r) == "allow",
          repr(r))
    r = drive(d, {"prompt": "read x", "model": "opus"})
    check("an Opus spawn is asked", decision(r) == "ask"
          and "subagent" in r.get("permissionDecisionReason", ""), repr(r))
    r = drive(d, {"prompt": "read x"})
    check("a spawn naming no model is asked", decision(r) == "ask", repr(r))

    if _failures:
        print("\n%d FAILED" % len(_failures))
        sys.exit(1)
    print("\nall cases passed")


if __name__ == "__main__":
    main()
