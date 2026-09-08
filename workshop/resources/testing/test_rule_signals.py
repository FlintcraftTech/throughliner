#!/usr/bin/env python3
"""Regression tests for rule_signals.py's backfill skip.

Host-only dev artifact — not shipped in the plugin package.

Run:  py resources/testing/test_rule_signals.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

A real git repository is built per case, because the thing under test reads
`git log` and the defect is specifically about which commit is newest.
"""

import importlib.util
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

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SCRIPT = os.path.join(ROOT, "workshop", "resources", "rule_signals.py")

_spec = importlib.util.spec_from_file_location("rule_signals", SCRIPT)
signals = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(signals)

failures = []


def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


def git(root, *args):
    subprocess.run(["git"] + list(args), cwd=root, check=True,
                   capture_output=True, text=True, errors="replace")


def repo(heading):
    """A repo with a baseline commit, then one commit touching a rule file.

    `heading` is the LOG entry's first line — a real hash or the `[HASH]`
    placeholder — written before the rule-bearing commit is made, exactly as a
    close writes it.
    """
    root = tempfile.mkdtemp(prefix="rule-signals-test-")
    git(root, "init", "-q")
    git(root, "config", "user.email", "t@example.com")
    git(root, "config", "user.name", "T")

    os.makedirs(os.path.join(root, "LOG"))
    with open(os.path.join(root, "README.md"), "w", encoding="utf-8") as f:
        f.write("baseline\n")
    git(root, "add", "README.md")
    git(root, "commit", "-q", "-m", "baseline")
    baseline = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root,
                              capture_output=True, text=True).stdout.strip()

    docs = os.path.join(root, "plugin", "throughliner", "docs")
    os.makedirs(docs)
    with open(os.path.join(docs, "plan.md"), "w", encoding="utf-8") as f:
        f.write("A rule-bearing file.\n")
    with open(os.path.join(root, "LOG", "2026-08-21-thing.md"), "w",
              encoding="utf-8") as f:
        f.write(f"# {heading} — a session\n\nRule gate: run — admitted.\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "a rule-bearing commit")
    return root, baseline


def rule_commits(root, baseline):
    signals.DISPOSITION_BASELINE = baseline
    return signals._rule_bearing_commits(root)


def test_placeholder_entry_suppresses_the_freshest_commit():
    """Run immediately after a close, the check must find nothing.

    The disposition is written and correct; its heading just cannot be matched
    to a hash that did not exist when the entry was written.
    """
    root, baseline = repo("[HASH]")
    commits, err = rule_commits(root, baseline)
    check("a pending backfill hides the newest commit",
          err is None and commits == [], f"{err!r} {commits!r}")
    shutil.rmtree(root, ignore_errors=True)


def test_backfilled_entry_restores_normal_behaviour():
    """With every heading backfilled, nothing is skipped."""
    root, baseline = repo("PLACEHOLDER")
    real = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root,
                          capture_output=True, text=True).stdout.strip()
    entry = os.path.join(root, "LOG", "2026-08-21-thing.md")
    with open(entry, "w", encoding="utf-8") as f:
        f.write(f"# {real} — a session\n\nRule gate: run — admitted.\n")
    commits, err = rule_commits(root, baseline)
    check("a backfilled repository checks the newest commit as before",
          err is None and len(commits) == 1, f"{err!r} {commits!r}")
    shutil.rmtree(root, ignore_errors=True)


def test_placeholder_only_counts_in_a_heading():
    """A prose mention of the placeholder is not a pending backfill."""
    root = tempfile.mkdtemp(prefix="rule-signals-test-")
    os.makedirs(os.path.join(root, "LOG"))
    with open(os.path.join(root, "LOG", "e.md"), "w", encoding="utf-8") as f:
        f.write("# abc1234 — a session\n\nThe close writes [HASH] first.\n")
    check("a placeholder in prose does not read as pending",
          not signals._backfill_pending(root))
    shutil.rmtree(root, ignore_errors=True)


def test_no_log_directory_is_not_pending():
    root = tempfile.mkdtemp(prefix="rule-signals-test-")
    check("a project with no LOG/ is never pending",
          not signals._backfill_pending(root))
    shutil.rmtree(root, ignore_errors=True)


