#!/usr/bin/env python3
"""Regression tests for pre_tool_use.py's time-word scan.

Host-only dev artifact — not shipped in the plugin package.

Run:  py workshop/resources/testing/test_pre_tool_use_time_words.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

[unfounded-time-words-stopped-once]: a relative time word with no source —
"yesterday", "an hour ago", "this morning" — written into a session record,
the queue or SPEC is refused once per distinct phrase per session, then
allowed. A write to any other file is untouched, and a phrase inside
backticks or quotation marks passes, since quoted text is someone else's
words or a specimen.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "pre_tool_use.py")

SESSION = "time-words-session"
failures = []


def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


def project():
    """A set-up project with no build: SPEC.md, QUEUE.md, LOG/, and a research
    folder, so the standing list admits every path these cases write."""
    d = tempfile.mkdtemp(prefix="time-words-test-")
    for name in ("SPEC.md", "QUEUE.md"):
        with open(os.path.join(d, name), "w", encoding="utf-8") as f:
            f.write("# " + name + "\n")
    os.makedirs(os.path.join(d, "LOG"))
    os.makedirs(os.path.join(d, "workshop", "resources", "research"))
    return d


def drive(cwd, tool_name, filepath, tool_input):
    payload = {
        "cwd": cwd,
        "tool_name": tool_name,
        "tool_input": dict(tool_input, file_path=filepath),
        "session_id": SESSION,
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
    return json.loads(proc.stdout)["hookSpecificOutput"]


def decision(result):
    return result.get("permissionDecision", "allow")


def main():
    print("test_pre_tool_use_time_words")

    # 1. A LOG write carrying "yesterday" is refused once, then allowed.
    d = project()
    log_file = os.path.join(d, "LOG", "2026-09-06-something.md")
    first = drive(d, "Write", log_file,
                  {"content": "# Record\n\nWe decided this yesterday.\n"})
    check("a LOG write carrying 'yesterday' is refused",
          decision(first) == "deny"
          and '"yesterday"' in first.get("permissionDecisionReason", ""),
          repr(first))
    log_path = os.path.join(d, ".throughliner", "pre-tool-use.log")
    with open(log_path, encoding="utf-8") as f:
        log_text = f.read()
    check("the decision log names the branch 'time word'",
          "\tdeny\ttime word\t" in log_text, log_text)
    second = drive(d, "Write", log_file,
                   {"content": "# Record\n\nWe decided this yesterday.\n"})
    check("the same phrase is allowed on the second attempt",
          decision(second) == "allow", repr(second))

    # 1b. A different phrase in the same session is still refused once.
    third = drive(d, "Edit", os.path.join(d, "QUEUE.md"),
                  {"old_string": "x", "new_string": "Filed an hour ago."})
    check("a different phrase is refused once too",
          decision(third) == "deny", repr(third))

    # 2. A write to a research file carrying the phrase is allowed.
    d2 = project()
    research = os.path.join(d2, "workshop", "resources", "research", "note.md")
    r = drive(d2, "Write", research, {"content": "Found yesterday.\n"})
    check("a research-file write carrying 'yesterday' is allowed",
          decision(r) == "allow", repr(r))

    # 3. An Edit to QUEUE.md with the phrase inside backticks or quotation
    # marks is allowed.
    d3 = project()
    q = os.path.join(d3, "QUEUE.md")
    r = drive(d3, "Edit", q, {"old_string": "x",
                              "new_string": "The rule names `an hour ago`."})
    check("a phrase inside backticks is allowed", decision(r) == "allow", repr(r))
    r = drive(d3, "Edit", q, {"old_string": "x",
                              "new_string": 'Her words: "do it like yesterday".'})
    check("a phrase inside quotation marks is allowed",
          decision(r) == "allow", repr(r))
    r = drive(d3, "Edit", q, {"old_string": "x",
                              "new_string": "Filed 2026-09-06 21:50, read from the clock."})
    check("a dated line with no phrase is allowed", decision(r) == "allow", repr(r))

    # 4. [counted-up-clock-times-uncaught]: a clock time later than the clock
    # is refused once; a past time, a quoted time and a dated past time pass.
    d4 = project()
    q4 = os.path.join(d4, "QUEUE.md")
    os.environ["THROUGHLINER_TEST_CLOCK"] = "2026-09-09 12:00"
    try:
        r = drive(d4, "Edit", q4, {"old_string": "x",
                                   "new_string": "Filed at 14:30, stamped by the queue tool."})
        check("a clock time later than the clock is refused",
              decision(r) == "deny"
              and "14:30" in r.get("permissionDecisionReason", "")
              and "12:00" in r.get("permissionDecisionReason", ""),
              repr(r))
        with open(os.path.join(d4, ".throughliner", "pre-tool-use.log"), encoding="utf-8") as f:
            check("the decision log names the branch 'future clock time'",
                  "\tdeny\tfuture clock time\t" in f.read())
        r = drive(d4, "Edit", q4, {"old_string": "x",
                                   "new_string": "Filed at 14:30, stamped by the queue tool."})
        check("the same future time is allowed on the second attempt",
              decision(r) == "allow", repr(r))
        r = drive(d4, "Edit", q4, {"old_string": "x",
                                   "new_string": "Filed at 11:45, read from the clock."})
        check("a time behind the clock is allowed", decision(r) == "allow", repr(r))
        r = drive(d4, "Edit", q4, {"old_string": "x",
                                   "new_string": "Filed at 12:00, read from the clock."})
        check("a time equal to the clock is allowed", decision(r) == "allow", repr(r))
        r = drive(d4, "Edit", q4, {"old_string": "x",
                                   "new_string": 'The wrong stamp read "15:20".'})
        check("a future time inside quotation marks is allowed",
              decision(r) == "allow", repr(r))
        r = drive(d4, "Edit", q4, {"old_string": "x",
                                   "new_string": "Opened 2026-09-08 22:26, per its record."})
        check("a time carrying an earlier date is allowed",
              decision(r) == "allow", repr(r))
        r = drive(d4, "Edit", q4, {"old_string": "x",
                                   "new_string": "Due 2026-09-10 09:00."})
        check("a time carrying a later date is refused",
              decision(r) == "deny", repr(r))
        r = drive(d4, "Write", os.path.join(d4, "workshop", "resources", "research", "n.md"),
                  {"content": "Seen at 18:00.\n"})
        check("a future time in a research file is allowed",
              decision(r) == "allow", repr(r))
    finally:
        del os.environ["THROUGHLINER_TEST_CLOCK"]

    for folder in (d, d2, d3, d4):
        shutil.rmtree(folder, ignore_errors=True)

    print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
