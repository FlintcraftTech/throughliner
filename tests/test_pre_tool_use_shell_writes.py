#!/usr/bin/env python3
"""Regression tests for pre_tool_use.py's structured shell-write matcher.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_pre_tool_use_shell_writes.py

No test framework, matching test_reorder_queue.py: each case builds a temp
project (SPEC.md + optional _build.md), drives the hook as a subprocess with a
real PreToolUse payload, and asserts on the JSON decision that comes back.

Why this exists ([shell-heredoc-write-immediately-after-authoring-the-rule]):
two live slips in one run reached for `python - <<'PY'` to write shipped docs,
and the matcher that would deny that shape was built in the same run — so its
coverage had never been tested against the commands that actually slipped.
This suite drives those exact shapes.

The finding the first run of this suite established, and what was done about it
([shell-write-matcher-blind-to-in-scope-targets]): the matcher used to deny a
scripted write only when the target was OUTSIDE the build's Files list, and
both real slips wrote files that were IN scope for their run — so the matcher
as built would not have caught either of them. The denial's two reasons come
apart: the scope-lock reason does not apply to an in-scope target, but the
stale-view reason (the shell can read a stale copy and silently clobber work)
applies to every scripted write regardless of scope. So the scope condition was
dropped. A detectable scripted write to ANY file inside the project is now
denied, build or no build; the scratchpad, the memory directory and anything
outside the project still pass.

The computed-target fail-open closed on 2026-08-09
([shell-write-guard-computed-path-gap]). It used to be deliberate: a target the
matcher could not read was allowed through. Two live corruptions came through
that hole in a single day — one of them inside the very session that diagnosed
it — so an unreadable target now denies, on the reasoning that "cannot tell
whether this is protected" must not resolve to "allow". Cases 7-9 below cover
it, and case 9 pins the deliberate remaining cost: the scratchpad carve-out
survives only for a literally-written path.
"""

import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "pre_tool_use.py")

_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("  -- " + detail if detail else ""))
        _failures.append(name)


