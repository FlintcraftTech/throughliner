#!/usr/bin/env python3
"""Throughliner state — an MCP server answering four live questions, plus two
structured writes.

Slices one to three of the MCP helper. Slice one is the four read-only tools,
which proved the plumbing — a server registered, trusted, connected, its tools
reachable from a session — with no risk that a bug in the plumbing costs a
file. Slice two adds the first write, `file_capture`, which starts where the
writes are most frequent: filing a capture. It refuses only what is checkably
wrong, echoing the reason so the retry is instant, and appends to the bottom
of Unprocessed and nowhere else, so placement cannot go wrong by construction.
Slice three adds `append_sent_line`, which composes one outbound-register line
from its fields and appends it at the end of `INBOX/sent.md` — the one file
with no history to restore from, where an edit anchored on whatever a session
last read has landed a line out of order. Slice five adds the queue tool's
three moves — `queue_move`, `queue_move_section`, `queue_delete` — each checked
at the door and each running the script's own move, so a planning session
moves, keeps and deletes entries through calls whose arguments are validated
before anything is written.

**Every tool wraps a calculation or a write path existing code already
performs.** Nothing here invents an answer or a second write mechanism: the
queue counts and the next pick come from `scripts/queue_digest.py`, the cycle
facts and the content stamp from `hooks/session_start.py`, and the capture
append goes through `scripts/reorder_queue.py`'s own append path. That is what
keeps the server's answers and the session opening's answers the same answer
rather than two implementations that drift.

**Registration is project-scoped.** This file travels inside the plugin package
but nothing in the package registers it; the registration is a `.mcp.json` at
the development project's own root, so slice one reaches that project only. To
consumers it is an inert passenger until it is promoted, which is a separate
decision and a separate build.

Standard library only, like every script in this project — it runs on machines
whose interpreters nobody here controls.
"""

import contextlib
import datetime
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile

# UTF-8 on all three streams, copied from reorder_queue.py, which is the
# canonical copy. The duplication is deliberate: this file may run standalone
# from a copied plugin cache and cannot rely on importing a shared module.
# stdin is included because this server READS it: on Windows a bare sys.stdin
# decodes the incoming tool call as the legacy codepage, which is how every
# em-dash in a filed capture landed as mojibake — the corruption happened on
# the way in ([mcp-file-capture-encoding-mangles]).
for _stream in (sys.stderr, sys.stdout, sys.stdin):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        # Python < 3.7, or a stream that cannot be reconfigured (redirected to
        # a pipe or replaced by a test harness). Messages then behave as before
        # — degraded, never fatal.
        pass

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "throughliner-state"
SERVER_VERSION = "0.6.0"

# This file sits at <plugin-root>/mcp/server.py, so the plugin root is its
# grandparent. Derived rather than hardcoded, per the working conventions.
PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def project_root():
    """The project whose state is being reported.

    Taken from the environment or the working directory rather than guessed
    from this file's own location: the plugin package can be installed anywhere,
    and the project it reports on is wherever the session is open.
    """
    return os.path.abspath(
        os.environ.get("THROUGHLINER_PROJECT_ROOT") or os.getcwd())


def _load(name, path):
    """Import a module by path. Returns None where the file is absent."""
    if not os.path.isfile(path):
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _digest():
    return _load("throughliner_queue_digest",
                 os.path.join(PLUGIN_ROOT, "scripts", "queue_digest.py"))


def _session_start():
    return _load("throughliner_session_start",
                 os.path.join(PLUGIN_ROOT, "hooks", "session_start.py"))


def _mover():
    return _load("throughliner_reorder_queue",
                 os.path.join(PLUGIN_ROOT, "scripts", "reorder_queue.py"))


def _queue_path(root):
    return os.path.join(root, "QUEUE.md")


# --------------------------------------------------------------------------
# The four tools. Each returns a plain string — what the caller reads.
# --------------------------------------------------------------------------

def tool_queue_checkpoint_counts(_arguments):
    """How much work is ready to build, and how much is left to process."""
    root = project_root()
    digest = _digest()
    if digest is None:
        return "Cannot read the queue: queue_digest.py is not where this " \
               "server expects it (%s)." % PLUGIN_ROOT
    path = _queue_path(root)
    try:
        items = digest.parse(path)
    except OSError as error:
        return "Cannot read %s: %s" % (path, error)

    processed = [i for i in items if i["section"] == "Processed"]
    ready = [i for i in processed if i["cleared"]]
    held = [i for i in processed if not i["cleared"]]
    unprocessed = [i for i in items if i["section"] == "Unprocessed"]
    # The presentable count comes from the digest's own pass-over code — the
    # same function `--next` picks from — so the checkpoint number and the
    # pick can never disagree. Raw and presentable both have a reader: the
    # opening's "captures waiting" line reads the raw count.
    presentable = digest.offerable(items, root)

    return "\n".join([
        "Ready to build (Processed, above the cleared-to-run line): %d"
        % len(ready),
        "Held below the line: %d" % len(held),
        "captures waiting: %d (raw) · left to process: %d (presentable — "
        "minus those dated out, owned by a cycle, or held behind an open "
        "blocker)" % (len(unprocessed), len(presentable)),
        "",
        "Counts only. What to do with them is planning work.",
    ])


def tool_queue_next_pick(arguments):
    """Which item the ordering ladder picks next, and why that rung."""
    root = project_root()
    digest = _digest()
    if digest is None:
        return "Cannot read the queue: queue_digest.py is not where this " \
               "server expects it (%s)." % PLUGIN_ROOT
    path = _queue_path(root)
    try:
        items = digest.parse(path)
    except OSError as error:
        return "Cannot read %s: %s" % (path, error)

    skip = arguments.get("skip") or []
    if isinstance(skip, str):
        skip = [s for s in skip.split(",") if s]
    try:
        picked = int(arguments.get("picked") or 0)
    except (TypeError, ValueError):
        picked = 0
    medians = digest.parse_medians(str(arguments.get("medians") or ""))

    return digest.render_whats_next(items, root, path, skip=skip,
                                    picked=picked, medians=medians)


def tool_cycles_state(_arguments):
    """Each cycle definition's cadence and what its observable currently reads.

    Named for what it returns. The hook reports these facts and the skills
    compute due-ness from them — so this tool stops where the hook stops, and
    turning a cadence and an observable into due-or-not stays the reader's
    step. Reporting a verdict here would put a second due-ness implementation
    in the project, which is the drift the reuse rule exists to prevent.
    """
    root = project_root()
    hooks = _session_start()
    if hooks is None:
        return "Cannot read the cycles doc: session_start.py is not where " \
               "this server expects it (%s)." % PLUGIN_ROOT
    if not os.path.isfile(os.path.join(root, "CYCLES.md")):
        return "No CYCLES.md in this project — nothing is on a cycle, and " \
               "nothing is owed here."

    lines = []
    for slug, description, cadence, observable, last_date in \
            hooks.cycles_facts(root):
        lines.append("[%s] %s" % (slug, description))
        lines.append("  cadence:    %s" % (cadence or "(none stated)"))
        lines.append("  observable: %s" % (observable or "(none stated)"))
        if last_date:
            lines.append("  latest date in that observable: %s" % last_date)
        lines.append("")

    # A chained cycle: its next anchor date and each checklist's computed due
    # date, from the hook's own calendar arithmetic. Dates, not verdicts —
    # whether a checklist whose date has arrived still needs running is read from
    # the record by the skill.
    chains = getattr(hooks, "cycle_chains", None)
    for chain in (chains(root) if chains else []) or []:
        lines.append("[%s] chain — anchor %s, next %s" % (
            chain["slug"], chain["anchor"] or "not stated",
            chain["anchor_date"] or "weekday not read"))
        for checklist, due in chain["checklists"]:
            lines.append("  [%s] due %s" % (checklist, due or "no lead stated"))
        lines.append("")

    checklists = hooks.checklists_facts(root)
    if checklists:
        lines.append("Checklists (fired by a word, never due):")
        for slug, description, trigger in checklists:
            lines.append("  [%s] %s — %s" % (slug, description, trigger))
        lines.append("")

    lines.append("Facts as the definitions state them. Due-ness is computed "
                 "by the skill reading this, not here.")
    return "\n".join(lines)


