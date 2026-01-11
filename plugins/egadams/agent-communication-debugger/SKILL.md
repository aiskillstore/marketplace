---
name: Agent Communication Debugger
description: Diagnoses and debugs A2A agent communication issues including agent status, message routing, transport connectivity, and log analysis. Use when agents aren't responding, messages aren't being delivered, routing is incorrect, or when debugging orchestrator, coder-agent, tester-agent communication problems.
allowed-tools: Bash, Read, Grep, Glob
---

# Agent Communication Debugger

Debug and diagnose issues with the A2A (Agent-to-Agent) communication system, including the orchestrator, coder-agent, tester-agent, and message transport layers.

## Prerequisites

- A2A agent system located in `a2a_communicating_agents/`
- Python 3.10+ environment
- Access to agent logs in `logs/` directory
- Agent configurations in respective `agent.json` files

## Instructions

### 1. Check Agent Status

First, determine which agents are running:

```bash
# Check all agent processes
ps aux | grep -E "(orchestrator|coder|tester|websocket)_agent|main.py" | grep -v grep
```

Look for:
- `orchestrator_agent/main.py`
- `coder_agent/main.py`
- `tester_agent/main.py`
- `websocket_server.py`

**Common issues:**
- Agent process not found → Agent isn't running, needs to be started
- Multiple instances → Duplicate processes causing conflicts

### 2. Inspect Agent Configurations

Read the agent configuration files to verify capabilities and topics:

```bash
# View orchestrator config
cat a2a_communicating_agents/orchestrator_agent/agent.json

# View coder agent config
cat a2a_communicating_agents/coder_agent/agent.json

# View tester agent config (if exists)
cat a2a_communicating_agents/tester_agent/agent.json
```

**Verify:**
- Agent names match expected values
- Topics are correctly defined
- Capabilities describe what the agent does
- No JSON syntax errors

### 3. Check Agent Logs

Examine logs for errors and message flow:

```bash
# View orchestrator logs (last 50 lines)
tail -50 logs/orchestrator.log

# View all logs with timestamps
tail -f logs/*.log

# Search for specific errors
grep -i "error\|exception\|failed" logs/*.log

# Check for routing decisions
grep -i "routing to\|routed to" logs/orchestrator.log
```

**Look for:**
- Connection errors
- Routing decisions showing wrong agent selection
- JSON parsing errors
- Message processing failures

### 4. Verify Message Transport

Check if the message transport (WebSocket or RAG board) is working:

```bash
# Check if WebSocket server is running
ps aux | grep websocket_server | grep -v grep
netstat -tlnp 2>/dev/null | grep 8765 || ss -tlnp 2>/dev/null | grep 8765

# Check RAG board storage
ls -lh a2a_communicating_agents/storage/
ls -lh storage/

# Check recent messages in message board
tail -20 storage/message_board.jsonl 2>/dev/null || echo "Message board not found"
```

**Expected:**
- WebSocket server on port 8765 (if using WebSocket transport)
- Recent messages in storage/message_board.jsonl (if using RAG transport)
- No permission errors accessing storage

### 5. Test Message Sending

Use the provided test script to send a message and verify delivery:

```bash
# Send a test message to orchestrator
python .claude/skills/agent-debug/scripts/test_message.py
```

This script will:
1. Send a test message to the orchestrator topic
2. Wait for response
3. Show message delivery status
4. Display any responses received

### 6. Diagnose Routing Issues

If messages reach orchestrator but route to wrong agent:

**Check orchestrator's routing logic:**
```bash
# View the decide_route method
grep -A 50 "def decide_route" a2a_communicating_agents/orchestrator_agent/main.py
```

**Check priority keyword mappings:**
```bash
# View fallback routing keywords
grep -A 20 "priority_mappings = {" a2a_communicating_agents/orchestrator_agent/main.py
```

**Verify agent discovery:**
```bash
# Check discovered agents in logs
grep "Discovered.*agents" logs/orchestrator.log | tail -5
```

