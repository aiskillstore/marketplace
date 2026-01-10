# Letta Voice Agent - Quick Reference

## 🚨 MOST COMMON ISSUES

### 1. Voice Cuts Off / Audio Stops Intermittently ⭐ **#1 ISSUE**
**Cause**: Duplicate voice agents (competing for audio stream)
**NEW**: Scripts auto-detect and fix this as of Dec 2024!

```bash
# Check for duplicates (auto-fixed by scripts now)
ps aux | grep "letta_voice_agent" | grep -v grep | wc -l
# Should return 1, not 2+

# Scripts automatically detect and kill duplicates:
/home/adamsl/planner/a2a_communicating_agents/hybrid_letta_agents/restart_voice_system.sh
```

### 2. Timeout Error: "room connection has timed out (signal)"
**Cause**: Voice agent in wrong mode OR duplicate processes

```bash
# Check what's running
ps aux | grep "letta_voice_agent" | grep -v grep

# Should see ONLY ONE with "dev" in command
# Scripts auto-fix this:
/home/adamsl/planner/a2a_communicating_agents/hybrid_letta_agents/start_voice_system.sh
```

### 3. Agent Joins But Doesn't Respond
**Cause**: Duplicate voice agents
**Fix**: Scripts auto-detect duplicates now

```bash
# Restart script kills all duplicates automatically
/home/adamsl/planner/a2a_communicating_agents/hybrid_letta_agents/restart_voice_system.sh
```

### 4. Waiting for Agent to Join (Never Resolves) ⚠️ **NEW DEC 2024**
**Cause**: Stale Livekit rooms with ghost participants
**Fix**: Scripts auto-detect and force kill Livekit

```bash
# Automatic fix - restart script handles this:
/home/adamsl/planner/a2a_communicating_agents/hybrid_letta_agents/restart_voice_system.sh

# Or use dedicated room cleaner:
/home/adamsl/planner/a2a_communicating_agents/hybrid_letta_agents/clean_livekit_rooms.sh
```

### 5. Token Expired
**Cause**: Token is >6 hours old

```bash
# Generate fresh token
/home/adamsl/planner/.venv/bin/python3 /home/adamsl/planner/.claude/skills/voice-agent-expert/scripts/generate_token.py
```

## ⚡ Quick Commands

| Task | Command |
|------|---------|
| **Start system** | `/home/adamsl/planner/a2a_communicating_agents/hybrid_letta_agents/start_voice_system.sh` |
| **Restart (broken)** | `/home/adamsl/planner/a2a_communicating_agents/hybrid_letta_agents/restart_voice_system.sh` |
| **Clean stale rooms** | `/home/adamsl/planner/a2a_communicating_agents/hybrid_letta_agents/clean_livekit_rooms.sh` |
| **Check status** | `ps aux \| grep "letta_voice_agent" \| grep -v grep` |
| **Check stale rooms** | `grep "waiting for participants" /tmp/livekit.log` |
| **Generate token** | `/home/adamsl/planner/.venv/bin/python3 /home/adamsl/planner/.claude/skills/voice-agent-expert/scripts/generate_token.py` |
| **Diagnostic** | `/home/adamsl/planner/.venv/bin/python3 /home/adamsl/planner/.claude/skills/voice-agent-expert/scripts/diagnose_voice_system.py` |

## 🎯 Critical Rules

1. ✅ **ALWAYS** use `dev` mode
2. ❌ **NEVER** use `start` mode for local testing
3. ❌ **NEVER** start directly with `python letta_voice_agent.py dev` - use scripts!
4. 🤖 **Scripts auto-detect & prevent duplicates** (PID/lock files - Dec 2024)
5. 🔄 Use `start_voice_system.sh` after reboots (safe, idempotent, duplicate-protected)
6. 💥 Use `restart_voice_system.sh` for audio cutting or broken state (cleans PID files)

## 🛡️ Duplicate Prevention (NEW - Dec 2024)

Scripts now use PID file locking to **prevent** duplicates from being created:

```bash
# Check if safe to start
./check_agent_running.sh

# Safe start (with PID locking)
./start_voice_agent_safe.sh

# Safe stop (cleans up PID/lock files)
./stop_voice_agent_safe.sh

# Check for stale files
ls -la /tmp/letta_voice_agent.*

# Clean up stale files
rm -f /tmp/letta_voice_agent.{pid,lock}
```

**Files used:**
- `/tmp/letta_voice_agent.pid` - Tracks running agent
- `/tmp/letta_voice_agent.lock` - Prevents race conditions (30s)

## 📋 Required Services

| Service | Port | Check |
|---------|------|-------|
| Letta | 8283 | `curl http://localhost:8283/` |
| Livekit | 7880 | `curl http://localhost:7880/` |
| Voice Agent | - | `ps aux \| grep "letta_voice_agent.py dev"` |

## 🌐 Browser Connection

1. Open: http://localhost:8888/test-simple.html
2. Click "Connect"
3. Allow microphone
4. Say "Hello!"

## 🆘 Emergency Fix

When nothing works:

```bash
# Kill everything
pkill -f "letta_voice_agent.py"
pkill -f "livekit-server"

# Start fresh
/home/adamsl/planner/a2a_communicating_agents/hybrid_letta_agents/start_voice_system.sh
```

## 📝 Aliases (Add to ~/.bashrc)

```bash
alias start-voice='/home/adamsl/planner/a2a_communicating_agents/hybrid_letta_agents/start_voice_system.sh'
alias restart-voice='/home/adamsl/planner/a2a_communicating_agents/hybrid_letta_agents/restart_voice_system.sh'
alias voice-status='ps aux | grep "letta_voice_agent" | grep -v grep'
```
