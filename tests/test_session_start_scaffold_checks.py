#!/usr/bin/env python3
"""session_start.py's opening reports an ignore line setup would have written
and an address book in neither shape the send script reads — report only.

Run: py tests/test_session_start_scaffold_checks.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

[temp-folder-not-gitignored-in-existing-project]: a consumer's temp/ arrived
by a fallback write and no ignore line covered it, and the opening read
folders and documents, never ignore lines. [address-book-format-unstated]:
two projects wrote bullet-list books the send script could not read, and
nothing said so before the send.
"""

import importlib.util
import os
import shutil
import sys
import tempfile

for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "plugin", "throughliner", "hooks", "session_start.py")

_spec = importlib.util.spec_from_file_location("session_start", HOOK)
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)

failures = []


def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + ("" if ok else f" — {detail}"))
    if not ok:
        failures.append(label)


def write(d, rel, text):
    path = os.path.join(d, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


print("test_session_start_scaffold_checks")

d = tempfile.mkdtemp(prefix="scaffold-checks-")
os.makedirs(os.path.join(d, "temp"))
write(d, ".gitignore", "INBOX/\n.throughliner/\n")
check("temp/ present with no ignore line is reported",
      hook._missing_ignore_lines(d) == ["temp/"], repr(hook._missing_ignore_lines(d)))
write(d, ".gitignore", "INBOX/\n.throughliner/\ntemp/\n")
check("with the line present nothing is reported",
      hook._missing_ignore_lines(d) == [], repr(hook._missing_ignore_lines(d)))
os.remove(os.path.join(d, ".gitignore"))
check("no .gitignore at all reads as nothing to report",
      hook._missing_ignore_lines(d) == [])
shutil.rmtree(d, ignore_errors=True)

d = tempfile.mkdtemp(prefix="scaffold-checks-")
write(d, "INBOX/.address-book.md", "# Address book\n\nOther Project: C:/x\n")
check("a book in neither shape is reported", hook._address_book_unreadable(d))
write(d, "INBOX/.address-book.md", "# Address book\n\n- Other Project — `C:/x`\n")
check("a bullet book is readable", not hook._address_book_unreadable(d))
write(d, "INBOX/.address-book.md", "| Correspondent | Folder |\n| --- | --- |\n| Other | `C:/x` |\n")
check("a table book is readable", not hook._address_book_unreadable(d))
write(d, "INBOX/.address-book.md", "# Address book\n\n")
check("an empty book is not reported", not hook._address_book_unreadable(d))
shutil.rmtree(d, ignore_errors=True)

print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)
