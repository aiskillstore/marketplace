"""Resolve versioned public presets into a verified cache outside the installation."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

PACKAGE = Path(__file__).resolve().parents[1]


def records():
    data = json.loads((PACKAGE / 'assets/hosted-manifest.json').read_text())['files']
    for key, record in data.items():
        path, url = PurePosixPath(key), urlsplit(record['url'])
        if path.is_absolute() or '..' in path.parts or str(path) != key or '\\' in key:
            raise ValueError('Invalid hosted asset path')
        if url.scheme != 'https' or not url.hostname or url.username or url.password:
            raise ValueError('Hosted assets require public HTTPS URLs')
        if type(record['bytes']) is not int or record['bytes'] <= 0 or not re.fullmatch('[a-f0-9]{64}', record['sha256']):
            raise ValueError('Hosted assets require size and SHA-256')
    return data


def checked(content, record):
    return len(content) == record['bytes'] and hashlib.sha256(content).hexdigest() == record['sha256']


def cache_path(key, record):
    base = Path(os.environ.get('HANDDRAW_ASSET_CACHE', str(Path.home() / '.cache/sweety-handdraw-video'))).expanduser()
    return base / record['sha256'] / Path(key).name


def asset_available(path):
    path = Path(path)
    if path.is_file():
        return True
    try:
        return path.relative_to(PACKAGE).as_posix() in records()
    except ValueError:
        return False


def resolve_asset(path):
    path = Path(path)
    try:
        key = path.relative_to(PACKAGE).as_posix()
    except ValueError:
        if not path.is_file():
            raise FileNotFoundError(path)
        return path
    record = records().get(key)
    if record is None:
        if not path.is_file():
            raise FileNotFoundError(path)
        return path
    target = cache_path(key, record)
    for candidate in (path, target):
        if candidate.is_file() and checked(candidate.read_bytes(), record):
            return candidate
    if os.environ.get('HANDDRAW_OFFLINE') == '1':
        raise ValueError('Offline asset cache missing or damaged: ' + key)
    request = Request(record['url'], headers={'User-Agent': 'sweety-handdraw-video'})
    with urlopen(request, timeout=60) as response:
        content = response.read(record['bytes'] + 1)
    if not checked(content, record):
        raise ValueError('Downloaded asset failed size/SHA-256 validation: ' + key)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(content)
    try:
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    return target


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('keys', nargs='*')
    parser.add_argument('--all', action='store_true')
    arguments = parser.parse_args()
    keys = list(records()) if arguments.all else arguments.keys
    if not keys:
        parser.error('Provide asset keys or --all')
    for key in keys:
        if key not in records():
            parser.error('Unknown asset: ' + key)
        print(resolve_asset(PACKAGE / key))
