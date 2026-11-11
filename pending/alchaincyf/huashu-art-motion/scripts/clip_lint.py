#!/usr/bin/env python3
"""参数化片段 spec 校验：渲染前跑一遍，把「写错了不报错只是不生效」的坑提前说出来。

uv run scripts/clip_lint.py spec.json [--strict]
红灯（退出码 1）：grammar 不存在、cue 类型不是这个语法的、必填字段缺、at 不是数、色板/finish 写错、图片文件不存在、cue 全在时长之外。
黄灯：表外的字段（多半拼错或放错层级）、camera 写在不生效的位置、开头/结尾空太久、片段 >8 秒、cue 挤在同一帧。
--strict：黄灯也算失败。字段表在 engine/clip_schema.json，改语法时同步改。
"""
import argparse, json, sys
from pathlib import Path

ENG = Path(__file__).resolve().parent / 'engine'


def get(o, path):
    for k in path.split('.'):
        if not isinstance(o, dict) or k not in o: return None
        o = o[k]
    return o


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('spec'); ap.add_argument('--strict', action='store_true')
    a = ap.parse_args()
    sp = Path(a.spec).resolve(); red, yel = [], []
    try: spec = json.loads(sp.read_text())
    except Exception as e: sys.exit(f'🔴 JSON 读不了：{e}')
    S = json.loads((ENG / 'clip_schema.json').read_text()); C = S['common']
    g = spec.get('grammar'); G = S['grammars'].get(g)
    if not G or not (ENG / 'clips' / f'{g}.js').exists():
        red.append(f'grammar「{g}」不存在。可用：{" / ".join(S["grammars"])}'); report(red, yel, a); return
    for k in spec:
        if k.startswith('_'): continue                      # _note 之类的注释键
        if k not in C['spec']:
            hint = '（camera 要写在 data 里：{"data": {"camera": "snap"}}）' if k == 'camera' else ''
            yel.append(f'spec 顶层的「{k}」不认，会被忽略{hint}')
    d = spec.get('duration')
    if not isinstance(d, (int, float)) or d <= 0: red.append('duration 要是 >0 的数（秒）'); d = 0
    elif d > 8: yel.append(f'duration={d}s 超过 8s：单个片段撑太久会读成一页 PPT，拆成几镜')
    th = spec.get('theme')
    if isinstance(th, str) and th not in C['themes'] and g != 't3_finance_chart': red.append(f'theme「{th}」不是色板名：{" / ".join(C["themes"])}')
    fn = spec.get('finish')
    if fn is not None and not (isinstance(fn, dict) or fn in C['finish']): red.append(f'finish「{fn}」不是预设：{" / ".join(C["finish"])}（或写对象）')
    sd = spec.get('data') or {}
    if isinstance(sd, dict):
        for k in sd:
            if k not in G['specData']: yel.append(f'spec.data 里的「{k}」不在 {g} 的字段表里（拼错或放错层级？认：{", ".join(G["specData"])}）')
        for need in G.get('specNeeds', []):
            if get(spec, need) in (None, [], {}, ''): red.append(f'{g} 必须有 {need}')
        if sd.get('camera') not in (None, 'smooth', 'snap'): red.append(f'data.camera 只认 smooth / snap，写的是「{sd.get("camera")}」')
    cues = spec.get('cues') or []
    if not cues: red.append('cues 是空的')
    prev = -1; seen_at = {}
    inside = 0
    for i, q in enumerate(cues):
        tag = f'cue[{i}]'
        if not isinstance(q, dict): red.append(f'{tag} 不是对象'); continue
        at, kind = q.get('at'), q.get('kind')
        tag = f'cue[{i}] {kind}@{at}'
        if not isinstance(at, (int, float)): red.append(f'{tag}：at 要是数字'); continue
        if kind not in G['kinds']: red.append(f'{tag}：{g} 没有这个 kind。可用：{" / ".join(G["kinds"])}'); continue
        if at < prev - 1e-9: yel.append(f'{tag}：at 比上一条小（cue 会被按时间重排，确认是故意的）')
        prev = max(prev, at)
        if d and at > d + 1e-9: yel.append(f'{tag}：超出片段时长 {d}s，看不到，会被丢掉')
        else: inside += 1
        key = round(at, 3); seen_at[key] = seen_at.get(key, 0) + 1
        for k in q:
            if k not in C['cue']: yel.append(f'{tag}：cue 里的「{k}」不认（认：{", ".join(C["cue"])}）')
        qd = q.get('data') or {}
        if isinstance(qd, dict):
            for k in qd:
                if k == 'camera': yel.append(f'{tag}：camera 写在 cue 的 data 里不生效，要写在 spec 顶层 data 里')
                elif k not in G['cueData']: yel.append(f'{tag}：data 里的「{k}」不在 {g}/{kind} 的字段表里（拼错？认：{", ".join(G["cueData"])}）')
        for need in (G.get('needs', {}).get(kind) or []):
            ok = any(get(q, n) not in (None, '', [], {}) for n in need.split('|'))
            if not ok: red.append(f'{tag}：缺 {need}')
        for im in ([q.get('image')] if q.get('image') else []) + (q['frames'] if isinstance(q.get('frames'), list) else []):
            if isinstance(im, str) and not im.startswith(('data:', 'http')) and not (sp.parent / im).exists() and not Path(im).exists():
                red.append(f'{tag}：图片不存在 {im}（相对 spec 文件）')
    if cues and d and inside == 0: red.append('所有 cue 都在片段时长之外')
    if cues and d:
        ats = [q['at'] for q in cues if isinstance(q, dict) and isinstance(q.get('at'), (int, float)) and q['at'] <= d]
        if ats:
            if min(ats) > 1.2: yel.append(f'第一条 cue 在 {min(ats)}s：开头空了 {min(ats)}s（口播管线里可能是故意留的）')
            if d - max(ats) > 3.0: yel.append(f'最后一条 cue 在 {max(ats)}s，之后还有 {d - max(ats):.1f}s 没有新事件，画面会定住')
    for k, n in seen_at.items():
        if n >= 3: yel.append(f'{n} 条 cue 挤在 {k}s 同一刻：只有最后一条看得清')
    report(red, yel, a)


def report(red, yel, a):
    for r in red: print('🔴', r)
    for y in yel: print('🟡', y)
    if not red and not yel: print('✅ spec 没有发现问题')
    sys.exit(1 if red or (a.strict and yel) else 0)


main()
