#!/usr/bin/env python3
"""The editing-state marker the hook writes matches EDITING-STATE-CONTRACT.md.

A consumer application is built against the contract document, so drift between
the hook's payload and the documented fields must fail a suite instead of
decaying silently. Runs under the existing hooks-staged-paths close trigger,
which is the only moment the format can change.

Run as a plain script: py tests/test_editing_state_contract.py
(never through pytest — see CLAUDE.md's scripting constraints).
"""

import importlib.util
import io
import json
import os
import re
import sys
import tempfile

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "pre_tool_use.py")
CONTRACT = os.path.join(ROOT, "EDITING-STATE-CONTRACT.md")

failures = []


def check(name, cond, detail=""):
    if cond:
        print("PASS  " + name)
    else:
        failures.append(name)
        print("FAIL  " + name + ("  — " + detail if detail else ""))


def load_hook():
    spec = importlib.util.spec_from_file_location("pre_tool_use", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    with io.open(CONTRACT, encoding="utf-8") as f:
        contract = f.read()

    m = re.search(r"\*\*Currently (\d+)\.\*\*", contract)
    check("contract states a current version", m is not None)
    contract_version = int(m.group(1)) if m else None

    mod = load_hook()

    with tempfile.TemporaryDirectory() as td:
        target = os.path.join(td, "docs", "thing.md")
        os.makedirs(os.path.dirname(target))
        with open(target, "w", encoding="utf-8") as f:
            f.write("x")

        mod.write_editing_marker(td, "test-session", target, True)

        marker = os.path.join(td, ".throughliner", "editing-test-session.json")
        check("marker file lands at .throughliner/editing-<session-id>.json",
              os.path.isfile(marker))
        with open(marker, encoding="utf-8") as f:
            payload = json.load(f)

        check("payload version matches the contract's current version",
              payload.get("version") == contract_version,
              "payload %r vs contract %r" % (payload.get("version"),
                                             contract_version))
        # The five documented fields, and only those five.
        documented = {"version", "active", "written_at", "files", "producer"}
        check("payload carries exactly the documented fields",
              set(payload.keys()) == documented,
              "payload keys: %s" % sorted(payload.keys()))
        for field in sorted(documented):
            check("contract documents `%s`" % field,
                  ("`%s`" % field) in contract)
        check("active is a real boolean", payload.get("active") is True)
        check("files is a list of project-relative forward-slash paths",
              payload.get("files") == ["docs/thing.md"],
              repr(payload.get("files")))
        check("producer is the documented constant",
              payload.get("producer") == "throughliner"
              and "`throughliner`" in contract)
        check("written_at parses as ISO 8601 with an offset",
              isinstance(payload.get("written_at"), str)
              and ("+" in payload["written_at"]
                   or payload["written_at"].endswith("Z")))

        # A file outside the project falls back to its absolute path.
        outside = os.path.abspath(os.path.join(td, "..", "outside.md"))
        mod.write_editing_marker(td, "test-session", outside, False)
        with open(marker, encoding="utf-8") as f:
            payload2 = json.load(f)
        check("outside-project file falls back to an absolute path",
              payload2.get("files") == [outside], repr(payload2.get("files")))
        check("active false is a real boolean", payload2.get("active") is False)

    if failures:
        print("\n%d failure(s)" % len(failures))
        sys.exit(1)
    print("\nall passed")


if __name__ == "__main__":
    main()
