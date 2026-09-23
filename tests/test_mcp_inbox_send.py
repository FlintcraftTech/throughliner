#!/usr/bin/env python3
"""Regression tests for mcp/server.py's inbox_send tool.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_mcp_inbox_send.py

No test framework, matching the suites alongside it.

Why this exists ([mcp-inbox-send-tool]): an outbound INBOX send was the one
kind of write with no server tool — the message was glued together by a
script, which the safety check refuses, and the register line written apart
from the copy. The tool composes the message from named files, runs the send
script's checks, places the file and appends the register line in one call.
This suite pins the composed body, the register line's fields, each refusal
with nothing written on either side, and both say-so flags — driven end to
end over raw UTF-8 bytes, like the register suite.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER = os.path.join(ROOT, "plugin", "throughliner", "mcp", "server.py")

failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        failures.append(name)


def fixture(recipient_inbox=True, recipient_ignore=True, book=True):
    """A sender and a recipient side by side under one temp folder."""
    top = tempfile.mkdtemp(prefix="mcp-inbox-send-")
    sender = os.path.join(top, "sender")
    recipient = os.path.join(top, "Recipient Project")
    os.makedirs(os.path.join(sender, "INBOX"))
    os.makedirs(recipient)
    with open(os.path.join(sender, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    if book:
        with open(os.path.join(sender, "INBOX", ".address-book.md"), "w",
                  encoding="utf-8") as f:
            f.write("# Address book\n\n- Recipient — `%s`\n" % recipient)
    if recipient_inbox:
        os.makedirs(os.path.join(recipient, "INBOX"))
    if recipient_ignore:
        with open(os.path.join(recipient, ".gitignore"), "w",
                  encoding="utf-8") as f:
            f.write("INBOX/\n")
    with open(os.path.join(sender, "part-one.md"), "w", encoding="utf-8",
              newline="") as f:
        f.write("# Part one — “curly” and a résumé\nline two\n")
    with open(os.path.join(sender, "part-two.md"), "w", encoding="utf-8",
              newline="") as f:
        f.write("part two, no trailing newline")
    return top, sender, recipient


def call(cwd, arguments):
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": "inbox_send", "arguments": arguments}},
    ]
    payload = "".join(json.dumps(r, ensure_ascii=False) + "\n"
                      for r in requests).encode("utf-8")
    env = dict(os.environ)
    env["THROUGHLINER_PROJECT_ROOT"] = cwd
    proc = subprocess.run([sys.executable, SERVER], input=payload, cwd=cwd,
                          capture_output=True, env=env, timeout=60)
    if proc.returncode != 0:
        raise AssertionError(
            f"server exited {proc.returncode}\n"
            f"stdout: {proc.stdout!r}\nstderr: {proc.stderr!r}")
    for line in proc.stdout.decode("utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("id") == 2:
            return r.get("result", {}).get("content", [{}])[0].get("text", "")
    return ""


def register(sender):
    path = os.path.join(sender, "INBOX", "sent.md")
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as f:
        return f.read().decode("utf-8")


GOOD = {
    "to": "recipient",
    "filename": "2026-09-23-a-message.md",
    "header": "# A subject\nFrom the sender, running Throughliner 1.23.0.\nReturn path: here",
    "files": ["part-one.md", "part-two.md"],
    "intent": "for completion",
    "claim": "that the tool composes and sends in one call",
}

# 1. The happy path: composition, delivery, register line.
top, sender, recipient = fixture()
try:
    answer = call(sender, GOOD)
except Exception as exc:  # noqa: BLE001
    print(f"  FAIL the server runs and answers\n       {exc}")
    failures.append("the server runs and answers")
    answer = ""
dest = os.path.join(recipient, "INBOX", GOOD["filename"])
check("the tool reports the message delivered by name",
      answer.startswith("Recipient: 2026-09-23-a-message.md delivered"),
      f"tool answered: {answer!r}")
check("the answer never carries the recipient's path",
      recipient not in answer, f"tool answered: {answer!r}")
body = open(dest, "rb").read().decode("utf-8") if os.path.isfile(dest) else None
expected = (GOOD["header"] + "\n\n"
            + "# Part one — “curly” and a résumé\nline two\n"
            + "\n\n" + "part two, no trailing newline\n")
check("the message is the header, a blank line, then each file verbatim",
      body == expected, f"body: {body!r}")
text = register(sender) or ""
last = text.splitlines()[-1] if text else ""
check("the register line is appended with the clock stamp",
      re.match(r"^- \d{4}-\d{2}-\d{2} \d{2}:\d{2} — INBOX mail to Recipient — for completion — ", last) is not None,
      f"last line: {last!r}")
check("the pointer defaults to the message file's name",
      last.endswith(" — " + GOOD["filename"]), f"last line: {last!r}")
check("the register line names the correspondent, never the path",
      recipient not in text, f"register: {text!r}")
shutil.rmtree(top, ignore_errors=True)

# 2. An explicit pointer is kept.
top, sender, recipient = fixture()
call(sender, dict(GOOD, pointer="temp/draft.txt"))
last = (register(sender) or "").splitlines()[-1]
check("an explicit pointer is written as given",
      last.endswith(" — temp/draft.txt"), f"last line: {last!r}")
shutil.rmtree(top, ignore_errors=True)


def nothing_written(sender, recipient):
    inbox = os.path.join(recipient, "INBOX")
    delivered = os.path.isdir(inbox) and any(
        n.endswith(".md") for n in os.listdir(inbox))
    return register(sender) is None and not delivered


# 3. Each refusal writes nothing on either side.
for label, tweak, needle in [
    ("a name not in the address book is refused",
     dict(GOOD, to="nobody"), "not a correspondent"),
    ("a missing register field is refused",
     {k: v for k, v in GOOD.items() if k != "claim"}, "claim is missing"),
    ("an intent outside the two is refused",
     dict(GOOD, intent="for reference"), "intent must be exactly"),
    ("a line break inside a register field is refused",
     dict(GOOD, claim="two\nlines"), "line break"),
    ("a named file that does not exist is refused",
     dict(GOOD, files=["missing.md"]), "does not exist"),
    ("a named file outside the project is refused",
     dict(GOOD, files=["../outside.md"]), "outside the project"),
    ("a filename that is a path is refused",
     dict(GOOD, filename="sub/x.md"), "bare name"),
]:
    top, sender, recipient = fixture()
    answer = call(sender, tweak)
    check(label, answer.startswith("Refused") and needle in answer,
          f"tool answered: {answer!r}")
    check(label + " — and nothing was written",
          nothing_written(sender, recipient),
          f"register: {register(sender)!r}")
    shutil.rmtree(top, ignore_errors=True)

# 4. A same-named message already in the mailbox.
top, sender, recipient = fixture()
with open(os.path.join(recipient, "INBOX", GOOD["filename"]), "w",
          encoding="utf-8") as f:
    f.write("old\n")
answer = call(sender, GOOD)
check("a same-named message in the mailbox is refused",
      answer.startswith("Refused") and "already in the mailbox" in answer,
      f"tool answered: {answer!r}")
check("the existing message is untouched and no register line was written",
      open(os.path.join(recipient, "INBOX", GOOD["filename"]),
           encoding="utf-8").read() == "old\n" and register(sender) is None)
shutil.rmtree(top, ignore_errors=True)

# 5. No mailbox: refused without the flag, created with it.
top, sender, recipient = fixture(recipient_inbox=False)
answer = call(sender, GOOD)
check("a recipient with no INBOX/ is refused without create_mailbox",
      answer.startswith("Refused") and "create_mailbox" in answer
      and not os.path.isdir(os.path.join(recipient, "INBOX")),
      f"tool answered: {answer!r}")
answer = call(sender, dict(GOOD, create_mailbox=True))
check("with create_mailbox the mailbox is created and the message delivered",
      "delivered" in answer and "mailbox created" in answer
      and os.path.isfile(os.path.join(recipient, "INBOX", GOOD["filename"])),
      f"tool answered: {answer!r}")
shutil.rmtree(top, ignore_errors=True)

# 6. Uncovered mailbox: refused without the flag, sent with it.
top, sender, recipient = fixture(recipient_ignore=False)
answer = call(sender, GOOD)
check("an uncovered mailbox is refused without send_uncovered",
      answer.startswith("Refused") and "send_uncovered" in answer
      and nothing_written(sender, recipient),
      f"tool answered: {answer!r}")
answer = call(sender, dict(GOOD, send_uncovered=True))
check("with send_uncovered the message is delivered and the answer says so",
      "delivered" in answer and "uncovered" in answer
      and os.path.isfile(os.path.join(recipient, "INBOX", GOOD["filename"])),
      f"tool answered: {answer!r}")
shutil.rmtree(top, ignore_errors=True)

# 7. No address book at all.
top, sender, recipient = fixture(book=False)
answer = call(sender, GOOD)
check("a missing address book is refused",
      answer.startswith("Refused") and "address book" in answer
      and nothing_written(sender, recipient),
      f"tool answered: {answer!r}")
shutil.rmtree(top, ignore_errors=True)

# 8. tools/list advertises it.
top, sender, recipient = fixture()
requests = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
]
payload = "".join(json.dumps(r) + "\n" for r in requests).encode("utf-8")
env = dict(os.environ)
env["THROUGHLINER_PROJECT_ROOT"] = sender
proc = subprocess.run([sys.executable, SERVER], input=payload, cwd=sender,
                      capture_output=True, env=env, timeout=60)
names = []
for line in proc.stdout.decode("utf-8").splitlines():
    if line.strip() and json.loads(line).get("id") == 2:
        names = [t["name"] for t in json.loads(line)["result"]["tools"]]
check("tools/list advertises inbox_send", "inbox_send" in names, repr(names))
shutil.rmtree(top, ignore_errors=True)

print()
if failures:
    print(f"{len(failures)} failure(s):")
    for name in failures:
        print(f"  {name}")
    sys.exit(1)
print("all cases passed")
