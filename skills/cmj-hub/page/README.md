<p align="center">
  <img src="./assets/lockup.png" width="880" alt="Landing page skill for Claude Code. A landing page is one page, one offer, and one action.">
</p>

# Landing page skill for Claude Code

A landing page is one page, one offer, and one action.

The sample is a one-page desk that names the week's leak.

The good draft passes. A sitemap fails the score.

<p align="center">
  <img src="./assets/demo.gif" alt="Landing page skill — one page passes, a sitemap fails" width="100%">
</p>

The build guide teaches a human. The pack teaches an agent.

## Install

```bash
npx skills add cmj-hub/claude-landing-page --all -g --full-depth
```

`--all` writes this pack for every host the installer knows. One host:

```bash
npx skills add cmj-hub/claude-landing-page --skill '*' -g --full-depth -y -a claude-code
```

Swap `claude-code` for `cursor`, `codex`, `grok`, `github-copilot`, `windsurf`, `cline`, or `opencode`. The scorer is Python in this repo. It does not call a paid API.

## What you walk out with in 15 minutes

Artifact: `examples/page-good.json`.

```bash
python3 scripts/score.py --file examples/page-good.json
python3 scripts/score.py --file examples/page-sitemap.json
```

The good draft exits 0 and prints the URL, the offer, and the action. The sitemap draft exits 1. Then drop in yours.

## What this pack will not do

It will not publish the page. It does not emit a sitemap. It will not list every URL on the site.

## What belongs on a landing page?

One page, one offer, and one action. A second offer, or a list of every URL on the site, fails the score.

## Does this publish the page?

No. It scores the draft. You publish it.

## On the site

- [Landing page pack](https://jaymountconsulting.com/skills/claude-landing-page) — this pack's page
- [Skill packs catalog](https://jaymountconsulting.com/skills) — install paths + every pack

## Free, no signup

[All free tools](https://jaymountconsulting.com/prototypes)

## Free, by email

[**Growth Audit**](https://jaymountconsulting.com/growth-audit) — architecture gaps in the GTM you already run. Free written report.

[**Friday Signal**](https://jaymountconsulting.com/newsletter/signal) — one Friday GTM read. No pitch in it.

## Next

Previous: [Sales offer](https://github.com/cmj-hub/claude-sales-offer)

Next: [Generative engine optimization](https://github.com/cmj-hub/claude-geo)

## License

MIT. No paid APIs. Python 3 standard library only.
