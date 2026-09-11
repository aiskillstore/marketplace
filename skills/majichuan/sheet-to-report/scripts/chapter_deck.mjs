// Generic evidence deck author. No spreadsheet access or industry-specific copy.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {samplePageIndices,composePolishedPage,wrapPolishedText} from './chapter_slideviber_layout.mjs';
import {composeVisualPage} from './chapter_visual_layout.mjs';
import {EXTENDED_KINDS,axisRange,chartGeometry,drawExtendedChart,drawScatterKey,scatterIdentifiers} from './chapter_chart_geometry.mjs';
const [modelFile,selectionFile,projectionFile,outDir,mode,storyFile]=process.argv.slice(2);
if(!outDir)throw Error('usage: model.json selection.json projection.json NEW_OUTPUT [scene-only]');
const root=path.dirname(fileURLToPath(import.meta.url));
const PY=process.env.RUNTIME_PYTHON||(process.platform==='win32'?'python':'python3');
process.env.PYTHONUTF8='1';
execFileSync(PY,[path.join(root,'chapter_presentation.py'),'--model',modelFile,'--selection',selectionFile,'--verify',projectionFile,...(storyFile?['--story',storyFile]:[])],{encoding:'utf8'});
const d=JSON.parse(await fs.readFile(projectionFile,'utf8')),c=d.selection.config.palette,F=d.selection.config.font;
const polished=d.selection.target==='slideviber';
const sampleIndices=samplePageIndices(mode,d.slides);
if(mode && !['scene-only','full'].includes(mode) && !sampleIndices)throw Error('Unknown authoring mode');
const pageIndices=sampleIndices??d.slides.map((_,i)=>i);
const pages=pageIndices.map(i=>d.slides[i]);
const compositions=[];
// Design accents retain theme hue while meeting text contrast; plotted series stay unchanged.
function readableAccent(index){
 const rgb=c.chart[index%c.chart.length].match(/../g).map(n=>parseInt(n,16));
 const luminance=values=>values.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
 const bg=luminance(c.background.match(/../g).map(n=>parseInt(n,16)));
 let scale=1,result=rgb;
 while((Math.max(bg,luminance(result))+.05)/(Math.min(bg,luminance(result))+.05)<4.5 && scale>.1){scale*=.9;result=rgb.map(v=>Math.round(v*scale));}
 return result.map(v=>v.toString(16).padStart(2,'0')).join('').toUpperCase();
}
const color=role=>'#'+(/^design-\d+$/.test(role)?readableAccent(Number(role.slice(7))):(c[role]??c.ink)),seriesColor=i=>'#'+c.chart[i%c.chart.length];
const scene=[],charts=[];let objects;
const text=(t,x,y,w,h,size=26,role='ink',bold=false)=>objects.push({kind:'text',t:String(t),x,y,w,h,size,fill:color(role),bold});
const rect=(x,y,w,h,fill)=>objects.push({kind:'rect',x,y,w,h,fill});
const line=(x1,y1,x2,y2,fill=color('line'),width=1)=>objects.push({kind:'line',x1,y1,x2,y2,fill,width});
const fmt=v=>Number(v).toLocaleString('en-US',{maximumFractionDigits:2});
const chartNumber=v=>Math.abs(v)>=1e8?fmt(v/1e8)+'亿':Math.abs(v)>=1e4?Number(v/1e4).toFixed(1)+'万':fmt(v);
const wrap=(t,n=36)=>wrapPolishedText(t,n);
function vectorChart(v,box){
 if(EXTENDED_KINDS.includes(v.kind))return drawExtendedChart(v,box,{push:o=>objects.push(o),text,rect,line,color,seriesColor,wrap,fmt,chartNumber});
 const {x,y,w,h,horizontal,range}=chartGeometry(v,box);
 if(v.kind==='paired'){
  v.series.forEach((z,j)=>{text(z.label+'（'+z.unit+'）',x+j*w/2,y-35,w/2-30,30,22,'muted');vectorChart({...v,kind:'bar',series:[z]},{x:x+j*w/2,y,w:w/2-40,h});});return;
 }
 if(v.kind==='donut'){
  const cx=x+w*.33,cy=y+h*.47,r=Math.min(w*.23,h*.40),inner=r*.58;let a=-Math.PI/2;
  v.series[0].values.forEach((value,i)=>{const b=a+value/100*Math.PI*2;
   const point=(rr,aa)=>[cx+rr*Math.cos(aa),cy+rr*Math.sin(aa)];const p=point(r,a),q=point(r,b),u=point(inner,b),z=point(inner,a);
   objects.push({kind:'path',d:`M ${p} A ${r} ${r} 0 ${b-a>Math.PI?1:0} 1 ${q} L ${u} A ${inner} ${inner} 0 ${b-a>Math.PI?1:0} 0 ${z} Z`,fill:seriesColor(i)});
   text(v.labels[i]+'  '+fmt(value)+'%',x+w*.63,y+35+i*55,w*.37,45,25);a=b;});return;
 }
 const axisLabelChars=Math.max(chartNumber(range.min).length,chartNumber(range.max).length);
 const left=horizontal?Math.min(240,w*.29):Math.max(70,axisLabelChars*12+24),plot={x:x+left,y:y+15,w:w-left-25,h:h-100};
 const sy=value=>plot.y+plot.h-(value-range.min)/(range.max-range.min)*plot.h;
 const sx=value=>plot.x+(value-range.min)/(range.max-range.min)*plot.w;
 for(let i=0;i<=Math.round((range.max-range.min)/range.step);i++){const value=range.min+range.step*i;
  if(horizontal){line(sx(value),plot.y,sx(value),plot.y+plot.h);text(chartNumber(value),sx(value)-35,plot.y+plot.h+15,78,30,18,'muted');}
  else{line(plot.x,sy(value),plot.x+plot.w,sy(value));text(chartNumber(value),x,sy(value)-13,left-10,30,18,'muted');}}
 const gap=(horizontal?plot.h:plot.w)/v.labels.length;
 const valueLabelBoxes=[];
 const columnValueLabel=(value,x,y,w)=>{
  if(box.avoid_label_overlap){
   const label=chartNumber(value),actualWidth=[...label].reduce((s,c)=>s+(/[^\x00-\xff]/.test(c)?20:11),0);
   while(valueLabelBoxes.some(b=>x<b.x+b.w+5&&x+actualWidth+5>b.x&&y<b.y+30&&y+30>b.y))y-=32;
   if(y<box.y-20)throw Error('Chart value labels require a wider layout');
   valueLabelBoxes.push({x,y,w:actualWidth});
  }
  text(chartNumber(value),x,y,w,32,20);
 };
 if(v.kind==='line'||v.kind==='scatter'){
  const xs=v.x_values.map((a,i)=>typeof a==='number'?a:i),lo=Math.min(...xs),hi=Math.max(...xs),xx=a=>plot.x+(a-lo)/(hi-lo||1)*plot.w;
  v.series.forEach((z,j)=>{const points=z.values.map((value,i)=>[xx(xs[i]),sy(value)]);
   if(v.kind==='line')objects.push({kind:'polyline',points,fill:seriesColor(j),width:3});
   for(const [px,py] of points)objects.push({kind:'circle',cx:px,cy:py,r:4,fill:seriesColor(j)});
  });
  v.labels.forEach((label,i)=>{if(v.labels.length<=10||i%Math.ceil(v.labels.length/8)===0||i===v.labels.length-1)text(wrap(label,10),xx(xs[i])-40,plot.y+plot.h+15,95,55,18,'muted');});
 }else if(v.kind==='waterfall'){
  v.labels.forEach((label,i)=>{const bw=gap*.58,xx=plot.x+gap*(i+.5)-bw/2,yy=Math.min(sy(v.bases[i]),sy(v.ends[i])),hh=Math.abs(sy(v.bases[i])-sy(v.ends[i]));
   rect(xx,yy,bw,Math.max(.01,hh),v.roles[i]==='delta'?(v.series[0].values[i]<0?'#BA442F':'#167A67'):seriesColor(0));
   if(i<v.labels.length-1)line(xx+bw,sy(v.ends[i]),xx+gap,sy(v.ends[i]),color('muted'));
   text(fmt(v.series[0].values[i]),xx-18,yy-30,bw+36,30,20);text(wrap(label,9),plot.x+gap*i,plot.y+plot.h+15,gap-3,65,20);
  });
 }else{
  v.labels.forEach((label,i)=>{
   if(horizontal)text(wrap(label,Math.floor(left/22)),x,plot.y+gap*(i+.5)-26,left-12,60,22);
   else {
    text(wrap(label,Math.max(6,Math.floor(gap/22))),plot.x+gap*i,plot.y+plot.h+12,gap-4,65,20,'ink',box.focus_indices?.includes(i));
    const note=box.label_notes?.[label];
    if(note)text(wrap(note,Math.max(6,Math.floor(gap/18))),plot.x+gap*i,plot.y+plot.h+49,gap-4,30,18,'muted',true);
   }
   v.series.forEach((z,j)=>{const bw=gap*.68/(v.kind==='stacked'?1:v.series.length),value=z.values[i],base=v.kind==='stacked'?z.bases[i]:0,end=v.kind==='stacked'?z.ends[i]:value;
    if(horizontal){const yy=plot.y+gap*i+gap*.16+j*bw;rect(Math.min(sx(base),sx(end)),yy,Math.abs(sx(end)-sx(base)),bw-3,seriesColor(j));text(chartNumber(value),value<0?sx(end)-94:sx(end)+8,yy-3,90,32,21);}
    else{const xx=plot.x+gap*i+gap*.16+(v.kind==='stacked'?0:j*bw);rect(xx,Math.min(sy(base),sy(end)),bw-3,Math.abs(sy(end)-sy(base)),seriesColor(j));if(v.kind!=='stacked')columnValueLabel(value,xx-12,Math.min(sy(base),sy(end))-29,bw+35);}
   });
  });
 }
 if(v.series.length>1)v.series.forEach((z,j)=>{rect(x+j*w/v.series.length,y+h+8,13,13,seriesColor(j));text(z.label,x+j*w/v.series.length+20,y+h,w/v.series.length-28,35,21,'muted');});
}

