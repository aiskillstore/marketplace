#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2025-2026 Maksim Kochetkov
import os
import sys

if os.name != 'posix' or not all(hasattr(os, name) for name in ('O_NOFOLLOW', 'O_DIRECTORY', 'getuid')):
    print('FAILED: secure history requires POSIX Python 3 (macOS/Linux or WSL); native Windows is unsupported', file=sys.stderr)
    sys.exit(1)
import fcntl
import hashlib
import json
import re
import secrets
import shutil
import stat
import subprocess
from datetime import datetime, timezone
from urllib.parse import urlsplit, parse_qs

LIMIT = 8 * 1024 * 1024
HISTORY = 'brewpage-history.md'
RECOVERY = 'brewpage-recovery.json'
PENDING = 'brewpage-pending-create.json'
RESOLUTION = 'brewpage-reconciliation.json'
OWNER_TOKEN = re.compile(r'[A-Za-z0-9]{32}')
OWNER_ORIGIN = 'https://brewpage.app'
OWNER_PATH = re.compile(r'/api/(html|json|kv|files|sites)/([a-z0-9-]{1,32})/([A-Za-z0-9_-]{1,128})')
CONTROL_LABELS = frozenset('unlock www api admin assets static cdn status health metrics grafana prometheus monitoring autoconfig autodiscover fe-bounces account check'.split())
ROW_KIND = {'html': 'html', 'json': 'json', 'kv': 'kv', 'file': 'files', 'files': 'files', 'site': 'sites', 'sites': 'sites'}


class UnsupportedReaderHost(ValueError):
    pass


def regular(directory, name):
    try:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
    except FileNotFoundError:
        return None
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1:
        os.close(fd)
        raise ValueError('unsafe history or ignore file')
    return fd


def same_file(left, right):
    return (left.st_dev, left.st_ino) == (right.st_dev, right.st_ino)


def replace(directory, name, data, mode):
    temporary = '.brewpage-' + secrets.token_hex(12)
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode, dir_fd=directory)
    try:
        with os.fdopen(fd, 'wb') as output:
            os.fchmod(output.fileno(), mode)
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, name, src_dir_fd=directory, dst_dir_fd=directory)
    finally:
        try:
            os.unlink(temporary, dir_fd=directory)
        except FileNotFoundError:
            pass


def read(directory, name, private=False):
    fd = regular(directory, name)
    if fd is None:
        return None
    with os.fdopen(fd, 'rb') as source:
        if private and stat.S_IMODE(os.fstat(source.fileno()).st_mode) != 0o600:
            raise ValueError('history must be mode 0600')
        return source.read(LIMIT + 1)


def git(root, arguments, allowed=(0, 1)):
    environment = {'PATH': os.environ['PATH'], 'LC_ALL': 'C', 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull}
    result = subprocess.run(['git', '-C', root] + arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment)
    if result.returncode not in allowed:
        raise ValueError('Git safety check failed; repair repository configuration before publishing')
    return result


def repository(root):
    if shutil.which('git') is None:
        parent = root
        while True:
            if os.path.lexists(os.path.join(parent, '.git')):
                raise ValueError('git required to protect history in a repository')
            ancestor = os.path.dirname(parent)
            if ancestor == parent:
                return False
            parent = ancestor
    result = git(root, ['rev-parse', '--git-dir'], (0, 128))
    if result.returncode == 0:
        return True
    if result.stderr.strip() == b'fatal: not a git repository (or any of the parent directories): .git':
        return False
    raise ValueError('Git repository detection failed; repair repository configuration before publishing')


def lock(directory):
    inherited = os.environ.get('BREWPAGE_HISTORY_LOCK_FD')
    if inherited:
        fd = int(inherited)
        if not same_file(os.fstat(fd), os.fstat(directory)):
            raise ValueError('workspace changed while selecting the owner')
        fcntl.flock(fd, fcntl.LOCK_EX)
    else:
        fcntl.flock(directory, fcntl.LOCK_EX)


