# Retired terms

Mechanisms, settings and vocabulary this method has retired.

**What this file is for.** Retiring a mechanism automatically puts every rule
that still mentions it into question. This list is what makes that checkable: a
search for a retired term across your live rules reports references that should
have gone with it, so a stale reference produces a visible signal rather than
silence.

**It is source data, not derived state.** A retirement is an event, recorded once
at /done that retires it — which is why storing it does not contradict
computing everything else fresh.

**How a term gets added.** The session that retires something appends a line
here, in the same move as the gate disposition its record already carries. One
line per term:

```
- `<term>` — <what it was>, retired <YYYY-MM-DD>. Replaced by: <what, or "nothing">.
```

**What counts as a term.** Anything a rule could name: a mechanism, a marker
string, a field, a setting, a section heading, a piece of vocabulary. If a live
rule could plausibly still instruct a session to look for it, it belongs here.

**What does not.** A rule that was repealed without leaving a name behind. There
is nothing to search for, so nothing to record — its history lives in the session
record that repealed it.

## Retired

<!-- One line per term, newest last. Delete this comment when the first lands. -->
