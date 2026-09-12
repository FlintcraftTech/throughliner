#!/usr/bin/env python3
"""Regression tests for plugin/throughliner/scripts/queue_digest.py.

Host-only dev artifact — not shipped in the plugin package.

Run:  py resources/testing/test_queue_digest.py

No test framework, matching test_reorder_queue.py alongside it: this project has
no test runner, and `python` on the author's machine resolves to an application's
bundled interpreter that has no pytest.

The digest is imported directly rather than run as a subprocess, because what
needs pinning here is what each field computes, not the command-line wrapper.
Each case writes a small project — a QUEUE.md, sometimes a LOG/ folder — into a
temp dir and asserts on the rendered output.

The standing constraint these tests protect: every field reports a fact, never a
verdict. A case asserting that some item is "ready to lift" would be pinning an
interpretation, and interpreting dependency conditions is what this method
retired. Assert on lookups.
"""

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SCRIPT = os.path.join(ROOT, "plugin", "throughliner", "scripts", "queue_digest.py")

_spec = importlib.util.spec_from_file_location("queue_digest", SCRIPT)
digest = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(digest)

MARKER = "--- Cleared to run above this line ---"

# The minimum build block a cleared build or [audit] item must carry. Fixtures
# whose case is about something else include it so the blockless-item check
# below doesn't fire on them and change an unrelated contradiction count.
BLOCK = (
    "--- Build block ---\n"
    "Changes: `docs/a.md` — reword the thing\n"
    "Acceptance: the thing reads right\n"
    "--- End build block ---\n"
)

_failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        _failures.append(name)


BUILT_BODY = "An entry.\n\n**Files touched:** `docs/a.md`\n"
PROCESSED_BODY = "An entry.\n\n**Work processed:** kept [alpha]\n"
OLD_FORMAT_BODY = "An entry from before the per-flavor fields existed.\n"


def project(processed="", unprocessed="", log_entries=()):
    """Write a temp project and return its root. Never a git repository.

    Not being a repo is deliberate for most cases — it exercises the quiet
    degrade of the age field on every run rather than only in the case written
    for it.

    A `log_entries` element is either a filename — which gets a BUILT body, the
    ordinary case — or a `(filename, body)` pair where the record's KIND is what
    the case is about. The body matters because the digest classifies a record by
    reading it: the filename cannot tell a build's record from a planning
    session's.
    """
    d = tempfile.mkdtemp(prefix="digest-test-")
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8") as f:
        f.write(
            "# QUEUE\n\nIntro prose.\n\n## Processed\n\n"
            + processed
            + "\n" + MARKER + "\n\n## Unprocessed\n\n"
            + unprocessed
        )
    if log_entries:
        os.mkdir(os.path.join(d, "LOG"))
        for entry in log_entries:
            name, body = entry if isinstance(entry, tuple) else (entry, BUILT_BODY)
            with open(os.path.join(d, "LOG", name), "w", encoding="utf-8") as f:
                f.write(body)
    return d


def run(root):
    items = digest.parse(os.path.join(root, "QUEUE.md"))
    return items, digest.render(items, root, os.path.join(root, "QUEUE.md"))


def git(cwd, *args):
    return subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True,
                          text=True, encoding="utf-8")


def git_project():
    """A temp project that IS a git repository, with two commits to QUEUE.md.

    The three cases needing real commit dates used to read this project's own
    QUEUE.md at the suite's computed root. Since the wrap of 2026-09-04 the
    queue lives one level above the folder the suite computes, so the open
    failed and the suite aborted before its remaining cases ran. A fixture of
    its own keeps the suite independent of where the project keeps its queue.

    First commit: two entries. Second commit: a third entry plus a held item
    written already held, so first-seen dates differ across commits and the
    held-since field has exactly one commit to attribute to.
    """
    d = tempfile.mkdtemp(prefix="digest-git-")
    git(d, "init", "-q")
    git(d, "config", "user.email", "suite@example.invalid")
    git(d, "config", "user.name", "suite")
    path = os.path.join(d, "QUEUE.md")

    def write(processed):
        with open(path, "w", encoding="utf-8") as f:
            f.write("# QUEUE\n\nIntro prose.\n\n## Processed\n\n" + processed
                    + "\n" + MARKER + "\n\n## Unprocessed\n\n")

    write("#### First item [alpha]\nRationale.\n" + BLOCK
          + "\n#### Second item [beta]\nRationale.\n" + BLOCK)
    git(d, "add", "QUEUE.md")
    git(d, "commit", "-q", "-m", "two entries",
        "--date", "2026-01-01T12:00:00")
    write("#### First item [alpha]\nRationale.\n" + BLOCK
          + "\n#### Second item [beta]\nRationale.\n" + BLOCK
          + "\n#### Third item [gamma]\nRationale.\n" + BLOCK
          + "\n#### A held item [delta]\nRationale.\nBlocked by: [alpha]\n")
    git(d, "add", "QUEUE.md")
    git(d, "commit", "-q", "-m", "a third entry and a held item",
        "--date", "2026-02-01T12:00:00")
    return d


# --- a migration-written build block is surfaced until planning checks it -----