function navigation(page){
 if(page.kind==='cover')return;
 text(page.navigation.eyebrow,64,20,1150,28,20,'accent',true);
 text(page.navigation.phase,66,690,600,24,17,'muted');
 text(`${String(d.slides.indexOf(page)+1).padStart(2,'0')} / ${d.slides.length}`,1100,688,130,26,18,'muted');
}
function overview(page,polish=false){
 text(page.period+' · 全分析期整体口径',66,158,1140,32,22,'muted');
 page.blocks.forEach((b,i)=>{
  const x=66+(i%2)*590,y=235+Math.floor(i/2)*142;
  if(polish)line(x,y-22,x+528,y-22,color('line'),1);
  text(b.label,x,y,530,33,23,'muted');
  text(b.text,x,y+45,544,58,polish?36:34,'accent',true);
 });
}
for(const page of pages){
 objects=[];scene.push(objects);
 const nativeChart=(id,box)=>{
  const v=d.chart_views[id];chartGeometry(v,box);
  if(v.kind==='waterfall'){vectorChart(v,box);return;}
  if(v.kind==='paired'){
   v.series.forEach((s,j)=>text(wrap(s.label+'（'+s.unit+'）',20),box.x+j*box.w/2,box.y-12,box.w/2-20,35,22,'muted'));
   objects.push({kind:'chart',id,...box,y:box.y+30,h:box.h-30});return;
  }
  if(v.kind==='donut'){
   objects.push({kind:'chart',id,...box,w:box.w*.58});
   v.labels.forEach((label,i)=>{const x=box.x+box.w*.62,y=box.y+24+i*51;rect(x,y+7,14,14,seriesColor(i));text(wrap(label+'  '+fmt(v.series[0].values[i])+'%',17),x+25,y,box.w*.38-30,45,22,'muted');});return;
  }
  if(['scatter','histogram'].includes(v.kind)){
   text('横轴：'+v.axes.x.label+(v.axes.x.unit?'（'+v.axes.x.unit+'）':'')+'；纵轴：'+v.series[0].label+'（'+v.series[0].unit+'）',box.x,box.y-10,box.w,32,20,'muted');
   if(v.kind==='scatter')box=drawScatterKey(v,{...box,y:box.y+26,h:box.h-26},{text,wrap,fmt});
   objects.push({kind:'chart',id,...box,...(v.kind==='histogram'?{y:box.y+26,h:box.h-26}:{})});return;
  }
  objects.push({kind:'chart',id,...box});
 };
 const visual=composeVisualPage(page,d,{text,rect,line,color,wrap,vectorChart,nativeChart},polished);
 if(visual){compositions.push(visual);navigation(page);continue;}
 if(polished){
  const fallback=composePolishedPage(page,d,{text,rect,line,color,wrap,vectorChart,overview});
  compositions.push({...fallback,...(page.visual?{fallback_reason:'density, capacity or page relationship uses existing layout'}:{})});
  navigation(page);
  continue;
 }
 const cover=page.kind==='cover';rect(0,0,1280,720,color(cover?'cover_background':'background'));
 if(cover){text(wrap(page.title,17),72,160,1110,235,64,'cover_ink',true);page.blocks.forEach((b,i)=>text(wrap(b.text,38),76,432+i*74,1100,65,28,'cover_muted'));}
 else{
  text(wrap(page.title,29),64,65,1150,92,38,'ink',true);
  if(page.kind==='overview'){overview(page);}
  else if(page.kind==='chart'){
   const v=d.chart_views[page.chart_id],units=[...new Set(v.series.map(z=>z.unit))].join(' / ');
   text(wrap(page.blocks[0].text+'；单位：'+units,48),66,151,1130,54,22,'muted');
   const box={x:65,y:204,w:1135,h:380};chartGeometry(v,box);
   if(polished||v.kind==='waterfall')vectorChart(v,box);else nativeChart(page.chart_id,box);
   const note=[v.tail_note,...(v.warnings??[]),...(v.constraints??[])].filter(Boolean).join('；');
   if(note.length>140)throw Error('Chart disclosure capacity exceeded; revise upstream constraints');
   if(note)text(wrap(note,60),66,635,1100,50,18,'muted');
    }else if(page.kind==='summary' && page.blocks.some(b=>b.label!=='判断' && b.label!=='判断（续）')){
     page.blocks.forEach((b,i)=>{const y=182+i*158;text(String(b.conclusion_number).padStart(2,'0'),66,y,72,42,30,'accent',true);text(wrap(b.label,38),154,y,1050,38,28,'accent',true);text(wrap(b.text,40),154,y+43,1048,110,26);});
    }else{
     const count=page.blocks.length,step=440/Math.max(1,count);
   page.blocks.forEach((b,i)=>{let y=186+i*step;text(wrap(b.label,7),66,y,180,72,23,'accent',true);text(wrap(b.text,34),258,y-2,942,step-14,26);});
  }
  navigation(page);
 }
 if(!polished)compositions.push({layout:'standard-existing',...(page.visual?{fallback_reason:'density, capacity or page relationship uses existing layout'}:{})});
}
await fs.mkdir(outDir,{recursive:false});
await fs.writeFile(path.join(outDir,'scene.json'),JSON.stringify({source:d.sha256,width:1280,height:720,scene,
 ...(sampleIndices?{purpose:mode.startsWith('design-review:')?'design-review':'design-sample',page_indices:pageIndices}:{}),
 compositions,...(polished?{layout_version:d.story?.visual?'slideviber-composition/3':'slideviber-composition/2',vector_line_mode:'thin-rect'}:{})},null,2));
