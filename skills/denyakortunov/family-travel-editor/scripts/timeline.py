#!/usr/bin/env python3
"""Export an explicit, same-rate, video-only shot plan as FCP 7 XML."""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def child(parent, name, text=None, **attrs):
    node = ET.SubElement(parent, name, attrs)
    if text is not None:
        node.text = str(text)
    return node


def validate(plan, media_root):
    if not isinstance(plan, dict):
        raise ValueError('Shot plan must be a JSON object')
    missing = [key for key in ('fps', 'width', 'height', 'shots') if key not in plan]
    if missing:
        raise ValueError('Missing shot-plan fields: ' + ', '.join(missing) +
                         '. scene.json is a narrative plan; derive shot-plan-v1.json using references/plan-formats.md.')
    fps = plan.get('fps')
    if type(fps) is not int or fps not in (24, 25, 30):
        raise ValueError('This helper supports integer 24, 25 or 30 fps only')
    for key in ('width', 'height'):
        if type(plan.get(key)) is not int or plan[key] <= 0:
            raise ValueError('Positive integer dimensions are required')
    if not isinstance(plan.get('shots'), list) or not plan['shots']:
        raise ValueError('A nonempty shot list is required')
    root = Path(media_root).resolve()
    for index, shot in enumerate(plan['shots'], 1):
        if not isinstance(shot, dict) or not isinstance(shot.get('path'), str) or not shot['path']:
            raise ValueError(f'Shot {index} needs a nonempty relative path')
        path = Path(shot['path'])
        if path.is_absolute() or root not in (root / path).resolve().parents:
            raise ValueError('Shot paths must stay inside the media directory')
        if not (root / path).is_file():
            raise ValueError(f'Missing source: {path}')
        if any(type(shot.get(k)) is not int for k in ('in', 'out', 'source_frames')):
            raise ValueError('Ranges must be integer frame counts')
        if not 0 <= shot['in'] < shot['out'] <= shot['source_frames']:
            raise ValueError('Invalid source range (out is exclusive)')
    return root


def build(plan, media_root, output):
    root = validate(plan, media_root)
    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    fps = plan['fps']
    def rate(parent):
        r = child(parent, 'rate'); child(r, 'timebase', fps); child(r, 'ntsc', 'FALSE')
    def format_video(parent):
        fmt = child(parent, 'format'); sample = child(fmt, 'samplecharacteristics')
        rate(sample); child(sample, 'width', plan['width']); child(sample, 'height', plan['height'])
        child(sample, 'pixelaspectratio', 'square'); child(sample, 'fielddominance', 'none')
    xml = ET.Element('xmeml', version='5')
    seq = child(xml, 'sequence', id='sequence-1')
    child(seq, 'name', plan.get('name', 'Travel scene'))
    duration = sum(s['out'] - s['in'] for s in plan['shots'])
    child(seq, 'duration', duration); rate(seq)
    video = child(child(seq, 'media'), 'video'); format_video(video)
    track = child(video, 'track'); cursor = 0
    for index, shot in enumerate(plan['shots'], 1):
        clip = child(track, 'clipitem', id=f'clip-{index}')
        child(clip, 'name', Path(shot['path']).name); child(clip, 'enabled', 'TRUE')
        child(clip, 'duration', shot['source_frames']); rate(clip)
        child(clip, 'start', cursor); cursor += shot['out'] - shot['in']; child(clip, 'end', cursor)
        child(clip, 'in', shot['in']); child(clip, 'out', shot['out'])
        file = child(clip, 'file', id=f'file-{index}')
        child(file, 'name', Path(shot['path']).name); child(file, 'pathurl', (root / shot['path']).as_uri())
        rate(file); child(file, 'duration', shot['source_frames'])
        fv = child(child(file, 'media'), 'video')
        sample = child(fv, 'samplecharacteristics')
        child(sample, 'width', plan['width']); child(sample, 'height', plan['height'])
        st = child(clip, 'sourcetrack'); child(st, 'mediatype', 'video'); child(st, 'trackindex', 1)
    ET.indent(xml)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as stream:
        stream.write(b'<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n')
        stream.write(ET.tostring(xml, encoding='utf-8'))
    return duration


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('plan', type=Path); p.add_argument('--media-root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    try:
        frames = build(json.loads(a.plan.read_text()), a.media_root, a.output)
        print(f'Wrote {frames} video frames. Audio is NOT included. Native editor import, playback and export still need verification.')
    except (ValueError, KeyError, OSError) as error:
        p.exit(1, f'Error: {error}\n')


if __name__ == '__main__':
    main()
