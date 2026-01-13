# Slash Command Encoder - Workflow

## Complete Script

```bash
#!/bin/bash
# command-creation-workflow.sh

# Phase 1: Design Interface
cat > command-schema.json <<EOF
{
  "name": "analyze",
  "parameters": [{"name": "path", "type": "string", "required": true}]
}
EOF

# Phase 2: Generate Code
npx claude-flow@alpha command generate --schema command-schema.json --output commands/analyze.js

# Phase 3: Test
npx claude-flow@alpha command test --command analyze

# Phase 4: Document
npx claude-flow@alpha command docs --command analyze --output docs/analyze.md

# Phase 5: Deploy
npx claude-flow@alpha command build --commands ./commands
npx claude-flow@alpha command install --from dist/commands.bundle.js
npx claude-flow@alpha analyze ./src
```

## Success Criteria
- [ ] Command interface designed
- [ ] Handler generated and tested
- [ ] Documentation complete
- [ ] Command deployed successfully
