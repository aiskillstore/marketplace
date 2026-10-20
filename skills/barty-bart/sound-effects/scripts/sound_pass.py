#!/usr/bin/env python3
"""Measured sound pass for a motion-graphics video.
Approach credit: Vox (@Voxyz_ai), x.com/Voxyz_ai/status/2109358372873183564
Usage: sound_pass.py --video silent.mp4 --cues cues.json --music track.mp3 --manifest ../sfx/manifest.json --out outdir
Needs ffmpeg, python libs: librosa soundfile numpy scipy matplotlib.
"""
import argparse,json,os,re,subprocess,random
import numpy as np,librosa,soundfile as sf
from scipy.signal import butter,sosfiltfilt,find_peaks
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
SR=48000
ap=argparse.ArgumentParser()
for a in ['video','cues','music','manifest','out']: ap.add_argument('--'+a,required=True)
ap.add_argument('--music-db',type=float,default=-12.0)
ap.add_argument('--music-source',default=None,help='where the music came from (track, artist, link), for CREDITS.txt')
ap.add_argument('--music-license',default=None,help='the music licence the user confirmed, e.g. "Mixkit Stock Music Free License"')
ap.add_argument('--use-case',default=None,help='where the video will be published, e.g. "YouTube and Instagram"; checked against known licence limits')
ap.add_argument('--seed',type=int,default=7)
ap.add_argument('--swaps',default=None,help='swaps.json from report.html: {cue_index: file|runtime_url|"auto"}')
A=ap.parse_args(); os.makedirs(A.out,exist_ok=True); os.makedirs(f'{A.out}/checks',exist_ok=True)
random.seed(A.seed)
run=lambda c:subprocess.run(c,capture_output=True,text=True)
dur=float(run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',A.video]).stdout)
fps=eval(run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=r_frame_rate','-of','csv=p=0',A.video]).stdout.strip())
cues=json.load(open(A.cues)); man=json.load(open(A.manifest)); base=os.path.dirname(os.path.abspath(A.manifest))
log=[]
# 1. beat grid + sub-120Hz check
y,_=librosa.load(A.music,sr=SR,mono=True)
tempo,bf=librosa.beat.beat_track(y=y,sr=SR); beats=librosa.frames_to_time(bf,sr=SR); period=float(np.median(np.diff(beats)))
low=sosfiltfilt(butter(4,120,'low',fs=SR,output='sos'),y)
env=np.abs(low); hop=240; envd=env[:len(env)//hop*hop].reshape(-1,hop).max(1); te=np.arange(len(envd))*hop/SR
pk,_=find_peaks(envd,height=envd.max()*0.5,distance=int(period*0.6*SR/hop)); kicks=te[pk]
def offs(g): return np.array([kicks[np.argmin(np.abs(kicks-b))]-b for b in g if kicks.size])
o=offs(beats); med=float(np.median(o)) if o.size else 0.0
grid=beats.copy(); shifted=False
if abs(med)>0.03:
  grid=beats+med; shifted=True
log.append(f"librosa tempo {float(np.atleast_1d(tempo)[0]):.1f} BPM, beat period {period:.3f}s. Kicks (<120 Hz) vs librosa grid: median offset {med*1000:+.0f} ms -> {'SHIFTED whole grid' if shifted else 'grid OK'}.")
fig,ax=plt.subplots(2,1,figsize=(12,5),sharex=True); w=4*4*period; m=te<w
for a_,g,lab in [(ax[0],beats,'librosa grid'),(ax[1],grid,'checked grid')]:
  a_.plot(te[m],envd[m],lw=.8); [a_.axvline(b,color='r',lw=1) for b in g if b<w]; a_.set_title(f'{lab}: waveform <120 Hz vs beat lines (first 4 bars)')
plt.tight_layout(); plt.savefig(f'{A.out}/beatgrid.png',dpi=90); plt.close()
# 2. align music so hard cuts land on beats (can't change the animation -> move where the music starts)
hard=[c['t'] for c in cues if c['type'] in('scene_cut','reveal')]
best=None
for s in np.arange(0,min(period*8,len(y)/SR-dur),0.005):
  e=sum(min(abs((grid-s)-t)) for t in hard)
  if best is None or e<best[0]: best=(e,s)
mstart=float(best[1]); vgrid=grid-mstart
resid={t:float(min(abs(vgrid-t))) for t in hard}
log.append(f"Music starts {mstart:.3f}s into the track. Cut-to-beat error: "+', '.join(f'{t:.2f}s={r*1000:.0f}ms' for t,r in resid.items()))
# 3. choose one SFX per cue: default kit first, then swaps (--swaps), alternatives for the report
cmap=man['category_map']; lib={}
for e in man.get('bundled',[]): lib.setdefault(e['category'],[]).append({**e,'path':os.path.join(base,e['file'])})
for e in man.get('runtime',[]): lib.setdefault(e['category'],[]).append({**e,'path':None})
kit={e['category']:e for e in man.get('default_kit',[])}
cache=os.path.join(A.out,'sound-effects-cache'); os.makedirs(cache,exist_ok=True)
def fetch(e):
  if e.get('path') and os.path.exists(e['path']): return e['path']
  url=e.get('runtime_url'); f=os.path.join(cache,(e.get('category','x'))+'-'+os.path.basename(url))
  if not os.path.exists(f):
    r=run(['curl','-fsSL','-o',f,url])
    if r.returncode!=0:
      if os.path.exists(f): os.remove(f)
      raise SystemExit(f"Could not download runtime sound for '{e.get('category')}' from {url} (curl exit {r.returncode}: {r.stderr.strip()}). Check your connection, or pick a bundled sound via --swaps.")
  return f
def kit_entry(cat):
  k=kit.get(cat)
  if not k: return None
  return {**k,'path':os.path.join(base,k['file']) if k.get('file') else None}
def alts(cat):
  out=[]
  for c in man.get('alt_categories',{}).get(cat,[cat]): out+=lib.get(c,[])
  return out
swaps=json.load(open(A.swaps)) if A.swaps else {}
def pick(cat,want=None,idx=None):
  sw=swaps.get(str(idx))
  pool=alts(cat)
  if sw and sw!='auto':
    for e in pool+[kit_entry(cat)]:
      if e and (e.get('file')==sw or e.get('runtime_url')==sw): return e
  if sw=='auto' or not kit_entry(cat):
    c=[e for e in pool if not want or e.get('length') in (None,want)] or pool
    return random.choice(c)
  return kit_entry(cat)
mix=np.zeros((int(dur*SR)+SR,2),dtype=np.float32); placed=[]
def load(p):
  a,_=librosa.load(p,sr=SR,mono=False); a=np.atleast_2d(a)
  if a.shape[0]==1: a=np.vstack([a,a])
  return a.T
for idx,c in enumerate(cues):
  cat=cmap[c['type']]; want={'movement':'short','scene_cut':'short'}.get(c['type'])
  e=pick(cat,want,idx); a=load(fetch(e))
  gain=0.0; pre=0.0
  if c['type'] in('movement','scene_cut'): pre=2/fps; gain=-4
  if c['type']=='typing':
    need=int(c.get('dur',1)*SR); a=np.tile(a,(need//len(a)+1,1))[:need]; f=int(.05*SR); a[-f:]*=np.linspace(1,0,f)[:,None]; gain=-8
  if c['type']=='build_up':
    need=int(c.get('dur',.8)*SR); a=a[-need:] if len(a)>need else a; gain=-6; start=c['t']+c.get('dur',.8)-len(a)/SR
  else: start=c['t']-pre
  if c['type'] in('appear','click','hover_or_small_ui'): gain=-6
  i=max(0,int(start*SR)); a=a*10**(gain/20); n=min(len(a),len(mix)-i); mix[i:i+n]+=a[:n]
  placed.append({**c,'idx':idx,'category':cat,'sfx':e.get('file') or e.get('runtime_url'),'sfx_path':fetch(e),'source_url':e.get('source_url') or e.get('source_page'),'license':e.get('license'),'credit':e.get('credit') or e.get('attribution') or 'Mixkit','start':round(start,3),'gain_db':gain,'alternatives':[{'id':x.get('file') or x.get('runtime_url'),'play':(os.path.relpath(x['path'],A.out) if x.get('path') else x.get('runtime_url')),'source_url':x.get('source_url') or x.get('source_page'),'license':x.get('license'),'label':x.get('note') or x.get('title') or os.path.basename(x.get('file') or x.get('runtime_url'))} for x in alts(cat)][:12]})
# music bed
yt,_=librosa.load(A.music,sr=SR,mono=False); yt=np.atleast_2d(yt); yt=(np.vstack([yt,yt]) if yt.shape[0]==1 else yt).T
seg=yt[int(mstart*SR):int(mstart*SR)+len(mix)]; seg=seg*10**(A.music_db/20)
f=int(.6*SR); seg[-f:]*=np.linspace(1,0,f)[:,None]; mix[:len(seg)]+=seg
mix=mix[:int(dur*SR)]; sf.write(f'{A.out}/mix_raw.wav',mix,SR)
# 4. loudness: measure the exported MP4, adjust, repeat
def export(gain_db,limit):
  af=f"volume={gain_db}dB"+(f",alimiter=limit={limit}:level=false" if limit else "")
  run(['ffmpeg','-y','-v','error','-i',A.video,'-i',f'{A.out}/mix_raw.wav','-map','0:v','-map','1:a','-c:v','copy','-af',af,'-c:a','aac','-b:a','256k','-shortest',f'{A.out}/after.mp4'])
def measure(p,mono=False):
  cmd=['ffmpeg','-nostats','-i',p]+(['-ac','1'] if mono else [])+['-af','ebur128=peak=true','-f','null','-']
  o=run(cmd).stderr; I=float(re.findall(r'I:\s+([-\d.]+) LUFS',o)[-1]); P=float(re.findall(r'Peak:\s+([-\d.]+) dBFS',o)[-1]); return I,P
g=0.0; lim=False
for it in range(10):
  export(g,lim); I,P=measure(f'{A.out}/after.mp4'); log.append(f"pass {it+1}: gain {g:+.1f} dB, limiter {lim if lim else 'off'} -> {I:.1f} LUFS, true peak {P:.1f} dBFS")
  if abs(I+16)<=0.5 and P< -4: break
  if P>=-4: lim=round((lim or 0.6)*0.9,3)
  if abs(I+16)>0.5: g+=(-16-I)
Im,Pm=measure(f'{A.out}/after.mp4',mono=True)
log.append(f"FINAL after.mp4: {I:.1f} LUFS integrated, true peak {P:.1f} dBFS. Mono downmix: {Im:.1f} LUFS, peak {Pm:.1f} dBFS.")
# 5. proof: frames before/after each cue + waveform window
run(['ffmpeg','-y','-v','error','-i',f'{A.out}/after.mp4','-ac','1','-ar',str(SR),'/tmp/after_audio.wav']); au,_=librosa.load('/tmp/after_audio.wav',sr=SR,mono=True)
for k,c in enumerate(placed):
  for tag,dt in (('a',-0.1),('b',0.15)):
    run(['ffmpeg','-y','-v','error','-ss',f"{max(0,c['t']+dt):.3f}",'-i',f'{A.out}/after.mp4','-frames:v','1','-vf','scale=320:-1',f'/tmp/cue{k}{tag}.png'])
  fig,ax=plt.subplots(1,3,figsize=(12,2.6),gridspec_kw={'width_ratios':[1,1,2]})
  for j,tag in enumerate('ab'): ax[j].imshow(plt.imread(f'/tmp/cue{k}{tag}.png')); ax[j].axis('off'); ax[j].set_title(('before ' if tag=='a' else 'after ')+'cue')
  s0=max(0,c['t']-0.5); s1=min(dur,c['t']+0.8); seg=au[int(s0*SR):int(s1*SR)]
  ax[2].plot(np.linspace(s0,s1,len(seg)),seg,lw=.4); ax[2].axvline(c['t'],color='r'); ax[2].set_title(f"cue {k} @ {c['t']:.2f}s {c['type']} <- {os.path.basename(c['sfx'])}",fontsize=8)
  plt.tight_layout(); plt.savefig(f"{A.out}/checks/cue-{k:02d}.png",dpi=80); plt.close()
# credits + licence check: only CC0 and Mixkit Free License count as known free licences; anything else is named as unknown
allman={}
for e in man.get('bundled',[])+man.get('runtime',[])+man.get('default_kit',[]): allman[e.get('file') or e.get('runtime_url')]=e
def free(lic): l=(lic or ''); return 'CC0' in l or ('Mixkit' in l and 'Free License' in l and 'Restricted' not in l)
def credit_line(c):
  e=allman.get(c['sfx'],{}); lic=c.get('license') or e.get('license') or 'licence unknown'
  if e.get('title') and e.get('creator'): name,who,src=e['title'],e['creator'],e.get('source','Freesound').split(' (')[0]
  elif str(c['sfx']).startswith('http'): name,who,src='Mixkit #'+str(e.get('mixkit_id') or ''),'Mixkit','Mixkit'
  else:
    b=os.path.basename(c['sfx']).rsplit('.',1)[0]; kenney=b.startswith('kenney-')
    name=re.sub(r'^kenney-','',re.sub(r'^fs-?\d+-?','',b)).replace('-',' ').strip().capitalize() or 'Freesound '+(re.findall(r'\d+',b) or [''])[0]
    a=e.get('attribution') or ''; who='Kenney' if kenney else (a.split(' via ')[0].strip() or 'unknown creator'); src='kenney.nl' if kenney else (a.split(' via ')[1].split(' (')[0].strip() if ' via ' in a else 'unknown source')
  url=c.get('source_url') or e.get('source_url') or e.get('source_page'); ok=free(lic)
  return ok,name,who,lic,url,f'"{name}" by {who} ({src}), {lic.split(" (")[0]}'+('' if ok else ' - LICENCE UNKNOWN, check before publishing')+(f' - {url}' if url else '')
seen={}; unknown=[]
for c in placed:
  if c['sfx'] in seen: continue
  ok,name,who,lic,url,line=credit_line(c); seen[c['sfx']]=line
  if not ok: unknown.append(f'"{name}" by {who} ({url or "no source link"}): licence "{lic}" is not a known free licence')
music_line=(f"{A.music_source or os.path.basename(A.music)}, {A.music_license}" if A.music_license else f"{A.music_source or os.path.basename(A.music)} - LICENCE NOT CONFIRMED, add the track, artist and licence before publishing")
open(f'{A.out}/CREDITS.txt','w').write('Sound effects\n'+'\n'.join(seen.values())+'\n\nMusic\n'+music_line+'\n')
lic_report=(["All sound effects have a known free licence (CC0 or Mixkit Free License). Sources can change their terms; check the source pages now and then."] if not unknown else ["UNKNOWN LICENCES, do not publish until checked:"]+['  '+u for u in unknown])+[("Music licence: "+A.music_license) if A.music_license else "Music licence: NOT CONFIRMED. Ask the user where the track is from and what licence it has."]
# use case against the known limits of the sources (Claude still checks each source's current page, SKILL.md step 0)
uc=(A.use_case or '').lower(); conflicts=[]
if A.use_case:
  if 'mixkit' in ((A.music_license or '')+(A.music_source or '')).lower() and any(w in uc for w in ('tv','television','broadcast','radio','game','cd','dvd')):
    conflicts.append('Mixkit music is not allowed for TV/radio broadcast, video games or CDs/DVDs: pick another track.')
  if any('Mixkit' in str(c.get('license')) for c in placed) and any(w in uc for w in ('template','tool','asset pack','stock')):
    conflicts.append('Mixkit sounds cannot be redistributed inside a template or tool: swap them for CC0 sounds.')
lic_report.append(('Use case: '+A.use_case+(' - CONFLICT: '+' '.join(conflicts) if conflicts else ' - no conflict with the known licence limits; still check each source page today (SKILL.md step 0).')) if A.use_case else 'Use case: NOT GIVEN. Ask the user where the video will be published.')
# 6. five timestamps for a human with headphones (riskiest first)
risk=sorted(placed,key=lambda c:-(resid.get(c['t'],0)*10+{'typing':.5,'build_up':.4,'reveal':.3,'scene_cut':.2}.get(c['type'],0)))[:5]
ts=[f"{c['t']:.2f}s ({c['type']}: {c['desc']}) - check {'beat sync' if c['t'] in resid else 'level/feel'}" for c in sorted(risk,key=lambda c:c['t'])]
rep=["# SOUND.md (generated by sound_pass.py)","Approach: Vox (@Voxyz_ai) sound pass. Claude can't hear, so everything below is measured.","",f"Music: {music_line}","","## Licences"]+['- '+l for l in lic_report]+["- CREDITS.txt: optional, ready to paste into a YouTube, Instagram or TikTok description. CC0 sounds need no credit; the list doubles as proof of source if a platform flags the audio.","","## Log"]+['- '+l for l in log]+["","## Cues"]+[f"- {c['t']:.2f}s {c['type']} -> {c['sfx']} (start {c['start']}s, {c['gain_db']} dB)" for c in placed]+["","## Check these 5 with headphones"]+['- '+t for t in ts]+["","Not claiming it sounds good: listen to these."]
open(f'{A.out}/SOUND.md','w').write('\n'.join(rep)); print('\n'.join(rep))
import report; report.write(A.out,placed,A.video,I,P)
