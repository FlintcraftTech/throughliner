#!/usr/bin/env python3
"""pre_tool_use.py reads /close's close marker from the project's own
`.throughliner/` folder, per session ([scratchpad-refused-after-resume-close-marker]).

Run: py tests/test_pre_tool_use_close_marker.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

Two assertions: with `close-active-<this session>` standing, an Edit to
README.md — a close-obligation file — is allowed in a build session; with only
another session's marker standing, the same Edit is refused.
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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "pre_tool_use.py")
SESSION = "close-marker-suite"

failures = []


def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


def project():
    d = tempfile.mkdtemp(prefix="close-marker-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    with open(os.path.join(d, "README.md"), "w", encoding="utf-8") as f:
        f.write("# README\n")
    with open(os.path.join(d, f"_build-{SESSION}.md"), "w", encoding="utf-8") as f:
        f.write("# Active Build\n\nFiles:\n- src/listed.py\n\nProgress:\n")
    os.makedirs(os.path.join(d, ".throughliner"))
    return d


def decision(cwd, filepath):
    payload = {"cwd": cwd, "tool_name": "Edit",
               "tool_input": {"file_path": filepath, "old_string": "a", "new_string": "b"},
               "session_id": SESSION}
    proc = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                          capture_output=True, text=True, encoding="utf-8",
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    if not proc.stdout.strip():
        return "allow"
    return json.loads(proc.stdout).get("hookSpecificOutput", {}).get("permissionDecision", "allow")


print("test_pre_tool_use_close_marker")
d = project()
readme = os.path.join(d, "README.md")
check("no marker: README.md is refused in a build", decision(d, readme) == "deny")
with open(os.path.join(d, ".throughliner", "close-active-other-session"), "w", encoding="utf-8") as f:
    f.write("")
check("another session's marker unlocks nothing", decision(d, readme) == "deny")
with open(os.path.join(d, ".throughliner", f"close-active-{SESSION}"), "w", encoding="utf-8") as f:
    f.write("")
check("this session's marker in .throughliner/ unlocks the close file",
      decision(d, readme) == "allow")
check("an unlisted ordinary file stays refused under the marker",
      decision(d, os.path.join(d, "src", "other.py")) == "deny")
shutil.rmtree(d, ignore_errors=True)

# The three development-project paths the close's obligations write — the
# nested README, the retired-terms register and setup's 3b table — are permitted
# while this session's marker stands and refused without it, exactly as
# README.md is ([retired-terms-append-refused-at-build-close]).
NESTED_CLOSE_FILES = (
    os.path.join("throughliner", "README.md"),
    os.path.join("method", "retired-terms.md"),
    os.path.join("throughliner", "plugin", "throughliner", "docs", "setup.md"),
)
d = project()
for rel in NESTED_CLOSE_FILES:
    os.makedirs(os.path.dirname(os.path.join(d, rel)), exist_ok=True)
    with open(os.path.join(d, rel), "w", encoding="utf-8") as f:
        f.write("x\n")
    check(f"no marker: {rel} is refused in a build",
          decision(d, os.path.join(d, rel)) == "deny")
with open(os.path.join(d, ".throughliner", f"close-active-{SESSION}"), "w", encoding="utf-8") as f:
    f.write("")
for rel in NESTED_CLOSE_FILES:
    check(f"this session's marker unlocks {rel}",
          decision(d, os.path.join(d, rel)) == "allow")
check("a sibling doc under the marker stays refused",
      decision(d, os.path.join(d, "throughliner", "plugin", "throughliner",
                               "docs", "plan.md")) == "deny")
shutil.rmtree(d, ignore_errors=True)

# The two markers /close writes are permitted for the session's own id and
# refused for another's, in a build session and a planning session alike
# ([close-markers-refused-by-safety-check]).
def marker_path(cwd, prefix, sid):
    return os.path.join(cwd, ".throughliner", f"{prefix}-{sid}")


for label, make in (("build", project), ("planning", None)):
    d = project()
    if make is None:
        os.remove(os.path.join(d, f"_build-{SESSION}.md"))
    for prefix in ("close-active", "session-closed"):
        check(f"{label} session: own {prefix} marker is allowed",
              decision(d, marker_path(d, prefix, SESSION)) == "allow")
        check(f"{label} session: another session's {prefix} marker is refused",
              decision(d, marker_path(d, prefix, "other-session")) == "deny")
    shutil.rmtree(d, ignore_errors=True)

print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)
