#!/usr/bin/env python3
"""Regression tests for mcp/server.py's cycle_define tool.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_mcp_cycle_define.py

No test framework, matching the suites alongside it: this project has no test
runner, and `python` on the author's machine resolves to an application's
bundled interpreter that has no pytest.

Why this exists ([mcp-cycle-define-tool]): the session-start hook reads a
cycles definition with fixed field patterns, so a misspelt field or a malformed
slug drops the definition from the opening's cycles line with nothing reporting
why. The tool composes the block from fields and refuses at the door. The
server is driven end to end as a subprocess over raw UTF-8 bytes, as the
hold_entry suite does, and every block it writes is read back with the hook's
own parser — the same read the opening makes.
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER = os.path.join(ROOT, "plugin", "throughliner", "mcp", "server.py")
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "session_start.py")

failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        failures.append(name)


def load_hook():
    spec = importlib.util.spec_from_file_location("tl_session_start", HOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


hook = load_hook()

EXISTING = """# CYCLES

A preamble the tool must leave alone.

## Rezip [rezip]

**Artifact:** the installed host.

**Trigger:** the user says "rezip".

**Writes:** `plugin/rezip-archive/`

**Steps of one turn.** Each step fires on the one before it and is Claude's
unless the step says otherwise.
1. Bump the suffix.
2. Install.
"""


def project(with_doc=True):
    d = tempfile.mkdtemp(prefix="mcp-cycle-define-")
    # A queue so the server starts; the tool itself never reads it.
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8",
              newline="") as f:
        f.write("# QUEUE\n\n## Processed\n\n## Unprocessed\n")
    if with_doc:
        with open(os.path.join(d, "CYCLES.md"), "w", encoding="utf-8",
                  newline="") as f:
            f.write(EXISTING)
    return d


def call(cwd, arguments):
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": "cycle_define", "arguments": arguments}},
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


def doc_text(d):
    path = os.path.join(d, "CYCLES.md")
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as f:
        return f.read().decode("utf-8")


def entries(d):
    return {e["slug"]: e for e in (hook._parse_cycles_doc(d) or [])}


CYCLE = {
    "heading": "Weekly release — the maintenance cycle",
    "slug": "weekly-release",
    "artifact": "the GitHub release of the plugin — pruned before it goes",
    "cadence": "weekly on Wednesday, declared by the user 2026-08-22",
    "due_rule": "time-based — the cadence above; the turn's record closes it",
    "observable": "the published date of the latest GitHub release",
    "anchor": "Wednesday morning",
    "chain": [{"slug": "sweep", "lead_days": 2},
              {"slug": "rezip", "lead_days": 1},
              {"slug": "ship", "lead_days": 0}],
    "writes": ["plugin/throughliner.zip", "README.md"],
    "material": "the rezip readmes, one per build.",
    "steps": ["Check the branch is main.", "Cut the release branch — résumé "
              "the picks.", "Publish."],
}

CHECKLIST = {
    "heading": "Maintenance sweep",
    "slug": "sweep",
    "artifact": "the plugin's own documents",
    "trigger": "the user says \"sweep\", or the release cycle reaches it",
    "steps": ["Measure the size criterion.", "One eviction pass."],
}

SHIP = {
    "heading": "Release",
    "slug": "ship",
    "artifact": "the published pre-release",
    "trigger": "the user says \"release\"",
    "steps": ["Bump the version.", "Attach the zip."],
}


def refused(name, arguments, expect, with_doc=True):
    d = project(with_doc)
    before = doc_text(d)
    text = call(d, arguments)
    check("refuses: " + name, text.startswith("Refused") and expect in text,
          repr(text))
    check("refusal wrote nothing: " + name, doc_text(d) == before)
    shutil.rmtree(d, ignore_errors=True)


# --- a checklist, parsed back as a checklist --------------------------------
d = project()
text = call(d, CHECKLIST)
got = entries(d)
check("a checklist appends and the tool reports it as a checklist",
      "Appended to CYCLES.md" in text and "as a checklist" in text, repr(text))
check("the hook's parser reads the checklist back",
      "sweep" in got and hook._is_checklist(got["sweep"]), repr(got.get("sweep")))
check("the checklist carries its trigger and no cadence",
      got.get("sweep", {}).get("trigger", "").startswith("the user says")
      and got.get("sweep", {}).get("cadence") is None, repr(got.get("sweep")))
check("the existing definition and preamble are untouched",
      doc_text(d).startswith(EXISTING) and "rezip" in got)
check("the doc's checklists_facts lists both",
      sorted(s for s, _, _ in hook.checklists_facts(d)) == ["rezip", "sweep"])

# --- a cycle chaining the checklists, every field read back ------------------
call(d, SHIP)
text = call(d, CYCLE)
got = entries(d)
wr = got.get("weekly-release", {})
check("a cycle appends and the tool reports the chain",
      "as a cycle, chaining 3 checklist(s)" in text, repr(text))
check("slug, cadence, observable and anchor all parse back",
      wr.get("cadence") == CYCLE["cadence"]
      and wr.get("observable") == CYCLE["observable"]
      and wr.get("anchor") == CYCLE["anchor"], repr(wr))
check("the cycle is not a checklist", wr and not hook._is_checklist(wr))
check("the chain parses to the three checklists with their leads",
      hook._parse_chain(wr.get("chain")) == [("sweep", 2), ("rezip", 1),
                                              ("ship", 0)],
      repr(wr.get("chain")))
chains = {c["slug"]: c for c in (hook.cycle_chains(d) or [])}
check("cycle_chains computes a due date for every checklist in the chain",
      "weekly-release" in chains
      and all(due for _, due in chains["weekly-release"]["checklists"]),
      repr(chains))
facts = {s: (cad, obs) for s, _, cad, obs, _ in hook.cycles_facts(d)}
check("cycles_facts lists the cycle and not the checklists",
      set(facts) == {"weekly-release"}, repr(facts))
after = doc_text(d)
check("the block carries Writes as backticked paths",
      "**Writes:** `plugin/throughliner.zip`, `README.md`" in after)
check("the block carries the steps sentence and numbered steps",
      "**Steps of one turn.** Each step fires on the one before it and is "
      "Claude's unless the step says otherwise.\n1. Check the branch is main."
      in after, repr(after[-600:]))
check("a 1-day lead is written singular",
      "2. [rezip] — 1 day before the anchor" in after)
check("an em-dash and a non-ASCII character survive the transport",
      "— pruned before it goes" in after and "résumé" in after
      and "â€”" not in after and "Ã©" not in after)
shutil.rmtree(d, ignore_errors=True)

# --- the doc is created where absent -----------------------------------------
d = project(with_doc=False)
text = call(d, CHECKLIST)
after = doc_text(d)
check("the doc is created with a preamble where none exists",
      after is not None and after.startswith("# CYCLES\n\n")
      and "Created CYCLES.md" in text, repr(text))
check("the created doc parses to the one definition",
      list(entries(d)) == ["sweep"])
shutil.rmtree(d, ignore_errors=True)

# --- one refusal per door check ----------------------------------------------
refused("a malformed slug", dict(CHECKLIST, slug="Bad Slug"), "malformed")
refused("a missing slug", dict(CHECKLIST, slug=""), "slug is missing")
refused("a slug already defined", dict(CHECKLIST, slug="rezip"),
        "already defined")
refused("both cadence and trigger",
        dict(CHECKLIST, cadence="weekly, declared 2026-01-01",
             observable="x"), "both cadence and trigger")
refused("neither cadence nor trigger",
        {k: v for k, v in CHECKLIST.items() if k != "trigger"}, "neither")
refused("a cadence with no observable",
        {"heading": "Posting", "slug": "posting", "artifact": "the channel",
         "cadence": "every three days, declared by the user 2026-08-29",
         "steps": ["Post."]}, "no observable")
refused("a cadence naming no derivation",
        {"heading": "Posting", "slug": "posting", "artifact": "the channel",
         "cadence": "every three days", "observable": "the register",
         "steps": ["Post."]}, "no derivation")
refused("a chain naming an undefined checklist",
        {"heading": "Weekly", "slug": "weekly", "artifact": "x",
         "cadence": "weekly, declared 2026-01-01", "observable": "y",
         "anchor": "Monday",
         "chain": [{"slug": "ghost", "lead_days": 1},
                   {"slug": "rezip", "lead_days": 0}],
         "steps": ["Go."]}, "not defined")
refused("a chain naming the anchor twice",
        {"heading": "Weekly", "slug": "weekly", "artifact": "x",
         "cadence": "weekly, declared 2026-01-01", "observable": "y",
         "anchor": "Monday",
         "chain": [{"slug": "rezip", "lead_days": 0},
                   {"slug": "rezip", "lead_days": 0}],
         "steps": ["Go."]}, "anchor twice")
refused("a chain with no anchor",
        {"heading": "Weekly", "slug": "weekly", "artifact": "x",
         "cadence": "weekly, declared 2026-01-01", "observable": "y",
         "chain": [{"slug": "rezip", "lead_days": 0}],
         "steps": ["Go."]}, "no anchor")
refused("an absolute writes path",
        dict(CHECKLIST, writes=[os.path.abspath(os.sep) + "etc"]),
        "absolute")
refused("a writes path resolving outside the project",
        dict(CHECKLIST, writes=["../elsewhere/file.md"]), "outside the project")
refused("an empty steps list", dict(CHECKLIST, steps=[]), "steps is empty")

print()
if failures:
    print("%d failure(s):" % len(failures))
    for name in failures:
        print("  " + name)
    sys.exit(1)
print("all cases passed")
