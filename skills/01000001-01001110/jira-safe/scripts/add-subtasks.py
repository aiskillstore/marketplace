#!/usr/bin/env python3
"""
Jira Add Subtasks (Python)
Add subtasks to an existing story.
Following jira-safe skill patterns for Next-Gen projects.

Usage:
  python jira-add-subtasks.py demo
    Creates a test story with 5 subtasks

  python jira-add-subtasks.py SCRUM-148 "Task 1" "Task 2" "Task 3"
    Adds subtasks to an existing story
"""

import base64
import json
import os
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# Load .env file from jira root (two levels up from scripts/)
def load_env():
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

load_env()

# Configuration from environment variables
JIRA_EMAIL = os.environ.get('JIRA_EMAIL')
JIRA_API_TOKEN = os.environ.get('JIRA_API_TOKEN')
JIRA_BASE_URL = os.environ.get('JIRA_BASE_URL')
PROJECT_KEY = os.environ.get('JIRA_PROJECT_KEY', 'SCRUM')

# Validate required env vars
if not all([JIRA_EMAIL, JIRA_API_TOKEN, JIRA_BASE_URL]):
    print('Error: Missing required environment variables.', file=sys.stderr)
    print('Required: JIRA_EMAIL, JIRA_API_TOKEN, JIRA_BASE_URL', file=sys.stderr)
    print('Set these in .claude/skills/jira/.env or export them manually.', file=sys.stderr)
    sys.exit(1)

# Build auth header
auth_string = f'{JIRA_EMAIL}:{JIRA_API_TOKEN}'
auth_bytes = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

HEADERS = {
    'Authorization': f'Basic {auth_bytes}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}


def make_request(method, path, data=None):
    """Make HTTP request to Jira API."""
    url = f'{JIRA_BASE_URL}/rest/api/3{path}'

    body = json.dumps(data).encode('utf-8') if data else None
    req = Request(url, data=body, headers=HEADERS, method=method)

    try:
        with urlopen(req) as response:
            status = response.status
            if status == 204:
                return None
            return json.loads(response.read().decode('utf-8'))
    except HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f'{e.code}: {error_body[:200]}')


def create_story(summary):
    """Create a Story."""
    fields = {
        'project': {'key': PROJECT_KEY},
        'issuetype': {'name': 'Story'},
        'summary': summary
    }
    return make_request('POST', '/issue', {'fields': fields})


def create_subtask(parent_key, summary):
    """Create a Subtask under a parent Story.

    NOTE: Next-Gen uses 'Subtask' (no hyphen), NOT 'Sub-task'
    """
    fields = {
        'project': {'key': PROJECT_KEY},
        'issuetype': {'name': 'Subtask'},  # Next-Gen: 'Subtask', Classic: 'Sub-task'
        'parent': {'key': parent_key},
        'summary': summary
    }
    return make_request('POST', '/issue', {'fields': fields})


def verify_issue(issue_key):
    """Verify an issue exists."""
    try:
        return make_request('GET', f'/issue/{issue_key}?fields=summary,issuetype')
    except:
        return None


def run_demo():
    """Demo mode - creates a story with subtasks."""
    print('=' * 40)
    print('  ADD SUBTASKS DEMO (PYTHON)')
    print('  (Following jira-safe skill patterns)')
    print('=' * 40 + '\n')

    # Create demo story
    print('Creating demo Story...')
    story = create_story('[Demo-Python] Test story with subtasks')
    print(f'+ Story created: {story["key"]}\n')

    # Demo subtasks
    demo_subtasks = [
        'Subtask 1: Research and planning',
        'Subtask 2: Implementation',
        'Subtask 3: Testing',
        'Subtask 4: Documentation',
        'Subtask 5: Review and merge'
    ]

    print(f'Adding {len(demo_subtasks)} subtasks to {story["key"]}...')
    created = 0
    failed = 0

    for summary in demo_subtasks:
        try:
            subtask = create_subtask(story['key'], summary)
            print(f'  + {subtask["key"]}: {summary}')
            created += 1
        except Exception as e:
            print(f'  - FAILED: {summary} ({e})')
            failed += 1
        time.sleep(0.1)  # Rate limiting

    print('\n' + '=' * 40)
    print('  SUMMARY')
    print('=' * 40)
    print(f'Story: {story["key"]}')
    print(f'Subtasks created: {created}')
    print(f'Subtasks failed: {failed}')
    print(f'\nView: {JIRA_BASE_URL}/browse/{story["key"]}')
    print('=' * 40)


def add_subtasks_to_story(story_key, subtask_summaries):
    """Add subtasks to an existing story."""
    print('=' * 40)
    print('  ADD SUBTASKS TO STORY (PYTHON)')
    print('  (Following jira-safe skill patterns)')
    print('=' * 40 + '\n')

    # Verify story exists
    print(f'Verifying {story_key}...')
    story = verify_issue(story_key)

    if not story:
        print(f'ERROR: Issue {story_key} not found or not accessible.')
        sys.exit(1)

    print(f'Found: {story["key"]} [{story["fields"]["issuetype"]["name"]}]')
    print(f'Summary: {story["fields"]["summary"]}\n')

    created = 0
    failed = 0

    print(f'Adding {len(subtask_summaries)} subtasks...')
    for summary in subtask_summaries:
        try:
            subtask = create_subtask(story_key, summary)
            print(f'  + {subtask["key"]}: {summary}')
            created += 1
        except Exception as e:
            print(f'  - FAILED: {summary} ({e})')
            failed += 1
        time.sleep(0.1)  # Rate limiting

    print('\n' + '=' * 40)
    print('  SUMMARY')
    print('=' * 40)
    print(f'Story: {story_key}')
    print(f'Subtasks created: {created}')
    print(f'Subtasks failed: {failed}')
    print(f'\nView: {JIRA_BASE_URL}/browse/{story_key}')
    print('=' * 40)


def main():
    args = sys.argv[1:]

    if not args:
        print('Usage:')
        print('  python jira-add-subtasks.py demo')
        print('    Creates a test story with 5 subtasks')
        print('')
        print('  python jira-add-subtasks.py SCRUM-148 "Task 1" "Task 2" "Task 3"')
        print('    Adds subtasks to an existing story')
        sys.exit(0)

    if args[0] == 'demo':
        run_demo()
    else:
        story_key = args[0]
        subtasks = args[1:]

        if not subtasks:
            print('ERROR: No subtask summaries provided.')
            print('Usage: python jira-add-subtasks.py SCRUM-148 "Task 1" "Task 2"')
            sys.exit(1)

        add_subtasks_to_story(story_key, subtasks)


if __name__ == '__main__':
    main()
