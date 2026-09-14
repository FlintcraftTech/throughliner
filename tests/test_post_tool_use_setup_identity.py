#!/usr/bin/env python3
"""Regression test for post_tool_use.py's setup identity advisory.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_post_tool_use_setup_identity.py

Why this exists ([setup-infers-identity-and-close-scrubs-the-owner]): /setup
wrote the user's first name and a wrong pronoun into SPEC.md with nothing in
the interview supplying either. After a Write or Edit to SPEC.md or CLAUDE.md
while the setup marker stands in the session scratchpad, the lint compares
the written text against the git user.name and the account name and prints
one advisory line asking whether the interview supplied it.

Two assertions: a setup-marked write of SPEC.md containing the configured git
name produces the advisory; the same write without the marker produces
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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = os.path.join(ROOT, "plugin", "throughliner", "hooks")
HOOK = os.path.join(HOOKS, "post_tool_use.py")
sys.path.insert(0, HOOKS)
import post_tool_use  # noqa: E402

SESSION = "setup-identity-test-session"
GIT_NAME = "Testy McTestface"
_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("  -- " + detail if detail else ""))
        _failures.append(name)


def make_project():
    d = tempfile.mkdtemp(prefix="setup-identity-test-")
    subprocess.run(["git", "init", "-q"], cwd=d, check=True)
    subprocess.run(["git", "config", "user.name", GIT_NAME], cwd=d, check=True)
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n\nThe owner, " + GIT_NAME + ", builds this.\n")
    return d


def drive_write(cwd, filepath, session=SESSION):
    payload = {"cwd": cwd, "tool_name": "Write",
               "tool_input": {"file_path": filepath, "content": ""},
               "session_id": session}
    proc = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                          capture_output=True, text=True, encoding="utf-8")
    if not proc.stdout.strip():
        return ""
    return json.loads(proc.stdout)["hookSpecificOutput"].get("additionalContext", "")


def main():
    print("setup identity advisory:")
    scratch = os.path.join(tempfile.gettempdir(), "claude", "setup-identity-test-project",
                           SESSION, "scratchpad")
    os.makedirs(scratch, exist_ok=True)
    marker = os.path.join(scratch, post_tool_use.SETUP_MARKER_NAME)
    if os.path.exists(marker):
        os.remove(marker)

    d = make_project()
    spec = os.path.join(d, "SPEC.md")

    check("no marker: a SPEC.md carrying the git name produces nothing",
          "Setup identity" not in drive_write(d, spec))

    with open(marker, "w", encoding="utf-8") as f:
        f.write("")
    out = drive_write(d, spec)
    check("marker present: the advisory names the file and the git name",
          "Setup identity" in out and GIT_NAME in out and "SPEC.md" in out, out)
    check("the advisory is advisory — it asks, it does not block",
          "Did the interview supply it" in out, out)

    with open(spec, "w", encoding="utf-8") as f:
        f.write("# SPEC\n\nNo names here.\n")
    check("marker present, no machine name in the text: nothing",
          "Setup identity" not in drive_write(d, spec))
    os.remove(marker)

    if _failures:
        print(f"\n{len(_failures)} FAILURE(S)")
        return 1
    print("\nall passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
