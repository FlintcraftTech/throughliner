#!/usr/bin/env python3
"""Regression tests for stop.py's filing-claim check.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_stop_hook.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

The hook is driven as a subprocess, because what needs pinning is whether it
blocks — which is its exit code and its emitted reason, not an internal call.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "stop.py")

failures = []


def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


QUEUE = """# QUEUE

## Processed

#### An item that is still queued [still-queued]
Prose.

--- Cleared to run above this line ---

## Unprocessed
"""


def project(log_files=()):
    d = tempfile.mkdtemp(prefix="stop-hook-test-")
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8") as f:
        f.write(QUEUE)
    log = os.path.join(d, "LOG")
    os.makedirs(log)
    for name in log_files:
        with open(os.path.join(log, name), "w", encoding="utf-8") as f:
            f.write("A session record.\n")
    return d


def run(root, message, session_id="s1"):
    payload = {
        "last_assistant_message": message,
        "cwd": root,
        "session_id": session_id,
    }
    r = subprocess.run(
        [sys.executable, HOOK],
        input=json.dumps(payload),
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def blocked(out, code):
    """The hook blocks by emitting its reason; a clean pass emits nothing."""
    return "not in QUEUE.md" in out or code != 0


def test_cited_shipped_slug_does_not_block():
    """The recorded defect: five instances, every one a correct citation.

    A built item leaves QUEUE.md, so from the queue alone a citation of finished
    work is indistinguishable from a report of a write that never happened.
    """
    root = project(log_files=["2026-08-21-already-shipped.md"])
    code, out = run(root, "I've filed [already-shipped] as agreed.")
    check("a slug with a LOG entry does not block", not blocked(out, code), out)
    shutil.rmtree(root, ignore_errors=True)


def test_filing_claim_with_no_heading_and_no_log_entry_still_blocks():
    """The hook's real catch has to survive the fix."""
    root = project()
    code, out = run(root, "I've filed [never-written] to Unprocessed.")
    check("a claim with no heading and no record still blocks",
          blocked(out, code), out)
    check("the block asks for a correction saying the earlier report was wrong",
          "earlier report was wrong" in out, out)
    check("the block asks for the correction alone, nothing repeated",
          "nothing" in out and "repeated" in out and "re-send" not in out, out)
    shutil.rmtree(root, ignore_errors=True)


def test_placeholder_slugs_from_a_specimen_do_not_block():
    """[stop-hook-placeholder-slugs]: discussing a specimen is ordinary work.

    The live instance: a reorder specimen carrying [slug-a] and [beta-slug] was
    read as two claims of filed captures, and the turn was blocked. Correct by
    the hook's own rules, and wrong for the session.
    """
    root = project()
    code, out = run(root, "The specimen should read: moved [slug-a] above "
                          "[some-slug] so it builds first.")
    check("placeholder slugs in a specimen do not block",
          not blocked(out, code), out)
    shutil.rmtree(root, ignore_errors=True)


def test_a_genuinely_absent_slug_still_blocks_alongside_placeholders():
    """The suppression must be the specimen vocabulary and nothing wider."""
    root = project()
    code, out = run(root, "I've filed [genuinely-absent] to Unprocessed.")
    check("a real absent slug still blocks after the placeholder carve-out",
          blocked(out, code), out)
    shutil.rmtree(root, ignore_errors=True)


def test_a_queued_slug_does_not_block():
    root = project()
    code, out = run(root, "I've filed [still-queued] to the queue.")
    check("a slug present as a heading does not block",
          not blocked(out, code), out)
    shutil.rmtree(root, ignore_errors=True)


def test_block_still_downgrades_after_one_fire():
    """Block-once-per-claim is untouched, so a mismatch can't trap the chat."""
    root = project()
    first = run(root, "I've filed [never-written] to Unprocessed.")
    second = run(root, "I've filed [never-written] to Unprocessed.")
    check("the first claim blocks", blocked(first[1], first[0]), first[1])
    check("the same claim does not block twice",
          not blocked(second[1], second[0]) or "not in QUEUE.md" not in second[1]
          or second[0] == 0,
          second[1])
    shutil.rmtree(root, ignore_errors=True)


