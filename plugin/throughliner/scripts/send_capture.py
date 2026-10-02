#!/usr/bin/env python3
"""Send one capture to a correspondent project's queue without ever printing
the correspondent's path.

Usage:
    python send_capture.py <project root> --to <correspondent name>
                           --heading <text> --slug <slug> --body <body file>
                           [--attach <path>]... [--send-tracked]

Why this exists ([cross-project-captures-replace-mail-send]): a session sends
anything to another project — work, a reply, copy on offer — by adding a
capture to the bottom of that project's Unprocessed section, on the user's
yes to the exact text. No message file is written into a mailbox. The address
book that supplies the path is write-and-send only: a session may pass a
recorded path to a send and never quote it, so this script takes a NAME, does
the checks, appends through reorder_queue.py's own append path, and prints
one line naming the correspondent and the slug — never the path.

Refuses, with a status line and a non-zero exit, where the name is not in the
address book, the recipient's folder or its QUEUE.md is missing, the QUEUE.md
has no Unprocessed section, the slug is already an entry there, an attachment
resolves outside this project, a file of the attachment's name already sits
in the recipient's temp/, or the recipient's QUEUE.md is tracked in a
repository that has a remote (the go is given by re-running with
--send-tracked on the user's say-so). Every check runs before any write.

Known limit: two sessions can write one queue at once. The queue tool
re-reads the file before writing, which narrows that and does not close it.

Standard library only. UTF-8 reconfiguration copied from reorder_queue.py.
"""

import contextlib
import datetime
import importlib.util
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

# Status lines can carry non-ASCII characters; a console that cannot render
# them must degrade, never crash.
for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ADDRESS_BOOK = os.path.join("INBOX", ".address-book.md")
ROW_RE = re.compile(r'^\|\s*(?P<name>[^|]+?)\s*\|\s*`?(?P<path>[^|`]+?)`?\s*\|\s*$')
# The second shape the book may be written in ([address-book-format-unstated]):
# a bullet — a hyphen, the name, an em dash (or an en dash, or a spaced
# hyphen), the path, with or without backticks.
BULLET_RE = re.compile(r'^-\s+(?P<name>.+?)\s+(?:—|–|-)\s+`?(?P<path>[^`]+?)`?\s*$')
SLUG_SHAPE = re.compile(r'^[a-z0-9][a-z0-9-]*$')
SHAPES = ("a table row:  | <name> | <path> |\n"
          "  or a bullet:  - <name> — <path>")
USAGE = ("usage: send_capture.py <project root> --to <correspondent name> "
         "--heading <text> --slug <slug> --body <body file> "
         "[--attach <path>]... [--send-tracked]")


class Refused(Exception):
    """A send refused before anything was written."""


def fail(msg):
    sys.stderr.write("send_capture: " + msg + "\n")
    sys.exit(1)


def read_address_book(root):
    """Correspondent name (lower-cased) to (name, folder path)."""
    path = os.path.join(root, ADDRESS_BOOK)
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        raise Refused("no address book at INBOX/.address-book.md in this "
                      "project.")
    book = {}
    content = 0
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        content += 1
        m = ROW_RE.match(stripped) or BULLET_RE.match(stripped)
        if not m:
            continue
        name, folder = m.group("name").strip(), m.group("path").strip()
        if name.lower() in ("correspondent", "---") or set(name) <= set("-"):
            continue
        book[name.lower()] = (name, folder)
    if content and not book:
        # A non-empty book that parses to nothing is a shape fault, not a
        # missing correspondent: the missing-name message's obvious remedy
        # is a second unreadable entry.
        raise Refused("the address book's shape could not be read — none of "
                      "its lines is in a shape this script reads:\n  "
                      + SHAPES + "\nRewrite the entries in one of those "
                      "shapes; nothing here rewrites the file.")
    return book


