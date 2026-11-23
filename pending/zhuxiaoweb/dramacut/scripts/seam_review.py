"""Read-only source/preview contact sheets for new fine-cut joins.

No face recognition, editorial approval, draft writes, or repair application.
Uses ffprobe's actual decoded frame timestamps rather than assuming source FPS.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import html
import json
import math
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
OFFSETS = (-5, -2, -1, 0, 1, 3, 8)
W, H = 144, 256


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def run(argv):
    process = subprocess.run(list(map(str, argv)), capture_output=True, timeout=210,
                             creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if process.returncode:
        raise ValueError(process.stderr.decode('utf-8', 'replace')[-1600:])
    return process.stdout


def bounds(segment):
    value = segment['target_timerange']
    start = value.get('start', 0)
    return start, start + value['duration']


def lookup(doc):
    return {m['id']: m for group in doc.get('materials', {}).values() if isinstance(group, list)
            for m in group if isinstance(m, dict) and m.get('id')}


def source_path(material, copy_root):
    raw = material.get('path')
    if not raw:
        raise ValueError('Video material has no local media path: ' + material.get('id', ''))
    if raw.startswith('##_draftpath_placeholder_'):
        if not copy_root:
            raise ValueError('A draft-relative video path requires --copy-root')
        raw = re.sub(r'^##_draftpath_placeholder_[^#]+_##', lambda _: str(copy_root), raw, count=1)
    path = Path(raw)
    if not path.is_absolute() or not path.is_file():
        raise ValueError('Video media is not an existing absolute local file: ' + raw)
    return path.resolve()


def signature(left, right, mats):
    """Ignore segment IDs; compare actual source/appearance around a boundary."""
    def edge(segment, side):
        source = segment.get('source_timerange') or {}
        ins = source.get('start', 0)
        return (mats[segment['material_id']].get('path'),
                ins + (source.get('duration', 0) if side == 'end' else 0),
                json.dumps(segment.get('clip', {}), sort_keys=True),
                segment.get('speed', 1), bool(segment.get('reverse') or segment.get('is_reverse')))
    return edge(left, 'end'), edge(right, 'start')


def boundary_map(baseline, edited, report, primary_id=None, all_boundaries=False):
    before = [t for t in baseline['tracks'] if t.get('type') == 'video']
    after = [t for t in edited['tracks'] if t.get('type') == 'video']
    if not before or not after:
        raise ValueError('Both timelines need a video track')
    if primary_id:
        old = next((t for t in before if t['id'] == primary_id), None)
        new = next((t for t in after if t['id'] == primary_id), None)
    else:
        old, new = before[0], after[0]
    if old is None or new is None:
        raise ValueError('Primary video track is missing from baseline or edited timeline')
    mats_before, mats_after = lookup(baseline), lookup(edited)
    old_edges = {signature(a, b, mats_before) for a, b in zip(old['segments'], old['segments'][1:])}
    reasons = {}
    for point in report.get('seams_us', []):
        if type(point) is not int:
            raise ValueError('Edit report seams_us must contain integer microseconds')
        if 0 < point < edited['duration']:
            reasons.setdefault(point, []).append('edit_report_seam')
    rows = sorted(new['segments'], key=lambda s: bounds(s)[0])
    for left, right in zip(rows, rows[1:]):
        point = bounds(right)[0]
        if not 0 < point < edited['duration']:
            continue
        if all_boundaries or signature(left, right, mats_after) not in old_edges:
            reasons.setdefault(point, []).append('all_video_boundaries' if all_boundaries else 'new_source_or_appearance_boundary')
    return new, [{'time_us': point, 'reasons': values} for point, values in sorted(reasons.items())]


def containing(rows, time_us):
    matches = [s for s in rows if bounds(s)[0] <= time_us < bounds(s)[1]]
    if len(matches) != 1:
        raise ValueError(f'Expected one primary picture at {float(time_us):.3f} us; found {len(matches)}')
    return matches[0]


def mapping(segment, time_us):
    a, b = bounds(segment)
    source = segment.get('source_timerange')
    if not source or segment.get('reverse') or segment.get('is_reverse'):
        raise ValueError('Source sampling does not support missing/reverse timing: ' + segment['id'])
    ratio = Fraction(source['duration'], b-a)
    # The edit backend supports ordinary constant 1x segments. Do not guess curve speed.
    if abs(float(ratio)-1) > .000001 or segment.get('speed', 1) != 1:
        raise ValueError('Source sampling needs an ordinary forward 1x segment: ' + segment['id'])
    return Fraction(source.get('start', 0)) + (time_us-a)*ratio


def probe(ffprobe, path):
    data = json.loads(run([ffprobe, '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,r_frame_rate,avg_frame_rate,start_time,duration',
        '-show_entries', 'frame=best_effort_timestamp_time', '-show_frames', '-of', 'json', path]))
    stream = data.get('streams', [None])[0]
    if not stream:
        raise ValueError('No video stream: ' + str(path))
    times = [Fraction(str(row['best_effort_timestamp_time'])) for row in data.get('frames', [])
             if row.get('best_effort_timestamp_time') is not None]
    if not times or any(a > b for a, b in zip(times, times[1:])):
        raise ValueError('Decoded source frames have no ordered PTS: ' + str(path))
    origin = times[0]
    times = [x-origin for x in times]
    steps = {round(float(b-a), 6) for a, b in zip(times, times[1:])}
    return dict(path=str(path), sha256=sha(path), width=stream['width'], height=stream['height'],
                r_frame_rate=stream.get('r_frame_rate'), avg_frame_rate=stream.get('avg_frame_rate'),
                frame_count=len(times), pts_origin_seconds=float(origin),
                variable_frame_timestamps=len(steps) > 2, times=times)


def frame_at(info, source_us):
    seconds = Fraction(source_us, 1_000_000)
    index = bisect.bisect_right(info['times'], seconds)-1
    if index < 0 or index >= len(info['times']):
        raise ValueError('Mapped source time lies outside decoded frames')
    return index


def extract_frames(ffmpeg, path, indices):
    indices = sorted(set(indices))
    if not indices:
        return {}
    ranges = []
    a = b = indices[0]
    for n in indices[1:]:
        if n == b+1:
            b = n
        else:
            ranges.append((a, b))
            a = b = n
    ranges.append((a, b))
    expression = '+'.join(f'eq(n,{a})' if a == b else f'between(n,{a},{b})' for a, b in ranges)
    vf = (f"select='{expression}',scale={W}:{H}:force_original_aspect_ratio=decrease,"
          f'pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,format=rgb24')
    raw = run([ffmpeg, '-nostdin', '-v', 'error', '-i', path, '-an', '-vf', vf,
               '-fps_mode', 'passthrough', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
    stride = W*H*3
    if len(raw) != stride*len(indices):
        raise ValueError(f'Expected {len(indices)} frames; decoded {len(raw)/stride:g}: {path}')
    return {index: raw[i*stride:(i+1)*stride] for i, index in enumerate(indices)}


def sheet(ffmpeg, pixels, output, offsets=OFFSETS):
    # Pure standard library contact sheet; colored separators identify the join.
    margin, gap = 4, 4
    width = len(pixels)*(W+gap)+margin
    height = H+2*margin
    buf = bytearray(bytes((24, 24, 24))*(width*height))
    for col, image in enumerate(pixels):
        x = margin+col*(W+gap)
        for y in range(H):
            offset = ((y+margin)*width+x)*3
            buf[offset:offset+W*3] = image[y*W*3:(y+1)*W*3]
        bar = (70, 150, 220) if offsets[col] < 0 else (230, 150, 50)
        for y in range(margin):
            offset = (y*width+x)*3
            buf[offset:offset+W*3] = bytes(bar)*W
    ppm = f'P6\n{width} {height}\n255\n'.encode()+buf
    # subprocess input is explicit; no shell interpolation or temporary source files.
    p = subprocess.run([str(ffmpeg), '-nostdin', '-v', 'error', '-f', 'image2pipe', '-vcodec', 'ppm', '-i', '-',
                        '-frames:v', '1', '-update', '1', str(output)], input=ppm, capture_output=True, timeout=60,
                       creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if p.returncode or not output.is_file():
        raise ValueError('Contact-sheet conversion failed: '+p.stderr.decode('utf-8', 'replace')[-1000:])


def visual_metrics(left, right):
    # Raw low-resolution mean absolute difference: a locator, never a face/pose decision.
    difference = sum(abs(a-b) for a, b in zip(left, right))/(len(left)*255)
    return dict(source_thumbnail_mean_absolute_difference=round(difference, 6),
                scope='Untransformed source thumbnails only; no subject, shot-size or pose recognition')


def safe_inputs(args):
    baseline, edited, report = (Path(getattr(args, key)).resolve(strict=True)
                                for key in ('baseline', 'input', 'edit_report'))
    copy_root = Path(args.copy_root).resolve(strict=True) if args.copy_root else None
    output = Path(args.output).resolve()
    if output.exists():
        raise ValueError('Use a new output directory')
    if copy_root and (output.is_relative_to(copy_root) or baseline.is_relative_to(copy_root)
                      or edited.is_relative_to(copy_root) or report.is_relative_to(copy_root)):
        raise ValueError('Inputs must be isolated saved JSON and output must be outside the live draft')
    if any(p.is_relative_to(output) for p in (baseline, edited, report)):
        raise ValueError('Output must not contain an input')
    old, new, edit = load(baseline), load(edited), load(report)
    if edit.get('input_sha256') != sha(baseline) or edit.get('output_sha256') != sha(edited):
        raise ValueError('Edit report is stale for baseline or edited JSON')
    if old.get('id') != new.get('id') or edit.get('timeline_id') != new.get('id'):
        raise ValueError('Timeline identities differ')
    return baseline, edited, report, copy_root, output, old, new, edit


def scan(args):
    baseline, edited, report, copy_root, output, old, new, edit = safe_inputs(args)
    checks = {str(p): sha(p) for p in (baseline, edited, report)}
    track, points = boundary_map(old, new, edit, args.primary_video_track_id, args.all_boundaries)
    mats = lookup(new)
    fps = Fraction(str(new.get('fps', 30)))
    if fps <= 0 or fps > 120:
        raise ValueError('Timeline FPS is invalid')
    sources, requests, results = {}, {}, []
    preview_data = None
    if args.preview:
        certificate_path = Path(args.preview).resolve()/ 'preview.json'
        certificate = load(certificate_path)
        preview_path = Path(certificate['preview']).resolve(strict=True)
        if certificate.get('input_sha256') != sha(edited) or certificate.get('preview_sha256') != sha(preview_path):
            raise ValueError('Preview is stale for this edited JSON')
        preview_data = probe(args.ffprobe, preview_path)
        if Fraction(preview_data['avg_frame_rate']) != fps:
            raise ValueError('Preview FPS differs from the timeline')
        checks[str(certificate_path)] = sha(certificate_path)
        checks[str(preview_path)] = sha(preview_path)
    for ordinal, point in enumerate(points, 1):
        at = point['time_us']
        # First target frame at or after the real microsecond boundary; sample both sides.
        center = math.ceil(Fraction(at, 1_000_000)*fps)
        samples = []
        for offset in OFFSETS:
            n = max(0, min(math.ceil(Fraction(new['duration'], 1_000_000)*fps)-1, center+offset))
            target = Fraction(n*1_000_000, 1)/fps
            segment = containing(track['segments'], target)
            material = mats[segment['material_id']]
            path = source_path(material, copy_root)
            if str(path) not in sources:
                sources[str(path)] = probe(args.ffprobe, path)
                checks[str(path)] = sources[str(path)]['sha256']
            source_us = mapping(segment, target)
            if not 0 <= source_us < material.get('duration', 0):
                raise ValueError('Mapped source time exceeds material duration: '+segment['id'])
            for ref in segment.get('extra_material_refs', []):
                effect = mats.get(ref, {})
                if effect.get('type') == 'speed' and effect.get('curve_speed'):
                    raise ValueError('Source sampling does not support curve speed: '+segment['id'])
            frame = frame_at(sources[str(path)], source_us)
            requests.setdefault(str(path), set()).add(frame)
            samples.append(dict(offset_target_frames=offset, target_frame=n, target_seconds=float(target/1_000_000),
                segment_id=segment['id'], path=str(path), mapped_source_us=round(source_us),
                source_frame=frame, source_frame_pts_seconds=float(sources[str(path)]['times'][frame]),
                clip=segment.get('clip', {})))
        left, right = samples[2], samples[3]
        same_source = left['path'] == right['path']
        same_appearance = left['clip'] == right['clip']
        left_segment = containing(track['segments'], Fraction(at)-Fraction(1, 10))
        right_segment = containing(track['segments'], Fraction(at)+Fraction(1, 10))
        source_gap = mapping(right_segment, Fraction(at))-mapping(left_segment, Fraction(at)) if same_source else None
        risk = []
        if same_source and source_gap and same_appearance:
            risk.append('same_media_same_transform_skipped_source: check subject/shot-size/pose manually')
        if same_source and right['source_frame'] < left['source_frame']:
            risk.append('source_frame_reversal_at_join')
        lengths = [bounds(x)[1]-bounds(x)[0] for x in (left_segment, right_segment)]
        if min(lengths)*fps < 3_000_000:
            risk.append('adjacent_piece_shorter_than_three_target_frames')
        results.append(dict(id=f'seam-{ordinal:04d}', time_us=at, reasons=point['reasons'],
            same_media=same_source, same_static_clip=same_appearance,
            source_gap_us=round(source_gap) if source_gap is not None else None,
            risk_locators=risk, samples=samples, source_sheet=f'seam-{ordinal:04d}-source.png',
            rendered_sheet=f'seam-{ordinal:04d}-rendered.png' if preview_data else None,
            status='pending', judgement='Computer metrics do not establish same person, shot size, match action, or acceptable continuity'))
    output.mkdir(parents=True)
    images = {path: extract_frames(args.ffmpeg, path, indices) for path, indices in requests.items()}
    rendered = extract_frames(args.ffmpeg, preview_data['path'], [s['target_frame'] for row in results for s in row['samples']]) if preview_data and results else {}
    for row in results:
        pixels = [images[s['path']][s['source_frame']] for s in row['samples']]
        sheet(args.ffmpeg, pixels, output/row['source_sheet'])
        row['metrics'] = visual_metrics(pixels[2], pixels[3])
        if rendered:
            sheet(args.ffmpeg, [rendered[s['target_frame']] for s in row['samples']], output/row['rendered_sheet'])
        checks[str(output/row['source_sheet'])] = sha(output/row['source_sheet'])
        if row['rendered_sheet']:
            checks[str(output/row['rendered_sheet'])] = sha(output/row['rendered_sheet'])
    for path, checksum in checks.items():
        if sha(path) != checksum:
            raise ValueError('An input or source changed during seam sampling: '+path)
    summary = dict(schema_version=1, timeline_id=new['id'], baseline=str(baseline), input=str(edited),
        edit_report=str(report), baseline_sha256=checks[str(baseline)], input_sha256=checks[str(edited)],
        edit_report_sha256=checks[str(report)], primary_video_track_id=track['id'], fps=str(fps),
        preview_available=bool(preview_data), required_review_count=len(results),
        source_media=[{k: v for k, v in x.items() if k != 'times'} for x in sources.values()],
        dependencies=checks, seams=results,
        evidence_scope='Source sheets omit Jianying crop/filter/animation/subtitles; rendered sheets show the bound preview. No subjective normal-speed playback was performed.',
        status='needs_review' if results else 'no_new_seams')
    scan_path = output/'seam_review.json'
    save(scan_path, summary)
    contact_sheet = decisions_template = None
    if not getattr(args, 'no_html', False):
        template = dict(schema_version=1, scan_sha256=sha(scan_path), input_sha256=checks[str(edited)],
            seams=[dict(id=x['id'], time_us=x['time_us'], decision='pending', same_subject=None, same_shot_size=None,
                pose_and_prop_checked=False, frame_review=False, normal_speed_review=False,
                repair_method='none', reason='') for x in results])
        decisions_template = output/'decisions.template.json'
        save(decisions_template, template)
        cards = []
        for row in results:
            labels = ' | '.join(f'{s["offset_target_frames"]:+d}: {s["target_seconds"]:.3f}s / source #{s["source_frame"]}' for s in row['samples'])
            cards.append(f'<section><h2>{row["id"]}: {row["time_us"]/1e6:.3f}s</h2><p>{html.escape(str(row["risk_locators"]))}</p>'
                f'<p>源帧（上方蓝条=接点前；橙条=接点后；不含剪映画面变换）</p><img src="{row["source_sheet"]}">'
                +(f'<p>实际渲染帧</p><img src="{row["rendered_sheet"]}">' if row['rendered_sheet'] else '')
                +f'<p>{html.escape(labels)}</p></section>')
        contact_sheet = output/'review.html'
        contact_sheet.write_text('<!doctype html><meta charset="utf-8"><title>接点逐帧审阅</title>'
            '<style>body{background:#17191d;color:#eee;font:15px sans-serif;margin:24px}section{margin:30px 0}img{max-width:100%}p{line-height:1.6}</style>'
            '<h1>新接点联系表</h1><p>联系表只负责定位。每项仍须正常速度看前后至少一组完整对白/动作；不能凭相似度决定通过。</p>'
            +(''.join(cards) or '<p>本轮没有新视频接点；音频编辑无需伪造画面审阅。</p>'), encoding='utf-8')
    return dict(status=summary['status'], review=str(scan_path), contact_sheet=str(contact_sheet) if contact_sheet else None,
        decisions_template=str(decisions_template) if decisions_template else None, required_review_count=len(results),
        primary_video_track_id=track['id'])


def validate_review(args):
    scan_path, decisions_path = Path(args.scan).resolve(strict=True), Path(args.decisions).resolve(strict=True)
    review, decisions = load(scan_path), load(decisions_path)
    if decisions.get('scan_sha256') != sha(scan_path) or decisions.get('input_sha256') != review.get('input_sha256'):
        raise ValueError('Decisions are stale for this scan or edited timeline')
    for path, checksum in review['dependencies'].items():
        if not Path(path).is_file() or sha(path) != checksum:
            raise ValueError('A reviewed input, preview, or source changed: '+path)
    expected = {row['id']: row for row in review['seams']}
    values = decisions.get('seams', [])
    if len(values) != len(expected) or {x.get('id') for x in values} != set(expected):
        raise ValueError('Decisions must contain every required seam exactly once')
    issues = []
    for row in values:
        ref = expected[row['id']]
        if row.get('time_us') != ref['time_us']:
            raise ValueError('Decision seam time changed: '+row['id'])
        if row.get('decision') != 'pass':
            issues.append(row['id']+': pending or needs repair')
        if not review.get('preview_available'):
            issues.append(row['id']+': no bound rendered preview')
        if any(row.get(key) is not True for key in ('pose_and_prop_checked', 'frame_review', 'normal_speed_review')):
            issues.append(row['id']+': frame/pose/normal-speed review incomplete')
        if type(row.get('same_subject')) is not bool or type(row.get('same_shot_size')) is not bool:
            issues.append(row['id']+': subject and shot-size observation missing')
        if row.get('repair_method') not in ('none', 'cutaway', 'reframe', 'match_action', 'restore_handle', 'native'):
            issues.append(row['id']+': unsupported repair method')
        if not isinstance(row.get('reason'), str) or not row['reason'].strip():
            issues.append(row['id']+': concrete retention/continuity reason required')
    return dict(status='needs_review' if issues else 'passed', required_review_count=len(expected),
                reviewed_count=sum(x.get('decision') == 'pass' for x in values), issues=issues,
                input_sha256=review['input_sha256'], scan_sha256=sha(scan_path), decisions_sha256=sha(decisions_path))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('scan')
    for field in ('baseline', 'input', 'edit-report', 'output', 'ffmpeg', 'ffprobe'):
        p.add_argument('--'+field, required=True)
    p.add_argument('--copy-root', required=True); p.add_argument('--primary-video-track-id'); p.add_argument('--preview')
    p.add_argument('--all-boundaries', action='store_true', help='Also review unchanged saved video boundaries')
    p.add_argument('--no-html', action='store_true', help='Write machine-readable reports and frame sheets only')
    p = sub.add_parser('validate-review')
    for field in ('scan', 'decisions'):
        p.add_argument('--'+field, required=True)
    p = sub.add_parser('inspect-range', help='Inspect every target frame in a bridge/reframe, including both handles')
    for field in ('input', 'edit-report', 'copy-root', 'preview', 'output', 'ffmpeg', 'ffprobe'):
        p.add_argument('--'+field, required=True)
    p.add_argument('--range-id', help='Bind this exact bridge/reframe operation from the edit report')
    p.add_argument('--start-us', type=int, required=True)
    p.add_argument('--end-us', type=int, required=True)
    p.add_argument('--handles-ms', type=float, default=300)
    p.add_argument('--primary-video-track-id')
    p.add_argument('--no-html', action='store_true', help='Write machine-readable range evidence without a human-review page')
    p = sub.add_parser('validate-range')
    p.add_argument('--scan', required=True)
    p.add_argument('--decisions', required=True)
    args = parser.parse_args()
    try:
        if args.command == 'inspect-range':
            from picture_range import inspect_range
            result = inspect_range(args)
        elif args.command == 'validate-range':
            from picture_range import validate_range
            result = validate_range(args)
        else:
            result = scan(args) if args.command == 'scan' else validate_review(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, 'Seam review unavailable: '+str(exc)+'\n')


if __name__ == '__main__':
    main()
