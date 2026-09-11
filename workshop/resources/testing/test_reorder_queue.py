#!/usr/bin/env python3
"""Regression tests for plugin/throughliner/scripts/reorder_queue.py.

Host-only dev artifact — not shipped in the plugin package.

Run:  python resources/testing/test_reorder_queue.py

No test framework required, deliberately: this project has no test runner and
adding one to guard a single script would cost more than it protects. Each test
writes a small QUEUE.md into a temp dir, runs the mover as a subprocess exactly
the way /plan drives it, and asserts on the resulting file.

The headline case is `marker above all items`. That shape made the mover refuse
EVERY reorder of Processed — not just the greenlighting move — because the
marker scan started at the first `####` item and so never matched a marker
sitting above them all. The defect is a scan-range off-by-one, which is easy to
reintroduce, so it gets a permanent case here.
"""

import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SCRIPT = os.path.join(ROOT, "plugin", "throughliner", "scripts", "reorder_queue.py")

MARKER = "--- Cleared to run above this line ---"

_failures = []


def build_queue(processed_body, unprocessed_body="#### Later thing [later]\nSome rationale.\n"):
    return (
        "# QUEUE\n\n"
        "Intro prose that must survive untouched.\n\n"
        "## Processed\n\n"
        + processed_body
        + "\n## Unprocessed\n\n"
        + unprocessed_body
    )


def run(text, *args):
    """Write `text` to a temp QUEUE.md, run the mover, return (rc, stderr, new_text)."""
    d = tempfile.mkdtemp(prefix="reorder-test-")
    path = os.path.join(d, "QUEUE.md")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    proc = subprocess.run(
        [sys.executable, SCRIPT, path] + list(args),
        capture_output=True, text=True,
    )
    with open(path, "r", encoding="utf-8", newline="") as f:
        return proc.returncode, proc.stderr, f.read()


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        _failures.append(name)


def order_of(text, section="## Processed"):
    """Slugs, in file order, within a section — plus MARKER where it sits."""
    out = []
    inside = False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line.strip() == section
            continue
        if not inside:
            continue
        if line.strip() == MARKER:
            out.append(MARKER)
        elif line.startswith("#### "):
            out.append(line.rstrip().rsplit("[", 1)[1].rstrip("]"))
    return out


# --- --replace-in ([pointer-drift-unfixable-at-a-build-close]) ---------------

REPLACE_QUEUE = (
    "#### First thing [first]\n"
    "Rationale naming resources/research/old-name.md once.\n\n"
    "#### Second thing [second]\n"
    "Rationale also naming resources/research/old-name.md — a different entry.\n"
)


def test_replace_in_fires():
    rc, err, out = run(build_queue(REPLACE_QUEUE),
                       "--replace-in", "first",
                       "--old", "resources/research/old-name.md",
                       "--new", "resources/research/new-name.md")
    check("replace-in succeeds", rc == 0, err)
    check("target entry updated",
          "Rationale naming resources/research/new-name.md once." in out, out)
    check("other entry untouched",
          "Rationale also naming resources/research/old-name.md" in out, out)
    check("replacement reported", "replaced in [first]" in err, err)


def test_replace_in_refuses_non_unique():
    text = build_queue(
        "#### First thing [first]\n"
        "Names old-name.md twice: old-name.md again.\n"
    )
    rc, err, out = run(text, "--replace-in", "first",
                       "--old", "old-name.md", "--new", "new-name.md")
    check("non-unique refuses", rc != 0, err)
    check("non-unique changes nothing", "old-name.md twice: old-name.md" in out)


def test_replace_in_refuses_absent_match():
    rc, err, out = run(build_queue(REPLACE_QUEUE),
                       "--replace-in", "first",
                       "--old", "not-in-the-entry.md", "--new", "x.md")
    check("absent match refuses", rc != 0, err)
    check("absent match changes nothing",
          "resources/research/old-name.md once." in out)


def test_replace_in_refuses_unknown_slug():
    rc, err, out = run(build_queue(REPLACE_QUEUE),
                       "--replace-in", "no-such-slug",
                       "--old", "a", "--new", "b")
    check("unknown slug refuses", rc != 0, err)


def test_replace_in_reaches_unprocessed():
    rc, err, out = run(build_queue(REPLACE_QUEUE),
                       "--replace-in", "later",
                       "--old", "Some rationale.", "--new", "Fresh rationale.")
    check("unprocessed entry reachable", rc == 0, err)
    check("unprocessed entry updated", "Fresh rationale." in out, out)


# --- the regression case ------------------------------------------------------

def test_marker_above_all_items():
    """Marker sitting above every item must not block a plain reorder."""
    body = (
        MARKER + "\n\n"
        "#### First item [alpha]\nRationale for alpha.\n\n"
        "#### Second item [beta]\nRationale for beta.\n"
    )
    rc, err, new = run(build_queue(body), "Processed", "beta", "alpha")
    check("marker-above-all: exits 0", rc == 0, err)
    check("marker-above-all: no self-check failure", "self-check failed" not in err, err)
    check("marker-above-all: no bogus 'no marker' warning",
          "section has no marker" not in err, err)
    check("marker-above-all: items swapped, marker still at top",
          order_of(new) == [MARKER, "beta", "alpha"], repr(order_of(new)))
    check("marker-above-all: marker appears exactly once",
          new.count(MARKER) == 1, str(new.count(MARKER)))
    check("marker-above-all: block text preserved byte-for-byte",
          "#### First item [alpha]\nRationale for alpha." in new
          and "#### Second item [beta]\nRationale for beta." in new)
    check("marker-above-all: other section untouched", "#### Later thing [later]" in new)


