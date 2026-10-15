#!/usr/bin/env python3
"""Required narration adapter for local VoiceStudio; no hidden remote fallback."""
from pathlib import Path
from hosted_assets import resolve_asset, asset_available
import argparse
import hashlib
import json
import urllib.parse
import requests
from narration_master import generation_target

PACKAGE = Path(__file__).resolve().parents[1]
PERSONAL_CATALOG = Path.home()/'.local/share/sweety-handdraw-video/voices/catalog.json'


def load_voice_catalog(root):
    catalog = json.loads((PACKAGE/'assets/voices/catalog.json').read_text())
    profiles = {voice['id']: voice for voice in catalog['voices']}
    identities = {identifier: {key: profile[key] for key in ('name', 'description', 'requires_original_reference') if key in profile}
                  for identifier, profile in profiles.items()}
    for path in (PERSONAL_CATALOG, Path(root)/'options/local-voices.json'):
        if not path.is_file():
            continue
        local = json.loads(path.read_text())
        for entry in local['voices']:
            entry = dict(entry)
            if entry['id'] not in profiles:
                continue
            local_root = path.parent if path == PERSONAL_CATALOG else Path(root)
            for field in ('reference_audio', 'reference_text', 'preview_audio'):
                if entry.get(field):
                    value = Path(entry[field]).expanduser()
                    entry[field] = str(value if value.is_absolute() else (local_root/value).resolve())
            profiles[entry['id']].update(entry)
            profiles[entry['id']].update(identities[entry['id']])
        if local.get('default') in profiles:
            catalog['default'] = local['default']
    for profile in catalog['voices']:
        profile['preferred'] = profile['id'] == catalog['default']
    return catalog


def checked_reference(audio, transcript, expected_audio_hash=None, expected_text_hash=None):
    audio = Path(audio).resolve()
    if not audio.is_file() or not transcript.strip():
        raise ValueError('Voice reference requires an existing audio file and exact transcript')
    if expected_audio_hash and hashlib.sha256(audio.read_bytes()).hexdigest() != expected_audio_hash:
        raise ValueError('Voice reference audio changed after import')
    if expected_text_hash and hashlib.sha256(transcript.strip().encode()).hexdigest() != expected_text_hash:
        raise ValueError('Voice reference transcript changed after import')
    return audio, transcript.strip()


