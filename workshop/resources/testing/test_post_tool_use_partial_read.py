#!/usr/bin/env python3
"""Regression test for post_tool_use.py's partial-read advisory.

Host-only dev artifact — not shipped in the plugin package.

Run:  py workshop/resources/testing/test_post_tool_use_partial_read.py

Why this exists ([over-cap-docs-read-one-page-in-consumer-session]): three
reads in a tester's session each returned a partial view with a "call again
with offset" note, and the session took the first page as the read each
time. After a Read whose result carries the truncation note, the hook prints
one advisory line naming the file and the offset to call again with.

Two cases: a truncated Read result produces the line; a whole one produces
nothing.
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
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "post_tool_use.py")
_failures = []

NOTE = ("[Truncated: PARTIAL view — C:\\p\\docs\\skill-nonspecific-rules.md: showing "
        "lines 1-1265 of 1499 total (25170 tokens, cap 25000). Call Read with "
        "offset=1266 limit=1265 for the next page, or Grep to find a specific "
        "section. Do NOT answer from this page alone if the answer may be further "
        "in the file.]")


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        _failures.append(name)


def drive(cwd, response):
    payload = {"cwd": cwd, "tool_name": "Read",
               "tool_input": {"file_path": os.path.join(cwd, "docs", "skill-nonspecific-rules.md")},
               "tool_response": response, "session_id": "partial-read-test"}
    proc = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                          capture_output=True, text=True, encoding="utf-8")
    if not proc.stdout.strip():
        return ""
    return json.loads(proc.stdout)["hookSpecificOutput"].get("additionalContext", "")


def main():
    print("partial-read advisory:")
    d = tempfile.mkdtemp(prefix="partial-read-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")

    out = drive(d, "1\tline one\n2\tline two\n\n" + NOTE)
    check("a truncated result draws the advisory", "Partial read" in out, out)
    check("it names the file and the offset",
          "skill-nonspecific-rules.md" in out and "offset=1266" in out, out)

    out = drive(d, {"type": "text", "file": {"content": "1\tline one\n" + NOTE}})
    check("a structured result carrying the note is read too", "offset=1266" in out, out)

    out = drive(d, "1\tline one\n2\tline two\n")
    check("a whole result produces nothing", out == "", out)

    if _failures:
        print(f"\n{len(_failures)} FAILURE(S)")
        return 1
    print("\nall passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
