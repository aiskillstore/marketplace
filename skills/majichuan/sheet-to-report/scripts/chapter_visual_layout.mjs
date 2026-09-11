import {composeSlideviberDesign} from './chapter_slideviber_design.mjs';
// Content-aware presentation layouts. Every analytical string is a bound input.
// Returning null delegates to the existing capacity-safe layout without losing copy.
export function composeVisualPage(page, deck, api, polished) {
  if(!page.visual)return null;
  if(polished){const design=composeSlideviberDesign(page,deck,api);if(design)return design;}
  const {text,rect,line,color,wrap,vectorChart,nativeChart}=api;
  const fits=(t,n,rows)=>{try{return wrap(t,n).split('\n').length<=rows;}catch{return false;}};
  const balanced=(t,n)=>{
    let result=wrap(t,n);
    while(n>5 && result.includes('\n') && result.split('\n').at(-1).length<Math.ceil(n*.4))result=wrap(t,--n);
    return result;
  };
  const put=(t,x,y,w,h,size,role='ink',bold=false,n=36)=>text(wrap(t,n),x,y,w,h,size,role,bold);
  const meta=layout=>({layout,relation:page.visual.relation,sourcePage:page.id,
    sourceBlockIndices:page.visual.block_indices,focus_indices:page.visual.focus_indices,contextSource:null});
  const header=()=>{
    rect(0,0,1280,720,color(polished?'surface':'background'));
    put(page.title,64,65,1152,92,38,'ink',true,29);
  };
  const blocks=page.blocks;
  if(page.kind==='summary'){
    const w=(1152-40*(blocks.length-1))/blocks.length;
    if(polished){
      const n=Math.floor(w/30),body=Math.floor(w/26);
      if(blocks.some(b=>!fits(b.label,n,3)||!fits(b.text,body,7)))return null;
      header();
      blocks.forEach((b,i)=>{
        const x=64+i*(w+40);
        put(String(b.conclusion_number).padStart(2,'0'),x,184,w,86,60,'accent',true);
        line(x,282,x+w,282,color('line'),2);
        text(balanced(b.label,n),x,308,w,118,30,'ink',true);
        put(b.text,x,443,w,222,26,'ink',false,body);
      });return meta('equal-judgement-columns');
    }
    if(blocks.some(b=>!fits(b.label,36,1)||!fits(b.text,38,3)))return null;
    header();blocks.forEach((b,i)=>{
      const y=192+i*157;
      rect(64,y,5,127,color('line'));
      put(String(b.conclusion_number).padStart(2,'0'),86,y+1,74,48,34,'accent',true);
      put(b.label,184,y,1015,40,28,'ink',true,36);
      put(b.text,184,y+48,1015,99,26,'ink',false,38);
    });return meta('judgement-led-rows');
  }
  if(page.kind==='overview'){
    const cols=polished?3:2,cellW=polished?357:554;
    if(blocks.some(b=>!fits(b.label,Math.floor(cellW/23),1)||!fits(b.text,Math.floor(cellW/36),1)))return null;
    header();put(page.period+' · 全分析期整体口径',66,158,1140,32,22,'muted');
    blocks.forEach((b,i)=>{
      const x=64+(i%cols)*(polished?397:598),y=polished?226+Math.floor(i/cols)*215:229+Math.floor(i/cols)*145;
      put(b.label,x,y,cellW,34,23,'muted');
      put(b.text,x,y+48,cellW,62,polished?38:36,'ink',true,Math.floor(cellW/(polished?38:36)));
      // Identical dividers signal equal status; their width never encodes metric magnitude.
      rect(x,y+121,cellW,2,color('line'));
      rect(x,y+121,35,2,color('muted'));
    });return meta(polished?'equal-metric-spread':'declared-metric-ledger');
  }
  if(page.kind==='action' && blocks.length===3 && blocks[2].label==='执行步骤'){
    if(polished){
      if(!fits(blocks[0].text,14,4)||!fits(blocks[1].text,15,6)||!fits(blocks[2].text,18,9))return null;
      header();
      put(blocks[0].label,66,202,424,34,23,'accent',true);
      put(blocks[0].text,66,247,424,148,29,'ink',false,14);
      put(blocks[1].label,66,408,424,34,23,'accent',true);
      put(blocks[1].text,66,453,424,198,27,'ink',false,15);
      rect(546,194,670,461,color('cover_background'));
      put(blocks[2].label,583,226,593,36,24,'cover_muted',true);
      put(blocks[2].text,583,286,593,351,32,'cover_ink',false,18);
      return meta('action-context-and-execution-focus');
    }
    if(blocks.some(b=>!fits(b.text,34,4)))return null;
    header();blocks.forEach((b,i)=>{
      const y=199+i*151;
      put(b.label,66,y,175,38,24,'accent',true);
      put(b.text,258,y,940,131,26,'ink',false,34);
      if(i<2)line(258,y+134,1208,y+134,color('line'),1);
    });return meta('action-purpose-rows');
  }
  if(page.kind==='action'&&blocks.length===2&&blocks[0].label==='验证信号'&&blocks[1].label==='行动边界'){
    if(polished){
      if(!fits(blocks[0].text,33,3)||!fits(blocks[1].text,37,4))return null;
      header();rect(64,194,1152,198,color('cover_background'));
      put(blocks[0].label,96,218,1088,34,24,'cover_muted',true);
      put(blocks[0].text,96,273,1088,116,32,'cover_ink',false,33);
      put(blocks[1].label,66,445,1148,37,24,'accent',true);
      put(blocks[1].text,66,504,1148,148,29,'ink',false,37);
      return meta('validation-signal-and-guardrail');
    }
    if(blocks.some(b=>!fits(b.text,37,4)))return null;
    header();blocks.forEach((b,i)=>{
      const y=218+i*235;
      put(b.label,66,y,220,38,24,'accent',true);
      put(b.text,300,y,900,166,26,'ink',false,32);
      if(!i)line(66,422,1214,422,color('line'),1);
    });return meta('validation-purpose-rows');
  }
  if(page.kind==='chart' && page.visual.focus_indices.length){
    const view=deck.chart_views[page.chart_id];
    header();
    put('单位：'+[...new Set(view.series.map(s=>s.unit))].join(' / '),66,158,1148,36,22,'muted');
    const box={x:65,y:207,w:1135,h:383};
    if(polished)vectorChart(view,{...box,avoid_label_overlap:true,
      focus_indices:page.visual.focus_indices,label_notes:page.visual.label_notes??{}});
    else nativeChart(page.chart_id,box);
    put(page.blocks[0].text,66,627,1148,32,20,'muted',false,58);
    const note=[view.tail_note,...(view.warnings??[]),...(view.constraints??[])].filter(Boolean).join('；');
    if(note)put(note,66,662,1148,26,18,'muted',false,60);
    return meta('wide-chart-with-direct-focus');
  }
  return null;
}