def voice_reference(options, root):
    root = Path(root).resolve()
    if options.get('reference_audio'):
        if not options.get('reference_text'):
            raise ValueError('A custom voice requires its exact reference transcript')
        return checked_reference(root/options['reference_audio'], options['reference_text'], options.get('reference_sha256'))
    directory=PACKAGE/'assets'/'voices'
    packaged=json.loads((directory/'catalog.json').read_text())
    catalog=load_voice_catalog(root)
    identifier=options.get('voice',catalog['default'])
    packaged_profile=next((voice for voice in packaged['voices'] if voice['id']==identifier),None)
    profile=next((voice for voice in catalog['voices'] if voice['id']==identifier),None)
    if profile is None:
        raise ValueError('Unknown voice: '+identifier)
    if not profile.get('reference_audio'):
        raise ValueError('Import the user-provided audio and exact transcript for this reference voice')
    if packaged_profile and packaged_profile.get('requires_original_reference'):
        if profile.get('reference_kind') != 'source_recording' or not profile.get('reference_sha256'):
            raise ValueError('This voice requires an imported source recording; generated previews cannot replace it')
    audio = Path(profile['reference_audio']).expanduser()
    transcript = Path(profile['reference_text']).expanduser()
    audio = audio if audio.is_absolute() else resolve_asset(directory/audio)
    transcript = transcript if transcript.is_absolute() else directory/transcript
    if not audio.is_file() or not transcript.is_file():
        raise ValueError('Voice reference audio or transcript is not installed: '+identifier)
    return checked_reference(audio, transcript.read_text(), profile.get('reference_sha256'), profile.get('transcript_sha256'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job', type=Path)
    parser.add_argument('--url', help='Override voice_studio.url; local HTTP only')
    parser.add_argument('--transcribe', action='store_true', help='Save ASR evidence for existing or generated clips')
    arguments = parser.parse_args()
    root = arguments.job.resolve()
    manifest = json.loads((root / 'job.json').read_text())
    options = manifest.get('voice_studio', {})
    service_url = (arguments.url or options.get('url','http://127.0.0.1:3900')).rstrip('/')
    endpoint = urllib.parse.urlparse(service_url)
    if endpoint.scheme != 'http' or endpoint.hostname not in ('127.0.0.1', 'localhost', '::1') or endpoint.username or endpoint.password:
        raise ValueError('This adapter accepts only an unauthenticated local VoiceStudio service')
    reference_audio,reference_text = voice_reference(options,root)
    try:
        response=requests.get(service_url + '/engines/tts', timeout=10)
        response.raise_for_status()
        engine=response.json()
    except requests.RequestException as error:
        raise SystemExit('VoiceStudio 未安装、未启动或服务不可达：本任务没有旁白，不会交付无声视频冒充完整成片。请安装并启动 VoiceStudio，或在 VoiceStudio 编辑后导出旁白。') from error
    backend = options.get('backend', 'mlx-audio')
    expected_model = options.get('model', 'mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16')
    if engine.get('active') != backend or engine.get('active_model') != expected_model:
        raise ValueError('VoiceStudio active engine/model differs from the configured voice; no global settings were changed')
    target, complete_text = generation_target(root, manifest)
    for beat in [{'id': 'narration-master', 'text': complete_text, 'audio': str(target)}]:
        target = (root / beat['audio']).resolve()
        if not target.is_relative_to(root):
            raise ValueError('Generated voice clips must stay inside the job directory')
        target.parent.mkdir(parents=True, exist_ok=True)
        fields = {'text': beat['text'], 'ref_text': reference_text, 'language': options.get('language', 'Chinese'),
                  'engine': backend, 'seed': str(options.get('seed', 2026)), 'speed': str(options.get('speed', 1.03)),
                  'effect_preset': options.get('effect_preset', 'broadcast'), 'max_chunk_chars': '0'}
        signature = hashlib.sha256(json.dumps({'fields': fields, 'model': expected_model}, sort_keys=True).encode() + reference_audio.read_bytes()).hexdigest()
        record_path = target.with_suffix('.voice.json')
        cached = target.is_file() and record_path.is_file() and json.loads(record_path.read_text()).get('signature') == signature
        if not cached:
            if target.exists() and not record_path.exists():
                raise ValueError(f'Existing untracked audio will not be overwritten: {target}')
            print('GENERATING', beat.get('id', target.stem), flush=True)
            with reference_audio.open('rb') as reference:
                response = requests.post(service_url + '/generate', data=fields,
                    files={'ref_audio': ('reference.wav', reference, 'audio/wav')}, timeout=600)
            response.raise_for_status()
            if not response.headers.get('Content-Type', '').startswith('audio/'):
                raise ValueError('VoiceStudio did not return audio')
            temporary = target.with_suffix('.generating.wav')
            temporary.write_bytes(response.content)
            temporary.replace(target)
            record_path.write_text(json.dumps({'signature': signature, 'text': beat['text'], 'model': expected_model,
                'duration': response.headers.get('X-Audio-Duration')}, ensure_ascii=False, indent=2))
        if arguments.transcribe:
            with target.open('rb') as audio_file:
                response = requests.post(service_url + '/transcribe', files={'audio': (target.name, audio_file, 'audio/wav')},
                    data={'mode': 'reference', 'language': options.get('asr_language', 'zh')}, timeout=300)
            response.raise_for_status()
            target.with_suffix('.asr.json').write_text(json.dumps({'expected': beat['text'], 'response': response.json()}, ensure_ascii=False, indent=2))
        print('READY', beat.get('id', target.stem), flush=True)


if __name__ == '__main__':
    main()
