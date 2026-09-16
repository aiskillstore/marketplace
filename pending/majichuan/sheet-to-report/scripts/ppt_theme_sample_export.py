"""Export an explicitly marked, source-bound theme sample with public libraries."""
import argparse
import hashlib
import json
from pathlib import Path
from ppt_theme_selection import validate_selection
from chapter_pptx_export import render_deck,canonical
from chapter_native_scene_qa import inspect_native_scene


def export_sample(source_path,selection,manifest,out):
    cfg=validate_selection(selection,preview=True)
    if selection['target']!='standard':raise ValueError('Standard sample only')
    source=json.loads(source_path.read_text(encoding='utf-8'))
    if (manifest.get('schema')!='ppt-theme-sample-export/1' or manifest.get('source')!=source
        or manifest.get('source_file_sha256')!=hashlib.sha256(source_path.read_bytes()).hexdigest()
        or manifest.get('selection')!=selection or source.get('schema')!='ppt-theme-sample/1'
        or source.get('source_model_sha256')!=selection['source_model_sha256']):
        raise ValueError('Theme sample source mismatch')
    if len(manifest['scene'])!=2:raise ValueError('Theme sample needs exactly two pages')
    chart=source['chart'];view={'id':'theme-chart','kind':'grouped','labels':chart['labels'],
        'series':[{'label':s['name'],'values':s['values']} for s in chart['series']],
        'axes':{'x':{'scale':'category'}},'_sample_axis':(chart['min'],chart['max'],chart['step']),
        '_sample_format':chart.get('format','0.0')}
    d={'selection':selection,'source_model_sha256':selection['source_model_sha256'],
       'slides':[{'id':'theme-cover','evidence_ids':[]},{'id':'theme-chart','evidence_ids':[]}],
       'scope_records':{},'chart_views':{'theme-chart':view}}
    d['sha256']=canonical(d)
    pages=[]
    for objects in manifest['scene']:
        pages.append([{**o,**({'id':'theme-chart'} if o['kind']=='chart' else {'fill':'#'+cfg['palette'][o['role']]})}
                      for o in objects])
    scene={'source':d['sha256'],'width':1280,'height':720,'purpose':'theme-preview','scene':pages}
    render_deck(d,scene,[1,2],out)
    errors,checks=inspect_native_scene(out,scene)
    if errors:raise ValueError('; '.join(errors))
    return {'purpose':'theme-preview','full_deck':False,'checks':checks,'source_model_sha256':source['source_model_sha256']}


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    for field in ['source','selection','manifest','output']:ap.add_argument('--'+field,type=Path,required=True)
    a=ap.parse_args();read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    print(json.dumps(export_sample(a.source,read(a.selection),read(a.manifest),a.output),ensure_ascii=False))