def _installed_snapshot():
    """The newest plugin snapshot the CLI has written, or (None, None).

    The CLI copies each installed build into
    `~/.claude/plugins/cache/flintcraft/throughliner/<version>/` and does not
    touch it again, so the newest directory by modification time is the one
    most recently installed. Degrades to nothing found rather than guessing:
    a wrong answer here would be read as evidence that the host is current.
    """
    cache = os.path.join(os.path.expanduser("~"), ".claude", "plugins",
                         "cache", "flintcraft", "throughliner")
    if not os.path.isdir(cache):
        return None, None
    entries = []
    for name in os.listdir(cache):
        full = os.path.join(cache, name)
        if os.path.isdir(full):
            try:
                entries.append((os.path.getmtime(full), name, full))
            except OSError:
                continue
    if not entries:
        return None, None
    entries.sort()
    _when, version, full = entries[-1]
    return version, full


VISIBILITY_INNER_RE = re.compile(r"inner repository \(`([^`]+?)/?`\)")


def _inner_root(root):
    """The product subfolder in a nested project, or None for a flat one.

    Read from the project CLAUDE.md's Visibility line, which names the inner
    in backticks; failing that, the one immediate subfolder holding a `.git`.
    Two candidates and no Visibility line is ambiguous, and None is returned
    rather than a guess.
    """
    claude = os.path.join(root, "CLAUDE.md")
    try:
        with open(claude, "r", encoding="utf-8") as f:
            for line in f:
                if not line.startswith("Visibility:"):
                    continue
                m = VISIBILITY_INNER_RE.search(line)
                if m:
                    cand = os.path.join(root, m.group(1))
                    if os.path.isdir(os.path.join(cand, ".git")):
                        return cand
    except OSError:
        pass
    found = []
    try:
        for name in os.listdir(root):
            p = os.path.join(root, name)
            if (not name.startswith(".") and os.path.isdir(p)
                    and os.path.isdir(os.path.join(p, ".git"))):
                found.append(p)
    except OSError:
        return None
    return found[0] if len(found) == 1 else None


def tool_host_currency(_arguments):
    """Whether the installed host carries the source's current files."""
    root = project_root()
    hooks = _session_start()
    if hooks is None:
        return "Cannot compute a stamp: session_start.py is not where this " \
               "server expects it (%s)." % PLUGIN_ROOT

    source = os.path.join(root, "plugin", "throughliner")
    if not os.path.isdir(source):
        # A nested project keeps the product one level down; the same lookup
        # rule_signals.py's inner_root() performs, copied rather than imported
        # since the server runs standalone from the plugin folder.
        inner = _inner_root(root)
        if inner is not None:
            source = os.path.join(inner, "plugin", "throughliner")
    if not os.path.isdir(source):
        return "No plugin source at %s — this tool answers only in the " \
               "project that develops the plugin." % source

    source_stamp = hooks.content_stamp(source)
    version, installed_dir = _installed_snapshot()
    if installed_dir is None:
        return "Source stamp: %s\nNo installed snapshot found in the plugin " \
               "cache, so there is nothing to compare against." % source_stamp

    installed_stamp = hooks.content_stamp(installed_dir)
    when = hooks.install_date(installed_dir)

    lines = [
        "Installed version: %s%s" % (version,
                                     " (installed %s)" % when if when else ""),
        "Installed stamp:   %s" % installed_stamp,
        "Source stamp:      %s" % source_stamp,
    ]
    if installed_stamp == source_stamp:
        lines.append("Stamps MATCH — the installed host carries the current "
                     "source files, so a host-side change is live.")
    else:
        lines.append("Stamps DIFFER — the host has not been reinstalled since "
                     "the most recent host-side change, so host-side tests "
                     "are not live yet.")
    lines.append("")
    lines.append("The stamp hashes plugin.json with its version key dropped, "
                 "so a -testN suffix or a pure release bump does not move it.")
    return "\n".join(lines)


SLUG_SHAPE = re.compile(r'^[a-z0-9][a-z0-9-]*$')


def tool_file_capture(arguments):
    """File one capture at the bottom of Unprocessed, refusing what is
    checkably wrong.

    The tool composes the canonical entry itself and appends it through
    reorder_queue.py's own append path, so no second write mechanism exists.
    Placement is not a parameter: the bottom of Unprocessed is the only
    destination, which is the Captures placement rule by construction.

    It refuses only what is checkably wrong, echoing the reason so the retry
    is instant. Body prose, length and structure pass untouched — the lint
    stays advisory, and a tool that enforced more of it would turn advice
    into a gate nobody agreed to.
    """
    root = project_root()
    queue = _queue_path(root)
    mover = _mover()
    if mover is None:
        return "Cannot write: reorder_queue.py is not where this server " \
               "expects it (%s)." % PLUGIN_ROOT
    if not os.path.isfile(queue):
        return "Cannot write: no QUEUE.md at %s." % queue

    heading = (arguments.get("heading") or "").strip()
    slug = (arguments.get("slug") or "").strip()
    body = (arguments.get("body") or "").strip()
    blocked_by = arguments.get("blocked_by") or []
    if isinstance(blocked_by, str):
        blocked_by = [s.strip() for s in blocked_by.split(",") if s.strip()]
    blocked_by = [s.strip().strip("[]") for s in blocked_by]
    not_before = (arguments.get("not_before") or "").strip()
    cycle = (arguments.get("cycle") or "").strip().strip("[]")

    problems = []

    if not heading:
        problems.append("heading is missing — the entry's one-line "
                        "description, distinguishing words first.")
    else:
        first_word = heading.split()[0].lower().rstrip(",.:;")
        if first_word in ("a", "an", "the"):
            problems.append(
                "heading leads with %r — the queue is read through an "
                "outline that truncates each heading, so put the "
                "distinguishing words first and drop the leading article."
                % heading.split()[0])

    if not slug:
        problems.append("slug is missing — kebab-case, e.g. "
                        "'lint-cries-wolf-on-prose'.")
    elif not SLUG_SHAPE.match(slug):
        problems.append("slug %r is malformed — lowercase letters, digits "
                        "and hyphens only, starting with a letter or digit."
                        % slug)

    if not body:
        problems.append("body is missing — the rationale prose, in plain "
                        "short sentences.")

    with open(queue, 'r', encoding='utf-8', newline='') as f:
        queue_lines = f.read().splitlines(keepends=True)
    existing = (mover.section_slugs(queue_lines, 'Processed')
                | mover.section_slugs(queue_lines, 'Unprocessed'))

    if slug and slug in existing:
        problems.append("slug %r is already taken by an entry in the queue — "
                        "pick another, or edit the existing entry instead."
                        % slug)

    for b in blocked_by:
        if b not in existing:
            problems.append("blocked_by names [%s], which is not an entry in "
                            "the queue — a blocker must resolve to a real "
                            "entry." % b)

    if not_before:
        try:
            datetime.date.fromisoformat(not_before)
        except ValueError:
            problems.append("not_before %r is not a real date — YYYY-MM-DD."
                            % not_before)

    if cycle:
        hooks = _session_start()
        cycle_slugs = []
        if hooks is not None and os.path.isfile(
                os.path.join(root, "CYCLES.md")):
            cycle_slugs = [row[0] for row in hooks.cycles_facts(root)]
        if cycle not in cycle_slugs:
            problems.append(
                "cycle names [%s], which matches no definition in the "
                "project's cycles doc — a typo at write time is refused even "
                "though a later-deleted cycle correctly releases its "
                "material.%s" % (cycle,
                                 " Definitions on file: %s."
                                 % ", ".join("[%s]" % c for c in cycle_slugs)
                                 if cycle_slugs else
                                 " This project has no cycle definitions."))

    if problems:
        return "Refused — nothing was written:\n" + \
               "\n".join("- " + p for p in problems)

    # The filed-at stamp is written mechanically, date and time, read from
    # the clock at the moment of writing ([captures-carry-a-time]): a bare
    # date leaves same-day relative-time claims with no source finer than a
    # day. Prose convention, not a parsed field — the lint reads nothing here.
    filed_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = ["#### %s [%s]\n" % (heading, slug),
             body.rstrip() + "\n",
             "Filed %s, stamped by the capture tool.\n" % filed_at]
    if blocked_by:
        entry.append("Blocked by: %s\n"
                     % ", ".join("[%s]" % b for b in blocked_by))
    if not_before:
        entry.append("Not before: %s\n" % not_before)
    if cycle:
        entry.append("Cycle: [%s]\n" % cycle)

    # The append goes through the mover's own path. Its refusals call
    # sys.exit via die(), which must not kill the server — so the call runs
    # under a captured stderr and a caught SystemExit, and a refusal comes
    # back as this tool's answer instead.
    tmp = tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.md',
                                      delete=False)
    try:
        tmp.write("".join(entry))
        tmp.close()
        captured = io.StringIO()
        try:
            with contextlib.redirect_stderr(captured), \
                    contextlib.redirect_stdout(captured):
                mover.append_item(queue, 'Unprocessed', tmp.name)
        except SystemExit:
            return "Refused by the queue tool — nothing was written:\n" + \
                   captured.getvalue().strip()
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass

    return "Filed at the bottom of Unprocessed: #### %s [%s]" \
           % (heading, slug)


