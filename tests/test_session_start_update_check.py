#!/usr/bin/env python3
"""Regression test for session_start.py's weekly update check.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_session_start_update_check.py

Why this exists ([weekly-update-check-on-users-channel]): once a week, where
the GitHub CLI is installed and signed in, the opening reads the newest
version on the user's channel and says in one line where a newer one exists.
The `gh` calls are injected so the suite never reaches the network.

Cases: the weekly gate (marker fresh, stale, absent); the compare on each
channel; silence without the CLI or without a sign-in.
"""

import datetime
import importlib.util
import json
import os
import sys
import tempfile

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "session_start.py")
_spec = importlib.util.spec_from_file_location("session_start", HOOK)
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)

_failures = []
NOW = datetime.datetime(2026, 9, 14, 12, 0)


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        _failures.append(name)


def project(channel=None):
    d = tempfile.mkdtemp(prefix="update-check-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    if channel:
        with open(os.path.join(d, "TOOLS.md"), "w", encoding="utf-8") as f:
            f.write("# TOOLS\n\n- Throughliner channel: %s\n" % channel)
    return d


class Runner:
    """A fake `gh`: records the calls and answers from a script."""

    def __init__(self, release="v1.23.0", beta="1.24.0-test2", auth_rc=0):
        self.calls = []
        self.release = release
        self.beta = beta
        self.auth_rc = auth_rc

    def __call__(self, args):
        self.calls.append(list(args))
        if args[:2] == ["auth", "status"]:
            return self.auth_rc, ""
        if args[0] == "release":
            return 0, json.dumps([{"tagName": self.release}])
        if args[0] == "api":
            return 0, json.dumps({"name": "throughliner", "version": self.beta})
        return 1, ""


def gh_present(name):
    return "/usr/bin/gh"


def gh_absent(name):
    return None


def main():
    print("weekly update check:")

    # Marker absent: the check runs, and a newer stable release is named.
    d = project()
    r = Runner()
    line = hook.update_check(d, "1.22.0", now=NOW, run=r, which=gh_present)
    check("marker absent: gh is asked", any(c[0] == "release" for c in r.calls), str(r.calls))
    check("stable channel by default: the release list is read, not the beta branch",
          not any(c[0] == "api" for c in r.calls))
    check("a newer release is named in one line",
          "1.23.0" in line and "stable" in line, line)
    marker = os.path.join(d, hook.UPDATE_CHECK_MARKER)
    check("the marker is written", os.path.isfile(marker))

    # Marker fresh: nothing is asked.
    r2 = Runner()
    line = hook.update_check(d, "1.22.0", now=NOW + datetime.timedelta(days=2), run=r2, which=gh_present)
    check("marker fresh (two days old): gh is not asked", r2.calls == [], str(r2.calls))
    check("marker fresh: silence", line == "")

    # Marker stale: asked again.
    r3 = Runner()
    line = hook.update_check(d, "1.22.0", now=NOW + datetime.timedelta(days=8), run=r3, which=gh_present)
    check("marker stale (eight days): gh is asked again", any(c[0] == "release" for c in r3.calls))

    # Installed is already the newest: silence, marker still written.
    d2 = project()
    line = hook.update_check(d2, "1.23.0", now=NOW, run=Runner(), which=gh_present)
    check("installed equals newest: silence", line == "", line)
    check("marker written even when nothing is newer",
          os.path.isfile(os.path.join(d2, hook.UPDATE_CHECK_MARKER)))

    # Beta channel: the beta branch's manifest is read and compared.
    d3 = project(channel="beta")
    r4 = Runner(beta="1.24.0-test2")
    line = hook.update_check(d3, "1.22.0-test6", now=NOW, run=r4, which=gh_present)
    check("beta channel: the beta manifest is read", any(c[0] == "api" for c in r4.calls), str(r4.calls))
    check("beta channel: a newer test build is named", "1.24.0-test2" in line and "beta" in line, line)
    d4 = project(channel="beta")
    line = hook.update_check(d4, "1.24.0-test2", now=NOW, run=Runner(beta="1.24.0-test2"), which=gh_present)
    check("beta channel: same build installed, silence", line == "", line)
    d5 = project(channel="beta")
    line = hook.update_check(d5, "1.24.0", now=NOW, run=Runner(beta="1.24.0-test2"), which=gh_present)
    check("a bare version outranks a test build of the same number", line == "", line)

    # A version string that is not a version is named as unreadable, never
    # printed ([sweep-security-hook-output-carries-machine-and-remote-strings]).
    d7 = project()
    line = hook.update_check(d7, "1.22.0", now=NOW,
                             run=Runner(release="<b>not a version</b>"),
                             which=gh_present)
    check("a non-version string is not printed", "not a version" not in line, line)
    check("the opening says the string was unreadable", "unreadable" in line, line)

    # No CLI, or not signed in: silence, nothing asked beyond the sign-in check.
    d6 = project()
    r5 = Runner()
    line = hook.update_check(d6, "1.0.0", now=NOW, run=r5, which=gh_absent)
    check("gh absent: silence and nothing asked", line == "" and r5.calls == [], str(r5.calls))
    r6 = Runner(auth_rc=1)
    line = hook.update_check(d6, "1.0.0", now=NOW, run=r6, which=gh_present)
    check("gh not signed in: silence", line == "" and not any(c[0] == "release" for c in r6.calls))
    check("gh not signed in: no marker written",
          not os.path.isfile(os.path.join(d6, hook.UPDATE_CHECK_MARKER)))

    if _failures:
        print(f"\n{len(_failures)} FAILURE(S)")
        return 1
    print("\nall passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
