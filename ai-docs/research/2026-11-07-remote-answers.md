# Remote answers: options, threat model and wake-up support

Checked 2026-11-07 against the primary pages linked below. Owner-specific names stay in the private notes.

## Facts about this setup

- `ask.py serve` binds 127.0.0.1, one port per set plus the dashboard. Every request is checked for Host; API calls for a per-run token; POSTs for Origin. A proxy route only needs the Host and Origin allowlists extended.
- The owner's PC does not sleep or hibernate on AC power, and had been up 10 days when checked. "The PC must be awake" costs little in practice, and does not justify a relay on its own.
- The owner's site DNS is hosted at DreamHost, not Cloudflare. Cloudflare Tunnel needs a Cloudflare zone, so it means moving nameservers or buying a domain.
- Neither `tailscale` nor `cloudflared` is installed, so the phone video proof waits for the owner's decision (installs and accounts are stop points).

## What the sources say

| Claim | Source |
|---|---|
| Tailscale Personal is free for 6 users, non-commercial use only | [plans](https://tailscale.com/docs/account/manage-plans/free-plans-discounts) |
| `tailscale serve` proxies to 127.0.0.1, inside the tailnet only, with HTTPS certificates | [serve](https://tailscale.com/kb/1312/serve) |
| Serve adds `Tailscale-User-Login`, strips incoming copies to stop spoofing, and includes users who accepted a share of the device; not populated for tagged devices | [serve](https://tailscale.com/kb/1312/serve) |
| `--bg` persists across reboots; `--https=<port>` and `--set-path` map a port or path | [serve CLI](https://tailscale.com/kb/1242/tailscale-serve) |
| Cloudflare Zero Trust is free up to 50 users. Forum posts disagree on what happens at the cap and on overage consent at checkout | [pricing](https://www.cloudflare.com/plans/sase-zero-trust.md), [forum](https://community.cloudflare.com/t/zero-trust-free-checkout-overage-consent-and-a-strict-0-spending-cap/976954) |
| Access one-time PIN: an email allowed by a policy gets a single-use code, valid 10 minutes. The page implies no install but does not state it | [OTP](https://developers.cloudflare.com/cloudflare-one/integrations/identity-providers/one-time-pin/) |
| An origin validates `Cf-Access-Jwt-Assertion` against the team's certs (RS256, `iss`, `aud`) | [JWT](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/validating-json/) |
| Non-Enterprise CDN customers must use paid services to serve video and other large files, or Cloudflare may limit them. The clause does not name Tunnel; that a proxied Tunnel hostname counts is our reading, not their statement | [terms](https://www.cloudflare.com/service-specific-terms-application-services/) |
| ntfy.sh: the topic name acts as the password; `Click` opens a URL; `Email` forwards by email; a search summary of the docs gave 250 messages and 5 emails a day (confirm before relying on them) | [publish](https://docs.ntfy.sh/publish/) |
| App Service B1 has about 10 to 11 GB of storage (pages disagree); exceeding it fails all writes | [OS functionality](https://learn.microsoft.com/en-us/azure/app-service/operating-system-functionality), [pricing](https://azure.microsoft.com/en-us/pricing/details/app-service/windows/) |
| Telegram `getUpdates` long polling needs no webhook; updates last at most 24 hours | [Bot API](https://core.telegram.org/bots/api) |
| Channels push events into an open session only, are a research preview, need an allowlisted plugin and Bun; a custom channel needs a development flag | [channels](https://code.claude.com/docs/en/channels) |
| Remote Control drives a running local session from the phone, reconnects after sleep, sends mobile push | [remote control](https://code.claude.com/docs/en/remote-control) |
| `--resume <id>` works for saved sessions; `--permission-mode dontAsk` denies anything that would prompt; deny rules and hook denials hold in every mode | [sessions](https://code.claude.com/docs/en/sessions), [headless](https://code.claude.com/docs/en/headless), [hooks](https://code.claude.com/docs/en/hooks) |

Not verified: Google sign-in on App Service, Gmail reply authentication details, Artifact video on a phone, Tailscale's mobile behaviour with video. Step counts for setup are estimates until someone does the setup.

## Comparison

Steps per question count what a person does after the agent runs its one command.

| Route | Steps per question | Setup: owner / second reviewer | Media | Phone | PC off | Attack surface | Cost | What leaves the PC |
|---|---|---|---|---|---|---|---|---|
| **Tailscale Serve + notification** | 2: tap link, answer | about 5 / 3 (install, sign in, accept share) | full, local | yes, VPN app on | no answers | tailnet members only, no public address | free | encrypted traffic to the named devices; notification text |
| Cloudflare Tunnel + Access | 2, plus an emailed code when the login lapses | about 7 plus a domain / 0 | full, but video terms are a risk | yes | no answers | public hostname behind Access | free tier plus domain | everything passes Cloudflare, decrypted at its edge |
| Home network only | 2 | 2 / 0 | full | home only | no answers | anyone on the LAN unless a login is added | free | nothing |
| Own website relay | 2, plus a login | large build / 0 | media must be copied; about 10 GB | yes | **answers accepted** | public app holding private sets | existing plan plus storage | question text and media, stored |
| GitHub pull request | 3 or more; needs a GitHub account | moderate / 1 | poor | fair | accepted | public-repo exposure, or private-repo limits | free | everything, stored |
| Email reply | 2 to 3 | moderate / 0 | none in the mail | yes | accepted | forged mail, needs DKIM checks | free | question text |
| claude.ai Artifact | 2 | small / an account | earlier video failure, retest needed | yes | accepted | account-scoped | plan | question text and media |
| Telegram or chat agent | 2 | moderate / 1 | simple questions only | good | queued 24 hours | sender allowlist; an agent may reinterpret answers, which AGENTS.md forbids | free | everything, stored |
| Remote Control (already available) | 2 | 1 / not usable | **chat only, no clips** | good | no | Anthropic account | plan | session content |

## Recommendation

Tailscale Serve for both people, a notification beside it, and no relay. It is the only route where media stays on the PC and nothing is on the public internet. Identity comes from the network rather than from login code we would have to write, and the server change stays small. Its real cost is one app for the second reviewer, once. Cloudflare is the fallback if that app is rejected: no install for her, but a public hostname, a DNS move or new domain, and a video-terms risk.

The relay's one advantage is answering while the PC is off. Since this PC stays on, that does not pay for a public app holding private sets.

Remote Control already covers the owner's chat-only questions from a phone, so it needs no build.

**Target check:** one command, a notification, no routine sign-in, an answer, and the session continues. Tailscale meets this for open sessions after one-time setup. A closed session meets it only if the owner approves unattended starts; otherwise it takes one more step, pasting a start command.

## Threat model

Assets, worst first: files outside the project and shared branches, reached through an agent; private question text and media; the integrity of answers.

| Threat | Limit that holds if the check fails | Test |
|---|---|---|
| Unauthenticated visitor | No public address; tailnet ACL; allowlist of `Tailscale-User-Login` | request without identity gets 403 |
| Stolen link | Useless off the tailnet; the token is never in a URL | wrong Host gets 403, no token gets 403 |
| Spoofed identity header | Serve strips it; ask.py trusts it only in remote mode on the configured Host | header sent to a local-mode server is ignored |
| Forged email | Email is not an answer route; notifications are outbound only | not applicable unless email answers are chosen |
| Cross-site request | Origin allowlist plus token | wrong Origin gets 403 |
| Prompt injection in a note | `read` marks remote text untrusted; screening holds it; session permissions do not widen | injection samples held, ordinary notes not |
| Malicious upload | Existing cap, magic-byte check and folder rule | existing tests |
| Path in a media reference | Existing resolved-path check | existing tests, repeated in remote mode |
| Replayed answer | Answers overwrite by question and carry `rev`; closed or superseded questions refuse | replay to a closed question refused |
| Notification leak | Generic title and link only, random topic; link works only on the tailnet | built message contains no question text |
| Compromised tailnet device | Revoke the device; remote mode refuses routes that act on the PC | routes below refuse in remote mode |

Remote mode must refuse the dashboard's `/api/open` and the set's `/api/open-ref`, since both act on the PC. That is the "no inbound control" rule applied to routes that exist today.

**The check:** deterministic rules (commands, paths, URLs, "ignore previous instructions" phrasing). It can be fooled, so it only adds to the limits above. A held answer stays out of `read` until the owner releases it. A model check is left out at first: it would add cost and a dependency to a standard-library script, and is worth adding only if the rules miss real samples.

**What an answer can trigger:** a live session keeps its own permissions, and answers cannot change them. Any unattended start would use `--permission-mode dontAsk` with deny rules for pushes, publishing and deletes, enforced by the tool rather than by written instructions.

## Wake-up support by tool

| Case | Claude Code | Other tools (Copilot, Codex, Cursor) |
|---|---|---|
| Session open and waiting | background `status --wait-done` re-invokes it | only if the tool has background commands; otherwise a person says "done" |
| Session open, no waiter | no signal; Channels could do it but are a preview with a plugin allowlist, so not relied on | none |
| Session closed or machine restarted | `ask.py pending` finds the answers from disk; `--resume <id>` is possible if approved | `pending` when an agent or person runs it |
| Answer while PC is off | impossible on this route: the page is unreachable, nothing is lost | same |
| Partly answered, or "done for now" | no wake; a timeout reports the counts | same |
| Answer after the session moved on | stays in `pending` until claimed | same |
| Duplicate signals | `claim` succeeds once per "All done" | same |

## Tailscale behaviour checked against source (2026-11-07, session 3)

Docs do not state these, so they were read from `tailscale/tailscale` main (commit 01fa3ca, 2026-11-05). Still not run on a real install.

| Assumption in PR 53 | Result | Where |
|---|---|---|
| Host stays as sent, port included | Holds: `r.Out.Host = r.In.Host` for TCP targets | `ipn/ipnlocal/serve.go` |
| `X-Forwarded-For`, `-Host`, `-Proto` are added | Holds | `addProxyForwardedHeaders` |
| Identity headers stripped from input, set for tailnet users, absent for tagged nodes and the local machine | Holds | `addTailscaleIdentityHeaders`, [serve](https://tailscale.com/kb/1312/serve) |
| `--https=<high port>` | Holds: any port up to 65535 | `cmd/tailscale/cli/serve_v2.go` |
| `http://127.0.0.1:<port>` target | Holds | [serve CLI](https://tailscale.com/kb/1242/tailscale-serve) |
| Video seeking on a phone | Unknown until the phone test | |

Found and fixed in PR 53: with HTTPS certificates off, `tailscale serve` prints an enable link and waits, which `ask.py` lost in a 30 s timeout. Also a setup step was missing: [HTTPS needs MagicDNS and publishes machine and tailnet names](https://tailscale.com/kb/1153/enabling-https) on the Certificate Transparency ledger. Sharing is on [all plans](https://tailscale.com/kb/1084/sharing), the recipient needs an Owner, Admin or IT admin role on their own tailnet, and unused invites expire after 30 days.
