#!/usr/bin/env python3
"""Regression tests for scripts/send_capture.py.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_send_capture.py

No test framework, matching the suites alongside it.

Why this exists ([cross-project-captures-replace-mail-send]): a session sends
anything to another project by adding a capture to the bottom of that
project's Unprocessed section. The first case is the fact the design rested
on and had not exercised: the queue tool's append path accepts a queue
outside the project it is run from. The rest pin each refusal with nothing
written, a clean send, an attachment landing in the recipient's temp/, and
the path never being printed.
"""

import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "plugin", "throughliner", "scripts")
SCRIPT = os.path.join(SCRIPTS, "send_capture.py")
MOVER = os.path.join(SCRIPTS, "reorder_queue.py")

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

failures = []

QUEUE = ("# QUEUE\n\n## Processed\n\n"
         "#### Existing work [existing-work]\nprose\n\n"
         "--- Cleared to run above this line ---\n\n"
         "## Unprocessed\n\n"
         "#### Waiting capture [waiting-capture]\nprose\n")


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        failures.append(name)


def fixture(queue=QUEUE, book=True):
    """A sender and a recipient side by side under one temp folder."""
    top = tempfile.mkdtemp(prefix="send-capture-")
    sender = os.path.join(top, "Sender Project")
    recipient = os.path.join(top, "Recipient Project")
    os.makedirs(os.path.join(sender, "INBOX"))
    os.makedirs(recipient)
    if book:
        with open(os.path.join(sender, "INBOX", ".address-book.md"), "w",
                  encoding="utf-8") as f:
            f.write("# Address book\n\n- Recipient — `%s`\n" % recipient)
    if queue is not None:
        with open(os.path.join(recipient, "QUEUE.md"), "w", encoding="utf-8",
                  newline="") as f:
            f.write(queue)
    with open(os.path.join(sender, "body.md"), "w", encoding="utf-8") as f:
        f.write("A capture's prose — with “curly” quotes.\nSecond line.\n")
    with open(os.path.join(sender, "notes.txt"), "wb") as f:
        f.write("attached bytes — résumé\r\n".encode("utf-8"))
    return top, sender, recipient


def run(sender, *extra, to="recipient", slug="sent-capture",
        heading="Sent capture heading"):
    return subprocess.run(
        [sys.executable, SCRIPT, sender, "--to", to, "--heading", heading,
         "--slug", slug, "--body", os.path.join(sender, "body.md"), *extra],
        capture_output=True, text=True, encoding="utf-8", timeout=60)


def queue_text(recipient):
    with open(os.path.join(recipient, "QUEUE.md"), encoding="utf-8",
              newline="") as f:
        return f.read()


# 1. The fact the design rested on: the queue tool appends to a queue outside
#    the folder it is run from.
top, sender, recipient = fixture()
with open(os.path.join(sender, "entry.md"), "w", encoding="utf-8") as f:
    f.write("#### Outside append [outside-append]\nprose\n")
proc = subprocess.run(
    [sys.executable, MOVER, os.path.join(recipient, "QUEUE.md"),
     "--append", "Unprocessed", "--body", os.path.join(sender, "entry.md")],
    cwd=sender, capture_output=True, text=True, encoding="utf-8", timeout=60)
check("the queue tool appends to a queue outside the folder it runs from",
      proc.returncode == 0 and "[outside-append]" in queue_text(recipient),
      proc.stderr)
shutil.rmtree(top, ignore_errors=True)

# 2. A clean send.
top, sender, recipient = fixture()
proc = run(sender)
text = queue_text(recipient)
check("a clean send exits zero", proc.returncode == 0, proc.stderr)
check("the answer names the correspondent and the slug",
      "Recipient: capture [sent-capture]" in proc.stdout, proc.stdout)
check("the answer never carries the recipient's path",
      recipient not in proc.stdout + proc.stderr, proc.stdout + proc.stderr)
check("the entry is the last block of Unprocessed",
      text.rfind("#### Sent capture heading [sent-capture]")
      > text.rfind("[waiting-capture]") > text.find("## Unprocessed"), text)
check("the entry carries the body and the From line",
      "“curly” quotes.\nSecond line.\n" in text
      and "\nFrom: Sender Project, sent 20" in text, text)
check("existing entries are untouched",
      "#### Existing work [existing-work]\nprose\n" in text
      and "#### Waiting capture [waiting-capture]\nprose\n" in text, text)
shutil.rmtree(top, ignore_errors=True)

