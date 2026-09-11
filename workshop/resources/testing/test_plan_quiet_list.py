#!/usr/bin/env python3
"""Regression tests for pre_tool_use.py's planning quiet list.

Host-only dev artifact — not shipped in the plugin package.

Run:  python resources/testing/test_plan_quiet_list.py

No test framework, matching test_reorder_queue.py and
test_pre_tool_use_shell_writes.py: each case calls `_is_plan_quiet_path`
directly and asserts on the boolean.

Why this exists ([plan-quiet-list-case-mismatch]): the function built its
relative path with `_normalise`, which calls `os.path.normcase` — a lowercaser
on Windows and the identity on POSIX. The relative path therefore arrived as
`queue.md` and was compared case-sensitively against `"QUEUE.md"`, which could
never match. The quiet list was inverted on Windows from the day it shipped:
every write to QUEUE.md, SPEC.md and LOG/ in a planning session raised a
permission dialog, including in auto mode. On macOS and Linux `normcase` is the
identity function, so the list matched and the gate behaved as designed — which
is why a POSIX-only test would have passed throughout.

The whole class of defect is invisible without a mixed-case path, so the
mixed-case block below is the point of the file.

Extended 2026-08-15 ([plan-scope-lock-denies]): the gate no longer asks about a
write outside the list, it DENIES it, on the user's decision that an ask waved
through is not consent. The list itself is unchanged, so the boolean cases below
still pin what they always did — but a suite that only checks the list cannot
tell an ask from a denial, which is now the whole point of the gate. The
end-to-end block at the bottom drives the hook for real and asserts the decision.
"""

import json
import os
import subprocess
import sys
import tempfile

HOOKS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))),
    "plugin", "throughliner", "hooks",
)
sys.path.insert(0, HOOKS)

import pre_tool_use  # noqa: E402

CWD = os.path.normpath(r"C:\Users\Someone\Projects\My Project") if os.name == "nt" \
    else "/home/someone/projects/My Project"

CASES = [
    # (relative path, expected, what it pins)
    ("QUEUE.md", True, "the queue itself — the case that was failing"),
    ("SPEC.md", True, "the spec"),
    # The build working file is session-scoped: `_build-<session id>.md`. The
    # bare `_build.md` name this case used to assert is the retired shape, and
    # the hook deliberately no longer matches it — a bare name was visible to
    # every session on the project, which is what session-scoping removed.
    # Asserting the current shape is what keeps the suite honest.
    ("_build-3f9c1a2b-7d4e-4c88-b1a0-5e2d6f8c9a01.md", True,
     "the build working file"),
    ("_build.md", False, "the retired bare name is no longer on the list"),
    # The planning working file was deleted from the method on 2026-08-14: a
    # planning session now writes QUEUE.md, SPEC.md and LOG/ and nothing else,
    # so a `_plan-` write is exactly the surprise the gate should surface. This
    # case asserted True until then.
    ("_plan-3f9c1a2b-7d4e-4c88-b1a0-5e2d6f8c9a01.md", False,
     "the retired planning working file is denied"),
    (os.path.join("LOG", "index.md"), True, "the log index"),
    (os.path.join("LOG", "2026-08-11-entry.md"), True, "a log entry file"),
    # FAQ/ is on the list because the close REQUIRES an FAQ disposition, so a
    # denial there would break a mandated step. templates/ is deliberately off
    # it — a template edit changes what every future consumer receives — EXCEPT
    # the two FAQ templates, on the same mandated-step ground: the FAQ template
    # is canonical and FAQ/ is a copy of it, so the announcement-time rule
    # cannot be obeyed without writing it.
    (os.path.join("FAQ", "faq.md"), True, "the FAQ the close must be able to write"),
    (os.path.join("FAQ", "index.md"), True, "the FAQ index"),
    (os.path.join("plugin", "throughliner", "templates", "faq-template.md"), True,
     "the FAQ template passes — widened 2026-08-28, since the announcement-time "
     "FAQ rule requires this write in the same turn as the sent-register line"),
    (os.path.join("plugin", "throughliner", "templates", "faq-index-template.md"),
     True, "its index template passes for the same reason"),
    (os.path.join("plugin", "throughliner", "templates", "CLAUDE-TEMPLATE.md"),
     False,
     "every OTHER template is still denied — the widening is exactly the FAQ "
     "pair, and this case is what proves it did not widen further"),
    # The plugin's version manifest, added 2026-08-16 ([scope-lock-blocks-the-rezip]).
    # The rezip runs after a close, which has deleted the build working file, so
    # every chat it can run in is classified as planning — and its first step is
    # bumping the `-testN` suffix in this file. Without the permission there was
    # no chat shape in which the rezip could run at all.
    #
    # The sibling case below is the guard that matters: the permission is ONE
    # path, not the folder, so it cannot be read as opening plugin/throughliner/
    # to planning chats.
    (os.path.join("plugin", "throughliner", ".claude-plugin", "plugin.json"), True,
     "the version manifest the rezip must bump"),
    (os.path.join("plugin", "throughliner", ".claude-plugin", "marketplace.json"), False,
     "a sibling in the same folder is still denied"),
    # The rezip archive, permitted 2026-08-29 after the archive step was denied
    # on its first ever run. A FOLDER where the manifest above is one path —
    # defensible because it is gitignored build output rather than part of the
    # plugin package, which the third case here is the guard on.
    (os.path.join("plugin", "rezip-archive", "throughliner-v1.21.1-test1.zip"),
     True, "a build's archived zip"),
    (os.path.join("plugin", "rezip-archive", "throughliner-v1.21.1-test1.md"),
     True, "the readme beside it, which is the channel post's own text"),
    (os.path.join("plugin", "throughliner", "hooks", "session_start.py"), False,
     "a sibling under the plugin package is still denied"),
    ("README.md", False, "an ordinary project file is denied"),
    (os.path.join("plugin", "throughliner", "docs", "plan.md"), False,
     "a shipped doc is denied"),
    ("QUEUEQ.md", False, "a near-miss name is not on the list"),
]

