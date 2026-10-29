#!/usr/bin/env python3
"""Check an installed skill in temporary storage; no footage, network or editor."""
import json
import io
from contextlib import redirect_stderr
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

from project import catalog, doctor, sha256
from timeline import build


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def run():
    skill = Path(__file__).resolve().parents[1]
    version = (skill / 'VERSION').read_text().strip()
    check(doctor('plan')['ready'], 'Python 3.9 or newer is required')
    with tempfile.TemporaryDirectory(prefix='family-travel-editor-check-') as temp:
        root = Path(temp)
        workspace = root / 'film'
        command = [sys.executable, str(skill / 'scripts/project.py'), 'init', str(workspace)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        for name in ('scene.json', 'preferences.json', 'feedback.json'):
            json.loads((workspace / name).read_text())
        check((workspace / 'STATUS.md').is_file(), 'Missing status template')
        check(subprocess.run(command, capture_output=True).returncode != 0,
              'Existing workspace was not protected')
        media = root / 'media'
        media.mkdir()
        source = media / 'fixture.mp4'
        source.write_bytes(b'Metadata-only fixture. This is not a playable video.')
        original = sha256(source)
        # This deliberate metadata-only probe must not diagnose the user's setup.
        with redirect_stderr(io.StringIO()):
            check(catalog(media, workspace / 'catalog.json', ffprobe='') == 1,
                  'Catalogue did not contain the fixture')
        plan = {'fps': 25, 'width': 640, 'height': 360,
                'shots': [{'path': 'fixture.mp4', 'in': 25, 'out': 75, 'source_frames': 100}]}
        output = workspace / 'check.xml'
        check(build(plan, media, output) == 50, 'Wrong XML duration')
        clip = ET.parse(output).find('.//clipitem')
        check(clip.findtext('in') == '25' and clip.findtext('out') == '75',
              'XML did not preserve source range')
        try:
            build(plan, media, output)
        except FileExistsError:
            pass
        else:
            raise RuntimeError('Existing output was not protected')
        check(sha256(source) == original, 'Source fixture changed')
    print(f'PASS: family-travel-editor {version} installation check')
    print('Templates, catalogue, XML ranges and overwrite refusal checked in temporary storage.')
    print('No film was rendered, watched or listened to. No editor connection was tested.')
    print('Next: give your agent a footage folder, a separate workspace and one scene to plan.')


if __name__ == '__main__':
    try:
        run()
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, ET.ParseError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        sys.exit(1)
