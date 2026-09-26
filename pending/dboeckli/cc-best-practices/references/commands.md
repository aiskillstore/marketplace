# Claude Code Quick Reference

Source: https://code.claude.com/docs/en/best-practices

## Key Commands

| Command             | Purpose                                      |
| ------------------- | -------------------------------------------- |
| `/plan`             | Enter plan mode (explore/plan without edits) |
| `/clear`            | Reset context window                         |
| `/compact <hint>`   | Compact conversation with a focus hint       |
| `/rewind`           | Open checkpoint rewind menu                  |
| `/btw <question>`   | Side-question that doesn't enter history     |
| `/code-review`      | Adversarial bug review via subagent          |
| `/goal <condition>` | Set a stop condition Claude checks each turn |
| `/context`          | Verify which files Claude has loaded         |
| `/hooks`            | Browse configured hooks                      |
| `/permissions`      | Manage tool allowlists                       |
| `Esc`               | Stop Claude mid-action (context preserved)   |
| `Esc + Esc`         | Open rewind / summarize menu                 |

## Non-Interactive Mode Examples

```bash
# Structured output for CI
claude -p "List all API endpoints" --output-format json

# Streaming for large outputs
claude -p "Analyze this log file" --output-format stream-json --verbose

# Fan out across files
for file in $(cat files.txt); do
  claude -p "Migrate $file from React to Vue. Return OK or FAIL." \
    --allowedTools "Edit,Bash(git commit *)"
done

# Auto mode (uninterrupted)
claude --permission-mode auto -p "fix all lint errors"
```

## Common Failure Patterns

| Pattern                      | Symptom                                      | Fix                                                  |
| ---------------------------- | -------------------------------------------- | ---------------------------------------------------- |
| **Kitchen-sink session**     | Context full of unrelated tasks              | `/clear` between unrelated tasks                     |
| **Correcting over and over** | Same mistake after 2+ corrections            | `/clear`, write a better prompt                      |
| **Over-specified CLAUDE.md** | Claude ignores rules buried in noise         | Prune ruthlessly; convert repetitive checks to hooks |
| **Trust-then-verify gap**    | Plausible-looking code with edge-case holes  | Always provide tests or a verification script        |
| **Infinite exploration**     | Claude reads hundreds of files, context full | Scope narrowly or use subagents                      |
