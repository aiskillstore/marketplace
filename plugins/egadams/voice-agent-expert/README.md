# Voice Agent Expert Skill

Claude Code skill for troubleshooting and managing the Letta Voice Agent system.

## What This Skill Does

Expert guidance for setting up and troubleshooting voice conversations with Letta agents via Livekit WebRTC.

## Files

- **SKILL.md** - Complete skill documentation with all instructions
- **QUICK_REFERENCE.md** - Fast reference for common issues
- **scripts/diagnose_voice_system.py** - Automated diagnostic tool
- **scripts/generate_token.py** - Generate Livekit connection tokens
- **scripts/start_voice_system.py** - Start services interactively

## Key Learnings

### Critical Discovery: START vs DEV Mode

The voice agent has two modes that behave completely differently:

| Mode | Command | Behavior | Use Case |
|------|---------|----------|----------|
| **START** | `letta_voice_agent.py start` | Waits for external dispatch, **times out** on direct connections | Production with load balancer |
| **DEV** | `letta_voice_agent.py dev` | Auto-joins rooms immediately, **works** for direct connections | Local testing |

**For local voice chat, ALWAYS use DEV mode.**

### Most Common Issues

1. **Voice cuts off intermittently** → Duplicate voice agents (auto-fixed by scripts as of Dec 2024)
2. **"Waiting for agent to join..."** → Stale Livekit rooms (auto-fixed by restart script as of Dec 2024)
3. **Timeout errors** → Voice agent in START mode or duplicate processes
4. **Agent doesn't respond** → Multiple voice agents running simultaneously
5. **Connection fails** → Expired token (>6 hours old)

## Quick Start

```bash
# Start the system (safe, idempotent)
/home/adamsl/planner/a2a_communicating_agents/hybrid_letta_agents/start_voice_system.sh

# Generate token
/home/adamsl/planner/.venv/bin/python3 /home/adamsl/planner/.claude/skills/voice-agent-expert/scripts/generate_token.py

# Open browser
# http://localhost:8888/test-simple.html
```

## When to Use This Skill

Use this skill when:
- User wants to talk (speak/hear) to their Letta agent
- Setting up voice chat for the first time
- Troubleshooting voice connection issues
- Getting timeout or WebSocket errors
- Agent joins room but doesn't respond

## Emergency Fixes

### Duplicate Processes (Auto-Fixed as of Dec 2024)

**NEW**: Scripts now automatically detect and kill duplicate processes!

```bash
# Check for duplicates (scripts do this automatically now)
ps aux | grep "letta_voice_agent" | grep -v grep
# Should see ONLY ONE with "dev"

# Start script auto-detects and fixes duplicates
/home/adamsl/planner/a2a_communicating_agents/hybrid_letta_agents/start_voice_system.sh

# Restart script reports and kills all duplicates
/home/adamsl/planner/a2a_communicating_agents/hybrid_letta_agents/restart_voice_system.sh
```

### Manual Kill (if needed)
```bash
pkill -f "letta_voice_agent.py"
/home/adamsl/planner/a2a_communicating_agents/hybrid_letta_agents/start_voice_system.sh
```

## System Architecture

```
User Voice → Browser WebRTC → Livekit Server (7880) →
Voice Agent Worker (DEV mode) → Deepgram STT →
Letta Server (8283) → OpenAI/Cartesia TTS → User Hears Response
```

## Required Components

1. **Letta Server** (port 8283) - Agent memory & orchestration
2. **Livekit Server** (port 7880) - WebRTC audio streaming
3. **Voice Agent Worker** (DEV mode) - Bridges Livekit ↔ Letta
4. **Browser** - Frontend with microphone access

## Scripts Created

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `start_voice_system.sh` | Smart startup with **auto-duplicate detection**, checks what's running, skips if already running correctly | After reboot, not sure what's running |
| `restart_voice_system.sh` | Nuclear restart with **duplicate detection** and **stale room auto-cleanup**, kills everything | When things are broken, audio cutting, "waiting for agent", duplicates exist |
| `clean_livekit_rooms.sh` | **NEW (Dec 2024)**: Force kills Livekit to clear stale rooms with ghost participants | When "waiting for agent to join" never resolves |
| `diagnose_voice_system.py` | Automated diagnostics | Check system health |
| `generate_token.py` | Create connection token | Token expired, new session |

## Alternative: Text Chat

Don't need voice? Use text chat instead:

```bash
cd /home/adamsl/planner/a2a_communicating_agents/hybrid_letta_agents/agents
/home/adamsl/planner/.venv/bin/python3 chat_with_letta.py
```

## Updated Knowledge

This skill was created and refined based on real troubleshooting sessions that discovered:

1. The critical difference between START and DEV modes
2. How duplicate processes cause WebSocket timeouts **and audio cutting**
3. Token expiration after ~6 hours
4. The importance of idempotent startup scripts
5. Common error patterns and their root causes
6. **NEW (Dec 2024)**: Automatic duplicate detection to prevent audio cutting
7. **NEW (Dec 2024)**: Improved VAD settings to reduce false triggers (fixed parameter names)
8. **NEW (Dec 2024)**: Stale Livekit room detection and automatic force-kill cleanup
9. **NEW (Dec 2024)**: Comprehensive duplicate prevention system with PID/lock files
10. Scripts now intelligently handle duplicate agents and stale rooms without manual intervention

### Duplicate Prevention System (Dec 2024)

Complete protection against duplicate agents:
- **PID file locking** (`/tmp/letta_voice_agent.pid`)
- **Lock files during startup** (`/tmp/letta_voice_agent.lock`)
- **Pre-start checks** (`check_agent_running.sh`)
- **Safe starter wrapper** (`start_voice_agent_safe.sh`)
- **Safe stopper with cleanup** (`stop_voice_agent_safe.sh`)
- **Systemd service** (optional, production-grade)

See `DUPLICATE_PREVENTION.md` for complete documentation.

All troubleshooting knowledge is captured in SKILL.md and QUICK_REFERENCE.md.
