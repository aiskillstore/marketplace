---
name: chatgpt-app-builder
description: |
  Build ChatGPT Apps using the Apps SDK and MCP. Use when users want to:
  (1) Evaluate if their product should become a ChatGPT App
  (2) Design and implement MCP servers with widgets
  (3) Test apps locally and in ChatGPT
  (4) Prepare for App Store submission
  Triggers: "ChatGPT app", "Apps SDK", "build for ChatGPT",
  "ChatGPT integration", "MCP server for ChatGPT", "submit to ChatGPT"
license: MIT
compatibility: |
  Requires Node.js 18+, npm. Network access needed for testing with ngrok.
  Intended for Claude Code and similar filesystem-based agents.
metadata:
  author: Bayram Annakov (onsa.ai)
  version: "1.0.0"
  category: development
allowed-tools: Bash(npm:*) Bash(npx:*) Bash(node:*) Bash(ngrok:*) Read Write Edit Glob Grep
---

# ChatGPT App Builder

Build production-ready ChatGPT Apps from concept to App Store submission.

## Quick Start

```
New app?           → Start at Phase 1 (Fit Evaluation)
Have app-spec.md?  → Start at Phase 3 (Implementation)
App built?         → Start at Phase 4 (Testing)
Ready to ship?     → Start at Phase 5 (Deployment)
```

---

## Phase 1: Fit Evaluation

**Goal**: Determine if a ChatGPT App is right for this product.

### Step 1: Gather Context
Ask the user:
1. What does your product do?
2. Who are your users?
3. What API/data does it expose?
4. What actions can users take?

### Step 2: Apply Know/Do/Show Framework
Evaluate against three value pillars (see [fit_evaluation.md](references/fit_evaluation.md)):

| Pillar | Question | Strong Signal |
|--------|----------|---------------|
| **Know** | Does it provide data ChatGPT lacks? | Live prices, user-specific data, internal metrics |
| **Do** | Can it take real actions? | Create, update, delete, send, schedule |
| **Show** | Can it display better than text? | Lists, charts, maps, media galleries |

**Minimum requirement**: At least one pillar must be strong.

### Step 3: Check Blockers
Review [fit_evaluation.md](references/fit_evaluation.md) for:
- Prohibited categories (gambling, adult, crypto speculation)
- Data restrictions (no PCI, PHI, SSN, API keys)
- Age requirements (13+ audience)

### Step 4: Create Golden Prompt Set
Draft prompts for discovery testing:
- **5 direct prompts**: Explicitly name your product ("Show my TaskFlow tasks")
- **5 indirect prompts**: Describe intent without naming ("What should I work on?")
- **3 negative prompts**: Similar but shouldn't trigger ("Create a reminder")

### Step 5: Write app-spec.md
Create the specification file:

```markdown
# [Product Name] ChatGPT App Spec

## Product Context
- Name: [Product name]
- API Base: [API URL]
- Auth: [Bearer token / OAuth / None]

## Value Proposition
- Know: [What data does it provide?]
- Do: [What actions can it take?]
- Show: [What UI is needed?]

## Golden Prompts
### Direct (should trigger)
1. ...

### Indirect (should trigger)
1. ...

### Negative (should NOT trigger)
1. ...
```

**Output**: `app-spec.md` in project directory

---

## Phase 2: App Design

**Goal**: Define complete technical specification.

### Step 1: Define Tools (2-5)
Follow one-job-per-tool principle. See [chatgpt_app_best_practices.md](references/chatgpt_app_best_practices.md).

For each tool, specify:
```yaml
name: service_verb_noun  # e.g., taskflow_get_tasks
title: Human Readable Name
description: Use this when the user wants to... [be specific]
annotations:
  readOnlyHint: true/false
  destructiveHint: true/false
  openWorldHint: true/false
inputSchema:
  param1: type (required/optional)
  param2: enum["a", "b", "c"]
outputStructure:
  content: [text summary for model]
  structuredContent: {machine-readable data}
  _meta: {widget-only data}
```

### Step 2: Decide Widget Needs
Does the app need custom UI?

| Use Case | Widget Needed? | Component Type |
|----------|----------------|----------------|
| Task list with checkboxes | Yes | List with actions |
| Data display only | Maybe | Could use text |
| Maps, charts, media | Yes | Specialized |
| Multi-step workflow | Yes | Stateful widget |

See [widget_development.md](references/widget_development.md) for patterns.

### Step 3: Plan Authentication
If accessing user-specific data or write operations, auth is required.

