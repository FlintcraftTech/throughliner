#!/usr/bin/env python3
"""Fixture suite for the retired-artifact report at a session opening.

Run: py tests/test_session_start_retired_artifacts.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

What this is guarding. A consumer project ran the format 3 to 4 migration, which
generated `BUILD-VIEW.md` at its root. The generated view was retired the
following week. Their version top-up then refreshed the managed CLAUDE.md block,
ran every scaffold and settings check, and reported nothing to do — with the
15KB orphan still sitting at the root, because a retirement removes the code that
writes an artifact and not the artifact from projects that already ran it.

**This project cannot dogfood the check**, which is unusual here and is stated
rather than glossed: its own `BUILD-VIEW.md` was never generated, so a fixture is
the only place it can be proved.

The standing property: the check REPORTS and never deletes. A case pins that the
file is still there afterwards, because deleting a file from someone's project is
exactly what the add-only posture exists to prevent.
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
LIST = os.path.join(ROOT, "plugin", "throughliner", "retired-artifacts.md")

failures = []


def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


def load():
    spec = importlib.util.spec_from_file_location("session_start", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def listed_paths():
    """The paths the shipped list actually names, read rather than assumed."""
    mod = load()
    with open(LIST, encoding="utf-8") as handle:
        parsed = mod._parse_retired_artifacts(handle.read().splitlines())
    return [path for path, _ in parsed]


def project(*present):
    d = tempfile.mkdtemp(prefix="retired-artifacts-test-")
    for name in present:
        path = os.path.join(d, name.rstrip("/").replace("/", os.sep))
        os.makedirs(os.path.dirname(path) or d, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("orphan\n")
    return d


def test_the_shipped_list_parses():
    """A list nothing can read reports nothing, silently, forever."""
    paths = listed_paths()
    check("the shipped list names at least one artifact", bool(paths), str(paths))
    check("the format example in the doc is not read as an entry",
          not any("path/relative" in p for p in paths), str(paths))


def test_a_present_orphan_is_reported_with_what_produced_it():
    mod = load()
    target = listed_paths()[0]
    d = project(target)
    found = mod.retired_artifacts_present(d)
    check("the orphan is found", len(found) == 1, str(found))
    check("the report names the path",
          found and found[0][0] == target, str(found))
    check("the report says what produced it",
          found and len(found[0][1]) > 10, str(found))
    check("nothing was deleted",
          os.path.exists(os.path.join(d, target.rstrip("/"))),
          "the file is gone, and this check must never delete")
    shutil.rmtree(d, ignore_errors=True)


def test_a_project_without_one_gets_nothing():
    """The control. A line that appears whether or not it applies is one people
    learn to read past."""
    mod = load()
    d = project()
    check("a clean project reports nothing",
          mod.retired_artifacts_present(d) == [],
          str(mod.retired_artifacts_present(d)))
    shutil.rmtree(d, ignore_errors=True)


def test_a_similarly_named_file_is_not_matched():
    mod = load()
    d = project("BUILD-VIEW-notes.md")
    check("a near-miss name is not reported",
          mod.retired_artifacts_present(d) == [],
          str(mod.retired_artifacts_present(d)))
    shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    print("session_start — retired artifacts")
    test_the_shipped_list_parses()
    test_a_present_orphan_is_reported_with_what_produced_it()
    test_a_project_without_one_gets_nothing()
    test_a_similarly_named_file_is_not_matched()
    print()
    if failures:
        print(f"{len(failures)} failure(s): " + ", ".join(failures))
        sys.exit(1)
    print("all passed")