failures = []

for rel, expected, what in CASES:
    got = pre_tool_use._is_plan_quiet_path(os.path.join(CWD, rel), CWD)
    status = "ok" if got == expected else "FAIL"
    if got != expected:
        failures.append((rel, expected, got, what))
    print(f"[{status}] {rel!r} -> {got} ({what})")

# The mixed-case cases. On Windows a caller can hand the hook a path whose
# casing differs from the project root's, and the containment test normcases,
# so the relative path must survive that without being lowercased itself.
if os.name == "nt":
    mixed = [
        (CWD.lower() + os.sep + "queue.md", True, "an all-lowercase absolute path"),
        (CWD.upper() + os.sep + "QUEUE.MD", True, "an all-uppercase absolute path"),
        (CWD + os.sep + "log" + os.sep + "index.md", True, "a lowercased LOG folder"),
        (CWD.lower() + os.sep + "readme.md", False,
         "case-insensitivity must not widen the list"),
    ]
    for path, expected, what in mixed:
        got = pre_tool_use._is_plan_quiet_path(path, CWD)
        status = "ok" if got == expected else "FAIL"
        if got != expected:
            failures.append((path, expected, got, what))
        print(f"[{status}] {path!r} -> {got} ({what})")
else:
    print("[skip] mixed-case cases are Windows-only — "
          "normcase is the identity on this platform")

# --- end to end: the decision itself, not just the list ----------------------
#
# The list has never distinguished an ask from a denial, and from 2026-08-15 the
# difference is the gate. These cases drive the hook as a subprocess with a real
# PreToolUse payload, exactly as test_pre_tool_use_shell_writes.py does, in a
# temp project with NO build working file — which is the condition the planning
# branch keys on.

HOOK = os.path.join(HOOKS, "pre_tool_use.py")


