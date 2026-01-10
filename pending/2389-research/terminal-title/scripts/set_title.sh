#!/bin/bash
# ABOUTME: Sets terminal window title with emoji, project name, and topic
# ABOUTME: Usage: ./set_title.sh "Project Name" "Topic"

# Exit silently if arguments missing (fail-safe behavior)
if [ -z "$1" ] || [ -z "$2" ]; then
    exit 0
fi

PROJECT="$1"
TOPIC="$2"

# Get emoji from environment, default to 🎉
# Sanitize to prevent ANSI escape sequence injection
EMOJI=$(echo "${TERMINAL_TITLE_EMOJI:-🎉}" | tr -d '\000-\037')

# Validate and sanitize inputs (remove control characters, limit length)
PROJECT=$(echo "$PROJECT" | tr -d '\000-\037' | head -c 40)
TOPIC=$(echo "$TOPIC" | tr -d '\000-\037' | head -c 40)

# Ensure values not empty after sanitization
if [ -z "$PROJECT" ] || [ -z "$TOPIC" ]; then
    exit 0
fi

# Set the terminal title using ANSI escape sequences
# Format: "emoji ProjectName - Topic   " (3 spaces compensate for Bash tool truncation)
#
# Dual-path approach:
# 1. Hook context: Write to /dev/tty (stdout is captured by hook logging)
# 2. Skill context: Write to stdout (Bash tool passes it through to terminal)
#
# Try /dev/tty first (suppress all errors), fall back to stdout if unavailable
{
    if printf '\033]0;%s %s - %s   \007' "$EMOJI" "$PROJECT" "$TOPIC" > /dev/tty 2>&1; then
        exit 0  # Success via /dev/tty (hook context)
    fi
} 2>/dev/null

# If we reach here, /dev/tty failed - use stdout (Bash tool context)
printf '\033]0;%s %s - %s   \007' "$EMOJI" "$PROJECT" "$TOPIC"
