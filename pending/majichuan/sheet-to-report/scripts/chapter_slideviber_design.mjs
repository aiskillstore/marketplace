// Source-bound visual decisions for polished decks, independent of standard layout.
// Host declarations choose emphasis/relationships; no business inference occurs here.
export function composeSlideviberDesign(page, deck, api) {
  if(page.visual?.version!=='presentation-visual/2')return null;
  const {text,rect,line,color,wrap}=api,blocks=page.blocks;
  const fits=(s,n,rows)=>{try{return wrap(s,n).split('\n').length<=rows;}catch{return false;}};
  const put=(s,x,y,w,h,size=26,role='ink',bold=false,n=32)=>text(wrap(s,n),x,y,w,h,size,role,bold);
  const balanced=(s,n)=>{let value=wrap(s,n);while(n>5&&value.includes('\n')&&value.split('\n').at(-1).length<Math.ceil(n*.4))value=wrap(s,--n);return value;};
  const header=()=>{rect(0,0,1280,720,color('surface'));put(page.title,64,65,1152,92,38,'ink',true,29);};
  const meta=layout=>({layout,relation:page.visual.relation,sourcePage:page.id,
    sourceBlockIndices:page.visual.block_indices,focus_indices:page.visual.focus_indices,contextSource:null});
  if(page.kind==='summary'){
    // Leave 32px for exported text-frame insets and font metrics. Browser fit alone
    // is insufficient: OOXML reflow otherwise adds a line before an explicit break.
    const w=(1152-(blocks.length-1)*28)/blocks.length,n=Math.floor((w-48-32)/26),hn=Math.floor((w-48)/29);
    if(blocks.some(b=>!fits(b.label,hn,3)||!fits(b.text,n,5)))return null;
    header();
    blocks.forEach((b,i)=>{
      const x=64+i*(w+28),role=`design-${i}`;
      rect(x,193,w,435,color('background'));
      rect(x,193,w,5,color(role));
      put(String(b.conclusion_number).padStart(2,'0'),x+24,216,w-48,65,48,role,true);
      text(balanced(b.label,hn),x+24,305,w-48,105,27,'ink',true);
      line(x+24,422,x+w-24,422,color('line'),1);
      put(b.text,x+24,448,w-48,180,26,'ink',false,n);
    });return meta('judgement-panels-with-equal-weight');
  }
  if(page.kind==='overview' && page.visual.focus_indices.length===1){
    const index=page.visual.focus_indices[0],hero=blocks[index],others=blocks.filter((_,i)=>i!==index);
    if(others.length>5||!fits(hero.text,10,2)||!fits(hero.label,17,2)||
      others.some(b=>!fits(b.label,12,2)||!fits(b.text,9,1)))return null;
    header();put(page.period+' · 全分析期整体口径',66,156,1140,36,22,'muted');
    // Area communicates declared narrative emphasis, never compares unlike units.
    rect(64,219,508,406,color('cover_background'));
    put(hero.label,96,269,442,75,30,'cover_muted',true,14);
    put(hero.text,96,377,444,135,48,'cover_ink',true,10);
    others.forEach((b,i)=>{
      const x=606+(i%2)*312,y=231+Math.floor(i/2)*141;
      put(b.label,x,y,298,58,22,'muted',false,12);
      put(b.text,x,y+65,298,65,34,`design-${i%2}`,true,9);
    });return meta('declared-metric-spotlight');
  }
  const action=page.visual.action_layout;
  if(page.kind==='action' && action && blocks.length===3 && action.block_index===2){
    const w=(1152-(action.parts.length-1)*30)/action.parts.length,n=Math.floor((w-44-32)/26);
    if(!fits(blocks[0].text,36,2)||!fits(blocks[1].text,36,3)||
      action.parts.some(p=>!fits(p.label,n,2)||!fits(p.text,n,4)))return null;
    header();
    put(blocks[0].label,66,182,180,35,23,'accent',true);
    put(blocks[0].text,258,182,950,78,26,'ink',false,36);
    put(blocks[1].label,66,266,180,35,23,'accent',true);
    put(blocks[1].text,258,266,950,103,26,'ink',false,36);
    if(action.relation==='sequence')line(91,386,1173,386,color('line'),3);
    // First create headings, then source fragments in source order. Every clause remains visible.
    action.parts.forEach((p,i)=>{
      const x=64+i*(w+30),role=`design-${i}`;
      if(action.relation==='sequence'){
        rect(x,376,58,40,color('surface'));
        put(String(i+1).padStart(2,'0'),x+8,370,54,46,30,role,true);
      }
      rect(x,423,w,222,color('background'));rect(x,423,4,222,color(role));
      put(p.label,x+22,439,w-44,72,27,role,true,n);
    });
    action.parts.forEach((p,i)=>put(p.text,86+i*(w+30),518,w-44,134,26,'ink',false,n));
    return {...meta(action.relation==='sequence'?'source-bound-action-sequence':'source-bound-action-parallel'),
      source_fragments:[{block_index:2,texts:action.parts.map(p=>p.text)}],order_basis:action.basis};
  }
  if(page.kind==='action' && blocks.length===2 && blocks[0].label==='验证信号'&&blocks[1].label==='行动边界'){
    if(blocks.some(b=>!fits(b.text,16,7)))return null;
    header();
    blocks.forEach((b,i)=>{
      const x=64+i*596,role=i?'design-2':'design-1';
      rect(x,230,548,388,color('background'));rect(x,230,548,5,color(role));
      put(b.label,x+28,264,490,52,32,role,true);
      put(b.text,x+28,362,490,250,29,'ink',false,16);
    });return meta('validation-and-boundary-comparison');
  }
  return null;
}
