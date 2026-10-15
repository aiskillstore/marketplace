"""Build optional user-supplied text and keep its gentle drift inside the frame."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageColor
from caption_assets import caption_font


def prepare_watermark(options, work, width, height):
    if not options or options.get('enabled') is False or not str(options.get('text', '')).strip():
        return None
    text = str(options['text']).strip()
    opacity = float(options.get('opacity', .24))
    if not math.isfinite(opacity) or not 0 < opacity <= .35:
        raise ValueError('Quiet watermark opacity must be within 0..0.35')
    path, index = caption_font(options)
    size = int(options.get('font_size', round(height * 27 / 1080)))
    font = ImageFont.truetype(path, max(12, size), index=index)
    lines, line = [], ''
    for char in text:
        if char == '\n' or (line and font.getlength(line + char) > width * .58):
            lines.append(line)
            line = ''
        if char != '\n':
            line += char
    if line:
        lines.append(line)
    boxes = [font.getbbox(line) for line in lines]
    line_height = max(box[3]-box[1] for box in boxes)
    gap, margin = round(size*.35), 7
    sprite = Image.new('RGBA', (max(box[2]-box[0] for box in boxes)+2*margin,
                              len(lines)*line_height+(len(lines)-1)*gap+2*margin))
    if sprite.height > height * .3:
        raise ValueError('Watermark text is too long for a quiet background mark')
    draw = ImageDraw.Draw(sprite)
    color = ImageColor.getrgb(options.get('color', '#374753'))+(round(255*opacity),)
    for row, (line, box) in enumerate(zip(lines, boxes)):
        draw.text((margin-box[0], margin+row*(line_height+gap)-box[1]), line, font=font, fill=color)
    target = Path(work)/'watermark.png'
    sprite.save(target)
    return {'source':str(target.resolve()), 'text':text, 'opacity':opacity,
            'width':sprite.width, 'height':sprite.height, 'font_size':size,
            'color':options.get('color', '#374753'), 'start_seconds':1.,
            'motion':'gentle_drift', 'font':{'path':path,'index':index}}


def watermark_position(mark, width, height, seconds):
    scale = height/1080
    x = width-mark['width']-90*scale + 45*scale*math.sin(seconds/17)
    y = 210*scale + 35*scale*math.sin(seconds/23)
    margin = round(24*scale)
    return (round(max(margin,min(width-mark['width']-margin,x))),
            round(max(margin,min(height-mark['height']-margin,y))))
