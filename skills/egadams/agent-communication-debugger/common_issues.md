# Common Agent Communication Issues

This guide covers frequent problems and their solutions.

## Issue 1: Messages Not Being Delivered

**Symptoms:**
- Send message via orchestrator_chat.py but no response
- Orchestrator logs show no activity
- Agent doesn't receive messages

**Root Causes & Solutions:**

### A. Transport Layer Issues

**WebSocket transport not running:**
```bash
# Check if WebSocket server is up
ps aux | grep websocket_server | grep -v grep
```

Solution:
```bash
cd a2a_communicating_agents
python agent_messaging/websocket_server.py &
```

**RAG board storage missing:**
```bash
# Check storage directory
ls -la storage/
```

Solution:
```bash
mkdir -p storage
# Restart agents to recreate storage
```

### B. Topic Mismatch

**Wrong topic specified:**
- Check message is sent to correct topic ("orchestrator", "code", etc.)
- Verify agent is listening on expected topic

Solution:
```bash
# Check agent topics in config
grep -r '"topics"' a2a_communicating_agents/*/agent.json

# Verify inbox calls in agent code
grep 'inbox(' a2a_communicating_agents/*/main.py
```

### C. Message Deduplication

**Message already processed:**
- Agents track seen message IDs
- Duplicate messages are ignored

Solution:
- Send a new, unique message
- Restart agent to clear processed message cache

## Issue 2: Routing to Wrong Agent

**Symptoms:**
- Message reaches orchestrator
- Routes to unexpected agent (e.g., dashboard-agent instead of coder-agent)
- Wrong agent responds

**Root Causes & Solutions:**

### A. LLM Routing Failure

**API key missing or invalid:**
```bash
# Check API key is set
env | grep OPENAI_API_KEY
```

Solution:
```bash
export OPENAI_API_KEY="your-key-here"
# Or add to .env file
echo "OPENAI_API_KEY=sk-..." >> .env
```

**LLM returns unexpected decision:**
- Check orchestrator logs for routing reasoning
- LLM might be confused by ambiguous request

Solution:
- Update routing prompt in `orchestrator_agent/main.py` with clearer rules
- Add priority keywords for your use case

### B. Fallback Routing Issues

**Keywords not matching:**
```bash
# Check priority keywords
grep -A 10 "priority_mappings" a2a_communicating_agents/orchestrator_agent/main.py
```

Solution:
- Add relevant keywords to priority_mappings:
```python
"coder-agent": ["code", "write", "implement", "webassembly", "wasm", ...],
```

### C. Agent Not Discovered

**Agent config missing or invalid:**
```bash
# Check all agent.json files exist
find a2a_communicating_agents -name "agent.json" -type f
```

Solution:
- Ensure agent.json exists in agent directory
- Validate JSON syntax:
```bash
python -m json.tool < a2a_communicating_agents/coder_agent/agent.json
```

**Agent not running when discovery happens:**
- Orchestrator discovers agents on startup
- New agents added after startup won't be found

Solution:
- Restart orchestrator after adding new agents

## Issue 3: Agent Not Generating Responses

**Symptoms:**
- Agent receives message (logs show it)
- No response sent back
- No code/output generated

**Root Causes & Solutions:**

### A. Missing Dependencies

**LLM client not available:**
```bash
# Check if OpenAI package installed
python -c "import openai; print('OK')" 2>&1
```

Solution:
```bash
pip install openai
# Restart agent
```

### B. API Key Issues

**Key not set in agent environment:**
- Agent inherits environment from parent shell
- If started without API key, won't work

Solution:
```bash
# Stop agent
pkill -f "coder_agent/main.py"

# Set key
export OPENAI_API_KEY="sk-..."

# Restart agent
cd a2a_communicating_agents
python coder_agent/main.py &
```

### C. Agent Logic Errors

**Exception in request handling:**
```bash
# Check agent logs for tracebacks
grep -A 20 "Traceback" logs/coder.log
```

Solution:
- Fix the error in agent code
- Restart agent after code changes

### D. Response Not Reaching Topic

**Agent posts to wrong topic:**
```bash
# Check where agent posts responses
grep 'post_message' a2a_communicating_agents/coder_agent/main.py
```

Solution:
- Verify agent posts to "orchestrator" topic with to_agent="board"
- Check chat interface listens on correct topic

## Issue 4: Duplicate Message Processing

**Symptoms:**
- Same message processed multiple times
- Multiple responses for one request
- Logs show duplicate entries