def test_nested_project_reads_both_histories():
    """A nested project's rule corpus straddles two repositories.

    The outer holds CLAUDE.md and LOG/; the inner holds the shipped docs. Both
    histories carry rule-bearing commits, and the dispositions for both sit in
    the outer's LOG. Run from the outer, the check must find both commits and
    match each to its disposition — before this, run from either repository it
    saw half the corpus.
    """
    outer = tempfile.mkdtemp(prefix="rule-signals-nested-")
    git(outer, "init", "-q")
    git(outer, "config", "user.email", "t@example.com")
    git(outer, "config", "user.name", "T")
    os.makedirs(os.path.join(outer, "LOG"))
    inner = os.path.join(outer, "product")
    os.makedirs(inner)
    git(inner, "init", "-q")
    git(inner, "config", "user.email", "t@example.com")
    git(inner, "config", "user.name", "T")

    # The inner: a baseline commit, then a commit touching a shipped doc.
    with open(os.path.join(inner, "README.md"), "w", encoding="utf-8") as f:
        f.write("product\n")
    git(inner, "add", "README.md")
    git(inner, "commit", "-q", "-m", "baseline")
    baseline = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=inner,
                              capture_output=True, text=True).stdout.strip()
    docs = os.path.join(inner, "plugin", "throughliner", "docs")
    os.makedirs(docs)
    with open(os.path.join(docs, "plan.md"), "w", encoding="utf-8") as f:
        f.write("A rule-bearing file.\n")
    git(inner, "add", "-A")
    git(inner, "commit", "-q", "-m", "inner rule commit")
    inner_sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=inner,
                               capture_output=True, text=True).stdout.strip()

    # The outer: CLAUDE.md with the Visibility line naming the inner, then a
    # second commit touching it (rule-bearing in the outer).
    claude = os.path.join(outer, "CLAUDE.md")
    with open(claude, "w", encoding="utf-8") as f:
        f.write("# Project\n\nVisibility: nested — the outer repository holds "
                "the documents; the inner repository (`product/`) holds only "
                "the product.\n")
    with open(os.path.join(outer, ".gitignore"), "w", encoding="utf-8") as f:
        f.write("product/\n")
    git(outer, "add", "CLAUDE.md", ".gitignore")
    git(outer, "commit", "-q", "-m", "outer first commit")
    with open(claude, "a", encoding="utf-8") as f:
        f.write("\n- **A rule.**\n")
    git(outer, "add", "CLAUDE.md")
    git(outer, "commit", "-q", "-m", "outer rule commit")
    outer_sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=outer,
                               capture_output=True, text=True).stdout.strip()

    # Dispositions for both, in the outer's LOG.
    with open(os.path.join(outer, "LOG", "2026-09-05-inner.md"), "w",
              encoding="utf-8") as f:
        f.write(f"# {inner_sha} — inner session\n\nRule gate: run — admitted.\n")
    with open(os.path.join(outer, "LOG", "2026-09-05-outer.md"), "w",
              encoding="utf-8") as f:
        f.write(f"# {outer_sha} — outer session\n\nRule gate: run — admitted.\n")

    check("the inner is found from the Visibility line",
          signals.inner_root(outer) == inner, repr(signals.inner_root(outer)))
    commits, err = rule_commits(outer, baseline)
    shas = {c["sha"] for c in commits}
    check("both repositories' rule-bearing commits are read",
          err is None and shas == {inner_sha, outer_sha}, f"{err!r} {shas!r}")
    check("the outer's root commit, which imported CLAUDE.md, owes no "
          "disposition", len(commits) == 2, repr([c["subject"] for c in commits]))
    born = signals.signal_born(outer)
    check("each commit matches its disposition in the outer's LOG",
          not born["firing"], born["message"])
    total, per_file = signals.count_statements(
        outer, ["CLAUDE.md", "plugin/throughliner/docs/plan.md"])
    check("corpus files are read from whichever repository holds them",
          set(per_file) == {"CLAUDE.md", "plugin/throughliner/docs/plan.md"},
          repr(per_file))
    shutil.rmtree(outer, ignore_errors=True)


