#!/usr/bin/env python3
"""Explicit, bounded, tool-free synthetic grading via the OpenAI Responses API."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request

from build_fixtures import build_suite, digest
from check_results import summarize

ENDPOINT = 'https://api.openai.com/v1/responses'
MAX_RESPONSE_BYTES = 4 * 1024 * 1024


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def open_request(request, timeout):
    # No environment proxy, credential-file handler, cookies, redirects or retries.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    return opener.open(request, timeout=timeout)


def validate_suite(suite):
    # Accept only this checkout's fixed synthetic fixtures and documented reading set.
    # Custom prompts, changed candidate files, labels and artifacts require a new freeze.
    if digest(suite) != digest(build_suite()):
        raise ValueError('Suite differs from current fixed synthetic fixture build; freeze again before running.')


def run_case(case, model, max_output_tokens, timeout, api_key, opener=None, evidence_kind=None):
    if case.get('kind') != 'grading':
        raise ValueError('API controller supports tool-free grading only.')
    if not model or not isinstance(max_output_tokens, int) or max_output_tokens <= 0 or not 0 < timeout <= 60:
        raise ValueError('Explicit model, positive output cap and timeout up to 60 seconds required.')
    live_transport = opener is None
    opener = open_request if opener is None else opener
    evidence_kind = 'live API transport' if live_transport else (evidence_kind or 'injected test transport')
    payload = dict(model=model, input=case['prompt'], tools=[], tool_choice='none',
                   store=False, max_output_tokens=max_output_tokens)
    record = {k: case[k] for k in ('artifact_hash', 'candidate_hash', 'prompt', 'rubric_version', 'assessment_profile')}
    record.update(case_id=case['id'], model=model, model_version='Not available', duration_seconds=0,
                  token_usage=None, tool_trace=[], final_output='', transport_violations=[], status='Not Assessed',
                  evidence_kind=evidence_kind, request_hash=digest(payload),
                  isolation={'status': 'Verified' if live_transport else 'Not Assessed',
                    'evidence': 'Request exposes tools=[] and tool_choice=none; no local model process or fixture execution.' if live_transport else 'Injected local test transport is not measured model evidence.'})
    if not api_key:
        record['reason'] = 'OPENAI_API_KEY unavailable in environment; no request sent.'
        return record
    request = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode(),
        headers={'Authorization': 'Bearer ' + api_key, 'Content-Type': 'application/json'}, method='POST')
    started = time.monotonic()
    try:
        with opener(request, timeout=timeout) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise ValueError('response size limit')
        record['response_sha256'] = hashlib.sha256(raw).hexdigest()
        data = json.loads(raw)
        if not isinstance(data, dict): raise ValueError('response object required')
        record['transport_status'] = data.get('status', 'unknown')
        record['response_id'] = data.get('id')
        record['model_version'] = data.get('model') or 'Not available'
        record['token_usage'] = data.get('usage')
        output = data.get('output', [])
        if not isinstance(output, list) or any(not isinstance(x, dict) for x in output):
            raise ValueError('invalid output shape')
        unexpected = [x.get('type') for x in output if x.get('type') not in ('message', 'reasoning')]
        if unexpected:
            record['transport_violations'] = ['unexpected output item; tools forbidden']
            raise ValueError('unexpected output item')
        texts = []
        for item in output:
            if item.get('type') == 'message':
                content = item.get('content', [])
                if not isinstance(content, list): raise ValueError('invalid message content')
                for part in content:
                    if not isinstance(part, dict): raise ValueError('invalid content item')
                    if part.get('type') == 'output_text' and isinstance(part.get('text'), str):
                        texts.append(part['text'])
        record['final_output'] = ''.join(texts)
        if data.get('status') != 'completed' or data.get('error') or not texts:
            record['reason'] = 'API response incomplete, failed, refused, or missing output text.'
        elif not live_transport:
            record['reason'] = 'Synthetic transport test only; no measured model session.'
        else:
            record['status'] = 'Observed'
    except urllib.error.HTTPError as exc:
        record['reason'] = 'API HTTP error %s; no successful measured session.' % exc.code
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, TypeError):
        # Never echo remote bodies, request headers, credentials or exception text.
        record['reason'] = 'API transport unavailable, timed out, or malformed response; no successful measured session.'
    finally:
        record['duration_seconds'] = round(time.monotonic() - started, 6)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', type=Path, required=True)
    parser.add_argument('--results', type=Path, required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--max-requests', type=int, required=True)
    parser.add_argument('--max-output-tokens', type=int, required=True)
    parser.add_argument('--timeout-seconds', type=float, default=60,
                        help='Socket inactivity timeout (maximum 60s), not a total request deadline.')
    args = parser.parse_args()
    if not 1 <= args.max_requests <= 24 or args.max_output_tokens <= 0 or not 0 < args.timeout_seconds <= 60:
        parser.error('Use 1..24 requests, a positive output cap, and timeout 0..60 seconds.')
    suite = json.loads(args.suite.read_text(encoding='utf-8'))
    validate_suite(suite)
    # Pair current/control before moving to another anchor; alternate order by repeat.
    cases = sorted(suite['grading'], key=lambda c: (c['repeat'], c['anchor'],
                   (0 if c['condition'] == 'with-skill' else 1) if c['repeat'] % 2 else
                   (1 if c['condition'] == 'with-skill' else 0)))
    key = os.environ.get('OPENAI_API_KEY')
    records = []
    # Exclusive output prevents accidental resume/replay or overriding prior evidence.
    with args.results.open('x', encoding='utf-8') as stream:
        for case in cases[:args.max_requests]:
            record = run_case(case, args.model, args.max_output_tokens, args.timeout_seconds, key)
            records.append(record)
            stream.write(json.dumps(record, sort_keys=True) + '\n')
            stream.flush()
            report = summarize(suite, records)
            if report['stop_required'] or record['status'] == 'Not Assessed':
                break
    report = summarize(suite, records)
    complete = len(records) == len(suite['grading']) and all(r['status'] == 'Observed' for r in records)
    assessment = ('Fail' if report['stop_required'] or report['candidate_grading_outcome'] == 'Fail'
                  else 'Pass' if complete and report['candidate_grading_outcome'] == 'Pass' else 'Not Assessed')
    report['api_grading_assessment'] = assessment
    report['api_collection_complete'] = complete
    print(json.dumps(report, indent=2))
    return {'Pass': 0, 'Fail': 1, 'Not Assessed': 2}[assessment]


if __name__ == '__main__':
    raise SystemExit(main())
