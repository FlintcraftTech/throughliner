#!/usr/bin/env python3
"""Regression tests for pre_tool_use.py admitting a goals session's own writes.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_pre_tool_use_goals_writes.py

Why this exists ([goals-skill-writes-blocked]): the goals command writes two
notes, `goals.md` and `strategy.md`, in the folder holding the note the
project's `Task list:` line names. A session that typed a Throughliner command
has no cold door through the scope-lock, so the user had to say yes twice and
a `_freeform` scope file was left behind. The check now admits those two
paths itself, in a goals session and nowhere else.

Every case drives the hook directly against a made-up project and session.
"""

import json
import os
import subprocess
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "pre_tool_use.py")

SESSION = "goals-test-session"

_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("  -- " + detail if detail else ""))
        _failures.append(name)


def make_project(task_list_line="Task list: notes/TASKS.md", skill="goals"):
    """Temp project: SPEC.md, a CLAUDE.md carrying the given line (None for no
    line), the task-list note's folder, and the prompt hook's record of the
    session's typed command (None for no record)."""
    d = tempfile.mkdtemp(prefix="goals-writes-test-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n\n## Goals\n\n- [ ] A goal, reached when it is "
                "(Test) 🆔 a-goal #goal\n")
    claude = "# CLAUDE.md\n\nSome project.\n"
    if task_list_line is not None:
        claude += "\n" + task_list_line + "\n"
    with open(os.path.join(d, "CLAUDE.md"), "w", encoding="utf-8") as f:
        f.write(claude)
    os.makedirs(os.path.join(d, "notes"), exist_ok=True)
    os.makedirs(os.path.join(d, "elsewhere"), exist_ok=True)
    os.makedirs(os.path.join(d, ".throughliner"), exist_ok=True)
    if skill is not None:
        state = os.path.join(d, ".throughliner",
                             "session-skill-%s.txt" % SESSION)
        with open(state, "w", encoding="utf-8") as f:
            f.write(skill + "\n")
    return d


def drive(cwd, filepath, tool="Write"):
    """Run the hook with a write payload; return the decision dict."""
    tool_input = {"file_path": filepath}
    if tool == "Write":
        tool_input["content"] = "# Goals\n"
    payload = {
        "cwd": cwd,
        "tool_name": tool,
        "tool_input": tool_input,
        "session_id": SESSION,
    }
    env = dict(os.environ)
    env.pop("CLAUDE_PROJECT_DIR", None)
    proc = subprocess.run(
        [sys.executable, HOOK],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )
    if not proc.stdout.strip():
        return {}
    return json.loads(proc.stdout)["hookSpecificOutput"]


def decision(result):
    return result.get("permissionDecision", "allow")


def log_text(d):
    try:
        with open(os.path.join(d, ".throughliner", "pre-tool-use.log"),
                  encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def main():
    print("goals session writes:")

    # 1. Both notes admitted in a goals session, with no prior refusal and no
    # scope file.
    d = make_project()
    for name in ("goals.md", "strategy.md"):
        r = drive(d, os.path.join(d, "notes", name))
        check("%s beside the task-list note is admitted in a goals session"
              % name, decision(r) == "allow", repr(r))
    check("no refusal was logged on the way",
          "\tdeny\t" not in log_text(d) and "deny" not in
          [ln.split("\t")[0] for ln in log_text(d).splitlines()],
          log_text(d))
    check("the admitting branch is named in the log",
          "goals session: its two notes" in log_text(d), log_text(d))
    check("no _freeform scope file was written",
          not [n for n in os.listdir(d) if n.startswith("_freeform-")],
          repr(os.listdir(d)))

    # 2. An Edit of an existing note is admitted the same way.
    with open(os.path.join(d, "notes", "goals.md"), "w", encoding="utf-8") as f:
        f.write("# Goals\n")
    r = drive(d, os.path.join(d, "notes", "goals.md"), tool="Edit")
    check("an Edit of goals.md is admitted in a goals session",
          decision(r) == "allow", repr(r))

    # 3. The same paths are refused in a session of another command.
    for skill in ("plan", "tasks", "none"):
        d = make_project(skill=skill)
        r = drive(d, os.path.join(d, "notes", "goals.md"))
        check("goals.md refused in a session whose command is %s" % skill,
              decision(r) == "deny", repr(r))
        r = drive(d, os.path.join(d, "notes", "strategy.md"))
        check("strategy.md refused in a session whose command is %s" % skill,
              decision(r) == "deny", repr(r))

    # 4. No record of the session's command: refused.
    d = make_project(skill=None)
    r = drive(d, os.path.join(d, "notes", "goals.md"))
    check("goals.md refused where the prompt hook left no record",
          decision(r) == "deny", repr(r))

    # 5. A goals.md in any other folder is refused, the project root included.
    d = make_project()
    for where in ("elsewhere", ""):
        r = drive(d, os.path.join(d, where, "goals.md"))
        check("goals.md in %s is refused" % (where or "the project root"),
              decision(r) == "deny", repr(r))

    # 6. Another file in the note's folder is refused, the note itself too.
    for name in ("TASKS.md", "other.md"):
        r = drive(d, os.path.join(d, "notes", name))
        check("%s beside the notes is refused" % name,
              decision(r) == "deny", repr(r))

    # 7. No `Task list:` line, or one reading none: refused.
    for line in (None, "Task list: none"):
        d = make_project(task_list_line=line)
        r = drive(d, os.path.join(d, "notes", "goals.md"))
        check("goals.md refused with %s"
              % ("no Task list: line" if line is None else "Task list: none"),
              decision(r) == "deny", repr(r))

    # 8. An absolute, backticked, bolded line resolves the same folder.
    d = make_project(task_list_line=None)
    note = os.path.join(d, "notes", "TASKS.md")
    with open(os.path.join(d, "CLAUDE.md"), "a", encoding="utf-8") as f:
        f.write("\n**Task list:** `%s`\n" % note)
    r = drive(d, os.path.join(d, "notes", "strategy.md"))
    check("an absolute, bolded, backticked Task list: line is read",
          decision(r) == "allow", repr(r))

    # 9. A note folder outside the project root is admitted, and only it.
    outside = tempfile.mkdtemp(prefix="goals-writes-vault-")
    d = make_project(task_list_line="Task list: %s"
                     % os.path.join(outside, "TASKS.md"))
    r = drive(d, os.path.join(outside, "goals.md"))
    check("goals.md beside a task-list note outside the project is admitted",
          decision(r) == "allow", repr(r))

    # 10. The session's other writes are admitted already, in any session:
    # a goal's tick in the project's own SPEC.md and an address-book row.
    for skill in ("goals", "plan"):
        d = make_project(skill=skill)
        r = drive(d, os.path.join(d, "SPEC.md"), tool="Edit")
        check("SPEC.md edit admitted in a %s session" % skill,
              decision(r) == "allow", repr(r))
        r = drive(d, os.path.join(d, ".throughliner", "address-book.md"),
                  tool="Edit")
        check("address-book edit admitted in a %s session" % skill,
              decision(r) == "allow", repr(r))

    print()
    if _failures:
        print("%d check(s) failed: %s" % (len(_failures), ", ".join(_failures)))
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
