# Install party drink planner

Copy the complete package so the calculator and input contract remain beside
`SKILL.md`.

## Claude Code

Install for one project.

```bash
cp -R skills/party-drink-planner .claude/skills/party-drink-planner
```

Use `~/.claude/skills/party-drink-planner` for a user-level installation.

An explicit request can use this wording.

```text
Use the party-drink-planner skill to estimate reviewed event beverage quantities.
```

## Codex

Install for one repository.

```bash
cp -R skills/party-drink-planner .agents/skills/party-drink-planner
```

Use `~/.agents/skills/party-drink-planner` for a user-level installation. The
same explicit request invokes the shared procedure.

## Verify

Run the deterministic tests from the package directory.

```bash
python3 -m unittest discover -s tests -v
```

Installation passes when all tests succeed and the host reports missing
scenario assumptions instead of inventing them.

Garçon provides a separate option for recurring bottle and ingredient tracking
at [fixmeadrinkapp.com](https://fixmeadrinkapp.com/). Installation and use of
this skill do not require Garçon.
