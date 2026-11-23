"""Prepare referenced/embedded audio and inspect captions/voice activity without rendering a full video."""
from __future__ import annotations
import argparse,json,math,subprocess,sys
from array import array
from pathlib import Path
sys.dont_write_bytecode=True
from preview_draft import directory,material_lookup,check_media,save,fingerprint

def run(argv):
    p=subprocess.run(list(map(str,argv)),capture_output=True,timeout=210)
    if p.returncode:raise ValueError(p.stderr.decode('utf-8','replace')[-1200:])
    return p.stdout
def bounds(s):
    r=s['target_timerange'];return r.get('start',0),r.get('start',0)+r['duration']
def interp(points,t):
    if t<=points[0][0]:return points[0][1]
    for (a,v),(b,w) in zip(points,points[1:]):
        if a<=t<=b:return v+(w-v)*(t-a)/(b-a)
    return points[-1][1]


def energy_dip_candidates(activity, captions, unknown, min_gap_us=180_000, min_run_us=40_000):
    """Find bounded energy dips even inside one caption, using only measured voice."""
    anchors = []
    for run in activity:
        start, end = run['start_us'], run['end_us']
        if anchors and start - anchors[-1][1] < min_run_us:
            anchors[-1] = (anchors[-1][0], end)
        else:
            anchors.append((start, end))
    anchors = [(a, b) for a, b in anchors if b-a >= min_run_us]
    result = []
    for (_, start), (end, _) in zip(anchors, anchors[1:]):
        if end-start < min_gap_us:
            continue
        inside = [c['segment_id'] for c in captions if c['start_us'] < start and c['end_us'] > end]
        result.append(dict(start_us=start, end_us=end, seconds=(end-start)/1e6,
                           within_caption_ids=inside,
                           overlaps_unsupported_voice=any(r['start_us'] < end and r['end_us'] > start for r in unknown)))
    return result

