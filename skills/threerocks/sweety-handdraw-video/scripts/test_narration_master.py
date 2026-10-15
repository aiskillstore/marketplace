"""Regressions for voice continuity when scenes change or alignment becomes stale."""
from pathlib import Path
import hashlib
import json
import tempfile
import unittest
import wave
import numpy as np
from PIL import Image
from narration_master import load_master, sha256, script_text, verify_compiled_master, generation_target
from video_job import FilmBuilder, save_wave


class NarrationMasterTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        Image.new('RGB', (640, 360), 'white').save(self.root/'cover.png')
        # A real gap plus quiet nonzero breath must survive page changes byte-for-byte.
        time = np.arange(8 * 48000) / 48000
        self.samples = (np.sin(time * 2 * np.pi * 220) * 7000).astype(np.int16)
        self.samples[3 * 48000:round(3.5 * 48000)] = 0
        self.samples[round(3.5 * 48000):4 * 48000] //= 30
        save_wave(self.root/'master.wav', self.samples)
        self.manifest = {'version': 1, 'runtime_fixture': True, 'title': '连续旁白',
            'canvas': {'width': 640, 'height': 360, 'fps': 24},
            'cover': {'source': 'cover.png'}, 'audio': {'end_hold_seconds': 1},
            'narration': {'source': 'master.wav', 'alignment': 'alignment.json'},
            'pages': [{'beats': [{'id': name, 'text': text, 'actions':
                [{'type': 'text', 'text': text, 'x': 30, 'y': 30, 'size': 30}]}]}
                for name, text in [('a', '前一句。'), ('b', '后一句。')]]}
        self.alignment = {'source_sha256': sha256(self.root/'master.wav'),
            'script_sha256': hashlib.sha256(script_text(self.manifest).encode()).hexdigest(),
            'beats': [{'id': beat['id'], 'text': beat['text'], 'start': start, 'end': end}
                for beat, start, end in [(self.manifest['pages'][0]['beats'][0], 0, 3),
                                        (self.manifest['pages'][1]['beats'][0], 4, 7.8)]]}
        self.write_inputs()

    def tearDown(self):
        self.temporary.cleanup()

    def write_inputs(self):
        (self.root/'job.json').write_text(json.dumps(self.manifest))
        (self.root/'alignment.json').write_text(json.dumps(self.alignment))

    def test_page_change_preserves_every_master_sample_and_breath(self):
        timeline = FilmBuilder(self.root).build()
        self.assertEqual(timeline['pages'][1]['start'], 5)
        self.assertEqual(timeline['duration'], 10)
        self.assertEqual(timeline['cues'][-1]['end'], 9)
        self.assertTrue(verify_compiled_master(self.root, timeline)['pcm_preserved'])
        with wave.open(str(self.root/'work/narration.wav')) as stream:
            audio = np.frombuffer(stream.readframes(stream.getnframes()), dtype='<i2')
        self.assertTrue(np.array_equal(audio[48000:9 * 48000], self.samples))

    def test_different_page_grouping_does_not_change_audio(self):
        first = FilmBuilder(self.root).build()
        before = (self.root/'work/narration.wav').read_bytes()
        self.manifest['pages'][0]['beats'] += self.manifest['pages'].pop()['beats']
        self.write_inputs()
        second = FilmBuilder(self.root).build()
        self.assertEqual(first['duration'], second['duration'])
        self.assertEqual(before, (self.root/'work/narration.wav').read_bytes())

    def test_rejects_injected_pauses_trimming_and_speed_changes(self):
        for key, value in [('page_pause_seconds', .28), ('sentence_pause_seconds', .18),
                           ('trim_silence', True), ('pace', 1.1)]:
            with self.subTest(key=key):
                self.manifest['audio'] = {key: value}
                with self.assertRaises(ValueError):
                    load_master(self.root, self.manifest, self.root/'converted.wav')

    def test_rejects_overlaps_wrong_text_and_stale_audio(self):
        for update in [{'start': 2.9}, {'text': '漏字。'}, {'end': 9}]:
            original = dict(self.alignment['beats'][1])
            self.alignment['beats'][1].update(update)
            self.write_inputs()
            with self.assertRaises(ValueError):
                load_master(self.root, self.manifest, self.root/'converted.wav')
            self.alignment['beats'][1] = original
        self.alignment['source_sha256'] = 'old'
        self.write_inputs()
        with self.assertRaises(ValueError):
            load_master(self.root, self.manifest, self.root/'converted.wav')

    def test_waveform_tampering_invalidates_verification(self):
        timeline = FilmBuilder(self.root).build()
        audio = self.samples.copy(); audio[4 * 48000] += 1
        save_wave(self.root/'work/narration.wav', np.concatenate([np.zeros(48000, dtype=np.int16), audio, np.zeros(48000, dtype=np.int16)]))
        with self.assertRaises(ValueError):
            verify_compiled_master(self.root, timeline)

    def test_frame_retiming_rejects_reversed_order_and_changed_cover(self):
        from frame_retime import validate_anchors, timestamp_expression
        self.assertIn('/TB', timestamp_expression([(0, 0), (1, 1), (8, 7), (9, 8)]))
        for anchors in [[(0, 0), (1, 1), (8, .8)], [(0, 0), (1, 1.2), (9, 8)],
                        [(0, 0), (.5, .6), (1, 1), (9, 8)]]:
            with self.assertRaises(ValueError):
                validate_anchors(anchors)

    def test_tts_receives_complete_script_once(self):
        target, text = generation_target(self.root, self.manifest)
        self.assertEqual(target, self.root/'master.wav')
        self.assertEqual(text, '前一句。后一句。')
        self.manifest['ending'] = {'closing_text': '尚未加入的结语。'}
        with self.assertRaises(ValueError):
            generation_target(self.root, self.manifest)
        self.manifest.pop('ending')
        self.manifest['narration']['source'] = '../outside.wav'
        with self.assertRaises(ValueError):
            generation_target(self.root, self.manifest)


if __name__ == '__main__':
    unittest.main()
