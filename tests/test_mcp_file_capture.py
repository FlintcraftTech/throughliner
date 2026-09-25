#!/usr/bin/env python3
"""Regression tests for mcp/server.py's file_capture tool.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_mcp_file_capture.py

No test framework, matching the suites alongside it: this project has no test
runner, and `python` on the author's machine resolves to an application's
bundled interpreter that has no pytest.

Why this exists ([mcp-file-capture-encoding-mangles]): the server's first two
real filings landed every em-dash in QUEUE.md as mojibake. The mechanism: the
request loop read `sys.stdin` bare, and stdin was the one stream never
reconfigured to UTF-8, so on Windows the incoming tool call was decoded as the
legacy codepage. The server had no suite at all, which is why it shipped. The
core assertion here is transport fidelity: bytes in equal bytes landed.

The server is driven end to end as a subprocess over its own stdin/stdout,
with the request encoded to UTF-8 **bytes** — text mode would let Python's own
locale handling mask exactly the defect this pins.
"""

import json
import os
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


def project():
    """A minimal adopted project with an empty two-section queue."""
    d = tempfile.mkdtemp(prefix="mcp-file-capture-")
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8") as f:
        f.write("# QUEUE\n\n## Processed\n\n"
                "--- Cleared to run above this line ---\n\n## Unprocessed\n")
    return d


def call_file_capture(cwd, arguments):
    """Drive the server over raw UTF-8 bytes and return its responses."""
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": "file_capture", "arguments": arguments}},
    ]
    payload = "".join(json.dumps(r, ensure_ascii=False) + "\n"
                      for r in requests).encode("utf-8")
    env = dict(os.environ)
    env["THROUGHLINER_PROJECT_ROOT"] = cwd
    proc = subprocess.run(
        [sys.executable, SERVER],
        input=payload,
        cwd=cwd,
        capture_output=True,
        env=env,
        timeout=60,
    )
    if proc.returncode != 0:
        raise AssertionError(
            f"server exited {proc.returncode}\n"
            f"stdout: {proc.stdout!r}\nstderr: {proc.stderr!r}")
    responses = [json.loads(line) for line in
                 proc.stdout.decode("utf-8").splitlines() if line.strip()]
    return responses


BODY = ("Filed by the suite — an em-dash, “curly quotes” and a résumé, "
        "all of which must land byte-clean.")

d = project()
try:
    responses = call_file_capture(d, {
        "heading": "Fixture capture — non-ASCII fidelity",
        "slug": "fixture-non-ascii-fidelity",
        "body": BODY,
    })
except Exception as exc:  # noqa: BLE001 — a failure to run IS the finding
    print(f"  FAIL the server runs and answers\n       {exc}")
    failures.append("the server runs and answers")
    responses = []

result_text = ""
for r in responses:
    if r.get("id") == 2:
        result_text = r.get("result", {}).get("content", [{}])[0].get("text", "")

check(
    "the tool reports the capture as filed",
    result_text.startswith("Filed at the bottom of Unprocessed:"),
    f"tool answered: {result_text!r}",
)

check(
    "the tool's own echo carries the em-dash intact",
    "—" in result_text,
    f"tool answered: {result_text!r}",
)

with open(os.path.join(d, "QUEUE.md"), "rb") as f:
    queue_bytes = f.read()
queue_text = queue_bytes.decode("utf-8")

check(
    "bytes in equal bytes landed — the body's non-ASCII text is in QUEUE.md verbatim",
    BODY in queue_text,
    f"queue tail: {queue_text[-400:]!r}",
)

check(
    "no cp1252 mojibake shape reached the file",
    "â€”" not in queue_text and "Ã©" not in queue_text,
    f"queue tail: {queue_text[-400:]!r}",
)

check(
    "the entry carries the mechanical filed-at stamp with a clock time",
    "stamped by the capture tool." in queue_text,
    f"queue tail: {queue_text[-400:]!r}",
)

shutil.rmtree(d, ignore_errors=True)

# --- assigned_to: one name lands as the entry's line; two names are refused --
d = project()
responses = call_file_capture(d, {
    "heading": "Fixture capture with an assignee",
    "slug": "fixture-assignee",
    "body": "Filed by the suite.",
    "assigned_to": "Alex",
})
text = ""
for r in responses:
    if r.get("id") == 2:
        text = r.get("result", {}).get("content", [{}])[0].get("text", "")
with open(os.path.join(d, "QUEUE.md"), "rb") as f:
    queue_text = f.read().decode("utf-8")
check("assigned_to writes the entry's Assigned to: line",
      text.startswith("Filed") and "Assigned to: Alex" in queue_text,
      f"tool answered: {text!r}; queue tail: {queue_text[-300:]!r}")
