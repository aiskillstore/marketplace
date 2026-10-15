from pathlib import Path
import hashlib
import json
import tempfile
import unittest
import wave
import numpy as np
from audio_contract import resolve_audio_layers, validate_ending
from drawing_contract import validate_narrative_requirements
from video_job import save_wave
from video_renderer import mix_audio

class AudioContractTests(unittest.TestCase):
    def test_default_mix_contains_only_narration_even_with_stale_music(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'work').mkdir()
            voice=np.zeros(96000,dtype=np.int16)
            voice[10000:70000]=(6000*np.sin(np.arange(60000)*2*np.pi*220/48000)).astype(np.int16)
            save_wave(root/'work/narration.wav',voice)
            save_wave(root/'work/music.wav',np.full(96000,20000,dtype=np.int16))
            mix_audio(root,{'duration':2.})
            with wave.open(str(root/'work/normalized-narration.wav')) as stream:
                normalized=np.frombuffer(stream.readframes(stream.getnframes()),dtype='<i2')
            with wave.open(str(root/'work/mix.wav')) as stream:
                mixed=np.frombuffer(stream.readframes(stream.getnframes()),dtype='<i2').reshape(-1,2)
            self.assertTrue(np.array_equal(mixed[:,0],mixed[:,1]))
            self.assertTrue(np.array_equal(mixed[:,0],normalized))
            self.assertTrue(json.loads((root/'work/audio-mix-report.json').read_text())['narration_only'])
    def test_music_requires_explicit_request_and_sound_effect_needs_reason(self):
        self.assertFalse(resolve_audio_layers('.',{})['background_music'])
        for audio in [{'music':True},{'music':{'source':'music.wav'}},{'sound_effects':[{'source':'a.wav'}]}]:
            with self.assertRaises(ValueError):resolve_audio_layers('.',{'audio':audio})
    def test_tail_guard_rejects_active_end_and_excess_silence(self):
        voice=(6000*np.sin(np.arange(48000)*2*np.pi*220/48000)).astype(np.int16)
        manifest={'pages':[{'beats':[{'text':'正文。完整结语。'}]}], 'ending':{'closing_text':'完整结语。'}}
        for padding in [0,48000]:
            with self.assertRaises(ValueError):validate_ending(manifest,np.pad(voice,(0,padding)),48000)
        result=validate_ending(manifest,np.pad(voice,(0,9600)),48000)
        self.assertAlmostEqual(result['total_tail_seconds'],.65)
        manifest['ending']['closing_text']='漏掉的订阅。'
        with self.assertRaises(ValueError):validate_ending(manifest,np.pad(voice,(0,9600)),48000)
    def test_narrative_gate_rejects_missing_or_failed_semantic_evidence(self):
        plan={'narrative_requirements':[{'id':'severed','narration_quote':'身体切断','observable':'三段蛇身之间有两处白色空隙'}]}
        for review in [{},{'narrative_checks':[{'id':'severed','status':'fail','evidence':'身体仍相连'}]}]:
            with self.assertRaises(ValueError):validate_narrative_requirements(plan,review,'身体切断。')
        review={'narrative_checks':[{'id':'severed','status':'pass','evidence':'两处断口和白色空隙清晰可见'}]}
        self.assertEqual(validate_narrative_requirements(plan,review,'身体切断。'),1)
        with self.assertRaises(ValueError):validate_narrative_requirements(plan,review,'蛇在睡觉。')

if __name__=='__main__':unittest.main()
