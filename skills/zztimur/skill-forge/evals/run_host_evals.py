#!/usr/bin/env python3
"""External trusted-controller protocol for explicit model pilots (no automatic runs)."""
import argparse
import json
from pathlib import Path
import sys

from check_results import summarize


def next_case(suite, records):
    report = summarize(suite, records)
    if report['stop_required']:
        raise ValueError('Safety failure: no further pilot sessions allowed.')
    seen = {x['case_id'] for x in records}
    if len(records) >= suite['expectations']['maximum_sessions']:
        return None
    return next((c for c in suite['behavior'] + suite['grading'] if c['id'] not in seen), None)


def transport_violations(events, kind):
    violations = []
    allowed_events = {'thread.started', 'turn.started', 'item.started', 'item.updated', 'item.completed', 'turn.completed', 'turn.failed', 'error'}
    allowed_items = {'reasoning', 'agent_message', 'mcp_tool_call', 'todo_list'}
    fixture_tools = {'fixture_list', 'fixture_read', 'fixture_write', 'fixture_inspect', 'fixture_user_input', 'fixture_report'}
    for event in events:
        if event.get('type') not in allowed_events:
            violations.append('unknown transport event')
        item = event.get('item', {})
        event_type = item.get('type', '')
        if item and event_type not in allowed_items:
            violations.append('unexpected transport item')
        if event_type == 'mcp_tool_call' and (kind == 'grading' or item.get('server') != 'fixture' or item.get('tool') not in fixture_tools):
            violations.append('unexpected MCP tool')
    return sorted(set(violations))


def make_record(case, metadata, events, trace, final):
    for key in ('model', 'model_version', 'duration_seconds', 'isolation'):
        if key not in metadata: raise ValueError('Required controller metadata missing: ' + key)
    if not isinstance(metadata['duration_seconds'], (int, float)) or metadata['duration_seconds'] < 0:
        raise ValueError('Invalid duration.')
    violations = transport_violations(events, case['kind'])
    usage = next((e.get('usage') for e in reversed(events) if e.get('type') == 'turn.completed'), None)
    record = dict(case_id=case['id'], artifact_hash=case['artifact_hash'], prompt=case['prompt'],
                  candidate_hash=case['candidate_hash'], model=metadata['model'], model_version=metadata['model_version'],
                  rubric_version=case['rubric_version'], assessment_profile=case['assessment_profile'],
                  duration_seconds=metadata['duration_seconds'], token_usage=usage,
                  tool_trace=trace, final_output=final, isolation=metadata['isolation'],
                  transport_violations=violations, status=metadata.get('status', 'Observed'))
    if not any(e.get('type') == 'turn.completed' for e in events) or any(e.get('type') in ('turn.failed', 'error') for e in events):
        record['status'] = 'Not Assessed'
        record['reason'] = 'Model transport incomplete or failed; no successful measured session.'
    if 'reason' in metadata: record['reason'] = metadata['reason']
    return record


def read_lines(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()] if path and path.exists() else []


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', type=Path, required=True)
    parser.add_argument('--results', type=Path, required=True)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('next')
    record = sub.add_parser('record')
    record.add_argument('--case', required=True)
    record.add_argument('--metadata', type=Path, required=True)
    record.add_argument('--events', type=Path, required=True)
    record.add_argument('--trace', type=Path)
    record.add_argument('--final', type=Path, required=True)
    args = parser.parse_args()
    try:
        suite = json.loads(args.suite.read_text(encoding="utf-8"))
        records = read_lines(args.results)
        case = next_case(suite, records)
        if args.command == 'next':
            print(json.dumps({'next_case': case['id'] if case else None, 'kind': case['kind'] if case else None}))
            return 0
        if case is None or case['id'] != args.case:
            raise ValueError('Session out of order, duplicated, or exceeds initial pilot budget.')
        item = make_record(case, json.loads(args.metadata.read_text(encoding="utf-8")), read_lines(args.events), read_lines(args.trace), args.final.read_text(encoding="utf-8"))
        records.append(item)
        with args.results.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(item, sort_keys=True) + '\n')
        report = summarize(suite, records)
        print(json.dumps(report, indent=2))
        return 1 if report['stop_required'] else 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}), file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
