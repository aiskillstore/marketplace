#!/usr/bin/env python3
"""Self-contained smoke test for compose_panels.py; creates only synthetic temp assets."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import runpy
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw


HERE = Path(__file__).resolve().parent
COMPOSITOR = HERE / "compose_panels.py"
TEMPLATE_MANIFEST = HERE.parent / "templates/compositor-manifest.example.json"
PAGE_NATIVE_TEMPLATE = HERE.parent / "templates/page-native-lettering-manifest.example.json"
DEFAULT_FONTS = (
    Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
    Path("/System/Library/Fonts/STHeiti Medium.ttc"),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
    Path("C:/Windows/Fonts/msyh.ttc"),
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_panel(path: Path, size: tuple[int, int], color: str, accent: str, index: int) -> None:
    image = Image.new("RGB", size, color)
    draw = ImageDraw.Draw(image)
    margin = min(size) // 8
    draw.rounded_rectangle(
        (margin, margin, size[0] - margin, size[1] - margin),
        radius=margin // 2,
        fill=accent,
    )
    draw.ellipse(
        (size[0] // 2 - margin, size[1] // 2 - margin, size[0] // 2 + margin, size[1] // 2 + margin),
        fill="#fffdf7",
    )
    draw.text((margin, size[1] - margin), f"P{index}", fill="#20201e")
    image.save(path, format="PNG", compress_level=9)


def run(command: list[str], expected: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, check=False, text=True, capture_output=True)
    if result.returncode != expected:
        raise AssertionError(
            f"unexpected exit {result.returncode}, wanted {expected}\n"
            f"command: {' '.join(command)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def assert_manifest_rejected(
    manifest: object,
    path: Path,
    expected_message: str,
) -> None:
    write_json(path, manifest)
    result = run(
        [sys.executable, str(COMPOSITOR), "--manifest", str(path), "--dry-run"],
        expected=2,
    )
    if expected_message not in result.stderr:
        raise AssertionError(
            f"manifest rejection did not include {expected_message!r}: {result.stderr}"
        )


def choose_font(requested: str | None) -> Path:
    if requested:
        font = Path(requested).expanduser().resolve()
        if not font.is_file():
            raise AssertionError(f"requested font does not exist: {font}")
        return font
    for candidate in DEFAULT_FONTS:
        if candidate.is_file():
            return candidate
    raise AssertionError("no CJK font found; rerun with --font /path/to/CJK-font.ttf")


def make_manifest(font: Path, root: Path) -> dict[str, object]:
    panels = [
        {
            "id": "p1",
            "reading_order": 1,
            "row": 1,
            "column": 1,
            "source": "panels/01.png",
            "expected_sha256": digest(root / "panels/01.png"),
            "expected_size": [640, 360],
            "source_crop": [20, 50, 620, 310],
            "frame": [32, 32, 768, 350],
            "corner_radius": 18,
            "border": {"width": 4, "color": "#20201e"},
            "protected_action_regions": [
                {"id": "p1-main-action", "bbox": [72, 82, 382, 310]}
            ],
        },
        {
            "id": "p2",
            "reading_order": 2,
            "row": 2,
            "column": 1,
            "source": "panels/02.png",
            "expected_sha256": digest(root / "panels/02.png"),
            "expected_size": [420, 420],
            "source_crop": [30, 20, 390, 400],
            "frame": [32, 374, 350, 710],
            "corner_radius": 28,
            "border": {"width": 4, "color": "#20201e"},
            "protected_action_regions": [
                {"id": "p2-main-action", "bbox": [72, 414, 316, 676]}
            ],
        },
        {
            "id": "p3",
            "reading_order": 3,
            "row": 2,
            "column": 2,
            "source": "panels/03.png",
            "expected_sha256": digest(root / "panels/03.png"),
            "expected_size": [500, 420],
            "source_crop": [30, 20, 480, 400],
            "frame": [374, 374, 768, 710],
            "corner_radius": 10,
            "border": {"width": 4, "color": "#20201e"},
            "protected_action_regions": [
                {"id": "p3-main-action", "bbox": [424, 414, 726, 676]}
            ],
        },
        {
            "id": "p4",
            "reading_order": 4,
            "row": 3,
            "column": 1,
            "source": "panels/04.png",
            "expected_sha256": digest(root / "panels/04.png"),
            "expected_size": [640, 360],
            "source_crop": [10, 39, 630, 321],
            "frame": [32, 734, 768, 1068],
            "corner_radius": 22,
            "border": {"width": 4, "color": "#20201e"},
            "protected_action_regions": [
                {"id": "p4-main-action", "bbox": [350, 786, 718, 1030]}
            ],
        },
    ]
    return {
        "schema_version": 1,
        "artifact_stages": {
            "panel_inputs": "unlettered-panel",
            "composition": "unlettered-page",
        },
        "canvas": {"size": [800, 1100], "background": "#f4efe6"},
        "lettering": {
            "font_candidates": ["/System/Library/Fonts/Helvetica.ttc", str(font)],
            "face_index": 0,
            "color": "#20201e",
        },
        "panels": panels,
        "bubbles": [
            {
                "id": "p1-dialogue",
                "panel": "p1",
                "reading_order": 1,
                "speaker": "protagonist",
                "speaker_anchor": [400, 220],
                "shape": "ellipse",
                "bbox": [420, 68, 724, 202],
                "safe_region": [400, 52, 744, 270],
                "tail": [[500, 165], [460, 248], [570, 185]],
                "fill": "#fffdf7",
                "stroke": "#20201e",
                "stroke_width": 3,
                "text": {
                    "language": "zh-Hans",
                    "exact": "先做关键格。",
                    "lines": ["先做关键格。"],
                    "bbox": [445, 92, 699, 174],
                    "font_size": 32,
                    "line_gap": 4,
                    "align": "center",
                },
            },
            {
                "id": "p4-silent-bubble",
                "panel": "p4",
                "reading_order": 2,
                "speaker": "narrator",
                "speaker_anchor": [400, 850],
                "shape": "rounded_rect",
                "bbox": [78, 774, 310, 874],
                "safe_region": [60, 750, 330, 900],
                "corner_radius": 22,
                "tail": [],
                "fill": "#fffdf7",
                "stroke": "#20201e",
                "stroke_width": 3,
            },
        ],
        "output": {
            "stage": "lettered-final",
            "unlettered_image": "out/page.unlettered.png",
            "image": "out/page.png",
            "ledger": "out/page.ledger.json",
        },
    }


def make_v2_manifest(font: Path, root: Path) -> dict[str, object]:
    manifest = copy.deepcopy(make_manifest(font, root))
    manifest["schema_version"] = 2
    manifest["canvas"]["paper_matte"] = {  # type: ignore[index]
        "enabled": True,
        "seed": 20260810,
        "grain_strength": 4,
        "tile_size": 96,
    }
    panels = manifest["panels"]  # type: ignore[assignment]
    for z_index, panel in enumerate(panels):  # type: ignore[arg-type]
        panel["z_index"] = z_index * 10
        panel["rotation_degrees"] = 0
        panel["allow_overlap_with"] = []

    p2 = panels[1]  # type: ignore[index]
    p2["source_crop"] = [20, 40, 400, 397]
    p2["frame"] = [32, 374, 390, 710]
    p2.pop("corner_radius")
    p2["clip_polygon"] = [[32, 386], [390, 374], [382, 710], [40, 700]]
    p2["rotation_degrees"] = 2
    p2["z_index"] = 10
    p2["allow_overlap_with"] = ["p3"]
    p2["protected_action_regions"] = [
        {"id": "p2-main-action", "bbox": [72, 520, 300, 660]}
    ]

    p3 = panels[2]  # type: ignore[index]
    p3["source_crop"] = [22, 20, 477, 400]
    p3["frame"] = [366, 374, 768, 710]
    p3["z_index"] = 20
    p3["allow_overlap_with"] = ["p2"]

    bubbles = manifest["bubbles"]  # type: ignore[assignment]
    bubbles[1]["reading_order"] = 3  # type: ignore[index]
    bubbles.insert(  # type: ignore[union-attr]
        1,
        {
            "id": "p2-silent-bubble",
            "panel": "p2",
            "reading_order": 2,
            "speaker": "protagonist",
            "speaker_anchor": [210, 500],
            "shape": "rounded_rect",
            "bbox": [112, 420, 238, 466],
            "safe_region": [100, 410, 250, 480],
            "corner_radius": 16,
            "tail": [],
            "fill": "#fffdf7",
            "stroke": "#20201e",
            "stroke_width": 3,
        },
    )
    manifest["output"] = {
        "stage": "lettered-final",
        "unlettered_image": "out/page-v2.unlettered.png",
        "image": "out/page-v2.png",
        "ledger": "out/page-v2.ledger.json",
    }
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--font", help="CJK font override")
    args = parser.parse_args()
    font = choose_font(args.font)

    with tempfile.TemporaryDirectory(prefix="comic-compositor-test-") as temporary:
        root = Path(temporary)
        (root / "panels").mkdir()
        (root / "out").mkdir()
        make_panel(root / "panels/01.png", (640, 360), "#dce8de", "#739b80", 1)
        make_panel(root / "panels/02.png", (420, 420), "#eadccf", "#b67d57", 2)
        make_panel(root / "panels/03.png", (500, 420), "#d9e3ef", "#587aa2", 3)
        make_panel(root / "panels/04.png", (640, 360), "#eadfeb", "#8a688b", 4)

        manifest = make_manifest(font, root)
        manifest_path = root / "manifest.json"
        write_json(manifest_path, manifest)
        base_command = [sys.executable, str(COMPOSITOR), "--manifest", str(manifest_path)]

        dry_run = run(base_command + ["--dry-run"])
        if "panels=4" not in dry_run.stdout or "zh-Hans_blocks=1" not in dry_run.stdout:
            raise AssertionError(f"unexpected dry-run summary: {dry_run.stdout}")
        if (root / "out/page.png").exists():
            raise AssertionError("dry-run wrote an output image")

        run(base_command)
        output = root / "out/page.png"
        unlettered = root / "out/page.unlettered.png"
        ledger = root / "out/page.ledger.json"
        if not unlettered.is_file():
            raise AssertionError("lettered run did not retain the unlettered-page artifact")
        with Image.open(output) as image:
            if image.size != (800, 1100) or image.mode != "RGB":
                raise AssertionError(f"unexpected output geometry: {image.mode} {image.size}")
        first_image_hash = digest(output)
        first_ledger_hash = digest(ledger)
        ledger_data = json.loads(ledger.read_text(encoding="utf-8"))
        if [item["stage"] for item in ledger_data["artifacts"]] != ["unlettered-page", "lettered-final"]:
            raise AssertionError(f"artifact stages were not preserved: {ledger_data['artifacts']}")
        runtime = ledger_data.get("runtime", {})
        if not all(runtime.get(key) for key in ("python_version", "python_implementation", "platform", "pillow_version")):
            raise AssertionError(f"runtime versions were not recorded: {runtime}")
        if not runtime.get("raster_libraries", {}).get("freetype2"):
            raise AssertionError(f"FreeType version was not recorded: {runtime}")

        snapshot_font = root / "font-snapshot.ttc"
        snapshot_font_bytes = font.read_bytes()
        snapshot_font.write_bytes(snapshot_font_bytes)
        snapshot_manifest = make_manifest(snapshot_font, root)
        snapshot_manifest["lettering"]["font_candidates"] = [str(snapshot_font)]  # type: ignore[index]
        snapshot_manifest_path = root / "snapshot-font-manifest.json"
        write_json(snapshot_manifest_path, snapshot_manifest)
        compositor_module = runpy.run_path(str(COMPOSITOR), run_name="compositor_snapshot_test")
        polygons_overlap = compositor_module["polygons_overlap"]
        rectangle = ((0.0, 0.0), (20.0, 0.0), (20.0, 20.0), (0.0, 20.0))
        adjacent = ((20.0, 0.0), (40.0, 0.0), (40.0, 20.0), (20.0, 20.0))
        concave = ((0.0, 0.0), (20.0, 0.0), (20.0, 8.0), (8.0, 8.0), (8.0, 20.0), (0.0, 20.0))
        if not polygons_overlap(rectangle, rectangle) or not polygons_overlap(concave, concave):
            raise AssertionError("coincident polygon footprints were not detected as overlaps")
        if polygons_overlap(rectangle, adjacent):
            raise AssertionError("edge-touching polygon footprints were misclassified as overlaps")
        atomic_target = root / "out/atomic-race.png"
        atomic_target.write_bytes(b"appeared after preflight")
        try:
            compositor_module["atomic_save_png"](
                Image.new("RGB", (8, 8), "#cc3344"),
                atomic_target,
                False,
            )
        except compositor_module["ManifestError"] as error:
            if "refusing to overwrite existing output" not in str(error):
                raise AssertionError(f"atomic no-clobber error was not actionable: {error}")
        else:
            raise AssertionError("atomic no-clobber commit overwrote a late-arriving output")
        if atomic_target.read_bytes() != b"appeared after preflight":
            raise AssertionError("atomic no-clobber commit changed a late-arriving output")
        compositor_module["atomic_save_png"](
            Image.new("RGB", (8, 8), "#cc3344"),
            atomic_target,
            True,
        )
        with Image.open(atomic_target) as atomic_image:
            if atomic_image.size != (8, 8):
                raise AssertionError("atomic force commit did not replace the target PNG")
        atomic_target.unlink()
        validated_snapshot = compositor_module["validate_manifest"](
            snapshot_manifest_path,
            None,
            None,
            None,
        )
        expected_font_sha256 = hashlib.sha256(snapshot_font_bytes).hexdigest()
        snapshot_font.write_bytes(b"replaced after validation")
        snapshot_font.unlink()
        _, snapshot_final, snapshot_ledger = compositor_module["compose"](validated_snapshot)
        if snapshot_ledger["font"]["sha256"] != expected_font_sha256:
            raise AssertionError(f"font ledger hash did not use frozen bytes: {snapshot_ledger['font']}")
        if snapshot_ledger["font"]["snapshot_bytes"] != len(snapshot_font_bytes):
            raise AssertionError(f"font snapshot length drifted: {snapshot_ledger['font']}")
        with Image.open(output) as rendered_output:
            if snapshot_final.tobytes() != rendered_output.convert("RGB").tobytes():
                raise AssertionError("font source replacement changed rendering after validation")

        protected = run(base_command, expected=2)
        if "refusing to overwrite" not in protected.stderr:
            raise AssertionError(f"existing-output error was not actionable: {protected.stderr}")

        run(base_command + ["--force"])
        if digest(output) != first_image_hash:
            raise AssertionError("repeat render was not pixel-file deterministic")
        if digest(ledger) != first_ledger_hash:
            raise AssertionError("repeat ledger was not byte deterministic")

        bad_manifest = copy.deepcopy(manifest)
        bad_manifest["panels"][0]["expected_size"] = [641, 360]  # type: ignore[index]
        bad_path = root / "bad-manifest.json"
        write_json(bad_path, bad_manifest)
        invalid = run(
            [sys.executable, str(COMPOSITOR), "--manifest", str(bad_path), "--dry-run"],
            expected=2,
        )
        if "expected_size mismatch" not in invalid.stderr:
            raise AssertionError(f"invalid-size error was not actionable: {invalid.stderr}")

        missing_manifest = copy.deepcopy(manifest)
        missing_manifest["panels"][2]["source"] = "panels/missing.png"  # type: ignore[index]
        missing_path = root / "missing-manifest.json"
        write_json(missing_path, missing_manifest)
        missing = run(
            [sys.executable, str(COMPOSITOR), "--manifest", str(missing_path), "--dry-run"],
            expected=2,
        )
        if "does not exist or is not a file" not in missing.stderr:
            raise AssertionError(f"missing-path error was not actionable: {missing.stderr}")

        collision_manifest = copy.deepcopy(manifest)
        collision_manifest["panels"][0]["protected_action_regions"] = [  # type: ignore[index]
            {"id": "p1-bubble-collision", "bbox": [600, 100, 700, 180]}
        ]
        collision_path = root / "collision-manifest.json"
        write_json(collision_path, collision_manifest)
        collision = run(
            [sys.executable, str(COMPOSITOR), "--manifest", str(collision_path), "--dry-run"],
            expected=2,
        )
        if "intersects protected action region" not in collision.stderr:
            raise AssertionError(f"protected-action error was not actionable: {collision.stderr}")

        overflow_manifest = copy.deepcopy(manifest)
        overflow_manifest["bubbles"][0]["text"]["font_size"] = 400  # type: ignore[index]
        overflow_path = root / "overflow-manifest.json"
        write_json(overflow_path, overflow_manifest)
        overflow = run(
            [sys.executable, str(COMPOSITOR), "--manifest", str(overflow_path), "--dry-run"],
            expected=2,
        )
        if "font_size may not exceed" not in overflow.stderr:
            raise AssertionError(f"dry-run text overflow error was not actionable: {overflow.stderr}")

        exact_control_manifest = copy.deepcopy(manifest)
        exact_control_manifest["bubbles"][0]["text"]["exact"] = "先做\n关键格。"  # type: ignore[index]
        exact_control_manifest["bubbles"][0]["text"]["lines"] = ["先做\n关键格。"]  # type: ignore[index]
        exact_control_path = root / "exact-control-manifest.json"
        write_json(exact_control_path, exact_control_manifest)
        exact_control = run(
            [sys.executable, str(COMPOSITOR), "--manifest", str(exact_control_path), "--dry-run"],
            expected=2,
        )
        if "text.exact contains forbidden control or line-break" not in exact_control.stderr:
            raise AssertionError(f"exact control-character error was not actionable: {exact_control.stderr}")

        line_control_manifest = copy.deepcopy(manifest)
        line_control_manifest["bubbles"][0]["text"]["lines"] = ["先做\t关键格。"]  # type: ignore[index]
        line_control_path = root / "line-control-manifest.json"
        write_json(line_control_path, line_control_manifest)
        line_control = run(
            [sys.executable, str(COMPOSITOR), "--manifest", str(line_control_path), "--dry-run"],
            expected=2,
        )
        if "text.lines[0] contains forbidden control or line-break" not in line_control.stderr:
            raise AssertionError(f"line control-character error was not actionable: {line_control.stderr}")

        normal_space_manifest = copy.deepcopy(manifest)
        normal_space_manifest["bubbles"][0]["text"]["exact"] = "先做 关键格。"  # type: ignore[index]
        normal_space_manifest["bubbles"][0]["text"]["lines"] = ["先做 关键格。"]  # type: ignore[index]
        normal_space_path = root / "normal-space-manifest.json"
        write_json(normal_space_path, normal_space_manifest)
        run(
            [sys.executable, str(COMPOSITOR), "--manifest", str(normal_space_path), "--dry-run"],
        )

        plain_manifest = copy.deepcopy(manifest)
        plain_manifest.pop("lettering")
        plain_manifest["bubbles"] = []
        plain_manifest["output"] = {
            "stage": "unlettered-page",
            "image": "out/plain-page.png",
            "ledger": "out/plain-page.ledger.json",
        }
        plain_path = root / "plain-manifest.json"
        write_json(plain_path, plain_manifest)
        plain_command = [sys.executable, str(COMPOSITOR), "--manifest", str(plain_path)]
        plain_dry_run = run(plain_command + ["--dry-run"])
        if "bubbles=0" not in plain_dry_run.stdout or "zh-Hans_blocks=0" not in plain_dry_run.stdout:
            raise AssertionError(f"unexpected no-lettering dry-run summary: {plain_dry_run.stdout}")
        run(plain_command)
        if not (root / "out/plain-page.png").is_file():
            raise AssertionError("no-lettering composition did not write its fixed output")

        v2_manifest = make_v2_manifest(font, root)
        v2_path = root / "manifest-v2.json"
        write_json(v2_path, v2_manifest)
        v2_command = [sys.executable, str(COMPOSITOR), "--manifest", str(v2_path)]
        v2_dry_run = run(v2_command + ["--dry-run"])
        if "panels=4" not in v2_dry_run.stdout or "bubbles=3" not in v2_dry_run.stdout:
            raise AssertionError(f"unexpected v2 dry-run summary: {v2_dry_run.stdout}")
        run(v2_command)
        v2_output = root / "out/page-v2.png"
        v2_ledger_path = root / "out/page-v2.ledger.json"
        v2_output_hash = digest(v2_output)
        v2_ledger_hash = digest(v2_ledger_path)
        v2_ledger = json.loads(v2_ledger_path.read_text(encoding="utf-8"))
        if v2_ledger["schema_version"] != 2 or v2_ledger["compositor_version"] != "2.1.0":
            raise AssertionError(f"v2 version metadata drifted: {v2_ledger}")
        if v2_ledger["paper_matte"] != {
            "algorithm": "tiled-lcg-luminance-v1",
            "grain_strength": 4,
            "seed": 20260810,
            "tile_size": 96,
        }:
            raise AssertionError(f"paper matte was not recorded exactly: {v2_ledger['paper_matte']}")
        v2_p2 = next(panel for panel in v2_ledger["panels"] if panel["id"] == "p2")
        v2_p3 = next(panel for panel in v2_ledger["panels"] if panel["id"] == "p3")
        if (
            v2_p2["clip_polygon"] is None
            or v2_p2["rotation_degrees"] != 2.0
            or v2_p2["z_index"] != 10
            or v2_p3["z_index"] != 20
            or v2_p2["render_order"] >= v2_p3["render_order"]
        ):
            raise AssertionError(f"v2 panel geometry was not preserved: {v2_ledger['panels']}")
        run(v2_command + ["--force"])
        if digest(v2_output) != v2_output_hash or digest(v2_ledger_path) != v2_ledger_hash:
            raise AssertionError("v2 paper/polygon/rotation render was not byte deterministic")

        orientation_source = root / "panels/orientation.png"
        orientation_image = Image.new("RGB", (100, 100), "#fffdf7")
        ImageDraw.Draw(orientation_image).rectangle((45, 5, 55, 20), fill="#e02020")
        orientation_image.save(orientation_source, format="PNG", compress_level=9)
        orientation_manifest = {
            "schema_version": 2,
            "artifact_stages": {
                "panel_inputs": "unlettered-panel",
                "composition": "unlettered-page",
            },
            "canvas": {"size": [400, 400], "background": "#d8d8d8"},
            "panels": [
                {
                    "id": "orientation",
                    "reading_order": 1,
                    "row": 1,
                    "column": 1,
                    "source": "panels/orientation.png",
                    "expected_sha256": digest(orientation_source),
                    "expected_size": [100, 100],
                    "source_crop": [0, 0, 100, 100],
                    "frame": [100, 100, 300, 300],
                    "rotation_degrees": 10,
                    "z_index": 0,
                    "allow_overlap_with": [],
                    "border": {"width": 0, "color": "#20201e"},
                    "protected_action_regions": [],
                }
            ],
            "bubbles": [],
            "output": {
                "stage": "unlettered-page",
                "image": "out/orientation.png",
                "ledger": "out/orientation.ledger.json",
            },
        }
        orientation_path = root / "orientation-manifest.json"
        write_json(orientation_path, orientation_manifest)
        run([sys.executable, str(COMPOSITOR), "--manifest", str(orientation_path)])
        with Image.open(root / "out/orientation.png") as orientation_output:
            red_pixels = [
                (x, y)
                for y in range(orientation_output.height)
                for x in range(orientation_output.width)
                if (
                    orientation_output.getpixel((x, y))[0] > 180
                    and orientation_output.getpixel((x, y))[1] < 90
                    and orientation_output.getpixel((x, y))[2] < 90
                )
            ]
        if not red_pixels:
            raise AssertionError("clockwise-orientation probe lost its asymmetric marker")
        red_center = (
            sum(point[0] for point in red_pixels) / len(red_pixels),
            sum(point[1] for point in red_pixels) / len(red_pixels),
        )
        if not red_center[0] > 205 or not red_center[1] < 150:
            raise AssertionError(
                f"positive rotation did not move the top marker clockwise: centroid={red_center}"
            )

        validated_v2 = compositor_module["validate_manifest"](v2_path, None, None, None)
        frozen_source_path = root / "panels/02.png"
        frozen_source_bytes = frozen_source_path.read_bytes()
        frozen_source_hash = hashlib.sha256(frozen_source_bytes).hexdigest()
        frozen_source_path.write_bytes(b"replaced after validation")
        frozen_source_path.unlink()
        _, frozen_v2_final, frozen_v2_ledger = compositor_module["compose"](validated_v2)
        frozen_source_path.write_bytes(frozen_source_bytes)
        if frozen_v2_ledger["panels"][1]["source_sha256"] != frozen_source_hash:
            raise AssertionError("v2 source ledger did not use the frozen source bytes")
        with Image.open(v2_output) as rendered_v2_output:
            if frozen_v2_final.tobytes() != rendered_v2_output.convert("RGB").tobytes():
                raise AssertionError("source replacement changed v2 rendering after validation")

        unauthorized_overlap = copy.deepcopy(v2_manifest)
        unauthorized_overlap["panels"][2]["allow_overlap_with"] = []  # type: ignore[index]
        unauthorized_path = root / "v2-unauthorized-overlap.json"
        write_json(unauthorized_path, unauthorized_overlap)
        unauthorized = run(
            [sys.executable, str(COMPOSITOR), "--manifest", str(unauthorized_path), "--dry-run"],
            expected=2,
        )
        if "without mutual allow_overlap_with" not in unauthorized.stderr:
            raise AssertionError(f"unauthorized overlap was not rejected: {unauthorized.stderr}")

        same_z = copy.deepcopy(v2_manifest)
        same_z["panels"][2]["z_index"] = 10  # type: ignore[index]
        same_z_path = root / "v2-same-z.json"
        write_json(same_z_path, same_z)
        same_z_result = run(
            [sys.executable, str(COMPOSITOR), "--manifest", str(same_z_path), "--dry-run"],
            expected=2,
        )
        if "must have different z_index" not in same_z_result.stderr:
            raise AssertionError(f"same-z overlap was not rejected: {same_z_result.stderr}")

        protected_overlap = copy.deepcopy(v2_manifest)
        protected_overlap["panels"][1]["protected_action_regions"] = [  # type: ignore[index]
            {"id": "p2-overlap-proof", "bbox": [368, 500, 382, 540]}
        ]
        protected_overlap_path = root / "v2-protected-overlap.json"
        write_json(protected_overlap_path, protected_overlap)
        protected_overlap_result = run(
            [
                sys.executable,
                str(COMPOSITOR),
                "--manifest",
                str(protected_overlap_path),
                "--dry-run",
            ],
            expected=2,
        )
        if "overlaps protected action region" not in protected_overlap_result.stderr:
            raise AssertionError(
                f"upper-panel protected overlap was not rejected: {protected_overlap_result.stderr}"
            )

        covered_bubble = copy.deepcopy(v2_manifest)
        covered_bubble["bubbles"][1]["speaker_anchor"] = [340, 500]  # type: ignore[index]
        covered_bubble["bubbles"][1]["bbox"] = [355, 445, 375, 495]  # type: ignore[index]
        covered_bubble["bubbles"][1]["safe_region"] = [350, 440, 380, 500]  # type: ignore[index]
        covered_bubble["bubbles"][1]["corner_radius"] = 8  # type: ignore[index]
        covered_bubble_path = root / "v2-covered-bubble.json"
        write_json(covered_bubble_path, covered_bubble)
        covered_bubble_result = run(
            [
                sys.executable,
                str(COMPOSITOR),
                "--manifest",
                str(covered_bubble_path),
                "--dry-run",
            ],
            expected=2,
        )
        if "safe_region is covered by higher-z panel" not in covered_bubble_result.stderr:
            raise AssertionError(
                f"higher-z bubble coverage was not rejected: {covered_bubble_result.stderr}"
            )

        overlapping_bubbles = copy.deepcopy(v2_manifest)
        duplicate_bubble = copy.deepcopy(overlapping_bubbles["bubbles"][0])  # type: ignore[index]
        duplicate_bubble["id"] = "p1-dialogue-duplicate"
        duplicate_bubble["reading_order"] = 4
        overlapping_bubbles["bubbles"].append(duplicate_bubble)  # type: ignore[index]
        overlapping_bubbles_path = root / "v2-overlapping-bubbles.json"
        write_json(overlapping_bubbles_path, overlapping_bubbles)
        overlapping_bubbles_result = run(
            [
                sys.executable,
                str(COMPOSITOR),
                "--manifest",
                str(overlapping_bubbles_path),
                "--dry-run",
            ],
            expected=2,
        )
        if "bubble visual bounds overlap without mutual allow_overlap_with" not in overlapping_bubbles_result.stderr:
            raise AssertionError(
                f"uncontrolled bubble overlap was not rejected: {overlapping_bubbles_result.stderr}"
            )

        covered_text = copy.deepcopy(overlapping_bubbles)
        covered_text["bubbles"][0]["allow_overlap_with"] = ["p1-dialogue-duplicate"]  # type: ignore[index]
        covered_text["bubbles"][3]["allow_overlap_with"] = ["p1-dialogue"]  # type: ignore[index]
        covered_text_path = root / "v2-covered-text.json"
        write_json(covered_text_path, covered_text)
        covered_text_result = run(
            [sys.executable, str(COMPOSITOR), "--manifest", str(covered_text_path), "--dry-run"],
            expected=2,
        )
        if "text coverage cannot be allowed" not in covered_text_result.stderr:
            raise AssertionError(f"locked text coverage was not rejected: {covered_text_result.stderr}")

        self_intersection = copy.deepcopy(v2_manifest)
        self_intersection["panels"][1]["clip_polygon"] = [  # type: ignore[index]
            [32, 374],
            [390, 710],
            [390, 374],
            [32, 650],
        ]
        self_intersection_path = root / "v2-self-intersection.json"
        write_json(self_intersection_path, self_intersection)
        self_intersection_result = run(
            [
                sys.executable,
                str(COMPOSITOR),
                "--manifest",
                str(self_intersection_path),
                "--dry-run",
            ],
            expected=2,
        )
        if "simple non-self-intersecting polygon" not in self_intersection_result.stderr:
            raise AssertionError(
                f"self-intersecting polygon was not rejected: {self_intersection_result.stderr}"
            )

        v1_with_v2_field = copy.deepcopy(manifest)
        v1_with_v2_field["panels"][0]["z_index"] = 0  # type: ignore[index]
        v1_with_v2_field_path = root / "v1-with-v2-field.json"
        write_json(v1_with_v2_field_path, v1_with_v2_field)
        v1_with_v2_field_result = run(
            [
                sys.executable,
                str(COMPOSITOR),
                "--manifest",
                str(v1_with_v2_field_path),
                "--dry-run",
            ],
            expected=2,
        )
        if "v2 geometry fields require schema_version 2" not in v1_with_v2_field_result.stderr:
            raise AssertionError(f"v1 accepted a v2 panel field: {v1_with_v2_field_result.stderr}")

        unknown_manifest_key = copy.deepcopy(v2_manifest)
        unknown_manifest_key["metdata"] = {"note": "typo must not be ignored"}
        assert_manifest_rejected(
            unknown_manifest_key,
            root / "unknown-manifest-key.json",
            "manifest contains unknown field: 'metdata'",
        )

        unknown_canvas_key = copy.deepcopy(v2_manifest)
        unknown_canvas_key["canvas"]["paper_matt"] = {}  # type: ignore[index]
        assert_manifest_rejected(
            unknown_canvas_key,
            root / "unknown-canvas-key.json",
            "canvas contains unknown field: 'paper_matt'",
        )

        misspelled_rotation = copy.deepcopy(v2_manifest)
        misspelled_rotation["panels"][1]["rotation_degree"] = 2  # type: ignore[index]
        assert_manifest_rejected(
            misspelled_rotation,
            root / "misspelled-rotation.json",
            "panels[1] contains unknown field: 'rotation_degree'",
        )

        misspelled_polygon = copy.deepcopy(v2_manifest)
        misspelled_polygon["panels"][1]["clip_polgyon"] = [  # type: ignore[index]
            [32, 386],
            [390, 374],
            [382, 710],
            [40, 700],
        ]
        assert_manifest_rejected(
            misspelled_polygon,
            root / "misspelled-polygon.json",
            "panels[1] contains unknown field: 'clip_polgyon'",
        )

        unknown_bubble_key = copy.deepcopy(v2_manifest)
        unknown_bubble_key["bubbles"][0]["speaker_achor"] = [400, 220]  # type: ignore[index]
        assert_manifest_rejected(
            unknown_bubble_key,
            root / "unknown-bubble-key.json",
            "bubbles[0] contains unknown field: 'speaker_achor'",
        )

        unknown_text_key = copy.deepcopy(v2_manifest)
        unknown_text_key["bubbles"][0]["text"]["font_sze"] = 32  # type: ignore[index]
        assert_manifest_rejected(
            unknown_text_key,
            root / "unknown-text-key.json",
            "bubbles[0].text contains unknown field: 'font_sze'",
        )

        (root / "pages").mkdir()
        (root / "build").mkdir()
        page_source = root / "pages/page-native.png"
        make_panel(page_source, (1200, 1600), "#eee8dc", "#a57a56", 1)
        page_native_manifest = json.loads(PAGE_NATIVE_TEMPLATE.read_text(encoding="utf-8"))
        page_native_manifest["panels"][0]["source"] = "pages/page-native.png"
        page_native_manifest["panels"][0]["expected_sha256"] = digest(page_source)
        page_native_manifest["lettering"]["font_candidates"] = [str(font)]
        page_native_path = root / "page-native-manifest.json"
        write_json(page_native_path, page_native_manifest)
        page_native_command = [
            sys.executable,
            str(COMPOSITOR),
            "--manifest",
            str(page_native_path),
        ]
        page_native_dry_run = run(page_native_command + ["--dry-run"])
        if "panels=1" not in page_native_dry_run.stdout or "bubbles=1" not in page_native_dry_run.stdout:
            raise AssertionError(f"page-native lettering template did not validate: {page_native_dry_run.stdout}")
        run(page_native_command)
        page_native_unlettered = root / "build/page-native.unlettered.png"
        page_native_final = root / "build/page-native.final.png"
        page_native_ledger = json.loads((root / "build/page-native.ledger.json").read_text(encoding="utf-8"))
        with Image.open(page_source) as source_image, Image.open(page_native_unlettered) as copied_image:
            if source_image.convert("RGB").tobytes() != copied_image.convert("RGB").tobytes():
                raise AssertionError("page-native lettering changed the accepted unlettered page pixels")
        if page_native_ledger["input_stage"] != "page-native-unlettered":
            raise AssertionError(f"page-native input stage was not recorded: {page_native_ledger}")
        if page_native_ledger["bubbles"][0]["tail_style"] != "soft-rounded":
            raise AssertionError(f"soft-rounded tail style was not recorded: {page_native_ledger['bubbles']}")
        if not page_native_final.is_file():
            raise AssertionError("page-native lettering did not write the final artifact")

        detached_tail = copy.deepcopy(page_native_manifest)
        detached_tail["bubbles"][0]["tail"]["points"] = [  # type: ignore[index]
            [700, 270],
            [690, 320],
            [760, 290],
        ]
        detached_tail["bubbles"][0]["tail"]["tip_trim"] = 16  # type: ignore[index]
        assert_manifest_rejected(
            detached_tail,
            root / "page-native-detached-tail.json",
            "soft-rounded order must be",
        )

        needle_tail = copy.deepcopy(page_native_manifest)
        needle_tail["bubbles"][0]["tail"]["tip_trim"] = 2  # type: ignore[index]
        assert_manifest_rejected(
            needle_tail,
            root / "page-native-needle-tail.json",
            "tip_trim must be between",
        )

        split_page_native = copy.deepcopy(page_native_manifest)
        duplicate_page = copy.deepcopy(split_page_native["panels"][0])  # type: ignore[index]
        duplicate_page["id"] = "page-base-duplicate"
        duplicate_page["reading_order"] = 2
        duplicate_page["column"] = 2
        split_page_native["panels"].append(duplicate_page)  # type: ignore[index]
        assert_manifest_rejected(
            split_page_native,
            root / "page-native-split-source.json",
            "page-native lettering requires exactly one full-canvas source",
        )

        template_manifest = json.loads(TEMPLATE_MANIFEST.read_text(encoding="utf-8"))
        template_sizes = [(1536, 1024), (1024, 1024), (1024, 1024), (1536, 1024)]
        template_colors = [
            ("#e5dfd1", "#8d7c62"),
            ("#e4d9cf", "#a16f53"),
            ("#d8e0e8", "#627d98"),
            ("#e4dce8", "#7f688c"),
        ]
        for index, (size, colors) in enumerate(zip(template_sizes, template_colors), start=1):
            source_path = root / f"panels/template-{index:02d}.png"
            make_panel(source_path, size, colors[0], colors[1], index)
            panel = template_manifest["panels"][index - 1]
            panel["source"] = f"panels/template-{index:02d}.png"
            panel["expected_sha256"] = digest(source_path)
        template_manifest["lettering"]["font_candidates"] = [str(font)]
        template_manifest["output"] = {
            "stage": "lettered-final",
            "unlettered_image": "out/template.unlettered.png",
            "image": "out/template.png",
            "ledger": "out/template.ledger.json",
        }
        template_path = root / "template-filled.json"
        write_json(template_path, template_manifest)
        template_result = run(
            [sys.executable, str(COMPOSITOR), "--manifest", str(template_path), "--dry-run"]
        )
        if "panels=4" not in template_result.stdout:
            raise AssertionError(f"filled public template did not validate: {template_result.stdout}")

        print(
            "PASS compositor self-test: "
            f"dry-run, 4-panel irregular layout, zh-Hans bubble, silent bubble, "
            f"staged unlettered artifact, no-bubble mode, protected-action rejection, "
            f"repeat determinism, overwrite protection, bad-size rejection, missing-path rejection, "
            f"dry-run text overflow rejection, inline-control rejection, normal-space acceptance, "
            f"frozen-font/source replacement safety, atomic no-clobber commit, "
            f"v2 polygon/clockwise-rotation/z-order/controlled-overlap, "
            f"protected/bubble/text-overlap and self-intersection rejection, template validation, "
            f"page-native pixel-preserving lettering, closed soft-rounded tails, "
            f"fail-closed unknown-key rejection, and deterministic paper matte; "
            f"v1_output_sha256={first_image_hash} "
            f"v2_output_sha256={v2_output_hash}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
