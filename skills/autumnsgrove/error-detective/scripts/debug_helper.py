#!/usr/bin/env python3
"""
Debug Helper - Stack Trace Parsing and Debug Session Management

This utility provides automated assistance for debugging:
1. Parse and analyze stack traces
2. Extract error patterns from logs
3. Manage debug sessions with timestamped notes

Usage:
    python debug_helper.py parse-trace error.log
    python debug_helper.py analyze-log application.log --pattern ERROR
    python debug_helper.py session start "Description of issue"
    python debug_helper.py session note "Finding or hypothesis"
    python debug_helper.py session close "Solution description"
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class StackTraceParser:
    """Parse and analyze stack traces from multiple languages."""

    # Regex patterns for different stack trace formats
    PATTERNS = {
        'python': {
            'traceback_start': r'^Traceback \(most recent call last\):',
            'file_line': r'^\s+File "([^"]+)", line (\d+), in (.+)',
            'error_line': r'^(\w+(?:Error|Exception|Warning)): (.+)',
            'code_line': r'^\s+(.+)',
        },
        'javascript': {
            'error_line': r'^(\w+Error): (.+)',
            'at_line': r'^\s+at (.+) \(([^:]+):(\d+):(\d+)\)',
            'at_line_simple': r'^\s+at ([^:]+):(\d+):(\d+)',
        },
        'java': {
            'exception_line': r'^([\w\.]+(?:Exception|Error)): (.+)',
            'at_line': r'^\s+at ([\w\.$]+)\(([^:]+):(\d+)\)',
            'caused_by': r'^Caused by: ([\w\.]+(?:Exception|Error)): (.+)',
        },
        'go': {
            'panic_line': r'^panic: (.+)',
            'goroutine': r'^goroutine \d+ \[.+\]:',
            'file_line': r'^(.+)\(.*\)',
            'location': r'^\s+([^:]+):(\d+)',
        },
    }

    def parse_file(self, filepath: str) -> List[Dict]:
        """Parse stack traces from a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.parse_text(content)
        except FileNotFoundError:
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            return []
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return []

    def parse_text(self, text: str) -> List[Dict]:
        """Parse stack traces from text content."""
        traces = []

        # Try each language pattern
        for lang, patterns in self.PATTERNS.items():
            if lang == 'python':
                traces.extend(self._parse_python(text))
            elif lang == 'javascript':
                traces.extend(self._parse_javascript(text))
            elif lang == 'java':
                traces.extend(self._parse_java(text))
            elif lang == 'go':
                traces.extend(self._parse_go(text))

        return traces

    def _parse_python(self, text: str) -> List[Dict]:
        """Parse Python stack traces."""
        traces = []
        lines = text.split('\n')
        i = 0

        while i < len(lines):
            if re.match(self.PATTERNS['python']['traceback_start'], lines[i]):
                trace = {
                    'language': 'python',
                    'stack': [],
                    'error_type': None,
                    'error_message': None,
                }
                i += 1

                # Parse stack frames
                while i < len(lines):
                    file_match = re.match(self.PATTERNS['python']['file_line'], lines[i])
                    if file_match:
                        filename, line_num, function = file_match.groups()
                        code = lines[i + 1].strip() if i + 1 < len(lines) else ''
                        trace['stack'].append({
                            'file': filename,
                            'line': int(line_num),
                            'function': function,
                            'code': code,
                        })
                        i += 2
                    else:
                        error_match = re.match(self.PATTERNS['python']['error_line'], lines[i])
                        if error_match:
                            trace['error_type'] = error_match.group(1)
                            trace['error_message'] = error_match.group(2)
                            traces.append(trace)
                        break
            i += 1

        return traces

    def _parse_javascript(self, text: str) -> List[Dict]:
        """Parse JavaScript stack traces."""
        traces = []
        lines = text.split('\n')
        i = 0

        while i < len(lines):
            error_match = re.match(self.PATTERNS['javascript']['error_line'], lines[i])
            if error_match:
                trace = {
                    'language': 'javascript',
                    'error_type': error_match.group(1),
                    'error_message': error_match.group(2),
                    'stack': [],
                }
                i += 1

                # Parse stack frames
                while i < len(lines):
                    at_match = re.match(self.PATTERNS['javascript']['at_line'], lines[i])
                    if at_match:
                        function, filename, line_num, col = at_match.groups()
                        trace['stack'].append({
                            'function': function,
                            'file': filename,
                            'line': int(line_num),
                            'column': int(col),
                        })
                        i += 1
                    else:
                        simple_match = re.match(self.PATTERNS['javascript']['at_line_simple'], lines[i])
                        if simple_match:
                            filename, line_num, col = simple_match.groups()
                            trace['stack'].append({
                                'file': filename,
                                'line': int(line_num),
                                'column': int(col),
                            })
                            i += 1
                        else:
                            break

                if trace['stack']:
                    traces.append(trace)
            i += 1

        return traces

    def _parse_java(self, text: str) -> List[Dict]:
        """Parse Java stack traces."""
        traces = []
        lines = text.split('\n')
        i = 0

        while i < len(lines):
            exception_match = re.match(self.PATTERNS['java']['exception_line'], lines[i])
            if exception_match:
                trace = {
                    'language': 'java',
                    'error_type': exception_match.group(1),
                    'error_message': exception_match.group(2),
                    'stack': [],
                    'caused_by': [],
                }
                i += 1

                # Parse stack frames
                while i < len(lines):
                    at_match = re.match(self.PATTERNS['java']['at_line'], lines[i])
                    if at_match:
                        method, filename, line_num = at_match.groups()
                        trace['stack'].append({
                            'method': method,
                            'file': filename,
                            'line': int(line_num),
                        })
                        i += 1
                    else:
                        caused_match = re.match(self.PATTERNS['java']['caused_by'], lines[i])
                        if caused_match:
                            trace['caused_by'].append({
                                'type': caused_match.group(1),
                                'message': caused_match.group(2),
                            })
                            i += 1
                        else:
                            break

                traces.append(trace)
            i += 1

        return traces

    def _parse_go(self, text: str) -> List[Dict]:
        """Parse Go panic stack traces."""
        traces = []
        lines = text.split('\n')
        i = 0

        while i < len(lines):
            panic_match = re.match(self.PATTERNS['go']['panic_line'], lines[i])
            if panic_match:
                trace = {
                    'language': 'go',
                    'error_message': panic_match.group(1),
                    'stack': [],
                }
                i += 1

                # Parse stack frames
                while i < len(lines):
                    if re.match(self.PATTERNS['go']['goroutine'], lines[i]):
                        i += 1
                        continue

                    func_match = re.match(self.PATTERNS['go']['file_line'], lines[i])
                    if func_match and i + 1 < len(lines):
                        function = func_match.group(1)
                        loc_match = re.match(self.PATTERNS['go']['location'], lines[i + 1])
                        if loc_match:
                            filename, line_num = loc_match.groups()
                            trace['stack'].append({
                                'function': function,
                                'file': filename,
                                'line': int(line_num),
                            })
                            i += 2
                        else:
                            i += 1
                    else:
                        if trace['stack']:
                            break
                        i += 1

                if trace['stack']:
                    traces.append(trace)
            i += 1

        return traces

    def format_trace(self, trace: Dict) -> str:
        """Format a parsed trace for display."""
        lines = []
        lines.append(f"\n{'='*60}")
        lines.append(f"Language: {trace['language'].upper()}")

        if 'error_type' in trace and trace['error_type']:
            lines.append(f"Error Type: {trace['error_type']}")
        if 'error_message' in trace and trace['error_message']:
            lines.append(f"Error Message: {trace['error_message']}")

        lines.append(f"\nStack Trace:")
        lines.append(f"{'-'*60}")

        for i, frame in enumerate(trace['stack'], 1):
            lines.append(f"\n{i}. {frame.get('function', frame.get('method', 'N/A'))}")
            lines.append(f"   File: {frame['file']}:{frame['line']}")
            if 'code' in frame and frame['code']:
                lines.append(f"   Code: {frame['code']}")

        if 'caused_by' in trace and trace['caused_by']:
            lines.append(f"\nCaused By:")
            for cause in trace['caused_by']:
                lines.append(f"  - {cause['type']}: {cause['message']}")

        lines.append(f"{'='*60}\n")
        return '\n'.join(lines)