def test_dispositions_window_follows_index_order():
    """A same-day build record sorts BEFORE the planning record by filename
    (`-build.md` < `.md`) but sits above it in the index, and it is in the
    window ([dispositions-window-misses-same-day-records])."""
    root = tempfile.mkdtemp(prefix="rule-signals-window-")
    log = os.path.join(root, "LOG")
    os.makedirs(log)
    with open(os.path.join(log, "2026-09-05-item.md"), "w", encoding="utf-8") as f:
        f.write("# abc1234 — plan — the item\n\nPlanning.\n\n"
                "**Work processed:** kept.\n\nRule gate: run — admitted.\n")
    with open(os.path.join(log, "2026-09-05-item-build.md"), "w",
              encoding="utf-8") as f:
        f.write("# def5678 — the item built\n\nBuilt.\n\n"
                "**Files touched:** `a.md`\n\nRule gate: run — refused the extra clause.\n")
    with open(os.path.join(log, "2026-09-04-older.md"), "w", encoding="utf-8") as f:
        f.write("# 0123abc — an older build\n\nRule gate: run — admitted earlier.\n")
    with open(os.path.join(log, "index.md"), "w", encoding="utf-8") as f:
        f.write("# LOG Index\n\n"
                "- def5678 — the item built → 2026-09-05-item-build.md\n"
                "- abc1234 — plan — the item → 2026-09-05-item.md\n"
                "- 0123abc — an older build → 2026-09-04-older.md\n")
    found, note = signals.dispositions(root, window=True)
    entries = [d["entry"] for d in found]
    check("the same-day build record is inside the window",
          entries == ["2026-09-05-item-build.md"], repr((entries, note)))
    check("its refusal is read", any(d["refusal"] for d in found), repr(found))
    check("the older record below the boundary is outside the window",
          "2026-09-04-older.md" not in entries, repr(entries))
    shutil.rmtree(root, ignore_errors=True)


def test_parent_lookup_ranks_a_paraphrase_first():
    """A paraphrase of a known always-loaded rule ranks that rule first, and
    the section printed for it is the heading above it
    ([rule-gate-parent-lookup])."""
    root = tempfile.mkdtemp(prefix="rule-signals-parent-")
    docs = os.path.join(root, "plugin", "throughliner", "docs")
    os.makedirs(docs)
    with open(os.path.join(docs, "skill-nonspecific-rules.md"), "w",
              encoding="utf-8") as f:
        f.write("# Rules\n\n## Communication\n\n"
                "- Write in plain language, using a term of art only after "
                "the user has used it.\n\n"
                "## File safety\n\n"
                "- **Name each path when staging a commit, and never push "
                "with force.**\n")
    with open(os.path.join(root, "CLAUDE.md"), "w", encoding="utf-8") as f:
        f.write("# Project\n\n## Working conventions\n\n"
                "- **Use absolute paths for sub-folder lookups on this "
                "machine.**\n")
    hits = signals.parent_lookup(
        root, "Stage a commit by naming each path, and never force-push")
    check("the paraphrased rule ranks first",
          hits and "name each path" in hits[0]["norm"], repr(hits[:2]))
    check("the top hit names its own section",
          hits and hits[0]["section"] == "File safety", repr(hits[:1]))
    shutil.rmtree(root, ignore_errors=True)


def test_duplicate_check_flags_a_cross_group_pair():
    """One statement in an always-loaded fixture and its near-copy in a skill
    doc are flagged as a pair, and the report names each side's group
    ([duplicate-check-covers-skill-docs])."""
    root = tempfile.mkdtemp(prefix="rule-signals-dup-")
    docs = os.path.join(root, "plugin", "throughliner", "docs")
    os.makedirs(docs)
    rule = ("- **A send or post goes out only after the user has seen the "
            "exact text and given an explicit yes.**\n")
    with open(os.path.join(docs, "skill-nonspecific-rules.md"), "w",
              encoding="utf-8") as f:
        f.write("# Rules\n\n## Mail\n\n" + rule)
    with open(os.path.join(docs, "plan.md"), "w", encoding="utf-8") as f:
        f.write("# Plan\n\n## Sends\n\n" + rule)
    with open(os.path.join(root, "CLAUDE.md"), "w", encoding="utf-8") as f:
        f.write("# Project\n")
    result = signals.signal_maintained(root)
    check("the always-loaded rule and its skill-doc copy are flagged",
          result["firing"] and result["value"] == 1, result["message"])
    check("the pair names the group of each side",
          "[always-loaded]" in result["message"]
          and "[skill doc]" in result["message"], result["message"])
    shutil.rmtree(root, ignore_errors=True)


