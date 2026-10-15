"""Check subtitle visibility, text fidelity and completion after the last voice."""
from pathlib import Path
import tempfile
import copy
from unittest.mock import patch
from subtitle_contract import validate_subtitles, validate_subtitle_delivery
import unittest
import wave
import numpy as np
from PIL import Image
from caption_assets import build_caption, resolve_cues
from video_job import read_narration
from video_renderer import Renderer
from smoke_test import write_test_tone


class CaptionAndEndingTests(unittest.TestCase):
    def test_caption_has_transparent_background_and_appears_as_complete_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata = build_caption(root, 'subtitle', '学会放过自己。', {}, 1920, 1080)
            artwork = Image.open(root / 'subtitle.png').convert('RGBA')
            pixels = np.array(artwork)
            self.assertTrue((pixels[:, :, 3] == 0).any())
            self.assertFalse((pixels[:5, :, 3] > 0).any())
            self.assertEqual(metadata['type'], 'typeset_caption')
            self.assertEqual(metadata['segments'], [])
            self.assertEqual(metadata['stroke_color'], '#000000')
            self.assertEqual(metadata['stroke_width'], 2)
            self.assertTrue(((pixels[:, :, :3] == 0).all(axis=2) & (pixels[:, :, 3] == 255)).any())
            renderer = Renderer.__new__(Renderer)
            renderer.artwork = {'subtitle': artwork}
            event = {'asset': 'subtitle', 'caption': True, 'start': 2., 'end': 4.}
            self.assertTrue(np.array_equal(np.array(renderer.layer(event, 2.)), pixels))

    def test_single_caption_contract_rejects_duplicate_layers_and_tracks(self):
        timeline = {'captions': {'presentation': 'burned', 'owner': 'caption_events'},
                    'assets': {'c': {'type': 'typeset_caption', 'text': '一句话。'}},
                    'cues': [{'start': 1., 'end': 2., 'text': '一句话。'}],
                    'pages': [{'start': 1., 'end': 3., 'events': [
                        {'asset': 'c', 'caption': True, 'role': 'caption', 'start': 1., 'hide': 2.}]}]}
        self.assertEqual(validate_subtitles(timeline)['cue_count'], 1)
        duplicate = copy.deepcopy(timeline)
        duplicate['pages'][0]['events'].append(copy.deepcopy(duplicate['pages'][0]['events'][0]))
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            validate_subtitles(duplicate)
        repeated_text = copy.deepcopy(timeline)
        repeated_text['assets']['label'] = {'type': 'text', 'text': '一句话。'}
        repeated_text['pages'][0]['events'].append({'asset': 'label', 'caption': False, 'role': 'title', 'y': 100})
        self.assertEqual(validate_subtitles(repeated_text)['cue_count'], 1)
        repeated_text['pages'][0]['events'][-1]['y'] = 1000
        with self.assertRaisesRegex(ValueError, 'bottom artwork'):
            validate_subtitles(repeated_text)
        wrong_role = copy.deepcopy(timeline)
        wrong_role['pages'][0]['events'][0]['caption'] = False
        with self.assertRaisesRegex(ValueError, 'roles'):
            validate_subtitles(wrong_role)
        overlap = copy.deepcopy(timeline)
        overlap['cues'].append({'start': 1.5, 'end': 2.5, 'text': '另一句。'})
        overlap['assets']['d'] = {'type': 'typeset_caption', 'text': '另一句。'}
        overlap['pages'][0]['events'].append({'asset': 'd', 'caption': True, 'role': 'caption', 'start': 1.5, 'hide': 2.5})
        with self.assertRaisesRegex(ValueError, 'same time'):
            validate_subtitles(overlap)
        with tempfile.TemporaryDirectory() as directory:
            video = Path(directory) / 'film.mp4'
            (video.parent / 'film.zh.srt').write_text('duplicate')
            with self.assertRaisesRegex(ValueError, 'sidecars'):
                validate_subtitle_delivery(video)
            (video.parent / 'film.zh.srt').unlink()
            with patch('subtitle_contract.subprocess.run') as probe:
                probe.return_value.stdout = '{"streams":[{"index":2}]}'
                with self.assertRaisesRegex(ValueError, 'another subtitle track'):
                    validate_subtitle_delivery(video)

    def test_caption_cues_reject_text_loss_and_overlapping_times(self):
        beat = {'text': '前句。后句。', 'start': 10., 'duration': 4.,
                'caption_cues': [{'text': '前句。', 'start': 0., 'end': 2.},
                                 {'text': '后句。', 'start': 2., 'end': 4.}]}
        cues = resolve_cues(beat)
        self.assertEqual((cues[0]['start'], cues[-1]['end']), (10., 14.))
        beat['caption_cues'][1]['start'] = 1.9
        with self.assertRaises(ValueError):
            resolve_cues(beat)
        beat['caption_cues'][1].update(start=2., text='句。')
        with self.assertRaises(ValueError):
            resolve_cues(beat)

    def test_unchanged_pace_preserves_source_sample_count(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_test_tone(root / 'voice.wav', 1.73, 220)
            with wave.open(str(root / 'voice.wav')) as stream:
                expected = stream.getnframes()
            samples, _ = read_narration(root / 'voice.wav', root / 'converted.wav', 1., False)
            self.assertEqual(len(samples), expected)

    def test_ending_keeps_completed_frame_then_fades_to_paper(self):
        renderer = Renderer.__new__(Renderer)
        renderer.timeline = {'cover_seconds': 1., 'pages': [{'end': 10.}], 'ending': {'fade_seconds': .6}}
        renderer.starts = [1.]
        renderer.paper = (255, 255, 255, 255)
        renderer.page_frame = lambda index, time: Image.new('RGBA', (20, 20), (0, 0, 0, 255))
        self.assertEqual(np.array(renderer.frame(9.3)).max(), 0)
        self.assertTrue(100 < np.array(renderer.frame(9.7)).mean() < 150)
        self.assertGreater(np.array(renderer.frame(9.99)).mean(), 250)


if __name__ == '__main__':
    unittest.main()