def state_root(workspace):
    home = os.path.expanduser('~')
    if sys.platform == 'darwin':
        base = os.path.join(home, 'Library', 'Application Support')
    else:
        base = os.environ.get('XDG_STATE_HOME') or os.path.join(home, '.local', 'state')
    if not os.path.isabs(base):
        raise ValueError('user state location must be absolute')
    os.makedirs(base, mode=0o700, exist_ok=True)
    base = os.path.realpath(base)
    parent = base
    while True:
        info = os.stat(parent)
        if info.st_uid not in (0, os.getuid()) or (info.st_mode & 0o022 and not (info.st_uid == 0 and info.st_mode & stat.S_ISVTX)):
            raise ValueError('user state directory has an unsafe ancestor')
        ancestor = os.path.dirname(parent)
        if ancestor == parent:
            break
        parent = ancestor
    if repository(base):
        raise ValueError('user state cannot be in a Git repository')
    work_id = hashlib.sha256(os.fsencode(os.path.realpath(workspace))).hexdigest()
    directory = os.open(base, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for name in ('brewpage-publish-safe', work_id):
            try:
                os.mkdir(name, 0o700, dir_fd=directory)
            except FileExistsError:
                pass
            child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = child
            info = os.fstat(directory)
            if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
                raise ValueError('BrewPage user state needs owner-only directories')
    finally:
        os.close(directory)
    destination = os.path.join(base, 'brewpage-publish-safe', work_id)
    if repository(destination):
        raise ValueError('BrewPage user state cannot be in a Git repository')
    return destination


def owner_api(value):
    if not isinstance(value, str) or not value.startswith(OWNER_ORIGIN + '/'):
        return None
    return OWNER_PATH.fullmatch(value[len(OWNER_ORIGIN):])


def reader_url(value, target):
    if target is None or not isinstance(value, str) or not re.fullmatch(r'https://[A-Za-z0-9.-]+(?:[/?][^\s\x00-\x20\x7f#|`\[\]]*)?', value):
        raise ValueError('receipt needs an official target and valid reader URL')
    parsed = urlsplit(value)
    hostname = parsed.hostname.rstrip('.').lower()
    namespace, item = target[2], target[3]
    if hostname == 'brewpage.app':
        expected = f'/{namespace}/{item}'
    else:
        prefix = '' if namespace == 'public' else ('n' if namespace.startswith('-') else '') + namespace + '-'
        if hostname.split('.', 1)[0] in CONTROL_LABELS or not re.fullmatch(re.escape(prefix) + r'[a-z0-9]{10}\.brewpage\.app', hostname):
            raise UnsupportedReaderHost('reader URL needs a supported BrewPage publication host')
        expected = '/'
    if parsed.path != expected or parsed.query:
        raise ValueError('reader URL conflicts with the publication identity')
    return value


def rows(data):
    for line in data.decode('utf-8').splitlines():
        parts = [value.strip() for value in line.split('|')[1:-1]]
        if len(parts) != 7:
            continue
        reader = re.fullmatch(r'\[(https://[^\]\s]+)\]\(\1\)', parts[1])
        if reader is None:
            continue
        api = parts[5]
        target = owner_api(api)
        if target is None:
            continue
        try:
            link = reader_url(reader[1], target)
        except UnsupportedReaderHost:
            continue
        cells = json.loads(parts[6].strip('`')) if parts[6].strip('`') else {}
        validate_identity(cells, target)
        token = parts[2].strip('`')
        if token:
            yield link, api, token


def select(data, intent, target, out):
    if intent == 'anonymous':
        return
    candidates = [(api, token) for link, api, token in rows(data) if not target or target in (link, api)]
    tokens = {token for _, token in candidates}
    if len(tokens) > 1 or (target and not tokens):
        raise ValueError('choose the exact saved publication')
    if not tokens:
        return
    token, = tokens
    if not OWNER_TOKEN.fullmatch(token):
        raise ValueError('stored owner proof is invalid')
    if intent == 'update' or target:
        endpoints = {api for api, _ in candidates}
        if len(endpoints) != 1:
            raise ValueError('update target is ambiguous')
        print(next(iter(endpoints)))
    write_owner_header(out, token)


def write_owner_header(out, token):
    fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w', encoding='ascii') as header:
        header.write('X-Owner-Token: ' + token + '\n')


def validate_identity(identity, target):
    if not isinstance(identity, dict):
        raise ValueError('owner receipt needs typed publication identity')
    kind, ns, item = target.groups()
    for alias, expected in (('id', item), ('namespace', ns), ('ns', ns), ('kind', kind), ('type', kind)):
        if alias not in identity or identity[alias] is None and alias in ('id', 'namespace', 'type'):
            continue
        value = identity[alias]
        actual = ROW_KIND.get(value) if alias in ('kind', 'type') and isinstance(value, str) else value
        if not isinstance(value, str) or actual != expected:
            raise ValueError('owner receipt has a conflicting publication identity alias')


def validate_receipt(receipt, target):
    validate_identity(receipt, target)
    locations = [receipt]
    result = receipt.get('result')
    if isinstance(result, dict):
        locations.append(result)
        if isinstance(result.get('extras'), dict):
            locations.append(result['extras'])
    for location in locations:
        if 'isOwner' in location and location['isOwner'] is not True:
            raise ValueError('owner receipt has false or invalid ownership confirmation')


def owner_row(target, reader, token, identity):
    api = owner_api(target)
    reader_url(reader, api)
    kind, ns, item = api.groups()
    if not isinstance(token, str) or not OWNER_TOKEN.fullmatch(token):
        raise ValueError('owner receipt has invalid proof or conflicting target identity')
    validate_identity(identity, api)
    identity = {**identity, 'id': item, 'namespace': ns}
    identity = json.dumps(identity, separators=(',', ':'))
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')
    return f'| {now} | [{reader}]({reader}) | `{token}` | — | {kind} | {target} | `{identity}` |\n'.encode()


def receipt_row(data):
    if not data or len(data) > 1024 * 1024:
        raise ValueError('invalid recovery receipt size')
    receipt = json.loads(data)
    api = owner_api(receipt.get('ownerApi')) if isinstance(receipt, dict) else None
    if api is None or receipt.get('origin') != OWNER_ORIGIN:
        raise ValueError('invalid recovery receipt origin')
    validate_receipt(receipt, api)
    identity = receipt.get('identity')
    validate_identity(identity, api)
    reader = receipt.get('readerUrl')
    token = receipt.get('ownerToken')
    if not isinstance(token, str) or not OWNER_TOKEN.fullmatch(token) or not isinstance(reader, str) or token in reader or reader == receipt.get('manageUrl'):
        raise ValueError('invalid recovery receipt proof')
    if receipt.get('manageUrl'):
        identity = {**identity, 'manageUrl': receipt['manageUrl']}
    row = owner_row(receipt['ownerApi'], reader, token, identity)
    if len(list(rows(row))) != 1:
        raise ValueError('receipt could not be retained')
    return receipt, api, row


def request_binding(value):
    if not isinstance(value, dict) or value.get('method') != 'POST' or value.get('kind') not in ROW_KIND.values() or not isinstance(value.get('endpoint'), str):
        raise ValueError('resolution requires the exact create request binding')
    endpoint = urlsplit(value.get('endpoint', ''))
    if endpoint.scheme != 'https' or endpoint.netloc != 'brewpage.app' or endpoint.fragment or endpoint.path != '/api/' + value['kind'] or parse_qs(endpoint.query).get('ns') != [value.get('namespace')]:
        raise ValueError('request kind, namespace and official endpoint must agree')
    if not isinstance(value.get('namespace'), str) or not isinstance(value.get('payloadSha256'), str) or not re.fullmatch(r'[a-z0-9-]{1,32}', value['namespace']) or not re.fullmatch(r'[a-f0-9]{64}', value['payloadSha256']):
        raise ValueError('request needs a namespace and exact payload fingerprint')
    return value


def request_digest(request):
    return hashlib.sha256(json.dumps(request, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def pending_record(data):
    value = json.loads(data)
    if not isinstance(value, dict) or not re.fullmatch(r'[a-f0-9]{24}', value.get('operationId', '')):
        raise ValueError('invalid pending create')
    request_binding(value.get('request'))
    proof = value.get('ownerProofSha256')
    if proof is not None and not re.fullmatch(r'[a-f0-9]{64}', proof):
        raise ValueError('invalid pending authority')
    return value


def check_create(pending, operation, target, token):
    if not pending or pending['operationId'] != operation or target is None:
        raise ValueError('receipt does not match a pending create')
    request = pending['request']
    if target[2] != request['namespace'] or target[1] != request['kind'] and (request['kind'], target[1]) != ('files', 'html'):
        raise ValueError('receipt does not match requested publication type')
    authority = pending.get('ownerProofSha256')
    if authority and hashlib.sha256(token.encode()).hexdigest() != authority:
        raise ValueError('receipt conflicts with pending authority')


def bound_receipt(data, pending):
    receipt, target, row = receipt_row(data)
    check_create(pending, receipt.get('operationId'), target, receipt['ownerToken'])
    return row


def reconcile_input(data, pending):
    if not pending or not data or len(data) > 1024 * 1024:
        raise ValueError('verified reconciliation requires a pending create')
    value = json.loads(data)
    if not isinstance(value, dict) or value.get('schema') != 'brewpage-safe-reconciliation-v1':
        raise ValueError('invalid reconciliation')
    if value.get('operationId') != pending['operationId'] or value.get('requestSha256') != request_digest(pending['request']):
        raise ValueError('reconciliation does not match the pending request')
    evidence = value.get('evidence')
    if (not isinstance(evidence, dict) or evidence.get('source') != 'owner-verified-first-party' or
        evidence.get('verifiedByOperator') is not True or not isinstance(evidence.get('reference'), str) or not 1 <= len(evidence['reference'].strip()) <= 1000):
        raise ValueError('first-party outcome must be externally verified')
    outcome = value.get('outcome')
    if outcome == 'no-write' and value.get('receipt') is None:
        row = b''
    elif outcome == 'publication-owned':
        receipt = json.dumps(value.get('receipt'), separators=(',', ':')).encode()
        row = bound_receipt(receipt, pending)
    else:
        raise ValueError('invalid reconciliation outcome')
    audit = {'operationId': pending['operationId'], 'requestSha256': value['requestSha256'], 'outcome': outcome,
             'verification': 'owner-verified-first-party', 'resolutionSha256': hashlib.sha256(data).hexdigest()}
    return b'<!-- brewpage-reconciliation:' + json.dumps(audit, separators=(',', ':')).encode() + b' -->\n' + row


def write_checked(directory, root, name, data):
    replace(directory, name, data, 0o600)
    if not same_file(os.stat(root, follow_symlinks=False), os.fstat(directory)) or read(directory, name, private=True) != data:
        raise ValueError('storage readback failed')


def main():
    mode, *args = sys.argv[1:]
    if mode == 'state-root':
        print(state_root(*args))
        return
    if mode == 'reader-check':
        receipt = json.load(sys.stdin)
        print(reader_url(receipt['link'], owner_api(receipt['ownerApi'])))
        return
    root, *args = args
    directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        info = os.fstat(directory)
        if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
            raise ValueError('owner storage directory must be private')
        lock(directory)
        if mode == 'lock':
            return

        recovery = read(directory, RECOVERY, private=True) or b''
        pending_bytes = read(directory, PENDING, private=True)
        pending = pending_record(pending_bytes) if pending_bytes is not None else None
        operation = os.environ.get('BREWPAGE_OPERATION_ID', '')
        if mode == 'recover-target':
            receipt, target, _ = receipt_row(recovery)
            check_create(pending, receipt.get('operationId'), target, receipt['ownerToken'])
            write_owner_header(args[0], receipt['ownerToken'])
            print(json.dumps({'reader': receipt['readerUrl'], 'ownerApi': receipt['ownerApi']}, separators=(',', ':')))
            return
        if mode == 'pending-list':
            state = []
            if pending:
                if recovery:
                    bound_receipt(recovery, pending)
                state.append({'operationId': pending['operationId'], 'requestSha256': request_digest(pending['request']), 'receiptAvailable': bool(recovery)})
            print(json.dumps({'workspaceSlot': os.path.basename(root), 'pending': state}, separators=(',', ':')))
            return
        if mode == 'receipt-ready':
            if recovery:
                raise ValueError('recovery must precede more writes')
            write_checked(directory, root, RECOVERY, b'')
            return
        if mode == 'pending':
            if pending:
                raise ValueError('resolve the previous create before creating again')
            incoming = sys.stdin.buffer.read(1024 * 1024 + 1)
            if len(incoming) > 1024 * 1024 or pending_record(incoming)['operationId'] != operation:
                raise ValueError('invalid pending request')
            write_checked(directory, root, PENDING, incoming)
            return
        if mode == 'receipt':
            if recovery:
                raise ValueError('recovery already contains proof')
            incoming = sys.stdin.buffer.read(1024 * 1024 + 1)
            bound_receipt(incoming, pending)
            write_checked(directory, root, RECOVERY, incoming)
            return
        if mode == 'clear':
            if not pending or pending['operationId'] != operation:
                raise ValueError('refusal does not match the pending create')
            os.unlink(PENDING, dir_fd=directory)
            return

        data = read(directory, HISTORY, private=True) or b''
        if len(data) > LIMIT:
            raise ValueError('owner history exceeds local limit')
        if data and not data.endswith(b'\n'):
            data += b'\n'
        if mode == 'select':
            intent, target, _ = args
            if pending and intent != 'update':
                raise ValueError('resolve the previous create before creating again')
            select(data, *args)
            return
        if mode == 'init':
            write_checked(directory, root, HISTORY, data or sys.stdin.buffer.read(65536))
            return

        if mode == 'recover':
            incoming = bound_receipt(recovery, pending)
        elif mode == 'reconcile':
            if recovery:
                raise ValueError('use the existing local receipt')
            incoming = reconcile_input(read(directory, RESOLUTION, private=True), pending)
        elif mode == 'append':
            incoming = sys.stdin.buffer.read(1024 * 1024 + 1)
            retained = list(rows(incoming))
            if len(incoming) > 1024 * 1024 or len(retained) != 1 or not OWNER_TOKEN.fullmatch(retained[0][2]):
                raise ValueError('publication does not carry valid proof')
            if args == ['POST']:
                _, api, token = retained[0]
                check_create(pending, operation, owner_api(api), token)
            elif args != ['PUT']:
                raise ValueError('invalid history write method')
        else:
            raise ValueError('invalid owner storage operation')

        if incoming:
            if len(data) + len(incoming) > LIMIT:
                raise ValueError('owner history exceeds local limit')
            write_checked(directory, root, HISTORY, data + incoming)
        if mode == 'recover':
            os.unlink(RECOVERY, dir_fd=directory)
        if mode in ('recover', 'reconcile') or args == ['POST']:
            os.unlink(PENDING, dir_fd=directory)
        if mode == 'reconcile':
            os.unlink(RESOLUTION, dir_fd=directory)
    finally:
        os.close(directory)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, TypeError):
        print('FAILED: protected owner storage unavailable or invalid; check recovery before retrying', file=sys.stderr)
        sys.exit(1)