def test_migration_written_block_on_a_cleared_item_is_reported():
    """A block the format migration wrote under an existing item carries a line
    saying so; a cleared item still carrying it never passed the buildability
    check ([migration-marks-unvetted-build-blocks]). Reported as a placement
    contradiction; a held item or a capture carrying the same line is not."""
    marked = (
        "#### Migrated item [migrated]\nRationale.\n" + BLOCK +
        "Build block written by the format migration on 2026-09-01, not yet "
        "checked at planning\n"
    )
    plain = "#### Checked item [checked]\nRationale.\n" + BLOCK
    held = (
        "#### Held migrated item [heldm]\nRationale.\n" + BLOCK +
        "Build block written by the format migration on 2026-09-01, not yet "
        "checked at planning\nBlocked by: [checked]\n"
    )
    root = project(processed=marked + plain, unprocessed="")
    # Move the held one below the marker by rewriting the file.
    path = os.path.join(root, "QUEUE.md")
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    text = text.replace(MARKER + "\n", MARKER + "\n\n" + held)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    _, out = run(root)
    shutil.rmtree(root, ignore_errors=True)
    check("the cleared migrated item is reported",
          "[migrated] is cleared but its build block was written by a migration "
          "and never checked" in out, out)
    check("the checked item is not reported",
          "[checked] is cleared but" not in out, out)
    check("the held migrated item is not reported",
          "[heldm] is cleared but" not in out, out)


# --- the readiness marker is a line, never a substring ------------------------

def test_marker_text_in_prose_does_not_move_the_line():
    """An item may describe how the queue works, quoting the marker text.

    The digest once matched that text as a substring and took the first hit
    inside Processed as the readiness line — so a sentence in an item's own
    rationale silently moved the line, hiding cleared work from the run and
    reporting invented held-since dates. The counts must not move.
    """
    quoting = (
        "#### An item that describes the queue [talker]\n"
        "This explains that /next builds from above the\n"
        "--- Cleared to run above this line --- marker, which is what bounds a run.\n"
    )
    plain = "#### An ordinary second item [quiet]\nRationale.\n"

    baseline = project(processed="#### First [one]\nRationale.\n" + plain)
    _, out_baseline = run(baseline)
    shutil.rmtree(baseline, ignore_errors=True)

    root = project(processed=quoting + plain)
    _, out = run(root)
    check(
        "prose quoting the marker leaves both items cleared",
        "2 cleared to run, 0 held below the line" in out,
        out,
    )
    check(
        "the quoting item is not reported as held",
        "(held," not in out,
        out,
    )
    check(
        "the count matches a queue whose prose says nothing",
        "2 cleared to run, 0 held below the line" in out_baseline,
        out_baseline,
    )
    shutil.rmtree(root, ignore_errors=True)


# --- fields: line count and section median -----------------------------------

def test_line_count_and_median_print():
    """Both fields the ladder's rungs 3 and 4 read must be computed, not judged.

    Rung 3 orders only entries at or above the section median, which is what
    makes it terminate; rung 4 sits beneath it. Neither can read a field the
    digest does not print.
    """
    root = project(
        processed=(
            "#### Short one [short]\nOne line.\n"
            "\n"
            "#### Long one [long]\nLine.\nLine.\nLine.\nLine.\nLine.\nLine.\n"
        ),
    )
    _, out = run(root)
    check("the section median prints once",
          "median entry length:" in out, out)
    check("every entry line carries its own line count",
          out.count("| Lines: ") >= 2, out)
    check("the longer entry is marked at/above median",
          "[long]" in out and "(at/above median)" in out, out)
    shutil.rmtree(root, ignore_errors=True)


def test_median_absent_on_an_empty_section():
    """An empty section has no median, and must not print a made-up one."""
    root = project(processed="", unprocessed="#### Only capture [c]\nProse.\n")
    _, out = run(root)
    processed_block = out.split("## Unprocessed")[0]
    check("no median line on an empty Processed section",
          "median entry length:" not in processed_block, processed_block)
    shutil.rmtree(root, ignore_errors=True)


# --- field: slugs cited, resolved against LOG --------------------------------

