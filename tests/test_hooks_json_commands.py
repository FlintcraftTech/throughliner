#!/usr/bin/env python3
"""Regression test for hooks/hooks.json's command lines.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_hooks_json_commands.py

Why this exists ([hook-interpreter-fallback-on-windows]): a bare `python` on
Windows may be the Store placeholder or an application's bundled interpreter,
while `py` reaches the real one. Every hook command is shell form — no `args`
field, so the app hands it to a shell — and runs `py -3 <script>` where `py`
exists and `python <script>` otherwise. Two halves: every command carries
both interpreters in that shape and names a file that exists under hooks/;
and the line, run under a POSIX shell with a fake `py` on PATH and then
without one, reaches the script exactly once each way.
"""

import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugin", "throughliner")
HOOKS_JSON = os.path.join(PLUGIN, "hooks", "hooks.json")

failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        failures.append(name)


SHAPE = re.compile(
    r'^if command -v py >/dev/null 2>&1; then py -3 "\$\{CLAUDE_PLUGIN_ROOT\}/hooks/'
    r'([a-z_]+\.py)"; else python "\$\{CLAUDE_PLUGIN_ROOT\}/hooks/\1"; fi$')


def commands():
    with open(HOOKS_JSON, encoding="utf-8") as f:
        manifest = json.load(f)
    found = []
    for event, groups in manifest["hooks"].items():
        for group in groups:
            for hook in group.get("hooks", []):
                found.append((event, hook))
    return found


def posix_shell():
    for name in ("sh", "bash"):
        path = shutil.which(name)
        if path:
            return path
    for candidate in (r"C:\Program Files\Git\usr\bin\sh.exe",
                      r"C:\Program Files\Git\bin\bash.exe"):
        if os.path.isfile(candidate):
            return candidate
    return None


print("test_hooks_json_commands")
found = commands()
check("seven hook commands are registered", len(found) == 7, str(len(found)))
for event, hook in found:
    cmd = hook.get("command", "")
    m = SHAPE.match(cmd)
    check("%s: shell form with both interpreters" % event, m is not None, cmd)
    check("%s: no args field, so a shell runs it" % event, "args" not in hook, repr(hook))
    if m:
        check("%s: names an existing hook file (%s)" % (event, m.group(1)),
              os.path.isfile(os.path.join(PLUGIN, "hooks", m.group(1))))

shell = posix_shell()
check("a POSIX shell is available to run the line", shell is not None,
      "neither sh nor bash found; Git for Windows supplies one")

if shell and found:
    line = found[0][1]["command"]
    d = tempfile.mkdtemp(prefix="hooks-json-")
    os.makedirs(os.path.join(d, "root", "hooks"))
    script = os.path.join(d, "root", "hooks", found[0][1]["command"].split("/hooks/")[1].split('"')[0])
    with open(script, "w", encoding="utf-8") as f:
        f.write("print('hook ran')\n")
    log = os.path.join(d, "calls.log").replace("\\", "/")

    def fake(name, tag):
        path = os.path.join(d, "bin", name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write('#!/bin/sh\necho "%s $*" >> "%s"\n' % (tag, log))
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)

    def run(with_py):
        if os.path.exists(log):
            os.remove(log)
        shutil.rmtree(os.path.join(d, "bin"), ignore_errors=True)
        fake("python", "python")
        if with_py:
            fake("py", "py")
        env = dict(os.environ)
        env["CLAUDE_PLUGIN_ROOT"] = os.path.join(d, "root").replace("\\", "/")
        # PATH holds the fake bin and the shell's own folder only, so a real
        # `py` on this machine cannot answer `command -v py` in the without-py run.
        env["PATH"] = os.path.join(d, "bin") + os.pathsep + os.path.dirname(shell)
        subprocess.run([shell, "-c", line], env=env, capture_output=True,
                       timeout=30)
        try:
            with open(log, encoding="utf-8") as f:
                return [ln.strip() for ln in f if ln.strip()]
        except OSError:
            return []

    calls = run(with_py=True)
    check("with py on PATH: py -3 runs the script once and python never",
          len(calls) == 1 and calls[0].startswith("py -3 ") and "hooks/" in calls[0],
          repr(calls))
    calls = run(with_py=False)
    check("without py: python runs the script once",
          len(calls) == 1 and calls[0].startswith("python ") and "hooks/" in calls[0],
          repr(calls))
    shutil.rmtree(d, ignore_errors=True)

if failures:
    print("\n%d FAILURE(S)" % len(failures))
    sys.exit(1)
print("\nall passed")
