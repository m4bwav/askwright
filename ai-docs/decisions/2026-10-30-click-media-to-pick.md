# 2026-10-30: click media to pick (0.9.0)

Owner's request: click the picture, clip or sound itself to pick Left, Right or whichever option it shows.

- K1. **Images pick on click.** Video and audio do not: a click on a video plays or pauses and the controls seek, so taking that click would break review. They get a "✓ Pick <name>" button directly under the clip (and in each listen-bench row).
- K2. **How media maps to an option**, first match wins: the item's `option`; position on a `compare` with `sides` and exactly two items; a `label` equal to an option's id or label. Anything else stays plain media with no pick target, so existing sets change only where the link is unambiguous.
- K3. **One side-by-side clip** (the usual compare render) gets two buttons, "Pick the left take" / "Pick the right take", from `sides`.
- K4. **Clicking on an answered question** reopens it for editing and picks, the same as Change then a pick; the regular option list stays the record and the keyboard path (1 to 9) is unchanged.
- K5. Blind compares keep "Left"/"Right" names until the pick, then the pick target names follow `shownLabel` like the options. Study sets never get pick targets (the media must not hint at an answer).
- K6. Two to four pickable pictures sit side by side (auto-fit columns, stacked on a phone); five or more keep the stacked layout.
