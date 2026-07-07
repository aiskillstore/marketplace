#!/usr/bin/env python3
"""
Commit Message Drafter

What: Automatically generates commit messages by analyzing git changes
Why: Save time and create consistent, meaningful commit messages
How: Analyze git status and diff, then generate a structured message

This script is invoked by the commit-drafter skill when triggered by phrases like
"draft a commit for me to review".
"""

# Import required libraries
import subprocess  # For running git commands
import sys         # For system operations like exit
import re          # For pattern matching in git output
from typing import Dict, List, Tuple  # For type hints


def run_git_command(command: List[str]) -> Tuple[bool, str, str]:
    """
    What: Execute a git command safely
    Why: We need to interact with Git to analyze repository = storage location for code
    How: Use subprocess to run git commands and capture output

    Returns: (success, stdout, stderr)
    """
    try:
        # Run the git command with subprocess
        # capture_output means we collect stdout and stderr
        # text means we get strings instead of bytes
        # timeout prevents commands from hanging forever
        result = subprocess.run(
            ['git'] + command,
            capture_output=True,
            text=True,
            timeout=10
        )
        # Return success status (True if exit code was 0) along with output
        return (result.returncode == 0, result.stdout, result.stderr)
    except subprocess.TimeoutExpired:
        # Command took too long, return failure
        return (False, "", "Command timed out")
    except Exception as e:
        # Something else went wrong, return error message
        return (False, "", str(e))


def check_git_repository() -> bool:
    """
    What: Check if current directory is a Git repository = storage location for code
    Why: Commands will fail if not in a Git repo
    How: Try to run 'git rev-parse --git-dir'
    """
    success, _, _ = run_git_command(['rev-parse', '--git-dir'])
    return success


def get_staged_files() -> Dict[str, List[str]]:
    """
    What: Get list of staged files categorized by status
    Why: Understand what's being committed
    How: Parse 'git status --short' output

    Returns: Dict with keys: modified, added, deleted, renamed
    """
    # Run git status in machine-readable format
    success, stdout, _ = run_git_command(['status', '--short'])

    if not success:
        return {'modified': [], 'added': [], 'deleted': [], 'renamed': []}

    # Initialize our status dictionary
    status = {'modified': [], 'added': [], 'deleted': [], 'renamed': []}

    # Parse each line of git status output
    for line in stdout.strip().split('\n'):
        # Skip empty lines
        if not line or len(line) < 3:
            continue

        # Format: XY filename
        # X = index status (staging area), Y = working tree status
        # First character is what we care about (staging area)
        status_code = line[0]
        filename = line[3:].strip()

        # Categorize files by their status
        # M = modified, A = added, D = deleted, R = renamed
        if status_code == 'M':
            status['modified'].append(filename)
        elif status_code == 'A':
            status['added'].append(filename)
        elif status_code == 'D':
            status['deleted'].append(filename)
        elif status_code == 'R':
            status['renamed'].append(filename)

    return status


def analyze_diff() -> Dict[str, any]:
    """
    What: Analyze the staged diff to understand changes
    Why: Need statistics for the commit message
    How: Parse 'git diff --staged --stat' output
    """
    # Run git diff --staged --stat to get change statistics
    success, stdout, _ = run_git_command(['diff', '--staged', '--stat'])

    if not success or not stdout:
        return {'files': [], 'insertions': 0, 'deletions': 0}

    # Initialize counters
    files_changed = []
    total_insertions = 0
    total_deletions = 0

    # Parse each line of the stat output
    for line in stdout.strip().split('\n'):
        # Skip the summary line (at the end)
        if 'file' in line and 'changed' in line:
            continue

        # Skip empty lines
        if not line.strip():
            continue

        # Extract filename and stats
        # Format: "filename | 10 +++++-----"
        parts = line.split('|')
        if len(parts) == 2:
            filename = parts[0].strip()
            stats = parts[1].strip()

            # Count insertions and deletions from the +/- symbols
            insertions = stats.count('+')
            deletions = stats.count('-')

            files_changed.append({
                'name': filename,
                'insertions': insertions,
                'deletions': deletions
            })

            total_insertions += insertions
            total_deletions += deletions

    return {
        'files': files_changed,
        'insertions': total_insertions,
        'deletions': total_deletions
    }


