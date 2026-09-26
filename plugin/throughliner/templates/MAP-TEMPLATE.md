# MAP

This file is for Claude to read, not a person: it says what this project's folders and human-used files are for, so a folder a session never opened is still in view when something belongs there. A line is earned by every folder, and by every file a person uses — a markdown document, a PDF, a slide deck, a spreadsheet, an image someone looks at, a calendar file; the list is a specimen, so a new kind of file gets the question rather than the list. Machinery earns no line: scripts, modules, configuration, anything wired to other files describes itself by how it is used. Where many like files form a set, the set gets one line, not each file. A line for a human-used file carries who uses it and when — its audience and its use time — and a folder's line says which repository holds it where the project has two. The map puts a folder in view; it does not decide what belongs there.

Written by setup from the tree it adopted; a session that creates a folder or a human-used file writes its line in the same turn; the close names every new or moved path with no line.

<!-- Line shapes, one per line, in the order the tree reads:
     - <path>/ — what it holds, in one or two lines — <which repository, where there are two>
     - <path> — what the file is — who uses it, and when
     - <folder>/<pattern> (N files) — what the set is — who uses it, and when
     - a folder's line as above, and beneath it, indented one level, each
       human-used file or set by its own name only, carrying the same facts a
       full-path line carries — so a path is written once and the files sit
       under their folder; the flat forms above stay allowed
     e.g.:
     - programme/ — the workshop programme, one folder per day — outer repository
       - day-1/handout.md — the participants' handout for day one — read by participants on the day
       - day-1/*.png (6 files) — the slides' images, in slide order — shown by the facilitator during the session -->
