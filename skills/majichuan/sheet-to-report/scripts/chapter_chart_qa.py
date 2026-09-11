"""Source-based checks for extended chart geometry and native chart semantics."""
import math

NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
EXTENDED={'paired','stacked','donut','scatter','waterfall','histogram'}
def near(a,b,t=.025):return abs(a-b)<=t
def axis_range(values):
 low=min(0,*values);high=max(0,*values);span=high-low or 1
 rough=span*1.12/4;power=10**math.floor(math.log10(rough));step=next(x for x in [1,2,2.5,5,10] if x*power>=rough)*power
 return dict(min=math.floor(low/step)*step,max=max(step,math.ceil(high*1.08/step)*step),step=step)
def polygon_points(shape):
 """Resolve custom geometry points into absolute slide-pixel coordinates."""
 e=shape['element'];paths=e.findall('.//a:custGeom/a:pathLst/a:path',NS)
 if len(paths)!=1:return []
 p=paths[0];w=float(p.get('w','0'));h=float(p.get('h','0'))
 if not w or not h:return []
 if p.findall('a:cubicBezTo',NS) or p.findall('a:arcTo',NS):return []
 x,y,bw,bh=shape['box'];result=[];drawn=False
 for child in p:
  if child.tag.endswith(('moveTo','lnTo')):
   pt=child.find('a:pt',NS)
   if pt is None:return []
   point=(x+float(pt.get('x'))/w*bw,y+float(pt.get('y'))/h*bh)
   if child.tag.endswith('moveTo'):
    # SlideViber may emit an initial pen move before the actual polygon start.
    # It draws no segment. Reject a second contour after drawing has begun.
    if drawn:return []
    result=[point]
   else:result.append(point);drawn=True
 return result
def polygon_equal(actual,expected):
 if len(actual)==len(expected)+1 and all(near(a,b) for a,b in zip(actual[0],actual[-1])):actual=actual[:-1]
 return len(actual)==len(expected) and all(near(a,b) for p,q in zip(actual,expected) for a,b in zip(p,q))
