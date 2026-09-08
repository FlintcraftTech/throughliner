#!/usr/bin/env python3
"""Regression tests for mcp/server.py's three queue-move tools:
queue_move, queue_move_section and queue_delete.

Host-only dev artifact — not shipped in the plugin package.

Run:  py workshop/resources/testing/test_mcp_queue_moves.py

No test framework, matching the suites alongside it: this project has no test
runner, and `python` on the author's machine resolves to an application's
bundled interpreter that has no pytest.

Why this exists ([mcp-queue-move-tools]): a planning session moves, keeps and
deletes queue entries many times a session, and each was a hand-typed command
whose arguments nothing checked until the script refused them. The tools check
at the door — the slug and anchor resolve, the position word is one of four, a
marker placement is named whenever anything would cross the readiness line —
and run the script's own move, so there is one implementation. The server is
driven end to end as a subprocess over raw UTF-8 bytes, as the sibling suites
do, so transport fidelity is pinned alongside the tools' own logic: every
moved block must land byte-identical, non-ASCII included, and every refusal
must leave the file byte-identical.
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

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SERVER = os.path.join(ROOT, "plugin", "throughliner", "mcp", "server.py")

MARKER = "--- Cleared to run above this line ---"

failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        failures.append(name)


QUEUE = """# QUEUE

Intro prose — with an em-dash — that must survive untouched.

## Processed

#### Alpha — a cleared build [alpha]
Alpha's rationale — an em-dash and a résumé, which must survive untouched.

#### Beta — another cleared build [beta]
Beta's rationale.

--- Cleared to run above this line ---

#### Gamma — a held build [gamma]
Gamma's rationale, naming “curly quotes”.
Blocked by: [beta]

#### Delta — another held build [delta]
Delta's rationale.

## Unprocessed

#### Epsilon — a capture [epsilon]
Epsilon's rationale — ¡con acentos!