def test_ticked_slug_in_working_file_does_not_block():
    """[stop-hook-blind-between-tick-and-close]: a slug built earlier in the
    same run is in neither the queue nor LOG/ until the close — its tick in
    this session's working file is what says it's finished work being cited.
    """
    root = project()
    with open(os.path.join(root, "_build-s1.md"), "w", encoding="utf-8") as f:
        f.write("# Active Build\n\nProgress:\n- [x] built earlier "
                "[built-this-run] — done, confirmed\n")
    code, out = run(root, "I've filed [built-this-run] earlier this run.")
    check("a slug ticked in this run's working file does not block",
          not blocked(out, code), out)
    shutil.rmtree(root, ignore_errors=True)


def test_unticked_absent_slug_still_blocks_with_working_file():
    """The working-file suppression must not quiet the guard generally."""
    root = project()
    with open(os.path.join(root, "_build-s1.md"), "w", encoding="utf-8") as f:
        f.write("# Active Build\n\nProgress:\n- [x] built earlier "
                "[built-this-run] — done\n")
    code, out = run(root, "I've filed [never-written] to Unprocessed.")
    check("an absent slug not in the working file still blocks",
          blocked(out, code), out)
    shutil.rmtree(root, ignore_errors=True)


def test_no_working_file_behaves_as_before():
    root = project()
    code, out = run(root, "I've filed [never-written] to Unprocessed.")
    check("no working file leaves the check exactly as it was",
          blocked(out, code), out)
    shutil.rmtree(root, ignore_errors=True)


def test_missing_log_directory_behaves_as_before():
    """A project with no LOG/ must not start passing everything."""
    d = tempfile.mkdtemp(prefix="stop-hook-test-")
    with open(os.path.join(d, "QUEUE.md"), "w", encoding="utf-8") as f:
        f.write(QUEUE)
    code, out = run(d, "I've filed [never-written] to Unprocessed.")
    check("no LOG/ folder leaves the check exactly as it was",
          blocked(out, code), out)
    shutil.rmtree(d, ignore_errors=True)


# --------------------------------------------------------------------------
# Hedge-suppression fixtures, widened to full-paragraph reports.
#
# [stop-hook-negation-window-eats-real-claims]: every fixture above is a bare
# sentence, so the hedging suppressor can never fire in one — the suite passed,
# correctly, while the guard was defeated live. The general lesson, which
# belongs to the record rather than to this file: a fixture that isolates the
# unit can isolate away the interaction that breaks it.
#
# The three CATCH cases are the three replies driven through the live hook on
# 2026-08-31 that went undetected. Each carries its hedge in the sentence
# BEFORE the claim, which is the shape next-build.md's capture-report rule
# actually mandates.
# --------------------------------------------------------------------------

RECORDED_MISSES = [
    ("hedge in the previous sentence — 'rather than'",
     "I captured this **rather than** folding it in. Filed as "
     "[never-written]."),
    ("hedge in the previous sentence — 'instead of'",
     "This needed a decision instead of a build, so it goes to planning. "
     "I've filed [never-written] to Unprocessed."),
    ("hedge in the previous sentence — 'not'",
     "That is not part of the described work, so it is not being folded in "
     "here.\nFiled [never-written] as a capture."),
]

SAME_SENTENCE_HEDGES = [
    ("same-sentence hedge — 'would'",
     "I would file [never-written] if you want it tracked."),
    ("same-sentence hedge — 'once'",
     "I'll file [never-written] once the build lands."),
]


def test_recorded_misses_are_now_caught():
    """The three live misses: a real claim whose hedge sits one sentence back."""
    for label, message in RECORDED_MISSES:
        root = project()
        code, out = run(root, message)
        check(label + " now blocks", blocked(out, code), out)
        shutil.rmtree(root, ignore_errors=True)


def test_same_sentence_hedges_are_still_suppressed():
    """The suppressor's real job survives: it was added for exactly this."""
    for label, message in SAME_SENTENCE_HEDGES:
        root = project()
        code, out = run(root, message)
        check(label + " stays suppressed", not blocked(out, code), out)
        shutil.rmtree(root, ignore_errors=True)


