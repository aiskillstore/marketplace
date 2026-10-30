#!/usr/bin/env python3
"""Generate the public reference from abstract geometry, with no external input."""
from pathlib import Path
import json
from types import SimpleNamespace

from PIL import Image, ImageDraw, ImageFont

from vectorize import run


def fixture(destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    scale = 4
    image = Image.new('RGB', (360 * scale, 240 * scale), 'white')
    draw = ImageDraw.Draw(image)
    def box(values):
        return tuple(round(value * scale) for value in values)
    draw.rounded_rectangle(box((20, 20, 340, 220)), radius=12 * scale,
                           outline='black', width=3 * scale)
    draw.line(box((180, 20, 180, 220)), fill='black', width=3 * scale)
    draw.rectangle(box((173, 106, 187, 134)), fill='white')
    font = ImageFont.load_default(size=18 * scale)
    draw.text((180 * scale, 120 * scale), '1', fill='black', font=font,
              anchor='mm')
    draw.ellipse(box((52, 60, 120, 128)), fill=(145, 145, 145),
                 outline='black', width=2 * scale)
    draw.ellipse(box((67, 75, 105, 113)), fill='white',
                 outline='black', width=2 * scale)
    draw.rounded_rectangle(box((232, 62, 302, 130)), radius=9 * scale,
                           outline='black', width=2 * scale)
    draw.line(box((65, 177, 128, 177)), fill=(96, 96, 96), width=2 * scale)
    draw.line(box((238, 177, 296, 177)), fill='black', width=2 * scale)
    image.resize((360, 240), Image.Resampling.LANCZOS).save(destination / 'source.png')
    spec = {
        'canvas': [360, 240],
        'threshold': 190,
        'barriers': [{'points': [[180, 102], [180, 138]], 'width': 3}],
        'regions': [
            {'id': 'region-left', 'seeds': [[70, 150]], 'fill_holes': True},
            {'id': 'region-right', 'seeds': [[280, 150]], 'fill_holes': True},
        ],
    }
    (destination / 'regions.json').write_text(json.dumps(spec, indent=2) + '\n')
    return destination / 'source.png', destination / 'regions.json'


def main():
    destination = Path(__file__).resolve().parents[1] / 'examples'
    source, spec = fixture(destination)
    report = run(SimpleNamespace(
        input=str(source), out=str(destination), signal='luminance',
        gray_levels='0,48,96,144,208', regions=str(spec), background='white',
        despeckle=1, alphamax=1.0, tolerance=0.1, potrace='potrace', overwrite=True,
    ))
    print(json.dumps(report['comparison'], indent=2))


if __name__ == '__main__':
    main()
