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

print()
if failures:
    print(f"{len(failures)} failure(s):")
    for name in failures:
        print(f"  {name}")
    sys.exit(1)
print("all cases passed")