def test_marker_above_all_explicit_placement():
    """With the marker above all items, --marker-after must still be honoured."""
    body = (
        MARKER + "\n\n"
        "#### First item [alpha]\nRationale for alpha.\n\n"
        "#### Second item [beta]\nRationale for beta.\n"
    )
    rc, err, new = run(build_queue(body), "Processed", "alpha", "beta",
                       "--marker-after", "alpha")
    check("marker-above-all + --marker-after: exits 0", rc == 0, err)
    check("marker-above-all + --marker-after: marker moved below alpha",
          order_of(new) == ["alpha", MARKER, "beta"], repr(order_of(new)))


def test_marker_above_all_move_mode():
    """--move mode hits the same split_blocks path and must work too."""
    body = (
        MARKER + "\n\n"
        "#### First item [alpha]\nRationale for alpha.\n\n"
        "#### Second item [beta]\nRationale for beta.\n"
    )
    rc, err, new = run(build_queue(body), "Processed", "--move", "beta", "TOP")
    check("marker-above-all + --move: exits 0", rc == 0, err)
    check("marker-above-all + --move: beta on top, marker still at top",
          order_of(new) == [MARKER, "beta", "alpha"], repr(order_of(new)))


# --- the shapes that already worked, kept so the fix doesn't break them --------

def test_marker_between_items():
    body = (
        "#### First item [alpha]\nRationale for alpha.\n\n"
        + MARKER + "\n\n"
        "#### Second item [beta]\nRationale for beta.\n"
    )
    rc, err, new = run(build_queue(body), "Processed", "alpha", "beta")
    check("marker-between: exits 0", rc == 0, err)
    check("marker-between: marker keeps its relative spot",
          order_of(new) == ["alpha", MARKER, "beta"], repr(order_of(new)))


def test_marker_below_all_items():
    body = (
        "#### First item [alpha]\nRationale for alpha.\n\n"
        "#### Second item [beta]\nRationale for beta.\n\n"
        + MARKER + "\n"
    )
    rc, err, new = run(build_queue(body), "Processed", "beta", "alpha")
    check("marker-below-all: exits 0", rc == 0, err)
    # Documented behaviour with no --marker-after: the marker keeps its RELATIVE
    # spot — immediately after whichever slug it currently follows (beta), which
    # after this swap is no longer the bottom.
    check("marker-below-all: marker follows the slug it followed before",
          order_of(new) == ["beta", MARKER, "alpha"], repr(order_of(new)))
    rc, err, new = run(build_queue(body), "Processed", "beta", "alpha",
                       "--marker-after", "BOTTOM")
    check("marker-below-all + BOTTOM: pinned to the bottom",
          rc == 0 and order_of(new) == ["beta", "alpha", MARKER],
          err + repr(order_of(new)))


def test_section_with_no_marker():
    body = (
        "#### First item [alpha]\nRationale for alpha.\n\n"
        "#### Second item [beta]\nRationale for beta.\n"
    )
    rc, err, new = run(build_queue(body), "Processed", "beta", "alpha")
    check("no-marker: exits 0", rc == 0, err)
    check("no-marker: no marker invented", MARKER not in new)
    check("no-marker: reordered", order_of(new) == ["beta", "alpha"], repr(order_of(new)))


def test_no_marker_with_marker_after_warns():
    body = (
        "#### First item [alpha]\nRationale for alpha.\n\n"
        "#### Second item [beta]\nRationale for beta.\n"
    )
    rc, err, new = run(build_queue(body), "Processed", "beta", "alpha",
                       "--marker-after", "alpha")
    check("no-marker + --marker-after: still succeeds", rc == 0, err)
    check("no-marker + --marker-after: warns and ignores",
          "section has no marker" in err, err)


def test_slug_set_mismatch_refuses():
    body = (
        "#### First item [alpha]\nRationale for alpha.\n\n"
        "#### Second item [beta]\nRationale for beta.\n"
    )
    original = build_queue(body)
    rc, err, new = run(original, "Processed", "beta")
    check("mismatch: exits non-zero", rc != 0, err)
    check("mismatch: file unchanged", new == original)


# --- the delete operation -----------------------------------------------------

def test_delete_clean():
    """A plain delete removes exactly one block and leaves the rest byte-exact."""
    body = (
        "#### First item [alpha]\nRationale for alpha.\n\n"
        "#### Second item [beta]\nRationale for beta.\n\n"
        + MARKER + "\n\n"
        "#### Third item [gamma]\nRationale for gamma.\n"
    )
    rc, err, new = run(build_queue(body), "--delete", "beta", "Processed")
    check("delete-clean: exits 0", rc == 0, err)
    check("delete-clean: item gone", "[beta]" not in new, repr(order_of(new)))
    check("delete-clean: its rationale gone too", "Rationale for beta." not in new)
    check("delete-clean: order otherwise intact",
          order_of(new) == ["alpha", MARKER, "gamma"], repr(order_of(new)))
    check("delete-clean: surviving blocks byte-for-byte",
          "#### First item [alpha]\nRationale for alpha." in new
          and "#### Third item [gamma]\nRationale for gamma." in new)
    check("delete-clean: other section untouched", "#### Later thing [later]" in new)
    check("delete-clean: names the heading it removed",
          "First item" not in err and "Second item [beta]" in err, err)


