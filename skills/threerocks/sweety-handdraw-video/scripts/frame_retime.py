"""Retime approved video frames with one monotonic map; do not redraw its layers."""
import math
from pathlib import Path
import subprocess


def validate_anchors(anchors):
    if len(anchors) < 3 or tuple(anchors[0]) != (0., 0.):
        raise ValueError('Frame retiming requires a complete monotonic map starting at zero')
    if not any(tuple(point) == (1., 1.) for point in anchors):
        raise ValueError('Frame retiming must preserve the one-second cover')
    if any(not math.isfinite(value) for point in anchors for value in point):
        raise ValueError('Frame retiming timestamps must be finite')
    for left, right in zip(anchors, anchors[1:]):
        if not left[0] < right[0] or not left[1] < right[1]:
            raise ValueError('Frame retiming cannot reverse, delete or reorder a time interval')
        if left[0] < 1 and (left[0] != left[1] or right[0] != right[1]):
            raise ValueError('Frame retiming cannot change the cover timing')


def timestamp_expression(anchors):
    validate_anchors(anchors)
    segments = []
    for (old, new), (old_end, new_end) in zip(anchors, anchors[1:]):
        slope = (new_end - new) / (old_end - old)
        segments.append((old_end, f'({new:.9f}+(T-{old:.9f})*{slope:.12f})'))

    def branch(items):
        if len(items) == 1:
            return items[0][1]
        middle = len(items) // 2
        return f'if(lt(T,{items[middle - 1][0]:.9f}),{branch(items[:middle])},{branch(items[middle:])})'

    return branch(segments) + '/TB'


def retime_frames(source, mixed_audio, anchors, destination, filter_record, fps=30):
    """Only timestamps change; the caller supplies the locked, complete mixed audio."""
    expression = timestamp_expression(anchors)
    destination = Path(destination)
    source = Path(source)
    if source.resolve() == destination.resolve():
        raise ValueError('Keep the approved source video; write retiming to a new file')
    filter_record = Path(filter_record)
    filter_record.write_text("setpts='" + expression + f"',fps={fps}")
    temporary = destination.with_name(destination.stem + '.encoding.mp4')
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(source),
        '-i', str(mixed_audio), '-filter_script:v', str(filter_record), '-map', '0:v:0', '-map', '1:a:0',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-threads', '4', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k', '-t', str(anchors[-1][1]), '-movflags', '+faststart',
        '-map_metadata', '-1', str(temporary)], check=True)
    temporary.replace(destination)
