#!/usr/bin/env python3
"""Verify one installable entry, vendor integrity, routed guides and presets."""
import hashlib
import json
from pathlib import Path
from hosted_assets import asset_available, records as hosted_records

PACKAGE = Path(__file__).resolve().parents[1]


def validate_package():
    entries = list(PACKAGE.rglob('SKILL.md'))
    if entries != [PACKAGE / 'SKILL.md']:
        raise ValueError('The installation must expose exactly one SKILL.md')
    records = json.loads((PACKAGE / 'dependencies/vendor-manifest.json').read_text())
    checked = 0
    for dependency in records:
        directory = PACKAGE / 'dependencies' / dependency['name']
        if not (directory / 'GUIDE.md').is_file() or not (directory / 'LICENSE').is_file():
            raise ValueError('Missing guide or license: ' + dependency['name'])
        for record in dependency['files']:
            path = directory / record['path']
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != record['sha256']:
                raise ValueError('Bundled dependency changed: ' + str(path.relative_to(PACKAGE)))
            checked += 1
    for guide in ['FILM-ART GUIDE.md', 'DIRECTOR-VISION GUIDE.md']:
        if not (PACKAGE / 'dependencies/omniailab-ai-director/references' / guide).is_file():
            raise ValueError('Missing routed director guide: ' + guide)
    for directory, collection, required_fields in [
            ('hands', 'presets', ['source']), ('voices', 'voices', ['reference_audio', 'reference_text'])]:
        catalog = json.loads((PACKAGE / 'assets' / directory / 'catalog.json').read_text())
        ids = [entry['id'] for entry in catalog[collection]]
        if len(ids) != len(set(ids)) or catalog['default'] not in ids:
            raise ValueError('Invalid catalog: ' + directory)
        for entry in catalog[collection]:
            if directory == 'voices' and entry.get('requires_import'):
                if entry.get('reference_audio') or entry.get('reference_text'):
                    raise ValueError('An import-only reference must not bundle an external recording')
                continue
            for field in required_fields:
                if not asset_available(PACKAGE / 'assets' / directory / entry[field]):
                    raise ValueError('Missing preset: ' + entry['id'])
    previews = json.loads((PACKAGE/'assets/style-previews/manifest.json').read_text())['images']
    hosted = hosted_records()
    for preview in previews:
        record = hosted['assets/style-previews/'+preview['thumbnail']]
        if record['sha256'] != preview['thumbnail_sha256'] or record['url'] != preview['url']:
            raise ValueError('Catalog preview changed: '+preview['id'])
    binaries = [p for p in (PACKAGE/'assets').rglob('*') if p.suffix.lower() in {'.png','.jpg','.jpeg','.gif','.wav'}]
    if binaries:
        raise ValueError('Public presets belong in hosted storage, not the install package')
    return {'catalog_previews_checked': len(previews), 'status': 'passed', 'skill_entries': 1, 'bundled_dependencies': len(records), 'vendor_files_checked': checked}


if __name__ == '__main__':
    print(json.dumps(validate_package(), ensure_ascii=False))
