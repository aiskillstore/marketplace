import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import check_release as gate


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.repo=Path(self.tmp.name)
        self.git('init','-q');self.git('config','user.name','Fixture');self.git('config','user.email','fixture@users.noreply.github.com')
        (self.repo/'README.md').write_text('base\n');self.git('add','README.md');self.git('commit','-qm','base')
        self.base=self.git('rev-parse','HEAD').decode().strip()

    def git(self,*args):return gate.git(self.repo,*args)
    def manifest(self):
        (self.repo/gate.MANIFEST).write_text(json.dumps(gate.build_manifest(self.repo)))
        self.git('add',gate.MANIFEST)

    def test_incremental_commit_with_manifest_passes(self):
        (self.repo/'new.py').write_text('print(1)');self.git('add','new.py');self.manifest();self.git('commit','-qm','incremental')
        self.assertEqual(gate.check(self.repo,'HEAD',self.base,'fixture@users.noreply.github.com')['outgoing_commits_checked'],1)

    def test_stale_manifest_rejected(self):
        self.manifest();(self.repo/'README.md').write_text('changed');self.git('add','README.md')
        with self.assertRaises(ValueError):gate.check(self.repo,'INDEX')

    def test_secret_in_intermediate_commit_rejected(self):
        secret=self.repo/'secret.txt';secret.write_text('ghp_'+'a'*40);self.git('add','secret.txt');self.git('commit','-qm','leak')
        secret.rename(Path(self.tmp.name).parent/(Path(self.tmp.name).name+'-fixture-archive'))
        self.addCleanup(lambda: (Path(self.tmp.name).parent/(Path(self.tmp.name).name+'-fixture-archive')).unlink(missing_ok=True))
        self.git('add','-u');self.manifest();self.git('commit','-qm','remove')
        with self.assertRaisesRegex(ValueError,'凭据'):gate.check(self.repo,'HEAD',self.base)

    def test_private_filename_rejected(self):
        (self.repo/'voices.json').write_text('{}');self.git('add','voices.json')
        with self.assertRaises(ValueError):gate.build_manifest(self.repo)

    def test_symlink_rejected(self):
        try:(self.repo/'link').symlink_to('README.md')
        except OSError:self.skipTest('host cannot create symlinks')
        self.git('add','link')
        with self.assertRaises(ValueError):gate.build_manifest(self.repo)

    def test_real_identity_checked_only_when_requested(self):
        self.manifest();self.git('commit','-qm','release')
        with self.assertRaises(ValueError):gate.check(self.repo,'HEAD',self.base,'other@users.noreply.github.com')

    def test_unstaged_content_not_silently_approved(self):
        (self.repo/'README.md').write_text('unstaged')
        with self.assertRaises(ValueError):gate.build_manifest(self.repo)


    def test_secret_in_commit_message_is_rejected(self):
        self.manifest();self.git('commit','-qm','message '+'ghp_'+'z'*40)
        with self.assertRaisesRegex(ValueError,'提交元数据'):gate.check(self.repo,'HEAD',self.base)

    def test_replace_object_cannot_hide_secret(self):
        secret=self.repo/'hidden.txt';secret.write_text('ghp_'+'b'*40);self.git('add','hidden.txt');self.git('commit','-qm','leak')
        blob=self.git('rev-parse','HEAD:hidden.txt').decode().strip()
        clean=subprocess.check_output(['git','-C',str(self.repo),'hash-object','-w','--stdin'],input=b'clean').decode().strip()
        self.git('replace',blob,clean)
        with self.assertRaisesRegex(ValueError,'凭据'):gate.inspect(self.repo,'HEAD')


    def test_secret_in_deleted_filename_is_rejected(self):
        name='ghp_'+'c'*40
        file=self.repo/name;file.write_text('safe');self.git('add',name);self.git('commit','-qm','bad filename')
        archive=Path(self.tmp.name).parent/(Path(self.tmp.name).name+'-filename-archive');file.rename(archive)
        self.addCleanup(lambda: archive.unlink(missing_ok=True))
        self.git('add','-u');self.manifest();self.git('commit','-qm','remove filename')
        with self.assertRaisesRegex(ValueError,'路径名') as error:gate.check(self.repo,'HEAD',self.base)
        self.assertNotIn(name,str(error.exception))

if __name__=='__main__':unittest.main()
