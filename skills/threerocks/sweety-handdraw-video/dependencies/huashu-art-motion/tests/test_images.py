import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import capabilities as c
import images as im


class ImageTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.cfg,_=c.effective(str(self.root/'config.json'))
        self.tool={'id':'current.image','kind':'host','operations':['generate','edit'],'reference_images':True,'transparent_background':True,'cost':'subscription','network':'cloud'}
        self.runtime={'host':'codex','session_id':'session-a','observed_at':time.time(),'tools':[self.tool]}
        self.req={'prompt':'test','operation':'generate','references':[],'transparent_background':True,'min_width':4,'min_height':4}
        self.grants=['image_generation','cloud']
        self.source=self.root/'source.png';Image.new('RGBA',(8,8),(30,40,50,120)).save(self.source)
        self.output=self.root/'project/asset.png';self.plan=self.root/'plan.json';self.receipt=self.root/'receipt.json'

    def prepare(self):
        result=im.make_plan(self.cfg,self.req,self.runtime,'session-a',self.plan,mode='generate',grants=self.grants)
        self.assertEqual(result['status'],'host_action_required')
        data={'status':'success','plan_id':result['plan_id'],'session_id':'session-a','tool_id':self.tool['id'],'output_sha256':im.sha(self.source)}
        self.receipt.write_text(json.dumps(data))

    def accept(self,**kw):
        return im.accept(kw.get('config',self.cfg),self.plan,self.receipt,self.source,self.output,
                         kw.get('runtime',self.runtime),kw.get('session','session-a'),self.grants)

    def test_old_profile_does_not_enable_new_capability(self):
        self.cfg['policy'].update(cloud='allow',paid_api='allow')
        self.assertEqual(im.choose(self.cfg,self.runtime)['status'],'needs_configuration')

    def test_deny_cannot_be_bypassed_by_flags(self):
        self.cfg['policy']['image_generation']='deny'
        self.assertEqual(im.choose(self.cfg,self.runtime,self.req,'generate',grants=self.grants)['status'],'blocked')

    def test_empty_runtime_does_not_invent_host_tool(self):
        self.runtime['tools']=[]
        self.assertEqual(im.choose(self.cfg,self.runtime,self.req,'generate',grants=self.grants)['status'],'unavailable')

    def test_multiple_tools_require_selection(self):
        self.runtime['tools'].append(dict(self.tool,id='another.image'))
        self.assertEqual(im.choose(self.cfg,self.runtime,self.req,'generate',grants=self.grants)['status'],'needs_selection')

    def test_features_filter_before_choice(self):
        self.tool['transparent_background']=False
        self.assertEqual(im.choose(self.cfg,self.runtime,self.req,'generate',grants=self.grants)['status'],'unavailable')

    def test_cloud_reference_upload_separate_permission(self):
        self.req['references']=[{'path':str(self.source),'sha256':im.sha(self.source)}]
        r=im.choose(self.cfg,self.runtime,self.req,'generate',grants=self.grants)
        self.assertEqual(r['status'],'needs_permission');self.assertIn('reference_upload',r['candidates'][0]['needs'])

    def test_unknown_price_never_means_free(self):
        self.tool['cost']='unknown'
        r=im.choose(self.cfg,self.runtime,self.req,'generate',grants=self.grants)
        self.assertEqual(r['status'],'needs_permission');self.assertIn('unknown_image_cost',r['candidates'][0]['needs'])

    def test_paid_api_needs_paid_permission(self):
        self.tool['cost']='paid_api'
        self.assertEqual(im.choose(self.cfg,self.runtime,self.req,'generate',grants=self.grants)['status'],'needs_permission')

    def test_stale_or_other_host_snapshot_rejected(self):
        file=self.root/'runtime.json'
        for changes in ({'observed_at':time.time()-901},{'session_id':'other'}):
            file.write_text(json.dumps(dict(self.runtime,**changes)))
            with self.assertRaises(c.ConfigError):im.runtime_tools(file,'session-a')

    def test_success_imports_bytes_and_reports_provenance_limit(self):
        self.prepare();self.accept()
        self.assertEqual(self.source.read_bytes(),self.output.read_bytes())
        meta=json.loads(Path(str(self.output)+'.json').read_text())
        self.assertEqual(meta['provenance'],'agent_reported_tool_call');self.assertTrue(meta['has_transparency'])

    def test_modified_output_receipt_does_not_match(self):
        self.prepare();Image.new('RGB',(8,8),'red').save(self.source)
        with self.assertRaises(c.ConfigError):self.accept()
        self.assertFalse(self.output.exists())

    def test_opaque_output_fails_transparency(self):
        Image.new('RGB',(8,8),'red').save(self.source);self.prepare()
        with self.assertRaises(c.ConfigError):self.accept()

    def test_all_transparent_output_is_not_a_valid_generated_asset(self):
        Image.new('RGBA',(8,8),(0,0,0,0)).save(self.source);self.prepare()
        with self.assertRaises(c.ConfigError):self.accept()

    def test_revoked_permission_or_changed_preference_invalidates_plan(self):
        self.prepare()
        cfg=copy.deepcopy(self.cfg);cfg['preferences']['image']['mode']='off'
        with self.assertRaises(c.ConfigError):self.accept(config=cfg)
        cfg=copy.deepcopy(self.cfg);cfg['policy']['image_generation']='deny'
        with self.assertRaises(c.ConfigError):self.accept(config=cfg)

    def test_changed_host_cannot_reuse_plan(self):
        self.prepare();runtime=copy.deepcopy(self.runtime);runtime['host']='kimi'
        with self.assertRaises(c.ConfigError):self.accept(runtime=runtime)

    def test_missing_tool_cannot_reuse_plan(self):
        self.prepare();runtime=copy.deepcopy(self.runtime);runtime['tools']=[]
        with self.assertRaises(c.ConfigError):self.accept(runtime=runtime)

    def test_different_session_cannot_reuse_plan(self):
        self.prepare()
        with self.assertRaises(c.ConfigError):self.accept(session='different')

    def test_existing_image_never_calls_host(self):
        meta=im.inspect_image(self.source);meta.update(generated=False,mode='existing')
        im.import_artifact(self.source,self.output,meta)
        self.assertEqual(self.source.read_bytes(),self.output.read_bytes())

    def test_no_overwrite_and_matching_extension(self):
        self.prepare();self.accept()
        with self.assertRaises(c.ConfigError):self.accept()
        with self.assertRaises(c.ConfigError):im.import_artifact(self.source,self.root/'wrong.jpg',im.inspect_image(self.source))

    def test_request_reference_relative_to_request_file(self):
        file=self.root/'request.json';file.write_text(json.dumps({'prompt':'test','operation':'edit','references':['source.png']}))
        result=im.request_data(file);self.assertEqual(result['references'][0]['path'],str(self.source.resolve()))

    def test_project_cannot_grant_images(self):
        with self.assertRaises(c.ConfigError):c.project_patch({'policy':{'image_generation':'allow'}})
        c.project_patch({'policy':{'image_generation':'deny'}})

    def test_cli_error_is_structured_not_traceback(self):
        r=subprocess.run([sys.executable,str(c.ROOT/'scripts/capabilities.py'),'use-image','--config',str(self.root/'config.json'),'--file',str(self.root/'missing.png'),'--out',str(self.output)],capture_output=True,text=True)
        self.assertEqual(r.returncode,2);self.assertEqual(json.loads(r.stderr)['status'],'error')


    def test_single_payload_inspection_rejects_file_swapped_during_decode(self):
        self.prepare()
        original=im.inspect_image
        def race(path):
            info=original(path)
            Image.new('RGB',(1,1),'white').save(path)
            return info
        with patch.object(im,'inspect_image',side_effect=race):
            with self.assertRaises(c.ConfigError):self.accept()
        self.assertFalse(self.output.exists())

    def test_malformed_plan_request_is_structured_error(self):
        self.prepare();data=json.loads(self.plan.read_text());data['request']=None;self.plan.write_text(json.dumps(data))
        with self.assertRaises(c.ConfigError):self.accept()

if __name__=='__main__':unittest.main()