#### Zeta — a capture [zeta]
Zeta's rationale.
"""

ALPHA_BLOCK = ("#### Alpha — a cleared build [alpha]\n"
               "Alpha's rationale — an em-dash and a résumé, which must "
               "survive untouched.\n")
GAMMA_BLOCK = ("#### Gamma — a held build [gamma]\n"
               "Gamma's rationale, naming “curly quotes”.\n"
               "Blocked by: [beta]\n")
EPSILON_BLOCK = ("#### Epsilon — a capture [epsilon]\n"
                 "Epsilon's rationale — ¡con acentos!\n")


def project():
    d = tempfile.mkdtemp(prefix="mcp-queue-moves-")
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8",
              newline="") as f:
        f.write(QUEUE)
    return d


def call(cwd, tool, arguments):
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": tool, "arguments": arguments}},
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


def queue_text(d):
    with open(os.path.join(d, "QUEUE.md"), "rb") as f:
        return f.read().decode("utf-8")


def order_of(text, section="## Processed"):
    out = []
    inside = False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line.strip() == section
            continue
        if not inside:
            continue
        if line.strip() == MARKER:
            out.append(MARKER)
        elif line.startswith("#### "):
            out.append(line.rstrip().rsplit("[", 1)[1].rstrip("]"))
    return out


def refused(tool, name, arguments, expect):
    d = project()
    before = queue_text(d)
    text = call(d, tool, arguments)
    check("%s refuses: %s" % (tool, name),
          text.startswith("Refused") and expect in text, repr(text))
    check("%s refusal wrote nothing: %s" % (tool, name),
          queue_text(d) == before)
    shutil.rmtree(d, ignore_errors=True)


# --- queue_move: door refusals ----------------------------------------------
refused("queue_move", "a dangling slug",
        {"section": "Processed", "slug": "nope", "position": "TOP"},
        "names no entry")
refused("queue_move", "a bad position word",
        {"section": "Processed", "slug": "alpha", "position": "MIDDLE"},
        "position must be one of")
refused("queue_move", "BEFORE with no anchor",
        {"section": "Processed", "slug": "alpha", "position": "BEFORE"},
        "needs an anchor")
refused("queue_move", "an anchor not in the section",
        {"section": "Processed", "slug": "alpha", "position": "AFTER",
         "anchor": "epsilon"}, "names no entry")
refused("queue_move", "a section outside the two",
        {"section": "Held", "slug": "alpha", "position": "TOP"},
        "section must be")
refused("queue_move", "a crossing with no marker placement named",
        {"section": "Processed", "slug": "alpha", "position": "BOTTOM"},
        "across the")
refused("queue_move", "marker_after on a section with no marker",
        {"section": "Unprocessed", "slug": "zeta", "position": "TOP",
         "marker_after": "zeta"}, "has no cleared-to-run marker")

# --- queue_move: the script's own unnamed-crossing refusal comes back --------
d = project()
before = queue_text(d)
text = call(d, "queue_move", {"section": "Processed", "slug": "delta",
                              "position": "AFTER", "anchor": "alpha",
                              "marker_after": "gamma"})
check("queue_move: an unnamed clearing is refused at the door, in the "
      "script's words",
      text.startswith("Refused") and "[gamma]" in text and "CLEAR" in text,
      repr(text))
check("queue_move: the refusal names the one-move-per-item route",
      "one --move per item" in text, repr(text))
check("queue_move: the unnamed-crossing refusal wrote nothing",
      queue_text(d) == before)
shutil.rmtree(d, ignore_errors=True)

# --- the downward sweep is refused at the door too ---------------------------
# ([queue-move-downward-sweep-unguarded]) Naming alpha as the last cleared
# item while beta sits after it would drop beta below the line unnamed.
d = project()
before = queue_text(d)
text = call(d, "queue_move", {"section": "Processed", "slug": "alpha",
                              "position": "TOP", "marker_after": "alpha"})
check("queue_move: an unnamed downward sweep is refused at the door",
      text.startswith("Refused") and "[beta]" in text and "DROP" in text,
      repr(text))
check("queue_move: the downward refusal wrote nothing (byte-identical)",
      queue_text(d) == before)
shutil.rmtree(d, ignore_errors=True)

d = project()
before = queue_text(d)
text = call(d, "queue_move_section", {"slug": "epsilon",
                                      "from_section": "Unprocessed",
                                      "to_section": "Processed",
                                      "position": "AFTER", "anchor": "alpha",
                                      "marker_after": "epsilon"})
check("queue_move_section: an unnamed downward sweep is refused at the door",
      text.startswith("Refused") and "[beta]" in text and "DROP" in text,
      repr(text))
check("queue_move_section: the downward refusal wrote nothing "
      "(byte-identical)", queue_text(d) == before)
shutil.rmtree(d, ignore_errors=True)

# --- queue_move: a named clearing lands, bytes intact -----------------------
d = project()
text = call(d, "queue_move", {"section": "Processed", "slug": "gamma",
                              "position": "AFTER", "anchor": "beta",
                              "marker_after": "gamma"})
after = queue_text(d)
check("queue_move: gamma is cleared, after beta, marker after it",
      order_of(after) == ["alpha", "beta", "gamma", MARKER, "delta"],
      repr(order_of(after)))
check("queue_move: the moved block landed byte-identical, non-ASCII included",
      GAMMA_BLOCK in after and "â€”" not in after and "Ã©" not in after,
      repr(after))
check("queue_move: the untouched block is untouched", ALPHA_BLOCK in after)
check("queue_move: the tool reports the crossing",
      "Moved [gamma]" in text and "crossed the readiness line" in text,
      repr(text))
shutil.rmtree(d, ignore_errors=True)

# --- queue_move: a move that crosses nothing needs no marker ---------------
d = project()
text = call(d, "queue_move", {"section": "Processed", "slug": "beta",
                              "position": "TOP"})
after = queue_text(d)
check("queue_move: a move within the cleared region keeps the marker's place",
      order_of(after) == ["beta", "alpha", MARKER, "gamma", "delta"],
      repr(order_of(after)))
shutil.rmtree(d, ignore_errors=True)

# --- queue_move_section: door refusals --------------------------------------
refused("queue_move_section", "a slug not in the source",
        {"slug": "gamma", "from_section": "Unprocessed",
         "to_section": "Processed"}, "names no entry")
refused("queue_move_section", "the same section twice",
        {"slug": "alpha", "from_section": "Processed",
         "to_section": "Processed"}, "are the same")
refused("queue_move_section", "an anchor not in the destination",
        {"slug": "epsilon", "from_section": "Unprocessed",
         "to_section": "Processed", "position": "AFTER", "anchor": "zeta"},
        "names no entry")
refused("queue_move_section", "a bad position word",
        {"slug": "epsilon", "from_section": "Unprocessed",
         "to_section": "Processed", "position": "SIDEWAYS"},
        "position must be one of")
refused("queue_move_section", "a clearing with no marker placement named",
        {"slug": "epsilon", "from_section": "Unprocessed",
         "to_section": "Processed", "position": "AFTER", "anchor": "alpha"},
        "across the")

# --- queue_move_section: the script's own unnamed-crossing refusal ---------
d = project()
before = queue_text(d)
text = call(d, "queue_move_section",
            {"slug": "epsilon", "from_section": "Unprocessed",
             "to_section": "Processed", "position": "BOTTOM",
             "marker_after": "epsilon"})
check("queue_move_section: sweeping the held region into the cleared region "
      "is refused at the door, in the script's words",
      text.startswith("Refused") and "[gamma]" in text
      and "[delta]" in text and "CLEAR" in text, repr(text))
check("queue_move_section: that refusal wrote nothing", queue_text(d) == before)
shutil.rmtree(d, ignore_errors=True)

# --- queue_move_section: the keep-move, cleared in one call -----------------
d = project()
text = call(d, "queue_move_section",
            {"slug": "epsilon", "from_section": "Unprocessed",
             "to_section": "Processed", "position": "AFTER", "anchor": "beta",
             "marker_after": "epsilon"})
after = queue_text(d)
check("queue_move_section: epsilon is kept and cleared, marker after it",
      order_of(after) == ["alpha", "beta", "epsilon", MARKER, "gamma", "delta"],
      repr(order_of(after)))
check("queue_move_section: epsilon left Unprocessed",
      order_of(after, "## Unprocessed") == ["zeta"],
      repr(order_of(after, "## Unprocessed")))
check("queue_move_section: the moved block landed byte-identical, "
      "non-ASCII included",
      EPSILON_BLOCK in after and "Â¡" not in after, repr(after))
check("queue_move_section: the tool reports the move and the side",
      "Moved [epsilon]" in text and "ABOVE" in text, repr(text))
shutil.rmtree(d, ignore_errors=True)

# --- queue_move_section: the default lands below the line, no marker needed -
d = project()
text = call(d, "queue_move_section",
            {"slug": "zeta", "from_section": "Unprocessed",
             "to_section": "Processed"})
after = queue_text(d)
check("queue_move_section: the default bottom lands below the marker",
      order_of(after) == ["alpha", "beta", MARKER, "gamma", "delta", "zeta"],
      repr(order_of(after)))
check("queue_move_section: the report says it is NOT cleared",
      "BELOW" in text, repr(text))
shutil.rmtree(d, ignore_errors=True)

# --- queue_delete -----------------------------------------------------------
refused("queue_delete", "a dangling slug",
        {"slug": "nope", "section": "Processed"}, "names no entry")
refused("queue_delete", "a slug in the other section",
        {"slug": "epsilon", "section": "Processed"}, "names no entry")
refused("queue_delete", "a section outside the two",
        {"slug": "alpha", "section": "Done"}, "section must be")

d = project()
text = call(d, "queue_delete", {"slug": "beta", "section": "Processed"})
after = queue_text(d)
check("queue_delete: the block is gone",
      order_of(after) == ["alpha", MARKER, "gamma", "delta"],
      repr(order_of(after)))
check("queue_delete: deleting the marker's anchor re-anchors it above",
      after.index("[alpha]") < after.index(MARKER) < after.index("[gamma]"))
check("queue_delete: the blocker note comes back through the tool",
      "Deleted [beta]" in text and "name [beta] as their blocker" in text
      and "[gamma]" in text, repr(text))
check("queue_delete: the other blocks are untouched",
      ALPHA_BLOCK in after and GAMMA_BLOCK in after and EPSILON_BLOCK in after)
shutil.rmtree(d, ignore_errors=True)

# --- the three tools are advertised -----------------------------------------
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
check("tools/list advertises the three moves",
      all(n in names for n in ("queue_move", "queue_move_section",
                                "queue_delete")), repr(names))
shutil.rmtree(d, ignore_errors=True)

print()
if failures:
    print("%d failure(s):" % len(failures))
    for name in failures:
        print("  " + name)
    sys.exit(1)
print("all cases passed")
