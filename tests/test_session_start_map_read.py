#!/usr/bin/env python3
"""Regression test for the project map ([project-map-for-claude]).

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_session_start_map_read.py

Two halves: the session opening names MAP.md as the first read where the
file exists at the root and says nothing where it does not, without ever
flagging its absence as a missing scaffold; and the package ships the
template setup writes it from, carrying the criterion in its preamble.
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
PLUGIN = os.path.join(ROOT, "plugin", "throughliner")
HOOK = os.path.join(PLUGIN, "hooks", "session_start.py")
_spec = importlib.util.spec_from_file_location("session_start", HOOK)
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)

failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        failures.append(name)


print("test_session_start_map_read")
d = tempfile.mkdtemp(prefix="map-read-")
with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
    f.write("# SPEC\n")
check("no MAP.md: no pointer line", hook._map_pointer(d) == "", repr(hook._map_pointer(d)))
with open(os.path.join(d, "MAP.md"), "w", encoding="utf-8") as f:
    f.write("# MAP\n\n- docs/ — the documents\n")
line = hook._map_pointer(d)
check("MAP.md present: the opening names it as the first read",
      "MAP.md" in line and "read it first" in line, repr(line))
shutil.rmtree(d, ignore_errors=True)

template = os.path.join(PLUGIN, "templates", "MAP-TEMPLATE.md")
check("the package ships MAP-TEMPLATE.md", os.path.isfile(template), template)
if os.path.isfile(template):
    with open(template, encoding="utf-8") as f:
        text = f.read()
    check("the template's preamble says it is for Claude to read",
          "for Claude to read" in text, text[:200])
    check("the template's preamble states the criterion — human-used files, sets, no machinery",
          "Machinery earns no line" in text and "the set gets one line" in text, text[:600])
    check("the template shows the three line shapes",
          "<path>/ —" in text and "<path> —" in text and "(N files)" in text, text)

if failures:
    print("\n%d FAILURE(S)" % len(failures))
    sys.exit(1)
print("\nall passed")
