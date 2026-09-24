#!/usr/bin/env python3
"""Regression tests for pre_tool_use.py's refusal of self-invoked method skills.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_pre_tool_use_skill_invocation.py

Why this exists ([claude-invoked-plan-against-the-rule]): the method's five
skills ship with model invocation disabled, so an attempt fails and shows the
user a red error at the moment they have least context for it — once at a
close, landing between "now closing the session" and any explanation. The
always-loaded rules already forbid it and were relied on twice; a mechanical,
recurring failure whose cost lands on the user is what the rule gate's fourth
admission question sends to a hook.

The cases below drive the hook as a subprocess with a real PreToolUse payload.
The negative cases are the guard: this must refuse the method's own commands
and nothing else, and in particular a same-named skill from another plugin in
an unadopted folder has to pass.

Verification note, and it is load-bearing: every case here drives the hook code
directly. Invoking a live skill to watch the guard refuse it is the destructive
test this project has already been bitten by — the installed host is the OLD
code, so the guard would not fire and the action would complete for real.
"""

import json
import os
import subprocess
import sys
import tempfile

HOOKS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "plugin", "throughliner", "hooks",
)
HOOK = os.path.join(HOOKS, "pre_tool_use.py")

failures = []


def _decide(cwd, tool_name, tool_input):
    payload = {
        "cwd": cwd,
        "tool_name": tool_name,
        "tool_input": tool_input,
        "session_id": "skill-invocation-test-session",
    }
    proc = subprocess.run(
        [sys.executable, HOOK], input=json.dumps(payload),
        capture_output=True, text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if not proc.stdout.strip():
        return "pass", ""
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return "pass", ""
    spec = out.get("hookSpecificOutput") or {}
    return spec.get("permissionDecision", "pass"), spec.get(
        "permissionDecisionReason", ""
    )


# An adopted project, and an unadopted folder — the two states the bare-name
# arm distinguishes between.
ADOPTED = tempfile.mkdtemp(prefix="skill-inv-adopted-")
with open(os.path.join(ADOPTED, "SPEC.md"), "w", encoding="utf-8") as _f:
    _f.write("# SPEC\n")
UNADOPTED = tempfile.mkdtemp(prefix="skill-inv-unadopted-")

CASES = [
    # (cwd, skill name, expected, what it pins)
    (ADOPTED, "throughliner:plan", "deny", "the recorded failure: /plan invoked"),
    (ADOPTED, "throughliner:close", "deny", "/close, where the failure landed at a close"),
    (ADOPTED, "throughliner:next", "deny", "/next"),
    (ADOPTED, "throughliner:rescan", "deny", "/rescan"),
    (ADOPTED, "throughliner:setup", "deny", "/setup"),
    (ADOPTED, "plan", "deny", "the bare name in an adopted project"),
    # /setup's own failure happens in a folder that is not adopted yet, which is
    # the whole reason the prefixed arm is not gated on adoption.
    (UNADOPTED, "throughliner:setup", "deny",
     "/setup is refused in an unadopted folder too"),
    # The guard cases.
    (UNADOPTED, "plan", "pass",
     "a bare same-named skill outside an adopted project is NOT ours to refuse"),
    (ADOPTED, "someone-else:plan", "pass",
     "another plugin's skill is untouched even when the name collides"),
    (ADOPTED, "throughliner:something-else", "pass",
     "a name outside the five passes"),
    (ADOPTED, "pdf", "pass", "an unrelated skill passes"),
    (ADOPTED, "docx", "pass", "another unrelated skill passes"),
]

for cwd, name, expected, what in CASES:
    got, reason = _decide(cwd, "Skill", {"skill": name})
    status = "ok" if got == expected else "FAIL"
    if got != expected:
        failures.append((name, expected, got, what))
    print(f"[{status}] Skill {name!r} -> {got} ({what})")

# The message has to carry the early-typing guidance, because that is the
# trigger the user reports recurring — a refusal that only says no sends them
# looking for a fault that isn't there.
_, reason = _decide(ADOPTED, "Skill", {"skill": "throughliner:plan"})
for fragment, what in [
    ("/plan", "names the command"),
    ("yours to type", "says whose the command is"),
    ("hadn't registered", "names the early-typing trigger"),
]:
    ok = fragment in reason
    if not ok:
        failures.append(("deny message", fragment, "absent", what))
    print(f"[{'ok' if ok else 'FAIL'}] deny message contains {fragment!r} ({what})")

# A malformed or absent skill name must not crash the hook or refuse anything.
for tool_input, what in [
    ({}, "no skill key"),
    ({"skill": ""}, "an empty name"),
    ({"skill": None}, "a null name"),
    ({"skill": 42}, "a non-string name"),
]:
    got, _ = _decide(ADOPTED, "Skill", tool_input)
    ok = got == "pass"
    if not ok:
        failures.append(("malformed input", "pass", got, what))
    print(f"[{'ok' if ok else 'FAIL'}] malformed Skill input -> {got} ({what})")

print()
if failures:
    print(f"{len(failures)} failure(s):")
    for path, expected, got, what in failures:
        print(f"  {path!r}: expected {expected}, got {got} — {what}")
    sys.exit(1)
print("all cases passed")
