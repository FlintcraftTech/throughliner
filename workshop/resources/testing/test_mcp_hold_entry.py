#!/usr/bin/env python3
"""Regression tests for mcp/server.py's hold_entry tool.

Host-only dev artifact — not shipped in the plugin package.

Run:  py workshop/resources/testing/test_mcp_hold_entry.py

No test framework, matching the suites alongside it: this project has no test
runner, and `python` on the author's machine resolves to an application's
bundled interpreter that has no pytest.

Why this exists ([mcp-hold-entry-tool]): an unbracketed `Blocked by:` slug once
made a consumer's item permanently unliftable with nothing reporting it. The
tool composes the line itself and refuses at the door what the lint would only
flag afterwards. The server is driven end to end as a subprocess over raw
UTF-8 bytes, as the file_capture suite does, so transport fidelity is pinned
alongside the tool's own logic.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
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
Alpha's rationale — an em-dash and a résumé, which must survive untouched.

#### Beta — another cleared build [beta]
Beta's rationale.

--- Cleared to run above this line ---

#### Gamma — a held build [gamma]
Gamma's rationale.
Blocked by: [beta]

## Unprocessed

#### Delta — a capture [delta]
Delta's rationale.

#### Epsilon — a capture with a date [epsilon]
Epsilon's rationale.
Not before: 2031-01-01
"""


def project():
    d = tempfile.mkdtemp(prefix="mcp-hold-entry-")
    # newline="" keeps the fixture's LF endings on Windows, so the byte-level
    # assertions below read the file as written.
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8",
              newline="") as f:
        f.write(QUEUE)
    return d


def call(cwd, arguments):
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": "hold_entry", "arguments": arguments}},
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


def refused(name, arguments, expect):
    d = project()
    before = queue_text(d)
    text = call(d, arguments)
    check("refuses: " + name, text.startswith("Refused") and expect in text,
          repr(text))
    check("refusal wrote nothing: " + name, queue_text(d) == before)
    shutil.rmtree(d, ignore_errors=True)


# --- one case per refusal --------------------------------------------------
refused("a slug naming no entry", {"slug": "nope", "blocked_by": ["alpha"]},
        "names no entry")
refused("both fields", {"slug": "delta", "blocked_by": ["alpha"],
                        "not_before": "2031-01-01"}, "both blocked_by")
refused("neither field", {"slug": "delta"}, "neither")
refused("a blocker that is not an entry", {"slug": "delta",
                                          "blocked_by": ["zeta"]},
        "not an entry")
refused("the entry naming itself", {"slug": "delta", "blocked_by": ["delta"]},
        "names the entry itself")
refused("an unreal date", {"slug": "delta", "not_before": "2031-13-40"},
        "not a real date")
refused("a spent date", {"slug": "delta", "not_before": "2020-01-01"},
        "already past")

# --- a capture gains the field and stays put ---------------------------------
d = project()
text = call(d, {"slug": "delta", "blocked_by": ["alpha", "gamma"]})
after = queue_text(d)
check("a capture gains a Blocked by: line with bracketed slugs",
      "Delta's rationale.\nBlocked by: [alpha], [gamma]\n" in after, repr(after))
check("the tool reports the line it wrote", "Blocked by: [alpha], [gamma]" in text,
      repr(text))
check("a capture stays where it is", "bow-out" in text and
      after.index("[delta]") < after.index("[epsilon]"), repr(text))
check("non-ASCII text elsewhere is untouched",
      "an em-dash and a résumé" in after and "â€”" not in after)
shutil.rmtree(d, ignore_errors=True)

# --- until_built: a capture's line ends `until built`; a work item is refused --
d = project()
text = call(d, {"slug": "delta", "blocked_by": ["alpha"], "until_built": True})
after = queue_text(d)
check("until_built on a capture writes the qualified line",
      "Delta's rationale.\nBlocked by: [alpha] until built\n" in after, repr(after))
check("the tool reports the qualified line", "until built" in text, repr(text))
shutil.rmtree(d, ignore_errors=True)
refused("until_built on a work item",
        {"slug": "gamma", "blocked_by": ["alpha"], "until_built": True},
        "adds nothing")
refused("until_built without blocked_by",
        {"slug": "delta", "not_before": "2031-01-01", "until_built": True},
        "without blocked_by")

# --- replace, not double: date kind over date kind ---------------------------
d = project()
call(d, {"slug": "epsilon", "not_before": "2032-06-01"})
after = queue_text(d)
check("a Not before: line is replaced rather than doubled",
      after.count("Not before:") == 1 and "Not before: 2032-06-01" in after,
      repr(after))
shutil.rmtree(d, ignore_errors=True)

# --- replace, not double: blocker kind over date kind ------------------------
d = project()
call(d, {"slug": "epsilon", "blocked_by": ["delta"]})
after = queue_text(d)
check("a Blocked by: replaces an existing Not before: rather than adding to it",
      "Not before:" not in after.split("[epsilon]")[1] and
      "Blocked by: [delta]" in after, repr(after))
shutil.rmtree(d, ignore_errors=True)

# --- replace, not double: blocker over blocker on a held item ----------------
d = project()
text = call(d, {"slug": "gamma", "blocked_by": ["alpha"]})
after = queue_text(d)
gamma_block = after.split("[gamma]")[1].split("## Unprocessed")[0]
check("a held item's existing Blocked by: is replaced",
      gamma_block.count("Blocked by:") == 1 and "Blocked by: [alpha]" in gamma_block,
      repr(gamma_block))
check("a held item is not moved", "below the line where it already sat" in text,
      repr(text))
shutil.rmtree(d, ignore_errors=True)

# --- a cleared item crosses the line to the top of the held region ----------
d = project()
text = call(d, {"slug": "alpha", "not_before": "2031-01-01"})
after = queue_text(d)
marker = after.index("--- Cleared to run above this line ---")
check("the cleared item now sits below the marker",
      after.index("[alpha]") > marker, repr(after))
check("it sits at the top of the held region",
      after.index("[alpha]") < after.index("[gamma]"), repr(after))
check("beta is still cleared", after.index("[beta]") < marker)
check("the hold line landed on the moved item",
      "Alpha's rationale — an em-dash and a résumé, which must survive "
      "untouched.\nNot before: 2031-01-01\n" in after, repr(after))
check("the tool reports the crossing", "crossed the line" in text, repr(text))
shutil.rmtree(d, ignore_errors=True)

# --- the moved item was the marker's anchor: the marker keeps its place ------
d = project()
call(d, {"slug": "beta", "blocked_by": ["gamma"]})
after = queue_text(d)
marker = after.index("--- Cleared to run above this line ---")
check("moving the marker's anchor leaves alpha cleared and beta held",
      after.index("[alpha]") < marker < after.index("[beta]") < after.index("[gamma]"),
      repr(after))
shutil.rmtree(d, ignore_errors=True)

print()
if failures:
    print("%d failure(s):" % len(failures))
    for name in failures:
        print("  " + name)
    sys.exit(1)
print("all cases passed")
