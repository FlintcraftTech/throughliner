#!/usr/bin/env python3
"""Regression tests for session_start.py's mailbox scan.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_session_start_inbox_scan.py

No test framework, matching the suites alongside it: this project has no test
runner, and `python` on the author's machine resolves to an application's
bundled interpreter that has no pytest.

The hook is imported directly rather than run as a subprocess, because what
needs pinning is which filenames the scan counts as mail.
"""

import importlib.util
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "session_start.py")

_spec = importlib.util.spec_from_file_location("session_start", HOOK)
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)

_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        _failures.append(name)


def project(files):
    """A project root whose INBOX/ holds exactly `files` (name -> contents)."""
    root = tempfile.mkdtemp(prefix="inbox-scan-test-")
    inbox = os.path.join(root, "INBOX")
    os.makedirs(os.path.join(inbox, "archive"))
    for name, body in files.items():
        with open(os.path.join(inbox, name), "w", encoding="utf-8") as f:
            f.write(body)
    return root


def test_os_metadata_is_not_mail():
    """The reporting projects' state: a mailbox holding only desktop.ini.

    A folder-icon file the operating system writes counts as a waiting message,
    so a project that has never received mail opens every session being told to
    read one. Reported from a consumer project running 1.20.0-test12.
    """
    root = project({"desktop.ini": "[.ShellClassInfo]\n"})
    found = hook._waiting_inbox_messages(root)
    check(
        "a mailbox holding only OS metadata reports no waiting mail",
        found == [],
        repr(found),
    )
    shutil.rmtree(root, ignore_errors=True)


def test_os_metadata_matches_case_insensitively():
    """Windows writes `desktop.ini` and `Desktop.ini` interchangeably."""
    root = project({"Desktop.ini": "[.ShellClassInfo]\n", "Thumbs.db": "x"})
    found = hook._waiting_inbox_messages(root)
    check(
        "OS metadata is skipped whatever its capitalisation",
        found == [],
        repr(found),
    )
    shutil.rmtree(root, ignore_errors=True)


def test_sent_register_is_not_mail():
    """`sent.md` is the outbound register, and it lives in INBOX/ permanently.

    Counting it is worse than a wrong number: the directive riding the notice
    tells the session to archive each message it routes, which would file away
    the one artifact a repeal is checked against.
    """
    root = project({"sent.md": "# Sent\n\n- 2026-08-20 - somewhere - ...\n"})
    found = hook._waiting_inbox_messages(root)
    check(
        "the outbound send register is not reported as waiting mail",
        found == [],
        repr(found),
    )
    shutil.rmtree(root, ignore_errors=True)


def test_a_real_message_still_reports():
    """The exclusions must not make the scan blind."""
    root = project(
        {
            "desktop.ini": "[.ShellClassInfo]\n",
            "sent.md": "# Sent\n",
            "2026-08-21-from-somewhere.md": "A real message.\n",
        }
    )
    found = hook._waiting_inbox_messages(root)
    check(
        "a real message still reports, alongside the excluded files",
        found == ["2026-08-21-from-somewhere.md"],
        repr(found),
    )
    shutil.rmtree(root, ignore_errors=True)


def test_dotfiles_and_archive_are_still_skipped():
    """The existing exclusions are untouched."""
    root = project({".DS_Store": "x", "real.md": "A real message.\n"})
    found = hook._waiting_inbox_messages(root)
    check(
        "dotfiles and the archive directory stay skipped",
        found == ["real.md"],
        repr(found),
    )
    shutil.rmtree(root, ignore_errors=True)


def test_no_mailbox_reports_nothing():
    root = tempfile.mkdtemp(prefix="inbox-scan-test-")
    found = hook._waiting_inbox_messages(root)
    check("a project with no INBOX/ reports nothing", found == [], repr(found))
    shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    test_os_metadata_is_not_mail()
    test_os_metadata_matches_case_insensitively()
    test_sent_register_is_not_mail()
    test_a_real_message_still_reports()
    test_dotfiles_and_archive_are_still_skipped()
    test_no_mailbox_reports_nothing()
    print()
    if _failures:
        print("FAILED: " + ", ".join(_failures))
        sys.exit(1)
    print("all passed")
