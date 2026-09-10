# The parts of the method you can direct

A plain-language map of where the method's behaviour is decided, with an example
request that would reach each part. You never need a filename — describe the
behaviour and Claude locates the part; this map is what Claude answers from.

- **The always-loaded rules** (`plugin/throughliner/docs/skill-nonspecific-rules.md`)
  — how Claude talks to you and handles work in every chat: message shape,
  capturing ideas, red flags, file safety, when text is shown before writing.
  *"Stop putting the question in the middle of the message"* lands here.
- **One procedure doc per command** (`plugin/throughliner/docs/`) — what each
  command actually does, step by step: `plan.md`, `next.md` (+ `next-build.md`,
  which carries the audit section too), `done.md` (+ its per-flavour close
  docs), `setup.md`,
  `rescan.md`. *"When /plan presents an item, I want the analysis shorter"*
  lands in plan.md.
- **The brevity output style** (`plugin/throughliner/output-styles/brevity.md`)
  — the strongest lever on how Claude writes replies, applied per project.
  *"Replies are still too long even after the rules"* lands here.
- **This project's CLAUDE.md** — how sessions work on the method's own
  repository: the rule gate, the release rituals, host-only obligations.
  *"Stop running a release unless I ask"* lands here.
- **SPEC.md** — what the product is and does. *"The plugin should offer X at
  setup"* is a SPEC change plus build work.
- **The hooks** (`plugin/throughliner/hooks/`) — what is mechanically enforced:
  the scope-lock (`pre_tool_use`), session openings (`session_start`), the
  queue lint (`post_tool_use`), the filed-claim check (`stop`). *"Claude edited
  a file it shouldn't have been able to"* lands here.
- **The templates** (`plugin/throughliner/templates/`) — what a fresh consumer
  project receives: the CLAUDE.md block, the FAQ. *"New projects should start
  with a different explanation of the queue"* lands here.
