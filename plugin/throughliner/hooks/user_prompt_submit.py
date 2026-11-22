#!/usr/bin/env python3
"""UserPromptSubmit hook: hand Claude the one FAQ entry a question matches,
and record whether the session has typed one of the method's commands.

Runs on each message the user sends ([faq-entry-offered-when-user-asks]).
Where the message is shaped like a question and clearly matches one question
in the installed plugin's own FAQ, the hook returns that one entry as
additional context for the turn, once per entry per chat. On every other
message it prints nothing, and it never blocks a message: any fault exits 0
with empty stdout.

THE MATCH IS BY SHARED WORDS, and that is its stated limit. A question worded
with none of an entry's words is missed, and the session opening's pointer at
the FAQ remains the fallback. A wrong match costs one entry's text, and the
text handed over tells Claude to ignore it where it does not fit.

Rests on the Claude Code hooks reference (read 2026-11-17): a plugin's
`hooks/hooks.json` may register `UserPromptSubmit`, which takes no matcher;
the hook receives the user's text in `prompt` with `session_id` and `cwd`;
and `hookSpecificOutput.additionalContext` is added to what Claude reads for
the turn, capped at 10,000 characters. A typed slash command reaches the hook
as typed, not as its expanded text.
"""

import json
import os
import re
import sys

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        # Python < 3.7, or a stream that cannot be reconfigured (redirected to
        # a pipe or replaced by a test harness). Messages then behave as before
        # — degraded, never fatal.
        pass

# Tuned only by tests/test_user_prompt_submit_faq.py.
MIN_SCORE = 5          # a heading word counts 2, a summary-only word 1
MIN_HEADING_WORDS = 2  # shared words that must come from the question heading
MAX_WORDS = 60         # a longer message is not a quick question
ANSWER_CAP = 2000      # characters of the entry's answer handed over

QUESTION_OPENERS = {
    "how", "why", "what", "where", "when", "which", "who", "can", "could",
    "does", "do", "did", "is", "are", "should", "will",
}

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "so", "of", "to", "in",
    "on", "at", "by", "for", "from", "with", "without", "into", "onto", "as",
    "is", "are", "was", "were", "be", "been", "am", "it", "its", "this", "that",
    "these", "those", "there", "here", "i", "me", "my", "we", "our", "you",
    "your", "he", "she", "they", "them", "their", "do", "does", "did", "doe",
    "done", "can", "could", "should", "would", "will", "shall", "may", "might",
    "must", "have", "has", "had", "ha", "how", "why", "what", "where", "when",
    "which", "who", "whose", "not", "no", "yes", "ok", "okay", "just", "get",
    "got", "go", "going", "one", "any", "some", "all", "every", "each", "more",
    "up", "out", "about", "after", "before", "again", "also", "than", "too",
    "very", "thi", "wa", "need", "want", "like", "make", "mean", "happen",
    "actually", "thing", "something", "anything", "way", "use", "using",
    "next", "take", "now", "still", "ever", "between", "instead", "own",
    "claude", "throughliner", "project", "show", "tell", "say", "see", "know",
    "let", "put", "keep", "give", "s", "t", "d", "ll", "re", "ve", "m",
}

_WORD = re.compile(r"[a-z0-9]+")


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


def _safe_id(session_id) -> str:
    """The hooks' own sanitiser: filename-safe characters only."""
    return re.sub(r"[^A-Za-z0-9._-]", "_", str(session_id or "unknown"))


# The method's own commands, as pre_tool_use.py's METHOD_SKILLS lists them.
METHOD_SKILLS = frozenset({
    "setup", "plan", "process", "build", "rescan", "close", "catchup", "tasks",
    "memory-setup", "goals",
})
SKILL_STATE_NONE = "none"


def method_skill_typed(prompt: str) -> str:
    """The Throughliner command a prompt types, or ''. A typed slash command
    reaches this hook as the line typed. `/throughliner:plan` and the bare
    `/plan` both count; another plugin's or the project's own skill does not,
    so a session running one stays a session with no Throughliner skill."""
    stripped = (prompt or "").strip()
    if not stripped.startswith("/"):
        return ""
    token = stripped[1:].split(None, 1)[0].lower() if stripped[1:].strip() else ""
    prefix, _, bare = token.rpartition(":")
    if bare in METHOD_SKILLS and (
            not prefix or "throughliner" in prefix or "flintcraft" in prefix):
        return bare
    return ""