def test_shipped_citation_prints():
    root = project(
        processed=(
            "#### Do the thing [alpha]\n"
            "This builds on [beta], which is already done.\n"
            "**Files:** `docs/a.md`\n"
        ),
        log_entries=("2026-08-01-beta.md",),
    )
    _, out = run(root)
    check(
        "a citation with a LOG entry prints on the item's line",
        "Cites shipped: [beta]" in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


def test_processed_record_is_not_reported_as_shipped():
    """A planning session's record must not read as work that was built.

    The whole defect: a plan entry splits per item PROCESSED, so a discussed-
    and-kept item has a record named after it exactly like a built one, and the
    filename cannot tell them apart.
    """
    root = project(
        processed=(
            "#### Do the thing [alpha]\n"
            "This builds on [beta], which was discussed.\n"
        ),
        log_entries=(("2026-08-01-beta.md", PROCESSED_BODY),),
    )
    _, out = run(root)
    check(
        "a record a planning session wrote prints under Cites processed",
        "Cites processed: [beta]" in out,
        out,
    )
    check(
        "and never under Cites shipped",
        "Cites shipped" not in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


def test_old_format_record_is_reported_unclassified():
    """Neither marker present — say so rather than guessing which it was."""
    root = project(
        processed=(
            "#### Do the thing [alpha]\n"
            "This builds on [beta].\n"
        ),
        log_entries=(("2026-08-01-beta.md", OLD_FORMAT_BODY),),
    )
    _, out = run(root)
    check(
        "an older-format record prints as found but unclassified",
        "[beta] (record kind unknown)" in out,
        out,
    )
    check(
        "and is claimed as neither built nor processed",
        "Cites shipped" not in out and "Cites processed" not in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


def test_processed_only_blocker_is_not_reported_as_shipped():
    """The consequence that makes the distinction load-bearing.

    A held item lifts when its blockers resolve. A blocker a planning session
    merely processed has not resolved, so resolving it to a bare record would
    release work whose dependency is still outstanding.
    """
    root = project(
        processed=(
            "#### Do the thing [alpha]\n"
            "Waits for the other work.\n"
            "Blocked by: [beta]\n"
        ),
        log_entries=(("2026-08-01-beta.md", PROCESSED_BODY),),
    )
    _, out = run(root)
    check(
        "a blocker with only a planning record says it was not built",
        "[beta] -> ABSENT, only processed — not built" in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


def test_built_blocker_says_it_was_built():
    root = project(
        processed=(
            "#### Do the thing [alpha]\n"
            "Waits for the other work.\n"
            "Blocked by: [beta]\n"
        ),
        log_entries=("2026-08-01-beta.md",),
    )
    _, out = run(root)
    check(
        "a blocker with a build record says it was built",
        "[beta] -> ABSENT, built" in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


def test_unshipped_citation_stays_quiet():
    root = project(
        processed=(
            "#### Do the thing [alpha]\n"
            "This waits on [gamma], which has not shipped.\n"
        ),
        log_entries=("2026-08-01-beta.md",),
    )
    _, out = run(root)
    check(
        "a citation with no LOG entry prints nothing",
        "gamma" not in out.split("## Placement")[0].split("Cites shipped")[-1]
        and "Cites shipped" not in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


def test_flavor_tag_is_not_a_citation():
    """[freeform] in prose must not resolve as a slug of that name."""
    root = project(
        processed="#### Do the thing [alpha]\nThis is tagged [freeform] work.\n",
        log_entries=("2026-08-01-freeform.md",),
    )
    _, out = run(root)
    check(
        "a flavor tag in prose is not read as a citation",
        "Cites shipped" not in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


def test_co_write_heading_prints_its_flavor_and_is_not_a_citation():
    """A [co-write] heading prints (co-write) as its flavor, and the tag is
    never read as a cited slug."""
    root = project(
        processed="#### [co-write] Finish the readme [beta]\nThe one file: README.md.\n",
        log_entries=("2026-08-01-co-write.md",),
    )
    _, out = run(root)
    check(
        "a co-write heading prints its flavor",
        "co-write" in out,
        out,
    )
    check(
        "the co-write tag is not read as a citation",
        "Cites shipped" not in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


def test_own_slug_is_not_a_citation():
    root = project(
        processed="#### Do the thing [alpha]\nAs [alpha] says, do it.\n",
        log_entries=("2026-08-01-alpha.md",),
    )
    _, out = run(root)
    check(
        "an item citing its own slug does not report itself",
        "Cites shipped" not in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


# --- field: files named by two or more items ---------------------------------

def test_shared_file_is_grouped():
    root = project(
        processed=(
            "#### First [alpha]\n**Files:** `docs/plan.md` (a change)\n\n"
            "#### Second [beta]\n**Files:** `docs/plan.md` (another change)\n"
        ),
    )
    _, out = run(root)
    check(
        "a file named by two items is reported with both slugs",
        "docs/plan.md: [alpha], [beta]" in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


def test_single_file_is_not_grouped():
    root = project(processed="#### Only one [alpha]\n**Files:** `docs/plan.md`\n")
    _, out = run(root)
    check(
        "a file named by one item surfaces nothing",
        "## Files named by two or more items — 0" in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


def test_backticked_non_path_is_ignored():
    """A Files line backticks skill names too; those are not files."""
    root = project(
        processed=(
            "#### First [alpha]\n**Files:** `/plan` and `docs/a.md`\n\n"
            "#### Second [beta]\n**Files:** `/plan` and `docs/b.md`\n"
        ),
    )
    _, out = run(root)
    check(
        "a backticked non-path is not grouped as a file",
        "/plan:" not in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


# --- placement contradictions: chains ----------------------------------------

def test_terminating_chain_is_not_reported():
    """A deliberate pacing chain ending in Unprocessed is correct work.

    Three of these fired on every run of the real queue before the fix, on a
    chain built to the user's own instruction. Each held item's own line already
    prints its blocker, so reporting the chain again said nothing new.
    """
    root = project(
        processed=(
            MARKER + "\n\n"
            "#### First post [post-one]\nProse.\nBlocked by: [wake-up]\n\n"
            "#### Second post [post-two]\nProse.\nBlocked by: [post-one]\n"
        ),
        unprocessed="#### Wake up [wake-up]\nProse.\n",
    )
    _, out = run(root)
    check(
        "a chain terminating outside the held region is not reported",
        "## Placement contradictions — 0" in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


def test_looping_chain_is_reported():
    root = project(
        processed=(
            MARKER + "\n\n"
            "#### One [alpha]\nProse.\nBlocked by: [beta]\n\n"
            "#### Two [beta]\nProse.\nBlocked by: [alpha]\n"
        ),
    )
    _, out = run(root)
    check(
        "a chain that comes back to itself is reported as a loop",
        "loop of blockers" in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


def test_converging_chain_is_not_reported_as_a_loop():
    """A diamond is an ordering, not a cycle.

    C waits on both A and B, and B also waits on A. A visited-set walk reaches A
    twice by two routes and calls the second arrival a loop. Nothing here fails
    to release — A ships, then B, then C — and the false flag invites moving a
    correctly placed item out of Processed, which is a fate decision made on a
    premise that is not true. Reported from a consumer project.
    """
    root = project(
        processed=(
            MARKER + "\n\n"
            "#### A [alpha]\nProse.\nBlocked by: [groundwork]\n\n"
            "#### B [beta]\nProse.\nBlocked by: [alpha]\n\n"
            "#### C [gamma]\nProse.\nBlocked by: [alpha], [beta]\n"
        ),
        unprocessed="#### Groundwork [groundwork]\nProse.\n",
    )
    _, out = run(root)
    check(
        "a converging blocker chain is not reported as a loop",
        "loop of blockers" not in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


def test_loop_reachable_through_a_second_blocker_is_reported():
    """The multi-blocker walk must survive the path fix.

    The cycle runs through the SECOND slug on the line, so a walk following only
    the first named blocker misses it. That was an earlier defect here and the
    path-tracking fix must not reintroduce it.
    """
    root = project(
        processed=(
            MARKER + "\n\n"
            "#### One [alpha]\nProse.\nBlocked by: [harmless], [beta]\n\n"
            "#### Two [beta]\nProse.\nBlocked by: [alpha]\n\n"
            "#### Three [harmless]\nProse.\n"
        ),
    )
    _, out = run(root)
    check(
        "a loop reachable only through a second named blocker is reported",
        "loop of blockers" in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


def test_absent_blocker_is_not_a_loop():
    root = project(
        processed=MARKER + "\n\n#### One [alpha]\nProse.\nBlocked by: [ghost]\n",
    )
    _, out = run(root)
    check(
        "a blocker resolving to nothing is left alone, not called a loop",
        "loop of blockers" not in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


# --- placement contradictions: the do-not-build phrase list -------------------

def test_built_into_is_not_a_do_not_build_phrase():
    """"Must not be built into X" says other work stays out — the opposite."""
    root = project(
        processed=(
            "#### Do the thing [alpha]\n"
            "Other work must not be built into this item; keep it narrow.\n"
            + BLOCK
        ),
    )
    _, out = run(root)
    check(
        "a phrase followed by 'into' does not fire the do-not-build check",
        "## Placement contradictions — 0" in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


def test_do_not_build_still_fires():
    root = project(
        processed=(
            "#### Do the thing [alpha]\nThis must not be built as written.\n"
            + BLOCK
        ),
    )
    _, out = run(root)
    check(
        "a genuine do-not-build statement still fires",
        "must not be built as written" in out and "Placement contradictions — 1" in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


# --- placement contradictions: a capture bearing on cleared work --------------

def test_capture_naming_a_cleared_item_is_flagged():
    """The recorded instance: newly filed work invalidating cleared work.

    Nothing else looks for this, and it was caught once only because one
    session happened to be holding both entries in view.
    """
    root = project(
        processed="#### Do the thing [alpha]\nRationale for alpha.\n" + BLOCK,
        unprocessed=(
            "#### Something learned later [beta]\n"
            "This turns out to bear on [alpha], which cannot be built as "
            "written.\n"
        ),
    )
    _, out = run(root)
    check(
        "a capture naming a cleared item is flagged",
        "[beta] is a capture whose prose names [alpha]" in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


def test_capture_naming_another_capture_is_not_flagged():
    """The flag is about work about to be BUILT, so only cleared work counts.

    Captures cross-reference each other constantly; firing on that would make
    the flag noise on the first run and learned past by the second.
    """
    root = project(
        processed="#### Do the thing [alpha]\nRationale for alpha.\n" + BLOCK,
        unprocessed=(
            "#### Something learned later [beta]\nThis bears on [gamma].\n"
            "\n#### Something else [gamma]\nRationale for gamma.\n"
        ),
    )
    _, out = run(root)
    check(
        "a capture naming another capture is not flagged",
        "is a capture whose prose names" not in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


# --- the retired cleared-item-with-no-build-block report ---------------------
#
# Retired 2026-08-27 ([builds-read-the-queue-again]). It existed because a run
# read a generated view assembled from delimited build blocks, so an item
# without one reached the run with nothing to build from. A run now reads each
# item whole from the queue: there is no block that can be missing, and whether
# an item says what changes inside the files it names is judgment the decision
# step makes, which no delimiter test can answer.
#
# What is asserted here is the SILENCE, which is the part that could regress. A
# leftover report would fire on every item in every real queue from now on,
# since none of them will carry the delimiters.

def test_no_build_block_report_survives():
    for label, kwargs in [
        ("a cleared build item with no delimiters",
         {"processed": "#### Do the thing [alpha]\nProse, and no block.\n"}),
        ("a cleared [audit] item with no delimiters",
         {"processed": "#### [audit] Review the thing [alpha]\nProse.\n"}),
        ("a [user] item carrying only a walkthrough",
         {"processed": ("#### [user] Do the manual thing [alpha]\n"
                        "**Walkthrough.** 1. Do it. 2. Confirm.\n")}),
        ("an unprocessed capture",
         {"unprocessed": "#### An idea [gamma]\nSomething noticed.\n"}),
    ]:
        root = project(**kwargs)
        _, out = run(root)
        check(
            f"{label} draws no build-block report",
            "carries no build block" not in out,
            out,
        )
        shutil.rmtree(root, ignore_errors=True)


# --- field: age ---------------------------------------------------------------

def test_no_git_degrades_quietly():
    """A project that is not a git repository gets no dates and no noise."""
    root = project(processed="#### Do the thing [alpha]\nProse.\n")
    items, out = run(root)
    check(
        "first_seen returns nothing outside a git repository",
        digest.first_seen(root, os.path.join(root, "QUEUE.md")) == {},
    )
    check(
        "no date is printed and no error appears in the output",
        "First seen" not in out and "error" not in out.lower(),
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


def test_age_prints_in_a_git_repository():
    """A git repo with a committed QUEUE.md yields a first-seen date per slug.

    Run against a fixture repository of its own (see `git_project`), never
    against this project's queue. Skipped rather than failed where git itself
    is unavailable — a machine without git is a legitimate state, and the
    degrade case above is what pins the behaviour that matters.
    """
    root = git_project()
    dates = digest.first_seen(root, os.path.join(root, "QUEUE.md"))
    if not dates:
        print("  skip first-seen dates (git unavailable on this machine)")
        shutil.rmtree(root, ignore_errors=True)
        return
    check(
        "every date is an ISO day",
        all(len(d) == 10 and d[4] == "-" for d in dates.values()),
        str(list(dates.items())[:3]),
    )
    check(
        "every committed slug has a date",
        set(dates) == {"alpha", "beta", "gamma", "delta"},
        str(sorted(dates)),
    )
    check(
        "a slug added in the second commit carries the later date",
        dates["alpha"] < dates["gamma"],
        "%s vs %s" % (dates["alpha"], dates["gamma"]),
    )
    shutil.rmtree(root, ignore_errors=True)


def test_runs_alone_reports_what_is_ahead_of_it():
    """A correctly placed `Runs alone` item recedes as the queue is worked.

    /next stops BEFORE it, so it is reached only once everything ahead is built
    — and every planning session adds newly ready work ahead of it. Nothing in
    the queue shows that happening, and it was noticed once only because someone
    happened to say it out loud.

    A count is reportable where an age is not: how long something has been ready
    would need a threshold nobody can derive.
    """
    root = project(
        processed=(
            "#### First [a]\nProse.\n"
            "\n"
            "#### Second [b]\nProse.\n"
            "\n"
            "#### The one that runs alone [c]\nProse.\nRuns alone\n"
        ),
    )
    _, out = run(root)
    check("the runs-alone block appears",
          "Runs-alone work" in out, out[-400:])
    check("it counts the two cleared items ahead",
          "[c]: 2 cleared item(s) ahead" in out, out[-400:])
    shutil.rmtree(root, ignore_errors=True)


def test_no_runs_alone_work_says_none():
    """A computed zero must not look like a check that never ran."""
    root = project(processed="#### Ordinary [a]\nProse.\n")
    _, out = run(root)
    block = out.split("Runs-alone work")[1]
    check("no runs-alone work reports none", "- none" in block, block[:200])
    shutil.rmtree(root, ignore_errors=True)


def test_whats_next_answers_only_the_pick():
    """The scoped mode prints the rung, the item, its line number and its text.

    Nothing else: the whole point is that re-deriving a pick costs a scoped
    call rather than the full digest, which runs to thousands of tokens.
    """
    root = project(
        unprocessed=(
            "#### Cited by another entry [alpha]\nProse.\n"
            "\n"
            "#### Cites alpha [beta]\nThis depends on [alpha].\n"
        ),
    )
    out = digest.render_whats_next(
        digest.parse(os.path.join(root, "QUEUE.md")), root,
        os.path.join(root, "QUEUE.md"))
    check("the rung is named", out.startswith("Rung "), out)
    check("the top item is the most-cited one", "[alpha]" in out, out)
    check("its starting line number is given", "Starts at line" in out, out)
    check("its text is included", "Prose." in out, out)
    check("nothing else is printed", "median entry length" not in out, out)
    shutil.rmtree(root, ignore_errors=True)


def test_whats_next_rung_changes_when_the_queue_changes_beneath_it():
    """The rung is re-derived at every pick, which is why this is a recurring
    cost and not a field the opening digest could carry."""
    root = project(
        unprocessed=(
            "#### Carries an uncleared risk [risky]\nProse.\n"
            "Red flag · State: uncleared\n"
            "\n"
            "#### Cited by another entry [alpha]\nProse.\n"
            "\n"
            "#### Cites alpha [beta]\nThis depends on [alpha].\n"
        ),
    )
    queue = os.path.join(root, "QUEUE.md")
    items = digest.parse(queue)

    rung, _, item = digest.whats_next(items, root, queue)
    check("an uncleared red flag takes rung 1",
          rung == 1 and item["slug"] == "risky", f"rung {rung}")

    rung, _, item = digest.whats_next(items, root, queue, skip=("risky",))
    check("skipping it falls through to rung 3 (unblock potential)",
          rung == 3 and item["slug"] == "alpha", f"rung {rung}")
    shutil.rmtree(root, ignore_errors=True)


def test_whats_next_cycle_pass_over_and_due_rung():
    """A `Cycle:` naming a live definition never returns; a capture filed
    UNDER a definition's own slug is due cycle work and ranks at rung 2.
    A Cycle: naming no definition is a deleted cycle's release and ranks."""
    root = project(
        unprocessed=(
            "#### Tip pool entry [tip-something]\nProse.\n"
            "Cycle: [tips-posting]\n"
            "\n"
            "#### First tips turn due [tips-posting]\nProse.\n"
            "\n"
            "#### Ordinary capture [ordinary]\nProse.\n"
        ),
    )
    with open(os.path.join(root, "CYCLES.md"), "w", encoding="utf-8") as f:
        f.write("# Cycles\n\n## Tips posting [tips-posting]\n\nCadence: x.\n")
    queue = os.path.join(root, "QUEUE.md")
    rung, _, item = digest.whats_next(digest.parse(queue), root, queue)
    check("a due-turn capture ranks at rung 2",
          rung == 2 and item["slug"] == "tips-posting",
          f"rung {rung}, {item and item['slug']}")
    rung, _, item = digest.whats_next(digest.parse(queue), root, queue,
                                      skip=("tips-posting",))
    check("cycle-owned material is never returned",
          item["slug"] == "ordinary", str(item and item["slug"]))
    os.remove(os.path.join(root, "CYCLES.md"))
    _, _, item = digest.whats_next(digest.parse(queue), root, queue,
                                   skip=("tips-posting", "ordinary"))
    check("a deleted cycle releases its material",
          item is not None and item["slug"] == "tip-something",
          str(item and item["slug"]))
    shutil.rmtree(root, ignore_errors=True)


def test_whats_next_holds_the_openings_medians_when_passed():
    """The ladder fixes both medians at the opening; a pick that recomputes
    them drifts from that promise silently.

    Two entries, one long. With the medians recomputed from the file, the
    long one qualifies for the alternating rung's long pick; with the opening's
    medians passed in — here a length no entry reaches — nothing is long and
    the pick falls to oldest-first. The output names which it used.
    """
    root = project(
        unprocessed=(
            "#### A short entry [short]\nOne line.\n"
            "\n"
            "#### A long entry [long]\nLine.\nLine.\nLine.\nLine.\nLine.\n"
            "Line.\nLine.\n"
        ),
    )
    queue = os.path.join(root, "QUEUE.md")
    items = digest.parse(queue)
    _, _, recomputed = digest.whats_next(items, root, queue, picked=1)
    _, _, held = digest.whats_next(items, root, queue, picked=1,
                                   medians=(100, None))
    check("recomputed medians make the long entry the long pick",
          recomputed["slug"] == "long", repr(recomputed["slug"]))
    check("the opening's medians change the pick",
          held["slug"] != recomputed["slug"], repr(held["slug"]))
    out = digest.render_whats_next(items, root, queue, picked=1)
    check("the output names recomputed medians",
          "medians:" in out and "recomputed" in out, out)
    out = digest.render_whats_next(items, root, queue, picked=1,
                                   medians=(100, "2026-09-04"))
    check("the output names passed-in medians",
          "medians: 100 lines, 2026-09-04 — passed in" in out, out)
    check("the argument parses", digest.parse_medians("7,2026-09-04")
          == (7, "2026-09-04") and digest.parse_medians("x") is None)
    shutil.rmtree(root, ignore_errors=True)


def test_whats_next_respects_a_capture_bowing_out():
    """`Not before:` on a capture means do not OFFER it again, which is what a
    pick does."""
    root = project(
        unprocessed=(
            "#### Waiting on something outside the project [held]\nProse.\n"
            "Not before: 2999-01-01\n"
            "\n"
            "#### Ordinary capture [ordinary]\nProse.\n"
        ),
    )
    queue = os.path.join(root, "QUEUE.md")
    _, _, item = digest.whats_next(digest.parse(queue), root, queue)
    check("a dated-out capture is not offered",
          item["slug"] == "ordinary", str(item and item["slug"]))
    shutil.rmtree(root, ignore_errors=True)


def test_capture_held_on_a_processed_item_is_offerable():
    """A capture's `Blocked by:` releases once the named entry is in Processed:
    the rule reads "processed or built", and a kept item counts as processed
    ([digest-offerable-reads-processed-or-built])."""
    root = project(
        processed=(
            "#### Kept item [kept]\nProse.\n" + BLOCK + "\n" + MARKER + "\n"
        ),
        unprocessed=(
            "#### Waiting on the kept item [waits]\nProse.\n"
            "Blocked by: [kept]\n"
        ),
    )
    queue = os.path.join(root, "QUEUE.md")
    items = digest.parse(queue)
    pool = [i["slug"] for i in digest.offerable(items, root)]
    check("a capture held on a Processed item is in the pool",
          pool == ["waits"], str(pool))
    _, _, item = digest.whats_next(items, root, queue)
    check("--next offers it", item is not None and item["slug"] == "waits",
          str(item and item["slug"]))
    shutil.rmtree(root, ignore_errors=True)


def test_capture_held_until_built_waits_for_the_build_record():
    """`Blocked by: [slug] until built` holds a capture past the blocker's
    processing: kept into Processed and not built, the capture stays out of
    the pool; with a build record it returns. The same line without the words
    releases on the keep ([capture-hold-says-designed-or-shipped])."""
    root = project(
        processed=(
            "#### Kept item [kept]\nProse.\n" + BLOCK + "\n" + MARKER + "\n"
        ),
        unprocessed=(
            "#### Waiting for the build [waits-build]\nProse.\n"
            "Blocked by: [kept] until built\n"
            "\n"
            "#### Waiting for the keep [waits-keep]\nProse.\n"
            "Blocked by: [kept]\n"
        ),
    )
    queue = os.path.join(root, "QUEUE.md")
    items = digest.parse(queue)
    pool = [i["slug"] for i in digest.offerable(items, root)]
    check("the qualified capture is passed over while the same bare line is offered",
          pool == ["waits-keep"], str(pool))
    _, _, item = digest.whats_next(items, root, queue)
    check("--next does not offer the qualified capture",
          item is not None and item["slug"] == "waits-keep",
          str(item and item["slug"]))
    _, out = run(root)
    line = [l for l in out.splitlines() if "[waits-build]" in l]
    check("the digest line prints the qualifier",
          line and "until built" in line[0], str(line))
    shutil.rmtree(root, ignore_errors=True)

    # With a build record for the blocker, the qualified capture returns.
    root = project(
        unprocessed=(
            "#### Waiting for the build [waits-build]\nProse.\n"
            "Blocked by: [kept] until built\n"
        ),
        log_entries=["2026-09-12-kept.md"],
    )
    queue = os.path.join(root, "QUEUE.md")
    pool = [i["slug"] for i in digest.offerable(digest.parse(queue), root)]
    check("a built blocker releases the qualified capture",
          pool == ["waits-build"], str(pool))
    shutil.rmtree(root, ignore_errors=True)


def test_capture_held_on_an_unprocessed_item_still_bows_out():
    """A named entry still in Unprocessed holds the capture, as before."""
    root = project(
        unprocessed=(
            "#### Still a capture [open]\nProse.\n"
            "\n"
            "#### Waiting on the open capture [waits]\nProse.\n"
            "Blocked by: [open]\n"
        ),
    )
    queue = os.path.join(root, "QUEUE.md")
    pool = [i["slug"] for i in digest.offerable(digest.parse(queue), root)]
    check("a capture held on an Unprocessed entry is not in the pool",
          pool == ["open"], str(pool))
    shutil.rmtree(root, ignore_errors=True)


def test_full_print_names_how_many_cite_a_capture():
    """The per-entry line on a capture carries a cited-by count where other
    entries name its slug ([opening-names-blocking-captures])."""
    root = project(
        unprocessed=(
            "#### The umbrella [umbrella]\nProse.\n"
            "\n"
            "#### First dependent [one]\nProse.\nBlocked by: [umbrella]\n"
            "\n"
            "#### Second dependent [two]\nWaits on [umbrella] too.\n"
        ),
    )
    queue = os.path.join(root, "QUEUE.md")
    text = digest.render(digest.parse(queue), root, queue)
    line = next(l for l in text.splitlines() if "[umbrella]" in l and l.startswith("- "))
    check("the umbrella's line says two other entries cite it",
          "Cited by: 2 other entries" in line, line)
    shutil.rmtree(root, ignore_errors=True)


def test_incoming_citations_are_computed_not_guessed():
    """Rung 2's field is computed here and nowhere else, which is what makes
    'every rung reads a computed field' true rather than aspirational."""
    root = project(
        unprocessed=(
            "#### Cited twice [alpha]\nProse.\n"
            "\n"
            "#### First citer [beta]\nSee [alpha].\n"
            "\n"
            "#### Second citer [gamma]\nAlso [alpha].\n"
        ),
    )
    counts = digest.incoming_citations(
        digest.parse(os.path.join(root, "QUEUE.md")))
    check("the count is two", counts.get("alpha") == 2, str(counts))
    check("an entry does not cite itself", counts.get("beta") == 0, str(counts))
    shutil.rmtree(root, ignore_errors=True)


def _with_research(root, name, body):
    """Drop a research file into a fixture project."""
    folder = os.path.join(root, "workshop", "resources", "research")
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
        f.write(body)
    return root


def test_copied_finding_flags_the_item_as_resting_on_a_snapshot():
    """A finding another project owns is copied in, never pointed at.

    The citing item then rests on a copy taken on a date, and the digest says
    so. The label is permanent: nothing reads the owning project, so this is
    not and must never be described as a staleness check.
    """
    root = project(
        processed=(
            "#### Scoped on a sibling's finding [a]\n"
            "Rests on resources/research/borrowed-finding.md.\n"
        ),
    )
    _with_research(
        root, "borrowed-finding.md",
        "# Borrowed finding\n\n"
        "**Copied from: the recipe project** — what the connector returns, "
        "copied 2026-08-20\n\nBody.\n",
    )
    _, out = run(root)
    check("the citing item is flagged as resting on a snapshot",
          "[a] rests on a SNAPSHOT" in out, out[-600:])
    check("the flag names the owning project",
          "the recipe project" in out, out[-600:])
    check("the output states it is not a staleness check",
          "not a staleness check" in out, out[-900:])
    shutil.rmtree(root, ignore_errors=True)


def test_research_without_the_copied_line_prints_no_snapshot_flag():
    """The other direction: an ordinary local finding is not a snapshot."""
    root = project(
        processed=(
            "#### Scoped on our own finding [a]\n"
            "Rests on resources/research/local-finding.md.\n"
        ),
    )
    _with_research(root, "local-finding.md",
                   "# Local finding\n\nBody, owned here.\n")
    _, out = run(root)
    check("no snapshot flag for a finding this project owns",
          "rests on a SNAPSHOT" not in out, out[-600:])
    shutil.rmtree(root, ignore_errors=True)


def test_median_age_is_computed_not_judged():
    """Rung 3 is an intersection of two medians, so BOTH must be printed.

    The length half was already computed. The age half was not, and the rung
    cannot read a field the digest does not print — working the median date out
    by hand is the judgment the ladder exists to remove.

    Run against a fixture repository, because a median age needs real commit
    dates. Skipped rather than failed where git is unavailable, exactly as the
    first-seen test above is.
    """
    root = git_project()
    dates = digest.first_seen(root, os.path.join(root, "QUEUE.md"))
    if not dates:
        print("  skip median age (git unavailable on this machine)")
        shutil.rmtree(root, ignore_errors=True)
        return
    queue = os.path.join(root, "QUEUE.md")
    out = digest.render(digest.parse(queue), root, queue)
    text = "\n".join(out) if isinstance(out, list) else out
    check("the section median age prints", "median first seen:" in text, text[:400])
    check("at least one entry is marked at/above median age",
          "(at/above median age)" in text, text[:400])
    shutil.rmtree(root, ignore_errors=True)


def test_median_age_absent_without_dates():
    """No git history means no dates, so no median age may be invented.

    The length median still prints — it needs no history — which is what makes
    this worth pinning separately: the two medians degrade independently.
    """
    root = project(processed="#### Do the thing [alpha]\nProse.\nProse.\n")
    _, out = run(root)
    check("no median age line without git history",
          "median first seen:" not in out, out)
    check("the length median still prints",
          "median entry length:" in out, out)
    shutil.rmtree(root, ignore_errors=True)


def test_held_since_degrades_without_git():
    """No repository, no date — and no error, exactly as first_seen degrades.

    The attribution limit is pinned by the same case: `held_dates` is filled
    from the same git pass, so where there is no pass there is nothing to fill
    and the field simply does not print.
    """
    root = project(processed="#### An item [alpha]\nRationale.\n")
    path = os.path.join(root, "QUEUE.md")
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    text = text.replace(
        "## Unprocessed",
        "#### A held item [gamma]\nRationale.\nBlocked by: [alpha]\n\n"
        "## Unprocessed",
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    _, out = run(root)
    check(
        "held-since prints nothing outside a git repository, and no error",
        "Held since" not in out and "error" not in out.lower(),
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


def test_held_since_attributes_within_one_commit():
    """A hold added beside its heading is attributed; one added alone is not.

    This is the honest half of the field. `first_seen` walks the queue's patch
    history with no context lines, so a hold line can be tied to an item only
    when the two arrived together — the ordinary case, since an item is
    normally written already held.
    """
    root = git_project()
    held = {}
    dates = digest.first_seen(root, os.path.join(root, "QUEUE.md"), held)
    if not dates:
        print("  skip held-since (git unavailable on this machine)")
        shutil.rmtree(root, ignore_errors=True)
        return
    check(
        "every held-since date is an ISO day",
        all(len(d) == 10 and d[4] == "-" for d in held.values()),
        str(list(held.items())[:3]),
    )
    check(
        "held-since never invents a date for an item first_seen doesn't know",
        set(held) <= set(dates),
        str(set(held) - set(dates)),
    )
    check(
        "the item written already held is attributed to its own commit",
        held.get("delta") == dates.get("delta"),
        "held %r, first seen %r" % (held.get("delta"), dates.get("delta")),
    )
    check(
        "an item never held gets no held-since date",
        "alpha" not in held,
        str(held),
    )
    shutil.rmtree(root, ignore_errors=True)


def test_not_before_prints_with_its_state():
    """The field, and the fact of whether the date has arrived.

    Both directions in one case: a date far in the future counts down, a date
    already past says so. This is a lookup against today's calendar, not an
    interpretation of a dependency condition — nobody has to confirm that a day
    has passed, which is the whole reason the field exists.
    """
    root = project(
        processed=(
            "#### An ordinary cleared item [alpha]\nRationale.\n"
        ),
    )
    with open(os.path.join(root, "QUEUE.md"), "a", encoding="utf-8") as f:
        pass
    # Rewrite with two held items below the marker.
    path = os.path.join(root, "QUEUE.md")
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    text = text.replace(
        "## Unprocessed",
        "#### Waits for a future day [future]\nRationale.\n"
        "Not before: 2099-01-01\n\n"
        "#### Waited for a day now past [past]\nRationale.\n"
        "Not before: 2000-01-01\n\n## Unprocessed",
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    _, out = run(root)
    check(
        "a future date prints with how far away it is",
        "Not before: 2099-01-01 -> " in out and "day(s) away" in out,
        out,
    )
    check(
        "a date that has arrived says so",
        "Not before: 2000-01-01 -> passed, ready to lift" in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


def test_unreadable_not_before_says_so():
    root = project(processed="#### An item [alpha]\nRationale.\n")
    path = os.path.join(root, "QUEUE.md")
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    text = text.replace(
        "## Unprocessed",
        "#### Held on something unreadable [bad]\nRationale.\n"
        "Not before: soon\n\n## Unprocessed",
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    _, out = run(root)
    check(
        "a date nobody can read is named rather than ignored",
        "NOT A DATE" in out,
        out,
    )
    shutil.rmtree(root, ignore_errors=True)


def test_unblock_potential_singular():
    """One citing entry reads "1 other entry cites it", not "1 other entries
    cite it" ([lint-gone-notice-repeats-every-call])."""
    d = project(unprocessed=(
        "#### Cited once [alpha]\nRationale.\n\n"
        "#### Cites alpha [beta]\nWaits on [alpha] in its prose.\n"))
    items = digest.parse(os.path.join(d, "QUEUE.md"))
    rung, why, item = digest.whats_next(items, d, os.path.join(d, "QUEUE.md"))
    check("singular: the cited entry is picked",
          rung == 3 and item is not None and item["slug"] == "alpha",
          repr((rung, why)))
    check("singular: one citer reads as one entry",
          "1 other entry cites it" in why, repr(why))


if __name__ == "__main__":
    print("test_queue_digest.py")
    test_unblock_potential_singular()
    test_migration_written_block_on_a_cleared_item_is_reported()
    test_marker_text_in_prose_does_not_move_the_line()
    test_line_count_and_median_print()
    test_median_absent_on_an_empty_section()
    test_shipped_citation_prints()
    test_processed_record_is_not_reported_as_shipped()
    test_old_format_record_is_reported_unclassified()
    test_processed_only_blocker_is_not_reported_as_shipped()
    test_built_blocker_says_it_was_built()
    test_unshipped_citation_stays_quiet()
    test_flavor_tag_is_not_a_citation()
    test_co_write_heading_prints_its_flavor_and_is_not_a_citation()
    test_own_slug_is_not_a_citation()
    test_shared_file_is_grouped()
    test_single_file_is_not_grouped()
    test_backticked_non_path_is_ignored()
    test_terminating_chain_is_not_reported()
    test_looping_chain_is_reported()
    test_converging_chain_is_not_reported_as_a_loop()
    test_loop_reachable_through_a_second_blocker_is_reported()
    test_absent_blocker_is_not_a_loop()
    test_built_into_is_not_a_do_not_build_phrase()
    test_do_not_build_still_fires()
    test_capture_naming_a_cleared_item_is_flagged()
    test_capture_naming_another_capture_is_not_flagged()
    test_no_build_block_report_survives()
    test_no_git_degrades_quietly()
    test_age_prints_in_a_git_repository()
    test_runs_alone_reports_what_is_ahead_of_it()
    test_no_runs_alone_work_says_none()
    test_whats_next_answers_only_the_pick()
    test_whats_next_rung_changes_when_the_queue_changes_beneath_it()
    test_whats_next_cycle_pass_over_and_due_rung()
    test_whats_next_holds_the_openings_medians_when_passed()
    test_whats_next_respects_a_capture_bowing_out()
    test_capture_held_on_a_processed_item_is_offerable()
    test_capture_held_on_an_unprocessed_item_still_bows_out()
    test_capture_held_until_built_waits_for_the_build_record()
    test_full_print_names_how_many_cite_a_capture()
    test_incoming_citations_are_computed_not_guessed()
    test_copied_finding_flags_the_item_as_resting_on_a_snapshot()
    test_research_without_the_copied_line_prints_no_snapshot_flag()
    test_median_age_is_computed_not_judged()
    test_median_age_absent_without_dates()
    test_held_since_degrades_without_git()
    test_held_since_attributes_within_one_commit()
    test_not_before_prints_with_its_state()
    test_unreadable_not_before_says_so()
    print()
    if _failures:
        print(f"{len(_failures)} failure(s): " + ", ".join(_failures))
        sys.exit(1)
    print("all passed")
