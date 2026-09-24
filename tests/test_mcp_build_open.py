#!/usr/bin/env python3
"""Regression tests for mcp/server.py's build_open tool.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_mcp_build_open.py

Why this exists ([mcp-build-open-tool]): the run wrote its working file by
hand from next.md's specimen, and two failures nothing caught before the run
started — a folder line, which covers no file beneath it, and a path outside
the project — reached the safety check only at the first refused edit. The
tool writes the build working file, or the freeform scope file, from fields,
checks every path at the door, and for the freeform kind admits a path only
after the safety check's own log shows it refused that path earlier in the
same session. Driven end to end as a subprocess over raw UTF-8 bytes, like
the sibling MCP suites; the round trip reads the written file back through
the safety check's own parser.
"""

import importlib.util
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
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "pre_tool_use.py")

failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        failures.append(name)


QUEUE = """# QUEUE

## Processed

#### Alpha — a cleared build with a résumé [alpha]
Alpha's rationale.

#### [user] Gamma — a step of the user's [gamma]
Gamma's rationale.

#### Beta — a cleared build [beta]
Beta's rationale.

--- Cleared to run above this line ---

#### Held — a build below the line [held]
Blocked by: [alpha]

## Unprocessed

#### Delta — a capture [delta]
Delta's rationale.
"""


def project():
    d = tempfile.mkdtemp(prefix="mcp-build-open-")
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8",
              newline="") as f:
        f.write(QUEUE)
    os.makedirs(os.path.join(d, "src"))
    with open(os.path.join(d, "src", "app.py"), "w", encoding="utf-8") as f:
        f.write("print('hi')\n")
    with open(os.path.join(d, "notes.md"), "w", encoding="utf-8") as f:
        f.write("notes\n")
    os.makedirs(os.path.join(d, "day one"))
    with open(os.path.join(d, "day one", "plan.md"), "w", encoding="utf-8") as f:
        f.write("plan\n")
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


def read(d, name):
    with open(os.path.join(d, name), "rb") as f:
        return f.read().decode("utf-8")


def listing(d):
    return sorted(n for n in os.listdir(d) if n.startswith("_"))


