#!/usr/bin/env python3
"""Build the FAQ website from the FAQ the plugin ships.

Run:  py site/build_faq_site.py            (from the repository root)
      py site/build_faq_site.py --faq <faq.md> --index <faq-index.md>
                                --manifest <plugin.json> --out <folder>

Reads `plugin/throughliner/templates/faq-template.md` for the answers and
`faq-index-template.md` for each question's one-line summary, and writes a
small static site into `docs/`, which GitHub Pages serves from the default
branch: `index.html` with every question and a search box, one page per
question, one stylesheet and an empty `.nojekyll`. A run deletes the pages of
questions that no longer exist; it deletes only pages this script wrote.

Standard library only. The search runs in the page over the questions and
answers embedded in it: no outside service and no outside script.
"""

import html
import json
import os
import re
import sys

# The block reorder_queue.py carries: Windows consoles default to a legacy
# codepage, and the FAQ's text is not ASCII.
for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
TEMPLATES = os.path.join(REPO, "plugin", "throughliner", "templates")
DEFAULTS = {
    "--faq": os.path.join(TEMPLATES, "faq-template.md"),
    "--index": os.path.join(TEMPLATES, "faq-index-template.md"),
    "--manifest": os.path.join(REPO, "plugin", "throughliner",
                               ".claude-plugin", "plugin.json"),
    "--out": os.path.join(REPO, "docs"),
}
USAGE = ("usage: build_faq_site.py [--faq <file>] [--index <file>] "
         "[--manifest <file>] [--out <folder>]")

SITE_TITLE = "Throughliner FAQ"
KOFI = "https://ko-fi.com/itscoughfee"
SPONSORS = "https://github.com/sponsors/its-coughfee"
REPO_URL = "https://github.com/FlintcraftTech/throughliner"
# Written into every page this script generates, and the only pages a run
# will delete: a file someone else put in the folder is never removed.
GENERATOR_MARK = '<meta name="generator" content="throughliner build_faq_site">'

STYLESHEET = """:root {
  --bg: #fbfaf7; --text: #1f2328; --muted: #5c6470; --line: #e3e0d8;
  --accent: #7a4a1e; --code-bg: #f1eee6; --card: #ffffff;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #17181a; --text: #e6e3dc; --muted: #9aa0a8; --line: #2e3034;
    --accent: #e0a56b; --code-bg: #232528; --card: #1e2022;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--text);
  font: 17px/1.6 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}
main { max-width: 44rem; margin: 0 auto; padding: 2rem 1rem 3rem; }
h1 { font-size: 1.7rem; line-height: 1.25; margin: 0 0 1rem; }
h2, h3 { line-height: 1.3; margin: 1.6rem 0 0.5rem; }
a { color: var(--accent); }
p { margin: 0 0 1rem; }
code {
  background: var(--code-bg); padding: 0.1em 0.3em; border-radius: 4px;
  font: 0.9em ui-monospace, Consolas, monospace; overflow-wrap: anywhere;
}
pre {
  background: var(--code-bg); padding: 0.8rem 1rem; border-radius: 6px;
  overflow-x: auto;
}
pre code { background: none; padding: 0; }
ul, ol { padding-left: 1.3rem; margin: 0 0 1rem; }
li { margin-bottom: 0.4rem; }
.lead { color: var(--muted); margin-bottom: 1.5rem; }
.back { display: inline-block; margin-bottom: 1.2rem; font-size: 0.95rem; }
#search {
  width: 100%; font: inherit; padding: 0.65rem 0.8rem; margin-bottom: 0.4rem;
  color: var(--text); background: var(--card);
  border: 1px solid var(--line); border-radius: 8px;
}
#count { color: var(--muted); font-size: 0.9rem; min-height: 1.4rem; margin-bottom: 0.8rem; }
#questions { list-style: none; padding: 0; margin: 0; }
#questions li { border-top: 1px solid var(--line); padding: 0.8rem 0; margin: 0; }
#questions a { font-weight: 600; text-decoration: none; }
#questions a:hover { text-decoration: underline; }
#questions .blurb { display: block; color: var(--muted); font-size: 0.95rem; }
footer {
  max-width: 44rem; margin: 0 auto; padding: 1rem 1rem 2.5rem;
  border-top: 1px solid var(--line); color: var(--muted); font-size: 0.9rem;
}
"""

SEARCH_SCRIPT = """
(function () {
  var data = JSON.parse(document.getElementById('faq-data').textContent);
  var box = document.getElementById('search');
  var count = document.getElementById('count');
  var items = document.querySelectorAll('#questions li');
  function filter() {
    var words = box.value.toLowerCase().split(/\\s+/).filter(Boolean);
    var shown = 0;
    for (var i = 0; i < items.length; i++) {
      var text = data[i].text;
      var hit = words.every(function (w) { return text.indexOf(w) !== -1; });
      items[i].hidden = !hit;
      if (hit) { shown++; }
    }
    count.textContent = words.length
      ? shown + ' of ' + items.length + ' questions match'
      : items.length + ' questions';
  }
  box.addEventListener('input', filter);
  filter();
})();
"""


