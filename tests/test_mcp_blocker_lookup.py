#!/usr/bin/env python3
"""Tests for cross-project holds: the blocker_lookup tool, the hold written
with a project suffix, and every reader of a suffixed `Blocked by:` line.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_mcp_blocker_lookup.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

Why this exists ([cross-project-holds-in-task-marks]): a dependency between
two projects had no notation and no reader. A hold may now name an item in
another project's queue, written `Blocked by: [slug] in <project>`, and one
state-server tool says where that item sits. The fixture is a two-project
vault: `alpha` is the project the server runs in, `beta` holds the blockers.
The server is driven as a subprocess over raw UTF-8 bytes, as the hold_entry
suite does; the readers are imported and called.
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
PLUGIN = os.path.join(ROOT, "plugin", "throughliner")
SERVER = os.path.join(PLUGIN, "mcp", "server.py")

failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        failures.append(name)


def load(name, *parts):
    spec = importlib.util.spec_from_file_location(name, os.path.join(PLUGIN, *parts))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ALPHA_QUEUE = """# QUEUE

## Processed

#### Alpha one — a cleared build [alpha-one]
Alpha one's rationale.

--- Cleared to run above this line ---

## Unprocessed

#### Alpha capture [alpha-capture]
A capture's rationale.
"""

BETA_QUEUE = """# QUEUE

## Processed

#### Beta cleared — a build ready to run [beta-cleared]
Beta cleared's rationale.

#### [user] Beta step — a task of the user's [beta-step]
- [x] Beta step — a task of the user's (beta) 🆔 beta-step #user
The step's rationale.

--- Cleared to run above this line ---

#### Beta held — waits on a date [beta-held]
Beta held's rationale.
Not before: 2031-01-01

## Unprocessed

#### Beta idea — not yet kept [beta-idea]
An idea's rationale.
"""

BETA_BUILD_RECORD = """---
summary: beta-built built and confirmed
---
# abc1234 — beta-built built

