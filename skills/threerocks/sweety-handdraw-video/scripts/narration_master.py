"""Keep one complete narration waveform authoritative for every visual timing."""
from pathlib import Path
import hashlib
import json
import math
import subprocess
import wave
import numpy as np

SAMPLE_RATE = 48000


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def script_text(manifest):
    return ''.join(beat['text'] for page in manifest['pages'] for beat in page['beats'])


def generation_target(root, manifest):
    """TTS sees the complete script once; page boundaries are never synthesis units."""
    settings = manifest.get('narration', {})
    target = (Path(root) / settings.get('source', 'inputs/narration/master.wav')).resolve()
    if not target.is_relative_to(Path(root).resolve()):
        raise ValueError('Generated narration master must stay inside the job')
    text = script_text(manifest)
    closing = manifest.get('ending', {}).get('closing_text')
    if closing and not text.endswith(closing):
        raise ValueError('Add the requested closing to the complete script before generating narration')
    return target, text


def load_master(root, manifest, destination):
    settings = manifest.get('narration')
    if not settings or not settings.get('source') or not settings.get('alignment'):
        raise ValueError('Production requires narration.source and narration.alignment: finish the complete voice before visuals')
    options = manifest.get('audio', {})
    if float(options.get('pace', 1)) != 1 or options.get('trim_silence', False):
        raise ValueError('A locked narration master cannot be stretched or silence-trimmed')
    if any(float(options.get(key, 0)) != 0 for key in ('sentence_pause_seconds', 'page_pause_seconds')):
        raise ValueError('Page and sentence pauses cannot insert silence into a narration master')
    source = (Path(root) / settings['source']).resolve()
    alignment_path = (Path(root) / settings['alignment']).resolve()
    alignment = json.loads(alignment_path.read_text())
    if alignment.get('version', 1) != 1:
        raise ValueError('Unsupported narration alignment version')
    text = script_text(manifest)
    if alignment.get('source_sha256') != sha256(source):
        raise ValueError('Narration alignment belongs to a different audio master')
    if alignment.get('script_sha256') != hashlib.sha256(text.encode()).hexdigest():
        raise ValueError('Narration alignment belongs to a different script')
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(source), '-ar', str(SAMPLE_RATE),
                    '-ac', '1', '-c:a', 'pcm_s16le', str(destination)], check=True)
    with wave.open(str(destination)) as stream:
        samples = np.frombuffer(stream.readframes(stream.getnframes()), dtype='<i2').copy()
    if not len(samples) or not np.any(samples):
        raise ValueError('Narration master is empty or silent')
    duration = len(samples) / SAMPLE_RATE
    expected = [beat for page in manifest['pages'] for beat in page['beats']]
    entries = alignment.get('beats', [])
    if len(entries) != len(expected):
        raise ValueError('Narration alignment must cover every beat exactly once')
    previous_end = 0.
    beats = {}
    for expected_beat, entry in zip(expected, entries):
        identifier = expected_beat.get('id')
        if not identifier or entry.get('id') != identifier or entry.get('text') != expected_beat['text'] or identifier in beats:
            raise ValueError('Narration alignment IDs, order and text must match the script')
        start, end = float(entry['start']), float(entry['end'])
        if not math.isfinite(start + end) or not 0 <= previous_end <= start < end <= duration + 1 / SAMPLE_RATE:
            raise ValueError('Narration ranges must be finite, ordered, nonoverlapping and inside the master')
        beats[identifier] = {**entry, 'start': start, 'end': end}
        previous_end = end
    report = {'mode': 'continuous_master', 'source': str(source), 'source_sha256': sha256(source),
              'alignment': str(alignment_path), 'alignment_sha256': sha256(alignment_path),
              'duration': duration, 'sample_rate': SAMPLE_RATE, 'samples': len(samples),
              'pcm_sha256': hashlib.sha256(samples.astype('<i2').tobytes()).hexdigest(),
              'inserted_page_silence_seconds': 0, 'internal_samples_preserved': True}
    return samples, beats, report


def verify_compiled_master(root, timeline):
    """Detect lost breaths, inserted gaps, stale inputs or stretched master samples."""
    report = timeline.get('narration_master')
    if not report:
        return None
    if sha256(report['source']) != report['source_sha256'] or sha256(report['alignment']) != report['alignment_sha256']:
        raise ValueError('Narration master or alignment changed after build')
    with wave.open(str(Path(root) / 'work/narration.wav')) as stream:
        if (stream.getframerate(), stream.getnchannels(), stream.getsampwidth()) != (SAMPLE_RATE, 1, 2):
            raise ValueError('Compiled narration format changed')
        samples = np.frombuffer(stream.readframes(stream.getnframes()), dtype='<i2')
    start = round(timeline['cover_seconds'] * SAMPLE_RATE)
    master = samples[start:start + report['samples']]
    if hashlib.sha256(master.tobytes()).hexdigest() != report['pcm_sha256']:
        raise ValueError('Compiled narration changed the locked master waveform')
    if np.any(samples[:start]) or np.any(samples[start + report['samples']:]):
        raise ValueError('Cover and ending padding must not contain extra narration')
    return {'continuous_master': True, 'pcm_preserved': True, 'inserted_page_silence_seconds': 0}
