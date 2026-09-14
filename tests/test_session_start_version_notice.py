#!/usr/bin/env python3
"""Fixture suite pinning that a plugin version change, on its own, says nothing.

Run: py tests/test_session_start_version_notice.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

What this guards. `session_start.py` used to compare the project's recorded
plugin version against the installed one and, on any difference, print a line
telling the user /setup wanted a session of its own. Only /setup writes
`.throughliner-version`, so the line did not fire once per update — it fired at
every session opening until /setup ran, and nothing about a version change
requires /setup at all. The version bumps at every release and most releases
change no format and scaffold no file.

The assertions therefore come in a matched pair, and both halves matter equally:
a version-only difference produces no notice and no /setup recommendation, AND
the two signals that genuinely mean /setup is outstanding — a stale format epoch,
and a missing scaffolded document — still fire. A repeal that also silenced the
real checks would be the worse defect, so it is pinned here rather than trusted.

The hook is run as a subprocess because what needs pinning is what reaches the
user, which is the assembled payload rather than any one computed value.
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
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "session_start.py")
PLUGIN_ROOT = os.path.join(ROOT, "plugin", "throughliner")

MARKER = "--- Cleared to run above this line ---"

failures = []


def check(label, ok, detail=""):
    print(("  ok   " if ok else "  FAIL ") + label
          + ("" if ok else "\n       " + detail))
    if not ok:
        failures.append(label)


def current_epoch():
    """Read FORMAT_EPOCH from the hook rather than hardcoding it.

    A suite carrying its own copy of the number goes stale the first time a
    build bumps the epoch, and it goes stale silently.
    """
    with open(HOOK, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("FORMAT_EPOCH = "):
                return int(line.split("=", 1)[1].strip())
    raise AssertionError("FORMAT_EPOCH not found in session_start.py")


EPOCH = current_epoch()


def project(recorded_version="0.0.1", epoch=None, drop=()):
    """A fully scaffolded, adopted project. `drop` removes named scaffolding."""
    d = tempfile.mkdtemp(prefix="version-notice-test-")
    files = {
        "SPEC.md": "# SPEC\n",
        "QUEUE.md": ("# QUEUE\n\n## Processed\n\n" + MARKER
                     + "\n\n## Unprocessed\n"),
        ".throughliner-version": recorded_version + "\n",
        ".throughliner-format-epoch": str(EPOCH if epoch is None else epoch) + "\n",
    }
    for name, body in files.items():
        if name in drop:
            continue
        with open(os.path.join(d, name), "w", encoding="utf-8") as f:
            f.write(body)
    for folder, index in (("LOG", "index.md"), ("FAQ", "index.md")):
        if folder in drop:
            continue
        os.makedirs(os.path.join(d, folder), exist_ok=True)
        with open(os.path.join(d, folder, index), "w", encoding="utf-8") as f:
            f.write("# index\n")
    return d


def without_style_offer(out):
    """The output minus the brevity-style offer sentence.

    That sentence legitimately names /setup ("The brevity output style is not
    enabled for this project. /setup offers it.") and fires in any project
    without the style setting — these fixtures included. This suite guards
    VERSION-driven /setup recommendations, so the style sentence is removed
    before the no-/setup assertions rather than counted against them.
    """
    return out.replace(
        "The brevity output style is not enabled for this project. "
        "/setup offers it.", "")


def run(cwd):
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=PLUGIN_ROOT)
    payload = json.dumps({"cwd": cwd, "session_id": "version-notice-test"})
    proc = subprocess.run(
        [sys.executable, HOOK], input=payload, cwd=cwd, env=env,
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    return proc.stdout or ""


def test_version_only_difference_says_nothing():
    """The whole point. Everything present, epoch current, version behind."""
    d = project(recorded_version="0.0.1")
    out = run(d)
    check("a version-only difference emits no version-change notice",
          "version changed since this project was" not in out,
          out[:800])
    check("a version-only difference recommends no /setup",
          "/setup" not in without_style_offer(out), out[:800])
    shutil.rmtree(d, ignore_errors=True)


def test_matching_version_also_says_nothing():
    """The control, so a pass above cannot come from the hook printing nothing
    at all for reasons unrelated to the version."""
    d = project()
    out = run(d)
    check("a project opening at all produces output",
          "[Throughliner]" in out, out[:400])
    check("a matching-version project recommends no /setup",
          "/setup" not in without_style_offer(out), out[:800])
    shutil.rmtree(d, ignore_errors=True)


def test_stale_epoch_still_halts():
    """The signal that genuinely means /setup is outstanding."""
    d = project(epoch=EPOCH - 1)
    out = run(d)
    check("a stale format epoch still halts the session",
          "STOP" in out and "/setup" in out, out[:1200])
    shutil.rmtree(d, ignore_errors=True)


def test_missing_document_still_reports():
    """The other genuine signal: presence-based drift."""
    d = project(drop=("FAQ",))
    out = run(d)
    check("a missing scaffolded document is still reported",
          "/setup" in out, out[:1200])
    shutil.rmtree(d, ignore_errors=True)


def test_flag_is_gone_from_the_source():
    """The item's own acceptance test, kept where it runs with the rest."""
    with open(HOOK, "r", encoding="utf-8") as f:
        source = f.read()
    check("version_mismatch appears nowhere in session_start.py",
          "version_mismatch" not in source)


if __name__ == "__main__":
    print("test_session_start_version_notice")
    test_version_only_difference_says_nothing()
    test_matching_version_also_says_nothing()
    test_stale_epoch_still_halts()
    test_missing_document_still_reports()
    test_flag_is_gone_from_the_source()
    print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
    sys.exit(1 if failures else 0)
