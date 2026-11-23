"""Inspect every displayed target frame inside a bridge/reframe and both handles.

Companion to seam_review; source PTS and rendered frames are distinct evidence.
No transition/pose classification, live-draft writes or automatic subjective pass.
"""
from __future__ import annotations

from fractions import Fraction
import html
import math
from pathlib import Path

import seam_review as seam
from timeline_ops import mapped


def required_ranges(report, primary_video_track_id=None):
    """Map the current edit report's picture operations to output-time ranges."""
    operations = report.get('picture_operations', {})
    cuts = report.get('cuts_us', [])
    for cut in cuts:
        if not isinstance(cut, list) or len(cut) != 2 or any(type(t) is not int for t in cut):
            raise ValueError('Edit report cuts must be integer microsecond ranges')
        lo, hi = cut
        if not 0 <= lo < hi <= report.get('old_duration_us', hi):
            raise ValueError('Edit report cut is outside the input timeline')
    result = []
    for field, operation in (('bridges', 'bridge'), ('reframes', 'reframe')):
        rows = operations.get(field, [])
        if not isinstance(rows, list):
            raise ValueError('Picture operations must be arrays')
        for index, row in enumerate(rows, 1):
            first, last = row.get('start_us'), row.get('end_us')
            if type(first) is not int or type(last) is not int:
                raise ValueError('Picture operation input range must use integer microseconds')
            start, end = mapped(first, cuts), mapped(last, cuts)
            if not 0 <= start < end <= report.get('duration_us', end):
                raise ValueError('Picture operation was removed or has no valid output range')
            result.append(dict(range_id=f'{operation}-{index:04d}', operation=operation,
                               track_id=row.get('track_id') or primary_video_track_id,
                               primary_video_track_id=row.get('track_id') or primary_video_track_id,
                               input_start_us=first, input_end_us=last,
                               start_us=start, end_us=end))
    return result


def schedule(start, end, duration, fps, handles_ms=300):
    if type(start) is not int or type(end) is not int or not 0 <= start < end <= duration:
        raise ValueError('Range must be integer microseconds inside the timeline')
    if not math.isfinite(handles_ms) or handles_ms < 0:
        raise ValueError('handles-ms must be finite and nonnegative')
    fps = Fraction(str(fps))
    if not 0 < fps <= 120:
        raise ValueError('Invalid timeline FPS')
    count = math.ceil(Fraction(duration, 1_000_000)*fps)
    a = max(0, math.floor(Fraction(start-round(handles_ms*1000), 1_000_000)*fps)-1)
    b = min(count, math.ceil(Fraction(end+round(handles_ms*1000), 1_000_000)*fps)+1)
    if b-a > 900:
        raise ValueError('More than 900 target frames; inspect overlapping shorter ranges')
    return list(range(a, b))