def inspect_extended(view,scene,actual,colors,scale=1.5):
 errors=[];checks=0
 metas=[x for x in scene if x['kind']=='chart-meta']
 if len(metas)!=1 or metas[0].get('id')!=view['id'] or metas[0].get('chart_kind')!=view['kind']:
  return ['missing or foreign extended chart geometry'],checks
 m=metas[0];marks=[x for x in scene if x.get('chart_mark')]
 if any(x['chart_mark']['id']!=view['id'] for x in marks):errors.append('foreign chart mark')
 if view['kind']=='donut':
  ring=m.get('ring',{});cx,cy,r,inner=[ring.get(k,float('nan')) for k in ['cx','cy','r','inner']]
  if not all(math.isfinite(n) for n in [cx,cy,r,inner]) or not 0<inner<r:return ['invalid donut ring'],checks
  angle=-math.pi/2;expected_count=0;unused=list(actual)
  for i,value in enumerate(view['series'][0]['values']):
   end=angle+value/100*math.tau;pieces=max(1,math.ceil((end-angle)/math.pi))
   subset=[o for o in marks if o['chart_mark'].get('index')==i]
   if len(subset)!=(pieces if value>0 else 0):errors.append('donut sector count differs')
   if value>0:
    expected_count+=pieces
    for part in range(pieces):
     a=angle+(end-angle)*part/pieces;b=angle+(end-angle)*(part+1)/pieces;n=max(2,math.ceil((b-a)/(math.pi/60)))
     angles=[a+(b-a)*k/n for k in range(n+1)]
     expected=[(cx+r*math.cos(t),cy+r*math.sin(t)) for t in angles]+[(cx+inner*math.cos(t),cy+inner*math.sin(t)) for t in reversed(angles)]
     o=next((o for o in subset if o['chart_mark'].get('part')==part),None)
     if not o or o['kind']!='polygon' or not polygon_equal(o.get('points',[]),expected):errors.append('donut angle differs from source percentage');continue
     fill=('#'+colors[i%len(colors)]).lower()
     found=next((s for s in unused if (s.get('fill') or '').lower()==fill and polygon_equal(polygon_points(s),[(x*scale,y*scale) for x,y in expected])),None)
     if found is None:errors.append('exported donut sector path differs')
     else:unused.remove(found)
     checks+=len(expected)*2
   # A zero sector still needs a visible value legend; text-to-package matching is done by the caller.
   joined=''.join(o.get('t','') for o in scene if o['kind']=='text')
   if view['labels'][i] not in ''.join(joined.split()):
    if ''.join(view['labels'][i].split()) not in ''.join(joined.split()):errors.append('donut category missing')
   angle=end
  if len(marks)!=expected_count:errors.append('unexpected donut marks')
  return errors,checks
 panels=m.get('panels',[]);expected_panels=2 if view['kind']=='paired' else 1
 if len(panels)!=expected_panels:return ['extended chart panel count differs'],checks
 expected_marks=0
 for pi,p in enumerate(panels):
  indices=[pi] if view['kind']=='paired' else list(range(len(view['series'])))
  if p.get('series_indices')!=indices:errors.append('panel series differ')
  vals=[x for j in indices for x in view['series'][j]['values']]
  if view['kind']=='waterfall':vals=view['bases']+view['ends']
  if view['kind']=='stacked':vals=[x for s in view['series'] for x in s['bases']+s['ends']]
  rng=axis_range(vals)
  if any(not near(p.get('range',{}).get(k,float('inf')),v,1e-8*max(1,abs(v))) for k,v in rng.items()):errors.append('numeric range differs from source extent')
  plot=p['plot'];x,y,w,h=[plot[k] for k in ['x','y','w','h']]
  if w<=0 or h<=0:errors.append('invalid plot area');continue
  horizontal=view['kind']=='paired';gap=(h if horizontal else w)/len(view['labels'])
  sy=lambda v:y+h-(v-rng['min'])/(rng['max']-rng['min'])*h
  sx=lambda v:x+(v-rng['min'])/(rng['max']-rng['min'])*w
  # Check declared scales are actually printed and laid out, not merely trusted metadata.
  for k in range(round((rng['max']-rng['min'])/rng['step'])+1):
   value=rng['min']+k*rng['step'];coord=sx(value) if horizontal else sy(value)
   from chapter_vector_qa import axis_number
   matching=[]
   for o in scene:
    if o['kind']!='text':continue
    try:n=axis_number(o['t'])
    except ValueError:continue
    if near(n,value,1e-5*max(1,abs(value))) and near(o['x']+35 if horizontal else o['y']+13,coord):matching.append(o)
   if not matching:errors.append('extended numeric axis tick missing')
  if view['kind']=='scatter':
   lo=min(view['x_values']);hi=max(view['x_values']);pad=max(1,abs(lo)*.05) if lo==hi else 0
   xr=dict(min=lo-pad,max=hi+pad)
   if p.get('x_range')!=xr:errors.append('scatter horizontal numeric domain differs')
  for j in indices:
   s=view['series'][j]
   for i,value in enumerate(s['values']):
    expected_marks+=1;role={'paired':'bar','stacked':'stack','waterfall':'waterfall','histogram':'bin','scatter':'point'}[view['kind']]
    subset=[o for o in marks if o['chart_mark'].get('role')==role and o['chart_mark'].get('series')==j and o['chart_mark'].get('index')==i]
    if len(subset)!=1:errors.append('chart source mark missing or duplicated');continue
    o=subset[0]
    expected_color=colors[(1 if value<0 else 2) if view['kind']=='waterfall' and view['roles'][i]=='delta' else j%len(colors)]
    if o.get('fill','').lower()!=('#'+expected_color).lower():errors.append('source series color differs')
    if view['kind']=='scatter':
     expected=(x+(view['x_values'][i]-xr['min'])/(xr['max']-xr['min'])*w,sy(value))
     if o['kind']!='circle' or not all(near(a,b) for a,b in zip((o.get('cx',float('inf')),o.get('cy',float('inf'))),expected)):errors.append('scatter coordinates differ from source')
     checks+=2;continue
    base=0;end=value
    if view['kind']=='stacked':base,end=s['bases'][i],s['ends'][i]
    if view['kind']=='waterfall':base,end=view['bases'][i],view['ends'][i]
    if horizontal:expected=(min(sx(base),sx(end)),y+gap*i+gap*.16,abs(sx(end)-sx(base)),gap*.68)
    else:
     bw=gap if view['kind']=='histogram' else gap*(.58 if view['kind']=='waterfall' else .68)
     xx=x+(i+.5)*gap-bw/2
     expected=(xx,min(sy(base),sy(end)),bw,abs(sy(base)-sy(end)))
    if o['kind']!='rect' or not all(near(o.get(k,float('inf')),v) for k,v in zip(['x','y','w','h'],expected)):errors.append('extended bar geometry differs from source')
    if view['kind']=='waterfall' and i<len(s['values'])-1:
     expected_marks+=1;cn=[o for o in marks if o['chart_mark'].get('role')=='connector' and o['chart_mark'].get('index')==i]
     if len(cn)!=1 or not all(near(cn[0].get(k,float('inf')),v) for k,v in zip(['x1','y1','x2','y2'],[expected[0]+expected[2],sy(end),expected[0]+gap,sy(end)])):errors.append('waterfall connector differs')
    checks+=4
 if len(marks)!=expected_marks:errors.append('unexpected extended chart marks')
 return errors,checks