def make_project(build_files=None):
    """Temp project dir: SPEC.md always; _build.md with Files: when given."""
    d = tempfile.mkdtemp(prefix="pretool-test-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    if build_files is not None:
        lines = ["# Active Build\n\nFiles:\n"]
        for p in build_files:
            lines.append("- " + p + "\n")
        with open(os.path.join(d, "_build.md"), "w", encoding="utf-8") as f:
            f.write("".join(lines))
    return d


def drive(cwd, command):
    """Run the hook with a Bash PreToolUse payload; return the decision dict."""
    payload = {
        "cwd": cwd,
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "session_id": "test-session",
    }
    proc = subprocess.run(
        [sys.executable, HOOK],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if not proc.stdout.strip():
        return {}
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {}
    return (out.get("hookSpecificOutput") or {})


def decision(cwd, command):
    return drive(cwd, command).get("permissionDecision", "pass")


# The two shapes that actually slipped, verbatim in structure.
HEREDOC_APPEND = (
    "python - <<'PY'\n"
    "with open('plugin/throughliner/templates/faq-template.md', 'a') as f:\n"
    "    f.write('new entry')\n"
    "PY"
)
HEREDOC_SUBSTITUTE = (
    "python - <<'PY'\n"
    "p = 'plugin/throughliner/docs/setup.md'\n"
    "text = open(p).read()\n"
    "open('plugin/throughliner/docs/setup.md', 'w').write(text.replace('a', 'b'))\n"
    "PY"
)
COMPUTED_PATH = (
    "python - <<'PY'\n"
    "name = 'faq-template.md'\n"
    "with open(f'plugin/throughliner/templates/{name}', 'a') as f:\n"
    "    f.write('x')\n"
    "PY"
)


def main():
    print("test_pre_tool_use_shell_writes")

    # 1. The slipped append shape, target OUT of scope during a build -> deny.
    d = make_project(build_files=["plugin/throughliner/docs/plan.md"])
    check(
        "heredoc append to out-of-scope file denied",
        decision(d, HEREDOC_APPEND) == "deny",
        "got: " + decision(d, HEREDOC_APPEND),
    )

    # 2. The slipped substitution shape, out of scope -> deny.
    check(
        "heredoc substitution on out-of-scope file denied",
        decision(d, HEREDOC_SUBSTITUTE) == "deny",
        "got: " + decision(d, HEREDOC_SUBSTITUTE),
    )

    # 3. Computed path -> denies. This case previously asserted the opposite,
    #    pinning the fail-open as intended behaviour so nobody "fixed" it. That
    #    was the right call on the evidence then available and the wrong one on
    #    the evidence since: the hole was used twice in one day. The assertion
    #    is flipped rather than deleted, so the reversal is visible here.
    check(
        "computed path denies (fail-open closed 2026-08-09)",
        decision(d, COMPUTED_PATH) == "deny",
        "got: " + decision(d, COMPUTED_PATH),
    )

    # 4. The case this suite's first run exposed, now flipped: the same slipped
    #    shape against a file IN the build's Files list is denied. Both real
    #    slips were of exactly this shape, so this is the assertion that says
    #    the matcher would now catch them.
    d2 = make_project(
        build_files=["plugin/throughliner/templates/faq-template.md"]
    )
    check(
        "in-scope scripted write denied (scope condition dropped)",
        decision(d2, HEREDOC_APPEND) == "deny",
        "got: " + decision(d2, HEREDOC_APPEND),
    )

    # 5. No active build -> still denied. The stale-view reason does not depend
    #    on a build being open, and the user's standing instruction forbids
    #    shell file-writes unconditionally.
    d3 = make_project(build_files=None)
    check(
        "no active build: scripted write still denied",
        decision(d3, HEREDOC_APPEND) == "deny",
        "got: " + decision(d3, HEREDOC_APPEND),
    )

    # 5b. A scripted write to a method doc is denied too — the old exemption for
    #     detectable shapes is gone. QUEUE.md is exactly the corruption route the
    #     queue mover exists to prevent.
    QUEUE_WRITE = (
        "python - <<'PY'\n"
        "open('QUEUE.md', 'w').write('clobbered')\n"
        "PY"
    )
    check(
        "scripted write to QUEUE.md denied (method-doc exemption removed)",
        decision(d3, QUEUE_WRITE) == "deny",
        "got: " + decision(d3, QUEUE_WRITE),
    )

    # 5c. The scratchpad carve-out stays: sanctioned scratch space, outside the
    #     repo, and named in the denial text as the route when scratch is what
    #     you actually need.
    scratch = os.path.join(
        tempfile.gettempdir(), "claude", "proj", "sess", "scratchpad", "note.md"
    )
    SCRATCH_WRITE = (
        "python - <<'PY'\n"
        "open(%r, 'w').write('x')\n"
        "PY" % scratch.replace("\\", "/")
    )
    check(
        "scratchpad scripted write still passes",
        decision(d3, SCRATCH_WRITE) == "pass",
        "got: " + decision(d3, SCRATCH_WRITE),
    )

    # 6. A plain non-writing python invocation passes. This is also the case
    #    that keeps the queue mover usable: invoking a script file carries no
    #    write call in the command text, so neither matcher sees anything.
    check(
        "non-writing python command passes",
        decision(d, "python plugin/throughliner/scripts/reorder_queue.py QUEUE.md --delete x Processed")
        == "pass",
        "",
    )

    # 7. The exact shape of the first live corruption: the path assigned to a
    #    variable one statement before the write. This passed before 2026-08-09
    #    and wrote a QUEUE.md with six work items still in it.
    VAR_PATH_WRITE = (
        "python -c \"p='QUEUE.md'; "
        "open(p, 'w').write('clobbered')\""
    )
    check(
        "computed target via variable is denied",
        decision(d3, VAR_PATH_WRITE) == "deny",
        "got: " + decision(d3, VAR_PATH_WRITE),
    )

    # 7b. The second live instance, in the session that diagnosed the first:
    #     a heredoc using io.open on the same variable.
    IO_OPEN_WRITE = (
        "python - <<'PY'\n"
        "import io\n"
        "p = 'QUEUE.md'\n"
        "io.open(p, 'w', encoding='utf-8').write('x')\n"
        "PY"
    )
    check(
        "computed target via io.open in a heredoc is denied",
        decision(d3, IO_OPEN_WRITE) == "deny",
        "got: " + decision(d3, IO_OPEN_WRITE),
    )

    # 8. pathlib's side of the same gap: write_text on a receiver that is not a
    #    literal Path(...). The literal form is matched by PY_PATH_WRITE; this
    #    one is only visible as an excess of the general shape.
    VAR_PATHLIB_WRITE = (
        "python - <<'PY'\n"
        "import pathlib\n"
        "target = pathlib.Path('QUEUE.md')\n"
        "target.write_text('clobbered')\n"
        "PY"
    )
    check(
        "computed pathlib write_text is denied",
        decision(d3, VAR_PATHLIB_WRITE) == "deny",
        "got: " + decision(d3, VAR_PATHLIB_WRITE),
    )

    # 8b. An f-string target is computed even though it is quoted — the quotes
    #     make it look literal, which is exactly why it needs its own case.
    FSTRING_WRITE = (
        "python - <<'PY'\n"
        "open(f'{d}/QUEUE.md', 'w').write('x')\n"
        "PY"
    )
    check(
        "f-string target is denied",
        decision(d3, FSTRING_WRITE) == "deny",
        "got: " + decision(d3, FSTRING_WRITE),
    )

    # 9. The accepted cost, pinned so nobody later "fixes" it as a bug: a
    #    scratchpad write with a COMPUTED path is denied, even though the same
    #    write with the path spelled out (case 5c) passes. Scratch space is
    #    still available; it just has to be named.
    SCRATCH_COMPUTED = (
        "python - <<'PY'\n"
        "import os\n"
        "p = os.path.join(base, 'note.md')\n"
        "open(p, 'w').write('x')\n"
        "PY"
    )
    check(
        "computed scratchpad path is denied (accepted cost)",
        decision(d3, SCRATCH_COMPUTED) == "deny",
        "got: " + decision(d3, SCRATCH_COMPUTED),
    )

    # 10. A read-only script is untouched. The rejected alternative to all of
    #     the above was widening detection to "imports io/pathlib and names a
    #     project doc", which would have denied this.
    READ_ONLY = (
        "python - <<'PY'\n"
        "import io\n"
        "p = 'QUEUE.md'\n"
        "print(len(io.open(p).read()))\n"
        "PY"
    )
    check(
        "read-only script still passes",
        decision(d3, READ_ONLY) == "pass",
        "got: " + decision(d3, READ_ONLY),
    )

    # 11. `py -c` was the invocation the guard missed, and the one this
    #     project's own scripting rules require on this machine. It ran live
    #     during a rezip, wrote plugin.json, and nothing fired.
    PY_DASH_C = (
        "py -c \"open('plugin/throughliner/.claude-plugin/plugin.json', 'w')"
        ".write('{}')\""
    )
    check(
        "py -c scripted write is denied",
        decision(d3, PY_DASH_C) == "deny",
        "got: " + decision(d3, PY_DASH_C),
    )

    # 12. `sed -i` is the same fault in another tool. This exact shape ran
    #     against QUEUE.md and was harmless only because the scripts were empty.
    SED_INPLACE_CMD = "sed -i '' -e '' QUEUE.md"
    check(
        "sed -i on a project file is denied",
        decision(d3, SED_INPLACE_CMD) == "deny",
        "got: " + decision(d3, SED_INPLACE_CMD),
    )

    # 13. The false positive the widened pattern must not create: invoking the
    #     queue mover names a .py file and passes flags, and it is the
    #     sanctioned route for awkward queue edits. A bare `\bpy\b` would have
    #     fired on the `py` inside `reorder_queue.py`.
    MOVER = "py plugin/throughliner/scripts/reorder_queue.py QUEUE.md --delete a-slug Processed"
    check(
        "queue mover invocation still passes",
        decision(d3, MOVER) == "pass",
        "got: " + decision(d3, MOVER),
    )

    # 14. A read-only sed carries no in-place flag and is not a write.
    SED_READ = "sed -n '1,5p' QUEUE.md"
    check(
        "sed without -i still passes",
        decision(d3, SED_READ) == "pass",
        "got: " + decision(d3, SED_READ),
    )

    # 12b. The QUOTED target — the live escape of 2026-09-01. The old token
    #      filter skipped every quoted token to avoid reading the quoted sed
    #      script as a path, and on a machine whose folders carry spaces every
    #      target path is quoted — so the skip removed exactly the targets the
    #      check exists for. A `sed -i` ran against a project test file and
    #      nothing fired. Quotes are resolved now, and the script is told
    #      apart by its own shape.
    for label, cmd in (
        ("quoted relative target",
         "sed -i 's/a/b/' \"workshop/resources/testing/test_stop_hook.py\""),
        ("single-quoted relative target",
         "sed -i 's/a/b/' 'plugin/throughliner/docs/plan.md'"),
        ("quoted absolute target with spaces",
         "sed -i 's/a/b/' \"" + os.path.join(d3, "sub dir", "file.py") + "\""),
        ("suffix variant -i.bak on a quoted target",
         "sed -i.bak 's/a/b/' \"QUEUE.md\""),
    ):
        check(
            f"sed -i with a {label} is denied",
            decision(d3, cmd) == "deny",
            "got: " + decision(d3, cmd),
        )

    # 12c. The narrowing that must survive 12b: a target OUTSIDE the project
    #      passes, quoted or not, and a pipe-delimited script is never read as
    #      a path (which would have denied by a bogus in-project resolution).
    for label, cmd in (
        ("quoted outside target",
         "sed -i 's/a/b/' \"C:/elsewhere/some file.md\""),
        ("pipe-delimited script, outside target",
         "sed -i 's|a|b|' \"C:/elsewhere/whatever.md\""),
    ):
        check(
            f"sed -i with a {label} still passes",
            decision(d3, cmd) == "pass",
            "got: " + decision(d3, cmd),
        )

    # --- raw-string paths: literal passes, computed still denied -------------
    #
    # `r'C:\...'` is the ordinary way to write a Windows path in Python. The
    # literal extractor could not read one and the computed check read every one
    # as computed, so a scratchpad path spelled out in full was denied by a
    # message that promises a literal scratchpad path passes. Both halves are
    # pinned here, because fixing one and not the other is what produced the
    # disagreement in the first place.
    d4 = make_project()
    scratch = os.path.join(
        tempfile.gettempdir(), "claude", "proj", "sess", "scratchpad", "x.md"
    ).replace("\\", "/")

    raw_scratch = "py -c \"open(r'%s', 'w').write('hi')\"" % scratch
    check(
        "a scratchpad path written as a raw string passes",
        decision(d4, raw_scratch) == "pass",
        "got: " + decision(d4, raw_scratch),
    )

    plain_scratch = "py -c \"open('%s', 'w').write('hi')\"" % scratch
    check(
        "a scratchpad path written plainly still passes",
        decision(d4, plain_scratch) == "pass",
        "got: " + decision(d4, plain_scratch),
    )

    raw_queue = "py -c \"open(r'%s', 'w').write('hi')\"" % (
        os.path.join(d4, "QUEUE.md").replace("\\", "/")
    )
    check(
        "a raw-string path inside the project is still denied",
        decision(d4, raw_queue) == "deny",
        "got: " + decision(d4, raw_queue),
    )

    computed = "py -c \"open(p, 'w').write('hi')\""
    check(
        "a computed target is still denied",
        decision(d4, computed) == "deny",
        "got: " + decision(d4, computed),
    )

    fstring = "py -c \"open(f'{d}/x.md', 'w').write('hi')\""
    check(
        "an f-string target is still denied, prefix or not",
        decision(d4, fstring) == "deny",
        "got: " + decision(d4, fstring),
    )

    # --- call-built paths: computed by definition, denied ---------------------
    #
    # `open(os.path.join(...), "w")` matched neither the literal extractor nor
    # PY_OPEN_WRITE_ANY (whose argument class excludes parens and commas), so a
    # write whose path was built by a call sailed through both halves of the
    # guard. A call-built argument is computed by definition — there is no
    # literal to read — so it denies. Matching reaches one level of nested
    # parentheses inside the call.
    joined = "py -c \"open(os.path.join('QUEUE', 'x.md'), 'w').write('hi')\""
    check(
        "a call-built target (os.path.join) is denied",
        decision(d4, joined) == "deny",
        "got: " + decision(d4, joined),
    )

    # Direct drive: the detector itself reports the join form as computed.
    import importlib.util
    spec = importlib.util.spec_from_file_location("pre_tool_use", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    check(
        "has_computed_write_target sees the join form",
        mod.has_computed_write_target(joined) is True,
    )
    check(
        "has_computed_write_target still sees the bare-variable form",
        mod.has_computed_write_target("py -c \"open(p, 'w').write('x')\"")
        is True,
    )
    check(
        "a literal path is still not computed",
        mod.has_computed_write_target("py -c \"open('a.md', 'w').write('x')\"")
        is False,
    )
    check(
        "a read-mode open with a call-built path does not trigger",
        mod.has_computed_write_target(
            "py -c \"open(os.path.join('a', 'b.md'), 'r').read()\""
        )
        is False,
    )

    print()
    if _failures:
        print("FAILURES: " + ", ".join(_failures))
        return 1
    print("all passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
