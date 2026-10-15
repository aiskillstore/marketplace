#!/usr/bin/env python3
"""Collect optional production choices with an independent per-step deadline."""
import argparse
import json
from pathlib import Path
from hosted_assets import resolve_asset, asset_available
import secrets
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit
from style_choice import prepare_catalog, validate_selection

PACKAGE = Path(__file__).resolve().parents[1]
STAGES = ('style', 'hand', 'voice', 'advertising', 'watermark', 'captions')


def save_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n')
    temporary.replace(path)


def validate_choice(stage, value, catalog, hands, voices):
    if not isinstance(value, dict):
        raise ValueError('Choice must be an object')
    if stage == 'style':
        validate_selection(value, catalog)
    elif stage == 'hand' and value.get('preset') not in {hand['id'] for hand in hands}:
        raise ValueError('Unknown drawing tool')
    elif stage == 'voice' and value.get('voice') not in {voice['id'] for voice in voices if voice.get('available', True)}:
        raise ValueError('This voice reference is not installed')
    elif stage == 'advertising' and (not isinstance(value.get('text'), str) or len(value['text']) > 16):
        raise ValueError('笔杆广告最多16个字符，不能自动截短')
    elif stage == 'watermark' and (not isinstance(value.get('text'), str) or len(value['text']) > 180):
        raise ValueError('请输入不超过180个字符的水印，或留空不加')
    elif stage == 'captions' and value.get('mode') not in ('quiet', 'plate'):
        raise ValueError('Unknown subtitle appearance')


class ChoiceSession:
    def __init__(self, job, defaults, explicit, catalog, hands, voices, timeout=60, now=None):
        if not isinstance(defaults.get('content'), str) or not defaults['content'].strip():
            raise ValueError('MISSING_CONTENT: 请先输入主题或故事内容')
        self.job, self.defaults = Path(job), defaults
        self.catalog, self.hands, self.voices = catalog, hands, voices
        self.timeout = min(60, max(.01, float(timeout)))
        saved_path = self.job/'options/selection.json'
        saved = json.loads(saved_path.read_text()) if saved_path.is_file() else {}
        if saved and saved.get('content') != defaults['content']:
            raise ValueError('Use a new job directory for different content; existing choices were preserved')
        self.choices, self.index = dict(saved.get('choices', {})), 0
        self.started = time.monotonic() if now is None else now
        for stage in STAGES:
            validate_choice(stage, defaults[stage], catalog, hands, voices)
            if stage in self.choices:
                validate_choice(stage, self.choices[stage]['value'], catalog, hands, voices)
            if stage in explicit:
                validate_choice(stage, explicit[stage], catalog, hands, voices)
                self.choices[stage] = {'value':explicit[stage], 'reason':'explicit_user_request'}
        self.skip_answered()
        self.persist()

    def skip_answered(self):
        while self.index < len(STAGES) and STAGES[self.index] in self.choices:
            self.index += 1

    def persist(self):
        save_json(self.job/'options/selection.json', {'complete':self.index == len(STAGES), 'choices':self.choices,
                  'timeout_seconds':self.timeout, 'content':self.defaults['content']})
        if 'style' in self.choices:
            choice = self.choices['style']
            selection = dict(choice['value'])
            selection.update(confirmation=choice['reason'], evidence=('No answer before the optional preference deadline; used model-authored defaults' if choice['reason']=='timeout_default' else 'User selected or delegated this style route'))
            save_json(self.job/'style/selection.json', selection)

    def advance(self, now=None):
        now = time.monotonic() if now is None else now
        changed = False
        while self.index < len(STAGES) and now-self.started >= self.timeout:
            stage = STAGES[self.index]
            self.choices[stage] = {'value':self.defaults[stage], 'reason':'timeout_default', 'waited_seconds':self.timeout}
            self.index += 1
            self.skip_answered()
            self.started += self.timeout
            changed = True
        if changed:
            self.persist()
        return self.status(now)

    def choose(self, stage, value, now=None):
        now = time.monotonic() if now is None else now
        self.advance(now)
        if self.index == len(STAGES) or stage != STAGES[self.index]:
            raise ValueError('This step has advanced; use the saved choices or submit a later correction in chat')
        validate_choice(stage, value, self.catalog, self.hands, self.voices)
        self.choices[stage] = {'value':value, 'reason':'user_dialog'}
        self.index += 1
        self.skip_answered()
        self.started = now
        self.persist()
        return self.status(now)

    def status(self, now):
        complete = self.index == len(STAGES)
        return {'complete':complete, 'stage':None if complete else STAGES[self.index], 'index':self.index,
                'remaining_seconds':0 if complete else max(0,self.timeout-(now-self.started)), 'choices':self.choices}


def load_voices(job):
    from voice_studio import load_voice_catalog
    voices = load_voice_catalog(job)['voices']
    for voice in voices:
        voice['audio_path'] = str(PACKAGE/'assets/voices'/voice['reference_audio']) if voice.get('reference_audio') else None
        voice['available'] = bool(voice['audio_path'] and asset_available(Path(voice['audio_path'])))
        if voice.get('requires_original_reference'):
            voice['available'] = voice['available'] and voice.get('reference_kind') == 'source_recording' and bool(voice.get('reference_sha256'))
        preview = PACKAGE/'assets/voices'/voice.get('preview_audio', '')
        if voice.get('preview_audio') and asset_available(preview):
            voice['audio_path'] = str(preview)
        voice['preview_available'] = bool(voice['audio_path'] and asset_available(Path(voice['audio_path'])))
    return voices


