"""Exercise asset download integrity and offline behavior without public service access."""
from pathlib import Path
import hashlib
import io
import json
import tempfile
import unittest
from unittest.mock import patch
import hosted_assets


class HostedAssetTests(unittest.TestCase):
    def test_valid_download_then_offline_cache_and_corruption_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root/'assets').mkdir()
            content = b'test asset bytes'
            key = 'assets/hands/test.png'
            record = {'url':'https://example.test/test.png','bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()}
            (root/'assets/hosted-manifest.json').write_text(json.dumps({'files':{key:record}}))
            with patch.object(hosted_assets, 'PACKAGE', root), patch.dict('os.environ', {'HANDDRAW_ASSET_CACHE':str(root/'cache'),'HANDDRAW_OFFLINE':'0'}):
                self.assertTrue(hosted_assets.asset_available(root/key))
                with patch('hosted_assets.urlopen', return_value=io.BytesIO(content)) as request:
                    target = hosted_assets.resolve_asset(root/key)
                    self.assertEqual(target.read_bytes(), content)
                    request.assert_called_once()
                with patch.dict('os.environ', {'HANDDRAW_OFFLINE':'1'}), patch('hosted_assets.urlopen') as request:
                    self.assertEqual(hosted_assets.resolve_asset(root/key), target)
                    request.assert_not_called()
                    target.write_bytes(b'corrupt')
                    with self.assertRaisesRegex(ValueError, 'Offline'):
                        hosted_assets.resolve_asset(root/key)
                with patch('hosted_assets.urlopen', return_value=io.BytesIO(b'wrong')):
                    with self.assertRaisesRegex(ValueError, 'SHA-256'):
                        hosted_assets.resolve_asset(root/key)

    def test_cache_never_accepts_traversal_or_unverified_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'assets').mkdir()
            (root/'assets/hosted-manifest.json').write_text(json.dumps({'files':{'../escape.png':{'url':'https://example.test/a','bytes':1,'sha256':'0'*64}}}))
            with patch.object(hosted_assets,'PACKAGE',root), self.assertRaisesRegex(ValueError,'path'):
                hosted_assets.records()
