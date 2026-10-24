---
kind: research
title: Web platform, accessibility and media for a stdlib local question server (creation pass, subject track)
date: 2026-10-24
tags: [research, http.server, range, clipboard, wcag, video, playwright, axe]
---

# Web platform, accessibility and media (creation pass, 2026-10-24)

Subject track, plus the tooling and testing questions on the same topic. 8 searches, 22 fetches. The CPython source (`Lib/http/server.py` and `Lib/socketserver.py` on main) settled the Range and port-reuse questions; the docs say nothing about either.

## Findings

| R | Date | Source | Finding | Weight |
|---|---|---|---|---|
| R-W01 | 2026-10-24 (main) | [http.server docs](https://docs.python.org/3/library/http.server.html), [server.py](https://raw.githubusercontent.com/python/cpython/main/Lib/http/server.py) | `SimpleHTTPRequestHandler` never reads `Range` and never sends 206 or `Accept-Ranges`: it always sends the whole file. Python says it is "not recommended for production", and the handler follows symlinks out of the served directory. The CLI binds to all interfaces unless given `--bind`. `ThreadingHTTPServer` is needed because browsers pre-open sockets. | high |
| R-W02 | 2026-10-24 | [socketserver.py](https://raw.githubusercontent.com/python/cpython/main/Lib/socketserver.py), [MS: SO_EXCLUSIVEADDRUSE](https://msdn.microsoft.com/en-us/library/ms740621) | `HTTPServer` sets `allow_reuse_address = True`, so it sets `SO_REUSEADDR` with no Windows guard. On Windows that lets a second socket take a busy port. Use `allow_reuse_address = False` plus `SO_EXCLUSIVEADDRUSE`. Bind port 0 to get a free port and read `server_address` back. | high |
| R-W03 | 2026-10-20 | [MDN Clipboard API](https://developer.mozilla.org/en-US/docs/Web/API/Clipboard_API), [Clipboard.read](https://developer.mozilla.org/en-US/docs/Web/API/Clipboard/read), [paste event](https://developer.mozilla.org/en-US/docs/Web/API/Element/paste_event) | `navigator.clipboard.read()` (Baseline 2024) behaves differently in each browser: a permission prompt in Chromium, a "Paste" menu in Firefox and Safari. The `paste` event with `clipboardData.items`/`files` needs no permission and has been Baseline since 2015, so it is the dependable route; listen on `document`. `image/png` is the cross-browser image type. | high |
| R-W04 | 2026-10-22 | [playwright on PyPI](https://pypi.org/project/playwright/), [browsers](https://playwright.dev/python/docs/browsers) | Playwright 1.64.1 needs Python 3.10 or later, and the wheel is about 39 MB. `playwright install chromium --only-shell`; Chromium is about 281 MB. Bundled Chromium likely lacks H.264/AAC, so use `channel="chrome"` or `"msedge"` for playback tests. Use it in development only; the runtime stays stdlib. | med |
| R-W05 | 2026-09-10 | [WCAG 3.0 WD](https://www.w3.org/TR/wcag-3.0/), [WCAG 2.2](https://www.w3.org/TR/WCAG22/) | WCAG 3 is still a working draft with "several years of work" left. Build to WCAG 2.2 AA. | low |
| R-W06 | 2026-09-07 | [MDN video codecs](https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/Video_codecs) | H.264 with AAC in MP4 plays in every browser. HEVC depends on hardware and OS, and AV1 in Safari needs recent hardware. Warn on HEVC-only or AV1-only media. | med |
| R-W07 | bug reports | [WebKit 221622](https://bugs.webkit.org/show_bug.cgi?id=221622), [cendyne 2023](https://cendyne.dev/posts/2023-01-23-fixing-html-video-playback-on-chrome.txt) | Safari asks for `bytes=0-1` and treats the video as broken without a 206 and `Content-Range`. Chrome plays a 200 but cannot seek. The stdlib server must serve single-range 206. | high |
| R-W08 | 2026-07-24 | [axe-playwright-python 0.1.8](https://pypi.org/project/axe-playwright-python/) | `Axe().run(page)`; alternatively, vendor `axe.min.js` and inject it with `add_script_tag`, which saves a pip package. | med |
| R-W09 | 2026-06-10 | [MDN prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion) | Baseline since 2020. Respect it for transitions. | low |
| R-W10 | ED 2023-11-10 | [Secure Contexts §3.1](https://w3c.github.io/webappsec-secure-contexts/) | 127.0.0.0/8 and ::1 are potentially trustworthy, so `http://127.0.0.1:PORT` is a secure context without TLS. `localhost` counts only under let-localhost-be-localhost rules, so use the literal IP. | med |
| R-W11 | 2023-10-05 / 2024-12-12 | [WCAG 2.2](https://www.w3.org/TR/WCAG22/), [APG radio](https://www.w3.org/WAI/ARIA/apg/patterns/radio/) | Contrast: 4.5:1 for text (1.4.3), 3:1 for UI and focus (1.4.11). Keyboard: everything works by keyboard (2.1.1), focus is visible (2.4.7) and not hidden behind sticky bars (2.4.11). Targets are at least 24 px (2.5.8). Help stays in the same place on every screen (3.2.6). Earlier answers are never re-typed (3.3.7). Media: captions (1.2.2) and audio control (1.4.2). Native radios in a `fieldset`/`legend` give the APG keyboard behaviour (arrow keys move and check). | high |
| R-W12 | current | [Chrome autoplay](https://developer.chrome.com/blog/autoplay) | Muted autoplay is always allowed. Sound needs a user gesture, and a Next click counts as one. Catch the rejected `play()` promise. | low |
| R-W13 | 3.15 | [webbrowser docs](https://docs.python.org/3/library/webbrowser.html) | On macOS, 3.15 uses `/usr/bin/open`; `MacOSXOSAScript` is deprecated, with removal in 3.17. `open()` returning True only means a browser launched. | low |
| R-W14 | issue threads | [Playwright paste thread](https://lightrun.com/answers/microsoft-playwright-feature-how-to-simulate-a-paste-event), [WebKit layout test](https://webkit.googlesource.com/WebKit/+/master/LayoutTests/editing/pasteboard/data-transfer-items-image-png-expected.html) | Playwright has no paste API. Build `File` and `DataTransfer` in `page.evaluate`, then dispatch `new ClipboardEvent('paste', {clipboardData: dt, bubbles: true})`. Test the fallback with `set_input_files`. Test playback with `readyState>=2`, then `play()` and `currentTime` advancing. Test Range with `Range: bytes=0-1`, which should return 206. `--dump-dom` cannot interact, and a stdlib CDP client would need WebSocket. | med |

## Implementation rules

1. **Binding:** bind `('127.0.0.1', 0)` (or a requested port) with `ThreadingHTTPServer`. On Windows set `allow_reuse_address = False` and `SO_EXCLUSIVEADDRUSE`. Print and open `http://127.0.0.1:{port}/`.
2. **Serving:** subclass `BaseHTTPRequestHandler` and serve from an allowlist (the plugin's static files and the question folder). `Path.resolve()` each path and check `is_relative_to(root)`. Never echo request data into headers.
3. **Range:** handle single ranges `a-b`, `a-` and `-n`, answering 206 with `Content-Range` and an exact `Content-Length`. Send `Accept-Ranges: bytes` on every response. Answer 416 with `bytes */size` when the range is out of bounds. Stream in chunks and support HEAD.
4. **MIME types:** use an explicit map (mp4, webm, vtt, mp3, m4a, ogg, wav, png, jpg, gif, webp, svg). On Windows, `mimetypes` reads the registry.
5. **Media:** recommend H.264/AAC; the lint warns on HEVC or AV1 (when ffprobe exists). Use WebVTT `<track>` when captions exist.
6. **Controls and autoplay:** native `<video controls>` and `<audio controls>`. Never autoplay with sound, and catch `play()` rejections.
7. **Images:** the `paste` listener on `document`, drag and drop, and `<input type=file accept=image/* multiple>`. A "Paste image" button using `clipboard.read()` is optional, with `NotAllowedError` handled.
8. **Upload and request safety:**
   - Uploads: POST the blob with its `Content-Type`. Cap the size, check magic bytes, use a server-chosen filename, and save next to the questions.
   - All POSTs: require a per-run token in a header, and check `Host` and `Origin`, so another web page cannot write to the port. That check is our inference, not sourced.
9. **Accessibility:** one `h1` per question; radios in `fieldset`/`legend`; 44 px targets; a visible focus ring with 3:1 contrast; `scroll-padding` for sticky bars; 4.5:1 text contrast; fixed button positions; Back keeps the earlier answer; an `aria-live` save status.
10. **Tests:** Playwright `--only-shell`, or the branded `channel` for H.264, plus axe. All of it is a development dependency only.

## Open

- From which version Firefox lets web pages call `clipboard.read()`.
- Whether synthetic paste events carry `clipboardData` in Firefox and WebKit under Playwright (needs a spike).
- Whether bundled Chromium 156 plays H.264 (likely not).

## Search notes

The raw CPython source answered what the docs do not. Searching "SimpleHTTPRequestHandler Range" returns noise. Use WebKit bug 221622 and Microsoft Learn's SO_EXCLUSIVEADDRUSE page.

Upcoming: Python 3.17 removes `MacOSXOSAScript` (date not fixed).
