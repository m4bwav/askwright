---
kind: research
title: Form and survey design practice for agent question pages (creation pass, practice track)
date: 2026-10-24
tags: [research, forms, survey, gov-uk, bias, pairwise]
---

# Form and survey design practice (creation pass, 2026-10-24)

Practice track of the askwright creation pass. 12 searches, 21 fetches (17 succeeded). Weight is how strongly the finding should shape the design.

## Findings

| R | Date | Source | Finding | Weight |
|---|---|---|---|---|
| R-F01 | 2026-06-24 (page update) | [GOV.UK Service Manual, Designing good questions](https://www.gov.uk/service-manual/design/designing-good-questions) | Several simple questions are easier than one complex one. Closed questions are easier than open ones. Allow "I'm not sure" when it is a valid answer. Option labels that describe the action beat a bare "Yes". Help text explains consequences and jargon, never the interface. | high |
| R-F02 | current | [GOV.UK Radios](https://design-system.service.gov.uk/components/radios/) | "Do not pre-select radio options" (people miss the question or submit the wrong answer). Offer "None of the above" or "I do not know" when valid. Order options alphabetically by default; most-common-first only "with extreme caution as it can reinforce bias". Put an "or" divider before an option that differs from the rest. | high |
| R-F03 | current | [GOV.UK Question pages](https://design-system.service.gov.uk/patterns/question-pages/) | One question per page: a back link, the question as the heading, the section name as a caption, and Continue. No two pages share a heading. Hints are one sentence with no links. A complex question gets a statement heading, then the explanation, then the question label. Test without a progress indicator first. | high |
| R-F04 | 2015-07-03 | [GDS, One thing per page](https://designnotes.blog.gov.uk/2015/07/03/one-thing-per-page/) | Handles errors, branches, loops and saving progress better. Pair it with check-answers and save-and-return. It "shouldn't be used to mask the fact that you've got too many questions". | high |
| R-F05 | current | [GOV.UK Check answers](https://design-system.service.gov.uk/patterns/check-answers/) | A review page before finishing, with Change links. A skipped question shows "Not provided". After a change, Continue returns to the check page. | high |
| R-F06 | Frontend v5.0 (Dec 2023) | [GOV.UK Task list](https://design-system.service.gov.uk/components/task-list/) | Each task shows its status. Completed is plain text and Incomplete is a tag, so the open ones stand out. Built for long work done in any order over several sittings. | med-high |
| R-F07 | current | [GOV.UK Error summary](https://design-system.service.gov.uk/components/error-summary/) | A summary at the top under "There is a problem" that links to each field and takes focus. | med |
| R-F08 | 2017-06-25 and current | [One Login, save progress](https://sign-in.service.gov.uk/documentation/design-recommendations/save-progress); [Agriculture DS multi-task form](https://design-system.agriculture.gov.au/patterns/multi-task-form); [NN/g Wizards](https://www.nngroup.com/articles/wizards/) | Save without validation, land a returning user on the task list. Users still have to rebuild context when they come back, so the page must restate it. The GOV.UK save-a-draft pattern URL returns 404. | med |
| R-F09 | 2017-06-25 | [NN/g Wizards](https://www.nngroup.com/articles/wizards/) | Show the whole process and mark the current and completed steps. Buttons should name the next step instead of a bare "Next". Wizards make comparing steps hard. | med |
| R-F10 | 2010-06-07 | [Jarrett, The question protocol](https://www.uxmatters.com/mt/archives/2010/06/the-question-protocol-how-to-make-sure-every-form-field-is-necessary.php) | For each question record who uses the answer, what they do with it, and whether it is required. Cut questions whose answers nobody uses. Maps to a `why` field. | high |
| R-F11 | 2019 | [Jachimowicz et al., default effects meta-analysis](https://ideas.repec.org/a/cup/bpubpo/v3y2019i02p159-186_00.html); [Netspar default-as-advice](https://www.netspar.nl/kennisplein/default-as-advice-a-survey-experiment-on-preselecting-pension-choices-and-the-endorsement-effect/) | 58 studies, d = 0.68. The effect is strongest when the default reads as an endorsement. Pre-selection moved answers by 19 to 28 points. The agent's guess is an endorsement, so it is shown and never pre-selected. | high |
| R-F12 | 2026 | [AIES, Limits of interventions in AI-assisted decision making](https://ojs.aaai.org/index.php/AIES/article/view/43309) | Seeing the AI's suggestion after judging still pulled people off correct judgments. Accountability prompts did not help. Framing consequences cut over-reliance. One study, not replicated. | med |
| R-F13 | 2005 | [Holbrook, Krosnick et al.](https://web.stanford.edu/dept/communication/faculty/krosnick/docs/2005/2005_holbrook_gallup.pdf) | Options shown on screen produce primacy effects. Do not always list the recommended option first. | med |
| R-F14 | 2002 | [Krosnick et al., no-opinion options](https://asu.elsevierpure.com/en/publications/the-impact-of-no-opinion-response-options-on-data-quality-non-att) | "No opinion" is used most late in a survey and by tired respondents. Allow "not sure", but record it as a state that comes back for follow-up. | med |
| R-F15 | secondary | [Pew guidance, quoted by GVSU](https://www.gvsu.edu/cms5/asset/f1045829-476f-432e-ac84-e42b5b53aaa5/1e119ed7-9f0e-4b70-81b7-36546651fe0b/pew_surveydesign_nodate.pdf) | Split double-barrelled questions. Wording shifts results by tens of points. Agree/disagree scales invite acquiescence. pewresearch.org returned 403, so this is second-hand. | med |
| R-F16 | 2024-03-07 | [Chatbot Arena paper](https://arxiv.org/html/2403.04132v1); [Zheng et al. 2023](https://arxiv.org/abs/2306.05685) | Model identities stay anonymous until after the vote. The votes are A better, B better, tie, both bad. Position bias in pairwise judging is documented. The paper does not say outright that sides are randomized. | high (compare) |
| R-F17 | 2015-10 | [MUSHRA, ITU-R BS.1534-3](https://audiolabs-erlangen.de/content/resources/aesCodingTutorial/mushra.html) | Versions are shown in random order with a hidden reference. Listeners who rate the hidden reference below 90 are screened out. A known-answer pair can check attention. | med |
| R-F18 | 2016 | [Bezos, 2015 letter](https://www.sec.gov/Archives/edgar/data/1018724/000119312516530910/d168744dex991.htm) | Reversible "two-way door" decisions should be quick, irreversible ones careful. A `reversible` field sets the depth of explanation. | med |
| R-F19 | 2024-09-17 | [MADR 4.0.0](https://adr.github.io/madr/) | Context and problem, options considered, then the outcome, with pros, cons and consequences per option. Anti-patterns: a buried recommendation, strawman options, over-deliberating reversible calls. This is the shape of a one-pager. | med |

## Rules this implies

- **Schema:** each question has an id and a version, a status (open, superseded or withdrawn), and the question text ending in "?". It also has why it matters (who uses the answer), what to look for, context, and whether it is reversible. Options carry an action label and a consequence. Add an allow-unsure flag, the guess with its reason, and a required flag. The kind is choice, multi, text or compare; compare questions also carry random sides plus tie and both-bad.
- **Lint:** fail on a missing "?", a duplicate heading or an empty why. Fail on position-only labels ("left", "right", "A", "option 1", bare yes/no) outside compare questions. Fail when a superseded or withdrawn question is still open. Warn when one heading joins two asks with "and" or "or", on leading words ("obviously", "don't you think"), when the guess is always the first option, and when a set has more than about 12 open questions.
- **Page:** one question per screen and nothing pre-selected. The guess is shown as a labelled line after the consequences. A note without a choice gets an error summary unless "Not sure" is chosen. Autosave and land on the task list. A check-answers screen shows "Not provided" with Change links. A "where was I" line names what is left. Compare answers are stored as the option id and the side that was shown, never "left".
- **Answer record:** option id, the label shown, note, time, question version, and whether it matched the guess (to measure guess-following).

## Open

- Should the guess be hidden until the person picks, then revealed? Hiding it guards against anchoring (R-F11, R-F12), but Mark asked to see the guess. Default: show it, collapsed behind "Show my guess", with a per-set switch. This is a decision for Mark.
- Pew primary pages (403). Whether Chatbot Arena randomizes sides officially. NN/g progress-indicator and interruption pages were not found.

## Search notes for refreshes

GOV.UK Design System and service manual pages fetch cleanly. pewresearch.org returns 403 to WebFetch. NN/g search results are swamped by form-builder SEO, so fetch nngroup.com URLs directly. arXiv HTML pages carry the UI details.
