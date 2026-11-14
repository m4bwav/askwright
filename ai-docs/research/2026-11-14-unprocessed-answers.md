# Unprocessed answers: what the owner's inbox shows and where the code lets answers slip

Measured 2026-11-14 on the owner's registry with askwright 0.30.0, and read from `ask.py` and `page/dashboard.js` at
that version. Set names and paths stay out of this public repository; rerun the snippet below to see them.

The owner's report: some answered questions are never processed, so the answers are never used; others are used but
never marked as processed. Both show up in the numbers.

## Counts

191 registered sets:

| State | Sets | Notes |
|---|---|---|
| Consumed (`ask.py consume` at or after the latest answer) | 113 | |
| Read, not consumed | 27 | 7 have a latest answer more than 7 days old; the oldest is 13.9 days |
| Answered, never read with `ask.py read` | 14 | none over 7 days yet; the oldest is 6.6 days |
| No answers yet | 10 | |
| Registry entry whose folder is gone | 27 | all under a temp folder |

So 41 sets hold answers that nothing records as used, about one in five.

Of the 12 oldest read-not-consumed sets, 6 have no answered and no open question left: every question was closed.
Inferred, not checked set by set: a session acted on the answers, closed the questions and never ran `consume`. That
is the "used but not marked" case.

Of the 12 oldest never-read sets, 3 also have nothing answered or open. Unknown why: a session may have read
`answers.json` directly, or closed the questions without reading. Check before deciding what the routine does with them.

## Where the code lets answers slip (0.30.0)

1. **Never-read sets are invisible.** `use_state` sets `unconsumed` only when a read happened, so the dashboard's
   Unconsumed tab leaves out every set that was answered and never read. Its empty text says "Every answer set that
   was read has been used", which is true and hides the worse case.
2. **`pending` is narrow.** `pending_sets` lists a set only if it recorded a `working_dir`, has an "All done" mark with
   no claim, and the mark is under `PENDING_DAYS` (30). The session-start hook also filters by the current folder. A
   partly answered set, an "I'm done for now" set, and a set whose project folder no session opens never surface.
   After 30 days a set drops out without a word.
3. **`close` does not record use.** `cmd_close` writes the question status and nothing to `uses.jsonl`, so closing
   every answered question leaves the set unconsumed.
4. **The generated continue prompt never says consume.** `continue_prompt()` (the text behind the page's Copy
   continue prompt button) tells the session to read, act and close. Only SKILL.md Step 6 mentions `consume`.
5. **chainwright's prompt template has the same gap.** Step 2 of the template in its `chain.py` says read, act on
   answered questions and close them. Every chain scaffolded from it inherits that.
6. **Nothing shows age.** The Unconsumed tab sorts by read time and has no threshold. No page and no command says
   how long an answer has waited, and nothing warns.
7. **The registry holds dead entries.** 27 entries point at temp folders that no longer exist. An earlier cleanup
   (L-023 `verify-scripts-leak-registry`) removed some and fixed one source; either another source leaks or these are
   newer. They cost a failed load on every dashboard scan.

## Snippet to rerun the count

Run from the repository root. It reads only.

```python
import collections, sys, time
sys.path.insert(0, "skills/askwright/scripts")
import ask

rows = []
for f in sorted((ask.state_dir() / "sessions").glob("*.json")):
    try:
        d, data = ask.load_set(ask.registered_set(f.stem))
        st, u = ask.summarize(d, check_server=False), ask.use_state(d)
    except Exception as e:
        rows.append(("error", f.stem, None)); continue
    last = u["last_answer_at"]
    age = round((time.time() - ask.parse_time(last)) / 86400, 1) if last else None
    state = ("no-answers" if not last else "never-read" if not u["read_at"]
             else "read-not-consumed" if u["unconsumed"] else "consumed")
    rows.append((state, str(d), age, len(st["answered"]), st["open"]))
print(collections.Counter(r[0] for r in rows))
for r in sorted((r for r in rows if r[0] in ("never-read", "read-not-consumed")), key=lambda r: -(r[2] or 0)):
    print(r)
```
