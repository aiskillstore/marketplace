// Two-page presentation consumer. Takes frozen display evidence, never raw Excel.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
process.on('uncaughtException',e=>{console.error(e.message);process.exit(1);});
const [inputFile,selectionFile,outDir]=process.argv.slice(2);
if(!inputFile||!selectionFile||!outDir)throw Error('usage: input.json selection.json new-output-directory');
const root=path.dirname(fileURLToPath(import.meta.url));
const script=path.join(root,'ppt_theme_selection.py');
const PY=process.env.RUNTIME_PYTHON||(process.platform==='win32'?'python':'python3');
process.env.PYTHONUTF8='1';
const s=JSON.parse(await fs.readFile(selectionFile,'utf8')),d=JSON.parse(await fs.readFile(inputFile,'utf8'));
const validated=JSON.parse(execFileSync(PY,['-c',
 'import sys,json;sys.path.insert(0,sys.argv[1]);from ppt_theme_selection import validate_selection;v=json.load(open(sys.argv[2],encoding="utf-8"));print(json.dumps(validate_selection(v,preview=True),ensure_ascii=False))',path.dirname(script),selectionFile],{encoding:'utf8'}));
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
if(d.schema!=='ppt-theme-sample/1'||!d.source_model_sha256||d.source_model_sha256!==s.source_model_sha256)throw Error('source binding mismatch');
if(d.chart.labels.length<2||d.chart.series.some(z=>z.values.length!==d.chart.labels.length||z.values.some(v=>!Number.isFinite(v))))throw Error('invalid chart values');
if(d.chart.min>=d.chart.max||d.chart.series.some(z=>z.values.some(v=>v<d.chart.min||v>d.chart.max)))throw Error('invalid chart limits');
await fs.mkdir(outDir,{recursive:false});
const c=validated.palette,F=validated.font,editorial=validated.layout==='editorial',polished=s.target==='slideviber';
const scene=[];let page;
function rect(x,y,w,h,role){page.push({kind:'rect',x,y,w,h,role});}
function text(t,x,y,w,h,size,role='ink',bold=false){page.push({kind:'text',t,x,y,w,h,size,role,bold});}
function newPage(){page=[];scene.push(page);rect(0,0,1280,720,'background');}
newPage();
if(editorial){
 rect(825,0,455,720,'cover_background');text(d.cover.eyebrow,70,65,680,48,22,'accent',true);
 text(d.cover.title,70,170,700,245,polished?72:66,'ink',true);rect(70,453,170,5,'secondary');
 text(d.cover.subtitle,70,491,690,126,28,'muted');text(d.cover.side,875,175,330,310,38,'cover_ink',true);
}else if(validated.cover==='navy-panel'){
 rect(0,0,1280,720,'cover_background');rect(65,74,7,515,'secondary');text(d.cover.eyebrow,112,82,1030,45,23,'cover_muted');
 text(d.cover.title,110,190,1050,205,66,'cover_ink',true);text(d.cover.subtitle,114,435,1000,92,28,'cover_muted');text(d.cover.side,114,580,1060,82,30,'cover_ink',true);
}else{
 rect(0,0,1280,16,'accent');text(d.cover.eyebrow,80,85,1100,48,23,'accent',true);
 text(d.cover.title,78,207,1100,205,66,'ink',true);text(d.cover.subtitle,83,435,1080,88,29,'muted');
 rect(80,577,1120,3,'line');text(d.cover.side,83,614,1100,69,28,'accent',true);
}
newPage();
const a=editorial?{x:425,y:166,w:785,h:375}:{x:170,y:215,w:1035,h:335};
if(editorial){text(d.chart.title,58,74,326,250,38,'ink',true);rect(60,364,270,4,'secondary');text(d.chart.subtitle,60,407,305,168,23,'muted');}
else{text(d.chart.title,65,57,1150,80,43,'ink',true);text(d.chart.subtitle,68,141,1140,58,23,'muted');}
page.push({kind:'chart',...a});text(d.chart.note,65,651,1150,58,19,'muted');
const manifest={schema:'ppt-theme-sample-export/1',selection:s,source_file_sha256:sha(await fs.readFile(inputFile)),source:d,scene};
await fs.writeFile(path.join(outDir,'manifest.json'),JSON.stringify(manifest,null,2));
const esc=t=>String(t).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
function svgText(t,x,y,w,h,size,color,bold=false,align='left'){return `<foreignObject x="${x*1.5}" y="${y*1.5}" width="${w*1.5}" height="${h*1.5}"><div xmlns="http://www.w3.org/1999/xhtml" style="font-family:var(--font-body);font-size:${size*1.5}px;line-height:1.2;color:${color};font-weight:${bold?700:400};text-align:${align};margin:0;padding:0;">${esc(t).replaceAll('\n','<br/>')}</div></foreignObject>`;}
const mapping={background:'bg',surface:'surface',ink:'text-primary',muted:'text-muted',line:'border',accent:'secondary',secondary:'accent2',cover_background:'primary',cover_ink:'bg',cover_muted:'primary-light'};
if(s.target==='standard'){
 execFileSync(PY,[path.join(root,'ppt_theme_sample_export.py'),'--source',inputFile,'--selection',selectionFile,
  '--manifest',path.join(outDir,'manifest.json'),'--output',path.join(outDir,'draft.pptx')],{encoding:'utf8',stdio:'inherit'});
}else{
 const sv=JSON.parse(execFileSync(PY,['-c','import sys,json;sys.path.insert(0,sys.argv[1]);from ppt_theme_selection import slideviber_theme;v=json.load(open(sys.argv[2],encoding="utf-8"));print(json.dumps(slideviber_theme(v,preview=True),ensure_ascii=False))',path.dirname(script),selectionFile],{encoding:'utf8'}));
 // Specific cover roles remain theme variables; no literal per-slide color aliases.
 sv.colors['cover-ink']='#'+c.cover_ink;sv.colors['cover-muted']='#'+c.cover_muted;sv.colors['cover-background']='#'+c.cover_background;
 mapping.cover_ink='cover-ink';mapping.cover_muted='cover-muted';mapping.cover_background='cover-background';
 await fs.writeFile(path.join(outDir,'theme.json'),JSON.stringify(sv,null,2));await fs.mkdir(path.join(outDir,'slides'));
 for(let n=0;n<scene.length;n++){const parts=[];
  const r=(x,y,w,h,col)=>parts.push(`<rect x="${x*1.5}" y="${y*1.5}" width="${w*1.5}" height="${h*1.5}" fill="${col}"/>`);
  for(let o of scene[n]){
   if(o.kind==='chart')o={...o,x:o.x+(editorial?30:0),w:o.w-(editorial?30:0),h:o.h-50};
   const col='var(--'+mapping[o.role]+')';
   if(o.kind==='rect')r(o.x,o.y,o.w,o.h,col);
   else if(o.kind==='text')parts.push(svgText(editorial&&n===0&&o.t===d.cover.side?o.t.replace(' · ',' ·\n'):o.t,o.x,o.y,o.w,o.h,o.size,col,o.bold));
   else{
    const g=d.chart;const yy=v=>o.y+o.h-(v-g.min)/(g.max-g.min)*o.h;const gap=o.w/g.labels.length,bw=Math.min(65,gap/(g.series.length+1));
    for(let v=g.min;v<=g.max+.001;v+=g.step){r(o.x,yy(v),o.w,1,'var(--border)');parts.push(svgText(v+(g.suffix??''),o.x-65,yy(v)-13,60,32,18,'var(--text-muted)'));}
    for(let i=0;i<g.labels.length;i++){
     const center=o.x+gap*(i+.5);
     for(let j=0;j<g.series.length;j++){
      const v=g.series[j].values[i],x=center+(j-g.series.length/2)*bw;
      r(x,Math.min(yy(0),yy(v)),bw-4,Math.abs(yy(v)-yy(0)),'var(--accent'+(j+1)+')');
      parts.push(svgText(v.toFixed(1)+(g.suffix??''),x-14,v>=0?yy(v)-33:yy(v)+5,bw+24,32,19,'var(--text-primary)',true,'center'));
     }parts.push(svgText(g.labels[i],center-gap*.46,o.y+o.h+22,gap*.92,77,19,'var(--text-primary)',false,'center'));
    }
    g.series.forEach((z,j)=>{const x=o.x+j*o.w/g.series.length;r(x,o.y+o.h+103,14,14,'var(--accent'+(j+1)+')');parts.push(svgText(z.name,x+22,o.y+o.h+97,o.w/g.series.length-30,47,18,'var(--text-primary)'));});
   }
  }await fs.writeFile(path.join(outDir,'slides',`slide_${n+1}.svg`),parts.join('\n'));
 }
}
console.log(outDir);
