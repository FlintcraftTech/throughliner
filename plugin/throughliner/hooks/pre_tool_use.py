#!/usr/bin/env python3
"""
PreToolUse hook — enforces three rules:

4. With NO build running (a planning or freeform session), a write outside
   the standing list — QUEUE.md, SPEC.md, CYCLES.md, LOG/, FAQ/, the
   session's own notes, plus the always-editable paths — is DENIED, never asked: an ask
   that gets waved through is not consent, and a planning session is where
   a change becomes queued work instead of an edit. A session extends the
   standing list by declaring a scope file (_freeform-<session-id>.md)
   listing paths — a freeform session copies them from its queue item's
   instructions; any no-build session writes one path at a time on the
   user's repeated direction, which is the user's door through a denial.
   An unscoped build (a working file with no Files: section) is surfaced
   once.

1. During a build, the session's own build working file
   (_build-<session-id>.md) has a Files: section governing which files are
   editable (method docs — QUEUE.md, LOG/, that working file — plus the user's
   memory dir, workshop/resources/research/, the session scratchpad dir,
   TOOLS.md, and
   any project's INBOX/ are always editable). Tri-state:
   no Files: section = no enforcement;
   section present but empty = method docs only; entries listed = only
   those files. SPEC.md is not a method doc, so a build can edit it only
   when it's explicitly listed in Files: — a batch that needs to change
   SPEC lists it; a feature build that doesn't name SPEC can't touch it,
   so scope-lock alone keeps SPEC read-only for any build that doesn't
   name it. A part's own SPEC.md, at any depth, is governed the same way:
   listed in Files: by path, or read-only to the build.
2. Git safety: block git reset --hard, git push --force, blanket
   staging (git add -A / --all / .), and git commit -a / -am.
3. Subagent cost ask-gate: the Task tool (spawning a subagent) returns
   permissionDecision "ask" — never "deny" — so the user is always
   prompted before a subagent runs, but keeps full choice. A subagent
   burns tokens fast and a single run can exhaust the user's usage, so
   the spawn must never be silent. Fires wherever the plugin is
   installed, independent of project adoption.

5. A Write whose target is an existing file under LOG/ is refused, naming
   the next free `-2`, `-3`, … filename. Write only, never Edit: appending
   to an existing record is legitimate and goes through Edit.

For Task: checks rule 3 (cost ask-gate).
For Edit/Write/MultiEdit: checks rule 1, and publishes the editing-state
signal (see write_editing_marker) — not a rule, a side effect that can
never block or fail a tool call.
For Bash/PowerShell: checks rule 2 (git safety) only.
"""

import datetime
import json
import os
import re
import shlex
import sys


# How long a pre-change snapshot of an untracked method document is kept.
# NOT a chosen number: it is git's own `gc.reflogExpire` default, the window git
# keeps work that is no longer reachable from a branch. Snapshots exist because
# these documents have left git's history, so the undo window git itself
# provides is the figure this is derived from.
SNAPSHOT_WINDOW_DAYS = 90


# --- Git safety patterns ---

RESET_HARD = re.compile(r"\bgit\b.*\breset\b.*--hard\b")
# PUSH_FORCE is anchored to `git push` as the actual subcommand (git then
# whitespace then push), not `push` appearing anywhere after git. Without the
# anchor, `\bgit\b.*\bpush\b` let an unrelated `push` token satisfy the rule —
# e.g. a staged filename like `rezip-push-cli-flow.md`, where `\bpush\b` matches
# `-push-`. Combined with per-segment scanning (see _split_segments), this stops
# a `push`-bearing filename in one part of a compound command from pairing with
# a `-f` (e.g. an `rm -f`) elsewhere to trigger a false denial.
PUSH_FORCE = re.compile(r"\bgit\s+push\b.*(?:--force(?!-with-lease)\b|-f\b)")
# Blanket-add boundaries: a bare "." token only (explicit paths like
# ./scripts/x.py or .gitignore must pass), -A/--all as standalone flags.
BLANKET_ADD = re.compile(r'\bgit\b.*\badd\b.*(?:\s-A\b|\s--all\b|\s\.(?=\s|$|[;&|"\')]))')
# Commit boundaries: --amend and --allow-empty must not match -a / --all.
COMMIT_ALL = re.compile(r"\bgit\b.*\bcommit\b.*\s(?:-a\b|-am\b|--all\b)")
# Any commit, bare or `git -C <dir> commit`, for the conflict-marker refusal
# below: the repository is the -C path where one is given, the cwd otherwise.
GIT_COMMIT = re.compile(r"\bgit\b(?:\s+-C\s+(\"[^\"]+\"|'[^']+'|\S+))?\s+(?:\S+\s+)*?commit\b")


def _conflicted_tracked_file(repo_dir: str):
    """The first tracked file in `repo_dir` carrying a git conflict marker,
    or None. Read with `git grep` over the working tree, so an unresolved
    merge is found whether or not the file is staged; any failure — no git,
    not a repository — reads as none, since the guard is a backstop."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "grep", "-l", "-e", "^<<<<<<< ", "-e", "^>>>>>>> ", "--", "."],
            cwd=repo_dir, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    files = [f for f in result.stdout.splitlines() if f.strip()]
    return files[0] if files else None

# Shell control operators that separate independent command segments. The
# git-safety patterns are applied to each segment alone (see _split_segments),
# so tokens from unrelated segments can't combine across an `&&` / `;` / `|`.
# Order in the alternation matters: the two-char operators (`&&`, `||`) come
# before the single-char ones so `&&` isn't split as two empty `&` halves.
SEGMENT_SPLIT = re.compile(r"&&|\|\||[;|\n]")

# Destruction of the outbound register through the shell. The register has no
# git history to restore from — its folder is gitignored on every path — so an
# `rm`, a truncating redirect or a `mv` away from the name is final. Matched on
# the filename with either separator, since a segment may carry a Windows path.
# Deliberately narrow: it catches removal, truncation and rename, and lets
# everything that merely reads the file through.
SENT_REGISTER_DESTRUCTION = re.compile(
    r"(?:\brm\b|\bdel\b|\bRemove-Item\b|\bmv\b|\bmove\b|\bClear-Content\b|"
    r"\btruncate\b|(?<!>)>(?!>))[^\n]*INBOX[/\\]sent\.md"
    r"|INBOX[/\\]sent\.md[^\n]*\|\s*(?:Out-File|Set-Content)\b",
    re.IGNORECASE)

# Appended to every git-safety denial: the patterns match command text,
# not intent, so a denial can fire on a command that only carries the
# pattern as data.
# --- Structured shell writes ---
#
# A scripted write to a project file bypasses the editing tools entirely. It
# has happened repeatedly here — a heredoc'd Python splice used to remove work
# items from QUEUE.md because the edit looked too awkward to do by hand.
#
# So this catches the STRUCTURED forms only — a write whose target path is
# literally present and extractable. General shell parsing was considered and
# rejected: it is fragile, and false denials train workarounds, which is the
# worse failure. Anything that does not parse cleanly PASSES, and that limit is
# stated in the denial text rather than hidden.
#
# Matched: a Python invocation (heredoc or -c) containing a write-mode open() or
# a pathlib write_text/write_bytes.
#
# A LITERAL path is checked against the protected set and denied if it lands
# inside the project. A COMPUTED path — a variable, an f-string, a concatenation
# — used to fail open, and that fail-open was the whole cost of a real
# corruption: `python -c` with `p='QUEUE.md'` assigned one line earlier slipped
# straight past, matched a structural marker against the wrong occurrence, and
# wrote a QUEUE.md with six work items still in it. A later heredoc against the
# same file, this time with the path written out, was blocked correctly. One
# variable assignment was the entire difference. The same slip then recurred in
# the very session that diagnosed it, which is the strongest evidence available
# that knowing about a gap does not close it.
#
# So a computed target now DENIES rather than passing. The reasoning is that the
# guard cannot tell whether an unreadable target is protected, and "cannot tell"
# must not resolve to "allow" for a check whose whole job is preventing a
# silent clobber. It does not guess at the path — it says plainly that the
# target is unreadable and names the two ways forward.
#
# Accepted cost, stated rather than discovered: a python script writing to the
# session scratchpad with a computed path is denied too, and must write its path
# out literally. That is a small, visible tax; the alternative was a silent hole.
#
# Invoking a SCRIPT FILE is unaffected — this check reads the command's text,
# and `python scripts/reorder_queue.py QUEUE.md ...` contains no write call at
# all. The mover stays the sanctioned route for awkward queue edits.
# `py -c` used to escape this entirely: the alternation read `\bpy\s+-[0-9]`,
# which reaches `py -3.13` and nothing else. That is the worse half of the gap,
# because this project's own scripting rules steer sessions towards `py` and
# away from `python` — so the guard covered the invocation the rules discourage
# and missed the one they require. Widened to `\bpy\s+-`, which reaches -c, -m
# and the version flags alike.
#
# NOT widened to a bare `\bpy\b`, and the reason is a real false positive rather
# than caution: a word boundary sits before the `py` in `file.py`, so the bare
# form fires on any command merely naming a Python file — including invoking the
# queue mover, the one scripted route this check exists to keep open. Requiring
# a following flag costs nothing a real invocation has.
PY_INVOCATION = re.compile(r"\bpython[0-9.]*\b|\bpy\s+-")

# `sed -i` is the same fault in a different tool: an in-place rewrite of a
# project file, through a script rather than the editing tools. It ran here
# once, against QUEUE.md, and was harmless only because the scripts were empty.
# CLAUDE.md's file-safety rules already name it; nothing enforced them.
#
# Same narrowness as the Python patterns: the flag must be present and the
# target must be a literal path in the command text. GNU `sed -i` takes an
# optional suffix attached to the flag (`-i.bak`); BSD takes it as a separate
# argument (`-i ''`). Both forms are matched, and every remaining bare token
# that is not an option or a quoted script is treated as a target.
SED_INPLACE = re.compile(r"\bsed\b(?=[^;|&\n]*\s-i)")
# A raw/bytes string prefix is still a LITERAL path. `r'C:\Users\...'` is the
# ordinary way to write a Windows path in Python, and without this the literal
# extractor read none of them while has_computed_write_target read all of them
# as computed — so a scratchpad path spelled out in full was denied by a message
# promising that a literal scratchpad path passes. `f` is deliberately absent:
# an f-string interpolates, so it is genuinely computed.
PY_STR_PREFIX = r"(?:[rRbBuU]{1,2})?"

PY_OPEN_WRITE = re.compile(
    r"""\bopen\s*\(\s*""" + PY_STR_PREFIX
    + r"""(?P<q>['"])(?P<path>[^'"]+)(?P=q)\s*,\s*['"][waxr]*[wax]b?\+?['"]"""
)
PY_PATH_WRITE = re.compile(
    r"""\bPath\s*\(\s*""" + PY_STR_PREFIX
    + r"""(?P<q>['"])(?P<path>[^'"]+)(?P=q)\s*\)\s*\.\s*write_(?:text|bytes)\s*\("""
)

# The same two shapes with the path left unconstrained. Used only to spot a
# write call the literal patterns above could not read a path out of.
PY_OPEN_WRITE_ANY = re.compile(
    r"""\bopen\s*\(\s*(?P<arg>[^,()]+?)\s*,\s*['"][waxr]*[wax]b?\+?['"]"""
)
PY_WRITE_METHOD_ANY = re.compile(r"""\.\s*write_(?:text|bytes)\s*\(""")

# An `open(` whose first argument is BUILT BY A CALL — `os.path.join(...)`,
# `Path(...)` and the like — followed by a write mode. PY_OPEN_WRITE_ANY's
# argument class excludes parentheses and commas, so a call-built path matched
# neither the literal extractor nor the computed detector and sailed through
# both. The argument may contain at most ONE level of nested parentheses; a
# deeper nesting is not matched, which is an accepted limit of text-matching
# rather than parsing. A call-built path is computed by definition.
PY_OPEN_WRITE_CALL = re.compile(
    r"""\bopen\s*\(\s*(?P<arg>[A-Za-z_][\w.]*\s*\((?:[^()]|\([^()]*\))*\))"""
    r"""\s*,\s*['"][waxr]*[wax]b?\+?['"]"""
)

PATTERN_AS_DATA_NOTE = (
    "\n\nNote: this check matches the command's text, not its intent — a "
    "command that merely contains the pattern as data (a test string, "
    "quoting, documentation) is denied too. Assemble such strings at "
    "runtime instead of writing the pattern out literally."
)


# --- Helpers ---

# --- The decision log ([research-writes-passed-lock-unexplained]) ---
#
# Every decision this hook makes — allow, deny or ask — appends one line to
# `.throughliner/pre-tool-use.log` under the project root: clock time, the
# tool, the decision, the branch that decided, and the path or command it
# targeted. An allowed hook leaves no trace in the transcript, so a write
# that passed with no line here is a hook that did not run, or ran and
# exited without deciding — which is the case the log exists to make
# visible. The folder is the project's ignored `.throughliner/`, which
# already holds the snapshots. A failure to write never changes the decision.
#
# The file is pruned to its newest 500 lines on each append — about a
# session's worth of tool calls, derived from the run-cost measurements'
# 254–417 calls per run (workshop/resources/research/run-cost-measurements-
# 2026-08-28.md).
_DECISION_LOG_NAME = "pre-tool-use.log"
_DECISION_LOG_LINES = 500
_ctx = {"cwd": "", "tool": "", "target": "", "sid": ""}


def _log_decision(decision: str, branch: str) -> None:
    cwd = _ctx.get("cwd") or ""
    if not cwd:
        return
    target = (_ctx.get("target") or "").replace("\r", " ").replace("\n", " ")
    if len(target) > 200:
        target = target[:200] + "…"
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Sixth column: the session id. The user's door reads it back to find a
    # refusal of the same path in the SAME session, so the column is what
    # makes that match possible ([sweep-security-users-door-is-self-declared]).
    line = "%s\t%s\t%s\t%s\t%s\t%s\n" % (
        stamp, _ctx.get("tool") or "", decision, branch, target,
        safe_session_id(_ctx.get("sid") or ""))
    folder = os.path.join(cwd, ".throughliner")
    path = os.path.join(folder, _DECISION_LOG_NAME)
    try:
        os.makedirs(folder, exist_ok=True)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.read().splitlines(keepends=True)
        except OSError:
            lines = []
        lines.append(line)
        dropped = lines[:-_DECISION_LOG_LINES]
        lines = lines[-_DECISION_LOG_LINES:]
        if dropped:
            # Rotation ([decision-log-retention-too-short-for-audits]): every
            # line the prune drops is appended, in order, to a dated archive
            # beside the live file — one per month, read from the clock at
            # the prune — that nothing prunes. The live file stays the user's
            # door; an audit reads the archive. The bound is the month, not a
            # number.
            month = datetime.datetime.now().strftime("%Y-%m")
            archive = os.path.join(folder, "pre-tool-use-" + month + ".log")
            with open(archive, "a", encoding="utf-8", newline="") as f:
                f.write("".join(dropped))
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write("".join(lines))
    except OSError:
        pass


def _allow(branch: str) -> int:
    """An allow is a decision too, and it leaves a line like the others."""
    _log_decision("allow", branch)
    return 0


def _deny(reason: str, branch: str = "") -> int:
    _log_decision("deny", branch)
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    if _ctx.get("notice"):
        output["systemMessage"] = _ctx["notice"]
    _ctx["printed"] = True
    json.dump(output, sys.stdout)
    return 0


def _ask(reason: str, branch: str = "") -> int:
    """Surface a permission prompt the user approves or declines.

    Unlike _deny, "ask" does not block — it hands the decision to the user
    with the reason shown. Used by the subagent cost gate so a subagent
    spawn is never silent, while the user keeps full choice.
    """
    _log_decision("ask", branch)
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }
    }
    if _ctx.get("notice"):
        output["systemMessage"] = _ctx["notice"]
    _ctx["printed"] = True
    json.dump(output, sys.stdout)
    return 0


