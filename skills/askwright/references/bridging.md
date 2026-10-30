# Moving an existing review page onto askwright

Many projects already have a long, scrolling review page: every candidate of a batch on one page, with clicks
saved to the project's own picks file that later tools read. Past ten or so items that page gets too long to
answer in one sitting. Move the items onto askwright, one per screen, and keep the old picks file as the record.

## The bridge

Write a small script in the project (not in askwright) with two commands:

1. **make**: read the open items from the page's own source data (not its HTML) and write a set:
   - one question per item; the question id encodes the item's key in the picks file (`still.<id>`,
     `card.<id>`; ids allow letters, digits, `-`, `_` and `.`);
   - candidates in **one labelled image** per question (`scripts/contact.py`), so no candidate hides behind
     gallery navigation; options name each candidate ("Candidate 2 (s22)") plus the real "none of these" outcome
     ("Re-render, say why in the note");
   - the person's earlier notes on that item as the `hint`, so a re-roll is judged against what they asked for;
   - `back_link` to the old page (`ask.py new --back-link URL LABEL`), and a sidecar file in the set folder that
     says which picks file to write to;
   - skip items already decided in the picks file; split sets at about 10 questions.
2. **sync**: `ask.py read <set>`, then write each answer into the picks file in that file's own format. Skip
   `unsure`, unanswered and `stale` answers; map `other` to the project's redo or re-roll value with the note.
   Keep entries the picks file already has. Run it before any tool reads the picks file.

Test the round trip on a copy of the picks file: post answers through the served page's API (`/api/answer` with
the page's token), stop the server, sync, and check the copy.

## Guesses

Every question needs a guess. Look at the candidates and write real ones (a file mapping question id to guess
is easiest to pass to the bridge). An earlier pick from the picks file is a fair guess. A placeholder such as
"no guess made" defeats the guess's purpose; use it only when you truly could not look, and say so.
