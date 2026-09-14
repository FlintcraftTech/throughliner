#!/usr/bin/env python3
"""Regression tests for mcp/server.py's build_tick tool.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_mcp_build_tick.py

Why this exists ([mcp-build-tick-tool]): the build run's per-item close was
six free-text edits copied from a specimen, and a 22-tick run came out with
its forms wrong. The tool writes the tick, the slug-bound depth and rule-gate
lines, the index candidate and the changes entry in the specimen's exact
shapes, refuses at the door what the close and the stop hook would otherwise
mis-parse, and removes the item from Processed in the same call. Driven end
to end as a subprocess over raw UTF-8 bytes, like the sibling MCP suites.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

# UTF-8 on both streams, copied from reorder_queue.py — the fixtures carry
# non-ASCII on purpose, and a cp1252 console would crash the report.
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

#### Alpha — a cleared build with a gate [alpha]
Alpha's rationale — an em-dash and a résumé.
Rule gate: run — one clause admitted to its parent; nothing evicted.

#### Beta — a cleared build with no gate [beta]
Beta's rationale.

--- Cleared to run above this line ---

## Unprocessed

#### Delta — a capture [delta]
Delta's rationale.
"""

WORKING = """# Active Build

Run: build alpha, build beta

Entries:
- build — alpha — Alpha — a cleared build with a gate
- build — beta — Beta — a cleared build with no gate

Index entry candidates:

Run-level:

Files:
- some/file.py

Progress:

Changes:
"""


def project(session="s1", working=WORKING, extra_working=False):
    d = tempfile.mkdtemp(prefix="mcp-build-tick-")
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8",
              newline="") as f:
        f.write(QUEUE)
    if working is not None:
        with open(os.path.join(d, "_build-%s.md" % session), "w",
                  encoding="utf-8", newline="") as f:
            f.write(working)
    if extra_working:
        with open(os.path.join(d, "_build-other.md"), "w", encoding="utf-8",
                  newline="") as f:
            f.write(working)
    return d


def call(cwd, arguments):
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": "build_tick", "arguments": arguments}},
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


GOOD = {
    "slug": "alpha",
    "verdict": "confirmed",
    "depth": "short",
    "rule_gate": "run — one clause admitted to its parent; nothing evicted",
    "index_candidate": "some/file.py: the guard gains a résumé check — Ω",
    "changes": "- some/file.py: added the check, 12 lines",
}


def refused(name, arguments, expect, **kw):
    d = project(**kw)
    before_q = read(d, "QUEUE.md")
    before_w = read(d, "_build-s1.md") if kw.get("working", WORKING) else None
    text = call(d, arguments)
    check("refuses: " + name, text.startswith("Refused") and expect in text,
          repr(text))
    check("refusal wrote nothing: " + name,
          read(d, "QUEUE.md") == before_q
          and (before_w is None or read(d, "_build-s1.md") == before_w))
    shutil.rmtree(d, ignore_errors=True)


# --- one case per refusal --------------------------------------------------
refused("a slug not in the working file",
        dict(GOOD, slug="delta", rule_gate=""), "not a work item in Processed")
refused("a missing verdict", dict(GOOD, verdict=""), "verdict must be")
refused("unconfirmed with no reason", dict(GOOD, verdict="unconfirmed"),
        "reason is missing")
refused("a full depth with no trigger", dict(GOOD, depth="full"),
        "names its trigger")
refused("a gate line the item does not carry",
        dict(GOOD, slug="beta"), "carries no `Rule gate:` line")
refused("a missing gate line the item carries",
        dict(GOOD, rule_gate=""), "rule_gate is required")
refused("an index candidate led by an article",
        dict(GOOD, index_candidate="The guard gains a check"),
        "opens with A/An/The")
refused("no working file", GOOD, "no build working file", working=None)
refused("two working files and no session id", GOOD,
        "pass session_id", extra_working=True)

# --- a good tick lands every line and removes the item -----------------------
d = project()
text = call(d, GOOD)
w = read(d, "_build-s1.md")
q = read(d, "QUEUE.md")
check("the tick line is in the specimen's confirmed shape",
      "\nProgress:\n- [x] Alpha — a cleared build with a gate — done, confirmed\n"
      in w, repr(w))
check("the slug-bound Depth line follows the tick",
      "done, confirmed\nDepth: alpha — short\n" in w, repr(w))
check("the slug-bound Rule gate line follows the depth",
      "Depth: alpha — short\nRule gate: alpha — run — one clause admitted to "
      "its parent; nothing evicted\n" in w, repr(w))
check("the index candidate lands under its header",
      "\nIndex entry candidates:\n- some/file.py: the guard gains a résumé "
      "check — Ω\n" in w, repr(w))
check("the changes entry lands under Changes",
      "\nChanges:\n- some/file.py: added the check, 12 lines\n" in w, repr(w))
check("non-ASCII survives byte-identical (em-dash, é, Ω)",
      "résumé check — Ω" in w and "â€”" not in w and "Ã©" not in w)
check("the Files section is untouched", "\nFiles:\n- some/file.py\n" in w)
check("the item left Processed", "[alpha]" not in q and "[beta]" in q, repr(q))
check("the tool reports the writes and the removal",
      "Wrote to _build-s1.md" in text and "Removed [alpha] from Processed" in text,
      repr(text))

# --- a second tick appends after the first, and a re-tick is refused --------
text2 = call(d, {"slug": "beta", "verdict": "unconfirmed",
                 "reason": "the suite has not run",
                 "depth": "full", "trigger": "alternative seriously weighed",
                 "index_candidate": "docs/x.md: reworded",
                 "changes": "docs/x.md: one sentence"})
w = read(d, "_build-s1.md")
check("the second tick follows the first under Progress",
      "Rule gate: alpha — run — one clause admitted to its parent; nothing "
      "evicted\n- [x] Beta — a cleared build with no gate — done, UNCONFIRMED: "
      "the suite has not run\nDepth: beta — full, alternative seriously "
      "weighed\n" in w, repr(w))
check("a bare changes line gains its bullet",
      "- some/file.py: added the check, 12 lines\n- docs/x.md: one sentence\n"
      in w, repr(w))
check("beta left Processed too", "[beta]" not in read(d, "QUEUE.md"))
text3 = call(d, dict(GOOD))
check("re-ticking a ticked item is refused",
      text3.startswith("Refused") and "not a work item in Processed" in text3,
      repr(text3))
shutil.rmtree(d, ignore_errors=True)

# --- session_id names the file where several exist ---------------------------
d = project(extra_working=True)
text = call(d, dict(GOOD, session_id="s1"))
check("session_id selects the named working file",
      "Wrote to _build-s1.md" in text
      and "Depth: alpha" in read(d, "_build-s1.md")
      and "Depth: alpha" not in read(d, "_build-other.md"), repr(text))
shutil.rmtree(d, ignore_errors=True)

# --- a CRLF working file keeps its line endings -----------------------------
d = project(working=WORKING.replace("\n", "\r\n"))
call(d, GOOD)
w = read(d, "_build-s1.md")
check("a CRLF working file gains CRLF lines only",
      "\r\n" in w and "\n" not in w.replace("\r\n", ""), repr(w[:200]))
shutil.rmtree(d, ignore_errors=True)

print()
if failures:
    print("%d failure(s):" % len(failures))
    for name in failures:
        print("  " + name)
    sys.exit(1)
print("all cases passed")
