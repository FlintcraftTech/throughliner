#!/usr/bin/env python3
"""Regression test: the gate-line lint runs only where the project has a rule gate.

Host-only dev artifact — not shipped in the plugin package.

Run:  py workshop/resources/testing/test_queue_lint_rule_gate_condition.py

Why this exists ([rule-gate-lint-fires-in-consumer-projects]): the lint's
check that a cleared item naming a gate-trigger path carries a `Rule gate:`
line ran in every project, and a consumer with no rule gate wrote "not
needed, this project defines no rule gate" into their queue to satisfy a
demand they had never been shown. The check now runs only where the project
root's CLAUDE.md carries the gate's heading words.

Two cases, driven through the hook: a CLAUDE.md without the phrase draws no
flag for a cleared item naming CLAUDE.md; one with it does.
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

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
HOOKS = os.path.join(ROOT, "plugin", "throughliner", "hooks")
HOOK = os.path.join(HOOKS, "post_tool_use.py")
sys.path.insert(0, HOOKS)
import post_tool_use  # noqa: E402

MARKER = "--- Cleared to run above this line ---"
_failures = []

QUEUE = (
    "# QUEUE\n\n## Processed\n\n"
    "#### Fix the project instructions [fix-instructions]\n"
    "Rationale.\n\nFiles: `CLAUDE.md` — one line reworded\n\n"
    + MARKER + "\n\n## Unprocessed\n\n"
)


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        _failures.append(name)


def make_project(claude_md_text):
    d = tempfile.mkdtemp(prefix="gate-cond-test-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    with open(os.path.join(d, "CLAUDE.md"), "w", encoding="utf-8") as f:
        f.write(claude_md_text)
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8", newline="") as f:
        f.write(QUEUE)
    return d


def drive(cwd):
    payload = {"cwd": cwd, "tool_name": "Edit",
               "tool_input": {"file_path": os.path.join(cwd, "QUEUE.md")},
               "session_id": "gate-cond-test"}
    proc = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                          capture_output=True, text=True, encoding="utf-8")
    if not proc.stdout.strip():
        return ""
    return json.loads(proc.stdout)["hookSpecificOutput"].get("additionalContext", "")


def main():
    print("gate-line lint conditioned on the rule gate:")
    consumer = make_project("# CLAUDE.md\n\nA plain consumer project.\n")
    out = drive(consumer)
    # With no committed copy and no snapshot the hook prints a flag COUNT
    # rather than the listing, so the two cases are told apart by the count.
    check("a plain consumer's CLAUDE.md: no flag at all",
          out == "" or "0 flag" in out, out)

    host = make_project("# CLAUDE.md\n\n- **" + post_tool_use.RULE_GATE_HEADING
                        + ".** Four parts.\n")
    out = drive(host)
    check("a CLAUDE.md carrying the rule gate: one flag fires",
          "1 flag(s)" in out or "gate disposition" in out, out)

    check("the direct lint keeps the check on by default",
          any("gate disposition" in w for w in post_tool_use.lint(QUEUE)))
    check("the direct lint can be told the project has no gate",
          not any("gate disposition" in w for w in post_tool_use.lint(QUEUE, gate_check=False)))

    if _failures:
        print(f"\n{len(_failures)} FAILURE(S)")
        return 1
    print("\nall passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
