#!/usr/bin/env python3
"""Setup script for installing skill tracker hooks."""

import json
import os
import stat
from pathlib import Path

# Path constants
PROJECT_ROOT = Path.cwd()
HOOKS_DIR = PROJECT_ROOT / ".claude" / "hooks"
LOGS_DIR = PROJECT_ROOT / ".claude" / "activity-logs"
SETTINGS_FILE = PROJECT_ROOT / ".claude" / "settings.json"

# T009: Track prompt hook script (async, logs to prompts.jsonl)
TRACK_PROMPT_SH = '''#!/usr/bin/env bash
# Track user prompt submissions
echo '{"async":true,"asyncTimeout":15000}'

# Read JSON input from stdin
INPUT=$(cat)

# Extract fields using jq
PROMPT=$(echo "$INPUT" | jq -r '.prompt // empty')
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Skip if no prompt
[ -z "$PROMPT" ] && exit 0

# Ensure log directory exists
mkdir -p .claude/activity-logs

# Write log entry using jq for proper JSON (compact for JSONL)
jq -nc --arg ts "$TIMESTAMP" --arg sid "$SESSION_ID" --arg prompt "$PROMPT" \
  '{timestamp: $ts, session_id: $sid, prompt: $prompt}' >> .claude/activity-logs/prompts.jsonl

exit 0
'''

# T010: Track skill start hook script (async, detects SKILL.md reads)
TRACK_SKILL_START_SH = r'''#!/usr/bin/env bash
# Track skill activations via SKILL.md reads
echo '{"async":true,"asyncTimeout":15000}'

# Read JSON input from stdin
INPUT=$(cat)

# Extract tool and file path
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.command // empty')

# Only process Read tool or cat commands
case "$TOOL" in
    Read|Bash) ;;
    *) exit 0 ;;
esac

# Check if path matches any file in a skill directory
# Matches: .claude/skills/[name]/* or /skills/[name]/*
if [[ "$FILE_PATH" =~ \.claude/skills/([^/]+)/ ]] || [[ "$FILE_PATH" =~ /skills/([^/]+)/ ]]; then
    SKILL_NAME="${BASH_REMATCH[1]}"
elif [[ "$FILE_PATH" =~ cat.*skills/([^/]+)/ ]]; then
    SKILL_NAME="${BASH_REMATCH[1]}"
else
    exit 0
fi

SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Ensure log directory exists
mkdir -p .claude/activity-logs

# Write start event using jq for proper JSON (compact for JSONL)
jq -nc --arg ts "$TIMESTAMP" --arg sid "$SESSION_ID" --arg skill "$SKILL_NAME" \
  '{timestamp: $ts, session_id: $sid, skill: $skill, event: "start"}' >> .claude/activity-logs/skill-usage.jsonl

exit 0
'''

# T011: Track skill end hook script (async, captures verify.py results)
TRACK_SKILL_END_SH = r'''#!/usr/bin/env bash
# Track skill verification results
echo '{"async":true,"asyncTimeout":15000}'

# Read JSON input from stdin
INPUT=$(cat)

# Extract command and exit code
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
EXIT_CODE=$(echo "$INPUT" | jq -r '.tool_result.exit_code // empty')

# Check if command is running verify.py
if [[ "$COMMAND" =~ skills/([^/]+)/scripts/verify\.py ]]; then
    SKILL_NAME="${BASH_REMATCH[1]}"
elif [[ "$COMMAND" =~ python.*verify\.py ]] && [[ "$COMMAND" =~ skills/([^/]+)/ ]]; then
    SKILL_NAME="${BASH_REMATCH[1]}"
else
    exit 0
fi

# Determine status from exit code
if [ "$EXIT_CODE" = "0" ]; then
    STATUS="success"
else
    STATUS="failure"
fi

SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Ensure log directory exists
mkdir -p .claude/activity-logs

# Write verify event using jq for proper JSON (compact for JSONL)
jq -nc --arg ts "$TIMESTAMP" --arg sid "$SESSION_ID" --arg skill "$SKILL_NAME" --arg status "$STATUS" \
  '{timestamp: $ts, session_id: $sid, skill: $skill, event: "verify", status: $status}' >> .claude/activity-logs/skill-usage.jsonl

exit 0
'''

