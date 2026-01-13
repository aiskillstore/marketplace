---
name: copilot-mcp-server
description: Direct access to GitHub Copilot MCP server tools for AI-powered development assistance
license: MIT
---

# Copilot MCP Server

When to use this skill:
- When you need direct access to Copilot AI models for specific tasks
- When you want to use Copilot's specialized tools (review, debug, explain, etc.)
- When you need AI assistance outside of the copilot-flow workflow

## Available MCP Tools

### Core Tools

#### ask-copilot
General-purpose AI assistant for coding help, debugging, and architecture design.

```javascript
mcp__plugin__copilot__ask-copilot(
  prompt="string",           // Required: The question or task for Copilot
  context="string",          // Optional: Additional context
  model="string",            // Optional: Specific model to use (default: claude-sonnet-4.5)
  allowAllTools=true/false   // Optional: Allow Copilot to use all available tools
)
```

#### copilot-review
Professional code review with focus on specific areas.

```javascript
mcp__plugin__copilot__copilot-review(
  code="string",                      // Required: Code to review
  focusAreas=["security", "performance", "maintainability", "best-practices"]  // Optional: Specific areas to focus
)
```

#### copilot-explain
Get detailed explanations of code snippets.

```javascript
mcp__plugin__copilot__copilot-explain(
  code="string",      // Required: Code to explain
  model="string"      // Optional: Model to use
)
```

#### copilot-debug
Debug errors in code with context-aware analysis.

```javascript
mcp__plugin__copilot__copilot-debug(
  code="string",      // Required: Code with error
  error="string",     // Required: Error message
  context="string"    // Optional: Additional context
)
```

#### copilot-refactor
Get suggestions for code refactoring and improvements.

```javascript
mcp__plugin__copilot__copilot-refactor(
  code="string",      // Required: Code to refactor
  goal="string"       // Required: Refactoring goal (e.g., "improve performance")
)
```

#### copilot-test-generate
Generate unit tests for existing code.

```javascript
mcp__plugin__copilot__copilot-test-generate(
  code="string",        // Required: Code to test
  framework="string"    // Optional: Testing framework (e.g., jest, pytest, mocha)
)
```

#### copilot-suggest
Get CLI command suggestions for specific tasks.

```javascript
mcp__plugin__copilot__copilot-suggest(
  task="string",       // Required: Task description
  model="string"       // Optional: Model to use
)
```

### Session Management

#### copilot-session-start
Start a new conversation session with context tracking.

```javascript
mcp__plugin__copilot__copilot-session_start()
```

#### copilot-session-history
Retrieve conversation history for continuity.

```javascript
mcp__plugin__copilot__copilot-session_history(
  sessionId="string"   // Optional: Specific session ID
)
```

## Model Selection

Choose from available models based on task complexity:

### claude-sonnet-4.5 (default)
- Best for: System design, architecture decisions, code review, performance optimization
- Balance of capability and speed

### claude-opus-4.5
- Best for: Complex problems requiring strict execution
- Highest reasoning capability

### claude-haiku-4.5
- Best for: Quick syntax queries, simple logic questions, API usage
- Fastest response

### gemini-3-pro-preview
- Best for: Flutter, Angular, GCP, Firebase, Google Cloud development
- Google ecosystem specialization

### gpt-5-mini (unlimited usage)
- Best for: Concept explanations, general technical questions, documentation queries
- No usage limits for Pro+ subscribers

### gpt-5.1-codex / gpt-5.1-codex-max
- Best for: Complex algorithms, system refactoring, large feature development
- Advanced code generation

### gpt-5.2
- Best for: Complex reasoning with large context
- Highest comprehension

## Usage Examples

### Code Implementation
```javascript
mcp__plugin__copilot__ask-copilot(
  prompt="Implement a REST API endpoint for user authentication with JWT",
  model="claude-sonnet-4.5",
  allowAllTools=true
)
```

### Security Review
```javascript
mcp__plugin__copilot__copilot_review(
  code=`function login(username, password) {
    const query = \`SELECT * FROM users WHERE username = '\${username}' AND password = '\${password}'\`;
    return db.query(query);
  }`,
  focusAreas=["security", "sql-injection", "authentication"]
)
```

### Error Debugging
```javascript
mcp__plugin__copilot__copilot_debug(
  code="const result = await fetchData().json;",
  error="TypeError: fetchData(...).json is not a function",
  context="Trying to parse JSON response from API"
)
```

### Test Generation
```javascript
mcp__plugin__copilot__copilot_test_generate(
  code=`function isPrime(n) {
    if (n <= 1) return false;
    for (let i = 2; i * i <= n; i++) {
      if (n % i === 0) return false;
    }
    return true;
  }`,
  framework="jest"
)
```

## Best Practices

### Do
- Be specific in your prompts
- Provide context when available
- Choose appropriate model for task complexity
- Use session management for related queries
- Focus review on specific areas

### Don't
- Use overly broad prompts like "write code"
- Overuse powerful models for simple tasks
- Pass empty parameters
- Ask for review on all areas without focus
- Mix unrelated queries in one session

## Error Handling

If MCP server is unavailable:
1. Check GitHub Copilot CLI authentication
2. Verify MCP server configuration
3. Restart Claude Code or your MCP client

## Integration Notes

- This skill provides direct tool access
- For structured workflow, use copilot-flow-integration skill
- All tools require active GitHub Copilot subscription
- Usage counts towards Copilot API limits

## Keywords
copilot, mcp, ai, code review, debugging, testing, refactoring, github copilot, claude, gpt, gemini