def test_delete_unknown_slug_refuses():
    """An unresolvable slug changes nothing and exits non-zero."""
    body = "#### First item [alpha]\nRationale for alpha.\n\n" + MARKER + "\n"
    text = build_queue(body)
    rc, err, new = run(text, "--delete", "nosuchthing", "Processed")
    check("delete-unknown: exits non-zero", rc != 0, err)
    check("delete-unknown: file unchanged", new == text)
    check("delete-unknown: says it refuses rather than guessing",
          "refuses rather than guessing" in err, err)


def test_delete_last_item_in_section():
    """Deleting the only item leaves a valid, empty section with its marker."""
    body = "#### Only item [solo]\nRationale for solo.\n\n" + MARKER + "\n"
    rc, err, new = run(build_queue(body), "--delete", "solo", "Processed")
    check("delete-last: exits 0", rc == 0, err)
    check("delete-last: item gone", "[solo]" not in new)
    check("delete-last: marker survives", new.count(MARKER) == 1, str(new.count(MARKER)))
    check("delete-last: intro prose untouched",
          "Intro prose that must survive untouched." in new)


def test_delete_marker_anchor_reanchors():
    """Deleting the item the marker sits after must not lose the marker.

    The dangerous case: the marker is anchored to the deleted item, so a naive
    rebuild drops it — and a queue with no marker reads as nothing cleared,
    silently unclearing every item above the line.
    """
    body = (
        "#### First item [alpha]\nRationale for alpha.\n\n"
        "#### Second item [beta]\nRationale for beta.\n\n"
        + MARKER + "\n\n"
        "#### Third item [gamma]\nRationale for gamma.\n"
    )
    rc, err, new = run(build_queue(body), "--delete", "beta", "Processed")
    check("delete-anchor: marker survives", new.count(MARKER) == 1, str(new.count(MARKER)))
    check("delete-anchor: marker keeps its position",
          order_of(new) == ["alpha", MARKER, "gamma"], repr(order_of(new)))


def test_move_marker_anchor_does_not_drag_the_marker():
    """Moving the item the marker sits after must NOT drag the marker with it.

    The observed failure, 2026-08-06: `--move <anchor> AFTER <shelved-item>`
    with no --marker-after given. The marker is stored as an anchor slug rather
    than a position, so it followed its anchor down the section and a
    deliberately-shelved item ended up ABOVE the line — cleared for an
    unattended run nobody had authorised. The script reported only
    "marker placed".

    delete_item() had carried a re-anchor branch since it was written; the
    reorder path (used by --move and the full-slug-list form) did not. The
    discriminator is whether the moved item is the marker's anchor, NOT which
    command name was used — a `--move-section` call can hit it too.
    """
    body = (
        "#### First item [alpha]\nRationale for alpha.\n\n"
        "#### Second item [beta]\nRationale for beta.\n\n"
        + MARKER + "\n\n"
        "#### Third item [gamma]\nDeliberately shelved.\n\n"
        "#### Fourth item [delta]\nRationale for delta.\n"
    )
    rc, err, new = run(build_queue(body),
                       "Processed", "--move", "beta", "AFTER", "gamma")
    check("move-anchor: exits 0", rc == 0, err)
    check("move-anchor: marker survives", new.count(MARKER) == 1,
          str(new.count(MARKER)))
    check("move-anchor: marker holds its position, gamma stays shelved",
          order_of(new) == ["alpha", MARKER, "gamma", "beta", "delta"],
          repr(order_of(new)))
    check("move-anchor: the crossing is reported, not silent",
          "crossed the readiness line" in err and "beta" in err, err)
    check("move-anchor: the message states the marker's real position",
          "above the line" in err, err)


def test_move_non_anchor_leaves_marker_alone():
    """A move that doesn't touch the anchor must leave the marker exactly where
    it was — the negative half, so the re-anchor branch can't over-fire."""
    body = (
        "#### First item [alpha]\nRationale for alpha.\n\n"
        "#### Second item [beta]\nRationale for beta.\n\n"
        + MARKER + "\n\n"
        "#### Third item [gamma]\nRationale for gamma.\n"
    )
    rc, err, new = run(build_queue(body),
                       "Processed", "--move", "gamma", "TOP")
    check("move-nonanchor: exits 0", rc == 0, err)
    check("move-nonanchor: marker still sits after beta",
          order_of(new) == ["gamma", "alpha", "beta", MARKER],
          repr(order_of(new)))


def test_unnamed_crossing_refusal_names_one_move_per_item():
    """A refused clearing names the route that clears several held items
    without retyping the section: one --move per item, each naming itself
    as --marker-after ([marker-guard-escape-hatch-is-full-retype])."""
    body = (
        "#### First item [alpha]\nRationale for alpha.\n\n"
        + MARKER + "\n\n"
        "#### Second item [beta]\nHeld.\n\n"
        "#### Third item [gamma]\nHeld.\n\n"
        "#### Fourth item [delta]\nHeld.\n"
    )
    rc, err, new = run(build_queue(body), "Processed",
                       "--move", "delta", "AFTER", "alpha",
                       "--marker-after", "gamma")
    check("crossing-refusal: refuses", rc != 0, err)
    check("crossing-refusal: names the one-move-per-item route",
          "one --move per item" in err and "crosses only what it names" in err,
          err)
    check("crossing-refusal: nothing written",
          order_of(new) == ["alpha", MARKER, "beta", "gamma", "delta"],
          repr(order_of(new)))


