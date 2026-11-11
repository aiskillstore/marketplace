"""Exercise the server definitions and construction used by both CLI scripts."""
import ast
from concurrent.futures import ThreadPoolExecutor
import functools
import http.server
from pathlib import Path
import socket
import socketserver
import tempfile
import threading
import time
import unittest
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


class LocalServerTests(unittest.TestCase):
    def test_idle_connection_does_not_block_parallel_assets_or_shutdown(self):
        for relative in ('scripts/engine/render.py', 'scripts/qa.py'):
            with self.subTest(script=relative), tempfile.TemporaryDirectory() as directory:
                payload = b'window.assetLoaded = true;'
                Path(directory, 'asset.js').write_bytes(payload)
                namespace = dict(http=http, socketserver=socketserver, functools=functools,
                                 urllib=urllib, root=Path(directory), spec=None, ALLOWED=set())
                defaults = (socketserver.ThreadingTCPServer.request_queue_size,
                            socketserver.ThreadingTCPServer.daemon_threads)
                tree = ast.parse((ROOT / relative).read_text(encoding='utf-8'))
                # Run the actual handler, server class and construction, without the CLI/browser.
                nodes = [node for node in tree.body if
                         isinstance(node, ast.ClassDef) and node.name in ('Q', 'LocalServer') or
                         isinstance(node, ast.Assign) and any(
                             isinstance(target, ast.Name) and target.id == 'srv'
                             for target in node.targets)]
                exec(compile(ast.Module(body=nodes, type_ignores=[]), str(ROOT / relative), 'exec'), namespace)
                server = namespace['srv']
                idle = None
                worker = None
                try:
                    self.assertEqual(server.server_address[0], '127.0.0.1')
                    self.assertEqual(server.request_queue_size, 128)
                    self.assertTrue(server.daemon_threads)
                    self.assertEqual((socketserver.ThreadingTCPServer.request_queue_size,
                                      socketserver.ThreadingTCPServer.daemon_threads), defaults)
                    accepted = threading.Event()
                    original_accept = server.get_request
                    def get_request():
                        connection = original_accept()
                        accepted.set()
                        return connection
                    server.get_request = get_request
                    worker = threading.Thread(target=server.serve_forever, daemon=True)
                    worker.start()
                    idle = socket.create_connection(server.server_address, timeout=3)
                    self.assertTrue(accepted.wait(3), 'idle connection was not accepted')
                    url = 'http://127.0.0.1:%s/asset.js' % server.server_address[1]
                    def fetch(_):
                        # Ignore user proxy configuration for this loopback regression test.
                        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
                        with opener.open(url, timeout=5) as response:
                            return response.status, response.read()
                    with ThreadPoolExecutor(max_workers=16) as pool:
                        results = list(pool.map(fetch, range(32)))
                    self.assertEqual(results, [(200, payload)] * 32)
                    started = time.monotonic()
                    server.shutdown()
                    server.server_close()
                    worker.join(2)
                    self.assertFalse(worker.is_alive())
                    self.assertLess(time.monotonic() - started, 2)
                finally:
                    if idle is not None:
                        idle.close()
                    if worker is not None and worker.is_alive():
                        server.shutdown()
                        worker.join(2)
                    server.server_close()


if __name__ == '__main__':
    unittest.main()
