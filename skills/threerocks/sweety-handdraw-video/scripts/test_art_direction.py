"""Reject missing, empty or stale art-direction preparation for every generated input."""
from pathlib import Path
import json
import tempfile
import unittest
from art_direction import bind_evidence, check_record, digest, image_inputs


class ArtDirectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.image = self.root/'image.png'; self.image.write_bytes(b'accepted-image')
        self.brief = self.root/'brief.txt'; self.brief.write_text('主体与道具接触，侧光，留出底部字幕区域。')
        self.prompt = self.root/'prompt.txt'; self.prompt.write_text('人物双手握住道具，轮廓连续，背景留白。')
        self.record = self.root/'review.json'
        self.data = {'dependency_sha256':'guide-version','images':[{'source':'image.png','sha256':digest(self.image),
                     'method':'generated_under_guidance','status':'pass','evidence':'实际查看主体、接触、构图与边缘。',
                     'brief_file':'brief.txt','prompt_file':'prompt.txt'}]}
        self.record.write_text(json.dumps(self.data))
        bind_evidence(self.record)

    def tearDown(self):
        self.temporary.cleanup()

    def check(self):
        return check_record(self.record,[(self.image,None)],'guide-version')

    def test_every_used_generated_image_is_enumerated(self):
        job={'cover':{'source':'cover.png'},'hand':{'source':'custom-hand.png'},'pages':[
              {'beats':[{'actions':[{'type':'illustration','source':'character.png'}]}],
               'visual_groups':[{'actions':[{'type':'illustration','source':'prop.png'}]}]}]}
        self.assertEqual({p.name for p,_ in image_inputs(job,self.root)},
                         {'cover.png','custom-hand.png','character.png','prop.png'})

    def test_missing_review_and_changed_image_are_rejected(self):
        self.assertEqual(self.check(),1)
        with self.assertRaisesRegex(ValueError,'no completed'):
            check_record(self.record,[(self.root/'unreviewed-cover.png',None)],'guide-version')
        self.image.write_bytes(b'replaced-image')
        with self.assertRaisesRegex(ValueError,'Image changed'):
            self.check()

    def test_empty_preparation_is_rejected_even_when_files_exist(self):
        for path in (self.brief,self.prompt):
            content=path.read_text();path.write_text(' \n ')
            with self.assertRaisesRegex(ValueError,'empty'):
                self.check()
            with self.assertRaisesRegex(ValueError,'empty'):
                bind_evidence(self.record)
            path.write_text(content)

    def test_changed_preparation_requires_new_binding(self):
        for path in (self.brief,self.prompt):
            content=path.read_text();path.write_text(content+'新修改')
            with self.assertRaisesRegex(ValueError,'changed or was not bound'):
                self.check()
            path.write_text(content)

    def test_missing_binding_or_guidance_version_is_rejected(self):
        self.record.write_text(json.dumps(self.data))
        with self.assertRaisesRegex(ValueError,'not bound'):
            self.check()
        bind_evidence(self.record)
        with self.assertRaisesRegex(ValueError,'dependency'):
            check_record(self.record,[(self.image,None)],'another-guide')

    def test_binding_cannot_turn_pending_review_into_pass(self):
        data=json.loads(self.record.read_text());data['images'][0].update(status='pending',evidence='')
        self.record.write_text(json.dumps(data));bind_evidence(self.record)
        self.assertEqual(json.loads(self.record.read_text())['images'][0]['status'],'pending')
        with self.assertRaisesRegex(ValueError,'no completed'):
            self.check()

    def test_whitespace_visual_review_is_rejected(self):
        data=json.loads(self.record.read_text());data['images'][0]['evidence']=' \n '
        self.record.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,'no completed'):
            self.check()