def test_unnamed_downward_sweep_refuses():
    """A move naming a build as the last cleared item while `[user]` items
    sit after it would drop those items below the line; it is refused, each
    crossing item is named, and the file is byte-identical afterwards
    ([queue-move-downward-sweep-unguarded])."""
    body = (
        "#### First build [alpha]\nRationale.\n\n"
        "#### Second build [beta]\nRationale.\n\n"
        "#### [user] Walk one [gamma]\nWalkthrough.\n\n"
        "#### [user] Walk two [delta]\nWalkthrough.\n\n"
        + MARKER + "\n\n"
        "#### Held [epsilon]\nHeld.\n"
    )
    text = build_queue(body)
    rc, err, new = run(text, "Processed",
                       "--move", "alpha", "AFTER", "beta",
                       "--marker-after", "alpha")
    check("downward-sweep: refuses", rc != 0, err)
    check("downward-sweep: names each item that would drop",
          "[gamma]" in err and "[delta]" in err and "DROP" in err, err)
    check("downward-sweep: names the one-move-per-item route",
          "one --move per item" in err, err)
    check("downward-sweep: file byte-identical", new == text)
    # The same sweep through --move-section: keeping a capture at the bottom
    # with the marker after it drops nothing, but placing the marker after a
    # build ahead of the walk-throughs does.
    rc2, err2, new2 = run(text, "--move-section", "later", "Unprocessed",
                          "Processed", "--position", "AFTER", "beta",
                          "--marker-after", "later")
    check("downward-sweep via --move-section: refuses", rc2 != 0, err2)
    check("downward-sweep via --move-section: names the walk-throughs",
          "[gamma]" in err2 and "[delta]" in err2, err2)
    check("downward-sweep via --move-section: file byte-identical", new2 == text)


def test_move_explicit_marker_after_still_wins():
    """An explicit --marker-after is the caller asking for the marker to move,
    so the re-anchor branch must not override it."""
    body = (
        "#### First item [alpha]\nRationale for alpha.\n\n"
        "#### Second item [beta]\nRationale for beta.\n\n"
        + MARKER + "\n\n"
        "#### Third item [gamma]\nRationale for gamma.\n"
    )
    rc, err, new = run(build_queue(body), "Processed",
                       "--move", "beta", "BOTTOM", "--marker-after", "alpha")
    check("move-explicit-marker: exits 0", rc == 0, err)
    check("move-explicit-marker: honoured over the re-anchor",
          order_of(new) == ["alpha", MARKER, "gamma", "beta"],
          repr(order_of(new)))


def test_delete_first_item_when_marker_anchored_to_it():
    """Deleting the only item above the marker re-anchors the marker to TOP."""
    body = (
        "#### First item [alpha]\nRationale for alpha.\n\n"
        + MARKER + "\n\n"
        "#### Second item [beta]\nRationale for beta.\n"
    )
    rc, err, new = run(build_queue(body), "--delete", "alpha", "Processed")
    check("delete-first: exits 0", rc == 0, err)
    check("delete-first: marker survives at the top",
          order_of(new) == [MARKER, "beta"], repr(order_of(new)))


def test_delete_block_containing_heading_like_lines():
    """A block whose rationale contains #### text must delete whole and alone."""
    body = (
        "#### First item [alpha]\n"
        "Rationale mentioning a heading shape: '#### Not a real item [fake]'.\n"
        "More rationale.\n\n"
        "#### Second item [beta]\nRationale for beta.\n\n"
        + MARKER + "\n"
    )
    rc, err, new = run(build_queue(body), "--delete", "beta", "Processed")
    check("delete-headinglike: exits 0", rc == 0, err)
    check("delete-headinglike: beta gone", "[beta]" not in new)
    check("delete-headinglike: alpha's heading-shaped prose survives",
          "'#### Not a real item [fake]'" in new)


def test_delete_from_unprocessed():
    """The other section works the same way — /plan's most frequent delete."""
    rc, err, new = run(
        build_queue("#### Kept [alpha]\nRationale.\n\n" + MARKER + "\n"),
        "--delete", "later", "Unprocessed",
    )
    check("delete-unprocessed: exits 0", rc == 0, err)
    check("delete-unprocessed: item gone", "[later]" not in new)
    check("delete-unprocessed: Processed untouched",
          order_of(new) == ["alpha", MARKER], repr(order_of(new)))


def test_move_section_after_last_cleared_reports_below():
    """AFTER the marker's own anchor item lands the block BELOW the marker —
    the observed 2026-08-07 defect. The mover now REPORTS which side the item
    ended on, so the ambiguity is visible at the moment it happens."""
    rc, err, new = run(
        build_queue("#### Kept [alpha]\nRationale.\n\n" + MARKER + "\n"),
        "--move-section", "later", "Unprocessed", "Processed",
        "--position", "AFTER", "alpha",
    )
    check("move-section-after-anchor: exits 0", rc == 0, err)
    check("move-section-after-anchor: lands below the marker",
          order_of(new)[:3] == ["alpha", MARKER, "later"], repr(order_of(new)))
    check("move-section-after-anchor: reports BELOW",
          "BELOW the cleared-to-run marker" in err, err)


def test_move_section_top_reports_above():
    """--position TOP lands above the marker and the mover says so."""
    rc, err, new = run(
        build_queue("#### Kept [alpha]\nRationale.\n\n" + MARKER + "\n"),
        "--move-section", "later", "Unprocessed", "Processed",
        "--position", "TOP",
    )
    check("move-section-top: exits 0", rc == 0, err)
    check("move-section-top: reports ABOVE",
          "ABOVE the cleared-to-run marker" in err, err)


