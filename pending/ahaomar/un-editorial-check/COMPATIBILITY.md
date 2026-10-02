# Compatibility

**Verification date: 25 September 2026.** This document distinguishes native discovery documented by a host or specification from installation supported by the Vercel `skills` CLI. The CLI may create a host's documented skills path; installation support alone is not a claim that every host implements the full Agent Skills specification.

## Portable skill format

The canonical file is the repository-root `SKILL.md`. It uses a restricted portable frontmatter subset shared by the [Agent Skills specification](https://agentskills.io/specification) and current OpenCode documentation. The bundled portability validator enforces this exact restricted subset; it is not a general YAML parser.

| Field | Rule in this package |
|---|---|
| `name` | `un-editorial-check`; lower kebab-case; equal to the npm package and repository directory |
| `description` | Non-empty and no more than 1,024 characters; states what the skill does and when to use it |
| `license` | `MIT` |
| `compatibility` | Node.js 18 or later is required to run the bundled CLI |
| `metadata` | String-to-string values only |

The experimental `allowed-tools` field is not used. Host-specific frontmatter is not used. There are no committed host copies of `SKILL.md`, because they could drift. The `skills` CLI copies the canonical repository skill to a host directory or links to one canonical installed copy.

## Host matrix

| Host | Native discovery verified | `skills` CLI agent name | Project path | Global path | Boundary |
|---|---:|---|---|---|---|
| OpenCode 1.x | Version-dependent; not independently verified | `opencode` | `.opencode/skills/` or shared `.agents/skills/` | `~/.config/opencode/skills/` | The format is designed for OpenCode 1.x, but users must verify discovery in their exact 1.x release. |
| OpenCode 2.x | Yes | `opencode` | `.opencode/skills/`, `.agents/skills/`, `.claude/skills/` | `~/.config/opencode/skills/`, `~/.agents/skills/`, `~/.claude/skills/` | V2 derives the skill ID from the path; keep the directory equal to the frontmatter name. |
| Claude Code | Yes | `claude-code` | `.claude/skills/` | `~/.claude/skills/` | Claude API and Claude Code skill distribution are separate. This package is filesystem-based. |
| Codex | Yes | `codex` | `.agents/skills/` | `~/.codex/skills/` via CLI; official Codex authoring also documents `~/.agents/skills/` | `agents/openai.yaml` is optional UI metadata, not part of the portable format. |
| Kimi Code CLI | Yes | `kimi-code-cli` | `.agents/skills/` | `~/.agents/skills/` | Other Kimi products or version-specific `.kimi*` paths may differ. |
| Cursor | Host support is version-dependent | `cursor` | `.agents/skills/` via CLI | `~/.cursor/skills/` via CLI | The CLI installation is verified. Confirm the installed Cursor version supports Agent Skills at that path. |
| Gemini CLI | Yes | `gemini-cli` | `.agents/skills/` | `~/.gemini/skills/` | CLI support and other Gemini surfaces are not interchangeable. |
| Windsurf | Host support is version-dependent | `windsurf` | `.windsurf/skills/` via CLI | `~/.codeium/windsurf/skills/` via CLI | The CLI installation is verified. Confirm native discovery in the installed version; otherwise use a rules adapter. |
| Cline | Host support is version-dependent | `cline` | `.agents/skills/` via CLI | `~/.agents/skills/` via CLI | The CLI installation is verified. Confirm native discovery in the installed version; otherwise use a rules adapter. |
| GitHub Copilot | Yes, subject to product and surface | `github-copilot` | `.agents/skills/` | `~/.copilot/skills/` via CLI | Copilot Chat, IDE and CLI surfaces can differ. |
| Generic Agent Skills host | Depends on implementation | `universal` installs to `.agents/skills/` | `.agents/skills/<name>/SKILL.md` | Host-defined | A conforming host must load `SKILL.md`; execution still requires Node.js and filesystem access. |

## Exact installation commands

Run from the target project unless `--global` is shown:

```sh
npx skills add https://github.com/ahaomar/un-editorial-check
npx skills add https://github.com/ahaomar/un-editorial-check --skill un-editorial-check --agent opencode --yes
npx skills add https://github.com/ahaomar/un-editorial-check --skill un-editorial-check --agent claude-code --yes
npx skills add https://github.com/ahaomar/un-editorial-check --skill un-editorial-check --agent codex --yes
npx skills add https://github.com/ahaomar/un-editorial-check --skill un-editorial-check --agent kimi-code-cli --yes
npx skills add https://github.com/ahaomar/un-editorial-check --skill un-editorial-check --agent cursor --yes
npx skills add https://github.com/ahaomar/un-editorial-check --skill un-editorial-check --agent gemini-cli --yes
npx skills add https://github.com/ahaomar/un-editorial-check --skill un-editorial-check --agent windsurf --yes
npx skills add https://github.com/ahaomar/un-editorial-check --skill un-editorial-check --agent cline --yes
npx skills add https://github.com/ahaomar/un-editorial-check --skill un-editorial-check --agent github-copilot --yes
```

Add `--global` for user-level installation or `--copy` where symbolic links are unsuitable. Review the CLI prompt and target paths. The installer may be updated independently of this package.

### Manual installation

Download or clone this repository, then copy the complete package—not only `SKILL.md`—to the host's project or global directory above. The skill needs `bin/`, `lib/`, `rules/` and `config/`. Example for a project using the shared path:

```sh
mkdir -p .agents/skills/un-editorial-check
cp -R SKILL.md bin lib rules config README.md LICENSE .agents/skills/un-editorial-check/
```

Do not create recursive symbolic links. If a host lacks native skills, create a documented rules adapter that tells the agent to read the canonical `SKILL.md`; this package does not claim that every rules system loads `SKILL.md` natively.

## Agent invocation

After installation, invoke the skill using the host's skill mechanism—for example, by asking the agent to use `un-editorial-check`, or through the host's `/skills` or `$skill` selector. The agent should resolve bundled paths from the directory containing `SKILL.md` and run:

```sh
node <skill-base>/bin/check.mjs <paths> --format text
```

The angle-bracket path is a placeholder, not a shell redirection. Agents must not assume that their installation directory equals the current working directory.

## Host-specific differences

- OpenCode 1.x and 2.x have different frontmatter and precedence details. The portable format is designed for both, but native discovery in a given OpenCode 1.x release must be verified by the user; 2.x treats the path-derived ID as authoritative.
- Claude Code supports additional frontmatter and plugin features. They are intentionally absent.
- Codex can use optional `agents/openai.yaml` for display metadata and invocation policy. That file does not make the skill portable and is not required.
- Cursor, Windsurf and Cline versions may lag the shared specification. `skills` CLI installation support does not remove the need to verify host discovery.
- Product surfaces within a vendor can have separate skill stores. Installing in one surface does not install it in another.
- Use only the commands listed by the current `npx skills --help`. The CLI is released independently; rerun the help output when updating installer guidance.

## Sources

Sources were checked on **25 September 2026**:

- [Agent Skills specification](https://agentskills.io/specification)
- [Vercel `skills` CLI repository and supported-agent table](https://github.com/vercel-labs/skills)
- [OpenCode Agent Skills](https://opencode.ai/docs/skills/)
- [OpenCode 2 Agent Skills](https://opencode.ai/v2/docs/skills/)
- [Claude Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [OpenAI Codex skill authoring](https://developers.openai.com/codex/build-skills/)
- [Cursor skills documentation](https://cursor.com/docs/context/skills)
- [Cline skills documentation](https://docs.cline.bot/features/skills)
- [Kimi Code skills documentation](https://moonshotai.github.io/kimi-code/en/customization/skills)
- [Gemini CLI skills documentation](https://geminicli.com/docs/cli/skills/)
- [GitHub Copilot Agent Skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
