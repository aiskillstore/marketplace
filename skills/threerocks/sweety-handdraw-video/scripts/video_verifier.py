"""Verify encoded output and require separate evidence for visual acceptance."""
from pathlib import Path
import hashlib
import json
import math
import re
import subprocess
import numpy as np
from PIL import Image


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def build_fingerprint(root):
    root = Path(root)
    timeline = json.loads((root / 'work' / 'timeline.json').read_text())
    paths = [root / 'work' / 'timeline.json', root / 'work' / 'narration.wav', root / 'work' / 'mix.wav',
             root / 'work' / 'audio-mix-report.json', root / 'outputs' / 'cover.png', Path(timeline['hand']['source'])]
    if timeline.get('watermark'):
        paths.append(Path(timeline['watermark']['source']))
    manifest = json.loads((root / 'job.json').read_text())
    if manifest.get('art_direction',{}).get('record'):
        paths.append(root/manifest['art_direction']['record'])
    if not manifest.get('runtime_fixture'):
        paths.append(root/manifest.get('design_file','design.json'))
        from drawing_contract import illustration_actions
        plan_path = root/manifest['drawing_plan']
        paths.extend([root/'style/catalog.json',root/'style/selection.json',root/'style/resolved.json',plan_path,plan_path.with_suffix('.preflight.json'),root/manifest['drawing_review']])
        paths.extend((root/action['outline_mask']).resolve() for action in illustration_actions(manifest) if action.get('outline_mask'))
    if timeline.get('narration_master'):
        from narration_master import verify_compiled_master
        verify_compiled_master(root, timeline)
        paths.append(Path(timeline['narration_master']['alignment']))
    paths.extend(Path(layer['source']) for layer in timeline.get('audio_policy', {}).get('layers', []))
    paths.extend(sorted(Path(__file__).parent.glob('*.py')))
    source_cover = Path(manifest['cover']['source']).expanduser()
    paths.append(source_cover if source_cover.is_absolute() else root / source_cover)
    paths.extend(Path(clip['source']) for clip in timeline['audio_report'])
    for name in sorted(timeline['assets']):
        paths.extend(root / 'work' / 'assets' / f'{name}.{extension}' for extension in ('png', 'npz'))
        if timeline['assets'][name].get('font'):
            paths.append(Path(timeline['assets'][name]['font']['path']))
        if timeline['assets'][name].get('source'):
            paths.append(Path(timeline['assets'][name]['source']))
    digest = hashlib.sha256()
    for path in paths:
        digest.update(file_hash(path).encode())
    return digest.hexdigest()


