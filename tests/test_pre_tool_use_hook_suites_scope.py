#!/usr/bin/env python3
"""Fixture suite for the hook-suites scope rule.

Run: py tests/test_pre_tool_use_hook_suites_scope.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

What this is guarding. A run that changes a hook always meets that hook's test
suites, because the close cannot commit a hook change until they pass. Refusing
them was guarding files the method already makes part of every such change, and
it cost two mid-run interruptions in a single run — a scope-widening ask being
the one thing a run nobody is watching should not need.

The pairing is bounded on purpose, so the assertions run in both directions: a
run that lists a hook may write the suites, and a run that lists no hook still
may not. Without the second, this would be an unbounded widening wearing a
narrow rule's description.
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
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "pre_tool_use.py")

failures = []


def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


def load():
    spec = importlib.util.spec_from_file_location("pre_tool_use", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


HOOK_FILES = ["plugin/throughliner/hooks/pre_tool_use.py"]
DOC_FILES = ["plugin/throughliner/docs/plan.md"]
SUITE = "workshop/resources/testing/test_pre_tool_use_shell_writes.py"
OLD_SUITE = "resources/testing/test_pre_tool_use_shell_writes.py"


def test_a_hook_run_may_write_its_suites():
    """The case the rule exists for."""
    mod = load()
    d = tempfile.mkdtemp(prefix="hook-suites-scope-")
    check("a run listing a hook may write a suite file",
          mod._is_build_file(os.path.join(d, SUITE), d, HOOK_FILES),
          "suite refused to a hook-touching run")
    check("the pre-move suite path is permitted too",
          mod._is_build_file(os.path.join(d, OLD_SUITE), d, HOOK_FILES),
          "pre-move path refused")
    shutil.rmtree(d, ignore_errors=True)


def test_a_hook_run_may_write_the_inner_tests_folder():
    """The suites live at tests/ since the repository cleanup
    ([hooks-name-old-workshop-paths])."""
    mod = load()
    d = tempfile.mkdtemp(prefix="hook-suites-scope-")
    check("a run listing a hook may write tests/test_x.py",
          mod._is_build_file(os.path.join(d, "tests", "test_x.py"), d, HOOK_FILES),
          "tests/ refused to a hook-touching run")
    check("a run listing no hook is still refused tests/test_x.py",
          not mod._is_build_file(os.path.join(d, "tests", "test_x.py"), d, DOC_FILES),
          "tests/ permitted to a run touching no hook")
    shutil.rmtree(d, ignore_errors=True)


def test_a_run_with_no_hook_may_not():
    """The bound. Without this the rule is a general widening."""
    mod = load()
    d = tempfile.mkdtemp(prefix="hook-suites-scope-")
    check("a run listing no hook is still refused a suite file",
          not mod._is_build_file(os.path.join(d, SUITE), d, DOC_FILES),
          "suite permitted to a run that touches no hook")
    shutil.rmtree(d, ignore_errors=True)


def test_the_pairing_does_not_widen_beyond_the_testing_folder():
    """A hook-touching run gets its suites, not the run of the repository."""
    mod = load()
    d = tempfile.mkdtemp(prefix="hook-suites-scope-")
    for outside in ("README.md",
                    "workshop/resources/research/some-finding.md",
                    "plugin/throughliner/docs/next.md"):
        check(f"a hook-touching run is still refused {outside}",
              not mod._is_build_file(os.path.join(d, outside), d, HOOK_FILES),
              "permitted outside the testing folder")
    shutil.rmtree(d, ignore_errors=True)


def test_listed_files_still_pass_normally():
    """The ordinary path is untouched."""
    mod = load()
    d = tempfile.mkdtemp(prefix="hook-suites-scope-")
    check("a file named in the list is permitted",
          mod._is_build_file(os.path.join(d, DOC_FILES[0]), d, DOC_FILES),
          "listed file refused")
    shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    print("test_pre_tool_use_hook_suites_scope")
    test_a_hook_run_may_write_its_suites()
    test_a_hook_run_may_write_the_inner_tests_folder()
    test_a_run_with_no_hook_may_not()
    test_the_pairing_does_not_widen_beyond_the_testing_folder()
    test_listed_files_still_pass_normally()
    print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
    sys.exit(1 if failures else 0)
