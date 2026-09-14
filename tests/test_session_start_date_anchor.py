#!/usr/bin/env python3
"""Regression tests for session_start.py's date-at-session-start line.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_session_start_date_anchor.py

No test framework, matching the suites alongside it: this project has no test
runner, and `python` on the author's machine resolves to an application's
bundled interpreter that has no pytest.

Why this exists ([session-date-anchor]): sessions were deriving today's date by
assumption and writing wrong ones into records and captures. That failure is
invisible downstream — a wrong date reads exactly like a right one — so the
anchor has to be a fact the payload carries, and the thing worth pinning is
that it is genuinely there and genuinely from the clock rather than a plausible
constant somebody typed.

The hook is driven end to end as a subprocess, because the line is emitted in
main() rather than by a helper a test could call.
"""

import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "session_start.py")
PLUGIN_ROOT = os.path.join(ROOT, "plugin", "throughliner")

failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        failures.append(name)


def project():
    """A minimal adopted project — enough for the hook to take the set-up path."""
    d = tempfile.mkdtemp(prefix="session-start-date-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n\n## What this is\nA fixture.\n")
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8") as f:
        f.write("# QUEUE\n\n## Processed\n\n"
                "--- Cleared to run above this line ---\n\n## Unprocessed\n")
    os.makedirs(os.path.join(d, "LOG"))
    return d


def run_hook(cwd):
    payload = json.dumps({"cwd": cwd, "session_id": "date-anchor-fixture"})
    env = dict(os.environ)
    env["CLAUDE_PLUGIN_ROOT"] = PLUGIN_ROOT
    proc = subprocess.run(
        [sys.executable, HOOK],
        input=payload,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        timeout=60,
    )
    if proc.returncode != 0:
        raise AssertionError(
            f"hook exited {proc.returncode}\nstdout: {proc.stdout}\n"
            f"stderr: {proc.stderr}"
        )
    data = json.loads(proc.stdout)
    return data["hookSpecificOutput"]["additionalContext"]


d = project()
try:
    context = run_hook(d)
except Exception as exc:  # noqa: BLE001 — a failure to run IS the finding
    print("  FAIL the hook runs against a minimal adopted project"
          f"\n       {exc}")
    failures.append("the hook runs against a minimal adopted project")
    context = ""

check(
    "the payload carries a date-at-session-start line",
    "Date at session start:" in context,
    f"context was: {context[:400]!r}",
)

today = datetime.date.today().isoformat()
check(
    "the line carries today's real date, read from the clock",
    today in context,
    f"expected {today} in the payload; got: {context[:400]!r}",
)

check(
    "the line says the date is at session start, not 'today'",
    "Date at session start:" in context and "session start" in context,
    f"context was: {context[:400]!r}",
)

check(
    "the line tells the session not to derive the date by assumption",
    "by assumption" in context,
    f"context was: {context[:400]!r}",
)

# The line carries a time of day beside the date ([captures-carry-a-time]):
# a bare date left same-day relative-time claims ("this morning") with no
# source finer than a day. Matching "<date> HH:MM" loosely — the minute may
# tick over between the hook run and this check, so only the shape is pinned.
import re  # noqa: E402 — kept beside the one check that uses it

check(
    "the line carries a clock time beside the date",
    re.search(re.escape(today) + r" \d{2}:\d{2}", context) is not None,
    f"expected '{today} HH:MM' in the payload; got: {context[:400]!r}",
)

shutil.rmtree(d, ignore_errors=True)

print()
if failures:
    print(f"{len(failures)} failure(s):")
    for name in failures:
        print(f"  {name}")
    sys.exit(1)
print("all cases passed")