def test_delete_reports_inbound_citations():
    """A delete names the items whose prose still cites the deleted slug.

    Until this printed, those were found by grepping afterwards — one delete
    left five citing items, repaired across three passes, the first incomplete
    because the grep output was truncated.
    """
    text = build_queue(
        "#### The one being deleted [alpha]\nRationale.\n\n"
        "#### A citing item [beta]\nThis builds on [alpha].\n\n"
        + MARKER + "\n"
    )
    rc, err, _ = run(text, "--delete", "alpha", "Processed")
    check("delete with citations: exits 0", rc == 0, err)
    check("delete reports the citing item", "[beta]" in err and "cite" in err, err)
    check(
        "delete does not assert the citation is wrong",
        "often correct as written" in err,
        err,
    )


def test_delete_skips_cycle_lines_in_the_citation_note():
    """A `Cycle:` line names a cycle definition, not the deleted capture.

    Deleting a spent [tips-posting] turn capture once listed all twenty-five
    candidates in the tips pool as citing it, because each carries
    `Cycle: [tips-posting]`. A prose citation must still be reported.
    """
    text = build_queue(
        "#### Unrelated cleared work [gamma]\nRationale.\n\n" + MARKER + "\n",
        "#### Tips turn due [tips-posting]\nRationale.\n\n"
        "#### Tip candidate one [tip-one]\nProse.\nCycle: [tips-posting]\n\n"
        "#### Tip candidate two [tip-two]\nProse.\nCycle: [tips-posting]\n\n"
        "#### Talks about the turn [delta]\nSee [tips-posting] for why.\n",
    )
    rc, err, _ = run(text, "--delete", "tips-posting", "Unprocessed")
    check("delete with cycle lines: exits 0", rc == 0, err)
    check("cycle lines are not reported as citations",
          "[tip-one]" not in err and "[tip-two]" not in err, err)
    check("a prose citation is still reported", "[delta]" in err, err)


def test_delete_reports_nothing_when_uncited():
    """The other half — a report that fires on every delete is one people skip."""
    text = build_queue(
        "#### The one being deleted [alpha]\nRationale.\n\n"
        "#### An unrelated item [beta]\nNothing to do with it.\n\n"
        + MARKER + "\n"
    )
    rc, err, _ = run(text, "--delete", "alpha", "Processed")
    check("delete without citations: exits 0", rc == 0, err)
    check("no citation note when nothing cites it", "cite" not in err, err)


# --- atomic write with one retry ([mcp-write-invalid-argument-transient]) ---

