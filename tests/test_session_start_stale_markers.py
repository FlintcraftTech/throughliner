#!/usr/bin/env python3
"""session_start.py names a close-active marker another session left, and
ignores this session's own ([scratchpad-refused-after-resume-close-marker]).

Run: py tests/test_session_start_stale_markers.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)
"""

import importlib.util
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
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "session_start.py")
_spec = importlib.util.spec_from_file_location("session_start", HOOK)
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)

failures = []


def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


print("test_session_start_stale_markers")
d = tempfile.mkdtemp(prefix="stale-markers-")
folder = os.path.join(d, ".throughliner")
os.makedirs(folder)
for name in ("close-active-other-session", "close-active-this-session", "stop-claim-x.marker"):
    with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
        f.write("")
stale = hook._stale_close_markers(d, "this-session")
check("another session's marker is named, this session's and other files are not",
      stale == ["close-active-other-session"], repr(stale))
check("no folder reads as nothing", hook._stale_close_markers(os.path.join(d, "nope"), "x") == [])
check("the markers are still there — nothing deleted",
      sorted(os.listdir(folder)) == ["close-active-other-session", "close-active-this-session", "stop-claim-x.marker"])

# The opening logs the version it ran as, in the decision log's own shape.
hook._log_session_opened(d, "this-session", "1.24.0-test1")
with open(os.path.join(folder, "pre-tool-use.log"), encoding="utf-8") as f:
    line = f.read().strip()
cols = line.split("\t")
check("the opened-version line has the log's six columns",
      len(cols) == 6 and cols[1] == "SessionStart" and cols[3] == "session opened"
      and cols[4] == "version 1.24.0-test1" and cols[5] == "this-session", line)
shutil.rmtree(d, ignore_errors=True)

print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)
