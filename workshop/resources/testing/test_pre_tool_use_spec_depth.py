#!/usr/bin/env python3
"""Regression tests for pre_tool_use.py's per-part SPEC.md matching.

Host-only dev artifact — not shipped in the plugin package.

Run:  py workshop/resources/testing/test_pre_tool_use_spec_depth.py

Why this exists ([per-part-specs]): each part of a project carries its own
SPEC.md in its folder beneath the root spec, and planning writes a decision's
sentence into the part's spec where it concerns that part. The planning
standing list matched only the root SPEC.md, so every such write was denied.
The list now matches a file named SPEC.md at any depth inside the project —
a nested project's inner repository included — and a build still edits one
only by listing its path in Files:, exactly as for the root spec.

Assertions: with no build working file, a part's SPEC.md at one and two
levels down is allowed and one inside an inner repository is allowed; a
differently named file beside it is still denied; with a build working file,
a part's SPEC.md is allowed only where Files: lists it.
"""

import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "pre_tool_use.py")

SESSION = "test-session"

_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("  -- " + detail if detail else ""))
        _failures.append(name)


def make_project(build_files=None):
    """Temp project dir: root SPEC.md always; a build working file when given."""
    d = tempfile.mkdtemp(prefix="spec-depth-test-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    if build_files is not None:
        lines = ["# Active Build\n\nFiles:\n"]
        for p in build_files:
            lines.append("- " + p + "\n")
        with open(os.path.join(d, f"_build-{SESSION}.md"), "w",
                  encoding="utf-8") as f:
            f.write("".join(lines))
    return d


def drive_edit(cwd, filepath):
    payload = {
        "cwd": cwd,
        "tool_name": "Edit",
        "tool_input": {"file_path": filepath},
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
    print("per-part SPEC.md depth:")

    # 1. Planning session (no build working file): a part's spec is allowed.
    d = make_project()
    one_deep = os.path.join(d, "app", "SPEC.md")
    two_deep = os.path.join(d, "process", "research", "SPEC.md")
    inner = os.path.join(d, "product", "SPEC.md")
    os.makedirs(os.path.join(d, "product", ".git"))  # an inner repository
    for label, path in (("one level down", one_deep),
                        ("two levels down", two_deep),
                        ("inside an inner repository", inner)):
        r = drive_edit(d, path)
        check("planning: part SPEC.md " + label + " allowed",
              decision(r) == "allow", repr(r))

    # 2. A differently named file beside a part's spec is still denied.
    beside = os.path.join(d, "app", "spec-notes.md")
    r = drive_edit(d, beside)
    check("planning: a non-SPEC file beside it still denied",
          decision(r) == "deny", repr(r))

    # 3. Build session: a part's spec is allowed only where Files: lists it.
    d2 = make_project(build_files=["app/SPEC.md"])
    listed = os.path.join(d2, "app", "SPEC.md")
    unlisted = os.path.join(d2, "process", "SPEC.md")
    r = drive_edit(d2, listed)
    check("build: part SPEC.md listed in Files: allowed",
          decision(r) == "allow", repr(r))
    r = drive_edit(d2, unlisted)
    check("build: part SPEC.md NOT listed in Files: denied",
          decision(r) == "deny", repr(r))

    print()
    if _failures:
        print(f"{len(_failures)} FAILED: {_failures}")
        sys.exit(1)
    print("all passed")


if __name__ == "__main__":
    main()
