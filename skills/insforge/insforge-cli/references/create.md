# npx -y @insforge/cli create

Create a new InsForge project.

## Syntax

```bash
npx -y @insforge/cli create [options]
```

## Options

| Option | Description |
|--------|-------------|
| `--name <name>` | Project name |
| `--org-id <id>` | Organization ID |
| `--region <region>` | Region: `us-east`, `us-west`, `eu-central`, `ap-southeast` |
| `--template <template>` | Template: `react`, `nextjs`, `empty` |
| `--json` | Non-interactive mode. Skips all value-collection prompts (including the "Directory name:" prompt) and errors out if any required flag is missing. Required for agent / CI use. |

## Interactive Mode

Without flags, the command prompts for organization, project name, region, and template.

## Non-Interactive Mode

For CI/CD or agent use, pass `--json` along with all required flags:

```bash
npx -y @insforge/cli create --json --name my-app --org-id org_123 --region us-east --template react
```

`--json` skips value-collection prompts (text inputs like `Directory name:`, pickers like organization / region) and errors out if any required flag is missing. The `-y` flag is a different feature — it only auto-accepts Y/N confirmations and does NOT suppress value-collection prompts. For `create` specifically, `--json` alone is sufficient (there are no Y/N confirmations); for destructive commands like `delete`, agents should pass both `--json` and `-y`. Agents sandboxed from stdin (e.g., Codex) hang on any unsuppressed prompt — always pass `--json` for programmatic create.

## What It Does

1. Creates the project via the InsForge Platform API
2. Waits for the project to become active (polls every 3s, timeout 120s)
3. Fetches the project's API key
4. Downloads template files (if not `empty`)
5. Installs InsForge Agent Skills via `npx skills add insforge/agent-skills`
6. Creates `.insforge/project.json` in the current directory

## Output

Project details: ID, name, appkey, region, and OSS host URL.

## Examples

```bash
# Interactive — prompts for everything
npx -y @insforge/cli create

# Non-interactive with all options (agents, CI)
npx -y @insforge/cli create --json --name blog-app --org-id org_abc --region us-east --template react

# Create with empty template (no frontend scaffolding)
npx -y @insforge/cli create --json --name api-only --org-id org_abc --region eu-central --template empty
```

## Notes

- Requires authentication (`npx -y @insforge/cli login` first).
- Creates `.insforge/project.json` which links the directory to the project.
- Agent skills are auto-installed into `.agents/skills/insforge/`.
