"""Prevent derivative previews and changed source files from silently becoming references."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from import_voice import import_reference
from production_options import load_voices
from voice_studio import voice_reference, load_voice_catalog
from voxcpm_voice import resolved_options, enhancement_fingerprint


class VoiceReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.audio = self.root / 'source.wav'
        self.text = self.root / 'source.txt'
        self.audio.write_bytes(b'original recording fixture')
        self.text.write_text('这是准确的原文。')
        self.personal = patch('voice_studio.PERSONAL_CATALOG', self.root/'personal/catalog.json')
        self.personal.start()

    def tearDown(self):
        self.personal.stop()
        self.temporary.cleanup()

    def test_packaged_derivative_is_unavailable_for_exact_source_voice(self):
        profile = next(item for item in load_voices(self.root) if item['id'] == 'bilibili-outro')
        self.assertFalse(profile['available'])
        with self.assertRaisesRegex(ValueError, 'Import'):
            voice_reference({'voice': 'bilibili-outro'}, self.root)

    def test_source_import_can_be_used_and_audio_changes_are_rejected(self):
        import_reference(self.root, 'bilibili-outro', '原片女声', self.audio, self.text, 'source_recording')
        audio, text = voice_reference({'voice': 'bilibili-outro'}, self.root)
        self.assertEqual(text, self.text.read_text())
        self.assertTrue(next(item for item in load_voices(self.root) if item['id'] == 'bilibili-outro')['available'])
        audio.write_bytes(b'replaced by generated preview')
        with self.assertRaisesRegex(ValueError, 'changed after import'):
            voice_reference({'voice': 'bilibili-outro'}, self.root)

    def test_synthetic_import_cannot_satisfy_an_original_reference(self):
        import_reference(self.root, 'bilibili-outro', '合成方向', self.audio, self.text, 'synthetic_direction')
        self.assertFalse(next(item for item in load_voices(self.root) if item['id'] == 'bilibili-outro')['available'])
        with self.assertRaisesRegex(ValueError, 'generated previews'):
            voice_reference({'voice': 'bilibili-outro'}, self.root)

    def test_transcript_changes_are_rejected(self):
        catalog = import_reference(self.root, 'calm-woman', '知性女讲师', self.audio, self.text)
        profile = json.loads(catalog.read_text())['voices'][0]
        Path(profile['reference_text']).write_text('不同的文本。')
        with self.assertRaisesRegex(ValueError, 'transcript changed'):
            voice_reference({'voice': 'calm-woman'}, self.root)

    def test_stale_local_catalog_cannot_restore_retired_voices_or_names(self):
        directory = self.root/'options'
        directory.mkdir()
        (directory/'local-voices.json').write_text(json.dumps({'default':'friendly-man','voices':[
            {'id':'friendly-man','name':'旧男声'},
            {'id':'bilibili-outro','name':'旧女声名','requires_original_reference':False}]}))
        catalog = load_voice_catalog(self.root)
        self.assertEqual([voice['name'] for voice in catalog['voices']],
                         ['逼真男声','逼真女声','甜美学姐','Iapetus','知性女讲师','故事解说'])
        self.assertEqual(catalog['default'], 'iapetus')
        with self.assertRaisesRegex(ValueError, 'Unknown voice'):
            voice_reference({'voice':'friendly-man'}, self.root)
        with self.assertRaisesRegex(ValueError, 'six catalog voices'):
            import_reference(self.root, 'warm-elder', '旧旁白', self.audio, self.text)
        self.assertTrue(next(voice for voice in catalog['voices'] if voice['id']=='bilibili-outro')['requires_original_reference'])

    def test_both_film_voices_keep_preview_separate_from_source_reference(self):
        for identifier in ('realistic-man', 'bilibili-outro'):
            profile = next(voice for voice in load_voices(self.root) if voice['id']==identifier)
            self.assertFalse(profile['available'])
            self.assertTrue(profile['preview_available'])
            import_reference(self.root, identifier, profile['name'], self.audio, self.text, 'source_recording')
            reference, _ = voice_reference({'voice':identifier}, self.root)
            self.assertNotEqual(str(reference), profile['audio_path'])
            self.assertTrue(next(voice for voice in load_voices(self.root) if voice['id']==identifier)['available'])

    def test_personal_default_uses_source_recording_and_job_can_override_it(self):
        catalog = import_reference(self.root/'personal', 'bilibili-outro', '主力女声', self.audio, self.text, 'source_recording')
        personal = json.loads(catalog.read_text())
        personal['default'] = 'bilibili-outro'
        personal['voices'][0]['verified_generation_parameters'] = {'mode':'combined', 'cfg_value':1.5, 'timesteps':24}
        destination = self.root/'personal/catalog.json'
        destination.write_text(json.dumps(personal))
        reference, _ = voice_reference({}, self.root)
        self.assertEqual(reference, Path(personal['voices'][0]['reference_audio']))
        self.assertTrue(next(item for item in load_voices(self.root) if item['id']=='bilibili-outro')['preferred'])
        reference, _ = voice_reference({'voice':'iapetus'}, self.root)
        self.assertEqual(reference.name, 'iapetus.wav')
        self.assertEqual(resolved_options({}, self.root)['cfg_value'], 1.5)
        self.assertEqual(resolved_options({'cfg_value':1.7}, self.root)['cfg_value'], 1.7)

    def test_cleanup_model_is_local_and_model_change_invalidates_cache(self):
        self.assertIsNone(enhancement_fingerprint(None))
        with self.assertRaisesRegex(ValueError, 'installed local model'):
            enhancement_fingerprint(self.root/'missing')
        directory = self.root/'cleanup-model'
        directory.mkdir()
        weights = directory/'model.safetensors'
        weights.write_bytes(b'first fixture')
        original = enhancement_fingerprint(directory)
        weights.write_bytes(b'changed fixture')
        self.assertNotEqual(original, enhancement_fingerprint(directory))


if __name__ == '__main__':
    unittest.main()
