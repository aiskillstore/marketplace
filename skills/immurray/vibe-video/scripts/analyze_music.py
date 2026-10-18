#!/usr/bin/env python3
"""Measure local audio events. Tempo candidates are estimates, not editing decisions."""
import argparse,json,shutil,subprocess
from pathlib import Path
import numpy as np
from scipy.signal import stft,find_peaks,correlate
p=argparse.ArgumentParser();p.add_argument('--audio',required=True);p.add_argument('--start',type=float,default=0);p.add_argument('--duration',type=float,default=60);p.add_argument('--output',required=True)
a=p.parse_args()
if a.start<0 or a.duration<=0:p.error('invalid start or duration')
ff=shutil.which('ffmpeg')
if not ff:p.error('ffmpeg not found')
sr=22050
raw=subprocess.check_output([ff,'-v','error','-ss',str(a.start),'-i',a.audio,'-t',str(a.duration),'-vn','-ac','1','-ar',str(sr),'-f','s16le','pipe:1'])
x=np.frombuffer(raw,dtype='<i2').astype(float)/32768
if len(x)<sr or np.max(np.abs(x))<1e-5:p.error('audio too short or silent')
f,t,z=stft(x,sr,nperseg=1024,noverlap=768);m=np.abs(z)
def onset(lo,hi):
 band=m[(f>=lo)&(f<hi)]
 return np.r_[0,np.maximum(np.diff(np.log1p(band*100),axis=1),0).mean(axis=0)]
o=onset(35,180)+onset(35,9000)*.5;step=float(t[1]-t[0])
peaks,_=find_peaks(o,distance=max(1,int(.21/step)),prominence=float(np.quantile(o,.6)*.6))
v=o[t>min(8,a.duration/4)];ac=correlate(v,v,mode='full',method='fft')[len(v)-1:]
mi,ma=int(.30/step),min(int(1.05/step),len(ac));lp,_=find_peaks(ac[mi:ma]);cand=sorted(lp+mi,key=lambda j:ac[j],reverse=True)[:6]
data={'audio':str(Path(a.audio).resolve()),'start':a.start,'duration':len(x)/sr,'sample_rate':sr,'step':step,'time':t.tolist(),'bass':m[(f>=35)&(f<180)].mean(axis=0).tolist(),'flux':o.tolist(),'peaks':[{'t':float(t[i]),'strength':float(o[i])}for i in peaks],'tempo_candidates_bpm':[round(60/(i*step),3)for i in cand]}
out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(data))
print(json.dumps({'output':str(out.resolve()),'duration':data['duration'],'tempo_candidates_bpm':data['tempo_candidates_bpm'],'strong_events':sorted(data['peaks'],key=lambda e:e['strength'],reverse=True)[:15]},ensure_ascii=False))