INTENTS = ("for completion", "for continuation")


def tool_append_sent_line(arguments):
    """Compose one register line from its fields and append it at the end of
    INBOX/sent.md, changing nothing else.

    The register is append-only by design and has no git history, so a line
    written by an edit anchored on a stale read can land above the end and
    never be noticed. This is the safe append path: the date and time are
    stamped from the clock, the line is composed in the canonical shape, the
    file is made to end on a newline first, and one line goes on the end.
    It refuses only what is checkably wrong, echoing the reason.
    """
    root = project_root()
    inbox = os.path.join(root, "INBOX")
    register = os.path.join(inbox, "sent.md")

    fields = {}
    for name in ("destination", "intent", "claim", "pointer", "message_id"):
        value = arguments.get(name)
        fields[name] = value.strip() if isinstance(value, str) else ""

    problems = []
    for name in ("destination", "intent", "claim", "pointer"):
        if not fields[name]:
            problems.append("%s is missing." % name)
    if fields["intent"] and fields["intent"] not in INTENTS:
        problems.append("intent must be exactly 'for completion' or "
                        "'for continuation', not %r." % fields["intent"])
    for name, value in fields.items():
        if "\n" in value or "\r" in value:
            problems.append("%s contains a line break — a register line is "
                            "one line." % name)
    if fields["message_id"] and not fields["message_id"].isdigit():
        # A Discord message or topic id is a run of digits. Anything else
        # would land inside the backticked id segment and could split the
        # line's fields when the claims sweep reads it back.
        problems.append("message_id %r is not a run of digits — a Discord "
                        "message or topic id is digits only; leave it empty "
                        "for a send that has none." % fields["message_id"])
    if not os.path.isdir(inbox):
        problems.append("this project has no INBOX/ folder — the mailbox is "
                        "not scaffolded, so there is no register to append to.")

    if problems:
        return "Refused — nothing was written:\n" + \
               "\n".join("- " + p for p in problems)

    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    head = fields["destination"]
    if fields["message_id"]:
        head += " — message id `%s`" % fields["message_id"]
    line = "- %s — %s — %s — %s — %s" % (
        stamp, head, fields["intent"], fields["claim"], fields["pointer"])

    created = not os.path.isfile(register)
    with open(register, "a+", encoding="utf-8", newline="") as f:
        f.seek(0, os.SEEK_END)
        if f.tell() > 0:
            f.seek(f.tell() - 1)
            last = f.read(1)
            if last not in ("\n", "\r"):
                f.write("\n")
        f.write(line + "\n")

    return "%s the register line at the end of INBOX/sent.md:\n%s" % (
        "Created INBOX/sent.md and wrote" if created else "Appended", line)


HOLD_LINE_RE = re.compile(r"^(Blocked by|Not before):.*$", re.MULTILINE)


def _run_mover(args, cwd):
    """Run reorder_queue.py as a subprocess and return (ok, its stderr).

    The mover's refusals exit via die(); running it as its own process keeps
    those out of the server and hands the refusal text back as this tool's
    answer, the same shape file_capture gets by catching SystemExit.
    """
    script = os.path.join(PLUGIN_ROOT, "scripts", "reorder_queue.py")
    proc = subprocess.run([sys.executable, script] + list(args), cwd=cwd,
                          capture_output=True, encoding="utf-8",
                          errors="replace")
    return proc.returncode == 0, (proc.stderr or proc.stdout or "").strip()


