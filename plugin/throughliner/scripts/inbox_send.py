#!/usr/bin/env python3
"""Send one message file to a correspondent project's INBOX/ without ever
printing the correspondent's path.

Usage:
    python inbox_send.py <project root> --to <correspondent name> --file <message path>
                          [--create-mailbox] [--send-uncovered]

Why this exists ([inbox-send-script]): the outbound send is three checks and a
copy — the recipient has a mailbox, that mailbox is gitignored there, and the
file goes in byte-for-byte — and the address book that supplies the path is
write-and-send only: a session may pass a recorded path to a send and never
quote it, name a correspondent in a document, or carry either into chat. With
the steps done by hand, fragments of the address book reached a tool result.
This script takes a NAME and a FILE, does the checks, copies, and prints one
line naming the correspondent and the filename — never the path.

Refuses, with a status line and a non-zero exit, where the name is not in the
address book, the recipient's folder is missing, the recipient has no INBOX/
(naming that one would have to be created — the user's call, performed only
with --create-mailbox), the recipient's .gitignore does not cover INBOX/ (the
go the doc promises is given by re-running with --send-uncovered on the user's
say-so), or a file of the same name already sits in the recipient's mailbox.

Standard library only. UTF-8 reconfiguration copied from reorder_queue.py.
"""

import os
import re
import shutil
import sys

# Status lines can carry non-ASCII characters; a console that cannot render
# them must degrade, never crash.
for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

ADDRESS_BOOK = os.path.join("INBOX", ".address-book.md")
ROW_RE = re.compile(r'^\|\s*(?P<name>[^|]+?)\s*\|\s*`?(?P<path>[^|`]+?)`?\s*\|\s*$')
IGNORE_RE = re.compile(r'^/?INBOX(/|/\*\*|)$')


def fail(msg):
    sys.stderr.write("inbox_send: " + msg + "\n")
    sys.exit(1)


def read_address_book(root):
    """Correspondent name (lower-cased) to folder path."""
    path = os.path.join(root, ADDRESS_BOOK)
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        fail("no address book at INBOX/.address-book.md in this project.")
    book = {}
    for line in lines:
        m = ROW_RE.match(line)
        if not m:
            continue
        name, folder = m.group("name").strip(), m.group("path").strip()
        if name.lower() in ("correspondent", "---") or set(name) <= set("-"):
            continue
        book[name.lower()] = (name, folder)
    return book


def gitignore_covers_inbox(recipient):
    path = os.path.join(recipient, ".gitignore")
    try:
        with open(path, encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if line and not line.startswith("#") and IGNORE_RE.match(line):
                    return True
    except OSError:
        return False
    return False


def main(argv):
    args = list(argv)
    create = "--create-mailbox" in args
    if create:
        args.remove("--create-mailbox")
    send_uncovered = "--send-uncovered" in args
    if send_uncovered:
        args.remove("--send-uncovered")
    to = fname = None
    for flag in ("--to", "--file"):
        if flag not in args:
            fail("usage: inbox_send.py <project root> --to <correspondent name> "
                 "--file <message path> [--create-mailbox] [--send-uncovered]")
        k = args.index(flag)
        try:
            val = args[k + 1]
        except IndexError:
            fail(flag + " needs a value")
        args = args[:k] + args[k + 2:]
        if flag == "--to":
            to = val
        else:
            fname = val
    if len(args) != 1:
        fail("usage: inbox_send.py <project root> --to <correspondent name> "
             "--file <message path> [--create-mailbox] [--send-uncovered]")
    root = args[0]

    if not os.path.isfile(fname):
        fail("message file not found: " + fname)
    book = read_address_book(root)
    entry = book.get(to.strip().lower())
    if entry is None:
        fail("'%s' is not a correspondent in this project's address book. "
             "Record the folder the user supplies first; nothing here scans "
             "for projects." % to)
    name, folder = entry
    if not os.path.isdir(folder):
        fail("%s: the recorded folder does not exist on this machine." % name)
    mailbox = os.path.join(folder, "INBOX")
    if not os.path.isdir(mailbox):
        if not create:
            fail("%s has no INBOX/ folder; one would have to be created, which "
                 "is the user's call. Re-run with --create-mailbox on their "
                 "say-so. Nothing was sent." % name)
        os.makedirs(mailbox)
        sys.stderr.write("inbox_send: %s: created INBOX/ on the user's "
                         "say-so.\n" % name)
    if not gitignore_covers_inbox(folder):
        if not send_uncovered:
            fail("%s: that project's .gitignore does not cover INBOX/, so a "
                 "message would be committed there. Say so plainly and do "
                 "not send until the user says go, which is the user's call. "
                 "Re-run with --send-uncovered on their say-so. Nothing was "
                 "sent." % name)
        sys.stderr.write("inbox_send: %s: sent to an uncovered mailbox on "
                         "the user's say-so.\n" % name)
    dest = os.path.join(mailbox, os.path.basename(fname))
    if os.path.exists(dest):
        fail("%s: a message named %s is already in the mailbox. Nothing was "
             "sent." % (name, os.path.basename(fname)))
    shutil.copyfile(fname, dest)
    with open(fname, "rb") as a, open(dest, "rb") as b:
        if a.read() != b.read():
            os.remove(dest)
            fail("%s: the copy did not land byte-for-byte; removed." % name)
    print("%s: %s delivered" % (name, os.path.basename(fname)))


if __name__ == "__main__":
    main(sys.argv[1:])