def _mover():
    path = os.path.join(HERE, "reorder_queue.py")
    spec = importlib.util.spec_from_file_location(
        "throughliner_reorder_queue_for_send", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(folder, *args):
    try:
        return subprocess.run(
            ["git", "-C", folder, *args], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None


def queue_tracked_with_remote(folder):
    """True where the recipient's QUEUE.md is tracked in a repository that has
    a remote — the capture would then be published with that repository."""
    tracked = _git(folder, "ls-files", "--error-unmatch", "QUEUE.md")
    if tracked is None or tracked.returncode != 0:
        return False
    remote = _git(folder, "remote")
    return remote is not None and bool(remote.stdout.strip())


def _inside(root, path):
    real_root = os.path.normcase(os.path.realpath(root))
    full = os.path.normcase(os.path.realpath(path))
    return full == real_root or full.startswith(real_root + os.sep)


def send(root, to, heading, slug, body, attachments=(), send_tracked=False):
    """Run every check, then append the capture and copy the attachments.

    Returns (correspondent name, note). Raises Refused, with nothing written,
    on any failed check. `body` is the entry's prose as text.
    """
    heading = (heading or "").strip()
    slug = (slug or "").strip().strip("[]")
    body = (body or "").strip()
    if heading.endswith("[%s]" % slug):
        heading = heading[:-len("[%s]" % slug)].rstrip()
    if not heading:
        raise Refused("heading is missing.")
    if "\n" in heading or "\r" in heading:
        raise Refused("heading contains a line break — it is one line.")
    if not slug or not SLUG_SHAPE.match(slug):
        raise Refused("slug %r is missing or malformed — lowercase letters, "
                      "digits and hyphens only." % slug)
    if not body:
        raise Refused("body is missing.")
    if any(l.startswith("#### ") for l in body.splitlines()):
        raise Refused("body carries a '#### ' heading line — one capture per "
                      "send.")

    book = read_address_book(root)
    entry = book.get((to or "").strip().lower())
    if entry is None:
        raise Refused("'%s' is not a correspondent in this project's address "
                      "book. Record the folder the user supplies first; "
                      "nothing here scans for projects." % to)
    name, folder = entry
    if not os.path.isdir(folder):
        raise Refused("%s: the recorded folder does not exist on this "
                      "machine." % name)
    queue = os.path.join(folder, "QUEUE.md")
    if not os.path.isfile(queue):
        raise Refused("%s: that project has no QUEUE.md, so there is no "
                      "queue to add a capture to." % name)

    mover = _mover()
    with open(queue, 'r', encoding='utf-8', newline='') as f:
        queue_lines = f.read().splitlines(keepends=True)
    if 'Unprocessed' not in mover.parse(queue_lines):
        raise Refused("%s: that project's QUEUE.md has no Unprocessed "
                      "section." % name)
    taken = (mover.section_slugs(queue_lines, 'Processed')
             | mover.section_slugs(queue_lines, 'Unprocessed'))
    if slug in taken:
        raise Refused("%s: slug '%s' is already an entry in that project's "
                      "queue — pick another." % (name, slug))

    temp_dir = os.path.join(folder, "temp")
    sources = []
    seen = set()
    for rel in attachments or ():
        src = rel if os.path.isabs(rel) else os.path.join(root, rel)
        if not _inside(root, src):
            raise Refused("attachment %s resolves outside this project."
                          % rel)
        if not os.path.isfile(src):
            raise Refused("attachment %s does not exist." % rel)
        base = os.path.basename(src)
        if base.lower() in seen:
            raise Refused("two attachments are named %s." % base)
        seen.add(base.lower())
        if os.path.exists(os.path.join(temp_dir, base)):
            raise Refused("%s: a file named %s already sits in that "
                          "project's temp/ folder." % (name, base))
        sources.append((src, base))

    note = ""
    if queue_tracked_with_remote(folder):
        if not send_tracked:
            raise Refused("%s: that project's QUEUE.md is tracked in a "
                          "repository that has a remote, so the capture "
                          "would be published with it. Say so plainly and do "
                          "not send until the user says go. Re-run with "
                          "--send-tracked on their say-so. Nothing was sent."
                          % name)
        note = "sent into a tracked queue with a remote on the user's say-so"

    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    sender = os.path.basename(os.path.normpath(os.path.abspath(root)))
    entry_lines = ["#### %s [%s]\n" % (heading, slug),
                   body + "\n",
                   "From: %s, sent %s\n" % (sender, stamp)]
    for _, base in sources:
        entry_lines.append("Attachment: temp/%s\n" % base)

    tmp = tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.md',
                                      delete=False, newline='')
    try:
        tmp.write("".join(entry_lines))
        tmp.close()
        captured = io.StringIO()
        try:
            with contextlib.redirect_stderr(captured), \
                    contextlib.redirect_stdout(captured):
                mover.append_item(queue, 'Unprocessed', tmp.name)
        except SystemExit as exc:
            if exc.code not in (0, None):
                raise Refused("%s: the queue tool refused the capture — "
                              "nothing was written:\n%s"
                              % (name, captured.getvalue().strip()))
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass

    if sources:
        os.makedirs(temp_dir, exist_ok=True)
    for src, base in sources:
        dest = os.path.join(temp_dir, base)
        shutil.copyfile(src, dest)
        with open(src, "rb") as a, open(dest, "rb") as b:
            if a.read() != b.read():
                raise Refused("%s: attachment %s did not land byte-for-byte; "
                              "the capture is in the queue and names it."
                              % (name, base))
    return name, note


def main(argv):
    args = list(argv)
    send_tracked = "--send-tracked" in args
    if send_tracked:
        args.remove("--send-tracked")
    values = {}
    attachments = []
    for flag in ("--to", "--heading", "--slug", "--body"):
        if flag not in args:
            fail(USAGE)
        k = args.index(flag)
        try:
            values[flag] = args[k + 1]
        except IndexError:
            fail(flag + " needs a value")
        args = args[:k] + args[k + 2:]
    while "--attach" in args:
        k = args.index("--attach")
        try:
            attachments.append(args[k + 1])
        except IndexError:
            fail("--attach needs a path")
        args = args[:k] + args[k + 2:]
    if len(args) != 1:
        fail(USAGE)
    root = args[0]
    try:
        with open(values["--body"], encoding="utf-8") as f:
            body = f.read()
    except OSError:
        fail("body file not found: " + values["--body"])
    try:
        name, note = send(root, values["--to"], values["--heading"],
                          values["--slug"], body, attachments, send_tracked)
    except Refused as exc:
        fail(str(exc))
    print("%s: capture [%s] added to the bottom of Unprocessed%s%s" % (
        name, values["--slug"].strip().strip("[]"),
        ", with %d attachment(s) in temp/" % len(attachments)
        if attachments else "",
        " (" + note + ")" if note else ""))


if __name__ == "__main__":
    main(sys.argv[1:])