before = queue_text
responses = call_file_capture(d, {
    "heading": "Fixture capture with two assignees",
    "slug": "fixture-two-assignees",
    "body": "Filed by the suite.",
    "assigned_to": "Alex, Sam",
})
text = ""
for r in responses:
    if r.get("id") == 2:
        text = r.get("result", {}).get("content", [{}])[0].get("text", "")
with open(os.path.join(d, "QUEUE.md"), "rb") as f:
    after = f.read().decode("utf-8")
check("two names are refused and nothing is written",
      text.startswith("Refused") and "not one name" in text and after == before,
      f"tool answered: {text!r}")
shutil.rmtree(d, ignore_errors=True)

# --- a heading given with its own slug on the end lands once
# ([advisory-heading-doubles-slug-through-file-capture]) --------------------
d = project()
responses = call_file_capture(d, {
    "heading": "Last session advises processing [x] next [forward-advisory]",
    "slug": "forward-advisory",
    "body": "Filed by the suite.",
})
text = ""
for r in responses:
    if r.get("id") == 2:
        text = r.get("result", {}).get("content", [{}])[0].get("text", "")
with open(os.path.join(d, "QUEUE.md"), "rb") as f:
    queue_text = f.read().decode("utf-8")
check("a heading typed with its slug files the slug once",
      text.startswith("Filed")
      and "next [forward-advisory]" in queue_text
      and "[forward-advisory] [forward-advisory]" not in queue_text,
      f"tool answered: {text!r}; queue tail: {queue_text[-300:]!r}")
shutil.rmtree(d, ignore_errors=True)

# --- a standing entry is refused at the door; a plain slice is filed
# ([standing-entry-reads-as-unshipped]) ------------------------------------
def answer(responses):
    for r in responses:
        if r.get("id") == 2:
            return r.get("result", {}).get("content", [{}])[0].get("text", "")
    return ""


for phrase in ("stays open until", "kept open", "kept whole while",
               "returns at each", "returns when the next", "the umbrella"):
    d = project()
    text = answer(call_file_capture(d, {
        "heading": "Fixture standing entry",
        "slug": "fixture-standing",
        "body": "This entry %s every piece has shipped." % phrase,
    }))
    with open(os.path.join(d, "QUEUE.md"), "rb") as f:
        queue_text = f.read().decode("utf-8")
    check("a body carrying %r is refused and names the goal route" % phrase,
          text.startswith("Refused") and "Goals section" in text
          and "fixture-standing" not in queue_text,
          f"tool answered: {text!r}")
    shutil.rmtree(d, ignore_errors=True)

d = project()
text = answer(call_file_capture(d, {
    "heading": "Fixture slice of work",
    "slug": "fixture-slice",
    "body": "The next concrete piece: the tool gains one field and one test.",
}))
check("a body naming a slice of work with none of the phrases is filed",
      text.startswith("Filed"), f"tool answered: {text!r}")
shutil.rmtree(d, ignore_errors=True)

# --- until_built ([file-capture-until-built]): with a blocker the line ends
# `until built`; without one the switch is refused --------------------------
d = project()
answer(call_file_capture(d, {
    "heading": "Fixture blocker",
    "slug": "fixture-blocker",
    "body": "Filed by the suite.",
}))
text = answer(call_file_capture(d, {
    "heading": "Fixture held until the blocker is built",
    "slug": "fixture-held-until-built",
    "body": "Filed by the suite.",
    "blocked_by": ["fixture-blocker"],
    "until_built": True,
}))
with open(os.path.join(d, "QUEUE.md"), "rb") as f:
    queue_text = f.read().decode("utf-8")
check("until_built with a blocker writes the line ending `until built`",
      text.startswith("Filed")
      and "Blocked by: [fixture-blocker] until built" in queue_text.replace("\r", ""),
      f"tool answered: {text!r}; queue tail: {queue_text[-300:]!r}")
before = queue_text
text = answer(call_file_capture(d, {
    "heading": "Fixture switch with no blocker",
    "slug": "fixture-switch-alone",
    "body": "Filed by the suite.",
    "until_built": True,
}))
with open(os.path.join(d, "QUEUE.md"), "rb") as f:
    after = f.read().decode("utf-8")
check("until_built without blocked_by is refused and nothing is written",
      text.startswith("Refused") and "without blocked_by" in text
      and after == before, f"tool answered: {text!r}")
shutil.rmtree(d, ignore_errors=True)

print()
if failures:
    print(f"{len(failures)} failure(s):")
    for name in failures:
        print(f"  {name}")
    sys.exit(1)
print("all cases passed")
