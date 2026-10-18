#!/usr/bin/env python3
"""Mix and verify a rendered 2K30 film; visual editorial QA remains manual."""
import argparse,json,math,re,shutil,subprocess,sys
from fractions import Fraction
from pathlib import Path
from PIL import Image,ImageDraw
p=argparse.ArgumentParser()
for flag in ['silent','music','output']:p.add_argument('--'+flag,required=True)
p.add_argument('--duration',type=float,default=60);p.add_argument('--music-start',type=float,default=0);p.add_argument('--sfx');p.add_argument('--qa-dir');p.add_argument('--overwrite',action='store_true')
a=p.parse_args()
if a.duration<2 or a.music_start<0:p.error('duration must be >=2 and music-start >=0')
ff=shutil.which('ffmpeg');fp=shutil.which('ffprobe')
if not ff or not fp:p.error('ffmpeg and ffprobe are required')
out=Path(a.output).resolve();qa=Path(a.qa_dir or 'work/qa').resolve()
if out.exists() and not a.overwrite:p.error('output exists; choose a new name or explicitly pass --overwrite')
if out in [Path(x).resolve()for x in [a.silent,a.music,a.sfx]if x]:p.error('output must not replace an input')
def run(args):
 r=subprocess.run(args,text=True,capture_output=True)
 if r.returncode:raise RuntimeError(r.stderr[-6000:])
 return r

def probe(path):return json.loads(run([fp,'-v','error','-show_format','-show_streams','-of','json',str(path)]).stdout)
def video_errors(v):
 checks={'1440x2560':(v.get('width'),v.get('height'))==(1440,2560),'H264':v.get('codec_name')=='h264','yuv420p':v.get('pix_fmt')=='yuv420p','30fps':Fraction(v.get('avg_frame_rate','0/1'))==30,'duration':abs(float(v.get('duration',0))-a.duration)<=1/30+.005,'frame_count':int(v.get('nb_frames',0))==round(a.duration*30)}
 return [k for k,val in checks.items()if not val]
source=probe(a.silent);videos=[s for s in source['streams']if s['codec_type']=='video']
if not videos:p.error('silent input has no video')
errors=video_errors(videos[0])
if errors:p.error('render must be corrected before mux: '+', '.join(errors))
music=probe(a.music)
if float(music['format'].get('duration',0))+.03<a.music_start+a.duration:p.error('music is shorter than the requested segment')
out.parent.mkdir(parents=True,exist_ok=True);qa.mkdir(parents=True,exist_ok=True)
fade=min(1.1,a.duration/5);fade_start=a.duration-fade
cmd=[ff,'-hide_banner','-v','error','-y','-i',a.silent,'-ss',str(a.music_start),'-i',a.music]
fil=f'[1:a]atrim=0:{a.duration},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.06,afade=t=out:st={fade_start}:d={fade},volume=0.65[m];'
if a.sfx:
 cmd+=['-i',a.sfx];fil+='[2:a]asetpts=PTS-STARTPTS,apad[s];[m][s]amix=inputs=2:duration=first:normalize=0[mix];';label='[mix]'
else:label='[m]'
fil+=label+'loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[a]'
staged=qa/'encoded.mp4'
cmd+=['-filter_complex',fil,'-map','0:v:0','-map','[a]','-c:v','copy','-bsf:v','h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1','-c:a','aac','-b:a','320k','-ar','48000','-ac','2','-t',str(a.duration),'-movflags','+faststart',str(staged)]
run(cmd)
meta=probe(staged);v=next(s for s in meta['streams']if s['codec_type']=='video');audio=next(s for s in meta['streams']if s['codec_type']=='audio')
errors=video_errors(v)
for k in ['color_space','color_primaries','color_transfer']:
 if v.get(k)!='bt709':errors.append(k)
if audio.get('codec_name')!='aac' or audio.get('sample_rate')!='48000' or audio.get('channels')!=2:errors.append('AAC stereo 48kHz')
if abs(float(audio.get('duration',0))-a.duration)>.05:errors.append('audio duration')
run([ff,'-v','error','-i',str(staged),'-f','null','-'])
l=run([ff,'-hide_banner','-nostats','-i',str(staged),'-vn','-af','loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json','-f','null','-'])
blocks=re.findall(r'\{\s*"input_i".*?\}',l.stderr,re.S)
if not blocks:raise RuntimeError('Could not read measured loudness')
loud=json.loads(blocks[-1]);integrated=float(loud['input_i']);tp=float(loud['input_tp'])
if not math.isfinite(integrated) or not -17<=integrated<=-11:errors.append('loudness outside -17..-11 LUFS')
if not math.isfinite(tp) or tp>-1:errors.append('true peak above -1 dBTP')
report={'output':str(out),'duration':a.duration,'errors':errors,'full_decode':'passed','loudness':loud,'probe':meta,'visual_review':'required: inspect contact.jpg and action/transition sequences'}
(qa/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
if errors:raise RuntimeError('Export checks failed: '+', '.join(errors))
times=sorted(set(round(min(a.duration-.1,t),3)for t in [0,.833,1.633,3]+[a.duration*i/9 for i in range(1,9)]+[a.duration-1.5]))
contact=Image.new('RGB',(1200,564*math.ceil(len(times)/4)),(9,13,20));draw=ImageDraw.Draw(contact)
for i,t in enumerate(times):
 frame=qa/f'frame-{t:06.3f}.jpg';run([ff,'-v','error','-y','-ss',str(t),'-i',str(staged),'-frames:v','1','-q:v','2',str(frame)])
 with Image.open(frame)as im:im.thumbnail((288,512));contact.paste(im,(i%4*300+6,i//4*564+30))
 draw.text((i%4*300+6,i//4*564+8),f'{t:.3f}s',fill='white')
contact.save(qa/'contact.jpg',quality=92)
shutil.move(str(staged),str(out))
print(json.dumps({'output':str(out),'qa':str(qa),'duration':a.duration,'size_bytes':out.stat().st_size,'integrated_LUFS':integrated,'true_peak_dBTP':tp,'technical_checks':'passed','visual_review':'required'},ensure_ascii=False))