def _split_segments(command: str) -> list[str]:
    """Split a compound command into independent segments on shell control
    operators (`&&`, `||`, `;`, `|`, newlines).

    The git-safety patterns are matched per segment so a token in one segment
    can't pair with a token in another to satisfy a pattern — the cross-segment
    false-denial bug (a `push`-bearing filename in a `git add` segment combining
    with an `rm -f` segment to trigger PUSH_FORCE). Splitting is deliberately
    naive about quoting and escaping: an operator inside a quoted string would
    over-split, but over-splitting only ever narrows what each pattern sees, so
    it can cause a missed denial in a contrived case, never a new false one —
    the fail-safe direction for a guard whose job is removing false denials.
    """
    return SEGMENT_SPLIT.split(command)


def _bare_path(entry: str) -> str:
    """A Files bullet's text reduced to its path: surrounding backticks
    removed, and anything after a spaced dash dropped."""
    entry = entry.strip()
    for dash in (" — ", " - "):
        cut = entry.find(dash)
        if cut != -1:
            entry = entry[:cut]
    return entry.strip().strip("`").strip()


def _parse_build_files(build_path: str) -> list[str] | None:
    """Extract file paths from the build working file's Files: section.

    Returns None when no Files: section exists (no enforcement),
    an empty list when a section exists but lists nothing
    (method docs only), or the listed paths.

    Robust to a stray, content-bearing `Files: a, b, c` line — e.g. one
    copied into the Entry field from a batch's own text. Such a line used
    to shadow the real section: the parser latched onto the FIRST line
    starting with `Files:`, found no bare-path bullets beneath it, broke at
    the next prose line, and returned an empty list — which locked the build
    out of its own files (method docs only). Two changes fix that, and the
    pair is the fail-safe choice (a malformed file can never silently turn
    the lock off):

      - EVERY `Files:` line contributes; the scan never stops at the first.
        A non-bullet line ends only the current bullet run, not the whole
        scan, so a structured `Files:` section further down is still read.
      - A content-bearing `Files: a, b, c` line is not ignored — its
        comma-separated paths after the colon are taken directly. So even
        when an inline line is the ONLY `Files:` present, it yields a
        non-empty list (lock on, scoped) rather than None (lock off).

    A bare `Files:` header (nothing after the colon) opens a bullet section
    whose `- path` bullets are collected. found_section is set by any
    `Files:` line, so the None (no-enforcement) return is reserved for a
    file carrying no `Files:` line at all. Over-collecting is safe: an extra
    path only widens the allow-list to a file the build named anyway, never
    grants access to an unrelated file.

    Each bullet's path is taken with surrounding backticks removed and
    anything after a spaced dash (` — ` or ` - `) dropped, for the build
    working file and the freeform scope file alike
    ([freeform-scope-paths-matched-literally]): paths are written as code
    spans everywhere else in the method's documents, and a bullet copied in
    that shape used to carry the backtick characters into the stored entry
    and never match a real path.
    """
    files = []
    try:
        with open(build_path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return None

    in_bullets = False
    found_section = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("files:"):
            found_section = True
            inline = stripped[len("files:"):].strip()
            if inline:
                # Content-bearing line: take the comma-separated paths after
                # the colon. It does not open a bullet section — any bullets
                # that follow belong to a later bare `Files:` header.
                in_bullets = False
                for part in inline.split(","):
                    entry = part.strip()
                    if entry:
                        files.append(entry)
            else:
                # Bare header: the bullets beneath it are the paths.
                in_bullets = True
            continue
        if in_bullets:
            if stripped.startswith("- "):
                file_entry = _bare_path(stripped[2:])
                if file_entry:
                    files.append(file_entry)
            elif stripped and not stripped.startswith("-"):
                # End of this bullet run — but keep scanning: a later
                # `Files:` header (the real structured section) may follow.
                in_bullets = False
    if not found_section:
        return None
    return files


def _normalise(path: str) -> str:
    """Normalise a path for comparison."""
    return os.path.normcase(os.path.normpath(path))


def _is_inside(filepath: str, cwd: str) -> bool:
    """Check if a path sits inside the project folder.

    Used by the structured-shell-write check, which denies a scripted write to
    any project file rather than consulting the build's Files list. Paths
    outside the project are somebody else's business and pass.
    """
    norm = _normalise(filepath)
    root = _normalise(cwd)
    return norm == root or norm.startswith(root + os.sep)


# A sed script token, unquoted: s/a/b/, y|a|b|, s#a#b#, 1,3d, $d, 2,5p.
# Recognised so the script is never read as a target — which matters more now
# that quotes are resolved, since a quoted script arrives here unwrapped.
_SED_SCRIPT_TOKEN = re.compile(r"^(?:[a-z]?[0-9,$]*[a-z]?[/|,;#]|[0-9,$]+[a-z]{1,2}$)")


def _unquoted_tokens(segment: str):
    """The segment's tokens with shell quoting resolved, or None on a form
    that does not tokenise cleanly.

    Backslashes are kept literal — Windows paths carry them as separators, and
    treating them as escapes would mangle every such path into a token the
    resolution step cannot place.
    """
    lex = shlex.shlex(segment, posix=True)
    lex.whitespace_split = True
    lex.escape = ""
    lex.commenters = ""
    try:
        return list(lex)
    except ValueError:
        return None


def _sed_inplace_targets(command: str) -> list:
    """Literal file paths a `sed -i` segment names as its target.

    Same narrowness as the Python patterns: the in-place flag must be present
    and the target must be readable from the command's own text. Tokens are
    read with quoting RESOLVED: the live escape this closes was a quoted
    target path — every path on a machine whose folders carry spaces must be
    quoted, so skipping all quoted tokens (meant for the quoted script)
    skipped exactly the targets the check exists to catch. The script is told
    apart by its own shape instead. Where the segment does not tokenise
    cleanly, the old whitespace split with the quoted-token skip is the
    fallback, so a malformed command is never guessed at.
    """
    targets = []
    for segment in _split_segments(command):
        if not SED_INPLACE.search(segment):
            continue
        tokens = _unquoted_tokens(segment)
        quotes_resolved = tokens is not None
        if not quotes_resolved:
            tokens = segment.split()
        for token in tokens:
            if not token or token == "sed" or token.startswith("-"):
                continue
            if not quotes_resolved and token[:1] in "'\"":
                continue
            if _SED_SCRIPT_TOKEN.match(token):
                continue
            if "$" in token or "{" in token:
                continue
            targets.append(token)
    return targets


def structured_write_targets(command: str) -> list:
    """Literal file paths a structured shell write names as its target.

    Deliberately narrow. Returns paths only where the command is recognisably a
    Python invocation carrying a literal quoted path in its write call, or a
    `sed -i` naming a file. Anything else returns nothing and the command passes
    — a form that does not parse cleanly is never guessed at.
    """
    targets = _sed_inplace_targets(command)
    if not PY_INVOCATION.search(command):
        return targets
    for pattern in (PY_OPEN_WRITE, PY_PATH_WRITE):
        for m in pattern.finditer(command):
            path = m.group("path").strip()
            # A path carrying substitution syntax is computed, not literal —
            # the ambiguity case, so it is dropped rather than resolved.
            if path and "$" not in path and "{" not in path:
                targets.append(path)
    return targets


def has_computed_write_target(command: str) -> bool:
    """True if a Python invocation writes to a path this check cannot read.

    The counterpart to structured_write_targets(): that function returns the
    targets it CAN read, this one reports that a write call exists whose target
    it CANNOT. A caller denies on either — one because the target is protected,
    the other because whether it is protected is unknowable.

    Deliberately does not attempt to resolve the path. Guessing at a variable's
    value is the fragile general-parsing this module rejects; refusing to guess
    and saying so is not.
    """
    if not PY_INVOCATION.search(command):
        return False

    # A call-built first argument (`open(os.path.join(...), "w")`) is computed
    # by definition — there is no literal to read. Checked first because the
    # general pattern below cannot match an argument containing parentheses.
    if PY_OPEN_WRITE_CALL.search(command):
        return True

    for m in PY_OPEN_WRITE_ANY.finditer(command):
        arg = m.group("arg").strip()
        # A raw/bytes prefix is stripped before the quoting test, for the reason
        # given at PY_STR_PREFIX: `r'...'` is a literal path, and reading it as
        # computed is what denied a literal scratchpad write.
        body = re.sub(r"^[rRbBuU]{1,2}(?=['\"])", "", arg)
        quoted = len(body) >= 2 and body[0] in "'\"" and body[-1] == body[0]
        if not quoted:
            return True
        # A quoted string carrying shell or format substitution is computed
        # too — the literal extractor drops these for the same reason.
        if "$" in arg or "{" in arg:
            return True

    # Every literal Path("...").write_text( is also a .write_text( , so an
    # excess of the general shape means at least one call on a receiver whose
    # path could not be read.
    if len(PY_WRITE_METHOD_ANY.findall(command)) > len(
        PY_PATH_WRITE.findall(command)
    ):
        return True

    return False


def project_root(data: dict) -> str:
    """The project root every path test runs against.

    The hook payload's `cwd` follows Claude: after a shell `cd` into a nested
    project's inner repository it is the inner folder, and every path test
    then refuses the outer's own files ([scope-lock-root-follows-shell-cwd]).
    `CLAUDE_PROJECT_DIR` is the folder the session started in, exported into
    every hook's environment, so it is the root where it is set and holds
    SPEC.md. The one exception: a `cwd` inside a `.claude/worktrees/` folder
    is kept, since a linked-worktree session's started-in folder is the main
    checkout and would be the wrong root there.

    Copied into each hook rather than shared — the hooks run standalone from
    a copied plugin cache and cannot import a module. Change one, change all.
    """
    cwd = data.get("cwd", "") or ""
    env_root = os.environ.get("CLAUDE_PROJECT_DIR", "") or ""
    if not env_root or not os.path.isfile(os.path.join(env_root, "SPEC.md")):
        return cwd
    norm_cwd = os.path.normcase(os.path.normpath(cwd)).replace("\\", "/")
    if "/.claude/worktrees/" in norm_cwd + "/":
        return cwd
    return env_root


def safe_session_id(session_id: str) -> str:
    """A session id reduced to filename-safe characters.

    Identical to the editing marker's sanitiser, deliberately: the working
    files and the marker are the same kind of per-session artifact, and a
    second convention for the same job is how two things that must agree
    drift apart.
    """
    return re.sub(r"[^A-Za-z0-9._-]", "_", session_id or "unknown")


def working_file(cwd: str, kind: str, session_id: str) -> str:
    """This session's build or plan working file.

    Working files are per SESSION, not per project. They used to sit at
    `_build.md` and `_plan.md` in the project root, which made every check
    that keys on their existence ask "is there a build?" when it meant "is
    there a build FOR THIS SESSION?". The behaviour rules explicitly permit a
    planning session in one chat alongside a build in another, so a planning
    session would find `_build.md` present, conclude it was inside a build,
    and have the build's file list applied to writes it never agreed to.

    The name follows the editing marker's `<name>-<safe id>` shape rather
    than a per-session directory, and stays in the project root because that
    is where the docs and the FAQ already tell users to look.
    """
    return os.path.join(cwd, f"_{kind}-{safe_session_id(session_id)}.md")


def _is_method_doc(filepath: str, cwd: str, session_id: str) -> bool:
    """Check if a path is a method doc (QUEUE.md, LOG/, this session's working files).

    `session_id` is required, deliberately. It used to default to "", and a
    caller that omitted it resolved this session's working file as
    `_build-unknown.md` — a name that can never match, so every scoped build
    was denied every write to its own working file, with no error to say why.
    Without the default, a caller that forgets raises instead of failing
    silently.
    """
    norm = _normalise(filepath)

    if norm == _normalise(os.path.join(cwd, "QUEUE.md")):
        return True

    for kind in ("build", "plan"):
        if norm == _normalise(working_file(cwd, kind, session_id)):
            return True

    log_dir = _normalise(os.path.join(cwd, "LOG"))
    if norm.startswith(log_dir + os.sep) or norm == log_dir:
        return True

    return False


def _is_memory_dir(filepath: str) -> bool:
    """Check if a path is under the user's Claude memory directory.

    Claude's memory lives at a path shaped like `.../.claude/.../memory/...`
    — a `memory` directory somewhere beneath a `.claude` directory. Matched
    by path shape, never a hardcoded machine path, so it holds for every
    consumer regardless of where their home or project lives. Memory writes
    (user preferences, working style, communication feedback) are allowed at
    any time per the memory-boundary rules, so the scope-lock must not block
    them — this exemption mirrors the method-docs one.
    """
    norm = _normalise(filepath)
    parts = norm.split(os.sep)
    if ".claude" not in parts:
        return False
    claude_idx = parts.index(".claude")
    return "memory" in parts[claude_idx + 1:]


def _is_temp_dir(filepath: str, cwd: str) -> bool:
    """The project's `temp/` folder — writable in every session, build,
    planning or none, on the same ground as the scratchpad: it is gitignored
    and disposable by definition, and the co-authoring rule sends every
    draft there, so a build run reaching a draft step met a refusal
    ([rezip-drafts-need-a-permitted-path-in-a-build]). The shell-write check
    already let a `cp` into it through; permitting the editing tools makes
    the two routes agree."""
    norm = _normalise(filepath)
    temp_dir = _normalise(os.path.join(cwd, "temp"))
    return norm.startswith(temp_dir + os.sep)


def _is_plans_dir(filepath: str, cwd: str) -> bool:
    """Check if a path is the harness's plan-mode plans directory.

    Plan mode is a harness feature: it designates one file under the harness's
    plans directory as the only file the session may edit, and reads the plan
    back from it on exit. Permitted on the same ground as the scratchpad — it
    sits outside the repository, so nothing the scope-lock protects lives there.

    Without this the two rules fought and the workaround was worse than either:
    a session wrote its plan to the scratchpad and copied it across with a shell
    `cp`, which is a write the hook cannot see at all.

    Matched by path SHAPE — a `plans` directory somewhere beneath a `.claude`
    directory — exactly as the memory directory is, and never as a hardcoded
    machine path. The location was observed live rather than documented, and a
    harness fact can move between versions; a shape holds for every consumer
    wherever their home lives. A path inside the project is excluded, so a
    project that happens to contain a `.claude/plans` folder of its own is
    still governed.
    """
    norm = _normalise(filepath)
    parts = norm.split(os.sep)
    if ".claude" not in parts:
        return False
    claude_idx = parts.index(".claude")
    if "plans" not in parts[claude_idx + 1:]:
        return False
    cwd_norm = _normalise(cwd)
    if norm == cwd_norm or norm.startswith(cwd_norm + os.sep):
        return False
    return True


def _is_research_dir(filepath: str, cwd: str) -> bool:
    """Check if a path is under the project's workshop/resources/research/ folder.

    Research notes are filed under workshop/resources/research/<topic>.md the moment a
    finding is produced (skill-nonspecific-rules.md Research > Filing), and that
    filing is open to every session type — build, test, or audit. The
    scope-lock must not block it, so this folder is always editable, mirroring
    the method-docs and memory exemptions. Matched relative to the project
    root, so it holds wherever the project lives.

    A nested project keeps its workshop in the product subfolder — an
    immediate child of the project root holding its own `.git` — so the same
    folder under such a child is the project's research folder too. The child
    is recognised by the `.git` on disk, never by a configured name.
    """
    norm = _normalise(filepath)
    # Two forms: the workshop path every project gets, and `research/` at the
    # project root, which is where a project whose Parts block names a research
    # part keeps it ([hooks-name-old-workshop-paths]). A part named otherwise
    # goes through the user's door.
    # `workshop/resources/supplied/` rides the same exemption
    # ([user-material-permanent-home-at-planning]): text the user wrote or
    # attached, written unchanged, needs a committed home a planning session
    # may write, and the user's door cost a refusal and a second ask nobody
    # knew to give.
    for research_dir in (
        _normalise(os.path.join(cwd, "workshop", "resources", "research")),
        _normalise(os.path.join(cwd, "workshop", "resources", "supplied")),
        _normalise(os.path.join(cwd, "research")),
    ):
        if norm.startswith(research_dir + os.sep) or norm == research_dir:
            return True
    if not _is_inside(filepath, cwd):
        return False
    rel = os.path.relpath(os.path.normpath(filepath), os.path.normpath(cwd))
    parts = rel.replace("\\", "/").split("/")
    if len(parts) < 4 or parts[0] in ("", ".", ".."):
        return False
    child = os.path.join(cwd, parts[0])
    if not os.path.exists(os.path.join(child, ".git")):
        return False
    for nested_dir in (
        _normalise(os.path.join(child, "workshop", "resources", "research")),
        _normalise(os.path.join(child, "workshop", "resources", "supplied")),
    ):
        if norm.startswith(nested_dir + os.sep) or norm == nested_dir:
            return True
    return False


def _is_retired_terms_file(filepath: str, cwd: str) -> bool:
    """Check if a path is the project's workshop/resources/retired-terms.md.

    Exempt for a structural reason, not a convenient one. The method requires a
    session that retires a term to append it to this file. Retirement is
    discovered DURING a build — you find out a term is retired by retiring it —
    so it can never appear in a `Files:` list that /next computed from the work
    items before the build started. No amount of better self-scoping can fix
    that; the write is unschedulable by construction.

    Without this, the obligation was satisfiable only in a narrow undocumented
    window: denied during the build and anywhere in /done before the
    working file is deleted, and working only after, by accident of ordering.
    A session that hit the denial mid-close was told to ask the user to widen
    scope, which is a bad trade for a bookkeeping append.

    Two alternatives were weighed and lost. Stating the ordering in done.md
    works but leaves a trap for anyone who reorders /done, and the ordering
    that currently works is an accident rather than a design. Having /next
    widen `Files:` whenever a run touches rule-bearing files is more machinery
    than the problem deserves, and it guesses.

    This ships to consumers, who will never have the file. Accepted knowingly:
    a host-only branch inside a shipped hook costs more than an inert path
    check. Matched relative to the project root, like the research exemption.

    Note what is deliberately NOT swept in. SPEC.md is also outside the exempt
    set, and correctly so — a build may edit SPEC only by naming it in
    `Files:`, which is the whole point of the SPEC gate. It is not a second
    instance of this problem.
    """
    return _normalise(filepath) == _normalise(
        os.path.join(cwd, "workshop", "resources", "retired-terms.md"))


def _is_tools_file(filepath: str, cwd: str) -> bool:
    """True for `TOOLS.md` at the project root.

    The project's record of what it has on hand — a tool installed at a known
    path, a command that fails specifically from Claude's shell. Always
    writable, in a planning session and mid-build alike, because the moment a
    session learns such a fact is the moment it must be written down: a fact
    deferred to a queue item is a fact the next session re-derives, which is
    the cost this file exists to remove. next-build.md's environment check
    reads it before assuming a tool is absent and writes to it on learning
    one.

    Root-level and exact, so a `TOOLS.md` a user keeps inside a subfolder of
    their own app is not silently exempted from the scope-lock.
    """
    return _normalise(filepath) == _normalise(os.path.join(cwd, "TOOLS.md"))


def _is_inbox_dir(filepath: str) -> bool:
    """Check if a path is inside any project's INBOX folder.

    Two directions, and both must pass the scope-lock. Inbound: this project's
    own `INBOX/`, where an arriving message is archived after being triaged.
    Outbound: another project's `INBOX/`, which is where a message is delivered
    — that path sits outside this project entirely, so no cwd-relative check
    could recognise it. Matching on an `INBOX` path segment covers both.

    The scope-lock is not what protects the user here. Every outbound message
    is shown and approved before it is written (skill-nonspecific-rules.md, the
    cross-project INBOX channel) — a message leaving this project is an
    outward-facing action, and the user's approval is the backstop, exactly as
    it is for a feedback report.
    """
    norm = _normalise(filepath)
    parts = norm.replace("/", os.sep).split(os.sep)
    return _normalise("INBOX") in parts


def _is_scratchpad_dir(filepath: str, cwd: str) -> bool:
    """Check if a path is under the session's scratchpad directory.

    The harness gives each session a scratchpad directory OUTSIDE the repo,
    shaped like `<temp>/claude/<project-slug>/<session-id>/scratchpad/...` —
    a `scratchpad` directory sitting beneath a `claude` temp directory.
    skill-nonspecific-rules.md's Temporary-files rule actively instructs Claude to
    route scratch scripts and working files there, so the scope-lock must not
    block those writes — this exemption mirrors the method-docs, memory, and
    research exemptions.

    Matched tightly by path SHAPE, never a hardcoded machine path, so it holds
    for every consumer wherever their temp dir lives. Three conditions must all
    hold, keeping the whitelist scoped to the actual scratchpad and nowhere
    else: (1) a `scratchpad` path segment; (2) a `claude` segment somewhere
    above it (the harness scratchpad always sits under a `claude` temp dir);
    and (3) the path is OUTSIDE the project repo — scratch is never in-tree, so
    an in-repo `scratchpad/` folder stays under the normal scope-lock. Requiring
    all three keeps the scope-lock's containment value everywhere else.
    """
    norm = _normalise(filepath)
    parts = norm.split(os.sep)
    if "scratchpad" not in parts:
        return False
    sp_idx = parts.index("scratchpad")
    if "claude" not in parts[:sp_idx]:
        return False
    cwd_norm = _normalise(cwd)
    if norm == cwd_norm or norm.startswith(cwd_norm + os.sep):
        return False
    return True


def _is_snapshot_subject(filepath: str, cwd: str) -> bool:
    """Check whether a path is one of the project's own method documents.

    The set is the documents /setup scaffolds and the privacy posture offers to
    keep out of the repository — the ones whose only undo is git, and which
    therefore have no undo at all once they are untracked. Working files are
    deliberately absent: a build or plan working file is deleted at /done by
    design, so snapshotting it would preserve the thing /done removes.
    """
    norm = _normalise(filepath)
    for name in ("SPEC.md", "QUEUE.md", "CYCLES.md", "TOOLS.md", "CLAUDE.md"):
        if norm == _normalise(os.path.join(cwd, name)):
            return True
    for folder in ("LOG", "FAQ"):
        base = _normalise(os.path.join(cwd, folder))
        if norm.startswith(base + os.sep):
            return True
    return False


def _is_untracked(filepath: str, cwd: str) -> bool:
    """Is this file outside git's history, so that git holds no previous copy?

    Fails toward True on any error — no git, git missing from PATH, a timeout, a
    repository this file does not belong to. The two failure directions are not
    symmetrical: failing to False silently withdraws the safety net at exactly
    the moment nobody can tell it is gone, while failing to True costs a copy of
    a file git already holds. A wasted copy is the cheaper mistake, and the
    duplicate-collapse in _snapshot_before_write means an unchanging file makes
    no more than one of them.
    """
    try:
        import subprocess
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", filepath],
            cwd=cwd,
            capture_output=True,
            encoding="utf-8",
            timeout=5,
        )
        return result.returncode != 0
    except Exception:
        return True


