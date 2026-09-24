#!/usr/bin/env python3
"""Regression test for pre_tool_use.py's refusal of a build record claiming
an unticked item.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_pre_tool_use_record_claims_unticked.py

Why this exists ([close-records-unticked-item-as-built]): a close wrote a
build record, an index line and a commit message for an item that was in the
run's item list but never built or ticked, and nothing mechanical stopped it.
A run removes each item from the queue at its tick, so a build record naming
a slug still in Processed is always a false claim. The hook refuses that Write
and names the slug; a NOT BUILT record, a user-step record, a planning
record, a slug not in the queue, and an Edit appending to an existing record
all pass. Driven as a subprocess with real PreToolUse payloads, in the shape
of test_pre_tool_use_overwrite_guard.py.
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

_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        _failures.append(name)


QUEUE = """# QUEUE

## Processed

#### Still queued, never ticked [still-queued]
Prose.

--- Cleared to run above this line ---

## Unprocessed

#### A capture [a-capture]
Prose.
"""


def make_project():
    d = tempfile.mkdtemp(prefix="record-claims-test-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8") as f:
        f.write(QUEUE)
    os.makedirs(os.path.join(d, "LOG"))
    return d


def drive(cwd, tool_name, relpath, tool_input):
    payload = {"cwd": cwd, "tool_name": tool_name,
               "tool_input": dict(tool_input, file_path=os.path.join(cwd, relpath)),
               "session_id": "test-session"}
    proc = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                          capture_output=True, text=True, encoding="utf-8",
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    if not proc.stdout.strip():
        return {}
    try:
        return json.loads(proc.stdout).get("hookSpecificOutput") or {}
    except json.JSONDecodeError:
        return {}


def decision(out):
    return out.get("permissionDecision", "allow")


def main():
    print("test_pre_tool_use_record_claims_unticked")
    d = make_project()
    build = "# abc1234 — build — the thing, built and confirmed\n\nRecorded 2026-09-24 16:00.\n"

    out = drive(d, "Write", os.path.join("LOG", "2026-09-24-still-queued.md"),
                {"content": build})
    check("a build record for a slug still in Processed is refused",
          decision(out) == "deny", repr(out))
    check("the refusal names the slug and says it was never ticked",
          "[still-queued]" in out.get("permissionDecisionReason", "")
          and "never ticked" in out.get("permissionDecisionReason", ""), repr(out))

    out = drive(d, "Write", os.path.join("LOG", "2026-09-24-shipped-thing.md"),
                {"content": build})
    check("a build record for a slug not in the queue passes",
          decision(out) == "allow", repr(out))
    out = drive(d, "Write", os.path.join("LOG", "2026-09-24-a-capture.md"),
                {"content": build})
    check("a build record for a slug in Unprocessed passes",
          decision(out) == "allow", repr(out))

    out = drive(d, "Write", os.path.join("LOG", "2026-09-24-still-queued-2.md"),
                {"content": "# abc1234 — build — NOT BUILT: the run stopped before it\n"})
    check("a NOT BUILT record passes", decision(out) == "allow", repr(out))
    out = drive(d, "Write", os.path.join("LOG", "2026-09-24-still-queued-3.md"),
                {"content": "# abc1234 — user step — walked to its second step\n"})
    check("a user-step record passes", decision(out) == "allow", repr(out))
    out = drive(d, "Write", os.path.join("LOG", "2026-09-24-still-queued-4.md"),
                {"content": "# abc1234 — planning — processed into Processed\n\nWork processed: one.\n"})
    check("a planning record passes", decision(out) == "allow", repr(out))
    out = drive(d, "Write", os.path.join("LOG", "2026-09-24-chat-build.md"),
                {"content": "# abc1234 — chat-level record for the build run\n"})
    check("a chat-level record passes", decision(out) == "allow", repr(out))

    existing = os.path.join(d, "LOG", "2026-09-24-still-queued-build.md")
    with open(existing, "w", encoding="utf-8") as f:
        f.write("# abc1234 — build — earlier\n")
    out = drive(d, "Edit", os.path.join("LOG", "2026-09-24-still-queued-build.md"),
                {"old_string": "earlier", "new_string": "earlier, with a tail"})
    check("an Edit appending to an existing record passes",
          decision(out) == "allow", repr(out))

    if _failures:
        print("\n%d FAILURE(S)" % len(_failures))
        return 1
    print("\nall passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
