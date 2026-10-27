(function () {
  'use strict';
  const root = document.getElementById('report');
  const dialog = document.getElementById('transactions-dialog');
  const words = {
    en: {title:'Personal finance',subtitle:'A closer look at your money',demo:'Fictional demo data',language:'Language',overview:'Overview',expenses:'Expenses',income:'Income',transfers:'Transfers',day:'Day',week:'Week',month:'Month',year:'Year',period:'Period',previous:'Previous period',next:'Next period',covered:'Source coverage',total:'Total spending',daily:'Everyday spending',dailyAverage:'Daily average',fixed:'Fixed services',ai:'AI services',housing:'Housing',education:'Education',equipment:'Equipment',other:'Other',inflow:'Total inflow',outflow:'Total outflow',net:'Net change',transferIn:'Transfers in',transferOut:'Transfers out',transferNet:'Net transfers',incomeTotal:'Total income',incomeAverage:'Income per day',incomeCount:'Income payments',trend:'Daily spending',incomeTrend:'Daily income',transfersTrend:'Daily transfer movement',cashTrend:'Daily cash movement',breakdown:'By category',sources:'By income category',transferBreakdown:'Transfer categories',cashBreakdown:'Cash movement',transactions:'Transactions',allTransactions:'All transactions in this view',summaries:'Period summary',explanations:'How this report is calculated',refunds:'Refunds',matched:'Full refund matched',settled:'Settled transfer',internal:'Internal transfer',empty:'No transactions in this period.',noChart:'No movement in this period.',date:'Date',description:'Description',category:'Category',account:'Account',bankAmount:'Bank amount',personalAmount:'Personal spending',adjusted:'Adjusted amount',source:'Source',count:'transactions',close:'Close transaction details',details:'Open transactions',days:'covered days',dayLabel:'day',range:'Covered dates',clickChart:'Select a bar to see its transactions',retained:'Original bank transactions are retained.',refundNote:'Confirmed full returns are excluded from spending, including across periods. Other refunds are shown separately.',explanation:'Spending uses confirmed personal shares and removes matched full returns. Cash movement follows bank dates, excludes internal transfers, and uses confirmed transfer settlements. Unknown incoming payments are transfers, not income. All amounts use the report currency.',averageTip:'Everyday spending divided by covered calendar days in this period.',dailyTip:'Personal spending in the everyday group. Fixed services, AI, housing and other groups are separate.',totalTip:'All expense groups at the confirmed personal share, excluding purchases with matched full refunds.',fixedTip:'Recurring services classified as fixed; excludes AI and housing.',aiTip:'Only expenses explicitly classified as AI services.',housingTip:'Housing spending at the confirmed personal share.',cashTip:'External bank-date movement after confirmed transfer settlements; internal movements are excluded.',incomeTip:'Only payments classified as income. Incoming transfers are separate.',transferTip:'External transfers after confirmed settlements. Original bank amounts remain available.',local:'Standalone report · no network connection required',error:'The report could not be opened',errorBody:'Check dates, amount signs, unique IDs, coverage and mappings against references/schema.md, then rerun the command.',unpaired:'Unpaired refund',refundType:'Refund status',zero:'No data',periodTotal:'Total',amount:'Amount',notes:'Source notes',uncategorized:'Uncategorized'},
    zh: {title:'个人财务',subtitle:'看清每一段时间的收支',demo:'虚构演示数据',language:'语言',overview:'收支总览',expenses:'消费',income:'收入',transfers:'转账',day:'天',week:'周',month:'月',year:'年',period:'期间',previous:'上一期',next:'下一期',covered:'资料覆盖',total:'总花费',daily:'日常消费',dailyAverage:'日均日常消费',fixed:'固定服务',ai:'AI 服务',housing:'租房',education:'教育',equipment:'数码设备',other:'其他',inflow:'总流入',outflow:'总流出',net:'净增减',transferIn:'转入',transferOut:'转出',transferNet:'转账净额',incomeTotal:'总收入',incomeAverage:'日均收入',incomeCount:'收入笔数',trend:'每日消费',incomeTrend:'每日收入',transfersTrend:'每日转账',cashTrend:'每日资金变动',breakdown:'消费分类',sources:'收入分类',transferBreakdown:'转账分类',cashBreakdown:'资金构成',transactions:'交易明细',allTransactions:'本视图全部交易',summaries:'各期一览',explanations:'统计口径与资料说明',refunds:'退款',matched:'已匹配全额退款',settled:'已确认抵消',internal:'内部调拨',empty:'本期没有交易。',noChart:'本期没有资金变动。',date:'日期',description:'交易说明',category:'分类',account:'账户',bankAmount:'银行金额',personalAmount:'本人消费',adjusted:'调整后金额',source:'来源',count:'笔交易',close:'关闭交易明细',details:'查看交易明细',days:'个覆盖日',dayLabel:'天',range:'覆盖日期',clickChart:'选择柱形查看当天交易',retained:'原始银行流水完整保留。',refundNote:'已核对的全额退货从消费中抵消，跨期也回到购买时处理。其余退款单独列示。',explanation:'消费按已确认的个人比例计算，排除已匹配全额退款的购买。资金总览按银行入账日统计，排除内部调拨，并应用已确认的转账抵消。未知转入不计收入。金额均使用报表币种。',averageTip:'本期日常消费除以资料覆盖的自然日数。',dailyTip:'日常组的本人消费。固定服务、AI、租房及其他组分别统计。',totalTip:'所有消费组按确认比例计算的本人支出，排除已匹配全额退款的购买。',fixedTip:'已归类为固定服务的费用，不含 AI 及租房。',aiTip:'仅包含明确归入 AI 服务的支出。',housingTip:'按已确认个人分摊比例计算的租房支出。',cashTip:'按银行日期计算、应用已确认转账抵消后的对外资金变动，不含内部调拨。',incomeTip:'只统计归类为收入的款项，转入另计。',transferTip:'应用已确认抵消后的对外转账，原始银行金额仍可查看。',local:'独立本地报表 · 无需联网',error:'报表无法打开',errorBody:'请按 references/schema.md 核对日期、金额正负、唯一 ID、覆盖期和配对关系，再重新运行命令。',unpaired:'未配对退款',refundType:'退款状态',zero:'暂无数据',periodTotal:'合计',amount:'金额',notes:'资料说明',uncategorized:'未分类'}
  };
  Object.assign(words.en,{budget:'Daily allowance'});Object.assign(words.zh,{budget:'每日可花'});
  Object.assign(words.en, {title:'Personal finance statistics',expenses:'Spending',daily:'Everyday spending',dailyAverage:'Daily living cost',fixed:'Fixed spending',ai:'AI spending',housing:'Housing',netSpending:'Net spending',average:'Per day',merchantBreakdown:'Merchant breakdown',scope:'Breakdown',allMonths:'All months',periodSummary:'Period amounts',explanations:'Notes',salary:'Salary',support:'Living allowance',otherIncome:'Other income',outgoing:'Outgoing transfers',incoming:'Incoming transfers',netOut:'Net transferred out',repaid:'Confirmed repayments',outstanding:'Confirmed loans outstanding',settlements:'Confirmed settlements',internalRows:'Internal account movements',needsReview:'Needs review',share:'Personal share',beforeShare:'Before sharing',search:'Search transactions',viewAll:'View all transactions',chartMenu:'Chart options',theme:'Switch color theme',zeroSpending:'No spending in this period',zeroIncome:'No income in this period',zeroTransfers:'No transfers in this period',dailyTrend:'Everyday spending by day',monthlyTrend:'Everyday spending by month',view:'Report view',asOf:'As of',all:'All',close:'Close',group:'Group'});
  Object.assign(words.zh, {title:'个人财务统计',expenses:'支出',daily:'日常支出',dailyAverage:'日均生活费',fixed:'固定支出',ai:'AI 支出',housing:'租房',netSpending:'净支出',average:'平均每天',merchantBreakdown:'商户细分',scope:'细分范围',allMonths:'全部月份一览',periodSummary:'本期金额汇总',allTransactions:'本期消费明细',explanations:'说明',salary:'工资收入',support:'生活费汇入',otherIncome:'其他收入',outgoing:'对外转出',incoming:'对外转入',netOut:'净转出',repaid:'已核对归还',outstanding:'已确认借款未还',settlements:'已确认借还配对',internalRows:'本人账户内部调拨',needsReview:'待核对往来',share:'本人比例',beforeShare:'分摊前净额',search:'搜索交易',viewAll:'查看全部明细',chartMenu:'图表选项',theme:'切换明暗主题',zeroSpending:'本期暂无支出',zeroIncome:'本期暂无收入',zeroTransfers:'本期暂无转账',dailyTrend:'每天的日常生活费',monthlyTrend:'每月的日常生活费',view:'统计内容',asOf:'截至',all:'全部',close:'关闭',group:'范围',day:'按天',week:'按周',month:'按月',year:'按年',previous:'上一期',next:'下一期'});
  Object.assign(words.en,{allCategories:'All categories',allAccounts:'All accounts',resetDetails:'Reset',closeSearch:'Close search',amountOrderNote:'Amounts are sorted by absolute value; original signs are retained.',matching:'Matching',filteredTotal:'Filtered total',originalScope:'Original scope',unspecified:'Unspecified'});
  Object.assign(words.zh,{allCategories:'全部分类',allAccounts:'全部账户',resetDetails:'重置',closeSearch:'收起搜索',amountOrderNote:'金额按绝对值排序，原有正负号保留。',matching:'匹配',filteredTotal:'筛选合计',originalScope:'原始范围',unspecified:'未指定'});
  let detailSequence=0;
  const colors=['#3E7DA3','#C59A3B','#6F9377','#AA6F88','#BB784A','#87919B','#7EA7C0','#8DA98F'];
  const groupColors={daily:colors[0],fixed:colors[1],ai:colors[2],housing:colors[3],education:colors[4],equipment:colors[5],other:colors[6]};
  const categoryColors={Groceries:colors[0],Dining:colors[1],Shopping:colors[3],Transport:colors[2],Rent:colors[0],Internet:colors[2],Utilities:colors[1],Music:colors[3],Software:colors[5],Other:colors[4],Uncategorized:colors[5],Salary:colors[0],Freelance:colors[2]};
  let data, language=window.REPORT_DATA?.language?.startsWith('zh')?'zh':'en', view=window.REPORT_DATA?.budget&&location.hash==='#budget'?'budget':'expenses', grain='month', periodKey, currentPeriod, currentSummary;
  const t=k=>words[language][k]||k;
  const e=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=String(text);return n;};
  const btn=(text,cls,fn)=>{const n=e('button',cls,text);n.type='button';n.addEventListener('click',fn);return n;};
  const locale=()=>language==='zh'?'zh-CN':'en';
  const moneyFormats=new Map();
  const money=v=>{const key=locale()+':'+data.currency;if(!moneyFormats.has(key))moneyFormats.set(key,new Intl.NumberFormat(locale(),{style:'currency',currency:data.currency,maximumFractionDigits:2}));return moneyFormats.get(key).format((Math.abs(v)<1e-8?0:v)/100);};
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
  function hint(text){const wrap=e('span','hint');const b=btn('i','info',()=>b.focus());b.setAttribute('aria-label',text);chartTooltip(b,[text]);wrap.append(b);return wrap;}
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
  const displayNames=window.REPORT_DATA?.merchantDisplayNames;
  const merchantName=raw=>displayNames&&typeof displayNames==='object'&&Object.hasOwn(displayNames,raw)&&typeof displayNames[raw]==='string'&&displayNames[raw].trim()&&displayNames[raw].length<=80?displayNames[raw].trim():raw;
  function bucket(rows,field,measure,colorMap={}){
    const map=new Map();for(const r of rows){const key=typeof field==='function'?field(r):r[field]||t('uncategorized');if(!map.has(key))map.set(key,[]);map.get(key).push(r);}
    return [...map].map(([key,items],i)=>({key,label:typeof field==='function'?merchantName(key):categoryName(key),fullLabel:key,rows:items,value:sum(items,measure),color:colorMap[key]||colors[i%colors.length]})).filter(x=>x.value!==0).sort((a,b)=>b.value-a.value);
  }
  function transactionTable(rows,mode='expenses'){
    const wrap=e('div','transaction-explorer'),toolbar=e('div','detail-toolbar');
    const area=e('div','table-area'),table=e('table','data-table'),head=e('thead'),body=e('tbody');
    const state={query:'',category:null,account:null,sort:'date',direction:1};
    const collator=new Intl.Collator(locale(),{numeric:true,sensitivity:'base'});
    const valueKey=mode==='expenses'?'personalCents':mode==='income'?'amountCents':mode==='transfers'?'transferCents':'cashCents';
    const valueLabel=mode==='expenses'?'personalAmount':mode==='income'?'bankAmount':'adjusted';
    const secondary=mode==='expenses'?'personalAmount':'adjusted';
    const searchBox=e('div','detail-search');
    const search=e('input','detail-search-input');search.type='search';search.placeholder=t('search');search.setAttribute('aria-label',t('search'));search.dataset.filter='search';search.id='detail-search-'+(++detailSequence);search.disabled=true;
    const toggle=btn('','detail-icon search-toggle',()=>{searchBox.classList.add('is-open');toggle.setAttribute('aria-expanded','true');search.disabled=false;requestAnimationFrame(()=>search.focus());});toggle.setAttribute('aria-label',t('search'));toggle.setAttribute('aria-expanded','false');toggle.setAttribute('aria-controls',search.id);toggle.title=t('search');
    const searchIcon=svg('svg',{viewBox:'0 0 24 24',width:18,height:18,fill:'none',stroke:'currentColor','stroke-width':1.7,'aria-hidden':true});searchIcon.append(svg('circle',{cx:10.5,cy:10.5,r:6.5}),svg('path',{d:'M16 16l4.5 4.5','stroke-linecap':'round'}));toggle.append(searchIcon);
    function closeSearch(focus=false){search.value='';state.query='';search.disabled=true;searchBox.classList.remove('is-open');toggle.setAttribute('aria-expanded','false');if(focus)toggle.focus();draw();}
    const close=btn('×','detail-icon search-close',()=>closeSearch(true));close.setAttribute('aria-label',t('closeSearch'));close.title=t('closeSearch');
    search.addEventListener('input',()=>{state.query=search.value.trim().toLocaleLowerCase();draw();});
    search.addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();event.stopPropagation();closeSearch(true);}});
    searchBox.append(toggle,search,close);
    const filterSelect=key=>{const values=[...new Set(rows.map(r=>r[key]))].sort((a,b)=>collator.compare(key==='category'?categoryName(a):a,key==='category'?categoryName(b):b));const control=select(t(key),[['',t(key==='category'?'allCategories':'allAccounts')],...values.map((v,i)=>[String(i),(key==='category'?categoryName(v):v)||t('unspecified')])],'',v=>{state[key]=v===''?null:values[Number(v)];draw();});control.dataset.filter=key;return control;};
    const category=filterSelect('category'),account=filterSelect('account');
    const sortKeys=['date','category','account','bankAmount',secondary];
    const reset=btn('↺','detail-icon',()=>{Object.assign(state,{query:'',category:null,account:null,sort:'date',direction:1});category.value=account.value='';closeSearch();});reset.dataset.reset='details';reset.setAttribute('aria-label',t('resetDetails'));reset.title=t('resetDetails');
    const status=e('span','detail-status');status.setAttribute('role','status');toolbar.append(searchBox,category,account,reset,status);
    const empty=e('p','empty',t('empty')),hr=e('tr'),headers=['date','description','category','account','bankAmount',...(mode==='expenses'?['share','personalAmount']:['adjusted'])],headerControls=[];
    for(const key of headers){const th=e('th');th.scope='col';if(sortKeys.includes(key)){const b=btn('','sort-heading',()=>{if(state.sort===key)state.direction*=-1;else{state.sort=key;state.direction=1;}draw();});b.dataset.sortKey=key;if(['bankAmount','personalAmount','adjusted'].includes(key))b.title=t('amountOrderNote');th.append(b);headerControls.push({key,th,b});}else th.textContent=t(key);hr.append(th);}
    head.append(hr);table.append(head,body);area.append(table,empty);wrap.append(toolbar,area);
    function draw(){
      const selected=rows.filter(r=>(state.category===null||r.category===state.category)&&(state.account===null||r.account===state.account)&&(!state.query||[r.date,r.description,r.merchant,merchantName(r.merchant||r.description),categoryName(r.category),r.account].join(' ').toLocaleLowerCase().includes(state.query)));
      const amountKey=state.sort==='bankAmount'?'amountCents':state.sort==='personalAmount'?'personalCents':state.sort==='adjusted'?(mode==='transfers'?'transferCents':'cashCents'):null;
      selected.sort((a,b)=>{const difference=amountKey?Math.abs(a[amountKey])-Math.abs(b[amountKey]):state.sort==='date'?a.date.localeCompare(b.date):collator.compare(state.sort==='category'?categoryName(a.category):a.account,state.sort==='category'?categoryName(b.category):b.account);return difference*state.direction||a.date.localeCompare(b.date)||a.id.localeCompare(b.id);});
      for(const {key,th,b}of headerControls){const active=key===state.sort;th.setAttribute('aria-sort',active?(state.direction===1?'ascending':'descending'):'none');b.textContent=t(key)+' '+(active?(state.direction===1?'↑':'↓'):'↕');}
      const detail=t('matching')+' '+selected.length+' / '+rows.length+' '+t('count')+' · '+t('filteredTotal')+'（'+t(valueLabel)+'） '+money(sum(selected,valueKey));
      status.replaceChildren(e('span','',selected.length+' / '+rows.length),e('span','detail-total',' · '+money(sum(selected,valueKey))));status.title=detail;status.setAttribute('aria-label',detail);
      empty.hidden=selected.length>0;body.replaceChildren();
      for(const row of selected){const tr=e('tr');tr.append(e('td','nowrap',row.date));const raw=row.merchant||row.description,display=merchantName(raw),description=e('td','description',display);if(display!==raw)description.append(e('small','',raw));if(row.merchant&&row.description!==row.merchant)description.append(e('small','',row.description));if(row.source)description.append(e('small','',t('source')+': '+row.source));if(row.bankStatus==='pending')description.append(e('small','',bt('待入账 · 已计入个人支出','Pending · included in personal spending')));if(row.matchedRefund)description.append(e('small','',t('matched')));if(row.settledCents)description.append(e('small','',t('settled')+': '+money(row.settledCents)));tr.append(description,e('td','',categoryName(row.category)),e('td','',row.account),e('td','amount',money(row.amountCents)));if(mode==='expenses')tr.append(e('td','amount',String(row.share*100)+'%'),e('td','amount',money(row.personalCents)));else tr.append(e('td','amount',money(mode==='transfers'?row.transferCents:row.cashCents)));body.append(tr);}
    }
    draw();return wrap;
  }
  let dialogClosing=null;
  function closeRows(){if(!dialog.open)return;dialogClosing?.cancel();if(reducedMotion()){dialog.close();return;}dialogClosing=dialog.animate([{opacity:1,transform:'translateY(0) scale(1)'},{opacity:0,transform:'translateY(6px) scale(.985)'}],{duration:140,easing:'ease-out'});dialogClosing.onfinish=()=>{dialog.close();dialogClosing=null;};}
  function openRows(title,rows,mode=view,average=false){
    dialogClosing?.cancel();dialogClosing=null;
    hideChartTip();
    document.getElementById('dialog-title').textContent=title;
    const measure=mode==='expenses'?'personalCents':mode==='income'?'amountCents':mode==='transfers'?'transferCents':'cashCents';
    const total=sum(rows,measure);
    document.getElementById('dialog-subtitle').textContent=periodLabel(currentPeriod)+' · '+t('originalScope')+' '+rows.length+' '+t('count')+' · '+money(total)+(average?' · '+t('average')+' '+money(total/currentSummary.days):'');
    const content=document.getElementById('dialog-content');content.replaceChildren(transactionTable(rows,mode));document.getElementById('dialog-close').setAttribute('aria-label',t('close'));dialog.showModal();
  }
  function chartHeader(title,tip,rows,mode=view){const header=e('div','card-heading');const heading=e('div','card-title');heading.append(e('h2','',title),hint(tip));const menu=e('details','chart-menu');const trigger=e('summary','','···');trigger.setAttribute('aria-label',t('chartMenu')+' '+title);const action=btn(t('viewAll'),'menu-action',()=>{menu.open=false;openRows(title,rows,mode);});menu.append(trigger,action);header.append(heading,menu);return header;}
  function updateLegendFade(legend){
    const remaining=legend.scrollHeight-legend.clientHeight-legend.scrollTop;
    legend.style.setProperty('--fade-top',Math.min(24,Math.max(0,legend.scrollTop))+'px');
    legend.style.setProperty('--fade-bottom',remaining>1?Math.min(24,remaining)+'px':'0px');
  }
  const ringFrames=new Map();
  let ringJobs=[],ringAnimation=0,cardObserver=null;
  function stopCardMotion(){cancelAnimationFrame(ringAnimation);ringAnimation=0;cardObserver?.disconnect();cardObserver=null;ringJobs=[];}
  function paintRing(job,progress){
    const values=job.entries.map(item=>Math.max(0,item.from+(item.to-item.from)*progress)),sumValues=values.reduce((a,b)=>a+b,0),positiveCount=values.filter(v=>v>0).length;let angle=0;
    const frame={entries:[],total:job.fromTotal+(job.total-job.fromTotal)*progress};
    job.entries.forEach((item,index)=>{const value=values[index],sweep=sumValues?value/sumValues*Math.PI*2:0,visible=sweep*100*(job.reveal?progress:1);item.node.setAttribute('stroke-dasharray',`${Math.max(0,visible-(sumValues&&positiveCount>1?Math.min(2.6,visible*.25):0))} ${Math.PI*200}`);item.node.setAttribute('stroke-dashoffset',String(-angle*100));item.node.style.opacity=item.to===0?String(1-progress):'1';angle+=sweep;frame.entries.push({key:item.key,value,color:item.color});});
    job.number.textContent=money(progress===1?job.total:frame.total);
    frame.legend=(job.legend||[]).map(item=>{const value=progress===1?item.to:item.from+(item.to-item.from)*progress;item.node.textContent=money(value);return {key:item.key,value};});ringFrames.set(job.key,frame);
  }
  function runRingMotion(){if(ringAnimation)return;function tick(now){ringAnimation=0;let running=false;for(const job of ringJobs){if(!job.started||job.done)continue;if(!job.card.isConnected){job.done=true;continue;}const raw=reducedMotion()?1:Math.min(1,Math.max(0,(now-job.start)/560));const progress=1-(1-raw)**3;paintRing(job,progress);if(raw===1){job.done=true;for(const item of job.entries)if(item.to===0)item.node.remove();job.card.classList.remove('ring-updating');}else running=true;}if(running)ringAnimation=requestAnimationFrame(tick);}ringAnimation=requestAnimationFrame(tick);}
  function beginCardMotion(page,changed){
    const cards=[...page.querySelectorAll('.card-board > [data-card-id]')];
    const reveal=card=>{if(changed&&!reducedMotion())for(const [index,row]of [...card.querySelectorAll('.legend-row')].entries()){const animation=row.animate([{opacity:0,translate:'0 3px'},{opacity:1,translate:'0 0'}],{duration:220,delay:Math.min(index,5)*35,easing:'cubic-bezier(.22,1,.36,1)',fill:'backwards'});animation.id='legend-reveal';}
      const job=ringJobs.find(j=>j.card===card);if(job&&!job.started){job.started=true;job.start=performance.now();card.classList.add('ring-updating');runRingMotion();}};
    cardObserver=new IntersectionObserver(entries=>{for(const entry of entries)if(entry.isIntersecting){cardObserver.unobserve(entry.target);reveal(entry.target);}}, {threshold:.08});
    for(const card of cards){const rect=card.getBoundingClientRect();if(rect.bottom>0&&rect.top<innerHeight)reveal(card);else cardObserver.observe(card);}
  }
  function ring(title,items,opts={}){
    const rows=items.flatMap(x=>x.rows),divisor=opts.average?currentSummary.days:1,list=items.map(x=>({...x,value:x.value/divisor})),total=sum(list,'value');
    const card=e('section','ring-card '+(opts.size||'secondary'));if(opts.layoutId)card.dataset.cardId=opts.layoutId;
    card.append(chartHeader(title,opts.tip||t('totalTip'),rows,opts.mode));
    const key=(opts.mode||view)+':'+(opts.layoutId||title),previous=ringFrames.get(key),plot=e('div','ring-plot'),center=e('div','ring-center'),number=e('strong','',money(total));
    number.setAttribute('aria-label',money(total));center.append(number,e('span','',opts.average?t('average'):opts.label||t('netSpending')));
    const positive=list.filter(x=>x.value>0),positiveTotal=sum(positive,'value'),entries=[],oldByKey=new Map((previous?.entries||[]).map(x=>[x.key,x]));
    if(positiveTotal||previous?.entries.some(x=>x.value>0)){
      const drawing=svg('svg',{viewBox:'0 0 300 300','aria-label':title,role:'img'}),newByKey=new Map(positive.map(x=>[x.key,x]));
      const keys=[...new Set([...(previous?.entries||[]).map(x=>x.key),...positive.map(x=>x.key)])];
      const percentFormat=new Intl.NumberFormat(locale(),{style:'percent',maximumFractionDigits:2});
      for(const itemKey of keys){const item=newByKey.get(itemKey),old=oldByKey.get(itemKey),color=item?.color||old.color;const segment=svg('circle',{cx:150,cy:150,r:100,fill:'none',stroke:color,'stroke-width':40,transform:'translate(0 300) scale(1 -1)'});
        if(item){const percentage=percentFormat.format(item.value/positiveTotal),shareText=(language==='zh'?'占本圆环 ':'Share of this ring: ')+percentage;segment.setAttribute('tabindex','0');segment.setAttribute('role','button');segment.setAttribute('aria-label',item.label+' '+money(item.value)+' · '+shareText);chartTooltip(segment,[item.label,money(item.value)+(opts.average?' / '+t('dayLabel'):''),shareText,item.rows.length+' '+t('count')]);const open=()=>openRows(item.label,item.rows,opts.mode||view,opts.average);segment.addEventListener('click',open);segment.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();open();}});}else{segment.setAttribute('aria-hidden','true');segment.style.pointerEvents='none';}
        drawing.append(segment);entries.push({key:itemKey,node:segment,color,from:old?.value||0,to:item?.value||0});
      }
      plot.append(drawing,center);
    }else{plot.classList.add('empty-ring');plot.append(center);}
    if(!positiveTotal)plot.append(e('span','empty-caption',t(opts.mode==='income'?'zeroIncome':opts.mode==='transfers'?'zeroTransfers':'zeroSpending')));
    card.append(plot);const legend=e('div','ring-legend'),legendValues=[],oldLegend=new Map((previous?.legend||previous?.entries||[]).map(item=>[item.key,item.value]));for(const item of list){const row=btn('','legend-row',()=>openRows(item.label,item.rows,opts.mode||view,opts.average));row.title=item.fullLabel||item.label;const label=e('span','legend-label'),dot=e('i');dot.style.background=item.color;label.append(dot,e('span','',item.label));const amount=e('strong','',money(item.value));amount.setAttribute('aria-label',money(item.value));row.append(label,amount);legendValues.push({key:item.key,node:amount,from:oldLegend.get(item.key)||0,to:item.value});legend.append(row);}legend.addEventListener('scroll',()=>updateLegendFade(legend),{passive:true});card.append(legend);requestAnimationFrame(()=>{if(legend.isConnected)updateLegendFade(legend);});
    const job={key,card,entries,legend:legendValues,number,total,fromTotal:previous?.total||0,reveal:!previous||!previous.entries.some(x=>x.value>0),started:false,done:false,start:0};
    const changed=!previous||previous.total!==total||entries.some(x=>x.from!==x.to)||legendValues.some(x=>x.from!==x.to);
    paintRing(job,1);
    if(changed&&!reducedMotion()){paintRing(job,0);ringJobs.push(job);}else for(const item of entries)if(item.to===0)item.node.remove();
    return card;
  }
  function metric(title,value,rows,tip,mode=view){
    const box=e('section','metric-card'),head=e('div','card-title'),number=btn(money(value),'metric-number',()=>openRows(title,rows,mode));number.setAttribute('aria-label',title+' '+money(value));head.append(e('h2','',title),hint(tip));box.append(head,number);
    const key=mode+':metric:'+title,previous=ringFrames.get(key),job={key,card:box,entries:[],number,total:value,fromTotal:previous?.total||0,reveal:false,started:false,done:false,start:0};
    if((!previous||previous.total!==value)&&!reducedMotion()){paintRing(job,0);ringJobs.push(job);}else paintRing(job,1);return box;
  }
  function fold(title,content){
    const box=e('details','fold'),summary=e('summary','',title),body=e('div','fold-body');let built=false,animation=null,wanted=false;
    const build=()=>{if(!built){body.append(typeof content==='function'?content():content);built=true;}};
    if(typeof content!=='function')build();box.append(summary,body);
    const settle=open=>{animation?.cancel();animation=null;box.open=open;box.style.height='';box.style.overflow='';summary.setAttribute('aria-expanded',String(open));};
    summary.addEventListener('click',event=>{event.preventDefault();wanted=animation?!wanted:!box.open;const from=box.getBoundingClientRect().height;animation?.cancel();box.style.height='';if(wanted)build();box.open=true;const to=wanted?box.getBoundingClientRect().height:summary.getBoundingClientRect().height;summary.setAttribute('aria-expanded',String(wanted));if(reducedMotion()){settle(wanted);return;}box.style.overflow='hidden';animation=box.animate([{height:from+'px'},{height:to+'px'}],{duration:240,easing:'cubic-bezier(.22,1,.36,1)',fill:'both'});const current=animation;animation.onfinish=()=>{if(current===animation)settle(wanted);};if(wanted)body.animate([{opacity:0,translate:'0 -3px'},{opacity:1,translate:'0 0'}],{duration:220,easing:'ease-out'});});
    box.addEventListener('toggle',()=>{if(box.open&&box.isConnected)build();});return box;
  }

  let trendStyle='area', trendFrame=null, disposeTrend=()=>{}, trendSequence=0;
  Object.assign(words.en,{areaChart:'Area',barChart:'Bars',chartStyle:'Chart style',trendHelp:'Move over the chart to inspect a date. Use left/right arrows to move, up/down to choose a transfer direction, Enter to open transactions, and Escape to clear.'});
  Object.assign(words.zh,{areaChart:'面积图',barChart:'柱状图',chartStyle:'图表样式',trendHelp:'移动查看日期和金额；左右键切换日期，上下键切换转账方向，回车打开明细，Esc 收起提示。'});
  function trendControls(card){
    const controls=e('div','segments trend-controls');controls.setAttribute('role','group');controls.setAttribute('aria-label',t('chartStyle'));
    for(const value of ['area','bars']){const button=btn(t(value==='area'?'areaChart':'barChart'),'',()=>{trendStyle=value;render();});button.setAttribute('aria-pressed',String(value===trendStyle));button.setAttribute('aria-label',t(value==='area'?'areaChart':'barChart'));controls.append(button);}
    card.querySelector('.card-heading').insertBefore(controls,card.querySelector('.chart-menu'));
  }
  function areaTimeline(card,points,mode,title){
    // EasyUI-inspired SVG scrubbing and interruptible morphing; no runtime dependencies.
    // Smoothstep interpolation stays within each pair of real observations.
    const series=[{key:'a',label:t(mode==='expenses'?'daily':mode==='income'?'income':'transferOut'),color:mode==='income'?colors[2]:mode==='transfers'?colors[4]:colors[0]},...(mode==='transfers'?[{key:'b',label:t('transferIn'),color:colors[0]}]:[])];
    const previous=trendFrame?.mode===mode?trendFrame:null;
    const positions=[...new Set([...Array.from({length:513},(_,i)=>i/512),...points.map((_,i)=>points.length>1?i/(points.length-1):.5),...(previous?.positions||[])])].sort((a,b)=>a-b);
    const sample=(values,x)=>{if(values.length===1)return values[0];const q=x*(values.length-1),i=Math.min(values.length-2,Math.floor(q)),p=q-i;return values[i]+(values[i+1]-values[i])*p*p*(3-2*p);};
    const oldSample=(values,x)=>{if(!previous)return 0;let i=0;while(i<previous.positions.length-2&&previous.positions[i+1]<x)i++;const a=previous.positions[i],b=previous.positions[i+1];return values[i]+(values[i+1]-values[i])*(x-a)/(b-a);};
    const targets=series.map(s=>positions.map(x=>sample(points.map(p=>p[s.key]),x)));
    const from=series.map((_,i)=>positions.map(x=>previous?oldSample(previous.values[i],x):0));
    const rawStep=Math.max(100,...points.flatMap(p=>series.map(s=>p[s.key])))*1.08/4;
    const magnitude=10**Math.floor(Math.log10(rawStep));
    const step=[1,1.25,1.5,2,2.5,3,4,5,6,8,10].find(value=>value>=rawStep/magnitude);
    const ceiling=step*magnitude*4;
    const startMax=previous?.max||ceiling;
    const signature=mode+':'+grain+':'+currentPeriod.key,unchanged=previous?.signature===signature;
    let progress=unchanged?1:0,frameId=0,finished=unchanged,width=0,active=null,activeSeries=0,observer;
    const reduced=matchMedia('(prefers-reduced-motion: reduce)');
    const frame={mode,signature,positions,values:from.map(a=>a.slice()),max:startMax};trendFrame=frame;
    const readout=e('div','area-readout'),readoutDate=e('span','area-readout-date',t('periodTotal')),readoutValues=e('div','area-readout-values');
    const selectedRows=(point,s)=>mode==='transfers'?point.rows.filter(r=>s.key==='a'?r.transferCents<0:r.transferCents>0):point.rows;
    const readoutButtons=series.map((s,i)=>{const b=btn('','area-value',()=>{const selected=active===null?{key:periodLabel(currentPeriod),rows:points.flatMap(p=>p.rows)}:points[active];openRows(selected.key+' · '+s.label,selectedRows(selected,s),mode);});b.style.setProperty('--series-color',s.color);readoutValues.append(b);return b;});
    const updateReadout=()=>{readoutDate.textContent=active===null?t('periodTotal'):points[active].key;series.forEach((s,i)=>{const value=active===null?sum(points,s.key):points[active][s.key];readoutButtons[i].replaceChildren(e('span','area-series-label',s.label),e('strong','',money(value)));});};updateReadout();
    readout.append(readoutDate,readoutValues);card.append(readout);
    const wrap=e('div','area-chart'),drawing=svg('svg',{height:300,tabindex:0,role:'group','aria-label':title+'. '+t('trendHelp')});
    const defs=svg('defs'),grid=svg('g'),paths=svg('g'),cross=svg('g',{'pointer-events':'none',visibility:'hidden'}),crossLine=svg('line',{'class':'area-crosshair',y1:16,y2:266});cross.append(crossLine);
    const uid='trend-'+(++trendSequence),linePaths=[],fillPaths=[],dots=[];
    series.forEach((s,i)=>{const gradient=svg('linearGradient',{id:uid+'-'+i,x1:0,y1:0,x2:0,y2:1});gradient.append(svg('stop',{offset:'0%','stop-color':s.color,'stop-opacity':.24}),svg('stop',{offset:'100%','stop-color':s.color,'stop-opacity':0}));defs.append(gradient);const fill=svg('path',{fill:'url(#'+uid+'-'+i+')'}),line=svg('path',{fill:'none',stroke:s.color,'stroke-width':2.5,'stroke-linecap':'round','stroke-linejoin':'round'});paths.append(fill,line);fillPaths.push(fill);linePaths.push(line);const dot=svg('circle',{r:4.5,fill:s.color,stroke:'var(--surface)','stroke-width':2});cross.append(dot);dots.push(dot);});
    drawing.append(defs,grid,paths,cross);wrap.append(drawing);card.append(wrap);
    const status=e('span','sr-only');status.setAttribute('role','status');status.setAttribute('aria-live','polite');wrap.append(status);
    const padding=Math.max(64,Math.min(116,money(ceiling).length*7+14));
    const pad=()=>padding;
    const xAt=x=>pad()+x*Math.max(1,width-pad()-12),yAt=v=>266-v/frame.max*234;
    const tickFormat=new Intl.NumberFormat(locale(),{style:'currency',currency:data.currency,notation:'compact',maximumFractionDigits:1});
    const formatTick=value=>tickFormat.format(value/100);
    function draw(){
      frame.max=startMax+(ceiling-startMax)*progress;
      frame.values=targets.map((values,s)=>values.map((v,i)=>from[s][i]+(v-from[s][i])*progress));
      grid.replaceChildren();
      for(let i=0;i<5;i++){const y=266-i/4*234,label=svg('text',{x:pad()-12,y,'text-anchor':'end','dominant-baseline':'middle','class':'area-axis'});label.textContent=formatTick(frame.max*i/4);grid.append(svg('line',{x1:pad(),x2:width-12,y1:y,y2:y,'class':'area-grid'}),label);}
      const labelCount=width<480?3:6,indices=[...new Set(Array.from({length:labelCount},(_,i)=>Math.round(i/(labelCount-1)*(points.length-1))))];
      indices.forEach((index,j)=>{const text=svg('text',{x:xAt(points.length>1?index/(points.length-1):.5),y:293,'text-anchor':j===0?'start':j===indices.length-1?'end':'middle','class':'area-axis'});text.textContent=points[index].key.slice(5);grid.append(text);});
      series.forEach((_,s)=>{const path=positions.map((x,i)=>(i?'L':'M')+xAt(x).toFixed(2)+' '+yAt(frame.values[s][i]).toFixed(2)).join('');linePaths[s].setAttribute('d',path);fillPaths[s].setAttribute('d',path+'L'+xAt(1)+' 266L'+xAt(0)+' 266Z');});
      if(active!==null){const x=xAt(points.length>1?active/(points.length-1):.5);crossLine.setAttribute('x1',x);crossLine.setAttribute('x2',x);dots.forEach((dot,s)=>{dot.setAttribute('cx',x);dot.setAttribute('cy',yAt(points[active][series[s].key]));dot.setAttribute('r',s===activeSeries?5:3.5);});}
    }
    const finish=()=>{finished=true;cancelAnimationFrame(frameId);progress=1;draw();};
    const clear=()=>{active=null;cross.setAttribute('visibility','hidden');hideChartTip();updateReadout();status.textContent='';};
    function inspect(index,event){
      finish();active=Math.max(0,Math.min(points.length-1,index));const p=points[active];
      if(event&&series.length>1){const y=event.clientY-drawing.getBoundingClientRect().top;activeSeries=Math.abs(y-yAt(p.a))<=Math.abs(y-yAt(p.b))?0:1;}
      cross.setAttribute('visibility','visible');updateReadout();draw();
      const lines=[p.key,...series.map(s=>s.label+' · '+money(p[s.key]))];
      hideChartTip();tipOwner=drawing;chartTip.replaceChildren(...lines.map((text,i)=>e(i?'span':'strong','',text)));chartTip.hidden=false;drawing.setAttribute('aria-describedby',chartTip.id);
      const rect=drawing.getBoundingClientRect();placeChartTip(event?.clientX??rect.left+xAt(points.length>1?active/(points.length-1):.5),event?.clientY??rect.top+32);if(!event)status.textContent=lines.join(' · ');
    }
    drawing.addEventListener('pointermove',event=>{if(event.pointerType==='touch'&&!event.buttons)return;const rect=drawing.getBoundingClientRect();inspect(Math.round(Math.max(0,Math.min(1,(event.clientX-rect.left-pad())/Math.max(1,width-pad()-12)))*(points.length-1)),event);});
    drawing.addEventListener('pointerleave',event=>{if(event.pointerType!=='touch')clear();});
    drawing.addEventListener('click',event=>{const rect=drawing.getBoundingClientRect();inspect(Math.round(Math.max(0,Math.min(1,(event.clientX-rect.left-pad())/Math.max(1,width-pad()-12)))*(points.length-1)),event);if(event.pointerType!=='touch')readoutButtons[activeSeries].click();});
    drawing.addEventListener('keydown',event=>{if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home','End','Enter',' ','Escape'].includes(event.key))event.preventDefault();else return;if(event.key==='Escape'){clear();return;}if(event.key==='Enter'||event.key===' '){if(active===null)inspect(points.length-1);readoutButtons[activeSeries].click();return;}if(event.key==='ArrowUp'||event.key==='ArrowDown')activeSeries=(activeSeries+1)%series.length;inspect(event.key==='Home'?0:event.key==='End'?points.length-1:(active??points.length-1)+(event.key==='ArrowRight'?1:event.key==='ArrowLeft'?-1:0));});
    drawing.addEventListener('focus',()=>inspect(active??points.length-1));drawing.addEventListener('blur',event=>{if(!readout.contains(event.relatedTarget))clear();});
    function resize(){width=wrap.getBoundingClientRect().width;drawing.setAttribute('width',width);draw();}
    const onMotion=()=>{if(reduced.matches)finish();};reduced.addEventListener('change',onMotion);
    requestAnimationFrame(()=>{if(!card.isConnected)return;resize();observer=new ResizeObserver(resize);observer.observe(wrap);const start=performance.now();function tick(now){if(!card.isConnected)return;if(finished){progress=1;draw();return;}const p=Math.min(1,(now-start)/520);progress=reduced.matches?1:p*p*(3-2*p);draw();if(progress<1)frameId=requestAnimationFrame(tick);}frameId=requestAnimationFrame(tick);});
    disposeTrend=()=>{cancelAnimationFrame(frameId);observer?.disconnect();reduced.removeEventListener('change',onMotion);};
    return card;
  }

  function timeline(rows,mode){
    const title=mode==='expenses'?t(grain==='year'?'monthlyTrend':'dailyTrend'):t(mode==='income'?'incomeTrend':'transfersTrend');
    const card=e('section','timeline-card');card.append(chartHeader(title,t(mode==='expenses'?'dailyTip':mode==='income'?'incomeTip':'transferTip'),rows,mode));
    const map=new Map(),cursor=new Date(currentPeriod.start+'T00:00:00Z'),end=new Date(currentPeriod.end+'T00:00:00Z');
    while(cursor<=end){const day=cursor.toISOString().slice(0,10);map.set(grain==='year'?day.slice(0,7):day,[]);cursor.setUTCDate(cursor.getUTCDate()+1);}
    for(const row of rows){const key=grain==='year'?row.date.slice(0,7):row.date;map.get(key)?.push(row);}
    const points=[...map].map(([key,rs])=>({key,rows:rs,a:sum(rs,r=>mode==='expenses'?r.personalCents:mode==='income'?r.amountCents:Math.max(0,-r.transferCents)),b:mode==='transfers'?sum(rs,r=>Math.max(0,r.transferCents)):0}));
    trendControls(card);
    if(trendStyle==='area')return areaTimeline(card,points,mode,title);
    const max=Math.max(1,...points.flatMap(p=>[p.a,p.b]));
    const numberFormat=new Intl.NumberFormat(locale(),{minimumFractionDigits:2,maximumFractionDigits:2});
    const number=value=>numberFormat.format(value/100);
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
  let disposePicker=()=>{};
  Object.assign(words.en,{choosePeriod:'Choose period',previousCalendar:'Previous calendar page',nextCalendar:'Next calendar page',chooseMonth:'Choose month',chooseYear:'Choose year',coveredDates:'Available dates'});
  Object.assign(words.zh,{choosePeriod:'选择日期',previousCalendar:'日历上一页',nextCalendar:'日历下一页',chooseMonth:'选择月份',chooseYear:'选择年份',coveredDates:'资料范围'});
  function periodPicker(periods){
    const wrap=e('div','period-picker'),trigger=btn('','period-select date-trigger',()=>{});trigger.setAttribute('popovertarget','period-calendar');
    trigger.id='period-picker-trigger';trigger.setAttribute('aria-label',t('choosePeriod')+' · '+periodLabel(currentPeriod));trigger.setAttribute('aria-haspopup','dialog');trigger.setAttribute('aria-expanded','false');trigger.setAttribute('aria-controls','period-calendar');
    const icon=svg('svg',{viewBox:'0 0 24 24',width:16,height:16,fill:'none',stroke:'currentColor','stroke-width':1.6,'aria-hidden':'true'});icon.append(svg('rect',{x:3,y:5,width:18,height:16,rx:3}),svg('path',{d:'M16 3v4M8 3v4M3 11h18'}));trigger.append(icon,e('span','',periodLabel(currentPeriod)));
    const panel=e('div','date-popover');panel.id='period-calendar';panel.setAttribute('popover','auto');panel.setAttribute('role','dialog');panel.setAttribute('aria-label',t('choosePeriod'));
    let focusDate=currentPeriod.end,month=focusDate.slice(0,7),level=grain==='year'?'year':grain==='month'?'month':'day',direction=0;
    const min=data.coverage.start,max=data.coverage.end;
    const date=(key)=>new Date(key+'T12:00:00Z');
    const iso=d=>d.toISOString().slice(0,10);
    const addDay=(key,n)=>{const d=date(key);d.setUTCDate(d.getUTCDate()+n);return iso(d);};
    const addMonth=(key,n)=>{const d=date(key),day=d.getUTCDate();d.setUTCDate(1);d.setUTCMonth(d.getUTCMonth()+n);const end=new Date(Date.UTC(d.getUTCFullYear(),d.getUTCMonth()+1,0)).getUTCDate();d.setUTCDate(Math.min(day,end));return iso(d);};
    const clamp=key=>key<min?min:key>max?max:key;
    const overlaps=(start,end)=>start<=max&&end>=min;
    const monthEnd=key=>iso(new Date(Date.UTC(Number(key.slice(0,4)),Number(key.slice(5,7)),0,12)));
    function close(restore=false){if(panel.matches(':popover-open'))panel.hidePopover();trigger.setAttribute('aria-expanded','false');if(restore)trigger.focus({preventScroll:true});}
    function choose(key){const selected=periods.find(p=>p.start<=key&&p.end>=key);if(!selected)return;close();periodKey=selected.key;render();document.getElementById('period-picker-trigger')?.focus({preventScroll:true});}
    function position(){const b=trigger.getBoundingClientRect(),w=Math.min(310,innerWidth-24),h=panel.offsetHeight||360;panel.style.width=w+'px';panel.style.left=Math.max(12,Math.min(b.right-w,innerWidth-w-12))+'px';const above=innerHeight-b.bottom<h+20&&b.top>=h+12;panel.style.top=Math.max(12,Math.min(above?b.top-h-8:b.bottom+8,innerHeight-h-12))+'px';panel.style.transformOrigin=above?'bottom right':'top right';panel.style.maxHeight=Math.max(120,innerHeight-24)+'px';}
    function draw(){
      panel.replaceChildren();const year=Number(month.slice(0,4)),block=Math.floor(year/12)*12;
      const header=e('div','calendar-header'),back=btn('‹','calendar-nav',()=>navigate(-1)),next=btn('›','calendar-nav',()=>navigate(1));back.setAttribute('aria-label',t('previousCalendar'));next.setAttribute('aria-label',t('nextCalendar'));
      const heading=level==='day'?new Intl.DateTimeFormat(locale(),{month:'long',year:'numeric',timeZone:'UTC'}).format(date(month+'-01')):level==='month'?String(year):block+' – '+(block+11);
      const title=btn(heading,'calendar-title',()=>{if(level==='year')return;level=level==='day'?'month':'year';direction=0;draw();panel.querySelector('.calendar-choice[aria-pressed="true"],.calendar-choice:not(:disabled)')?.focus({preventScroll:true});});title.disabled=level==='year';title.setAttribute('aria-label',heading+' · '+t(level==='day'?'chooseMonth':'chooseYear'));
      const pageStart=level==='day'?month+'-01':level==='month'?year+'-01-01':block+'-01-01',pageEnd=level==='day'?monthEnd(month):level==='month'?year+'-12-31':(block+11)+'-12-31';back.disabled=pageStart<=min;next.disabled=pageEnd>=max;header.append(back,title,next);panel.append(header);
      const body=e('div','calendar-body'+(direction?' is-changing':''));body.style.setProperty('--calendar-direction',String(direction));
      if(level==='day'){
        const labels=e('div','calendar-weekdays');labels.setAttribute('aria-hidden','true');for(let i=0;i<7;i++)labels.append(e('span','',new Intl.DateTimeFormat(locale(),{weekday:'narrow',timeZone:'UTC'}).format(date('2024-01-'+String(i+1).padStart(2,'0')))));body.append(labels);
        const grid=e('div','calendar-days');grid.setAttribute('role','grid');grid.setAttribute('aria-label',heading);const first=month+'-01',offset=(date(first).getUTCDay()+6)%7,days=Number(monthEnd(month).slice(8));
        if(focusDate.slice(0,7)!==month)focusDate=clamp(first);
        for(let rowIndex=0;rowIndex<6;rowIndex++){const row=e('div','calendar-week');row.setAttribute('role','row');for(let col=0;col<7;col++){const day=rowIndex*7+col-offset+1,cell=e('div','calendar-cell');cell.setAttribute('role','gridcell');if(day>0&&day<=days){const key=month+'-'+String(day).padStart(2,'0'),selected=key>=currentPeriod.start&&key<=currentPeriod.end,b=btn(String(day),'calendar-day',()=>choose(key));b.dataset.date=key;b.disabled=key<min||key>max;b.tabIndex=key===focusDate?0:-1;b.setAttribute('aria-label',new Intl.DateTimeFormat(locale(),{dateStyle:'full',timeZone:'UTC'}).format(date(key)));cell.setAttribute('aria-selected',String(selected));if(selected){cell.classList.add('is-selected');if(key===currentPeriod.start||col===0||day===1)cell.classList.add('range-start');if(key===currentPeriod.end||col===6||day===days)cell.classList.add('range-end');}b.addEventListener('focus',()=>{focusDate=key;for(const item of grid.querySelectorAll('[data-date]'))item.tabIndex=item===b?0:-1;});cell.append(b);}row.append(cell);}grid.append(row);}
        grid.addEventListener('keydown',event=>{const key=event.target.dataset.date;if(!key)return;let target;const column=(date(key).getUTCDay()+6)%7;switch(event.key){case 'ArrowLeft':target=addDay(key,-1);break;case 'ArrowRight':target=addDay(key,1);break;case 'ArrowUp':target=addDay(key,-7);break;case 'ArrowDown':target=addDay(key,7);break;case 'Home':target=addDay(key,-column);break;case 'End':target=addDay(key,6-column);break;case 'PageUp':target=addMonth(key,event.shiftKey?-12:-1);break;case 'PageDown':target=addMonth(key,event.shiftKey?12:1);break;default:return;}event.preventDefault();focusDate=clamp(target);direction=focusDate.slice(0,7)===month?0:focusDate>key?1:-1;month=focusDate.slice(0,7);draw();panel.querySelector('[data-date="'+focusDate+'"]')?.focus({preventScroll:true});});body.append(grid);
      }else{
        const grid=e('div','calendar-choices');for(let i=0;i<12;i++){const key=level==='month'?year+'-'+String(i+1).padStart(2,'0'):String(block+i),start=key+(level==='month'?'-01':'-01-01'),end=level==='month'?monthEnd(key):key+'-12-31',label=level==='month'?new Intl.DateTimeFormat(locale(),{month:'short',timeZone:'UTC'}).format(date(start)):key;
          const b=btn(label,'calendar-choice',()=>{if(level===grain){choose(clamp(start));return;}month=level==='year'?key+'-'+month.slice(5):key;level=level==='year'?'month':'day';focusDate=clamp(month+'-01');direction=0;draw();panel.querySelector('[data-date][tabindex="0"],.calendar-choice[aria-pressed="true"],.calendar-choice:not(:disabled)')?.focus({preventScroll:true});});b.disabled=!overlaps(start,end);b.setAttribute('aria-label',level==='month'?year+' '+label:key);b.setAttribute('aria-pressed',String(currentPeriod.end.startsWith(key)));grid.append(b);}body.append(grid);
      }
      panel.append(body,e('p','calendar-coverage',t('coveredDates')+' · '+min+' – '+max));
      if(panel.matches(':popover-open'))position();
    }
    function navigate(n){direction=n;if(level==='day')month=addMonth(month+'-01',n).slice(0,7);else month=String(Number(month.slice(0,4))+n*(level==='year'?12:1))+month.slice(4);draw();const nav=panel.querySelectorAll('.calendar-nav')[n<0?0:1];(nav.disabled?panel.querySelector('[data-date][tabindex="0"],.calendar-choice:not(:disabled)'):nav)?.focus({preventScroll:true});}
    panel.addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();event.stopPropagation();close(true);}});
    panel.addEventListener('beforetoggle',event=>{if(event.newState==='open'){draw();position();}});
    panel.addEventListener('toggle',event=>{trigger.setAttribute('aria-expanded',String(event.newState==='open'));if(event.newState==='open'){position();panel.querySelector('[data-date][tabindex="0"],.calendar-choice[aria-pressed="true"],.calendar-choice:not(:disabled)')?.focus({preventScroll:true});}else if(panel.contains(document.activeElement))trigger.focus({preventScroll:true});});
    const reposition=()=>{if(panel.matches(':popover-open'))position();};window.addEventListener('resize',reposition);document.addEventListener('scroll',reposition,true);
    disposePicker=()=>{window.removeEventListener('resize',reposition);document.removeEventListener('scroll',reposition,true);};wrap.append(trigger,panel);return wrap;
  }

  const layoutStorageKey='personal-finance-visualizer.layout.v1';
  let layouts={},disposeLayout=()=>{},disposePeriodMotion=()=>{},lastPeriodRender=null;
  const reducedMotion=()=>matchMedia('(prefers-reduced-motion: reduce)').matches;
  Object.assign(words.en,{reorder:'Reorder',moreInfo:'More information',resetLayout:'Reset layout',layoutKeys:'With this handle focused, use arrow keys to move, Home or End to move to the edges.',layoutSaved:'Layout saved in this browser.',layoutReset:'Default layout restored.',layoutUnavailable:'Layout kept for this page; browser storage is unavailable.'});
  Object.assign(words.zh,{reorder:'移动',moreInfo:'更多信息',resetLayout:'恢复默认布局',layoutKeys:'聚焦此手柄后，用方向键移动，Home、End 移到最前或最后。',layoutSaved:'布局已保存到当前浏览器。',layoutReset:'已恢复默认布局。',layoutUnavailable:'本页布局已保留，浏览器暂不允许保存。'});
  try{const saved=JSON.parse(localStorage.getItem(layoutStorageKey));if(saved?.version===1)for(const v of ['expenses','income','transfers','overview']){const ids=saved.views?.[v];if(Array.isArray(ids)&&ids.length<=500&&ids.every(id=>typeof id==='string'&&/^[a-z0-9:_-]{1,80}$/.test(id))&&new Set(ids).size===ids.length)layouts[v]=ids;}}catch{}
  // Persist opaque category identifiers, never category text or financial values.
  function cardKey(value){let hash=14695981039346656037n;for(const ch of value){hash^=BigInt(ch.codePointAt(0));hash=BigInt.asUintN(64,hash*1099511628211n);}return hash.toString(16);}
  function wireLayout(page){
    const core={expenses:['total','daily','average','fixed','ai','housing'],income:['income-total','income-average','salary','support','other-income'],transfers:['outgoing','incoming','net-out','repaid','outstanding'],overview:['inflow','outflow','net']}[view];
    const board=e('div','card-board'),toolbar=e('div','layout-toolbar'),reset=btn(t('resetLayout'),'layout-reset',()=>restore());
    const status=e('span','sr-only');status.setAttribute('role','status');status.setAttribute('aria-live','polite');const warning=e('span','layout-warning');warning.hidden=true;
    const first=page.querySelector('.ring-grid,.metric-grid,.timeline-card');if(!first)return;
    first.before(toolbar,board);toolbar.append(reset,status,warning);
    let coreIndex=0;for(const container of [...page.children]){if(container.matches('.ring-grid,.metric-grid')){for(const card of [...container.children]){if(!card.matches('.ring-card,.metric-card')){card.classList.add('board-note');board.append(card);continue;}card.dataset.cardId=card.dataset.cardId||core[coreIndex++];card.dataset.cardSpan=container.classList.contains('two')?'half':'third';board.append(card);}container.remove();}else if(container.matches('.timeline-card')){container.dataset.cardId='trend';container.dataset.cardSpan='full';board.append(container);}}
    const cards=[...board.querySelectorAll(':scope > [data-card-id]')],defaults=cards.map(c=>c.dataset.cardId),byId=new Map(cards.map(c=>[c.dataset.cardId,c]));
    const current=()=>[...board.children].filter(c=>c.dataset.cardId).map(c=>c.dataset.cardId);
    const arrange=ids=>{for(const id of ids)if(byId.has(id))board.append(byId.get(id));};
    const saved=layouts[view]||[];arrange([...saved.filter(id=>byId.has(id)),...defaults.filter(id=>!saved.includes(id))]);
    const layoutView=view;let dragging=null,raf=0,moveAnimations=new Map();
    const boxes=()=>new Map(cards.filter(c=>!c.classList.contains('is-dragging')).map(c=>[c,c.getBoundingClientRect()]));
    function animateMove(before){if(reducedMotion())return;for(const [card,old]of before){moveAnimations.get(card)?.cancel();const now=card.getBoundingClientRect(),dx=old.left-now.left,dy=old.top-now.top;if(Math.abs(dx)+Math.abs(dy)<1)continue;const zoom=Number(getComputedStyle(card).zoom)||1;const animation=card.animate([{transform:`translate(${dx/zoom}px,${dy/zoom}px)`},{transform:'translate(0,0)'}],{duration:220,easing:'cubic-bezier(.22,1,.36,1)'});moveAnimations.set(card,animation);animation.onfinish=()=>{if(moveAnimations.get(card)===animation)moveAnimations.delete(card);};}}
    function save(){const ids=current(),visible=new Set(ids),old=layouts[layoutView]||defaults,queue=ids.slice();layouts[layoutView]=[...old.map(id=>visible.has(id)?queue.shift():id),...queue].filter(Boolean);write(t('layoutSaved'));}
    function write(message){try{localStorage.setItem(layoutStorageKey,JSON.stringify({version:1,views:layouts}));status.textContent=message;warning.hidden=true;}catch{warning.textContent=t('layoutUnavailable');warning.hidden=false;}reset.disabled=!layouts[layoutView];}
    function restore(){if(dragging)finish(false);const before=boxes();arrange(defaults);delete layouts[layoutView];write(t('layoutReset'));animateMove(before);}
    reset.disabled=!layouts[view];
    const orderAnnouncement=card=>{status.textContent=card.querySelector('h2')?.textContent+' · '+(current().indexOf(card.dataset.cardId)+1)+' / '+cards.length;};
    function start(event,card,header){if(event.button!==0||dragging||event.target.closest('button:not(.drag-handle),input,select,a,summary,.chart-menu'))return;event.preventDefault();header.querySelector('.drag-handle').focus({preventScroll:true});dragging={card,header,id:event.pointerId,startX:event.clientX,startY:event.clientY,x:event.clientX,y:event.clientY,before:current(),active:false,lastMove:0};header.setPointerCapture(event.pointerId);}
    function activate(){const d=dragging,rect=d.card.getBoundingClientRect();moveAnimations.get(d.card)?.cancel();d.rect=rect;d.zoom=Number(getComputedStyle(d.card).zoom)||1;d.style=d.card.getAttribute('style');d.placeholder=e('div','card-placeholder');d.placeholder.dataset.cardSpan=d.card.dataset.cardSpan;d.placeholder.style.height=rect.height+'px';d.placeholder.setAttribute('aria-hidden','true');d.card.before(d.placeholder);d.card.classList.add('is-dragging');Object.assign(d.card.style,{position:'fixed',left:rect.left/d.zoom+'px',top:rect.top/d.zoom+'px',width:rect.width/d.zoom+'px',height:rect.height/d.zoom+'px',margin:'0',zIndex:'1000',pointerEvents:'none'});document.body.classList.add('layout-dragging');d.active=true;hideChartTip();raf=requestAnimationFrame(tick);}
    function tick(now){const d=dragging;if(!d?.active)return;d.card.style.transform=`translate3d(${(d.x-d.startX)/d.zoom}px,${(d.y-d.startY)/d.zoom}px,0)`;const scroll=d.y<72?-Math.ceil((72-d.y)/6):d.y>innerHeight-72?Math.ceil((d.y-innerHeight+72)/6):0;if(scroll)window.scrollBy(0,scroll);
      const target=document.elementFromPoint(d.x,d.y)?.closest('[data-card-id]');if(target&&target!==d.card&&target.parentElement===board&&now-d.lastMove>240){const siblings=[...board.children].filter(n=>n!==d.card);const from=siblings.indexOf(d.placeholder),targetIndex=siblings.indexOf(target),after=targetIndex>from,at=targetIndex+(after?1:0),to=at>from?at-1:at;if(from!==to){const before=boxes();if(after)target.after(d.placeholder);else target.before(d.placeholder);animateMove(before);d.lastMove=now;}}
      raf=requestAnimationFrame(tick);
    }
    function move(event){if(!dragging||event.pointerId!==dragging.id)return;dragging.x=event.clientX;dragging.y=event.clientY;if(!dragging.active&&Math.hypot(dragging.x-dragging.startX,dragging.y-dragging.startY)>5)activate();}
    function finish(commit){const d=dragging;if(!d)return;dragging=null;cancelAnimationFrame(raf);if(d.header.hasPointerCapture(d.id))d.header.releasePointerCapture(d.id);if(d.active){const before=boxes(),visual=d.card.getBoundingClientRect();d.placeholder.replaceWith(d.card);d.card.classList.remove('is-dragging');if(d.style===null)d.card.removeAttribute('style');else d.card.setAttribute('style',d.style);document.body.classList.remove('layout-dragging');if(!commit)arrange(d.before);before.set(d.card,visual);animateMove(before);if(commit){save();orderAnnouncement(d.card);}}d.header.querySelector('.drag-handle')?.focus({preventScroll:true});}
    function end(event){if(event.pointerId!==dragging?.id)return;const b=board.getBoundingClientRect();finish(event.type==='pointerup'&&event.clientX>=b.left&&event.clientX<=b.right&&event.clientY>=Math.max(0,b.top-40)&&event.clientY<=Math.min(innerHeight,b.bottom+40));}
    function cancel(event){if(event.key==='Escape'&&dragging){event.preventDefault();finish(false);}}
    for(const card of cards){let header=card.querySelector('.card-heading');if(!header){header=e('div','card-heading');const title=card.querySelector('.card-title');title.before(header);header.append(title);}header.classList.add('draggable-heading');const handle=btn('⠿','drag-handle',()=>{});handle.setAttribute('aria-label',t('reorder')+' '+card.querySelector('h2').textContent);handle.title=t('layoutKeys');header.prepend(handle);header.addEventListener('pointerdown',event=>start(event,card,header));header.addEventListener('lostpointercapture',event=>{if(dragging?.id===event.pointerId)finish(false);});
      handle.addEventListener('keydown',event=>{if(event.altKey||event.ctrlKey||event.metaKey||dragging)return;const ids=current(),from=ids.indexOf(card.dataset.cardId),delta=event.key==='ArrowLeft'||event.key==='ArrowUp'?-1:event.key==='ArrowRight'||event.key==='ArrowDown'?1:0;let to=event.key==='Home'?0:event.key==='End'?ids.length-1:from+delta;if(!delta&&!['Home','End'].includes(event.key))return;event.preventDefault();to=Math.max(0,Math.min(ids.length-1,to));if(from===to)return;const before=boxes();ids.splice(from,1);ids.splice(to,0,card.dataset.cardId);arrange(ids);animateMove(before);save();handle.focus({preventScroll:true});orderAnnouncement(card);});}
    const abort=()=>finish(false);window.addEventListener('blur',abort);window.addEventListener('resize',abort);
    document.addEventListener('pointermove',move);document.addEventListener('pointerup',end);document.addEventListener('pointercancel',end);document.addEventListener('keydown',cancel);
    disposeLayout=()=>{window.removeEventListener('blur',abort);window.removeEventListener('resize',abort);finish(false);for(const a of moveAnimations.values())a.cancel();document.removeEventListener('pointermove',move);document.removeEventListener('pointerup',end);document.removeEventListener('pointercancel',end);document.removeEventListener('keydown',cancel);};
  }
  const switchGroups=[['view','.view-segments'],['grain','.grain-segments'],['trend','.trend-controls']];
  function periodMotionSnapshot(){
    const groups={};for(const [key,selector]of switchGroups){const bar=root.querySelector(selector),pill=bar?.querySelector('.segment-pill');if(bar&&pill){const rect=bar.getBoundingClientRect(),p=pill.getBoundingClientRect();groups[key]={left:p.left-rect.left,width:p.width,index:[...bar.querySelectorAll(':scope > button')].findIndex(b=>b.getAttribute('aria-pressed')==='true')};}}
    return {state:lastPeriodRender,groups};
  }
  function wirePeriodMotion(page,snapshot){
    const observers=[];
    for(const [key,selector]of switchGroups){const bar=page.querySelector(selector);if(!bar)continue;bar.classList.add('motion-segments');bar.setAttribute('role','group');if(!bar.hasAttribute('aria-label'))bar.setAttribute('aria-label',t('scope'));const tabs=[...bar.querySelectorAll(':scope > button')],index=tabs.findIndex(b=>b.getAttribute('aria-pressed')==='true'),active=tabs[index];if(!active)continue;
      const pill=e('span','segment-pill');pill.setAttribute('aria-hidden','true');bar.prepend(pill);const previous=snapshot.groups[key];
      const place=(animate=false)=>{const left=active.offsetLeft,width=active.offsetWidth;pill.style.transition='none';pill.style.top=active.offsetTop+'px';pill.style.height=active.offsetHeight+'px';pill.style.transform=`translateX(${animate?previous.left:left}px)`;pill.style.width=(animate?previous.width:width)+'px';void pill.offsetWidth;pill.style.transition='';pill.style.transform=`translateX(${left}px)`;pill.style.width=width+'px';};
      place(!!previous&&previous.index!==index&&!reducedMotion());let width=bar.getBoundingClientRect().width;const observer=new ResizeObserver(()=>{const next=bar.getBoundingClientRect().width;if(next!==width){width=next;place();}});observer.observe(bar);observers.push(observer);
    }
    const old=snapshot.state,periodChanged=old&&(old.grain!==grain||old.periodKey!==periodKey),viewChanged=old&&old.view!==view,languageChanged=old&&old.language!==language,styleChanged=old&&old.trendStyle!==trendStyle;
    beginCardMotion(page,!old||!!periodChanged||!!viewChanged||!!languageChanged||!!styleChanged);
    disposePeriodMotion=()=>observers.forEach(observer=>observer.disconnect());lastPeriodRender={view,grain,periodKey,trendStyle,language};
  }
  let themeTimer;
  function toggleTheme(){clearTimeout(themeTimer);const html=document.documentElement;if(!reducedMotion())html.classList.add('theme-transition');html.classList.toggle('light');themeTimer=setTimeout(()=>html.classList.remove('theme-transition'),190);}

  const budgetState={phase:'idle',settings:null,revision:null,error:'',saved:false,loading:false,lastDate:null};
  const bt=(zh,en)=>language==='zh'?zh:en;
  let budgetDialog=null,budgetSaving=false;
  async function budgetRequest(method,body,revision){
    const headers={};if(method==='POST'){headers['Content-Type']='application/json';headers['X-Budget-Revision']=revision||'absent';}
    const response=await fetch(data.budget.endpoint,{method,headers,body:body?JSON.stringify(body):undefined,credentials:'same-origin',cache:'no-store',redirect:'error',signal:AbortSignal.timeout(15000)});
    const result=await response.json();if(!response.ok){const err=new Error(result.error||'unavailable');err.status=response.status;throw err;}
    if(!result||!Object.hasOwn(result,'settings'))throw new Error('unavailable');
    if(result.revision!==null&&(typeof result.revision!=='string'||!/^"[A-Za-z0-9._:-]{1,200}"$/.test(result.revision)))throw new Error('unavailable');
    if(result.settings&&result.settings.currency!==data.currency)throw new Error('currency_mismatch');
    return {settings:result.settings?Finance.validateBudgetSettings(result.settings):null,revision:result.revision};
  }
  async function loadBudget(){
    if(budgetState.loading)return;
    const wasReady=budgetState.phase==='ready',before=JSON.stringify([budgetState.settings,budgetState.revision,budgetState.saved]);
    budgetState.loading=true;if(!wasReady)budgetState.phase='loading';budgetState.error='';let unchanged=false;
    await Promise.resolve();
    try{
      const result=data.budget.endpoint?await budgetRequest('GET'):{settings:budgetState.settings||data.budget.defaults,revision:null};
      budgetState.settings=result.settings||data.budget.defaults;budgetState.revision=result.revision;budgetState.saved=!!result.settings;budgetState.phase='ready';
      unchanged=wasReady&&before===JSON.stringify([budgetState.settings,budgetState.revision,budgetState.saved])&&budgetState.lastDate===Finance.budgetDate(budgetState.settings);
    }catch{budgetState.phase='error';budgetState.error=bt('暂时无法读取预算设置。请确认登录状态后重试。','Budget settings could not be loaded. Check your sign-in and retry.');}
    budgetState.loading=false;if(view==='budget'&&!unchanged)render();
  }
  function budgetDetail(title,rows,result){
    openRows(title,rows,'expenses');
    document.getElementById('dialog-subtitle').textContent=result.start+' – '+(data.coverage.end<result.asOf?data.coverage.end:result.asOf)+' · '+rows.length+' '+t('count')+' · '+money(sum(rows,'personalCents'));
  }
  function editBudget(){
    if(budgetState.phase!=='ready')return;
    if(!budgetDialog){budgetDialog=e('dialog','budget-settings');budgetDialog.setAttribute('aria-labelledby','budget-settings-title');document.body.append(budgetDialog);budgetDialog.addEventListener('cancel',event=>{if(budgetSaving)event.preventDefault();});}
    budgetDialog.replaceChildren();
    const current=budgetState.settings,revisionAtOpen=budgetState.revision,result=Finance.dailyBudget(data,current),draftShares=result.allocationShares;
    const title=e('h2','',bt('预算设置','Budget settings'));title.id='budget-settings-title';const heading=e('div','budget-dialog-heading');heading.append(title);
    const close=btn('×','icon-button',()=>budgetDialog.close());close.setAttribute('aria-label',t('close'));heading.append(close);budgetDialog.append(heading);
    const form=e('form','budget-form');form.noValidate=true;
    const label=e('label','budget-field');label.append(e('span','',bt('每日预算上限','Daily budget limit')+' · '+data.currency));
    const amount=e('input');amount.type='number';amount.min='0';amount.max='100000';amount.step='0.01';amount.inputMode='decimal';amount.value=current.dailyLimit;amount.required=true;amount.setAttribute('aria-label',bt('每日预算上限','Daily budget limit'));label.append(amount);form.append(label);
    form.append(e('p','muted',bt('按自然月结算，修改后重算本月总预算，下月重新开始。','The limit recalculates this calendar month. A new month starts fresh.')));
    form.append(e('p','muted',bt('计入：','Included: ')+current.groups.map(g=>t(g)).join(' · ')));
    const modeLabel=e('label','budget-field');modeLabel.append(e('span','',bt('类别分配','Category allocation')));
    let mode=current.allocationMode,customValues=null;
    const modeControl=select(bt('类别分配','Category allocation'),[['history',bt('最近三个完整月的历史比例','Historical shares: last three complete months')],['manual',bt('自定义参考比例','Custom reference shares')]],mode,v=>{if(mode==='manual')customValues=new Map(inputs.map(x=>[x.category,x.input.value]));mode=v;for(const x of inputs){x.input.disabled=mode==='history';if(mode==='history')x.input.value=((result.automaticShares.find(s=>s.category===x.category)?.basisPoints||0)/100).toFixed(2);else if(customValues?.has(x.category))x.input.value=customValues.get(x.category);}updateTotal();});if(!result.categoryRows.length)modeControl.querySelector('option[value=manual]').disabled=true;modeLabel.append(modeControl);form.append(modeLabel);
    const shares=e('div','budget-share-fields'),inputs=[];
    for(const row of result.categoryRows){
      const field=e('label','budget-share-field');field.append(e('span','',categoryName(row.category)));
      const input=e('input');input.type='number';input.min='0';input.max='100';input.step='0.01';input.inputMode='decimal';input.value=((draftShares.find(x=>x.category===row.category)?.basisPoints||0)/100).toFixed(2);input.disabled=mode==='history';input.setAttribute('aria-label',categoryName(row.category)+bt('分配百分比',' allocation percent'));
      field.append(input,e('span','muted','%'));shares.append(field);inputs.push({category:row.category,input});input.addEventListener('input',()=>updateTotal());
    }
    const initialShares=inputs.map(x=>x.input.value);
    form.append(shares);const total=e('p','budget-form-status');total.setAttribute('aria-live','polite');form.append(total);
    function updateTotal(){
      if(mode==='history'){total.textContent=result.historicalMonths.length?bt('会按最新完整月份自动更新比例；额度可在类别间挪用。','Shares update from complete months. You can move the allowance between categories.'):bt('暂无完整历史月份，可改用自定义比例。','No complete historical months yet; choose custom shares.');total.classList.remove('is-error');return;}
      let n=0;try{for(const x of inputs)n+=Finance.cents(x.input.value);}catch{n=NaN;}
      total.textContent=Number.isFinite(n)?bt('比例合计：','Total: ')+(n/100).toFixed(2)+'%'+(n===10000?'':bt('，需要等于100%。','; must equal 100%.')):bt('请填写有效的百分比。','Enter valid percentages.');total.classList.toggle('is-error',n!==10000);
    }
    updateTotal();const error=e('p','budget-form-error');error.setAttribute('role','alert');form.append(error);
    const actions=e('div','budget-form-actions'),cancel=btn(bt('取消','Cancel'),'period-button',()=>budgetDialog.close());
    const save=e('button','budget-save',data.budget.endpoint?bt('保存并同步','Save and sync'):bt('应用到本页','Apply to this page'));save.type='submit';
    const reload=btn(bt('载入最新设置','Load latest settings'),'period-button',async()=>{budgetDialog.close();await loadBudget();});reload.hidden=true;
    actions.append(reload,cancel,save);form.append(actions);
    form.append(e('p','budget-save-note',data.budget.endpoint?(data.budget.preview?bt('此预览独立保存设置，不影响正式报告。','This preview saves settings separately from the live report.'):bt('设置保存在私有存储中，手机和电脑共用。','Settings are saved privately and shared across your devices.')):bt('此独立报表只在本页试算，刷新后恢复原值。','This standalone report keeps changes only for this page session.')));
    form.addEventListener('submit',async event=>{
      event.preventDefault();if(budgetSaving)return;error.textContent='';reload.hidden=true;
      let settings;
      try{settings=Finance.validateBudgetSettings({...current,dailyLimit:amount.value,allocationMode:mode,shares:mode==='manual'?(mode===current.allocationMode&&inputs.every((x,i)=>x.input.value===initialShares[i])?current.shares:inputs.map(x=>({category:x.category,basisPoints:Finance.cents(x.input.value)}))):[]});}
      catch{error.textContent=bt('请检查日预算和类别比例；自定义比例合计须为100%。','Check the daily limit and shares. Custom shares must total 100%.');return;}
      budgetSaving=true;for(const b of [save,cancel,close])b.disabled=true;save.textContent=bt('正在保存…','Saving…');
      try{
        const saved=data.budget.endpoint?await budgetRequest('POST',settings,revisionAtOpen):{settings,revision:null};
        if(!saved.settings)throw new Error('unavailable');budgetState.settings=saved.settings;budgetState.revision=saved.revision;budgetState.saved=true;budgetState.phase='ready';budgetDialog.close();render();root.querySelector('.budget-heading button')?.focus({preventScroll:true});
      }catch(err){error.textContent=err.status===409?bt('设置已在另一处更新。请载入最新设置后再修改。','Settings changed elsewhere. Load the latest settings before editing again.'):bt('保存未能确认。请载入最新设置核对后再试。','Save could not be confirmed. Load the latest settings before retrying.');reload.hidden=false;}
      finally{budgetSaving=false;for(const b of [save,cancel,close])b.disabled=false;save.textContent=data.budget.endpoint?bt('保存并同步','Save and sync'):bt('应用到本页','Apply to this page');}
    });
    budgetDialog.append(form);budgetDialog.showModal();amount.focus();
  }
  function budgetPie(result){
    const figure=e('figure','budget-pie'),drawing=svg('svg',{viewBox:'0 0 520 520',role:'group','aria-label':bt('日常可花参考比例','Everyday allowance shares')}),legend=e('figcaption','budget-pie-legend');
    const items=result.categoryRows.filter(row=>row.basisPoints>0);let angle=-Math.PI/2;
    for(const [index,row] of items.entries()){
      const color=(Object.hasOwn(categoryColors,row.category)?categoryColors[row.category]:null)||colors[index%colors.length],sweep=row.basisPoints/10000*Math.PI*2,end=angle+sweep;
      const point=a=>[260+244*Math.cos(a),260+244*Math.sin(a)];
      const segment=items.length===1?svg('circle',{cx:260,cy:260,r:244,fill:color}):svg('path',{d:'M260 260 L'+point(angle).join(' ')+' A244 244 0 '+(sweep>Math.PI?1:0)+' 1 '+point(end).join(' ')+' Z',fill:color});
      const name=categoryName(row.category),percent=(row.basisPoints/100).toLocaleString(locale(),{maximumFractionDigits:2})+'%',amount=row.availableCents===null?'—':money(row.availableCents);
      const open=()=>budgetDetail(name,row.rows,result);segment.classList.add('budget-pie-slice');segment.setAttribute('role','button');segment.setAttribute('tabindex','0');segment.setAttribute('aria-label',name+' · '+percent+' · '+amount);
      chartTooltip(segment,[name,percent,bt('今天参考可花：','Available today: ')+amount]);segment.addEventListener('click',open);segment.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();open();}});drawing.append(segment);
      if(row.basisPoints>=1000){
        const middle=angle+sweep/2,radius=items.length===1?0:151,x=260+radius*Math.cos(middle),y=260+radius*Math.sin(middle);
        const rgb=color.slice(1).match(/../g).map(value=>{const c=parseInt(value,16)/255;return c<=.04045?c/12.92:((c+.055)/1.055)**2.4;});
        const ink=rgb[0]*.2126+rgb[1]*.7152+rgb[2]*.0722>.179?'#111111':'#ffffff';
        const label=svg('text',{x,y:y-7,'text-anchor':'middle',fill:ink,'class':'budget-pie-label','aria-hidden':'true'}),value=svg('tspan',{x,dy:27});label.textContent=name;value.textContent=percent;label.append(value);drawing.append(label);
      }
      const key=btn('','budget-pie-key',open),dot=e('i','budget-pie-dot'),label=e('span','budget-pie-name',name),value=e('span','budget-pie-value');dot.style.background=color;value.append(e('strong','',percent),e('small','muted',amount));key.append(dot,label,value);legend.append(key);angle=end;
    }
    figure.append(drawing,legend);return figure;
  }
  function budgetPage(page){
    const header=e('div','budget-heading');header.append(e('h2','',bt('每日可花','Daily allowance')));const edit=btn(bt('预算设置','Budget settings'),'period-button',editBudget);edit.disabled=budgetState.phase!=='ready';header.append(edit);page.append(header);
    if(budgetState.phase==='idle'){loadBudget();}
    if(budgetState.phase==='loading'){const loading=e('p','budget-status',bt('正在读取你的预算设置…','Loading your budget settings…'));loading.setAttribute('role','status');page.append(loading);return;}
    if(budgetState.phase==='error'){const box=e('div','budget-status');box.setAttribute('role','alert');box.append(e('p','',budgetState.error),btn(bt('重试','Retry'),'period-button',loadBudget));page.append(box);return;}
    const b=Finance.dailyBudget(data,budgetState.settings),scope=b.settings.groups.map(g=>t(g)).join(' · ');budgetState.lastDate=b.asOf;
    page.append(e('p','budget-date',b.asOf+' · '+bt('数据截至 ','Data through ')+data.coverage.end));
    if(!budgetState.saved&&data.budget.endpoint)page.append(e('p','budget-status',bt('当前使用预设预算。打开预算设置并保存后，所有设备将共用。','Using the proposed budget. Save it in Budget settings to share it across devices.')));
    if(!b.usable){const warning=e('p','budget-status is-warning',b.missingMonthStart?bt('缺少本月前段资料，暂不能可靠计算今天可花多少。','Earlier records for this month are missing, so today’s allowance is not available.'):bt('资料尚未更新到昨天，暂不显示今天的可花额度。','Records are not current through yesterday, so today’s allowance is not shown.'));warning.setAttribute('role','status');warning.append(e('br'),btn(bt('刷新报告','Refresh report'),'period-button',()=>location.reload()));page.append(warning);}
    const summary=e('section','budget-summary'),main=e('div','budget-today'),amount=e('div','budget-amount');
    amount.append(e('strong','budget-available',b.availableCents===null?'—':money(b.availableCents)));
    const previous=Finance.dailyBudget(data,budgetState.settings,b.expectedCoverageThrough);
    const change=b.availableCents===null||previous.openingCents===null?null:b.availableCents-previous.openingCents;
    const signed=(value,digits)=>(value>0?'+':value<0?'−':'')+Math.abs(value).toLocaleString(data.language==='zh-CN'?'zh-CN':'en-US',{maximumFractionDigits:digits});
    const percent=change===null||previous.openingCents===0?null:change/previous.openingCents*100;
    const delta=e('span','budget-change'+(change>0?' is-up':change<0?' is-down':''));
    const deltaAmount=change===null?'—':signed(change/100,2),deltaPercent=percent===null?'—':signed(percent,2)+'%';
    delta.title=bt('相比昨天一开始的可花额度（按当前预算设置）','Compared with yesterday’s opening allowance (using current budget settings)');
    delta.setAttribute('aria-label',delta.title+': '+deltaAmount+', '+deltaPercent);
    delta.append(e('span','',deltaAmount),e('span','',deltaPercent));amount.append(delta);
    main.append(e('span','budget-kicker',bt('今天还能花','Available today')),amount);
    if(b.overspentTodayCents>0)main.append(e('p','muted',bt('今天已超出 ','Over today’s allowance by ')+money(b.overspentTodayCents)));
    else if(data.coverage.end>=b.asOf)main.append(e('p','muted',bt('今天已确认支出 ','Confirmed spending today: ')+money(b.spentTodayCents)));
    const stats=e('dl','budget-stats');for(const [label,value] of [[bt('每日上限','Daily limit'),money(b.dailyLimitCents)],[bt('本月总预算','Monthly budget'),money(b.monthlyBudgetCents)],[bt('本月剩余','Left this month'),b.usable?money(b.remainingMonthCents):'—'],[bt('含今天还剩','Days including today'),b.remainingDays+bt('天',' days')]]){const item=e('div');item.append(e('dt','',label),e('dd','',value));stats.append(item);}summary.append(main,stats);page.append(summary);
    if(b.monthDeficitCents>0)page.append(e('p','budget-status is-warning',bt('本月预算已超出 ','This month is over budget by ')+money(b.monthDeficitCents)+bt('。今日可花按0显示，下月重新开始。','. Today’s available amount is zero. Next month starts fresh.')));
    const section=e('section','budget-section');const sectionHead=e('div','budget-section-heading');sectionHead.append(e('h2','',bt('日常可花参考','Everyday category allowances')));section.append(sectionHead);
    section.append(e('p','muted',b.settings.allocationMode==='manual'?bt('按你保存的比例分配，可以在类别间挪用。','Using your saved shares. You can move amounts between categories.'):bt('参考完整月份：','Complete months used: ')+(b.historicalMonths.length?b.historicalMonths.slice().reverse().join(' · '):bt('暂无','none'))));
    if(!b.hasAllocation)section.append(e('p','budget-status',b.categoryRows.length?bt('暂无可用的历史比例。可以在预算设置中手动分配。','No historical allocation is available. Set custom shares in Budget settings.'):bt('暂无日常类别记录，获得数据后显示参考分配。','Category references will appear when everyday records are available.')));
    if(b.hasAllocation)section.append(budgetPie(b));page.append(section);
    if(b.costGroups.length){const costs=e('section','budget-section budget-costs');costs.append(e('h2','',bt('固定费用已经占用多少','Recorded fixed costs')));const list=e('div','budget-cost-list');for(const group of b.costGroups){const row=btn('','budget-cost-row',()=>budgetDetail(t(group.group),group.rows,b));row.append(e('span','',t(group.group)),e('strong','',money(group.spentMonthCents)),e('small','muted',bt('折合每天 ','Per calendar day: ')+money(group.monthlyDailyCostCents)));list.append(row);}costs.append(list);page.append(costs);}
    const details=e('div','notes');details.append(e('p','',bt('今日起始额度＝（本月预算－今天之前已花）÷剩余天数（含今天），最多不超过每日上限；再扣今天已确认支出。','Opening allowance = (monthly budget − spending before today) ÷ remaining days including today, capped at your daily limit. Confirmed spending today, including pending purchases, is then deducted.')),e('p','',bt('计入：','Included: ')+scope+'。'),e('p','',bt('“折合全月每天”只解释费用，不会再扣一次。类别额度是参考分配，不是互相独立的硬限制。','Cost per calendar day explains spending; it is not deducted again. Category amounts are reference allocations, not separate hard limits.')),e('p','',bt('已确认的待入账消费计入花费与预算；尚未导入或未确认的记录不计入，未来固定扣款不预估。','Confirmed pending purchases count toward spending and budget. Unimported or unconfirmed records are excluded; future fixed charges are not forecast.')));details.append(e('p','',bt('这是预算额度，账户余额未用于这项计算。','This is a budget allowance; account balances are not used in this calculation.')));for(const note of data.notes)details.append(e('p','',note));page.append(fold(bt('预算怎么算','How the budget works'),details));
  }
  document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible'&&view==='budget'&&!budgetDialog?.open&&!budgetSaving){loadBudget();}});

  function render(){
    stopCardMotion();const motionSnapshot=periodMotionSnapshot();disposeLayout();disposeLayout=()=>{};disposePeriodMotion();disposePeriodMotion=()=>{};
    disposeTrend();disposeTrend=()=>{};disposePicker();disposePicker=()=>{};
    hideChartTip();
    const focused=document.activeElement?.getAttribute('aria-label');const periods=Finance.periods(data,grain);let index=periods.findIndex(p=>p.key===periodKey);if(index<0)index=periods.length-1;currentPeriod=periods[index];periodKey=currentPeriod.key;currentSummary=Finance.summarize(data,currentPeriod);const s=currentSummary,rows=s.rows,spending=rows.filter(r=>r.kind==='expense'&&!r.matchedRefund),daily=spending.filter(r=>r.group==='daily');
    document.documentElement.lang=locale();document.title=t('title');root.replaceChildren();
    const top=e('header','topbar');const left=e('div','topbar-title');left.append(e('span','',t('title')),e('span','as-of',t('asOf')+' '+data.coverage.end));const right=e('div','topbar-actions');if(data.demo)right.append(e('span','demo-badge',t('demo')));right.append(btn('◐','theme-toggle',toggleTheme),select(t('language'),[['en','English'],['zh','简体中文']],language,v=>{language=v;render();},'language'));right.querySelector('button').setAttribute('aria-label',t('theme'));top.append(left,right);root.append(top);
    const page=e('article','finance-page'+(data.budget?' has-budget':''));const heading=e('header','finance-heading');heading.append(e('h1','',t('title')));const views=e('div','segments view-segments');views.setAttribute('role','group');views.setAttribute('aria-label',t('view'));for(const key of ['overview','expenses','income','transfers',...(data.budget?['budget']:[])]){const b=btn(t(key),'',()=>{view=key;if(key==='budget')loadBudget();render();});b.setAttribute('aria-pressed',String(view===key));b.setAttribute('aria-label',t(key));views.append(b);}heading.append(views);page.append(heading);
    if(view==='budget'){budgetPage(page);root.append(page);wirePeriodMotion(page,motionSnapshot);root.setAttribute('aria-busy','false');return;}
    const controls=e('div','period-header');controls.append(e('h2','period-title',periodLabel(currentPeriod)));const tools=e('div','period-tools');const grains=e('div','segments grain-segments t-tabs');grains.setAttribute('role','group');grains.setAttribute('aria-label',t('period'));for(const g of ['day','week','month','year']){const b=btn(t(g),'t-tab',()=>{const date=currentPeriod.end;grain=g;periodKey=Finance.periods(data,g).find(p=>p.start<=date&&p.end>=date)?.key;render();});b.setAttribute('aria-pressed',String(g===grain));b.setAttribute('aria-label',t(g));grains.append(b);}controls.append(grains);const previous=btn(t('previous'),'period-button',()=>{periodKey=periods[index-1].key;render();});previous.disabled=index===0;const next=btn(t('next'),'period-button',()=>{periodKey=periods[index+1].key;render();});next.disabled=index===periods.length-1;tools.append(previous,periodPicker(periods),next);controls.append(tools);page.append(controls);
    if(view==='expenses'){
      const total=bucket(spending,r=>r.group,'personalCents',groupColors).map(x=>({...x,label:t(x.key)}));const daySlices=bucket(daily,'category','personalCents',categoryColors);const primary=e('div','ring-grid three');primary.append(ring(t('total'),total,{size:'primary'}),ring(t('daily'),daySlices,{size:'primary',tip:t('dailyTip')}),ring(t('dailyAverage'),daySlices,{size:'primary',average:true,tip:t('averageTip')}));page.append(primary);
      const secondary=e('div','ring-grid three');for(const g of ['fixed','ai','housing'])secondary.append(ring(t(g),bucket(spending.filter(r=>r.group===g),'category','personalCents',categoryColors),{tip:t(g+'Tip')}));page.append(secondary);
      const merchants=e('div','ring-grid three merchant-grid');const categories=bucket(spending.filter(r=>r.group==='daily'),'category','personalCents',categoryColors);for(const category of categories){if(['Transport','Other','Uncategorized','Needs review','交通出行','其他日常','商户待分类'].includes(category.key))continue;merchants.append(ring(category.label,bucket(category.rows,r=>r.merchant||r.description,'personalCents'),{size:'merchant',layoutId:'merchant:daily:'+cardKey(category.key)}));}if(!merchants.children.length)merchants.append(e('p','empty',t('zeroSpending')));page.append(merchants);
      if(grain!=='day')page.append(timeline(daily,'expenses'));page.append(fold(t('periodSummary'),()=>amountSummary(s)),fold(t('allTransactions'),()=>transactionTable(spending)),fold(t('allMonths'),()=>monthSummary()));const refundRows=rows.filter(r=>r.kind==='refund'||r.matchedRefund);page.append(fold(t('refunds'),()=>transactionTable(refundRows,'overview')));
    }else if(view==='overview'){
      const grid=e('div','metric-grid');grid.append(metric(t('inflow'),s.inflow,rows.filter(r=>r.cashCents>0),t('cashTip')),metric(t('outflow'),s.outflow,rows.filter(r=>r.cashCents<0),t('cashTip')),metric(t('net'),s.net,rows.filter(r=>r.kind!=='internal'&&r.bankStatus!=='pending'),t('cashTip')));page.append(grid);
    }else if(view==='income'){
      const income=rows.filter(r=>r.kind==='income');const slices=bucket(income,'category','amountCents',categoryColors);const primary=e('div','ring-grid two');primary.append(ring(t('incomeTotal'),slices,{size:'primary',mode:'income',label:t('income'),tip:t('incomeTip')}),ring(t('incomeAverage'),slices,{size:'primary',mode:'income',average:true,tip:t('incomeTip')}));page.append(primary);const secondary=e('div','ring-grid three');for(const type of ['salary','support','other'])secondary.append(ring(t(type==='other'?'otherIncome':type),bucket(income.filter(r=>r.incomeType===type),r=>r.merchant||r.description,'amountCents'),{mode:'income',label:t('income'),tip:t('incomeTip')}));page.append(secondary);if(grain!=='day')page.append(timeline(income,'income'));page.append(fold(t('transactions'),()=>transactionTable(income,'income')));
    }else{
      const transfers=rows.filter(r=>r.kind.startsWith('transfer_'));const outgoing=transfers.filter(r=>r.transferCents<0),incoming=transfers.filter(r=>r.transferCents>0);const primary=e('div','ring-grid two');primary.append(ring(t('outgoing'),bucket(outgoing,'category',r=>-r.transferCents),{size:'primary',mode:'transfers',label:t('transferOut'),tip:t('transferTip')}),ring(t('incoming'),bucket(incoming,'category','transferCents'),{size:'primary',mode:'transfers',label:t('transferIn'),tip:t('transferTip')}));page.append(primary);const loans=rows.filter(r=>r.kind==='transfer_out'&&r.purpose==='loan');const metrics=e('div','metric-grid');metrics.append(metric(t('netOut'),s.transferOut-s.transferIn,transfers,t('transferTip')),metric(t('repaid'),sum(loans,'settledCents'),loans,t('transferTip')),metric(t('outstanding'),sum(loans,r=>-r.transferCents),loans,t('transferTip')));page.append(metrics);if(grain!=='day')page.append(timeline(transfers,'transfers'));page.append(fold(t('transactions'),()=>transactionTable(transfers,'transfers')),fold(t('settlements'),()=>transactionTable(transfers.filter(r=>r.settledCents),'transfers')),fold(t('internalRows'),()=>transactionTable(rows.filter(r=>r.kind==='internal'),'overview')));
    }
    page.append(notes());const moreItems=e('div','more-info-sections');for(const item of [...page.querySelectorAll(':scope > .fold')])moreItems.append(item);const moreInfo=fold(t('moreInfo'),moreItems);moreInfo.classList.add('more-info');page.append(moreInfo);wireLayout(page);root.append(page);wirePeriodMotion(page,motionSnapshot);root.setAttribute('aria-busy','false');if(focused){const target=[...root.querySelectorAll('[aria-label]')].find(n=>n.getAttribute('aria-label')===focused);target?.focus({preventScroll:true});}
  }
  matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change',event=>{if(event.matches){cancelAnimationFrame(ringAnimation);ringAnimation=0;for(const job of ringJobs){paintRing(job,1);job.done=true;job.card.classList.remove('ring-updating');for(const item of job.entries)if(item.to===0)item.node.remove();}document.getAnimations().forEach(a=>a.finish());}});
  dialog.addEventListener('cancel',event=>{event.preventDefault();closeRows();});
  document.getElementById('dialog-close').addEventListener('click',closeRows);dialog.addEventListener('click',ev=>{if(ev.target===dialog){const b=dialog.getBoundingClientRect();if(ev.clientX<b.left||ev.clientX>b.right||ev.clientY<b.top||ev.clientY>b.bottom)closeRows();}});
  try{data=Finance.validate(window.REPORT_DATA);render();}catch(err){root.replaceChildren(e('h1','error',t('error')),e('p','error',t('errorBody')));root.setAttribute('aria-busy','false');}
}());

/*
Area-chart and calendar interaction references: https://github.com/Surajmaurya1/easyui
MIT License

Copyright (c) 2026 Suraj Maurya

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/
