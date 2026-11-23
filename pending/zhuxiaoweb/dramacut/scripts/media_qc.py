"""Hash-bound FFmpeg preview checks and small seam contact sheets; no desktop UI."""
from __future__ import annotations
import argparse,hashlib,json,math,re,subprocess,sys,time
from pathlib import Path

def load(p):return json.loads(Path(p).read_text('utf-8-sig'))
def save(p,value):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:f.write(json.dumps(value,ensure_ascii=False,indent=2))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(argv,timeout=300):
    p=subprocess.run(list(map(str,argv)),capture_output=True,timeout=timeout)
    if p.returncode:raise ValueError(p.stderr.decode('utf-8','replace')[-1500:])
    return p


def audio_stats(args,video,start,end):
    if not 0<=start<end:raise ValueError(f'Invalid audio measurement window: {start}–{end}')
    p=run([args.ffmpeg,'-nostdin','-hide_banner','-v','info','-xerror',
           '-ss',f'{start:.6f}','-i',video,'-t',f'{end-start:.6f}',
           '-map','0:a:0','-vn','-af','astats','-f','null','-'])
    log=p.stderr.decode('utf-8','replace')
    def level(label):
        values=re.findall(rf'{label}: (-?(?:[\d.]+|inf))',log,re.IGNORECASE)
        if not values:return None
        value=float(values[-1])
        return value if math.isfinite(value) else None
    return dict(start_seconds=round(start,6),end_seconds=round(end,6),
                peak_dbfs=level('Peak level dB'),rms_dbfs=level('RMS level dB'))


def measure_audio_events(args,video,events,seconds):
    result=[]
    radius=args.attack_window_ms/1000
    for event in events:
        start=max(0,event['start_us']/1e6);end=min(seconds,event['end_us']/1e6)
        target=event['target_us']/1e6
        if not start<=target<=end or target>seconds:raise ValueError(f"Audio event {event.get('segment_id')} is outside the preview")
        item=dict(event)
        item['mixed_event']=audio_stats(args,video,start,end)
        item['mixed_attack']=audio_stats(args,video,max(0,target-radius),min(seconds,target+radius))
        item['evidence_scope']='Mixed output only; does not isolate this event or prove perceptibility, duck depth or subjective attack alignment'
        result.append(item)
    return result