# T012: Analysis script (detects skill types, calculates metrics)
ANALYZE_SKILLS_PY = '''#!/usr/bin/env python3
"""Analyze skill usage from activity logs."""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

SKILLS_DIR = Path(".claude/skills")
LOGS_DIR = Path(".claude/activity-logs")
SKILL_USAGE_LOG = LOGS_DIR / "skill-usage.jsonl"
PROMPTS_LOG = LOGS_DIR / "prompts.jsonl"


def get_skill_type(skill_name: str) -> str:
    """Detect skill type by checking for verify.py."""
    verify_path = SKILLS_DIR / skill_name / "scripts" / "verify.py"
    return "procedural" if verify_path.exists() else "content"


def load_jsonl(path: Path) -> list:
    """Load JSONL file into list of dicts."""
    if not path.exists():
        return []
    entries = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def analyze():
    """Run skill usage analysis."""
    print("=" * 70)
    print("SKILL USAGE ANALYSIS")
    print("=" * 70)
    print()
    print(f"Analysis date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Log directory: {LOGS_DIR.absolute()}")
    print()

    # Load logs
    prompts = load_jsonl(PROMPTS_LOG)
    events = load_jsonl(SKILL_USAGE_LOG)

    print(f"Total prompts logged: {len(prompts)}")

    # Aggregate by skill
    invocations = defaultdict(int)
    successes = defaultdict(int)
    failures = defaultdict(int)

    for event in events:
        skill = event.get("skill", "unknown")
        event_type = event.get("event")

        if event_type == "start":
            invocations[skill] += 1
        elif event_type == "verify":
            status = event.get("status")
            if status == "success":
                successes[skill] += 1
            elif status == "failure":
                failures[skill] += 1

    total_invocations = sum(invocations.values())
    print(f"Total skill invocations: {total_invocations}")
    print()

    # Get all skills from directory
    all_skills = set()
    if SKILLS_DIR.exists():
        for skill_dir in SKILLS_DIR.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                all_skills.add(skill_dir.name)

    # Separate by type
    procedural_skills = {s for s in all_skills if get_skill_type(s) == "procedural"}
    content_skills = all_skills - procedural_skills

    # Print procedural skills
    if procedural_skills or any(get_skill_type(s) == "procedural" for s in invocations):
        print("PROCEDURAL SKILLS (with verify.py):")
        print(f"{'Skill':<40} {'Invocations':>12} {'Success':>10} {'Failure':>10} {'Rate':>8}")
        print("-" * 80)

        for skill in sorted(procedural_skills | {s for s in invocations if get_skill_type(s) == "procedural"}):
            inv = invocations.get(skill, 0)
            succ = successes.get(skill, 0)
            fail = failures.get(skill, 0)
            total_verify = succ + fail
            rate = f"{(succ / total_verify * 100):.1f}%" if total_verify > 0 else "N/A"
            print(f"{skill:<40} {inv:>12} {succ:>10} {fail:>10} {rate:>8}")
        print()

    # Print content skills
    if content_skills or any(get_skill_type(s) == "content" for s in invocations):
        print("CONTENT SKILLS (no verify.py):")
        print(f"{'Skill':<40} {'Invocations':>12} {'Success Rate':>15}")
        print("-" * 70)

        for skill in sorted(content_skills | {s for s in invocations if get_skill_type(s) == "content"}):
            inv = invocations.get(skill, 0)
            print(f"{skill:<40} {inv:>12} {'N/A':>15}")
        print()

    # Unused skills
    used_skills = set(invocations.keys())
    unused = all_skills - used_skills
    if unused:
        print(f"UNUSED SKILLS ({len(unused)}):")
        for skill in sorted(unused):
            skill_type = get_skill_type(skill)
            print(f"   - {skill} ({skill_type})")
        print()

    # High failure rate (procedural only)
    high_failure = []
    for skill in procedural_skills:
        total_verify = successes.get(skill, 0) + failures.get(skill, 0)
        if total_verify > 0:
            failure_rate = failures.get(skill, 0) / total_verify
            if failure_rate > 0.3:
                high_failure.append((skill, failure_rate))

    if high_failure:
        print("HIGH FAILURE RATE SKILLS (>30%):")
        for skill, rate in sorted(high_failure, key=lambda x: -x[1]):
            print(f"   - {skill}: {rate*100:.0f}% failure rate")
        print()

    # Overall success rate for procedural skills
    total_succ = sum(successes.values())
    total_fail = sum(failures.values())
    total_verify = total_succ + total_fail
    if total_verify > 0:
        overall_rate = total_succ / total_verify * 100
        print("=" * 70)
        print(f"Procedural skills success rate: {overall_rate:.1f}%")
        print("=" * 70)


if __name__ == "__main__":
    analyze()
'''

