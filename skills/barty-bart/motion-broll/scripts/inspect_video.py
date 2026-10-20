"""Inspect a talking-head video: specs, a contact sheet, and regions that are empty (e.g. a picture-in-picture layout).
usage: python3 inspect_video.py video.mp4 outdir"""
import sys, json, subprocess, numpy as np, os
v, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
p = json.loads(subprocess.run(['ffprobe','-v','error','-print_format','json','-show_streams','-show_format',v],capture_output=True,text=True).stdout)
vs = [s for s in p['streams'] if s['codec_type']=='video'][0]
W, H = int(vs['width']), int(vs['height']); fps = vs['r_frame_rate']; dur = float(p['format']['duration'])
subprocess.run(['ffmpeg','-loglevel','error','-y','-i',v,'-vf',f'fps=1/{max(1,dur/16):.2f},scale=480:-1,tile=4x4:padding=4','-frames:v','1',f'{out}/contact.png'])
raw = subprocess.run(['ffmpeg','-loglevel','error','-i',v,'-vf','fps=4,scale=96:54,format=gray','-f','rawvideo','-'],capture_output=True).stdout
fr = np.frombuffer(raw,np.uint8).reshape(-1,54,96)
# a column band that is near-black for a stretch = free space for an overlay panel.
# an all-black frame (fade, intro/outro) has no subject: its own 'black' layout, not 'pip'
def layout(f):
    if f.max()<=20: return 'black'
    return 'pip' if f[:,60:].mean()<8 or f[:,:36].mean()<8 else 'full'
sections=[]; prev=None; start=0
for i,f in enumerate(fr):
    lay=layout(f)
    if lay!=prev:
        if prev is not None: sections.append({'from':start/4,'to':i/4,'layout':prev})
        start=i; prev=lay
sections.append({'from':start/4,'to':len(fr)/4,'layout':prev})
# track the subject box through each PiP section; flag any resize (a panel sized for one box can collide with another)
for s in sections:
    if s['layout']!='pip': continue
    boxes=[]
    for i in range(int(s['from']*4),int(s['to']*4)):
        f=fr[i]; cols=np.where(f.max(0)>20)[0]; rows=np.where(f.max(1)>20)[0]
        if len(cols)==0: continue
        boxes.append((i/4,[int(cols.min()*W/96),int(rows.min()*H/54),int((cols.max()+1)*W/96),int((rows.max()+1)*H/54)]))
    if not boxes: continue
    s['subject_box']=[min(b[1][0] for b in boxes),min(b[1][1] for b in boxes),max(b[1][2] for b in boxes),max(b[1][3] for b in boxes)]
    changes=[]; ref=boxes[0][1]
    for t,b in boxes:
        if max(abs(b[k]-ref[k]) for k in range(4))>2*W/96: changes.append({'at':t,'box':b}); ref=b
    s['box_changes']=changes
    if changes: print(f"WARNING: subject box changes size/position inside PiP section {s['from']}-{s['to']}s at {[c['at'] for c in changes]}. Keep panels clear of the largest box, or ask the user whether the change is intended.")
info={'width':W,'height':H,'fps':fps,'duration':dur,'sections':sections}
json.dump(info,open(f'{out}/video.json','w'),indent=1); print(json.dumps(info,indent=1))