def test_size_report_deltas_against_the_last_sweep_turn():
    """Two commits: a sweep record names the first; the second grows one
    file. The per-file line reports the growth against the first
    ([doc-size-per-file-in-sweep])."""
    root = tempfile.mkdtemp(prefix="rule-signals-size-")
    git(root, "init", "-q")
    git(root, "config", "user.email", "t@example.com")
    git(root, "config", "user.name", "T")
    docs = os.path.join(root, "plugin", "throughliner", "docs")
    os.makedirs(docs)
    os.makedirs(os.path.join(root, "LOG"))
    rules = os.path.join(docs, "skill-nonspecific-rules.md")
    with open(rules, "w", encoding="utf-8") as f:
        f.write("one two three\n")
    with open(os.path.join(root, "CLAUDE.md"), "w", encoding="utf-8") as f:
        f.write("a b\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "sweep turn")
    sweep_sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root,
                               capture_output=True, text=True).stdout.strip()
    with open(os.path.join(root, "LOG", "2026-09-06-maintenance-sweep-build.md"),
              "w", encoding="utf-8") as f:
        f.write(f"# {sweep_sha} — the sweep\n\nThis record records a completed "
                "turn of the [maintenance-sweep] cycle.\n")
    with open(rules, "a", encoding="utf-8") as f:
        f.write("four five\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "growth")
    entry, rows = signals.size_report(root)
    by_file = {r[0].split("/")[-1]: r for r in rows}
    check("the anchor is the completed sweep turn's record",
          entry == "2026-09-06-maintenance-sweep-build.md", repr(entry))
    r = by_file.get("skill-nonspecific-rules.md")
    check("the grown file's delta is the ten bytes and two words appended",
          r and r[1] - r[3] == 10 and r[2] - r[4] == 2, repr(r))
    c = by_file.get("CLAUDE.md")
    check("an unchanged file reports zero change",
          c and c[1] == c[3] and c[2] == c[4], repr(c))
    shutil.rmtree(root, ignore_errors=True)


def _nested_close_fixture(with_gate_line):
    """An inner commit touching docs/ and, one second later, an outer commit
    touching LOG/ whose record carries the OUTER hash in its heading — the
    shape every nested close leaves ([rule-gate-dispositions-missing])."""
    outer = tempfile.mkdtemp(prefix="rule-signals-close-")
    for r in (outer,):
        git(r, "init", "-q")
        git(r, "config", "user.email", "t@example.com")
        git(r, "config", "user.name", "T")
    inner = os.path.join(outer, "product")
    os.makedirs(inner)
    git(inner, "init", "-q")
    git(inner, "config", "user.email", "t@example.com")
    git(inner, "config", "user.name", "T")
    os.makedirs(os.path.join(outer, "LOG"))

    env_t = lambda t: dict(os.environ, GIT_COMMITTER_DATE=t, GIT_AUTHOR_DATE=t)

    def commit(repo, msg, when):
        subprocess.run(["git", "commit", "-q", "-m", msg], cwd=repo, check=True,
                       env=env_t(when), capture_output=True)

    with open(os.path.join(inner, "README.md"), "w", encoding="utf-8") as f:
        f.write("product\n")
    git(inner, "add", "README.md")
    commit(inner, "baseline", "2026-09-06T10:00:00+10:00")
    baseline = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=inner,
                              capture_output=True, text=True).stdout.strip()
    docs = os.path.join(inner, "plugin", "throughliner", "docs")
    os.makedirs(docs)
    with open(os.path.join(docs, "plan.md"), "w", encoding="utf-8") as f:
        f.write("A rule-bearing file.\n")
    git(inner, "add", "-A")
    commit(inner, "inner rule commit", "2026-09-06T10:00:10+10:00")
    inner_sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=inner,
                               capture_output=True, text=True).stdout.strip()

    claude = os.path.join(outer, "CLAUDE.md")
    with open(claude, "w", encoding="utf-8") as f:
        f.write("# Project\n\nVisibility: nested — the inner repository "
                "(`product/`) holds only the product.\n")
    with open(os.path.join(outer, ".gitignore"), "w", encoding="utf-8") as f:
        f.write("product/\n")
    git(outer, "add", "CLAUDE.md", ".gitignore")
    commit(outer, "outer first commit", "2026-09-06T09:00:00+10:00")
    # The close's outer commit: it writes the record, one second after the
    # inner commit, and the record's heading names the OUTER hash — which is
    # unknown until the commit exists, so a placeholder goes in first and is
    # replaced the way the backfill would.
    entry = os.path.join(outer, "LOG", "2026-09-06-close.md")
    body = "Rule gate: run — admitted.\n" if with_gate_line else "Built.\n"
    with open(entry, "w", encoding="utf-8") as f:
        f.write("# PLACEHOLDER — the close\n\n" + body)
    git(outer, "add", "LOG")
    commit(outer, "close", "2026-09-06T10:00:11+10:00")
    outer_sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=outer,
                               capture_output=True, text=True).stdout.strip()
    with open(entry, "w", encoding="utf-8") as f:
        f.write(f"# {outer_sha} — the close\n\n" + body)
    return outer, baseline, inner_sha, outer_sha


