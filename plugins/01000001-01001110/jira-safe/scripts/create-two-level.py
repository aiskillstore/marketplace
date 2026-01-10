#!/usr/bin/env python3
"""
Jira Create Two-Level Hierarchy (Python)
Creates Epics with Stories and Subtasks from documentation.
Following jira-safe skill patterns for Next-Gen projects.
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


def build_adf(*sections):
    """Build Atlassian Document Format content."""
    return {'type': 'doc', 'version': 1, 'content': list(sections)}


def heading(level, text):
    """Create ADF heading."""
    return {
        'type': 'heading',
        'attrs': {'level': level},
        'content': [{'type': 'text', 'text': text}]
    }


def paragraph(text):
    """Create ADF paragraph."""
    return {
        'type': 'paragraph',
        'content': [{'type': 'text', 'text': text}]
    }


def bullet_list(items):
    """Create ADF bullet list."""
    return {
        'type': 'bulletList',
        'content': [
            {
                'type': 'listItem',
                'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': item}]}]
            }
            for item in items
        ]
    }


def create_issue(fields):
    """Create a Jira issue."""
    return make_request('POST', '/issue', {'fields': fields})


# ==================== EPIC/STORY DATA ====================

EPICS = [
    {
        'id': 'EPIC-001',
        'summary': 'EPIC-001: Database Schema - Two-Level Client/Brand Hierarchy',
        'description': build_adf(
            heading(2, 'Business Outcome'),
            paragraph('Enable multi-client management with proper data isolation and subscription-based limits.'),
            heading(2, 'Success Metrics'),
            bullet_list([
                'All brands belong to a client',
                'Client limits enforced by subscription tier',
                'Data integrity maintained across hierarchy'
            ])
        ),
        'labels': ['database', 'epic-001'],
        'stories': [
            {
                'id': 'US-001.1',
                'summary': 'US-001.1: As a developer, I want a clients table with subscription limits',
                'subtasks': [
                    'Create clients table migration',
                    'Add subscription tier columns',
                    'Add client limits (max_brands, max_users)',
                    'Create indexes for performance',
                    'Add foreign key to users table',
                    'Write migration tests',
                    'Document schema changes'
                ]
            },
            {
                'id': 'US-001.2',
                'summary': 'US-001.2: As a developer, I want brands linked to clients',
                'subtasks': [
                    'Add client_id foreign key to brands',
                    'Create migration for existing data',
                    'Update brand creation API',
                    'Add client validation on brand create',
                    'Enforce client brand limits',
                    'Update brand queries with client filter',
                    'Test data migration'
                ]
            }
        ]
    },
    {
        'id': 'EPIC-002',
        'summary': 'EPIC-002: Backend API - Client Management Endpoints',
        'description': build_adf(
            heading(2, 'Business Outcome'),
            paragraph('Provide RESTful API for client CRUD operations with proper authorization.'),
            heading(2, 'Success Metrics'),
            bullet_list([
                'Full CRUD for clients',
                'Proper authorization checks',
                'Subscription limit enforcement'
            ])
        ),
        'labels': ['backend', 'api', 'epic-002'],
        'stories': [
            {
                'id': 'US-002.1',
                'summary': 'US-002.1: As a user, I want to create a new client',
                'subtasks': [
                    'Create POST /api/clients endpoint',
                    'Add request validation with Zod',
                    'Implement subscription limit check',
                    'Add user authorization',
                    'Return created client data',
                    'Add error handling',
                    'Write API tests'
                ]
            },
            {
                'id': 'US-002.2',
                'summary': 'US-002.2: As a user, I want to list my clients',
                'subtasks': [
                    'Create GET /api/clients endpoint',
                    'Add pagination support',
                    'Filter by user ownership',
                    'Include brand counts',
                    'Add sorting options'
                ]
            }
        ]
    },
    {
        'id': 'EPIC-003',
        'summary': 'EPIC-003: Frontend UI - Client Selection Interface',
        'description': build_adf(
            heading(2, 'Business Outcome'),
            paragraph('Users can easily switch between clients and manage brands within each client.'),
            heading(2, 'Success Metrics'),
            bullet_list([
                'Client selector in header',
                'Smooth client switching',
                'Clear visual hierarchy'
            ])
        ),
        'labels': ['frontend', 'ui', 'epic-003'],
        'stories': [
            {
                'id': 'US-003.1',
                'summary': 'US-003.1: As a user, I want a client selector dropdown',
                'subtasks': [
                    'Create ClientSelector component',
                    'Fetch clients on mount',
                    'Store selected client in context',
                    'Add loading state',
                    'Add empty state',
                    'Style with Tailwind'
                ]
            },
            {
                'id': 'US-003.2',
                'summary': 'US-003.2: As a user, I want to see client details',
                'subtasks': [
                    'Create ClientDetails component',
                    'Display client name and info',
                    'Show brand count',
                    'Show subscription status',
                    'Add edit button'
                ]
            }
        ]
    }
]


def main():
    print('=' * 40)
    print('  CREATE TWO-LEVEL HIERARCHY (PYTHON)')
    print('  Following jira-safe skill patterns')
    print('=' * 40 + '\n')

    results = {
        'epics': {'created': 0, 'failed': 0},
        'stories': {'created': 0, 'failed': 0},
        'subtasks': {'created': 0, 'failed': 0}
    }

    created_issues = []

    for epic_data in EPICS:
        print(f'\n--- {epic_data["id"]} ---')

        # Create Epic
        try:
            epic_fields = {
                'project': {'key': PROJECT_KEY},
                'issuetype': {'name': 'Epic'},
                'summary': epic_data['summary'],
                'description': epic_data['description'],
                'labels': epic_data['labels']
            }

            epic = create_issue(epic_fields)
            print(f'+ Epic: {epic["key"]}')
            results['epics']['created'] += 1
            created_issues.append({'key': epic['key'], 'id': epic_data['id'], 'stories': []})

            # Create Stories under Epic
            for story_data in epic_data['stories']:
                try:
                    # Next-Gen: Use 'parent' field for Epic linking
                    story_fields = {
                        'project': {'key': PROJECT_KEY},
                        'issuetype': {'name': 'Story'},
                        'summary': story_data['summary'],
                        'parent': {'key': epic['key']},  # Next-Gen pattern
                        'labels': epic_data['labels'] + [story_data['id'].lower()]
                    }

                    story = create_issue(story_fields)
                    print(f'  + Story: {story["key"]} ({story_data["id"]})')
                    results['stories']['created'] += 1
                    created_issues[-1]['stories'].append({'key': story['key'], 'id': story_data['id']})

                    # Create Subtasks under Story
                    for subtask_summary in story_data.get('subtasks', []):
                        try:
                            # Next-Gen: Use 'Subtask' (not 'Sub-task')
                            subtask_fields = {
                                'project': {'key': PROJECT_KEY},
                                'issuetype': {'name': 'Subtask'},  # Next-Gen pattern
                                'summary': subtask_summary,
                                'parent': {'key': story['key']}
                            }

                            subtask = create_issue(subtask_fields)
                            print(f'    + Subtask: {subtask["key"]}')
                            results['subtasks']['created'] += 1

                        except Exception as e:
                            print(f'    - Subtask FAILED: {subtask_summary[:30]}... ({e})')
                            results['subtasks']['failed'] += 1

                        time.sleep(0.05)  # Rate limiting

                except Exception as e:
                    print(f'  - Story FAILED: {story_data["id"]} ({e})')
                    results['stories']['failed'] += 1

                time.sleep(0.1)  # Rate limiting

        except Exception as e:
            print(f'- Epic FAILED: {epic_data["id"]} ({e})')
            results['epics']['failed'] += 1

    # Summary
    print('\n' + '=' * 40)
    print('  SUMMARY')
    print('=' * 40)
    print(f'Epics:    {results["epics"]["created"]} created, {results["epics"]["failed"]} failed')
    print(f'Stories:  {results["stories"]["created"]} created, {results["stories"]["failed"]} failed')
    print(f'Subtasks: {results["subtasks"]["created"]} created, {results["subtasks"]["failed"]} failed')

    print('\n--- Created Issues ---')
    for epic in created_issues:
        print(f'{epic["key"]}: {epic["id"]}')
        for story in epic['stories']:
            print(f'  └─ {story["key"]}: {story["id"]}')

    print('\n' + '=' * 40)
    print(f'View: {JIRA_BASE_URL}/jira/software/projects/{PROJECT_KEY}/boards/1/backlog')
    print('=' * 40)


if __name__ == '__main__':
    main()
