"""Exercise the installed public CLI with synthetic media and no provider calls."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    root = args.out.resolve()
    root.mkdir(parents=True, exist_ok=False)
    env = os.environ.copy()
    env.pop("OPENAI_API_KEY", None)
    env.update(TEMP=str(root), TMP=str(root), PYTHONDONTWRITEBYTECODE="1")
    calls = []

    def run(*parts):
        result = subprocess.run([sys.executable, "-m", "gif_cinema", *parts],
                                cwd=root, env=env, check=True,
                                text=True, capture_output=True, timeout=60)
        calls.append({"arguments": list(parts), "exit_code": result.returncode})
        return result.stdout

    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def payload(output):
        # Execution prints plan JSON, a creation line, then its final JSON receipt.
        objects = [json.JSONDecoder().raw_decode(output, match.start())[0]
                   for match in re.finditer(r"(?m)^\{", output)]
        if not objects:
            raise ValueError("CLI output did not include a JSON object")
        return objects[-1]

    sources = []
    for shot in range(2):
        frames = []
        for frame in range(4):
            im = Image.new("RGB", (64, 64), "#23324a")
            ImageDraw.Draw(im).ellipse((8 + frame * 3, 20, 24 + frame * 3, 36),
                                      fill=(240, 180 - shot * 50, 100))
            frames.append(im)
        path = root / f"shot-{shot}.gif"
        frames[0].save(path, save_all=True, append_images=frames[1:],
                       duration=160, loop=0)
        sources.append(path)
    before = [sha(p) for p in sources]
    inspections = [json.loads(run("inspect", str(p))) for p in sources]
    assert all(x["frames"] == 4 and x["duration_ms"] == 640 for x in inspections)
    run("endpoints", str(sources[0]), "-o", str(root / "edge"))
    assert (root / "edge-last.png").is_file()
    run("continuity", str(sources[0]), str(sources[1]), "-o", str(root / "join.json"))
    run("film", *(str(p) for p in sources), "-o", str(root / "film.mp4"),
        "--width", "64", "--height", "64", "--fps", "25")
    subprocess.run(["ffmpeg", "-v", "error", "-xerror", "-i", str(root / "film.mp4"),
                    "-f", "null", "-"], env=env, check=True, capture_output=True,
                   timeout=60)
    script = {"schema_version": 1, "title": "Synthetic offline verification",
              "ratio": "1:1", "width": 64, "height": 64, "fps": 25,
              "style_bible": "Simple synthetic dots; not generated artwork.",
              "shots": [{"id": f"shot-{i}", "source": p.name,
                         "first_frame_target": "Dot at left.",
                         "last_frame_target": "Dot moves right."}
                        for i, p in enumerate(sources)]}
    (root / "film.json").write_text(json.dumps(script), encoding="utf-8")
    plan = payload(run("render", str(root / "film.json"), "--dry-run"))
    assert plan["minimum_new_api_calls"] == 0
    reference_plan = {**script, "shots": [{"id": "next-shot",
        "prompt": "A simple dot moves right against the same plain background.",
        "first_frame_target": "Dot matches the reference endpoint.",
        "last_frame_target": "Dot has moved slightly right.", "frames": 4,
        "duration_ms": 160, "references": ["edge-last.png"]}]}
    (root / "references.json").write_text(json.dumps(reference_plan), encoding="utf-8")
    referenced = payload(run("render", str(root / "references.json"), "--dry-run"))
    assert referenced["minimum_new_api_calls"] == 1
    render_checked = bool(shutil.which("ffprobe"))
    if render_checked:
        for _ in range(2):
            receipt = payload(run("render", str(root / "film.json"), "--execute",
                                    "--max-api-calls", "0", "--out", str(root / "render")))
            assert receipt["api_calls"] == 0
        render_sha = sha(root / "render" / "film.mp4")
    else:
        render_sha = None
    assert before == [sha(p) for p in sources]
    receipt = {"status": "passed", "source": "synthetic", "provider_calls": 0,
               "inspection": inspections, "film_sha256": sha(root / "film.mp4"),
               "sources_unchanged": True, "render_and_resume_checked": render_checked,
               "render_sha256": render_sha, "plan": plan, "commands": calls,
               "reference_preflight_checked": True,
               "scope": "CLI offline behavior; no live generation or artistic acceptance."}
    (root / "verification.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps({k: receipt[k] for k in ("status", "provider_calls", "sources_unchanged",
                                             "render_and_resume_checked", "scope")}, indent=2))


if __name__ == "__main__":
    main()
