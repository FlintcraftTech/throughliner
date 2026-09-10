#!/usr/bin/env python3
"""Fixture suite for the queue lint's never-fired flags.

Run: py resources/testing/test_queue_lint_flags.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

Why a fixture rather than an observation. Only the blocked-by flag has ever
fired in practice, because the real queue has never contained the other faults:
a work-item heading with no slug, a missing section heading, a red-flag state
that is neither cleared nor uncleared, and prose sitting under no work item.
Exercising those means writing bad queue lines on purpose. An unexercised check
is not a passing check — it is a check nobody has ever seen work.

One correction to the item that asked for this. It listed "missing provenance"
as a fourth lint flag. There is no such check and there should not be:
provenance is a prose convention, and the rules state explicitly that it is not
a lint-checked field. Orphaned prose is the fourth check that had never fired,
so it is what this suite covers in its place.
"""

import importlib.util
import os
import sys

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

HOOK = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))),
    "plugin", "throughliner", "hooks", "post_tool_use.py",
)

failures = []


def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


def load_lint():
    spec = importlib.util.spec_from_file_location("post_tool_use", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.lint


CLEAN = """# QUEUE

## Processed

#### Perfectly ordinary work item [alpha]
Filed by Claude. Rationale for alpha.

--- Build block ---
Changes: `somefile.md` — the thing the item describes.
Acceptance: the suite passes.
--- End build block ---

--- Cleared to run above this line ---

## Unprocessed

#### Another ordinary work item [beta]
Filed by Claude. Rationale for beta.
"""


def test_clean_queue_is_silent():
    """The control. A suite that fires on correct input proves nothing."""
    lint = load_lint()
    warnings = lint(CLEAN)
    check("a well-formed queue produces no warnings", not warnings,
          f"got: {warnings}")


def test_slugless_heading_is_flagged():
    lint = load_lint()
    bad = CLEAN.replace("#### Perfectly ordinary work item [alpha]",
                        "#### Work item nobody gave a slug")
    warnings = lint(bad)
    hit = any("no [slug]" in w for w in warnings)
    check("a heading with no slug is flagged", hit, f"got: {warnings}")


def test_missing_section_heading_is_flagged():
    lint = load_lint()
    bad = CLEAN.replace("## Unprocessed\n", "")
    warnings = lint(bad)
    hit = any("Unprocessed' section heading is missing" in w for w in warnings)
    check("a missing section heading is flagged", hit, f"got: {warnings}")


def test_invalid_red_flag_state_is_flagged():
    lint = load_lint()
    bad = CLEAN.replace("Rationale for beta.",
                        "Rationale for beta.\nRed flag · State: probably fine")
    warnings = lint(bad)
    hit = any("cleared / uncleared" in w for w in warnings)
    check("a red-flag state outside cleared/uncleared is flagged", hit,
          f"got: {warnings}")


def test_valid_red_flag_states_are_not_flagged():
    """The other half of the same check — it must not fire on correct markers."""
    lint = load_lint()
    for state in ("cleared", "uncleared"):
        ok = CLEAN.replace("Rationale for beta.",
                           f"Rationale for beta.\nRed flag · State: {state}")
        warnings = [w for w in lint(ok) if "cleared / uncleared" in w]
        check(f"'{state}' is accepted as a red-flag state", not warnings,
              f"got: {warnings}")


def test_mid_line_marker_is_flagged():
    """The live instance: a marker at the end of a prose sentence.

    Every reader of these three fields anchors to the start of a line, so a
    mid-line marker is invisible to all of them and nothing errors.
    """
    lint = load_lint()
    for marker in ("Red flag · State: uncleared", "Blocked by: [alpha]",
                   "Not before: 2026-09-01", "Cycle: [tips-posting]"):
        bad = CLEAN.replace(
            "Rationale for beta.",
            f"Rationale for beta, and it records public claims. {marker}")
        warnings = [w for w in lint(bad) if "mid-line" in w]
        check(f"a mid-line '{marker.split(':')[0]}:' is flagged", warnings,
              f"got: {lint(bad)}")
        # The advice is followable at every site the check fires on: a field
        # goes on its own line, and prose discussing the field goes in
        # backticks ([lint-mid-line-flag-names-backtick-remedy]).
        check(f"the '{marker.split(':')[0]}:' flag names the backtick remedy",
              warnings and "in backticks where the words are prose" in warnings[0],
              f"got: {warnings}")


def test_marker_on_its_own_line_is_not_flagged():
    """The other half — the canonical shape, and the tolerated emphasis."""
    lint = load_lint()
    for written in ("Red flag · State: uncleared", "**Blocked by:** [alpha]",
                    "Not before: 2026-09-01", "Cycle: [tips-posting]"):
        ok = CLEAN.replace("Rationale for beta.",
                           f"Rationale for beta.\n{written}")
        warnings = [w for w in lint(ok) if "mid-line" in w]
        check(f"'{written}' on its own line is not flagged", not warnings,
              f"got: {warnings}")


def test_marker_in_backticks_mid_line_is_not_flagged():
    """Prose discussing a field writes its name in backticks mid-sentence.

    Nine such mentions fired the warning on every tool call of a hundred-call
    session — every one a false positive, every real field written bare at
    line start. A backticked name is discussion; no reader parses it.
    """
    lint = load_lint()
    for prose in (
        "carried in prose rather than by a `Blocked by:` line.",
        "what `Not before:` means on a capture is different.",
        "the `Cycle:` field marks a cycle's standing material.",
    ):
        ok = CLEAN.replace("Rationale for beta.",
                           f"Rationale for beta, {prose}")
        warnings = [w for w in lint(ok) if "mid-line" in w]
        check(f"a backticked mid-line mention ({prose[:26]}…) is not flagged",
              not warnings, f"got: {warnings}")


def test_marker_quoted_in_a_fence_is_not_flagged():
    """A fenced block legitimately SHOWS the shape; quoting is not writing."""
    lint = load_lint()
    ok = CLEAN.replace(
        "Rationale for beta.",
        "Rationale for beta.\n\n```\nBlocked by: [slug]   # the line format\n```")
    warnings = [w for w in lint(ok) if "mid-line" in w]
    check("a marker quoted inside a fence is not flagged", not warnings,
          f"got: {warnings}")


def test_orphaned_prose_is_flagged():
    lint = load_lint()
    bad = CLEAN.replace("## Processed\n",
                        "## Processed\n\nProse belonging to no work item.\n")
    warnings = lint(bad)
    hit = any("no #### heading" in w or "belongs to no entry" in w
              for w in warnings)
    check("prose under no work item is flagged", hit, f"got: {warnings}")


HELD = CLEAN.replace(
    "## Unprocessed",
    "#### Held item [gamma]\nRationale for gamma.\n{hold}\n\n## Unprocessed",
)


def test_date_held_item_needs_no_blocker():
    """A `Not before:` date holds an item on its own.

    It is the one holding fact that resolves itself — no session and no user
    confirms that a day has passed — so it needs no blocker item standing in
    for it.
    """
    lint = load_lint()
    warnings = lint(HELD.format(hold="Not before: 2099-01-01"))
    hit = [w for w in warnings if "gamma" in w or "Not before" in w]
    check("a date-held item is not flagged for missing a blocker", not hit,
          f"got: {warnings}")


def test_held_item_with_neither_is_flagged():
    lint = load_lint()
    warnings = lint(HELD.format(hold="Waiting for a bit."))
    hit = any("Not before" in w and "Blocked by" in w for w in warnings)
    check("a held item with no blocker and no date is flagged", hit,
          f"got: {warnings}")


def test_malformed_date_is_flagged():
    lint = load_lint()
    warnings = lint(HELD.format(hold="Not before: next Tuesday"))
    hit = any("not a date in YYYY-MM-DD form" in w for w in warnings)
    check("a date nobody can read is flagged", hit, f"got: {warnings}")


def test_date_above_the_line_is_flagged():
    """Cleared work has nothing holding it, a date included."""
    lint = load_lint()
    bad = CLEAN.replace("Filed by Claude. Rationale for alpha.",
                        "Filed by Claude. Rationale for alpha.\n"
                        "Not before: 2099-01-01")
    warnings = lint(bad)
    hit = any("sits ABOVE" in w and "Not before" in w for w in warnings)
    check("a date on a cleared item is flagged", hit, f"got: {warnings}")


def test_build_block_delimiters_are_no_longer_asked_for_or_flagged():
    """The build-block check is retired ([builds-read-the-queue-again]).

    A run reads each item whole from the queue now, so there is no block that
    can be missing, half-written, or demanded of held work. What replaces it is
    judgment at the decision step, not another check.

    This asserts the SILENCE, which is the part that could regress: a leftover
    check would fire on every item in every real queue, since none of them will
    carry the delimiters any more.
    """
    lint = load_lint()
    for label, text in [
        ("an item with no delimiters at all", CLEAN.replace(
            "--- Build block ---\n"
            "Changes: `somefile.md` — the thing the item describes.\n"
            "Acceptance: the suite passes.\n"
            "--- End build block ---\n", "")),
        ("an item with half a leftover block", CLEAN.replace(
            "--- End build block ---\n", "")),
        ("an item with a whole leftover block", CLEAN),
    ]:
        warnings = lint(text)
        check(f"{label} draws no build-block warning",
              not any("build block" in w for w in warnings),
              f"got: {warnings}")


def test_malformed_date_on_a_capture_is_flagged():
    """`Not before:` reaches Unprocessed, so its date check must too.

    On a capture the field means "do not offer this again before this date", so
    a date nothing can parse holds the entry out of view forever — and nothing
    else in this check looks at Unprocessed at all.
    """
    lint = load_lint()
    bad = CLEAN.replace("Filed by Claude. Rationale for beta.",
                        "Filed by Claude. Rationale for beta.\n"
                        "Not before: sometime next spring")
    warnings = lint(bad)
    hit = any("not a date in YYYY-MM-DD form" in w for w in warnings)
    check("an unreadable date on a capture is flagged", hit, f"got: {warnings}")


def test_good_date_on_a_capture_is_silent():
    """A capture may carry a date, so a well-formed one draws no warning.

    This is the half that would break if the above/below warnings had been
    widened along with the date check: an Unprocessed entry sits below the
    marker in file order, so a position check applied there would fire on
    every dated capture.
    """
    lint = load_lint()
    ok = CLEAN.replace("Filed by Claude. Rationale for beta.",
                       "Filed by Claude. Rationale for beta.\n"
                       "Not before: 2099-01-01")
    warnings = lint(ok)
    check("a well-formed date on a capture is silent", not warnings,
          f"got: {warnings}")


def test_credit_without_a_quote_is_flagged():
    """A credit to the user rests on words they actually said.

    The check cannot tell invented reasoning from real reasoning and is not
    described as if it could. What it does is make an unsupported credit
    visible, raising its cost from nothing to fabricating a quotation.
    """
    lint = load_lint()
    bad = CLEAN.replace("Filed by Claude. Rationale for alpha.",
                        "Captured by you 2026-08-15, in your own words: you "
                        "wanted this done differently.")
    warnings = lint(bad)
    hit = any("quotes nothing" in w for w in warnings)
    check("a user credit with no quotation is flagged", hit, f"got: {warnings}")


def test_credit_with_a_quote_is_not_flagged():
    lint = load_lint()
    for quoted in ('"do it the other way"', '“do it the other way”'):
        ok = CLEAN.replace(
            "Filed by Claude. Rationale for alpha.",
            f"Captured by you 2026-08-15, in your own words: {quoted}.")
        warnings = [w for w in lint(ok) if "quotes nothing" in w]
        check(f"a credit quoting {quoted[:1]}…{quoted[-1:]} is accepted",
              not warnings, f"got: {warnings}")


def test_blockquote_counts_as_showing_the_words():
    lint = load_lint()
    ok = CLEAN.replace(
        "Filed by Claude. Rationale for alpha.",
        "Captured by you, in your own words:\n> do it the other way")
    warnings = [w for w in lint(ok) if "quotes nothing" in w]
    check("a blockquote counts as quoting them", not warnings,
          f"got: {warnings}")


def test_bare_origin_claim_is_not_flagged():
    """The whole of the provenance split, and nothing asserted it until now.

    "Captured by you", with nothing quoted anywhere, is an ORIGIN claim: it says
    where the item came from, and a paraphrase is the normal way to state it.
    Everything in these documents is written by Claude, so a rule demanding a
    quotation for an origin claim would move every un-transcribed idea of the
    user's into Claude's column — and the cheapest way to satisfy such a rule is
    to ask the user to prove their own work is theirs.

    Reverting the split — folding the origin phrases back into
    QUOTE_CLAIM_PHRASES — makes this case fail, which is what makes it a test of
    the split rather than of the lint in general.
    """
    lint = load_lint()
    for claim in ("Captured by you 2026-08-15.",
                  "You raised this, and the reasoning is yours.",
                  "Filed on your instruction."):
        item = CLEAN.replace("Filed by Claude. Rationale for alpha.",
                             claim + " Rationale for alpha.")
        warnings = [w for w in lint(item) if "quotes nothing" in w]
        check(f"a bare origin claim ({claim.split(',')[0][:24]}…) is accepted",
              not warnings, f"got: {warnings}")


def test_quote_claim_without_verbatim_text_is_still_flagged():
    """The other side of the same split, pinned alongside it.

    Narrowing the phrase list must not narrow it to nothing: a claim about how
    something was PHRASED, with no phrasing shown, is exactly what the check
    exists for.

    The cases are the two introducer shapes the check now fires on. "Her
    words:" over a paraphrase is this project's own recorded failure and is
    pinned here so a later narrowing cannot drop third-person phrases from the
    list.
    """
    lint = load_lint()
    for claim in ("In your own words, this should be done differently.",
                  "Her words: the ordering was wrong."):
        item = CLEAN.replace("Filed by Claude. Rationale for alpha.", claim)
        warnings = [w for w in lint(item) if "quotes nothing" in w]
        check(f"a quote claim with nothing quoted ({claim[:18]}…) is flagged",
              bool(warnings), f"got: {warnings}")


def test_possessive_words_in_ordinary_prose_is_not_flagged():
    """A possessive plus "words" is not by itself a claim about wording.

    The consumer's sentence that exposed this: a paraphrase explicitly
    disclaiming verbatimness was read as claiming it. Only an introducer — the
    phrase followed by a colon, or "in <possessive> own words" — fires now, and
    this case is what stops the bare-phrase match coming back.
    """
    lint = load_lint()
    for claim in ("Recorded as her words as closely as he can recall them.",
                  "The item keeps their words out of the operative rule."):
        item = CLEAN.replace("Filed by Claude. Rationale for alpha.", claim)
        warnings = [w for w in lint(item) if "quotes nothing" in w]
        check(f"ordinary prose ({claim[:22]}…) is not flagged",
              not warnings, f"got: {warnings}")


def test_uncredited_item_is_not_asked_for_a_quote():
    """The other half — an unmarked item reads as Claude's and owes nothing."""
    lint = load_lint()
    warnings = [w for w in lint(CLEAN) if "quotes nothing" in w]
    check("an unmarked item is never asked to quote anyone", not warnings,
          f"got: {warnings}")


def test_growth_reports_a_delta_per_edited_item():
    """Word growth is a bare fact per item, with no threshold anywhere.

    Driven through the module's own counter rather than a git repository, so
    the case pins the arithmetic and the shape. The git baseline degrades to
    nothing when there is no repository, which is why the report can be absent
    without being wrong.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location("post_tool_use", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    before = mod._item_word_counts(CLEAN)
    grown = CLEAN.replace("Rationale for alpha.",
                          "Rationale for alpha, now with five extra words.")
    after = mod._item_word_counts(grown)
    check("an edited item's word count rises", after["alpha"] > before["alpha"],
          f"{before.get('alpha')} -> {after.get('alpha')}")
    check("an untouched item's count is unchanged",
          after["beta"] == before["beta"],
          f"{before.get('beta')} -> {after.get('beta')}")


def test_duplicate_gate_lines_are_flagged():
    """Two `Rule gate:` lines on one item make its disposition ambiguous."""
    lint = load_lint()
    bad = CLEAN.replace("Filed by Claude. Rationale for alpha.",
                        "Filed by Claude. Rationale for alpha.\n"
                        "Rule gate: run — the full disposition.\n"
                        "Rule gate: run — the full")
    warnings = lint(bad)
    hit = any("duplicate Rule gate" in w for w in warnings)
    check("two Rule gate: lines on one item are flagged", hit, f"got: {warnings}")


def test_single_or_absent_gate_line_is_not_flagged():
    lint = load_lint()
    one = CLEAN.replace("Filed by Claude. Rationale for alpha.",
                        "Filed by Claude. Rationale for alpha.\n"
                        "Rule gate: run — the disposition.")
    for label, content in (("one gate line", one), ("no gate line", CLEAN)):
        warnings = [w for w in lint(content) if "duplicate Rule gate" in w]
        check(f"{label} is not flagged as duplicate", not warnings,
              f"got: {warnings}")


GATED = CLEAN.replace(
    "Changes: `somefile.md` — the thing the item describes.",
    "Changes: `plugin/throughliner/docs/plan.md` — reword a rule.")


def test_cleared_rule_path_item_without_gate_line_is_flagged():
    lint = load_lint()
    warnings = lint(GATED)
    hit = any("no gate disposition" in w for w in warnings)
    check("a cleared rule-path item with no gate line is flagged", hit,
          f"got: {warnings}")


def test_cleared_rule_path_item_with_gate_line_is_not_flagged():
    lint = load_lint()
    ok = GATED.replace("Filed by Claude. Rationale for alpha.",
                       "Filed by Claude. Rationale for alpha.\n"
                       "Rule gate: run — eviction named.")
    warnings = [w for w in lint(ok) if "no gate disposition" in w]
    check("a cleared rule-path item with a gate line is not flagged",
          not warnings, f"got: {warnings}")


def test_held_rule_path_item_is_not_asked_for_a_gate_line():
    """Held work is not yet through the keep-step, so it owes nothing."""
    lint = load_lint()
    held = CLEAN.replace(
        "## Unprocessed",
        "#### Held rule item [gdelta]\nRationale.\n"
        "Changes: `plugin/throughliner/docs/plan.md` — reword.\n"
        "Blocked by: [alpha]\n\n## Unprocessed")
    warnings = [w for w in lint(held) if "no gate disposition" in w]
    check("a rule-path item below the line is not flagged", not warnings,
          f"got: {warnings}")


def test_non_rule_path_item_without_gate_line_is_not_flagged():
    lint = load_lint()
    warnings = [w for w in lint(CLEAN) if "no gate disposition" in w]
    check("a non-rule-path item without a gate line is not flagged",
          not warnings, f"got: {warnings}")


def test_cleared_item_naming_queue_is_flagged():
    lint = load_lint()
    bad = CLEAN.replace(
        "Changes: `somefile.md` — the thing the item describes.",
        "Changes: `QUEUE.md` — reword three item headings.")
    warnings = lint(bad)
    hit = any("names QUEUE.md" in w for w in warnings)
    check("a cleared item naming QUEUE.md is flagged", hit, f"got: {warnings}")


def test_cleared_audit_item_naming_queue_is_flagged():
    lint = load_lint()
    bad = CLEAN.replace(
        "#### Perfectly ordinary work item [alpha]",
        "#### [audit] Perfectly ordinary work item [alpha]").replace(
        "Changes: `somefile.md` — the thing the item describes.",
        "Changes: `QUEUE.md` — read and report on item wording.")
    warnings = lint(bad)
    hit = any("names QUEUE.md" in w for w in warnings)
    check("a cleared [audit] item naming QUEUE.md is flagged", hit,
          f"got: {warnings}")


def test_held_item_naming_queue_is_not_flagged():
    lint = load_lint()
    held = CLEAN.replace(
        "## Unprocessed",
        "#### Held queue item [qheld]\nRationale.\n"
        "Changes: `QUEUE.md` — reword headings.\n"
        "Blocked by: [alpha]\n\n## Unprocessed")
    warnings = [w for w in lint(held) if "names QUEUE.md" in w]
    check("the same item below the line is not flagged", not warnings,
          f"got: {warnings}")


def test_cleared_item_naming_other_files_is_not_flagged():
    lint = load_lint()
    warnings = [w for w in lint(CLEAN) if "names QUEUE.md" in w]
    check("a cleared item naming other files is not flagged", not warnings,
          f"got: {warnings}")


def _load_module():
    spec = importlib.util.spec_from_file_location("post_tool_use", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_untracked_baseline_is_the_newest_snapshot():
    """With no committed copy, the baseline is the newest pre-change snapshot.

    The untracked configuration is what setup proposes, so this is the default
    consumer's path — and before this existed, a missing committed copy made
    every standing flag print as new after every tool call, permanently.
    """
    import tempfile

    mod = _load_module()
    with tempfile.TemporaryDirectory() as td:
        snap = os.path.join(td, ".throughliner", "snapshots")
        os.makedirs(snap)
        for stamp, text in (("20260901T010000000000", "older version"),
                            ("20260901T020000000000", "newer version")):
            with open(os.path.join(snap, f"QUEUE.md@{stamp}"), "w",
                      encoding="utf-8") as f:
                f.write(text)
        content, kind = mod._baseline_queue(td)
        check("the untracked baseline is the newest snapshot",
              (content, kind) == ("newer version", "snapshot"),
              f"got kind={kind!r}, content={content!r}")


def test_untracked_standing_flag_reads_as_pre_existing():
    """A flag present in the snapshot is standing, not new — both directions
    read the same baseline, so an untouched queue lints silent."""
    mod = _load_module()
    bad = CLEAN.replace("#### Perfectly ordinary work item [alpha]",
                        "#### Work item nobody gave a slug")
    warnings = mod.lint(bad)
    new, pre = mod._split_warnings(warnings, bad)
    check("a flag also in the snapshot baseline is pre-existing",
          not new and len(pre) == len(warnings),
          f"new={new}, pre={pre}")
    check("the same baseline clears nothing when the flag still stands",
          mod._cleared_warnings(warnings, bad) == [],
          f"got: {mod._cleared_warnings(warnings, bad)}")


def test_untracked_no_snapshot_yields_no_baseline():
    """No committed copy and no snapshot: kind is None, and the caller emits
    one plain no-baseline line — never the whole set as new."""
    import tempfile

    mod = _load_module()
    with tempfile.TemporaryDirectory() as td:
        content, kind = mod._baseline_queue(td)
        check("no snapshot and no commit means no baseline",
              (content, kind) == ("", None),
              f"got kind={kind!r}, content={content!r}")


if __name__ == "__main__":
    print("test_queue_lint_flags")
    test_clean_queue_is_silent()
    test_slugless_heading_is_flagged()
    test_missing_section_heading_is_flagged()
    test_invalid_red_flag_state_is_flagged()
    test_valid_red_flag_states_are_not_flagged()
    test_mid_line_marker_is_flagged()
    test_marker_on_its_own_line_is_not_flagged()
    test_marker_in_backticks_mid_line_is_not_flagged()
    test_marker_quoted_in_a_fence_is_not_flagged()
    test_orphaned_prose_is_flagged()
    test_date_held_item_needs_no_blocker()
    test_held_item_with_neither_is_flagged()
    test_malformed_date_is_flagged()
    test_date_above_the_line_is_flagged()
    test_build_block_delimiters_are_no_longer_asked_for_or_flagged()
    test_malformed_date_on_a_capture_is_flagged()
    test_good_date_on_a_capture_is_silent()
    test_credit_without_a_quote_is_flagged()
    test_credit_with_a_quote_is_not_flagged()
    test_blockquote_counts_as_showing_the_words()
    test_bare_origin_claim_is_not_flagged()
    test_quote_claim_without_verbatim_text_is_still_flagged()
    test_possessive_words_in_ordinary_prose_is_not_flagged()
    test_uncredited_item_is_not_asked_for_a_quote()
    test_growth_reports_a_delta_per_edited_item()
    test_duplicate_gate_lines_are_flagged()
    test_single_or_absent_gate_line_is_not_flagged()
    test_cleared_rule_path_item_without_gate_line_is_flagged()
    test_cleared_rule_path_item_with_gate_line_is_not_flagged()
    test_held_rule_path_item_is_not_asked_for_a_gate_line()
    test_non_rule_path_item_without_gate_line_is_not_flagged()
    test_cleared_item_naming_queue_is_flagged()
    test_cleared_audit_item_naming_queue_is_flagged()
    test_held_item_naming_queue_is_not_flagged()
    test_cleared_item_naming_other_files_is_not_flagged()
    test_untracked_baseline_is_the_newest_snapshot()
    test_untracked_standing_flag_reads_as_pre_existing()
    test_untracked_no_snapshot_yields_no_baseline()
    print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
    sys.exit(1 if failures else 0)
