#!/usr/bin/env python3
"""The project's temp/ folder is writable in every session.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_pre_tool_use_temp_folder.py

Why this exists ([rezip-drafts-need-a-permitted-path-in-a-build]): the
co-authoring rule sends every draft to `temp/`, and inside a build the safety
check refused the Write tool on `temp/<draft>.txt` because the path was not on
the run's Files list, while a shell `cp` into the same folder passed. The
folder is gitignored and disposable by definition — the scratchpad's ground —
so it is permitted to a build, a planning session and a session with neither.

A second case pins the folder-line diagnosis
([files-list-folder-line-covers-nothing]): a Files list carrying `tests` and a
write to `tests/x.py` is refused with a message naming the folder line and the
file to add.

A third pins the planning list's `research/` at the project root
([hooks-name-old-workshop-paths]).
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "pre_tool_use.py")
SESSION = "temp-folder-test-session"

_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        _failures.append(name)


def make_project(build_files=None):
    d = tempfile.mkdtemp(prefix="temp-folder-test-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    os.makedirs(os.path.join(d, "temp"))
    if build_files is not None:
        with open(os.path.join(d, f"_build-{SESSION}.md"), "w",
                  encoding="utf-8") as f:
            f.write("# Active Build\n\nFiles:\n"
                    + "".join("- " + p + "\n" for p in build_files)
                    + "\nProgress:\n")
    return d


def drive_write(cwd, filepath):
    payload = {"cwd": cwd, "tool_name": "Write",
               "tool_input": {"file_path": filepath, "content": "draft"},
               "session_id": SESSION}
    proc = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                          capture_output=True, text=True, encoding="utf-8")
    if not proc.stdout.strip():
        return {}
    return json.loads(proc.stdout)["hookSpecificOutput"]


def decision(result):
    return result.get("permissionDecision", "allow")


def main():
    print("test_pre_tool_use_temp_folder")

    # A build whose Files list does not name temp/ writes a draft there.
    d = make_project(build_files=["plugin/throughliner/docs/plan.md"])
    r = drive_write(d, os.path.join(d, "temp", "draft.txt"))
    check("a build not listing temp/ may write temp/draft.txt",
          decision(r) == "allow", repr(r))
    r = drive_write(d, os.path.join(d, "README.md"))
    check("the same build is still refused an unlisted file elsewhere",
          decision(r) == "deny", repr(r))

    # A folder line covers nothing beneath it, and the refusal says so.
    d2 = make_project(build_files=["plugin/throughliner/hooks/stop.py", "tests"])
    os.makedirs(os.path.join(d2, "tests"))
    r = drive_write(d2, os.path.join(d2, "docs", "x.md"))
    reason = r.get("permissionDecisionReason", "")
    check("a write outside every listed folder is refused as before",
          decision(r) == "deny" and "not in the list at all" in reason, reason)
    d3 = make_project(build_files=["plugin/throughliner/docs/plan.md", "src"])
    r = drive_write(d3, os.path.join(d3, "src", "x.py"))
    reason = r.get("permissionDecisionReason", "")
    check("a write under a listed folder is refused",
          decision(r) == "deny", repr(r))
    check("the refusal names the folder line and the file to add",
          "folder line covers no file" in reason and "src/x.py" in reason,
          reason)

    # [spec-rework-files-line-checked]: a build whose Files list lacks SPEC.md
    # editing SPEC.md is refused with the SPEC diagnosis; another unlisted
    # file keeps the existing one.
    d5 = make_project(build_files=["plugin/throughliner/docs/plan.md"])
    r = drive_write(d5, os.path.join(d5, "SPEC.md"))
    reason = r.get("permissionDecisionReason", "")
    check("a build not listing SPEC.md is refused SPEC.md with the SPEC diagnosis",
          decision(r) == "deny"
          and "a sentence in the item's prose about SPEC is not that line" in reason,
          reason)
    r = drive_write(d5, os.path.join(d5, "docs", "other.md"))
    check("another unlisted file keeps the existing diagnosis",
          decision(r) == "deny"
          and "not in the list at all" in r.get("permissionDecisionReason", ""),
          repr(r))
    shutil.rmtree(d5, ignore_errors=True)

    # [user-material-permanent-home-at-planning]: a planning session may write
    # supplied material under workshop/resources/supplied/, and nothing else
    # new under workshop/resources/.
    d6 = make_project()
    r = drive_write(d6, os.path.join(d6, "workshop", "resources", "supplied", "notes.md"))
    check("a planning session may write workshop/resources/supplied/notes.md",
          decision(r) == "allow", repr(r))
    r = drive_write(d6, os.path.join(d6, "workshop", "resources", "other", "notes.md"))
    check("a planning session is refused workshop/resources/other/ as before",
          decision(r) == "deny", repr(r))
    shutil.rmtree(d6, ignore_errors=True)

    # A planning session writes temp/ and research/ at the project root.
    d4 = make_project()
    r = drive_write(d4, os.path.join(d4, "temp", "draft.txt"))
    check("a planning session may write temp/draft.txt",
          decision(r) == "allow", repr(r))
    r = drive_write(d4, os.path.join(d4, "research", "x.md"))
    check("a planning session may write research/x.md at the project root",
          decision(r) == "allow", repr(r))
    r = drive_write(d4, os.path.join(d4, "notes", "x.md"))
    check("a planning session is still refused elsewhere",
          decision(r) == "deny", repr(r))

    for d_ in (d, d2, d3, d4):
        shutil.rmtree(d_, ignore_errors=True)

    if _failures:
        print(f"\n{len(_failures)} FAILURE(S)")
        return 1
    print("\nall passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
