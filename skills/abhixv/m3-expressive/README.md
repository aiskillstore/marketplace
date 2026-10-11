# m3-expressive

The skill itself. `SKILL.md` is what an agent reads. Start there, or let it load on its own when a
request touches Material Design.

```
m3-expressive/
├── SKILL.md                    # entry point: source contract, quick reference, router
├── references/
│   ├── tokens.md               # every exact number: type scale, radii, springs
│   ├── component-tokens.md     # 916 per-component dp values across 104 component groups
│   ├── components/*.md         # 40+ components: variants, placement, states, do/don'ts
│   ├── motion · shape · typography · color · color-schemes · transitions
│   ├── layout · interaction · foundations · platforms
│   └── expressive-tactics.md · visuals.md
├── visuals/                    # 2,587 reference images + INDEX.tsv caption index
└── scripts/                    # refresh scripts (Node.js)
```

**Install instructions, per-agent setup, and everything else:**
[repository README](../../README.md) · [github.com/abhixv/m3-expressive-design-skill](https://github.com/abhixv/m3-expressive-design-skill)

MIT for the original work; Material Design content and reference images remain © Google LLC under
their own licenses. See [LICENSE](../../LICENSE) and [NOTICE.md](../../NOTICE.md). Not affiliated
with or endorsed by Google.
