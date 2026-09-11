#!/usr/bin/env python3
"""Schema-conformance check for the plugin's three hooks.

Host-only dev artifact — not shipped in the plugin package. Consumers never
author hooks.

Run:  python resources/testing/hook_schema_check.py

WHY THIS EXISTS. `session_start.py` once emitted an output shape Claude Code
does not accept, and its entire payload was silently discarded — probably for a
long time. Nothing caught it, because sessions kept working: Claude read
CLAUDE.md and the queue directly and reconstructed roughly what the hook would
have said. That compensation is exactly what makes a dead hook invisible. This
script is the half of the fix that a machine can do — it drives each hook with a
sample payload and asserts the OUTPUT SHAPE against the published contract.

WHAT IT CANNOT TELL YOU. A correctly-shaped hook can still be dropped before it
reaches a session. Shape conformance is not delivery. The other half of the fix
is the liveness step in CLAUDE.md's Rezip and Push checklists: after a rebuild and
a full restart, ask a fresh session **what it actually received** — never
whether the output "looks right". Both halves are needed; neither substitutes
for the other.

THE CONTRACT BEING ASSERTED (code.claude.com/docs/en/hooks). A hook that wants
to feed something back writes a JSON object on stdout with everything nested
under `hookSpecificOutput`, which carries a `hookEventName` naming the event:

    SessionStart  {"hookSpecificOutput": {"hookEventName": "SessionStart",
                                          "additionalContext": "..."}}
    PreToolUse    {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                          "permissionDecision": "allow|deny|ask",
                                          "permissionDecisionReason": "..."}}
    PostToolUse   {"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                          "additionalContext": "..."}}

The specific defect that got through: `additionalContext` at the TOP level,
with no `hookSpecificOutput` wrapper. That flat shape is checked for by name
below, because it is the one this project has actually shipped.

If the published contract changes, update the expectations here against the
DOCUMENTED contract — not against a remembered one, and not against whatever
the hooks currently emit (that would make the check agree with the bug).
"""

import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PLUGIN_ROOT = os.path.join(ROOT, "plugin", "throughliner")
HOOKS = os.path.join(PLUGIN_ROOT, "hooks")

_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        _failures.append(name)


