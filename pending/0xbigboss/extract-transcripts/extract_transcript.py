#!/usr/bin/env python3
"""Extract readable transcripts from Claude Code session JSONL files."""

import json
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, TextIO


def parse_timestamp(ts: str) -> datetime:
    """Parse ISO timestamp."""
    return datetime.fromisoformat(ts.replace('Z', '+00:00'))


def format_duration(start: datetime, end: datetime) -> str:
    """Format duration between two timestamps."""
    delta = end - start
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def extract_text_content(content) -> str:
    """Extract text from message content (handles both string and array formats)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, dict):
                if block.get('type') == 'text':
                    texts.append(block.get('text', ''))
        return '\n'.join(texts)
    return ''


def extract_thinking(content) -> Optional[str]:
    """Extract thinking from message content."""
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get('type') == 'thinking':
                return block.get('thinking', '')
    return None


def extract_tool_calls(content) -> list:
    """Extract tool calls from message content."""
    tools = []
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get('type') == 'tool_use':
                tools.append({
                    'name': block.get('name', 'unknown'),
                    'input': block.get('input', {})
                })
    return tools


def process_session(filepath: Path, include_tools: bool = False,
                   include_thinking: bool = False, summary_only: bool = False) -> str:
    """Process a single session file and return formatted transcript."""
    messages = []
    metadata = {}
    first_ts = None
    last_ts = None

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            entry_type = entry.get('type')
            timestamp = entry.get('timestamp')

            if timestamp:
                ts = parse_timestamp(timestamp)
                if first_ts is None:
                    first_ts = ts
                last_ts = ts

            # Extract session metadata
            if entry_type == 'user' and not metadata:
                metadata = {
                    'sessionId': entry.get('sessionId', 'unknown'),
                    'version': entry.get('version', 'unknown'),
                    'cwd': entry.get('cwd', 'unknown'),
                    'gitBranch': entry.get('gitBranch', 'unknown'),
                }

            # Extract model from assistant messages
            if entry_type == 'assistant':
                msg = entry.get('message', {})
                if 'model' in msg and 'model' not in metadata:
                    metadata['model'] = msg['model']

            # Process user and assistant messages
            if entry_type in ('user', 'assistant'):
                msg = entry.get('message', {})
                role = msg.get('role', entry_type)
                content = msg.get('content', '')

                text = extract_text_content(content)
                thinking = extract_thinking(content) if include_thinking else None
                tools = extract_tool_calls(content) if include_tools else []

                if text or thinking or tools:
                    messages.append({
                        'role': role,
                        'text': text,
                        'thinking': thinking,
                        'tools': tools,
                        'timestamp': timestamp
                    })

    # Build output
    output = []

    # Header - use filename to ensure uniqueness (session_id can be shared by subagents)
    file_id = filepath.stem
    output.append(f"# Session: {file_id}")
    output.append("")

    if first_ts and last_ts:
        output.append(f"**Date:** {first_ts.strftime('%Y-%m-%d %H:%M')}")
        output.append(f"**Duration:** {format_duration(first_ts, last_ts)}")

    if metadata.get('model'):
        output.append(f"**Model:** {metadata['model']}")
    if metadata.get('cwd'):
        output.append(f"**Working Directory:** {metadata['cwd']}")
    if metadata.get('gitBranch'):
        output.append(f"**Git Branch:** {metadata['gitBranch']}")

    output.append("")
    output.append("---")
    output.append("")

    if summary_only:
        user_count = sum(1 for m in messages if m['role'] == 'user')
        assistant_count = sum(1 for m in messages if m['role'] == 'assistant')
        tool_count = sum(len(m['tools']) for m in messages)

        output.append(f"**Messages:** {user_count} user, {assistant_count} assistant")
        output.append(f"**Tool calls:** {tool_count}")

        # First user message preview - find first substantive prompt
        for m in messages:
            if m['role'] == 'user' and m['text']:
                text = m['text'].strip()
                # Skip very short prompts (likely just "Warmup" or partial)
                if len(text) < 20:
                    continue
                preview = text[:500].replace('\n', ' ')
                if len(text) > 500:
                    preview += '...'
                output.append(f"\n**First prompt:** {preview}")
                break
        else:
            # No substantive prompt found
            output.append(f"\n**First prompt:** (no substantive prompt found)")

        return '\n'.join(output)

    # Full transcript
    for msg in messages:
        role_header = "## User" if msg['role'] == 'user' else "## Assistant"
        output.append(role_header)
        output.append("")

        if msg['thinking']:
            output.append("> **Thinking:**")
            for line in msg['thinking'].split('\n'):
                output.append(f"> {line}")
            output.append("")

        if msg['text']:
            output.append(msg['text'])
            output.append("")

        if msg['tools']:
            for tool in msg['tools']:
                output.append(f"**Tool:** `{tool['name']}`")
                input_str = json.dumps(tool['input'], indent=2)
                if len(input_str) > 500:
                    input_str = input_str[:500] + '\n  ...(truncated)'
                output.append(f"```json\n{input_str}\n```")
                output.append("")

    return '\n'.join(output)


def has_substantive_content(filepath: Path, min_messages: int = 2) -> bool:
    """Check if session has substantive content (not just warmups or empty)."""
    user_count = 0
    assistant_count = 0
    has_real_content = False

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            entry_type = entry.get('type')
            if entry_type == 'user':
                msg = entry.get('message', {})
                content = msg.get('content', '')
                text = content if isinstance(content, str) else ''
                if isinstance(content, list):
                    text = ' '.join(b.get('text', '') for b in content if isinstance(b, dict))
                # Skip warmup-only sessions
                if text.strip().lower() not in ('warmup', ''):
                    has_real_content = True
                user_count += 1
            elif entry_type == 'assistant':
                assistant_count += 1

    return has_real_content and (user_count + assistant_count) >= min_messages


def main():
    parser = argparse.ArgumentParser(description='Extract transcripts from Claude Code sessions')
    parser.add_argument('path', help='Session file or directory')
    parser.add_argument('--include-tools', action='store_true', help='Include tool calls')
    parser.add_argument('--include-thinking', action='store_true', help='Include thinking blocks')
    parser.add_argument('--all', action='store_true', help='Process all .jsonl files in directory')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser.add_argument('--summary', action='store_true', help='Only output summary')
    parser.add_argument('--skip-empty', action='store_true', help='Skip empty and warmup-only sessions')
    parser.add_argument('--min-messages', type=int, default=2, help='Minimum messages for --skip-empty (default: 2)')

    args = parser.parse_args()

    path = Path(args.path)

    if args.all and path.is_dir():
        files = sorted(path.glob('*.jsonl'), key=lambda p: p.stat().st_mtime)
    elif path.is_file():
        files = [path]
    else:
        print(f"Error: {path} not found or invalid", file=sys.stderr)
        sys.exit(1)

    # Filter out empty/warmup sessions if requested
    if args.skip_empty:
        files = [f for f in files if has_substantive_content(f, args.min_messages)]

    output_file: Optional[TextIO] = None
    if args.output:
        output_file = open(args.output, 'w')

    seen_sessions = set()
    try:
        for filepath in files:
            # Track unique sessions by session ID to avoid duplicates
            session_id = filepath.stem
            if session_id in seen_sessions:
                continue
            seen_sessions.add(session_id)

            transcript = process_session(
                filepath,
                include_tools=args.include_tools,
                include_thinking=args.include_thinking,
                summary_only=args.summary
            )

            if output_file:
                output_file.write(transcript)
                output_file.write('\n\n---\n\n')
            else:
                print(transcript)
                print('\n---\n')
    finally:
        if output_file:
            output_file.close()


if __name__ == '__main__':
    main()
