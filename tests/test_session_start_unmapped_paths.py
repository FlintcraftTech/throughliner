#!/usr/bin/env python3
"""session_start.py lists the paths no MAP.md line covers
([close-leaves-other-sessions-scope-file]).

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_session_start_unmapped_paths.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

Three cases: a mapped tree lists nothing; an unmapped file and an unmapped
folder are listed, the method's own files and this session's working file
are not; an ignored path is not listed.
"""

import importlib.util
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
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "session_start.py")
_spec = importlib.util.spec_from_file_location("session_start", HOOK)
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)

failures = []


def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


def write(d, rel, text="x\n"):
    path = os.path.join(d, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


MAP = ("# MAP\n\nPreamble.\n\n"
       "- SPEC.md — the spec\n"
       "- research/ — findings, one `<topic>.md` per finding, with `index.md`\n"
       "- notes/plan.md — the plan a person reads\n"
       "- scripts/ — machinery\n")

print("test_session_start_unmapped_paths")

# 1. A mapped tree lists nothing.
d = tempfile.mkdtemp(prefix="unmapped-")
subprocess.run(["git", "init", "-q"], cwd=d, check=True)
write(d, "MAP.md", MAP)
write(d, "SPEC.md"); write(d, "QUEUE.md"); write(d, "CLAUDE.md")
write(d, "LOG/2026-01-01-x.md")
write(d, "research/alpha.md"); write(d, "research/index.md")
write(d, "notes/plan.md")
write(d, "scripts/run.py")
write(d, "_build-this-session.md", "# Active Build\n")
check("a mapped tree lists nothing",
      hook.unmapped_paths(d, "this-session") == [],
      repr(hook.unmapped_paths(d, "this-session")))
check("no MAP.md reads as nothing",
      hook.unmapped_paths(os.path.join(d, "research"), "x") == [])

# 2. An unmapped file and folder are listed; a human-used file under a
# mapped folder's sibling is listed by its path; machinery is not.
write(d, "stray.md")
write(d, "old-stuff/thing.pdf")
write(d, "notes/other.md")
write(d, "notes/helper.py")
write(d, "_freeform-old-session.md", "# Freeform scope\n\nFiles:\n")
found = hook.unmapped_paths(d, "this-session")
check("the stray root file, the unmapped folder, another session's scope "
      "file and the unmapped file below a mapped sibling are listed",
      set(found) == {"stray.md", "old-stuff", "notes/other.md",
                     "_freeform-old-session.md"}, repr(found))

# 3. An ignored path is not listed.
write(d, ".gitignore", "stray.md\nold-stuff/\n")
found = hook.unmapped_paths(d, "this-session")
check("ignored paths drop off the list",
      set(found) == {"notes/other.md", "_freeform-old-session.md"},
      repr(found))

shutil.rmtree(d, ignore_errors=True)

if failures:
    print(f"\n{len(failures)} FAILED")
    sys.exit(1)
print("\nall passed")
