# Editing-state signal — the published contract

While Claude is writing a file, this plugin's hooks publish a small marker saying
so, so another application open on the same document can hold off rather than the
two landing on top of each other.

**This document is the interface other applications are built against.** It will
not change without a version bump.

**Known consumers:** a companion application reads these markers, so a version-3
change is a change with a live dependency — the conformance test at
`tests/test_editing_state_contract.py` pins this document to what
the hook actually writes. It lives at the repository root, rather than in
`SPEC.md` or a development folder, because a consumer of the contract has to be
able to find it: SPEC.md answers "what is this product", and a field-level
interface specification is not that.

It is a **heartbeat, not a lock**, and that is what makes it safe. Every marker
carries a fresh timestamp, and a reader treats a stale marker as "not editing"
whatever its flag says — so a session that crashes between starting a write and
finishing one can never leave the user locked out. Staleness is the safety
property, not a detail.

## The contract

- **Location** — `.throughliner/` in the project root (the folder holding SPEC.md
  and QUEUE.md). A reader with a document open walks up the directory tree to find
  it, the way tools locate `.git/`.

- **The folder may hold other transient plugin state, so a conforming reader
  matches the marker filename shape (`editing-<session-id>.json`) and ignores
  everything else.** Entries that are not markers may include subdirectories,
  and a reader that lists the directory and opens every entry will meet one.
  This is additive: it makes explicit what the normative filename below already
  implied, so no reader that already filtered by that shape changes.

- **One file per session**, named `editing-<session-id>.json`, holding:

  - `version` — leading, so a reader can recognise a format it doesn't understand
    and fall back safely. **Currently 2.**
  - `active` — whether a write is in flight.
  - `written_at` — ISO 8601 with an explicit UTC offset. **For diagnosis, not
    freshness**; see the reader policy below.
  - `files` — **project-relative paths**, relative to the directory containing
    `.throughliner/`, forward slashes on every platform, no leading `./`, exactly
    one path per marker. A file outside the project falls back to its absolute
    path.
  - `producer` — a constant string naming what wrote the marker. This plugin
    writes `throughliner`, a format value that survives any product rename.

  Version 2 made `files` relative — a version-1 reader would resolve relative
  paths against the wrong root, which is exactly what the version field exists to
  prevent — renamed `updated` to `written_at` so the field is named for what it is
  safe to use for, and dropped `session` and `pid`, which nothing read: `pid` is
  unusable across machines and redundant on one, and `session` restates the
  filename.

  One file per session rather than one shared file, because two Claude sessions in
  one project is a supported shape: with a shared file, one session finishing a
  write would clear the flag while the other was still writing. The reader's rule
  is therefore trivially correct — **editing is happening if any file here is
  active and fresh.**

- **The signal fires per edit, not per build.** The opening hook writes
  `active: true` before each editing-tool call and the closing hook writes
  `active: false` after it, so a twenty-file build turns the signal on and off
  twenty times. A reader that maps the flag straight onto an indicator will
  flicker in every gap between edits, so it needs to hold briefly past
  `active: false`. **No number is published for that hold, deliberately** — nobody
  has measured real traffic yet, and publishing a guess would launder it into the
  interface. The trade-off that decides the length: a longer hold bridges longer
  thinking pauses; it also locks the user out for that long after every genuine
  finish.

- **Recommended reader policy, published as guidance rather than enforced.** Treat
  `active: true` as editing. Judge freshness by **the marker file's own local
  modification time**, treating a marker untouched for about 30 seconds as a dead
  session. Treat a missing directory or an unreadable file as "not editing", never
  as an error.

  `written_at` is for diagnosis, never freshness — and the reason mtime wins is
  about **failure direction**, not clock arithmetic. An mtime that reads wrongly
  old fails open (nothing held, nobody locked out) and wrongly new fails mild and
  self-clearing, while a `written_at` from a fast or foreign clock fails closed: a
  dead session looks permanently current and the user is locked out of their own
  document indefinitely, precisely the failure the heartbeat design exists to
  prevent. That reasoning holds whatever any sync client does to timestamps, on any
  platform.

  Two more comparisons made explicit so no consumer guesses at them: **path
  comparison is case-insensitive on Windows** — the marker's path and the reader's
  open-document path can differ in case and be the same file, and matching them is
  the one comparison the signal exists for — and relative paths carry **no leading
  `./`**, so readers are not string-trimming.

  The hook reports facts and the reader decides policy, deliberately: the reader
  knows what its user is doing and the hook does not.

- **It fails open**, and must: most projects never have this plugin installed, so a
  reader that blocked on the directory's absence would be broken everywhere else.
  Writing the marker can never block or fail a tool call either — a companion-app
  convenience must not be able to stop the user's actual work.

- **What it cannot say** — that Claude has *finished* rather than paused to think.
  Nothing available can know that, and pretending otherwise would be the same false
  promise the timing guess was rejected for. What changes is that the reader is no
  longer guessing: it knows a write is in flight and exactly how long things have
  been quiet.

- **Two known limits** — writes made through a shell command aren't covered (the
  hook only sees the edit tools, and a shell command's target file isn't reliably
  knowable), and the signal only exists where the plugin is installed and the
  project adopted. Everywhere else the directory simply never appears, which the
  fail-open rule already handles.

## Housekeeping

Marker files left by crashed sessions are swept at the next session start, after an
hour — housekeeping only, since the staleness rule is what makes the signal safe.

The folder is transient session state, so `/setup` gitignores it and git never
commits it. **Gitignore is all that claim covers:** it keeps the folder out of the
repository and does nothing about file sync. A project inside a Drive, OneDrive or
Dropbox folder replicates these markers as they are written, which is why version 2
stopped writing absolute paths — the identifying payload is gone rather than
contained.