def _snapshot_before_write(cwd: str, filepath: str) -> None:
    """Save the current contents of an untracked method document. Never raises.

    Write-first — Claude writes to a project document and then reports what
    landed — rests on one test: is the previous version recoverable without the
    user's help? For a tracked document git answers yes. For an untracked one
    nothing did, so the rule used to flip those documents to show-first. This
    supplies the recoverability itself instead, and write-first stays.

    Placed before the scope checks so the copy exists before the write does. A
    write that is then denied leaves one extra snapshot behind, which the
    duplicate-collapse below absorbs.

    PRUNE DEPTH, and the derivation it is required to state. Snapshots stand in
    for the history these files no longer have, so the window is git's own: the
    `gc.reflogExpire` default of 90 days, which is how long git itself keeps
    work that is no longer reachable from a branch. Within that window every
    DISTINCT version is kept — an identical re-write adds nothing — so the
    folder holds what git's history would have held for these files, and no
    count is invented.
    """
    try:
        if not _is_snapshot_subject(filepath, cwd):
            return
        if not os.path.isfile(filepath):
            return
        if not _is_untracked(filepath, cwd):
            return

        rel = os.path.relpath(filepath, cwd).replace(os.sep, "__")
        snap_dir = os.path.join(cwd, ".throughliner", "snapshots")
        os.makedirs(snap_dir, exist_ok=True)

        with open(filepath, "rb") as handle:
            current = handle.read()

        existing = sorted(
            name for name in os.listdir(snap_dir)
            if name.startswith(rel + "@")
        )

        # Duplicate collapse: an unchanged file adds no version.
        if existing:
            newest = os.path.join(snap_dir, existing[-1])
            try:
                with open(newest, "rb") as handle:
                    if handle.read() == current:
                        return
            except OSError:
                pass

        stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S%f")
        with open(os.path.join(snap_dir, f"{rel}@{stamp}"), "wb") as handle:
            handle.write(current)

        _prune_snapshots(snap_dir)
    except Exception:
        return


def _prune_snapshots(snap_dir: str) -> None:
    """Drop snapshots older than git's own reflog-expiry window. Never raises."""
    try:
        cutoff = datetime.datetime.now() - datetime.timedelta(
            days=SNAPSHOT_WINDOW_DAYS)
        for name in os.listdir(snap_dir):
            _, _, stamp = name.rpartition("@")
            try:
                taken = datetime.datetime.strptime(stamp, "%Y%m%dT%H%M%S%f")
            except ValueError:
                continue
            if taken < cutoff:
                try:
                    os.remove(os.path.join(snap_dir, name))
                except OSError:
                    continue
    except Exception:
        return


