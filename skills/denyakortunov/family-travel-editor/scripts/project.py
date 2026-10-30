#!/usr/bin/env python3
"""Local project helpers. No network access or account credentials."""
import argparse
import hashlib
import json
import os
import time
import shutil
import subprocess
import sys
from pathlib import Path

# Candidate extensions, not a guarantee that this ffprobe build can decode them.
MEDIA = {'.mov', '.mp4', '.mkv', '.m4v', '.mts', '.m2ts', '.avi', '.mxf', '.webm',
         '.wav', '.mp3', '.m4a', '.flac', '.aac', '.ogg', '.aiff', '.aif',
         '.jpg', '.jpeg', '.png', '.heic', '.heif', '.tif', '.tiff', '.webp'}


def sha256(path, progress=None):
    digest = hashlib.sha256()
    last_update = time.monotonic()
    processed = 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
            processed += len(block)
            if progress and time.monotonic() - last_update >= 5:
                progress(processed)
                last_update = time.monotonic()
    return digest.hexdigest()


def save_new(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def catalog(source, output, ffprobe='ffprobe'):
    source, output = Path(source).resolve(), Path(output).resolve()
    if not source.is_dir():
        raise ValueError('Source must be a readable directory')
    if output == source or source in output.parents:
        raise ValueError('Write the catalogue outside the source directory')
    if output.exists():
        raise FileExistsError(output)
    executable = shutil.which(ffprobe)
    records, skipped, scan_errors = [], [], []
    print('Scanning source files…', file=sys.stderr, flush=True)
    candidates = []
    def scan_error(error):
        path = Path(error.filename) if error.filename else source
        try:
            relative = path.relative_to(source).as_posix()
        except ValueError:
            relative = str(path)
        scan_errors.append({'path': relative, 'error': str(error),
                            'note': 'Contents could not be inventoried; file count is unknown.'})

    # pathlib.rglob can silently omit unreadable subdirectories. os.walk exposes
    # those failures through onerror and does not follow directory symlinks.
    for directory, folders, filenames in os.walk(source, followlinks=False, onerror=scan_error):
        folders.sort()
        for name in list(folders):
            path = Path(directory) / name
            if path.is_symlink():
                skipped.append({'path': path.relative_to(source).as_posix(),
                                'reason': 'symlink directory; contents not followed'})
                folders.remove(name)
        for name in sorted(filenames):
            path = Path(directory) / name
            relative = path.relative_to(source).as_posix()
            try:
                if path.is_symlink():
                    skipped.append({'path': relative, 'reason': 'symlink; originals are not followed'})
                elif not path.is_file():
                    skipped.append({'path': relative, 'reason': 'not a regular file or no longer available'})
                elif source not in path.resolve().parents:
                    skipped.append({'path': relative, 'reason': 'outside source directory'})
                elif path.suffix.lower() not in MEDIA:
                    skipped.append({'path': relative, 'reason': 'extension not in candidate list'})
                else:
                    candidates.append(path)
            except OSError as error:
                scan_error(error)
    candidates.sort()
    for index, path in enumerate(candidates, 1):
        relative = path.relative_to(source).as_posix()
        print(f'[{index}/{len(candidates)}] Hashing {relative}', file=sys.stderr, flush=True)
        record = {'path': relative, 'metadata_status': 'unavailable'}
        try:
            record.update(bytes=path.stat().st_size,
                          sha256=sha256(path, lambda size: print(
                              f'  {relative}: {size // (1024 * 1024)} MiB hashed…',
                              file=sys.stderr, flush=True)))
            if executable:
                print(f'  Reading metadata (timeout 120s): {relative}', file=sys.stderr, flush=True)
                result = subprocess.run([executable, '-v', 'error', '-show_streams', '-show_format',
                                         '-of', 'json', str(path)], capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    metadata = json.loads(result.stdout)
                    if not isinstance(metadata, dict) or not metadata.get('streams'):
                        raise ValueError('ffprobe returned no media streams')
                    record.update(metadata_status='probed', metadata=metadata)
                else:
                    record.update(metadata_status='failed', error=result.stderr[-2000:])
        except subprocess.TimeoutExpired:
            record.update(metadata_status='failed', error='ffprobe timed out after 120 seconds; retry this file separately')
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            record.update(metadata_status='failed', error=str(error)[-2000:])
        records.append(record)
    summary = {'included': len(records), 'skipped': len(skipped), 'scan_failed': len(scan_errors),
               'failed': sum(r['metadata_status'] == 'failed' for r in records),
               'metadata_unavailable': sum(r['metadata_status'] == 'unavailable' for r in records)}
    save_new(output, {'schema_version': 1, 'files': records, 'skipped': skipped, 'scan_errors': scan_errors, 'summary': summary,
                      'note': 'Metadata and hashes only; content has not been watched or listened to.'})
    print(f"Saved {output}: {summary['included']} included, {summary['skipped']} skipped, "
          f"{summary['failed']} failed files, {summary['scan_failed']} scan errors, "
          f"{summary['metadata_unavailable']} without metadata.", file=sys.stderr)
    if not records:
        print('No media candidates found. Check the folder and the skipped reasons in the catalogue.', file=sys.stderr)
    if summary['scan_failed']:
        print('Some source locations could not be inventoried. Check scan_errors; coverage is incomplete.', file=sys.stderr)
    if summary['failed']:
        print('Partial catalogue saved. Inspect each failed record before choosing source ranges.', file=sys.stderr)
    if summary['metadata_unavailable']:
        print('Install ffprobe for duration/rate metadata; hashes alone cannot establish shot ranges.', file=sys.stderr)
    return len(records)


def measure(media, output, ffmpeg='ffmpeg'):
    media, output = Path(media).resolve(), Path(output).resolve()
    if not media.is_file():
        raise FileNotFoundError(media)
    if output.exists() or output == media:
        raise FileExistsError(output)
    executable = shutil.which(ffmpeg)
    if not executable:
        raise ValueError('FFmpeg is unavailable; supply --ffmpeg PATH')
    result = subprocess.run([executable, '-hide_banner', '-nostdin', '-xerror', '-i', str(media),
                             '-map', '0:v?', '-map', '0:a?', '-vf', 'blackdetect=d=0.5,freezedetect=d=2',
                             '-af', 'loudnorm=print_format=json', '-f', 'null', '-'],
                            capture_output=True, text=True)
    report = {'schema_version': 1, 'file': media.name, 'sha256': sha256(media),
              'decode_returncode': result.returncode,
              'status': 'measurement_completed' if result.returncode == 0 else 'measurement_failed',
              'ffmpeg_log': result.stderr,
              'limitations': ['Not a listening or editorial verdict.',
                              'Black/freeze flags need interpretation; no speech completeness check.',
                              'No stereo-correlation or mono-compatibility test is performed.']}
    save_new(output, report)
    print(f'Measurement report: {output} ({report["status"]}). Not a listening or editorial verdict.')
    return result.returncode


def doctor(task='plan', ffmpeg='ffmpeg', ffprobe='ffprobe', source=None):
    binaries = {'ffmpeg': shutil.which(ffmpeg), 'ffprobe': shutil.which(ffprobe)}
    requirements = {'plan': [], 'catalog': [], 'preview': ['ffmpeg', 'ffprobe'],
                    'measure': ['ffmpeg'], 'resolve': []}
    missing = [name for name in requirements[task] if not binaries[name]]
    notes = ['Python 3.9+ is required for the helpers.']
    if task == 'catalog' and not binaries['ffprobe']:
        notes.append('Catalogue hashes are available; install ffprobe for duration/rate metadata.')
    if missing:
        notes.append('Install FFmpeg including ffprobe, or pass --ffmpeg PATH and --ffprobe PATH.')
    if task == 'resolve':
        notes.append('Not connected or tested. When no other edit is active, run resolve_bridge.py probe separately.')
    if task == 'plan':
        notes.append('Planning needs no editor or paid service; viewing/listening depends on your agent tools.')
    source_check = None
    if source is not None:
        source_path = Path(source).expanduser().resolve()
        accessible = source_path.is_dir() and os.access(source_path, os.R_OK | os.X_OK)
        source_check = {'path': str(source_path), 'readable_directory': accessible}
        if not accessible:
            notes.append('Source folder is unavailable. Check its path, drive connection and file permissions.')
    python_ok = sys.version_info >= (3, 9)
    return {'skill_version': (Path(__file__).resolve().parents[1] / 'VERSION').read_text().strip(),
            'skill_path': str(Path(__file__).resolve().parents[1]),
            'task': task, 'source': source_check,
            'ready': (python_ok and not missing and (source_check is None or source_check['readable_directory']))
                     if task != 'resolve' else None,
            'python': sys.version.split()[0], 'platform': sys.platform,
            'tools': binaries, 'missing': missing, 'notes': notes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    doc = sub.add_parser('doctor')
    doc.add_argument('--task', choices=['plan', 'catalog', 'preview', 'measure', 'resolve'], default='plan')
    doc.add_argument('--json', action='store_true')
    doc.add_argument('--source', type=Path, help='Check source folder access without modifying it')
    doc.add_argument('--ffmpeg', default='ffmpeg'); doc.add_argument('--ffprobe', default='ffprobe')
    init = sub.add_parser('init'); init.add_argument('workspace', type=Path)
    cat = sub.add_parser('catalog'); cat.add_argument('source', type=Path)
    cat.add_argument('--output', type=Path, required=True); cat.add_argument('--ffprobe', default='ffprobe')
    qc = sub.add_parser('measure'); qc.add_argument('media', type=Path)
    qc.add_argument('--output', type=Path, required=True); qc.add_argument('--ffmpeg', default='ffmpeg')
    args = parser.parse_args()
    try:
        if args.command == 'doctor':
            report = doctor(args.task, args.ffmpeg, args.ffprobe, args.source)
            if args.json:
                print(json.dumps(report, indent=2))
            else:
                state = 'NOT CHECKED' if report['ready'] is None else ('READY' if report['ready'] else 'NEEDS ATTENTION')
                print(f"family-travel-editor {report['skill_version']} at {report['skill_path']}")
                print(f"{args.task}: {state} (Python {report['python']})")
                for name, path in report['tools'].items():
                    print(f"  {name}: {path or 'not found'}")
                if report['source']:
                    print(f"  source: {report['source']['path']} (readable: {report['source']['readable_directory']})")
                for note in report['notes']:
                    print(note)
            return 0 if report['ready'] else 2
        elif args.command == 'init':
            args.workspace.mkdir(parents=True, exist_ok=False)
            templates = Path(__file__).resolve().parents[1] / 'assets/templates'
            for item in templates.iterdir():
                shutil.copyfile(item, args.workspace / item.name)
            print('Created a new planning workspace.')
        elif args.command == 'catalog':
            count = catalog(args.source, args.output, args.ffprobe)
            summary = json.loads(args.output.read_text())['summary']
            print(f'Catalogued {count} files; see {args.output.resolve()}.')
            return 2 if count == 0 or summary['failed'] or summary['scan_failed'] else 0
        elif args.command == 'measure':
            return measure(args.media, args.output, args.ffmpeg)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
