# AI template examples

## What is an AI template?

An **AI template** is a pre-built agent configuration — a ready-to-use agent blueprint with instructions, model settings, and action configuration already defined. Templates capture common agent patterns (lead research, company classification, email drafting) so you don't have to configure an agent from scratch.

**Always check templates before creating an agent.** Even if no template is a perfect match, they provide:
- A proven system prompt structure for the use case
- A recommended language model and temperature setting
- A list of actions and resources to consider attaching

AI templates are read-only. You discover them by listing, then use their configuration as a starting point when creating or updating an agent.

## List all AI templates

```bash
cargo-ai ai template list
```

Response:

```json
{
  "templates": [
    {
      "slug": "lead-researcher",
      "name": "Lead Researcher",
      "description": "Researches a prospect's company, role, and contact details",
      "languageModelSlug": "gpt-4o",
      "temperature": 0.3
    },
    {
      "slug": "company-classifier",
      "name": "Company Classifier",
      "description": "Classifies a company by industry, size, and ICP fit",
      "languageModelSlug": "gpt-4.1-mini",
      "temperature": 0.1
    },
    {
      "slug": "email-drafter",
      "name": "Email Drafter",
      "description": "Drafts personalised outbound emails based on enrichment data",
      "languageModelSlug": "gpt-4o",
      "temperature": 0.7
    }
  ]
}
```

Key fields:

- **`slug`** — identifier for reference
- **`name`** — human-readable name
- **`description`** — what the agent does
- **`languageModelSlug`** — recommended model for this use case
- **`temperature`** — recommended temperature setting

## Use a template to create an agent

The standard pattern:

1. List templates to find the right one
2. Create a new agent using the template's recommended settings
3. Attach any files or MCP servers the agent needs
4. Start chatting or embed the agent in a workflow

```bash
# 1. Find the right template
cargo-ai ai template list
# → Find "lead-researcher"

# 2. Create an agent
cargo-ai ai agent create \
  --name "Lead Researcher" \
  --icon-color purple --icon-face 🔍
# → Extract agent.uuid

# 3. Configure the draft release with template settings
cargo-ai ai release update-draft --agent-uuid <agent-uuid> \
  --system-prompt "You are a research assistant. Given a company domain and a contact name, find their role, LinkedIn profile, and email address. Be concise and structured." \
  --language-model-slug gpt-4o \
  --temperature 0.3

# 4. Attach a knowledge file (optional)
cargo-ai content file upload --file ./icp-criteria.pdf
# → Extract file.uuid — attach to agent via release update-draft --resources

# 5. Test with a message
cargo-ai ai chat create \
  --trigger '{"type":"draft"}' \
  --agent-uuid <agent-uuid> \
  --name "Test session"
# → Extract chat.uuid

cargo-ai ai message create \
  --chat-uuid <chat-uuid> \
  --parts '[{"type":"text","text":"Research the VP of Sales at acme.com"}]'
# → Poll with: cargo-ai ai message get <assistant-msg-uuid>
```

## Use a template to configure an agent in a workflow node

AI templates also inform how to configure an inline `agent` node inside a workflow node graph. Use the template's `languageModelSlug` and `temperature` in the node's `advancedSettings`:

```json
{
  "uuid": "ab12cd34-ab12-4ab1-aab1-ab12cd34ef56",
  "slug": "research_lead",
  "kind": "native",
  "actionSlug": "agent",
  "config": {
    "prompt": {
      "kind": "templateExpression",
      "expression": "Research the person {{nodes.start.first_name}} {{nodes.start.last_name}} at {{nodes.start.domain}}. Return their role, LinkedIn URL, and a 2-sentence summary.",
      "instructTo": "none",
      "fromRecipe": false
    },
    "advancedSettings": {
      "languageModelSlug": "gpt-4o",
      "temperature": 0.3,
      "maxSteps": 5
    }
  },
  "childrenUuids": ["cd34ef56-cd34-4cd3-acd3-cd34ef567890"],
  "fallbackOnFailure": false,
  "position": { "x": 0, "y": 166 }
}
```

See `cargo-orchestration/references/nodes.md` for the full node creation guide.

## Template-to-agent quick reference

| Template slug         | Use case                     | Recommended model  | Temperature |
| --------------------- | ---------------------------- | ------------------ | ----------- |
| `lead-researcher`     | Prospect research            | `gpt-4o`           | 0.3         |
| `company-classifier`  | Industry / ICP classification| `gpt-4.1-mini`     | 0.1         |
| `email-drafter`       | Personalised outbound emails | `gpt-4o`           | 0.7         |
