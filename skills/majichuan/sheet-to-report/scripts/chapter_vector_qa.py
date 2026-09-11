"""Check exported vector evidence against source values and recorded author geometry.

This gate currently covers nonnegative bar/grouped/column and time/category lines.
Other shapes require another verified gate; never silently mark them passed.
"""

import re

def axis_number(text):
    match=re.fullmatch(r'([+-]?[\d,]+(?:\.\d+)?)(万|亿)?',text)
    if not match:raise ValueError('Not a supported numeric axis label')
    return float(match[1].replace(',',''))*{'万':10000,'亿':100000000,None:1}[match[2]]

NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}


def near(a, b, tolerance=.02):
    return abs(a-b) <= tolerance


def shapes(root):
    result = []
    for s in root.findall('.//p:sp', NS) + root.findall('.//p:cxnSp', NS):
        off = s.find('p:spPr/a:xfrm/a:off', NS)
        ext = s.find('p:spPr/a:xfrm/a:ext', NS)
        if off is None or ext is None:
            continue
        geo = s.find('p:spPr/a:prstGeom', NS)
        fill = s.find('p:spPr/a:solidFill/a:srgbClr', NS)
        if fill is None and geo is not None and geo.get('prst')=='line':fill=s.find('p:spPr/a:ln/a:solidFill/a:srgbClr',NS)
        result.append({'kind': geo.get('prst') if geo is not None else 'path',
            'fill': '#' + fill.get('val') if fill is not None else None,
            'box': tuple(int(v)/9525 for v in (off.get('x'), off.get('y'), ext.get('cx'), ext.get('cy'))),
            'text': ''.join(t.text or '' for t in s.findall('.//a:t', NS)), 'element': s})
    return result


def inspect_vector(root, view, colors, scene, line_mode=None, scale=1.5):
    errors, checks = [], 0
    actual = shapes(root)
    # Match every visible source text box and primitive to the actual package.
    # Extra theme background rectangles are harmless; missing/shifted evidence is not.
    unused = list(actual)
    for obj in scene:
        # Zero-area bars are invisible by definition; their zero labels still
        # undergo the full text/position check and source values are checked below.
        if obj['kind']=='rect' and (obj['w']==0 or obj['h']==0):
            continue
        if obj['kind'] in ('text', 'rect'):
            box = tuple(obj[k]*scale for k in ('x', 'y', 'w', 'h'))
        elif obj['kind'] == 'line' and line_mode == 'thin-rect':
            box = tuple(v*scale for v in (min(obj['x1'],obj['x2']),min(obj['y1'],obj['y2']),
                max(abs(obj['x2']-obj['x1']),obj['width']),max(abs(obj['y2']-obj['y1']),obj['width'])))
        elif obj['kind']=='line' and line_mode is None:
            box=tuple(v*scale for v in (min(obj['x1'],obj['x2']),min(obj['y1'],obj['y2']),abs(obj['x2']-obj['x1']),abs(obj['y2']-obj['y1'])))
        elif obj['kind'] == 'circle':
            box = ((obj['cx']-obj['r'])*scale, (obj['cy']-obj['r'])*scale, obj['r']*2*scale, obj['r']*2*scale)
        else:
            continue
        def matches(candidate):
            if not all(near(a,b) for a,b in zip(candidate['box'], box)):
                return False
            if obj['kind']=='text':
                return ''.join(candidate['text'].split()) == ''.join(obj['t'].split())
            return candidate['fill'] and candidate['fill'].lower()==obj['fill'].lower()
        found = next((a for a in unused if matches(a)), None)
        if found is None:
            errors.append('exported object missing or shifted: '+obj['kind'])
        else:
            unused.remove(found)
        checks += 1
    if view is None:
        return errors, checks
    if view['kind'] in {'paired','stacked','donut','scatter','waterfall','histogram'}:
        from chapter_chart_qa import inspect_extended
        extra,count=inspect_extended(view,scene,actual,colors,scale)
        return errors+extra,checks+count
    if view['kind'] not in ('line','bar','column','grouped'):
        return errors+['vector value gate unavailable for '+view['kind']], checks
    # Use exported scale lines to resolve the numeric range from axis labels.
    horizontal = view['kind']=='bar'
    grid = [o for o in scene if o['kind']=='line' and
            (near(o['x1'],o['x2']) if horizontal else near(o['y1'],o['y2']))]
    if len(grid)<2:
        return errors+['missing numeric scale'], checks
    scale_text = []
    for o in scene:
        if o['kind']!='text': continue
        try: value=axis_number(o['t'])
        except ValueError: continue
        for g in grid:
            coord=g['x1'] if horizontal else g['y1']
            label_coord=o['x']+35 if horizontal else o['y']+13
            if near(coord,label_coord): scale_text.append((value,coord*scale))
    scale_text=sorted(set(scale_text))
    if len(scale_text)<2 or scale_text[-1][0]==scale_text[0][0]:
        return errors+['numeric axis cannot be resolved'], checks
    low,high=scale_text[0],scale_text[-1]
    coordinate=lambda value:low[1]+(value-low[0])/(high[0]-low[0])*(high[1]-low[1])
    for j, series in enumerate(view['series']):
        color='#'+colors[j%len(colors)]
        if view['kind']=='line':
            items=sorted([o for o in actual if o['kind']=='ellipse' and o['fill']==color],key=lambda a:a['box'][0])
            if len(items)!=len(series['values']):
                errors.append('line point count differs');continue
            xs=view['x_values']
            if not all(isinstance(v,(float,int)) for v in xs): xs=list(range(len(xs)))
            first=items[0]['box'][0]+items[0]['box'][2]/2
            last=items[-1]['box'][0]+items[-1]['box'][2]/2
            for item,value,x in zip(items,series['values'],xs):
                b=item['box']; expected_x=first+(x-xs[0])/(xs[-1]-xs[0] or 1)*(last-first)
                if not near(b[1]+b[3]/2,coordinate(value)) or not near(b[0]+b[2]/2,expected_x):
                    errors.append('line coordinates differ from source data')
                checks+=2
        else:
            if any(v is None for v in series['values']):
                errors.append('missing vector bar value gate unavailable');continue
            items=sorted([o for o in actual if o['kind']=='rect' and o['fill']==color and
                          (o['box'][3]>30 if horizontal else o['box'][2]>30)],
                         key=lambda a:a['box'][1 if horizontal else 0])
            # A zero-height SVG bar may be omitted by a converter, but never a nonzero one.
            values=series['values']
            if len(items)!=len(values):
                values=[v for v in values if v!=0]
            if len(items)!=len(values):
                errors.append('bar count differs');continue
            for item,value in zip(items,values):
                b=item['box'];start=b[0] if horizontal else b[1]+b[3];end=b[0]+b[2] if horizontal else b[1]
                if not (near(min(start,end),min(coordinate(0),coordinate(value))) and near(max(start,end),max(coordinate(0),coordinate(value)))):
                    errors.append('bar geometry differs from source values')
                checks+=2
    return errors, checks