See [oauth_integration.md](references/oauth_integration.md) for:
- Well-known endpoint setup
- Provider-specific guides (Auth0, Stytch)
- Tool-level securitySchemes

### Step 4: Update app-spec.md
Add technical specification:

```markdown
## Tools

### 1. service_get_items
- **Annotations**: readOnlyHint: true
- **Input**: { status?: "active" | "completed", limit?: number }
- **Output**:
  - content: "Found N items"
  - structuredContent: { items: [...] }
  - _meta: { fullData: [...] }

### 2. service_create_item
- **Annotations**: openWorldHint: true
- **Input**: { title: string, description?: string }
- **Output**: { id, title, created_at }

## Widget
- Type: List with action buttons
- Display modes: inline, fullscreen
- State: { selectedId, filter }

## Authentication
- Required: Yes
- Provider: Auth0
- Scopes: read:items, write:items
```

**Output**: Updated `app-spec.md` with full technical spec

---

## Phase 3: Implementation

**Goal**: Generate complete working project.

### Step 1: Initialize Project
Copy from assets and customize:

```bash
# Project structure
myapp-chatgpt/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts          # MCP server entry
│   ├── tools/            # Tool handlers
│   ├── widget/           # Widget source
│   └── types/            # TypeScript types
└── scripts/
    └── build-widget.ts   # Widget bundler
```

See [node_chatgpt_app.md](references/node_chatgpt_app.md) for complete patterns.

### Step 2: Implement MCP Server
Key components (from assets/server/):

1. **HTTP server with SSE transport** (required for ChatGPT Apps):
```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";

// GET /mcp - SSE stream connection
// POST /mcp/messages - Message handling
```

2. **Tool definitions with JSON Schema**:
```typescript
const tools: Tool[] = [{
  name: "service_get_items",
  title: "Get Items",
  description: "Use this when the user wants to see items...",
  inputSchema: { type: "object", properties: {...} },
  _meta: {
    "openai/outputTemplate": "ui://widget/app.html",
    "openai/widgetAccessible": true
  },
  annotations: { readOnlyHint: true, destructiveHint: false, openWorldHint: false }
}];
```

3. **Handler registration**:
```typescript
server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools }));
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  // Handle tool calls...
  return {
    content: [{ type: "text", text: `Found ${items.length} items` }],
    structuredContent: { items: items.slice(0, 10) },
    _meta: { fullItems: items }
  };
});
```

### Step 3: Implement Widget
Key patterns (from assets/widget/):

```typescript
// Access data
const output = window.openai.toolOutput;
const meta = window.openai.toolResponseMetadata;

// Invoke tools
await window.openai.callTool("service_action", { id: "123" });

// Persist state
window.openai.setWidgetState({ selectedId: "123" });

// Layout control
window.openai.notifyIntrinsicHeight(400);
await window.openai.requestDisplayMode({ mode: "fullscreen" });
```

See [widget_development.md](references/widget_development.md) for React hooks and patterns.

### Step 4: Build
```bash
npm install
npm run build  # Compiles server + bundles widget
```

### Step 5: Implementation Checklist

Before moving to testing, verify:

