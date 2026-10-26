---
title: GitHub wiki written and published for 0.1.1
kind: note
date: 2026-10-24
verified: 2026-10-24
stale_after: 2027-04-24
tags: [wiki, docs, 0.1.1, github]
summary: "the wiki's pages, where their git working copy is, how every example was verified against the 0.1.1 release zip, the facts found on the way, the inaccuracies in the shipped docs, and how to update the wiki; read before touching the wiki or the README sentences listed under inaccuracies"
---

# GitHub wiki for 0.1.1

## Summary

The owner asked for the wiki and a tag on 2026-10-24 ("do the wiki now and tag"). 0.1.1 was released first (README link to the wiki, version strings; no behaviour change), and the wiki was written against its release zip with the wikiwright skill: ten pages plus sidebar and footer, from the README, schema.md, ask.py, the tests, CI and the release workflow. Every output on the pages was printed by the verification program beside this note. Wiki commit `6dcb942`; `live`: 10 pages, 0 failures, sidebar and footer render, 13 anchor links to 4 pages, 0 broken. Prose checker: 0 strong findings.

Pages: Home, Getting-Started, Commands, Question-Set-Format, Lint-Rules-and-Errors, Server-and-Security, Recipes, Versions-and-Upgrading, FAQ, Development, `_Sidebar`, `_Footer`.

