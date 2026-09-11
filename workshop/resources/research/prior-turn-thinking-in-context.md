# Does a session see its own earlier thinking? — kept in context on Opus 4.5 and every 4.6-and-higher model; stripped on Sonnet 4.5, Haiku 4.5 and earlier

Filed 2026-09-11 10:55 at planning, to settle [sweep-howto-6-rescan-reads-thinking-unsupported]: how-to topic 6 claims /rescan reads back over Claude's own thinking from earlier in the conversation, and no shipped doc says whether that is possible.

## Finding

Anthropic's extended-thinking documentation, read 2026-09-11 (https://platform.claude.com/docs/en/build-with-claude/extended-thinking, "Migrating to adaptive thinking"): *"Claude Opus 4.5 and models numbered 4.6 and higher keep prior turns' thinking blocks in context and bill them as input, where Claude Sonnet 4.5, Claude Haiku 4.5, and earlier models stripped them."* The same page points at a per-model "thinking block preservation" table on the thinking overview page. A search across the same subject turned up the older behaviour in several harness bug reports — thinking blocks stripped from every assistant turn but the latest — which is the pre-4.6 shape, not the current one.

So on the models this method targets (the 5-series, and Opus 4.5 and up), a session's earlier thinking is in its context, and a /rescan reading back over the conversation can see it. On Sonnet 4.5, Haiku 4.5 and earlier it cannot.

## What this settles

The how-to topic's claim holds for the method's target models and needs no correction. The claim is model-dependent, and a reader on an older model would find it false; the topic does not say so, and that is accepted rather than corrected, since the method does not support those models.

## Frame assessment

- **TIME RANGE** — not applicable; no period.
- **PEOPLE** — applies to any user of the method on a supported model; a user on Sonnet 4.5 or earlier is outside the method's target and outside this finding's reassurance.
- **FRESHNESS** — a documented model capability; re-read when the docset's model target changes, and when Anthropic's thinking-preservation table changes.
- **RISK IF WRONG** — a how-to topic promising a read the session cannot make; the harm is a user expecting captures from reasoning that was never in view. Warrants the rests-on line on this finding and nothing more.
- **ALTERNATIVES** — a test in a live session (ask Claude to quote its own earlier thinking) was not run; the documentation statement is direct enough that the test would confirm rather than decide.
