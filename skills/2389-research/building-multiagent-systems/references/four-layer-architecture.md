# Four-Layer Architecture for Multi-Agent Systems

Every agent in a multi-agent system should follow the four-layer architecture for testability, safety, and modularity.

## The Stack

```
┌─────────────────────────────────────────┐
│  1. Reasoning Layer (LLM)               │  Plans, critiques, decides which tools to call
├─────────────────────────────────────────┤
│  2. Orchestration Layer                 │  Validates, routes, enforces policy, spawns sub-agents
├─────────────────────────────────────────┤
│  3. Tool Bus                            │  Schema validation, tool execution coordination
├─────────────────────────────────────────┤
│  4. Deterministic Adapters              │  File I/O, APIs, shell commands, database access
└─────────────────────────────────────────┘
```

## Why This Matters for Multi-Agent Systems

- Each sub-agent has the same four layers - consistency across the system
- Orchestration layer (Layer 2) is where you spawn sub-agents and coordinate their work
- Tools (Layer 4) must be deterministic - no LLM calls inside tool implementations
- Clear separation makes debugging multi-agent interactions tractable

## Orchestration Layer Choices

- **YOLO Mode** (like pi-mono): Minimal validation, fast iteration, trust LLM decisions
- **Safety-First** (like Claude Code): User approval, policy enforcement, guardrails
- **Hybrid**: Safety for dangerous operations, YOLO for safe ones

Choose based on trust level and production environment. Multi-agent systems often use hybrid: parent agent has safety layers, sub-agents run in YOLO mode within controlled scopes.

## The Deterministic Boundary

**Critical Rule**: Everything below the Reasoning Layer must be deterministic.

```typescript
// ❌ WRONG: LLM call in a tool (breaks determinism)
async function analyzeTool(code: string) {
  const analysis = await llm.generate(`Analyze this code: ${code}`);
  return analysis;
}

// ✅ RIGHT: LLM in orchestration, tools are deterministic
async function analyzeCode(code: string) {
  // Layer 2: Orchestration decides to spawn analyzer sub-agent
  const analyzer = await spawnAgent('code-analyzer', { model: 'haiku' });

  // Layer 3: Tool bus validates and routes
  const result = await analyzer.executeTool('parse_ast', { code });

  // Layer 4: parse_ast is deterministic (no LLM)
  return result;
}
```

**Why this matters**: Deterministic tools are testable with unit tests. Non-deterministic tools (with LLM calls) can only be integration-tested and add unpredictability to multi-agent coordination.

## Schema-First Tool Design

Every tool must have a typed schema defined before implementation. This is critical in multi-agent systems where sub-agents need to discover and use tools dynamically.

```typescript
// Define schema FIRST
const editSchema = {
  name: "edit",
  description: "Edit a file by replacing exact text",
  parameters: {
    type: "object",
    properties: {
      path: { type: "string", description: "Path to file" },
      oldText: { type: "string", description: "Text to replace" },
      newText: { type: "string", description: "Replacement text" }
    },
    required: ["path", "oldText", "newText"]
  }
};

// Then implement
async function editTool(params: SchemaType<typeof editSchema>) {
  // TypeScript/validation ensures params match schema
  const { path, oldText, newText } = params;
  // ... deterministic implementation ...
}
```

**Benefits for multi-agent systems**:
- Sub-agents can discover available tools via schema inspection
- Parent agents can validate sub-agent tool calls before execution
- Schema serves as contract between agents
- LLMs learn tool usage from schema descriptions