def inspect_range(args):
    src = Path(args.input).resolve(strict=True)
    edit_path = Path(args.edit_report).resolve(strict=True)
    root = Path(args.copy_root).resolve(strict=True)
    output = Path(args.output).resolve()
    if output.exists() or output.is_relative_to(root) or src.is_relative_to(root) or src.is_relative_to(output):
        raise ValueError('Use isolated input JSON and a fresh output directory outside the live draft')
    doc = seam.load(src)
    edit = seam.load(edit_path)
    if edit.get('output_sha256') != seam.sha(src) or edit.get('timeline_id') != doc.get('id'):
        raise ValueError('Range inspection edit report is stale or belongs to another timeline')
    fps = Fraction(str(doc.get('fps', 30)))
    indices = schedule(args.start_us, args.end_us, doc['duration'], fps, args.handles_ms)
    tracks = [t for t in doc.get('tracks', []) if t.get('type') == 'video']
    track = next((t for t in tracks if t['id'] == args.primary_video_track_id), None) if args.primary_video_track_id else (tracks[0] if tracks else None)
    if not track:
        raise ValueError('Primary video track not found')
    range_id = getattr(args, 'range_id', None)
    operation = 'manual'
    if range_id:
        matches = [r for r in required_ranges(edit, track['id']) if r['range_id'] == range_id]
        if len(matches) != 1:
            raise ValueError('Range ID is not an operation in this edit report')
        expected = matches[0]
        if (expected['start_us'], expected['end_us'], expected['track_id']) != (args.start_us, args.end_us, track['id']):
            raise ValueError('Range bounds or primary track differ from the edit report operation')
        operation = expected['operation']
    preview_folder = Path(args.preview).resolve(strict=True)
    if preview_folder.is_relative_to(root):
        raise ValueError('Preview must be an isolated rendering outside the live draft')
    certificate_path = preview_folder/'preview.json'
    certificate = seam.load(certificate_path)
    movie = Path(certificate['preview']).resolve(strict=True)
    if movie.parent != preview_folder or certificate.get('input_sha256') != seam.sha(src) or certificate.get('preview_sha256') != seam.sha(movie):
        raise ValueError('Preview is stale, redirected or belongs to another input')
    context = certificate.get('render_context', {})
    if context.get('copy_root') and Path(context['copy_root']).resolve() != root:
        raise ValueError('Preview copy root differs from the range source root')
    checks = {str(src): seam.sha(src), str(edit_path): seam.sha(edit_path),
              str(certificate_path): seam.sha(certificate_path), str(movie): seam.sha(movie)}
    dependencies = certificate.get('dependency_hashes', {})
    if certificate.get('certificate_version', 0) >= 2 and not dependencies:
        raise ValueError('Current preview certificate lacks dependency hashes')
    for path, digest in dependencies.items():
        resolved = Path(path).resolve(strict=True)
        if seam.sha(resolved) != digest:
            raise ValueError('Preview dependency changed: '+path)
        checks[str(resolved)] = digest
    rendered = seam.probe(args.ffprobe, movie)
    if Fraction(rendered['avg_frame_rate']) != fps:
        raise ValueError('Preview FPS differs from timeline')
    mats, sources, requests, samples = seam.lookup(doc), {}, {}, []
    for n in indices:
        time_us = Fraction(n*1_000_000, 1)/fps
        segment = seam.containing(track['segments'], time_us)
        path = seam.source_path(mats[segment['material_id']], root)
        if str(path) not in sources:
            sources[str(path)] = seam.probe(args.ffprobe, path)
            checks[str(path)] = sources[str(path)]['sha256']
        for ref in segment.get('extra_material_refs', []):
            if mats.get(ref, {}).get('curve_speed'):
                raise ValueError('Cannot map curve speed to source frames')
        source_us = seam.mapping(segment, time_us)
        frame = seam.frame_at(sources[str(path)], source_us)
        if source_us >= mats[segment['material_id']].get('duration', 0):
            raise ValueError('Mapped source time exceeds material duration')
        requests.setdefault(str(path), set()).add(frame)
        samples.append(dict(target_frame=n, target_us=float(time_us), source_path=str(path), source_frame=frame,
                            mapped_source_us=float(source_us), source_pts_seconds=float(sources[str(path)]['times'][frame]),
                            segment_id=segment['id'], region='before' if time_us < args.start_us else 'inside' if time_us < args.end_us else 'after'))
    output.mkdir(parents=True)
    originals = {p: seam.extract_frames(args.ffmpeg, p, frames) for p, frames in requests.items()}
    preview_frames = seam.extract_frames(args.ffmpeg, movie, indices)
    pages, cards = [], []
    for start in range(0, len(samples), 7):
        rows = samples[start:start+7]
        name = f'page-{start//7+1:04d}'
        offsets = [-1 if r['region'] == 'before' else 0 for r in rows]
        for suffix, pixels in [('source', [originals[r['source_path']][r['source_frame']] for r in rows]),
                               ('rendered', [preview_frames[r['target_frame']] for r in rows])]:
            path = output/(name+'-'+suffix+'.png')
            seam.sheet(args.ffmpeg, pixels, path, offsets=offsets)
            checks[str(path)] = seam.sha(path)
        pages.append(dict(source=name+'-source.png', rendered=name+'-rendered.png', samples=rows))
        labels = ' | '.join(f"#{r['target_frame']} {r['target_us']/1e6:.6f}s [{r['region']}] / src#{r['source_frame']}" for r in rows)
        cards.append(f'<section><p>{html.escape(labels)}</p><p>源帧</p><img src="{name}-source.png"><p>实际渲染帧</p><img src="{name}-rendered.png"></section>')
    for path, digest in checks.items():
        if seam.sha(path) != digest:
            raise ValueError('Evidence changed during range sampling: '+path)
    result = dict(schema_version=1, kind='continuous_picture_range', range_id=range_id, operation=operation,
                  timeline_id=doc['id'], track_id=track['id'], primary_video_track_id=track['id'], edit_report=str(edit_path),
                  input_sha256=checks[str(src)], edit_report_sha256=checks[str(edit_path)],
                  preview_certificate_sha256=checks[str(certificate_path)], preview_sha256=checks[str(movie)],
                  start_us=args.start_us, end_us=args.end_us, handles_ms=args.handles_ms, fps=str(fps),
                  target_frame_count=len(indices), first_target_frame=indices[0], last_target_frame=indices[-1],
                  first_display_frame_at_or_after_exit=math.ceil(Fraction(args.end_us, 1_000_000)*fps),
                  pages=pages, dependencies=checks, status='needs_review',
                  scope='Every displayed target frame sampled; source/rendered images and normal-speed review remain separate')
    report = output/'range_review.json'
    seam.save(report, result)
    review_page = decisions_template = None
    if not getattr(args, 'no_html', False):
        decisions_template = output/'decisions.template.json'
        seam.save(decisions_template, dict(schema_version=1, report_sha256=seam.sha(report),
            range_id=range_id, decision='pending', entry_checked=False, interior_checked=False,
            exit_checked=False, normal_speed_review=False, reason=''))
        url = html.escape(movie.as_uri()+f'#t={samples[0]["target_us"]/1e6:.6f},{samples[-1]["target_us"]/1e6:.6f}')
        review_page = output/'review.html'
        review_page.write_text('<!doctype html><meta charset="utf-8"><title>补画面整段检查</title>'
            '<style>body{background:#17191d;color:#eee;font:14px sans-serif;margin:24px}img{max-width:100%}video{max-height:65vh}section{margin:30px 0}</style>'
            '<h1>入口、内部、出口逐帧</h1><p>检查人物短暂回现、叠化尾帧和构图恢复晚一帧；再正常速度看完整动作。未自动判断通过。</p>'
            f'<video controls src="{url}"></video>'+''.join(cards), encoding='utf-8')
    return dict(status='needs_review', report=str(report), review=str(review_page) if review_page else None,
                decisions_template=str(decisions_template) if decisions_template else None, range_id=range_id,
                target_frame_count=len(indices))


def validate_range(args):
    report, decisions = seam.load(args.scan), seam.load(args.decisions)
    if report.get('kind') != 'continuous_picture_range' or decisions.get('report_sha256') != seam.sha(args.scan):
        raise ValueError('Decisions are not bound to this range inspection')
    if decisions.get('range_id') != report.get('range_id'):
        raise ValueError('Range decision identity differs')
    for path, digest in report['dependencies'].items():
        if not Path(path).is_file() or seam.sha(path) != digest:
            raise ValueError('Range dependency changed: '+path)
    issues = []
    if decisions.get('decision') != 'pass':
        issues.append('Range remains pending or needs changes')
    for field in ('entry_checked', 'interior_checked', 'exit_checked', 'normal_speed_review'):
        if decisions.get(field) is not True:
            issues.append(field+' incomplete')
    if not str(decisions.get('reason', '')).strip():
        issues.append('Concrete observation required')
    return dict(status='needs_review' if issues else 'passed', issues=issues, report_sha256=seam.sha(args.scan))
