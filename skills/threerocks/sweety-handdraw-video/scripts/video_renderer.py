"""Render measured story timelines with path-based text, artwork and marker motion."""
from pathlib import Path
import bisect
import json
import math
import subprocess
import wave
import numpy as np
from PIL import Image, ImageColor
from watermark_assets import watermark_position


def ease(fraction):
    fraction=float(np.clip(fraction,0,1))
    return fraction*fraction*(3-2*fraction)


def point_on_asset(metadata,progress):
    previous = None
    for segment in metadata['segments']:
        if progress < segment['start']:
            if previous:
                fraction = ease((progress-previous['end'])/max(1e-7,segment['start']-previous['end']))
                origin=np.array(previous['points'][-1]); destination=np.array(segment['points'][0])
                return origin+fraction*(destination-origin)+[0,-10*math.sin(math.pi*fraction)]
            return np.array(segment['points'][0])
        if segment['start']<=progress<=segment['end']:
            fraction=(progress-segment['start'])/max(1e-7,segment['end']-segment['start'])
            points=np.array(segment['points'])
            if segment['kind']=='travel':
                return points[0]+ease(fraction)*(points[-1]-points[0])+[0,-10*math.sin(math.pi*fraction)]
            distances=np.array(segment['lengths'])
            target=fraction*distances[-1]
            return np.array([np.interp(target,distances,points[:,0]),np.interp(target,distances,points[:,1])])
        previous=segment
    if progress<metadata['segments'][0]['start']:
        return np.array(metadata['segments'][0]['points'][0])
    return np.array(metadata['segments'][-1]['points'][-1])


