#!/usr/bin/env python3
"""Start the complete voice agent system."""

import os
import subprocess
import sys
import time
from pathlib import Path

LETTA_VOICE_AGENT_EXE="letta_voice_agent_groq.py"

def check_port(port: int) -> bool:
    """Check if a port is listening."""
    result = subprocess.run(
        f"ss -tlnp 2>/dev/null | grep :{port}",
        shell=True, capture_output=True, text=True
    )
    return result.returncode == 0

def main():
    print("=" * 60)
    print("STARTING VOICE AGENT SYSTEM")
    print("=" * 60)
    print()

    # Check Letta
    print("[1/3] Checking Letta Server...")
    if check_port(8283):
        print("      ✅ Already running on port 8283")
    else:
        print("      ❌ Not running")
        print("      → Please start Letta in a separate terminal:")
        print("        cd /home/adamsl/planner && ./start_letta_dec_09_2025.sh")
        print()
        input("      Press Enter when Letta is running...")

        if not check_port(8283):
            print("      ❌ Letta still not detected. Please start it first.")
            sys.exit(1)

    # Check Livekit
    print("[2/3] Checking Livekit Server...")
    if check_port(7880):
        print("      ✅ Already running on port 7880")
    else:
        print("      ❌ Not running")
        print("      → Please start Livekit in a separate terminal:")
        print("        livekit-server --dev")
        print()
        input("      Press Enter when Livekit is running...")

        if not check_port(7880):
            print("      ❌ Livekit still not detected. Please start it first.")
            sys.exit(1)

    # Start voice agent
    print("[3/3] Starting Voice Agent Worker...")
    print()

    # Load environment
    env_file = Path("/home/adamsl/ottomator-agents/livekit-agent/.env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

    # Also load planner env
    planner_env = Path("/home/adamsl/planner/.env")
    if planner_env.exists():
        with open(planner_env) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key, value)

    print("=" * 60)
    print("All services ready! Starting voice agent...")
    print("=" * 60)
    print()
    print("The voice agent will now start.")
    print("Connect via: https://agents-playground.livekit.io/")
    print()
    print("Generate a token with:")
    print("  python3 /home/adamsl/planner/.claude/skills/voice-agent-expert/scripts/generate_token.py")
    print()
    print("-" * 60)
    print()

    # Start the voice agent
    os.chdir("/home/adamsl/planner/a2a_communicating_agents/hybrid_letta_agents")
    os.execv(
        "/home/adamsl/planner/.venv/bin/python3",
        ["/home/adamsl/planner/.venv/bin/python3", LETTA_VOICE_AGENT_EXE, "start"]
    )

if __name__ == "__main__":
    main()