**Common routing issues:**
- Agent not discovered → Check agent.json exists and is valid
- Wrong agent selected → Keywords don't match, update priority_mappings
- Null target → No suitable agent found, check agent topics/capabilities

### 7. Check Environment Variables

Verify API keys and configuration:

```bash
# Check if OPENAI_API_KEY is set (don't display value)
env | grep -E "(OPENAI|API_KEY)" | sed 's/=.*/=***HIDDEN***/'

# Check model configuration
grep -E "(model|MODEL)" .env 2>/dev/null | sed 's/=.*/=***HIDDEN***/' || echo "No .env file"
```

**Required environment variables:**
- `OPENAI_API_KEY` - For LLM-based routing and code generation
- `ORCHESTRATOR_MODEL` or `OPENAI_MODEL` - Model to use (default: gpt-5-mini)
- `CODER_MODEL` - Model for coder agent (optional, defaults to OPENAI_MODEL)

### 8. Restart Agents (if needed)

If agents are stuck or not responding:

```bash
# Stop all agents
pkill -f "orchestrator_agent/main.py"
pkill -f "coder_agent/main.py"
pkill -f "tester_agent/main.py"
pkill -f "websocket_server.py"

# Wait a moment
sleep 2

# Start WebSocket server (if using)
cd a2a_communicating_agents
nohup python agent_messaging/websocket_server.py > ../logs/websocket.log 2>&1 &

# Start orchestrator
nohup python orchestrator_agent/main.py > ../logs/orchestrator.log 2>&1 &

# Start coder agent
nohup python coder_agent/main.py > ../logs/coder.log 2>&1 &

# Verify they started
sleep 3
ps aux | grep -E "(orchestrator|coder|websocket)" | grep -v grep
```

### 9. Common Issues and Solutions

See [common_issues.md](common_issues.md) for a detailed troubleshooting guide covering:
- Messages not being delivered
- Routing to wrong agent
- Agent not generating responses
- Duplicate message processing
- Transport connectivity problems

## Quick Diagnostic Checklist

Run through this checklist systematically:

- [ ] All required agents are running (orchestrator, coder, tester)
- [ ] WebSocket server is running (if using WebSocket transport)
- [ ] Agent configuration files are valid JSON
- [ ] Orchestrator discovered all agents (check logs)
- [ ] OPENAI_API_KEY is set in environment
- [ ] Recent log entries show activity
- [ ] No Python exceptions in logs
- [ ] Test message sends and receives successfully
- [ ] Routing decisions select correct agent

## Examples

### Example 1: Agent Not Responding to Messages

User problem:
```
I'm sending messages to the orchestrator but getting no response
```

Debug workflow:

1. Check if orchestrator is running:
   ```bash
   ps aux | grep orchestrator_agent | grep -v grep
   ```
   Result: No process found → Orchestrator isn't running

2. Check logs for crash:
   ```bash
   tail -50 logs/orchestrator.log
   ```
   Result: ImportError for OpenAI package

3. Solution: Install missing dependency
   ```bash
   pip install openai
   ```

4. Restart orchestrator:
   ```bash
   cd a2a_communicating_agents
   nohup python orchestrator_agent/main.py > ../logs/orchestrator.log 2>&1 &
   ```

5. Verify it's running:
   ```bash
   ps aux | grep orchestrator_agent | grep -v grep
   tail -10 logs/orchestrator.log
   ```

### Example 2: Messages Routing to Wrong Agent

User problem:
```
I asked for code but it routed to dashboard-agent instead of coder-agent
```

Debug workflow:

1. Check orchestrator discovered coder-agent:
   ```bash
   grep "Discovered.*agents" logs/orchestrator.log | tail -1
   ```
   Result: Shows coder-agent in list ✓

2. Check routing decision in logs:
   ```bash
   grep -A 5 "please write.*code" logs/orchestrator.log
   ```
   Result: Shows routing to dashboard-agent

