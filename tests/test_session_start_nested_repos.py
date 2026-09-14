#!/usr/bin/env python3
"""The nested two-repository shape draws no hazard from the session opening.

Run: py tests/test_session_start_nested_repos.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

What this pins, and what the build behind it found. The nesting item scoped a
change to session_start's "second-repository detection", and reading the hook
showed there is none to change: the second-repository rule is conversational
(skill-nonspecific-rules.md) and the only repository-shaped reports here are
the untracked-documents lines and the isolation cases. So the deliverable is
the assertion that the shape the method now scaffolds is NOT reported as a
fault: an outer repository tracking the method documents produces no
untracked-documents report, with or without an inner product repository
sitting in a subfolder.
"""

import importlib.util
import os
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

failures = []


def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label
          + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


def load_hook():
    spec = importlib.util.spec_from_file_location("session_start", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                   timeout=30)


def make_nested(td):
    """An outer repo tracking the method docs, an inner product repo."""
    git(td, "init")
    for name in ("SPEC.md", "QUEUE.md"):
        with open(os.path.join(td, name), "w", encoding="utf-8") as f:
            f.write(f"# {name}\n")
    os.makedirs(os.path.join(td, "LOG"))
    with open(os.path.join(td, "LOG", "index.md"), "w", encoding="utf-8") as f:
        f.write("# Index\n")
    inner = os.path.join(td, "product")
    os.makedirs(inner)
    git(inner, "init")
    with open(os.path.join(inner, "app.py"), "w", encoding="utf-8") as f:
        f.write("print('app')\n")
    return inner


def test_nested_shape_reports_no_untracked_docs():
    mod = load_hook()
    with tempfile.TemporaryDirectory() as td:
        make_nested(td)
        ignored = mod._untracked_core_docs(td)
        check("tracked docs in the outer repo report nothing untracked",
              ignored == [], f"got: {ignored}")


def test_nested_shape_with_an_ignored_doc_still_reports_it():
    """The report keys on what git ignores, not on the repository count —
    a nested project that also gitignores a document is still told what
    follows, exactly as a flat one is."""
    mod = load_hook()
    with tempfile.TemporaryDirectory() as td:
        make_nested(td)
        with open(os.path.join(td, ".gitignore"), "w", encoding="utf-8") as f:
            f.write("QUEUE.md\n")
        ignored = mod._untracked_core_docs(td)
        check("an ignored doc is still reported in a nested project",
              ignored == ["QUEUE.md"], f"got: {ignored}")


if __name__ == "__main__":
    print("test_session_start_nested_repos")
    test_nested_shape_reports_no_untracked_docs()
    test_nested_shape_with_an_ignored_doc_still_reports_it()
    print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
    sys.exit(1 if failures else 0)
