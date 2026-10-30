# 0.7.0: project label, continue prompt, listen bench and page cleanup

Owner request (2026-10-30): put the project on every page and session card with a button that copies a prompt to
continue the project and evaluate the answers; a dedicated area for comparing voices; and a cleaner page that makes
clear what each question asks and why. Calls made while building, each small enough to decide and flag:

- D1 `project` is a plain name or `{"name", "path"}`. A name alone covers most sets; the path is shown as a tooltip
  and in the default prompt, so an agent in a fresh session knows where to work.
- D2 The default continue prompt is built by ask.py, not the page, so it carries the absolute path of the very
  ask.py that served it and of the set folder. The page appends the counts at the moment of copying (answered, not
  sure, note only, not answered), computed from its own state after flushing unsaved answers, so the numbers are
  current without another server round trip. Study sets get no count line (attempts are the record there).
- D3 Clipboard: `navigator.clipboard.writeText` first (allowed on 127.0.0.1, a secure context), then a hidden
  textarea with `execCommand("copy")`. A toast confirms; failure says the browser blocked it.
- D4 The listen bench is the automatic layout for audio-only media (`auto`), and `media_layout: "listen"` asks for
  it explicitly (lint: audio only). One clip plays at a time everywhere on the page (a capture `play` listener
  plus explicit pausing before each play, so tests and fast clicks are deterministic).
- D5 Bench keys: Shift+1..9 play clip N (by `KeyboardEvent.code`, so keyboard layouts do not matter); `b` is the
  A/B switch, which starts the next clip at the same fraction of its length. Plain 1..9 still pick options; the
  Keys dialog lists both. The seek bar is a native range input (keyboard and screen readers work as is), with
  `aria-valuetext` in minutes and seconds.
- D6 A clip may name the option it is (`option`); on a compare question with `sides` the bench label reads
  "Left"/"Right" until the pick, exactly like the option rows. A clip may carry `text`, the line being spoken.
- D7 Audio inside an option's `media` is a small Play button, not an `<audio controls>` element inside the label:
  a button is interactive content, so clicking it never picks the option.
- D8 Question page reading order: context line (project · set title), the question title as a coloured eyebrow
  with "hard to undo" as a tag, the question as the heading, "Why this matters" in a tinted block, "What to look
  for" (or "What to listen for" on audio questions), then background (moved below the why: it supports the
  question instead of preceding it), media, options with consequences, guess, note.
- D9 Top bar: a small uppercase project line above the set title; "Copy continue prompt" shortens to "Copy prompt"
  on a phone so the bar does not overflow.
- D10 Dashboard cards: project eyebrow, title, meta, counts, then "Open questions" and "Copy continue prompt"; the
  search also matches the project name and path.
- D11 The install-size budget's yellow ceiling moves from 240 KB to 280 KB (247 KB after this release), the same
  way 0.4.0 moved it from 200 KB; the SKILL.md body stays under its 10 KB ceiling by trimming two lines.
