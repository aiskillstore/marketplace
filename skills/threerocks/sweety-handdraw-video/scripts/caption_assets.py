"""Typeset quiet subtitles independently of the hand-drawn artwork font."""
from pathlib import Path
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageColor


def caption_font(options):
    configured = options.get('font', {})
    if configured.get('path'):
        path = Path(configured['path']).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f'Caption font is missing: {path}')
        return str(path.resolve()), int(configured.get('index', 0))
    for path in ('/System/Library/Fonts/Hiragino Sans GB.ttc',
                 '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'):
        if Path(path).is_file():
            return path, 0
    raise FileNotFoundError('Set captions.font to a legible regular Chinese font')


def resolve_cues(beat):
    source = beat.get('caption_cues') or [{'text': beat['text'], 'start': 0, 'end': beat['duration']}]
    if ''.join(cue['text'] for cue in source) != beat['text']:
        raise ValueError('Caption cues must preserve every narration character in order')
    previous = 0.
    result = []
    for cue in source:
        start, end = float(cue['start']), float(cue['end'])
        if not cue['text'].strip() or not math.isfinite(start + end) or not 0 <= previous <= start < end <= beat['duration'] + .001:
            raise ValueError('Caption cues must be nonempty, ordered and inside the measured beat')
        result.append({'text': cue['text'], 'start': beat['start'] + start, 'end': beat['start'] + end})
        previous = end
    return result


def build_caption(directory, name, text, options, canvas_width, canvas_height):
    path, index = caption_font(options)
    size = int(options.get('font_size', max(18, round(canvas_height * 38 / 1080))))
    if size <= 0:
        raise ValueError('Captions require a positive font size')
    font = ImageFont.truetype(path, size, index=index)
    stroke = int(options.get('stroke_width', 2))
    ratio = float(options.get('max_width_ratio', .76))
    if not 0 < ratio <= .95 or not 0 <= stroke <= 4:
        raise ValueError('Invalid caption width or outline')
    width_limit = int(canvas_width * ratio)
    lines, current = [], ''
    for character in text:
        if character == '\n' or (current and font.getlength(current + character) > width_limit - 16 - stroke * 2):
            lines.append(current)
            current = ''
        if character != '\n':
            current += character
    if current:
        lines.append(current)
    if not lines or len(lines) > int(options.get('max_lines', 2)):
        raise ValueError('Split long subtitles into speech-aligned caption_cues')
    margin = 6 + stroke
    boxes = [font.getbbox(line, stroke_width=stroke) for line in lines]
    line_height = max(box[3] - box[1] for box in boxes)
    line_gap = round(size * .18)
    width = max(box[2] - box[0] for box in boxes) + margin * 2
    height = line_height * len(lines) + line_gap * (len(lines) - 1) + margin * 2
    image = Image.new('RGBA', (width, height))
    draw = ImageDraw.Draw(image)
    background = options.get('background')
    if background is not None:
        if not isinstance(background, dict) or not 0 < float(background.get('opacity', .76)) <= 1:
            raise ValueError('Caption background requires color and opacity within 0..1')
        color = ImageColor.getrgb(background.get('color', '#243039')) + (round(255 * background.get('opacity', .76)),)
        draw.rounded_rectangle((5, 5, width-6, height-6), radius=round(size*.2), fill=color)
    for row, (line, box) in enumerate(zip(lines, boxes)):
        x = (width - (box[2] - box[0])) // 2 - box[0]
        y = margin + row * (line_height + line_gap) - box[1]
        draw.text((x, y), line, font=font, fill=options.get('color', '#FFFFFF'),
                  stroke_width=stroke, stroke_fill=options.get('stroke_color', '#000000'))
    image.save(Path(directory) / f'{name}.png')
    np.savez_compressed(Path(directory) / f'{name}.npz', reveal=np.zeros((height, width), dtype=np.float32))
    return {'type': 'typeset_caption', 'text': text, 'lines': lines, 'width': width, 'height': height,
            'font': {'path': path, 'index': index, 'family': font.getname()[0], 'style': font.getname()[1]},
            'font_size': size, 'color': options.get('color', '#FFFFFF'), 'stroke_width': stroke,
            'stroke_color': options.get('stroke_color', '#000000'), 'background': background, 'safe_margin': 5, 'segments': []}
