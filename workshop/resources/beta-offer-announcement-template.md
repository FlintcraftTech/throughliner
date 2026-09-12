# Beta offer announcement — template

Cycle material for `[weekly-release]` (see `CYCLES.md`, step 6). Filled in and
posted on the Wednesday turn, and read by `[beta-launch-announcement]` for the
first one.

**How to use it.** Fill every `<...>` from the turn itself — the Release checklist
knows the version, the rezip archive entry knows the commit, and the week's LOG
entries say what changed. Delete the launch paragraph after the first post. Show
the filled text to the user in full and post only on their explicit yes; write
the `INBOX/sent.md` line in the same turn, naming the channel.

**Limit: 2,000 characters**, which is Discord's. Check the filled text, not this
file — the template is under the limit with room for three change lines.

---

**Throughliner `<version>` is on the beta channel.**

<Launch paragraph — first post only: Throughliner now has a beta channel. Each
Wednesday one tested build gets picked, and that's what the beta channel serves.
It's honestly early — I'm the main person running it so far, and I'd rather say
that than dress it up. If you're up for using it and telling me what breaks,
you're exactly who this is for.>

What's new this week:

- <one line, what changes for you, in plain words>
- <one line>
- <one line>

To install or update, open a chat in Claude Code and ask it to add the
marketplace `FlintcraftTech/throughliner#beta` and install
`throughliner@flintcraft` — Claude runs the commands, you never touch a
terminal. If you already have it, just ask Claude to update the plugin. Either
way, fully restart Claude Code afterwards, because plugins load at launch.

Beta means this build has had a week of real use before reaching you, not that
it's finished. Things will still be rough. If something goes wrong, say so here
or ask Claude to report it — it knows where to send it.
