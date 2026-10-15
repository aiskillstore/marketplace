"""Shared pre-render checks for timing, arm coverage and the fixed cover behavior."""
import numpy as np
from PIL import Image


def validate_timeline(timeline):
    if timeline['cover_seconds']!=1:
        raise ValueError('Cover must last exactly one second')
    if timeline['hand'].get('kind', 'hand') != 'pen' and timeline['hand'].get('arm_bottom_at_highest_tip',0)<timeline['canvas']['height']:
        raise ValueError('The forearm cut edge can become visible in-frame')
    for page in timeline['pages']:
        events=sorted((event for event in page['events'] if not event['caption']),key=lambda event:event['start'])
        if any(left['end']>right['start'] for left,right in zip(events,events[1:])):
            raise ValueError('Main drawing groups overlap; only one physical pen is allowed')
        if page['last_drawing_end']>page['speech_end']-.45:
            raise ValueError('Page drawing has no completion hold before narration ends')
    if timeline.get('cues') or timeline.get('assets'):
        from subtitle_contract import validate_subtitles
        validate_subtitles(timeline)
    return True


def validate_cover(renderer):
    original=np.array(renderer.cover.convert('RGB'))
    for moment in (0.,.25,.49,.5):
        if not np.array_equal(np.array(renderer.frame(moment)),original):
            raise ValueError('Cover moves or fades during its first half second')
    for moment in (.6,.75,.9):
        expected=np.array(Image.blend(renderer.cover,Image.new('RGBA',renderer.cover.size,renderer.paper),(moment-.5)/.5).convert('RGB'))
        if not np.array_equal(np.array(renderer.frame(moment)),expected):
            raise ValueError('Cover does not fade smoothly to paper in its last half second')
    return True