def hook_parse(path):
    spec = importlib.util.spec_from_file_location("pre_tool_use_for_test", HOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._parse_build_files(path)


GOOD = {
    "session_id": "s1",
    "kind": "build",
    "items": ["alpha", "beta"],
    "files": ["src/app.py", "notes.md"],
}


def refused(name, arguments, expect, setup=None):
    d = project()
    if setup:
        setup(d)
    before = listing(d)
    text = call(d, "build_open", arguments)
    check("refuses: " + name, text.startswith("Refused") and expect in text,
          repr(text))
    check("refusal wrote nothing: " + name, listing(d) == before,
          repr(listing(d)))
    shutil.rmtree(d, ignore_errors=True)


def existing(d):
    with open(os.path.join(d, "_build-s1.md"), "w", encoding="utf-8") as f:
        f.write("# Active Build\n")


# --- one case per refusal --------------------------------------------------
refused("a missing session id", dict(GOOD, session_id=""),
        "session_id is missing")
refused("a working file already open", GOOD, "already exists", setup=existing)
refused("a slug not in Processed", dict(GOOD, items=["alpha", "delta"]),
        "not a work item in Processed")
refused("a slug below the cleared-to-run line",
        dict(GOOD, items=["alpha", "held"]), "below the cleared-to-run line")
refused("a [user] slug", dict(GOOD, items=["alpha", "gamma"]),
        "never builds")
refused("a path carrying backticks", dict(GOOD, files=["`src/app.py`"]),
        "carries backticks")
refused("a path with text after a spaced dash",
        dict(GOOD, files=["src/app.py — the app"]), "spaced dash")
refused("a path with trailing text", dict(GOOD, files=["src/app.py (new)"]),
        "trailing text")
refused("a path that is an existing folder", dict(GOOD, files=["src"]),
        "existing folder")
refused("a path outside the project root",
        dict(GOOD, files=["../elsewhere.md"]), "outside the project root")
refused("a duplicate path", dict(GOOD, files=["src/app.py", "src/app.py"]),
        "listed twice")
refused("a freeform file with no refusal on record",
        {"session_id": "s1", "kind": "freeform", "files": ["notes.md"]},
        "no refusal under this session's id")

# --- a good build open writes the specimen shape, read back by the hook ------
d = project()
text = call(d, "build_open", GOOD)
w = read(d, "_build-s1.md")
check("the tool reports the file and the paths",
      "Wrote _build-s1.md" in text and "src/app.py, notes.md" in text,
      repr(text))
check("the Run line carries flavor and slug per item",
      "\nRun: build alpha, build beta\n" in w, repr(w))
check("the Entries lines carry flavor, slug and heading from the queue",
      "\nEntries:\n- build — alpha — Alpha — a cleared build with a résumé\n"
      "- build — beta — Beta — a cleared build\n" in w, repr(w))
check("every specimen section is present in order",
      w.index("Index entry candidates:") < w.index("Run-level:")
      < w.index("Files:") < w.index("Progress:") < w.index("Changes:"), repr(w))
check("non-ASCII survives byte-identical", "résumé" in w and "Ã©" not in w)
check("the safety check's parser yields exactly the paths passed",
      hook_parse(os.path.join(d, "_build-s1.md")) == ["src/app.py", "notes.md"],
      repr(hook_parse(os.path.join(d, "_build-s1.md"))))

# --- a space inside a folder name is an ordinary path -----------------------
# ([build-open-refuses-paths-with-spaces]): accepted, written as one bullet,
# and read back by the safety check's parser as one path.
d_sp = project()
text = call(d_sp, "build_open", dict(GOOD, files=["day one/plan.md", "notes.md"]))
check("a path with a space inside a folder name is accepted",
      text.startswith("Wrote _build-s1.md"), repr(text))
check("the spaced path is written to Files: as one bullet and parsed as one path",
      hook_parse(os.path.join(d_sp, "_build-s1.md")) == ["day one/plan.md", "notes.md"],
      repr(hook_parse(os.path.join(d_sp, "_build-s1.md"))))
shutil.rmtree(d_sp, ignore_errors=True)
# Trailing whitespace is stripped at the door, so the bare path is what lands.
d_tw = project()
call(d_tw, "build_open", dict(GOOD, files=["src/app.py  ", "notes.md"]))
check("trailing whitespace is stripped and the bare path written",
      hook_parse(os.path.join(d_tw, "_build-s1.md")) == ["src/app.py", "notes.md"],
      repr(hook_parse(os.path.join(d_tw, "_build-s1.md"))))
shutil.rmtree(d_tw, ignore_errors=True)

# --- the tick tool ticks an item in a file this tool opened ------------------
tick = call(d, "build_tick", {
    "slug": "alpha", "verdict": "confirmed", "depth": "short",
    "index_candidate": "src/app.py: the greeting", "changes": "src/app.py: one line"})
w = read(d, "_build-s1.md")
check("build_tick ticks an item in the opened file",
      "Wrote to _build-s1.md" in tick
      and "\nProgress:\n- [x] Alpha — a cleared build with a résumé — done, "
          "confirmed\nDepth: alpha — short\n" in w, repr(tick) + repr(w))
shutil.rmtree(d, ignore_errors=True)

# --- an empty files list writes an empty Files section -----------------------
d = project()
text = call(d, "build_open", dict(GOOD, files=[]))
w = read(d, "_build-s1.md")
check("an empty files list locks the run to the method docs",
      "\nFiles:\n\nProgress:\n" in w and "locked to the method docs" in text,
      repr(text) + repr(w))
check("the parser reads an empty section as an empty list",
      hook_parse(os.path.join(d, "_build-s1.md")) == [])
shutil.rmtree(d, ignore_errors=True)

# --- the freeform kind reads the safety check's log --------------------------
def with_log(d, sid, decision, path):
    os.makedirs(os.path.join(d, ".throughliner"), exist_ok=True)
    with open(os.path.join(d, ".throughliner", "pre-tool-use.log"), "a",
              encoding="utf-8") as f:
        f.write("2026-09-22 20:00:00\tEdit\t%s\tplanning: not on the standing "
                "list\t%s\t%s\n" % (decision, os.path.join(d, path), sid))


d = project()
with_log(d, "s1", "deny", "notes.md")
text = call(d, "build_open",
            {"session_id": "s1", "kind": "freeform", "files": ["notes.md"]})
check("a freeform path the log shows refused is admitted",
      "Wrote _freeform-s1.md" in text
      and read(d, "_freeform-s1.md").endswith("Files:\n- notes.md\n"),
      repr(text))
check("the parser reads the scope file's one path",
      hook_parse(os.path.join(d, "_freeform-s1.md")) == ["notes.md"])
shutil.rmtree(d, ignore_errors=True)

d = project()
with_log(d, "other", "deny", "notes.md")
with_log(d, "s1", "allow", "notes.md")
text = call(d, "build_open",
            {"session_id": "s1", "kind": "freeform", "files": ["notes.md"]})
check("a refusal under another session, or an allow under this one, "
      "does not open the door",
      text.startswith("Refused") and "no refusal under this session's id" in text
      and "_freeform-s1.md" not in listing(d), repr(text))
shutil.rmtree(d, ignore_errors=True)

# --- the tool is advertised --------------------------------------------------
d = project()
requests = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
]
payload = "".join(json.dumps(r) + "\n" for r in requests).encode("utf-8")
env = dict(os.environ)
env["THROUGHLINER_PROJECT_ROOT"] = d
proc = subprocess.run([sys.executable, SERVER], input=payload, cwd=d,
                      capture_output=True, env=env, timeout=60)
names = []
for line in proc.stdout.decode("utf-8").splitlines():
    if line.strip():
        r = json.loads(line)
        if r.get("id") == 2:
            names = [t["name"] for t in r["result"]["tools"]]
check("tools/list advertises build_open", "build_open" in names, repr(names))
shutil.rmtree(d, ignore_errors=True)

print()
if failures:
    print("%d failure(s):" % len(failures))
    for name in failures:
        print("  " + name)
    sys.exit(1)
print("all cases passed")