The repository is a command-line tool shipped as a skill, with no package registry. The page set was the command-line tool set (Commands, plus the library set's behaviour page, edge cases and errors) with one extra page for the server, since the HTTP surface is half of what the tool does. The "published package" was the GitHub release zip.

## Where the pages are

`../askwright.wiki` (a sibling of this clone, outside this repository), branch `master`, remote `origin` = `https://github.com/m4bwav/askwright.wiki.git`. Plain markdown links between pages, no wikilinks, LF line endings.

## How it was published

Preflight state `no-wiki-repo`; the owner saved the first page in the web UI while the pages were written; preflight then said `placeholder`; the pages were committed over it and pushed with a plain `git push` (no force). `live`: 10 pages, 0 failures.

## Updating the wiki later

1. `git -C ../askwright.wiki pull --ff-only`, then edit the pages.
2. Re-verify: download and unzip the new release zip into a scratch folder, then run `python 2026-10-24-wiki-verify.py <unzipped>/skills/askwright/scripts/ask.py > new.txt` on Linux (the pages show that run; WSL works), and on Windows with the newest Python and with 3.9. `python <wikiwright>/scripts/wikiwright.py diffout 2026-10-24-wiki-verify.out.txt new.txt` lists every changed section; every difference is a page to fix. Linux and Windows differ only in relative paths inside error messages (`new` on an existing set, `lint` on a missing folder); 3.9 and 3.14 differ only in the version line. `diffout ... --save 2026-10-24-wiki-verify.out.txt` saves the Linux output over the old one.
3. `wikiwright.py outputs ../askwright.wiki 2026-10-24-wiki-verify.out.txt --address ''`, `wikiwright.py snippets ../askwright.wiki 2026-10-24-wiki-verify.py`, `wikiwright.py check ../askwright.wiki --version <new>`, and the everwrite checker.
4. Commit, `git push`, then `wikiwright.py live m4bwav/askwright ../askwright.wiki`. The pages that name the version: `_Footer` (version, date, download link), Home (the run line and "The current version"), Getting-Started (the zip name and size, `--version` output), Versions-and-Upgrading (a new row and section).

## How the examples were verified

[2026-10-24-wiki-verify.py](2026-10-24-wiki-verify.py) builds every set in a fresh temporary folder, runs the unzipped 0.1.1 `ask.py` as a child process and prints transcripts with exit codes. It talks to the served page's API with the token from `server.json`, posting what the page posts, and stops each server with `ask.py stop`. Times, PIDs, ports and the scratch path are masked. Saved output: [2026-10-24-wiki-verify.out.txt](2026-10-24-wiki-verify.out.txt) (the Linux run).

Runs: Linux (Ubuntu under WSL, Python 3.14.4), Windows (Python 3.14.6 and CPython 3.9.25). macOS was not run (CI covers it). `ffprobe` was not installed, so every media case passed `--no-probe` and the codec warning is described from the source. Not run: the plugin install and uninstall, the clone-and-link route, the foreground `serve`, a 416 Range reply, two servers at once. Each is marked on its page.

`outputs`: 10 pages, 75 outputs checked, 0 missing, 1 skipped (the usage synopsis). `snippets`: 1 block checked, 3 skipped (install links and Claude Code slash commands), 4 commands. The repository's tests on Windows 3.14: `check_skills.py` 0 problems, `test_ask.py` 48 tests OK (1 skipped).

## Facts verified while writing (not in the README)

- A stale answer (given to an older `rev`) is listed under both `answered` and `stale` in `status`.
- `read` returns answers to superseded and withdrawn questions, with that `status`.
- `ask.py add` writes an "added" mark, so `done` turns false after "All done" when a round is added.
- `status --wait-done` exits 0 when it times out; test `timed_out`.
- `inline` cuts the AskUserQuestion `header` to 12 characters mid-word ("Credits musi") and prints the guess only when its confidence is `high`.
- `media_roots` resolve against the set folder, not the working folder.
- A `.vtt` beside a video is served as its captions without being named in the set.
- Error messages echo the path as given, with the platform's separator.
- A question id starting with `_` fails (`id`), as do ids over 64 characters.
- Limits: 10 MB per upload, 1 MB JSON bodies, 20 attachments, 50 timecodes and 20,000 characters of note per answer.

## Inaccuracies found in the shipped docs

1. README "ask.py": "Every command prints one JSON object." `--version` prints plain text, and a usage mistake prints argparse text on standard error with exit code 2 (wiki-verify `version` and `load-errors` sections). Fixed before the 0.2.0 tag (C-20261025-7).
2. README "Security": "Every API call needs a per-run token from the page and a matching Host header and Origin." The Origin is checked only on POST, and a POST without an Origin header is accepted (ask.py `origin_ok`, `do_GET`). Fixed before the 0.2.0 tag (C-20261025-7).
3. CHANGELOG release notes for 0.1.0: "Windows and macOS". CI also runs Linux, and the wiki's Linux run passed. Historical; leave or amend at the next release.
4. schema.md "What comes back" lists the states `answered`, `unsure`, `note_only`; `read --all` also returns `unanswered` (wiki-verify `add` section). Fixed before the 0.2.0 tag (C-20261025-7).

## Gotchas

- A Python program holding a page snippet in a triple-quoted string must start the snippet on its own line (`RECIPE = '''` then a newline): `snippets` compares whole lines, so a first line glued to the assignment is not found.
- `pathlib.Path.write_text(newline=...)` exists only from Python 3.10; the program writes with `open(..., newline="\n")` so it runs on 3.9.
- `tests/check_skills.py` refuses anything that looks like a home folder (`/home/<name>/`) or a drive path, so the scratch mask is `/work/proj`, and the program's timestamp regex is written with `[0-9]`: a digit escape after a colon reads as a drive letter to the guard.
- An output block that is part of a longer output line (one message inside a JSON line) fails `outputs`; quote it in prose instead.

Related: see also [../HANDOFF.md](../HANDOFF.md), [../log.md](../log.md).

## 0.2.0 update (2026-10-25)

Written on the owner's go ("yes" to tagging 0.2.0 and the wiki). Wiki commit `b7d5801`; `live`: 12 pages, 0 failures, sidebar and footer render, 24 anchor links to 7 pages, 0 broken. `check` 0 errors; `outputs` 119 checked, 0 missing, 1 skipped; `snippets` 0 missing; prose checker 0 strong.

- New pages: Study-Mode, Figures. Three SVG files in the wiki root (`figure-graph.svg`, `figure-forces.svg`, `figure-shapes.svg`), written by the program's `figure` section when it is given a second argument (a folder); each answered 200 `image/svg+xml` and renders on the Figures page.
- Changed: Home, Getting-Started (zip `askwright-0.2.0.zip`, 61,076 bytes), Commands (eleven commands; grade, figure, `read --attempt`, the status study block, the inline study reason), Question-Set-Format (`mode`, a Study sets section, figure media), Lint-Rules-and-Errors (Rules for study sets, `study-fields`, the relaxations), Server-and-Security (submit, retake, the key stripped before submit), Versions-and-Upgrading, FAQ, Development (67 tests), `_Sidebar`, `_Footer`.
- Program: [2026-10-25-wiki-verify.py](2026-10-25-wiki-verify.py), the 0.1.1 program plus `add-wrapper`, the study sections and the figure sections; saved output [2026-10-25-wiki-verify.out.txt](2026-10-25-wiki-verify.out.txt) (Linux, Python 3.14.4 under WSL). The 2026-10-24 files stay as the 0.1.1 record. Next release: run the 2026-10-25 program and diff against its output.
- Runs: Linux 3.14.4, Windows 3.14.6 and CPython 3.9.25 (from `uv python find 3.9`). Every 0.1.1 section printed the same on 0.2.0 apart from the version line. Expected differences: Windows paths in two error messages, and `study-page-sees`, whose option order is reshuffled every attempt (pass `--skip study-page-sees` to `diffout`, or accept the change).
- The 0.1.1 claim in Versions that `add` refused a `{"questions": [...]}` file was run against the 0.1.1 zip (seven lint errors, "lint failed; nothing was added").
- Not run: the page in a browser (the repository's page tests cover it; the program posts what the page posts), macOS, the plugin install.

Facts found while writing (not in the README):
- A submit counts as done: `status` says `"done": true` and `last_mark` is the submit, so `--wait-done` returns on submit.
- `grade --apply` refuses the whole file when one entry is bad (points over the maximum, a multiple-choice id, a blank answer).
- A retake empties `answers.json`; `results.json` keeps every attempt. A retake before submit, and an answer or submit after it, are 409.
- A forces figure labels an arrow with its newtons ("50 N") when it has no `label`.
- `inline` refuses every study set; `grade` on a decision set exits 1.

Inaccuracy found in the shipped docs (for the next release):
5. schema.md "Media items" and study-mode.md: forces arrows are "scaled to `newtons`", but each axis has its own room (`_forces` in ask.py), so a 30 N sideways arrow is drawn about as long as a 50 N upright one. Either scale both axes to one length per newton or say that lengths compare along one axis only. This is also the "force diagrams use space poorly" follow-up. The wiki's Figures page says it.

## Owed for 0.2.0 (study mode and figures): done 2026-10-25, see above


Not written yet; do them with the 0.2.0 tag, on the owner's go, with every example run against the release zip.
- A new page "Study mode": a whole small quiz set, the review it produces, `read` output for a study set, `grade` and `grade --apply` with real output, retakes and results.json.
- A new page or section "Figures": one example each of graph, forces and shapes with the rendered SVG, and `ask.py figure`.
- Question-set format page: `mode`, the study fields (topic, correct, option why, points, bonus, shuffle, rubric, model_answer) and `figure` media.
- Lint rules page: mode, study-kind, study-correct, study-why, study-rubric, points, topic, study-few-options, study-longest-right, study-fields, figure; the study relaxations of question-mark and option-label (L-016).
- Commands page: `grade`, `figure`, `read --attempt`; `status` `study` block; `inline` refusing study sets.
- Security page: the key and real option ids never reach the browser before submit (L-015).