class Renderer:
    def __init__(self, job_directory):
        self.root=Path(job_directory).resolve()
        self.work=self.root/'work'
        self.output=self.root/'outputs'
        self.timeline=json.loads((self.work/'timeline.json').read_text())
        self.width=self.timeline['canvas']['width']
        self.height=self.timeline['canvas']['height']
        self.fps=self.timeline['canvas']['fps']
        self.paper=ImageColor.getrgb(self.timeline['paper'])+(255,)
        self.starts=[page['start'] for page in self.timeline['pages']]
        self.artwork={name:Image.open(self.work/'assets'/f'{name}.png').convert('RGBA') for name in self.timeline['assets']}
        self.pixels={name:np.array(image) for name,image in self.artwork.items()}
        self.maps={name:np.load(self.work/'assets'/f'{name}.npz') for name in self.timeline['assets']}
        self.cover=Image.open(self.output/'cover.png').convert('RGBA')
        hand=Image.open(self.timeline['hand']['source']).convert('RGBA')
        scale=self.timeline['hand']['scale']
        self.hand=hand.resize((round(hand.width*scale),round(hand.height*scale)),Image.Resampling.LANCZOS)
        self.nib=np.array(self.timeline['hand']['nib'])*scale
        self.watermark = Image.open(self.timeline['watermark']['source']).convert('RGBA') if self.timeline.get('watermark') else None

    def layer(self,event,time):
        name=event['asset']
        if event.get('caption') or time>=event['end']:
            return self.artwork[name]
        progress=np.clip((time-event['start'])/(event['end']-event['start']),0,1)
        maps=self.maps[name]
        pixels=self.pixels[name].copy()
        if 'ink' in maps:
            ink_fraction=np.clip((progress-maps['ink'])*250,0,1)
            color_fraction=np.clip((progress-maps['color'])*250,0,1)
            fraction=maps['ink_weight']*ink_fraction+(1-maps['ink_weight'])*color_fraction
        else:
            fraction=np.clip((progress-maps['reveal'])*250,0,1)
        pixels[:,:,3]=np.rint(pixels[:,:,3]*fraction).astype(np.uint8)
        return Image.fromarray(pixels)

    def event_tip(self,event,progress):
        metadata=self.timeline['assets'][event['asset']]
        return np.array([event['x'],event['y']])+point_on_asset(metadata,progress)

    def pen(self,page,time):
        events=sorted((event for event in page['events'] if not event['caption']),key=lambda event:event['start'])
        previous=None
        for event in events:
            if event['start']<=time<=event['end']:
                progress=(time-event['start'])/(event['end']-event['start'])
                return self.event_tip(event,progress)
            if time<event['start']:
                following=self.event_tip(event,0)
                if previous and event['start']-previous['end']<.25:
                    origin=self.event_tip(previous,1)
                    progress=ease((time-previous['end'])/(event['start']-previous['end']))
                    return origin+progress*(following-origin)+[0,-12*math.sin(math.pi*progress)]
                if previous and time<previous['end']+.22:
                    origin=self.event_tip(previous,1)
                    return origin+ease((time-previous['end'])/.22)*np.array([650,750])
                if event['start']-time<.16:
                    return following+(1-ease(1-(event['start']-time)/.16))*np.array([650,750])
                return None
            previous=event
        if previous and time<previous['end']+.22:
            return self.event_tip(previous,1)+ease((time-previous['end'])/.22)*np.array([650,750])
        return None

    def page_frame(self,index,time,include_hand=True,include_captions=True):
        page=self.timeline['pages'][index]
        frame=Image.new('RGBA',(self.width,self.height),self.paper)
        events=sorted(page['events'],key=lambda event:(event['z'],event['start']))
        for event in events:
            if event['caption']:
                continue
            if event['start']<=time<event['hide']:
                frame.alpha_composite(self.layer(event,time),(event['x'],event['y']))
        if include_hand:
            point=self.pen(page,time)
            if point is not None:
                frame.alpha_composite(self.hand,tuple(np.rint(point-self.nib).astype(int)))
        if include_captions:
            for event in events:
                if event['caption'] and event['start']<=time<event['hide']:
                    frame.alpha_composite(self.layer(event,time),(event['x'],event['y']))
        return frame

    def frame(self,time):
        if time<self.timeline['cover_seconds']:
            frame=self.cover.copy()
            if time>.5:
                canvas=Image.new('RGBA',(self.width,self.height),self.paper)
                frame=Image.blend(frame,canvas,(time-.5)/.5)
            return frame.convert('RGB')
        index=min(len(self.starts)-1,max(0,bisect.bisect_right(self.starts,time)-1))
        page=self.timeline['pages'][index]
        frame=self.page_frame(index,time)
        remaining=page['end']-time
        if remaining<.24 and index<len(self.starts)-1:
            offset=round(self.width*ease(1-remaining/.24))
            canvas=Image.new('RGBA',(self.width,self.height),self.paper)
            canvas.alpha_composite(frame,(-offset,0))
            frame=canvas
        fade = self.timeline.get('ending', {}).get('fade_seconds', 0)
        if index == len(self.starts) - 1 and fade > 0 and remaining < fade:
            frame = Image.blend(frame, Image.new('RGBA', frame.size, self.paper), ease(1 - remaining / fade))
        if getattr(self, 'watermark', None) is not None and time >= self.timeline['watermark']['start_seconds']:
            frame.alpha_composite(self.watermark, watermark_position(self.timeline['watermark'], self.width, self.height, time))
        return frame.convert('RGB')


def mix_audio(root,timeline):
    root=Path(root)/'work'
    with wave.open(str(root/'narration.wav'),'rb') as stream:
        rate=stream.getframerate()
        samples=np.frombuffer(stream.readframes(stream.getnframes()),dtype='<i2')
    policy = timeline.get('audio_policy', {'background_music': False, 'layers': []})
    normalized_path=root/'normalized-narration.wav'
    # Duplicating mono into two full-level channels adds 3 LU to stereo loudness.
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(root/'narration.wav'),'-af','loudnorm=I=-20:TP=-2:LRA=7',
                    '-ar',str(rate),'-ac','1','-c:a','pcm_s16le',str(normalized_path)],check=True)
    layers = policy.get('layers', [])
    if not layers:
        # No implicit soundtrack and no buffered amix/limiter tail on narration-only output.
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(normalized_path),'-af','pan=stereo|c0=c0|c1=c0',
                        '-c:a','pcm_s16le',str(root/'mix.wav')],check=True)
    else:
        from narration_master import sha256
        command=['ffmpeg','-y','-v','error','-i',str(normalized_path)]
        filters=[]
        for index, layer in enumerate(layers, 1):
            if sha256(layer['source']) != layer['sha256']:
                raise ValueError('Audio layer changed after build')
            command.extend(['-i',layer['source']])
            filters.append(f"[{index}:a]volume={layer['gain']},adelay={round(layer['start']*1000)}:all=1[layer{index}]")
        inputs='[0:a]'+''.join(f'[layer{index}]' for index in range(1,len(layers)+1))
        filters.append(inputs+f'amix=inputs={len(layers)+1}:duration=first:normalize=0,alimiter=limit=0.89:level=false:latency=true[out]')
        command.extend(['-filter_complex',';'.join(filters),'-map','[out]','-ar',str(rate),'-ac','2',str(root/'mix.wav')])
        subprocess.run(command,check=True)
    (root/'audio-mix-report.json').write_text(json.dumps({'background_music':policy.get('background_music',False),
        'layers':layers,'narration_only':not layers,'delivery_notice':policy.get('delivery_notice',
        '默认未添加背景音乐；可自行合成，或在发布平台选择配乐。')},ensure_ascii=False,indent=2))
    with wave.open(str(root/'mix.wav'),'rb') as mixed_stream:
        mixed_seconds=mixed_stream.getnframes()/mixed_stream.getframerate()
    if abs(mixed_seconds-len(samples)/rate)>.01:
        raise ValueError('Audio mixing changed narration duration; refusing to encode a truncated track')