class LogAnalyzer:
    """Analyze log files for error patterns."""

    def analyze_file(self, filepath: str, pattern: str = None) -> Dict:
        """Analyze log file for errors and patterns."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            return {}

        analysis = {
            'total_lines': len(lines),
            'errors': defaultdict(int),
            'warnings': defaultdict(int),
            'patterns': defaultdict(list),
            'timestamps': [],
        }

        error_pattern = re.compile(r'(ERROR|CRITICAL|FATAL)', re.IGNORECASE)
        warning_pattern = re.compile(r'WARN(?:ING)?', re.IGNORECASE)
        timestamp_pattern = re.compile(r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}')

        for i, line in enumerate(lines, 1):
            # Check for errors
            if error_pattern.search(line):
                # Extract error message
                error_msg = self._extract_error_message(line)
                analysis['errors'][error_msg] += 1

            # Check for warnings
            if warning_pattern.search(line):
                warning_msg = self._extract_error_message(line)
                analysis['warnings'][warning_msg] += 1

            # Extract timestamps
            ts_match = timestamp_pattern.search(line)
            if ts_match:
                analysis['timestamps'].append(ts_match.group())

            # Custom pattern matching
            if pattern and pattern in line:
                analysis['patterns'][pattern].append({
                    'line_number': i,
                    'content': line.strip(),
                })

        return analysis

    def _extract_error_message(self, line: str) -> str:
        """Extract the core error message from a log line."""
        # Remove timestamp
        line = re.sub(r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}[.,\d]*', '', line)
        # Remove log level
        line = re.sub(r'\b(ERROR|WARN(?:ING)?|INFO|DEBUG|CRITICAL|FATAL)\b', '', line, flags=re.IGNORECASE)
        # Remove logger name
        line = re.sub(r'\[[\w\.]+\]', '', line)
        # Clean up
        line = line.strip(' :|-')
        return line[:100]  # Limit length

    def format_analysis(self, analysis: Dict) -> str:
        """Format analysis results for display."""
        lines = []
        lines.append(f"\n{'='*60}")
        lines.append(f"Log Analysis Report")
        lines.append(f"{'='*60}")
        lines.append(f"Total Lines: {analysis['total_lines']}")
        lines.append(f"Total Errors: {sum(analysis['errors'].values())}")
        lines.append(f"Total Warnings: {sum(analysis['warnings'].values())}")

        if analysis['errors']:
            lines.append(f"\nTop Errors:")
            lines.append(f"{'-'*60}")
            sorted_errors = sorted(analysis['errors'].items(), key=lambda x: x[1], reverse=True)
            for msg, count in sorted_errors[:10]:
                lines.append(f"  [{count:3d}x] {msg}")

        if analysis['warnings']:
            lines.append(f"\nTop Warnings:")
            lines.append(f"{'-'*60}")
            sorted_warnings = sorted(analysis['warnings'].items(), key=lambda x: x[1], reverse=True)
            for msg, count in sorted_warnings[:10]:
                lines.append(f"  [{count:3d}x] {msg}")

        if analysis['timestamps'] and len(analysis['timestamps']) > 1:
            lines.append(f"\nTime Range:")
            lines.append(f"  First: {analysis['timestamps'][0]}")
            lines.append(f"  Last:  {analysis['timestamps'][-1]}")

        lines.append(f"{'='*60}\n")
        return '\n'.join(lines)


class DebugSession:
    """Manage debug sessions with timestamped notes."""

    def __init__(self, session_dir: str = ".debug_sessions"):
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(exist_ok=True)
        self.current_session_file = self.session_dir / "current_session.json"

    def start(self, description: str) -> Dict:
        """Start a new debug session."""
        session = {
            'id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'description': description,
            'start_time': datetime.now().isoformat(),
            'notes': [],
            'status': 'active',
        }

        self._save_current_session(session)
        print(f"Started debug session: {session['id']}")
        print(f"Description: {description}")
        return session

    def add_note(self, note: str) -> None:
        """Add a note to the current debug session."""
        session = self._load_current_session()
        if not session:
            print("No active debug session. Start one with: session start <description>")
            return

        session['notes'].append({
            'timestamp': datetime.now().isoformat(),
            'content': note,
        })

        self._save_current_session(session)
        print(f"Added note to session {session['id']}")

    def close(self, solution: str) -> None:
        """Close the current debug session with a solution."""
        session = self._load_current_session()
        if not session:
            print("No active debug session to close.")
            return

        session['end_time'] = datetime.now().isoformat()
        session['solution'] = solution
        session['status'] = 'resolved'

        # Save to archive
        archive_file = self.session_dir / f"session_{session['id']}.json"
        with open(archive_file, 'w') as f:
            json.dump(session, f, indent=2)

        # Remove current session
        if self.current_session_file.exists():
            self.current_session_file.unlink()

        print(f"Closed debug session: {session['id']}")
        print(f"Solution: {solution}")
        print(f"Saved to: {archive_file}")

    def show_current(self) -> None:
        """Display the current debug session."""
        session = self._load_current_session()
        if not session:
            print("No active debug session.")
            return

        print(f"\n{'='*60}")
        print(f"Debug Session: {session['id']}")
        print(f"{'='*60}")
        print(f"Description: {session['description']}")
        print(f"Started: {session['start_time']}")
        print(f"Status: {session['status']}")

        if session['notes']:
            print(f"\nNotes:")
            print(f"{'-'*60}")
            for i, note in enumerate(session['notes'], 1):
                print(f"\n{i}. [{note['timestamp']}]")
                print(f"   {note['content']}")

        print(f"{'='*60}\n")

    def _save_current_session(self, session: Dict) -> None:
        """Save the current session to file."""
        with open(self.current_session_file, 'w') as f:
            json.dump(session, f, indent=2)

    def _load_current_session(self) -> Optional[Dict]:
        """Load the current session from file."""
        if not self.current_session_file.exists():
            return None

        try:
            with open(self.current_session_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None


def main():
    """Main entry point for debug helper CLI."""
    parser = argparse.ArgumentParser(
        description='Debug Helper - Stack trace parsing and debug session management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Parse trace command
    parse_parser = subparsers.add_parser('parse-trace', help='Parse stack trace from file')
    parse_parser.add_argument('file', help='File containing stack trace')
    parse_parser.add_argument('--format', choices=['text', 'json'], default='text',
                             help='Output format (default: text)')

    # Analyze log command
    analyze_parser = subparsers.add_parser('analyze-log', help='Analyze log file for errors')
    analyze_parser.add_argument('file', help='Log file to analyze')
    analyze_parser.add_argument('--pattern', help='Custom pattern to search for')
    analyze_parser.add_argument('--format', choices=['text', 'json'], default='text',
                               help='Output format (default: text)')

    # Session commands
    session_parser = subparsers.add_parser('session', help='Manage debug sessions')
    session_subparsers = session_parser.add_subparsers(dest='session_command')

    start_parser = session_subparsers.add_parser('start', help='Start new debug session')
    start_parser.add_argument('description', help='Description of the issue')

    note_parser = session_subparsers.add_parser('note', help='Add note to current session')
    note_parser.add_argument('note', help='Note content')

    close_parser = session_subparsers.add_parser('close', help='Close current session')
    close_parser.add_argument('solution', help='Description of the solution')

    session_subparsers.add_parser('show', help='Show current session')

    args = parser.parse_args()

    # Execute command
    if args.command == 'parse-trace':
        parser_obj = StackTraceParser()
        traces = parser_obj.parse_file(args.file)

        if args.format == 'json':
            print(json.dumps(traces, indent=2))
        else:
            if not traces:
                print("No stack traces found in file.")
            for trace in traces:
                print(parser_obj.format_trace(trace))

    elif args.command == 'analyze-log':
        analyzer = LogAnalyzer()
        analysis = analyzer.analyze_file(args.file, args.pattern)

        if args.format == 'json':
            # Convert defaultdicts to regular dicts for JSON serialization
            json_analysis = {
                'total_lines': analysis['total_lines'],
                'errors': dict(analysis['errors']),
                'warnings': dict(analysis['warnings']),
                'patterns': {k: list(v) for k, v in analysis['patterns'].items()},
                'timestamps': analysis['timestamps'],
            }
            print(json.dumps(json_analysis, indent=2))
        else:
            print(analyzer.format_analysis(analysis))

    elif args.command == 'session':
        session_mgr = DebugSession()

        if args.session_command == 'start':
            session_mgr.start(args.description)
        elif args.session_command == 'note':
            session_mgr.add_note(args.note)
        elif args.session_command == 'close':
            session_mgr.close(args.solution)
        elif args.session_command == 'show':
            session_mgr.show_current()
        else:
            session_parser.print_help()

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
