#!/usr/bin/env python3
"""Regression test for mcp/server.py's planning_anchor tool.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_mcp_planning_anchor.py

Why this exists ([mcp-planning-anchor-tool]): three opening reads typed the
date of the most recent planning session by hand — plan.md's index read and
issues check, and the development project's replies read. The tool answers
it from the record's own body fields, classified the way queue_digest.py
classifies a record (`Work processed:` and not `Files touched:`), never from
the filename, and lists the index lines newer than that record. Driven as a
subprocess like test_mcp_clock.py.
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
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        failures.append(name)


def call(cwd, method, params):
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": method, "params": params},
    ]
    payload = "".join(json.dumps(r) + "\n" for r in requests).encode("utf-8")
    env = dict(os.environ)
    env["THROUGHLINER_PROJECT_ROOT"] = cwd
    proc = subprocess.run([sys.executable, SERVER], input=payload, cwd=cwd,
                          capture_output=True, env=env, timeout=60)
    if proc.returncode != 0:
        raise AssertionError("server exited %d\nstderr: %r"
                             % (proc.returncode, proc.stderr))
    for line in proc.stdout.decode("utf-8").splitlines():
        if line.strip():
            message = json.loads(line)
            if message.get("id") == 2:
                return message
    return {}


def anchor(cwd):
    answer = call(cwd, "tools/call", {"name": "planning_anchor", "arguments": {}})
    return answer.get("result", {}).get("content", [{}])[0].get("text", "")


def project(records, index_lines):
    d = tempfile.mkdtemp(prefix="mcp-anchor-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    os.makedirs(os.path.join(d, "LOG"))
    for name, body in records.items():
        with open(os.path.join(d, "LOG", name), "w", encoding="utf-8") as f:
            f.write(body)
    with open(os.path.join(d, "LOG", "index.md"), "w", encoding="utf-8") as f:
        f.write("# LOG Index\n\nNewest first.\n\n" + "\n".join(index_lines) + "\n")
    return d


PLAN_OLD = "# aaa — plan — the older planning session\n\nRecorded 2026-09-20 10:00, read from the clock.\n\nWork processed: two items.\n"
BUILD_MID = "# bbb — build — a build between them\n\nRecorded 2026-09-22 12:00, read from the clock.\n\nFiles touched: x.md.\n"
PLAN_NEW = "# ccc — plan — the newer planning session, named by slug\n\nRecorded 2026-09-23 15:40, read from the clock.\n\nWork processed: one item.\n"
BUILD_LATEST = "# ddd — build — the latest build\n\nRecorded 2026-09-24 09:00, read from the clock.\n\nFiles touched: y.md.\n"

d = project(
    {"2026-09-20-chat-plan.md": PLAN_OLD,
     "2026-09-22-something-build.md": BUILD_MID,
     "2026-09-23-some-item-slug.md": PLAN_NEW,
     "2026-09-24-latest-thing.md": BUILD_LATEST},
    ["- ddd — the latest build → 2026-09-24-latest-thing.md",
     "- ccc — the newer planning session → 2026-09-23-some-item-slug.md",
     "- bbb — a build between them → 2026-09-22-something-build.md",
     "- aaa — the older planning session → 2026-09-20-chat-plan.md"])

listed = call(d, "tools/list", {})
names = [t["name"] for t in listed.get("result", {}).get("tools", [])]
check("the server lists the planning_anchor tool", "planning_anchor" in names,
      "tools: %r" % names)

text = anchor(d)
check("the newer planning record is the anchor, found by its body not its name",
      "2026-09-23 15:40" in text and "2026-09-23-some-item-slug.md" in text, text)
check("the build record after it is not taken as the anchor",
      "2026-09-24-latest-thing.md" not in text.splitlines()[0], text)
check("the anchor date is answered on its own line",
      "Anchor date for --since and the issues check: 2026-09-23" in text, text)
check("the index lines newer than the anchor are listed, and only those",
      "Index lines newer than it (1):" in text
      and "- ddd — the latest build" in text
      and "- aaa — the older" not in text, text)
shutil.rmtree(d, ignore_errors=True)

d2 = project({"2026-09-24-only-build.md": BUILD_LATEST},
             ["- ddd — the latest build → 2026-09-24-only-build.md"])
text = anchor(d2)
check("no planning record: says so and answers the current month's lines",
      "No planning record found" in text and "- ddd — the latest build" in text,
      text)
shutil.rmtree(d2, ignore_errors=True)

print()
if failures:
    print("%d failure(s):" % len(failures))
    for name in failures:
        print("  " + name)
    sys.exit(1)
print("all cases passed")
