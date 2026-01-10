#!/usr/bin/env python3
"""DuckDB-based indexer for Claude Code session transcripts."""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

try:
    import duckdb
except ImportError:
    print("Error: duckdb not installed. Run: pip install duckdb", file=sys.stderr)
    sys.exit(1)


# Default paths
DEFAULT_DB_PATH = Path.home() / ".claude" / "transcript-index" / "sessions.duckdb"
# Check both possible session locations
DEFAULT_SESSIONS_PATHS = [
    Path.home() / "Library" / "Application Support" / "Claude" / "sessions",  # macOS
    Path.home() / ".claude" / "projects",  # Claude Code CLI projects
    Path.home() / ".config" / "claude" / "sessions",  # Linux
]

# Schema - matches PLAN.md
SCHEMA = """
-- sessions table: file_path is the unique key (not session_id)
CREATE TABLE IF NOT EXISTS sessions (
    file_path TEXT PRIMARY KEY,
    session_id TEXT,
    source TEXT NOT NULL,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    duration_seconds INTEGER,
    model TEXT,
    cwd TEXT,
    git_branch TEXT,
    git_repo TEXT,
    message_count INTEGER,
    tool_count INTEGER,
    file_mtime DOUBLE,
    file_size BIGINT,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- messages table with id and foreign key reference
CREATE SEQUENCE IF NOT EXISTS messages_id_seq;
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER DEFAULT nextval('messages_id_seq') PRIMARY KEY,
    file_path TEXT NOT NULL REFERENCES sessions(file_path),
    message_idx INTEGER NOT NULL,
    role TEXT NOT NULL,
    content TEXT,
    timestamp TIMESTAMP,
    has_thinking BOOLEAN DEFAULT FALSE,
    UNIQUE(file_path, message_idx)
);

-- tool_calls table with id and foreign key reference
CREATE SEQUENCE IF NOT EXISTS tool_calls_id_seq;
CREATE TABLE IF NOT EXISTS tool_calls (
    id INTEGER DEFAULT nextval('tool_calls_id_seq') PRIMARY KEY,
    file_path TEXT NOT NULL REFERENCES sessions(file_path),
    message_idx INTEGER,
    tool_name TEXT NOT NULL
);

-- Indexes for search and lookup
-- Note: No index on messages.content - ILIKE search works without it and
-- avoids DuckDB's ART index key size limit (122KB) for large message content
CREATE INDEX IF NOT EXISTS idx_messages_file_path ON messages(file_path);
CREATE INDEX IF NOT EXISTS idx_tool_calls_file_path ON tool_calls(file_path);
"""


def parse_timestamp(ts: str) -> datetime:
    """Parse ISO timestamp."""
    return datetime.fromisoformat(ts.replace('Z', '+00:00'))


