#!/usr/bin/env python3
"""Regression tests for mcp/server.py's append_sent_line tool.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_mcp_append_sent_line.py

No test framework, matching the suites alongside it.

Why this exists ([sent-register-has-no-append-path]): the outbound register
`INBOX/sent.md` is append-only, has no git history, and had no append path —
every session wrote a new line with an edit anchored on whatever it last read,
and one line landed a row above the end. The tool is the safe path: it
composes the line, stamps the clock, and appends at the end. This suite pins
the composition, each refusal, the create-when-absent and refuse-when-no-mailbox
arms, and transport fidelity for non-ASCII text — driven end to end over raw
UTF-8 bytes, like the capture suite.
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


def project(with_inbox=True, register_text=None):
    d = tempfile.mkdtemp(prefix="mcp-append-sent-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    if with_inbox:
        os.makedirs(os.path.join(d, "INBOX"))
        if register_text is not None:
            with open(os.path.join(d, "INBOX", "sent.md"), "w",
                      encoding="utf-8", newline="") as f:
                f.write(register_text)
    return d


def call(cwd, arguments):
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": "append_sent_line", "arguments": arguments}},
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


def register(d):
    with open(os.path.join(d, "INBOX", "sent.md"), "rb") as f:
        return f.read().decode("utf-8")


GOOD = {
    "destination": "Discord, the 💡tips channel — “curly quotes” and a résumé",
    "intent": "for continuation",
    "claim": "that the queue tool appends — never edits — the register",
    "pointer": "the session scratchpad, tip-draft.txt",
    "message_id": "1544101479659475000",
}

# 1. Composition, on a register with existing lines.
d = project(register_text="# Sent\n\n- 2026-09-01 — old line — for completion — a claim — a pointer\n")
try:
    answer = call(d, GOOD)
except Exception as exc:  # noqa: BLE001
    print(f"  FAIL the server runs and answers\n       {exc}")
    failures.append("the server runs and answers")
    answer = ""
text = register(d)
lines = text.splitlines()
last = lines[-1] if lines else ""
check("the tool reports the line as appended", answer.startswith("Appended"),
      f"tool answered: {answer!r}")
check("the new line is the LAST line of the register",
      last.startswith("- ") and GOOD["claim"] in last,
      f"last line: {last!r}")
check("the line carries a clock stamp — date and time",
      re.match(r"^- \d{4}-\d{2}-\d{2} \d{2}:\d{2} — ", last) is not None,
      f"last line: {last!r}")
check("the message id sits after the destination, in the fixed place",
      " — message id `%s` — for continuation — " % GOOD["message_id"] in last,
      f"last line: {last!r}")
check("the old line above is untouched",
      lines[2] == "- 2026-09-01 — old line — for completion — a claim — a pointer",
      f"lines: {lines!r}")
check("bytes in equal bytes landed — the non-ASCII text is verbatim",
      GOOD["destination"] in text and "â€”" not in text and "Ã©" not in text,
      f"register: {text!r}")
check("the file ends on exactly one newline", text.endswith("\n") and not text.endswith("\n\n"),
      f"tail: {text[-20:]!r}")
shutil.rmtree(d, ignore_errors=True)

# 2. A register whose last line lacks a trailing newline gets one first.
d = project(register_text="- 2026-09-01 — old line — for completion — a claim — a pointer")
call(d, GOOD)
lines = register(d).splitlines()
check("a missing trailing newline is added before the append, so the old line is not fused",
      len(lines) == 2 and lines[0].endswith("a pointer") and lines[1].startswith("- "),
      f"lines: {lines!r}")
shutil.rmtree(d, ignore_errors=True)

# 3. Create-when-absent: INBOX/ exists, sent.md does not.
d = project()
answer = call(d, {k: v for k, v in GOOD.items() if k != "message_id"})
check("with INBOX/ present and no sent.md, the file is created",
      answer.startswith("Created INBOX/sent.md") and os.path.isfile(os.path.join(d, "INBOX", "sent.md")),
      f"tool answered: {answer!r}")
last = register(d).splitlines()[-1]
check("without a message id, no id segment is written",
      "message id" not in last, f"last line: {last!r}")
shutil.rmtree(d, ignore_errors=True)

# 4. Refuse-when-no-mailbox.
d = project(with_inbox=False)
answer = call(d, GOOD)
check("a project with no INBOX/ is refused and nothing is written",
      answer.startswith("Refused") and "not scaffolded" in answer
      and not os.path.exists(os.path.join(d, "INBOX")),
      f"tool answered: {answer!r}")
shutil.rmtree(d, ignore_errors=True)

# 5. Each refusal, and that a refused call writes nothing.
for label, args, needle in [
    ("a missing required field is refused", {k: v for k, v in GOOD.items() if k != "claim"}, "claim is missing"),
    ("an intent outside the two is refused", dict(GOOD, intent="for reference"), "intent must be exactly"),
    ("a line break inside a field is refused", dict(GOOD, claim="two\nlines"), "line break"),
    # [sweep-security-append-sent-line-message-id-unchecked]: an id carrying a
    # backtick and a spaced dash would land inside the backticked id segment
    # and could split the line's fields when the claims sweep reads it back.
    ("a message id that is not a run of digits is refused",
     dict(GOOD, message_id="1544101479659475000` — for completion"), "not a run of digits"),
]:
    d = project(register_text="# Sent\n")
    answer = call(d, args)
    check(label, answer.startswith("Refused") and needle in answer,
          f"tool answered: {answer!r}")
    check(label + " — and nothing was written", register(d) == "# Sent\n",
          f"register: {register(d)!r}")
    shutil.rmtree(d, ignore_errors=True)

print()
if failures:
    print(f"{len(failures)} failure(s):")
    for name in failures:
        print(f"  {name}")
    sys.exit(1)
print("all cases passed")
