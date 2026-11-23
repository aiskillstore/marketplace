"""Render an isolated Jianying work preview with a compatible installed engine."""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


def directory(value):
    path = Path(value).resolve(strict=True)
    if not path.is_dir():
        raise ValueError(f"Expected a directory: {path}")
    return path


def material_lookup(doc):
    result = {}
    for key, group in doc["materials"].items():
        if not isinstance(group, list):
            continue
        seen = {}
        clean = []
        for item in group:
            identifier = item.get("id") if isinstance(item, dict) else None
            if identifier and identifier in seen:
                if seen[identifier] != item:
                    raise ValueError(f"Conflicting material {identifier} in {key}")
                continue
            if identifier:
                seen[identifier] = item
                result[identifier] = item
            clean.append(item)
        doc["materials"][key] = clean
    return result


def check_media(doc):
    lookup = material_lookup(doc)
    for track in doc["tracks"]:
        if track.get("type") not in ("video", "audio"):
            continue
        for segment in track["segments"]:
            material = lookup[segment["material_id"]]
            value = material.get("path")
            if value and not Path(value).is_file():
                raise ValueError(f"Active media cannot be read: {value}")


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def fingerprint(path):
    path = Path(path)
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def input_files(doc, copy_root=None):
    lookup = material_lookup(doc)
    paths = set()
    complete = True
    def references(value):
        if isinstance(value, dict):
            return set().union(*(references(v) for k,v in value.items() if k != 'draft'))
        if isinstance(value, list):
            return set().union(*(references(v) for v in value))
        return {value} if isinstance(value, str) and value in lookup else set()
    active=references({k:v for k,v in doc.items() if k != 'materials'})
    pending=list(active)
    while pending:
        for identifier in references(lookup[pending.pop()]):
            if identifier not in active:
                active.add(identifier);pending.append(identifier)
    for identifier in active:
        mat=lookup[identifier]
        if mat.get('type') in ('draft','compound','combination') or 'draft' in mat or mat.get('draft_id'):
            complete=False
        if mat.get('type')=='vocal_separation' and (mat.get('choice') or mat.get('removed_sounds') or mat.get('final_algorithm')):
            raw=mat.get('production_path')
            path=Path(re.sub(r'^##_draftpath_placeholder_[^#]+_##',lambda _:str(copy_root),raw,count=1)) if isinstance(raw,str) and copy_root else Path(raw) if raw else None
            if path is not None and path.is_file():paths.add(str(path.resolve()))
            else:complete=False
    for track in doc['tracks']:
        if track.get('type') not in ('audio', 'video'):
            continue
        for seg in track['segments']:
            path = lookup[seg['material_id']].get('path')
            if path and Path(path).is_file():
                paths.add(str(Path(path).resolve()))
            else:
                complete = False
    return paths, complete


