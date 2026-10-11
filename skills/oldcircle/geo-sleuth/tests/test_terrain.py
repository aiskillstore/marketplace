#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow", "numpy"]
# ///
"""Offline terrain.py fit regressions on synthetic terrain. Run: uv run skills/geo-sleuth/tests/test_terrain.py"""
from __future__ import annotations

import contextlib
import io
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import terrain

LAT0, LON0 = 38.0, 106.0
W, H, HROW = 2000, 1125, 600.0


class FakeDEM:
    """Flat plain; a low near range 6 km west that ends 1 km north of the camera; a high far range 20 km west."""

    def __init__(self, *a, **k):
        pass

    def sample(self, lat, lon):
        y = (np.asarray(lat) - LAT0) * 110540
        x = (np.asarray(lon) - LON0) * 111320 * math.cos(math.radians(LAT0))
        crest = 1500 + 500 * np.sin(y / 2500) + 300 * np.cos(y / 1300)
        far = crest * np.exp(-((x + 20000) / 2500) ** 2)
        near = (350 + 120 * np.sin(y / 700)) * np.exp(-((x + 6000) / 400) ** 2) * (y < 1000) * (y > -4000)
        return np.maximum(far, near)


def synth_ridge(path: Path, f35: float, heading: float, two_layer: bool) -> None:
    """Project the fake terrain through a pinhole at f35 / heading, write ridge.json with an assumed 26 mm focal."""
    f = f35 / 43.2666 * math.hypot(W, H)
    xs = np.arange(40, W - 40, 80, dtype=float)
    az = (heading + np.degrees(np.arctan((xs - W / 2) / f))) % 360
    ang, dist = terrain.cast(FakeDEM(), (LAT0, LON0), 1.6, az, 30000, near=150, n=600)
    row = lambda a: HROW - f * np.tan(np.radians(a))
    far = row(ang.max(axis=1))
    near_ang = ang[:, dist <= 9000].max(axis=1)
    near = row(near_ang)
    ridge = {"photo": "", "image_size": [W, H], "cx": W / 2, "ridge": [[int(x), int(round(y))] for x, y in zip(xs, far)],
             "flat": None, "hrow": HROW, "f0": 26 / 43.2666 * math.hypot(W, H), "f0_source": "assumed", "f35_equiv": 26.0,
             "near": [], "near_clear": []}
    if two_layer:
        stand = near_ang > 0.3                                       # columns where the near range stands up
        ridge["near"] = [[int(x), int(round(y))] for x, y, s in zip(xs, near, stand) if s]
        clear = xs[~stand & (xs > W / 2)]
        ridge["near_clear"] = [[int(clear.min()), int(clear.max()), float(row(0.25))]]
    path.write_text(json.dumps(ridge))


def fit(ridge: Path, out: Path, *extra: str) -> tuple[dict, str]:
    argv = ["terrain.py", "fit", "--at", f"{LAT0},{LON0}", "--radius", "0", "--ridge", str(ridge), "--out", str(out),
            "--range", "30000", "--min-peak", "2", "--nsamp", "400", *extra]
    err = io.StringIO()
    with patch.object(terrain, "DEM", FakeDEM), patch.object(sys, "argv", argv), contextlib.redirect_stderr(err):
        terrain.main()
    return json.loads(out.read_text()), err.getvalue()


class FocalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_assumed_focal_searches_wide_and_finds_telephoto(self):
        synth_ridge(self.d / "r.json", 60, 270, two_layer=False)
        res, _ = fit(self.d / "r.json", self.d / "f.json")
        best = res["cams"][0]
        self.assertGreater(len(res["params"]["f35_ladder"]), 10)
        self.assertLess(abs(math.log(best["f35"] / 60)), math.log(1.2))
        self.assertLess(abs((best["H"] - 270 + 180) % 360 - 180), 1.0)
        self.assertIsNone(res["focal_edge"])

    def test_main_camera_only_hits_long_edge_and_warns(self):
        synth_ridge(self.d / "r.json", 60, 270, two_layer=False)
        res, err = fit(self.d / "r.json", self.d / "f.json", "--focal-scales", "0.9,1,1.12")
        self.assertEqual(res["focal_edge"]["top1"], "long")
        self.assertIn("--f35-range", err)

    def test_widened_range_clears_the_edge(self):
        synth_ridge(self.d / "r.json", 60, 270, two_layer=False)
        res, _ = fit(self.d / "r.json", self.d / "f.json", "--f35-range", "20:40")
        self.assertEqual(res["focal_edge"]["top1"], "long")
        res, _ = fit(self.d / "r.json", self.d / "f.json", "--f35-range", "24:80")
        self.assertIsNone(res["focal_edge"])

    def test_two_layer_scores_near_points(self):
        synth_ridge(self.d / "r.json", 60, 270, two_layer=True)
        ridge = json.loads((self.d / "r.json").read_text())
        self.assertGreaterEqual(len(ridge["near"]), 3)
        res, _ = fit(self.d / "r.json", self.d / "f.json")
        best = res["cams"][0]
        self.assertIn("D1", best)
        self.assertLess(best["rms_near_px"], 6)
        self.assertLess(abs((best["H"] - 270 + 180) % 360 - 180), 1.0)

    def test_perp_line_restricts_heading(self):
        synth_ridge(self.d / "r.json", 60, 270, two_layer=False)
        line = {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {},
                "geometry": {"type": "LineString", "coordinates": [[LON0 + 0.003, LAT0 - 0.02], [LON0 + 0.003, LAT0 + 0.02]]}}]}
        (self.d / "l.geojson").write_text(json.dumps(line))
        res, _ = fit(self.d / "r.json", self.d / "f.json", "--perp-line", str(self.d / "l.geojson"), "--perp-tol", "10")
        self.assertLess(abs((res["cams"][0]["H"] - 270 + 180) % 360 - 180), 10.5)
        self.assertEqual(res["cams"][0]["line_brg"], 0.0)

    def _lines(self, parts):
        p = self.d / "l.geojson"
        p.write_text(json.dumps({"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": {}, "geometry": {"type": "LineString", "coordinates": c}} for c in parts]}))
        return str(p)

    def test_perp_line_distance_ignores_vertex_density(self):
        synth_ridge(self.d / "r.json", 60, 270, two_layer=False)
        lon = LON0 + 0.0005
        a, _ = fit(self.d / "r.json", self.d / "a.json", "--perp-line", self._lines([[[lon, LAT0 - 0.002], [lon, LAT0 + 0.04]]]))
        b, _ = fit(self.d / "r.json", self.d / "b.json", "--perp-line", self._lines([[[lon, LAT0 - 0.002], [lon, LAT0], [lon, LAT0 + 0.04]]]))
        self.assertEqual(a["n_cams"], 1)
        self.assertEqual(b["n_cams"], 1)

    def test_perp_line_picks_nearest_segment_not_nearest_midpoint(self):
        synth_ridge(self.d / "r.json", 60, 270, two_layer=False)
        lon = LON0 + 0.0005
        p = self._lines([[[lon, LAT0 - 0.0001], [lon, LAT0 + 0.005]], [[LON0 - 0.002, LAT0 + 0.001], [LON0 + 0.002, LAT0 + 0.001]]])
        res, _ = fit(self.d / "r.json", self.d / "f.json", "--perp-line", p, "--perp-tol", "10")
        self.assertEqual(res["cams"][0]["line_brg"], 0.0)

    def test_near_dist_within_sight_line_start_is_dropped_not_crash(self):
        synth_ridge(self.d / "r.json", 60, 270, two_layer=True)
        res, err = fit(self.d / "r.json", self.d / "f.json", "--near", "4000")
        self.assertEqual(res["n_cams"], 1)
        self.assertIn("dropped", err)
        with self.assertRaises(SystemExit):
            fit(self.d / "r.json", self.d / "f.json", "--near", "4000", "--near-dist", "3000")

    def test_every_rung_recovers_heading(self):
        for f35 in (13, 20, 26, 40, 90, 135):
            with self.subTest(f35=f35):
                synth_ridge(self.d / "r.json", f35, 270, two_layer=False)
                res, _ = fit(self.d / "r.json", self.d / "f.json")
                self.assertLess(abs((res["cams"][0]["H"] - 270 + 180) % 360 - 180), 2)


class RidgeTests(unittest.TestCase):
    def test_points_and_near_layer_written(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "p.jpg"
            Image.new("RGB", (400, 300), (120, 160, 200)).save(p)
            out = Path(t) / "r.json"
            with patch.object(sys, "argv", ["terrain.py", "ridge", str(p), "--points", "10,100;200,90;390,110",
                                            "--near", "10,140;100,150;180,160", "--near-clear", "250:390@170", "--out", str(out)]), \
                    contextlib.redirect_stdout(io.StringIO()):
                terrain.main()
            r = json.loads(out.read_text())
            self.assertEqual(r["ridge_source"], "points")
            self.assertEqual(r["ridge"], [[10, 100], [200, 90], [390, 110]])
            self.assertEqual(len(r["near"]), 3)
            self.assertEqual(r["near_clear"], [[250, 390, 170.0]])


if __name__ == "__main__":
    unittest.main()