**Root Causes & Solutions:**

### A. Multiple Agent Instances

**Same agent running multiple times:**
```bash
# Check for duplicates
ps aux | grep "coder_agent/main.py" | grep -v grep | wc -l
```

Solution:
```bash
# Kill all instances
pkill -f "coder_agent/main.py"

# Start only one
cd a2a_communicating_agents
python coder_agent/main.py &
```

### B. Message Deduplication Not Working

**Message ID generation broken:**
- Check agent's `_extract_message_id` method
- IDs must be unique and stable

Solution:
- Use document_id from message metadata
- Fallback to timestamp + content hash

### C. Polling Too Frequently

**Agent fetches same messages repeatedly:**
- Check inbox() call frequency
- Sleep duration too short

Solution:
- Increase sleep time between inbox() calls
- Ensure processed message tracking works

## Issue 5: Transport Connectivity Problems

**Symptoms:**
- Connection refused errors
- Timeout when sending messages
- Transport initialization fails

**Root Causes & Solutions:**

### A. WebSocket Server Not Running

**Port 8765 not listening:**
```bash
netstat -tlnp | grep 8765
```

Solution:
```bash
cd a2a_communicating_agents/agent_messaging
python websocket_server.py &
```

### B. ChromaDB Storage Issues

**Database locked or corrupted:**
```bash
# Check ChromaDB files
ls -la a2a_communicating_agents/storage/chromadb/
```

Solution:
```bash
# Backup and recreate
mv a2a_communicating_agents/storage/chromadb{,.backup}
# Restart agents to recreate database
```

### C. Permission Errors

**Can't write to storage:**
```bash
# Check storage permissions
ls -ld storage/
```

Solution:
```bash
chmod -R u+w storage/
```

## Issue 6: Orchestrator Not Starting

**Symptoms:**
- Orchestrator process exits immediately
- No log entries generated
- Import errors on startup

**Root Causes & Solutions:**

### A. Missing Python Packages

**Import errors:**
```bash
# Try running manually to see errors
cd a2a_communicating_agents/orchestrator_agent
python main.py
```

Common missing packages:
- openai
- rich
- chromadb
- sentence-transformers

Solution:
```bash
pip install openai rich chromadb sentence-transformers
```

### B. Environment Loading Issues

**Can't find .env file:**
- Orchestrator loads from PLANNER_ROOT/.env
- Check path is correct

Solution:
```bash
# Verify .env exists
ls -la .env

# Check it has API keys
grep API_KEY .env | sed 's/=.*/=***/'
```

### C. Port Already in Use

**If orchestrator uses ports (rare):**
```bash
# Find what's using the port
lsof -i :PORT_NUMBER
```

Solution:
- Kill conflicting process
- Or change port configuration

## Prevention Best Practices

### 1. Start Order

Always start in this order:
1. WebSocket server (if using)
2. Orchestrator agent
3. Specialist agents (coder, tester)

### 2. Health Checks

Periodically verify:
```bash
# All agents running
ps aux | grep -E "(orchestrator|coder|tester)_agent" | grep -v grep

# No recent errors
grep -i error logs/*.log | tail -20

# Transport working
python -c "from a2a_communicating_agents.agent_messaging import inbox; print(len(inbox('orchestrator', limit=1)))"
```

### 3. Log Rotation

Prevent log files from growing too large:
```bash
# Truncate old logs
> logs/orchestrator.log
> logs/coder.log
```

### 4. Graceful Restarts

When restarting agents:
```bash
# Stop gracefully (allow cleanup)
pkill -TERM -f "orchestrator_agent/main.py"
sleep 2

# Then start fresh
cd a2a_communicating_agents
python orchestrator_agent/main.py &
```

## Getting More Help

If issues persist:

1. **Collect diagnostic info:**
   ```bash
   # System state
   ps aux | grep -E "agent|websocket" > debug_snapshot.txt

   # Logs
   tail -100 logs/*.log >> debug_snapshot.txt

   # Config
   cat a2a_communicating_agents/*/agent.json >> debug_snapshot.txt
   ```

2. **Enable debug logging:**
   - Add `import logging; logging.basicConfig(level=logging.DEBUG)` to agent main.py
   - Restart agent
   - Check detailed logs

3. **Test minimal case:**
   - Stop all agents
   - Start only orchestrator
   - Send simple test message
   - Add agents one at a time

4. **Review code changes:**
   - Check recent git commits
   - Verify no syntax errors introduced
   - Test rollback to last working version