def test_hedge_paragraph_around_a_shipped_citation_still_passes():
    """A paragraph-length citation of finished work must not start blocking."""
    root = project(log_files=["2026-08-21-already-shipped.md"])
    code, out = run(
        root,
        "I looked at whether this belonged in the run rather than in the "
        "queue. It was already built, so nothing was written this time. "
        "I've filed [already-shipped] as agreed, back when it was raised.")
    check("a paragraph citing shipped work does not block",
          not blocked(out, code), out)
    shutil.rmtree(root, ignore_errors=True)


def test_claim_inside_a_blockquote_does_not_block():
    """A quoted draft showing what Claude says mid-run is not a filing report.

    The instance: a tips draft quoted "moved [login-form] below the cleared
    line" in a blockquote, and the check blocked the turn for an item that
    does not exist. The same sentence as plain prose must still fire.
    """
    root = project()
    code, out = run(root, "Here is the draft:\n\n> I moved [login-form] below "
                          "the cleared line.\n\nSay yes to post it.")
    check("a claim inside a blockquote does not block",
          not blocked(out, code), out)
    code, out = run(root, "I moved [login-form] below the cleared line.")
    check("the same claim as plain prose still blocks", blocked(out, code), out)
    shutil.rmtree(root, ignore_errors=True)


def test_claim_inside_a_fence_does_not_block():
    """A specimen inside a code fence is not a filing report either."""
    root = project()
    code, out = run(root, "The specimen reads:\n\n```\nI filed [login-form] "
                          "to Unprocessed.\n```\n\nNothing was written.")
    check("a claim inside a code fence does not block",
          not blocked(out, code), out)
    shutil.rmtree(root, ignore_errors=True)


# --------------------------------------------------------------------------
# Relative time words with no source ([unfounded-time-words-stopped-once]).
# --------------------------------------------------------------------------

def time_blocked(out):
    return "with no source" in out


def test_bare_time_word_blocks_once_with_the_phrase_named():
    root = project()
    code, out = run(root, "That is what we settled an hour ago.")
    check("a bare 'an hour ago' blocks", time_blocked(out), out)
    check("the reason names the phrase", "an hour ago" in out, out)
    code, out = run(root, "Still what we settled an hour ago.")
    check("the same phrase does not block a second time",
          not time_blocked(out), out)
    shutil.rmtree(root, ignore_errors=True)


def test_time_word_inside_a_quotation_passes():
    root = project()
    code, out = run(root, "Your words were \"do it like an hour ago\" and I "
                          "have read them back.")
    check("a phrase inside quotation marks passes", not time_blocked(out), out)
    code, out = run(root, "> we settled this yesterday\n\nThat is the quote.")
    check("a phrase inside a blockquote passes", not time_blocked(out), out)
    code, out = run(root, "The rule names `this morning` as a specimen.")
    check("a phrase inside inline code passes", not time_blocked(out), out)
    shutil.rmtree(root, ignore_errors=True)


def test_day_words_and_elapsed_forms_block():
    root = project()
    for phrase in ("yesterday", "tomorrow", "last week", "3 minutes ago",
                   "just now", "tonight"):
        code, out = run(root, f"I did that {phrase}.")
        check(f"'{phrase}' blocks", time_blocked(out), out)
    shutil.rmtree(root, ignore_errors=True)


def test_sourced_sentence_passes_and_bare_word_still_blocks():
    root = project()
    code, out = run(root, "The sweep ran on 2026-09-14, per its record, so "
                          "today's opening files nothing.")
    check("a time word in a sentence carrying a date passes",
          not time_blocked(out), out)
    code, out = run(root, "It is 14:30 today, read from the clock.")
    check("a time word beside 'read from the clock' passes",
          not time_blocked(out), out)
    code, out = run(root, "The sweep ran on 2026-09-14. Nothing is due today.")
    check("a source in a DIFFERENT sentence does not cover the word",
          time_blocked(out), out)
    check("the block asks for a correction line",
          "correction" in out, out)
    check("the block asks for the correction alone, nothing repeated",
          "nothing" in out and "repeated" in out and "re-send" not in out, out)
    shutil.rmtree(root, ignore_errors=True)