def render(args):
    if not re.fullmatch(r"[1-9][0-9]*x[1-9][0-9]*", args.size):
        raise ValueError("Use WIDTHxHEIGHT for --size.")
    if not 0 < args.fps <= 120:
        raise ValueError("Preview FPS must be positive and supported by the engine.")
    copy_root = directory(args.copy_root)
    source_root = directory(args.source_root) if args.source_root else copy_root
    support = directory(args.support_dir)
    cache = directory(args.cache_dir)
    app = directory(args.app_dir)
    runtime = directory(args.runtime)
    codec = Path(args.codec).resolve(strict=True)
    source = Path(args.input).resolve(strict=True)
    workspace = Path(args.workspace).resolve()
    if any(workspace.is_relative_to(p) for p in (copy_root, source_root, support, cache, app, runtime)):
        raise ValueError("Use a new preview workspace outside draft, cache and installation folders.")
    if source.is_relative_to(copy_root) or source.is_relative_to(source_root):
        raise ValueError("Render a saved isolated JSON, outside the live draft folders.")
    if not (support / "jyexport" / "engine.py").is_file() or not codec.is_file():
        raise ValueError("Compatible preview support or the requested engine is unavailable.")
    data = source.read_bytes()
    context = dict(copy_root=str(copy_root), source_root=str(source_root), support_dir=str(support),
                   cache_dir=str(cache), app_dir=str(app), codec=str(codec), runtime=str(runtime),
                   size=args.size, fps=args.fps, software=args.software)
    if workspace.exists():
        if not args.reuse:
            raise ValueError('Use a new preview workspace, or --reuse for a fully verified identical version.')
        certificate = workspace / 'preview.json'
        if not certificate.is_file():
            raise ValueError('Incomplete previous render. Diagnose its log and use a new workspace.')
        prior = json.loads(certificate.read_bytes())
        if prior.get('certificate_version',0)<2:
            raise ValueError('Cached preview predates complete dependency binding; use a new workspace.')
        if str(Path(__file__).resolve()) not in prior.get('dependency_hashes',{}):
            raise ValueError('Cached preview belongs to a different helper version/location; use a new workspace.')
        if prior.get('input_sha256') != hashlib.sha256(data).hexdigest() or prior.get('render_context') != context:
            raise ValueError('Cached input or render settings differ. Use a new preview workspace.')
        if not prior.get('reuse_safe') or not prior.get('dependency_hashes'):
            raise ValueError('This preview lacks complete dependency evidence; use a new workspace.')
        if any(not Path(p).is_file() or fingerprint(p) != h for p, h in prior['dependency_hashes'].items()):
            raise ValueError('A media/backend dependency changed. Use a new preview workspace.')
        if not Path(prior['preview']).is_file() or fingerprint(prior['preview']) != prior.get('preview_sha256'):
            raise ValueError('Cached preview is missing or changed. Use a new workspace.')
        return dict(prior, reused=True)
    sys.path.insert(0, str(support))
    from jyexport.encoded_audio import bind_referenced_aac
    from jyexport.engine import relocate_document
    from jyexport.processed_audio import bind_referenced_media_results, bind_referenced_results

    doc = json.loads(data)
    material_lookup(doc)
    workspace.mkdir(parents=True, exist_ok=False)
    doc, relocation = relocate_document(doc, source_root, copy_root, cache)
    original_paths, complete = input_files(doc, copy_root)
    backend_paths={str(codec),str(Path(__file__).resolve()), *(str(p) for p in (support / 'jyexport').glob('*.py'))}
    backend_paths.update(str(p) for p in (runtime / 'videoeditor.dll', app / 'videoeditor.dll') if p.is_file())
    original_hashes={p:fingerprint(p) for p in sorted(original_paths | backend_paths)}
    doc, _ = bind_referenced_media_results(doc, copy_root, workspace / "timeline_audio")
    doc, _ = bind_referenced_results(doc, copy_root, workspace / "effects_audio")
    doc, _ = bind_referenced_aac(doc, copy_root, workspace / "preset_audio", app)
    check_media(doc)
    if any(fingerprint(p) != h for p,h in original_hashes.items()):
        raise ValueError('An original media/backend dependency changed while preparing audio.')
    prepared_paths, _ = input_files(doc, copy_root)
    before_hashes=dict(original_hashes)
    before_hashes.update({p:fingerprint(p) for p in sorted(prepared_paths) if p not in before_hashes})
    prepared, output = workspace / "draft_content.json", workspace / "preview.mp4"
    save(prepared, doc)
    with (workspace / "render.log").open("wb") as log:
        process = subprocess.run(
            [str(codec), "-ex", str(prepared), "-o", str(output), "--jy-dir", str(runtime),
             "--size", args.size, "--fps", f"{args.fps:g}", "--bitrate", "2500K",
             "--codec", "h264", "--hard-encode", str(int(not args.software)),
             "--timeout", "180", "-j", "1", "-q"],
            cwd=workspace, stdout=log, stderr=subprocess.STDOUT, timeout=210,
        )
    if process.returncode or not output.is_file() or not output.stat().st_size:
        raise ValueError(f"Preview render failed. See {workspace / 'render.log'}.")
    if source.read_bytes() != data:
        raise ValueError("The input changed during preview. Render again from the current version.")
    if any(fingerprint(p) != h for p, h in before_hashes.items()):
        raise ValueError('A media dependency changed during rendering. Render a fresh saved version.')
    result = dict(preview=str(output), input_sha256=hashlib.sha256(data).hexdigest(),
                  size=args.size, requested_fps=args.fps, timeline_id=doc.get("id"),
                  unresolved_cache_paths=relocation["unresolved_outer_cache_paths"])
    result.update(certificate_version=2, render_context=context, dependency_hashes=before_hashes, reuse_safe=complete,
                  preview_sha256=fingerprint(output), reused=False)
    save(workspace / "preview.json", result)
    return result


def main():
    sys.dont_write_bytecode = True
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Isolated edited timeline JSON.")
    parser.add_argument("--workspace", required=True, help="New directory for this preview version.")
    parser.add_argument("--copy-root", required=True, help="Verified copy whose resources the timeline uses.")
    parser.add_argument("--source-root", help="Original root to rebase, if the JSON still contains its paths.")
    parser.add_argument("--support-dir", required=True, help="Installed directory containing compatible jyexport modules.")
    parser.add_argument("--cache-dir", required=True, help="Jianying User Data Cache directory.")
    parser.add_argument("--app-dir", required=True, help="Installed Jianying version directory.")
    parser.add_argument("--codec", required=True, help="Compatible jy-draftc.exe.")
    parser.add_argument("--runtime", required=True, help="Matched headless engine runtime directory.")
    parser.add_argument("--size", default="540x960", help="Work-preview frame size (default 540x960).")
    parser.add_argument("--fps", type=float, default=30, help="Requested preview rate (default 30). Verify actual FPS.")
    parser.add_argument("--software", action="store_true", help="Use software encoding if the engine supports it.")
    parser.add_argument("--reuse", action="store_true", help="Reuse only an identical input/settings/media/backend hash-bound preview.")
    args = parser.parse_args()
    try:
        print(json.dumps(render(args), ensure_ascii=False, indent=2))
    except (OSError, ValueError, TypeError, ImportError, KeyError, RuntimeError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, f"Preview unavailable: {exc}\n")


if __name__ == "__main__":
    main()
