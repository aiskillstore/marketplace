# Contributing

Thanks for opening this repo. A few notes on how this project works
before you contribute.

## What kinds of contributions land

- **Bug reports** — open an issue with a reproducible case. The
  scripts in `scripts/` are deterministic, so bugs there are usually
  one-line fixes.
- **New sub-skills** that extend the existing framework. Discuss in
  an issue first if it's a substantial addition.
- **Calibration improvements** to the scoring scripts — if you can
  show a case where the script scores wrong, that's gold.
- **Cross-runtime ports** (Cursor, Gemini CLI, Codex) — see the
  Install section of the README.
- **Translation** of the framework reference docs.

## What doesn't land

- Renaming the JMC framework concepts (welcome → bargain → nurture,
  Signal → Pain → EVP → Ask, the 5 Schwartz tiers, the 4 content
  pillars) — these are course-anchored.
- Adding LLM calls inside the skills. The whole point is that the
  skills are deterministic.
- Adding paid-API dependencies to scripts. Scripts must work zero-dep.
- Renaming `claude-*` → `<other-runtime>-*`. We ship per-runtime ports
  as separate plugins instead.
- Turning this pack into a send tool or a cold-email writer. It scores
  lifecycle drafts only.

## Development setup

```bash
git clone https://github.com/cmj-hub/claude-email-sequence.git
cd claude-email-sequence
# Install into local agents (Claude Code, Cursor, Codex, …)
npx skills add cmj-hub/claude-email-sequence --all -g --full-depth
```

For Python scripts:

```bash
# All scripts are zero-dep Python 3.8+ — just run them
python3 scripts/score.py --help
python3 scripts/score.py --file examples/lifecycle-good.json
python3 scripts/score.py --file examples/lifecycle-refused.json
```

## Pull-request checklist

- [ ] Skill names follow the spec (lowercase, hyphens, ≤64 chars,
      directory matches `name:` in frontmatter)
- [ ] Sub-skill descriptions include trigger phrases inline
- [ ] If you touch a script, smoke-test it and paste output in the PR
- [ ] If you add a new sub-skill, list it in the README companion table
- [ ] Examples stay paired: one good exit-0 draft, one refused exit-1
- [ ] No new dependencies (any of: pip packages, npm packages, API
      keys, paid services)

## Reporting calibration issues with scoring scripts

If `scripts/score.py` scores something obviously wrong:

1. Paste the input JSON that produced the wrong result
2. State your expected exit code + actual exit code (and printed parts)
3. Note which gate misfired (generic drip, cold email, missing part,
   or pain mismatch)

Keep the deterministic path stable. Prefer new paired examples under
`examples/` over rewriting the scorer for one-off cases.

## License

By contributing, you agree your contributions ship under the MIT
license already on this repo.

## About

Built by [Jay Mount Consulting](https://jaymountconsulting.com).
Part of the JMC public-build spine — see [/build](https://jaymountconsulting.com/build).