def match_reveal_to_tip(metadata, reveal, mask, kinds):
    ys, xs = np.where(mask)
    timestamps = reveal[ys, xs].astype(float)
    distances = np.full(len(timestamps), np.inf)
    radii = np.zeros(len(timestamps))
    for segment in metadata['segments']:
        if segment['kind'] not in kinds:
            continue
        selected = (timestamps >= segment['start'] - 2e-7) & (timestamps <= segment['end'] + 2e-7)
        if not selected.any():
            continue
        points = np.array(segment['points'])
        lengths = np.array(segment['lengths'])
        along = np.clip((timestamps[selected] - segment['start']) / max(1e-8, segment['end'] - segment['start']), 0, 1) * lengths[-1]
        separation = np.hypot(xs[selected] - np.interp(along, lengths, points[:, 0]), ys[selected] - np.interp(along, lengths, points[:, 1]))
        distances[selected] = np.minimum(distances[selected], separation)
        radii[selected] = np.maximum(radii[selected], segment.get('radius', 0))
    return distances, radii


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_assets(root, timeline):
    entries = []
    for name, metadata in timeline['assets'].items():
        artwork = np.array(Image.open(root / 'work' / 'assets' / f'{name}.png').convert('RGBA'))
        maps = np.load(root / 'work' / 'assets' / f'{name}.npz')
        alpha = artwork[:, :, 3]
        entry = {'name': name, 'type': metadata['type']}
        if metadata['type'] == 'typeset_caption':
            mask = alpha > 0
            margin = metadata['safe_margin']
            require(mask.any() and not mask[:margin].any() and not mask[-margin:].any() and not mask[:, :margin].any() and not mask[:, -margin:].any(), f'{name}: empty or clipped caption')
            require(not metadata['segments'], f'{name}: captions must be static typeset text')
            entries.append({**entry, 'lines': len(metadata['lines']), 'font': metadata['font'], 'background': metadata.get('background')})
            continue
        require(bool(metadata['segments']), f'{name}: no drawing segments')
        from drawing_contract import validate_strokes
        validate_strokes(metadata)
        if metadata['type'] == 'illustration':
            require('owners' in maps and bool(metadata.get('parts')), f'{name}: missing semantic ownership')
            require((maps['owners'][alpha>0]>=0).all(), f'{name}: unowned illustration pixels')
            parts=metadata['parts']
            require(max(part['outline_end'] for part in parts)<=min(part['fill_start'] for part in parts)+1e-6,
                    f'{name}: filling starts before all outlines are complete')
            for phase,channel in [('outline','ink'),('fill','color')]:
                previous_end=0.
                for index,part in enumerate(parts):
                    require(part[phase+'_start']>=previous_end-1e-6,f'{name}: semantic part order is broken')
                    previous_end=part[phase+'_end']
                    selected=(alpha>0)&(maps['owners']==index)&np.isfinite(maps[channel])
                    if selected.any():
                        times=maps[channel][selected]
                        require(times.min()>=part[phase+'_start']-1e-6 and times.max()<=part[phase+'_end']+1e-6,
                                f'{name}: pixels leak into another semantic part interval')
            entry['semantic_parts_in_order']=[part['id'] for part in parts]
            ink_mask = (alpha > 0) & (maps['ink_weight'] > .01)
            if ink_mask.any():
                distances, _ = match_reveal_to_tip(metadata, maps['ink'], ink_mask, {'ink'})
                require(np.isfinite(distances).all() and distances.max() < 9, f'{name}: ink is too far from the nib')
                entry['ink_tip_max_distance_px'] = float(distances.max())
            color_mask = (alpha > 0) & (maps['ink_weight'] < .99)
            if color_mask.any():
                distances, radii = match_reveal_to_tip(metadata, maps['color'], color_mask, {'color'})
                require(np.isfinite(distances).all() and (radii > 0).all(), f'{name}: unpainted color pixels')
                require((distances <= radii + .04).all(), f'{name}: color outside the active brush')
                entry['paint_max_overshoot_px'] = float((distances - radii).max())
        else:
            mask = alpha > 0
            require(mask.any(), f'{name}: empty text or marker')
            distances, radii = match_reveal_to_tip(metadata, maps['reveal'], mask, {'ink', 'brush'})
            require(np.isfinite(distances).all(), f'{name}: missing reveal times')
            if metadata['type'] == 'handwritten_text':
                margin=int(metadata.get('safe_margin',0))
                require(margin>=5,f'{name}: missing font-boundary padding; rebuild text assets')
                require(not mask[:margin].any() and not mask[-margin:].any() and
                        not mask[:,:margin].any() and not mask[:,-margin:].any(),
                        f'{name}: glyph touches the image edge and may be clipped')
                require('owners' in maps and metadata.get('characters'),f'{name}: missing glyph isolation')
                require((maps['owners'][mask]>=0).all(),f'{name}: unowned glyph pixels')
                for glyph in metadata['characters']:
                    selected=mask&(maps['owners']==glyph['index'])
                    if selected.any():
                        times=maps['reveal'][selected]
                        require(times.min()>=glyph['start']-1e-6 and times.max()<=glyph['end']+1e-6,
                                f'{name}: a future character appears early')
                entry['isolated_characters']=len(metadata['characters'])
                require(distances.max() < 9, f'{name}: text is too far from the nib')
            else:
                require((distances <= radii + .04).all(), f'{name}: marker outside the active brush')
            entry['maximum_tip_distance_px'] = float(distances.max())
        entries.append(entry)
    return entries


