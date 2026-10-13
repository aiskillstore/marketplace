# Agent examples

## List all agents

```bash
cargo-ai ai agent list
```

## Find an agent by name

```bash
cargo-ai ai agent list
# → Scan the "name" fields in the response to find the target agent UUID
```

## Create an agent

```bash
cargo-ai ai agent create \
  --name "Lead Researcher" \
  --icon-color purple --icon-face 🔍 \
  --description "Researches and qualifies leads using web data"
```

## Create an agent in a folder

Folders are managed by the [`cargo-workspace-management`](../../../cargo-workspace-management/SKILL.md) skill — see its `references/examples/folders.md` for create/list/update.

```bash
cargo-ai workspaceManagement folder list
# → Find the folder UUID (kind: "agent")

cargo-ai ai agent create \
  --name "Lead Researcher" \
  --icon-color purple --icon-face 🔍 \
  --folder-uuid <folder-uuid>
```

## Configure and deploy an agent (full workflow)

```bash
# 1. Create the agent
cargo-ai ai agent create \
  --name "Company Scorer" \
  --icon-color green --icon-face 📊
# → agent.uuid

# 2. Get the draft release
cargo-ai ai release get-draft --agent-uuid <agent-uuid>
# → release.uuid

# 3. Configure the draft: set model, temperature, prompt
cargo-ai ai release update-draft --agent-uuid <agent-uuid> \
  --language-model-slug gpt-4o-mini \
  --temperature 0.0 \
  --max-steps 5 \
  --system-prompt "You are a company scoring assistant. Given a company record, score it from 1-10 based on fit criteria."

# 4. Deploy the draft
cargo-ai ai release deploy-draft --agent-uuid <agent-uuid> \
  --integration-slug openai \
  --language-model-slug gpt-4o-mini \
  --actions '[]' \
  --mcp-clients '[]' \
  --resources '[]' \
  --capabilities '[]' \
  --suggested-actions '[]' \
  --description "Initial deployment with scoring prompt"
```

## Update an agent's name and description

```bash
cargo-ai ai agent update --uuid <agent-uuid> \
  --name "Senior Lead Researcher" \
  --description "Advanced lead research with enrichment capabilities"
```

## Move an agent to a different folder

```bash
cargo-ai ai agent update --uuid <agent-uuid> --folder-uuid <folder-uuid>
```

## Remove an agent

```bash
cargo-ai ai agent remove <agent-uuid>
```

## Create an agent from a template

```bash
# 1. Browse templates — the response is complete, not a summary
cargo-ai ai template list

# 2. Pick one out of that same response (there is no `template get`)
cargo-ai ai template list | jq '.templates[] | select(.slug == "<template-slug>")'
# → Copy the systemPrompt, actions, resources, model settings

# 3. Create the agent
cargo-ai ai agent create \
  --name "My Custom Agent" \
  --icon-color blue --icon-face 🤖

# 4. Apply template settings to the draft
cargo-ai ai release update-draft --agent-uuid <agent-uuid> \
  --system-prompt "<from template>" \
  --language-model-slug <from template> \
  --temperature <from template>

# 5. Deploy
cargo-ai ai release deploy-draft --agent-uuid <agent-uuid> \
  --integration-slug <from template> \
  --language-model-slug <from template> \
  --actions '[]' \
  --mcp-clients '[]' \
  --resources '[]' \
  --capabilities '[]' \
  --suggested-actions '[]'
```

## List releases for an agent

```bash
cargo-ai ai release list --agent-uuid <agent-uuid>
```

## View the current live configuration

```bash
cargo-ai ai agent get <agent-uuid>
# → .deployedRelease contains the full live config (prompt, model, actions, resources)
```