# T014: Hook configuration for settings.json
HOOKS_CONFIG = {
    "hooks": {
        "UserPromptSubmit": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": ".claude/hooks/track-prompt.sh"
                    }
                ]
            }
        ],
        "PreToolUse": [
            {
                "matcher": "Read|Bash",
                "hooks": [
                    {
                        "type": "command",
                        "command": ".claude/hooks/track-skill-start.sh"
                    }
                ]
            }
        ],
        "PostToolUse": [
            {
                "matcher": "Bash",
                "hooks": [
                    {
                        "type": "command",
                        "command": ".claude/hooks/track-skill-end.sh"
                    }
                ]
            }
        ]
    }
}


def setup_directories():
    """T008: Create hooks and activity-logs directories."""
    HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Created {HOOKS_DIR}")
    print(f"Created {LOGS_DIR}")


def setup_hook_scripts():
    """T013: Write hook scripts and make executable."""
    scripts = {
        "track-prompt.sh": TRACK_PROMPT_SH,
        "track-skill-start.sh": TRACK_SKILL_START_SH,
        "track-skill-end.sh": TRACK_SKILL_END_SH,
        "analyze-skills.py": ANALYZE_SKILLS_PY,
    }

    for name, content in scripts.items():
        path = HOOKS_DIR / name
        path.write_text(content)
        # Make executable
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print(f"Created {path}")


def setup_settings():
    """T015: Merge hook configuration into settings.json."""
    # Load existing settings or create empty
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE) as f:
            settings = json.load(f)
    else:
        settings = {}
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Merge hooks
    if "hooks" not in settings:
        settings["hooks"] = {}

    for event_type, entries in HOOKS_CONFIG["hooks"].items():
        if event_type not in settings["hooks"]:
            settings["hooks"][event_type] = entries
            print(f"Added {event_type} hook")
        else:
            # Check if our hook is already registered
            existing_commands = set()
            for entry in settings["hooks"][event_type]:
                for hook in entry.get("hooks", []):
                    existing_commands.add(hook.get("command", ""))

            for entry in entries:
                for hook in entry.get("hooks", []):
                    if hook.get("command") not in existing_commands:
                        settings["hooks"][event_type].append(entry)
                        print(f"Added {event_type} hook")
                        break

    # Write back
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)
    print(f"Updated {SETTINGS_FILE}")


def main():
    """T016: Run all setup functions."""
    print("=" * 50)
    print("SKILL TRACKER SETUP")
    print("=" * 50)
    print()

    setup_directories()
    print()

    setup_hook_scripts()
    print()

    setup_settings()
    print()

    print("=" * 50)
    print("SETUP COMPLETE")
    print("=" * 50)
    print()
    print("Next: Run verify.py to confirm installation")
    print("  python .claude/skills/installing-skill-tracker/scripts/verify.py")


if __name__ == "__main__":
    main()