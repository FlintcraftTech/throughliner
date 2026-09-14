#!/usr/bin/env python3
"""Regression test: the rules directive names the resolved plugin path.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_session_start_rules_directive.py

Why this exists ([rules-directive-names-unexpanded-plugin-root]): the
directive printed the literal `${CLAUDE_PLUGIN_ROOT}`, which a plain chat
cannot expand; a tester's session ran it through a shell, got an empty read,
and hunted through the plugin cache. The directive now carries the resolved
absolute path, and keeps the literal only where the variable is empty.
"""

import importlib.util
import os
import sys

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "session_start.py")
_spec = importlib.util.spec_from_file_location("session_start", HOOK)
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)

_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        _failures.append(name)


def main():
    print("rules directive path:")
    root = r"C:\Users\Someone\.claude\plugins\cache\flintcraft\throughliner\1.22.0"
    out = hook._behaviour_rules_directive(root)
    check("variable set: the directive carries the absolute path",
          "C:/Users/Someone/.claude/plugins/cache/flintcraft/throughliner/1.22.0/docs/skill-nonspecific-rules.md" in out,
          out[:300])
    check("variable set: no shell variable remains", "${CLAUDE_PLUGIN_ROOT}" not in out)
    out = hook._behaviour_rules_directive("")
    check("variable unset: the directive still goes out",
          "READ" in out and "skill-nonspecific-rules.md" in out, out[:200])
    check("variable unset: it carries the literal fallback",
          "${CLAUDE_PLUGIN_ROOT}/docs/skill-nonspecific-rules.md" in out)

    if _failures:
        print(f"\n{len(_failures)} FAILURE(S)")
        return 1
    print("\nall passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