def analyze(args):
    source=Path(args.input).resolve(strict=True);raw=source.read_bytes();work=Path(args.workspace).resolve()
    root=directory(args.copy_root);original=directory(args.source_root) if args.source_root else root
    if any(work.is_relative_to(p) for p in (root,original)):raise ValueError('Use an analysis workspace outside live drafts')
    if source.is_relative_to(root) or source.is_relative_to(original):raise ValueError('Use an isolated saved input JSON')
    support=directory(args.support_dir);cache=directory(args.cache_dir);app=directory(args.app_dir)
    if any(work.is_relative_to(p) for p in (support,cache,app)):raise ValueError('Analysis workspace cannot be inside backend, cache or application directories')
    sys.path.insert(0,str(support))
    from jyexport.engine import relocate_document
    from jyexport.processed_audio import bind_referenced_media_results,bind_referenced_results
    from jyexport.encoded_audio import bind_referenced_aac
    work.mkdir(parents=True,exist_ok=False)
    doc=json.loads(raw);material_lookup(doc)
    doc,relocation=relocate_document(doc,original,root,cache)
    doc,_=bind_referenced_media_results(doc,root,work/'timeline_audio')
    doc,_=bind_referenced_results(doc,root,work/'effects_audio')
    doc,_=bind_referenced_aac(doc,root,work/'preset_audio',app)
    check_media(doc);save(work/'prepared.json',doc)
    mats=material_lookup(doc);step=args.step_ms/1000;sample_rate=8000;window=round(sample_rate*step)
    if not 5<=args.step_ms<=100 or window<=0:raise ValueError('step-ms must be 5–100')
    powers=[0.]*math.ceil(doc['duration']/(step*1e6));waves={};wave_errors={};audio=[];captions=[];videos=[]
    unknown=[];unmeasured=[];voice_measurements=[]

    def measure_voice(track,s,mat,a,b,path,source_kind):
        record=dict(track_id=track['id'],segment_id=s['id'],start_us=a,end_us=b,path=path,source=source_kind)
        if not path:
            reason='Voice media has no readable path'
            unmeasured.append(dict(id=s['id'],start_us=a,end_us=b,reason=reason))
            voice_measurements.append(dict(record,status='unmeasured',reason=reason));return
        src=s.get('source_timerange') or {};ins=src.get('start',0);duration=src.get('duration',b-a)
        rate=duration/(b-a)
        refs=[mats[r] for r in s.get('extra_material_refs',[]) if r in mats]
        if rate<=0 or s.get('reverse') or any(r.get('curve_speed') for r in refs if r.get('type')=='speed'):
            reason='Unsupported nonlinear/reverse voice timing'
            unknown.append(dict(id=s['id'],start_us=a,end_us=b,reason=reason))
            voice_measurements.append(dict(record,status='unsupported',reason=reason));return
        if path not in waves and path not in wave_errors:
            try:
                output=run([args.ffmpeg,'-nostdin','-v','error','-i',path,'-map','0:a:0','-vn',
                            '-ac','1','-ar',sample_rate,'-af','highpass=f=100,lowpass=f=3400','-f','f32le','-'])
                values=array('f');values.frombytes(output)
                waves[path]=[sum(x*x for x in values[i:i+window])/max(1,len(values[i:i+window]))
                             for i in range(0,len(values),window)]
            except (ValueError,subprocess.TimeoutExpired) as exc:
                wave_errors[path]=str(exc)
        if path in wave_errors:
            reason='Embedded/audio stream unavailable or decode failed: '+wave_errors[path]
            unmeasured.append(dict(id=s['id'],start_us=a,end_us=b,reason=reason))
            voice_measurements.append(dict(record,status='unmeasured',reason=reason));return
        curve=None;approximation=False
        for g in s.get('common_keyframes',[]):
            if g.get('property_type')=='KFTypeVolume':
                if any(k.get('curveType') not in (None,'','Line','Linear') or k.get('graphID') for k in g['keyframe_list']):
                    reason='Voice energy uses linear approximation of an unsupported volume curve'
                    unknown.append(dict(id=s['id'],start_us=a,end_us=b,reason=reason));approximation=True
                curve=sorted((k.get('time_offset',0),k['values'][0]) for k in g['keyframe_list'])
        for i in range(max(0,int(a/(step*1e6))),min(len(powers),math.ceil(b/(step*1e6)))):
            t=round((i+.5)*step*1e6)
            if a<=t<b:
                offset=ins+round((t-a)*rate);j=int(offset/(step*1e6))
                gain=interp(curve,offset) if curve else s.get('volume',1)
                if 0<=j<len(waves[path]):powers[i]+=waves[path][j]*gain*gain
        voice_measurements.append(dict(record,status='measured_with_approximation' if approximation else 'measured'))

    for track in doc['tracks']:
        for s in track['segments']:
            mat=mats[s['material_id']];a,b=bounds(s)
            if track['type']=='text':
                try:text=json.loads(mat.get('content','{}')).get('text','')
                except (ValueError,TypeError):text=mat.get('text','')
                captions.append(dict(track_id=track['id'],segment_id=s['id'],start_us=a,end_us=b,text=text));continue
            if track['type']=='video':
                videos.append(dict(track_id=track['id'],segment_id=s['id'],start_us=a,end_us=b,source=s.get('source_timerange'),path=mat.get('path'),clip=s.get('clip')))
                record=dict(track_id=track['id'],segment_id=s['id'],start_us=a,end_us=b,path=mat.get('path'),source='embedded_video')
                if mat.get('has_sound_separated'):
                    voice_measurements.append(dict(record,status='skipped_sound_separated'));continue
                if mat.get('type')=='photo' or mat.get('has_audio') is False or (not s.get('common_keyframes') and s.get('volume',1)==0):
                    voice_measurements.append(dict(record,status='skipped_silent_or_muted'));continue
                measure_voice(track,s,mat,a,b,mat.get('path'),'embedded_video');continue
            if track['type']!='audio':continue
            kind=mat.get('sound_separate_type');path=mat.get('path')
            audio.append(dict(track_id=track['id'],track_name=track.get('name'),segment_id=s['id'],start_us=a,end_us=b,path=path,material_name=mat.get('name'),separated_kind=kind))
            if kind!='human':
                if kind!='background':unmeasured.append(dict(id=s['id'],start_us=a,end_us=b,reason='Unclassified or mixed audio; not established as speech-free'))
                continue
            measure_voice(track,s,mat,a,b,path,'separated_human')
    db=[round(10*math.log10(max(1e-11,v)),1) for v in powers]
    active=[];start=None
    for i,v in enumerate(db+[-110.]):
        if v>=args.voice_threshold_dbfs and start is None:start=i
        elif v<args.voice_threshold_dbfs and start is not None:
            active.append(dict(start_us=round(start*step*1e6),end_us=min(doc['duration'],round(i*step*1e6))))
            start=None
    gaps=[]
    grouped={}
    for c in captions:grouped.setdefault(c['track_id'],[]).append(c)
    for track_id,rows in grouped.items():
        rows.sort(key=lambda c:c['start_us'])
        for left,right in zip(rows,rows[1:]):
            a,b=left['end_us'],right['start_us']
            if b-a<350000:continue
            i,j=max(0,int(a/(step*1e6))),min(len(db),math.ceil(b/(step*1e6)))
            gaps.append(dict(track_id=track_id,start_us=a,end_us=b,seconds=(b-a)/1e6,
                             previous=left['text'],next=right['text'],peak_window_rms_dbfs=max(db[i:j],default=-110),review='Check actual syllables and necessary picture action; not an automatic cut'))
    dips=energy_dip_candidates(active,captions,unknown)
    if source.read_bytes()!=raw:raise ValueError('Input changed during analysis')
    result=dict(input=str(source),input_sha256=fingerprint(source),prepared_json=str(work/'prepared.json'),timeline_id=doc['id'],duration_us=doc['duration'],fps=doc.get('fps'),
                waveform=dict(step_ms=args.step_ms,filtered_mono_rms_dbfs=db,threshold_dbfs=args.voice_threshold_dbfs,activity_intervals=active,
                              meaning='Measured band-limited energy; not ASR, complete speech coverage, silence proof, or subjective listening'),
                captions=captions,audio=audio,video=videos,gap_candidates=gaps,energy_dip_candidates=dips,
                energy_dip_note='Review locators only. A dip between voice-energy runs can contain speech, breathing, mixed audio, or action. Not a cut list.',
                voice_measurements=voice_measurements,
                voice_source_counts={kind:sum(m['source']==kind and m['status'].startswith('measured') for m in voice_measurements)
                                     for kind in ('separated_human','embedded_video')},
                embedded_audio_note='Embedded video audio may mix dialogue, music and effects. Band-limited energy is only a review locator, not ASR or speech proof.',
                unsupported_voice_segments=unknown,unmeasured_audio_segments=unmeasured,
                voice_timing='Source-range linear mapping; constant-speed activity is approximate and syllable boundaries still require verification',
                unresolved_cache_paths=relocation['unresolved_outer_cache_paths'],subjective_audio_listening=False)
    save(work/'analysis.json',result)
    return dict(analysis=str(work/'analysis.json'),prepared_json=str(work/'prepared.json'),input_sha256=result['input_sha256'],
                captions=len(captions),voice_sources=len(waves),voice_segments=sum(m['status'].startswith('measured') for m in voice_measurements),
                embedded_voice_sources=len({m['path'] for m in voice_measurements if m['source']=='embedded_video' and m['status'].startswith('measured')}),
                decode_errors=len(wave_errors),gap_candidates=len(gaps),energy_dip_candidates=len(dips),desktop_started=False)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('input','workspace','copy-root','support-dir','cache-dir','app-dir','ffmpeg'):p.add_argument('--'+name,required=True)
    p.add_argument('--source-root');p.add_argument('--step-ms',type=float,default=10);p.add_argument('--voice-threshold-dbfs',type=float,default=-38)
    args=p.parse_args()
    try:print(json.dumps(analyze(args),ensure_ascii=False,indent=2))
    except (OSError,ValueError,KeyError,TypeError,ImportError,subprocess.TimeoutExpired) as exc:p.exit(1,f'Analysis unavailable: {exc}\n')

if __name__=='__main__':main()
