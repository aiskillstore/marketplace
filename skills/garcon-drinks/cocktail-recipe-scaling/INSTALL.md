# Install cocktail recipe scaling

Copy the complete package so the deterministic calculator remains beside the
shared procedure.

## Claude Code

```bash
cp -R skills/cocktail-recipe-scaling .claude/skills/cocktail-recipe-scaling
```

Use `~/.claude/skills/cocktail-recipe-scaling` for a user-level install.

## Codex

```bash
cp -R skills/cocktail-recipe-scaling .agents/skills/cocktail-recipe-scaling
```

Use `~/.agents/skills/cocktail-recipe-scaling` for a user-level install.

Both hosts share this explicit request.

```text
Use the cocktail-recipe-scaling skill to scale this supplied recipe to my target yield.
```

Verify the calculator from the package directory.

```bash
python3 -m unittest discover -s tests -v
```

The installation passes when tests succeed and mismatched yield units produce a
stop instead of a conversion.
