#!/usr/bin/env python3
"""Extract readable transcripts from Codex CLI session JSONL files."""

import json
import sys
import os
from datetime import datetime
from pathlib import Path


def parse_timestamp(ts: str) -> datetime:
    """Parse ISO timestamp."""
    return datetime.fromisoformat(ts.replace('Z', '+00:00'))


def process_codex_session(filepath: Path) -> str:
    """Process a Codex session file and return formatted transcript."""
    output = []
    session_meta = None
    messages = []
    tool_calls = []

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

            if entry_type == 'session_meta':
                payload = entry.get('payload', {})
                session_meta = {
                    'id': payload.get('id', 'unknown'),
                    'timestamp': payload.get('timestamp'),
                    'cwd': payload.get('cwd'),
                    'cli_version': payload.get('cli_version'),
                    'git': payload.get('git', {}),
                }
            elif entry_type == 'event_msg':
                # Codex wraps messages in event_msg payloads
                payload = entry.get('payload', {})
                msg_type = payload.get('type')

                if msg_type == 'user_message':
                    text = payload.get('message', '')
                    if text:
                        messages.append({
                            'role': 'user',
                            'text': text,
                            'tools': [],
                            'timestamp': entry.get('timestamp')
                        })
                elif msg_type == 'agent_message':
                    text = payload.get('message', '')
                    if text:
                        messages.append({
                            'role': 'assistant',
                            'text': text,
                            'tools': [],
                            'timestamp': entry.get('timestamp')
                        })
                elif msg_type == 'function_call':
                    name = payload.get('name', 'unknown')
                    tool_calls.append({'name': name})
            elif entry_type == 'message':
                # Legacy format support
                payload = entry.get('payload', {})
                role = payload.get('role', 'unknown')
                content = payload.get('content', [])

                # Extract text from content
                text_parts = []
                for item in content:
                    if isinstance(item, dict):
                        if item.get('type') == 'text':
                            text_parts.append(item.get('text', ''))
                        elif item.get('type') == 'tool_use':
                            tool_calls.append({
                                'name': item.get('name'),
                            })
                        elif item.get('type') == 'tool_result':
                            pass  # Skip tool results for brevity
                    elif isinstance(item, str):
                        text_parts.append(item)

                if text_parts:
                    messages.append({
                        'role': role,
                        'text': '\n'.join(text_parts),
                        'tools': [],
                        'timestamp': entry.get('timestamp')
                    })

    # Build output
    output.append(f"# Codex Session: {filepath.stem}")
    output.append("")

    if session_meta:
        if session_meta.get('timestamp'):
            try:
                ts = parse_timestamp(session_meta['timestamp'])
                output.append(f"**Date:** {ts.strftime('%Y-%m-%d %H:%M')}")
            except:
                pass
        if session_meta.get('cwd'):
            output.append(f"**Working Directory:** {session_meta['cwd']}")
        if session_meta.get('cli_version'):
            output.append(f"**Codex Version:** {session_meta['cli_version']}")
        git = session_meta.get('git', {})
        if git.get('branch'):
            output.append(f"**Git Branch:** {git['branch']}")
        if git.get('commit_hash'):
            output.append(f"**Commit:** {git['commit_hash'][:8]}")

    output.append("")
    user_count = len([m for m in messages if m['role'] == 'user'])
    assistant_count = len([m for m in messages if m['role'] == 'assistant'])
    output.append(f"**Messages:** {user_count} user, {assistant_count} assistant, {len(tool_calls)} tool calls")
    output.append("")
    output.append("---")
    output.append("")

    # Output messages
    for msg in messages:
        role_header = "## User" if msg['role'] == 'user' else "## Assistant"
        output.append(role_header)
        output.append("")

        if msg['text']:
            # Truncate very long messages
            text = msg['text']
            if len(text) > 2000:
                text = text[:2000] + "\n\n... (truncated)"
            output.append(text)
            output.append("")

    # Append tool summary if any
    if tool_calls:
        output.append("## Tools Used")
        output.append("")
        tool_names = {}
        for t in tool_calls:
            name = t.get('name', 'unknown')
            tool_names[name] = tool_names.get(name, 0) + 1
        for name, count in sorted(tool_names.items(), key=lambda x: -x[1])[:10]:
            output.append(f"- `{name}`: {count}")
        output.append("")

    return '\n'.join(output)


def process_history_entry(entry: dict) -> str:
    """Format a single history entry."""
    session_id = entry.get('session_id', 'unknown')[:8]
    ts = entry.get('ts', 0)
    text = entry.get('text', '')

    # Format timestamp
    try:
        dt = datetime.fromtimestamp(ts)
        date_str = dt.strftime('%Y-%m-%d %H:%M')
    except:
        date_str = 'unknown'

    output = []
    output.append(f"## Session {session_id} ({date_str})")
    output.append("")

    # Truncate very long prompts
    if len(text) > 3000:
        text = text[:3000] + "\n\n... (truncated)"

    output.append(text)
    output.append("")
    output.append("---")
    output.append("")

    return '\n'.join(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_codex_transcript.py <file.jsonl> [--history]")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    is_history = '--history' in sys.argv

    if is_history:
        # Process history.jsonl format
        output = ["# Codex History Entries", "", "---", ""]
        with open(filepath, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    output.append(process_history_entry(entry))
                except json.JSONDecodeError:
                    continue
        print('\n'.join(output))
    else:
        # Process session rollout format
        print(process_codex_session(filepath))


if __name__ == '__main__':
    main()
