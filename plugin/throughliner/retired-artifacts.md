# Retired artifacts

Files the method used to generate and no longer does. Ships with the plugin, and
`session_start` reads it: where one of these paths is still sitting in a
project, the session opening names it and says what produced it.

**Why it ships when the retiring happens here.** Retiring a feature removes the
code that writes an artifact; it does not remove the artifact from projects that
already have one. Nothing carried that fact out of the development project, so a
file could sit at a user's project root that nothing produces and nothing reads,
and working out what it was took reading the plugin's source.

**Reported, never deleted.** Removing a file from someone's project is exactly
what the add-only posture exists to prevent. Whether to keep it is theirs.

**Format** — the reader parses exactly this shape, so keep it:

```
- `path/relative/to/the/project` — what produced it, and when it was retired
```

A path is matched relative to the project root. A trailing slash means a folder.

## The list

- `BUILD-VIEW.md` — the generated build view a run used to read instead of the
  queue, written by `scripts/generate_build_view.py`. Retired 2026-08-27 when
  builds went back to reading the queue whole.
- `.mcp.json` — the per-project registration of the method's state server,
  written by hand in the development project while the server was dogfooded
  there. Retired 2026-09-17 when the plugin's own package began registering the
  server, so every project gets the tools through the plugin; a project-level
  copy now registers the server twice.
