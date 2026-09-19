#!/usr/bin/env python3
"""Regression tests for pre_tool_use.py's freeform scope file.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_pre_tool_use_freeform_scope.py

Why this exists ([freeform-blocked-by-standing-list]): a freeform session runs
with no build working file, so Rule 4's standing list denied it the very files
its own queue item names — the 2026-08-21 freeform sitting was worked around by
hand, once per file, on approval. The fix: the session declares a scope file
(`_freeform-<session-id>.md`, same shape as the build working file) whose
Files: paths extend the standing list for that session.

Three assertions: a listed path is allowed, an unlisted path is still denied,
and a session with no scope file behaves exactly as before.
"""

import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "pre_tool_use.py")

SESSION = "test-session"

_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("  -- " + detail if detail else ""))
        _failures.append(name)


def make_project(scope_files=None):
    """Temp project dir: SPEC.md always; a freeform scope file when given."""
    d = tempfile.mkdtemp(prefix="freeform-test-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    if scope_files is not None:
        lines = ["# Freeform scope\n\nFiles:\n"]
        for p in scope_files:
            lines.append("- " + p + "\n")
        path = os.path.join(d, f"_freeform-{SESSION}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("".join(lines))
    return d


def drive_edit(cwd, filepath):
    """Run the hook with an Edit PreToolUse payload; return the decision dict."""
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
    print("freeform scope file:")

    # 1. A path the scope file lists is allowed — but only after a logged
    # refusal of that same path in this session
    # ([sweep-security-users-door-is-self-declared]). The first attempt with
    # the scope file present and no earlier refusal is refused, and the
    # refusal names the door's condition; that refusal is then the one the
    # second attempt reads from the log.
    d = make_project(scope_files=["plugin/docs/some-doc.md"])
    target = os.path.join(d, "plugin", "docs", "some-doc.md")
    cold = drive_edit(d, target)
    check(
        "listed path with NO prior refusal is refused",
        decision(cold) == "deny"
        and "door opens only" in cold.get("permissionDecisionReason", ""),
        repr(cold),
    )
    log_path = os.path.join(d, ".throughliner", "pre-tool-use.log")
    with open(log_path, encoding="utf-8") as f:
        log_text = f.read()
    check(
        "that refusal is logged with the door branch and the session id",
        "freeform scope file: no prior refusal" in log_text
        and ("\t" + SESSION + "\n") in log_text,
        log_text,
    )
    check(
        "listed path allowed after the logged refusal",
        decision(drive_edit(d, target)) == "allow",
        repr(drive_edit(d, target)),
    )

    # 1b. A refusal logged under a DIFFERENT session id does not open the door.
    d1 = make_project(scope_files=["plugin/docs/some-doc.md"])
    target1 = os.path.join(d1, "plugin", "docs", "some-doc.md")
    os.makedirs(os.path.join(d1, ".throughliner"))
    with open(os.path.join(d1, ".throughliner", "pre-tool-use.log"), "w",
              encoding="utf-8") as f:
        f.write("2026-09-06 21:00:00\tEdit\tdeny\tplanning standing list: "
                "not on it\t" + target1 + "\tother-session\n")
    check(
        "another session's refusal does not open the door",
        decision(drive_edit(d1, target1)) == "deny",
        repr(drive_edit(d1, target1)),
    )

    # 2. A path the scope file does not list is still denied.
    off_list = os.path.join(d, "plugin", "docs", "other-doc.md")
    check(
        "unlisted path denied",
        decision(drive_edit(d, off_list)) == "deny",
        repr(drive_edit(d, off_list)),
    )

    # 3. No scope file: behaviour unchanged — the same path is denied.
    d2 = make_project(scope_files=None)
    target2 = os.path.join(d2, "plugin", "docs", "some-doc.md")
    check(
        "no scope file, off-surface path denied as before",
        decision(drive_edit(d2, target2)) == "deny",
        repr(drive_edit(d2, target2)),
    )

    # 3b. No scope file: standing-list paths still pass.
    check(
        "no scope file, QUEUE.md still allowed",
        decision(drive_edit(d2, os.path.join(d2, "QUEUE.md"))) == "allow",
    )

    # 4. The scope file itself is writable (a freeform session's first write).
    scope_path = os.path.join(d2, f"_freeform-{SESSION}.md")
    check(
        "the scope file itself is writable",
        decision(drive_edit(d2, scope_path)) == "allow",
        repr(drive_edit(d2, scope_path)),
    )

    # 5. The user's door ([post-close-lock-blocks-user-work]): a scope file
    # with a Files: list and NO queue item behind it extends the list — the
    # hook reads the file and consults no queue. The project here has no
    # QUEUE.md at all, which is the strongest form of "no queue item". The
    # refusal comes first, as in case 1: the path is refused with no scope
    # file, the scope file is then written, and the write passes.
    d3 = make_project(scope_files=None)
    assert not os.path.exists(os.path.join(d3, "QUEUE.md"))
    claude_md = os.path.join(d3, "CLAUDE.md")
    check(
        "the door's precondition: the path is refused first",
        decision(drive_edit(d3, claude_md)) == "deny",
    )
    with open(os.path.join(d3, f"_freeform-{SESSION}.md"), "w",
              encoding="utf-8") as f:
        f.write("# Freeform scope\n\nFiles:\n- CLAUDE.md\n")
    check(
        "scope file with no queue item extends the list after the refusal (the user's door)",
        decision(drive_edit(d3, claude_md)) == "allow",
        repr(drive_edit(d3, claude_md)),
    )

    # 5b. The no-build denial names the door.
    d4 = make_project(scope_files=None)
    denied = drive_edit(d4, os.path.join(d4, "CLAUDE.md"))
    check(
        "the no-build denial message names the scope-file door",
        decision(denied) == "deny"
        and "_freeform-<session-id>.md" in denied.get("permissionDecisionReason", ""),
        repr(denied),
    )

    # 7. [freeform-scope-paths-matched-literally]: a backticked bullet and an
    # annotated bullet both match their path, and a refusal with a scope file
    # that names nothing matching says so.
    d6 = make_project(scope_files=["`plugin/docs/ticked.md`",
                                   "plugin/docs/noted.md — the one the item names"])
    ticked = os.path.join(d6, "plugin", "docs", "ticked.md")
    noted = os.path.join(d6, "plugin", "docs", "noted.md")
    drive_edit(d6, ticked)  # the door's first refusal
    check(
        "a backticked bullet matches its path",
        decision(drive_edit(d6, ticked)) == "allow",
        repr(drive_edit(d6, ticked)),
    )
    drive_edit(d6, noted)
    check(
        "an annotated bullet matches its path",
        decision(drive_edit(d6, noted)) == "allow",
        repr(drive_edit(d6, noted)),
    )
    unmatched = drive_edit(d6, os.path.join(d6, "plugin", "docs", "elsewhere.md"))
    check(
        "the refusal names the scope file when nothing in it matched",
        decision(unmatched) == "deny"
        and "nothing in its Files: list matched" in unmatched.get("permissionDecisionReason", ""),
        repr(unmatched),
    )

    # 6. The research exemption in a NESTED project: the workshop sits under
    # the product subfolder, an immediate child of the root holding its own
    # .git ([scope-lock-research-exemption-flat-path-only]). The same path
    # without the child .git is an ordinary subfolder and stays denied.
    d5 = make_project(scope_files=None)
    nested = os.path.join(d5, "product", "workshop", "resources", "research")
    os.makedirs(nested)
    research_file = os.path.join(nested, "x.md")
    check(
        "research folder under a child WITHOUT .git is denied",
        decision(drive_edit(d5, research_file)) == "deny",
        repr(drive_edit(d5, research_file)),
    )
    os.makedirs(os.path.join(d5, "product", ".git"))
    check(
        "research folder under a child holding .git is allowed",
        decision(drive_edit(d5, research_file)) == "allow",
        repr(drive_edit(d5, research_file)),
    )
    sibling = os.path.join(d5, "product", "workshop", "resources", "notes.md")
    check(
        "a non-research path under the same child is still denied",
        decision(drive_edit(d5, sibling)) == "deny",
        repr(drive_edit(d5, sibling)),
    )

    if _failures:
        print(f"\n{len(_failures)} FAILURE(S)")
        return 1
    print("\nall passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
