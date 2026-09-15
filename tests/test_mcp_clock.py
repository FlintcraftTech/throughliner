#!/usr/bin/env python3
"""Regression test for mcp/server.py's clock tool.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_mcp_clock.py

No test framework, matching the suites alongside it.

Why this exists ([clock-tool-on-touch-weekday-and-user-check]): a turn that
names a day of the week, a date or a time reads the clock first through one
state-server tool, so the answer's shape is what the rules doc relies on —
a date in YYYY-MM-DD form, a weekday word, a time to the minute and a timezone
name, in one line, read at the call and never stored.
"""

import datetime
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER = os.path.join(ROOT, "plugin", "throughliner", "mcp", "server.py")

WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday", "Sunday")

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


d = tempfile.mkdtemp(prefix="mcp-clock-")

listed = call(d, "tools/list", {})
names = [t["name"] for t in listed.get("result", {}).get("tools", [])]
check("the server lists the clock tool", "clock" in names,
      "tools: %r" % names)

before = datetime.datetime.now()
answer = call(d, "tools/call", {"name": "clock", "arguments": {}})
after = datetime.datetime.now()
text = answer.get("result", {}).get("content", [{}])[0].get("text", "")

check("the answer is one line", "\n" not in text.strip() and text.strip(),
      "answered: %r" % text)

shape = re.match(r"^(\d{4}-\d{2}-\d{2}), (\w+), (\d{2}:\d{2}) \((.+)\)$",
                 text.strip())
check("the line carries a date, a weekday, a time and a timezone",
      shape is not None, "answered: %r" % text)

if shape:
    date, weekday, clock, zone = shape.groups()
    check("the weekday is a weekday word", weekday in WEEKDAYS,
          "weekday: %r" % weekday)
    check("the date is the date the clock reads at the call",
          date in (before.strftime("%Y-%m-%d"), after.strftime("%Y-%m-%d")),
          "date: %r, clock: %s" % (date, before))
    check("the weekday matches the date",
          datetime.date.fromisoformat(date).strftime("%A") == weekday,
          "date %r, weekday %r" % (date, weekday))
    check("the timezone is named", bool(zone.strip()), "zone: %r" % zone)

print()
if failures:
    print("%d failure(s):" % len(failures))
    for name in failures:
        print("  " + name)
    sys.exit(1)
print("all cases passed")