def verify_job(job_directory, assets_only=False):
    root = Path(job_directory).resolve()
    work, output = root / 'work', root / 'outputs'
    timeline = json.loads((work / 'timeline.json').read_text())
    from art_direction import verify_art_direction
    art_review=verify_art_direction(root,json.loads((root/'job.json').read_text()))
    report = {'duration_seconds': timeline['duration'], 'art_direction':art_review,'checks': {}, 'assets': verify_assets(root, timeline), 'pages': []}
    if assets_only:
        print(json.dumps({'assets_checked': len(report['assets'])}))
        return report
    from timeline_contract import validate_timeline,validate_cover
    from video_renderer import Renderer
    validate_timeline(timeline)
    from subtitle_contract import validate_subtitle_delivery
    report['subtitles'] = validate_subtitle_delivery(output / 'film.mp4')
    validate_cover(Renderer(root))
    canvas = timeline['canvas']
    for page in timeline['pages']:
        primary = sorted((event for event in page['events'] if not event['caption']), key=lambda event: event['start'])
        require(all(left['end'] <= right['start'] for left, right in zip(primary, primary[1:])), 'Main pen events overlap')
        require(page['last_drawing_end'] <= page['speech_end'] - .45, 'Drawing overruns narration')
        for event in page['events']:
            asset = timeline['assets'][event['asset']]
            require(0 <= event['x'] and event['x'] + asset['width'] <= canvas['width'], 'Horizontal overflow')
            require(0 <= event['y'] and event['y'] + asset['height'] <= canvas['height'], 'Vertical overflow')
            require(event['end'] > event['start'], 'Empty drawing event')
        report['pages'].append({'page': page['index'] + 1, 'duration_seconds': page['end'] - page['start'],
            'drawing_completed_before_speech_end_seconds': page['speech_end'] - page['last_drawing_end']})
    previous_end = 0
    for cue in timeline['cues']:
        require(previous_end <= cue['start'] < cue['end'] <= timeline['duration'], 'Subtitle order/range error')
        previous_end = cue['end']
    video = output / 'film.mp4'
    render_record = json.loads((work / 'render-record.json').read_text())
    require(timeline['manifest_sha256'] == file_hash(root / 'job.json'), 'Manifest changed after build; build and render again')
    require(render_record['build_fingerprint'] == build_fingerprint(root), 'Inputs changed after rendering; build and render again')
    require(render_record['video_sha256'] == file_hash(video), 'Encoded file changed after rendering')
    metadata = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(video)]))
    video_stream = next(stream for stream in metadata['streams'] if stream['codec_type'] == 'video')
    audio_stream = next(stream for stream in metadata['streams'] if stream['codec_type'] == 'audio')
    require((video_stream['width'], video_stream['height'], video_stream['avg_frame_rate']) == (canvas['width'], canvas['height'], f"{canvas['fps']}/1"), 'Unexpected dimensions or frame rate')
    require(video_stream['codec_name'] == 'h264' and audio_stream['codec_name'] == 'aac', 'Unexpected delivery codec')
    require(abs(float(video_stream['duration']) - float(audio_stream['duration'])) < .08, 'Audio/video durations diverge')
    require(abs(float(video_stream['duration']) - timeline['duration']) < max(.08, 1 / canvas['fps'] + .001), 'Film is not the complete narration timeline')
    decode = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(video), '-f', 'null', '-'], capture_output=True, text=True)
    require(decode.returncode == 0 and not decode.stderr.strip(), 'Full decode failed: ' + decode.stderr)
    volume = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(video), '-af', 'loudnorm=I=-17:TP=-2:LRA=7:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
    match = re.search(r'\{\s*"input_i".*?\}', volume.stderr, re.S)
    require(bool(match), 'Loudness measurement failed')
    report['audio_mix'] = json.loads((work/'audio-mix-report.json').read_text())
    require(report['audio_mix']['layers'] == timeline.get('audio_policy', {}).get('layers', []), 'Mixed audio layers differ from approved audio policy')
    report['ending_review'] = timeline.get('ending_review')
    expected_audio = np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(work/'mix.wav'),'-ac','1','-ar','48000','-f','f32le','-']),dtype='<f4')
    encoded_audio = np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-vn','-ac','1','-ar','48000','-f','f32le','-']),dtype='<f4')
    common_samples = min(len(expected_audio),len(encoded_audio))
    require(abs(len(expected_audio)-len(encoded_audio))/48000 < .08, 'Encoded audio loses part of the intended track')
    audio_correlation = float(np.corrcoef(expected_audio[:common_samples],encoded_audio[:common_samples])[0,1])
    require(audio_correlation > .99, 'Encoded audio differs from the intended narration mix')
    tail = timeline.get('ending_review')
    if tail:
        last_voice = round((timeline['cover_seconds'] + tail['last_active_seconds'])*48000)
        tail_start = max(0,last_voice-2*48000)
        tail_correlation = float(np.corrcoef(expected_audio[tail_start:last_voice],encoded_audio[tail_start:last_voice])[0,1])
        require(tail_correlation > .98, 'Encoding changed or cut the final spoken phrase')
        report['ending_review'] = {**tail,'final_phrase_encoding_correlation':tail_correlation}
    report['audio_track_correlation'] = audio_correlation
    report['loudness'] = json.loads(match.group())
    require(-20 < float(report['loudness']['input_i']) < -14, 'Loudness outside expected narration range')
    require(float(report['loudness']['input_tp']) < -1, 'True peak too high')
    sample_times = [0] + [page['speech_end'] - .2 for page in timeline['pages']]
    frames = []
    for index, time in enumerate(sample_times):
        path = work / 'review' / f'decoded-{index:02d}.jpg'
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(time), '-i', str(video), '-frames:v', '1', str(path)], check=True)
        frame = Image.open(path).convert('RGB')
        frame.thumbnail((640, 360))
        frames.append(frame)
    sheet = Image.new('RGB', (1280, math.ceil(len(frames) / 2) * 360), '#FBF9F1')
    for index, frame in enumerate(frames):
        sheet.paste(frame, ((index % 2) * 640, (index // 2) * 360))
    sheet.save(work / 'review' / 'decoded-contact.jpg', quality=95)
    report.update(status='engineering_passed_review_required', video_sha256=file_hash(video), cover_sha256=file_hash(output / 'cover.png'),
                  build_fingerprint=render_record['build_fingerprint'], frames=video_stream.get('nb_frames'), bytes=int(metadata['format']['size']))
    report['checks'] = {'full_decode': True, 'complete_timeline': True, 'paths_and_paint_coverage': True,
                        'narration_controls_drawing_time': True, 'canvas_bounds': True, 'subtitle_order': True, 'loudness': True, 'semantic_part_order':True, 'glyph_isolation':True, 'arm_continues_off_canvas':True, 'cover_half_second_still_and_fade':True, 'mandatory_art_direction':True}
    (work / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    review_path = root / 'review.json'
    if not review_path.exists():
        review = {'video_sha256': report['video_sha256'], **{category: {'status': 'not_checked', 'evidence': ''}
                    for category in ('content', 'visual', 'motion', 'audio', 'privacy')}, 'limitations': []}
        review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2))
    print(json.dumps({key: value for key, value in report.items() if key not in ('assets', 'pages')}, ensure_ascii=False, indent=2))
    return report


def finalize_job(job_directory):
    root = Path(job_directory).resolve()
    report = json.loads((root / 'work' / 'verification.json').read_text())
    review = json.loads((root / 'review.json').read_text())
    video_hash = file_hash(root / 'outputs' / 'film.mp4')
    require(not json.loads((root/'job.json').read_text()).get('runtime_fixture'), 'Runtime fixtures can never be delivered as finished films')
    require(report['status'] == 'engineering_passed_review_required', 'Engineering checks must pass first')
    require(report['video_sha256'] == review['video_sha256'] == video_hash, 'Review belongs to a different video')
    timeline = json.loads((root / 'work' / 'timeline.json').read_text())
    require(timeline['manifest_sha256'] == file_hash(root / 'job.json'), 'Manifest changed since build')
    require(report['build_fingerprint'] == build_fingerprint(root), 'Inputs changed since verification')
    for category in ('content', 'visual', 'motion', 'audio', 'privacy'):
        decision = review.get(category, {})
        require(decision.get('status') == 'pass' and bool(decision.get('evidence', '').strip()), f'{category} review is incomplete or failed')
    receipt = {'status': 'delivery_review_completed', 'engineering': report, 'review': review}
    (root / 'outputs' / 'verification.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2))
    lines = ['交付检查记录', f"视频 SHA-256：{video_hash}", f"片长：{report['duration_seconds']:.3f}秒", '工程检查：通过']
    for category in ('content', 'visual', 'motion', 'audio', 'privacy'):
        lines.append(f"{category}：{review[category]['evidence']}")
    lines += ['未验证或限制：'] + (review.get('limitations') or ['未另行记录；不代表任意主题或平台均已验证。'])
    (root / 'outputs' / 'verification.txt').write_text('\n'.join(lines) + '\n')
    print(str(root / 'outputs' / 'verification.txt'))
