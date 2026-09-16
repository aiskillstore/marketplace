"""Encode the selected fonts in a SlideViber draft; never change slide content."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

A = 'http://schemas.openxmlformats.org/drawingml/2006/main'


def prepare(source: Path, output: Path, font: str) -> dict:
    if output.exists() or source.resolve() == output.resolve():
        raise ValueError('A new output path is required')
    if not font.strip():
        raise ValueError('An explicitly selected font is required')
    count = 0
    with ZipFile(source) as incoming, ZipFile(output, 'x') as outgoing:
        for item in incoming.infolist():
            data = incoming.read(item.filename)
            if item.filename.startswith('ppt/') and item.filename.endswith('.xml'):
                root = ET.fromstring(data)
                changed = False
                for node in root.iter():
                    if node.tag not in {f'{{{A}}}{name}' for name in
                                        ('rPr', 'defRPr', 'endParaRPr', 'majorFont', 'minorFont')}:
                        continue
                    for script in ('latin', 'ea', 'cs'):
                        child = node.find(f'{{{A}}}{script}')
                        if child is None:
                            child = ET.SubElement(node, f'{{{A}}}{script}')
                        child.set('typeface', font)
                        count += 1
                    changed = True
                if changed:
                    data = ET.tostring(root, encoding='utf-8', xml_declaration=True)
            outgoing.writestr(item, data)
    return {'input_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'output_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
            'font': font, 'font_declarations': count,
            'content_or_geometry_changes': False}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--font', required=True)
    args = p.parse_args()
    print(json.dumps(prepare(args.input, args.output, args.font), ensure_ascii=False))