3. Check routing logic:
   ```bash
   grep -A 30 "priority_mappings = {" a2a_communicating_agents/orchestrator_agent/main.py
   ```
   Result: Keywords look correct

4. Check LLM routing decision:
   ```bash
   grep "Error in decision making" logs/orchestrator.log
   ```
   Result: LLM routing failed, falling back to heuristic

5. Check API key:
   ```bash
   env | grep OPENAI_API_KEY | sed 's/=.*/=***HIDDEN***/'
   ```
   Result: Variable not set

6. Solution: Set API key and restart orchestrator:
   ```bash
   export OPENAI_API_KEY="your-key-here"
   # Or add to .env file
   echo "OPENAI_API_KEY=your-key-here" >> .env
   ```

7. Restart orchestrator to pick up new environment

### Example 3: Coder Agent Acknowledges But Doesn't Generate Code

User problem:
```
Coder agent receives the message but only acknowledges, doesn't generate code
```

Debug workflow:

1. Check coder agent logs:
   ```bash
   grep -i "generate\|code" logs/coder.log | tail -20
   ```
   Result: "OpenAI package not available. Code generation will be limited."

2. Check if OpenAI is installed:
   ```bash
   python -c "import openai; print(openai.__version__)" 2>&1
   ```
   Result: ModuleNotFoundError

3. Install OpenAI package:
   ```bash
   pip install openai
   ```

4. Restart coder agent:
   ```bash
   pkill -f "coder_agent/main.py"
   cd a2a_communicating_agents
   nohup python coder_agent/main.py > ../logs/coder.log 2>&1 &
   ```

5. Verify initialization:
   ```bash
   grep "Initialized with model" logs/coder.log | tail -1
   ```
   Result: Should show model name (e.g., gpt-5-mini)

6. Send test message and verify code generation

### Example 4: Complete System Health Check

User request:
```
Run a complete diagnostic on the agent system
```

Complete diagnostic workflow:

1. Check all agents running:
   ```bash
   echo "=== Agent Processes ==="
   ps aux | grep -E "(orchestrator|coder|tester|websocket)" | grep -v grep
   ```

2. Check agent configs:
   ```bash
   echo "=== Agent Configurations ==="
   for agent in orchestrator_agent coder_agent tester_agent; do
     if [ -f "a2a_communicating_agents/$agent/agent.json" ]; then
       echo "--- $agent ---"
       cat "a2a_communicating_agents/$agent/agent.json" | python -m json.tool
     fi
   done
   ```

3. Check environment:
   ```bash
   echo "=== Environment Variables ==="
   env | grep -E "(OPENAI|MODEL)" | sed 's/=.*/=***HIDDEN***/'
   ```

4. Check recent logs:
   ```bash
   echo "=== Recent Log Activity ==="
   tail -5 logs/*.log 2>/dev/null
   ```

5. Check for errors:
   ```bash
   echo "=== Recent Errors ==="
   grep -i "error\|exception" logs/*.log | tail -10
   ```

6. Test message sending:
   ```bash
   echo "=== Message Transport Test ==="
   python .claude/skills/agent-debug/scripts/test_message.py
   ```

7. Provide summary report with:
   - Agent status (running/stopped)
   - Configuration validity
   - Environment completeness
   - Recent error count
   - Transport test result

## Related Tools

- `orchestrator_chat.py` - Interactive chat interface for testing
- `send_agent_message.py` - Send messages programmatically
- Agent start/stop scripts in `a2a_communicating_agents/`

## Summary

This skill provides systematic debugging for the A2A agent communication system. Use it whenever:
- Agents aren't communicating
- Messages aren't being delivered
- Routing is incorrect
- System behavior is unexpected

Follow the diagnostic steps in order, checking status → configuration → logs → transport → routing. Most issues are:
1. Agent not running
2. Missing dependencies
3. Missing API keys
4. Invalid configurations
5. Routing logic issues

Start with the Quick Diagnostic Checklist and drill down based on what fails.
