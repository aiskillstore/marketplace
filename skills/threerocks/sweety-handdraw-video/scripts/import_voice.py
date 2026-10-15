#!/usr/bin/env python3
"""Import a user-provided reference and exact transcript into one job only."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
from production_options import save_json


def import_reference(job, identifier, name, audio, transcript, reference_kind='user_supplied'):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', identifier):
        raise ValueError('Voice id must use lowercase letters, digits and hyphens')
    catalog_path = Path(__file__).resolve().parents[1]/'assets/voices/catalog.json'
    allowed_ids = {voice['id'] for voice in json.loads(catalog_path.read_text())['voices']}
    if identifier not in allowed_ids:
        raise ValueError('Choose one of the six catalog voices; retired or extra voices cannot be imported')
    if reference_kind not in ('user_supplied', 'source_recording', 'synthetic_direction'):
        raise ValueError('Unknown reference kind')
    audio, transcript = Path(audio).resolve(), Path(transcript).resolve()
    if not audio.is_file() or not transcript.is_file() or not transcript.read_text().strip():
        raise ValueError('Provide reference audio and its nonempty exact transcript')
    destination = Path(job).resolve()/'options/voices'/identifier
    destination.mkdir(parents=True,exist_ok=True)
    copied_audio, copied_text = destination/('reference'+audio.suffix), destination/'transcript.txt'
    if copied_audio.exists() or copied_text.exists():
        raise ValueError('This job already has a reference with that id')
    shutil.copyfile(audio,copied_audio); shutil.copyfile(transcript,copied_text)
    catalog_path = Path(job).resolve()/'options/local-voices.json'
    catalog = json.loads(catalog_path.read_text()) if catalog_path.is_file() else {'voices':[]}
    catalog['voices'] = [entry for entry in catalog['voices'] if entry['id'] != identifier] + [{
        'id':identifier,'name':name,'description':'用户指定参考音色；仅存放在当前任务',
        'reference_audio':str(copied_audio),'reference_text':str(copied_text),'source':'User-provided local reference','redistribution':'not bundled',
        'reference_kind':reference_kind,'reference_sha256':hashlib.sha256(copied_audio.read_bytes()).hexdigest(),
        'transcript_sha256':hashlib.sha256(copied_text.read_text().strip().encode()).hexdigest()}]
    save_json(catalog_path,catalog)
    return catalog_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job',type=Path); parser.add_argument('--id',required=True); parser.add_argument('--name',required=True)
    parser.add_argument('--audio',type=Path,required=True); parser.add_argument('--transcript',type=Path,required=True)
    parser.add_argument('--kind',choices=['user_supplied','source_recording','synthetic_direction'],default='user_supplied')
    args=parser.parse_args(); print(import_reference(args.job,args.id,args.name,args.audio,args.transcript,args.kind))
