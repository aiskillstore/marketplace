import argparse
import json
import re
import sys
from pathlib import Path

import requests

import workflow_config

JIRA = ''
IMAGE = re.compile(r'!\[[^\]]*\]\(([^)\s]+\.png)\)')
LINK = re.compile(r'(?<!!)\[([^\]]+)\]\(([^)\s]+)\)')
CODE = re.compile(r'`([^`]+)`')
BOLD = re.compile(r'\*\*([^*]+)\*\*')
SEPARATOR = re.compile(r'^\|(\s*:?-+:?\s*\|)+\s*$')


def jira_session():
    global JIRA
    config = workflow_config.load_settings()
    JIRA = workflow_config.jira_url(config)
    return workflow_config.jira_session(config)


def attachment_name(path, prefix):
    return prefix + Path(path).name


def inline(text, prefix):
    text = IMAGE.sub(lambda m: f'!{attachment_name(m.group(1), prefix)}|thumbnail!', text)
    text = LINK.sub(r'[\1|\2]', text)
    text = CODE.sub(r'{{\1}}', text)
    return BOLD.sub(r'*\1*', text)


def cells(line):
    return [cell.strip() for cell in line.strip().strip('|').split('|')]


def markdown_to_wiki(markdown, prefix):
    lines = markdown.splitlines()
    out = []
    for i, line in enumerate(lines):
        if SEPARATOR.match(line):
            continue
        heading = re.match(r'^(#{1,6})\s+(.*)$', line)
        if heading:
            out.append(f'h{len(heading.group(1))}. {inline(heading.group(2), prefix)}')
        elif line.lstrip().startswith('|'):
            is_header = i + 1 < len(lines) and SEPARATOR.match(lines[i + 1])
            joiner = '||' if is_header else '|'
            out.append(joiner + joiner.join(inline(c, prefix) for c in cells(line)) + joiner)
        elif re.match(r'^\s*[-*]\s+', line):
            out.append('* ' + inline(re.sub(r'^\s*[-*]\s+', '', line), prefix))
        else:
            out.append(inline(line, prefix))
    return '\n'.join(out) + '\n'


def referenced_images(markdown, base_dir, prefix):
    images = []
    for path in dict.fromkeys(IMAGE.findall(markdown)):
        source = (base_dir / path).resolve()
        if not source.is_relative_to(base_dir.resolve()):
            sys.exit('Screenshot must be inside the report directory')
        if not source.is_file():
            sys.exit(f'Missing screenshot: {source}')
        images.append((attachment_name(path, prefix), source))
    if len({name for name, source in images}) != len(images):
        sys.exit('Screenshots must have distinct filenames')
    return images


def main():
    parser = argparse.ArgumentParser(description='Attach acceptance screenshots, post the Markdown comment to Jira, optionally transition.')
    parser.add_argument('--issue', required=True, help='Jira key, e.g. DEMO-1')
    parser.add_argument('--comment-file', required=True, type=Path,
                        help='Markdown draft; images as ![](screenshots/<file>.png) relative to the draft')
    parser.add_argument('--prefix', help='Attachment name prefix; defaults to the issue key in lowercase without hyphen plus "-"')
    parser.add_argument('--transition', help='Transition name to apply after commenting, use an available transition name')
    parser.add_argument('--dry-run', action='store_true', help='Print the converted comment and the plan; write nothing')
    parser.add_argument('--apply', action='store_true', help='Write only after the user requests posting; preview is the default')
    args = parser.parse_args()
    if args.apply and args.dry_run:
        parser.error('--apply and --dry-run are mutually exclusive')
    if not re.fullmatch(r'[A-Z][A-Z0-9_]*-[0-9]+', args.issue):
        parser.error('Expected a Jira issue key')

    prefix = args.prefix or args.issue.lower().replace('-', '') + '-'
    if not re.fullmatch(r'[A-Za-z0-9_-]+', prefix):
        parser.error('Attachment prefix may contain only letters, digits, underscores and hyphens')
    markdown = args.comment_file.read_text(encoding='utf-8')
    images = referenced_images(markdown, args.comment_file.parent, prefix)
    comment = markdown_to_wiki(markdown, prefix)
    session = jira_session()
    issue_url = f'{JIRA}/rest/api/2/issue/{args.issue}'

    response = session.get(issue_url, params={'fields': 'status,attachment'}, timeout=30)
    response.raise_for_status()
    issue = response.json()['fields']
    existing = {a['filename'] for a in issue['attachment']}
    to_upload = [(n, s) for n, s in images if n not in existing]
    transition = None
    if args.transition:
        response = session.get(f'{issue_url}/transitions', timeout=30)
        response.raise_for_status()
        transitions = response.json()['transitions']
        transition = next((t for t in transitions if t['name'] == args.transition), None)
        if transition is None:
            sys.exit(f'Transition {args.transition!r} not available; options: {[t["name"] for t in transitions]}')

    print(json.dumps({
        'issue': args.issue,
        'status': issue['status']['name'],
        'images_referenced': len(images),
        'to_upload': [n for n, _ in to_upload],
        'already_attached': sorted(existing & {n for n, _ in images}),
        'transition': transition and f'{transition["id"]} {transition["name"]} -> {transition["to"]["name"]}',
    }, indent=1))
    if args.dry_run or not args.apply:
        print(comment)
        return

    if existing & {name for name, source in images}:
        sys.exit('Attachment names already exist. Inspect prior writes, then choose a unique run prefix; do not reuse unverified screenshots.')

    for name, source in to_upload:
        response = session.post(
            f'{issue_url}/attachments',
            headers={'X-Atlassian-Token': 'no-check'},
            files={'file': (name, source.read_bytes(), 'image/png')},
            timeout=30,
        )
        response.raise_for_status()
    posted = session.post(f'{issue_url}/comment', json={'body': comment}, timeout=30)
    posted.raise_for_status()
    comment_id = posted.json()['id']
    if transition:
        session.post(f'{issue_url}/transitions', json={'transition': {'id': transition['id']}}, timeout=30).raise_for_status()

    response = session.get(issue_url, params={'fields': 'status,attachment'}, timeout=30)
    response.raise_for_status()
    after = response.json()['fields']
    verified_comment = session.get(f'{issue_url}/comment/{comment_id}', timeout=30)
    verified_comment.raise_for_status()
    if verified_comment.json().get('body') != comment:
        sys.exit('Posted comment did not pass read-back verification; inspect before retrying')
    if transition and after['status']['name'] != transition['to']['name']:
        sys.exit('Requested transition did not pass read-back verification')
    attached = {a['filename'] for a in after['attachment']}
    missing = [n for n, _ in images if n not in attached]
    print(json.dumps({
        'comment': f'{JIRA}/browse/{args.issue}?focusedCommentId={comment_id}',
        'status': after['status']['name'],
        'missing_attachments': missing,
    }, indent=1))
    if missing:
        sys.exit(1)


if __name__ == '__main__':
    main()
