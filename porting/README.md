# Porting Throughliner

This folder holds what a porter reads: someone running the method on a tool other than Claude Code.

## Two flavours

A **tracking** port follows this project closely and carries as many of its features as the other tool allows. An **independent** port is its own thing, adopting only the changes it wants. Both are supported. A port declares its own flavour and re-declares if it changes how it works. The flavours are described in [plugin/throughliner/docs/ports.md](../plugin/throughliner/docs/ports.md).

## What is here

- [PORT-CHANGELOG.md](PORT-CHANGELOG.md) — the changelog written for ports, produced per release: what changed inside which shipped file and why, marking a format change that would migrate a port's users' documents. It says what changed and never how to map it. Its own opening states the three limits it works under.
- [porter-prompt.md](porter-prompt.md) — a paste-ready prompt for a tester porting the plugin into their own harness with Claude's help.