def apply_choices(job):
    job = Path(job).resolve()
    selection = json.loads((job/'options/selection.json').read_text())
    if not selection.get('complete'):
        raise ValueError('Optional choice collection is still running')
    choices = {name:entry['value'] for name,entry in selection['choices'].items()}
    manifest = json.loads((job/'job.json').read_text())
    hand = dict(choices['hand'])
    hand['pen_text'] = choices['advertising']['text']
    manifest['hand'] = hand
    manifest['watermark'] = {'text':choices['watermark']['text'], 'opacity':.24}
    for engine in ('voice_studio','voxcpm'):
        options = manifest.setdefault(engine,{})
        options.pop('reference_audio',None)
        options.pop('reference_text',None)
        options.update(choices['voice'])
    captions = manifest.setdefault('captions',{})
    captions.update(color='#FFFFFF', stroke_width=2, stroke_color='#000000')
    if choices['captions']['mode'] == 'quiet':
        captions.update(background=None)
    else:
        captions.update(background={'color':'#243039','opacity':.76},color='#FFFFFF')
    save_json(job/'job.json',manifest)
    return manifest


def serve(job, defaults_path, explicit_path=None, port=0, timeout=60):
    job = Path(job).resolve()
    defaults = json.loads(Path(defaults_path).read_text())
    if not isinstance(defaults.get('content'), str) or not defaults['content'].strip():
        raise ValueError('MISSING_CONTENT: 请先输入主题或故事内容')
    explicit = json.loads(Path(explicit_path).read_text()) if explicit_path else {}
    catalog_path = job/'style/catalog.json'
    catalog = json.loads(catalog_path.read_text()) if catalog_path.is_file() else prepare_catalog(job, PACKAGE/'dependencies/hand-drawn-styles')
    hands = json.loads((PACKAGE/'assets/hands/catalog.json').read_text())['presets']
    voices = load_voices(job)
    session = ChoiceSession(job, defaults, explicit, catalog, hands, voices, timeout)
    token = secrets.token_urlsafe(24)
    payload = {'catalog':catalog,'hands':hands,'voices':[{k:v for k,v in voice.items() if k != 'audio_path'} for voice in voices], 'defaults':defaults}
    template = (PACKAGE/'assets/production-options.html').read_text()
    page = template.replace('__DATA__', json.dumps(payload,ensure_ascii=False).replace('<','\\u003c')).replace('__TOKEN__',token).encode()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def reply(self,status,body,kind='application/json'):
            self.send_response(status); self.send_header('Content-Type',kind); self.send_header('Content-Length',str(len(body))); self.send_header('Cache-Control','no-store'); self.send_header('X-Content-Type-Options','nosniff'); self.end_headers(); self.wfile.write(body)
        def do_GET(self):
            path = urlsplit(self.path).path
            if path == '/': return self.reply(200,page,'text/html; charset=utf-8')
            if path == '/status': return self.reply(200,json.dumps(session.advance()).encode())
            allowed = {}
            for hand in hands: allowed['/hands/'+hand['id']] = (PACKAGE/'assets/hands'/hand['source'],'image/png')
            for voice in voices:
                if voice['preview_available']: allowed['/voices/'+voice['id']] = (Path(voice['audio_path']),'audio/wav')
            for style in catalog['styles']:
                if not style['preview'].startswith('http'): allowed['/'+style['preview']] = (job/'style'/style['preview'],'image/jpeg')
            if path in allowed:
                source,kind = allowed[path]
                try:
                    return self.reply(200,resolve_asset(source).read_bytes(),kind)
                except (OSError, ValueError) as error:
                    return self.reply(503,json.dumps({'error':str(error)}).encode())
            return self.reply(404,b'{}')
        def do_POST(self):
            if self.path != '/choice' or self.headers.get('Origin') != 'http://127.0.0.1:'+str(self.server.server_port) or self.headers.get('X-Options-Token') != token:
                return self.reply(403,b'{}')
            try:
                length = int(self.headers.get('Content-Length',0))
                if not 0 < length < 12000: raise ValueError('Invalid request length')
                answer = json.loads(self.rfile.read(length))
                status = session.choose(answer['stage'], answer['value'])
                self.reply(200,json.dumps(status).encode())
            except (KeyError,ValueError,TypeError) as error:
                self.reply(400,json.dumps({'error':str(error)},ensure_ascii=False).encode())
    server = HTTPServer(('127.0.0.1',port),Handler)
    server.timeout = .5
    print('PRODUCTION_OPTIONS_URL=http://127.0.0.1:'+str(server.server_port),flush=True)
    announced = False
    while True:
        server.handle_request()
        if session.advance()['complete'] and not announced:
            print('PRODUCTION_OPTIONS_COMPLETE='+str(job/'options/selection.json'),flush=True)
            announced = True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job',type=Path)
    parser.add_argument('--defaults',type=Path)
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--explicit',type=Path)
    parser.add_argument('--port',type=int,default=0)
    parser.add_argument('--timeout',type=float,default=60)
    args = parser.parse_args()
    if args.apply:
        apply_choices(args.job)
        print('PRODUCTION_OPTIONS_APPLIED='+str(args.job/'job.json'))
    elif not args.defaults:
        parser.error('--defaults is required when collecting choices')
    else:
        serve(args.job,args.defaults,args.explicit,args.port,args.timeout)