def test_capitalised_name_mid_sentence_passes():
    """[time-word-check-hits-product-nouns]: a capital mid-sentence is a
    product's own page or feature; a capital opening the sentence is not."""
    root = project()
    code, out = run(root, "The test task added from Tomorrow appeared on Today "
                          "straight away.")
    check("capitalised page names mid-sentence pass", not time_blocked(out), out)
    code, out = run(root, "Today the build ran.")
    check("a sentence-initial capital still blocks", time_blocked(out), out)
    check("the reason names the mid-sentence capital as passing",
          "capital mid-sentence" in out, out)
    shutil.rmtree(root, ignore_errors=True)


def test_post_close_tail_offer_is_fed_back_once():
    """[post-close-tail-offer-enforced-once]: with the session-closed marker
    standing and a project write outside LOG/ logged after it, a reply that
    neither offers the tail nor carries one is fed back once; a reply that
    mentions the tail passes, and so does the second reply."""
    import time
    root = project()
    folder = os.path.join(root, ".throughliner")
    os.makedirs(folder)
    with open(os.path.join(folder, "session-closed-s1"), "w", encoding="utf-8") as f:
        f.write("2026-09-17-fixture.md\n")
    old = time.time() - 120
    os.utime(os.path.join(folder, "session-closed-s1"), (old, old))
    with open(os.path.join(folder, "pre-tool-use.log"), "w", encoding="utf-8", newline="") as f:
        f.write("2099-01-01 00:00:00\tEdit\tallow\tplanning standing list\t"
                + os.path.join(root, "SPEC.md") + "\ts1\n")
    code, out = run(root, "Reworded the sentence in SPEC.")
    check("a post-close reply with no tail offer is fed back",
          "marked tail" in out, out)
    code, out = run(root, "Reworded the sentence in SPEC.")
    check("the second reply passes", "marked tail" not in out, out)
    root2 = project()
    shutil.copytree(folder, os.path.join(root2, ".throughliner"))
    code, out = run(root2, "Reworded it. Want that appended to this session's record as a tail, or run done again?")
    check("a reply carrying the offer passes", "marked tail" not in out, out)
    shutil.rmtree(root, ignore_errors=True)
    shutil.rmtree(root2, ignore_errors=True)


def test_post_close_write_to_log_only_owes_nothing():
    root = project()
    folder = os.path.join(root, ".throughliner")
    os.makedirs(folder)
    with open(os.path.join(folder, "session-closed-s1"), "w", encoding="utf-8") as f:
        f.write("2026-09-17-fixture.md\n")
    with open(os.path.join(folder, "pre-tool-use.log"), "w", encoding="utf-8", newline="") as f:
        f.write("2099-01-01 00:00:00\tEdit\tallow\tplanning standing list\t"
                + os.path.join(root, "LOG", "x.md") + "\ts1\n")
    code, out = run(root, "Appended the note.")
    check("a write inside LOG/ alone owes no offer", "marked tail" not in out, out)
    shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    print("test_stop_hook")
    test_post_close_tail_offer_is_fed_back_once()
    test_post_close_write_to_log_only_owes_nothing()
    test_sourced_sentence_passes_and_bare_word_still_blocks()
    test_bare_time_word_blocks_once_with_the_phrase_named()
    test_time_word_inside_a_quotation_passes()
    test_day_words_and_elapsed_forms_block()
    test_capitalised_name_mid_sentence_passes()
    test_claim_inside_a_blockquote_does_not_block()
    test_claim_inside_a_fence_does_not_block()
    test_cited_shipped_slug_does_not_block()
    test_filing_claim_with_no_heading_and_no_log_entry_still_blocks()
    test_placeholder_slugs_from_a_specimen_do_not_block()
    test_a_genuinely_absent_slug_still_blocks_alongside_placeholders()
    test_a_queued_slug_does_not_block()
    test_block_still_downgrades_after_one_fire()
    test_ticked_slug_in_working_file_does_not_block()
    test_unticked_absent_slug_still_blocks_with_working_file()
    test_no_working_file_behaves_as_before()
    test_missing_log_directory_behaves_as_before()
    test_recorded_misses_are_now_caught()
    test_same_sentence_hedges_are_still_suppressed()
    test_hedge_paragraph_around_a_shipped_citation_still_passes()
    print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
    sys.exit(1 if failures else 0)
