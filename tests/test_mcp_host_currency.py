#!/usr/bin/env python3
"""The state server's host_currency reads the snapshot the server runs from
([host-currency-reads-stale-install]).

Run: py tests/test_mcp_host_currency.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

Why this exists: the tool used to pick the newest folder under the plugin
cache by modification time, and on Windows a folder's time moves whenever
anything inside it is touched, so an older build's folder read as newest and
the tool named a build the session was not running while the opening named
the right one. It now reads its own plugin root, as the hook does, and names
any newer build sitting beside it in the cache.
"""

import importlib.util
import os
import shutil
import sys
import tempfile
import time

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER = os.path.join(ROOT, "plugin", "throughliner", "mcp", "server.py")

failures = []


def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


spec = importlib.util.spec_from_file_location("throughliner_server", SERVER)
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)

print("test_mcp_host_currency")

d = tempfile.mkdtemp(prefix="host-currency-")
cache = os.path.join(d, ".claude", "plugins", "cache", "flintcraft", "throughliner")
older = os.path.join(cache, "1.24.0-test8")
newer = os.path.join(cache, "1.24.0-test9")
os.makedirs(older)
os.makedirs(newer)
# The older build's folder carries the NEWER modification time — the Windows
# shape that misled the old read.
past = time.time() - 86400
os.utime(newer, (past, past))

version, path = server._installed_snapshot(older)
check("the snapshot is the folder the server runs from, not the newest by time",
      (version, path) == ("1.24.0-test8", os.path.abspath(older)),
      repr((version, path)))
version, path = server._installed_snapshot(newer)
check("run from the newer folder, it reports that one",
      version == "1.24.0-test9", repr((version, path)))
check("a plugin root outside the cache is no snapshot",
      server._installed_snapshot(os.path.join(d, "source", "plugin", "throughliner"))
      == (None, None))

check("a newer build beside the older one is named",
      server._newer_installed_builds(older) == ["1.24.0-test9"],
      repr(server._newer_installed_builds(older)))
check("the newest build has nothing newer beside it",
      server._newer_installed_builds(newer) == [],
      repr(server._newer_installed_builds(newer)))
os.makedirs(os.path.join(cache, "1.24.0"))
check("a release sorts after its test builds",
      server._newer_installed_builds(newer) == ["1.24.0"],
      repr(server._newer_installed_builds(newer)))
check("version order reads the numbers, not the text",
      server._version_key("1.24.0-test10") > server._version_key("1.24.0-test9"))

shutil.rmtree(d, ignore_errors=True)

print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)
