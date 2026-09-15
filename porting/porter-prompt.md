# Porter prompt

A paste-ready prompt for a tester porting the plugin into their own harness with Claude's help. Paste the block below into a fresh session in the environment you are porting into. It was first handed over on 2026-08-27 and is re-checked against the installed plugin whenever it is copied here.

```
You're helping me port the Throughliner plugin into my own harness — my own environment, not the standard Claude Code desktop-app install. Please read the install guide at https://github.com/FlintcraftTech/throughliner/blob/main/INSTALL.md in full first: it explains what the plugin is, how a normal install behaves, and what a working install looks like. Confirm you've read it by opening with its verification line.

Then adapt rather than follow it literally — for this port:

1. SOURCE. I'm not installing from the marketplace or the beta branch. I'm using the most current test rezip: the newest entry in the Throughliner Discord's test-rezips channel. Use exactly the build that entry names, obtained however the entry provides it (its attached file, or the repository commit it points at) — read the entry's label and caveats first, and don't substitute the beta branch or the latest release.
2. WHAT TO PORT. The plugin is the `plugin/throughliner/` package: a plugin manifest (.claude-plugin/), four hooks (session_start, pre_tool_use, stop, post_tool_use — Python 3, standard library only), six skills (setup, plan, next, rescan, done, catchup), procedure docs under docs/, templates, helper scripts under scripts/, and a state server under mcp/ that is registered per project rather than by the package. Map each piece onto my harness's equivalents: wherever my environment fires session-start, pre-tool, post-tool and stop events, wire the matching hook there; expose the six skills however my harness surfaces commands.
3. KNOWN PORTABILITY POINTS. The hooks expect UTF-8 explicitly (don't rely on the platform default), run standalone (they can't import shared modules), and emit JSON in Claude Code's hook output shape — check what my harness expects and adapt the envelope, not the logic.
4. SMOKE TEST. Adapt the guide's smoke test: in a fresh empty folder, the setup command should be reachable, and starting a session should produce the plugin's session-start report. If the harness can't surface one of those, tell me plainly which half is unverified rather than calling it done.
5. HONESTY. This is a raw development build, not a soaked release: its label describes only what was seen at posting, and it can misbehave in a project's files. Keep my work in git before pointing the port at anything real. If something in the plugin itself looks broken, I'll report it as a GitHub issue on FlintcraftTech/throughliner rather than patching around it silently.

Work one step at a time and wait for me between steps.
```
