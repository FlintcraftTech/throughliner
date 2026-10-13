# Ports — running Throughliner somewhere else

Throughliner is a Claude Code plugin, so it does not simply run elsewhere. What
it consists of is plain documents plus small scripts that fire at particular
moments in a session, and a port is somebody mapping those moments onto another
tool's. That mapping is judgement, and it stays with the porter.

**Both flavours below are welcome, and neither is the lesser one.** You should
have the opportunity to run a Throughliner led by this project and carrying all
its features so far as your setup allows — and diverging, renaming and
developing it yourself is equally fine.

## The two flavours

```
TRACKING       accepts this project's changes at face value, and adds no new
               ones of its own beyond what its own system required to fit.

INDEPENDENT    unique and its own thing, which may or may not accept changes
               derived from the changelogs.
```

**Say which one yours is, wherever you present it.** Without it nobody can tell
what a given port promises — including this project. Someone choosing between
ports cannot tell whether the one they install will follow the method or has
gone its own way; a porter has no way to signal it; and this project cannot tell
which ports its changelog is even for. The name makes the promise legible in
both directions.

**No register of who runs which flavour is kept.** Maintaining a list of other
people's projects is a standing obligation this project cannot keep accurate,
and being absent from such a list would read as disapproval. The flavour is
something a port declares about itself. It describes what the port does now,
not what it promises for later: a port that changes how it works simply
changes its declaration, with nobody to ask.

## Keeping up

A tracking port surveys the **port-facing changelog** published with each
release: what changed inside which shipped file, and why. Everything under the
plugin package ships; everything outside it is the development project's own, so
the changelog marks the host-only changes — a porter following the session
records blind would otherwise carry across work never meant to leave.

Three limits it states about itself:

```
it says WHAT changed, never how to map it   the translating stays yours
a change to a hook                          may have no equivalent on your side
a format-epoch bump                         your own users' documents need
                                            migrating; that is yours to handle
```
