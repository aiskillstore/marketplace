import copy
import io
import json
import multiprocessing
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import wave

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import capabilities as c
import koubo


def write_setting(path, setting):
    c.save_patch(Path(path), {'preferences': {'voice': setting}})


class MediaConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.file = self.root / 'media.json'
        self.config, _ = c.effective(str(self.file))

    def clone_config(self):
        return c.merge(self.config, {'preferences': {'voice': {'mode': 'clone'}},
                       'policy': {'cloud': 'allow', 'paid_api': 'allow'},
                       'bindings': {'voices': {'default': {'speaker_id': 'S_test'}}}})

    def test_clean_install_does_not_probe_credentials(self):
        with patch.object(c, 'credentials', side_effect=AssertionError('must not read credentials')):
            result = c.resolve(self.config)
        self.assertEqual(result['status'], 'needs_configuration')
        self.assertFalse(self.file.exists())

    def test_existing_audio_wins_without_cloud(self):
        audio = self.root / 'own.wav'; audio.write_bytes(b'example')
        cfg = self.clone_config()
        with patch.object(c, 'credentials', side_effect=AssertionError()):
            result = c.resolve(cfg, audio=str(audio))
        self.assertEqual(result['mode'], 'provided')

    def test_explicit_revoice_overrides_existing_audio(self):
        with patch.object(c.platform, 'system', return_value='Darwin'), patch.object(c.shutil, 'which', return_value='/bin/tool'):
            self.assertEqual(c.resolve(self.config, mode='system', audio='old.wav')['mode'], 'system')

    def test_deny_beats_temporary_grant_before_credentials(self):
        cfg = self.clone_config(); cfg['policy']['cloud'] = 'deny'
        with patch.object(c, 'credentials', side_effect=AssertionError()):
            self.assertEqual(c.resolve(cfg, grants=['cloud', 'paid_api'])['status'], 'blocked')

    def test_credentials_do_not_grant_permission(self):
        cfg = self.clone_config(); cfg['policy']['paid_api'] = 'ask'
        with patch.object(c, 'credentials', side_effect=AssertionError()):
            self.assertEqual(c.resolve(cfg)['status'], 'needs_permission')

    def test_training_needs_separate_permission(self):
        cfg = self.clone_config()
        self.assertEqual(c.resolve(cfg, operation='train')['status'], 'needs_permission')

    def test_default_is_zero_not_author_rate(self):
        self.assertEqual(self.config['provider_options']['volcengine']['speech_rate'], 0)

    def test_known_credentials_file_only_and_environment_precedence(self):
        env = self.root / '.env';env.write_text('export VOLC_SPEECH_APPID="from-file"\nVOLC_SPEECH_TOKEN=local-test\n')
        self.config['bindings']['volcengine']['env_file'] = str(env)
        with patch.dict(os.environ, {'VOLC_SPEECH_APPID': 'from-process'}, clear=True):
            self.assertEqual(c.credentials(self.config), ('from-process', 'local-test'))

    def test_no_implicit_env_fallback(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(c.credentials(self.config), (None, None))

    def test_bind_existing_voice_without_registry_mutation(self):
        registry = self.root / 'voices.json';registry.write_text('{"default":"old","voices":{"old":{"speaker_id":"S_old"}}}')
        cfg = self.clone_config();cfg['bindings']['volcengine']['registry_file'] = str(registry)
        cfg['bindings']['voices'] = {'my_voice': {'speaker_id': 'S_new'}}
        before = registry.read_bytes()
        self.assertEqual(c.speaker(cfg, 'my_voice'), 'S_new')
        self.assertEqual(c.speaker(cfg, 'old'), 'S_old')
        self.assertEqual(before, registry.read_bytes())

    def test_project_cannot_grant_or_supply_credentials(self):
        for data in [{'policy': {'cloud': 'allow'}}, {'bindings': {'volcengine': {'env_file': '/elsewhere'}}},
                     {'preferences': {'voice': {'voice_ref': 'someone'}}}]:
            with self.assertRaises(c.ConfigError):c.project_patch(data)
        c.project_patch({'policy': {'cloud': 'deny'}, 'preferences': {'voice': {'mode': 'system'}}})

    def test_unknown_schema_and_null_fail_closed(self):
        for data in [{'schema_version':2}, {'preferences':{'voice':None}}, {'policy':{'paid_api':'alow'}}, {'unknown':True}]:
            with self.assertRaises(c.ConfigError):c.validate(data)

    def test_skip_and_reset_preserve_other_preferences(self):
        c.save_patch(self.file, {'preferences': {'voice': {'mode': 'system'}}, 'policy': {'cloud': 'deny'}})
        c.save_patch(self.file, {'onboarding': {'voice':'manual'}, 'preferences':{'voice':{'mode':'unconfigured'}}})
        config,_ = c.effective(str(self.file));self.assertFalse(c.resolve(config)['prompt'])
        c.save_patch(self.file, {}, reset='preferences.voice')
        config,_ = c.effective(str(self.file));self.assertEqual(config['policy']['cloud'], 'deny')

    def test_revision_detects_stale_writer(self):
        c.save_patch(self.file, {'policy':{'cloud':'deny'}}, expected=0)
        with self.assertRaises(c.ConfigError):c.save_patch(self.file, {'policy':{'cloud':'allow'}}, expected=0)
        self.assertEqual(c.read_json(self.file)['policy']['cloud'], 'deny')

    def test_concurrent_writes_preserve_both_fields(self):
        ctx=multiprocessing.get_context('spawn')
        procs=[ctx.Process(target=write_setting,args=(str(self.file),x)) for x in [{'mode':'system'},{'system_voice':'Tingting'}]]
        for p in procs:p.start()
        for p in procs:p.join(15);self.assertEqual(p.exitcode,0)
        cfg=c.read_json(self.file)
        self.assertEqual(cfg['preferences']['voice'],{'mode':'system','system_voice':'Tingting'})
        self.assertEqual(cfg['revision'],2)

    def test_dead_lock_owner_releases_lock(self):
        command=[sys.executable,'-c', 'import sys,os;from pathlib import Path;sys.path.insert(0,sys.argv[1]);import capabilities as c\nwith c.locked(Path(sys.argv[2])): os._exit(0)',str(c.ROOT/'scripts'),str(self.file)]
        subprocess.run(command,check=True,timeout=10)
        c.save_patch(self.file, {'policy': {'cloud':'deny'}})

    def test_base_commands_work_without_site_packages(self):
        result=subprocess.run([sys.executable,'-S',str(c.ROOT/'scripts/capabilities.py'),'status','--config',str(self.file)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'],'needs_configuration')

    def test_network_timeout_is_not_retried(self):
        import requests
        cfg=self.clone_config();koubo.configure_backend(cfg)
        with patch.object(koubo,'load_env',return_value=('test','test')),patch.object(koubo,'_session') as session:
            session.return_value.post.side_effect=requests.exceptions.Timeout()
            with self.assertRaisesRegex(SystemExit,'outcome_unknown'):koubo.api('/test','resource',{})
            self.assertEqual(session.return_value.post.call_count,1)

    def test_proxy_setting_respects_user(self):
        cfg=self.clone_config();cfg['bindings']['volcengine']['trust_env']=True;koubo.configure_backend(cfg)
        self.assertTrue(koubo._session().trust_env)
        cfg['bindings']['volcengine']['trust_env']=False;koubo.configure_backend(cfg)
        self.assertFalse(koubo._session().trust_env)

    def test_partial_error_not_saved(self):
        import base64
        out=self.root/'bad.wav'
        class Response:
            status_code=200
            def iter_lines(self):
                return [json.dumps({'data':base64.b64encode(b'partial').decode(),'code':0}).encode(),b'{"code":45000000}']
        with patch.object(koubo,'api',return_value=Response()):
            with self.assertRaises(SystemExit):koubo.synthesize('text','S_test',out)
        self.assertFalse(out.exists())

    def test_system_platform_never_falls_back_to_cloud(self):
        with patch.object(c.platform,'system',return_value='Linux'),patch.object(c,'credentials',side_effect=AssertionError()):
            self.assertEqual(c.resolve(self.config,mode='system')['status'],'unavailable')

    def test_existing_audio_copy_preserves_bytes(self):
        source=self.root/'source.wav';out=self.root/'copy.wav'
        with wave.open(str(source),'wb') as f:
            f.setnchannels(1);f.setsampwidth(2);f.setframerate(48000);f.writeframes(b'\0\0'*4800)
        subprocess.run([sys.executable,str(c.ROOT/'scripts/capabilities.py'),'use-audio','--config',str(self.file),'--audio',str(source),'--out',str(out)],check=True,capture_output=True)
        self.assertEqual(source.read_bytes(),out.read_bytes())
        self.assertFalse(json.loads(Path(str(out)+'.json').read_text())['generated'])


    def test_stream_eof_without_completion_never_writes(self):
        import base64
        out=self.root/'incomplete.wav'
        class Response:
            status_code=200
            def iter_lines(self):
                return [json.dumps({'data':base64.b64encode(b'partial').decode(),'code':0}).encode()]
        with patch.object(koubo,'api',return_value=Response()):
            with self.assertRaises(SystemExit):koubo.synthesize('text','S_test',out)
        self.assertFalse(out.exists())

    def test_pcm_legacy_output_preserves_samples(self):
        import argparse, base64, math, struct
        samples=b''.join(struct.pack('<h',int(6000*math.sin(i*2*math.pi*440/48000))) for i in range(12000))
        buffer=io.BytesIO()
        with wave.open(buffer,'wb') as f:
            f.setnchannels(1);f.setsampwidth(2);f.setframerate(48000);f.writeframes(samples)
        class Response:
            status_code=200
            def iter_lines(self):
                return [json.dumps({'data':base64.b64encode(buffer.getvalue()).decode(),'code':0}).encode(),b'{"code":20000000}']
        args=argparse.Namespace(mode='clone',voice=None,out=str(self.root/'raw.pcm'),text='test voice',fit=None,match=None,
             match_ss=None,match_t=None,loudness=None,format='pcm',sample_rate=48000,model=None,speech_rate=None,no_fidelity=None,
             allow_cloud=False,allow_paid_api=False)
        with patch.object(c,'resolve',return_value={'status':'configured_unverified','mode':'clone','provider':'volcengine'}),patch.object(koubo,'api',return_value=Response()),patch('sys.stdout',new_callable=io.StringIO):
            c.run_say(args,self.clone_config())
        self.assertEqual(Path(args.out).read_bytes(),samples)
        meta=json.loads(Path(args.out+'.json').read_text())
        self.assertEqual(meta['format'],'s16le');self.assertEqual(meta['channels'],1)
        self.assertAlmostEqual(meta['duration'],.25)

    def test_chinese_uses_installed_voice_only(self):
        result=subprocess.CompletedProcess([],0,'Alex en_US # Hello\nTingting zh_CN # 你好\n','')
        with patch.object(c.subprocess,'run',return_value=result) as run:
            self.assertEqual(c.system_voice_for('中文'),'Tingting')
            self.assertEqual(run.call_args.args[0],['say','-v','?'])
        with patch.object(c.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'Alex en_US # Hello\n','')):
            with self.assertRaises(c.ConfigError):c.system_voice_for('中文')

    def test_near_empty_system_audio_not_delivered(self):
        import argparse
        args=argparse.Namespace(mode='system',voice=None,out=str(self.root/'silent.wav'),text='中文文本',fit=None,match=None,
             match_ss=None,match_t=None,loudness=None,format='wav',sample_rate=48000,model=None,speech_rate=None,no_fidelity=None,
             allow_cloud=False,allow_paid_api=False)
        with patch.object(c,'resolve',return_value={'status':'ready','mode':'system','provider':'macos'}),patch.object(c,'system_voice_for',return_value='Tingting'),patch.object(c.subprocess,'run'),patch.object(c,'inspect_audio',return_value={'duration':.01}),patch.object(koubo,'mean_volume',return_value=-20):
            with self.assertRaises(c.ConfigError):c.run_say(args,self.config)
        self.assertFalse(Path(args.out).exists())


if __name__=='__main__':unittest.main()