def tool_hold_entry(arguments):
    """Write a `Blocked by:` or `Not before:` hold onto one queue entry,
    refusing at the door what the lint would only flag afterwards.

    Fields in, the canonical line out. The recorded harm this closes: an
    unbracketed blocker slug once made a consumer's item permanently
    unliftable with nothing reporting it. A work item above the readiness
    line is moved to the top of the held region in the same call; a capture
    gains the field only, a capture's hold being a bow-out rather than a move.
    """
    root = project_root()
    queue = _queue_path(root)
    mover = _mover()
    digest = _digest()
    if mover is None or digest is None:
        return "Cannot write: reorder_queue.py or queue_digest.py is not " \
               "where this server expects it (%s)." % PLUGIN_ROOT
    if not os.path.isfile(queue):
        return "Cannot write: no QUEUE.md at %s." % queue

    slug = (arguments.get("slug") or "").strip().strip("[]")
    blocked_by = arguments.get("blocked_by") or []
    if isinstance(blocked_by, str):
        blocked_by = [s.strip() for s in blocked_by.split(",") if s.strip()]
    blocked_by = [s.strip().strip("[]") for s in blocked_by if s.strip()]
    not_before = (arguments.get("not_before") or "").strip()
    until_built = bool(arguments.get("until_built"))

    problems = []
    if not slug:
        problems.append("slug is missing — the entry the hold is written on.")
    if blocked_by and not_before:
        problems.append("both blocked_by and not_before were given — a hold "
                        "is one or the other.")
    if not blocked_by and not not_before:
        problems.append("neither blocked_by nor not_before was given — "
                        "nothing to write.")
    if until_built and not blocked_by:
        problems.append("until_built was given without blocked_by — the "
                        "words qualify a Blocked by: hold and nothing else.")

    items = digest.parse(queue)
    by_slug = {}
    for item in items:
        if item["slug"]:
            by_slug.setdefault(item["slug"], []).append(item)
    if slug and slug not in by_slug:
        problems.append("slug %r names no entry in the queue." % slug)
    elif slug and len(by_slug[slug]) > 1:
        problems.append("slug %r matches %d entries — two items sharing a "
                        "slug is itself a fault; fix that first."
                        % (slug, len(by_slug[slug])))
    for b in blocked_by:
        if b == slug:
            problems.append("blocked_by names the entry itself.")
        elif b not in by_slug:
            problems.append("blocked_by names [%s], which is not an entry in "
                            "the queue — a blocker must resolve to a real "
                            "entry." % b)
    if not_before:
        try:
            date = datetime.date.fromisoformat(not_before)
        except ValueError:
            problems.append("not_before %r is not a real date — YYYY-MM-DD."
                            % not_before)
        else:
            if date <= datetime.date.today():
                problems.append("not_before %s is already past — a spent "
                                "date holds nothing." % not_before)
    if until_built and slug in by_slug and len(by_slug[slug]) == 1 \
            and by_slug[slug][0]["section"] != "Unprocessed":
        problems.append("until_built on a work item adds nothing — a work "
                        "item's hold already means do not build until every "
                        "named item resolves; the words belong on a capture, "
                        "which they hold until the named entries are built "
                        "rather than merely processed.")
    if problems:
        return "Refused — nothing was written:\n" + \
               "\n".join("- " + p for p in problems)

    item = by_slug[slug][0]
    section = item["section"]
    new_line = ("Blocked by: %s%s" % (", ".join("[%s]" % b for b in blocked_by),
                                      " until built" if until_built else "")
                if blocked_by else "Not before: %s" % not_before)

    # Read the entry's block to find an existing hold line of either kind,
    # which is replaced rather than doubled.
    with open(queue, "r", encoding="utf-8", newline="") as f:
        queue_lines = f.read().splitlines(keepends=True)
    block = "".join(queue_lines[item["first_line"] - 1:item["last_line"]])
    old = None
    for match in HOLD_LINE_RE.finditer(block):
        old = match.group(0)
        break

    if old is not None:
        if block.count(old) != 1:
            return "Refused — nothing was written:\n- the entry's existing " \
                   "hold line occurs more than once in its block."
        # Replace through the mover's in-item edit, in-process: the old string
        # is unique in the block (checked above) and the replacement is
        # byte-literal.
        captured = io.StringIO()
        try:
            with contextlib.redirect_stderr(captured), \
                    contextlib.redirect_stdout(captured):
                mover.replace_in_item(queue, slug, old, new_line, section)
        except SystemExit:
            return "Refused by the queue tool — nothing was written:\n" + \
                   captured.getvalue().strip()
        action = "Replaced the entry's %s line with" % old.split(":")[0]
    else:
        # Append as the block's last line: the block ends on the entry's
        # last line, so the old string is that line and the new is it plus
        # the hold. The last line is made unique by including the line
        # before it where needed.
        block_lines = block.splitlines(keepends=True)
        tail = ""
        for line in reversed(block_lines):
            tail = line + tail
            if block.count(tail) == 1:
                break
        # Match the file's own line ending, so a CRLF queue does not gain a
        # lone LF line.
        eol = "\r\n" if "\r\n" in block else "\n"
        if not tail.endswith("\n"):
            replacement = tail + eol + new_line + eol
        else:
            replacement = tail + new_line + eol
        captured = io.StringIO()
        try:
            with contextlib.redirect_stderr(captured), \
                    contextlib.redirect_stdout(captured):
                mover.replace_in_item(queue, slug, tail, replacement, section)
        except SystemExit:
            return "Refused by the queue tool — nothing was written:\n" + \
                   captured.getvalue().strip()
        action = "Wrote"

    where = "in %s" % section
    moved = ""
    if section == "Processed" and item["cleared"]:
        # A cleared work item with a hold belongs below the readiness line, at
        # the top of the held region. The mover's --move keeps the marker's
        # position when the moved item was its anchor.
        held = [i for i in items if i["section"] == "Processed"
                and not i["cleared"] and i["slug"]]
        if held:
            args = [queue, "Processed", "--move", slug, "BEFORE", held[0]["slug"]]
        else:
            args = [queue, "Processed", "--move", slug, "BOTTOM"]
        ok, report = _run_mover(args, root)
        if not ok:
            return ("%s the hold line on [%s] %s:\n%s\nBut the move below the "
                    "cleared-to-run line was refused by the queue tool, so "
                    "the entry still sits above it:\n%s"
                    % (action, slug, where, new_line, report))
        moved = ("\nMoved [%s] from above the cleared-to-run line to the top "
                 "of the held region — it crossed the line." % slug)
        where = "in Processed, now below the line"
    elif section == "Unprocessed":
        where = "in Unprocessed (a capture's hold is a bow-out, so it stays " \
                "where it is)"
    else:
        where = "in Processed, below the line where it already sat"

    return "%s the hold line on [%s] %s:\n%s%s" % (
        action, slug, where, new_line, moved)


# --------------------------------------------------------------------------
# Slice five: the queue tool's three moves, checked at the door
# ([mcp-queue-move-tools]). Each wraps reorder_queue.py's own move — the
# within-section --move (which lives in the script's main, so it runs as a
# subprocess), --move-section and --delete (the script's functions, called
# in-process) — so there is one implementation. The door checks refuse what
# is checkably wrong before anything is written; the script's own refusals,
# the unnamed-crossing one included, come back as the tool's answer.
# --------------------------------------------------------------------------

SECTIONS = ("Processed", "Unprocessed")
POSITIONS = ("TOP", "BOTTOM", "BEFORE", "AFTER")
MARKER_TEXT = "the `--- Cleared to run above this line ---` marker"


def _section_state(mover, queue):
    """Per section: (slugs in order, marker anchor or None, had_marker)."""
    with open(queue, 'r', encoding='utf-8', newline='') as f:
        lines = f.read().splitlines(keepends=True)
    sections = mover.parse(lines)
    state = {}
    for name in SECTIONS:
        if name not in sections:
            continue
        start, end = sections[name]
        _pre, blocks, marker_after, had = mover.split_blocks(lines[start:end])
        state[name] = ([s for s, _ in blocks], marker_after, had)
    return state


def _mover_ready():
    """(mover, queue) or (None, refusal text)."""
    root = project_root()
    queue = _queue_path(root)
    mover = _mover()
    if mover is None:
        return None, "Cannot write: reorder_queue.py is not where this " \
                     "server expects it (%s)." % PLUGIN_ROOT
    if not os.path.isfile(queue):
        return None, "Cannot write: no QUEUE.md at %s." % queue
    return mover, queue


def _refused(problems):
    return "Refused — nothing was written:\n" + \
           "\n".join("- " + p for p in problems)


def _crossing_problem(mover, before, before_anchor, after, after_anchor,
                      named, marker_after):
    """Two door checks. Where the caller named a marker placement that would
    carry any entry it did not name across the readiness line — in either
    direction — refuse before the script runs, in the script's own words
    ([queue-move-downward-sweep-unguarded]). Where the caller named no
    placement and a move would put ANY entry across the line, refuse and say
    which entries would cross, so the placement is named on purpose rather
    than falling out of where the marker sat."""
    unnamed, note = mover.crossing_note(before, before_anchor, after,
                                        after_anchor, named=named)
    if marker_after is not None:
        return mover.unnamed_crossing_message(unnamed, after_anchor)
    crossed = [line.split("[", 1)[1].split("]", 1)[0]
               for line in note.splitlines()
               if "crossed the readiness line" in line]
    if not crossed:
        return None
    return ("this move would put %s across %s — name marker_after "
            "(TOP, BOTTOM, or the slug of the last entry that should stay "
            "cleared) so the placement is deliberate."
            % (", ".join("[%s]" % s for s in crossed), MARKER_TEXT))


def _in_process(call):
    """Run one of the script's functions under captured output, returning
    (ok, text). The script's refusals exit via die(); a SystemExit is caught
    and its text returned as a refusal rather than killing the server."""
    captured = io.StringIO()
    try:
        with contextlib.redirect_stderr(captured), \
                contextlib.redirect_stdout(captured):
            call()
    except SystemExit:
        return False, captured.getvalue().strip()
    return True, captured.getvalue().strip()