def _load_mover():
    import importlib.util
    spec = importlib.util.spec_from_file_location("reorder_queue_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _refusing_replace(mod, refusals):
    """Patch the module's os.replace to refuse `refusals` times with the
    EINVAL shape the sync client produced, then behave normally. Returns
    the restore function."""
    real = mod.os.replace
    state = {"left": refusals}

    def fake(src, dst):
        if state["left"] > 0:
            state["left"] -= 1
            raise OSError(22, "Invalid argument", dst)
        return real(src, dst)
    mod.os.replace = fake
    return lambda: setattr(mod.os, "replace", real)


def test_write_retries_once_on_a_refused_handle():
    """One refusal: the script says it is waiting and trying again, then the
    write lands whole."""
    import io, contextlib
    mod = _load_mover()
    mod.RETRY_PAUSE_SECONDS = 0
    d = tempfile.mkdtemp(prefix="reorder-retry-")
    path = os.path.join(d, "QUEUE.md")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("old\n")
    restore = _refusing_replace(mod, 1)
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            mod._write_with_one_retry(path, "new — résumé\n")
    finally:
        restore()
    with open(path, "r", encoding="utf-8", newline="") as f:
        got = f.read()
    check("retry: says it is trying again", "trying again" in err.getvalue(),
          err.getvalue())
    check("retry: the write landed whole and byte-identical",
          got == "new — résumé\n", repr(got))
    check("retry: no temp file left behind",
          not os.path.exists(path + ".tmp-reorder"))


def test_write_names_what_to_check_on_a_second_refusal():
    """Two refusals: the script stops, names a sync client or an editor as
    what to check, and the queue is as it was."""
    import io, contextlib
    mod = _load_mover()
    mod.RETRY_PAUSE_SECONDS = 0
    d = tempfile.mkdtemp(prefix="reorder-retry-")
    path = os.path.join(d, "QUEUE.md")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("old\n")
    restore = _refusing_replace(mod, 2)
    err = io.StringIO()
    exited = False
    try:
        with contextlib.redirect_stderr(err):
            mod._write_with_one_retry(path, "new\n")
    except SystemExit:
        exited = True
    finally:
        restore()
    with open(path, "r", encoding="utf-8", newline="") as f:
        got = f.read()
    check("second refusal: the script stops", exited, err.getvalue())
    check("second refusal: names a sync client or an editor",
          "sync client" in err.getvalue() and "editor" in err.getvalue(),
          err.getvalue())
    check("second refusal: the queue is as it was", got == "old\n", repr(got))


def test_write_through_temp_path_is_byte_identical_over_non_ascii():
    """An ordinary move through the temp-and-replace path leaves every
    non-ASCII byte of the untouched blocks as it was."""
    body = (
        "#### First — with an em-dash [alpha]\nRationale — résumé, “curly”.\n\n"
        "#### Second [beta]\n¡Con acentos!\n\n"
        + MARKER + "\n"
    )
    text = build_queue(body)
    rc, err, new = run(text, "Processed", "--move", "beta", "TOP")
    check("temp-path write: exits 0", rc == 0, err)
    check("temp-path write: the alpha block is byte-identical",
          "#### First — with an em-dash [alpha]\nRationale — résumé, “curly”.\n"
          in new, repr(new))
    check("temp-path write: the intro prose is byte-identical",
          "Intro prose that must survive untouched." in new, repr(new))


# --- reporting, marker placement, retitle, write_verified, append stamping ----
#
# Merged 2026-09-11 from the suite that sat beside the script
# ([two-reorder-queue-suites-both-run]); names kept. Three faults were found
# in this script's OUTPUT rather than its writes — across every use, the file
# operations were correct and every fault was in what the tool said about
# them. The mover's messages are trusted and acted on without re-reading the
# file, so a wrong report matters more than a cosmetic wrong message.
# [mover-console-encoding-mangles-output] deliberately shipped without a test,
# because the failure would not reproduce in any shell available here.

# A held item whose `Blocked by:` names the item being moved — exactly what
# exists whenever the move matters. TWO cleared items, deliberately: an item's
# block runs to the next heading, so "AFTER the last cleared item" spans the
# marker and legitimately lands the moved item below it. Anchoring to the
# FIRST of two puts the moved item unambiguously above the marker.
FIXTURE = """# QUEUE

## Processed

#### First cleared item [alpha]
Rationale for alpha.

#### Second cleared item [delta]
Rationale for delta.

--- Cleared to run above this line ---

#### A held item [gamma]
Rationale for gamma.
Blocked by: [beta]

## Unprocessed

#### The item being moved [beta]
Rationale for beta.
"""


def run_move(queue_path):
    return subprocess.run(
        [sys.executable, SCRIPT, queue_path,
         "--move-section", "beta", "Unprocessed", "Processed",
         "--position", "AFTER", "alpha"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def test_side_of_marker_report():
    """The moved item lands above the marker, and the report must say so."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(FIXTURE)

        result = run_move(path)
        output = result.stdout + result.stderr

        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

        marker_i = next(i for i, l in enumerate(lines)
                        if "Cleared to run above this line" in l)
        beta_i = next(i for i, l in enumerate(lines)
                      if l.startswith("#### ") and l.rstrip().endswith("[beta]"))

        check("file places the item above the marker", beta_i < marker_i,
              f"(item at {beta_i}, marker at {marker_i})")
        check("report says ABOVE", "ABOVE" in output, f"got: {output.strip()}")
        check("report does not say BELOW", "BELOW" not in output,
              f"got: {output.strip()}")
        check("report does not call it waiting",
              "NOT cleared to run" not in output, f"got: {output.strip()}")
        check("the held item's Blocked by line survives the move",
              any(l.strip() == "Blocked by: [beta]" for l in lines))


def test_report_agrees_with_file():
    """The tool's claim and the file must never disagree — the real defect."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(FIXTURE)

        result = run_move(path)
        output = result.stdout + result.stderr

        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        marker_i = next(i for i, l in enumerate(lines)
                        if "Cleared to run above this line" in l)
        beta_i = next(i for i, l in enumerate(lines)
                      if l.startswith("#### ") and l.rstrip().endswith("[beta]"))

        said_above = "ABOVE" in output
        is_above = beta_i < marker_i
        check("report agrees with the file", said_above == is_above,
              f"(said ABOVE={said_above}, actually above={is_above})")


def test_move_section_marker_after_the_moved_item_is_refused():
    """Anchoring the marker to the item just placed, with a cleared item
    below it, is the drop guard's case: delta would be swept below the line
    with nothing saying why. Refused, and the file untouched.

    This case used to assert the opposite — that the call succeeds and the
    marker lands after beta — and predates the guard (added 2026-09-06).
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(FIXTURE)

        result = subprocess.run(
            [sys.executable, SCRIPT, path,
             "--move-section", "beta", "Unprocessed", "Processed",
             "--position", "AFTER", "alpha", "--marker-after", "beta"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        output = result.stdout + result.stderr

        check("the sweep behind the moved item is refused",
              result.returncode != 0, f"exit {result.returncode}: {output}")
        check("the refusal names the item it would drop",
              "DROP" in output and "[delta]" in output, f"got: {output}")
        check("nothing was written",
              open(path, "r", encoding="utf-8").read() == FIXTURE)


def test_move_section_applies_marker_after():
    """A cross-section move can place the readiness marker in the same call.

    Moving an item into Processed AND clearing it is the ordinary shape of
    keeping work at /plan, so it must be one command. It used to be two: this
    branch accepted --marker-after and silently ignored it, exiting 0 with the
    move applied and the marker untouched. `--marker-after` names the LAST
    item that should stay cleared — delta, not the item just placed.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(FIXTURE)

        result = subprocess.run(
            [sys.executable, SCRIPT, path,
             "--move-section", "beta", "Unprocessed", "Processed",
             "--position", "AFTER", "alpha", "--marker-after", "delta"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        output = result.stdout + result.stderr

        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        marker_i = next(i for i, l in enumerate(lines)
                        if "Cleared to run above this line" in l)
        beta_i = next(i for i, l in enumerate(lines)
                      if l.startswith("#### ") and l.rstrip().endswith("[beta]"))
        delta_i = next(i for i, l in enumerate(lines)
                       if l.startswith("#### ") and l.rstrip().endswith("[delta]"))

        check("the call succeeds", result.returncode == 0,
              f"exit {result.returncode}: {output.strip()}")
        check("the item landed in Processed above the marker", beta_i < marker_i,
              f"(item at {beta_i}, marker at {marker_i})")
        check("the marker sits after the last item that should stay cleared",
              beta_i < delta_i < marker_i,
              f"(beta {beta_i}, delta {delta_i}, marker {marker_i})")
        check("report says ABOVE", "ABOVE" in output, f"got: {output.strip()}")


def test_move_section_marker_failure_writes_nothing():
    """Both halves, or neither. A half-applied queue edit is worse than a refusal.

    The readiness marker decides how much work an unattended /next run may
    build with nobody present, so a move that lands while its marker placement
    fails is the dangerous outcome, not the tidy one.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(FIXTURE)

        result = subprocess.run(
            [sys.executable, SCRIPT, path,
             "--move-section", "beta", "Unprocessed", "Processed",
             "--position", "AFTER", "alpha", "--marker-after", "no-such-slug"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        output = result.stdout + result.stderr

        with open(path, "r", encoding="utf-8") as f:
            after = f.read()

        check("the call refuses", result.returncode != 0,
              f"exit {result.returncode}")
        check("the error names the bad marker slug", "no-such-slug" in output,
              f"got: {output.strip()}")
        check("the file is byte-for-byte unchanged", after == FIXTURE,
              "the move was applied despite the marker failing")


def test_delete_reports_only_what_landed():
    """The success line must mean the item really left the file.

    A --delete once printed its normal success line, exited zero, and left the
    item in place. /next reads that line as proof an item was built and
    removed, so a false success breaks the one guarantee the copy-per-item
    design rests on. This asserts the ordinary path genuinely lands.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(FIXTURE)

        result = subprocess.run(
            [sys.executable, SCRIPT, path, "--delete", "delta", "Processed"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        with open(path, "r", encoding="utf-8") as f:
            after = f.read()

        check("the delete succeeds", result.returncode == 0,
              f"exit {result.returncode}: {result.stderr.strip()}")
        check("the item is really gone from the file", "[delta]" not in after,
              "success was reported but the slug is still in the file")


def test_retitle_changes_the_heading_and_nothing_else():
    """--retitle rewrites one heading line; every other byte is identical
    ([queue-tool-no-heading-fix])."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(FIXTURE)
        result = subprocess.run(
            [sys.executable, SCRIPT, path, "--retitle", "gamma",
             "--heading", "Held item, distinguishing words first"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        with open(path, "r", encoding="utf-8") as f:
            after = f.read()
        expected = FIXTURE.replace(
            "#### A held item [gamma]",
            "#### Held item, distinguishing words first [gamma]")
        check("the retitle succeeds", result.returncode == 0,
              f"exit {result.returncode}: {result.stderr.strip()}")
        check("the heading changed and every other byte is identical",
              after == expected, "file differs beyond the heading line")
        check("old and new heading are reported",
              "old: #### A held item [gamma]" in result.stderr
              and "new: #### Held item, distinguishing words first [gamma]"
              in result.stderr, result.stderr.strip())


def test_retitle_refuses_a_bracketed_heading():
    """A heading carrying a bracket would read as a second slug: refused, and
    the file is untouched."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(FIXTURE)
        result = subprocess.run(
            [sys.executable, SCRIPT, path, "--retitle", "gamma",
             "--heading", "Held item [other]"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        with open(path, "r", encoding="utf-8") as f:
            after = f.read()
        check("a bracketed heading is refused", result.returncode != 0,
              "exit 0")
        check("the file is untouched", after == FIXTURE, "file changed")


def test_write_verified_refuses_a_write_that_did_not_land():
    """The verification itself fails loudly when the re-read disagrees.

    Simulated by asking write_verified to confirm the absence of a slug the
    written content still contains — which is exactly the state a write that
    silently did not land would leave behind.
    """
    mod = _load_mover()
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        lines = FIXTURE.splitlines(keepends=True)
        raised = False
        try:
            mod.write_verified(path, lines, absent=[("alpha", "Processed")])
        except SystemExit as exc:
            raised = exc.code != 0
        check("a write that did not land exits non-zero", raised,
              "write_verified reported success for a slug still in the file")


def test_move_section_refuses_an_unnamed_sweep():
    """A marker relocation that would CLEAR held items the caller never named.

    The recorded failure: `--position BOTTOM --marker-after <the moved slug>`
    put the marker below four held items and swept every one of them into the
    cleared region, reporting only that the moved item was now cleared. Here
    gamma is held; placing beta at the bottom and anchoring the marker to it
    would clear gamma too.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(FIXTURE)
        before = open(path, "r", encoding="utf-8").read()

        result = subprocess.run(
            [sys.executable, SCRIPT, path,
             "--move-section", "beta", "Unprocessed", "Processed",
             "--position", "BOTTOM", "--marker-after", "beta"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        output = result.stdout + result.stderr

        check("the sweep is refused", result.returncode != 0,
              f"exit {result.returncode}: {output}")
        check("the refusal names the swept item", "[gamma]" in output,
              f"got: {output}")
        check("nothing was written",
              open(path, "r", encoding="utf-8").read() == before)


def test_named_move_across_the_line_still_reports_and_succeeds():
    """The behaviour the refusal must NOT take: a deliberate, named crossing.

    Moving an item across the line is a legitimate way to clear or shelve work.
    The original code reported rather than refused for exactly this case, and
    that reasoning is unchanged — only unnamed crossings are new. gamma lands
    after alpha, and `--marker-after` names delta, the last item that should
    stay cleared, so gamma crosses into the cleared region and nothing is swept.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(FIXTURE)

        result = subprocess.run(
            [sys.executable, SCRIPT, path, "Processed",
             "--move", "gamma", "AFTER", "alpha", "--marker-after", "delta"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        output = result.stdout + result.stderr

        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        marker_i = next(i for i, l in enumerate(lines)
                        if "Cleared to run above this line" in l)
        gamma_i = next(i for i, l in enumerate(lines)
                       if l.startswith("#### ") and l.rstrip().endswith("[gamma]"))

        check("the named move succeeds", result.returncode == 0,
              f"exit {result.returncode}: {output}")
        check("the crossing is reported",
              "crossed the readiness line" in output, f"got: {output}")
        check("the moved item sits above the marker", gamma_i < marker_i,
              f"(gamma {gamma_i}, marker {marker_i})")


def test_append_stamps_an_unstamped_capture():
    """A capture appended without a stamp gains one, read from the clock, as
    the last prose line — before any field lines.

    The capture tool stamped every capture it filed; this route stamped none,
    and a planning session that filed everything through it wrote 34 clock
    times by hand, each counted up from the opening ([invented-clock-times-in-
    planning-writes]).
    """
    mod = _load_mover()
    body = ["#### A capture [zeta]\n", "Its rationale.\n",
            "Blocked by: [alpha]\n"]
    out = mod.stamp_filed_at(list(body))
    check("an unstamped body gains exactly one stamp line",
          len(out) == 4 and sum(1 for l in out if "stamped by the queue tool" in l) == 1,
          repr(out))
    check("the stamp lands before the field lines",
          out[2].startswith("Filed ") and out[3] == "Blocked by: [alpha]\n",
          repr(out))
    check("the stamp carries a clock time",
          re.match(r"^Filed \d{4}-\d{2}-\d{2} \d{2}:\d{2}, stamped by the queue tool\.\n$",
                   out[2]) is not None, repr(out[2]))

    # End to end through --append: the stamp is in the file.
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "QUEUE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(FIXTURE)
        body_path = os.path.join(tmp, "body.md")
        with open(body_path, "w", encoding="utf-8") as f:
            f.write("#### Another capture [eta]\nRationale for eta.\n")
        result = subprocess.run(
            [sys.executable, SCRIPT, path, "--append", "Unprocessed",
             "--body", body_path],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        with open(path, "r", encoding="utf-8") as f:
            after = f.read()
        check("--append succeeds", result.returncode == 0, result.stderr.strip())
        check("the appended capture carries the queue tool's stamp",
              "Rationale for eta.\nFiled " in after and
              "stamped by the queue tool." in after, after[-300:])


def test_append_leaves_a_stamped_capture_alone():
    """A body already carrying the capture tool's stamp is unchanged."""
    mod = _load_mover()
    body = ["#### A capture [zeta]\n", "Its rationale.\n",
            "Filed 2026-09-02 14:35, stamped by the capture tool.\n",
            "Cycle: [weekly-release]\n"]
    out = mod.stamp_filed_at(list(body))
    check("a body with the capture tool's stamp is returned as it is",
          out == body, repr(out))


def main():
    print("reorder_queue.py regression tests")
    for fn in (
        test_side_of_marker_report,
        test_report_agrees_with_file,
        test_move_section_marker_after_the_moved_item_is_refused,
        test_move_section_applies_marker_after,
        test_move_section_marker_failure_writes_nothing,
        test_delete_reports_only_what_landed,
        test_retitle_changes_the_heading_and_nothing_else,
        test_retitle_refuses_a_bracketed_heading,
        test_write_verified_refuses_a_write_that_did_not_land,
        test_move_section_refuses_an_unnamed_sweep,
        test_named_move_across_the_line_still_reports_and_succeeds,
        test_append_stamps_an_unstamped_capture,
        test_append_leaves_a_stamped_capture_alone,
        test_write_retries_once_on_a_refused_handle,
        test_write_names_what_to_check_on_a_second_refusal,
        test_write_through_temp_path_is_byte_identical_over_non_ascii,
        test_marker_above_all_items,
        test_marker_above_all_explicit_placement,
        test_marker_above_all_move_mode,
        test_marker_between_items,
        test_marker_below_all_items,
        test_section_with_no_marker,
        test_no_marker_with_marker_after_warns,
        test_slug_set_mismatch_refuses,
        test_delete_clean,
        test_delete_unknown_slug_refuses,
        test_delete_last_item_in_section,
        test_delete_marker_anchor_reanchors,
        test_move_marker_anchor_does_not_drag_the_marker,
        test_move_non_anchor_leaves_marker_alone,
        test_move_explicit_marker_after_still_wins,
        test_unnamed_crossing_refusal_names_one_move_per_item,
        test_unnamed_downward_sweep_refuses,
        test_delete_first_item_when_marker_anchored_to_it,
        test_delete_block_containing_heading_like_lines,
        test_delete_from_unprocessed,
        test_move_section_after_last_cleared_reports_below,
        test_move_section_top_reports_above,
        test_delete_reports_inbound_citations,
        test_delete_skips_cycle_lines_in_the_citation_note,
        test_delete_reports_nothing_when_uncited,
        test_replace_in_fires,
        test_replace_in_refuses_non_unique,
        test_replace_in_refuses_absent_match,
        test_replace_in_refuses_unknown_slug,
        test_replace_in_reaches_unprocessed,
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
