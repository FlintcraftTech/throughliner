#!/usr/bin/env python3
"""Tests for the no-skill session's door: one approval is enough.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_user_prompt_submit_skill_state.py

Why this exists ([safety-check-freeform-double-ask]): in a chat opened with
no Throughliner skill, the user approved a small fix and the safety check
refused the edit anyway, because a scope file opened its paths only after one
refusal. The prompt hook now records whether any prompt of the session typed
a Throughliner command, and the safety check admits a scope-file path with no
prior refusal where it did not. A session that typed one keeps the
refuse-once door, and so does a session the prompt hook left no record for.

Both hooks are driven directly as subprocesses, the prompt hook first so the
record the safety check reads is the one the hook really writes.
"""

import json
import os
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
PROMPT_HOOK = os.path.join(PLUGIN, "hooks", "user_prompt_submit.py")
SAFETY_HOOK = os.path.join(PLUGIN, "hooks", "pre_tool_use.py")
SERVER = os.path.join(PLUGIN, "mcp", "server.py")

failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        failures.append(name)


def project(scope_for=None, paths=("app/page.md",)):
    d = tempfile.mkdtemp(prefix="skill-state-")
    for name in ("SPEC.md", "QUEUE.md"):
        with open(os.path.join(d, name), "w", encoding="utf-8") as f:
            f.write("# %s\n\n## Processed\n\n## Unprocessed\n" % name)
    if scope_for:
        with open(os.path.join(d, "_freeform-%s.md" % scope_for), "w",
                  encoding="utf-8") as f:
            f.write("# Freeform scope\n\nFiles:\n"
                    + "".join("- %s\n" % p for p in paths))
    return d