def _position_args(arguments):
    """(position, anchor, marker_after, problems) read from the arguments."""
    problems = []
    position = (arguments.get("position") or "BOTTOM").strip().upper()
    anchor = (arguments.get("anchor") or "").strip().strip("[]") or None
    marker_after = arguments.get("marker_after")
    marker_after = marker_after.strip().strip("[]") if isinstance(
        marker_after, str) and marker_after.strip() else None
    if position not in POSITIONS:
        problems.append("position must be one of TOP, BOTTOM, BEFORE or "
                        "AFTER, not %r." % position)
    if position in ("BEFORE", "AFTER") and anchor is None:
        problems.append("position %s needs an anchor — the slug of the "
                        "entry to place it %s." % (position, position.lower()))
    if position in ("TOP", "BOTTOM") and anchor is not None:
        problems.append("position %s takes no anchor." % position)
    if marker_after is not None and marker_after.upper() in ("TOP", "BOTTOM"):
        marker_after = marker_after.upper()
    return position, anchor, marker_after, problems


def _marker_problems(marker_after, section, slugs_after, had_marker):
    problems = []
    if marker_after is None:
        return problems
    if section != "Processed" or not had_marker:
        problems.append("marker_after was given, but %s has no cleared-to-run "
                        "marker — the marker lives in Processed." % section)
    elif marker_after not in ("TOP", "BOTTOM") and marker_after not in slugs_after:
        problems.append("marker_after names [%s], which would not be an entry "
                        "in %s after the move." % (marker_after, section))
    return problems


def tool_queue_move(arguments):
    """Move one entry within its section, with the readiness marker's
    placement named where the move would put anything across it."""
    mover, queue = _mover_ready()
    if mover is None:
        return queue
    section = (arguments.get("section") or "").strip()
    slug = (arguments.get("slug") or "").strip().strip("[]")
    position, anchor, marker_after, problems = _position_args(arguments)

    if section not in SECTIONS:
        problems.append("section must be Processed or Unprocessed, not %r."
                        % section)
        return _refused(problems)
    state = _section_state(mover, queue)
    if section not in state:
        return _refused(problems + ["section %s is not in the queue." % section])
    have, marker_anchor, had_marker = state[section]
    if not slug:
        problems.append("slug is missing — the entry to move.")
    elif slug not in have:
        problems.append("slug [%s] names no entry in %s." % (slug, section))
    if anchor is not None:
        if anchor == slug:
            problems.append("anchor names the moved entry itself.")
        elif anchor not in have:
            problems.append("anchor [%s] names no entry in %s."
                            % (anchor, section))
    problems += _marker_problems(marker_after, section, have, had_marker)
    if problems:
        return _refused(problems)

    # The order the script will derive, so the crossing check sees the same
    # move the script is about to make.
    rest = [s for s in have if s != slug]
    if position == "TOP":
        desired = [slug] + rest
    elif position == "BOTTOM":
        desired = rest + [slug]
    else:
        idx = rest.index(anchor) + (1 if position == "AFTER" else 0)
        desired = rest[:idx] + [slug] + rest[idx:]
    if had_marker:
        before_anchor = marker_anchor if marker_anchor else "TOP"
        pref = marker_after if marker_after is not None else before_anchor
        if marker_after is None and pref == slug:
            # The script re-anchors a moved anchor so the marker keeps its
            # position; mirror that here so the check reads the real outcome.
            idx = have.index(slug)
            preceding = have[:idx]
            pref = preceding[-1] if preceding else "TOP"
        problem = _crossing_problem(mover, have, before_anchor, desired, pref,
                                    [slug], marker_after)
        if problem:
            return _refused([problem])

    args = [queue, section, "--move", slug, position]
    if anchor is not None:
        args.append(anchor)
    if marker_after is not None:
        args += ["--marker-after", marker_after]
    ok, report = _run_mover(args, os.path.dirname(queue))
    if not ok:
        return "Refused by the queue tool — nothing was written:\n" + report
    return "Moved [%s] %s%s in %s.\n%s" % (
        slug, position.lower(), " [%s]" % anchor if anchor else "", section,
        report)


def tool_queue_move_section(arguments):
    """Move one entry between the two sections — the keep-move — with the
    readiness marker placed in the same call where the move clears it."""
    mover, queue = _mover_ready()
    if mover is None:
        return queue
    slug = (arguments.get("slug") or "").strip().strip("[]")
    sec_from = (arguments.get("from_section") or "").strip()
    sec_to = (arguments.get("to_section") or "").strip()
    position, anchor, marker_after, problems = _position_args(arguments)

    for name in (sec_from, sec_to):
        if name not in SECTIONS:
            problems.append("from_section and to_section must each be "
                            "Processed or Unprocessed, not %r." % name)
    if problems:
        return _refused(problems)
    if sec_from == sec_to:
        return _refused(["from_section and to_section are the same — use "
                         "queue_move for a move within one section."])
    state = _section_state(mover, queue)
    for name in (sec_from, sec_to):
        if name not in state:
            return _refused(["section %s is not in the queue." % name])
    f_have, _f_anchor, _f_had = state[sec_from]
    t_have, t_anchor, t_had = state[sec_to]
    if not slug:
        problems.append("slug is missing — the entry to move.")
    elif slug not in f_have:
        problems.append("slug [%s] names no entry in %s." % (slug, sec_from))
    elif slug in t_have:
        problems.append("slug [%s] is already an entry in %s."
                        % (slug, sec_to))
    if anchor is not None and anchor not in t_have:
        problems.append("anchor [%s] names no entry in %s — the anchor is "
                        "an entry in the destination section."
                        % (anchor, sec_to))
    if problems:
        return _refused(problems)
    if position == "TOP":
        idx = 0
    elif position == "BOTTOM":
        idx = len(t_have)
    else:
        idx = t_have.index(anchor) + (1 if position == "AFTER" else 0)
    t_after = t_have[:idx] + [slug] + t_have[idx:]
    problems += _marker_problems(marker_after, sec_to, t_after, t_had)
    if problems:
        return _refused(problems)
    if t_had:
        before_anchor = t_anchor if t_anchor else "TOP"
        pref = marker_after if marker_after is not None else before_anchor
        problem = _crossing_problem(mover, t_have, before_anchor, t_after,
                                    pref, [slug], marker_after)
        if problem:
            return _refused([problem])

    ok, report = _in_process(lambda: mover.move_section(
        queue, slug, sec_from, sec_to, position, anchor, marker_after))
    if not ok:
        return "Refused by the queue tool — nothing was written:\n" + report
    return "Moved [%s] from %s to %s (%s%s).\n%s" % (
        slug, sec_from, sec_to, position.lower(),
        " [%s]" % anchor if anchor else "", report)


def tool_queue_delete(arguments):
    """Remove one entry's whole block, addressed by slug."""
    mover, queue = _mover_ready()
    if mover is None:
        return queue
    slug = (arguments.get("slug") or "").strip().strip("[]")
    section = (arguments.get("section") or "").strip()
    problems = []
    if section not in SECTIONS:
        problems.append("section must be Processed or Unprocessed, not %r."
                        % section)
        return _refused(problems)
    state = _section_state(mover, queue)
    if section not in state:
        return _refused(["section %s is not in the queue." % section])
    have, _anchor, _had = state[section]
    if not slug:
        problems.append("slug is missing — the entry to delete.")
    elif have.count(slug) == 0:
        problems.append("slug [%s] names no entry in %s." % (slug, section))
    elif have.count(slug) > 1:
        problems.append("slug [%s] matches %d entries in %s — two entries "
                        "sharing a slug is itself a fault; fix that first."
                        % (slug, have.count(slug), section))
    if problems:
        return _refused(problems)

    ok, report = _in_process(lambda: mover.delete_item(queue, slug, section))
    if not ok:
        return "Refused by the queue tool — nothing was written:\n" + report
    return "Deleted [%s] from %s.\n%s" % (slug, section, report)