def write_editing_marker(cwd: str, session_id: str, filepath: str, active: bool) -> None:
    """Publish the editing-state signal a companion app reads. Never raises.

    A live Markdown reader/editor open on the same file as Claude needs to know
    when Claude is writing, so the two don't land on each other mid-sentence.
    Inferring that from file-modification times was rejected: a watcher can see
    THAT a file changed but not WHO changed it, and can never tell "finished"
    from "paused to think" — and a wrong guess locks the user out of their own
    document.

    So this is a HEARTBEAT, not a lock. The marker always carries a fresh
    timestamp, and a reader treats a stale marker as "not editing" whatever the
    flag says. That staleness rule is the safety property: a session that
    crashes between starting a write and finishing one leaves a flag stuck on,
    and without staleness the reader would lock the user out permanently —
    reintroducing the exact harm the timing-guess approach was rejected for.

    One file PER SESSION, `editing-<session-id>.json`, because two Claude
    sessions in one project is a supported shape. With a single shared file,
    session A finishing a write would clear the flag while session B was still
    writing. Per-session files make the reader's rule trivially correct:
    editing is happening if ANY file here is active and fresh.

    Errors are swallowed in full: a companion-app convenience must never be able
    to block or fail the user's actual work.
    """
    try:
        import datetime

        marker_dir = os.path.join(cwd, ".throughliner")
        os.makedirs(marker_dir, exist_ok=True)
        safe_id = re.sub(r"[^A-Za-z0-9._-]", "_", session_id or "unknown")
        # Project-relative path, forward slashes, no leading "./" — version 2's
        # contract. Relative paths carry no account name (the privacy reason
        # this changed: the folder syncs, and gitignore never stopped that) and
        # resolve correctly against a synced copy on another machine. A file
        # outside the project falls back to its absolute path — a marker must
        # never lie about which file is being edited.
        if filepath:
            rel = os.path.relpath(os.path.abspath(filepath), cwd)
            marker_path = (
                os.path.abspath(filepath)
                if rel.startswith("..")
                else rel.replace(os.sep, "/")
            )
            files = [marker_path]
        else:
            files = []
        payload = {
            # `version` leads and is non-negotiable: another application is
            # built against this contract, so it must be able to recognise a
            # format it doesn't understand and fall back safely. A reader that
            # cannot parse this field defaults to 1, so version 2's
            # project-relative paths MUST NOT ship under a version-1 stamp —
            # they would resolve against the wrong root and hold nothing,
            # silently. Bumped to 2 when `files` went project-relative.
            "version": 2,
            # Must be a real boolean. A reader skips the marker entirely if
            # this is absent, the string "true", or 1.
            "active": bool(active),
            # Named for what it is safe to use it for: diagnosis. Freshness
            # comes from the marker file's own local mtime, never this field —
            # a synced marker carries another machine's clock, and comparing
            # that against the local clock fails closed (a dead session looks
            # permanently current). The old name `updated` invited exactly
            # that comparison. Nothing reads this field.
            "written_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            # Must be a list. Absent or non-list reads as empty.
            "files": files,
            # A format constant naming what wrote the marker, deliberately the
            # format's own name rather than the plugin slug so a product
            # rename never breaks a published value. `pid` and `session` were
            # dropped at version 2: written by these hooks, read by nothing —
            # pid is unusable across machines and redundant on one, session
            # restates the filename.
            "producer": "throughliner",
        }
        with open(
            os.path.join(marker_dir, f"editing-{safe_id}.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(payload, f)
    except Exception:
        return


def _is_plan_quiet_path(filepath: str, cwd: str) -> bool:
    """True for the files a session with no build working file may write.

    This is the planning session's STANDING list — QUEUE.md, SPEC.md (the
    root's, and a part's SPEC.md at any depth), CYCLES.md, LOG/ and
    FAQ/, plus the memory directory, `workshop/resources/research/`, the scratchpad and
    any INBOX (checked by their own helpers at the call site). Everything else
    is DENIED.

    This used to ask rather than deny, and the comment here instructed future
    sessions not to "improve" the ask into a denial. Both are reversed on the
    user's decision, after she re-argued the point over a period of weeks. Her
    reason: an ask that gets waved through is not consent — just because Claude
    asks for an edit does not mean the user reads the request in full and
    understands what it means.

    The old justification was also wrong on its own terms, and is evicted with
    it. It read "here there is no agreed list", which is false: a build has a
    list agreed for one specific piece of work, and a planning session has a
    standing list — the same few paths every time. Nothing needs restoring for
    this to work, and in particular the `_plan-<id>.md` working file deleted from
    the method on 2026-08-14 must not come back: a fixed list needs no per-session
    file to hold it.

    `workshop/resources/research/` is on the list because it must be. plan.md's own ground
    rules resolve research in-session, and the always-loaded rules REQUIRE a
    finding to be filed as part of using it — so denying that path would break a
    shipped duty rather than merely inconvenience a session.

    What a denial costs, stated rather than discovered: a genuinely needed write
    outside the list now stops the session and becomes a queue item, where before
    it was one sentence. That is the point. plan.md already says a planning
    session never builds — that work outside its surface is queued, not done here
    — so this adds no rule; it makes an existing one mechanical, and the stop is
    what makes the write visible.

    Keyed on the build working file being absent rather than on "a planning
    session", because absence is what the code can actually see — and that is also
    what makes the gate cover a freeform session, which has the same condition.

    One session kind is excluded, and it is excluded by its own declaration
    rather than by widening this list: /setup writes a marker into the session
    scratchpad for the length of its run (see _setup_marker_present), and the
    caller allows any write while that marker exists. /setup never creates a
    build working file, so without the exclusion it is classified here and every
    write its migration path makes — the version and format-epoch markers, the
    managed CLAUDE.md block, .gitignore — is denied with no prompt.
    """
    if not _is_inside(filepath, cwd):
        return False
    # Build the relative path from paths that have NOT been normcased, then
    # normcase each side of the comparison instead. `_normalise` lowercases on
    # Windows, so feeding it in here produced `queue.md`, which could never
    # match the literals below — the gate was inverted on Windows for every
    # user of it. `os.path.relpath` compares case-insensitively internally on
    # Windows while returning the original components, so passing raw paths is
    # safe. `os.path.normcase` is the identity on POSIX, so exact matching is
    # preserved there.
    rel = os.path.relpath(os.path.normpath(filepath), os.path.normpath(cwd))
    rel = os.path.normcase(rel).replace("\\", "/")
    # CYCLES.md is on the list because plan.md's own cycle-authoring rule
    # directs a planning session to write the definition doc in the session
    # that agrees it — a cycles doc a planning session cannot write is a rule
    # that can never run where it fires.
    quiet_files = ("QUEUE.md", "SPEC.md", "CYCLES.md")
    if rel in tuple(os.path.normcase(name) for name in quiet_files):
        return True
    # A part's own SPEC.md, at any depth inside the project — a nested
    # project's inner repository included. Planning writes a decision's
    # sentence into the spec of the part it concerns, so the file is matched
    # by name wherever it sits; the folder is the part's, the filename is
    # fixed by convention, and nothing else named SPEC.md exists to collide.
    if rel.split("/")[-1] == os.path.normcase("SPEC.md"):
        return True
    # A build working file, whichever session owns it. Matched by shape rather
    # than by this session's id: writing to another session's working file
    # should be rare, but it is a working-state write either way and the quiet
    # list is about noise, not about scope. The scope-lock enforces ownership.
    #
    # `_plan-<id>.md` was matched here too until the planning working file was
    # deleted from the method (2026-08-14). A session with no build working file
    # is now writing QUEUE.md, SPEC.md and LOG/ and nothing else by design, so a
    # `_plan-` write is exactly the surprise this gate should surface.
    # `_freeform-<id>.md` is matched alongside it: a freeform session's first
    # write is its own scope file, which must pass before the paths it declares
    # can.
    if re.match(r"^_(build|freeform)-[a-z0-9._-]+\.md$", rel):
        return True
    if rel.startswith(os.path.normcase("LOG") + "/"):
        return True
    # FAQ/ is on the list for the same reason workshop/resources/research/ is: /done
    # REQUIRES an FAQ disposition, so denying the path would break a mandated
    # step rather than merely inconvenience a session. Recovered from the
    # pre-reversion version of this gate, which carried it and said so; the
    # 2026-08-15 design was authored without it and would have shipped the break.
    #
    # templates/ is deliberately NOT here, and that asymmetry is a decision.
    # Editing a template changes what every future consumer receives, which is
    # exactly the class of change this gate exists to stop happening in a
    # planning session.
    #
    # EXCEPT the two FAQ templates, widened 2026-08-28 by exactly that pair and
    # no further. The announcement-time FAQ rule requires the entry to be
    # written in the same turn as the sent-register line, and the FAQ template
    # is canonical while FAQ/ is a copy of it — so under the unwidened list the
    # rule and this lock were two standing laws in direct collision, which fired
    # at every bot-posted announcement and did so twice in two days. Same
    # ground as FAQ/ itself: denying the path breaks a mandated step rather
    # than merely inconveniencing a session. The rest of templates/ stays
    # denied.
    #
    # CLAUDE.md is NOT here either, and that is intended behaviour rather than
    # an oversight — recorded because the question has now been raised three
    # times from three separate readings of this same list, and a denial with no
    # stated reason gets re-litigated by every session that meets it.
    #
    # The objection runs: in the method's own repository CLAUDE.md holds the rule
    # gate, and the gate's whole design argument is that only /plan can refuse a
    # rule — so a planning session that admits a rule and then cannot write it
    # has to queue the write as a build, which looks like the placement the gate
    # rejects.
    #
    # It conflates deciding with writing. The gate runs at the decision step, and its
    # output is a DISPOSITION on the queue item; the rule TEXT is written by the
    # build that item schedules. What the gate refuses is a build deciding
    # whether a rule may exist, never a build typing out a rule /plan already
    # admitted. The session that settled this dispositioned fifteen rule changes
    # at the decision step and queued every one as a build, with nothing blocked and
    # no decision moved downstream.
    #
    # It is also genuinely unlike the three exceptions fixed the same day — the
    # rezip's plugin.json, /done's README.md, and /setup's markers. Each of
    # those was a required write with no permitted moment anywhere in the method.
    # This write has a proper home.
    if rel.startswith(os.path.normcase("FAQ") + "/"):
        return True
    # Literals written lowercase with forward slashes, matching how `rel` was
    # built above. Passing them through os.path.normcase would swap in
    # backslashes on Windows and never match — the same inversion the comment
    # above records for QUEUE.md.
    if rel in (
        "plugin/throughliner/templates/faq-template.md",
        "plugin/throughliner/templates/faq-index-template.md",
    ):
        return True
    # The plugin's own version manifest. HOST-ONLY BY RESIDENCE: this path exists
    # only in the repository that develops the method, so in a consumer project
    # the permission is a no-op — there is nothing at that path to write.
    #
    # It is here because the rezip has no other route. A rezip bumps the `-testN`
    # suffix in this one file, and it runs after a close, which has already
    # deleted the build working file — so under the standing list every chat the
    # rezip can run in is classified as planning and its first step is denied.
    # There was no permitted chat shape at all.
    #
    # ONE PATH, not the folder: a sibling under plugin/throughliner/ is still
    # denied, so this cannot be read as opening the package to planning chats.
    # A self-declared marker like /setup's was refused for the same reason —
    # that is a full bypass, and this write is one field in one file.
    #
    # The `.replace` is load-bearing: on Windows `os.path.normcase` turns `/`
    # into `\`, so a multi-component literal must be put back into the same
    # forward-slash form `rel` carries or it can never match. The single-component
    # literals above escape this because they contain no separator.
    if rel == os.path.normcase(
        "plugin/throughliner/.claude-plugin/plugin.json"
    ).replace("\\", "/"):
        return True
    # The rezip archive. HOST-ONLY BY RESIDENCE, like the manifest above: the
    # folder exists only in the repository that develops the method, so in a
    # consumer project this permits nothing that exists.
    #
    # Same shape of failure as the manifest's, found the same way — live, on the
    # archive step's first ever run. The rezip archives each build's zip and
    # readme at the one moment the folder is provably the installed build, and a
    # rezip runs after a close, so the session is classified as planning and the
    # write is denied. There is no permitted chat shape for it either.
    #
    # A FOLDER here where its sibling is one path, which is a step beyond that
    # precedent and is said plainly rather than passed off as the same move. It
    # is defensible because `plugin/rezip-archive/` is gitignored build output
    # rather than part of the plugin package: permitting it opens nothing under
    # `plugin/throughliner/`, where a sibling write is still denied.
    #
    # SUPERSEDED WHEN [ritual-declares-writable-paths] SHIPS **and** the rezip
    # exists as a checklist definition declaring this path — not before, or the
    # rezip loses its only permitted route.
    if rel.startswith(os.path.normcase("plugin/rezip-archive")
                      .replace("\\", "/") + "/"):
        return True
    return False


CYCLES_DOC = "CYCLES.md"
# The paths a definition declares its steps write. Matched with the same
# tolerance the cycles parser gives Cadence:, Observable: and Trigger: — the
# label plain or bolded — because these are written by hand in a document a
# person reads.
CYCLE_WRITES_RE = re.compile(r"^\s*\*{0,2}Writes\s*:\*{0,2}\s*(.+?)\s*$",
                             re.IGNORECASE)


def _checklist_declared_paths(cwd: str) -> list[str]:
    """Paths the project's own cycles doc declares its checklists' steps write.

    A checklist's steps routinely need somewhere outside the planning session's
    standing list — a build folder, a generated artifact — and the alternative
    is a carve-out in this file per checklist, which has now been written twice.
    So a definition names the paths it writes and the lock reads them.

    **This is not the self-declared marker refused beside the manifest
    carve-out.** That objection is against a session granting itself
    permission. A checklist's declaration lives in CYCLES.md, written at a
    planning session with the user present and committed — exactly as a
    `[freeform]` session's list comes from a queued item's Files line. Who
    wrote the permission and when is the distinction, not whether a file is
    read at check time. Keep that true or this becomes the refused thing.

    **Declared paths are permitted whenever the project is open, not only while
    the checklist runs**, on the user's decision of 2026-08-29. The cost is stated
    rather than buried: a declared path is writable in any session. Nothing
    needs to detect which checklist is running, and the manifest carve-out has
    worked this way unconditionally with nothing going wrong.

    The field is read wherever it appears rather than only on definitions with
    no cadence: the authoring rule sites it on checklists, but a cycle whose turn
    runs a checklist's steps has the identical need, and a definition that declares
    nothing contributes nothing either way.

    A project with no cycles doc gets an empty list and pays one `isfile`.
    """
    path = os.path.join(cwd, CYCLES_DOC)
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except OSError:
        return []

    declared = []
    index = 0
    while index < len(lines):
        match = CYCLE_WRITES_RE.match(lines[index])
        index += 1
        if not match:
            continue
        # The field's own line, then its continuation lines: a field the
        # editor wrapped keeps its tail on the lines beneath, up to the next
        # blank line, heading or field ([writes-field-wrapped-paths-honoured]).
        text = match.group(1)
        while index < len(lines) and lines[index].lstrip().startswith("`"):
            # A continuation line is one more run of backticked paths; prose
            # or a blank line ends the field.
            text += " " + lines[index].strip()
            index += 1
        for chunk in text.split(","):
            chunk = chunk.strip().strip("`").strip().replace("\\", "/")
            chunk = chunk.lstrip("./")
            # A declaration of the project root itself would permit everything,
            # which is the one shape that turns this into the bypass above.
            if chunk and chunk not in ("/", ".."):
                declared.append(chunk.rstrip("/"))
    return declared


def _is_checklist_declared_path(filepath: str, cwd: str) -> bool:
    """True where the cycles doc declares this path, or a folder above it."""
    if not _is_inside(filepath, cwd):
        return False
    rel = os.path.relpath(os.path.normpath(filepath), os.path.normpath(cwd))
    rel = os.path.normcase(rel).replace("\\", "/")
    for declared in _checklist_declared_paths(cwd):
        target = os.path.normcase(declared).replace("\\", "/")
        if rel == target or rel.startswith(target + "/"):
            return True
    return False


def _freeform_scope_files(cwd: str, session_id: str) -> list[str]:
    """Paths this session's freeform scope file declares editable.

    A freeform session runs with no build working file, so Rule 4's standing
    list used to deny it the very files its own queue item names — the
    2026-08-21 freeform sitting was worked around by hand, on approval, once
    per file. The fix mirrors the build's mechanism rather than inventing one:
    the session writes `_freeform-<session-id>.md` (same location and naming
    shape as the build working file) carrying a `Files:` section, and those
    paths EXTEND the standing list for that session only. The list comes from
    the freeform item's instructions, or — in any no-build session — from the
    user's repeated direction, one path at a time; this parser reads the file
    and consults no queue either way.

    Reuses _parse_build_files, deliberately — one parser, one format, one set
    of parsing bugs. Returns an empty list when no scope file exists (standing
    list unchanged) or when one exists but lists nothing: an empty declaration
    widens nothing, the fail-safe direction.

    Reusing the build working file itself was refused at the decision step: the
    close and the one-build-at-a-time rule read that file as a build's.
    """
    path = working_file(cwd, "freeform", session_id)
    if not os.path.isfile(path):
        return []
    return _parse_build_files(path) or []


def _door_refused_earlier(filepath: str, cwd: str, session_id: str) -> bool:
    """True where this session's decision log holds a deny of this same path.

    The user's door — a scope file in a no-build session — opens only after
    the safety check has itself refused that path earlier in the same session
    ([sweep-security-users-door-is-self-declared]). The hook cannot tell a
    scope file written on the user's word from one a session wrote to get past
    a refusal, so this ties the door to the one thing it can read: its own
    log. Matched on the session id column and the path, normalised; lines
    from before the column existed carry no id and never match.
    """
    path = os.path.join(cwd, ".throughliner", _DECISION_LOG_NAME)
    if not os.path.isfile(path):
        return False
    sid = safe_session_id(session_id)
    want = _normalise(filepath)
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for raw in f:
                parts = raw.rstrip("\r\n").split("\t")
                if len(parts) < 6 or parts[2] != "deny" or parts[5] != sid:
                    continue
                if _normalise(parts[4]) == want:
                    return True
    except OSError:
        return False
    return False


SETUP_MARKER_NAME = ".throughliner-setup-active"
CLOSE_MARKER_NAME = ".throughliner-close-active"
# The /done marker's home since [scratchpad-refused-after-resume-close-marker]:
# `.throughliner/close-active-<session-id>` in the project's own working
# folder, which every session may write. The scratchpad was refused to a
# session whose plugin had been swapped under it, and a marker the close
# cannot write is the failure.
CLOSE_MARKER_PREFIX = "close-active-"


def _close_marker_present(cwd: str, session_id: str) -> bool:
    """True while THIS session's close marker stands in `.throughliner/`."""
    safe_id = safe_session_id(session_id)
    if safe_id == "unknown" or not cwd:
        return False
    return os.path.isfile(os.path.join(cwd, ".throughliner",
                                       CLOSE_MARKER_PREFIX + safe_id))


# The marker /done writes after its commit, read by the stop check's tail
# offer ([post-close-tail-offer-enforced-once]).
SESSION_CLOSED_MARKER_PREFIX = "session-closed-"


def _is_own_close_marker(filepath: str, cwd: str, session_id: str) -> bool:
    """True where `filepath` is one of THIS session's two close markers in
    `.throughliner/` — `close-active-<id>` or `session-closed-<id>` — so the
    editing tools may write them in every session type
    ([close-markers-refused-by-safety-check]). The read side above resolves
    the same name from the same id, so another session's id never matches.
    """
    safe_id = safe_session_id(session_id)
    if safe_id == "unknown" or not cwd:
        return False
    norm = _normalise(filepath)
    return any(
        norm == _normalise(os.path.join(cwd, ".throughliner", prefix + safe_id))
        for prefix in (CLOSE_MARKER_PREFIX, SESSION_CLOSED_MARKER_PREFIX)
    )


# --- The plugin changed under a live session ---
# ([scratchpad-refused-after-resume-close-marker], the sender's correction):
# a session opened on one version and, after a gap, ran on another, with the
# rules it read at its opening gone from the cache. The opening writes the
# version it ran as into the decision log; this hook, on its first decision
# in the session, compares that with the version it runs as and says once
# where they differ. Facts only: nothing here changes a decision.
OPENED_BRANCH = "session opened"


def _plugin_version_running() -> str:
    root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if not root:
        return ""
    try:
        with open(os.path.join(root, ".claude-plugin", "plugin.json"), "r",
                  encoding="utf-8") as f:
            return str(json.load(f).get("version", "") or "")
    except (OSError, ValueError, AttributeError):
        return ""


def _session_opened_version(cwd: str, session_id: str) -> str:
    """The version the opening logged for this session, or ""."""
    safe_id = safe_session_id(session_id)
    path = os.path.join(cwd, ".throughliner", _DECISION_LOG_NAME)
    found = ""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                cols = line.rstrip("\r\n").split("\t")
                if len(cols) >= 6 and cols[3] == OPENED_BRANCH \
                        and cols[5] == safe_id \
                        and cols[4].startswith("version "):
                    found = cols[4][len("version "):].strip()
    except OSError:
        return ""
    return found


def _version_change_notice(cwd: str, session_id: str) -> str:
    """One notice, once per session, where the plugin under it changed."""
    if not cwd or not _fire_once(cwd, session_id, "version-checked"):
        return ""
    opened = _session_opened_version(cwd, session_id)
    running = _plugin_version_running()
    if not opened or not running or opened == running:
        return ""
    return (
        f"[Throughliner] The plugin under this session changed: it opened on "
        f"{opened} and is now running {running}. The rules it read at its "
        "opening may no longer be the installed ones; a fresh chat carries "
        "the new version."
    )
# Left where /setup used to delete its marker: "setup ran in this chat". While
# it stands together with the /done marker, the /done run of that same chat
# may write the files setup scaffolds ([setup-close-cannot-fix-setup-output]).
# /done deletes it as its last action. On its own — a planning run before
# /done — it opens nothing.
SETUP_DONE_MARKER_NAME = ".throughliner-setup-done"

# The files /setup scaffolds, which its own chat's close may correct. Relative
# to the project root; SPEC.md matches at any depth (a part's spec), FAQ/ as a
# folder. `.claude/settings.local.json` is where the brevity style is written.
SETUP_SCAFFOLD_FILES = (
    "CLAUDE.md", ".gitignore", ".throughliner-version",
    ".throughliner-format-epoch", ".claude/settings.local.json",
)

# The method's own skills, all of which ship with model invocation disabled.
# Lowercased, and compared against the part of a skill name after any plugin
# prefix. Adding a skill to the method means adding it here.
METHOD_SKILLS = frozenset({"setup", "plan", "next", "rescan", "done"})

# The files the method's own CLOSE obligations name. A close is required to write
# these and a build is not, and the two phases share one working file — so
# without this a required write had no permitted moment anywhere.
#
# README.md is the recorded case. The README feature-list sync rides the
# SPEC-sync trigger, which fires at /done; /next self-scopes from the items
# it is about to build, and no item names README.md because the obligation is a
# consequence of several items TOGETHER. So the file could not have entered the
# build's list by any correct application of the scoping rule, and three
# genuinely required corrections were denied — one of them stale text about a
# permission that had already been withdrawn.
#
# THE COST, stated rather than discovered: this is a second list to maintain. A
# close obligation added later that names a new file must be added here in the
# same build, or the identical denial recurs one file over.
#
# It widens a BUILD's scope not at all — the marker below is written by /done
# and removed at its end, so during the build these paths are denied exactly as
# they were.
CLOSE_PHASE_FILES = ("README.md",)


def _setup_marker_present(session_id: str) -> bool:
    """True while /setup has declared itself for THIS session.

    /setup writes `.throughliner-setup-active` into its session scratchpad at
    the start of a run and `.throughliner-setup-done` beside it at the end —
    the active marker is left where it is, since renaming it fails in
    PowerShell where the scratchpad path carries an 8.3 short name
    ([setup-done-marker-rename-fails-in-powershell]) — so the door is open
    only while the active marker stands WITHOUT the done marker. A session
    carrying the open door is neither a planning session nor a build, so the
    standing list does not apply to it.

    The scratchpad is the marker's home for two reasons. It is already writable
    in every session type, so /setup can declare itself without being stopped by
    the very lock this works around; and it clears itself, so a run that dies
    mid-setup leaves nothing to clean up by hand.

    Matched by path SHAPE under the system temp directory —
    `<temp>/claude/<project-slug>/<session-id>/scratchpad/` — never a hardcoded
    machine path, and scoped to this session's own id so one project's setup run
    cannot unlock another session. Never raises: a scratchpad that cannot be
    read reports no marker, which leaves the lock ON, the fail-safe direction.

    Widening the standing list instead was weighed and refused: /setup's targets
    are the files the lock most exists to protect, and listing them would open
    them for every planning session in every consumer project to fix a condition
    that is only true during setup.
    """
    if _scratchpad_marker_present(session_id, SETUP_DONE_MARKER_NAME):
        return False
    return _scratchpad_marker_present(session_id, SETUP_MARKER_NAME)


def _scratchpad_marker_present(session_id: str, marker_name: str) -> bool:
    """True while THIS session's scratchpad carries `marker_name`.

    The shared mechanism behind the /setup marker and the /done marker. Matched
    by path shape under the system temp directory and scoped to this session's
    own id, so one project's run cannot unlock another's. Never raises: a
    scratchpad that cannot be read reports no marker, which leaves the lock ON.
    """
    try:
        import glob
        import tempfile

        safe_id = safe_session_id(session_id)
        if safe_id == "unknown":
            return False
        pattern = os.path.join(
            tempfile.gettempdir(), "claude", "*", safe_id, "scratchpad",
            marker_name,
        )
        return bool(glob.glob(pattern))
    except Exception:
        return False


def _is_setup_close_file(filepath: str, cwd: str, session_id: str) -> bool:
    """True for a scaffolded file while this chat's close follows its setup.

    Both markers must stand: `.throughliner-close-active` (this is a /done
    run) and `.throughliner-setup-done` (setup ran earlier in this same chat).
    The recorded instance: a consumer's first /done run found two corrections
    to what setup had just written — a CLAUDE.md line, a .gitignore line — and
    the standing list refused both, so the consumer's first queue opened with
    a cleanup item for the method's own scaffolding.

    Leaving the setup marker standing until the /done run was refused: a
    planning run in between would inherit setup's whole write set.
    """
    if not _close_marker_present(cwd, session_id):
        return False
    if not _scratchpad_marker_present(session_id, SETUP_DONE_MARKER_NAME):
        return False
    if not _is_inside(filepath, cwd):
        return False
    rel = os.path.relpath(os.path.normpath(filepath), os.path.normpath(cwd))
    rel = os.path.normcase(rel).replace("\\", "/")
    if rel in tuple(os.path.normcase(n) for n in SETUP_SCAFFOLD_FILES):
        return True
    if rel == os.path.normcase("SPEC.md") or rel.endswith("/" + os.path.normcase("SPEC.md")):
        return True
    return rel.startswith(os.path.normcase("FAQ") + "/")


def _is_close_phase_file(filepath: str, cwd: str, session_id: str) -> bool:
    """True for a close-obligation file while this session's close is running.

    Two conditions, and both must hold: /done has declared itself with a
    scratchpad marker, and the path is one the method's close obligations name
    (CLOSE_PHASE_FILES). Outside /done the marker is absent and these paths
    are denied exactly as before, so a build's scope is unchanged.

    The marker rather than a standing permission, because the hook has no other
    way to tell a /done run from the build that preceded it — they share one working
    file, and the build's Files list is what denies the write. This copies
    /setup's declaration mechanism rather than inventing a second one, and it is
    strictly narrower: /setup's marker permits everything, this one permits a
    fixed short list.
    """
    if not _close_marker_present(cwd, session_id):
        return False
    rel = os.path.relpath(os.path.normpath(filepath), os.path.normpath(cwd))
    rel = os.path.normcase(rel).replace("\\", "/")
    return rel in tuple(os.path.normcase(n) for n in CLOSE_PHASE_FILES)


# --- Relative time words with no source ([unfounded-time-words-stopped-once]) ---
#
# The always-loaded rule says every statement of when something happened is
# read from a clock, a timestamp or the record, never recalled. It failed
# repeatedly in practice, and a wrong time written into a record reads exactly
# like a right one for as long as it stands. So the phrase set below is caught
# mechanically in text written to a session record, the queue or SPEC: refused
# once per distinct phrase per session, then allowed, so a phrase that carries
# its source in the sentence costs one feedback turn and no more.
#
# THE ONE LIST. stop.py carries its own copy of this pattern and scans the
# finished reply with it — the hooks run standalone from a copied plugin cache
# and cannot import a shared module (CLAUDE.md's scripting constraints). Change
# one, change both.
#
# The limit, stated: a phrase matcher does not reach a bare wrong clock time
# ("at 19:10") or a wrong date; those stay with the rule.
TIME_WORD_PATTERN = re.compile(
    r"\b(?:"
    r"(?:\d+|a|an|one|two|three|four|five|few|a few|couple of|several)"
    r"\s+(?:minutes?|hours?|days?|weeks?|months?)\s+ago"
    r"|just now|moments ago|earlier today|this morning|this afternoon"
    r"|this evening|tonight|yesterday|today|tomorrow|last week|next week"
    r"|last night"
    r")\b",
    re.IGNORECASE,
)

# Spans a time word may legitimately sit inside: inline code, double or curly
# quotation marks, a blockquoted line, a fenced block. Quoted text is someone
# else's words or a specimen, and a specimen of the phrase is how this very
# rule is written down.
_QUOTED_SPAN = re.compile(r"`[^`\n]*`|\"[^\"\n]*\"|“[^”\n]*”")


def _strip_quoted_text(text: str) -> str:
    """The text with fenced blocks, blockquoted lines and quoted spans blanked."""
    out = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append("\n" if line.endswith("\n") else "")
            continue
        if in_fence or stripped.startswith(">"):
            out.append("\n" if line.endswith("\n") else "")
            continue
        out.append(_QUOTED_SPAN.sub(" ", line))
    return "".join(out)


# A time word whose own sentence carries its source passes
# ([time-word-check-blocks-planning-openings]): a date in YYYY-MM-DD form, or
# one of the phrases the always-loaded rule names as a reading. The sentence
# is the text between full stops (or line breaks) around the word. A COPY of
# stop.py's; change one, change both.
TIME_SOURCE_PATTERN = re.compile(
    r"\d{4}-\d{2}-\d{2}"
    r"|read from the clock|by the session clock|per the [^.\n]*?record"
    r"|the opening'?s clock line|the register",
    re.IGNORECASE,
)
_TIME_SENTENCE_BREAK = re.compile(r"(?:[.!?](?=\s|$))|\n")


def _time_sentence_span(text: str, start: int, end: int) -> tuple[int, int]:
    left = 0
    for match in _TIME_SENTENCE_BREAK.finditer(text, 0, start):
        left = match.end()
    right = len(text)
    match = _TIME_SENTENCE_BREAK.search(text, end)
    if match:
        right = match.end()
    return left, right


# What may stand between a sentence's start and its first word: whitespace,
# quotation marks, opening brackets and markdown leaders. A COPY sits in
# stop.py; change one, change both.
_TIME_SENTENCE_LEAD = re.compile(r"^[\s\"'“‘(\[{#*>-]*$")


def _is_name_mid_sentence(text: str, start: int, word: str) -> bool:
    """True where the matched time word opens with a capital and is not the
    first word of its sentence — a product's own page or feature written as a
    name ([time-word-check-hits-product-nouns]). A capital at a sentence's
    start says nothing, so that case still counts as a time word."""
    if not word[:1].isupper():
        return False
    left, _ = _time_sentence_span(text, start, start)
    return not _TIME_SENTENCE_LEAD.match(text[left:start])


# A day word denotes a date computable from the clock
# ([time-word-check-passes-denoted-date]): where that date appears anywhere
# in the text — before or after the word, in brackets or not — the word is
# sourced and passes. Words with no computable date keep the sentence-source
# rule. A COPY sits in stop.py; change one, change both.
_DENOTED_OFFSETS = {
    "yesterday": -1, "today": 0, "tonight": 0, "this morning": 0,
    "this afternoon": 0, "this evening": 0, "earlier today": 0, "tomorrow": 1,
}
# A sentence carrying this many distinct phrases from the check's own list is
# read as a list of the words — mentioned, not used — and is not refused. A
# tunable heuristic derived from the one instance (a planning chat quoting the
# list), stated here as such.
_MENTIONED_LIST_MIN = 3


def _denoted_date(phrase: str) -> "str | None":
    offset = _DENOTED_OFFSETS.get(phrase)
    if offset is None:
        return None
    import datetime as _dt
    today, _ = _clock_now()
    try:
        day = _dt.date.fromisoformat(today)
    except ValueError:
        return None
    return (day + _dt.timedelta(days=offset)).isoformat()


def _unfounded_time_phrases(text: str) -> list:
    """(phrase, sentence) pairs for each distinct time phrase in `text`
    outside quoted spans, lowercased — leaving out any whose sentence also
    carries a source, any written as a name with a capital mid-sentence, any
    whose denoted date the text names anywhere, and any in a sentence that
    lists three or more of the check's own phrases."""
    found = []
    stripped = _strip_quoted_text(text)
    for match in TIME_WORD_PATTERN.finditer(stripped):
        if _is_name_mid_sentence(stripped, match.start(), match.group(0)):
            continue
        left, right = _time_sentence_span(stripped, match.start(), match.end())
        if TIME_SOURCE_PATTERN.search(stripped, left, right):
            continue
        sentence = stripped[left:right]
        distinct = {" ".join(m.group(0).lower().split())
                    for m in TIME_WORD_PATTERN.finditer(sentence)}
        if len(distinct) >= _MENTIONED_LIST_MIN:
            continue
        phrase = " ".join(match.group(0).lower().split())
        denoted = _denoted_date(phrase)
        if denoted and denoted in text:
            continue
        if phrase not in [p for p, _ in found]:
            found.append((phrase, " ".join(sentence.split())))
    return found


def _unfounded_time_words(text: str) -> list[str]:
    """The phrases alone, for callers that key on them."""
    return [phrase for phrase, _ in _unfounded_time_phrases(text)]


def _is_time_word_guarded_path(filepath: str, cwd: str) -> bool:
    """LOG/ entries, QUEUE.md and SPEC.md — the records a wrong time skews."""
    if not cwd:
        return False
    norm = _normalise(filepath)
    if norm in (_normalise(os.path.join(cwd, "QUEUE.md")),
                _normalise(os.path.join(cwd, "SPEC.md"))):
        return True
    log_dir = _normalise(os.path.join(cwd, "LOG"))
    return norm.startswith(log_dir + os.sep)


# --- A clock time later than the clock ([counted-up-clock-times-uncaught]) ---
#
# A bare clock time passes the phrase scan above and reads exactly like a true
# one. Five wrong stamps in one build run were counted up from an earlier clock
# read instead of read by a command, and two of the five had overshot into the
# future. That overshoot is the one shape a hook can see: an `HH:MM` written
# into a record, the queue or SPEC that is later than the clock reads at the
# moment the hook runs. Refused once per distinct time per session, sharing the
# guarded-path set, the quoted-text stripper and the once-per-phrase gate above.
#
# The limit, stated: a time BEHIND the real clock is not reached — three of the
# five were — so this narrows the counted-up failure rather than closing it.
# A time that follows a date earlier than today is a past event and passes.
#
# Only a STAMP-SHAPED place is read ([clock-check-refuses-event-start-time]):
# a written file's first three lines, where a record's stamp lives, or a
# sentence carrying a stamp word — the words derived from the five wrong
# stamps above ("Recorded 22:21, read from the clock", "Filed at …",
# "stamped by the queue tool") and stated as such. A time that names when an
# event takes place — a session's 12:00 start, a video's runtime — sits in
# no such place and is not reached, which is what retired the duration-word
# carve-out.
_CLOCK_TIME_PATTERN = re.compile(
    r"(?:(?P<date>\d{4}-\d{2}-\d{2})[ T]?)?\b(?P<h>[01]?\d|2[0-3]):(?P<m>[0-5]\d)\b"
)
_STAMP_WORDS = re.compile(
    r"\b(?:recorded|filed|stamped|read from the clock)\b", re.IGNORECASE)
_STAMP_HEADER_LINES = 3


def _clock_now() -> "tuple[str, str]":
    """(today's date as YYYY-MM-DD, the clock as HH:MM). The test suites set
    THROUGHLINER_TEST_CLOCK to `YYYY-MM-DD HH:MM` to pin both."""
    import datetime as _dt
    pinned = os.environ.get("THROUGHLINER_TEST_CLOCK", "")
    if pinned:
        day, _, hhmm = pinned.partition(" ")
        return day, hhmm
    now = _dt.datetime.now()
    return now.strftime("%Y-%m-%d"), now.strftime("%H:%M")


def _future_clock_times(text: str, header_lines: int = 0) -> list[str]:
    """Distinct `HH:MM` times in `text`, outside quoted spans, sitting in a
    stamp-shaped place — one of the first `header_lines` lines (a whole
    file's header), or a sentence carrying a stamp word — that claim a
    moment later than the clock reads now. A time carrying a date before
    today is left alone; one carrying a date after today is reported."""
    today, now_hhmm = _clock_now()
    found = []
    stripped = _strip_quoted_text(text)
    for match in _CLOCK_TIME_PATTERN.finditer(stripped):
        hhmm = "%02d:%s" % (int(match.group("h")), match.group("m"))
        date = match.group("date")
        if date and date < today:
            continue
        line_index = stripped.count("\n", 0, match.start())
        left, right = _time_sentence_span(stripped, match.start(), match.end())
        sentence = stripped[left:right]
        if line_index >= header_lines and not _STAMP_WORDS.search(sentence):
            continue
        if (date and date > today) or hhmm > now_hhmm:
            if hhmm not in found:
                found.append(hhmm)
    return found


# The cycles doc's definition shape, as session_start.py reads it — copied
# rather than imported, since the hooks run standalone from a copied plugin
# cache ([malformed-cycle-definition-named-and-refused]). A definition carrying
# neither field is one the opening cannot compute from and no word fires.
_CYCLE_HEADING_RE = re.compile(r"^#{2,4}\s+(.*?)\s*\[([a-z0-9][a-z0-9-]*)\]\s*$")
_CYCLE_CADENCE_RE = re.compile(r"^\s*\*{0,2}Cadence\s*:\*{0,2}\s*(.+?)\s*$",
                               re.IGNORECASE)
_CYCLE_TRIGGER_RE = re.compile(r"^\s*\*{0,2}Trigger\s*:\*{0,2}\s*(.+?)\s*$",
                               re.IGNORECASE)


def _cycle_blocks(text: str) -> dict:
    """Each definition's block — its heading through the line before the next
    heading — keyed by slug."""
    blocks = {}
    slug = None
    for line in text.splitlines():
        heading = _CYCLE_HEADING_RE.match(line)
        if heading:
            slug = heading.group(2)
            blocks[slug] = []
            continue
        if slug is not None:
            blocks[slug].append(line)
    # Trailing blank lines are dropped so that appending a definition after
    # an untouched one does not read as a change to it.
    return {s: "\n".join(lines).rstrip() for s, lines in blocks.items()}


def _block_is_malformed(block: str) -> bool:
    return not any(_CYCLE_CADENCE_RE.match(l) or _CYCLE_TRIGGER_RE.match(l)
                   for l in block.splitlines())


def _content_after_write(tool_name: str, tool_input: dict, filepath: str):
    """The text the file would hold after this call, or None where it cannot
    be worked out (an Edit whose old text is not in the file)."""
    if tool_name == "Write":
        return tool_input.get("content") or ""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError:
        text = ""
    edits = [tool_input] if tool_name == "Edit" else \
        [e or {} for e in (tool_input.get("edits") or [])]
    for edit in edits:
        old = edit.get("old_string") or ""
        new = edit.get("new_string") or ""
        if old not in text:
            return None
        text = text.replace(old, new) if edit.get("replace_all") \
            else text.replace(old, new, 1)
    return text


def _malformed_cycle_definitions_written(tool_name: str, tool_input: dict,
                                         filepath: str) -> list:
    """Slugs of definitions this call would leave in the cycles doc carrying
    neither `Cadence:` nor `Trigger:` — only those the call writes or
    changes, so a malformed definition already there and untouched is not
    refused for it."""
    after = _content_after_write(tool_name, tool_input, filepath)
    if after is None:
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            before = _cycle_blocks(f.read())
    except OSError:
        before = {}
    return [slug for slug, block in _cycle_blocks(after).items()
            if _block_is_malformed(block) and before.get(slug) != block]


def _written_text(tool_name: str, tool_input: dict) -> str:
    """The text a Write, Edit or MultiEdit is about to put into the file."""
    if tool_name == "Write":
        return tool_input.get("content") or ""
    if tool_name == "Edit":
        return tool_input.get("new_string") or ""
    if tool_name == "MultiEdit":
        return "\n".join((e or {}).get("new_string") or ""
                         for e in (tool_input.get("edits") or []))
    return ""


def _fire_once(cwd: str, session_id: str, marker_name: str) -> bool:
    """True the first time a session asks for `marker_name`, False after.

    Used for the unscoped-build surfacing, which describes a standing condition
    rather than one write — repeating it on every edit would train the user to
    dismiss it unread. Never raises: if the marker cannot be written, the caller
    gets True and the notice simply fires again, which is the safe direction.
    """
    try:
        marker_dir = os.path.join(cwd, ".throughliner")
        os.makedirs(marker_dir, exist_ok=True)
        safe_id = re.sub(r"[^A-Za-z0-9._-]", "_", session_id or "unknown")
        path = os.path.join(marker_dir, f"fired-{marker_name}-{safe_id}")
        if os.path.exists(path):
            return False
        with open(path, "w", encoding="utf-8") as f:
            f.write("1")
        return True
    except OSError:
        return True


def _log_collision_suggestion(filepath: str) -> str:
    """The free name(s) beside an existing LOG entry, in the naming rule's order.

    Named rather than merely reported: the record-naming rule says a slug's
    second record carries the kind of session as a suffix — `-plan` or
    `-build` — so the denial hands back whichever of those is free. The
    numeric `-2`, `-3`, … form is the legacy fallback and is offered only when
    both kind names are already taken. The hook cannot see which kind this
    session is, so where both are free it names both and the session picks.
    """
    root, ext = os.path.splitext(filepath)
    kind_free = [f"{root}-{kind}{ext}" for kind in ("plan", "build")
                 if not os.path.exists(f"{root}-{kind}{ext}")]
    if kind_free:
        return " or ".join(os.path.basename(p) for p in kind_free)
    n = 2
    while os.path.exists(f"{root}-{n}{ext}") and n < 100:
        n += 1
    return os.path.basename(f"{root}-{n}{ext}")


def _is_log_entry_overwrite(tool_name: str, filepath: str, cwd: str) -> bool:
    """True for a Write whose target is an existing file under LOG/.

    A successful overwrite is indistinguishable from a successful create: the
    write reports success, the file exists, the index line resolves, and the
    entry reads correctly because it is the one just written. The only trace is
    a ` M` where `??` was expected in a list of twenty-odd staged paths. Two
    committed entries were destroyed that way in a single /done run and recovered
    only because the character was noticed by chance.

    WRITE ONLY, never Edit. A close legitimately edits `LOG/index.md` and
    appends a tail to an existing entry, and both go through Edit — so nothing
    correct is caught. A genuinely new entry filename does not exist yet, so
    this never fires on a correct /done run either.

    The filename derives from the /done date plus the session type, so every
    session of the same kind on one day competes for one name. A consumer
    running one session a day never meets this; a day with a morning and an
    afternoon session meets it immediately.
    """
    if tool_name != "Write":
        return False
    norm = _normalise(filepath)
    log_dir = _normalise(os.path.join(cwd, "LOG"))
    if not norm.startswith(log_dir + os.sep):
        return False
    return os.path.exists(filepath)


_RECORD_FILENAME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}-([a-z0-9][a-z0-9-]*?)(?:-plan|-build|-\d+)?\.md$")
_BUILD_RECORD_KIND = re.compile(r"^#[^\n]*—\s*build\s*—", re.MULTILINE)
_PROCESSED_HEADING_RE = re.compile(r"^#{4}\s+.*\[([a-z0-9][a-z0-9-]*)\]\s*$",
                                   re.MULTILINE)


def _processed_slugs(cwd: str) -> set:
    """Every slug still heading an entry in QUEUE.md's Processed section."""
    try:
        with open(os.path.join(cwd, "QUEUE.md"), "r", encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return set()
    start = text.find("## Processed")
    if start == -1:
        return set()
    end = text.find("## Unprocessed", start)
    section = text[start:end if end != -1 else len(text)]
    return set(_PROCESSED_HEADING_RE.findall(section))


def _build_record_claims_unticked(tool_name: str, filepath: str, cwd: str,
                                  content: str) -> str:
    """The slug a new build record claims while that slug still heads an
    entry in Processed, else "".

    A run removes each item from the queue at its tick, so at the close every
    built item is already out of Processed, and a build record naming a slug
    still there is always a false claim and never a timing accident — the
    recorded instance is a close that wrote a record, an index line and a
    commit message for an item never built
    ([close-records-unticked-item-as-built]). The record's kind is read from
    its first heading (`# <hash> — build — …`), the slug from its filename or
    from a `[slug]` in that heading. A record reading not built, a user-step
    or planning record, a chat-level record, and an Edit appending to an
    existing record all pass.
    """
    if tool_name != "Write":
        return ""
    norm = _normalise(filepath)
    log_dir = _normalise(os.path.join(cwd, "LOG"))
    if not norm.startswith(log_dir + os.sep):
        return ""
    heading = ""
    for line in (content or "").splitlines():
        if line.startswith("#"):
            heading = line
            break
    if not _BUILD_RECORD_KIND.match(heading):
        return ""
    if re.search(r"\bnot built\b", heading, re.IGNORECASE):
        return ""
    candidates = []
    m = _RECORD_FILENAME_RE.match(os.path.basename(filepath))
    if m:
        candidates.append(m.group(1))
    candidates.extend(re.findall(r"\[([a-z0-9][a-z0-9-]*)\]", heading))
    processed = _processed_slugs(cwd)
    for slug in candidates:
        if slug in processed:
            return slug
    return ""


SENT_REGISTER = os.path.join("INBOX", "sent.md")


def _is_sent_register_overwrite(tool_name: str, filepath: str, cwd: str) -> bool:
    """True for a Write whose target is the outbound register.

    `INBOX/sent.md` is the one-line index of everything the project has sent or
    posted, and it is what the repeal check greps for claims already announced.
    It sits inside a mailbox that is gitignored on every path, so unlike every
    other project document it has NO HISTORY to restore from and an accidental
    deletion is final.

    WRITE ONLY, like its LOG sibling. The register is appended to and edited
    constantly — every approved send writes a line in the same turn — and both
    go through Edit, so nothing correct is caught.

    The register is not un-ignored to fix this: the folder's ignore is what
    keeps the address book's identifying paths out of a published repository,
    and a project's outbound record is not necessarily something its owner
    wants public.

    The limit, stated rather than implied: a hook sees only what goes through
    Claude's tools. A file deleted outside the app, or a lost disk, is not
    reached by this.

    EXISTING FILES ONLY, like its LOG sibling: a Write that CREATES the
    register — a project's first-ever send — has nothing to protect and must
    pass, or the register can never come to exist at all (Edit cannot create
    a missing file, so the refusal's escape route was a dead end; two consumer
    projects hit exactly that on their first send).
    """
    if tool_name != "Write":
        return False
    if _normalise(filepath) != _normalise(os.path.join(cwd, SENT_REGISTER)):
        return False
    return os.path.exists(filepath)


def _is_hook_suite_file(filepath: str, cwd: str, build_files: list[str]) -> bool:
    """A test suite, in a run that is already changing a hook.

    Bounded to exactly that pairing, and it completes a requirement the method
    already imposes rather than widening what a run may write: a /done run whose
    staged paths include the hooks directory must run these suites before it can
    commit, so a hook-touching run ALWAYS meets its suites. Refusing them guarded
    files the rules make part of every such change.

    The failure it removes, seen twice in one run: an item named "the lint's
    suite under the testing folder", which is a folder and not a path a `Files:`
    list can carry, so self-scoping could name only the suite files the item's
    own text mentioned — and the run then met two others and stopped to ask.
    Interrupting to widen scope is the one thing a run nobody is watching should
    not need to do.

    Both the current path and the pre-move one are matched, because a project
    whose suites have not yet moved is in exactly the same position.
    """
    if not any(_normalise(os.path.join(cwd, bf)).startswith(
            _normalise(os.path.join(cwd, "plugin", "throughliner", "hooks"))
            + os.sep)
            for bf in build_files):
        return False

    norm = _normalise(filepath)
    # `tests/` at the inner repository root is where the suites live since the
    # repository cleanup; the two older testing paths stay for a project whose
    # suites have not moved ([hooks-name-old-workshop-paths]).
    for testing_dir in (
        os.path.join(cwd, "tests"),
        os.path.join(cwd, "workshop", "resources", "testing"),
        os.path.join(cwd, "resources", "testing"),
    ):
        base = _normalise(testing_dir)
        if norm.startswith(base + os.sep):
            return True
    return False


def _is_build_file(filepath: str, cwd: str, build_files: list[str]) -> bool:
    """Check if a path is in the build's file list."""
    norm = _normalise(filepath)
    for bf in build_files:
        # Build files can be relative to project root
        candidate = _normalise(os.path.join(cwd, bf))
        if norm == candidate:
            return True
    return _is_hook_suite_file(filepath, cwd, build_files)


# --- Main ---

def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError, ValueError):
        return 0

    if not isinstance(data, dict):
        return 0

    cwd = project_root(data)
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input") or {}

    # The decision log writes only inside an adopted project — an unadopted
    # folder must not gain a `.throughliner/` folder from a hook that fired
    # in passing.
    adopted_here = bool(cwd) and os.path.isfile(os.path.join(cwd, "SPEC.md"))
    _ctx["cwd"] = cwd if adopted_here else ""
    _ctx["tool"] = tool_name if isinstance(tool_name, str) else ""
    _ctx["target"] = ""
    _ctx["sid"] = data.get("session_id", "") or ""
    _ctx["notice"] = _version_change_notice(_ctx["cwd"], _ctx["sid"])
    _ctx["printed"] = False

    # --- Subagent (Agent / Task): cost ask-gate ---
    # A subagent run burns tokens fast and a single run can exhaust the
    # user's usage, so every spawn gets a permission prompt before it starts.
    # "ask", never "deny": the user keeps full choice — the cost just stops
    # being a silent surprise. Checked before the cwd / SPEC.md gates below,
    # because the cost protection is universal: a subagent is as expensive in
    # an unadopted folder as an adopted one. Pairs with the hardened
    # "Tool use" rule in skill-nonspecific-rules.md — the rule steers, the gate
    # guarantees.
    #
    # Both names are matched deliberately: current Claude Code names the
    # subagent tool "Agent", older harnesses name it "Task". Matching only
    # "Task" is how this gate was silently dead — registered, firing, and
    # never recognising the tool it exists to guard.
    if tool_name in ("Task", "Agent"):
        return _ask(
            "[Throughliner] Claude wants to start a subagent. "
            "Subagents burn tokens fast — a single run can use up your usage "
            "for the session. Approve if this genuinely needs wide, "
            "open-ended exploration; decline to have Claude do the work "
            "directly instead. Declining is a normal, safe choice.",
            branch="subagent cost gate",
        )

    # --- Skill: the method's own commands are the user's to type ---
    # These five ship with model invocation disabled, so an attempt fails and
    # shows the user a red error at the moment they have least context for it.
    # It has happened at a /done run, landing between "now closing the session" and
    # any explanation, and the wording-only rule has now failed twice on record
    # — which is what moves this to a hook under the gate's fourth admission
    # question: the failure is mechanical, it recurs, and its cost lands on the
    # user rather than on the run.
    #
    # The message names the likely trigger because the user reports it recurs
    # there: a command typed before Claude Code has registered it arrives as
    # chat text, and the natural repair looks like invoking it.
    if tool_name == "Skill":
        requested = tool_input.get("skill", "")
        if isinstance(requested, str) and requested:
            prefix, _, bare = requested.rpartition(":")
            # The prefix arm fires anywhere, including an unadopted folder,
            # which is where /setup's failure actually happens. The bare arm is
            # held to adopted projects so a same-named skill from somewhere
            # else is not caught by a name collision.
            ours = "throughliner" in prefix.lower() or "flintcraft" in prefix.lower()
            adopted = bool(cwd) and os.path.isfile(os.path.join(cwd, "SPEC.md"))
            if bare.lower() in METHOD_SKILLS and (ours or (not prefix and adopted)):
                _ctx["target"] = requested
                return _deny(
                    f"[Throughliner] The /{bare} command is yours to type — "
                    "Claude can't run it, and trying shows you a red error "
                    "instead of doing anything.\n\n"
                    "If you just typed it and it landed as ordinary chat text, "
                    "the command probably hadn't registered yet. Wait a few "
                    f"seconds and type /{bare} again.",
                    branch="method skill invocation",
                )

    if not cwd:
        return 0

    # Only enforce in adopted projects (SPEC.md exists)
    spec_path = os.path.join(cwd, "SPEC.md")
    if not os.path.isfile(spec_path):
        return 0

    # THIS session's build working file. The scope-lock must answer "is there a
    # build for this session?", not "is there a build?" — a planning session
    # running alongside a build in another chat used to inherit that build's
    # file list.
    build_path = working_file(cwd, "build", data.get("session_id", ""))
    has_active_build = os.path.isfile(build_path)

    # --- Bash/PowerShell: git safety ---
    if tool_name in ("Bash", "PowerShell"):
        command = tool_input.get("command", "")
        if not isinstance(command, str):
            return 0
        _ctx["target"] = command

        # Match each git-safety pattern per segment, never against the whole
        # compound command, so tokens from unrelated segments can't combine
        # across a shell operator (the cross-segment false-denial bug).
        for segment in _split_segments(command):
            if SENT_REGISTER_DESTRUCTION.search(segment):
                return _deny(
                    "[Throughliner] BLOCKED: this would delete or empty the "
                    "record of everything this project has sent, and that "
                    "record has no backup.\n\n"
                    f"File: {SENT_REGISTER}\n\n"
                    "The mailbox folder is deliberately kept out of git, so "
                    "this one file has no history to restore from.\n\n"
                    "Use Edit to change a line in it. Nothing else needs to "
                    "touch the whole file."
                    + PATTERN_AS_DATA_NOTE,
                    branch="git safety: sent-register destruction",
                )

            if RESET_HARD.search(segment):
                return _deny(
                    "[Throughliner] BLOCKED: `git reset --hard` destroys "
                    "uncommitted work and cannot be undone.\n\n"
                    "Safer alternatives:\n"
                    "- `git stash` — saves changes for later.\n"
                    "- `git checkout -- <file>` — discards one file's changes.\n"
                    "- `git reset HEAD~1` — moves HEAD back, keeps working tree."
                    + PATTERN_AS_DATA_NOTE,
                    branch="git safety: reset --hard",
                )

            if PUSH_FORCE.search(segment):
                return _deny(
                    "[Throughliner] BLOCKED: `git push --force` can "
                    "overwrite remote commits.\n\n"
                    "Use `git push --force-with-lease` instead — it refuses to "
                    "push if the remote has commits you haven't fetched."
                    + PATTERN_AS_DATA_NOTE,
                    branch="git safety: push --force",
                )

            if BLANKET_ADD.search(segment):
                return _deny(
                    "[Throughliner] BLOCKED: blanket adds (`git add -A`, "
                    "`git add --all`, `git add .`) stage everything in the tree, "
                    "including files never meant for the commit.\n\n"
                    "Stage explicitly — name each path: `git add <path> <path>`."
                    + PATTERN_AS_DATA_NOTE,
                    branch="git safety: blanket add",
                )

            if COMMIT_ALL.search(segment):
                return _deny(
                    "[Throughliner] BLOCKED: `git commit -a` / `-am` "
                    "auto-stages every modified file, including changes never "
                    "meant for the commit.\n\n"
                    "Stage explicitly, then commit: `git add <path> <path>`, "
                    'then `git commit -m "<message>"`.'
                    + PATTERN_AS_DATA_NOTE,
                    branch="git safety: commit -a",
                )

            commit_match = GIT_COMMIT.search(segment)
            if commit_match:
                repo_dir = commit_match.group(1)
                repo_dir = (repo_dir.strip("\"'") if repo_dir else "") or "."
                if not os.path.isabs(repo_dir):
                    repo_dir = os.path.join(cwd, repo_dir)
                conflicted = _conflicted_tracked_file(repo_dir)
                if conflicted:
                    return _deny(
                        "[Throughliner] BLOCKED: this commit would carry a "
                        "git conflict marker. A tracked file in this "
                        "repository is still mid-merge:\n\n"
                        f"File: {conflicted}\n\n"
                        "Resolve the conflict — for two captures appended "
                        "at the same spot, keep both — remove the `<<<<<<<`, "
                        "`=======` and `>>>>>>>` lines, then commit."
                        + PATTERN_AS_DATA_NOTE,
                        branch="git safety: conflict marker in a tracked file",
                    )

        # --- Structured shell writes to project files ---
        #
        # The denial had two reasons and they come apart. The scope-lock reason
        # genuinely does not apply to an in-scope target. The stale-view reason
        # does: a shell's view of a file can be stale, so a scripted write can
        # silently clobber work the edit tools would have refused to. That half
        # is unconditional, which is why this check is too — it does not consult
        # the Files list.
        #
        # What still passes, by construction: the session scratchpad (outside
        # the repo, sanctioned scratch space), the user's memory directory, and
        # anything outside the project — but only where the target is READABLE.
        # A write call whose target cannot be read is denied outright below,
        # scratchpad included, because an unreadable target cannot be shown to
        # be safe. Invoking the queue mover is unaffected: the command text is
        # just a script path and carries no write call.
        for target in structured_write_targets(command):
            resolved = target if os.path.isabs(target) else os.path.join(
                cwd, target
            )
            if _is_memory_dir(resolved) or _is_scratchpad_dir(resolved, cwd):
                continue
            if not _is_inside(resolved, cwd):
                continue
            return _deny(
                "[Throughliner] BLOCKED: this command writes to a file "
                f"through a script rather than through the editing tools.\n\n"
                f"Target: {target}\n\n"
                "The shell reads the file through a mount that can hold a stale "
                "view, so a scripted write can silently overwrite work the "
                "editing tools would have refused to clobber. That is true "
                "whatever the file is and whether or not it is in this build's "
                "scope, which is why this check does not consult the Files "
                "list.\n\n"
                "Use Edit or Write instead. If the edit is a large or awkward "
                "one (removing a whole work item from the queue is the usual "
                "case), there is a purpose-built tool for it: the queue mover, "
                "reorder_queue.py, which moves and deletes queue items "
                "byte-for-byte, addressed by slug. It ships inside the plugin, "
                "under the plugin root's scripts/ folder — search for the "
                "filename rather than assuming a path, since where the plugin "
                "is installed differs on every machine. If you genuinely need "
                "scratch space, the session scratchpad sits outside the repo "
                "and still passes.\n\n"
                "Note the honest limit of this check: it reads the command's "
                "text, not its behaviour. A write buried inside a script FILE "
                "this command merely invokes is not seen.",
                branch="shell-write guard: structured write to a project file",
            )

        if has_computed_write_target(command):
            return _deny(
                "[Throughliner] BLOCKED: this command writes to a file "
                "through a script, and the target path is computed at runtime "
                "rather than written out, so this check cannot tell what it "
                "writes to.\n\n"
                "An unreadable target cannot be shown to be safe, so it is "
                "denied rather than allowed. This is not a rule about where the "
                "file is — it is that nobody can say where the file is.\n\n"
                "Three ways forward. Use Edit or Write, which is the right "
                "answer almost every time. If the edit is a large or awkward "
                "one — removing a whole work item from the queue is the usual "
                "case — the queue mover, reorder_queue.py, moves and deletes "
                "queue items byte-for-byte, addressed by slug. It ships inside "
                "the plugin, under the plugin root's scripts/ folder — search "
                "for the filename rather than assuming a path, since where the "
                "plugin is installed differs on every machine. If you need a "
                "script, write the target path out literally so it can be "
                "checked; a scratchpad path written literally still passes.\n\n"
                "Why this is strict: a computed target slipped past an earlier "
                "version of this check and silently corrupted QUEUE.md, and the "
                "only difference from the version that was correctly blocked "
                "was one variable assignment.",
                branch="shell-write guard: computed target",
            )

        # The queue tool is the one sanctioned route by which a shell command
        # rewrites a method document, so it gets the same pre-change snapshot an
        # Edit would. Without this, every per-item removal in a run — the most
        # frequent queue write there is — would go unprotected in a project whose
        # queue has left git.
        #
        # inbox_send.py is the other sanctioned script: it passes here for the
        # same reason the mover does — the command text is a script path and
        # carries no write call — and it needs no snapshot, since it writes
        # into another project's INBOX/ and never into this project's files.
        if "reorder_queue" in command:
            _snapshot_before_write(cwd, os.path.join(cwd, "QUEUE.md"))

        return _allow("shell command: no guard matched")

    # --- Edit/Write/MultiEdit: file-scope enforcement ---
    #
    # A build READS QUEUE.md, and that is deliberate. The generated-view era
    # withheld the queue from a run so decision history could not be transcribed
    # into shipped documents. It stopped that and cost something larger: a build
    # that cannot see why a thing is being built infers a why, and a wrong why
    # aims the whole change wrong. The boundary is now stated in the procedure
    # (next.md's opening) rather than enforced by withholding — read the
    # reasoning to aim the work, write the action and not the reasoning.
    if tool_name not in ("Edit", "Write", "MultiEdit"):
        return 0

    filepath = tool_input.get("file_path", "")
    if not filepath:
        return 0
    _ctx["target"] = filepath

    # Publish the editing-state signal: a write is about to happen, on this
    # file, now. Placed before the scope checks so the marker is up before the
    # write, which is the whole point; if the write is then denied, the marker
    # simply goes stale and the reader treats it as not-editing. Cannot block
    # or fail the tool call — see write_editing_marker. Reached only after the
    # SPEC.md gate above, so the signal exists only in adopted projects.
    write_editing_marker(cwd, data.get("session_id", ""), filepath, True)

    # Save the previous version of an untracked method document, so write-first
    # keeps its recoverability test in a project that has taken these documents
    # out of git. Same placement reasoning as the marker above: before the write,
    # and never able to block or fail the tool call.
    _snapshot_before_write(cwd, filepath)

    # A Write onto an existing LOG entry destroys it silently. Checked ahead of
    # every scope branch, because LOG/ is editable in all of them — the scope
    # checks would let this through whatever kind of session is running.
    if _is_log_entry_overwrite(tool_name, filepath, cwd):
        return _deny(
            "[Throughliner] BLOCKED: a session record already exists at this "
            "name, and writing over it would destroy it with no sign that "
            "anything went wrong.\n\n"
            f"Existing: {os.path.basename(filepath)}\n"
            f"Free name: {_log_collision_suggestion(filepath)}\n\n"
            "The record-naming rule: a second record for the same name carries "
            "the kind of session as a suffix (-plan or -build); a number is the "
            "fallback only when both kind names are taken. Write the new record "
            "under the free name above that matches this session's kind.\n\n"
            "If you meant to add to the existing record rather than replace it, "
            "use Edit — appending to a record is always allowed.",
            branch="overwrite guard: LOG entry",
        )

    # A new build record for a slug still in Processed is a claim of work that
    # was never ticked ([close-records-unticked-item-as-built]). Checked here
    # beside the overwrite guard, for the same reason: LOG/ is writable in
    # every kind of session.
    unticked = _build_record_claims_unticked(
        tool_name, filepath, cwd, tool_input.get("content", ""))
    if unticked:
        return _deny(
            "[Throughliner] BLOCKED: this build record claims [%s] as built, "
            "but that item still sits in QUEUE.md's Processed section — it "
            "was never ticked. A run removes each item from the queue at its "
            "tick, so a built item is never still there.\n\n"
            "Either the item was not built, and the record says so (\"not "
            "built\" in its heading) or is not written; or the working file's "
            "Progress shows the tick and the queue removal did not happen, "
            "which is settled before the record is written." % unticked,
            branch="record claims unticked item",
        )

    # A Write over the outbound register destroys the only copy — the mailbox is
    # gitignored, so there is no history to restore from. Unconditional for the
    # same reason as its LOG sibling: every scope branch permits INBOX/.
    if _is_sent_register_overwrite(tool_name, filepath, cwd):
        return _deny(
            "[Throughliner] BLOCKED: this would write over the record of "
            "everything this project has sent, and that record has no backup.\n\n"
            f"File: {SENT_REGISTER}\n\n"
            "The mailbox folder is deliberately kept out of git — it holds "
            "other projects' folder paths — so this one file has no history to "
            "restore from and an overwrite is final.\n\n"
            "Use Edit instead: append the new line to the existing register, "
            "or change the line that needs changing. Replacing the whole file "
            "is what is refused. (This fires only against a register that "
            "already exists — a Write creating one passes.)",
            branch="overwrite guard: sent register",
        )

    # A cycles-doc definition the opening cannot read — neither a Cadence: nor
    # a Trigger: line — is refused at the write, naming the slug and the tool
    # that writes the field the hook reads. Reaches the definition this call
    # writes or changes; one already there and untouched passes.
    if _normalise(filepath) == _normalise(os.path.join(cwd, CYCLES_DOC)):
        malformed = _malformed_cycle_definitions_written(
            tool_name, tool_input, filepath)
        if malformed:
            named = ", ".join("[%s]" % s for s in malformed)
            return _deny(
                "[Throughliner] BLOCKED: this would write a definition into "
                f"CYCLES.md that the session opening cannot read — {named} "
                "carries neither a `Cadence:` line nor a `Trigger:` line.\n\n"
                "A cycle carries `Cadence:` and a checklist carries "
                "`Trigger:` (the word that fires it); a firing word written "
                "under any other label parses as a cycle with no cadence, so "
                "the word fires nothing and the opening reports an empty "
                "cycle. Write the definition with the state server's "
                "cycle_define tool where the server is registered — it writes "
                "the fields the opening reads — or add the missing line and "
                "try again.",
                branch="cycles doc: malformed definition",
            )

    # A relative time word with no source, written into a record, the queue or
    # SPEC. Refused once per distinct phrase per session, then allowed.
    if _is_time_word_guarded_path(filepath, cwd):
        sid = data.get("session_id", "")
        fresh = [
            (p, s) for p, s in
            _unfounded_time_phrases(_written_text(tool_name, tool_input))
            if _fire_once(cwd, sid, "time-word-" + re.sub(r"[^a-z0-9]+", "-", p))
        ]
        if fresh:
            listed = "; ".join('"%s" in: %s' % (p, s) for p, s in fresh)
            return _deny(
                "[Throughliner] BLOCKED once: this text says when something "
                f"happened with no source — {listed}\n\n"
                "Keep the word and put the date it means beside it in the "
                "same sentence — \"since yesterday (2026-09-20)\" — read from "
                "the clock or the record; drop the word only where no date "
                "exists. Reply with the corrected sentence alone, with no "
                "account of what the clock reads. A wrong time written into a "
                "record reads exactly like a right one for as long as it "
                "stands. A name written with a capital mid-sentence — a "
                "product's own page or feature — passes, so a refusal on one "
                "is a false positive to reword or ignore. A word that is "
                "content — what a slide, a template or a script says — goes "
                "in quotation marks, which this check does not read. The "
                "same phrase passes on the next attempt.",
                branch="time word",
            )

        # A clock time later than the clock reads now — the shape a time
        # counted up from an earlier reading takes. Refused once per distinct
        # time per session, then allowed.
        _, now_hhmm = _clock_now()
        future = [
            t for t in _future_clock_times(
                _written_text(tool_name, tool_input),
                header_lines=_STAMP_HEADER_LINES if tool_name == "Write" else 0)
            if _fire_once(cwd, sid, "future-time-" + t.replace(":", ""))
        ]
        if future:
            listed = ", ".join(future)
            return _deny(
                "[Throughliner] BLOCKED once: this text carries a clock time "
                f"later than the clock reads now — {listed}, against {now_hhmm}.\n\n"
                "A time counted up from an earlier reading overshoots. Read "
                "the clock by a command at the moment of writing and write "
                "what it says; where the time is a real past one, put its "
                "date in front of it. Only a stamp-shaped place is read — a "
                "file's first lines, or a sentence saying recorded, filed, "
                "stamped or read from the clock — so a time that names when "
                "an event takes place passes elsewhere. The same time passes "
                "on the next attempt.",
                branch="future clock time",
            )

    # Rule 1: the working file's Files: section governs editability. Tri-state:
    # no section = skip enforcement, present but empty = method docs only,
    # entries listed = enforce the list.
    if has_active_build:
        build_files = _parse_build_files(build_path)

        if build_files is None:
            # An UNSCOPED build: a build working file with no Files: section at
            # all. It fails open, and from the inside it is indistinguishable
            # from a properly contained build — nothing marks the difference, so
            # the containment can be absent for a whole run with nobody noticing.
            # Surface it once, then get out of the way.
            if _fire_once(cwd, data.get("session_id", ""), "unscoped-build"):
                return _ask(
                    "[Throughliner] This build's working file has no "
                    "Files: section, so nothing is limiting which files it can "
                    "change. That may be exactly right — an audit lists no "
                    "files — but it is worth knowing rather than assuming.\n\n"
                    "Proceed, or stop and give the build a file list first?",
                    branch="build scope: unscoped working file, asked once",
                )
            return _allow("build scope: unscoped working file")

        # A build does not edit QUEUE.md by hand. It reads the file — that is
        # where its instructions and their reasoning live — and the only queue
        # WRITES a run makes, removing a ticked item and appending a capture, go
        # through reorder_queue.py, which the shell guard permits by name (as
        # it does inbox_send.py, the outbound-mail script). A
        # direct Edit or Write here is either a build rewriting an item's
        # rationale, or the awkward hand-editing the mover exists to replace.
        #
        # Narrowed deliberately. The item that asked for this said the
        # scope-lock should "refuse QUEUE.md to a build", which taken flat would
        # have broken three shipped mechanisms: the per-item removal at each
        # tick, capture-and-continue, and abort-and-requeue. So writes are
        # routed through the mover rather than refused outright.
        #
        # The read-refusal that used to sit above this is retired (2026-08-27,
        # [builds-read-the-queue-again]): withholding the reasoning stopped a
        # build transcribing it and cost more than it saved, because a build
        # that cannot see why a thing is being built infers a why.
        if _normalise(filepath) == _normalise(os.path.join(cwd, "QUEUE.md")):
            return _deny(
                "[Throughliner] BLOCKED: a build does not edit the queue "
                "directly.\n\n"
                "A run READS the queue — that is where its instructions and "
                "their reasoning live — but it does not hand-edit it. The "
                "two queue writes a run legitimately makes both go through the "
                "queue tool instead:\n\n"
                "  - removing an item once it is built\n"
                "  - appending something noticed mid-run to Unprocessed\n\n"
                "Use reorder_queue.py, which ships under the plugin root's "
                "scripts/ folder — search for the filename rather than assuming "
                "a path. It moves, deletes and appends whole entries "
                "byte-for-byte, addressed by slug.\n\n"
                "If this is neither of those, it is work on the queue's own "
                "contents, which is planning rather than building.",
                branch="build scope: queue edited by hand",
            )

        # The session id must be passed: _is_method_doc resolves this session's
        # working files by name, and without the id it looks for
        # `_build-unknown.md` and never matches the real one — which denied a
        # scoped build every write to its own working file, including the
        # progress ticks and change notes /done reads.
        sid = data.get("session_id", "")
        # The Files list is checked further down; a listed path is allowed
        # there. What follows here is the ordered chain of standing
        # exemptions, and the checklist `Writes:` field sits at its head: a path
        # a cycles-doc definition declares is permitted whenever the project
        # is open, in a build session as much as a planning one
        # ([ritual-writes-refused-in-build-sessions]).
        if _is_build_file(filepath, cwd, build_files or []):
            return _allow("build scope: in Files list")
        for branch, hit in (
            ("checklist Writes: field",
             lambda: _is_checklist_declared_path(filepath, cwd)),
            ("build scope: method doc",
             lambda: _is_method_doc(filepath, cwd, sid)),
            ("build scope: memory dir", lambda: _is_memory_dir(filepath)),
            ("research exemption", lambda: _is_research_dir(filepath, cwd)),
            ("retired-terms file", lambda: _is_retired_terms_file(filepath, cwd)),
            ("scratchpad", lambda: _is_scratchpad_dir(filepath, cwd)),
            ("temp folder", lambda: _is_temp_dir(filepath, cwd)),
            ("plans dir", lambda: _is_plans_dir(filepath, cwd)),
            ("TOOLS.md", lambda: _is_tools_file(filepath, cwd)),
            ("INBOX", lambda: _is_inbox_dir(filepath)),
            ("close-phase file",
             lambda: _is_close_phase_file(filepath, cwd, sid)),
            ("own close marker",
             lambda: _is_own_close_marker(filepath, cwd, sid)),
        ):
            if hit():
                return _allow(branch)

        if not build_files:
            return _deny(
                "[Throughliner] BLOCKED: this session's build working "
                f"file ({os.path.basename(build_path)}) lists no editable "
                "files, so only QUEUE.md, LOG/, and the working file itself "
                "can be edited. Audit and test sessions "
                "don't edit source files — route findings to Captures in "
                "QUEUE.md instead. If a file genuinely needs editing, halt "
                "and add it to the working file's Files: section with the "
                "user's approval.",
                branch="build scope: empty Files list",
            )

        if not _is_build_file(filepath, cwd, build_files):
            # The trailing-text hint is useful only when the file IS named in
            # the list and the match broke on an annotation. When it is absent
            # entirely, that advice sends the reader hunting for a typo on a
            # line that does not exist — and a wrong diagnostic costs more than
            # a missing one, because the reader here is a run with nobody
            # watching and something has already gone wrong.
            looks_listed = any(
                os.path.basename(filepath) in listed for listed in build_files
            )
            # A folder line covers nothing beneath it: the match is exact, so
            # a run that listed `tests` expecting the suites under it to be
            # covered learns otherwise only here — name the file to add
            # ([files-list-folder-line-covers-nothing]).
            folder_lines = [
                listed for listed in build_files
                if _normalise(filepath).startswith(
                    _normalise(os.path.join(cwd, listed)) + os.sep)
            ]
            if os.path.basename(filepath) == "SPEC.md":
                # A sentence in the item's prose about SPEC is not the line
                # the check reads ([spec-rework-files-line-checked]).
                diagnosis = (
                    "SPEC.md is editable only by a run whose working file "
                    "lists it in its Files: section; a sentence in the item's "
                    "prose about SPEC is not that line. Halt and, with the "
                    "user's approval, add the path to the working file's "
                    "Files: section."
                )
            elif folder_lines:
                rel_file = os.path.relpath(
                    os.path.normpath(filepath), os.path.normpath(cwd)
                ).replace("\\", "/")
                diagnosis = (
                    f"The Files: list names the folder '{folder_lines[0]}', "
                    "and a folder line covers no file beneath it — the check "
                    "matches each line as an exact path. Add the file itself: "
                    f"{rel_file}"
                )
            elif looks_listed:
                diagnosis = (
                    "Files: lines must be bare paths — one path per line, "
                    "nothing else on the line. A note or annotation on a line "
                    "becomes part of the path and silently breaks the match, "
                    "and this file looks listed above, so check its line for "
                    "trailing text."
                )
            else:
                diagnosis = "This file is not in the list at all."
            return _deny(
                "[Throughliner] BLOCKED: this file is not in the "
                f"current build's file list.\n\n"
                f"{os.path.basename(build_path)} allows: {', '.join(build_files)}\n\n"
                f"{diagnosis}\n\n"
                "If this file genuinely needs editing, halt the build and, "
                "with the user's approval, add it to the working file's Files: "
                "section.",
                branch="build scope: not in Files list",
            )

        return _allow("build scope: in Files list")

    else:
        # /setup declares itself with a scratchpad marker, and a session
        # carrying it is neither a planning session nor a build — so the
        # standing list below does not apply. Checked ahead of the Rule 4
        # branch: /setup's whole migration path (the version and format-epoch
        # markers, the managed CLAUDE.md block, .gitignore, any missing
        # scaffold file) sits outside the standing list and was denied with no
        # prompt and no override.
        if _setup_marker_present(data.get("session_id", "")):
            return _allow("setup marker")

        # The /done run of the chat setup ran in may correct what setup wrote
        # ([setup-close-cannot-fix-setup-output]): both markers, and a
        # scaffolded path.
        if _is_setup_close_file(filepath, cwd, data.get("session_id", "")):
            return _allow("setup-done close: scaffolded file")

        # Rule 4: no build working file, so this is a planning or freeform
        # session, and the scope-lock runs against the STANDING list instead of
        # a build's agreed one. Writes to that surface pass silently; everything
        # else is denied. See _is_plan_quiet_path for why this denies rather
        # than asks.
        sid = data.get("session_id", "")
        for branch, hit in (
            ("planning standing list", lambda: _is_plan_quiet_path(filepath, cwd)),
            ("memory dir", lambda: _is_memory_dir(filepath)),
            ("research exemption", lambda: _is_research_dir(filepath, cwd)),
            ("scratchpad", lambda: _is_scratchpad_dir(filepath, cwd)),
            ("temp folder", lambda: _is_temp_dir(filepath, cwd)),
            ("plans dir", lambda: _is_plans_dir(filepath, cwd)),
            ("TOOLS.md", lambda: _is_tools_file(filepath, cwd)),
            ("INBOX", lambda: _is_inbox_dir(filepath)),
            ("checklist Writes: field",
             lambda: _is_checklist_declared_path(filepath, cwd)),
            ("own close marker",
             lambda: _is_own_close_marker(filepath, cwd, sid)),
        ):
            if hit():
                return _allow(branch)
        # The user's door: a scope file names the path. It admits the write
        # only where this session's log already holds a refusal of that same
        # path — a door that opens cold is a one-write convention, not a lock.
        door_line = ""
        scope_files = _freeform_scope_files(cwd, sid)
        if _is_build_file(filepath, cwd, scope_files):
            if _door_refused_earlier(filepath, cwd, sid):
                return _allow("freeform scope file")
            door_line = (
                "\n\nA scope file names this path, but the door opens only "
                "after the safety check has refused the path earlier in this "
                "same session — this refusal is that one.")
        elif os.path.isfile(working_file(cwd, "freeform", sid)):
            # A scope file exists and nothing in it matched: say so, so the
            # refusal is not read as though no scope file existed
            # ([freeform-scope-paths-matched-literally]).
            door_line = (
                "\n\nA scope file exists for this session "
                f"({os.path.basename(working_file(cwd, 'freeform', sid))}) "
                "and nothing in its Files: list matched this path — check "
                "the path as written there against the one above.")
        if True:
            return _deny(
                "[Throughliner] BLOCKED: planning sessions can only change a "
                "fixed set of files, and this isn't one of them.\n\n"
                f"About to edit: {filepath}\n\n"
                "A planning session may write QUEUE.md, any SPEC.md (the "
                "root's or a part's), CYCLES.md, TOOLS.md, anything in "
                "LOG/, research notes (under workshop/resources/research/ or "
                "research/ at the project root — a research part named "
                "otherwise goes through the user's door below), supplied "
                "material the user wrote or attached (under "
                "workshop/resources/supplied/), the temp/ "
                "folder and its own scratch files — plus any "
                "path a checklist definition in CYCLES.md declares its steps "
                "write. Everything "
                "else is work, and work gets queued and built rather than done "
                "here.\n\n"
                "Add this to the queue as a piece of work instead, and tell the "
                "user in plain words what you were about to change and why it "
                "is now an item rather than an edit. Where the user then asks "
                "for the same change again in their own words, write "
                "_freeform-<session-id>.md in the project root with a Files: "
                "section naming this one path, say so in one line, and make "
                "the edit — the user's repeated direction is what opens that "
                "door, one path at a time." + door_line,
                branch=("freeform scope file: no prior refusal" if door_line
                        else "planning standing list: not on it"),
            )

    return 0


def run() -> int:
    """main, then the once-per-session version-change notice where main
    printed no decision of its own — one JSON object on stdout either way."""
    rc = main()
    if _ctx.get("notice") and not _ctx.get("printed"):
        json.dump({"systemMessage": _ctx["notice"]}, sys.stdout)
    return rc


if __name__ == "__main__":
    sys.exit(run())
