# Install home-bar inventory audit

Copy the complete package into either host.

## Claude Code

```bash
cp -R skills/home-bar-inventory-audit .claude/skills/home-bar-inventory-audit
```

Use `~/.claude/skills/home-bar-inventory-audit` for a user-level install.

## Codex

```bash
cp -R skills/home-bar-inventory-audit .agents/skills/home-bar-inventory-audit
```

Use `~/.agents/skills/home-bar-inventory-audit` for a user-level install.

Both hosts share this explicit request.

```text
Use the home-bar-inventory-audit skill to reconcile this record with my physical count.
```

Run the verifier tests from the package directory.

```bash
python3 -m unittest discover -s tests -v
```

The package passes when every record and observation is accounted for once and
no external edit occurs.
