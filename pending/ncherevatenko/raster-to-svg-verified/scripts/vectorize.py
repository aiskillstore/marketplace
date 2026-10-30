#!/usr/bin/env python3
"""Trace neutral line art, recover explicit regions, and compare the render."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

import cv2
import numpy as np
from PIL import Image, ImageOps
import resvg_py

NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def tag(name):
    return f'{{{NS}}}{name}'


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def normalized_source(path, signal):
    with Image.open(path) as source:
        image = ImageOps.exif_transpose(source).convert('RGBA')
    white = Image.new('RGBA', image.size, 'white')
    rgb = np.asarray(Image.alpha_composite(white, image).convert('RGB'))
    if signal == 'channel-max':
        gray = rgb.max(axis=2)
    else:
        gray = np.asarray(Image.fromarray(rgb).convert('L'))
    return gray


def polygon(points, shape):
    points = np.asarray(points, dtype=float)
    if points.ndim != 2 or points.shape[0] < 3 or points.shape[1] != 2:
        raise ValueError('A clipping polygon needs at least three [x, y] points.')
    if not np.isfinite(points).all():
        raise ValueError('Polygon coordinates must be finite.')
    mask = np.zeros(shape, np.uint8)
    cv2.fillPoly(mask, [np.rint(points).astype(np.int32)], 1)
    return mask


def trace(mask, folder, name, args):
    """Write ink with correct PBM polarity, preserving Potrace coordinates."""
    if not mask.any():
        return [], None
    pbm, svg = folder / f'{name}.pbm', folder / f'{name}.svg'
    Image.fromarray(np.where(mask, 0, 255).astype('uint8')).convert('1').save(pbm)
    subprocess.run([
        args.potrace, str(pbm), '--svg', '--flat', '--output', str(svg),
        '--turdsize', str(args.despeckle), '--alphamax', str(args.alphamax),
        '--opttolerance', str(args.tolerance),
    ], check=True, capture_output=True, text=True)
    group = ET.parse(svg).getroot().find(tag('g'))
    if group is None:
        raise ValueError('Potrace output does not contain a geometry group.')
    return [node.get('d', '') for node in group.iter(tag('path'))], group.get('transform')


def region_masks(gray, spec):
    """Use explicit source-coordinate selections, never semantic auto-labeling."""
    if 'canvas' in spec and spec['canvas'] != [gray.shape[1], gray.shape[0]]:
        raise ValueError('Region specification canvas does not match the source.')
    threshold = int(spec.get('threshold', 190))
    if not 1 <= threshold <= 255:
        raise ValueError('Region threshold must be in 1..255.')
    barrier = (gray < threshold).astype(np.uint8)
    for repair in spec.get('barriers', []):
        points = np.asarray(repair['points'], dtype=float)
        width = int(repair.get('width', 1))
        if points.ndim != 2 or points.shape[1] != 2 or len(points) < 2:
            raise ValueError('A barrier needs at least two [x, y] points.')
        if not np.isfinite(points).all() or width < 1:
            raise ValueError('Barrier coordinates and width are invalid.')
        cv2.polylines(barrier, [np.rint(points).astype(np.int32)], False, 1, width)
    _, labels = cv2.connectedComponents(1 - barrier, connectivity=4)
    exterior = set(np.concatenate((labels[0], labels[-1], labels[:, 0], labels[:, -1])))

    def seed_labels(seeds):
        values = []
        for x, y in seeds:
            if not float(x).is_integer() or not float(y).is_integer():
                raise ValueError('Seed coordinates must be integers.')
            x, y = int(x), int(y)
            if not (0 <= x < gray.shape[1] and 0 <= y < gray.shape[0]):
                raise ValueError('A region seed is outside the source canvas.')
            value = int(labels[y, x])
            if value == 0:
                raise ValueError('A region seed lies on an ink or barrier pixel.')
            values.append(value)
        return values

    masks, used_ids, meta = [], set(), []
    for item in spec.get('regions', []):
        identifier = item['id']
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]*', identifier):
            raise ValueError('Region IDs must start with a letter and use safe ID characters.')
        if identifier in used_ids or identifier in {'background', 'regions', 'ink'}:
            raise ValueError(f'Duplicate or reserved region ID: {identifier}')
        used_ids.add(identifier)
        seeds = seed_labels(item.get('seeds', []))
        if not seeds:
            raise ValueError(f'Region {identifier} has no seeds.')
        clipped = 'clip' in item
        if exterior.intersection(seeds) and not clipped:
            raise ValueError(f'Region {identifier} leaks to the canvas edge; inspect the gap or specify a clip.')
        mask = np.isin(labels, seeds).astype(np.uint8)
        clip = polygon(item['clip'], gray.shape) if clipped else np.ones_like(mask)
        mask &= clip
        radius = int(item.get('close_radius', 0))
        if radius < 0:
            raise ValueError('close_radius cannot be negative.')
        if radius:
            kernel = np.ones((2 * radius + 1, 2 * radius + 1), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        if item.get('fill_holes', True):
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            mask[:] = 0
            # Keep every selected fragment; never silently drop all but the largest.
            cv2.drawContours(mask, contours, -1, 1, cv2.FILLED)
        mask &= clip
        excluded = seed_labels(item.get('exclude_seeds', []))
        mask[np.isin(labels, excluded)] = 0
        if not mask.any():
            raise ValueError(f'Region {identifier} is empty.')
        masks.append((identifier, mask))
        meta.append({'id': identifier, 'pixels': int(mask.sum()), 'clipped': clipped})
    overlap = 0
    if masks:
        overlap = int((np.sum([mask for _, mask in masks], axis=0) > 1).sum())
    return masks, {'regions': meta, 'overlap_pixels': overlap,
                   'barrier_repairs': len(spec.get('barriers', [])),
                   'semantic_correctness': 'requires visual review'}


def explicitly_closed(data):
    subpaths = re.split(r'(?=[Mm])', data.strip())
    return bool(data.strip()) and all(part.rstrip().endswith(('z', 'Z'))
                                     for part in subpaths if part.strip())


def audit(root, width, height):
    errors, ids = [], []
    forbidden = {'image', 'feImage', 'foreignObject', 'script', 'text', 'tspan'}
    for element in root.iter():
        local = element.tag.split('}')[-1]
        if local in forbidden:
            errors.append(f'Forbidden element: {local}')
        if element.get('id'):
            ids.append(element.get('id'))
        for key, value in element.attrib.items():
            local_key = key.split('}')[-1]
            if local_key.lower().startswith('on'):
                errors.append('Executable event attribute')
            if local_key == 'href' and not value.startswith('#'):
                errors.append('External or embedded asset reference')
            if 'url(' in value.lower() or '@import' in value.lower():
                errors.append('Unexpected CSS asset reference')
        if local == 'style' and element.text:
            errors.append('Unexpected stylesheet')
        if element.get('data-region') == 'true' and not explicitly_closed(element.get('d', '')):
            errors.append('Editable region has an unclosed subpath')
    if len(ids) != len(set(ids)):
        errors.append('Duplicate IDs')
    if root.get('viewBox') != f'0 0 {width} {height}':
        errors.append('Unexpected viewBox')
    if errors:
        raise ValueError('; '.join(sorted(set(errors))))
    return {'path_count': len(list(root.iter(tag('path')))),
            'editable_regions': sum(e.get('data-region') == 'true' for e in root.iter()),
            'embedded_images': 0, 'live_text_elements': 0, 'unique_ids': True,
            'editable_subpaths_explicitly_closed': True}


def comparison(reference, rendered, threshold=160):
    a, b = reference < threshold, rendered < threshold
    union = a | b
    error = ((reference.astype(float) - rendered) / 255) ** 2
    denom = int(a.sum() + b.sum())
    f1 = float(2 * (a & b).sum() / denom) if denom else 1.0
    edges_a = cv2.morphologyEx(a.astype('uint8'), cv2.MORPH_GRADIENT, np.ones((3, 3), 'uint8')) > 0
    edges_b = cv2.morphologyEx(b.astype('uint8'), cv2.MORPH_GRADIENT, np.ones((3, 3), 'uint8')) > 0
    distance = None
    if edges_a.any() and edges_b.any():
        da = cv2.distanceTransform((~edges_a).astype('uint8'), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
        db = cv2.distanceTransform((~edges_b).astype('uint8'), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
        samples = np.concatenate((da[edges_b], db[edges_a]))
        distance = float(np.percentile(samples, 95))
    overlay = np.full((*reference.shape, 3), 255, 'uint8')
    overlay[a] = (0, 150, 190)
    overlay[b] = (225, 65, 145)
    overlay[a & b] = (25, 25, 25)
    metrics = {'ink_threshold': threshold, 'ink_f1': f1,
               'canvas_rmse': float(math.sqrt(error.mean())),
               'foreground_rmse': float(math.sqrt(error[union].mean())) if union.any() else 0.0,
               'boundary_distance_p95_px': distance,
               'reference_ink_pixels': int(a.sum()), 'rendered_ink_pixels': int(b.sum())}
    return metrics, overlay


def run(args):
    source, out = Path(args.input), Path(args.out)
    if not source.is_file():
        raise ValueError('Input file does not exist.')
    if not shutil.which(args.potrace):
        raise ValueError('Potrace is missing. Install it with your system package manager.')
    if not (math.isfinite(args.alphamax) and math.isfinite(args.tolerance)):
        raise ValueError('Trace parameters must be finite.')
    if args.despeckle < 0 or args.alphamax < 0 or args.tolerance < 0:
        raise ValueError('Trace parameters cannot be negative.')
    outputs = ['drawing.svg', 'render.png', 'reference.png', 'overlay.png', 'difference.png', 'report.json']
    if source.resolve() in {(out / filename).resolve() for filename in outputs}:
        raise ValueError('Output would overwrite the input; select another output directory.')
    if not args.overwrite and any((out / name).exists() for name in outputs):
        raise ValueError('Output already exists. Choose another directory or use --overwrite.')
    palette = sorted(set(int(v.strip()) for v in args.gray_levels.split(',')))
    if not palette or min(palette) < 0 or max(palette) > 254:
        raise ValueError('Gray levels must be integers in 0..254; white is implicit.')
    gray = normalized_source(source, args.signal)
    height, width = gray.shape
    if not (gray < 128).any():
        raise ValueError('No dark drawing detail found; inspect the signal or select another workflow.')
    spec = json.loads(Path(args.regions).read_text()) if args.regions else None
    masks, region_info = region_masks(gray, spec) if spec else ([], None)
    root = ET.Element(tag('svg'), {'width': str(width), 'height': str(height),
                                  'viewBox': f'0 0 {width} {height}', 'version': '1.1'})
    ET.SubElement(root, tag('title')).text = 'Traced line drawing'
    if args.background == 'white':
        ET.SubElement(root, tag('path'), {'id': 'background', 'd': f'M0 0H{width}V{height}H0Z', 'fill': '#fff'})
    with tempfile.TemporaryDirectory(prefix='svg-trace-') as temp:
        folder = Path(temp)
        regions = ET.SubElement(root, tag('g'), {'id': 'regions', 'fill': '#fff'})
        for identifier, mask in masks:
            data, transform = trace(mask, folder, identifier, args)
            if not data:
                raise ValueError(f'Region {identifier} disappeared during tracing; lower --despeckle.')
            ET.SubElement(regions, tag('path'), {'id': identifier, 'data-region': 'true',
                                               'fill': '#ffffff', 'd': ' '.join(data), 'transform': transform})
        ink = ET.SubElement(root, tag('g'), {'id': 'ink', 'pointer-events': 'none'})
        values = palette + [255]
        for i in range(len(palette) - 1, -1, -1):
            value, threshold = values[i], (values[i] + values[i + 1]) / 2
            paths, transform = trace(gray < threshold, folder, f'ink-{value}', args)
            for data in paths:
                ET.SubElement(ink, tag('path'), {'fill': f'#{value:02x}{value:02x}{value:02x}',
                                                'd': data, 'transform': transform})
    structure = audit(root, width, height)
    svg = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    png = resvg_py.svg_to_bytes(svg_string=svg.decode(), width=width, height=height,
                               background=None if args.background == 'transparent' else 'white',
                               skip_system_fonts=True)
    preview = Image.open(io.BytesIO(png)).convert('RGBA')
    rendered = np.asarray(Image.alpha_composite(Image.new('RGBA', preview.size, 'white'), preview).convert('L'))
    metrics, overlay = comparison(gray, rendered)
    report = {'schema_version': 1, 'source_sha256': sha256(source.read_bytes()),
              'svg_sha256': sha256(svg), 'canvas': [width, height], 'signal': args.signal,
              'alpha_policy': 'input composited on white before tracing',
              'trace': {'gray_levels': palette, 'despeckle': args.despeckle,
                        'alphamax': args.alphamax, 'tolerance': args.tolerance},
              'structure': structure, 'comparison': metrics, 'region_recovery': region_info,
              'limits': 'Visual metrics do not establish region identity or correct inferred boundaries.'}
    if spec:
        report['region_spec_sha256'] = sha256(Path(args.regions).read_bytes())
    out.mkdir(parents=True, exist_ok=True)
    (out / 'drawing.svg').write_bytes(svg)
    (out / 'render.png').write_bytes(png)
    Image.fromarray(gray).save(out / 'reference.png')
    Image.fromarray(overlay).save(out / 'overlay.png')
    difference = np.abs(gray.astype(np.int16) - rendered.astype(np.int16)).astype('uint8')
    Image.fromarray(difference).save(out / 'difference.png')
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='Raster line drawing; never modified')
    parser.add_argument('--out', required=True, help='Output directory')
    parser.add_argument('--signal', choices=['luminance', 'channel-max'], default='luminance')
    parser.add_argument('--gray-levels', default='0,48,96,144,208', help='Ascending or unsorted gray values; white is implicit')
    parser.add_argument('--regions', help='JSON specification in source-pixel coordinates')
    parser.add_argument('--background', choices=['white', 'transparent'], default='white')
    parser.add_argument('--despeckle', type=int, default=1)
    parser.add_argument('--alphamax', type=float, default=1.0)
    parser.add_argument('--tolerance', type=float, default=0.1)
    parser.add_argument('--potrace', default='potrace')
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    try:
        report = run(args)
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(2, f'Error: {error}\n')
    print(json.dumps({'structure': report['structure'], 'comparison': report['comparison']}, indent=2))


if __name__ == '__main__':
    main()
