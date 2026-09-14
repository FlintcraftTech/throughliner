#!/usr/bin/env python3
"""Regression tests for the `.throughliner/` editing-state signal.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_editing_state_marker.py

No test framework, matching the other tests here: this project has no runner,
and adding one to guard two functions would cost more than it protects. Each
test builds a temp project, drives a hook as a subprocess exactly as the
harness does, and asserts on the marker file that lands.

The headline case is `version stamp matches path shape`, and it exists because
that mismatch is the one silent failure in this feature. A companion app that
cannot parse `version` defaults to **1**, and a version-1 reader resolves
`files` entries as ABSOLUTE paths. So a marker stamped `version: 1` while
carrying version 2's project-relative paths resolves each path against the
reader's working directory, finds nothing there, and holds nothing back — no
error, no overlay, no sign anything is wrong. A clean version-1 marker is not
broken (readers still support it, and absolute paths are correct on a single
machine); the mismatch is. Reading the graft carefully is not enough to catch
it, which is why it gets a permanent case here rather than a code review.
"""

import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = os.path.join(ROOT, "plugin", "throughliner", "hooks")
PRE = os.path.join(HOOKS, "pre_tool_use.py")
POST = os.path.join(HOOKS, "post_tool_use.py")

_failures = []


def check(name, condition, detail=""):
    if condition:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}{(' — ' + detail) if detail else ''}")
        _failures.append(name)


def make_project(tmp, adopted=True):
    if adopted:
        with open(os.path.join(tmp, "SPEC.md"), "w", encoding="utf-8") as f:
            f.write("# SPEC\n")
    with open(os.path.join(tmp, "QUEUE.md"), "w", encoding="utf-8") as f:
        f.write("# QUEUE\n\n## Processed\n\n## Unprocessed\n")
    return tmp


def run_hook(script, cwd, tool_name, file_path, session_id="sess-1"):
    payload = {
        "cwd": cwd,
        "tool_name": tool_name,
        "session_id": session_id,
        "tool_input": {"file_path": file_path},
    }
    subprocess.run(
        [sys.executable, script],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )


def read_markers(cwd):
    d = os.path.join(cwd, ".throughliner")
    if not os.path.isdir(d):
        return {}
    out = {}
    for name in os.listdir(d):
        # Read only what the contract calls a marker: `editing-<session-id>.json`.
        # The folder also holds other transient plugin state — the pre-change
        # snapshots of untracked method documents live in a subfolder here — and
        # a helper that read every entry was reading a directory as a file.
        if not (name.startswith("editing-") and name.endswith(".json")):
            continue
        with open(os.path.join(d, name), encoding="utf-8") as f:
            out[name] = json.load(f)
    return out


# --- The headline case ---------------------------------------------------

def test_version_stamp_matches_path_shape():
    """A version-2 relative path must never ship under a version-1 stamp."""
    print("\nversion stamp matches path shape")
    with tempfile.TemporaryDirectory() as tmp:
        make_project(tmp)
        target = os.path.join(tmp, "QUEUE.md")
        run_hook(PRE, tmp, "Edit", target)
        markers = read_markers(tmp)
        check("a marker was written", len(markers) == 1, f"got {list(markers)}")
        if not markers:
            return
        m = next(iter(markers.values()))

        files = m.get("files")
        version = m.get("version")
        relative = bool(files) and not os.path.isabs(files[0])

        # The mismatch itself: relative paths REQUIRE version >= 2.
        check(
            "relative paths carry version >= 2",
            (not relative) or (isinstance(version, int) and version >= 2),
            f"version={version!r} files={files!r} — a v1 reader would resolve "
            "these against its own working directory and hold nothing",
        )
        # And the converse: a version-1 stamp requires absolute paths.
        check(
            "a version-1 stamp would carry absolute paths",
            version != 1 or not relative,
            f"version={version!r} files={files!r}",
        )


# --- Field contract ------------------------------------------------------

def test_field_contract():
    """Each field must satisfy what the reader actually does with it."""
    print("\nfield contract")
    with tempfile.TemporaryDirectory() as tmp:
        make_project(tmp)
        target = os.path.join(tmp, "SPEC.md")
        run_hook(PRE, tmp, "Write", target)
        markers = read_markers(tmp)
        if not markers:
            check("a marker was written", False)
            return
        m = next(iter(markers.values()))

        # `active` absent, "true", or 1 all cause the reader to SKIP the marker.
        check(
            "active is a real boolean",
            isinstance(m.get("active"), bool),
            f"got {m.get('active')!r}",
        )
        check("active is true on the opening marker", m.get("active") is True)
        # `files` absent or non-list reads as empty.
        check("files is a list", isinstance(m.get("files"), list))
        check(
            "files uses forward slashes and no leading ./",
            m.get("files") == ["SPEC.md"],
            f"got {m.get('files')!r}",
        )
        check("version is 2", m.get("version") == 2, f"got {m.get('version')!r}")
        check("producer is throughliner", m.get("producer") == "throughliner")
        # Kept for diagnosis; the reader uses file mtime, not this.
        check("written_at is present", bool(m.get("written_at")))


