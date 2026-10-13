#!/usr/bin/env python3
"""The state server refuses any argument a tool's schema does not name
([queue-move-tools-ignore-anchor-silently]).

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_mcp_unknown_argument.py

Why this exists: two moves at planning passed `after_slug`, a field neither
move tool has, and the server dropped it and applied the default position
without a word. One check at the dispatcher covers every tool, since each
declares its properties in `inputSchema`.

Three assertions: a misnamed field is refused with the field named and the
declared names listed, nothing written; a call with only declared names
reaches the handler; a tool declaring no properties refuses every argument.
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


QUEUE = """# QUEUE

## Processed

#### Alpha — a cleared build [alpha]
Alpha's rationale.

--- Cleared to run above this line ---

## Unprocessed

#### Epsilon — a capture [epsilon]
Epsilon's rationale.
"""


def project():
    d = tempfile.mkdtemp(prefix="mcp-unknown-arg-")
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8",
              newline="") as f:
        f.write(QUEUE)
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    return d


def call(cwd, name, arguments):
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": name, "arguments": arguments}},
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
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("id") == 2:
            return r.get("result", {}).get("content", [{}])[0].get("text", "")
    return ""


def read(d):
    with open(os.path.join(d, "QUEUE.md"), "rb") as f:
        return f.read().decode("utf-8")


print("test_mcp_unknown_argument")

d = project()
before = read(d)
text = call(d, "queue_move_section",
            {"slug": "epsilon", "to_section": "Processed",
             "after_slug": "alpha"})
check("a misnamed field is refused and named",
      text.startswith("Refused") and "unknown argument(s): after_slug" in text,
      repr(text))
check("the refusal lists the declared names, position and anchor among them",
      "position" in text and "anchor" in text and "to_section" in text,
      repr(text))
check("the refusal wrote nothing", read(d) == before)

text = call(d, "queue_move_section",
            {"slug": "epsilon", "from_section": "Unprocessed",
             "to_section": "Processed", "position": "BOTTOM"})
check("a call with only declared names reaches the handler",
      not text.startswith("Refused") and "[epsilon]" in read(d).split(
          "## Processed")[1].split("## Unprocessed")[0], repr(text))

text = call(d, "clock", {"zone": "UTC"})
check("a tool declaring no properties refuses every argument",
      text.startswith("Refused") and "no arguments" in text, repr(text))
shutil.rmtree(d, ignore_errors=True)

print()
if failures:
    print("%d failure(s): %s" % (len(failures), ", ".join(failures)))
    sys.exit(1)
print("all cases passed")
