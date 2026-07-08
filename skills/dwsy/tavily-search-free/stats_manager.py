#!/usr/bin/env python3
"""
MCP Stats Manager
=================
Tracks tool calls, logs, and statistics.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class MCPStatsManager:
    """Manages MCP tool call statistics and logs."""

    def __init__(self, skill_dir: Path):
        self.skill_dir = skill_dir
        self.stats_file = skill_dir / '.mcp.stats.json'
        self.logs_file = skill_dir / '.mcp.logs.jsonl'

        self.stats = self._load_stats()

    def _load_stats(self) -> Dict[str, Any]:
        """Load statistics from file."""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except:
                pass

        return {
            'session_name': 'default',
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'tools': {},
            'first_call': None,
            'last_call': None,
            'created_at': time.time()
        }

    def _save_stats(self):
        """Save statistics to file."""
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

    def record_call(self, tool_name: str, arguments: Dict[str, Any], success: bool, duration: float, error: str = None):
        """Record a tool call."""
        timestamp = time.time()
        call_record = {
            'timestamp': timestamp,
            'datetime': datetime.fromtimestamp(timestamp).isoformat(),
            'tool': tool_name,
            'arguments': arguments,
            'success': success,
            'duration': duration,
            'error': error
        }

        # Update stats
        self.stats['total_calls'] += 1
        if success:
            self.stats['successful_calls'] += 1
        else:
            self.stats['failed_calls'] += 1

        # Tool-specific stats
        if tool_name not in self.stats['tools']:
            self.stats['tools'][tool_name] = {
                'count': 0,
                'success': 0,
                'failed': 0,
                'total_duration': 0
            }

        self.stats['tools'][tool_name]['count'] += 1
        if success:
            self.stats['tools'][tool_name]['success'] += 1
        else:
            self.stats['tools'][tool_name]['failed'] += 1
        self.stats['tools'][tool_name]['total_duration'] += duration

        # Update timestamps
        if self.stats['first_call'] is None:
            self.stats['first_call'] = timestamp
        self.stats['last_call'] = timestamp

        # Save stats
        self._save_stats()

        # Append to logs
        with open(self.logs_file, 'a') as f:
            f.write(json.dumps(call_record) + '\n')

    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        return self.stats.copy()

    def get_logs(self, limit: int = 100, tool_name: str = None) -> List[Dict[str, Any]]:
        """Get recent logs."""
        if not self.logs_file.exists():
            return []

        logs = []
        with open(self.logs_file, 'r') as f:
            for line in f:
                try:
                    log = json.loads(line.strip())
                    if tool_name is None or log.get('tool') == tool_name:
                        logs.append(log)
                except:
                    pass

        # Sort by timestamp descending and limit
        logs.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        return logs[:limit]

    def set_session_name(self, name: str):
        """Set session name."""
        self.stats['session_name'] = name
        self._save_stats()

    def get_session_name(self) -> str:
        """Get session name."""
        return self.stats.get('session_name', 'default')

    def reset_stats(self):
        """Reset all statistics."""
        session_name = self.stats.get('session_name', 'default')
        self.stats = {
            'session_name': session_name,
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'tools': {},
            'first_call': None,
            'last_call': None,
            'created_at': time.time()
        }
        self._save_stats()

        # Clear logs
        if self.logs_file.exists():
            self.logs_file.unlink()

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status."""
        return {
            'stats': self.get_stats(),
            'uptime': time.time() - self.stats.get('created_at', time.time()),
            'log_file_size': self.logs_file.stat().st_size if self.logs_file.exists() else 0,
            'log_file_exists': self.logs_file.exists(),
            'stats_file_exists': self.stats_file.exists()
        }


# Global manager instance
_stats_manager: MCPStatsManager = None


def init_stats_manager(skill_dir: Path):
    """Initialize the global stats manager."""
    global _stats_manager
    _stats_manager = MCPStatsManager(skill_dir)


def get_stats_manager() -> MCPStatsManager:
    """Get the global stats manager."""
    return _stats_manager