def record_skill_state(root: str, session_id, prompt: str) -> None:
    """Keep `.throughliner/session-skill-<session-id>.txt` saying whether any
    prompt of this session typed a Throughliner command
    ([safety-check-freeform-double-ask]): `none` from the first prompt on,
    the command's name once one is typed, and never back to `none`. The
    safety check opens a no-skill session's scope file with no prior refusal
    only where this file reads `none`; where the file is absent, because this
    hook did not run, the check behaves as it did before."""
    folder = os.path.join(root, ".throughliner")
    path = os.path.join(folder, "session-skill-%s.txt" % _safe_id(session_id))
    typed = method_skill_typed(prompt)
    if not typed and os.path.isfile(path):
        return
    os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write((typed or SKILL_STATE_NONE) + "\n")


def content_words(text: str) -> set:
    """Lower-cased content words: stop words dropped, a trailing `s` stripped."""
    words = set()
    for raw in _WORD.findall(text.lower()):
        if raw in STOP_WORDS:
            continue
        word = raw[:-1] if len(raw) > 3 and raw.endswith("s") else raw
        if word and word not in STOP_WORDS and len(word) > 1:
            words.add(word)
    return words


def is_question(message: str) -> bool:
    stripped = message.strip()
    if not stripped or stripped.startswith("/"):
        return False
    if len(stripped.split()) > MAX_WORDS:
        return False
    if "?" in stripped:
        return True
    first = _WORD.findall(stripped.lower()[:40])
    return bool(first) and first[0] in QUESTION_OPENERS


def _templates_dir() -> str:
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")


def load_entries() -> list:
    """Each FAQ entry as (question, answer, heading words, summary words)."""
    templates = _templates_dir()
    with open(os.path.join(templates, "faq-template.md"), encoding="utf-8") as f:
        faq = f.read()
    summaries = {}
    try:
        with open(os.path.join(templates, "faq-index-template.md"),
                  encoding="utf-8") as f:
            index = f.read()
        for bullet in re.split(r"(?m)^- (?=\*\*)", index)[1:]:
            m = re.match(r"\*\*(.+?)\*\*(.*)", bullet, re.DOTALL)
            if not m:
                continue
            summary = re.sub(r"\[faq\.md\]\(faq\.md\)", " ", m.group(2))
            summaries[" ".join(m.group(1).split()).lower()] = " ".join(summary.split())
    except OSError:
        pass
    entries = []
    parts = re.split(r"(?m)^## (.+)$", faq)
    for i in range(1, len(parts) - 1, 2):
        question = parts[i].strip()
        answer = parts[i + 1].strip()
        heading = content_words(question)
        summary = content_words(summaries.get(" ".join(question.split()).lower(), ""))
        entries.append((question, answer, heading, summary - heading))
    return entries


def best_match(message: str, entries: list):
    """The single clearly matching entry, or None."""
    words = content_words(message)
    if not words:
        return None
    scored = []
    for question, answer, heading, summary in entries:
        shared_heading = len(words & heading)
        score = 2 * shared_heading + len(words & summary)
        scored.append((score, shared_heading, question, answer))
    scored.sort(key=lambda s: s[0], reverse=True)
    if not scored:
        return None
    top = scored[0]
    if top[0] < MIN_SCORE or top[1] < MIN_HEADING_WORDS:
        return None
    if len(scored) > 1 and scored[1][0] == top[0]:
        return None
    return top[2], top[3]


def already_offered(root: str, session_id, question: str) -> bool:
    """True where this chat was already handed the entry; records it otherwise."""
    folder = os.path.join(root, ".throughliner")
    path = os.path.join(folder, "faq-offered-%s.txt" % _safe_id(session_id))
    seen = []
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            seen = [line.rstrip("\n") for line in f]
    if question in seen:
        return True
    os.makedirs(folder, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(question + "\n")
    return False


def faq_context(data: dict, root: str):
    prompt = data.get("prompt") or ""
    if not isinstance(prompt, str) or not is_question(prompt):
        return None
    match = best_match(prompt, load_entries())
    if not match:
        return None
    question, answer = match
    if already_offered(root, data.get("session_id"), question):
        return None
    if len(answer) > ANSWER_CAP:
        answer = answer[:ANSWER_CAP].rstrip() + " …"
    return (
        '[Throughliner] The workflow FAQ has an entry that may answer this: "%s". '
        "From the installed plugin's FAQ:\n\n%s\n\n"
        "Answer from it where it fits what was asked, saying the answer is from "
        "the FAQ; ignore it where the question is about something else."
        % (question, answer)
    )


def main():
    data = json.load(sys.stdin)
    if not isinstance(data, dict):
        return
    root = project_root(data)
    if not root or not os.path.isfile(os.path.join(root, "QUEUE.md")):
        return
    try:
        prompt = data.get("prompt")
        record_skill_state(root, data.get("session_id"),
                           prompt if isinstance(prompt, str) else "")
    except Exception:
        pass
    context = faq_context(data, root)
    if context:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": context,
            }
        }))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # A fault in this hook never blocks a message.
        pass
    sys.exit(0)
