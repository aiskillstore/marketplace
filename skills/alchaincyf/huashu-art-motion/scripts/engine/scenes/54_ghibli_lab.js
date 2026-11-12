/* Original urban bicycle-repair kiosk. Hand-painted environment + mechanical contact. */
SCENES['54_ghibli_lab']=(()=>{
 const T=Math.PI*2;let back,front;
 const rng=n=>()=>((n=(n*1664525+1013904223)>>>0)/4294967296);
 function P(g,p,col,stroke='#4e6158',w=2){g.beginPath();p.forEach((v,i)=>i?g.lineTo(...v):g.moveTo(...v));g.closePath();if(col){g.fillStyle=col;g.fill();}if(stroke){g.strokeStyle=stroke;g.lineWidth=w;g.stroke();}}
 function L(g,p,col='#4e6158',w=2){g.beginPath();p.forEach((v,i)=>i?g.lineTo(...v):g.moveTo(...v));g.strokeStyle=col;g.lineWidth=w;g.lineCap='round';g.stroke();}
 function R(g,x,y,w,h,col,stroke='#607363'){g.fillStyle=col;g.fillRect(x,y,w,h);if(stroke){g.strokeStyle=stroke;g.lineWidth=2;g.strokeRect(x,y,w,h);}}
 function E(g,x,y,rx,ry,col){g.fillStyle=col;g.beginPath();g.ellipse(x,y,rx,ry,0,0,T);g.fill();}
 function speck(g,x,y,w,h,n,seed,cols){const r=rng(seed);g.save();for(let i=0;i<n;i++){g.fillStyle=cols[i%cols.length];g.globalAlpha=.04+r()*.12;let xx=x+r()*w,yy=y+r()*h;g.beginPath();g.ellipse(xx,yy,2+r()*13,1+r()*4,r()*.4,0,T);g.fill();}g.restore();}
 function pigment(canvas,seed){const g=canvas.getContext('2d'),r=rng(seed),src=g.getImageData(0,0,1920,1080),d=src.data;for(let i=0;i<72000;i++){let x=r()*1920,y=r()*1080,k=(Math.floor(y)*1920+Math.floor(x))*4;if(d[k+3]<180)continue;let delta=(r()-.5)*35;g.strokeStyle=`rgba(${d[k]+delta},${d[k+1]+delta},${d[k+2]+delta*.8},${.06+r()*.10})`;g.lineWidth=.6+r()*2.5;g.beginPath();g.moveTo(x,y);g.lineTo(x+3+r()*14,y+(r()-.5)*4);g.stroke();}const p=g.getImageData(0,0,1920,1080),a=p.data;for(let i=0;i<a.length;i+=4){if(a[i+3]<180)continue;let n=(r()-.5)*7;a[i]+=n;a[i+1]+=n;a[i+2]+=n;}g.putImageData(p,0,0);}
 function window(g,x,y,w,h){R(g,x-5,y-5,w+10,h+10,'#c3ba8c');R(g,x,y,w,h,'#657f80');R(g,x+5,y+4,w-10,h*.44,'#94b2ac');L(g,[[x+w*.5,y],[x+w*.5,y+h]],'#e8ddb1',5);L(g,[[x,y+h*.5],[x+w,y+h*.5]],'#e8ddb1',5);L(g,[[x+4,y+h-4],[x+w-5,y+6]],'#d8dfbd55',4);}
 function plant(g,x,y,s,seed){const r=rng(seed);P(g,[[x-30*s,y],[x+30*s,y],[x+23*s,y+48*s],[x-21*s,y+48*s]],'#a86f51');E(g,x,y,32*s,9*s,'#694e37');for(let i=0;i<20;i++){let a=r()*T,len=(30+r()*65)*s,xx=x+Math.cos(a)*len,yy=y-40*s-r()*60*s;L(g,[[x,y],[xx,yy]],'#4e7957',2*s);g.save();g.translate(xx,yy);g.rotate(a);E(g,0,0,17*s,6*s,i%3?'#60875a':'#9aaa62');L(g,[[-13*s,0],[14*s,0]],'#c2c77d',.7*s);g.restore();}}
 function make(){if(back)return;back=document.createElement('canvas');back.width=1920;back.height=1080;let g=back.getContext('2d');let sky=g.createLinearGradient(0,0,0,620);sky.addColorStop(0,'#9dbeb8');sky.addColorStop(.7,'#d6d6ac');sky.addColorStop(1,'#efe2af');g.fillStyle=sky;g.fillRect(0,0,1920,1080);
  // Hills and connected city blocks, observed roofs, wires and masonry.
  P(g,[[0,270],[150,170],[300,208],[450,123],[620,210],[770,140],[950,258],[1250,177],[1510,242],[1920,120],[1920,650],[0,650]],'#95aa93',null);
  for(let i=0;i<9;i++){let x=i*171-25,y=190+(i%3)*55,w=155;R(g,x,y,w,340,['#c9c8a4','#d0bba0','#adbcb0'][i%3]);P(g,[[x-8,y],[x+70,y-62],[x+w+10,y],[x+w,y+14],[x,y+14]],['#6c8e80','#ad7b64','#7f9a8b'][i%3]);P(g,[[x,y+14],[x+w,y+14],[x+w,y+38],[x,y+30]],'#516d6033',null);for(let row=0;row<2;row++)for(let j=0;j<2;j++){let wx=x+20+j*75,wy=y+45+row*113;window(g,wx,wy,42,70);if(i%2){R(g,wx-13,wy,9,70,'#788b71');for(let k=0;k<8;k++)L(g,[[wx-12,wy+k*9],[wx-5,wy+k*9]],'#566b58',1);}R(g,wx-7,wy+72,56,8,'#c1b78c');if(row===1&&i%3===0){R(g,wx-5,wy+65,51,15,'#a77b5a');for(let k=0;k<9;k++){E(g,wx+k*5,wy+60-(k%3)*5,6,7,'#6c8c5e');E(g,wx+k*5,wy+56-(k%3)*5,3,3,'#d69b7f');}}}L(g,[[x+w-8,y+20],[x+w-8,y+330],[x+w-21,y+337]],'#7d8e78',4);R(g,x+65,y-62,21,35,'#a39275');R(g,x+60,y-64,30,7,'#657c6c');if(i%3===1){R(g,x+18,y+277,120,55,'#5d8279');for(let k=0;k<6;k++)P(g,[[x+10+k*23,y+265],[x+33+k*23,y+265],[x+40+k*23,y+292],[x+17+k*23,y+292]],k%2?'#d3ba8b':'#b87859');}speck(g,x,y,w,330,130,i+54,['#7e9b85','#fff2b3','#9e8e73']);}
  R(g,0,547,1920,183,'#b2b4a0');L(g,[[0,643],[1920,643]],'#e0d6ac',5);L(g,[[0,678],[1920,678]],'#6f857a',4);L(g,[[0,695],[1920,695]],'#e0d6ac',3);
  for(let i=0;i<50;i++){let x=(i*127)%1920,y=562+(i*43)%140;L(g,[[x,y],[x+42,y-2]],'#859b8b44',2);}
  // A plane tree's irregular leaf masses interrupt the repetitive street rhythm.
  L(g,[[1258,572],[1255,437],[1215,339]],'#6d8066',18);L(g,[[1251,451],[1320,355]],'#6d8066',10);const treeR=rng(558);for(let i=0;i<620;i++){let a=treeR()*T,rad=Math.sqrt(treeR())*127,xx=1250+Math.cos(a)*rad,yy=329+Math.sin(a)*rad*.7;E(g,xx,yy,8+treeR()*17,5+treeR()*10,['#678b6b','#7e9b70','#a4b77d','#88a575','#bbbf89'][i%5]);}
  // Overhead cable follows the rail direction and powers the tram's pantograph.
  L(g,[[-20,158],[490,186],[980,179],[1510,164]],'#677e72',3);L(g,[[74,0],[74,562]],'#76846e',9);L(g,[[60,154],[380,154]],'#76846e',5);
  speck(g,0,0,1920,1080,2900,545,['#fff0bd','#6c927f','#b5b28b']);
  pigment(back,555);
  front=document.createElement('canvas');front.width=1920;front.height=1080;g=front.getContext('2d');
  // Open kiosk structure leaves most of the street unobstructed.
  P(g,[[1415,0],[1920,0],[1920,1080],[1550,1080],[1435,716]],'#d8ccaa');speck(g,1415,0,505,1080,1700,549,['#a3ac91','#fff0bd','#b29976']);
  R(g,1432,0,42,754,'#526e65');R(g,1474,0,14,754,'#d4d0a2');R(g,0,0,1440,64,'#54796b');R(g,0,64,1440,12,'#a9b28b');
  P(g,[[0,720],[1448,702],[1920,1080],[0,1080]],'#b9b99b');speck(g,0,720,1920,360,1300,550,['#718d7c','#e9dcb0','#a89d78']);
  for(let i=-4;i<11;i++)L(g,[[100+i*170,720],[50+i*256,1080]],'#83948155',2);for(let y=778;y<1080;y+=70)L(g,[[0,y],[1920,y]],'#81968044',2);
  // Strong, coherent morning light, tied to the aperture and objects.
  P(g,[[118,720],[846,713],[1290,1080],[367,1080]],'#f5e8af66',null);P(g,[[1435,716],[1484,716],[1747,1080],[1670,1080]],'#5a75642d',null);
  // Wall tools with handles, hooks and tiny marks instead of ornamental symbols.
  R(g,1557,129,313,344,'#a88f68');R(g,1567,139,293,324,'#c6b68b');for(let y=160;y<455;y+=25)for(let x=1582;x<1850;x+=25)E(g,x,y,1.4,1.4,'#957d5b');
  for(let i=0;i<4;i++){let x=1610+i*65;L(g,[[x,179],[x,191]],'#71684c',3);if(i%2){L(g,[[x,195],[x,330]],'#737f70',11);E(g,x,208,17,22,'#7c8b7b');E(g,x,207,8,14,'#c6b68b');R(g,x-9,307,18,66,'#a05c45');}else{L(g,[[x,195],[x,336]],'#6e7f71',10);L(g,[[x-19,195],[x-14,221],[x+14,221],[x+19,195]],'#667c70',7);R(g,x-8,319,16,47,'#637d69');}}
  // Long well-used repair bench, a perspective volume with imperfect wood grain.
  P(g,[[1025,688],[1687,674],[1830,747],[1128,779]],'#b39061');P(g,[[1128,779],[1830,747],[1830,785],[1128,815]],'#8c704e');P(g,[[1025,688],[1128,779],[1128,815],[1025,726]],'#857556');for(let i=0;i<14;i++)L(g,[[1061+i*22,704+i*3],[1720+i*3,701+i*3]],'#dec18c66',1.4);
  R(g,1150,809,24,271,'#7a7451');R(g,1763,783,30,297,'#7a7451');R(g,1180,947,580,18,'#8c805a');R(g,1224,831,277,67,'#ad9065');R(g,1235,839,254,48,'#bd9f70');L(g,[[1338,858],[1380,858]],'#6f795b',6);P(g,[[1450,927],[1651,927],[1674,947],[1475,947]],'#c6ab78');R(g,1475,897,199,50,'#ad9164');for(let j=0;j<5;j++)L(g,[[1490+j*38,900],[1490+j*38,942]],'#927e59',2);
  // Two tins, packed parts tray, oil can, rag and bicycle pump.
  E(g,1632,711,61,15,'#536655');R(g,1573,650,118,60,'#9cae91');E(g,1632,650,59,14,'#c9ccb0');E(g,1632,648,47,9,'#697d68');for(let i=0;i<8;i++){let x=1594+i*11;L(g,[[x,646],[x+6,604-i%3*13]],'#566f66',3);}
  P(g,[[1395,727],[1528,724],[1570,743],[1433,753]],'#687c6e');for(let i=0;i<12;i++)E(g,1417+(i*37)%123,733+(i%3)*4,8,3,'#c1c8a6');
  P(g,[[1691,671],[1738,665],[1750,708],[1698,712]],'#b4774d');L(g,[[1717,669],[1725,635],[1776,621]],'#b4774d',7);R(g,1705,656,22,13,'#647667');
  // A bicycle at the open edge; tubes, spokes, chain and cast shadow agree.
  E(g,586,1025,381,26,'#5a79602b');for(const x of [358,815]){g.beginPath();g.arc(x,908,123,0,T);g.strokeStyle='#455a52';g.lineWidth=13;g.stroke();g.strokeStyle='#bec7a5';g.lineWidth=3;g.beginPath();g.arc(x,908,111,0,T);g.stroke();for(let i=0;i<32;i++){let a=i*T/32;L(g,[[x,908],[x+Math.cos(a)*111,908+Math.sin(a)*111]],'#8a9f8d',1.2);}E(g,x,908,9,9,'#516d61');}
  const red='#9c6254';L(g,[[358,908],[493,733],[574,908],[358,908]],red,10);L(g,[[493,733],[735,744],[574,908],[735,744],[815,908]],red,10);L(g,[[493,733],[478,691]],'#576f62',9);L(g,[[438,686],[507,686]],'#4e6052',16);L(g,[[735,744],[719,666],[773,643],[795,652]],'#536e63',9);E(g,574,908,31,31,'#66816c');E(g,574,908,23,23,'#9cae8c');L(g,[[574,908],[604,931],[633,930]],'#4c675c',6);L(g,[[360,908],[574,934],[574,882],[360,908]],'#718773',2);R(g,292,765,138,14,'#7b8e74');L(g,[[315,778],[336,888]],'#788974',3);L(g,[[420,778],[373,888]],'#788974',3);
  plant(g,102,892,1.35,547);plant(g,945,787,.85,548);plant(g,1832,662,.8,551);
  // Blue enamel kettle on an actual burner, cup and detached bicycle lamp.
  E(g,1285,750,82,19,'#53695b44');R(g,1214,712,137,34,'#75816b');E(g,1284,714,50,13,'#435b50');
  E(g,1283,672,59,58,'#4d8587');g.save();g.beginPath();g.ellipse(1283,672,59,58,0,0,T);g.clip();E(g,1308,696,52,51,'#396f78');E(g,1268,652,35,42,'#6caaa3');g.restore();P(g,[[1238,683],[1192,643],[1198,633],[1252,654]],'#6e9e99');E(g,1284,629,42,10,'#89b1a3');E(g,1284,621,13,8,'#4e6861');g.beginPath();g.arc(1288,649,51,Math.PI,0);g.strokeStyle='#566b58';g.lineWidth=10;g.stroke();L(g,[[1247,661],[1243,685]],'#adc6ac',5);
  E(g,1396,711,35,9,'#526d5933');R(g,1371,667,48,44,'#e3d0a0');E(g,1395,667,24,7,'#eae0b8');E(g,1395,668,18,4,'#856c4c');g.beginPath();g.arc(1422,686,14,-1.6,1.6);g.strokeStyle='#c9b68b';g.lineWidth=6;g.stroke();
  pigment(front,556);
 }
 function tram(g,x,t){g.save();g.translate(x,0);E(g,475,691,534,23,'#506d6830');for(let xx of [140,785]){E(g,xx,657,47,47,'#3e5b56');E(g,xx,657,31,31,'#86978a');for(let i=0;i<8;i++){let a=i*T/8-t*4;L(g,[[xx,657],[xx+Math.cos(a)*27,657+Math.sin(a)*27]],'#485f56',3);}}
  P(g,[[-40,389],[-17,343],[49,325],[905,325],[959,354],[978,624],[947,664],[-13,664]],'#b76543','#556b5d',3);R(g,-20,459,979,104,'#e0bd7c');P(g,[[-25,350],[944,350],[936,392],[-28,392]],'#d7c8a0');
  for(let i=0;i<7;i++){let xx=24+i*125;R(g,xx,376,103,145,'#465e5a');R(g,xx+5,381,93,105,'#8fb5ad');P(g,[[xx+5,381],[xx+35,381],[xx+93,461],[xx+93,486],[xx+70,486]],'#d6dfbe55',null);R(g,xx+5,491,93,25,'#5d7770');L(g,[[xx+52,381],[xx+52,486]],'#d6c89f',3);}
  R(g,850,365,98,263,'#b7754d');R(g,860,380,76,134,'#7ea099');L(g,[[899,380],[899,626]],'#e6bf7f',3);L(g,[[859,592],[939,592]],'#9f6341',3);E(g,944,586,12,17,'#f1d393');L(g,[[2,628],[946,628]],'#e3b777',4);
  // Roof pantograph stays in contact with the overhead wire.
  L(g,[[450,323],[410,260],[486,194],[570,260],[523,323]],'#5d7568',5);L(g,[[460,193],[520,193]],'#526e62',6);R(g,353,313,280,16,'#688276');
  speck(g,-10,535,952,112,180,554,['#f4c58a','#8b5b41']);g.restore();}
 return {draw(c,lt){let t=Math.max(0,lt);make();c.drawImage(back,0,0);c.save();c.beginPath();c.rect(0,75,1435,645);c.clip();tram(c,1270-t*390,t);c.restore();c.drawImage(front,0,0);
  // Steam rises continuously from the spout; translucent curls are attached to it.
  for(let i=0;i<5;i++){let q=(t*.35+i*.2)%1,x=1193-24*q+Math.sin(t*1.8+i)*10,y=636-q*150;c.beginPath();c.moveTo(x,y);c.bezierCurveTo(x-23,y-22,x+31,y-34,x+5,y-57);c.strokeStyle=`rgba(240,237,207,${(1-q)*.47})`;c.lineWidth=4+q*9;c.stroke();}
  // A hanging shop cloth responds to the tram's wake, with a fixed top seam.
  let wind=Math.sin(t*2)*10+18*Math.exp(-Math.pow((t-3)/1.5,2));c.beginPath();c.moveTo(57,84);c.lineTo(256,84);c.bezierCurveTo(244,161,270+wind,235,248+wind,312);c.quadraticCurveTo(153+wind,333,65+wind*.7,310);c.bezierCurveTo(74+wind,217,54,144,57,84);c.closePath();c.fillStyle='#839c8fe8';c.fill();c.strokeStyle='#5a7a6d';c.lineWidth=2;c.stroke();for(let i=0;i<6;i++){c.beginPath();c.moveTo(78+i*30,85);c.quadraticCurveTo(65+i*30+wind*.5,196,78+i*30+wind,315);c.strokeStyle='#b8c4a078';c.lineWidth=2;c.stroke();}
  // Dust only where morning light catches it, not a whole-frame particle layer.
  for(let i=0;i<23;i++){let x=525+(i*47)%510+Math.sin(t*.4+i)*8,y=703+(i*73)%280-Math.sin(t*.3+i)*9;E(c,x,y,1.2,1.2,'#fff0c0aa');}
 }};
})();
