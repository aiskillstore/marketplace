#!/usr/bin/env python3
"""Run bundled image privacy cleanup, remove synthetic camera tags, then audit."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

PACKAGE = Path(__file__).resolve().parents[1]


def clean_image(source, audit_path):
    source = Path(source).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    for command in ('bun', 'exiftool'):
        if not shutil.which(command):
            raise ValueError(f'{command} is required for the bundled image privacy workflow')
    upstream = PACKAGE / 'dependencies/sweety-image-privacy/scripts/main.ts'
    subprocess.run(['bun', str(upstream), str(source), '--json'], check=True, capture_output=True, text=True)
    subprocess.run(['exiftool', '-overwrite_original', '-all=', str(source)], check=True, capture_output=True)
    metadata = json.loads(subprocess.check_output([
        'exiftool', '-j', '-EXIF:all', '-GPS:all', '-XMP:all', '-IPTC:all', '-Comment', '-Software', str(source)]))[0]
    metadata.pop('SourceFile', None)
    if metadata:
        raise ValueError('Embedded privacy metadata remains after cleanup: ' + ', '.join(metadata))
    attributes = []
    if shutil.which('xattr'):
        attributes = subprocess.check_output(['xattr', str(source)], text=True).splitlines()
    report = {'file': source.name, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'embedded_metadata_empty': True, 'xattrs_remaining': attributes,
              'camera_profile_removed': True,
              'note': 'System-managed provenance attributes can remain; this is not an AI detector guarantee.'}
    audit_path = Path(audit_path)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--audit', type=Path, required=True)
    arguments = parser.parse_args()
    print(json.dumps(clean_image(arguments.image, arguments.audit), ensure_ascii=False))
