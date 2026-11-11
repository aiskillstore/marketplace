"""版面审计：对一个参数化片段每 0.25 秒采一帧，汇总文字版面问题。render.py --spec X --audit 调用。
红灯（退出码 1）：文字出界、被安全区吞掉、两段不同文字互相压住。黄灯：字小于可读下限（不含刻意的脚注字号时请人工判断）。
"""
import json


def run(pg, spec, grab, step=0.25):
    W, H, dur = spec.get('width', 1920), spec.get('height', 1080), spec['duration']
    safe = {'top': 0, 'bottom': 0, 'left': 0, 'right': 0, **(spec.get('safe') or {})}
    short = min(W, H); floor = 0.0204 * short                      # 1080 短边 ≈ 22px
    ts = [round(i * step, 3) for i in range(int(dur / step) + 1)] + [round(dur - 1 / spec.get('fps', 30), 3)]
    seen, red, yel = {}, [], []
    for t in ts:
        pg.evaluate('t => { window.__AUDIT.length = 0; window.__auditT = t; }', t)
        pg.evaluate(grab, t)
        items = [i for i in pg.evaluate('window.__AUDIT') if i['a'] > 0.35]
        for it in items:
            w, h = it['x1'] - it['x0'], it['y1'] - it['y0']
            if w < 1 or h < 1: continue
            vis = max(0, min(it['x1'], W) - max(it['x0'], 0)) * max(0, min(it['y1'], H) - max(it['y0'], 0)) / (w * h)
            if 0 < vis < 0.97 and it['px'] >= 8:             # vis==0：整条在画外（转场/镜头平移里），不算
                k = ('出界', it['text'][:20]); seen.setdefault(k, [t, t, f'可见 {vis:.0%}，字号 {it["px"]:.0f}px', 0]); seen[k][1] = t; seen[k][3] += 1
            elif (safe['top'] or safe['bottom'] or safe['left'] or safe['right']) and (it['y0'] < safe['top'] - 2 or it['y1'] > H - safe['bottom'] + 2 or it['x0'] < safe['left'] - 2 or it['x1'] > W - safe['right'] + 2) and it['px'] >= 20:
                k = ('进安全区', it['text'][:20]); seen.setdefault(k, [t, t, f'字号 {it["px"]:.0f}px', 0]); seen[k][1] = t; seen[k][3] += 1
            if it['px'] < floor and len(it['text']) >= 3 and it['px'] >= 6:
                k = ('字太小', it['text'][:20]); seen.setdefault(k, [t, t, f'{it["px"]:.0f}px < 下限 {floor:.0f}px', 0]); seen[k][1] = t; seen[k][3] += 1
        # 互相压住
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i], items[j]
                if a['text'] == b['text'] or a['px'] < 14 or b['px'] < 14 or len(a['text'].strip()) <= 2 or len(b['text'].strip()) <= 2: continue   # 单字符多是公式/图标的部件，刻意叠放
                ox, oy = min(a['x1'], b['x1']) - max(a['x0'], b['x0']), min(a['y1'], b['y1']) - max(a['y0'], b['y0'])
                if ox <= 2 or oy <= 2: continue
                sm = min((a['x1'] - a['x0']) * (a['y1'] - a['y0']), (b['x1'] - b['x0']) * (b['y1'] - b['y0']))
                if sm > 0 and ox * oy / sm > 0.3:
                    k = ('叠字', (a['text'][:10] + ' × ' + b['text'][:10])); seen.setdefault(k, [t, t, f'重叠 {ox * oy / sm:.0%}', 0]); seen[k][1] = t; seen[k][3] += 1
    for (kind, txt), (t0, t1, note, cnt) in seen.items():
        if cnt < 2: continue                   # 只出现一个采样点：多半是转场中的瞬间，不报
        if kind == '出界' and cnt < 3: continue  # 换屏横推约 0.4s：旧画面被推出去是设计动作，出界要持续 3 个采样（≥0.5s）才算
        row = {'kind': kind, 'text': txt, 't0': t0, 't1': t1, 'note': note}
        (yel if kind == '字太小' else red).append(row)
    print(f'版面审计 {W}×{H} {dur}s：红灯 {len(red)}　黄灯 {len(yel)}')
    for r in red: print(f"  🔴 {r['kind']}　「{r['text']}」　{r['t0']}–{r['t1']}s　{r['note']}")
    for r in yel: print(f"  🟡 {r['kind']}　「{r['text']}」　{r['t0']}–{r['t1']}s　{r['note']}")
    if not red and not yel: print('  ✅ 没有发现版面问题')
    return {'red': red, 'yellow': yel, 'size': [W, H], 'duration': dur}
