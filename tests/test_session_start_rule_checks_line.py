#!/usr/bin/env python3
"""The rule-checks board line names the path the script actually lives at.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_session_start_rule_checks_line.py

Why this exists ([hooks-name-old-workshop-paths]): the opening printed
`python workshop/resources/rule_signals.py .` after the repository cleanup
had moved the script to `method/rule_signals.py`, run with `py` from the
outer. The hook now prints the command for whichever path exists, and nothing
where neither does.

The board script is a stub that prints one firing line, so the case reads the
command the hook composed rather than running the real checks.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "session_start.py")

STUB = ("import sys\n"
        "sys.stdout.write('[FIRING] example-slug: a stub signal\\n')\n")

_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        _failures.append(name)


def project(script_rel=None):
    d = tempfile.mkdtemp(prefix="rule-checks-line-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8") as f:
        f.write("# QUEUE\n\n## Processed\n\n"
                "--- Cleared to run above this line ---\n\n## Unprocessed\n")
    if script_rel:
        path = os.path.join(d, *script_rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(STUB)
    return d


def opening(cwd):
    payload = {"cwd": cwd, "session_id": "rule-checks-line-session"}
    proc = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                          capture_output=True, text=True, encoding="utf-8",
                          cwd=cwd, timeout=120)
    return proc.stdout


def main():
    print("test_session_start_rule_checks_line")

    d = project("method/rule_signals.py")
    out = opening(d)
    check("with method/rule_signals.py present the line names the py command",
          "py method/rule_signals.py ." in out, out[-600:])
    check("the old workshop command is not printed",
          "workshop/resources/rule_signals.py" not in out, out[-600:])
    shutil.rmtree(d, ignore_errors=True)

    d = project("workshop/resources/rule_signals.py")
    out = opening(d)
    check("with only the old path present the old command is printed",
          "python workshop/resources/rule_signals.py ." in out, out[-600:])
    shutil.rmtree(d, ignore_errors=True)

    d = project()
    out = opening(d)
    check("with neither path present no board line is printed",
          "Rule-lifecycle board" not in out, out[-600:])
    shutil.rmtree(d, ignore_errors=True)

    if _failures:
        print(f"\n{len(_failures)} FAILURE(S)")
        return 1
    print("\nall passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