_MOVE_PROPERTIES = {
    "position": {
        "type": "string",
        "enum": ["TOP", "BOTTOM", "BEFORE", "AFTER"],
        "description":
            "Where the entry lands: TOP or BOTTOM of the section, or "
            "BEFORE/AFTER the entry named in anchor. Defaults to BOTTOM.",
    },
    "anchor": {
        "type": "string",
        "description":
            "With BEFORE or AFTER: the slug of the entry to place it next "
            "to, in the destination section.",
    },
    "marker_after": {
        "type": "string",
        "description":
            "Where the cleared-to-run marker lands afterwards (Processed "
            "only): TOP, BOTTOM, or the slug of the LAST entry that should "
            "stay cleared. Required whenever the move would put any entry "
            "across the marker. To clear several held entries, make one "
            "move per entry naming that entry here, so each call clears "
            "only what it names.",
    },
}


# --------------------------------------------------------------------------
# Slice six: the build run's per-item close as one checked call
# ([mcp-build-tick-tool]). The tick, the slug-bound depth and rule-gate lines,
# the index candidate and the changes entry go into the session's build
# working file in the exact shapes next.md's specimen shows, and the item
# leaves Processed through reorder_queue.py's own delete in the same call.
# --------------------------------------------------------------------------

WORKING_FILE_SECTIONS = ("Index entry candidates", "Run-level", "Files",
                         "Progress", "Changes")
_SECTION_HEADER_RE = re.compile(
    r"^(%s):\s*$" % "|".join(re.escape(s) for s in WORKING_FILE_SECTIONS))
_ARTICLE_LEAD_RE = re.compile(r"^\s*(?:-\s*)?(?:a|an|the)\b", re.IGNORECASE)


def _build_working_file(root, session_id):
    """The session's `_build-<session-id>.md`, or the one such file present.

    The server is not told the session id by the harness, so a caller may
    pass it; without one, exactly one working file in the project root is
    taken as this session's, and none or several is a refusal — a tick
    written into another session's file would record work that session
    never did.
    """
    if session_id:
        safe = re.sub(r"[^A-Za-z0-9._-]", "_", session_id)
        path = os.path.join(root, "_build-%s.md" % safe)
        return (path, None) if os.path.isfile(path) else \
            (None, "no build working file at %s." % path)
    found = sorted(name for name in os.listdir(root)
                   if name.startswith("_build-") and name.endswith(".md"))
    if not found:
        return None, "no build working file (_build-<session-id>.md) in %s." \
            % root
    if len(found) > 1:
        return None, "%d build working files in %s (%s) — pass session_id " \
            "to say which is this session's." % (len(found), root,
                                                 ", ".join(found))
    return os.path.join(root, found[0]), None


def _working_file_sections(lines):
    """Map each section name to (header index, index after its last non-blank
    line) — the point new lines are inserted at."""
    headers = [(i, m.group(1)) for i, line in enumerate(lines)
               for m in [_SECTION_HEADER_RE.match(line.rstrip("\r\n"))] if m]
    spans = {}
    for pos, (i, name) in enumerate(headers):
        end = headers[pos + 1][0] if pos + 1 < len(headers) else len(lines)
        last = i
        for j in range(i + 1, end):
            if lines[j].strip():
                last = j
        spans[name] = (i, last + 1)
    return spans


def tool_build_tick(arguments):
    """One checked call for a build item's completion: tick, depth, rule gate,
    index candidate and changes lines into the working file, then the item
    out of Processed."""
    root = project_root()
    queue = _queue_path(root)
    digest = _digest()
    if _mover() is None or digest is None:
        return "Cannot write: reorder_queue.py or queue_digest.py is not " \
               "where this server expects it (%s)." % PLUGIN_ROOT
    if not os.path.isfile(queue):
        return "Cannot write: no QUEUE.md at %s." % queue

    slug = (arguments.get("slug") or "").strip().strip("[]")
    verdict = (arguments.get("verdict") or "").strip().lower()
    reason = (arguments.get("reason") or "").strip()
    depth = (arguments.get("depth") or "").strip().lower()
    trigger = (arguments.get("trigger") or "").strip()
    rule_gate = (arguments.get("rule_gate") or "").strip()
    candidate = (arguments.get("index_candidate") or "").strip()
    changes = (arguments.get("changes") or "").strip("\r\n")
    session_id = (arguments.get("session_id") or "").strip()

    problems = []
    if not slug:
        problems.append("slug is missing — the item being ticked.")
    if verdict not in ("confirmed", "unconfirmed"):
        problems.append("verdict must be `confirmed` or `unconfirmed` — "
                        "choosing between the two tick forms is not optional.")
    if verdict == "unconfirmed" and not reason:
        problems.append("an unconfirmed tick names what still needs running "
                        "— reason is missing.")
    if depth not in ("short", "full"):
        problems.append("depth must be `short` or `full`.")
    if depth == "full" and not trigger:
        problems.append("a full depth names its trigger — reasoning "
                        "contested, or alternative seriously weighed.")
    if not candidate:
        problems.append("index_candidate is missing — the artifact touched "
                        "and the nature of the change.")
    elif _ARTICLE_LEAD_RE.match(candidate):
        problems.append("index_candidate opens with A/An/The — lead with the "
                        "artifact touched, since the index is scanned by its "
                        "opening words.")
    if not changes.strip():
        problems.append("changes is missing — the files this item touched, "
                        "one line each.")

    path, why = _build_working_file(root, session_id)
    if path is None:
        problems.append(why)

    items = digest.parse(queue)
    matches = [i for i in items if i["slug"] == slug
               and i["section"] == "Processed"]
    if slug and not matches:
        problems.append("slug %r is not a work item in Processed." % slug)
    elif len(matches) > 1:
        problems.append("slug %r matches %d Processed items — fix that first."
                        % (slug, len(matches)))
    item = matches[0] if len(matches) == 1 else None
    if item is not None:
        # The digest lowercases prose, so the read is case-insensitive.
        carries_gate = any(line.strip().lower().startswith("rule gate:")
                           for line in item["prose"])
        if carries_gate and not rule_gate:
            problems.append("the queue item carries a `Rule gate:` line, so "
                            "rule_gate is required — copy its disposition "
                            "across unchanged.")
        if rule_gate and not carries_gate:
            problems.append("the queue item carries no `Rule gate:` line, so "
                            "a disposition cannot be written here — the "
                            "gate's site is planning.")
        if rule_gate and not re.match(r"^(run|not needed)\b", rule_gate,
                                      re.IGNORECASE):
            problems.append("rule_gate opens `run — <what>` or "
                            "`not needed — <why>`.")

    text = None
    if path is not None:
        with open(path, "r", encoding="utf-8", newline="") as f:
            text = f.read()
        # The specimen writes the slug bare on the Run and Entries lines;
        # bracketed is accepted too.
        if slug and not re.search(r"(?<![a-z0-9-])%s(?![a-z0-9-])"
                                  % re.escape(slug), text):
            problems.append("[%s] is not in the working file's item list "
                            "(%s)." % (slug, os.path.basename(path)))
        if slug and re.search(r"^Depth:\s*%s\s" % re.escape(slug), text,
                              re.MULTILINE):
            problems.append("[%s] is already ticked in the working file."
                            % slug)
        lines = text.splitlines(keepends=True)
        spans = _working_file_sections(lines)
        for name in ("Index entry candidates", "Progress", "Changes"):
            if name not in spans:
                problems.append("the working file has no `%s:` section." % name)
    if problems:
        return "Refused — nothing was written:\n" + \
               "\n".join("- " + p for p in problems)

    eol = "\r\n" if "\r\n" in text else "\n"
    description = item["heading"]
    tick = "- [x] %s — done, %s" % (
        description, "confirmed" if verdict == "confirmed"
        else "UNCONFIRMED: %s" % reason)
    depth_line = "Depth: %s — %s" % (slug, depth if depth == "short"
                                     else "full, %s" % trigger)
    progress = [tick, depth_line]
    if rule_gate:
        progress.append("Rule gate: %s — %s" % (slug, rule_gate))
    candidate_line = candidate if candidate.startswith("-") else "- " + candidate
    change_lines = [l.rstrip("\r\n") for l in changes.splitlines()]
    change_lines = [l if l.lstrip().startswith("-") else "- " + l
                    for l in change_lines if l.strip()]

    # Insert bottom-up so earlier indices stay valid.
    inserts = [
        (spans["Changes"][1], change_lines),
        (spans["Progress"][1], progress),
        (spans["Index entry candidates"][1], [candidate_line]),
    ]
    for at, new in sorted(inserts, key=lambda p: p[0], reverse=True):
        lines[at:at] = [l + eol for l in new]
    new_text = "".join(lines)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(new_text)

    ok, report = _run_mover([queue, "--delete", slug, "Processed"], root)
    written = "Wrote to %s:\n%s" % (
        os.path.basename(path),
        "\n".join(progress + [candidate_line] + change_lines))
    if not ok:
        return ("%s\nBut the queue tool refused the removal of [%s] from "
                "Processed, so the item still sits in the queue:\n%s"
                % (written, slug, report))
    return "%s\nRemoved [%s] from Processed.\n%s" % (written, slug, report)


