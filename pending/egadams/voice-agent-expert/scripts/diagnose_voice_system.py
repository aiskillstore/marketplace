#!/usr/bin/env python3
"""Diagnose the complete voice agent system."""

import os
import subprocess
import sys
from pathlib import Path

def run_cmd(cmd: str) -> tuple[int, str]:
    """Run command and return (returncode, output)."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr

def check_port(port: int) -> bool:
    """Check if a port is listening."""
    code, output = run_cmd(f"ss -tlnp 2>/dev/null | grep :{port}")
    return code == 0 and str(port) in output

def check_process(pattern: str) -> bool:
    """Check if a process is running."""
    code, output = run_cmd(f"ps aux | grep '{pattern}' | grep -v grep")
    return code == 0 and pattern.split()[0] in output

def check_env_var(env_file: Path, var_name: str) -> bool:
    """Check if env var is set in file."""
    if not env_file.exists():
        return False
    with open(env_file) as f:
        for line in f:
            if line.strip().startswith(var_name + "="):
                value = line.split("=", 1)[1].strip()
                return len(value) > 0 and value not in ['', '""', "''"]
    return False

def main():
    print("=" * 60)
    print("VOICE AGENT SYSTEM DIAGNOSTIC")
    print("=" * 60)
    print()

    issues = []

    # Check Letta Server
    print("[1/6] Checking Letta Server (port 8283)...")
    if check_port(8283):
        print("      ✅ Letta server is RUNNING")
    else:
        print("      ❌ Letta server is NOT RUNNING")
        issues.append("Start Letta: cd /home/adamsl/planner && ./start_letta_dec_09_2025.sh")

    # Check Livekit Server
    print("[2/6] Checking Livekit Server (port 7880)...")
    if check_port(7880):
        print("      ✅ Livekit server is RUNNING")
    else:
        print("      ❌ Livekit server is NOT RUNNING")
        issues.append("Start Livekit: livekit-server --dev")

    # Check Voice Agent
    print("[3/6] Checking Voice Agent Worker...")
    if check_process("letta_voice"):
        print("      ✅ Voice agent is RUNNING")
    else:
        print("      ⚠️  Voice agent is NOT RUNNING")
        issues.append("Start Voice Agent: See instructions below")

    # Check environment files
    livekit_env = Path("/home/adamsl/ottomator-agents/livekit-agent/.env")
    planner_env = Path("/home/adamsl/planner/.env")

    print("[4/6] Checking Livekit environment...")
    livekit_vars = ["LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET", "DEEPGRAM_API_KEY"]
    for var in livekit_vars:
        if check_env_var(livekit_env, var):
            print(f"      ✅ {var} is set")
        else:
            print(f"      ❌ {var} is MISSING")
            issues.append(f"Set {var} in {livekit_env}")

    print("[5/6] Checking OpenAI API key...")
    if check_env_var(planner_env, "OPENAI_API_KEY") or check_env_var(livekit_env, "OPENAI_API_KEY"):
        print("      ✅ OPENAI_API_KEY is set")
    else:
        print("      ❌ OPENAI_API_KEY is MISSING")
        issues.append("Set OPENAI_API_KEY in .env file")

    # Check Python packages
    print("[6/6] Checking Python packages...")
    venv_python = "/home/adamsl/planner/.venv/bin/python3"
    packages = ["livekit", "letta_client", "deepgram"]
    for pkg in packages:
        import_name = pkg.replace("-", "_")
        code, _ = run_cmd(f"{venv_python} -c 'import {import_name}' 2>/dev/null")
        if code == 0:
            print(f"      ✅ {pkg} installed")
        else:
            print(f"      ⚠️  {pkg} may not be installed")

    print()
    print("=" * 60)

    if issues:
        print("ISSUES FOUND:")
        print("=" * 60)
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
        print()
        print("TO START VOICE AGENT:")
        print("-" * 40)
        print("cd /home/adamsl/planner/a2a_communicating_agents/hybrid_letta_agents")
        print("export $(grep -v '^#' /home/adamsl/ottomator-agents/livekit-agent/.env | xargs)")
        print("/home/adamsl/planner/.venv/bin/python3 letta_voice_agent.py start")
    else:
        print("ALL CHECKS PASSED!")
        print("=" * 60)
        print()
        print("System is ready. Generate a token to connect:")
        print("  python3 /home/adamsl/planner/.claude/skills/voice-agent-expert/scripts/generate_token.py")

    print()
    return len(issues)

if __name__ == "__main__":
    sys.exit(main())
