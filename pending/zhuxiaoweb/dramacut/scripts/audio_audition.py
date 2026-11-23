"""Render hash-bound native SFX full / without / solo listening windows.

This is a diagnostic renderer. It never writes a live draft and never marks an
event listened or relevant automatically.
"""
from __future__ import annotations
import argparse, copy, hashlib, html, json, math, re, subprocess, sys, wave
from pathlib import Path
sys.dont_write_bytecode = True
from timeline_ops import EditError, bounds, crop, editable, lookup, validate_document


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def load(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def save(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2,allow_nan=False)


def run(argv, timeout=210, log=None):
    if log:
        with Path(log).open('wb') as stream:
            result=subprocess.run(list(map(str,argv)),stdout=stream,stderr=subprocess.STDOUT,
                                  timeout=timeout,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        if result.returncode:raise ValueError(f'Native render failed; inspect {log}')
        return result
    result=subprocess.run(list(map(str,argv)),capture_output=True,timeout=timeout,
                          creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    if result.returncode:raise ValueError(result.stderr.decode('utf-8','replace')[-1800:])
    return result


def window_document(prepared, start_us, end_us, selected_id, mode):
    if mode not in ('full','without','solo'):raise ValueError('Unknown audition mode')
    doc=copy.deepcopy(prepared);mats=lookup(doc);tracks=[];found=False
    for track in doc['tracks']:
        if track['type']=='text':continue  # This copy evaluates audio only.
        if track['type'] not in ('video','audio'):
            if track.get('segments'):raise ValueError('Audition does not support non-video/audio tracks')
            continue
        segments=[]
        for segment in track['segments']:
            left,right=bounds(segment)
            if left>=end_us or right<=start_us:continue
            editable(segment,track['type'],mats,set())
            chosen=segment['id']==selected_id
            if chosen:
                if track['type']!='audio':raise ValueError('Selected SFX must be an audio segment')
                found=True
            item=crop(doc,segment,track['type'],max(start_us,left),min(end_us,right),
                      lambda t:t-start_us,set())
            if (mode=='without' and chosen) or (mode=='solo' and not chosen):
                item['volume']=0.0;item['common_keyframes']=[];item['last_nonzero_volume']=0.0
            segments.append(item)
        if segments:
            track['segments']=segments;tracks.append(track)
    if not found:raise ValueError('Selected SFX is absent from the audition window')
    doc['tracks']=tracks;doc['duration']=end_us-start_us
    validate_document(doc)
    return doc


def full_timeline_group_document(prepared, selected_ids, mode):
    """Keep authored timing/effects; group use requires independent-window prechecks."""
    if mode not in ('full','without','solo'):
        raise ValueError('Unknown audition mode')
    selected_ids = set(selected_ids)
    doc = copy.deepcopy(prepared)
    found = {identifier: 0 for identifier in selected_ids}
    for track in doc['tracks']:
        for segment in track.get('segments', []):
            chosen = segment.get('id') in selected_ids
            if chosen:
                if track.get('type') != 'audio':
                    raise ValueError('Selected SFX must be an audio segment')
                found[segment['id']] += 1
            if track.get('type') not in ('video', 'audio'):
                continue
            if (mode == 'without' and chosen) or (mode == 'solo' and not chosen):
                segment['volume'] = 0.0
                segment['common_keyframes'] = []
                segment['last_nonzero_volume'] = 0.0
    if not found or any(count != 1 for count in found.values()):
        raise ValueError('Selected SFX must identify exactly one native audio segment')
    validate_document(doc)
    return doc


def full_timeline_document(prepared, selected_id, mode):
    return full_timeline_group_document(prepared, {selected_id}, mode)


def event_context(prepared, event):
    target = event['target_us']
    return max(0, target-800000), min(prepared['duration'], max(target+1200000, event['end_us']+300000))


def prove_independent_events(prepared, events):
    """Check a narrowly supported signal model; native equivalence is not assumed."""
    if not events:
        raise ValueError('Batch requires at least one selected SFX event')
    ids = [e['segment_id'] for e in events]
    if len(ids) != len(set(ids)):
        raise ValueError('Batch has duplicate selected SFX IDs')
    validate_document(prepared)
    from preview_draft import material_lookup
    mats = material_lookup(copy.deepcopy(prepared))
    segments = {s['id']: (t, s) for t in prepared['tracks'] for s in t.get('segments', [])}
    dynamic_tokens = ('master', 'bus', 'compress', 'limiter', 'normalize', 'normalise',
                      'loudness', 'audio_effect', 'audiofx', 'audio_dynamics')

    def reject_dynamic(value, path):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == 'common_keyframes':
                    continue
                if any(token in key.casefold() for token in dynamic_tokens) and item:
                    raise ValueError('Batch rejects possible stateful processing: '+path+'/'+key+'; use per-event --full-timeline')
                reject_dynamic(item, path+'/'+key)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                reject_dynamic(item, path+'/'+str(index))

    safe_material_groups = {'videos', 'photos', 'audios', 'audio_fades', 'speeds', 'placeholder_infos',
                            'canvas_colors', 'canvas_blurs', 'beats', 'vocal_separations', 'sound_channel_mappings', 'texts'}
    for group, rows in prepared.get('materials', {}).items():
        if rows and group not in safe_material_groups:
            raise ValueError('Batch rejects unproved material group '+group+'; use per-event --full-timeline')
    reject_dynamic(prepared, 'timeline')
    try:
        for track in prepared['tracks']:
            if track.get('type') not in ('video', 'audio'):
                if track.get('type') != 'text' and track.get('segments'):
                    raise ValueError('Batch rejects an unproved non-audio/video track; use per-event --full-timeline')
                continue
            if track.get('common_keyframes'):
                raise ValueError('Batch rejects track automation; use per-event --full-timeline')
            for segment in track.get('segments', []):
                if segment.get('common_keyframes'):
                    raise ValueError('Batch rejects segment automation; use per-event --full-timeline')
                editable(segment, track['type'], mats, set())
    except EditError as exc:
        raise ValueError('Batch requires an entirely ordinary editable timeline; use per-event --full-timeline: '+str(exc)) from exc

    windows, selected = [], []
    for event in events:
        pair = segments.get(event['segment_id'])
        if pair is None or pair[0].get('type') != 'audio':
            raise ValueError('Batch selected SFX is missing or not audio')
        track, segment = pair
        left, right = bounds(segment)
        start, end = event_context(prepared, event)
        if (left, right) != (event['start_us'], event['end_us']):
            raise ValueError('Batch report target range differs from the selected SFX')
        if not left <= event['target_us'] < right or left+event.get('attack_offset_us', -1) != event['target_us']:
            raise ValueError('Batch report attack anchor differs from the selected SFX')
        if not start <= left < right <= end:
            raise ValueError('Batch cue extends outside its own event context; use per-event --full-timeline')
        material = mats[segment['material_id']]
        path = Path(material.get('path', '')).resolve(strict=True)
        if path.suffix.casefold() != '.wav':
            raise ValueError('Batch requires a prepared independent PCM WAV SFX')
        with wave.open(str(path), 'rb') as stream:
            if stream.getcomptype() != 'NONE' or stream.getsampwidth() not in (1, 2, 3, 4):
                raise ValueError('Batch requires integer PCM WAV SFX')
        windows.append({'segment_id': segment['id'], 'context_start_us': start, 'context_end_us': end,
                        'cue_start_us': left, 'cue_end_us': right})
        selected.append({'segment_id': segment['id'], 'path': str(path), 'sha256': sha(path),
                         'source_timerange': segment['source_timerange'], 'target_timerange': segment['target_timerange']})
    for i, current in enumerate(windows):
        for other in windows[i+1:]:
            if current['context_start_us'] < other['context_end_us'] and other['context_start_us'] < current['context_end_us']:
                raise ValueError('Batch event contexts overlap; use per-event --full-timeline')
    for current in windows:
        for other in windows:
            if current['segment_id'] != other['segment_id'] and other['cue_start_us'] < current['context_end_us'] and current['context_start_us'] < other['cue_end_us']:
                raise ValueError('Batch removed/retained cue intersects another event context; use per-event --full-timeline')
    return {'status': 'structural_prechecks_passed', 'selected_ids': ids, 'windows': windows,
            'selected_sources': selected,
            'scope': 'No dynamic fields or unproved processing anywhere in this bound document; disjoint contexts contain independent integer-PCM cues with local static gain/fades only.',
            'native_equivalence': 'Not assumed. Review the actual full/without/solo renders; lossy encoder history and engine mixing can differ between batch and per-event renders.'}



def stats(ffmpeg, path, start, end):
    if end<=start:raise ValueError('Empty audio measurement window')
    result=run([ffmpeg,'-nostdin','-hide_banner','-v','info','-ss',f'{start:.6f}',
                '-i',path,'-t',f'{end-start:.6f}','-map','0:a:0','-vn',
                '-af','astats','-f','null','-'])
    text=result.stderr.decode('utf-8','replace')
    def value(label):
        rows=re.findall(re.escape(label)+r': (-?(?:[\d.]+|inf))',text,re.I)
        if not rows:return None
        number=float(rows[-1]);return number if math.isfinite(number) else None
    return {'start_seconds':start,'end_seconds':end,'peak_dbfs':value('Peak level dB'),
            'rms_dbfs':value('RMS level dB')}


def playback_graph(value):
    """Compare the active playback graph, permitting only media relocation and exact duplicate cleanup."""
    from preview_draft import material_lookup
    doc=copy.deepcopy(value);mats=material_lookup(doc)
    def refs(item):
        if isinstance(item,dict):
            return set().union(*(refs(v) for v in item.values())) if item else set()
        if isinstance(item,list):
            return set().union(*(refs(v) for v in item)) if item else set()
        return {item} if isinstance(item,str) and item in mats else set()
    active=refs({k:v for k,v in doc.items() if k!='materials'});queue=list(active)
    while queue:
        for identifier in refs(mats[queue.pop()]):
            if identifier not in active:active.add(identifier);queue.append(identifier)
    for group,rows in doc['materials'].items():
        if isinstance(rows,list):doc['materials'][group]=[m for m in rows if isinstance(m,dict) and m.get('id') in active]
    from draft_workspace import without_active_media_paths
    return without_active_media_paths(doc)


def bind_draft_resource_paths(original, prepared, copy_root, checks):
    """Accept only exact in-copy placeholder resolution for nested draft resources."""
    from draft_workspace import media_path
    value = copy.deepcopy(original)
    old = {m['id']: m for m in value.get('materials', {}).get('drafts', []) if isinstance(m, dict) and 'id' in m}
    new = {m['id']: m for m in prepared.get('materials', {}).get('drafts', []) if isinstance(m, dict) and 'id' in m}
    root = Path(copy_root).resolve(strict=True)
    for identifier, material in old.items():
        other = new.get(identifier)
        if other is None:
            continue
        for key in ('draft_config_path', 'draft_file_path', 'draft_cover_path'):
            raw = material.get(key)
            resolved = other.get(key)
            if raw == resolved:
                continue
            if not isinstance(raw, str) or not raw.startswith('##_draftpath_placeholder_'):
                raise ValueError('Preset resource path changed beyond placeholder resolution: '+key)
            expected = media_path(raw, root)
            if not expected.is_relative_to(root) or Path(resolved).resolve() != expected:
                raise ValueError('Preset resource does not match the verified copy: '+key)
            if expected.is_file():
                checks[str(expected)] = sha(expected)
            elif key != 'draft_cover_path':
                raise ValueError('Preset playback/config resource is missing: '+key)
            material[key] = resolved
    return value


def validate_bindings(args):
    source=Path(args.input).resolve(strict=True);report=Path(args.edit_report).resolve(strict=True)
    folder=Path(args.preview).resolve(strict=True);certpath=folder/'preview.json'
    cert=load(certpath);edit=load(report);prepared_path=folder/'draft_content.json'
    checks={str(source):sha(source),str(report):sha(report),str(certpath):sha(certpath),
            str(prepared_path):sha(prepared_path)}
    if checks[str(source)]!=cert.get('input_sha256') or checks[str(source)]!=edit.get('output_sha256'):
        raise ValueError('Input, preview and edit report must describe the same exact JSON')
    if cert.get('certificate_version',0)<2 or not cert.get('dependency_hashes'):
        raise ValueError('Use a current hash-bound native preview certificate')
    video=Path(cert['preview']).resolve(strict=True)
    if video.parent!=folder or sha(video)!=cert.get('preview_sha256'):
        raise ValueError('Preview artifact is missing, redirected or changed')
    checks[str(video)]=sha(video)
    for path,digest in cert['dependency_hashes'].items():
        if sha(path)!=digest:raise ValueError(f'Preview dependency changed: {path}')
        checks[str(Path(path).resolve())]=digest
    if str(Path(args.codec).resolve())!=str(Path(cert['render_context']['codec']).resolve()):
        raise ValueError('Audition codec must match preview codec')
    if Path(args.runtime).resolve()!=Path(cert['render_context']['runtime']).resolve():
        raise ValueError('Audition runtime must match preview runtime')
    checks[str(Path(args.ffmpeg).resolve())]=sha(args.ffmpeg)
    checks[str(Path(__file__).resolve())]=sha(__file__)
    checks[str(Path(__file__).with_name('timeline_ops.py').resolve())]=sha(Path(__file__).with_name('timeline_ops.py'))
    prepared=load(prepared_path)
    if prepared.get('id')!=load(source).get('id') or prepared.get('duration')!=load(source).get('duration'):
        raise ValueError('Prepared preview document identity/duration differs')
    if cert.get('unresolved_cache_paths'):
        raise ValueError('Preview has unresolved media/cache references')
    # Binding the prepared document guards against path resolution changing playback.
    original = bind_draft_resource_paths(load(source), prepared, cert['render_context']['copy_root'], checks)
    if playback_graph(prepared) != playback_graph(original):
        raise ValueError('Prepared preview document differs beyond active media paths')
    return prepared,edit,cert,checks


def verify_manifest(path):
    data=load(path)
    if data.get('kind')!='native_sfx_audition' or data.get('status')!='rendered':
        raise ValueError('Audition manifest is not complete')
    for section in ('bindings','artifacts'):
        for name,digest in data.get(section,{}).items():
            if sha(name)!=digest:raise ValueError(f'Audition {section} changed: {name}')
    return data


def audition(args):
    prepared,edit,cert,checks=validate_bindings(args)
    output=Path(args.output).resolve()
    roots=[Path(cert['render_context'][k]).resolve() for k in ('copy_root','source_root','support_dir','cache_dir','app_dir','runtime') if cert['render_context'].get(k)]
    if any(output.is_relative_to(p) for p in roots):raise ValueError('Audition output must be outside drafts, backend and cache')
    if output.exists():raise ValueError('Use a new audition directory')
    events=[e for e in edit.get('sfx',[]) if e.get('mix_role')=='sfx' and
            (not args.segment_id or e.get('segment_id') in args.segment_id)]
    if args.segment_id and set(args.segment_id)-{e['segment_id'] for e in events}:
        raise ValueError('Unknown or non-SFX segment ID requested')
    batch = bool(getattr(args, 'batch_independent_events', False))
    if batch and not getattr(args, 'full_timeline', False):
        raise ValueError('--batch-independent-events requires explicit --full-timeline')
    proof = prove_independent_events(prepared, events) if batch else None
    output.mkdir(parents=True)
    records = []
    artifacts = {}
    shared_native = {}
    try:
        for index,event in enumerate(events,1):
            target = event['target_us']
            start, end = event_context(prepared, event)
            folder = output/f'event-{index:03d}'
            folder.mkdir()
            files = {}
            measurements = {}
            radius_start = max(0, (target-start)/1e6-.08)
            radius_end = min((end-start)/1e6, (target-start)/1e6+.08)
            for mode in ('full','without','solo'):
                complete = bool(getattr(args, 'full_timeline', False))
                movie = folder/f'{mode}.mp4'
                if batch and mode in shared_native:
                    jsonpath, native_movie, log = shared_native[mode]
                else:
                    render_folder = output/'shared-native' if batch else folder
                    render_folder.mkdir(exist_ok=True)
                    if batch:
                        doc = full_timeline_group_document(prepared, proof['selected_ids'], mode)
                    elif complete:
                        doc = full_timeline_document(prepared, event['segment_id'], mode)
                    else:
                        doc = window_document(prepared, start, end, event['segment_id'], mode)
                    jsonpath = render_folder/f'{mode}.json'
                    save(jsonpath, doc)
                    log = render_folder/f'{mode}.log'
                    native_movie = render_folder/f'{mode}.timeline.mp4' if complete else movie
                    run([args.codec,'-ex',jsonpath,'-o',native_movie,'--jy-dir',args.runtime,
                         '--size','270x480','--fps',str(prepared.get('fps',60)),
                         '--bitrate','900K','--codec','h264','--hard-encode','0',
                         '--timeout','180','-j','1','-q'],log=log)
                    if not native_movie.is_file() or not native_movie.stat().st_size:
                        raise ValueError('Native render produced no media')
                    if batch:
                        shared_native[mode] = (jsonpath, native_movie, log)
                wav = folder/f'{mode}.wav'
                trim = ['-ss',f'{start/1e6:.6f}','-t',f'{(end-start)/1e6:.6f}'] if complete else []
                run([args.ffmpeg,'-nostdin','-v','error','-i',native_movie,*trim,'-map','0:a:0',
                     '-vn','-acodec','pcm_s24le',wav])
                if complete:
                    run([args.ffmpeg,'-nostdin','-v','error','-i',native_movie,*trim,'-map','0:v:0','-map','0:a:0',
                         '-c:v','libx264','-preset','fast','-crf','23','-c:a','aac','-b:a','192k',movie])
                    artifacts[str(native_movie)] = sha(native_movie)
                measurements[mode] = {'attack':stats(args.ffmpeg,wav,radius_start,radius_end),
                                      'context':stats(args.ffmpeg,wav,0,(end-start)/1e6)}
                files[mode] = {'video':str(movie), 'audio':str(wav),
                               'native_full_timeline_video':str(native_movie) if complete else None,
                               'trim_start_us':start if complete else 0,
                               'trim_end_us':end if complete else end-start}
                for path in (jsonpath,movie,wav,log):
                    artifacts[str(path)] = sha(path)
            solo=measurements['solo']['attack']['rms_dbfs'];background=measurements['without']['attack']['rms_dbfs']
            ratio=solo-background if solo is not None and background is not None else None
            warnings=[]
            if solo is None or solo < -36:warnings.append('very_low_solo_attack_check_source_selection_and_attack')
            if ratio is not None and ratio < -18:warnings.append('possible_masking_compare_AB_or_duck_competing_layer')
            if any(x['context']['peak_dbfs'] is not None and x['context']['peak_dbfs']>-1 for x in measurements.values()):
                warnings.append('peak_above_minus_1_dbfs_review_headroom')
            records.append({'segment_id':event['segment_id'],'event_id':event.get('event_id'),
                            'purpose':event.get('purpose',''),
                            'render_mode':'batch_independent_full_timeline_then_trim' if batch else 'full_timeline_then_trim' if getattr(args,'full_timeline',False) else 'window',
                            'target_us':target,'context_start_us':start,
                            'context_end_us':end,'files':files,'measurements':measurements,
                            'solo_minus_without_attack_rms_db':ratio,'warnings':warnings,
                            'listened':False,'scene_relevance_verified':False,
                            'evidence_scope':'native-rendered stems and A/B; measurements are not human perceptibility or scene-relevance proof'})
        if any(sha(p)!=digest for p,digest in checks.items()):raise ValueError('Input or dependency changed during audition')
        webpage = None
        if not getattr(args, 'no_html', False):
            page=['<!doctype html><meta charset="utf-8"><title>SFX A/B</title><h1>SFX A/B and solo</h1>',
                  '<p>Listen to full, without and solo at the same player/device volume. The image is diagnostic; subtitles are omitted.</p>']
            for i,row in enumerate(records,1):
                page.append(f'<h2>{i}. {html.escape(row["purpose"])}</h2><p>{html.escape(str(row["warnings"]))}</p>')
                for mode in ('full','without','solo'):
                    relative=Path(row['files'][mode]['video']).relative_to(output).as_posix()
                    page.append(f'<p>{mode}</p><video controls width="180" src="{html.escape(relative)}"></video>')
            webpage=output/'audition.html';webpage.write_text('\n'.join(page),encoding='utf-8');artifacts[str(webpage)]=sha(webpage)
        result={'schema_version':1,'kind':'native_sfx_audition','status':'rendered','input_sha256':sha(args.input),
                'edit_report_sha256':sha(args.edit_report),'preview_sha256':cert['preview_sha256'],
                'bindings':checks,'artifacts':artifacts,'events':records,
                'full_timeline_mode':bool(getattr(args,'full_timeline',False)),
                'batch_independence':proof,'shared_native_render_count':len(shared_native),
                'subjective_audio_listening':False}
        save(output/'audition.json',result)
        if not getattr(args, 'no_html', False):
            save(output/'listening.template.json',{'schema_version':1,'audition_sha256':sha(output/'audition.json'),
                 'events':[{'segment_id':r['segment_id'],'listened':False,'scene_relevance_verified':False,
                            'attack_alignment_verified':False,'dialogue_clear':False,'perceptible':False,
                            'decision':'pending','anchor':'','notes':''} for r in records]})
        return {'status':'rendered','manifest':str(output/'audition.json'),'html':str(webpage) if webpage else None,'event_count':len(records),
                'subjective_audio_listening':False}
    except Exception as exc:
        save(output/'failure.json',{'status':'failed','error':str(exc),'bindings':checks,'completed_events':records})
        raise


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('input','preview','edit-report','output','ffmpeg','codec','runtime'):p.add_argument('--'+name,required=True)
    p.add_argument('--segment-id',action='append',help='Only this report SFX segment; repeat to select several')
    p.add_argument('--full-timeline',action='store_true',help='Render each full/without/solo complete native timeline before trimming the listening window')
    p.add_argument('--batch-independent-events',action='store_true',help='With --full-timeline: reuse three native renders only after conservative independent-window checks')
    p.add_argument('--no-html',action='store_true',help='Write hash-bound media and JSON evidence without human listening pages/templates')
    args=p.parse_args()
    try:print(json.dumps(audition(args),ensure_ascii=False,indent=2,allow_nan=False))
    except (OSError,ValueError,KeyError,TypeError,EditError,subprocess.TimeoutExpired) as exc:p.exit(1,f'Audio audition unavailable: {exc}\n')


if __name__=='__main__':main()