def _decide(cwd, path, session_id="test-session"):
    payload = {
        "cwd": cwd,
        "tool_name": "Write",
        "tool_input": {"file_path": path, "content": "x"},
        "session_id": session_id,
    }
    proc = subprocess.run(
        [sys.executable, HOOK], input=json.dumps(payload),
        capture_output=True, text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if not proc.stdout.strip():
        return "pass"
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return "pass"
    return (out.get("hookSpecificOutput") or {}).get("permissionDecision", "pass")


_tmp = tempfile.mkdtemp(prefix="plan-lock-test-")
with open(os.path.join(_tmp, "SPEC.md"), "w", encoding="utf-8") as _f:
    _f.write("# SPEC\n")

E2E = [
    ("README.md", "deny", "a write outside the list is DENIED, not asked"),
    (os.path.join("plugin", "hooks", "thing.py"), "deny",
     "a shipped file is denied in a planning session"),
    ("QUEUE.md", "pass", "the queue passes silently"),
    ("SPEC.md", "pass", "the spec passes silently"),
    (os.path.join("LOG", "2026-08-15-entry.md"), "pass", "a log entry passes"),
    # Load-bearing: the always-loaded rules require a research finding to be
    # filed as part of using it, so denying this path would break a shipped duty.
    (os.path.join("workshop", "resources", "research", "a-finding.md"), "pass",
     "research is writable in a planning session"),
    (os.path.join("FAQ", "faq.md"), "pass",
     "the FAQ is writable — the close is required to dispose of it"),
]

for rel, expected, what in E2E:
    got = _decide(_tmp, os.path.join(_tmp, rel))
    status = "ok" if got == expected else "FAIL"
    if got != expected:
        failures.append((rel, expected, got, what))
    print(f"[{status}] end-to-end {rel!r} -> {got} ({what})")

# --- the /setup marker -------------------------------------------------------
#
# /setup never creates a build working file, so it was classified by the branch
# above and every write its migration path makes was denied with no prompt —
# the version and format-epoch markers, the managed CLAUDE.md block, .gitignore.
# It now declares itself with `.throughliner-setup-active` in the session
# scratchpad, and a session carrying that marker is exempt from the standing
# list. These cases drive the hook for real, marker present and absent.

_setup_session = "setup-marker-test-session"
_scratch = os.path.join(
    tempfile.gettempdir(), "claude", "plan-lock-test-project",
    _setup_session, "scratchpad",
)
os.makedirs(_scratch, exist_ok=True)
_marker = os.path.join(_scratch, pre_tool_use.SETUP_MARKER_NAME)

SETUP_TARGET = os.path.join(_tmp, "CLAUDE.md")

got = _decide(_tmp, SETUP_TARGET, _setup_session)
if got != "deny":
    failures.append(("CLAUDE.md", "deny", got, "denied before the marker exists"))
print(f"[{'ok' if got == 'deny' else 'FAIL'}] setup marker absent -> {got} "
      "(a normally-denied path is denied)")

with open(_marker, "w", encoding="utf-8") as _f:
    _f.write("")

got = _decide(_tmp, SETUP_TARGET, _setup_session)
if got != "pass":
    failures.append(("CLAUDE.md", "pass", got, "allowed while the marker exists"))
print(f"[{'ok' if got == 'pass' else 'FAIL'}] setup marker present -> {got} "
      "(a normally-denied path passes)")

# The marker is scoped to the session that wrote it: one project's setup run
# must not unlock a planning session in another chat.
got = _decide(_tmp, SETUP_TARGET, "some-other-session")
if got != "deny":
    failures.append(("CLAUDE.md", "deny", got, "another session is unaffected"))
print(f"[{'ok' if got == 'deny' else 'FAIL'}] setup marker, other session -> {got} "
      "(the exemption does not leak between sessions)")

os.remove(_marker)

got = _decide(_tmp, SETUP_TARGET, _setup_session)
if got != "deny":
    failures.append(("CLAUDE.md", "deny", got, "denied again once cleaned up"))
print(f"[{'ok' if got == 'deny' else 'FAIL'}] setup marker cleaned up -> {got} "
      "(the exemption ends with the run)")

# --- checklist-declared paths ---------------------------------------------------
#
# A checklist definition names the paths its steps write, and the standing list
# permits exactly those. The declaration is committed text written at a planning
# session with the user present, which is what distinguishes it from the
# self-declared marker refused beside the manifest carve-out.

CHECKLIST_TARGET = os.path.join(_tmp, "build-output", "artifact.zip")
UNDECLARED_TARGET = os.path.join(_tmp, "build-output-other", "artifact.zip")

got = _decide(_tmp, CHECKLIST_TARGET)
if got != "deny":
    failures.append(("build-output/", "deny", got,
                     "denied with no cycles doc at all"))
print(f"[{'ok' if got == 'deny' else 'FAIL'}] no cycles doc -> {got} "
      "(a project without one behaves exactly as before)")

with open(os.path.join(_tmp, "CYCLES.md"), "w", encoding="utf-8") as _f:
    _f.write(
        "# CYCLES\n\n"
        "## Repackage [repackage]\n\n"
        "**Artifact:** the built zip.\n\n"
        "**Trigger:** the user says \"repackage\".\n\n"
        "**Writes:** `build-output/`\n\n"
        "**Steps of one turn.**\n"
        "1. Build the zip into that folder.\n"
    )

got = _decide(_tmp, CHECKLIST_TARGET)
if got != "pass":
    failures.append(("build-output/", "pass", got,
                     "a declared path is permitted"))
print(f"[{'ok' if got == 'pass' else 'FAIL'}] declared path -> {got} "
      "(the checklist's own definition permits it)")

got = _decide(_tmp, UNDECLARED_TARGET)
if got != "deny":
    failures.append(("build-output-other/", "deny", got,
                     "an undeclared sibling is still denied"))
print(f"[{'ok' if got == 'deny' else 'FAIL'}] undeclared sibling -> {got} "
      "(a near-miss prefix does not widen the declaration)")

got = _decide(_tmp, os.path.join(_tmp, "README.md"))
if got != "deny":
    failures.append(("README.md", "deny", got,
                     "the standing list is otherwise unchanged"))
print(f"[{'ok' if got == 'deny' else 'FAIL'}] ordinary file, cycles doc present "
      f"-> {got} (declaring one path widens nothing else)")

os.remove(os.path.join(_tmp, "CYCLES.md"))

print()
if failures:
    print(f"{len(failures)} failure(s):")
    for path, expected, got, what in failures:
        print(f"  {path!r}: expected {expected}, got {got} — {what}")
    sys.exit(1)
print("all cases passed")