TOOLS = [
    {
        "name": "queue_checkpoint_counts",
        "description":
            "How many queue items are ready to build, held below the "
            "cleared-to-run line, and still waiting to be processed. Counts "
            "only — never a recommendation about what to do with them.",
        "inputSchema": {"type": "object", "properties": {}},
        "handler": tool_queue_checkpoint_counts,
    },
    {
        "name": "queue_next_pick",
        "description":
            "Which item the ordering ladder picks next, which rung it fell "
            "to, where that item starts in QUEUE.md, and the item's own text. "
            "Optionally takes the slugs set aside this session, how many "
            "picks have already been made, which the ladder's alternating "
            "rung needs, and the two medians the opening printed, so the "
            "long-and-old groups stay fixed for the pass instead of being "
            "recomputed at every pick. The output names the medians it used "
            "and whether they were passed in or recomputed.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "medians": {
                    "type": "string",
                    "description":
                        "The opening's two medians as `<lines>,<YYYY-MM-DD>` "
                        "— the section's median entry length and median "
                        "filing date. Omitted, both are recomputed from the "
                        "file now and the output says so.",
                },
                "skip": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description":
                        "Slugs set aside for this session, which the script "
                        "cannot see for itself.",
                },
                "picked": {
                    "type": "integer",
                    "description":
                        "How many picks have been made this session. The "
                        "fourth rung alternates on this parity.",
                },
            },
        },
        "handler": tool_queue_next_pick,
    },
    {
        "name": "cycles_state",
        "description":
            "Every cycle definition's cadence and what its observable "
            "currently reads, plus any checklists and their firing words. Facts "
            "as written — computing due-ness from them is the reader's step, "
            "exactly as it is at a session opening.",
        "inputSchema": {"type": "object", "properties": {}},
        "handler": tool_cycles_state,
    },
    {
        "name": "host_currency",
        "description":
            "Whether the installed plugin snapshot carries the current source "
            "files: the installed version and stamp, the source stamp, and "
            "whether they match. A match means host-side changes are live.",
        "inputSchema": {"type": "object", "properties": {}},
        "handler": tool_host_currency,
    },
    {
        "name": "file_capture",
        "description":
            "File one capture at the bottom of the queue's Unprocessed "
            "section. Takes a heading, a slug, the body prose, and optional "
            "blocked_by, not_before and cycle fields; composes the canonical "
            "entry, stamps the filed-at date and time from the clock, and "
            "appends it through the queue tool's own append path. "
            "Refuses only what is checkably wrong — a missing, malformed or "
            "taken slug, a blocker resolving to no entry, an unreal date, a "
            "cycle naming no definition, a heading led by A/An/The — echoing "
            "the reason so the retry is instant. Body prose passes untouched.",
        "inputSchema": {
            "type": "object",
            "required": ["heading", "slug", "body"],
            "properties": {
                "heading": {
                    "type": "string",
                    "description":
                        "One-line description, distinguishing words first, "
                        "without the [slug] — the tool appends it.",
                },
                "slug": {
                    "type": "string",
                    "description": "Kebab-case slug, unique in the queue.",
                },
                "body": {
                    "type": "string",
                    "description":
                        "The rationale prose, passed through untouched.",
                },
                "blocked_by": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description":
                        "Slugs of entries this capture waits on. Each must "
                        "resolve to a real entry in the queue.",
                },
                "not_before": {
                    "type": "string",
                    "description":
                        "YYYY-MM-DD — do not offer this capture again "
                        "before the date. Needs the user's approval, per "
                        "the capture rules.",
                },
                "cycle": {
                    "type": "string",
                    "description":
                        "Slug of a cycle definition this capture is "
                        "material for. Must name a definition in the "
                        "project's cycles doc.",
                },
            },
        },
        "handler": tool_file_capture,
    },
    {
        "name": "append_sent_line",
        "description":
            "Append one line to the project's outbound register, "
            "INBOX/sent.md, for a send or post that has just been approved. "
            "Takes the line's fields — destination, intent, claim, pointer, "
            "and an optional Discord message id — stamps the date and time "
            "from the clock, composes the canonical line and appends it at "
            "the end of the file, changing nothing else. Refuses a missing "
            "field, an intent other than 'for completion' or 'for "
            "continuation', a line break inside a field, or a project with "
            "no INBOX/ folder, echoing the reason. Creates sent.md where "
            "INBOX/ exists and the file does not.",
        "inputSchema": {
            "type": "object",
            "required": ["destination", "intent", "claim", "pointer"],
            "properties": {
                "destination": {
                    "type": "string",
                    "description":
                        "Where it went: the channel, forum, project or "
                        "person, in the register's own words.",
                },
                "intent": {
                    "type": "string",
                    "enum": ["for completion", "for continuation"],
                    "description":
                        "Whether the item was handed over for completion "
                        "(which can close it) or for continuation.",
                },
                "claim": {
                    "type": "string",
                    "description":
                        "What the text claimed, in one clause, read off the "
                        "approved text as it stands.",
                },
                "pointer": {
                    "type": "string",
                    "description": "Where the text lives.",
                },
                "message_id": {
                    "type": "string",
                    "description":
                        "The Discord message or topic id, where there is one.",
                },
            },
        },
        "handler": tool_append_sent_line,
    },
    {
        "name": "hold_entry",
        "description":
            "Write a hold onto one queue entry: a `Blocked by:` line naming "
            "one or more entries, or a `Not before:` date — exactly one of "
            "the two. Composes the canonical line, replaces an existing hold "
            "line of either kind rather than doubling it, and moves a work "
            "item that sat above the cleared-to-run line to the top of the "
            "held region in the same call; a capture gains the field only. "
            "Refuses a slug naming no entry, both or neither field, a blocker "
            "that is not a real entry, the entry naming itself, an unreal "
            "date, or a date already past, echoing the reason. A date on a "
            "capture still needs the user's approval, which no tool can check. "
            "On a capture, until_built writes the hold as `Blocked by: [slug] "
            "until built`, which holds the capture until every named entry "
            "has a build record rather than releasing when one is kept into "
            "Processed; refused on a work item, whose hold already means that.",
        "inputSchema": {
            "type": "object",
            "required": ["slug"],
            "properties": {
                "slug": {
                    "type": "string",
                    "description": "The entry the hold is written on.",
                },
                "blocked_by": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description":
                        "Slugs of the entries this one waits on. Each must "
                        "be a real entry in either section.",
                },
                "not_before": {
                    "type": "string",
                    "description":
                        "YYYY-MM-DD, a future date the entry must not be "
                        "built (work item) or offered again (capture) before.",
                },
                "until_built": {
                    "type": "boolean",
                    "description":
                        "Captures only, with blocked_by: hold the capture "
                        "until every named entry is BUILT, not merely "
                        "processed. Written as the trailing words `until "
                        "built` on the Blocked by: line.",
                },
            },
        },
        "handler": tool_hold_entry,
    },
    {
        "name": "queue_move",
        "description":
            "Move one queue entry within its section — to the top or "
            "bottom, or before/after another entry — through the queue "
            "tool's own move, so every block is carried byte-for-byte. "
            "Refuses at the door a slug or anchor that is not an entry in "
            "that section, a position outside the four words, and a move "
            "that would put any entry across the cleared-to-run marker "
            "with no marker_after named; the queue tool's own refusal of "
            "an unnamed clearing comes back as the answer.",
        "inputSchema": {
            "type": "object",
            "required": ["section", "slug"],
            "properties": dict({
                "section": {
                    "type": "string",
                    "enum": ["Processed", "Unprocessed"],
                    "description": "The section the entry sits in.",
                },
                "slug": {
                    "type": "string",
                    "description": "The entry to move.",
                },
            }, **_MOVE_PROPERTIES),
        },
        "handler": tool_queue_move,
    },
    {
        "name": "queue_move_section",
        "description":
            "Move one entry from one section to the other — the keep-move "
            "from Unprocessed into Processed, or the reverse — through the "
            "queue tool's own cross-section move. Lands at the BOTTOM of "
            "the destination unless position says otherwise; in Processed "
            "the bottom is BELOW the cleared-to-run marker, so a kept entry "
            "that is cleared needs position and marker_after in the same "
            "call. Refuses at the door a slug not in the source section, a "
            "slug already in the destination, an anchor not in the "
            "destination, a bad position word, and a move that would put "
            "any entry across the marker with no marker_after named.",
        "inputSchema": {
            "type": "object",
            "required": ["slug", "from_section", "to_section"],
            "properties": dict({
                "slug": {
                    "type": "string",
                    "description": "The entry to move.",
                },
                "from_section": {
                    "type": "string",
                    "enum": ["Processed", "Unprocessed"],
                    "description": "The section it leaves.",
                },
                "to_section": {
                    "type": "string",
                    "enum": ["Processed", "Unprocessed"],
                    "description": "The section it joins.",
                },
            }, **_MOVE_PROPERTIES),
        },
        "handler": tool_queue_move_section,
    },
    {
        "name": "queue_delete",
        "description":
            "Remove one entry's whole block from the queue, addressed by "
            "slug, through the queue tool's own delete — which re-anchors "
            "the cleared-to-run marker where the deleted entry was its "
            "anchor and reports any other entries still citing the slug. "
            "Refuses at the door a slug that is not an entry in the named "
            "section, or one that matches more than one entry.",
        "inputSchema": {
            "type": "object",
            "required": ["slug", "section"],
            "properties": {
                "slug": {
                    "type": "string",
                    "description": "The entry to delete.",
                },
                "section": {
                    "type": "string",
                    "enum": ["Processed", "Unprocessed"],
                    "description": "The section the entry sits in.",
                },
            },
        },
        "handler": tool_queue_delete,
    },
    {
        "name": "build_tick",
        "description":
            "Close one build item in one checked call: writes the tick line "
            "(`- [x] <description> — done, confirmed` or `— done, "
            "UNCONFIRMED: <reason>`), the slug-bound `Depth:` line, the "
            "slug-bound `Rule gate:` line where the queue item carries one, "
            "the index-entry candidate and the `Changes:` entry into this "
            "session's build working file in the exact shapes next.md's "
            "specimen shows, then removes the item from Processed through "
            "the queue tool's own delete. Refuses at the door a slug not in "
            "the working file's item list or already ticked, a missing "
            "verdict, an unconfirmed tick with no reason, a full depth with "
            "no trigger, a rule-gate line the item does not carry (or a "
            "missing one it does), and an index candidate led by A/An/The.",
        "inputSchema": {
            "type": "object",
            "required": ["slug", "verdict", "depth", "index_candidate",
                         "changes"],
            "properties": {
                "slug": {"type": "string",
                         "description": "The item being ticked."},
                "verdict": {
                    "type": "string", "enum": ["confirmed", "unconfirmed"],
                    "description": "confirmed where something ran and "
                                   "passed; unconfirmed otherwise.",
                },
                "reason": {
                    "type": "string",
                    "description": "Required when unconfirmed: what still "
                                   "needs running.",
                },
                "depth": {
                    "type": "string", "enum": ["short", "full"],
                    "description": "The record's depth for this item.",
                },
                "trigger": {
                    "type": "string",
                    "description": "Required when full: `reasoning "
                                   "contested` or `alternative seriously "
                                   "weighed`.",
                },
                "rule_gate": {
                    "type": "string",
                    "description": "The item's disposition copied "
                                   "unchanged: `run — <what>` or `not "
                                   "needed — <why>`. Required where the "
                                   "queue item carries a Rule gate: line; "
                                   "refused where it does not.",
                },
                "index_candidate": {
                    "type": "string",
                    "description": "The artifact touched and the nature of "
                                   "the change, not led by A/An/The.",
                },
                "changes": {
                    "type": "string",
                    "description": "The files this item touched, one "
                                   "`- path: what changed` line each.",
                },
                "session_id": {
                    "type": "string",
                    "description": "This session's id, naming its "
                                   "_build-<session-id>.md; optional where "
                                   "exactly one working file exists.",
                },
            },
        },
        "handler": tool_build_tick,
    },
]

