# explainer-engaging

<p align="center"><img src="../../docs/explainer-engaging.gif" width="80%" alt="explainer-engaging before and after: the brief, then a one-take story through the product"></p>

## Product explainers

**Three skills that turn a few sentences about any product into a finished explainer video**, written in code and rendered to MP4 with its own soundtrack. Pick the energy you want:

This is the **engaging** one. Sister skills: [`explainer-high-energy`](../explainer-high-energy/README.md) · [`explainer-default`](../explainer-default/README.md).

| Skill | Style | Default length |
|---|---|---|
| `explainer-high-energy` | Showreel energy. A new idea on every beat (title slam, kinetic words, a signature 3D or particle moment, a product micro-interaction, an end card), and every transition is a shape carrying into the next scene. | 15 s |
| `explainer-default` | The calm homepage demo. Airy canvas, one short line at a time that the camera pushes into, then your product's real interface shown big while it's used: typing, results, tables, clicks. | 60 s |
| `explainer-engaging` | A one-take visual story. One hero element travels through your product's workflow, laid out as stations on one big canvas. Each station reacts as it passes, then the camera pulls out to show the whole journey. | 12 s loop |

**Use it:** in Claude Code, run the skill (e.g. `/explainer-default`) and answer one short brief: the product (a URL is best), the one thing viewers must remember, brand colours or "use the website", 16:9 or 9:16. Everything else it decides by itself, and it takes direction if you have any.

**What you get:** `demo.html` (scrub it live in your browser), a fast draft MP4 to review, then the final 60 fps MP4 with motion blur and audio, plus a silent copy.

It never invents facts: no made-up stats, customers or offers. Numbers appear only if you or your website give them.

**Requirements:** Node 18+, ffmpeg, and Playwright (`npm i playwright`; the skill sets it up). Each skill is a single [`SKILL.md`](SKILL.md) with its renderer inside it.

## Licence

MIT. Geist fonts: SIL Open Font License. Icon paths adapted from Lucide (ISC).
