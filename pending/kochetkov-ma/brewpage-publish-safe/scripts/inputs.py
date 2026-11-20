#!/usr/bin/env python3
import io
import os
import re
import stat
import sys
import zipfile
from pathlib import PurePosixPath

MIB = 1024 * 1024
ARCHIVE_SUFFIXES = {'.zip', '.tar', '.gz', '.tgz', '.bz2', '.tbz', '.tbz2', '.xz', '.txz', '.7z', '.rar', '.zst', '.z', '.jar', '.war', '.apk', '.iso'}
ARCHIVE_SIGNATURES = (b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08', b'\x1f\x8b', b'\x1f\x9d', b'BZh',
                      b'\xfd7zXZ\0', b'7z\xbc\xaf\x27\x1c', b'Rar!\x1a\x07', b'\x28\xb5\x2f\xfd')
OFFICE_SUFFIXES = {'.docx', '.docm', '.xlsx', '.xlsm', '.pptx', '.pptm', '.odt', '.ods', '.odp'}
CREDENTIAL = re.compile(rb'-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----|\b(?:AKIA|ASIA)[A-Z0-9]{16}\b|\b(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]{20,}\b|'
                        rb'\b(?:Authorization\s*:\s*Bearer|X-Owner-Token\s*:)\s+[A-Za-z0-9._~+/-]{12,}|'
                        rb'''["'](?:owner[_-]?token|access[_-]?token|client[_-]?secret|api[_-]?key)["']\s*[:=]\s*["'][A-Za-z0-9._~+/-]{12,}|'''
                        rb'https://[A-Za-z0-9.-]+/manage/[^\s"\']+#k=[A-Za-z0-9_-]{12,}', re.IGNORECASE)


def checked_open(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    return os.fdopen(fd, 'rb')


def password(source, destination):
    if not os.path.isabs(source):
        raise ValueError('password source must be absolute')
    with checked_open(source) as handle:
        info = os.fstat(handle.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1 or info.st_mode & 0o077:
            raise ValueError('password source must be owner-only')
        raw = handle.read(4097)
        after = os.fstat(handle.fileno())
        if (after.st_ctime_ns, after.st_mtime_ns, after.st_size) != (info.st_ctime_ns, info.st_mtime_ns, info.st_size):
            raise ValueError('password source changed during review')
    value = (raw[:-1] if raw.endswith(b'\n') else raw).decode('utf-8')
    if len(raw) > 4096 or len(value) < 4 or any(ord(char) < 32 or 127 <= ord(char) <= 159 for char in value):
        raise ValueError('password is not valid')
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as header:
        header.write(b'X-Password: ' + value.encode('utf-8') + b'\n')
    print(f'{info.st_dev}/{info.st_ino}')


def read_limit(handle, limit):
    value = handle.read(limit + 1)
    if len(value) > limit:
        raise ValueError('input exceeds local review limit')
    return value


def check_secrets(value, selected_password):
    if value.startswith((b'\xff\xfe', b'\xfe\xff')):
        value = value.decode('utf-16').encode('utf-8')
    if CREDENTIAL.search(value) or (selected_password and selected_password in value):
        raise ValueError('credential-like material in selected input')


def opaque(value, name):
    return value.startswith(ARCHIVE_SIGNATURES) or value[257:262] == b'ustar' or PurePosixPath(name).suffix.lower() in ARCHIVE_SUFFIXES


def checked_member(archive, member, selected_password):
    check_secrets(member.filename.encode('utf-8'), selected_password)
    if member.is_dir():
        return
    if member.flag_bits & 1 or member.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
        raise ValueError('archive member cannot be inspected')
    with archive.open(member) as handle:
        value = read_limit(handle, 5 * MIB)
    if opaque(value, member.filename):
        raise ValueError('nested opaque archive needs separate review')
    check_secrets(value, selected_password)


def scan_archive(archive, selected_password):
    members = archive.infolist()
    if len(members) > 400 or sum(member.file_size for member in members) > 40 * MIB:
        raise ValueError('archive exceeds local review limits')
    for member in members:
        checked_member(archive, member, selected_password)


def scan(path, kind, header):
    selected_password = None
    if header:
        with checked_open(header) as handle:
            selected_password = read_limit(handle, 4200)[len(b'X-Password: '):-1]
    if kind == 'site':
        with checked_open(path) as handle, zipfile.ZipFile(handle) as archive:
            scan_archive(archive, selected_password)
        return
    if path == '-':
        value = read_limit(sys.stdin.buffer, 25 * MIB)
    else:
        with checked_open(path) as handle:
            value = read_limit(handle, 25 * MIB)
        check_secrets(os.path.basename(path).encode('utf-8'), selected_password)
    if PurePosixPath(path).suffix.lower() in OFFICE_SUFFIXES and value.startswith(b'PK\x03\x04'):
        with zipfile.ZipFile(io.BytesIO(value)) as archive:
            scan_archive(archive, selected_password)
    elif opaque(value, path):
        raise ValueError('opaque archive requires separate site review')
    else:
        check_secrets(value, selected_password)


if __name__ == '__main__':
    try:
        operation, *args = sys.argv[1:]
        if operation == 'password':
            password(*args)
        elif operation == 'scan':
            scan(*args)
        else:
            raise ValueError('unknown input operation')
    except (OSError, ValueError, TypeError, RuntimeError, zipfile.BadZipFile):
        print('FAILED: input could not be reviewed safely; inspect the selected content, archive, or password source', file=sys.stderr)
        sys.exit(1)