if(mode==='scene-only'){console.log(outDir);process.exit(0);}
if(polished){
 const theme=d.slideviber_theme;theme.colors['cover-background']=color('cover_background');theme.colors['cover-ink']=color('cover_ink');theme.colors['cover-muted']=color('cover_muted');
 const reverse=new Map(Object.entries(theme.colors).map(([key,value])=>[value.toLowerCase(),`var(--${key})`]));
 const col=value=>reverse.get(value.toLowerCase())??value;
 const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
 await fs.writeFile(path.join(outDir,'theme.json'),JSON.stringify(theme,null,2));await fs.mkdir(path.join(outDir,'slides'));
 for(let i=0;i<scene.length;i++){
  const parts=scene[i].map(source=>{
   // SlideViber's text converter does not apply ancestor SVG transforms.
   // Author both text and primitives directly in its 1920x1080 coordinate space.
   const o={...source};for(const key of ['x','y','w','h','size','x1','x2','y1','y2','width','cx','cy','r'])if(typeof o[key]==='number')o[key]*=1.5;
   if(o.points)o.points=o.points.map(p=>p.map(n=>n*1.5));
   if(o.kind==='chart-meta')return '';
   if(o.kind==='polygon')return `<polygon points="${o.points.map(p=>p.join(',')).join(' ')}" fill="${col(o.fill)}"/>`;
   if(o.kind==='text')return `<foreignObject x="${o.x}" y="${o.y}" width="${o.w}" height="${o.h}"><div xmlns="http://www.w3.org/1999/xhtml" style="font-family:var(--font-body);font-size:${o.size}px;line-height:1.22;color:${col(o.fill)};font-weight:${o.bold?700:400};margin:0;padding:0;">${esc(o.t).replaceAll('\n','<br/>')}</div></foreignObject>`;
   if(o.kind==='rect')return `<rect x="${o.x}" y="${o.y}" width="${o.w}" height="${o.h}" fill="${col(o.fill)}"/>`;
   if(o.kind==='line'){
    if(o.x1===o.x2||o.y1===o.y2)return `<rect x="${Math.min(o.x1,o.x2)}" y="${Math.min(o.y1,o.y2)}" width="${Math.max(Math.abs(o.x2-o.x1),o.width)}" height="${Math.max(Math.abs(o.y2-o.y1),o.width)}" fill="${col(o.fill)}"/>`;
    return `<line x1="${o.x1}" y1="${o.y1}" x2="${o.x2}" y2="${o.y2}" stroke="${col(o.fill)}" stroke-width="${o.width}"/>`;
   }
   if(o.kind==='circle')return `<circle cx="${o.cx}" cy="${o.cy}" r="${o.r}" fill="${col(o.fill)}"/>`;
   if(o.kind==='polyline')return `<polyline points="${o.points.map(p=>p.join(',')).join(' ')}" fill="none" stroke="${col(o.fill)}" stroke-width="${o.width}"/>`;
   if(o.kind==='path')return `<path transform="scale(1.5)" d="${o.d}" fill="${col(o.fill)}"/>`;
   throw Error('unhandled vector object');
  });
  await fs.writeFile(path.join(outDir,'slides',`slide_${String(i+1).padStart(2,'0')}.svg`),parts.join('\n'));
 }
}else{
 execFileSync(PY,[path.join(root,'chapter_pptx_export.py'),'--model',modelFile,'--selection',selectionFile,
  '--projection',projectionFile,'--scene',path.join(outDir,'scene.json'),'--output',path.join(outDir,'draft.pptx'),
  ...(storyFile?['--story',storyFile]:[])],{encoding:'utf8',stdio:'inherit'});
}
console.log(outDir);
