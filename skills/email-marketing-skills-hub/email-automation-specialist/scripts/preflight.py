#!/usr/bin/env python3
"""Offline checklist completeness check, never an authorization or compliance engine.

Input: a JSON object with checklist fields set to literal true only when verified.
No account access, network calls, contact data, sending or persistent writes.
Exit 0: supplied checklist complete; 1: outstanding items; 2: invalid input.
"""
import argparse
import json
import sys

CHECKS = (
    'audience_eligibility_verified', 'suppression_tested', 'conversion_exits_tested',
    'deduplication_tested', 'overlap_and_frequency_tested',
    'unknown_send_outcomes_resolved', 'timezone_and_delays_tested',
    'content_and_links_verified', 'unsubscribe_tested',
    'sender_setup_verified', 'backfill_and_queues_reviewed',
    'measurement_defined', 'pause_and_rollback_reviewed',
    'external_action_authorization_verified',
)

def check(data):
    if not isinstance(data, dict):
        raise ValueError('Expected a JSON object.')
    unknown = sorted(set(data) - set(CHECKS))
    if unknown:
        raise ValueError('Unknown checklist fields: ' + ', '.join(unknown))
    for key, value in data.items():
        if not isinstance(value, bool):
            raise ValueError(key + ' must be a JSON boolean.')
    missing = [key for key in CHECKS if data.get(key) is not True]
    return {
        'checklist_complete': not missing,
        'outstanding': missing,
        'notice': 'Self-reported checklist only. Not authorization, legal advice, or proof of live readiness.'
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='Local JSON checklist file')
    args = parser.parse_args()
    try:
        with open(args.input, encoding='utf-8') as file:
            result = check(json.load(file))
    except (OSError, ValueError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result['checklist_complete'] else 1

if __name__ == '__main__':
    sys.exit(main())