HANDLERS = {tool["name"]: tool["handler"] for tool in TOOLS}


def _advertised_tools():
    return [{k: v for k, v in tool.items() if k != "handler"}
            for tool in TOOLS]


def handle(message):
    """One request in, one response out — or None for a notification."""
    method = message.get("method")
    request_id = message.get("id")

    # A notification carries no id and is never answered.
    if request_id is None:
        return None

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME,
                               "version": SERVER_VERSION},
            },
        }

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id,
                "result": {"tools": _advertised_tools()}}

    if method == "tools/call":
        params = message.get("params") or {}
        name = params.get("name")
        arguments = params.get("arguments") or {}
        handler = HANDLERS.get(name)
        if handler is None:
            return {"jsonrpc": "2.0", "id": request_id,
                    "error": {"code": -32602,
                              "message": "No such tool: %r" % name}}
        try:
            text = handler(arguments)
        except Exception as error:  # noqa: BLE001 — reported, never raised out
            return {"jsonrpc": "2.0", "id": request_id,
                    "result": {"isError": True,
                               "content": [{"type": "text",
                                            "text": "%s failed: %s"
                                                    % (name, error)}]}}
        return {"jsonrpc": "2.0", "id": request_id,
                "result": {"content": [{"type": "text", "text": text}]}}

    return {"jsonrpc": "2.0", "id": request_id,
            "error": {"code": -32601,
                      "message": "Method not found: %r" % method}}


def main():
    """Read newline-delimited JSON-RPC from stdin, answer on stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            # A malformed line has no id to answer against, so it is dropped
            # rather than answered wrongly.
            continue
        response = handle(message)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
