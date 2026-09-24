#!/usr/bin/env python3
"""Regression test for mcp/server.py starting in a folder that is not set up.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_mcp_not_set_up.py

Why this exists ([mcp-server-connection-closed-whole-session]): the server
used to exit at launch where the folder had neither QUEUE.md nor SPEC.md,
and the app keeps a launch failure for the chat's life — so a chat that
began with setup in an empty folder never got the server, even after setup
wrote the files. The server now starts anywhere; every tool answers the
not-set-up refusal until the files exist, and the same server then answers
normally.

Driven as ONE long-lived subprocess over raw UTF-8 bytes, with the files
written between requests, like the sibling MCP suites.
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

--- Cleared to run above this line ---

## Unprocessed

"""


class Server:
    def __init__(self, cwd):
        env = dict(os.environ)
        env["THROUGHLINER_PROJECT_ROOT"] = cwd
        self.proc = subprocess.Popen([sys.executable, SERVER], cwd=cwd,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, env=env)
        self.next_id = 0

    def ask(self, method, params=None):
        self.next_id += 1
        request = {"jsonrpc": "2.0", "id": self.next_id, "method": method,
                   "params": params or {}}
        self.proc.stdin.write((json.dumps(request, ensure_ascii=False) + "\n")
                              .encode("utf-8"))
        self.proc.stdin.flush()
        line = self.proc.stdout.readline().decode("utf-8")
        return json.loads(line) if line.strip() else {}

    def call(self, name, arguments):
        r = self.ask("tools/call", {"name": name, "arguments": arguments})
        return r.get("result", {}).get("content", [{}])[0].get("text", "")

    def close(self):
        self.proc.stdin.close()
        self.proc.wait(timeout=30)
        return self.proc.returncode, self.proc.stderr.read().decode("utf-8")


print("test_mcp_not_set_up")
d = tempfile.mkdtemp(prefix="mcp-not-set-up-")
s = Server(d)

init = s.ask("initialize")
check("an empty folder: the server answers the initialize handshake",
      init.get("result", {}).get("serverInfo", {}).get("name") == "throughliner-state",
      repr(init))
tools = s.ask("tools/list")
names = [t.get("name") for t in tools.get("result", {}).get("tools", [])]
check("an empty folder: the tools listing is answered",
      "file_capture" in names and "queue_checkpoint_counts" in names, repr(names))

text = s.call("queue_checkpoint_counts", {})
check("an empty folder: queue_checkpoint_counts is refused as not set up",
      text.startswith("Refused") and "not set up" in text and "/setup" in text,
      repr(text))
text = s.call("file_capture", {"heading": "First thing", "slug": "first-thing",
                               "body": "captured by you"})
check("an empty folder: file_capture is refused as not set up",
      text.startswith("Refused") and "not set up" in text, repr(text))
check("nothing was written to the empty folder", os.listdir(d) == [],
      repr(os.listdir(d)))

# Setup writes the files; the SAME server now answers.
with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
    f.write("# SPEC\n")
with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8", newline="") as f:
    f.write(QUEUE)
text = s.call("file_capture", {"heading": "First thing", "slug": "first-thing",
                               "body": "captured by you"})
with open(os.path.join(d, "QUEUE.md"), "r", encoding="utf-8") as f:
    queue = f.read()
check("once the files exist, the same server files a capture",
      not text.startswith("Refused") and "#### First thing [first-thing]" in queue,
      repr(text) + "\n" + queue)

rc, err = s.close()
check("the server exits cleanly at end of input", rc == 0,
      "rc=%r stderr=%r" % (rc, err))
shutil.rmtree(d, ignore_errors=True)

if failures:
    print("\n%d FAILURE(S)" % len(failures))
    sys.exit(1)
print("\nall passed")
