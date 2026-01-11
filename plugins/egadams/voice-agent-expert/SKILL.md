# Voice Agent Expert – Debugging Cheat Sheet (Skill)

This skill is a practical, "use-it-while-debugging" reference for getting a LiveKit + Letta voice agent working reliably.

---

## Core rules (fix 90% of issues)

1. **Override the right LiveKit hook**
   - The framework calls `llm_node`, **not** `generate_reply`.
   - If you override the wrong method, your changes won't run and your agent may "look alive" but never route text correctly.

2. **Only ONE voice-agent process can run at a time**
   - Duplicate processes commonly cause:
     - timeouts
     - audio cutting out
     - inconsistent behavior (you're looking at logs from one process while another is actually serving)

3. **Use `dev` mode for local testing**
   - `start` can sit waiting for dispatch and look "broken."
   - If you're actively testing locally, `dev` mode is the fast path.

---

## Nuclear reset (when it's just stuck)

Run this when things are wedged, timeouts are happening, or audio is cutting out.
It kills old processes, restarts LiveKit in dev mode, then restarts the Letta voice agent.

```bash
pkill -9 -f letta_voice_agent.py
pkill -f livekit-server
sleep 2

cd /home/adamsl/ottomator-agents/livekit-agent
nohup ./livekit-server --dev --bind 0.0.0.0 > /tmp/livekit.log 2>&1 &

cd /home/adamsl/planner/a2a_communicating_agents/hybrid_letta_agents
/home/adamsl/planner/.venv/bin/python3 letta_voice_agent.py dev > /tmp/letta_voice_agent.log 2>&1 &
```

---

## Is it alive? checks (fastest signals)

1. **LiveKit responding (not just "listening")**
   ```bash
   curl -v http://localhost:7880/ 2>&1 | head -20
   ```
   If this hangs or times out, LiveKit is stuck → restart it.

2. **Confirm you don't have duplicate voice-agent processes**
   ```bash
   ps aux | grep letta_voice_agent | grep -v grep
   ```
   You should see exactly one.

3. **Confirm Letta routing is actually being used**
   Watch your logs for your 🎤 marker (or equivalent logging) that proves `llm_node` is being hit.

---

## Common gotchas

### WebSocket double-slash problem

If the browser tries:
```
ws://127.0.0.1:7880//rtc
```

Use instead:
```
ws://localhost:7880
```

**Reason:** The client appends `/rtc`, and some configs end up producing a double-slash.

### Code changes not taking effect

- Edits don't apply until you kill + restart the running process.
- If you edited code and nothing changed, assume you're running an old process.

---

## If messages aren't showing up in Letta Desktop

Most common causes:

- You overrode the wrong method (`generate_reply` instead of `llm_node`)
- An old process is still running (your edits aren't live)
- The session LLM is bypassing Letta routing

### Recommended fix flow

1. Search your code for `llm_node` and confirm your override is in place.
2. Kill all running agent processes.
3. Restart cleanly using the Nuclear reset section above.
4. Tail logs and confirm you see your 🎤 marker.
