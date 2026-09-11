#!/usr/bin/env python3
"""Regression tests for plugin/throughliner/scripts/port_changelog.py.

Host-only dev artifact — not shipped in the plugin package.

Run:  py resources/testing/test_port_changelog.py

No test framework, matching the suites alongside it: this project has no test
runner, and `python` on the author's machine resolves to an application's
bundled interpreter that has no pytest.

The fixture is a real git repository built in a temp dir, because everything
this generator does is a question about a commit range — which commits touched
the plugin package, what a commit's diff did to FORMAT_EPOCH, whether a manifest
change was only the version. None of that can be faked with files alone.

The standing property these cases protect: a shipped change is never silently
absent from the changelog, and a host-only change is never in it.
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

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SCRIPT = os.path.join(ROOT, "plugin", "throughliner", "scripts",
                      "port_changelog.py")

_spec = importlib.util.spec_from_file_location("port_changelog", SCRIPT)
changelog = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(changelog)

_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        _failures.append(name)


def run(repo, *args):
    result = subprocess.run(["git", "-C", repo] + list(args),
                            capture_output=True, encoding="utf-8",
                            errors="replace")
    if result.returncode != 0:
        raise SystemExit("git %s failed: %s" % (" ".join(args), result.stderr))
    return result.stdout.strip()


def write(repo, relative, text):
    path = os.path.join(repo, relative.replace("/", os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def commit(repo, message):
    run(repo, "add", "-A")
    run(repo, "commit", "-q", "-m", message)
    return run(repo, "rev-parse", "HEAD")


def build_fixture(repo):
    """A repository with one shipped change, one epoch bump, one host-only
    change and one version-only manifest bump, in that order."""
    run(repo, "init", "-q")
    run(repo, "config", "user.email", "fixture@example.invalid")
    run(repo, "config", "user.name", "Fixture")

    write(repo, "plugin/throughliner/docs/next.md", "# next\n\noriginal\n")
    write(repo, "plugin/throughliner/hooks/session_start.py",
          "FORMAT_EPOCH = 4\n")
    write(repo, "plugin/throughliner/.claude-plugin/plugin.json",
          '{\n  "name": "throughliner",\n  "version": "1.0.0"\n}\n')
    write(repo, "resources/release-checklist.md", "# checklist\n\noriginal\n")
    base = commit(repo, "baseline")

    write(repo, "plugin/throughliner/docs/next.md", "# next\n\nreworded\n")
    shipped = commit(repo, "reword the run's pre-flight")

    write(repo, "plugin/throughliner/hooks/session_start.py",
          "FORMAT_EPOCH = 5\n")
    bumped = commit(repo, "bump the format epoch")

    write(repo, "resources/release-checklist.md", "# checklist\n\nreworded\n")
    host_only = commit(repo, "reword the release checklist")

    write(repo, "plugin/throughliner/.claude-plugin/plugin.json",
          '{\n  "name": "throughliner",\n  "version": "1.0.0-test1"\n}\n')
    version_only = commit(repo, "rezip stamp")

    # The records are written after the commits they describe, exactly as the
    # hash backfill does in the real project, and land in LOG/ — a host-only
    # path, so committing them adds no shipped commit of its own.
    write(repo, "LOG/2026-01-01-reworded.md",
          "# %s — The run's pre-flight is reworded\n\n"
          "The pre-flight said the run was unattended, which it is not.\n\n"
          "**Files touched:** `plugin/throughliner/docs/next.md`\n"
          % shipped[:7])
    write(repo, "LOG/2026-01-02-epoch.md",
          "# %s — The format epoch moves to 5\n\n"
          "An existing project's cleared items gain a field, so their files "
          "are structurally wrong until migrated.\n\n"
          "**Files touched:** `plugin/throughliner/hooks/session_start.py`\n\n"
          "Host-only note: the rezip checklist's own step list is untouched.\n"
          % bumped[:7])
    commit(repo, "records")

    return {"base": base, "shipped": shipped, "bumped": bumped,
            "host_only": host_only, "version_only": version_only}


def main():
    print("port_changelog")
    with tempfile.TemporaryDirectory() as repo:
        marks = build_fixture(repo)

        lines = changelog.build(repo, marks["base"], marks["bumped"])
        text = "\n".join(lines)

        check("one entry per shipped change",
              text.count("### ") == 2, text)
        check("the entry carries its record's behavioural summary",
              "The pre-flight said the run was unattended" in text, text)
        check("the entry names the shipped file it touched",
              "plugin/throughliner/docs/next.md" in text, text)
        check("the entry points at its record",
              "LOG/2026-01-01-reworded.md" in text, text)
        check("an epoch bump is flagged",
              "FORMAT EPOCH -> 5" in text, text)
        check("a record discussing host-only reasoning is marked",
              "host-only reasoning" in text, text)

        only_host = changelog.build(repo, marks["bumped"], marks["host_only"])
        check("a range touching only host-only paths prints nothing",
              only_host == [], "\n".join(only_host))

        only_version = changelog.build(repo, marks["host_only"],
                                       marks["version_only"])
        check("a version-only manifest bump is not a shipped change",
              only_version == [], "\n".join(only_version))

        # A manifest change that is NOT only the version must still report,
        # or the skip above would hide real work.
        write(repo, "plugin/throughliner/.claude-plugin/plugin.json",
              '{\n  "name": "throughliner",\n  "version": "1.0.0-test1",\n'
              '  "description": "new field"\n}\n')
        real_manifest = commit(repo, "manifest gains a field")
        reported = changelog.build(repo, marks["version_only"], real_manifest)
        check("a manifest change beyond the version still reports",
              reported != [], "nothing was reported")

        # The two roots apart ([release-ritual-commands-target-outer-repo]):
        # a nested project's git history is the inner and its records are the
        # outer's, so `--log-root` points the LOG/ reads elsewhere while every
        # git read stays on the repository.
        with tempfile.TemporaryDirectory() as outer:
            os.makedirs(os.path.join(outer, "LOG"))
            with open(os.path.join(outer, "LOG", "2026-01-01-reworded.md"),
                      "w", encoding="utf-8") as handle:
                handle.write(
                    "# %s — The run's pre-flight is reworded\n\n"
                    "Written from the outer.\n\n"
                    "**Files touched:** `plugin/throughliner/docs/next.md`\n"
                    % marks["shipped"][:7])
            with open(os.path.join(outer, "LOG", "2026-01-01-reworded-plan.md"),
                      "w", encoding="utf-8") as handle:
                handle.write(
                    "# abc1234 — plan — the pre-flight reword\n\n"
                    "Decided because the word misled.\n\n"
                    "**Work processed:** kept.\n")
            apart = "\n".join(changelog.build(repo, marks["base"],
                                              marks["shipped"], outer))
            check("--log-root finds the record in the other folder",
                  "Written from the outer" in apart, apart)
            check("--log-root finds the deciding record in the other folder",
                  "Decided because the word misled" in apart, apart)
            check("--log-root does not read the repository's own LOG/",
                  "The pre-flight said the run was unattended" not in apart,
                  apart)

        # The default is unchanged: no log root means the repository's own.
        default = "\n".join(changelog.build(repo, marks["base"],
                                            marks["shipped"]))
        check("without --log-root the repository's own records are read",
              "The pre-flight said the run was unattended" in default, default)

    print()
    if _failures:
        print("FAILED: %d" % len(_failures))
        return 1
    print("all passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