**Files touched:** `thing.md`
"""


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def vault():
    """A vault holding two projects, alpha and beta; returns (vault, alpha)."""
    d = tempfile.mkdtemp(prefix="blocker-lookup-")
    os.makedirs(os.path.join(d, ".obsidian"))
    alpha = os.path.join(d, "alpha")
    beta = os.path.join(d, "beta")
    write(os.path.join(alpha, "QUEUE.md"), ALPHA_QUEUE)
    write(os.path.join(alpha, "SPEC.md"), "# SPEC\n")
    write(os.path.join(beta, "QUEUE.md"), BETA_QUEUE)
    write(os.path.join(beta, "SPEC.md"), "# SPEC\n")
    write(os.path.join(beta, "LOG", "2026-01-01-beta-built.md"), BETA_BUILD_RECORD)
    write(os.path.join(beta, "LOG", "2026-01-02-beta-walked.md"),
          "# abc1234 — user step\n\nOutcome: done\n")
    return d, alpha


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


def queue_text(folder):
    with open(os.path.join(folder, "QUEUE.md"), "rb") as f:
        return f.read().decode("utf-8")


# --- 1. the tool: found cleared, held, captured, ticked, closed into LOG,
#        in this project, and not found -------------------------------------
print("blocker_lookup")
d, alpha = vault()
text = call(alpha, "blocker_lookup", {"slugs": [
    "beta-cleared", "beta-held", "beta-idea", "beta-step", "beta-built",
    "beta-walked", "alpha-one", "no-such-slug"]})
lines = text.splitlines()


def line_for(slug):
    return next((l for l in lines if l.startswith("[%s]" % slug)), "")


check("a cleared item in another project is found, with its project and heading",
      "beta: Processed, cleared to run" in line_for("beta-cleared")
      and "Beta cleared" in line_for("beta-cleared"), text)
check("a held item is returned with its hold line",
      "beta: Processed, held (Not before: 2031-01-01)" in line_for("beta-held"), text)
check("a capture is returned as captured",
      "beta: Unprocessed, captured" in line_for("beta-idea"), text)
check("a ticked task line is said",
      "its task line ticked" in line_for("beta-step"), text)
check("an item closed into LOG is returned with the record's kind and date",
      "no longer in the queue" in line_for("beta-built")
      and "being built" in line_for("beta-built")
      and "2026-01-01" in line_for("beta-built"), text)
check("a step of the user's recorded done is returned as done, with its date",
      "no longer in the queue" in line_for("beta-walked")
      and "the step being done" in line_for("beta-walked")
      and "2026-01-02" in line_for("beta-walked"), text)
check("an item in this project is returned as this project's",
      "alpha (this project): Processed, cleared to run" in line_for("alpha-one"), text)
check("a slug found nowhere is returned as not found, not refused",
      "not found" in line_for("no-such-slug") and "Refused" not in text, text)
check("no slugs at all is refused",
      call(alpha, "blocker_lookup", {}).startswith("Refused"))

# --- 2. hold_entry: a blocker in another project's queue is written with
#        the suffix, and one found nowhere is still refused --------------------
print("hold_entry")
before = queue_text(alpha)
text = call(alpha, "hold_entry",
            {"slug": "alpha-one", "blocked_by": ["beta-cleared"]})
after = queue_text(alpha)
check("the hold is accepted and carries the project suffix",
      "Blocked by: [beta-cleared] in beta\n" in after, text + "\n" + after)
check("the answer says where the other project's item sits",
      "another project's queue" in text and "beta: Processed, cleared to run" in text,
      text)
check("the held item moved below the cleared-to-run line",
      after.index("--- Cleared to run") < after.index("#### Alpha one"), after)
check("the derived task line carries the bare slug after the block mark",
      "⛔ beta-cleared" in after and "⛔ beta-cleared in" not in after, after)

text = call(alpha, "hold_entry",
            {"slug": "alpha-capture", "blocked_by": ["no-such-slug"]})
check("a blocker found in no project is refused, and nothing more is written",
      text.startswith("Refused") and queue_text(alpha) == after, text)

text = call(alpha, "hold_entry",
            {"slug": "alpha-capture", "blocked_by": ["alpha-one", "beta-idea"]})
check("a mixed hold suffixes only the blocker that lives elsewhere",
      "Blocked by: [alpha-one], [beta-idea] in beta\n" in queue_text(alpha),
      text + "\n" + queue_text(alpha))
held_queue = queue_text(alpha)

# --- 3. the lint reads the suffixed line without calling the slug missing ---
print("queue lint")
lint = load("post_tool_use", "hooks", "post_tool_use.py").lint
warnings = lint(held_queue)
check("the lint does not report the other project's slug as not in the queue",
      not any("beta-cleared" in w or "beta-idea" in w for w in warnings),
      "\n".join(warnings))
check("the lint does not call the suffixed item unheld",
      not any("with no 'Blocked by: [slug]' line" in w for w in warnings),
      "\n".join(warnings))
plain = held_queue.replace("[beta-cleared] in beta", "[beta-cleared]")
check("the same slug with no suffix is still reported as not in the queue",
      any("beta-cleared" in w and "not in the queue" in w for w in lint(plain)),
      "\n".join(lint(plain)))

# --- 4. the digest reads the slug, keeps the hold, and prints where it is ---
print("queue digest")
digest = load("queue_digest", "scripts", "queue_digest.py")
items = {i["slug"]: i for i in digest.parse(os.path.join(alpha, "QUEUE.md"))}
check("the digest reads the suffixed slug as a blocker",
      items["alpha-one"]["blocked_by"] == ["beta-cleared"], repr(items["alpha-one"]))
check("and records the project it lives in",
      items["alpha-one"]["blocked_elsewhere"] == {"beta-cleared": "beta"},
      repr(items["alpha-one"]["blocked_elsewhere"]))
check("a mixed line keeps both blockers and marks only the outside one",
      items["alpha-capture"]["blocked_by"] == ["alpha-one", "beta-idea"]
      and items["alpha-capture"]["blocked_elsewhere"] == {"beta-idea": "beta"},
      repr(items["alpha-capture"]))
proc = subprocess.run(
    [sys.executable, os.path.join(PLUGIN, "scripts", "queue_digest.py"),
     os.path.join(alpha, "QUEUE.md")],
    capture_output=True, encoding="utf-8", errors="replace", cwd=alpha)
check("the digest prints the blocker as in another project, never as ABSENT",
      "[beta-cleared] -> in beta, another project's queue" in proc.stdout
      and "[beta-cleared] -> ABSENT" not in proc.stdout, proc.stdout + proc.stderr)

# --- 5. the session opening's dependency facts leave it out of the pairs
#        resolved against this queue ------------------------------------------
print("session-start facts")
hook = load("session_start", "hooks", "session_start.py")
facts = hook._queue_dependency_facts(os.path.join(alpha, "QUEUE.md"))
(cleared, held, _in_unprocessed, _waiting, dead, _dh, _dp, _to_plan) = facts
check("the held item is still counted as held", held == 1 and cleared == 0,
      repr(facts))
check("its outside blocker is not reported as a blocker in neither section",
      dead == [], repr(dead))

# --- 6. the mover: deleting a local slug of the same name does not list the
#        item waiting on another project's slug as a dependent -----------------
print("mover")
write(os.path.join(alpha, "QUEUE.md"),
      held_queue.replace("#### Alpha capture [alpha-capture]",
                         "#### Beta cleared, a local namesake [beta-cleared]\n"
                         "A namesake's rationale.\n\n"
                         "#### Alpha capture [alpha-capture]"))
proc = subprocess.run(
    [sys.executable, os.path.join(PLUGIN, "scripts", "reorder_queue.py"),
     os.path.join(alpha, "QUEUE.md"), "--delete", "beta-cleared", "Unprocessed"],
    capture_output=True, encoding="utf-8", errors="replace", cwd=alpha)
check("the delete succeeds", proc.returncode == 0, proc.stderr)
check("no held item is named as waiting on the deleted local slug",
      "name [beta-cleared] as their blocker" not in proc.stderr, proc.stderr)
check("the suffixed hold line is carried byte for byte",
      "Blocked by: [beta-cleared] in beta\n" in queue_text(alpha), queue_text(alpha))

shutil.rmtree(d, ignore_errors=True)

# --- 7. [hold-until-goal-reached]: a slug that is a goal line in a SPEC is
#        returned as a goal with its state, a hold accepts it, and the lint
#        and the digest do not call it missing -------------------------------
print("goals")
d, alpha = vault()
write(os.path.join(alpha, "SPEC.md"), "# SPEC\n\n## Goals\n\n"
      "- [ ] Alpha ships, reached when a stranger installs it (alpha) "
      "🆔 alpha-ships #goal\n"
      "- [x] Alpha exists, reached when the folder exists (alpha) "
      "🆔 alpha-exists #goal\n"
      "- [ ] A step of mine (alpha) 🆔 alpha-not-a-goal #user\n")
write(os.path.join(d, "beta", "SPEC.md"), "# SPEC\n\n## Goals\n\n"
      "- [ ] Beta pays for itself, reached when a month's income covers it "
      "(beta) 🆔 beta-pays #goal\n"
      "- [ ] A goal sharing a queue slug (beta) 🆔 beta-cleared #goal\n")
text = call(alpha, "blocker_lookup", {"slugs": [
    "alpha-ships", "alpha-exists", "beta-pays", "alpha-not-a-goal",
    "beta-cleared"]})
lines = text.splitlines()
check("an unticked goal in this project's SPEC is returned as a goal, not reached",
      "alpha (this project): a goal, not reached" in line_for("alpha-ships")
      and "Alpha ships, reached when a stranger installs it" in line_for("alpha-ships"),
      text)
check("a ticked goal is returned as a goal, reached",
      "alpha (this project): a goal, reached" in line_for("alpha-exists"), text)
check("a goal in another project under the vault is found with its project",
      "beta: a goal, not reached" in line_for("beta-pays"), text)
check("a checkbox line with no #goal tag is not a goal",
      "not found" in line_for("alpha-not-a-goal"), text)
check("a queue entry of the same slug wins over a goal",
      "beta: Processed, cleared to run" in line_for("beta-cleared")
      and "a goal" not in line_for("beta-cleared"), text)

text = call(alpha, "hold_entry",
            {"slug": "alpha-one", "blocked_by": ["alpha-ships"]})
check("hold_entry accepts a goal's slug from this project's SPEC, written bare",
      "Blocked by: [alpha-ships]\n" in queue_text(alpha), text + "\n" + queue_text(alpha))
text = call(alpha, "hold_entry",
            {"slug": "alpha-capture", "blocked_by": ["beta-pays"]})
check("hold_entry accepts another project's goal, with the project suffix",
      "Blocked by: [beta-pays] in beta\n" in queue_text(alpha),
      text + "\n" + queue_text(alpha))

queue_file = os.path.join(alpha, "QUEUE.md")
post = load("post_tool_use", "hooks", "post_tool_use.py")
goal_slugs = post._spec_goal_slugs(alpha)
check("the lint reads this project's goal slugs from SPEC",
      goal_slugs == {"alpha-ships", "alpha-exists"}, repr(goal_slugs))
lint_out = post.lint(queue_text(alpha), in_flight=goal_slugs)
check("the lint does not report a goal's slug as not in the queue",
      not any("[alpha-ships], which is not in the queue" in w for w in lint_out),
      "\n".join(lint_out))
lint_bare = post.lint(queue_text(alpha))
check("without the SPEC read the same slug is reported, so the read is what clears it",
      any("[alpha-ships], which is not in the queue" in w for w in lint_bare),
      "\n".join(lint_bare))
proc = subprocess.run([sys.executable, os.path.join(PLUGIN, "scripts",
                       "queue_digest.py"), queue_file],
                      capture_output=True, encoding="utf-8", errors="replace")
check("the digest prints the blocker as a goal in SPEC, never as ABSENT",
      "[alpha-ships] -> a goal in SPEC, not reached" in proc.stdout
      and "[alpha-ships] -> ABSENT" not in proc.stdout, proc.stdout + proc.stderr)
facts = hook._queue_dependency_facts(queue_file)
check("the opening's dependency facts do not call a goal a blocker in neither section",
      not any(b == "alpha-ships" for _h, b in facts[4]), repr(facts[4]))
shutil.rmtree(d, ignore_errors=True)

print()
if failures:
    print("%d failure(s):" % len(failures))
    for name in failures:
        print("  " + name)
    sys.exit(1)
print("all cases passed")
