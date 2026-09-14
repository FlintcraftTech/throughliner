#!/usr/bin/env python3
"""Regression test for the hooks' project-root helper.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_hooks_project_root.py

Why this exists ([scope-lock-root-follows-shell-cwd]): the hook payload's
`cwd` follows Claude's last shell `cd`, so in a nested project a `cd` into
the inner repository at the commit step made the next edits to the outer's
LOG/ refuse. Each of the four hooks now carries `project_root(data)`: the
`CLAUDE_PROJECT_DIR` variable where it is set and holds SPEC.md, otherwise
the payload's cwd; and a cwd inside `.claude/worktrees/` is kept.

Assertions: with the payload's cwd one folder below the root and the variable
set to the root, an Edit to LOG/index.md is allowed; with the variable unset,
the shipped behaviour (the edit refused, since the file is outside the cwd);
the helper keeps a worktree cwd; and all four hooks carry the helper and no
raw `data.get("cwd"` read is left at their entry.
"""

import json
import os
import re
import subprocess
import sys
import tempfile

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = os.path.join(ROOT, "plugin", "throughliner", "hooks")
HOOK = os.path.join(HOOKS, "pre_tool_use.py")
sys.path.insert(0, HOOKS)
import pre_tool_use  # noqa: E402

SESSION = "project-root-test-session"
_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("  -- " + detail if detail else ""))
        _failures.append(name)


def make_nested_project():
    d = tempfile.mkdtemp(prefix="project-root-test-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    os.makedirs(os.path.join(d, "LOG"))
    with open(os.path.join(d, "LOG", "index.md"), "w", encoding="utf-8") as f:
        f.write("# index\n")
    os.makedirs(os.path.join(d, "inner", ".git"))
    # The inner carries a part SPEC.md, so the hook reads it as adopted and
    # the shipped behaviour — every path test against the inner — is visible
    # as a refusal rather than as an unadopted early return.
    with open(os.path.join(d, "inner", "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# part SPEC\n")
    return d


def drive_edit(cwd, filepath, env_root=None):
    env = dict(os.environ)
    env.pop("CLAUDE_PROJECT_DIR", None)
    if env_root is not None:
        env["CLAUDE_PROJECT_DIR"] = env_root
    payload = {"cwd": cwd, "tool_name": "Edit",
               "tool_input": {"file_path": filepath}, "session_id": SESSION}
    proc = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                          capture_output=True, text=True, encoding="utf-8", env=env)
    if not proc.stdout.strip():
        return "allow"
    return json.loads(proc.stdout)["hookSpecificOutput"].get("permissionDecision", "allow")


def main():
    print("hooks' project root:")
    d = make_nested_project()
    inner = os.path.join(d, "inner")
    index = os.path.join(d, "LOG", "index.md")

    check("cwd in the inner, variable set to the root: LOG/index.md allowed",
          drive_edit(inner, index, env_root=d) == "allow")
    check("cwd in the inner, variable unset: the shipped behaviour (refused)",
          drive_edit(inner, index, env_root=None) == "deny")
    check("cwd at the root, variable unset: allowed as before",
          drive_edit(d, index, env_root=None) == "allow")

    # The helper in isolation.
    os.environ["CLAUDE_PROJECT_DIR"] = d
    try:
        check("helper returns the variable where it holds SPEC.md",
              os.path.normcase(pre_tool_use.project_root({"cwd": inner})) == os.path.normcase(d))
        wt = os.path.join(d, ".claude", "worktrees", "abc")
        check("helper keeps a cwd inside .claude/worktrees/",
              pre_tool_use.project_root({"cwd": wt}) == wt)
        empty = tempfile.mkdtemp(prefix="no-spec-")
        os.environ["CLAUDE_PROJECT_DIR"] = empty
        check("helper ignores a variable whose folder holds no SPEC.md",
              pre_tool_use.project_root({"cwd": inner}) == inner)
    finally:
        os.environ.pop("CLAUDE_PROJECT_DIR", None)

    # All four hooks carry the helper, and none reads the payload's cwd raw
    # at its entry.
    for name in ("pre_tool_use.py", "post_tool_use.py", "session_start.py", "stop.py"):
        with open(os.path.join(HOOKS, name), encoding="utf-8") as f:
            src = f.read()
        check(f"{name} defines project_root", "def project_root(" in src)
        raw = [m for m in re.finditer(r'data\.get\("cwd"|payload\.get\("cwd"', src)]
        # The helper's own read is the one permitted occurrence.
        check(f"{name} reads cwd only inside the helper", len(raw) == 1, str(len(raw)))

    if _failures:
        print(f"\n{len(_failures)} FAILURE(S)")
        return 1
    print("\nall passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
