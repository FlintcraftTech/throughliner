#!/usr/bin/env python3
"""The queue tool writes one derived checkbox line under every heading
([queue-entry-task-line-written-by-tools]).

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_reorder_queue_sync_lines.py

Four assertions: a new entry gets its line; a hold adds ⛔; a delete removes
the line with its entry; a [user] item's own task line is left as the item's
line with no second one written. Plus: the digest's held and cleared counts
are unchanged by the lines.
"""

import os
import shutil
import subprocess
import sys
import tempfile

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "plugin", "throughliner", "scripts")
TOOL = os.path.join(SCRIPTS, "reorder_queue.py")
DIGEST = os.path.join(SCRIPTS, "queue_digest.py")

failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        failures.append(name)


QUEUE = """# QUEUE

## Processed

#### Alpha — a cleared build [alpha]
Alpha's rationale.

--- Cleared to run above this line ---

#### Gamma — a held build [gamma]
Gamma's rationale.
Blocked by: [alpha], [beta]
Not before: 2026-12-01

#### [user] Phone the office [phone-office]
A step of yours.
- [ ] Phone the office (Demo) 📅 2026-11-02 🆔 phone-office

## Unprocessed

#### Beta — a capture [beta]
Beta's rationale.
"""


def run(args, cwd):
    proc = subprocess.run([sys.executable, TOOL] + args, cwd=cwd,
                          capture_output=True, encoding="utf-8",
                          errors="replace")
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


print("test_reorder_queue_sync_lines")
d = os.path.join(tempfile.mkdtemp(prefix="sync-lines-"), "Demo Project")
os.makedirs(d)
q = os.path.join(d, "QUEUE.md")
with open(q, "w", encoding="utf-8", newline="") as f:
    f.write(QUEUE)
with open(os.path.join(d, "SPEC.md"), "w", encoding="utf-8") as f:
    f.write("# SPEC\n")

code, out = run([q, "--sync-lines"], d)
text = read(q)
check("the sync pass runs", code == 0, out)
check("a cleared entry gets its line under the heading",
      "#### Alpha — a cleared build [alpha]\n"
      "- [ ] Alpha — a cleared build (Demo Project) 🆔 alpha\n"
      "Alpha's rationale.\n" in text, text)
check("a held entry's line carries ⛔ from Blocked by and 📅 from Not before",
      "- [ ] Gamma — a held build (Demo Project) 🆔 gamma ⛔ alpha,beta "
      "📅 2026-12-01\n" in text, text)
check("a [user] item's own task line is its line, with no second one",
      text.count("🆔 phone-office") == 1
      and "- [ ] Phone the office (Demo) 📅 2026-11-02 🆔 phone-office\n"
      in text, text)
check("a capture gets its line too",
      "- [ ] Beta — a capture (Demo Project) 🆔 beta\n" in text, text)

# A second pass changes nothing: the line is derived, not accumulated.
run([q, "--sync-lines"], d)
check("a second pass is idempotent", read(q) == text)

# A hold added by --replace-in rewrites the line with the new ⛔.
code, out = run([q, "--replace-in", "alpha", "--old", "Alpha's rationale.",
                 "--new", "Alpha's rationale.\nBlocked by: [beta]"], d)
text = read(q)
check("a hold added to an entry adds ⛔ to its line",
      "- [ ] Alpha — a cleared build (Demo Project) 🆔 alpha ⛔ beta\n" in text,
      out + text)

# A delete removes the line with its entry.
code, out = run([q, "--delete", "beta", "Unprocessed"], d)
text = read(q)
check("a deleted entry's line goes with it",
      "🆔 beta" not in text and "[beta]" in text, text)

# The digest's counts read the fields, not the lines.
proc = subprocess.run([sys.executable, DIGEST, q], cwd=d, capture_output=True,
                      encoding="utf-8", errors="replace")
check("the digest's cleared and held counts are unchanged",
      "1 cleared to run, 2 held below the line" in proc.stdout, proc.stdout[:400])
check("the digest counts no cite from the derived line",
      "Cited by" not in proc.stdout.split("[alpha]")[1].split("\n")[0],
      proc.stdout[:600])

shutil.rmtree(os.path.dirname(d), ignore_errors=True)
print()
if failures:
    print("%d failure(s): %s" % (len(failures), ", ".join(failures)))
    sys.exit(1)
print("all cases passed")
