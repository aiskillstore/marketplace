# Slash Command Encoder - Quick Start

Create ergonomic slash commands for fast access to micro-skills.

## Quick Start

```bash
# 1. Design command
cat > command-schema.json <<EOF
{
  "name": "analyze",
  "description": "Analyze codebase",
  "parameters": [{"name": "path", "type": "string", "required": true}]
}
EOF

# 2. Generate handler
npx claude-flow@alpha command generate --schema command-schema.json

# 3. Test command
npx claude-flow@alpha command test --command analyze --input '{"path": "./src"}'

# 4. Deploy
npx claude-flow@alpha command install --from dist/commands.bundle.js
```

## Agents
- **coder:** Command implementation
- **base-template-generator:** Template generation

## Success Metrics
- Registration: <100ms
- Validation: <50ms
- Execution: <2s
