#!/usr/bin/env python3
"""pre_tool_use.py says once, on its first decision in a session, that the
plugin under the session changed — the version the opening logged against the
version it runs as ([scratchpad-refused-after-resume-close-marker]).

Run: py tests/test_pre_tool_use_version_change.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

The fixture plugin root carries a manifest reading 1.23.0; the decision log's
opened line says 1.22.0-test6. The notice rides the hook's JSON as a
systemMessage — beside a decision where one is printed, alone otherwise —
and fires once.
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
SESSION = "version-change-suite"

failures = []


def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


def project(opened_version):
    d = tempfile.mkdtemp(prefix="version-change-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8") as f:
        f.write("# QUEUE\n\n## Processed\n\n## Unprocessed\n")
    os.makedirs(os.path.join(d, ".throughliner"))
    with open(os.path.join(d, ".throughliner", "pre-tool-use.log"), "w",
              encoding="utf-8", newline="") as f:
        f.write("2026-09-17 10:00:00\tSessionStart\tallow\tsession opened\t"
                "version %s\t%s\n" % (opened_version, SESSION))
    plugin = os.path.join(d, "plugin-root")
    os.makedirs(os.path.join(plugin, ".claude-plugin"))
    with open(os.path.join(plugin, ".claude-plugin", "plugin.json"), "w",
              encoding="utf-8") as f:
        json.dump({"name": "throughliner", "version": "1.23.0"}, f)
    return d, plugin


def drive(cwd, plugin, filepath):
    payload = {"cwd": cwd, "tool_name": "Edit",
               "tool_input": {"file_path": filepath, "old_string": "a", "new_string": "b"},
               "session_id": SESSION}
    proc = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                          capture_output=True, text=True, encoding="utf-8",
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1",
                               "CLAUDE_PLUGIN_ROOT": plugin})
    if not proc.stdout.strip():
        return {}
    return json.loads(proc.stdout)


print("test_pre_tool_use_version_change")
d, plugin = project("1.22.0-test6")
queue = os.path.join(d, "QUEUE.md")
out = drive(d, plugin, queue)
check("a differing version prints the notice once, beside an allowed write",
      "systemMessage" in out and "opened on 1.22.0-test6" in out["systemMessage"]
      and "running 1.23.0" in out["systemMessage"], repr(out))
out = drive(d, plugin, queue)
check("the second decision carries no notice", "systemMessage" not in out, repr(out))
shutil.rmtree(d, ignore_errors=True)

d, plugin = project("1.23.0")
out = drive(d, plugin, os.path.join(d, "QUEUE.md"))
check("the same version prints nothing", "systemMessage" not in out, repr(out))
out = drive(d, plugin, os.path.join(d, "src", "app.py"))
check("a denied write still carries its decision", out.get("hookSpecificOutput", {})
      .get("permissionDecision") == "deny", repr(out))
shutil.rmtree(d, ignore_errors=True)

print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)