# 3. An attachment lands in the recipient's temp/, byte for byte.
top, sender, recipient = fixture()
proc = run(sender, "--attach", "notes.txt")
dest = os.path.join(recipient, "temp", "notes.txt")
check("a send with an attachment exits zero", proc.returncode == 0,
      proc.stderr)
check("the attachment is copied into the recipient's temp/ byte for byte",
      os.path.isfile(dest) and open(dest, "rb").read()
      == open(os.path.join(sender, "notes.txt"), "rb").read())
check("the entry names the attachment",
      "\nAttachment: temp/notes.txt\n" in queue_text(recipient),
      queue_text(recipient))
shutil.rmtree(top, ignore_errors=True)


def refused(label, needle, proc, recipient, before):
    check(label, proc.returncode != 0 and needle in proc.stderr, proc.stderr)
    after = (queue_text(recipient)
             if os.path.isfile(os.path.join(recipient, "QUEUE.md")) else None)
    check(label + " — and nothing was written",
          after == before and not os.path.isdir(
              os.path.join(recipient, "temp")), repr(after))


# 4. Each refusal writes nothing.
top, sender, recipient = fixture()
refused("a name not in the address book is refused", "not a correspondent",
        run(sender, to="nobody"), recipient, QUEUE)
refused("a slug already in the recipient's queue is refused",
        "already an entry", run(sender, slug="waiting-capture"), recipient,
        QUEUE)
refused("a malformed slug is refused", "malformed",
        run(sender, slug="Not A Slug"), recipient, QUEUE)
outside = os.path.join(top, "outside.txt")
with open(outside, "w", encoding="utf-8") as f:
    f.write("x\n")
refused("an attachment outside this project is refused",
        "outside this project", run(sender, "--attach", outside), recipient,
        QUEUE)
refused("an attachment that does not exist is refused", "does not exist",
        run(sender, "--attach", "missing.txt"), recipient, QUEUE)
shutil.rmtree(top, ignore_errors=True)

top, sender, recipient = fixture(queue=None)
refused("a recipient with no QUEUE.md is refused", "no QUEUE.md",
        run(sender), recipient, None)
shutil.rmtree(top, ignore_errors=True)

top, sender, recipient = fixture(queue="# QUEUE\n\n## Processed\n\n")
refused("a queue with no Unprocessed section is refused",
        "no Unprocessed section", run(sender), recipient,
        "# QUEUE\n\n## Processed\n\n")
shutil.rmtree(top, ignore_errors=True)

top, sender, recipient = fixture(book=False)
refused("a missing address book is refused", "address book", run(sender),
        recipient, QUEUE)
shutil.rmtree(top, ignore_errors=True)

top, sender, recipient = fixture()
os.makedirs(os.path.join(recipient, "temp"))
with open(os.path.join(recipient, "temp", "notes.txt"), "w",
          encoding="utf-8") as f:
    f.write("old\n")
proc = run(sender, "--attach", "notes.txt")
check("a same-named file in the recipient's temp/ is refused",
      proc.returncode != 0 and "already sits" in proc.stderr
      and queue_text(recipient) == QUEUE
      and open(os.path.join(recipient, "temp", "notes.txt"),
               encoding="utf-8").read() == "old\n", proc.stderr)
shutil.rmtree(top, ignore_errors=True)

# 5. A tracked queue in a repository with a remote: refused without the
#    flag, sent with it.
top, sender, recipient = fixture()


def git(*args):
    subprocess.run(["git", "-C", recipient, *args], capture_output=True,
                   text=True, timeout=30)


git("init")
git("add", "QUEUE.md")
git("-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit",
    "-m", "queue")
proc = run(sender)
check("a tracked queue with no remote is sent without the flag",
      proc.returncode == 0, proc.stderr)
git("remote", "add", "origin", "https://example.invalid/repo.git")
before = queue_text(recipient)
proc = run(sender, slug="second-capture")
check("a tracked queue with a remote is refused without --send-tracked",
      proc.returncode != 0 and "--send-tracked" in proc.stderr
      and queue_text(recipient) == before, proc.stderr)
proc = run(sender, "--send-tracked", slug="second-capture")
check("with --send-tracked the capture is added and the answer says so",
      proc.returncode == 0 and "say-so" in proc.stdout
      and "[second-capture]" in queue_text(recipient), proc.stderr)
shutil.rmtree(top, ignore_errors=True)

print()
if failures:
    print(f"{len(failures)} failure(s):")
    for name in failures:
        print(f"  {name}")
    sys.exit(1)
print("all cases passed")