def fail(message):
    sys.stderr.write("build_faq_site: " + message + "\n")
    sys.exit(1)


def read(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError) as exc:
        fail("cannot read %s: %s" % (path, exc))


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


# --- reading the two FAQ files ------------------------------------------------

def parse_faq(text):
    """[(question, answer markdown)] from the `## ` headings, in file order.
    Whatever sits before the first question is the template's own note and
    is left out."""
    entries = []
    question, body, in_fence = None, [], False
    for line in text.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
        if not in_fence and line.startswith("## "):
            if question is not None:
                entries.append((question, "\n".join(body).strip()))
            question, body = line[3:].strip(), []
        elif question is not None:
            body.append(line)
    if question is not None:
        entries.append((question, "\n".join(body).strip()))
    return entries


INDEX_ITEM_RE = re.compile(r"^- \*\*(?P<q>.+?)\*\*\s*(?:—|–|-)\s*(?P<blurb>.*)$",
                           re.DOTALL)
INDEX_LINK_RE = re.compile(r"\s*\[faq\.md\]\(faq\.md\)\s*$")


def parse_index(text):
    """{question: one-line summary} from the index's bullets. A bullet may
    wrap onto indented lines, and the question itself may wrap."""
    blurbs, current = {}, None

    def close(chunk):
        match = INDEX_ITEM_RE.match(" ".join(chunk.split()))
        if match:
            blurbs[match.group("q").strip()] = INDEX_LINK_RE.sub(
                "", match.group("blurb")).strip()

    for line in text.splitlines():
        if line.startswith("- "):
            if current is not None:
                close(current)
            current = line
        elif current is not None and line.strip():
            current += " " + line.strip()
        elif current is not None:
            close(current)
            current = None
    if current is not None:
        close(current)
    return blurbs


def slug_for(question, taken):
    """A file name from the question: lower-case words joined by hyphens."""
    base = re.sub(r"[^a-z0-9]+", "-", question.lower()).strip("-")[:80].strip("-")
    base = base or "question"
    slug, n = base, 2
    while slug in taken or slug == "index":
        slug = "%s-%d" % (base, n)
        n += 1
    taken.add(slug)
    return slug


# --- Markdown, for what the FAQ uses ------------------------------------------

CODE_SPAN_RE = re.compile(r"`([^`]+)`")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITALIC_RE = re.compile(r"(?<![*\w])\*([^*\s][^*]*?)\*(?![*\w])")
SAFE_URL_RE = re.compile(r"^(https?://|mailto:|#|[\w./-]+$)")


def inline(text):
    """Inline Markdown to HTML: code spans, links, bold, emphasis."""
    spans = []

    def stash(match):
        spans.append("<code>%s</code>" % html.escape(match.group(1), quote=False))
        return "\x00%d\x00" % (len(spans) - 1)

    text = CODE_SPAN_RE.sub(stash, text)
    text = html.escape(text, quote=False)

    def link(match):
        url = html.unescape(match.group(2))
        if not SAFE_URL_RE.match(url):
            return match.group(0)
        return '<a href="%s">%s</a>' % (html.escape(url, quote=True),
                                        match.group(1))

    text = LINK_RE.sub(link, text)
    text = BOLD_RE.sub(r"<strong>\1</strong>", text)
    text = ITALIC_RE.sub(r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: spans[int(m.group(1))], text)


