#!/usr/bin/env python3
"""Tests for site/build_faq_site.py, the FAQ website generator.

Host-only dev artifact — not shipped in the plugin package.

Run:  py tests/test_build_faq_site.py
(Plain script, never pytest — see CLAUDE.md's scripting constraints.)

Why this exists ([discord-posts-as-a-searchable-web]): the plugin's FAQ is
published as a small website on GitHub Pages, regenerated at each release. A
two-question fixture must produce an index and two pages, every page must
carry both sponsor links, and a question removed from the FAQ must lose its
page at the next run while a file the generator did not write is left alone.
"""

import json
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
SCRIPT = os.path.join(ROOT, "site", "build_faq_site.py")
KOFI = "https://ko-fi.com/itscoughfee"
SPONSORS = "https://github.com/sponsors/its-coughfee"

failures = []


def check(name, condition, detail=""):
    if condition:
        print("  ok   " + name)
    else:
        print("  FAIL " + name + ("\n       " + detail if detail else ""))
        failures.append(name)


FAQ_TWO = """# FAQ

The template's own note, which is not a question.

## How do I plant a tree?

Dig a hole with `spade --deep`, then **water it** — every day.

- **First** — pick a spot that
  gets sun.
- Second, see [the guide](https://example.invalid/guide).

```
plant --tree <oak>
```

## What is a <script> tag doing here?

Nothing: it is escaped, like `a < b`.
"""

FAQ_ONE = FAQ_TWO.split("## What is a <script>")[0]

INDEX = """# FAQ Index

- **How do I plant a tree?** — the hole, the water, and
  the sun. [faq.md](faq.md)
- **What is a <script> tag doing here?** — escaping. [faq.md](faq.md)
"""


def fixture(faq):
    d = tempfile.mkdtemp(prefix="faq-site-")
    with open(os.path.join(d, "faq.md"), "w", encoding="utf-8") as f:
        f.write(faq)
    with open(os.path.join(d, "index.md"), "w", encoding="utf-8") as f:
        f.write(INDEX)
    with open(os.path.join(d, "plugin.json"), "w", encoding="utf-8") as f:
        json.dump({"name": "throughliner", "version": "9.8.7"}, f)
    return d


def run(d):
    return subprocess.run(
        [sys.executable, SCRIPT, "--faq", os.path.join(d, "faq.md"),
         "--index", os.path.join(d, "index.md"),
         "--manifest", os.path.join(d, "plugin.json"),
         "--out", os.path.join(d, "out")],
        capture_output=True, text=True, encoding="utf-8", timeout=60)


def out(d, name):
    with open(os.path.join(d, "out", name), "r", encoding="utf-8") as f:
        return f.read()


# 1. Two questions produce an index and two pages, a stylesheet and .nojekyll.
d = fixture(FAQ_TWO)
proc = run(d)
check("the generator exits clean", proc.returncode == 0, proc.stdout + proc.stderr)
names = sorted(os.listdir(os.path.join(d, "out")))
tree, script = "how-do-i-plant-a-tree.html", "what-is-a-script-tag-doing-here.html"
check("an index, two question pages, a stylesheet and .nojekyll are written",
      names == sorted([".nojekyll", "index.html", "style.css", tree, script]),
      repr(names))
check(".nojekyll is empty", out(d, ".nojekyll") == "")

# 2. Every page carries both footer links and the version it was built from.
for name in ("index.html", tree, script):
    text = out(d, name)
    check("%s carries the Ko-fi and GitHub Sponsors links" % name,
          KOFI in text and SPONSORS in text and "Throughliner is free." in text,
          text[-600:])
    check("%s names the plugin version it was generated from" % name,
          "Generated from Throughliner 9.8.7" in text, text[-600:])

# 3. The index lists each question with its summary, linked, and embeds the
#    questions and answers for the in-page search with no outside script.
index = out(d, "index.html")
check("the index links each question to its page",
      'href="%s"' % tree in index and 'href="%s"' % script in index, index)
check("the index carries each question's summary from the index file",
      "the hole, the water, and the sun." in index and "[faq.md]" not in index,
      index)
check("the index has a search box and embeds the answers as data",
      'id="search"' in index and 'id="faq-data"' in index
      and "dig a hole" in index, index)
check("no page loads a script or stylesheet from outside",
      "src=" not in index and "http" not in index.split("<footer>")[0]
      .replace("https://github.com/FlintcraftTech/throughliner", ""), index)

# 4. Markdown is converted: inline code, bold, a list with a wrapped line, a
#    link, a fenced block; and angle brackets are escaped everywhere.
page = out(d, tree)
check("inline code and bold are converted",
      "<code>spade --deep</code>" in page and "<strong>water it</strong>" in page,
      page)
check("a list item's wrapped line joins its item",
      "<li><strong>First</strong> — pick a spot that gets sun.</li>" in page, page)
check("a link is converted",
      '<a href="https://example.invalid/guide">the guide</a>' in page, page)
check("a fenced block is kept as written, escaped",
      "<pre><code>plant --tree &lt;oak&gt;</code></pre>" in page, page)
page2 = out(d, script)
check("angle brackets in a question and in code are escaped",
      "<script> tag" not in page2 and "&lt;script&gt; tag" in page2
      and "<code>a &lt; b</code>" in page2, page2)
check("the template's opening note is not on any page",
      "which is not a question" not in index + page + page2)

# 5. A second run after a question is removed deletes its page, and leaves a
#    file the generator did not write.
with open(os.path.join(d, "out", "mine.html"), "w", encoding="utf-8") as f:
    f.write("<html>a page someone else put here</html>")
with open(os.path.join(d, "faq.md"), "w", encoding="utf-8") as f:
    f.write(FAQ_ONE)
proc = run(d)
names = sorted(os.listdir(os.path.join(d, "out")))
check("the removed question's page is deleted on the next run",
      proc.returncode == 0 and script not in names and tree in names,
      repr(names) + proc.stdout + proc.stderr)
check("the run says which page it removed", script in proc.stdout, proc.stdout)
check("a page the generator did not write is left alone", "mine.html" in names,
      repr(names))
check("the index no longer lists the removed question",
      script not in out(d, "index.html"))
shutil.rmtree(d, ignore_errors=True)

print()
if failures:
    print("%d failure(s):" % len(failures))
    for name in failures:
        print("  " + name)
    sys.exit(1)
print("all cases passed")
