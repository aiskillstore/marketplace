(function () {
  'use strict';
  const root = document.getElementById('report');
  const dialog = document.getElementById('transactions-dialog');
  const words = {
    en: {title:'Personal finance',subtitle:'A closer look at your money',demo:'Fictional demo data',language:'Language',overview:'Overview',expenses:'Expenses',income:'Income',transfers:'Transfers',day:'Day',week:'Week',month:'Month',year:'Year',period:'Period',previous:'Previous period',next:'Next period',covered:'Source coverage',total:'Total spending',daily:'Everyday spending',dailyAverage:'Daily average',fixed:'Fixed services',ai:'AI services',housing:'Housing',education:'Education',equipment:'Equipment',other:'Other',inflow:'Total inflow',outflow:'Total outflow',net:'Net change',transferIn:'Transfers in',transferOut:'Transfers out',transferNet:'Net transfers',incomeTotal:'Total income',incomeAverage:'Income per day',incomeCount:'Income payments',trend:'Daily spending',incomeTrend:'Daily income',transfersTrend:'Daily transfer movement',cashTrend:'Daily cash movement',breakdown:'By category',sources:'By income category',transferBreakdown:'Transfer categories',cashBreakdown:'Cash movement',transactions:'Transactions',allTransactions:'All transactions in this view',summaries:'Period summary',explanations:'How this report is calculated',refunds:'Refunds',matched:'Full refund matched',settled:'Settled transfer',internal:'Internal transfer',empty:'No transactions in this period.',noChart:'No movement in this period.',date:'Date',description:'Description',category:'Category',account:'Account',bankAmount:'Bank amount',personalAmount:'Personal spending',adjusted:'Adjusted amount',source:'Source',count:'transactions',close:'Close transaction details',details:'Open transactions',days:'covered days',dayLabel:'day',range:'Covered dates',clickChart:'Select a bar to see its transactions',retained:'Original bank transactions are retained.',refundNote:'Confirmed full returns are excluded from spending, including across periods. Other refunds are shown separately.',explanation:'Spending uses confirmed personal shares and removes matched full returns. Cash movement follows bank dates, excludes internal transfers, and uses confirmed transfer settlements. Unknown incoming payments are transfers, not income. All amounts use the report currency.',averageTip:'Everyday spending divided by covered calendar days in this period.',dailyTip:'Personal spending in the everyday group. Fixed services, AI, housing and other groups are separate.',totalTip:'All expense groups at the confirmed personal share, excluding purchases with matched full refunds.',fixedTip:'Recurring services classified as fixed; excludes AI and housing.',aiTip:'Only expenses explicitly classified as AI services.',housingTip:'Housing spending at the confirmed personal share.',cashTip:'External bank-date movement after confirmed transfer settlements; internal movements are excluded.',incomeTip:'Only payments classified as income. Incoming transfers are separate.',transferTip:'External transfers after confirmed settlements. Original bank amounts remain available.',local:'Standalone report · no network connection required',error:'The report could not be opened',errorBody:'Check dates, amount signs, unique IDs, coverage and mappings against references/schema.md, then rerun the command.',unpaired:'Unpaired refund',refundType:'Refund status',zero:'No data',periodTotal:'Total',amount:'Amount',notes:'Source notes',uncategorized:'Uncategorized'},
    zh: {title:'个人财务',subtitle:'看清每一段时间的收支',demo:'虚构演示数据',language:'语言',overview:'收支总览',expenses:'消费',income:'收入',transfers:'转账',day:'天',week:'周',month:'月',year:'年',period:'期间',previous:'上一期',next:'下一期',covered:'资料覆盖',total:'总花费',daily:'日常消费',dailyAverage:'日均日常消费',fixed:'固定服务',ai:'AI 服务',housing:'租房',education:'教育',equipment:'数码设备',other:'其他',inflow:'总流入',outflow:'总流出',net:'净增减',transferIn:'转入',transferOut:'转出',transferNet:'转账净额',incomeTotal:'总收入',incomeAverage:'日均收入',incomeCount:'收入笔数',trend:'每日消费',incomeTrend:'每日收入',transfersTrend:'每日转账',cashTrend:'每日资金变动',breakdown:'消费分类',sources:'收入分类',transferBreakdown:'转账分类',cashBreakdown:'资金构成',transactions:'交易明细',allTransactions:'本视图全部交易',summaries:'各期一览',explanations:'统计口径与资料说明',refunds:'退款',matched:'已匹配全额退款',settled:'已确认抵消',internal:'内部调拨',empty:'本期没有交易。',noChart:'本期没有资金变动。',date:'日期',description:'交易说明',category:'分类',account:'账户',bankAmount:'银行金额',personalAmount:'本人消费',adjusted:'调整后金额',source:'来源',count:'笔交易',close:'关闭交易明细',details:'查看交易明细',days:'个覆盖日',dayLabel:'天',range:'覆盖日期',clickChart:'选择柱形查看当天交易',retained:'原始银行流水完整保留。',refundNote:'已核对的全额退货从消费中抵消，跨期也回到购买时处理。其余退款单独列示。',explanation:'消费按已确认的个人比例计算，排除已匹配全额退款的购买。资金总览按银行入账日统计，排除内部调拨，并应用已确认的转账抵消。未知转入不计收入。金额均使用报表币种。',averageTip:'本期日常消费除以资料覆盖的自然日数。',dailyTip:'日常组的本人消费。固定服务、AI、租房及其他组分别统计。',totalTip:'所有消费组按确认比例计算的本人支出，排除已匹配全额退款的购买。',fixedTip:'已归类为固定服务的费用，不含 AI 及租房。',aiTip:'仅包含明确归入 AI 服务的支出。',housingTip:'按已确认个人分摊比例计算的租房支出。',cashTip:'按银行日期计算、应用已确认转账抵消后的对外资金变动，不含内部调拨。',incomeTip:'只统计归类为收入的款项，转入另计。',transferTip:'应用已确认抵消后的对外转账，原始银行金额仍可查看。',local:'独立本地报表 · 无需联网',error:'报表无法打开',errorBody:'请按 references/schema.md 核对日期、金额正负、唯一 ID、覆盖期和配对关系，再重新运行命令。',unpaired:'未配对退款',refundType:'退款状态',zero:'暂无数据',periodTotal:'合计',amount:'金额',notes:'资料说明',uncategorized:'未分类'}
  };
  Object.assign(words.en, {title:'Personal finance statistics',expenses:'Spending',daily:'Everyday spending',dailyAverage:'Daily living cost',fixed:'Fixed spending',ai:'AI spending',housing:'Housing',netSpending:'Net spending',average:'Per day',merchantBreakdown:'Merchant breakdown',scope:'Breakdown',allMonths:'All months',periodSummary:'Period amounts',explanations:'Notes',salary:'Salary',support:'Living allowance',otherIncome:'Other income',outgoing:'Outgoing transfers',incoming:'Incoming transfers',netOut:'Net transferred out',repaid:'Confirmed repayments',outstanding:'Confirmed loans outstanding',settlements:'Confirmed settlements',internalRows:'Internal account movements',needsReview:'Needs review',share:'Personal share',beforeShare:'Before sharing',search:'Search transactions',viewAll:'View all transactions',chartMenu:'Chart options',theme:'Switch color theme',zeroSpending:'No spending in this period',zeroIncome:'No income in this period',zeroTransfers:'No transfers in this period',dailyTrend:'Everyday spending by day',monthlyTrend:'Everyday spending by month',view:'Report view',asOf:'As of',all:'All',close:'Close',group:'Group'});
  Object.assign(words.zh, {title:'个人财务统计',expenses:'支出',daily:'日常支出',dailyAverage:'日均生活费',fixed:'固定支出',ai:'AI 支出',housing:'租房',netSpending:'净支出',average:'平均每天',merchantBreakdown:'商户细分',scope:'细分范围',allMonths:'全部月份一览',periodSummary:'本期金额汇总',allTransactions:'本期消费明细',explanations:'说明',salary:'工资收入',support:'生活费汇入',otherIncome:'其他收入',outgoing:'对外转出',incoming:'对外转入',netOut:'净转出',repaid:'已核对归还',outstanding:'已确认借款未还',settlements:'已确认借还配对',internalRows:'本人账户内部调拨',needsReview:'待核对往来',share:'本人比例',beforeShare:'分摊前净额',search:'搜索交易',viewAll:'查看全部明细',chartMenu:'图表选项',theme:'切换明暗主题',zeroSpending:'本期暂无支出',zeroIncome:'本期暂无收入',zeroTransfers:'本期暂无转账',dailyTrend:'每天的日常生活费',monthlyTrend:'每月的日常生活费',view:'统计内容',asOf:'截至',all:'全部',close:'关闭',group:'范围',day:'按天',week:'按周',month:'按月',year:'按年',previous:'上一期',next:'下一期'});
  const colors=['#3E7DA3','#C59A3B','#6F9377','#AA6F88','#BB784A','#87919B','#7EA7C0','#8DA98F'];
  const groupColors={daily:colors[0],fixed:colors[1],ai:colors[2],housing:colors[3],education:colors[4],equipment:colors[5],other:colors[6]};
  const categoryColors={Groceries:colors[0],Dining:colors[1],Shopping:colors[3],Transport:colors[2],Rent:colors[0],Internet:colors[2],Utilities:colors[1],Music:colors[3],Software:colors[5],Other:colors[4],Uncategorized:colors[5],Salary:colors[0],Freelance:colors[2]};
  let data, language=window.REPORT_DATA?.language?.startsWith('zh')?'zh':'en', view='expenses', grain='month', periodKey, detailGroup='daily', currentPeriod, currentSummary;
  const t=k=>words[language][k]||k;
  const e=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=String(text);return n;};
  const btn=(text,cls,fn)=>{const n=e('button',cls,text);n.type='button';n.addEventListener('click',fn);return n;};
  const locale=()=>language==='zh'?'zh-CN':'en';
  const money=v=>new Intl.NumberFormat(locale(),{style:'currency',currency:data.currency,maximumFractionDigits:2}).format((Math.abs(v)<1e-8?0:v)/100);
  const sum=(rows,f)=>rows.reduce((a,r)=>a+(typeof f==='function'?f(r):r[f]||0),0);
  const categoryName=value=>data.demo&&language==='zh'?({Groceries:'超市食品',Dining:'餐饮饮品',Shopping:'购物衣物',Transport:'交通出行',Rent:'房租',Internet:'宽带',Utilities:'水电账单',Music:'影音服务',Software:'软件服务','AI tools':'AI 服务',Study:'学费',Salary:'工资收入',Freelance:'兼职收入','Living allowance':'生活费汇入',Loan:'借款','Loan repayment':'借款归还','Needs review':'待核对',Other:'其他日常',Uncategorized:'商户待分类'}[value]||value):value;
  const periodLabel=p=>{
    let label=grain==='year'?p.key.slice(0,4)+(language==='zh'?'年':''):grain==='month'?new Intl.DateTimeFormat(locale(),{year:'numeric',month:'long'}).format(new Date(p.start+'T12:00:00')):grain==='week'?p.start+' – '+p.end:p.start;
    if(grain==='month'||grain==='year'){
      const d=new Date(p.key+'T00:00:00Z');
      const naturalEnd=grain==='year'?p.key.slice(0,4)+'-12-31':new Date(Date.UTC(d.getUTCFullYear(),d.getUTCMonth()+1,0)).toISOString().slice(0,10);
      if(p.end<naturalEnd)label+=language==='zh'?'（截至'+Number(p.end.slice(5,7))+'/'+Number(p.end.slice(8))+'）':' (through '+p.end+')';
    }
    return label;
  };
  const svg=(tag,attrs={})=>{const n=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,String(v));return n;};
  function select(label,values,value,onChange,cls=''){
    const s=e('select',cls);s.setAttribute('aria-label',label);for(const [v,l]of values){const o=e('option','',l);o.value=v;o.selected=v===value;s.append(o);}s.addEventListener('change',()=>onChange(s.value));return s;
  }
  function hint(text){const wrap=e('span','hint');const b=btn('i','info',()=>{});b.setAttribute('aria-label',text);const tip=e('span','tooltip',text);tip.setAttribute('role','tooltip');wrap.append(b,tip);return wrap;}
  const chartTip=e('div','chart-tooltip');
  chartTip.id='chart-tooltip';chartTip.hidden=true;chartTip.setAttribute('role','tooltip');document.body.append(chartTip);
  let tipOwner=null;
  function hideChartTip(){chartTip.hidden=true;tipOwner?.removeAttribute('aria-describedby');tipOwner=null;}
  function placeChartTip(x,y){
    const box=chartTip.getBoundingClientRect();
    const left=Math.max(8,Math.min(x+14,innerWidth-box.width-8));
    const top=y+14+box.height>innerHeight-8?Math.max(8,y-box.height-14):y+14;
    chartTip.style.left=left+'px';chartTip.style.top=top+'px';
  }
  function chartTooltip(target,lines){
    const show=event=>{
      if(event?.pointerType==='touch')return;
      hideChartTip();tipOwner=target;
      chartTip.replaceChildren(...lines.map((line,i)=>e(i?'span':'strong','',line)));
      chartTip.hidden=false;target.setAttribute('aria-describedby',chartTip.id);
      const box=target.getBoundingClientRect();placeChartTip(event?.clientX??box.x+box.width/2,event?.clientY??box.y);
    };
    target.addEventListener('pointerenter',show);
    target.addEventListener('pointermove',event=>{if(tipOwner===target)placeChartTip(event.clientX,event.clientY);});
    target.addEventListener('pointerleave',()=>{if(tipOwner===target)hideChartTip();});
    target.addEventListener('focus',()=>show());
    target.addEventListener('blur',()=>{if(tipOwner===target)hideChartTip();});
  }
  document.addEventListener('keydown',event=>{if(event.key==='Escape')hideChartTip();});
  document.addEventListener('scroll',hideChartTip,true);window.addEventListener('resize',hideChartTip);
  function bucket(rows,field,measure,colorMap={}){
    const map=new Map();for(const r of rows){const key=typeof field==='function'?field(r):r[field]||t('uncategorized');if(!map.has(key))map.set(key,[]);map.get(key).push(r);}
    return [...map].map(([key,items],i)=>({key,label:categoryName(key),rows:items,value:sum(items,measure),color:colorMap[key]||colors[i%colors.length]})).filter(x=>x.value!==0).sort((a,b)=>b.value-a.value);
  }
  function transactionTable(rows,mode='expenses'){
    const area=e('div','table-area');const table=e('table','data-table');const headers=['date','description','category','account','bankAmount'];
    if(mode==='expenses')headers.push('share','personalAmount');else headers.push('adjusted');
    const hr=e('tr');headers.forEach(k=>{const th=e('th','',t(k));th.scope='col';hr.append(th);});const head=e('thead');head.append(hr);table.append(head);const body=e('tbody');
    for(const row of [...rows].sort((a,b)=>a.date.localeCompare(b.date)||a.id.localeCompare(b.id))){const tr=e('tr');tr.append(e('td','nowrap',row.date));const description=e('td','description',row.merchant||row.description);if(row.merchant&&row.description!==row.merchant)description.append(e('small','',row.description));if(row.source)description.append(e('small','',t('source')+': '+row.source));if(row.matchedRefund)description.append(e('small','',t('matched')));if(row.settledCents)description.append(e('small','',t('settled')+': '+money(row.settledCents)));tr.append(description,e('td','',categoryName(row.category)),e('td','',row.account),e('td','amount',money(row.amountCents)));if(mode==='expenses')tr.append(e('td','amount',String(row.share*100)+'%'),e('td','amount',money(row.personalCents)));else tr.append(e('td','amount',money(mode==='transfers'?row.transferCents:row.cashCents)));body.append(tr);}
    table.append(body);area.append(table);if(!rows.length)area.append(e('p','empty',t('empty')));return area;
  }
  function openRows(title,rows,mode=view,average=false){
    hideChartTip();
    document.getElementById('dialog-title').textContent=title;
    const measure=mode==='expenses'?'personalCents':mode==='income'?'amountCents':mode==='transfers'?'transferCents':'cashCents';
    const total=sum(rows,measure);
    document.getElementById('dialog-subtitle').textContent=periodLabel(currentPeriod)+' · '+rows.length+' '+t('count')+' · '+money(total)+(average?' · '+t('average')+' '+money(total/currentSummary.days):'');
    const content=document.getElementById('dialog-content');const search=e('input','search');search.type='search';search.placeholder=t('search');search.setAttribute('aria-label',t('search'));const results=e('div');results.append(transactionTable(rows,mode));search.addEventListener('input',()=>{const q=search.value.toLocaleLowerCase();results.replaceChildren(transactionTable(rows.filter(r=>[r.date,r.description,r.merchant,r.category,r.account].join(' ').toLocaleLowerCase().includes(q)),mode));});content.replaceChildren(search,results);document.getElementById('dialog-close').setAttribute('aria-label',t('close'));dialog.showModal();
  }
  function chartHeader(title,tip,rows,mode=view){const header=e('div','card-heading');const heading=e('div','card-title');heading.append(e('h2','',title),hint(tip));const menu=e('details','chart-menu');const trigger=e('summary','','···');trigger.setAttribute('aria-label',t('chartMenu')+' '+title);const action=btn(t('viewAll'),'menu-action',()=>{menu.open=false;openRows(title,rows,mode);});menu.append(trigger,action);header.append(heading,menu);return header;}
  function updateLegendFade(legend){
    const remaining=legend.scrollHeight-legend.clientHeight-legend.scrollTop;
    legend.style.setProperty('--fade-top',Math.min(24,Math.max(0,legend.scrollTop))+'px');
    legend.style.setProperty('--fade-bottom',remaining>1?Math.min(24,remaining)+'px':'0px');
  }
  function ring(title,items,opts={}){
    const rows=items.flatMap(x=>x.rows);const divisor=opts.average?currentSummary.days:1;
    const list=items.map(x=>({...x,value:x.value/divisor}));const total=sum(list,'value');const card=e('section','ring-card '+(opts.size||'secondary'));
    card.append(chartHeader(title,opts.tip||t('totalTip'),rows,opts.mode));
    const plot=e('div','ring-plot');const center=e('div','ring-center');center.append(e('strong','',money(total)),e('span','',opts.average?t('average'):opts.label||t('netSpending')));
    const positive=list.filter(x=>x.value>0),positiveTotal=sum(positive,'value');
    if(positiveTotal){const drawing=svg('svg',{viewBox:'0 0 300 300','aria-label':title,role:'img'});let angle=0;
      for(const item of positive){const sweep=item.value/positiveTotal*Math.PI*2;const start=angle,end=angle+sweep;const segment=svg('circle',{cx:150,cy:150,r:100,fill:'none',stroke:item.color,'stroke-width':40,'stroke-dasharray':`${Math.max(0,sweep*100-(positive.length>1?Math.min(2.6,sweep*25):0))} ${Math.PI*200}`,'stroke-dashoffset':-start*100,transform:'translate(0 300) scale(1 -1)',tabindex:0,role:'button','aria-label':item.label+' '+money(item.value)});const percentage=new Intl.NumberFormat(locale(),{style:'percent',maximumFractionDigits:2}).format(item.value/positiveTotal);const shareText=(language==='zh'?'占本圆环 ':'Share of this ring: ')+percentage;segment.setAttribute('aria-label',item.label+' '+money(item.value)+' · '+shareText);chartTooltip(segment,[item.label,money(item.value)+(opts.average?' / '+t('dayLabel'):''),shareText,item.rows.length+' '+t('count')]);const open=()=>openRows(item.label,item.rows,opts.mode||view,opts.average);segment.addEventListener('click',open);segment.addEventListener('keydown',ev=>{if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();open();}});drawing.append(segment);angle=end;}
      plot.append(drawing,center);
    }else {plot.classList.add('empty-ring');plot.append(center,e('span','empty-caption',t(opts.mode==='income'?'zeroIncome':opts.mode==='transfers'?'zeroTransfers':'zeroSpending')));}
    card.append(plot);const legend=e('div','ring-legend');for(const item of list){const row=btn('','legend-row',()=>openRows(item.label,item.rows,opts.mode||view,opts.average));row.title=item.label;const label=e('span','legend-label');const dot=e('i');dot.style.background=item.color;label.append(dot,e('span','',item.label));row.append(label,e('strong','',money(item.value)));legend.append(row);}legend.addEventListener('scroll',()=>updateLegendFade(legend),{passive:true});card.append(legend);requestAnimationFrame(()=>{if(legend.isConnected)updateLegendFade(legend);});return card;
  }
  function metric(title,value,rows,tip,mode=view){const box=e('section','metric-card');const head=e('div','card-title');head.append(e('h2','',title),hint(tip));box.append(head,btn(money(value),'metric-number',()=>openRows(title,rows,mode)));return box;}
  function fold(title,content){const box=e('details','fold');box.append(e('summary','',title));const body=e('div','fold-body');body.append(content);box.append(body);return box;}
  function timeline(rows,mode){
    const title=mode==='expenses'?t(grain==='year'?'monthlyTrend':'dailyTrend'):t(mode==='income'?'incomeTrend':'transfersTrend');
    const card=e('section','timeline-card');card.append(chartHeader(title,t(mode==='expenses'?'dailyTip':mode==='income'?'incomeTip':'transferTip'),rows,mode));
    const map=new Map(),cursor=new Date(currentPeriod.start+'T00:00:00Z'),end=new Date(currentPeriod.end+'T00:00:00Z');
    while(cursor<=end){const day=cursor.toISOString().slice(0,10);map.set(grain==='year'?day.slice(0,7):day,[]);cursor.setUTCDate(cursor.getUTCDate()+1);}
    for(const row of rows){const key=grain==='year'?row.date.slice(0,7):row.date;map.get(key)?.push(row);}
    const points=[...map].map(([key,rs])=>({key,rows:rs,a:sum(rs,r=>mode==='expenses'?r.personalCents:mode==='income'?r.amountCents:Math.max(0,-r.transferCents)),b:mode==='transfers'?sum(rs,r=>Math.max(0,r.transferCents)):0}));
    const max=Math.max(1,...points.flatMap(p=>[p.a,p.b]));
    const number=value=>new Intl.NumberFormat(locale(),{minimumFractionDigits:2,maximumFractionDigits:2}).format(value/100);
    const labelWidth=Math.max(52,...points.flatMap(p=>[p.a,p.b]).map(value=>number(value).length*7+12));
    const chart=e('div','bar-chart'),axis=e('div','y-axis');[1,.75,.5,.25,0].forEach(v=>axis.append(e('span','',money(max*v))));
    const scroll=e('div','bar-scroll');scroll.tabIndex=0;scroll.setAttribute('role','region');scroll.setAttribute('aria-label',title);
    const plot=e('div','bar-plot');plot.style.minWidth=points.length*(labelWidth*(mode==='transfers'?2:1)+6)+'px';
    const lines=e('div','grid-lines');for(let i=0;i<5;i++)lines.append(e('i'));plot.append(lines);
    const bars=e('div','bars');points.forEach(point=>{
      const group=e('div','bar-group');
      for(const [key,color]of [['a',mode==='income'?colors[2]:mode==='transfers'?colors[4]:colors[0]],...(mode==='transfers'?[['b',colors[0]]]:[])]){
        const selected=mode==='transfers'?point.rows.filter(r=>key==='a'?r.transferCents<0:r.transferCents>0):point.rows;
        const series=t(mode==='expenses'?'daily':mode==='income'?'income':key==='a'?'transferOut':'transferIn');
        const bar=btn('','bar',()=>openRows(point.key+' · '+series,selected,mode));bar.style.height=(point[key]/max*100)+'%';bar.style.background=color;
        bar.setAttribute('aria-label',point.key+' · '+series+' · '+money(point[key]));bar.disabled=!point[key];
        if(point[key]){const label=e('span','bar-value',number(point[key]));label.setAttribute('aria-hidden','true');bar.append(label);chartTooltip(bar,[point.key,series+' · '+money(point[key]),selected.length+' '+t('count')]);}
        group.append(bar);
      }
      group.append(e('span','bar-date',point.key.slice(5)));bars.append(group);
    });
    plot.append(bars);scroll.append(plot);chart.append(axis,scroll);card.append(chart);return card;
  }
  function amountSummary(summary){const wrap=e('div','table-area'),table=e('table','data-table'),head=e('tr');[t('group'),t('netSpending')].forEach(x=>head.append(e('th','',x)));table.append(head);Object.entries(summary.groups).forEach(([g,v])=>{const row=e('tr');row.append(e('td','',t(g)),e('td','amount',money(v)));table.append(row);});wrap.append(table);return wrap;}
  function monthSummary(){const wrap=e('div','table-area'),table=e('table','data-table'),head=e('tr');[t('month'),t('daily'),t('fixed'),t('ai'),t('housing'),t('total')].forEach(x=>head.append(e('th','',x)));table.append(head);for(const p of Finance.periods(data,'month')){const s=Finance.summarize(data,p),row=e('tr'),cell=e('td');cell.append(btn(p.key.slice(0,7),'text-button',()=>{grain='month';periodKey=p.key;render();}));row.append(cell);[s.daily,s.groups.fixed,s.groups.ai,s.groups.housing,s.spending].forEach(x=>row.append(e('td','amount',money(x))));table.append(row);}wrap.append(table);return wrap;}
  function notes(){const content=e('div','notes');for(const [heading,body]of [[t('dailyAverage'),t('averageTip')+' '+currentSummary.days+' '+t('days')],[t('netSpending'),t('explanation')],[t('refunds'),t('refundNote')],[t('transfers'),t('transferTip')]]){const section=e('section');section.append(e('h3','',heading),e('p','',body));content.append(section);}for(const note of data.notes)content.append(e('p','',note));return fold(t('explanations'),content);}
  function render(){
    hideChartTip();
    const focused=document.activeElement?.getAttribute('aria-label');const periods=Finance.periods(data,grain);let index=periods.findIndex(p=>p.key===periodKey);if(index<0)index=periods.length-1;currentPeriod=periods[index];periodKey=currentPeriod.key;currentSummary=Finance.summarize(data,currentPeriod);const s=currentSummary,rows=s.rows,spending=rows.filter(r=>r.kind==='expense'&&!r.matchedRefund),daily=spending.filter(r=>r.group==='daily');
    document.documentElement.lang=locale();document.title=t('title');root.replaceChildren();
    const top=e('header','topbar');const left=e('div','topbar-title');left.append(e('span','',t('title')),e('span','as-of',t('asOf')+' '+data.coverage.end));const right=e('div','topbar-actions');if(data.demo)right.append(e('span','demo-badge',t('demo')));right.append(btn('◐','theme-toggle',()=>{document.documentElement.classList.toggle('light');}),select(t('language'),[['en','English'],['zh','简体中文']],language,v=>{language=v;render();},'language'));right.querySelector('button').setAttribute('aria-label',t('theme'));top.append(left,right);root.append(top);
    const page=e('article','finance-page');const heading=e('header','finance-heading');heading.append(e('h1','',t('title')));const views=e('div','segments view-segments');views.setAttribute('role','group');views.setAttribute('aria-label',t('view'));for(const key of ['overview','expenses','income','transfers']){const b=btn(t(key),'',()=>{view=key;render();});b.setAttribute('aria-pressed',String(view===key));b.setAttribute('aria-label',t(key));views.append(b);}heading.append(views);page.append(heading);
    const controls=e('div','period-header');controls.append(e('h2','period-title',periodLabel(currentPeriod)));const tools=e('div','period-tools');const grains=e('div','segments');for(const g of ['day','week','month','year']){const b=btn(t(g),'',()=>{const date=currentPeriod.end;grain=g;periodKey=Finance.periods(data,g).find(p=>p.start<=date&&p.end>=date)?.key;render();});b.setAttribute('aria-pressed',String(g===grain));grains.append(b);}tools.append(grains);const previous=btn(t('previous'),'period-button',()=>{periodKey=periods[index-1].key;render();});previous.disabled=index===0;const next=btn(t('next'),'period-button',()=>{periodKey=periods[index+1].key;render();});next.disabled=index===periods.length-1;tools.append(previous,select(t('period'),periods.map(p=>[p.key,periodLabel(p)]),periodKey,v=>{periodKey=v;render();},'period-select'),next);controls.append(tools);page.append(controls);
    if(view==='expenses'){
      const total=bucket(spending,r=>r.group,'personalCents',groupColors).map(x=>({...x,label:t(x.key)}));const daySlices=bucket(daily,'category','personalCents',categoryColors);const primary=e('div','ring-grid three');primary.append(ring(t('total'),total,{size:'primary'}),ring(t('daily'),daySlices,{size:'primary',tip:t('dailyTip')}),ring(t('dailyAverage'),daySlices,{size:'primary',average:true,tip:t('averageTip')}));page.append(primary);
      const secondary=e('div','ring-grid three');for(const g of ['fixed','ai','housing'])secondary.append(ring(t(g),bucket(spending.filter(r=>r.group===g),'category','personalCents',categoryColors),{tip:t(g+'Tip')}));page.append(secondary);
      const merchantHeader=e('div','section-header');merchantHeader.append(e('h2','',t('merchantBreakdown')));const scopes=e('div','segments');for(const g of ['daily','fixed','ai','housing']){const b=btn(t(g),'',()=>{detailGroup=g;render();});b.setAttribute('aria-pressed',String(g===detailGroup));scopes.append(b);}merchantHeader.append(scopes);page.append(merchantHeader);const merchants=e('div','ring-grid three merchant-grid');const categories=bucket(spending.filter(r=>r.group===detailGroup),'category','personalCents',categoryColors);for(const category of categories){if(detailGroup==='daily'&&['Transport','Other','Uncategorized','Needs review','交通出行','其他日常','商户待分类'].includes(category.key))continue;merchants.append(ring(category.label,bucket(category.rows,r=>r.merchant||r.description,'personalCents'),{size:'merchant'}));}if(!merchants.children.length)merchants.append(e('p','empty',t('zeroSpending')));page.append(merchants);
      if(grain!=='day')page.append(timeline(daily,'expenses'));page.append(fold(t('periodSummary'),amountSummary(s)),fold(t('allTransactions'),transactionTable(spending)),fold(t('allMonths'),monthSummary()));const refundRows=rows.filter(r=>r.kind==='refund'||r.matchedRefund);page.append(fold(t('refunds'),transactionTable(refundRows,'overview')));
    }else if(view==='overview'){
      const grid=e('div','metric-grid');grid.append(metric(t('inflow'),s.inflow,rows.filter(r=>r.cashCents>0),t('cashTip')),metric(t('outflow'),s.outflow,rows.filter(r=>r.cashCents<0),t('cashTip')),metric(t('net'),s.net,rows.filter(r=>r.kind!=='internal'),t('cashTip')));page.append(grid);
    }else if(view==='income'){
      const income=rows.filter(r=>r.kind==='income');const slices=bucket(income,'category','amountCents',categoryColors);const primary=e('div','ring-grid two');primary.append(ring(t('incomeTotal'),slices,{size:'primary',mode:'income',label:t('income'),tip:t('incomeTip')}),ring(t('incomeAverage'),slices,{size:'primary',mode:'income',average:true,tip:t('incomeTip')}));page.append(primary);const secondary=e('div','ring-grid three');for(const type of ['salary','support','other'])secondary.append(ring(t(type==='other'?'otherIncome':type),bucket(income.filter(r=>r.incomeType===type),r=>r.merchant||r.description,'amountCents'),{mode:'income',label:t('income'),tip:t('incomeTip')}));page.append(secondary);if(grain!=='day')page.append(timeline(income,'income'));page.append(fold(t('transactions'),transactionTable(income,'income')));
    }else{
      const transfers=rows.filter(r=>r.kind.startsWith('transfer_'));const outgoing=transfers.filter(r=>r.transferCents<0),incoming=transfers.filter(r=>r.transferCents>0);const primary=e('div','ring-grid two');primary.append(ring(t('outgoing'),bucket(outgoing,'category',r=>-r.transferCents),{size:'primary',mode:'transfers',label:t('transferOut'),tip:t('transferTip')}),ring(t('incoming'),bucket(incoming,'category','transferCents'),{size:'primary',mode:'transfers',label:t('transferIn'),tip:t('transferTip')}));page.append(primary);const loans=rows.filter(r=>r.kind==='transfer_out'&&r.purpose==='loan');const metrics=e('div','metric-grid');metrics.append(metric(t('netOut'),s.transferOut-s.transferIn,transfers,t('transferTip')),metric(t('repaid'),sum(loans,'settledCents'),loans,t('transferTip')),metric(t('outstanding'),sum(loans,r=>-r.transferCents),loans,t('transferTip')));page.append(metrics);if(grain!=='day')page.append(timeline(transfers,'transfers'));page.append(fold(t('transactions'),transactionTable(transfers,'transfers')),fold(t('settlements'),transactionTable(transfers.filter(r=>r.settledCents),'transfers')),fold(t('internalRows'),transactionTable(rows.filter(r=>r.kind==='internal'),'overview')));
    }
    page.append(notes());root.append(page);root.setAttribute('aria-busy','false');if(focused){const target=[...root.querySelectorAll('[aria-label]')].find(n=>n.getAttribute('aria-label')===focused);target?.focus({preventScroll:true});}
  }
  document.getElementById('dialog-close').addEventListener('click',()=>dialog.close());dialog.addEventListener('click',ev=>{if(ev.target===dialog){const b=dialog.getBoundingClientRect();if(ev.clientX<b.left||ev.clientX>b.right||ev.clientY<b.top||ev.clientY>b.bottom)dialog.close();}});
  try{data=Finance.validate(window.REPORT_DATA);render();}catch(err){root.replaceChildren(e('h1','error',t('error')),e('p','error',t('errorBody')));root.setAttribute('aria-busy','false');}
}());
