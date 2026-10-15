"""Exercise optional deadlines, literal text limits, pen-only motion and watermarks."""
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from PIL import Image
from production_options import ChoiceSession, validate_choice, apply_choices
from hand_assets import prepare_hand
from watermark_assets import prepare_watermark, watermark_position
from timeline_contract import validate_timeline
from caption_assets import build_caption
from video_job import find_font


class ProductionOptionsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.catalog = {'styles':[{'id':'1'}]}
        self.hands = [{'id':'navy'},{'id':'pen-only'}]
        self.voices = [{'id':'iapetus','available':True},{'id':'external','available':False}]
        self.defaults = {'content':'解释愤怒如何伤害自己','style':{'mode':'inferred'},'hand':{'preset':'navy'},
            'voice':{'voice':'iapetus'},'advertising':{'text':''},'watermark':{'text':''},'captions':{'mode':'quiet'}}

    def tearDown(self): self.temporary.cleanup()

    def session(self,explicit=None):
        return ChoiceSession(self.root,self.defaults,explicit or {},self.catalog,self.hands,self.voices,60,now=0)

    def test_each_timeout_continues_even_without_browser_requests(self):
        session=self.session()
        self.assertEqual(session.advance(59)['stage'],'style')
        self.assertEqual(session.advance(60)['stage'],'hand')
        self.assertEqual(session.advance(120)['stage'],'voice')
        self.assertTrue(session.advance(360)['complete'])
        persisted=json.loads((self.root/'options/selection.json').read_text())
        self.assertTrue(persisted['complete'])
        self.assertEqual(persisted['choices']['advertising']['value']['text'],'')
        self.assertEqual(persisted['choices']['watermark']['value']['text'],'')

    def test_explicit_preferences_skip_wait_and_survive_other_timeouts(self):
        session=self.session({'hand':{'preset':'pen-only'},'watermark':{'text':'版权所有：作者'}})
        self.assertEqual(session.advance(60)['stage'],'voice')
        session.choose('voice',{'voice':'iapetus'},now=61)
        self.assertEqual(session.advance(120)['stage'],'advertising')
        self.assertEqual(session.advance(121)['stage'],'captions')
        self.assertTrue(session.advance(181)['complete'])
        self.assertEqual(session.choices['hand']['value']['preset'],'pen-only')
        self.assertEqual(session.choices['watermark']['value']['text'],'版权所有：作者')

    def test_missing_content_is_rejected_and_sixteen_characters_are_preserved(self):
        self.defaults['content']=' '
        with self.assertRaisesRegex(ValueError,'MISSING_CONTENT'): self.session()
        for label in ['甲'*16, '😀'*16]:
            self.assertIsNone(validate_choice('advertising',{'text':label},self.catalog,self.hands,self.voices))
        with self.assertRaises(ValueError):
            validate_choice('advertising',{'text':'甲'*17},self.catalog,self.hands,self.voices)
        with self.assertRaises(ValueError):
            validate_choice('voice',{'voice':'external'},self.catalog,self.hands,self.voices)

    def test_applied_choices_control_real_manifest_layers(self):
        session=self.session({'hand':{'preset':'pen-only'},'advertising':{'text':'完整品牌名称'},'watermark':{'text':'版权署名'},'captions':{'mode':'plate'}})
        session.advance(120)
        (self.root/'job.json').write_text(json.dumps({'version':1,'hand':{'source':'old-hand.png'},'pages':[]}))
        job=apply_choices(self.root)
        self.assertEqual(job['hand'],{'preset':'pen-only','pen_text':'完整品牌名称'})
        self.assertEqual(job['watermark']['text'],'版权署名')
        self.assertEqual(job['captions']['color'],'#FFFFFF')
        self.assertNotIn('source',job['hand'])

    def test_pen_only_does_not_require_a_forearm_and_label_limit_is_enforced(self):
        font_path,font_index=find_font({})
        hand=prepare_hand({'preset':'pen-only','pen_text':'手绘口播Skill'},self.root,self.root,1080,font_path,font_index)
        self.assertEqual(hand['kind'],'pen')
        self.assertTrue(validate_timeline({'cover_seconds':1,'canvas':{'height':1080},'hand':hand,'pages':[]}))
        with self.assertRaisesRegex(ValueError,'16'):
            prepare_hand({'preset':'pen-only','pen_text':'甲'*17},self.root,self.root,1080,font_path,font_index)

    def test_optional_watermark_drift_is_visible_quiet_and_stays_in_frame(self):
        self.assertIsNone(prepare_watermark({},self.root,1920,1080))
        text='『手绘口播.Skill』今晚 18:00 全网首发。\n版权所有：@leo_xiaolei'
        mark=prepare_watermark({'text':text},self.root,1920,1080)
        self.assertEqual(mark['text'],text)
        alpha=np.array(Image.open(mark['source']))[:,:,3]
        self.assertGreater(alpha.max(),0);self.assertLessEqual(alpha.max(),62)
        positions=[watermark_position(mark,1920,1080,time) for time in range(0,3600,11)]
        self.assertGreater(len(set(positions)),20)
        for x,y in positions:
            self.assertGreaterEqual(x,0);self.assertGreaterEqual(y,0)
            self.assertLessEqual(x+mark['width'],1920);self.assertLessEqual(y+mark['height'],1080)

    def test_caption_plate_is_an_explicit_supported_choice(self):
        metadata=build_caption(self.root,'caption','完整字幕',{'background':{'color':'#243039','opacity':.76},'color':'#FFFFFF'},1920,1080)
        alpha=np.array(Image.open(self.root/'caption.png'))[:,:,3]
        self.assertTrue((alpha==194).any())
        self.assertEqual(metadata['background']['color'],'#243039')
        self.assertFalse(alpha[:5].any())


if __name__=='__main__': unittest.main()
