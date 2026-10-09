#!/usr/bin/env python3
"""Regression tests for mcp/server.py's send_capture tool.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_mcp_send_capture.py

No test framework, matching the suites alongside it.

Why this exists ([cross-project-captures-replace-mail-send]): a session sends
anything to another project by adding a capture to that project's queue, and
the tool does it in one call — the send script's checks, the append through
the queue tool, the attachments into the recipient's temp/, and the register
line. This suite pins the entry as it lands, the register line's fields, each
refusal with nothing written on either side, and the say-so flag — driven end
to end over raw UTF-8 bytes, like the register suite.
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

QUEUE = ("# QUEUE\n\n## Processed\n\n"
         "--- Cleared to run above this line ---\n\n"
         "## Unprocessed\n\n"
         "#### Waiting capture [waiting-capture]\nprose\n")


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        failures.append(name)


def fixture(book=True, queue=QUEUE):
    """A sender and a recipient side by side under one temp folder."""
    top = tempfile.mkdtemp(prefix="mcp-send-capture-")
    sender = os.path.join(top, "sender")
    recipient = os.path.join(top, "Recipient Project")
    os.makedirs(os.path.join(sender, ".throughliner"))
    os.makedirs(recipient)
    with open(os.path.join(sender, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    if book:
        with open(os.path.join(sender, ".throughliner", "address-book.md"), "w",
                  encoding="utf-8") as f:
            f.write("# Address book\n\n- Recipient — `%s`\n" % recipient)
    if queue is not None:
        with open(os.path.join(recipient, "QUEUE.md"), "w", encoding="utf-8",
                  newline="") as f:
            f.write(queue)
    with open(os.path.join(sender, "notes.txt"), "wb") as f:
        f.write("attached — résumé\n".encode("utf-8"))
    return top, sender, recipient


def rpc(cwd, method, params):
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": method, "params": params},
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
        if line.strip() and json.loads(line).get("id") == 2:
            return json.loads(line).get("result", {})
    return {}


def call(cwd, arguments):
    result = rpc(cwd, "tools/call",
                 {"name": "send_capture", "arguments": arguments})
    return result.get("content", [{}])[0].get("text", "")


def register(sender):
    path = os.path.join(sender, ".throughliner", "sent.md")
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as f:
        return f.read().decode("utf-8")


def queue_text(recipient):
    path = os.path.join(recipient, "QUEUE.md")
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as f:
        return f.read().decode("utf-8")


GOOD = {
    "to": "recipient",
    "heading": "Sent capture heading",
    "slug": "sent-capture",
    "body": "The capture's prose — “curly” and a résumé.\nSecond line.",
    "intent": "for completion",
    "claim": "that the tool adds a capture and registers it in one call",
}

# 1. The happy path: the entry, the register line.
top, sender, recipient = fixture()
try:
    answer = call(sender, GOOD)
except Exception as exc:  # noqa: BLE001
    print(f"  FAIL the server runs and answers\n       {exc}")
    failures.append("the server runs and answers")
    answer = ""
text = queue_text(recipient) or ""
check("the tool reports the capture added by name and slug",
      answer.startswith("Recipient: capture [sent-capture] added"),
      f"tool answered: {answer!r}")
check("the answer never carries the recipient's path",
      recipient not in answer, f"tool answered: {answer!r}")
check("the entry lands after the waiting capture, at the bottom",
      text.rfind("#### Sent capture heading [sent-capture]")
      > text.rfind("[waiting-capture]"), text)
check("the entry carries the body verbatim and the From line",
      GOOD["body"] + "\n" in text and "\nFrom: sender, sent 20" in text, text)
last = (register(sender) or "").splitlines()[-1:] or [""]
last = last[0]
check("the register line is appended with the clock stamp",
      re.match(r"^- \d{4}-\d{2}-\d{2} \d{2}:\d{2} — capture to Recipient — "
               r"for completion — ", last) is not None, f"last line: {last!r}")
check("the pointer defaults to the slug in the recipient's queue",
      last.endswith(" — [sent-capture] in that project's queue"),
      f"last line: {last!r}")
check("the register names the correspondent, never the path",
      recipient not in (register(sender) or ""), repr(register(sender)))
shutil.rmtree(top, ignore_errors=True)

# 2. An attachment and an explicit pointer.
top, sender, recipient = fixture()
answer = call(sender, dict(GOOD, attachments=["notes.txt"],
                           pointer="temp/draft.txt"))
dest = os.path.join(recipient, "temp", "notes.txt")
check("an attachment is copied into the recipient's temp/ byte for byte",
      os.path.isfile(dest) and open(dest, "rb").read()
      == open(os.path.join(sender, "notes.txt"), "rb").read(),
      f"tool answered: {answer!r}")
check("the entry names the attachment",
      "\nAttachment: temp/notes.txt\n" in (queue_text(recipient) or ""))
check("an explicit pointer is written as given",
      (register(sender) or "").splitlines()[-1].endswith(" — temp/draft.txt"))
shutil.rmtree(top, ignore_errors=True)

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
    ("a slug already in the recipient's queue is refused",
     dict(GOOD, slug="waiting-capture"), "already an entry"),
    ("an attachment that does not exist is refused",
     dict(GOOD, attachments=["missing.txt"]), "does not exist"),
    ("an attachment outside the project is refused",
     dict(GOOD, attachments=["../outside.txt"]), "outside this project"),
]:
    top, sender, recipient = fixture()
    with open(os.path.join(top, "outside.txt"), "w", encoding="utf-8") as f:
        f.write("x\n")
    answer = call(sender, tweak)
    check(label, answer.startswith("Refused") and needle in answer,
          f"tool answered: {answer!r}")
    check(label + " — and nothing was written",
          register(sender) is None and queue_text(recipient) == QUEUE
          and not os.path.isdir(os.path.join(recipient, "temp")),
          f"register: {register(sender)!r}")
    shutil.rmtree(top, ignore_errors=True)

# 4. No queue, and no address book.
top, sender, recipient = fixture(queue=None)
answer = call(sender, GOOD)
check("a recipient with no QUEUE.md is refused",
      answer.startswith("Refused") and "no QUEUE.md" in answer
      and register(sender) is None, f"tool answered: {answer!r}")
shutil.rmtree(top, ignore_errors=True)

top, sender, recipient = fixture(book=False)
answer = call(sender, GOOD)
check("a missing address book is refused, naming the book's path and the row shape",
      answer.startswith("Refused") and "address book" in answer
      and ".throughliner/address-book.md" in answer
      and "| <name> | <path> |" in answer and "- <name> — <path>" in answer
      and register(sender) is None and queue_text(recipient) == QUEUE,
      f"tool answered: {answer!r}")
shutil.rmtree(top, ignore_errors=True)

# 5. A tracked queue with a remote: refused without the flag, sent with it.
top, sender, recipient = fixture()
for args in (["init"], ["add", "QUEUE.md"],
             ["-c", "user.name=t", "-c", "user.email=t@example.invalid",
              "commit", "-m", "queue"],
             ["remote", "add", "origin", "https://example.invalid/r.git"]):
    subprocess.run(["git", "-C", recipient, *args], capture_output=True,
                   text=True, timeout=30)
answer = call(sender, GOOD)
check("a tracked queue with a remote is refused without send_tracked",
      answer.startswith("Refused") and "send_tracked" in answer
      and register(sender) is None and queue_text(recipient) == QUEUE,
      f"tool answered: {answer!r}")
answer = call(sender, dict(GOOD, send_tracked=True))
check("with send_tracked the capture is added and the answer says so",
      "added" in answer and "say-so" in answer
      and "[sent-capture]" in (queue_text(recipient) or ""),
      f"tool answered: {answer!r}")
shutil.rmtree(top, ignore_errors=True)

# 6. tools/list advertises it, and not the retired mail tool.
top, sender, recipient = fixture()
names = [t["name"] for t in rpc(sender, "tools/list", {}).get("tools", [])]
check("tools/list advertises send_capture", "send_capture" in names,
      repr(names))
check("tools/list no longer advertises the mail tool",
      "inbox" + "_send" not in names, repr(names))
shutil.rmtree(top, ignore_errors=True)

print()
if failures:
    print(f"{len(failures)} failure(s):")
    for name in failures:
        print(f"  {name}")
    sys.exit(1)
print("all cases passed")