def native_semantics(chart,view,series_index=None):
 errors=[];kind=view['kind']
 expected='doughnutChart' if kind=='donut' else 'scatterChart' if kind=='scatter' or (kind=='line' and view['axes']['x']['scale']!='category') else 'lineChart' if kind=='line' else 'barChart'
 node=chart.find('.//c:'+expected,NS)
 if node is None:return ['native chart type differs: '+kind]
 if expected=='barChart':
  direction=node.find('c:barDir',NS);group=node.find('c:grouping',NS)
  if direction is None or direction.get('val')!=('bar' if kind in {'bar','paired'} else 'col'):errors.append('native bar direction differs')
  if group is None or group.get('val')!=('stacked' if kind=='stacked' else 'clustered'):errors.append('native grouping differs')
  if kind=='histogram':
   gap=node.find('c:gapWidth',NS)
   if gap is None or float(gap.get('val'))!=0:errors.append('histogram bins have gaps')
 if kind=='scatter':
  style=node.find('c:scatterStyle',NS)
  if style is None or style.get('val')!='marker':errors.append('scatter points connected by lines')
 if kind!='donut':
  axes=chart.findall('.//c:valAx',NS)
  vals=[x for j,s in enumerate(view['series']) if series_index is None or j==series_index for x in s['values']]
  if kind=='stacked':vals=[x for s in view['series'] for x in s['bases']+s['ends']]
  rng=axis_range(vals)
  domains=[]
  for a in axes:
   low=a.find('c:scaling/c:min',NS);high=a.find('c:scaling/c:max',NS)
   if low is not None and high is not None:domains.append((float(low.get('val')),float(high.get('val'))))
  if not any(near(a,rng['min'],1e-6*max(1,abs(a))) and near(b,rng['max'],1e-6*max(1,abs(b))) for a,b in domains):errors.append('native numeric axis domain differs')
  if kind=='scatter' and 'x_values' in view:
   lo=min(view['x_values']);hi=max(view['x_values']);pad=max(1,abs(lo)*.05) if lo==hi else 0
   xaxes=[a for a in axes if a.find('c:axPos',NS) is not None and a.find('c:axPos',NS).get('val') in {'b','t'}]
   if not any(near(float(a.find('c:scaling/c:min',NS).get('val')),lo-pad) and near(float(a.find('c:scaling/c:max',NS).get('val')),hi+pad) for a in xaxes if a.find('c:scaling/c:min',NS) is not None and a.find('c:scaling/c:max',NS) is not None):errors.append('scatter native horizontal domain differs')
 return errors
