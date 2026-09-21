"""Source-bound presentation adjustments; preserve analysis and native chart values."""
from copy import deepcopy
import math,re

def units(text):
    return sum(1 if ord(c)>255 else .55 for c in text)

def cover_lines(text,width,size,height):
    # A single explicit layout owns wrapping. Preserve every non-space character.
    clean=re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])','',str(text))
    clean=re.sub(r'\s+',' ',clean).strip()
    budget=width/size*.88
    rows=[]
    # Prefer the title/subtitle boundary to splitting a Chinese phrase.
    split=next((i for i,c in enumerate(clean) if c in '（(' and i>0),None)
    if split is None:split=next((i+1 for i,c in enumerate(clean) if c in '｜|' and i>0),None)
    if split and max(units(clean[:split]),units(clean[split:]))<=budget:
        rows=[clean[:split],clean[split:]]
    elif units(clean)<=budget:rows=[clean]
    else:
        tokens=re.findall(r'\d{4}-\d{2}(?:-\d{2})?|[A-Za-z]+|[\s\S]',clean)
        row=''
        for token in tokens:
            if units(token)>budget:raise ValueError('Cover token exceeds layout capacity')
            if row and units(row+token)>budget:rows.append(row);row=''
            row+=token
        if row:rows.append(row)
    if len(rows)*size*1.22>height:raise ValueError('Cover title requires a larger source layout')
    assert ''.join(rows)==clean
    return '\n'.join(rows)

def negative_caption(view):
    items=[]
    for series in view['series']:
        for label,value in zip(view['labels'],series['values']):
            if value<0:
                number=f'{value:,.2f}'.rstrip('0').rstrip('.')
                prefix=(series['label']+'：') if len(view['series'])>1 else ''
                items.append(prefix+str(label)+' '+number+series.get('unit',''))
    return '负向项：'+'；'.join(items) if items else ''

def prepare_scene(projection,scene):
    result=deepcopy(scene)
    indices=scene.get('page_indices',list(range(len(scene['scene']))))
    for local,objects in enumerate(result['scene']):
        page=projection['slides'][indices[local]]
        cover=page.get('kind')=='cover' or (scene.get('purpose')=='theme-preview' and local==0)
        if cover:
            for obj in objects:
                if obj['kind']=='text' and obj['size']>=40:
                    obj['t']=cover_lines(obj['t'],obj['w'],obj['size'],obj['h'])
                    obj['explicit_wrap']=True
        additions=[]
        for obj in objects:
            if obj['kind']!='chart':continue
            view=projection['chart_views'][obj['id']]
            if view['kind'] not in {'bar','paired'}:continue
            caption=negative_caption(view)
            if not caption:continue
            # Put the bound names and exact signed values outside the chart renderer.
            # The original categories, native bars and editable workbook remain intact.
            budget=math.floor(obj['w']/20*.85)
            tokens=re.findall(r'[-+]?\d[\d,]*(?:\.\d+)?|[A-Za-z]+|[\s\S]',caption)
            rows=[];row=''
            for token in tokens:
                if units(token)>budget:raise ValueError('Negative annotation token exceeds layout capacity')
                if row and units(row+token)>budget:rows.append(row);row=''
                row+=token
            if row:rows.append(row)
            if len(rows)>2:raise ValueError('Negative annotations need a wider source chart layout')
            reserve=28*len(rows)+12
            if obj['h']-reserve<220:raise ValueError('Negative annotations leave insufficient chart space')
            additions.append({'kind':'text','t':'\n'.join(rows),'x':obj['x'],'y':obj['y'],
                'w':obj['w'],'h':28*len(rows),'size':20,'fill':'#'+projection['selection']['config']['palette']['ink'],
                'bold':False,'explicit_wrap':True,'bound_chart':obj['id'],'bound_role':'negative-values'})
            obj['y']+=reserve;obj['h']-=reserve
        objects.extend(additions)
    return result