#### Widget Requirements
- [ ] Uses Apps SDK UI design tokens (see [apps_sdk_ui_tokens.md](references/apps_sdk_ui_tokens.md))
- [ ] Implements dark mode with CSS variable architecture
- [ ] Uses LoadingDots pattern for loading states (see [widget_ui_patterns.md](references/widget_ui_patterns.md))
- [ ] Calls `notifyIntrinsicHeight()` after all DOM changes
- [ ] Includes copy button feedback for copyable content
- [ ] Has show more/less for long lists (>3 items)
- [ ] Works on mobile (test at 375px width)
- [ ] Loading UI guards against re-initialization (see [widget_loading_patterns.md](references/widget_loading_patterns.md))
- [ ] SVG animations use `.style` property, not `setAttribute()` (see [widget_development.md](references/widget_development.md#common-widget-gotchas))

#### Security Requirements
- [ ] All user input is validated (see [security_patterns.md](references/security_patterns.md))
- [ ] HTML output uses safe DOM methods (textContent, createElement)
- [ ] External image URLs are proxied with domain whitelist and size limits (200KB)
- [ ] Rate limiting is implemented per session with LRU eviction

#### Server Requirements
- [ ] `/.well-known/openai-apps-challenge` endpoint returns challenge token
- [ ] `/privacy` endpoint returns HTML privacy policy
- [ ] `/terms` endpoint returns HTML terms of service
- [ ] `/mcp` endpoint handles SSE connections
- [ ] `/health` or `/` returns health check JSON
- [ ] CORS configured for ChatGPT domains only
- [ ] Security headers set on all responses
- [ ] **Session routing uses direct lookup by sessionId** (CRITICAL - see [troubleshooting.md](references/troubleshooting.md#critical-multi-connection-session-routing))
- [ ] Response size under 300KB total (remove duplicates, limit images)

#### Production Readiness (if deploying to production)
- [ ] OAuth tokens stored in database, not in-memory (see [oauth_integration.md](references/oauth_integration.md#production-considerations-token-storage))
- [ ] Mutation tools include idempotency checks (see [chatgpt_app_best_practices.md](references/chatgpt_app_best_practices.md#idempotency-keys))
- [ ] Disambiguation pattern for multi-match scenarios (see [chatgpt_app_best_practices.md](references/chatgpt_app_best_practices.md#disambiguation-pattern))
- [ ] Confirmation receipts for all mutations (see [chatgpt_app_best_practices.md](references/chatgpt_app_best_practices.md#confirmation-receipts))

**Output**: Complete project in working directory

---

## Phase 4: Testing

**Goal**: Verify the app works correctly.

### Step 1: Local Testing with MCP Inspector
```bash
# Terminal 1: Start server
npm run dev
# Server runs at http://localhost:8000

# Terminal 2: Run inspector
npx @modelcontextprotocol/inspector@latest http://localhost:8000/mcp
```

Verify:
- [ ] All tools appear in inspector
- [ ] Tool calls return expected structure
- [ ] Widget renders without errors

### Step 2: Create HTTPS Tunnel
```bash
ngrok http 8000
# Copy the https://xxx.ngrok.app URL
```

### Step 3: Create ChatGPT Connector
1. Go to ChatGPT → Settings → Connectors
2. Enable Developer Mode (Settings → Apps & Connectors → Advanced)
3. Create new connector:
   - Name: Your app name
   - Description: From app-spec.md
   - URL: `https://xxx.ngrok.app/mcp`
4. Click Create and verify tools appear

### Step 4: Test Golden Prompts
In a new ChatGPT conversation:
1. Enable your connector (+ button → More → select connector)
2. Test each golden prompt from app-spec.md
3. Verify:
   - [ ] Direct prompts trigger correctly
   - [ ] Indirect prompts trigger correctly
   - [ ] Negative prompts do NOT trigger
   - [ ] Widget renders properly
   - [ ] Actions work (if applicable)

### Step 5: Iterate
If issues found:
1. Fix code
2. Rebuild: `npm run build`
3. Refresh connector in ChatGPT settings
4. Re-test

See [troubleshooting.md](references/troubleshooting.md) for common issues and solutions.

**Output**: Working app tested in ChatGPT

---

## Phase 5: Deployment & Submission

**Goal**: Ship to production and App Store.

### Step 1: Deploy to Production
Generate deployment configs from assets/deploy/:

**Fly.io** (recommended):
```bash
fly launch
fly deploy
```

**Vercel/Cloudflare**: Ensure streaming HTTP support.

### Step 2: Update Connector
1. Replace ngrok URL with production URL
2. Verify connection in ChatGPT settings

### Step 3: Pre-Submission Checklist
See [submission_requirements.md](references/submission_requirements.md):

**Required**:
- [ ] Organization verified on OpenAI Platform
- [ ] All tools have clear descriptions
- [ ] Annotations correct (readOnlyHint, destructiveHint, openWorldHint)
- [ ] No prohibited content/commerce
- [ ] No restricted data collection
- [ ] Widget renders on mobile
- [ ] Test credentials with sample data prepared

**If auth required**:
- [ ] Well-known endpoints accessible
- [ ] Test account credentials documented
- [ ] OAuth flow completes successfully

### Step 4: Submit
1. Go to platform.openai.com/apps-manage
2. Enter MCP server URL
3. Add OAuth metadata (if applicable)
4. Complete submission form
5. Submit for review

### Step 5: Post-Submission
- Monitor email for review status
- Address any reviewer feedback
- Click Publish after approval

**Output**: App live in ChatGPT App Store

---

## External Resources

- [OpenAI Apps SDK Docs](https://developers.openai.com/apps-sdk)
- [Apps SDK Examples](https://github.com/openai/openai-apps-sdk-examples)
- [Apps SDK UI Kit](https://openai.github.io/apps-sdk-ui)
- [MCP Protocol Spec](https://modelcontextprotocol.io)