def test_absolute_fallback_outside_project():
    """A file outside the project falls back to an absolute path."""
    print("\nabsolute fallback for a file outside the project")
    with tempfile.TemporaryDirectory() as outer:
        os.makedirs(os.path.join(outer, "proj"))
        proj = make_project(os.path.join(outer, "proj"))
        outside = os.path.join(outer, "elsewhere.md")
        with open(outside, "w", encoding="utf-8") as f:
            f.write("x\n")
        run_hook(PRE, proj, "Edit", outside)
        markers = read_markers(proj)
        if not markers:
            check("a marker was written", False)
            return
        m = next(iter(markers.values()))
        files = m.get("files") or [""]
        check(
            "path outside the project stays absolute",
            os.path.isabs(files[0]),
            f"got {files!r}",
        )
        # An absolute path under version 2 is the documented fallback, and the
        # reader passes an already-absolute entry through unchanged — so this
        # is NOT the mismatch case above.
        check("version is still 2", m.get("version") == 2)


# --- Open / close pairing ------------------------------------------------

def test_close_clears_active():
    """post_tool_use writes the same shape with active false."""
    print("\nclosing marker clears active")
    with tempfile.TemporaryDirectory() as tmp:
        make_project(tmp)
        target = os.path.join(tmp, "QUEUE.md")
        run_hook(PRE, tmp, "Edit", target)
        run_hook(POST, tmp, "Edit", target)
        markers = read_markers(tmp)
        if not markers:
            check("a marker was written", False)
            return
        m = next(iter(markers.values()))
        check("active is false after the write", m.get("active") is False)
        check("version still 2", m.get("version") == 2)
        check("files still relative", m.get("files") == ["QUEUE.md"])
        check("still one file for the session", len(markers) == 1)


def test_per_session_files():
    """Two sessions get two markers — one shared file would race."""
    print("\none marker file per session")
    with tempfile.TemporaryDirectory() as tmp:
        make_project(tmp)
        target = os.path.join(tmp, "QUEUE.md")
        run_hook(PRE, tmp, "Edit", target, session_id="sess-A")
        run_hook(PRE, tmp, "Edit", target, session_id="sess-B")
        markers = read_markers(tmp)
        check("two markers", len(markers) == 2, f"got {list(markers)}")
        check(
            "session id appears in each filename",
            set(markers) == {"editing-sess-A.json", "editing-sess-B.json"},
            f"got {sorted(markers)}",
        )


def test_unadopted_project_writes_nothing():
    """No SPEC.md means no marker — from EITHER hook.

    The asymmetry this guards: post_tool_use once wrote a closing marker in
    unadopted folders, so marker files accumulated in projects that had never
    run /setup and therefore had no .gitignore entry covering them.
    """
    print("\nunadopted project writes no marker")
    with tempfile.TemporaryDirectory() as tmp:
        make_project(tmp, adopted=False)
        target = os.path.join(tmp, "QUEUE.md")
        run_hook(PRE, tmp, "Edit", target)
        check("pre_tool_use wrote nothing", read_markers(tmp) == {})
        run_hook(POST, tmp, "Edit", target)
        check("post_tool_use wrote nothing", read_markers(tmp) == {})


def test_hook_never_fails_the_tool_call():
    """A marker-writing failure must not break the user's actual work."""
    print("\nmarker failure never fails the tool call")
    with tempfile.TemporaryDirectory() as tmp:
        make_project(tmp)
        # Occupy .throughliner with a FILE, so makedirs raises.
        with open(os.path.join(tmp, ".throughliner"), "w", encoding="utf-8") as f:
            f.write("not a directory\n")
        payload = {
            "cwd": tmp,
            "tool_name": "Edit",
            "session_id": "sess-1",
            "tool_input": {"file_path": os.path.join(tmp, "QUEUE.md")},
        }
        r = subprocess.run(
            [sys.executable, PRE],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
        )
        check("hook still exits 0", r.returncode == 0, f"rc={r.returncode} {r.stderr}")


def main():
    print("Editing-state signal (.throughliner/) — regression tests")
    test_version_stamp_matches_path_shape()
    test_field_contract()
    test_absolute_fallback_outside_project()
    test_close_clears_active()
    test_per_session_files()
    test_unadopted_project_writes_nothing()
    test_hook_never_fails_the_tool_call()

    print()
    if _failures:
        print(f"{len(_failures)} FAILED: {', '.join(_failures)}")
        return 1
    print("All passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
