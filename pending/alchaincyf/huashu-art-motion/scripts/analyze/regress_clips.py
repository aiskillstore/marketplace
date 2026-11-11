#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""动画语法回归：对 engine/examples/*.json 逐个跑 spec 校验＋版面审计（原版／竖屏／英文），出一张通过表。改了任何语法、库或引擎之后先跑这个。

uv run scripts/analyze/regress_clips.py [--only y1_kurzgesagt,t3_finance_chart] [--variants base,portrait,en] [--out <目录>]
红灯＝版面审计红灯或 spec 校验红灯，退出码 1；黄灯只列出。需要素材才能渲的示例（y4 要角色帧库）自动跳过并说明。
"""
import argparse, copy, json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; ENG = ROOT / 'engine'
EN = ["Gradient descent walks downhill", "One sentence turns into three thousand lines", "Revenue grew 7.8x in five years", "Two charts, both drawn by code", "Only one thing at a time"]
TK = ("text", "sub", "label", "title", "caption", "key")


def absolutize(o, base: Path):
    if isinstance(o, dict): return {k: absolutize(v, base) for k, v in o.items()}
    if isinstance(o, list): return [absolutize(v, base) for v in o]
    if isinstance(o, str) and not o.startswith(('/', 'data:', 'http')) and '.' in o.split('/')[-1] and (base / o).exists(): return str((base / o).resolve())
    return o


def en(o, key=None, n=[0]):
    if isinstance(o, dict): return {k: en(v, k) for k, v in o.items()}
    if isinstance(o, list): return [en(v, key) for v in o]
    if isinstance(o, str) and key in TK:
        n[0] += 1; return EN[n[0] % len(EN)] if len(o) > 4 else 'OK ' + str(n[0])
    return o


def run_audit(spec: dict, tmp: Path):
    f = tmp / 'v.json'; f.write_text(json.dumps(spec, ensure_ascii=False))
    r = subprocess.run(['uv', 'run', '--with', 'playwright', 'python', str(ENG / 'render.py'), '--spec', str(f), '--audit'], capture_output=True, text=True)
    txt = r.stdout + r.stderr; m = re.search(r'红灯 (\d+)\s+黄灯 (\d+)', txt)
    return (int(m.group(1)), int(m.group(2)), [l.strip() for l in txt.splitlines() if '🔴' in l or '🟡' in l]) if m else (-1, 0, [txt.strip().splitlines()[-1] if txt.strip() else '没有输出'])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--only'); ap.add_argument('--variants', default='base,portrait,en'); ap.add_argument('--out')
    a = ap.parse_args(); only = set(a.only.split(',')) if a.only else None; vs = a.variants.split(',')
    rows, bad = [], 0
    with tempfile.TemporaryDirectory() as td:
        for ex in sorted((ENG / 'examples').glob('*.json')):
            name = ex.stem
            if only and name not in only: continue
            spec = absolutize(json.loads(ex.read_text()), ex.parent)
            lint = subprocess.run([sys.executable, str(ROOT / 'clip_lint.py'), str(ex)], capture_output=True, text=True)
            lr = '🔴' if lint.returncode else ('🟡' if '🟡' in lint.stdout else '✅')
            cells = {}
            for v in vs:
                d = copy.deepcopy(spec)
                if v == 'portrait': d['width'], d['height'] = 1080, 1920
                elif v == 'en': d = en(d)
                red, yel, lines = run_audit(d, Path(td))
                if red < 0 and 'y4' in name: cells[v] = ('跳过', ['需要角色帧库']); continue
                cells[v] = (f'{"🔴" if red else "✅"}{red}/{yel}' if red >= 0 else '💥', lines)
                if red != 0: bad += 1
            if lr == '🔴': bad += 1
            rows.append((name, lr, cells))
    print(f'{"示例":28} 校验  ' + '  '.join(f'{v:>9}' for v in vs))
    for name, lr, cells in rows:
        print(f'{name:28} {lr}    ' + '  '.join(f'{cells[v][0]:>9}' for v in vs))
    for name, lr, cells in rows:
        for v, (st, lines) in cells.items():
            for l in lines:
                if '🔴' in l or st == '💥': print(f'  [{name} · {v}] {l}')
    print('\n格式：红灯数/黄灯数。' + ('通过。' if not bad else f'有 {bad} 项红灯，见上。'))
    if a.out: Path(a.out).write_text(json.dumps([(n, l, {k: v[0] for k, v in c.items()}) for n, l, c in rows], ensure_ascii=False, indent=1))
    sys.exit(1 if bad else 0)


main()
