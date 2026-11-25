#!/usr/bin/env python3
"""Offline helper checks. Instinct, acting on behalf of Tal Chaim Damri."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile

spec = importlib.util.spec_from_file_location('acq_helper', Path(__file__).with_name('acq.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
SECRET = 'fictional-test-secret'

with tempfile.TemporaryDirectory() as d:
    state = Path(d) / 'seat.json'
    calls = []
    def request(path, payload=None, token=None):
        calls.append((path, payload, token))
        if path == '/room':
            return {'roomId': 'AAAA-BBBB-CCCCC', 'token': SECRET}
        if '/join' in path:
            return {'token': SECRET}
        if payload is not None:
            return {'seq': 1}
        return {'messages': [{'seq': 3, 'text': 'fictional reply'}], 'ended': True}
    m.request = request
    def run(*args):
        sys.argv = ['acq.py', '--state', str(state), *args]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            m.main()
        assert SECRET not in out.getvalue()
        return out.getvalue()
    assert 'Invite' in run('open')
    assert state.stat().st_mode & 0o777 == 0o600
    assert len(calls) == 1
    try:
        run('open')
        raise AssertionError('overwrite allowed')
    except FileExistsError:
        pass
    assert len(calls) == 1
    assert json.loads(run('recv'))['ended'] is True
    assert json.loads(state.read_text())['since'] == 3
    assert 'since=3' in (run('recv') and calls[-1][0])
    assert 'since=0' in (run('recv', '--since', '0') and calls[-1][0])
    text = Path(d) / 'message.txt'
    text.write_text('Fictional answer')
    assert json.loads(run('send', '--text-file', str(text), '--end'))['endRequested']
    assert calls[-1][1]['end'] is True
    text.write_text('')
    try:
        run('send', '--text-file', str(text))
        raise AssertionError('empty send allowed')
    except ValueError:
        pass
    state.unlink()
    run('join', 'AAAA-BBBB-CCCCC')
    assert calls[-1][0].endswith('/join')
    state.chmod(0o644)
    try:
        run('recv')
        raise AssertionError('insecure state allowed')
    except ValueError:
        pass
    print('PASS offline: open/join/send/end/recv, private mode, no credential output, overwrite guard, replay cursor, empty message guard, insecure-state guard')
