#!/usr/bin/env python3
"""Test for hooks/user_prompt_submit.py's FAQ match.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_user_prompt_submit_faq.py

Why this exists ([faq-entry-offered-when-user-asks]): the hook hands Claude
the one FAQ entry a user's question clearly matches, once per entry per chat,
and prints nothing on any other message. The match is by shared words, so the
paraphrases below are the set `MIN_SCORE` is tuned against: each must fire on
the right entry, and the acknowledgements, instructions and questions about
the user's own project must stay silent. It drives the hook as a subprocess
against a temporary adopted project and the real FAQ templates.
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
HOOK = os.path.join(PLUGIN, "hooks", "user_prompt_submit.py")

failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        failures.append(name)


def project(adopted=True):
    d = tempfile.mkdtemp(prefix="ups-faq-")
    if adopted:
        for name in ("QUEUE.md", "SPEC.md"):
            with open(os.path.join(d, name), "w", encoding="utf-8") as f:
                f.write("# %s\n" % name)
    return d


def drive(root, prompt, session="s1", raw=None):
    env = dict(os.environ)
    env["CLAUDE_PLUGIN_ROOT"] = PLUGIN
    env.pop("CLAUDE_PROJECT_DIR", None)
    payload = raw if raw is not None else json.dumps({
        "hook_event_name": "UserPromptSubmit", "session_id": session,
        "cwd": root, "prompt": prompt})
    proc = subprocess.run([sys.executable, HOOK], input=payload,
                          capture_output=True, text=True, encoding="utf-8",
                          cwd=root, env=env)
    return proc.returncode, proc.stdout.strip()


def fired_question(stdout):
    if not stdout:
        return None
    hso = json.loads(stdout)["hookSpecificOutput"]
    assert hso["hookEventName"] == "UserPromptSubmit"
    text = hso["additionalContext"]
    return text.split('may answer this: "', 1)[1].split('". From the installed', 1)[0]


print("test_user_prompt_submit_faq")

PARAPHRASES = [
    ("why did my build stop before the end of the list?",
     "Why did my build run stop before finishing the list?"),
    ("why did my build run stop before finishing the list?",
     "Why did my build run stop before finishing the list?"),
    ("do I need to run a command every time?",
     "Do I have to run a command every time?"),
    ("what's a red flag in my queue?",
     "What does a red flag mean in my queue?"),
    ("how do I hold work until something else is done?",
     "How do I hold work back until something else happens?"),
    ("is it ok to move a queue item while the build is running?",
     "Can I move a queue item while a build is running?"),
    ("what is MAP.md and do I have to write it?",
     "What is MAP.md, and do I write it?"),
    ("the safety check refused my edit, how do I get it through?",
     "The safety check refused my edit — how do I get it through?"),
    ("what's the difference between kept and cleared for an item?",
     "What is the difference between an item being kept and being cleared?"),
    ("how do I report a problem and how does the answer get back to me?",
     "How do I report a problem, and how does the answer get back to me?"),
]

# The stated limit, pinned so a tuning change is a decision: a short question
# sharing only two content words with its entry scores below MIN_SCORE and is
# missed; the session opening's pointer at the FAQ is the fallback.
rc, out = drive(project(), "why does my project have two repositories?", session="limit")
check("a two-word match stays below the bar (the stated limit)",
      rc == 0 and out == "", out[:200])

for n, (prompt, expected) in enumerate(PARAPHRASES):
    rc, out = drive(project(), prompt, session="p%d" % n)
    check("fires on the right entry: " + prompt,
          rc == 0 and fired_question(out) == expected,
          "rc=%s got=%r" % (rc, fired_question(out) if out else out))

SILENT = [
    "ok", "yes", "yes cut it and post", "Take this one next?", "/throughliner:build",
    "/plan what is a red flag in my queue?",
    "can you fix the login page?", "why is the header blue?",
    "what does this function do?", "go",
    "what is a red flag in my queue " + "and so on " * 30 + "?",
]
for n, prompt in enumerate(SILENT):
    rc, out = drive(project(), prompt, session="q%d" % n)
    check("silent on: " + prompt[:50], rc == 0 and out == "", out[:200])

# No QUEUE.md: not an adopted project.
rc, out = drive(project(adopted=False), "what does a red flag mean in my queue?")
check("silent in a folder with no QUEUE.md", rc == 0 and out == "", out[:200])

# Once per entry per chat; fresh under a new session id.
root = project()
q = "what does a red flag mean in my queue?"
rc1, out1 = drive(root, q, session="same")
rc2, out2 = drive(root, q, session="same")
rc3, out3 = drive(root, q, session="other")
check("first ask in a chat fires", bool(out1), out1[:200])
check("second ask in the same chat is silent", rc2 == 0 and out2 == "", out2[:200])
check("a new session id fires again", bool(out3), out3[:200])
check("the state file sits in .throughliner/",
      os.path.isfile(os.path.join(root, ".throughliner", "faq-offered-same.txt")))

# The answer is cut at the cap and the envelope stays under the hook cap.
if out1:
    text = json.loads(out1)["hookSpecificOutput"]["additionalContext"]
    check("handed text carries the ignore instruction",
          "ignore it where the question is about something else" in text)
    check("handed text stays well under the 10,000-character hook cap",
          len(text) < 3000, str(len(text)))

# Malformed payloads never block a message.
for label, raw in (("not JSON", "{nope"), ("a list", "[1, 2]"), ("empty", ""),
                   ("prompt not a string", json.dumps({"cwd": root, "prompt": 7}))):
    rc, out = drive(root, None, raw=raw)
    check("malformed payload (%s): exit 0, no output" % label,
          rc == 0 and out == "", "rc=%s out=%r" % (rc, out[:100]))

print()
if failures:
    print("%d check(s) FAILED: %s" % (len(failures), ", ".join(failures)))
    sys.exit(1)
print("all checks passed")
