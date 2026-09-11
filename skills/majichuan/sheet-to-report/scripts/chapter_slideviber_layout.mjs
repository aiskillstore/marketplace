// Compositions consume bound presentation content only.
// No case names, metrics, slide numbers, or new analytical claims live here.
export function wrapPolishedText(value, columns=36) {
  const raw=String(value).match(/\d{4}-\d{2}(?:-\d{2})?|[-+]?\d[\d,]*(?:\.\d+)?%?|[A-Za-z]+|[^]/gu)??[];
  const tokens=[];
  for(const token of raw){
    if(/^[，。、；：！？）】》”’]$/.test(token)&&tokens.length&&tokens.at(-1)!=='\n')tokens[tokens.length-1]+=token;
    else tokens.push(token);
  }
  const rows=[];let row='',units=0;
  for(const token of tokens){
    if(token==='\n'){rows.push(row);row='';units=0;continue;}
    const width=[...token].reduce((sum,ch)=>sum+(/[^\x00-\xff]/.test(ch)?1:.55),0);
    if(width>columns)throw Error('Numeric text token exceeds polished text capacity');
    if(row&&units+width>columns){rows.push(row);row='';units=0;}
    row+=token;units+=width;
  }
  if(row)rows.push(row);
  return rows.filter(Boolean).join('\n');
}

export function samplePageIndices(mode, slides) {
  if(mode?.startsWith('design-review:')){
    const tokens=mode.slice('design-review:'.length).split(',');
    if(!tokens.length || tokens.some(t=>!/^page-\d{3}$/.test(t)) || new Set(tokens).size!==tokens.length)
      throw Error('Design review requires unique source page IDs');
    const indices=tokens.map(id=>slides.findIndex(s=>s.id===id));
    if(indices.some(i=>i<0))throw Error('Design review page is outside source projection');
    if(indices.some((i,n)=>n&&i<=indices[n-1]))throw Error('Design review preserves source reading order');
    return indices;
  }
  if (!mode?.startsWith('design-sample:')) return null;
  const tokens = mode.slice('design-sample:'.length).split(',');
  if (tokens.length !== 2 || tokens.some(t => !/^[1-9]\d*$/.test(t)))
    throw Error('Design sample requires a cover and a chart page, using two source page numbers');
  const indices = tokens.map(t => Number(t)-1);
  if (slides[indices[0]]?.kind !== 'cover' || slides[indices[1]]?.kind !== 'chart')
    throw Error('Design sample must preserve source cover then source chart');
  return indices;
}

