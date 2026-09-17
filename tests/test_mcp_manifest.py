#!/usr/bin/env python3
"""The plugin package's own server registration names a file that exists and
parses ([mcp-server-promotion]).

Run: py tests/test_mcp_manifest.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

The plugin-root `.mcp.json` form is used rather than an inline `mcpServers`
block in plugin.json: Claude Code's issue tracker carries a report of the
inline block being dropped at manifest parsing (anthropics/claude-code#16143,
open when re-read 2026-09-17).
"""

import json
import os
import py_compile
import sys

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugin", "throughliner")

failures = []


def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label
          + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


print("test_mcp_manifest")
path = os.path.join(PLUGIN, ".mcp.json")
check("the package carries a .mcp.json at its root", os.path.isfile(path), path)
try:
    with open(path, encoding="utf-8") as f:
        manifest = json.load(f)
except (OSError, ValueError) as exc:
    manifest = {}
    check("the registration parses as JSON", False, str(exc))
servers = manifest.get("mcpServers") or {}
check("one server is registered", list(servers) == ["throughliner-state"],
      repr(list(servers)))
entry = servers.get("throughliner-state") or {}
check("the server runs on python, the interpreter the hooks use",
      entry.get("command") == "python", repr(entry))
args = entry.get("args") or []
check("the argument names the server through ${CLAUDE_PLUGIN_ROOT}",
      len(args) == 1 and args[0].startswith("${CLAUDE_PLUGIN_ROOT}/"), repr(args))
resolved = os.path.join(PLUGIN, *args[0].replace("${CLAUDE_PLUGIN_ROOT}/", "")
                        .split("/")) if args else ""
check("the named file exists in the package", bool(resolved) and os.path.isfile(resolved),
      resolved)
if resolved and os.path.isfile(resolved):
    try:
        py_compile.compile(resolved, doraise=True)
        check("and it compiles", True)
    except py_compile.PyCompileError as exc:
        check("and it compiles", False, str(exc))

print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)
