#!/usr/bin/env python3
"""Prepare a topic project without embedding a provider or private media."""
import argparse,hashlib,json,os,shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--topic',required=True);p.add_argument('--project',required=True);p.add_argument('--profile');p.add_argument('--music');p.add_argument('--music-start',type=float)
a=p.parse_args();root=Path(__file__).resolve().parents[1];dest=Path(a.project).expanduser().resolve()
if not a.topic.strip():p.error('topic is empty')
if dest.exists():p.error('project exists; choose a new directory')
choices=[Path(a.profile).expanduser()]if a.profile else [Path.cwd()/'vibe-video.local.json',root/'local-profile.json',root/'assets/local-profile.example.json']
config=next((v.resolve()for v in choices if v.is_file()),None)
if not config:p.error('profile not found')
profile=json.loads(config.read_text());music=dict(profile.get('music',{}));explicit=a.music or os.environ.get('VIBE_MUSIC');path=explicit or music.get('path')
if a.music_start is not None and a.music_start<0:p.error('music-start must be >=0')
if path:
 q=Path(path).expanduser()
 if not q.is_absolute():q=(Path.cwd() if explicit else config.parent)/q
 q=q.resolve()
 if not q.is_file():p.error('Configured music file does not exist; no project was created')
 digest=hashlib.sha256(q.read_bytes()).hexdigest()
 if not explicit and music.get('sha256') and digest!=music['sha256']:p.error('Configured audio hash changed; verify or replace profile')
 music.update(path=str(q),sha256=digest,title=q.stem if explicit else music.get('title')or q.stem)
else:music.update(path=None,sha256=None)
start=a.music_start if a.music_start is not None else float(music.get('start_seconds',0))
if start<0:p.error('configured start_seconds must be >=0')
music.update(start_seconds=start,segment_seconds=60)
beats=json.loads((root/'assets/beat-edit.json').read_text());match=music['sha256']==beats['track_sha256'] and start==beats['music_start_seconds'] and music['segment_seconds']==beats['duration_seconds']
(dest/'work').mkdir(parents=True)
for old,new in [('reference-film.js','film.js'),('package.json','package.json'),('requirements.txt','requirements.txt')]:shutil.copy2(root/'assets'/old,dest/new)
shutil.copy2(root/'assets/beat-edit.json',dest/'work/reference-beat-edit.json')
if match:shutil.copy2(root/'assets/music-analysis.json',dest/'work/music-analysis.json')
else:(dest/'work/music-analysis.json').write_text(json.dumps({'status':'placeholder_requires_real_audio_analysis','step':1/30,'duration':60,'flux':[0]*1801,'peaks':[]}))
status='reference_verified'if match else 'requires_analysis'if path else 'music_not_configured'
brief={'topic':a.topic.strip(),'status':'needs_topic_specific_storyboard_and_animation','duration_seconds':60,'width':1440,'height':2560,'fps':30,'narration':False,'music':music,'beat_analysis_status':status,'reference_is_not_new_topic_output':True}
(dest/'brief.json').write_text(json.dumps(brief,ensure_ascii=False,indent=2))
print(json.dumps({'project':str(dest),'beat_analysis_status':status,'next':'Research and create new scenes. If music is not configured, continue visuals and request music. Analyze changed music before final render.'},ensure_ascii=False))