def extract_text_content(content) -> str:
    """Extract text from message content."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, dict) and block.get('type') == 'text':
                texts.append(block.get('text', ''))
        return '\n'.join(texts)
    return ''


def extract_tool_calls(content) -> list:
    """Extract tool calls from message content."""
    tools = []
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get('type') == 'tool_use':
                tools.append(block.get('name', 'unknown'))
    return tools


def has_thinking(content) -> bool:
    """Check if content has thinking blocks."""
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get('type') == 'thinking':
                return True
    return False


def parse_session_file(filepath: Path) -> dict:
    """Parse a Claude Code session JSONL file."""
    messages = []
    tool_calls = []
    metadata = {}
    first_ts = None
    last_ts = None
    message_idx = 0

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
                try:
                    ts = parse_timestamp(timestamp)
                    if first_ts is None:
                        first_ts = ts
                    last_ts = ts
                except (ValueError, TypeError):
                    pass

            # Extract session metadata from first user entry
            if entry_type == 'user' and not metadata:
                metadata = {
                    'session_id': entry.get('sessionId', 'unknown'),
                    'cwd': entry.get('cwd'),
                    'git_branch': entry.get('gitBranch'),
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
                tools = extract_tool_calls(content)
                thinking = has_thinking(content)

                if text or tools:
                    messages.append({
                        'message_idx': message_idx,
                        'role': role,
                        'content': text,
                        'timestamp': timestamp,
                        'has_thinking': thinking,
                    })

                    for tool_name in tools:
                        tool_calls.append({
                            'message_idx': message_idx,
                            'tool_name': tool_name,
                        })

                    message_idx += 1

    # Calculate duration
    duration_seconds = None
    if first_ts and last_ts:
        duration_seconds = int((last_ts - first_ts).total_seconds())

    # Derive git_repo from cwd
    git_repo = None
    if metadata.get('cwd'):
        git_repo = Path(metadata['cwd']).name

    return {
        'session_id': metadata.get('session_id'),
        'source': 'claude_code',
        'started_at': first_ts,
        'ended_at': last_ts,
        'duration_seconds': duration_seconds,
        'model': metadata.get('model'),
        'cwd': metadata.get('cwd'),
        'git_branch': metadata.get('git_branch'),
        'git_repo': git_repo,
        'messages': messages,
        'tool_calls': tool_calls,
    }


def should_reindex(file_path: Path, con: duckdb.DuckDBPyConnection) -> bool:
    """Check if file needs reindexing."""
    try:
        stat = file_path.stat()
        current_mtime = stat.st_mtime
        current_size = stat.st_size
    except OSError:
        return False

    result = con.execute("""
        SELECT file_mtime, file_size FROM sessions 
        WHERE file_path = ?
    """, [str(file_path)]).fetchone()

    if result is None:
        return True  # New file

    stored_mtime, stored_size = result
    return current_mtime != stored_mtime or current_size != stored_size


def delete_session(file_path: str, con: duckdb.DuckDBPyConnection):
    """Remove all data for a session file."""
    con.execute("DELETE FROM tool_calls WHERE file_path = ?", [file_path])
    con.execute("DELETE FROM messages WHERE file_path = ?", [file_path])
    con.execute("DELETE FROM sessions WHERE file_path = ?", [file_path])


def index_file(file_path: Path, con: duckdb.DuckDBPyConnection) -> bool:
    """Index a single session file. Returns True if indexed."""
    if not should_reindex(file_path, con):
        return False

    # Delete existing data
    delete_session(str(file_path), con)

    # Parse the file
    data = parse_session_file(file_path)

    # Get file stats
    stat = file_path.stat()

    # Insert session
    con.execute("""
        INSERT INTO sessions (
            file_path, session_id, source, started_at, ended_at,
            duration_seconds, model, cwd, git_branch, git_repo,
            message_count, tool_count, file_mtime, file_size
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        str(file_path),
        data['session_id'],
        data['source'],
        data['started_at'],
        data['ended_at'],
        data['duration_seconds'],
        data['model'],
        data['cwd'],
        data['git_branch'],
        data['git_repo'],
        len(data['messages']),
        len(data['tool_calls']),
        stat.st_mtime,
        stat.st_size,
    ])

    # Insert messages
    for msg in data['messages']:
        con.execute("""
            INSERT INTO messages (file_path, message_idx, role, content, timestamp, has_thinking)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            str(file_path),
            msg['message_idx'],
            msg['role'],
            msg['content'],
            msg['timestamp'],
            msg['has_thinking'],
        ])

    # Insert tool calls
    for tool in data['tool_calls']:
        con.execute("""
            INSERT INTO tool_calls (file_path, message_idx, tool_name)
            VALUES (?, ?, ?)
        """, [
            str(file_path),
            tool['message_idx'],
            tool['tool_name'],
        ])

    return True


def cleanup_deleted_files(con: duckdb.DuckDBPyConnection) -> int:
    """Remove entries for files that no longer exist."""
    indexed_files = con.execute("SELECT file_path FROM sessions").fetchall()
    deleted = 0
    for (file_path,) in indexed_files:
        if not Path(file_path).exists():
            delete_session(file_path, con)
            deleted += 1
    return deleted


def cmd_index(args, con: duckdb.DuckDBPyConnection):
    """Index command handler."""
    if args.path:
        # User-specified path - expand ~ and check existence
        sessions_path = Path(args.path).expanduser()
        if not sessions_path.exists():
            print(f"Error: Sessions directory not found: {sessions_path}", file=sys.stderr)
            sys.exit(1)
        sessions_paths = [sessions_path]
    else:
        # Use default paths - check all that exist
        sessions_paths = [p for p in DEFAULT_SESSIONS_PATHS if p.exists()]
        if not sessions_paths:
            print("Error: No sessions directory found. Checked:", file=sys.stderr)
            for p in DEFAULT_SESSIONS_PATHS:
                print(f"  - {p}", file=sys.stderr)
            sys.exit(1)

    # Get all JSONL files from all paths (recursively for project directories)
    all_files = []
    for sessions_path in sessions_paths:
        all_files.extend(sessions_path.glob('**/*.jsonl'))
    files = sorted(all_files, key=lambda p: p.stat().st_mtime, reverse=True)

    if args.limit:
        files = files[:args.limit]

    if args.full:
        # Force full reindex - delete all data first
        con.execute("DELETE FROM tool_calls")
        con.execute("DELETE FROM messages")
        con.execute("DELETE FROM sessions")
        print("Full reindex: cleared existing data")

    indexed = 0
    skipped = 0
    for filepath in files:
        if index_file(filepath, con):
            indexed += 1
            if not args.quiet:
                print(f"Indexed: {filepath.name}")
        else:
            skipped += 1

    # Cleanup deleted files
    deleted = cleanup_deleted_files(con)

    print(f"\nSummary: {indexed} indexed, {skipped} skipped (unchanged), {deleted} removed (deleted files)")


def cmd_recent(args, con: duckdb.DuckDBPyConnection):
    """Recent sessions command handler."""
    limit = args.limit or 10

    query = "SELECT file_path, session_id, started_at, duration_seconds, model, cwd, git_branch, message_count, tool_count FROM sessions"
    params = []

    conditions = []
    if args.project:
        conditions.append("cwd ILIKE ?")
        params.append(f"%{args.project}%")

    if args.since:
        # Parse duration like "7d", "24h"
        since = args.since.lower()
        try:
            if since.endswith('d'):
                days = int(since[:-1])
                cutoff = datetime.now() - timedelta(days=days)
            elif since.endswith('h'):
                hours = int(since[:-1])
                cutoff = datetime.now() - timedelta(hours=hours)
            else:
                print(f"Invalid --since format: {args.since}. Use '7d' or '24h'", file=sys.stderr)
                sys.exit(1)
        except ValueError:
            print(f"Invalid --since value: {args.since}. Use format like '7d' or '24h'", file=sys.stderr)
            sys.exit(1)
        conditions.append("started_at >= ?")
        params.append(cutoff)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY started_at DESC LIMIT ?"
    params.append(limit)

    results = con.execute(query, params).fetchall()

    if not results:
        print("No sessions found.")
        return

    for row in results:
        file_path, session_id, started_at, duration, model, cwd, git_branch, msg_count, tool_count = row
        duration_str = f"{duration // 60}m {duration % 60}s" if duration else "?"
        date_str = started_at.strftime('%Y-%m-%d %H:%M') if started_at else "?"
        cwd_short = Path(cwd).name if cwd else "?"

        print(f"{date_str} | {duration_str:>8} | {msg_count:>3} msgs | {tool_count:>4} tools | {cwd_short}")
        print(f"  {file_path}")
        print()


def cmd_search(args, con: duckdb.DuckDBPyConnection):
    """Search command handler."""
    query_text = args.query
    limit = args.limit or 20

    query = """
        SELECT DISTINCT s.file_path, s.started_at, s.cwd, s.git_branch, 
               m.content, m.role
        FROM messages m
        JOIN sessions s ON m.file_path = s.file_path
        WHERE m.content ILIKE ?
    """
    params = [f"%{query_text}%"]

    if args.cwd:
        query += " AND s.cwd ILIKE ?"
        params.append(f"%{args.cwd}%")

    query += " ORDER BY s.started_at DESC LIMIT ?"
    params.append(limit)

    results = con.execute(query, params).fetchall()

    if not results:
        print(f"No matches for '{query_text}'")
        return

    current_file = None
    for row in results:
        file_path, started_at, cwd, git_branch, content, role = row

        if file_path != current_file:
            current_file = file_path
            date_str = started_at.strftime('%Y-%m-%d %H:%M') if started_at else "?"
            cwd_short = Path(cwd).name if cwd else "?"
            print(f"\n{'='*60}")
            print(f"{date_str} | {cwd_short} | {git_branch or '?'}")
            print(f"  {file_path}")

        # Show context around match
        content_lower = content.lower()
        query_lower = query_text.lower()
        idx = content_lower.find(query_lower)
        if idx >= 0:
            start = max(0, idx - 50)
            end = min(len(content), idx + len(query_text) + 50)
            snippet = content[start:end].replace('\n', ' ')
            if start > 0:
                snippet = "..." + snippet
            if end < len(content):
                snippet = snippet + "..."
            print(f"  [{role}] {snippet}")


def cmd_show(args, con: duckdb.DuckDBPyConnection):
    """Show session command handler."""
    file_path = args.file_path

    # Check if session exists
    session = con.execute("""
        SELECT file_path, session_id, started_at, ended_at, duration_seconds,
               model, cwd, git_branch, message_count, tool_count
        FROM sessions WHERE file_path = ?
    """, [file_path]).fetchone()

    if not session:
        print(f"Session not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    file_path, session_id, started_at, ended_at, duration, model, cwd, git_branch, msg_count, tool_count = session

    print(f"# Session: {Path(file_path).stem}")
    print()
    if started_at:
        print(f"**Date:** {started_at.strftime('%Y-%m-%d %H:%M')}")
    if duration:
        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            print(f"**Duration:** {hours}h {minutes}m {seconds}s")
        elif minutes > 0:
            print(f"**Duration:** {minutes}m {seconds}s")
        else:
            print(f"**Duration:** {seconds}s")
    if model:
        print(f"**Model:** {model}")
    if cwd:
        print(f"**Working Directory:** {cwd}")
    if git_branch:
        print(f"**Git Branch:** {git_branch}")
    print(f"**Messages:** {msg_count}")
    print(f"**Tool Calls:** {tool_count}")
    print()
    print("---")
    print()

    if args.summary:
        # Get first user message as preview
        first_msg = con.execute("""
            SELECT content FROM messages 
            WHERE file_path = ? AND role = 'user' AND LENGTH(content) > 20
            ORDER BY message_idx LIMIT 1
        """, [file_path]).fetchone()

        if first_msg:
            preview = first_msg[0][:500].replace('\n', ' ')
            if len(first_msg[0]) > 500:
                preview += "..."
            print(f"**First prompt:** {preview}")
        return

    # Full transcript
    messages = con.execute("""
        SELECT message_idx, role, content, has_thinking
        FROM messages WHERE file_path = ?
        ORDER BY message_idx
    """, [file_path]).fetchall()

    for msg_idx, role, content, thinking in messages:
        role_header = "## User" if role == 'user' else "## Assistant"
        print(role_header)
        print()
        if content:
            print(content)
        print()


def main():
    parser = argparse.ArgumentParser(description='DuckDB-based transcript indexer')
    parser.add_argument('--db', type=str, help=f'Database path (default: {DEFAULT_DB_PATH})')

    subparsers = parser.add_subparsers(dest='command', required=True)

    # index command
    index_parser = subparsers.add_parser('index', help='Index session files')
    index_parser.add_argument('--path', type=str, help='Sessions directory (default: auto-detect)')
    index_parser.add_argument('--full', action='store_true', help='Force full reindex')
    index_parser.add_argument('--limit', type=int, help='Limit number of files to process')
    index_parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode')

    # recent command
    recent_parser = subparsers.add_parser('recent', help='List recent sessions')
    recent_parser.add_argument('--limit', '-n', type=int, default=10, help='Number of sessions')
    recent_parser.add_argument('--project', type=str, help='Filter by project (cwd contains)')
    recent_parser.add_argument('--since', type=str, help='Filter by time (e.g., 7d, 24h)')

    # search command
    search_parser = subparsers.add_parser('search', help='Search sessions')
    search_parser.add_argument('query', type=str, help='Search query')
    search_parser.add_argument('--cwd', type=str, help='Filter by working directory')
    search_parser.add_argument('--limit', '-n', type=int, default=20, help='Max results')

    # show command
    show_parser = subparsers.add_parser('show', help='Show session transcript')
    show_parser.add_argument('file_path', type=str, help='Session file path')
    show_parser.add_argument('--summary', action='store_true', help='Summary only')

    args = parser.parse_args()

    # Setup database
    db_path = Path(args.db) if args.db else DEFAULT_DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(db_path))
    con.execute(SCHEMA)

    # Dispatch command
    if args.command == 'index':
        cmd_index(args, con)
    elif args.command == 'recent':
        cmd_recent(args, con)
    elif args.command == 'search':
        cmd_search(args, con)
    elif args.command == 'show':
        cmd_show(args, con)

    con.close()


if __name__ == '__main__':
    main()