def test_inner_commit_is_attributed_to_the_outer_close():
    """With the gate line under the outer hash, the inner commit is covered
    and the check finds nothing."""
    outer, baseline, inner_sha, outer_sha = _nested_close_fixture(True)
    commits, err = rule_commits(outer, baseline)
    by_sha = {c["sha"]: c for c in commits}
    check("the inner commit's close is the outer commit",
          err is None and inner_sha in by_sha
          and by_sha[inner_sha]["close_sha"] == outer_sha,
          repr((err, {k: v.get("close_sha") for k, v in by_sha.items()})))
    born = signals.signal_born(outer)
    check("a gate line under the outer hash covers the inner commit",
          not born["firing"], born["message"])
    shutil.rmtree(outer, ignore_errors=True)


def test_inner_commit_without_a_gate_line_is_flagged_with_both_hashes():
    outer, baseline, inner_sha, outer_sha = _nested_close_fixture(False)
    signals.DISPOSITION_BASELINE = baseline
    born = signals.signal_born(outer)
    check("the inner commit is flagged when its close carries no line",
          born["firing"] and inner_sha in born["message"], born["message"])
    check("the flag prints both hashes",
          outer_sha in born["message"], born["message"])
    shutil.rmtree(outer, ignore_errors=True)


def test_flat_project_has_no_inner():
    root = tempfile.mkdtemp(prefix="rule-signals-flat-")
    os.makedirs(os.path.join(root, "LOG"))
    check("a flat project reports no inner repository",
          signals.inner_root(root) is None)
    check("a flat project reads one repository",
          [l for l, _ in signals.repos(root)] == ["outer"])
    shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    print("test_rule_signals")
    test_nested_project_reads_both_histories()
    test_flat_project_has_no_inner()
    test_parent_lookup_ranks_a_paraphrase_first()
    test_duplicate_check_flags_a_cross_group_pair()
    test_size_report_deltas_against_the_last_sweep_turn()
    test_inner_commit_is_attributed_to_the_outer_close()
    test_inner_commit_without_a_gate_line_is_flagged_with_both_hashes()
    test_dispositions_window_follows_index_order()
    test_placeholder_entry_suppresses_the_freshest_commit()
    test_backfilled_entry_restores_normal_behaviour()
    test_placeholder_only_counts_in_a_heading()
    test_no_log_directory_is_not_pending()
    print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
    sys.exit(1 if failures else 0)
