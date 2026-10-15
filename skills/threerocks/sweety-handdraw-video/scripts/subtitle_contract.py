"""Reject duplicate caption layers, muxed tracks and automatically loaded sidecars."""
import json
import math
from pathlib import Path
import subprocess


def validate_subtitles(timeline):
    if timeline.get('captions') != {'presentation': 'burned', 'owner': 'caption_events'}:
        raise ValueError('Exactly one burned subtitle owner is required')
    captions = []
    for page in timeline['pages']:
        for event in page['events']:
            asset = timeline['assets'][event['asset']]
            is_caption = asset['type'] == 'typeset_caption'
            if bool(event.get('caption')) != is_caption or (event.get('role') == 'caption') != is_caption:
                raise ValueError('Caption asset and event roles must match')
            if is_caption:
                start, end = event['start'], event['hide']
                if not math.isfinite(start + end) or not page['start'] <= start < end <= page['end'] + .001:
                    raise ValueError('Subtitle must remain inside its page')
                captions.append((start, end, asset['text']))
            elif (asset.get('text') in {cue['text'] for cue in timeline['cues']}
                  and event.get('y', 0) >= timeline.get('canvas', {}).get('height', 1080) * .8):
                raise ValueError('Narration subtitle is duplicated in a bottom artwork text layer')
    captions.sort()
    cues = sorted((cue['start'], cue['end'], cue['text']) for cue in timeline['cues'])
    if captions != cues:
        raise ValueError('Every subtitle cue must have exactly one matching caption event')
    if any(left[1] > right[0] + 1e-7 for left, right in zip(captions, captions[1:])):
        raise ValueError('Multiple subtitles are visible at the same time')
    return {'owner': 'caption_events', 'cue_count': len(cues), 'maximum_simultaneous_captions': 1}


def validate_subtitle_delivery(video):
    video = Path(video)
    # Players differ in sidecar naming rules, so keep all editing subtitles elsewhere.
    suffixes = {'.srt', '.ass', '.ssa', '.vtt', '.sub', '.idx'}
    if any(path.suffix.lower() in suffixes for path in video.parent.iterdir() if path.is_file()):
        raise ValueError('Move subtitle sidecars into editing/ before delivering a burned-caption video')
    result = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 's', '-show_entries',
                             'stream=index', '-of', 'json', str(video)], check=True, capture_output=True, text=True)
    if json.loads(result.stdout).get('streams'):
        raise ValueError('Burned-caption video must not contain another subtitle track')
    return {'subtitle_streams': 0, 'adjacent_sidecars': 0, 'presentation': 'burned'}
