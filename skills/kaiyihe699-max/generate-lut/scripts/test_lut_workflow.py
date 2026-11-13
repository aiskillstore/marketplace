"""Behavioral regression tests; run with python scripts/test_lut_workflow.py."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import random
import struct
import tempfile
import unittest
import zipfile

from PIL import Image, ImageCms
from apply_lut_preview import apply_lut, parse_cube, lookup
from cube_io import read_cube
from generate_cube_lut import LOOKS, apply_transform, write_cube
from image_color import open_srgb, open_for_lut, prepare_image, srgb_profile_bytes
from create_lut_package import build_package, digest, validate_recipe
from batch_apply_lut import process_image
from validate_lut import analyze


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def cube(self, text_prefix="", edit=None):
        path = self.root / "test.cube"
        rows = [f"{r} {g} {b}" for b in (0, 1) for g in (0, 1) for r in (0, 1)]
        if edit:
            rows = edit(rows)
        path.write_text(text_prefix + "\nLUT_3D_SIZE 2\n" + "\n".join(rows), encoding="utf-8")
        return path

    def args(self, folder="delivery", **overrides):
        image = self.root / "input.png"
        if not image.exists():
            im = Image.new("RGB", (7, 5))
            im.putdata([(x * 31, y * 51, (x + y) * 21) for y in range(5) for x in range(7)])
            im.save(image)
        values = dict(look="warm-film", recipe=None, output_dir=str(self.root / folder), input=str(image),
            size=9, strength=0.65, title="Test Look", description="test", max_size=20, no_protect_skin=False,
            contrast=None, saturation=None, warmth=None, exposure=None, lift=None, curve=None, bleach=None,
            shadow_tint=None, mid_tint=None, highlight_tint=None)
        values.update(overrides)
        return argparse.Namespace(**values)

    def test_identity_is_neutral_with_skin_protection(self):
        params = json.loads(json.dumps(LOOKS["neutral"]))
        self.assertEqual(apply_transform((0.7,0.45,0.3), params, 0.65, True), (0.7,0.45,0.3))
        rng = random.Random(4)
        for rgb in [(0.7, 0.45, 0.3)] + [tuple(rng.random() for _ in range(3)) for _ in range(100)]:
            output = apply_transform(rgb, LOOKS["neutral"], 0.65, True)
            self.assertLess(max(abs(a-b) for a,b in zip(rgb, output)), 1e-12)

    def test_identity_lut_preserves_all_8bit_values(self):
        size, values = parse_cube(self.cube())
        im = Image.new("RGB", (256, 1))
        im.putdata([(i, 255-i, (i*13) % 256) for i in range(256)])
        self.assertEqual(im.tobytes(), apply_lut(im, size, values).tobytes())

    def test_nondefault_domain_rejected_by_both_readers(self):
        path = self.cube("DOMAIN_MIN -1 -1 -1\nDOMAIN_MAX 1 1 1")
        for reader in (parse_cube, read_cube):
            with self.assertRaisesRegex(ValueError, "non-default domains"):
                reader(path)

    def test_malformed_external_files_rejected(self):
        variants = ["DOMAIN_MIN nan 0 0", "DOMAIN_MAX 1 1", "LUT_3D_SIZE 2", "LUT_1D_SIZE 2"]
        for prefix in variants:
            with self.subTest(prefix=prefix), self.assertRaises(ValueError):
                read_cube(self.cube(prefix))
        for bad in ("nan 0 0", "inf 0 0", "1.1 0 0", "0 0 0 9", "UNSUPPORTED 0 0"):
            with self.subTest(row=bad), self.assertRaises(ValueError):
                read_cube(self.cube(edit=lambda rows: [bad] + rows[1:]))

    def test_inline_comments_and_bom_supported(self):
        path = self.cube('\ufeffTITLE "test"\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1', lambda rows: [r + ' # ok' for r in rows])
        self.assertEqual(read_cube(path)[0], 2)

    def test_nonidentity_axis_order(self):
        path = self.cube(edit=lambda rows: [f"{b} {r} {g}" for b in (0,1) for g in (0,1) for r in (0,1)])
        size, values = parse_cube(path)
        self.assertEqual(lookup(values, size, 0.2, 0.4, 0.8), (0.8, 0.2, 0.4))

    def test_profile_conversion_and_srgb_output_tag(self):
        # Synthetic wide-red RGB profile: alter its PCS red colorant, preserving a valid RGB ICC structure.
        data = bytearray(srgb_profile_bytes())
        count = struct.unpack_from(">I", data, 128)[0]
        for index in range(count):
            offset = 132 + index * 12
            signature, tag_offset, length = struct.unpack_from(">4sII", data, offset)
            if signature == b"rXYZ":
                x = struct.unpack_from(">i", data, tag_offset + 8)[0]
                struct.pack_into(">i", data, tag_offset + 8, int(x * 1.2))
                break
        image = Image.new("RGBA", (1, 1), (160, 90, 70, 83))
        image.info["icc_profile"] = bytes(data)
        converted, info = prepare_image(image)
        self.assertNotEqual(converted.getpixel((0,0))[:3], (160,90,70))
        self.assertEqual(converted.getpixel((0,0))[3], 83)
        self.assertEqual(info["icc_action"], "converted_to_sRGB")
        profile = ImageCms.ImageCmsProfile(__import__('io').BytesIO(converted.info['icc_profile']))
        self.assertIn("sRGB", ImageCms.getProfileDescription(profile))

    def test_invalid_icc_and_high_bit_depth_rejected(self):
        image = Image.new("RGB", (1,1)); image.info['icc_profile'] = b'broken'
        with self.assertRaisesRegex(ValueError, "ICC"):
            prepare_image(image)
        with self.assertRaisesRegex(ValueError, "8-bit"):
            prepare_image(Image.new("I;16", (1,1)))

    def test_orientation_and_palette_alpha(self):
        image = Image.new("RGB", (3,2)); image.getexif()[274] = 6
        oriented, _ = prepare_image(image)
        self.assertEqual(oriented.size, (2,3))
        image = Image.new("P", (1,1)); image.info['transparency'] = 0
        transparent, _ = prepare_image(image)
        self.assertEqual(transparent.getpixel((0,0))[3], 0)

    def test_package_preview_matches_reimported_export(self):
        args = self.args(shadow_tint=[-0.02, 0.03, 0.04], highlight_tint=[0.04,0.01,-0.02], bleach=0.08)
        build_package(args)
        folder = Path(args.output_dir)
        size, values = parse_cube(folder / 'look.cube')
        source, _ = open_srgb(args.input)
        expected = apply_lut(source, size, values, 1.0)
        with Image.open(folder / 'preview.png') as preview:
            self.assertEqual(expected.tobytes(), preview.tobytes())
            self.assertTrue(preview.info.get('icc_profile'))
        double_strength = apply_lut(source, size, values, 0.65)
        self.assertNotEqual(double_strength.tobytes(), expected.tobytes())
        with zipfile.ZipFile(folder.with_suffix('.zip')) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(archive.read('look.cube'), (folder/'look.cube').read_bytes())

    def test_recipe_replay_byte_exact_and_preserves_source(self):
        args = self.args(); build_package(args)
        original = digest(Path(args.input))
        replay = self.args('replay', look=None, recipe=str(Path(args.output_dir)/'recipe.json'), size=None,
            strength=None, title=None, description=None)
        build_package(replay)
        self.assertEqual(digest(Path(args.output_dir)/'look.cube'), digest(Path(replay.output_dir)/'look.cube'))
        self.assertEqual(digest(Path(args.input)), original)
        with self.assertRaises(FileExistsError):
            build_package(args)

    def test_recipe_rejects_invalid_schema_and_nan(self):
        args = self.args(); build_package(args)
        recipe = json.loads((Path(args.output_dir)/'recipe.json').read_text(encoding='utf-8'))
        for field, value in [('strength',float('nan')), ('size',True), ('protect_skin','false'), ('engine_version','999')]:
            bad = copy.deepcopy(recipe); bad[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_recipe(bad)

    def test_batch_and_package_agree(self):
        args = self.args(); build_package(args)
        folder = Path(args.output_dir); size, values = parse_cube(folder/'look.cube')
        target = self.root/'batch.png'
        process_image(Path(args.input), target, size, values, 1.0)
        with Image.open(target) as batch, Image.open(folder/'preview.png') as preview:
            self.assertEqual(batch.tobytes(), preview.tobytes())
            self.assertIn('sRGB', ImageCms.getProfileDescription(ImageCms.ImageCmsProfile(__import__('io').BytesIO(batch.info['icc_profile']))))

    def test_generator_refuses_overwrite_or_nonfinite_params(self):
        path = self.root/'generated.cube'
        write_cube(path, 3, 'test', 'neutral', 1, LOOKS['neutral'], True)
        with self.assertRaises(FileExistsError):
            write_cube(path, 3, 'test', 'neutral', 1, LOOKS['neutral'], True)
        params = dict(LOOKS['neutral']); params['curve'] = float('nan')
        with self.assertRaises(ValueError):
            write_cube(self.root/'invalid.cube', 3, 'test', 'custom', 1, params, True)

    def test_technical_preview_bypasses_icc_only_when_explicit(self):
        image = Image.new('RGB', (2,1), (120,80,40))
        image.info['icc_profile'] = b'broken-profile'
        path = self.root/'encoded.png'; image.save(path, icc_profile=image.info['icc_profile'])
        with self.assertRaises(ValueError):
            open_for_lut(path)
        encoded, info = open_for_lut(path, 'encoded-rgb')
        self.assertEqual(encoded.tobytes(), image.tobytes())
        self.assertNotIn('icc_profile', encoded.info)
        self.assertEqual(info['icc_action'], 'explicit_bypass')

    def test_neutral_ramp_discontinuity_and_reversal_warnings(self):
        size = 9
        values = [(r/8,g/8,b/8) for b in range(size) for g in range(size) for r in range(size)]
        self.assertEqual(analyze(size, values), ([], []))
        values[((4*size)+4)*size+4] = (0.95,0.95,0.95)
        errors, warnings = analyze(size, values)
        self.assertEqual(errors, [])
        self.assertTrue(any('descending' in warning for warning in warnings))
        self.assertTrue(any('abruptly' in warning for warning in warnings))


if __name__ == '__main__':
    unittest.main(verbosity=2)
