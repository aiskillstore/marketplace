#!/usr/bin/env python3
"""逐帧渲染 index.html：起本地服务 → 无头 Chromium → 每帧 window.seek(t) → 截 #stage → ffmpeg。

uv run --with playwright python render.py --stills 2,10,20 --out 渲染/静帧
uv run --with playwright python render.py --out 渲染/成片_无声.mp4 [--from 0 --to 30] [--fps 24]
页面有 pageerror / console.error → 非零退出。
"""
import argparse, functools, http.server, socketserver, subprocess, sys, threading, time
from pathlib import Path
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('--out', required=True)
ap.add_argument('--stills')
ap.add_argument('--from', dest='t0', type=float, default=0)
ap.add_argument('--to', dest='t1', type=float)
ap.add_argument('--fps', type=int, default=24)
ap.add_argument('--crf', type=int, default=15)
a = ap.parse_args()
if a.fps <= 0 or a.t0 < 0 or (a.t1 is not None and a.t1 <= a.t0):
    ap.error("fps > 0, from >= 0, to > from required")
root = Path(__file__).resolve().parent

class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *x): pass
class Srv(socketserver.ThreadingTCPServer):
    daemon_threads = True; request_queue_size = 128
srv = Srv(('127.0.0.1', 0), functools.partial(Q, directory=str(root)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
port = srv.server_address[1]

errors = []
with sync_playwright() as p:
    b = p.chromium.launch(args=["--disable-partial-raster"])
    pg = b.new_page(viewport={'width': 1920, 'height': 1080}, device_scale_factor=1)
    pg.on('console', lambda m: (print('[page]', m.text), errors.append(m.text)) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: (print('[pageerror]', e), errors.append(str(e))))
    pg.goto(f'http://127.0.0.1:{port}/index.html?render=1')
    pg.wait_for_function('window.__ready === true', timeout=120000)
    bad = pg.evaluate('window.__filmFailed || window.__bootFailed || null')
    if bad: raise SystemExit('加载失败：\n' + bad)
    total = 8
    stage = pg.locator('#stage')
    def shot(t, path=None, fmt='png'):
        pg.evaluate('t => window.seek(t)', t)
        return pg.screenshot(path=path, clip={'x': 0, 'y': 0, 'width': 1920, 'height': 1080}, type=fmt, **({'quality': 95} if fmt == 'jpeg' else {}))
    if a.stills:
        out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
        for s in a.stills.split(','):
            shot(float(s), str(out / f't{float(s):06.2f}.png'))
        print('stills ->', out)
    else:
        t1 = a.t1 if a.t1 is not None else total
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', str(a.fps), '-c:v', 'png', '-i', '-',
                               '-c:v', 'libx264', '-preset', 'slow', '-crf', str(a.crf), '-pix_fmt', 'yuv420p', '-movflags', '+faststart', a.out], stdin=subprocess.PIPE)
        n0, n1 = round(a.t0 * a.fps), round(t1 * a.fps); st = time.time()
        for i in range(n0, n1):
            ff.stdin.write(shot(i / a.fps))
            if (i - n0) % 48 == 0: print(f'{i}/{n1}  {time.time() - st:.0f}s', flush=True)
        ff.stdin.close()
        if ff.wait() != 0: raise SystemExit("ffmpeg failed")
        print('done ->', a.out, f'total={total}')
    b.close()
srv.shutdown()
if errors: raise SystemExit(f'页面报错 {len(errors)} 条')