def detect_change_type(status: Dict[str, List[str]], diff_stats: Dict) -> str:
    """
    What: Detect the type of change being committed
    Why: Helps create appropriate commit message prefix
    How: Analyze file statuses and diff content

    Returns: One of: Add, Update, Fix, Remove, Refactor = restructure code
    """
    # Check if primarily adding new files
    if len(status['added']) > len(status['modified']) + len(status['deleted']):
        return "Add"

    # Check if primarily deleting files
    if len(status['deleted']) > len(status['modified']) + len(status['added']):
        return "Remove"

    # Check diff content for "fix" or "bug" keywords (if available)
    success, diff_content, _ = run_git_command(['diff', '--staged'])
    if success and diff_content:
        diff_lower = diff_content.lower()
        if 'fix' in diff_lower or 'bug' in diff_lower or 'error' in diff_lower:
            return "Fix"

    # Default to Update for modifications
    return "Update"


def generate_commit_summary(status: Dict[str, List[str]], diff_stats: Dict) -> str:
    """
    What: Generate the first line (summary) of the commit message
    Why: Provide a concise overview of what changed
    How: Combine change type with affected files
    """
    # Detect what type of change this is
    change_type = detect_change_type(status, diff_stats)

    # Get all changed files
    all_files = (status['modified'] + status['added'] +
                status['deleted'] + status['renamed'])

    num_files = len(all_files)

    # Create summary based on number of files
    if num_files == 0:
        return "No changes staged"
    elif num_files == 1:
        # Single file: use the filename
        filename = all_files[0]
        # Remove directory path, keep just the filename
        filename = filename.split('/')[-1]
        return f"{change_type} {filename}"
    elif num_files <= 3:
        # Few files: list them all (just filenames, not paths)
        filenames = [f.split('/')[-1] for f in all_files]
        return f"{change_type} {', '.join(filenames)}"
    else:
        # Many files: just show count
        return f"{change_type} {num_files} files"


def draft_commit_message() -> str:
    """
    What: Provide git context for AI to draft commit message
    Why: Let the AI write meaningful commits based on actual changes
    How: Output git status, diff stats, and full diff for AI analysis
    """
    # Check if we're in a Git repository = storage location for code
    if not check_git_repository():
        return "Error: Not in a Git repository"

    # Get staged file information
    status = get_staged_files()
    all_files = (status['modified'] + status['added'] +
                status['deleted'] + status['renamed'])

    # Check if there are any staged changes
    if not all_files:
        return "Error: No staged changes. Use 'git add' to stage files first."

    # Analyze the diff statistics
    diff_stats = analyze_diff()

    # Get the full diff content for AI analysis
    success, full_diff, _ = run_git_command(['diff', '--staged'])
    if not success:
        full_diff = "(Unable to retrieve diff content)"

    # Build context output for AI consumption
    output = "=== GIT CHANGES READY FOR COMMIT ===\n\n"

    # Section 1: File Status Overview
    output += "FILES CHANGED:\n"
    if status['added']:
        output += f"  Added ({len(status['added'])}):\n"
        for f in status['added']:
            output += f"    + {f}\n"
    if status['modified']:
        output += f"  Modified ({len(status['modified'])}):\n"
        for f in status['modified']:
            output += f"    M {f}\n"
    if status['deleted']:
        output += f"  Deleted ({len(status['deleted'])}):\n"
        for f in status['deleted']:
            output += f"    - {f}\n"
    if status['renamed']:
        output += f"  Renamed ({len(status['renamed'])}):\n"
        for f in status['renamed']:
            output += f"    R {f}\n"
    output += "\n"

    # Section 2: Change Statistics
    output += "CHANGE STATISTICS:\n"
    for file_info in diff_stats['files']:
        name = file_info['name']
        ins = file_info['insertions']
        dels = file_info['deletions']
        output += f"  {name}: +{ins} -{dels}\n"
    output += f"\n  TOTAL: +{diff_stats['insertions']} insertions, "
    output += f"-{diff_stats['deletions']} deletions\n\n"

    # Section 3: Full Diff Content
    output += "FULL DIFF:\n"
    output += "─" * 60 + "\n"
    output += full_diff
    output += "\n" + "─" * 60 + "\n\n"

    # Section 4: Instructions for AI
    output += "=== INSTRUCTIONS FOR AI ===\n"
    output += "Based on the changes above, write a commit message with:\n"
    output += "1. A clear summary line describing the main change\n"
    output += "2. What/Why/How sections explaining the change\n"
    

    return output


def main():
    """
    What: Entry point for the commit drafter
    Why: Allow the skill to execute this script
    How: Draft message and print to stdout
    """
    # Draft the commit message
    message = draft_commit_message()

    # Print the message
    print(message)

    # Exit with appropriate code
    if message.startswith("Error:"):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()