# Localhero.ai Agent Skill

An agent skill for [Claude Code](https://docs.anthropic.com/en/docs/claude-code/skills), [Cursor](https://cursor.com/docs/context/skills) and similar AI coding assistants. Helps work with i18n strings in projects that use Localhero.ai for translation management.

Your assistant gets access to your project's glossary and style settings, as well as instructions on how to work with Localhero.ai in your project. Glossary terms and settings are loaded dynamically when the skill activates.

## Install

```bash
npx skills add localheroai/agent-skill
```

## Prerequisites

The [Localhero.ai CLI](https://www.npmjs.com/package/@localheroai/cli) must be installed and authenticated in your project:

```bash
npx @localheroai/cli login
```

## More info

- [Localhero.ai](https://localhero.ai)
- [CLI documentation](https://localhero.ai/docs/cli-reference)
- [skills.sh](https://skills.sh/localheroai/agent-skill/localhero)
