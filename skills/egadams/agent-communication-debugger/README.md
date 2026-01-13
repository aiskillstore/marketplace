# Agent Communication Debugger Skill

A comprehensive debugging skill for the A2A (Agent-to-Agent) communication system.

## What This Skill Does

Provides systematic diagnosis and troubleshooting for:
- Agent status and health checks
- Message routing issues
- Transport layer connectivity
- Configuration validation
- Log analysis
- Common problem resolution

## When Claude Uses This Skill

Claude will automatically load this skill when you ask about:
- "debug agent communication"
- "why isn't the coder agent responding"
- "check agent status"
- "orchestrator routing problems"
- "messages not being delivered"
- "agent health check"

## Skill Structure

```
agent-debug/
├── SKILL.md               # Main skill instructions
├── README.md              # This file
├── common_issues.md       # Detailed troubleshooting guide
└── scripts/
    └── test_message.py    # Message delivery test script
```

## Quick Start

### Using the Skill

Simply ask Claude questions like:

```
Can you debug why my agents aren't communicating?
```

```
Check the status of the orchestrator agent
```

```
The coder agent isn't responding to messages, help me diagnose
```

Claude will:
1. Load the agent-debug skill automatically
2. Follow the diagnostic workflow
3. Run necessary checks
4. Provide specific solutions

### Running the Test Script Manually

You can also run the test script directly:

```bash
python .claude/skills/agent-debug/scripts/test_message.py
```

This will:
- Send a test message to the orchestrator
- Check for responses
- Verify agent processes are running
- Provide a diagnostic summary

## Features

### Systematic Diagnostics

The skill provides step-by-step diagnostics:
1. Check agent status (running/stopped)
2. Inspect configurations (agent.json files)
3. Analyze logs for errors
4. Verify message transport
5. Test message delivery
6. Diagnose routing issues
7. Check environment variables
8. Restart agents if needed

### Common Issues Guide

The `common_issues.md` file covers:
- Messages not being delivered
- Routing to wrong agent
- Agent not generating responses
- Duplicate message processing
- Transport connectivity problems
- Orchestrator not starting

### Quick Diagnostic Checklist

A handy checklist to run through:
- [ ] All required agents running
- [ ] WebSocket server active (if used)
- [ ] Agent configs valid
- [ ] Agents discovered by orchestrator
- [ ] API keys set
- [ ] Recent log activity
- [ ] No Python exceptions
- [ ] Test message succeeds
- [ ] Routing selects correct agent

## Example Usage

### Example 1: Quick Health Check

**You:** Check if all agents are running properly

**Claude will:**
1. Run `ps aux` to check processes
2. Verify orchestrator, coder, tester agents
3. Check logs for recent activity
4. Report status and any issues

### Example 2: Routing Problem

**You:** Messages are going to dashboard-agent instead of coder-agent

**Claude will:**
1. Check orchestrator's routing decisions in logs
2. Verify coder-agent is discovered
3. Check routing keywords and LLM prompts
4. Suggest fixes (update keywords, restart with API key)

### Example 3: No Response

**You:** Orchestrator receives my message but nothing happens

**Claude will:**
1. Check orchestrator logs for processing
2. Verify routing decision
3. Check target agent is running
4. Check target agent logs for errors
5. Identify missing dependencies or API keys

## Integration with Agent System

This skill is designed specifically for the agent system in:
```
a2a_communicating_agents/
├── orchestrator_agent/
├── coder_agent/
├── tester_agent/
├── agent_messaging/
└── storage/
```

It understands:
- Agent discovery via agent.json files
- Message routing through orchestrator
- Transport layers (WebSocket, RAG board)
- Log locations and formats
- Common configuration patterns

## Requirements

- Python 3.10+
- Rich library (for test script)
- Agent messaging system installed
- Access to agent processes and logs

## Maintenance

### Updating the Skill

To add new diagnostic capabilities:

1. Edit `SKILL.md` to add new workflow steps
2. Update `common_issues.md` with new issues and solutions
3. Extend test script if needed for new checks

### Adding New Agents

When adding new agents to the system:

1. Update routing keyword mappings in examples
2. Add agent-specific checks to diagnostic workflow
3. Document common issues for that agent

## Tips for Best Results

1. **Be specific:** "coder agent not responding" is better than "agent problem"
2. **Provide context:** Mention what you tried and what error you got
3. **Share symptoms:** "no response" vs "wrong response" lead to different diagnostics
4. **Run test script:** Provides baseline data for Claude to analyze

## Troubleshooting the Skill Itself

If Claude doesn't load the skill when expected:

1. Check the skill description contains relevant keywords
2. Make sure SKILL.md has valid YAML frontmatter
3. Try more explicit requests: "Use the agent-debug skill to check status"
4. Verify file is at: `.claude/skills/agent-debug/SKILL.md`

## Contributing

To improve this skill:
1. Add new common issues to `common_issues.md`
2. Enhance test script with more checks
3. Add examples for new scenarios
4. Document new agent types or configurations

## Related Skills

- May want to create additional skills for:
  - Performance monitoring
  - Agent development/creation
  - Message board analysis
  - Transport layer debugging

---

**Version:** 1.0
**Author:** Claude Code Collective
**Last Updated:** 2024-12-05