export function composePolishedPage(page, deck, api) {
  const {text, rect, line, color, wrap, vectorChart, overview} = api;
  // Text capacity is checked before export; never shrink type or omit source copy.
  const fitted = (value, columns, maxLines) => {
    const result = wrap(value, columns);
    if (result.split('\n').length > maxLines)
      throw Error('Polished composition text capacity exceeded; choose a wider layout or split upstream');
    return result;
  };
  rect(0,0,1280,720,color('surface'));
  if (page.kind === 'cover') {
    const [period, purpose, ...extra] = page.blocks;
    if (!period || !purpose || extra.length) throw Error('Cover requires bound period and purpose blocks');
    const qualifier = page.title.match(/^(.*?)([（(][^（）()]+[）)])$/);
    text(fitted(qualifier?qualifier[1]:page.title,12,2),72,220,1100,190,74,'ink',true);
    if(qualifier)text(fitted(qualifier[2],32,1),76,415,1080,42,28,'muted');
    text(period.label,74,65,260,32,22,'muted');
    text(fitted(period.text,30,1),74,103,1080,40,28,'accent',true);
    line(74,473,1206,473,color('line'),1);
    text(purpose.label,74,506,220,34,22,'accent',true);
    text(fitted(purpose.text,30,3),300,501,900,125,28,'ink');
    return {layout:'typographic-cover',contextSource:null};
  }
  if (page.kind !== 'chart') {
    if(page.kind==='overview'){
      text(fitted(page.title,26,2),64,65,1150,92,38,'ink',true);
      overview(page,true);return {layout:'overall-metric-grid',contextSource:null};
    }
    if (!['summary','chapter','action','method'].includes(page.kind)) throw Error('Unknown polished page kind');
    if (!page.blocks.length || page.blocks.length > 3) throw Error('Polished page block capacity exceeded');
    text(fitted(page.title,29,2),64,65,1150,92,38,'ink',true);
    const footer=()=>{}; // Shared navigation/footer is added by the author after composition.
    const block=(b,x,y,w,columns,size,maxLines)=>{
      text(b.label,x,y,w,32,22,'accent',true);
      text(fitted(b.text,columns,maxLines),x,y+43,w,maxLines*size*1.3,size,'ink');
    };
      if(page.kind==='summary'){
        page.blocks.forEach((b,i)=>{
          const titled=b.label!=='判断'&&b.label!=='判断（续）';
          const y=(titled?184:204)+i*(titled?158:144);
          text(String(b.conclusion_number??i+1).padStart(2,'0'),66,y-8,92,72,48,'accent',true);
          if(titled){
            text(fitted(b.label,40,1),188,y,1005,36,26,'accent',true);
            text(fitted(b.text,38,3),188,y+42,1005,108,26,'ink');
          }else text(fitted(b.text,30,3),188,y,1005,126,32,'ink');
          if(i<page.blocks.length-1)line(188,y+(titled?147:124),1196,y+(titled?147:124),color('line'),1);
      });
      footer();return {layout:'numbered-summary',contextSource:null};
    }
    if(page.kind==='chapter'){
      block(page.blocks[0],66,176,1148,32,32,5);
      for(let i=1;i<page.blocks.length;i++){
        const two=page.blocks.length===3,x=66+(i-1)*587;
        block(page.blocks[i],x,443,two?535:1148,two?19:39,26,6);
      }
      footer();return {layout:'evidence-meaning-boundary',contextSource:null};
    }
    if(page.kind==='action' && page.blocks.length===3 && page.blocks[2].label==='执行步骤'){
      block(page.blocks[0],66,194,418,14,27,3);
      block(page.blocks[1],66,380,418,14,27,7);
      line(530,190,530,646,color('line'),1);
      block(page.blocks[2],586,194,630,19,31,10);
      footer();return {layout:'action-context-and-steps',contextSource:null};
    }
    if(page.kind==='action' && page.blocks.length===2){
      block(page.blocks[0],66,215,522,17,29,10);
      line(622,210,622,647,color('line'),1);
      block(page.blocks[1],670,215,546,18,29,10);
      footer();return {layout:'action-signal-and-boundary',contextSource:null};
    }
    if(page.blocks.length===1){
      block(page.blocks[0],66,222,1138,30,34,7);
      footer();return {layout:'single-definition',contextSource:null};
    }
    // Reference material stays in a restrained, legible ledger.
    text('项目',66,173,220,32,22,'muted');text('口径',343,173,830,32,22,'muted');
    line(66,217,1214,217,color('line'),1);
    page.blocks.forEach((b,i)=>{
      const y=248+i*136;
      text(fitted(b.label,8,2),66,y,246,75,26,'accent',true);
      text(fitted(b.text,29,3),343,y,868,112,27,'ink');
      line(66,y+113,1214,y+113,color('line'),1);
    });
    footer();return {layout:'reference-ledger',contextSource:null};
  }
  const view = deck.chart_views[page.chart_id];
  const disclosure=[view.tail_note,...(view.warnings??[]),...(view.constraints??[])].filter(Boolean).join('；');
  const noteText=disclosure?fitted(disclosure,60,3):'';
  const scopeText=fitted(page.blocks[0].text,58,2);
  const noteExtra=Math.max(0,noteText.split('\n').length-1)*22;
  const scopeExtra=Math.max(0,scopeText.split('\n').length-1)*24;
  const footerExtra=noteExtra+scopeExtra;
  // A sidebar can repeat only a bound judgement from the same chapter sharing evidence.
  const context = deck.slides.find(s => s.kind === 'chapter' && s.owner === page.owner &&
    s.evidence_ids.some(id => page.evidence_ids.includes(id)));
  // Repeated context must actually discuss plotted values, not another metric
  // merely because it belongs to the same chapter. This is selection, not inference.
  const visibleNumber = n => Number(n).toLocaleString('en-US',{maximumFractionDigits:2}).replaceAll(',','');
  const values = new Set(view.series.flatMap(s=>s.values??[]).filter(n=>n!==0&&Number.isFinite(n)).map(visibleNumber));
  const contextBlockIndex = context?.blocks.findIndex(b=>{
    const mentioned=new Set((b.text.match(/-?\d[\d,]*(?:\.\d+)?/g)??[]).map(n=>visibleNumber(Number(n.replaceAll(',','')))));
    return [...values].filter(v=>mentioned.has(v)).length>=2;
  })??-1;
  const source = contextBlockIndex>=0?context.blocks[contextBlockIndex]:null;
  const contextFits = source && wrap(source.text,12).split('\n').length <= 7;
  const longestValue=Math.max(...view.series.flatMap(s=>s.values).map(v=>visibleNumber(v).length*11));
  const narrowBarWidth=(768-95)/view.labels.length*.68/view.series.length-3;
  const compact = ['line','bar','column','grouped'].includes(view.kind) && view.labels.length <= 6 && view.series.length <= 2 && contextFits && longestValue<=narrowBarWidth+5;
  if (compact) {
    const titleRows=fitted(page.title,8,4).split('\n');
    // Avoid a single trailing CJK character in narrow chart headings.
    const last=titleRows.length-1;
    if(last>0 && /^[\u3400-\u9fff]$/.test(titleRows[last]) && /[\u3400-\u9fff]{2}$/.test(titleRows[last-1])) {
      titleRows[last]=titleRows[last-1].slice(-1)+titleRows[last];
      titleRows[last-1]=titleRows[last-1].slice(0,-1);
    }
    text(titleRows.join('\n'),64,75,365,188,38,'ink',true);
    text(source.label,66,281,345,32,21,'accent',true);
    text(fitted(source.text,12,7),66,324,346,232,25,'ink');
    const units = [...new Set(view.series.map(s=>s.unit))].join(' / ');
    text('单位：'+units,478,88,700,32,21,'muted');
    vectorChart(view,{x:448,y:131,w:768,h:413-footerExtra});
  } else {
    // Dense trends retain the full chart width; no squeezing 18 labels into a sidebar layout.
    text(fitted(page.title,29,2),64,65,1150,92,38,'ink',true);
    text('单位：'+[...new Set(view.series.map(s=>s.unit))].join(' / '),66,155,1100,32,21,'muted');
    vectorChart(view,{x:65,y:205,w:1135,h:360-footerExtra});
  }
  line(64,610-footerExtra,1216,610-footerExtra,color('line'),1);
  text(scopeText,66,625-footerExtra,1140,24+scopeExtra,20,'muted');
  if(noteText) text(noteText,66,661-noteExtra,1134,24+noteExtra,18,'muted');
  return {layout:compact?'judgement-and-evidence':'wide-evidence',contextSource:compact?context.id:null,
    contextBlockIndex:compact?contextBlockIndex:null};
}
