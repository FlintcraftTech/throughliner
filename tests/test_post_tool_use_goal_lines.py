#!/usr/bin/env python3
"""Fixture suite for the SPEC.md Goals lint ([goal-lines-in-tasks-marks]).

Run: py tests/test_post_tool_use_goal_lines.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

A goal in a project's SPEC is one checkbox line in the Obsidian Tasks
plugin's marks tagged #goal, so a query note of the user's gathers every
project's goals the way the #user queries gather every project's steps. After
an edit lands on SPEC.md the hook reads the Goals section and names a line
missing any part — the checkbox, the reached-when clause, the project, the
🆔 slug or the #goal tag — and a line carrying #user, advisory and once while
it stands, through a state file beside the queue lint's.
"""

import contextlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "post_tool_use.py")

failures = []


def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


def load_hook():
    spec = importlib.util.spec_from_file_location("post_tool_use", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GOOD_LINE = ("- [ ] Ship the thing, reached when the page loads (Demo) "
             "🆔 ship-the-thing #goal")

SPEC = """# SPEC — Demo

## How it works

- [ ] not a goal, a feature bullet with no marks

## Goals

Where the project is heading.

{line}
  History of the goal, left alone.
- [x] An earlier goal, reached when it shipped (Demo) 🆔 earlier-goal #goal

## Principles

- Never a goal line here: `- [ ] bare` is outside the section.
"""


hook = load_hook()


def test_well_formed_section_is_silent():
    warnings = hook.lint_goals(SPEC.format(line=GOOD_LINE))
    check("a well-formed Goals section draws no warning", not warnings,
          repr(warnings))


def test_each_missing_part_is_named():
    cases = (
        ("reached when", GOOD_LINE.replace(", reached when the page loads", "")),
        ("the project in brackets", GOOD_LINE.replace(" (Demo)", "")),
        ("🆔 <slug>", GOOD_LINE.replace(" 🆔 ship-the-thing", "")),
        ("#goal", GOOD_LINE.replace(" #goal", "")),
    )
    for part, line in cases:
        warnings = hook.lint_goals(SPEC.format(line=line))
        check(f"a line missing {part} is named for it",
              len(warnings) == 1 and part in warnings[0], repr(warnings))


def test_sentence_shaped_goal_is_flagged_as_a_bullet():
    old = ("- **Ship the thing.** Reached when: the page loads.")
    warnings = hook.lint_goals(SPEC.format(line=old))
    check("a goal in the older bullet shape is flagged",
          len(warnings) == 1 and "rather than a checkbox" in warnings[0],
          repr(warnings))


def test_user_tag_on_a_goal_is_flagged():
    for tag in ("#user", "#user/alex"):
        warnings = hook.lint_goals(SPEC.format(line=GOOD_LINE + " " + tag))
        check(f"a goal line carrying {tag} is flagged",
              any("carries #user" in w for w in warnings), repr(warnings))


def test_lines_outside_the_section_are_not_read():
    spec = SPEC.format(line=GOOD_LINE).replace("## Goals", "## Aims")
    check("a spec with no Goals heading draws nothing",
          hook.lint_goals(spec) == [], repr(hook.lint_goals(spec)))


def run_hook(d, filepath):
    out = io.StringIO()
    data = {"tool_name": "Edit", "tool_input": {"file_path": filepath},
            "cwd": d, "session_id": "sess-goals"}
    stdin = io.StringIO(json.dumps(data))
    with contextlib.redirect_stdout(out):
        real = sys.stdin
        sys.stdin = stdin
        try:
            hook.main()
        finally:
            sys.stdin = real
    raw = out.getvalue().strip()
    return json.loads(raw)["hookSpecificOutput"]["additionalContext"] if raw else ""


def test_hook_prints_once_while_the_flag_stands():
    d = tempfile.mkdtemp(prefix="goals-lint-")
    try:
        spec_path = os.path.join(d, "SPEC.md")
        with open(spec_path, "w", encoding="utf-8") as f:
            f.write(SPEC.format(line=GOOD_LINE.replace(" #goal", "")))
        text1 = run_hook(d, spec_path)
        check("after an edit to SPEC.md the missing tag is named",
              "Goals lint" in text1 and "#goal" in text1, repr(text1))
        text2 = run_hook(d, spec_path)
        check("the same flag does not print on the next edit",
              "Goals lint" not in text2, repr(text2))
        with open(spec_path, "w", encoding="utf-8") as f:
            f.write(SPEC.format(line=GOOD_LINE))
        text3 = run_hook(d, spec_path)
        check("a fixed section prints nothing", "Goals lint" not in text3,
              repr(text3))
        with open(spec_path, "w", encoding="utf-8") as f:
            f.write(SPEC.format(line=GOOD_LINE.replace(" #goal", "")))
        text4 = run_hook(d, spec_path)
        check("a flag that went and came back prints again",
              "Goals lint" in text4, repr(text4))
        other = os.path.join(d, "QUEUE.md")
        with open(other, "w", encoding="utf-8") as f:
            f.write("# QUEUE\n\n## Processed\n\n--- Cleared to run above this line ---\n\n## Unprocessed\n")
        text5 = run_hook(d, other)
        check("an edit to another file runs no Goals lint",
              "Goals lint" not in text5, repr(text5))
    finally:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    print("test_post_tool_use_goal_lines")
    test_well_formed_section_is_silent()
    test_each_missing_part_is_named()
    test_sentence_shaped_goal_is_flagged_as_a_bullet()
    test_user_tag_on_a_goal_is_flagged()
    test_lines_outside_the_section_are_not_read()
    test_hook_prints_once_while_the_flag_stands()
    print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
    sys.exit(1 if failures else 0)