def encode(renderer,path,start=0.,duration=None):
    duration=renderer.timeline['duration']-start if duration is None else duration
    if start < 0 or duration <= 0 or start+duration > renderer.timeline['duration']+.001:
        raise ValueError('Preview interval must stay within the narration timeline')
    temporary_path=path.with_name(path.stem+'.rendering'+path.suffix)
    command=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{renderer.width}x{renderer.height}','-r',str(renderer.fps),'-i','-','-ss',str(start),'-i',str(renderer.work/'mix.wav'),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t',str(duration),'-movflags','+faststart','-map_metadata','-1',str(temporary_path)]
    process=subprocess.Popen(command,stdin=subprocess.PIPE)
    for index in range(math.ceil(duration*renderer.fps)):
        process.stdin.write(renderer.frame(start+index/renderer.fps).tobytes())
        if index%(15*renderer.fps)==0:
            print('RENDER',index/renderer.fps,'/',round(duration,2),flush=True)
    process.stdin.close()
    if process.wait()!=0:
        raise RuntimeError('ffmpeg failed to encode the video')
    temporary_path.replace(path)



def export_storyboard(renderer):
    review=renderer.work/'review'
    review.mkdir(parents=True,exist_ok=True)
    rows=math.ceil((len(renderer.timeline['pages'])+1)/2)
    sheet=Image.new('RGB',(1280,360*rows),renderer.paper[:3])
    frames=[renderer.cover.convert('RGB')]
    for page in renderer.timeline['pages']:
        frame=renderer.page_frame(page['index'],page['speech_end']-.15,False).convert('RGB')
        frame.save(review/f"page-{page['index']:02d}.jpg",quality=94)
        frames.append(frame)
    for index,frame in enumerate(frames):
        frame.thumbnail((640,360))
        sheet.paste(frame,((index%2)*640,(index//2)*360))
    sheet.save(review/'storyboard-contact.jpg',quality=95)


def render_job(job_directory,start=0.,duration=None,preview=False):
    from video_verifier import build_fingerprint, file_hash, verify_assets
    from art_direction import verify_art_direction
    renderer=Renderer(job_directory)
    verify_art_direction(renderer.root,json.loads((renderer.root/'job.json').read_text()))
    verify_assets(renderer.root,renderer.timeline)
    from narration_master import verify_compiled_master
    verify_compiled_master(renderer.root, renderer.timeline)
    from timeline_contract import validate_timeline,validate_cover
    validate_timeline(renderer.timeline)
    validate_cover(renderer)
    export_storyboard(renderer)
    mix_audio(renderer.root,renderer.timeline)
    path=renderer.work/'review'/'preview.mp4' if preview else renderer.output/'film.mp4'
    if not preview and (start or duration is not None):
        raise ValueError('Use --preview for partial renders; delivery film must include the complete timeline')
    encode(renderer,path,start,duration)
    from subtitle_contract import validate_subtitle_delivery
    validate_subtitle_delivery(path)
    if not preview:
        record={'video_sha256':file_hash(path),'build_fingerprint':build_fingerprint(renderer.root)}
        (renderer.work/'render-record.json').write_text(json.dumps(record,indent=2))
    print(str(path))
    return path