def _env():
    env = dict(os.environ)
    env.pop("CLAUDE_PROJECT_DIR", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def say(root, session, prompt):
    payload = {"hook_event_name": "UserPromptSubmit", "session_id": session,
               "cwd": root, "prompt": prompt}
    proc = subprocess.run([sys.executable, PROMPT_HOOK], input=json.dumps(payload),
                          capture_output=True, text=True, encoding="utf-8",
                          cwd=root, env=_env())
    return proc.returncode


def state(root, session):
    path = os.path.join(root, ".throughliner", "session-skill-%s.txt" % session)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def edit(root, session, relpath):
    payload = {"cwd": root, "tool_name": "Edit", "session_id": session,
               "tool_input": {"file_path": os.path.join(root, *relpath.split("/"))}}
    proc = subprocess.run([sys.executable, SAFETY_HOOK], input=json.dumps(payload),
                          capture_output=True, text=True, encoding="utf-8",
                          env=_env())
    if not proc.stdout.strip():
        return "allow", ""
    hso = json.loads(proc.stdout).get("hookSpecificOutput") or {}
    return hso.get("permissionDecision", "allow"), hso.get("permissionDecisionReason", "")


print("test_user_prompt_submit_skill_state")

# --- the record the prompt hook keeps ---------------------------------------
d = project()
check("the hook exits 0 on an ordinary message", say(d, "s", "fix the header") == 0)
check("the first prompt of a session records none", state(d, "s") == "none",
      repr(state(d, "s")))
say(d, "s", "/throughliner:plan")
check("a typed Throughliner command is recorded", state(d, "s") == "plan",
      repr(state(d, "s")))
say(d, "s", "thanks, carry on")
check("the record never goes back to none", state(d, "s") == "plan",
      repr(state(d, "s")))
say(d, "bare", "/process")
check("a bare method command counts", state(d, "bare") == "process",
      repr(state(d, "bare")))
say(d, "other", "/colouring-page a fox in a scarf")
check("a project's own skill is not a Throughliner skill",
      state(d, "other") == "none", repr(state(d, "other")))
say(d, "plug", "/another-plugin:build now")
check("another plugin's same-named skill is not a Throughliner skill",
      state(d, "plug") == "none", repr(state(d, "plug")))

# --- no skill, a scope file naming the path: admitted cold -------------------
d = project(scope_for="free")
say(d, "free", "the header link is broken, go ahead and fix it")
decision, why = edit(d, "free", "app/page.md")
check("no skill and a scope file naming the path: admitted with no prior refusal",
      decision == "allow", why[:300])
with open(os.path.join(d, ".throughliner", "pre-tool-use.log"), encoding="utf-8") as f:
    log = f.read()
check("the decision is logged under its own branch",
      "freeform scope file: no skill invoked" in log, log[-400:])

# --- a session running a project's own skill counts as no skill --------------
d = project(scope_for="own")
say(d, "own", "/colouring-page a fox in a scarf")
decision, why = edit(d, "own", "app/page.md")
check("a project's own skill running: the scope-file path is admitted cold",
      decision == "allow", why[:300])

# --- a Throughliner skill invoked: refused once, as before -------------------
d = project(scope_for="planning")
say(d, "planning", "/throughliner:plan")
decision, why = edit(d, "planning", "app/page.md")
check("a skill invoked: the listed path is refused the first time",
      decision == "deny" and "door opens only" in why, why[:300])
check("and its message keeps the queue instruction",
      "Add this to the queue as a piece of work instead" in why, why[:300])
decision, why = edit(d, "planning", "app/page.md")
check("and admitted after that one refusal", decision == "allow", why[:300])

# --- no record at all (the prompt hook did not run): refused once ------------
d = project(scope_for="norecord")
decision, why = edit(d, "norecord", "app/page.md")
check("no record from the prompt hook: the door keeps its refuse-once behaviour",
      decision == "deny" and "door opens only" in why, why[:300])

# --- no skill and no scope file: refused, with the no-skill wording ----------
d = project()
say(d, "bare-free", "go ahead and fix the header")
decision, why = edit(d, "bare-free", "app/page.md")
check("no skill and no scope file: refused", decision == "deny", why[:300])
check("the refusal says the change is made here, with no second ask",
      "is made here" in why and "no second ask" in why
      and "_freeform-bare-free.md" in why, why[:600])
check("the refusal does not send the change to the queue",
      "Add this to the queue as a piece of work instead" not in why, why[:600])
decision, why = edit(d, "bare-free", "_freeform-bare-free.md")
check("the scope file itself is writable", decision == "allow", why[:300])

# --- no skill, a scope file that names another path: refused -----------------
d = project(scope_for="narrow", paths=("app/other.md",))
say(d, "narrow", "go ahead")
decision, why = edit(d, "narrow", "app/page.md")
check("no skill and a path the scope file does not name: refused",
      decision == "deny" and "nothing in its Files: list matched" in why, why[:600])

# --- the state server's scope tool reads the same record ---------------------
def build_open(root, session):
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
            "name": "build_open",
            "arguments": {"session_id": session, "kind": "freeform",
                          "files": ["app/page.md"]}}},
    ]
    env = _env()
    env["THROUGHLINER_PROJECT_ROOT"] = root
    payload = "".join(json.dumps(r) + "\n" for r in requests).encode("utf-8")
    proc = subprocess.run([sys.executable, SERVER], input=payload, cwd=root,
                          capture_output=True, env=env, timeout=60)
    for line in proc.stdout.decode("utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            if r.get("id") == 2:
                return r.get("result", {}).get("content", [{}])[0].get("text", "")
    return ""


d = project()
say(d, "tool-free", "go ahead and fix the header")
text = build_open(d, "tool-free")
check("build_open writes a no-skill session's scope file with no prior refusal",
      os.path.isfile(os.path.join(d, "_freeform-tool-free.md")), text[:300])
say(d, "tool-plan", "/throughliner:process")
text = build_open(d, "tool-plan")
check("build_open still refuses a skill session that was never refused",
      text.startswith("Refused") and not os.path.isfile(
          os.path.join(d, "_freeform-tool-plan.md")), text[:300])

print()
if failures:
    print("%d check(s) FAILED: %s" % (len(failures), "; ".join(failures)))
    sys.exit(1)
print("all checks passed")
