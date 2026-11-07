# Refs and background tabs

Owner request, from a question that asked whether a build had been played without saying where to test it.

- D1. `refs` and `tabs` work on a question and on the set; set-level ones appear on every question, after the question's own.
- D2. A ref is a `path` or a `url`, never both. Paths may be relative to the set folder and are shown absolute.
- D3. Open folder is limited to paths the set lists, needs the page token, and opens a file's parent folder, so a listed `.bat` or `.exe` is never run.
- D4. Tabs sit under the question's heading, so the question stays in view. All panels stay in the page, so drafts and clips survive a switch. On another tab only n, p and the arrows act, so digit keys cannot pick an answer the reader cannot see.
- D5. A `no-refs` lint warning fires when an open question's `question` or `why` names a build, repo, branch, commit, pull request or source code and neither it nor the set has refs. Without it agents would forget the field. A warning only, since "build" also has everyday meanings.
- D6. `ask.py inline` refuses a set with refs or tabs, because chat would drop them.
- D7. The install is 322 KB after removing duplicate CSS, over the 320 KB yellow ceiling, which moves to 340 KB as in earlier releases. The next split candidates are the example and the study section in references/schema.md.
