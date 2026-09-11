"""Presentation-local theme choices; never mutate an analysis model or global prefs."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'ppt-theme/1'

def fingerprint(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

def catalog() -> dict:
    return json.loads((ROOT/'references/ppt-theme-directions.json').read_text(encoding='utf-8'))

def theme_config(theme_id: str) -> dict:
    if theme_id not in catalog():
        raise ValueError(f'unknown theme: {theme_id}')
    palettes = json.loads((ROOT/'references/themes.json').read_text(encoding='utf-8'))
    return {'id':theme_id, 'version':VERSION, 'palette':palettes[theme_id], **catalog()[theme_id]}

def select_theme(request: dict) -> dict:
    """Host supplies intent explicitly; no keyword guesses from private user prose."""
    target = request.get('target','standard')
    if target not in ('standard','slideviber'): raise ValueError('unknown output target')
    for key in ('explicit','project_preference','inherited','recommendation'):
        item = request.get(key)
        if item:
            theme_config(item['id'])
    candidate = None; origin = 'automatic'; confirmed = False
    if request.get('explicit'):
        candidate=request['explicit']['id'];origin='user';confirmed=True
    elif request.get('project_preference',{}).get('confirmed'):
        candidate=request['project_preference']['id'];origin='project';confirmed=True
    elif request.get('inherited',{}).get('confirmed'):
        candidate=request['inherited']['id'];origin='inherited';confirmed=True
    else:
        candidate=((request.get('recommendation') or request.get('inherited')) if not request.get('direct') else None) or {'id':'clean'}
        candidate=candidate['id']
        origin='inherited_automatic' if not request.get('direct') and not request.get('recommendation') and request.get('inherited') else 'automatic'
    reason = str(request.get('reason') or ('沿用已确认的风格' if confirmed else '未提供明确偏好，推荐清晰商务' if candidate=='clean' else '依据当前汇报用途推荐'))
    if request.get('template_required') and not request.get('template_supported',False):
        status='needs_decision'; issue='template_not_supported'
    elif target=='slideviber' and request.get('require_native_chart_data'):
        status='needs_decision'; issue='native_chart_data_conflict'
    elif not confirmed and not request.get('direct'):
        status='awaiting_choice'; issue=None
    else: status='ready'; issue=None
    cfg=theme_config(candidate)
    return {'schema':VERSION, 'status':status, 'issue':issue, 'theme_id':candidate,
            'selection_source':origin, 'confirmed':confirmed, 'reason':reason, 'target':target,
            'config':cfg, 'config_sha256':fingerprint(cfg),
            'source_model_sha256':request.get('source_model_sha256'),
            'editability':'native_charts_where_supported' if target=='standard' else 'vector_shapes',
            'alternatives':([candidate]+[k for k in catalog() if k!=candidate])[:3] if status=='awaiting_choice' else []}

def validate_selection(value: dict, *, preview=False) -> dict:
    if value.get('schema')!=VERSION: raise ValueError('unsupported theme selection schema')
    if value.get('status')!='ready' and not (preview and value.get('status')=='awaiting_choice'):
        raise ValueError('theme choice or capability decision required')
    cfg=theme_config(value['theme_id'])
    if value.get('config')!=cfg or value.get('config_sha256')!=fingerprint(cfg):
        raise ValueError('theme configuration drift or tampering')
    if value.get('target') not in ('standard','slideviber'): raise ValueError('unknown target')
    return cfg

def slideviber_theme(selection: dict, *, preview=False) -> dict:
    cfg=validate_selection(selection,preview=preview);p=cfg['palette']
    if selection['target']!='slideviber': raise ValueError('selection target mismatch')
    return {'style':cfg['slideviber_preset'],'designStyle':cfg['layout'], 'slideNumbers':True,
       'colors':{'primary':'#'+p['ink'],'primary-light':'#'+p['accent_soft'],'secondary':'#'+p['accent'],
        **{f'accent{i+1}':'#'+v for i,v in enumerate((p['chart']+[p['secondary']])[:6])},
        'bg':'#'+p['background'],'surface':'#'+p['surface'],'border':'#'+p['line'],
        'text-primary':'#'+p['ink'],'text-secondary':'#'+p['muted'],'text-muted':'#'+p['muted']},
       'fonts':{'heading':cfg['font']+', system-ui, sans-serif','body':cfg['font']+', system-ui, sans-serif'}}

def main():
    parser=argparse.ArgumentParser(description='Resolve presentation-local theme intent without changing evidence')
    parser.add_argument('--request',type=Path);parser.add_argument('--output',type=Path);parser.add_argument('--list',action='store_true')
    args=parser.parse_args()
    result=catalog() if args.list else select_theme(json.loads(args.request.read_text(encoding='utf-8')))
    data=json.dumps(result,ensure_ascii=False,indent=2)
    if args.output:
        with args.output.open('x',encoding='utf-8') as f:f.write(data)
    else:print(data)

if __name__=='__main__':main()