LIST_ITEM_RE = re.compile(r"^(?P<mark>-|\*|\d+[.)])\s+(?P<text>.*)$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def to_html(markdown):
    """Block Markdown to HTML: headings, paragraphs, bullet and numbered
    lists with wrapped lines, and fenced blocks."""
    out, paragraph, items, list_tag = [], [], [], None
    fence = None

    def flush_paragraph():
        if paragraph:
            out.append("<p>%s</p>" % inline(" ".join(paragraph)))
            del paragraph[:]

    def flush_list():
        if items:
            out.append("<%s>" % list_tag)
            out.extend("<li>%s</li>" % inline(item) for item in items)
            out.append("</%s>" % list_tag)
            del items[:]

    for line in markdown.splitlines():
        if fence is not None:
            if line.startswith("```"):
                out.append("<pre><code>%s</code></pre>"
                           % html.escape("\n".join(fence), quote=False))
                fence = None
            else:
                fence.append(line)
            continue
        if line.startswith("```"):
            flush_paragraph()
            flush_list()
            fence = []
            continue
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            flush_list()
            continue
        heading = HEADING_RE.match(stripped)
        if heading:
            flush_paragraph()
            flush_list()
            # A heading inside an answer sits below the page's own h1.
            level = min(6, len(heading.group(1)) + 1)
            out.append("<h%d>%s</h%d>" % (level, inline(heading.group(2)), level))
            continue
        item = LIST_ITEM_RE.match(stripped)
        if item and not (paragraph and not line.startswith(("-", "*"))
                         and not item.group("mark")[0].isdigit()):
            flush_paragraph()
            tag = "ol" if item.group("mark")[0].isdigit() else "ul"
            if items and tag != list_tag:
                flush_list()
            list_tag = tag
            items.append(item.group("text"))
            continue
        if items and line.startswith((" ", "\t")):
            items[-1] += " " + stripped     # a list item's wrapped line
            continue
        flush_list()
        paragraph.append(stripped)
    if fence is not None:
        out.append("<pre><code>%s</code></pre>"
                   % html.escape("\n".join(fence), quote=False))
    flush_paragraph()
    flush_list()
    return "\n".join(out)


def plain(markdown):
    """The answer as plain lower-case text, for the in-page search."""
    text = re.sub(r"[`*#]", "", markdown)
    text = LINK_RE.sub(r"\1", text)
    return " ".join(text.split()).lower()


# --- pages ---------------------------------------------------------------------

def footer(version):
    made = (" Generated from Throughliner %s." % html.escape(version)
            if version else "")
    return ('<footer>Throughliner is free. If it helps you: '
            '<a href="%s">Ko-fi</a> · <a href="%s">GitHub Sponsors</a>.%s</footer>'
            % (KOFI, SPONSORS, made))


def page(title, body, version, extra=""):
    return ("<!doctype html>\n<html lang=\"en\">\n<head>\n"
            "<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            + GENERATOR_MARK + "\n"
            "<title>%s</title>\n"
            "<link rel=\"stylesheet\" href=\"style.css\">\n"
            "</head>\n<body>\n<main>\n%s\n</main>\n%s\n%s</body>\n</html>\n"
            % (html.escape(title, quote=False), body, footer(version), extra))


def build(faq_path, index_path, manifest_path, out_dir):
    entries = parse_faq(read(faq_path))
    if not entries:
        fail("no `## ` question found in %s" % faq_path)
    blurbs = parse_index(read(index_path))
    version = ""
    try:
        version = str(json.loads(read(manifest_path)).get("version") or "")
    except ValueError:
        pass

    os.makedirs(out_dir, exist_ok=True)
    taken, pages, data, rows = set(), {}, [], []
    for question, answer in entries:
        name = slug_for(question, taken) + ".html"
        body = ('<a class="back" href="index.html">← All questions</a>\n'
                "<h1>%s</h1>\n%s" % (inline(question), to_html(answer)))
        pages[name] = page("%s — %s" % (question, SITE_TITLE), body, version)
        blurb = blurbs.get(question, "")
        rows.append('<li><a href="%s">%s</a>%s</li>' % (
            name, inline(question),
            '<span class="blurb">%s</span>' % inline(blurb) if blurb else ""))
        data.append({"text": (question + " " + blurb + " " + plain(answer)).lower()})

    # `</` inside the embedded JSON would end the script element early.
    embedded = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    index_body = (
        "<h1>%s</h1>\n"
        '<p class="lead">How Throughliner works, one question at a time. '
        'Throughliner is a Claude Code plugin for no-code developers: '
        '<a href="%s">the plugin on GitHub</a>.</p>\n'
        '<input id="search" type="search" placeholder="Search the questions '
        'and answers" aria-label="Search the questions and answers" autofocus>\n'
        '<div id="count" aria-live="polite"></div>\n'
        '<ul id="questions">\n%s\n</ul>'
        % (SITE_TITLE, REPO_URL, "\n".join(rows)))
    scripts = ('<script type="application/json" id="faq-data">%s</script>\n'
               "<script>%s</script>\n" % (embedded, SEARCH_SCRIPT))
    pages["index.html"] = page(SITE_TITLE, index_body, version, scripts)

    # Delete the pages of questions that no longer exist: only `.html` files
    # carrying this script's own mark.
    removed = []
    for name in sorted(os.listdir(out_dir)):
        if not name.endswith(".html") or name in pages:
            continue
        path = os.path.join(out_dir, name)
        try:
            with open(path, "r", encoding="utf-8") as f:
                mine = GENERATOR_MARK in f.read(2000)
        except (OSError, UnicodeDecodeError):
            mine = False
        if mine:
            os.remove(path)
            removed.append(name)

    for name, text in pages.items():
        write(os.path.join(out_dir, name), text)
    write(os.path.join(out_dir, "style.css"), STYLESHEET)
    write(os.path.join(out_dir, ".nojekyll"), "")
    return len(entries), removed, version


def main(argv):
    paths = dict(DEFAULTS)
    i = 0
    while i < len(argv):
        if argv[i] in paths and i + 1 < len(argv):
            paths[argv[i]] = os.path.abspath(argv[i + 1])
            i += 2
        else:
            fail(USAGE)
    count, removed, version = build(paths["--faq"], paths["--index"],
                                    paths["--manifest"], paths["--out"])
    print("build_faq_site: %d question page(s) and index.html written to %s%s%s"
          % (count, paths["--out"],
             ", from Throughliner %s" % version if version else "",
             "; removed %s" % ", ".join(removed) if removed else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
