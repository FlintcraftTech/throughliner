#!/usr/bin/env python3
"""Regression tests for plugin/throughliner/scripts/inbox_send.py.

Host-only dev artifact. Run as a plain script:  py resources/testing/test_inbox_send.py

Each case builds a scratch sender with an address book pointing at scratch
recipients, runs the script as a subprocess, and reads its output. The one
invariant every case asserts: the recipient's path never appears in stdout or
stderr ([inbox-send-script]).
"""

import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SCRIPT = os.path.join(ROOT, "plugin", "throughliner", "scripts", "inbox_send.py")

_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        _failures.append(name)


def fixture(mailbox=True, ignore=True):
    base = tempfile.mkdtemp(prefix="inbox-send-")
    sender = os.path.join(base, "sender")
    recipient = os.path.join(base, "recipient project")
    os.makedirs(os.path.join(sender, "INBOX"))
    os.makedirs(recipient)
    if mailbox:
        os.makedirs(os.path.join(recipient, "INBOX"))
    if ignore:
        with open(os.path.join(recipient, ".gitignore"), "w", encoding="utf-8") as f:
            f.write("# ignores\nINBOX/\n")
    with open(os.path.join(sender, "INBOX", ".address-book.md"), "w",
              encoding="utf-8") as f:
        f.write("# Address book\n\n| Correspondent | Folder |\n| --- | --- |\n"
                "| Other Project | `%s` |\n" % recipient)
    msg = os.path.join(base, "2026-09-10-hello.md")
    with open(msg, "wb") as f:
        f.write("From: sender\n\nHello — with a dash and an arrow ->\n".encode("utf-8"))
    return base, sender, recipient, msg


def run(sender, *extra):
    return subprocess.run([sys.executable, SCRIPT, sender] + list(extra),
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")


def no_path(result, recipient):
    return recipient not in result.stdout and recipient not in result.stderr


def test_delivers_byte_for_byte():
    base, sender, recipient, msg = fixture()
    r = run(sender, "--to", "other project", "--file", msg)
    dest = os.path.join(recipient, "INBOX", os.path.basename(msg))
    check("delivery succeeds", r.returncode == 0, r.stderr.strip())
    check("one line names the correspondent and the file",
          r.stdout.strip() == "Other Project: 2026-09-10-hello.md delivered",
          r.stdout.strip())
    with open(msg, "rb") as a, open(dest, "rb") as b:
        check("the delivered file is byte-identical", a.read() == b.read())
    check("the path never appears in the output", no_path(r, recipient))
    shutil.rmtree(base, ignore_errors=True)


def test_unknown_name_is_refused():
    base, sender, recipient, msg = fixture()
    r = run(sender, "--to", "Nobody", "--file", msg)
    check("an unknown name is refused", r.returncode != 0)
    check("nothing was delivered",
          not os.listdir(os.path.join(recipient, "INBOX")))
    check("the path never appears in the output", no_path(r, recipient))
    shutil.rmtree(base, ignore_errors=True)


def test_missing_mailbox_is_refused_then_created_on_the_flag():
    base, sender, recipient, msg = fixture(mailbox=False)
    r = run(sender, "--to", "Other Project", "--file", msg)
    check("a missing mailbox is refused", r.returncode != 0)
    check("the refusal says one would have to be created",
          "--create-mailbox" in r.stderr, r.stderr.strip())
    check("the path never appears in the output", no_path(r, recipient))
    r2 = run(sender, "--to", "Other Project", "--file", msg, "--create-mailbox")
    check("with the flag the mailbox is created and the file delivered",
          r2.returncode == 0 and os.path.isfile(
              os.path.join(recipient, "INBOX", os.path.basename(msg))),
          r2.stderr.strip())
    check("the creation is reported", "created INBOX/" in r2.stderr)
    check("the path never appears in the output", no_path(r2, recipient))
    shutil.rmtree(base, ignore_errors=True)


def test_uncovered_mailbox_is_refused():
    base, sender, recipient, msg = fixture(ignore=False)
    r = run(sender, "--to", "Other Project", "--file", msg)
    check("a mailbox not covered by .gitignore is refused", r.returncode != 0)
    check("nothing was delivered",
          not os.listdir(os.path.join(recipient, "INBOX")))
    check("the path never appears in the output", no_path(r, recipient))
    shutil.rmtree(base, ignore_errors=True)


if __name__ == "__main__":
    print("test_inbox_send")
    test_delivers_byte_for_byte()
    test_unknown_name_is_refused()
    test_missing_mailbox_is_refused_then_created_on_the_flag()
    test_uncovered_mailbox_is_refused()
    print()
    if _failures:
        print(f"{len(_failures)} failure(s): " + ", ".join(_failures))
        sys.exit(1)
    print("all passed")