def drive(hook_filename, payload, cwd=None):
    """Run a hook with a JSON payload on stdin. Returns (rc, stdout, stderr)."""
    env = dict(os.environ)
    env["CLAUDE_PLUGIN_ROOT"] = PLUGIN_ROOT
    proc = subprocess.run(
        [sys.executable, os.path.join(HOOKS, hook_filename)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=cwd or ROOT,
        env=env,
    )
    return proc.returncode, proc.stdout, proc.stderr


def assert_envelope(label, stdout, event, required_fields):
    """The shared contract assertions, applied to any hook's stdout."""
    check(label + ": stdout is valid JSON", _is_json(stdout), stdout[:300])
    if not _is_json(stdout):
        return None
    obj = json.loads(stdout)
    check(label + ": top level is an object", isinstance(obj, dict), type(obj).__name__)
    # The exact defect this script exists to catch.
    check(label + ": NOT the flat legacy shape (no top-level additionalContext)",
          "additionalContext" not in obj,
          "top-level keys: " + repr(sorted(obj)) if isinstance(obj, dict) else "")
    check(label + ": has hookSpecificOutput", "hookSpecificOutput" in obj,
          "top-level keys: " + repr(sorted(obj)) if isinstance(obj, dict) else "")
    hso = obj.get("hookSpecificOutput")
    if not isinstance(hso, dict):
        check(label + ": hookSpecificOutput is an object", False, repr(hso)[:200])
        return None
    check(label + ": hookEventName == " + event, hso.get("hookEventName") == event,
          repr(hso.get("hookEventName")))
    for field in required_fields:
        check(label + ": carries " + field, field in hso, repr(sorted(hso)))
        if field in hso:
            check(label + ": " + field + " is a string", isinstance(hso[field], str),
                  type(hso[field]).__name__)
    return hso


def _is_json(text):
    try:
        json.loads(text)
        return True
    except Exception:
        return False


# --- SessionStart -------------------------------------------------------------

def _installed_markers():
    """The version and format epoch the hook under test expects a project to
    carry, read from the source rather than remembered."""
    with open(os.path.join(PLUGIN_ROOT, ".claude-plugin", "plugin.json"),
              encoding="utf-8") as f:
        version = json.load(f).get("version", "")
    epoch = ""
    with open(os.path.join(HOOKS, "session_start.py"), encoding="utf-8") as f:
        for line in f:
            if line.startswith("FORMAT_EPOCH ="):
                epoch = line.split("=", 1)[1].strip()
                break
    return version, epoch


def _adopted_project():
    """A temp project the hook reads as adopted and current.

    The adopted-path cases used to drive the hook against the folder this
    suite sits in. Since the wrap of 2026-09-04 that folder is the inner
    repository, which holds no SPEC.md or QUEUE.md, so the hook took its
    unadopted path and the "project state within the first 2KB" check failed
    at every rezip. A fixture the suite builds itself is adopted whatever
    layout the project keeps: SPEC.md, a QUEUE.md with both sections and the
    cleared-to-run marker, a LOG/ with its index, the two marker files carrying
    the installed values, under git with one commit.
    """
    d = tempfile.mkdtemp(prefix="hookcheck-adopted-")
    version, epoch = _installed_markers()
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n\nA fixture project.\n")
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8") as f:
        f.write("# QUEUE\n\n## Processed\n\n"
                "--- Cleared to run above this line ---\n\n"
                "## Unprocessed\n")
    os.makedirs(os.path.join(d, "LOG"))
    with open(os.path.join(d, "LOG", "index.md"), "w", encoding="utf-8") as f:
        f.write("# LOG index\n")
    with open(os.path.join(d, ".throughliner-version"), "w",
              encoding="utf-8") as f:
        f.write(version + "\n")
    with open(os.path.join(d, ".throughliner-format-epoch"), "w",
              encoding="utf-8") as f:
        f.write(epoch + "\n")
    for args in (["init", "-q"],
                 ["config", "user.email", "suite@example.invalid"],
                 ["config", "user.name", "suite"],
                 ["add", "-A"],
                 ["commit", "-q", "-m", "fixture"]):
        subprocess.run(["git"] + args, cwd=d, capture_output=True,
                       text=True, encoding="utf-8")
    return d


def test_session_start_adopted():
    """An adopted project, so the hook takes its main path."""
    d = _adopted_project()
    rc, out, err = drive("session_start.py",
                         {"hook_event_name": "SessionStart", "cwd": d,
                          "source": "startup"}, cwd=d)
    check("SessionStart (adopted): exits 0", rc == 0, err[:500])
    hso = assert_envelope("SessionStart (adopted)", out, "SessionStart",
                          ["additionalContext"])
    if hso:
        check("SessionStart (adopted): context is non-empty",
              bool(hso.get("additionalContext", "").strip()))


def test_session_start_unadopted():
    """The empty-folder branch is a separate `json.dump` and needs its own case."""
    d = tempfile.mkdtemp(prefix="hookcheck-empty-")
    rc, out, err = drive("session_start.py",
                         {"hook_event_name": "SessionStart", "cwd": d,
                          "source": "startup"},
                         cwd=d)
    check("SessionStart (unadopted): exits 0", rc == 0, err[:500])
    assert_envelope("SessionStart (unadopted)", out, "SessionStart",
                    ["additionalContext"])


def test_session_start_survives_a_sparse_payload():
    """A payload carrying only the three required keys must not break the hook.

    The harness supplies optional fields inconsistently, so the hook has to cope
    with a payload stripped to the minimum rather than assuming a full one.
    """
    d = _adopted_project()
    rc, out, err = drive("session_start.py",
                         {"hook_event_name": "SessionStart", "cwd": d,
                          "source": "startup"}, cwd=d)
    check("SessionStart (sparse payload): still exits 0 with valid output",
          rc == 0 and _is_json(out), err[:500])


# Hook output strings are capped at 10,000 characters. Documented in the Claude
# Code hooks reference and confirmed by anthropics/claude-code#44086 and #70460:
# past the cap the harness saves the text to a file and injects a ~2KB preview
# plus a path in its place, so the model never sees the remainder.
HOOK_OUTPUT_CAP = 10_000


def test_session_start_payload_fits_under_the_cap():
    """The whole payload must fit in the injected context, not just its front.

    This is the check that matters most in this file, because the failure it
    guards was invisible in every other way. session_start once appended
    plugin-behaviour.md whole — ~50KB in the lighter docset, ~89KB in the
    heavier one, back when there were two — and the harness
    silently discarded everything past the preview. Sessions kept working, which
    is exactly why nobody noticed: Claude read CLAUDE.md and the queue directly
    and reconstructed roughly what the hook would have said.

    The hard cap is asserted. The size is REPORTED beside it and asserts
    nothing.

    There used to be a second assertion, that the payload stayed under half the
    cap. The 10,000 is sourced; the half was not — no comment, no measurement,
    no reference anywhere in the file or in any LOG entry, which was established
    by searching rather than assumed. A bare threshold with no derivation is
    what this project's own rule bans, and two others have been deleted for it.
    It had already failed once, which is the only reason anyone looked.

    Deriving an honest early-warning threshold was attempted and abandoned:
    it would need evidence of how the payload grows with project state — held
    items, waiting mail, worktrees, delivered INBOX bodies — and that evidence
    does not exist. Manufacturing a figure without it is the same failure with
    extra steps. A number nobody has to defend beats a defensible-sounding
    invention, so the size is printed and a human reads it.

    Measured on a minimal adopted fixture since 2026-09-06, so the printed
    size is a floor for the payload rather than this project's own figure.
    """
    d = _adopted_project()
    rc, out, err = drive("session_start.py",
                         {"hook_event_name": "SessionStart", "cwd": d,
                          "source": "startup"}, cwd=d)
    if not _is_json(out):
        check("SessionStart: payload size checkable", False, err[:300])
        return
    ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    size = len(ctx)
    check(f"SessionStart: payload within the {HOOK_OUTPUT_CAP}-char cap",
          size < HOOK_OUTPUT_CAP, f"{size} chars")
    pct = round(100 * size / HOOK_OUTPUT_CAP)
    print(f"  size SessionStart payload: {size} of {HOOK_OUTPUT_CAP} chars "
          f"({pct}%) — reported, not asserted")


def test_session_start_points_at_the_rules_rather_than_pasting_them():
    """The rules are REDIRECTED to, never inlined.

    A regression here would be silent in the worst way — the payload would grow
    past the cap and the rules would stop arriving, with sessions still appearing
    to work. So the check is on the mechanism, not just the size: the directive
    must be present, and the file's actual contents must NOT be.
    """
    d = _adopted_project()
    rc, out, err = drive("session_start.py",
                         {"hook_event_name": "SessionStart", "cwd": d,
                          "source": "startup"}, cwd=d)
    if not _is_json(out):
        check("SessionStart: rules directive checkable", False, err[:300])
        return
    ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    at = ctx.find("=== PLUGIN-WIDE BEHAVIOUR RULES")
    if at == -1:
        print("  skip SessionStart: behaviour-rules directive not emitted "
              "(no CLAUDE_PLUGIN_ROOT in this run)")
        return
    check("SessionStart: rules directive is not first", at > 0, "index " + str(at))
    check("SessionStart: rules are pointed at, not pasted",
          "plugin-behaviour.md IN FULL NOW" in ctx or "IN FULL NOW" in ctx,
          "no read-first instruction found")
    # [skill-docs-exceed-one-read]: the rules file can outrun a single read,
    # and the directive must say so, or a session takes the first page as
    # the whole.
    check("SessionStart: the directive says the read may take more than one page",
          "no further page" in ctx,
          "the more-than-one-read sentence is missing from the directive")
    # The giveaway that someone re-inlined the file: its own body text.
    check("SessionStart: the rules file's contents are absent from the payload",
          "## Response-shape tags" not in ctx and "## The throughline" not in ctx,
          "rules body detected in payload")
    # The FAQ pointer follows the rules directive: truncation ordering only
    # protects what sits earlier, and the rules are the thing that must arrive.
    faq = ctx.find("This project has an FAQ")
    if faq != -1:
        check("SessionStart: FAQ pointer sits after the rules directive",
              faq > at, f"faq at {faq}, rules at {at}")
        check("SessionStart: the FAQ index is pointed at, not pasted",
              "](faq.md#" not in ctx, "FAQ index body detected in payload")


def test_session_start_state_lines_lead_the_payload():
    """Ordering regression: short, load-bearing state must sit at the front.

    Nothing in the payload is bulky any more, so this is belt-and-braces rather
    than the live defence it once was. It stays because it is what makes adding
    a line safe.
    """
    d = _adopted_project()
    rc, out, err = drive("session_start.py",
                         {"hook_event_name": "SessionStart", "cwd": d,
                          "source": "startup"}, cwd=d)
    if not _is_json(out):
        check("SessionStart: ordering checkable", False, err[:300])
        return
    ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    state = ctx.find("[Throughliner] Project is set up.")
    # 2048 is derived, unlike the half-cap that was removed above: past the
    # 10,000-char cap the harness replaces the payload with a preview of about
    # 2KB plus a file path, so anything after the first 2KB is what a capped
    # session would never see. The figure measures the preview, and its
    # sourcing is the hooks reference plus anthropics/claude-code#44086 and
    # #70460 — the same two issues cited for the cap itself. Checked rather
    # than assumed to share the half's fate.
    check("SessionStart: project state within the first 2KB (the size of the "
          "preview a capped payload is replaced by)",
          0 <= state <= 2048, "state line at " + str(state))
    flags = ctx.find("UNCLEARED RED FLAG(S)")
    if flags != -1:
        # Only ONE thing may precede the red-flag notice: the format-migration
        # halt. Both claim primacy and the halt wins, because it says the
        # session's whole picture of the project may be stale — including the
        # queue the flag was read from. Written as an exception rather than by
        # relaxing the check to "somewhere near the front", so that anything
        # ELSE arriving above the flag still fails here.
        #
        # The collision is real rather than theoretical: it appeared the first
        # time this project simultaneously carried an uncleared flag and fell
        # behind the format epoch, and until then the check had never fired at
        # all.
        halt = ctx.find("PROJECT FORMAT OUT OF DATE")
        allowed = 0 if halt == -1 else 1
        preceding = sum(1 for pos in (halt,) if 0 <= pos < flags)
        check("SessionStart: nothing but the migration halt precedes the "
              "red-flag notice",
              flags == 0 or preceding == allowed,
              "flags at %s, halt at %s" % (flags, halt))
    else:
        print("  skip SessionStart: no uncleared red flags in this project right now")


# --- PreToolUse ---------------------------------------------------------------

# The working file is per SESSION, not per project: pre_tool_use resolves it as
# `_build-<safe session id>.md`. A fixture must therefore write that name AND
# send the matching session_id in its payload.
#
# This comment exists because getting it wrong is invisible. The fixture used to
# write the legacy plain `_build.md` and send no session_id, so the hook resolved
# `_build-unknown.md`, found nothing, and correctly concluded no build was
# running — which produced `ask` where the test expected `deny`, and the
# planning-quiet-list advisory where it expected silence. Two standing failures,
# one cause, and the fixture read as correct for weeks because the name it used
# is the name every document still calls it in prose.
#
# A real run is unaffected: it carries a real session id and a correctly named
# working file, which is why the scope-lock kept denying correctly in live
# sessions while this suite failed.
TEST_SESSION_ID = "hookcheck-fixed-session"


def _scoped_project(files_section):
    """A temp project with this session's build working file, whose Files:
    section is `files_section`.

    SPEC.md must exist: the hook only enforces in an ADOPTED project and
    returns silently without it. A fixture missing SPEC.md produces a passing-
    looking silence for every case, which is the failure mode this whole script
    exists to prevent.
    """
    d = tempfile.mkdtemp(prefix="hookcheck-scope-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    name = "_build-%s.md" % TEST_SESSION_ID
    with open(os.path.join(d, name), "w", encoding="utf-8") as f:
        f.write("# Active Build\n\nFiles:\n" + files_section + "\n\nProgress:\n")
    return d


def test_pre_tool_use_out_of_scope_denies():
    d = _scoped_project("- allowed.md")
    rc, out, err = drive("pre_tool_use.py",
                         {"hook_event_name": "PreToolUse", "cwd": d,
                          "session_id": TEST_SESSION_ID,
                          "tool_name": "Edit",
                          "tool_input": {"file_path": os.path.join(d, "forbidden.md")}},
                         cwd=d)
    check("PreToolUse (out of scope): exits 0", rc == 0, err[:500])
    hso = assert_envelope("PreToolUse (out of scope)", out, "PreToolUse",
                          ["permissionDecision", "permissionDecisionReason"])
    if hso:
        check("PreToolUse (out of scope): decision is deny",
              hso.get("permissionDecision") == "deny", repr(hso.get("permissionDecision")))


def test_pre_tool_use_in_scope_is_silent():
    d = _scoped_project("- allowed.md")
    rc, out, err = drive("pre_tool_use.py",
                         {"hook_event_name": "PreToolUse", "cwd": d,
                          "session_id": TEST_SESSION_ID,
                          "tool_name": "Edit",
                          "tool_input": {"file_path": os.path.join(d, "allowed.md")}},
                         cwd=d)
    check("PreToolUse (in scope): exits 0", rc == 0, err[:500])
    check("PreToolUse (in scope): emits nothing", out.strip() == "", out[:300])


def test_pre_tool_use_retired_terms_is_writable():
    """workshop/resources/retired-terms.md is writable with a build running.

    The method requires a session that retires a term to append it here, and
    retirement is discovered DURING a build — so this path can never be in a
    `Files:` list computed before the build started. Without the exemption the
    obligation is satisfiable only in an undocumented window at the close.
    """
    d = _scoped_project("- allowed.md")
    target = os.path.join(d, "workshop", "resources", "retired-terms.md")
    rc, out, err = drive("pre_tool_use.py",
                         {"hook_event_name": "PreToolUse", "cwd": d,
                          "session_id": TEST_SESSION_ID,
                          "tool_name": "Edit",
                          "tool_input": {"file_path": target}},
                         cwd=d)
    check("PreToolUse (retired-terms): exits 0", rc == 0, err[:500])
    check("PreToolUse (retired-terms): not denied",
          '"permissionDecision": "deny"' not in out.replace("'", '"'), out[:300])


def test_pre_tool_use_git_safety_denies():
    # Assembled at runtime rather than written out literally: the git-safety
    # patterns match command TEXT, so a literal here would be denied as data.
    cmd = " ".join(["git", "reset", "--" + "hard", "HEAD~1"])
    d = _scoped_project("- allowed.md")
    rc, out, err = drive("pre_tool_use.py",
                         {"hook_event_name": "PreToolUse", "cwd": d,
                          "tool_name": "Bash", "tool_input": {"command": cmd}},
                         cwd=d)
    check("PreToolUse (git safety): exits 0", rc == 0, err[:500])
    hso = assert_envelope("PreToolUse (git safety)", out, "PreToolUse",
                          ["permissionDecision", "permissionDecisionReason"])
    if hso:
        check("PreToolUse (git safety): decision is deny",
              hso.get("permissionDecision") == "deny", repr(hso.get("permissionDecision")))


def test_pre_tool_use_subagent_asks():
    d = _scoped_project("- allowed.md")
    rc, out, err = drive("pre_tool_use.py",
                         {"hook_event_name": "PreToolUse", "cwd": d,
                          "tool_name": "Task",
                          "tool_input": {"description": "do a thing"}},
                         cwd=d)
    check("PreToolUse (subagent): exits 0", rc == 0, err[:500])
    hso = assert_envelope("PreToolUse (subagent)", out, "PreToolUse",
                          ["permissionDecision", "permissionDecisionReason"])
    if hso:
        check("PreToolUse (subagent): decision is ask — never deny",
              hso.get("permissionDecision") == "ask", repr(hso.get("permissionDecision")))


# --- PostToolUse --------------------------------------------------------------

def _queue_project(queue_text):
    """SPEC.md again mandatory — the lint only runs in an adopted project."""
    d = tempfile.mkdtemp(prefix="hookcheck-queue-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8") as f:
        f.write(queue_text)
    return d


def test_post_tool_use_lint_shape():
    """A malformed queue should produce advisory output in the nested shape."""
    d = _queue_project("# QUEUE\n\n## Processed\n\n#### An item with no slug\n"
                       "Some rationale.\n\n## Unprocessed\n")
    rc, out, err = drive("post_tool_use.py",
                         {"hook_event_name": "PostToolUse", "cwd": d,
                          "tool_name": "Edit",
                          "tool_input": {"file_path": os.path.join(d, "QUEUE.md")}},
                         cwd=d)
    check("PostToolUse (lint): exits 0 — advisory, never blocking", rc == 0, err[:500])
    check("PostToolUse (lint): produced an advisory for a slugless work item",
          out.strip() != "", "(silence here usually means the fixture isn't adopted)")
    if out.strip() == "":
        return
    assert_envelope("PostToolUse (lint)", out, "PostToolUse", ["additionalContext"])


def test_content_stamp_ignores_the_cli_in_use_marker():
    """A runtime bookkeeping file must not move the build stamp.

    The plugin CLI writes `.in_use` into whichever installed build is active
    and removes it again. While `content_stamp()` hashed it, the installed
    host's stamp moved between two session starts with no reinstall between
    them, and a host byte-identical to the target reported as stale — a false
    reading that was acted on, arguing to defer a merge because the branch's
    plugin changes supposedly weren't live. They were.

    This asserts the shape of the fix rather than the one filename: any future
    CLI artifact of the same kind should be caught here, by the pre-restart
    check in the Rezip and Release checklists, rather than by another multi-day
    investigation.
    """
    sys.path.insert(0, HOOKS)
    try:
        import session_start
    finally:
        sys.path.pop(0)

    d = tempfile.mkdtemp(prefix="si-stamp-")
    with open(os.path.join(d, "hook.py"), "w", encoding="utf-8") as fh:
        fh.write("print('hello')\n")
    os.makedirs(os.path.join(d, "docs"), exist_ok=True)
    with open(os.path.join(d, "docs", "plan.md"), "w", encoding="utf-8") as fh:
        fh.write("# plan\n")

    before = session_start.content_stamp(d)
    check("content_stamp: produces a stamp for a plugin-shaped directory",
          bool(before), repr(before))

    # The REAL shape, and getting this wrong is why the first version of this
    # fix shipped broken: `.in_use` is a DIRECTORY holding one marker file per
    # live session, not a single file. A test that created it as a file passed
    # against an exclusion that did nothing.
    in_use = os.path.join(d, ".in_use")
    os.makedirs(in_use, exist_ok=True)
    with open(os.path.join(in_use, "3260"), "w", encoding="utf-8") as fh:
        fh.write("")
    after = session_start.content_stamp(d)
    check("content_stamp: an .in_use DIRECTORY does NOT move the stamp",
          before == after, "before=%r after=%r" % (before, after))

    # A second session adds a second marker file inside it. Without the
    # directory exclusion the stamp moves with the number of open sessions.
    with open(os.path.join(in_use, "8168"), "w", encoding="utf-8") as fh:
        fh.write("")
    check("content_stamp: a SECOND session marker still doesn't move it",
          session_start.content_stamp(d) == before,
          "the stamp is tracking how many sessions are open")

    # Belt and braces: the flat-file form is excluded too, in case the CLI
    # ever writes it that way.
    import shutil
    shutil.rmtree(in_use)
    with open(in_use, "w", encoding="utf-8") as fh:
        fh.write("some-session-id\n")
    check("content_stamp: a flat .in_use file doesn't move it either",
          session_start.content_stamp(d) == before)

    os.remove(in_use)
    check("content_stamp: removing the marker leaves the stamp unchanged too",
          session_start.content_stamp(d) == before)

    # The exclusion must be narrow: a real package file still moves it.
    with open(os.path.join(d, "docs", "next.md"), "w", encoding="utf-8") as fh:
        fh.write("# next\n")
    check("content_stamp: a genuine package file DOES move the stamp",
          session_start.content_stamp(d) != before)


def test_post_tool_use_non_queue_edit_is_silent():
    d = _queue_project("# QUEUE\n\n## Processed\n\n## Unprocessed\n")
    rc, out, err = drive("post_tool_use.py",
                         {"hook_event_name": "PostToolUse", "cwd": d,
                          "tool_name": "Edit",
                          "tool_input": {"file_path": os.path.join(d, "notes.md")}},
                         cwd=d)
    check("PostToolUse (unrelated file): exits 0", rc == 0, err[:500])
    check("PostToolUse (unrelated file): emits nothing", out.strip() == "", out[:300])


def test_session_start_directs_to_inbox_messages():
    """A waiting message arrives as a filename and a directive, not as text.

    Bodies were inlined for a period, on the reasoning that an instruction to
    open a file is a step and a step can be skipped — which had happened. The
    ceiling is what overturned it: hook output is capped at 10,000 characters,
    and past the cap the harness discards the payload entirely, so enough unread
    mail costs the session its project state and its rules directive as well as
    its mail. The replacement is the shape this payload already trusts for a far
    larger file — a directive carrying a self-check.

    Four halves are pinned: the filename is named, the body is absent, the
    directive carries a check, and the message is still labelled as data.
    """
    d = tempfile.mkdtemp(prefix="hookcheck-inbox-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8") as f:
        f.write("# QUEUE\n\n## Processed\n\n## Unprocessed\n")
    os.makedirs(os.path.join(d, "INBOX"))
    body = "A distinctive sentence only this message carries."
    with open(os.path.join(d, "INBOX", "2026-08-15-a-report.md"), "w",
              encoding="utf-8") as f:
        f.write("# A report\n\n" + body + "\n")
    rc, out, err = drive("session_start.py",
                         {"hook_event_name": "SessionStart", "cwd": d,
                          "source": "startup"})
    check("SessionStart (mail): exits 0", rc == 0, err[:500])
    ctx = ""
    if _is_json(out):
        ctx = (json.loads(out).get("hookSpecificOutput") or {}).get(
            "additionalContext", "")
    check("SessionStart: the message filename is named",
          "INBOX/2026-08-15-a-report.md" in ctx, ctx[:300])
    check("SessionStart: the message body is NOT inlined",
          body not in ctx, ctx[:300])
    check("SessionStart: the read directive carries a self-check",
          "SELF-CHECK" in ctx, ctx[:300])
    check("SessionStart: the message is labelled as data, not instruction",
          "not an instruction" in ctx, ctx[:300])
    check("SessionStart: routing and archiving are still required",
          "INBOX/archive/" in ctx, ctx[:300])


def test_session_start_empty_mailbox_is_silent():
    """The other half — a mailbox with nothing in it adds nothing."""
    d = tempfile.mkdtemp(prefix="hookcheck-inbox-empty-")
    with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
        f.write("# SPEC\n")
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8") as f:
        f.write("# QUEUE\n\n## Processed\n\n## Unprocessed\n")
    os.makedirs(os.path.join(d, "INBOX"))
    rc, out, err = drive("session_start.py",
                         {"hook_event_name": "SessionStart", "cwd": d,
                          "source": "startup"})
    check("SessionStart (empty mail): exits 0", rc == 0, err[:500])
    ctx = ""
    if _is_json(out):
        ctx = (json.loads(out).get("hookSpecificOutput") or {}).get(
            "additionalContext", "")
    check("SessionStart: an empty mailbox says nothing",
          "INBOX" not in ctx, ctx[:300])


def main():
    print("hook schema-conformance check")
    print("(shape only — delivery is proved by the liveness step in CLAUDE.md)\n")
    for fn in (
        test_session_start_adopted,
        test_session_start_unadopted,
        test_session_start_survives_a_sparse_payload,
        test_session_start_payload_fits_under_the_cap,
        test_session_start_points_at_the_rules_rather_than_pasting_them,
        test_session_start_state_lines_lead_the_payload,
        test_session_start_directs_to_inbox_messages,
        test_session_start_empty_mailbox_is_silent,
        test_pre_tool_use_out_of_scope_denies,
        test_pre_tool_use_in_scope_is_silent,
        test_pre_tool_use_retired_terms_is_writable,
        test_pre_tool_use_git_safety_denies,
        test_pre_tool_use_subagent_asks,
        test_content_stamp_ignores_the_cli_in_use_marker,
        test_post_tool_use_lint_shape,
        test_post_tool_use_non_queue_edit_is_silent,
    ):
        print(fn.__name__)
        fn()
    print()
    if _failures:
        print("%d check(s) FAILED: %s" % (len(_failures), ", ".join(_failures)))
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
