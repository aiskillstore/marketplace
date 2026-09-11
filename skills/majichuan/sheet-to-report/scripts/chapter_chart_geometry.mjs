// Full-deck chart capabilities. Geometry consumes validated chart-spec projections only.
export const EXTENDED_KINDS=['paired','stacked','donut','scatter','waterfall','histogram'];
export const CHART_CAPACITY={line:18,bar:18,column:18,grouped:18,paired:8,stacked:12,donut:6,scatter:8,waterfall:12,histogram:20};
export function scatterIdentifiers(v){
 return v.labels.map((_,i)=>{
  const same=v.labels.map((_,j)=>j).filter(j=>v.x_values[j]===v.x_values[i]&&v.series[0].values[j]===v.series[0].values[i]);
  return same[0]===i?same.map(j=>String(j+1)).join('/'):'';
 });
}
export function drawScatterKey(v,box,{text,wrap,fmt}){
 const x=box.x+box.w*.72,w=box.w*.28,step=Math.min(60,box.h/v.labels.length);
 if(step<48)throw Error('Scatter object key exceeds vertical capacity; split or aggregate explicitly');
 v.labels.forEach((label,i)=>{
  const t=wrap(`${i+1} ${label}\n${fmt(v.x_values[i])}, ${fmt(v.series[0].values[i])}`,Math.floor(w/19));
  if(t.split('\n').length>2)throw Error('Scatter object key exceeds text capacity; split or aggregate explicitly');
  text(t,x,box.y+i*step,w,48,18,'muted');
 });
 return {...box,w:box.w*.68};
}
export function axisRange(values){
 const min=Math.min(0,...values),max=Math.max(0,...values),span=max-min||1;
 const rough=span*1.12/4,power=10**Math.floor(Math.log10(rough)),step=[1,2,2.5,5,10].find(n=>n*power>=rough)*power;
 return {min:Math.floor(min/step)*step,max:Math.max(step,Math.ceil(max*1.08/step)*step),step};
}
export function chartGeometry(v,box){
 if(!(v.kind in CHART_CAPACITY))throw Error('Full chapter-deck export gate is not verified for '+v.kind);
 const values=v.series.flatMap(s=>s.values);
 if(values.some(x=>x===null||!Number.isFinite(x)))throw Error('Full-deck missing values require explicit supported segmentation; no zero filling');
 if(v.labels.length>CHART_CAPACITY[v.kind])throw Error('Full-deck chart label capacity exceeded for '+v.kind+'; use explicit source aggregation, never drop labels');
 if(v.kind==='scatter'&&v.x_values.some(x=>!Number.isFinite(x)))throw Error('Scatter needs finite numeric x coordinates');
 if(v.kind==='paired'&&v.axes.x.scale!=='category')throw Error('Full-deck paired time charts need a separately verified line-panel layout');
 const extent=v.kind==='waterfall'?[...v.bases,...v.ends]:v.kind==='stacked'?v.series.flatMap(s=>[...s.bases,...s.ends]):values;
 return {...box,horizontal:['bar','paired'].includes(v.kind),range:axisRange(extent)};
}
export function drawExtendedChart(v,box,api){
 const {push,text,rect,line,color,seriesColor,wrap,fmt,chartNumber}=api;
 chartGeometry(v,box);
 if(['scatter','histogram'].includes(v.kind)){
  text('横轴：'+v.axes.x.label+(v.axes.x.unit?'（'+v.axes.x.unit+'）':'')+'；纵轴：'+v.series[0].label+'（'+v.series[0].unit+'）',box.x,box.y-10,box.w,32,20,'muted');
  box={...box,y:box.y+26,h:box.h-26};
 }
 if(v.kind==='scatter')box=drawScatterKey(v,box,api);
 const meta={kind:'chart-meta',version:'chart-geometry/1',id:v.id,chart_kind:v.kind,box:{...box},panels:[]};push(meta);
 const tag=(obj,role,series,index,extra={})=>push({...obj,chart_mark:{id:v.id,role,series,index,...extra}});
 const put=(s,x,y,w,h,size=20)=>{
  const t=wrap(s,Math.max(2,Math.floor(w/size)));
  if(t.split('\n').length*size*1.22>h+1)throw Error('Extended chart text capacity exceeded; widen or split the source chart');
  text(t,x,y,w,h,size,'muted');
 };
 if(v.kind==='donut'){
  const {x,y,w,h}=box,cx=x+w*.30,cy=y+h*.49,r=Math.min(w*.24,h*.47),inner=r*.58;let angle=-Math.PI/2;
  meta.ring={cx,cy,r,inner};
  v.series[0].values.forEach((value,i)=>{
   const end=angle+value/100*Math.PI*2;
   // Split a full circle into simple sectors; zero has a visible legend row but no area.
   const pieces=Math.max(1,Math.ceil((end-angle)/Math.PI));
   if(value>0)for(let part=0;part<pieces;part++){
    const a=angle+(end-angle)*part/pieces,b=angle+(end-angle)*(part+1)/pieces;
    const steps=Math.max(2,Math.ceil((b-a)/(Math.PI/60))),angles=Array.from({length:steps+1},(_,k)=>a+(b-a)*k/steps);
    const points=[...angles.map(t=>[cx+r*Math.cos(t),cy+r*Math.sin(t)]),...angles.toReversed().map(t=>[cx+inner*Math.cos(t),cy+inner*Math.sin(t)])];
    tag({kind:'polygon',points,fill:seriesColor(i)},'sector',0,i,{part,pieces});
   }
   rect(x+w*.61,y+22+i*51,14,14,seriesColor(i));
   put(v.labels[i]+'  '+fmt(value)+'%',x+w*.61+25,y+14+i*51,w*.39-30,45,22);
   angle=end;
  });return meta;
 }
 function panel(seriesIndices,pbox,orientation='vertical'){
  const vals=seriesIndices.flatMap(j=>v.series[j].values),stack=v.kind==='stacked',wf=v.kind==='waterfall';
  const range=axisRange(wf?[...v.bases,...v.ends]:stack?v.series.flatMap(s=>[...s.bases,...s.ends]):vals);
  const horizontal=orientation==='horizontal',left=horizontal?Math.min(190,pbox.w*.33):Math.max(70,Math.max(chartNumber(range.min).length,chartNumber(range.max).length)*12+24);
  const right=horizontal?Math.max(86,...vals.map(n=>chartNumber(n).length*11+26)):30;
  const plot={x:pbox.x+left,y:pbox.y+15,w:pbox.w-left-right,h:pbox.h-98};
  if(plot.w<180||plot.h<100)throw Error('Extended chart plot too small');
  const p={series_indices:seriesIndices,orientation,plot,range};meta.panels.push(p);
  const sy=n=>plot.y+plot.h-(n-range.min)/(range.max-range.min)*plot.h,sx=n=>plot.x+(n-range.min)/(range.max-range.min)*plot.w;
  for(let k=0;k<=Math.round((range.max-range.min)/range.step);k++){
   const value=range.min+k*range.step;
   if(horizontal){line(sx(value),plot.y,sx(value),plot.y+plot.h);text(chartNumber(value),sx(value)-35,plot.y+plot.h+15,90,30,18,'muted');}
   else{line(plot.x,sy(value),plot.x+plot.w,sy(value));text(chartNumber(value),pbox.x,sy(value)-13,left-10,30,18,'muted');}
  }
  return {p,plot,range,sy,sx,horizontal};
 }
 if(v.kind==='paired'){
  v.series.forEach((s,j)=>{
   const b={x:box.x+j*(box.w/2+12),y:box.y+24,w:box.w/2-24,h:box.h-24};
   put(s.label+'（'+s.unit+'）',b.x,box.y-10,b.w,35,22);
   const {plot,sx}=panel([j],b,'horizontal'),gap=plot.h/v.labels.length;
   if(gap<26)throw Error('Paired chart rows too dense');
   v.labels.forEach((label,i)=>{
    put(label,b.x,plot.y+gap*i,plot.x-b.x-10,gap,20);
    const a=sx(0),z=sx(s.values[i]),yy=plot.y+gap*i+gap*.16;
    tag({kind:'rect',x:Math.min(a,z),y:yy,w:Math.abs(z-a),h:gap*.68,fill:seriesColor(j)},'bar',j,i);
    const valueText=chartNumber(s.values[i]),valueWidth=Math.max(78,valueText.length*11+20);
    text(valueText,s.values[i]<0?z-valueWidth-2:z+6,yy,valueWidth,28,18,'muted');
   });
  });return meta;
 }
 const {p,plot,sy}=panel(v.series.map((_,j)=>j),box),gap=plot.w/v.labels.length;
 if(v.kind==='scatter'){
  const lo=Math.min(...v.x_values),hi=Math.max(...v.x_values),padding=lo===hi?Math.max(1,Math.abs(lo)*.05):0;
  p.x_range={min:lo-padding,max:hi+padding};
  const xx=n=>plot.x+(n-p.x_range.min)/(p.x_range.max-p.x_range.min)*plot.w;
  for(let k=0;k<=4;k++){const n=p.x_range.min+(p.x_range.max-p.x_range.min)*k/4;text(chartNumber(n),xx(n)-36,plot.y+plot.h+15,88,28,18,'muted');}
  const ids=scatterIdentifiers(v),used=[];
  v.series.forEach((s,j)=>s.values.forEach((value,i)=>{
   const cx=xx(v.x_values[i]),cy=sy(value);
   tag({kind:'circle',cx,cy,r:5,fill:seriesColor(j)},'point',j,i);
   if(ids[i]){
    const w=Math.max(24,ids[i].length*12),x=Math.min(cx+9,plot.x+plot.w-w),y=cy-27;
    if(used.some(b=>x<b.x+b.w&&x+w>b.x&&y<b.y+25&&y+25>b.y))throw Error('Scatter identifiers overlap; split or aggregate explicitly, never jitter source coordinates');
    used.push({x,y,w});text(ids[i],x,y,w,25,18,'ink');
   }
  }));
  put(v.axes.x.label+'（'+v.axes.x.unit+'）',box.x,box.y+box.h-26,box.w,28,18);
  return meta;
 }
 v.labels.forEach((label,i)=>{
  const histogram=v.kind==='histogram';
  const shown=histogram?`[${fmt(v.bin_lower[i])}, ${fmt(v.bin_upper[i])}${i===v.labels.length-1?']':')'}`:label;
  put(shown,plot.x+i*gap,plot.y+plot.h+12,gap-4,65,histogram?18:20);
  if(v.kind==='waterfall'){
   const a=v.bases[i],b=v.ends[i],bw=gap*.58,x=plot.x+(i+.5)*gap-bw/2;
   tag({kind:'rect',x,y:Math.min(sy(a),sy(b)),w:bw,h:Math.abs(sy(a)-sy(b)),fill:v.roles[i]==='delta'?(v.series[0].values[i]<0?seriesColor(1):seriesColor(2)):seriesColor(0)},'waterfall',0,i);
   if(i<v.labels.length-1)tag({kind:'line',x1:x+bw,y1:sy(b),x2:x+gap,y2:sy(b),fill:color('muted'),width:1},'connector',0,i);
   text(chartNumber(v.series[0].values[i]),x-10,Math.min(sy(a),sy(b))-28,bw+30,28,20,'muted');
  }else v.series.forEach((s,j)=>{
   const base=v.kind==='stacked'?s.bases[i]:0,end=v.kind==='stacked'?s.ends[i]:s.values[i],bw=histogram?gap:gap*.68,x=plot.x+i*gap+(histogram?0:gap*.16);
   tag({kind:'rect',x,y:Math.min(sy(base),sy(end)),w:bw,h:Math.abs(sy(base)-sy(end)),fill:seriesColor(j)},v.kind==='stacked'?'stack':'bin',j,i);
   if(histogram)text(chartNumber(s.values[i]),x+5,sy(end)-28,bw-10,28,20,'muted');
  });
 });
 if(v.kind==='stacked')v.series.forEach((s,j)=>{rect(box.x+j*box.w/v.series.length,box.y+box.h+8,13,13,seriesColor(j));put(s.label,box.x+j*box.w/v.series.length+20,box.y+box.h,box.w/v.series.length-28,35,21);});
 return meta;
}
