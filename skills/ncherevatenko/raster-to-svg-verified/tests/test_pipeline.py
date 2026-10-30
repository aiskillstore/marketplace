"""Observable integration checks with synthetic, non-sensitive inputs."""
from copy import deepcopy
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from make_example import fixture
from vectorize import audit, normalized_source, region_masks, tag


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='vector-skill-test-')
        self.directory = Path(self.temp.name)
        self.source, self.spec_path = fixture(self.directory / 'input')

    def tearDown(self):
        self.temp.cleanup()

    def cli(self, *extra, source=None, output=None):
        return subprocess.run([
            sys.executable, str(ROOT / 'scripts' / 'vectorize.py'),
            str(source or self.source), '--out', str(output or self.directory / 'output'),
            *map(str, extra),
        ], capture_output=True, text=True)

    def test_actual_trace_and_render_preserve_canvas_and_ink(self):
        result = self.cli('--regions', self.spec_path)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = self.directory / 'output'
        report = json.loads((output / 'report.json').read_text())
        self.assertEqual(report['canvas'], [360, 240])
        self.assertEqual(report['structure']['editable_regions'], 2)
        self.assertEqual(report['structure']['embedded_images'], 0)
        self.assertEqual(report['region_recovery']['overlap_pixels'], 0)
        self.assertGreater(report['comparison']['ink_f1'], 0.85)
        self.assertLess(report['comparison']['foreground_rmse'], 0.25)
        self.assertLessEqual(report['comparison']['boundary_distance_p95_px'], 2)
        with Image.open(output / 'render.png') as image:
            self.assertEqual(image.size, (360, 240))
        text = (output / 'report.json').read_text()
        self.assertNotIn(str(self.directory), text)
        root = ET.parse(output / 'drawing.svg').getroot()
        self.assertEqual(root.find(f'.//*[@id="region-left"]').get('fill'), '#ffffff')

    def test_barrier_repair_splits_regions_without_changing_source(self):
        gray = normalized_source(self.source, 'luminance')
        original = gray.copy()
        spec = json.loads(self.spec_path.read_text())
        masks, info = region_masks(gray, spec)
        self.assertEqual(info['overlap_pixels'], 0)
        self.assertTrue(np.array_equal(gray, original))
        self.assertTrue(masks[0][1][150, 70])
        self.assertFalse(masks[0][1][150, 280])
        unrepaired = deepcopy(spec)
        unrepaired['barriers'] = []
        _, merged = region_masks(gray, unrepaired)
        self.assertGreater(merged['overlap_pixels'], 1000)

    def test_exterior_leak_is_rejected_and_explicit_clip_can_bound_it(self):
        gray = normalized_source(self.source, 'luminance').copy()
        gray[80:100, 16:25] = 255
        spec = json.loads(self.spec_path.read_text())
        with self.assertRaisesRegex(ValueError, 'leaks'):
            region_masks(gray, spec)
        spec['regions'][0]['clip'] = [[22, 22], [178, 22], [178, 218], [22, 218]]
        masks, info = region_masks(gray, spec)
        self.assertTrue(info['regions'][0]['clipped'])
        self.assertFalse(masks[0][1][0, 0])

    def test_selected_disconnected_fragments_and_excluded_hole_survive(self):
        gray = np.full((70, 110), 255, 'uint8')
        cv2.rectangle(gray, (5, 5), (104, 64), 0, 2)
        cv2.line(gray, (55, 5), (55, 64), 0, 2)
        cv2.circle(gray, (25, 30), 8, 0, 2)
        spec = {'regions': [{'id': 'compound', 'seeds': [[15, 15], [75, 15]],
                             'exclude_seeds': [[25, 30]]}]}
        masks, _ = region_masks(gray, spec)
        mask = masks[0][1]
        self.assertTrue(mask[15, 15])
        self.assertTrue(mask[15, 75])
        self.assertFalse(mask[30, 25])

    def test_channel_max_has_explicit_color_removal_limits(self):
        pixels = np.array([[(255, 0, 0), (255, 210, 0), (90, 90, 90),
                            (0, 0, 0), (0, 0, 255)]], 'uint8')
        path = self.directory / 'colors.png'
        Image.fromarray(pixels).save(path)
        self.assertEqual(normalized_source(path, 'channel-max').tolist(),
                         [[255, 255, 90, 0, 255]])
        self.assertLess(normalized_source(path, 'luminance')[0, 0], 100)

    def test_structure_audit_rejects_hidden_bitmap_and_open_region(self):
        root = ET.Element(tag('svg'), {'viewBox': '0 0 100 100'})
        ET.SubElement(root, tag('image'), {'href': 'data:image/png;base64,AA=='})
        with self.assertRaisesRegex(ValueError, 'Forbidden element'):
            audit(root, 100, 100)
        root = ET.Element(tag('svg'), {'viewBox': '0 0 100 100'})
        ET.SubElement(root, tag('path'), {'data-region': 'true',
                      'd': 'M0 0L10 0L10 10Z M20 20L30 20'})
        with self.assertRaisesRegex(ValueError, 'unclosed'):
            audit(root, 100, 100)

    def test_input_and_existing_output_are_not_overwritten(self):
        output = self.directory / 'output'
        output.mkdir()
        sentinel = output / 'drawing.svg'
        sentinel.write_text('keep-existing-file')
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(sentinel.read_text(), 'keep-existing-file')
        source = output / 'reference.png'
        source.write_bytes(self.source.read_bytes())
        original = source.read_bytes()
        result = self.cli('--overwrite', source=source)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(source.read_bytes(), original)

    def test_canvas_mismatch_and_blank_source_fail_clearly(self):
        gray = normalized_source(self.source, 'luminance')
        spec = json.loads(self.spec_path.read_text())
        spec['canvas'] = [100, 100]
        with self.assertRaisesRegex(ValueError, 'canvas does not match'):
            region_masks(gray, spec)
        path = self.directory / 'blank.png'
        Image.new('RGB', (100, 100), 'white').save(path)
        result = self.cli(source=path)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('No dark drawing detail', result.stderr)
        self.assertFalse((self.directory / 'output' / 'drawing.svg').exists())

    def test_transparent_output_is_explicit_and_source_alpha_policy_recorded(self):
        result = self.cli('--background', 'transparent')
        self.assertEqual(result.returncode, 0, result.stderr)
        output = self.directory / 'output'
        image = Image.open(output / 'render.png').convert('RGBA')
        self.assertEqual(image.getpixel((0, 0))[3], 0)
        report = json.loads((output / 'report.json').read_text())
        self.assertIn('composited on white', report['alpha_policy'])


if __name__ == '__main__':
    unittest.main()
