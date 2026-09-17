#!/usr/bin/env python3
"""mcp/server.py's append_tail tool: post-close work appended to the chat's
own record under `## After /done`, found through the session-closed marker
([post-close-tail-offer-enforced-once]).

Run: py tests/test_mcp_append_tail.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER = os.path.join(ROOT, "plugin", "throughliner", "mcp", "server.py")

failures = []


def check(name, condition, detail=""):
    print(("  PASS  " if condition else "  FAIL  ") + name
          + ("" if condition else f" — {detail}"))
    if not condition:
        failures.append(name)


def project(marker=True):
    d = tempfile.mkdtemp(prefix="mcp-append-tail-")
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8") as f:
        f.write("# QUEUE\n\n## Processed\n\n--- Cleared to run above this line ---\n\n## Unprocessed\n")
    os.makedirs(os.path.join(d, "LOG"))
    with open(os.path.join(d, "LOG", "2026-09-17-fixture.md"), "w", encoding="utf-8") as f:
        f.write("# abc1234 — a fixture record\n\nThe entry — with an em-dash.\n")
    if marker:
        os.makedirs(os.path.join(d, ".throughliner"))
        with open(os.path.join(d, ".throughliner", "session-closed-s1"), "w",
                  encoding="utf-8") as f:
            f.write("2026-09-17-fixture.md\n")
    return d


def call(cwd, arguments):
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": "append_tail", "arguments": arguments}},
    ]
    payload = "".join(json.dumps(r, ensure_ascii=False) + "\n"
                      for r in requests).encode("utf-8")
    env = dict(os.environ)
    env["THROUGHLINER_PROJECT_ROOT"] = cwd
    proc = subprocess.run([sys.executable, SERVER], input=payload, cwd=cwd,
                          capture_output=True, env=env, timeout=60)
    if proc.returncode != 0:
        raise AssertionError("server exited %d\nstdout: %r\nstderr: %r"
                             % (proc.returncode, proc.stdout, proc.stderr))
    for line in proc.stdout.decode("utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            if r.get("id") == 2:
                return r["result"]["content"][0]["text"]
    return ""


print("test_mcp_append_tail")
d = project()
text = call(d, {"prose": "Fixed the wording — one sentence."})
with open(os.path.join(d, "LOG", "2026-09-17-fixture.md"), encoding="utf-8") as f:
    record = f.read()
check("the tail lands under the heading, once", text.startswith("Appended")
      and record.count("## After /done") == 1
      and "Fixed the wording — one sentence." in record, record)
check("the tail is stamped from the clock", "**2026-" in record.split("## After /done")[1], record)
call(d, {"prose": "A second piece."})
with open(os.path.join(d, "LOG", "2026-09-17-fixture.md"), encoding="utf-8") as f:
    record = f.read()
check("a second tail reuses the heading", record.count("## After /done") == 1
      and "A second piece." in record, record)
check("non-ASCII in the record survives", "with an em-dash" in record and "â€”" not in record)
shutil.rmtree(d, ignore_errors=True)

d = project(marker=False)
text = call(d, {"prose": "Nothing closed."})
check("no marker refuses", text.startswith("Refused") and "no session-closed marker" in text, text)
shutil.rmtree(d, ignore_errors=True)

print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)