def contact_sheet(args,video,fps,points,last_frame):
    out=Path(args.frames_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    sheets=[]
    for page in range(0,len(points),5):
        group=points[page:page+5];indices=[]
        for t in group:
            indices.extend(min(last_frame,max(0,round(t*fps)+offset)) for offset in (-5,-2,-1,0,1,3,8))
        distinct=sorted(set(indices));expr='+'.join(f'eq(n,{n})' for n in distinct)
        path=out/f'seams_{page//5+1:03}.jpg'
        if path.exists():raise ValueError(f'Use a fresh frames directory: {path}')
        columns=min(7,len(distinct))
        filt=f"select='{expr}',scale=160:284,tile={columns}x{math.ceil(len(distinct)/columns)}:padding=2:margin=2:color=black"
        run([args.ffmpeg,'-nostdin','-v','error','-i',video,'-an','-vf',filt,'-frames:v','1','-update','1',path])
        if not path.is_file() or not path.stat().st_size:raise ValueError(f'No review frames were decoded: {path}')
        sheets.append(dict(image=str(path),source_frames=distinct,times_seconds=[round(n/fps,6) for n in distinct],
                           requested_seams_seconds=group,columns=columns))
    save(out/'frames.json',sheets)
    return sheets

def check(args):
    source=Path(args.input).resolve();doc=load(source)
    folder=Path(args.preview).resolve()
    cert=load(folder/'preview.json');video=Path(cert['preview'])
    if Path(args.report).resolve().exists():raise ValueError('QC report must be a new file; do not overwrite inputs or earlier evidence')
    if not video.is_file() or video.resolve().parent!=folder:raise ValueError('Missing or redirected preview file')
    if cert['input_sha256']!=sha(source):raise ValueError('Preview is stale for the supplied input JSON')
    if cert.get('certificate_version',0)<2 or not cert.get('preview_sha256') or not cert.get('dependency_hashes'):raise ValueError('Preview lacks artifact/dependency evidence; render with the current preview helper')
    if sha(video)!=cert['preview_sha256']:raise ValueError('Preview artifact changed after rendering')
    for path,digest in cert['dependency_hashes'].items():
        if not Path(path).is_file() or sha(path)!=digest:raise ValueError(f'Preview dependency changed: {path}')
    checks={str(source):cert['input_sha256'],str(folder/'preview.json'):sha(folder/'preview.json'),str(video):cert['preview_sha256'],**cert['dependency_hashes']}
    roots=[Path(cert['render_context'][k]).resolve() for k in ('copy_root','source_root','support_dir','cache_dir','app_dir','runtime') if cert.get('render_context',{}).get(k)]
    if any(Path(args.report).resolve().is_relative_to(p) for p in roots):raise ValueError('QC report must be outside live drafts and installation/cache folders')
    if args.frames_dir and any(Path(args.frames_dir).resolve().is_relative_to(p) for p in roots):raise ValueError('Frames must be outside live drafts and installation/cache folders')
    if cert.get('unresolved_cache_paths'):raise ValueError('Preview has unresolved cache/media paths')
    probe=json.loads(run([args.ffprobe,'-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,avg_frame_rate,nb_frames:format=duration','-of','json',video]).stdout)
    streams={s['codec_type']:s for s in probe['streams']}
    if not {'video','audio'}<=streams.keys():raise ValueError('Expected video and audio streams')
    n,d=map(int,streams['video']['r_frame_rate'].split('/'));fps=n/d
    an,ad=map(int,streams['video']['avg_frame_rate'].split('/'))
    if abs(an/ad-fps)>.001:raise ValueError('Variable or inconsistent preview frame rate')
    width,height=map(int,cert['size'].split('x'))
    if (streams['video']['width'],streams['video']['height'])!=(width,height):raise ValueError('Preview dimensions differ from the certificate')
    expected=float(doc.get('fps',cert['requested_fps']))
    if abs(fps-expected)>.001:raise ValueError(f'Frame rate differs from the timeline: {fps} vs {expected}')
    seconds=float(probe['format']['duration'])
    if abs(seconds-doc['duration']/1e6)>max(.06,2/fps):raise ValueError('Preview duration differs from the timeline')
    p=run([args.ffmpeg,'-nostdin','-hide_banner','-v','info','-xerror','-i',video,
           '-map','0:v:0','-map','0:a:0','-vf',"scale=120:216,blackdetect=d=0:pix_th=0.10,select='gt(scene,0.19)',showinfo",
           '-af','astats','-f','null','-'])
    log=p.stderr.decode('utf-8','replace')
    peaks=re.findall(r'Peak level dB: (-?[\d.]+)',log)
    peak=float(peaks[-1]) if peaks else None
    scenes=[float(x) for x in re.findall(r'pts_time:([\d.]+)',log)]
    short=[dict(start=a,end=b,duration=round(b-a,6)) for a,b in zip(scenes,scenes[1:]) if b-a<args.short_scene_seconds]
    black=[dict(start=float(a),end=float(b),duration=float(c)) for a,b,c in re.findall(r'black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)',log)]
    issues=[]
    if peak is None:issues.append('No finite audio peak measured')
    elif peak>args.max_peak_dbfs:issues.append(f'Peak {peak:.2f} dBFS exceeds {args.max_peak_dbfs:.2f}')
    if black:issues.append('Review detected black intervals against the intended edit')
    points=list(args.points or []);audio_events=[]
    if args.edit_report:
        edit_path=Path(args.edit_report).resolve()
        data=edit_path.read_bytes()
        edit=json.loads(data.decode('utf-8-sig'))
        if edit.get('output_sha256')!=cert['input_sha256']:
            raise ValueError('Edit report belongs to a different output JSON. Use the report bound to this preview input.')
        checks[str(edit_path)]=hashlib.sha256(data).hexdigest()
        points.extend(float(x)/1e6 for x in edit.get('seams_us',[]))
        audio_events=measure_audio_events(args,video,edit.get('sfx',[]),seconds)
    # Include global short-scene candidates: a quick motion or intended effect is not automatically a bad cut.
    points.extend(x['start'] for x in short)
    points.extend(x['start'] for x in black)
    points=sorted(set(round(t,6) for t in points if 0<=t<=max(seconds,doc['duration']/1e6)))
    frames=[]
    if args.frames_dir and points:
        count=str(streams['video'].get('nb_frames',''))
        if not count.isdigit() or int(count)<1:
            counted=json.loads(run([args.ffprobe,'-v','error','-select_streams','v:0','-count_frames',
                                    '-show_entries','stream=nb_read_frames','-of','json',video]).stdout)
            count=str(counted['streams'][0].get('nb_read_frames',''))
        if not count.isdigit() or int(count)<1:
            raise ValueError('No video frames could be counted for exact seam sampling.')
        frames=contact_sheet(args,video,fps,points,int(count)-1)
    result=dict(input=str(source),input_sha256=cert['input_sha256'],preview=str(video),seconds=seconds,
                actual_fps=fps,video=streams['video'],peak_dbfs=peak,full_decode=True,
                black_intervals=black,global_short_scene_candidates=short,issues=issues,
                frames=frames,visual_review='required for changed seams and scene candidates',
                audio_event_measurements=audio_events,attack_window_ms=args.attack_window_ms,
                audio_event_evidence='Mixed-output windows only; isolated BGM/SFX RMS, actual duck depth and perceptibility still require stems, A/B or listening',
                subjective_audio_listening=False,technical_status='needs_review' if issues else 'passed')
    if any(not Path(p).is_file() or sha(p)!=digest for p,digest in checks.items()):raise ValueError('An input, preview, certificate or dependency changed during QC')
    save(args.report,result)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True);p.add_argument('--preview',required=True);p.add_argument('--report',required=True)
    p.add_argument('--ffmpeg',required=True);p.add_argument('--ffprobe',required=True)
    p.add_argument('--max-peak-dbfs',type=float,default=-1.0);p.add_argument('--short-scene-seconds',type=float,default=.12)
    p.add_argument('--attack-window-ms',type=float,default=80,help='Radius around each planned audio attack to measure (10–500 ms).')
    p.add_argument('--edit-report');p.add_argument('--points',nargs='*',type=float);p.add_argument('--frames-dir')
    args=p.parse_args()
    if not 10<=args.attack_window_ms<=500:p.error('--attack-window-ms must be between 10 and 500')
    try:print(json.dumps(check(args),ensure_ascii=False,indent=2))
    except (OSError,ValueError,KeyError,TypeError,subprocess.TimeoutExpired) as exc:p.exit(1,f'Media QC unavailable: {exc}\n')

if __name__=='__main__':main()
