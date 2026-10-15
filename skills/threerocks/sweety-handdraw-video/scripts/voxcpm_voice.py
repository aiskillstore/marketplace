#!/usr/bin/env python3
"""Generate narration with an explicitly configured, already installed VoxCPM2 model."""
import argparse
import hashlib
import json
from pathlib import Path
from voice_studio import voice_reference, load_voice_catalog
from narration_master import generation_target


def resolved_options(options, root):
    catalog = load_voice_catalog(root)
    identifier = options.get('voice', catalog['default'])
    profile = next((voice for voice in catalog['voices'] if voice['id'] == identifier), {})
    approved = profile.get('verified_generation_parameters', {})
    fields = ('mode', 'cfg_value', 'timesteps', 'seed', 'max_tokens', 'model_path', 'enhancement_model_path')
    defaults = {key: approved[key] for key in fields if key in approved}
    return {**defaults, 'voice': identifier, **options}


def enhancement_fingerprint(path):
    if not path:
        return None
    directory = Path(path).expanduser().resolve()
    weights = directory/'model.safetensors'
    if not directory.is_dir() or not weights.is_file():
        raise ValueError('Speech cleanup requires an explicitly configured, installed local model')
    return {'model_path':str(directory), 'weights_sha256':hashlib.sha256(weights.read_bytes()).hexdigest()}


def generate(job):
    import mlx.core as mx
    import numpy as np
    import soundfile as sf
    from mlx_audio.tts.utils import load
    root = Path(job).resolve()
    manifest = json.loads((root/'job.json').read_text())
    options = resolved_options(manifest.get('voxcpm', {}), root)
    model_path = Path(options.get('model_path', '')).expanduser()
    if not options.get('model_path') or not (model_path/'config.json').is_file():
        raise ValueError('Set voxcpm.model_path to an already installed local VoxCPM2 model')
    reference, transcript = voice_reference(options, root)
    model = load(str(model_path.resolve()))
    target, complete_text = generation_target(root, manifest)
    for beat in [{'id': 'narration-master', 'text': complete_text, 'audio': str(target)}]:
        target = (root/beat['audio']).resolve()
        if not target.is_relative_to(root):
            raise ValueError('Narration output must stay in the job')
        params = {'text':beat['text'],'seed':int(options.get('seed',2026)),
                  'timesteps':int(options.get('timesteps',10)),'cfg_value':float(options.get('cfg_value',2.)),
                  'mode':options.get('mode','combined'),'max_tokens':int(options.get('max_tokens',6500))}
        params['enhancement'] = enhancement_fingerprint(options.get('enhancement_model_path'))
        if params['mode'] not in ('combined','reference'):
            raise ValueError('VoxCPM2 mode must be combined or reference')
        signature = hashlib.sha256(json.dumps(params,sort_keys=True).encode()+reference.read_bytes()+transcript.encode()+str(model_path.resolve()).encode()).hexdigest()
        record_path = target.with_suffix('.voice.json')
        if target.is_file() and record_path.is_file() and json.loads(record_path.read_text()).get('signature') == signature:
            continue
        if target.exists() and not record_path.exists():
            raise ValueError('Existing untracked narration will not be overwritten: '+str(target))
        mx.random.seed(params['seed'])
        conditioning = {'prompt_audio':str(reference),'prompt_text':transcript} if params['mode']=='combined' else {}
        result = list(model.generate(text=beat['text'], ref_audio=str(reference), **conditioning,
                      inference_timesteps=params['timesteps'], cfg_value=params['cfg_value'], max_tokens=params['max_tokens']))
        samples = np.concatenate([np.asarray(chunk.audio) for chunk in result])
        if not len(samples) or not np.isfinite(samples).all():
            raise ValueError('Generated narration is empty or non-finite')
        if params['enhancement']:
            from mlx_audio.sts.models.deepfilternet import DeepFilterNetModel
            if result[0].sample_rate != 48000:
                raise ValueError('Configured speech cleanup requires a 48 kHz narration waveform')
            cleaner = DeepFilterNetModel.from_pretrained(params['enhancement']['model_path'], subfolder=None)
            enhanced = np.asarray(cleaner.enhance_array(samples), dtype=np.float32)
            if len(enhanced) != len(samples) or not np.isfinite(enhanced).all():
                raise ValueError('Speech cleanup changed narration duration or produced invalid samples')
            samples = enhanced
        target.parent.mkdir(parents=True,exist_ok=True)
        temporary = target.with_name(target.stem+'.generating.wav')
        sf.write(temporary,samples,result[0].sample_rate,subtype='PCM_24')
        temporary.replace(target)
        record_path.write_text(json.dumps({'signature':signature,'text':beat['text'],'model_path':str(model_path),
            'duration':len(samples)/result[0].sample_rate,'voice':options.get('voice'),'method':'single_call_complete_script','conditioning':params['mode'],
            'reference_audio':str(reference),'reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),
            'reference_text':transcript,'parameters':params,'subjective_listening':'not_performed'},ensure_ascii=False,indent=2))
        print('READY',beat.get('id',target.stem),flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job',type=Path)
    generate(parser.parse_args().job)
