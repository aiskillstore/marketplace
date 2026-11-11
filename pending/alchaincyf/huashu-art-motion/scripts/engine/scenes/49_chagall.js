// Original scene; fixed pigment seed, continuous object motion, arbitrary-seek safe.
SCENES['49_chagall'] = (() => {
  const W=1920,H=1080,TAU=Math.PI*2;
  const rng=(seed)=>()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
  const canvas=(w=W,h=H)=>{const a=document.createElement('canvas');a.width=w;a.height=h;return a;};
  const poly=(g,pts,col)=>{g.fillStyle=col;g.beginPath();pts.forEach((p,i)=>i?g.lineTo(...p):g.moveTo(...p));g.closePath();g.fill();};
  const shape=(g,d,col,stroke=null,width=2)=>{const p=new Path2D(d);g.fillStyle=col;g.fill(p);if(stroke){g.strokeStyle=stroke;g.lineWidth=width;g.stroke(p);}return p;};
  const oval=(g,x,y,rx,ry,col,a=0)=>{g.fillStyle=col;g.beginPath();g.ellipse(x,y,rx,ry,a,0,TAU);g.fill();};
  const line=(g,pts,col,w=2)=>{g.strokeStyle=col;g.lineWidth=w;g.lineCap='round';g.beginPath();pts.forEach((p,i)=>i?g.lineTo(...p):g.moveTo(...p));g.stroke();};
  function paint(src,seed,cell,len,angle,amount=17){
    const out=canvas(src.width,src.height),g=out.getContext('2d'),s=src.getContext('2d',{willReadFrequently:true}),ww=src.width,hh=src.height,data=s.getImageData(0,0,ww,hh).data,r=rng(seed);
    g.drawImage(src,0,0);g.lineCap='butt';
    for(let yy=0;yy<hh+cell;yy+=cell)for(let xx=0;xx<ww+cell;xx+=cell){
      const x=xx+(r()-.5)*cell*1.8,y=yy+(r()-.5)*cell*1.8,ix=Math.min(ww-1,Math.max(0,x|0)),iy=Math.min(hh-1,Math.max(0,y|0)),i=(iy*ww+ix)*4;if(data[i+3]<200)continue;
      const a=angle(x,y)+(r()-.5)*.45,l=len*(.5+r()),q=(r()-.5)*amount,rr=data[i]+q,gg=data[i+1]+q*.8,bb=data[i+2]+q*.65;
      g.strokeStyle=`rgba(${rr|0},${gg|0},${bb|0},.68)`;g.lineWidth=cell*(.55+r()*.65);g.beginPath();g.moveTo(x-Math.cos(a)*l/2,y-Math.sin(a)*l/2);g.quadraticCurveTo(x,y+(r()-.5)*3,x+Math.cos(a)*l/2,y+Math.sin(a)*l/2);g.stroke();
      if(r()<.22){g.strokeStyle=`rgba(${(rr+17)|0},${(gg+15)|0},${(bb+10)|0},.3)`;g.lineWidth=.7;g.stroke();}
    }
    // Fine weave remains stationary in the object coordinate system.
    g.globalAlpha=.035;g.strokeStyle='#fff4d6';g.lineWidth=.6;for(let y=1;y<hh;y+=3){g.beginPath();g.moveTo(0,y);g.lineTo(ww,y);g.stroke();}g.globalAlpha=1;return out;
  }
  let bg,bouquet,caseBase,lid,letter;
  function house(g,x,y,w,h,a,wall,roof){g.save();g.translate(x,y);g.rotate(a);shape(g,`M${-w/2} 0 L${-w/2} ${-h} L${w/2} ${-h-8} L${w/2} 0Z`,wall,'#3c426c',3);shape(g,`M${-w/2-15} ${-h} L-4 ${-h-w*.55} L${w/2+18} ${-h-7}Z`,roof,'#54405d',3);const n=w>140?3:2;for(let j=0;j<2;j++)for(let i=0;i<n;i++){const xx=-w/2+18+i*(w-32)/n,yy=-h+24+j*(h-36)/2;g.fillStyle=j%2?'#e2cb8a':'#a1c8bf';g.fillRect(xx,yy,w/n*.38,h*.19);line(g,[[xx+w/n*.18,yy],[xx+w/n*.18,yy+h*.19]],'#78616d',2);}line(g,[[-w/2+3,-h+5],[-w/2+3,-5]],'#b8c4b4',2);g.restore();}
  function init(){if(bg)return;const a=canvas(),g=a.getContext('2d',{willReadFrequently:true}),r=rng(491);
    let gr=g.createLinearGradient(0,0,1700,1000);gr.addColorStop(0,'#153f81');gr.addColorStop(.45,'#2a4a93');gr.addColorStop(1,'#66517e');g.fillStyle=gr;g.fillRect(0,0,W,H);
    // Translucent emotional colour zones, full of stationary dry pigment.
    shape(g,'M0 0 L770 0 Q650 230 791 482 Q387 463 0 870Z','#224f8b');shape(g,'M1323 0 L1920 0 L1920 666 Q1590 587 1438 358 Q1263 230 1323 0Z','#4d7d8555');shape(g,'M0 857 Q380 719 751 848 Q1098 995 1455 769 Q1700 608 1920 764 L1920 1080 L0 1080Z','#625480');
    for(let i=0;i<18000;i++){const x=r()*W,y=r()*H,aa=r()*TAU;line(g,[[x,y],[x+Math.cos(aa)*(3+r()*23),y+Math.sin(aa)*(3+r()*23)]],['#7d93b31b','#142d681a','#596eae22','#b381a419'][i%4],1+r()*5);}
    oval(g,1547,185,80,87,'#c9d6ac',-.15);shape(g,'M1536 99 Q1460 159 1524 242 Q1465 220 1465 165 Q1472 115 1536 99Z','#8fbdab');
    for(let i=0;i<120;i++){const x=60+r()*1800,y=35+r()*580;oval(g,x,y,1+r()*2,1+r()*2,['#c7d3bb88','#d4b78b77','#8cc2c0aa'][i%3]);}
    // A street bends upward into remembered architecture; each roof has a different axis.
    for(let i=0;i<9;i++){const x=890+i*122,y=1000-Math.sin(i*.35)*170;house(g,x,y,116+r()*62,140+r()*90,-.12+i*.07,['#73918d','#b9a1a0','#8b95af','#b29a82'][i%4],['#9a5365','#c66e6d','#597d91'][i%3]);}
    house(g,1535,561,268,229,-.34,'#a2bdaf','#b95369');house(g,1840,409,179,170,.28,'#96b6aa','#9d5d77');
    // A door hangs in memory above its own pavement; no borrowed character symbols.
    shape(g,'M1140 719 L1165 477 L1297 485 L1283 735Z','#517993','#283e6b',4);shape(g,'M1160 704 L1178 491 L1282 498 L1272 716Z','#87a2a3');shape(g,'M1193 689 L1195 511 L1267 510 L1257 702Z','#d5b998');oval(g,1244,613,4,5,'#755e72');
    // Fine chalk/pigment traces do not move independently of the houses.
    line(g,[[1010,1040],[1168,930],[1430,928],[1628,879],[1920,972]],'#a69ea155',4);
    for(let i=0;i<60;i++){let x=850+r()*1060,y=880+r()*200;line(g,[[x,y],[x+8+r()*26,y-8]],['#9e8b9f77','#b4a8a966','#574b7a66'][i%3],2);}
    bg=paint(a,4901,6,19,(x,y)=>y>800?-.2:Math.sin(x*.003+y*.004)*.8,16);
    const b=canvas(700,900),q=b.getContext('2d',{willReadFrequently:true}),rr=rng(494);
    // An oversized bouquet is the memory of a garden, distinct from literal village scale.
    const flowers=[[195,240,67,'#d7b7c3'],[382,127,92,'#b85e86'],[501,334,74,'#e8cfb5'],[268,440,74,'#bd6387'],[419,464,63,'#b4ccd0'],[125,416,61,'#e1c9bf']];
    for(const [x,y,sz,col] of flowers){line(q,[[341,885],[329+(x-330)*.3,610],[x,y]],'#668b8a',7);line(q,[[342,881],[332+(x-330)*.3,610],[x+4,y]],'#96a497',2);for(let j=0;j<11;j++){const aa=j*TAU/11+rr()*.25,rx=x+Math.cos(aa)*sz*.48,ry=y+Math.sin(aa)*sz*.43;oval(q,rx,ry,sz*(.3+rr()*.2),sz*(.18+rr()*.17),col,aa);line(q,[[x,y],[rx+Math.cos(aa)*sz*.2,ry+Math.sin(aa)*sz*.2]],'#f0d7c23c',2);}oval(q,x,y,sz*.2,sz*.17,'#a78568');for(let k=0;k<30;k++){const aa=rr()*TAU,ra=rr()*sz*.2;oval(q,x+Math.cos(aa)*ra,y+Math.sin(aa)*ra,2,2,k%2?'#dec89d':'#706b76');}}
    for(let i=0;i<18;i++){const y=520+i*18,x=330+Math.sin(i*1.4)*60,dir=i%2?-1:1;shape(q,`M${x} ${y} Q${x+dir*105} ${y-83} ${x+dir*104} ${y-26} Q${x+dir*72} ${y+29} ${x} ${y}Z`,['#567d80','#7c9d92','#3e7079'][i%3]);line(q,[[x,y],[x+dir*87,y-34]],'#99b09b',2);}
    bouquet=paint(b,4904,4,12,(x,y)=>Math.atan2(y-450,x-335)+.6,17);
    const cb=canvas(640,260),v=cb.getContext('2d',{willReadFrequently:true});shape(v,'M16 43 Q310 20 610 54 L626 194 Q327 246 30 197Z','#7b4f62','#463e63',5);shape(v,'M25 49 Q316 27 600 59 L586 106 Q311 156 40 105Z','#b88f85');shape(v,'M36 57 Q316 40 590 68 L577 94 Q310 134 49 98Z','#524763');for(const x of [116,486]){shape(v,`M${x} 104 L${x+29} 105 L${x+37} 209 L${x+8} 213Z`,'#bba18d');g.fillStyle='#fff';}shape(v,'M266 174 Q272 143 355 154 L362 183 L347 185 L344 168 L283 167 L281 184Z','#b6a28a');for(let i=0;i<100;i++){const xx=45+rr()*540,yy=123+rr()*68;line(v,[[xx,yy],[xx+4+rr()*12,yy]],'#bd8f801f',2);}caseBase=paint(cb,4905,4,11,()=>.05,12);
    const ld=canvas(640,330),z=ld.getContext('2d',{willReadFrequently:true});shape(z,'M25 300 L42 38 Q318 0 590 40 L612 303Z','#976c79','#453f66',5);shape(z,'M45 286 L58 55 Q317 20 575 56 L593 287Z','#b89a98');shape(z,'M65 272 L74 70 Q317 41 560 70 L576 271Z','#b4a2a5');for(let j=0;j<12;j++)line(z,[[75,78+j*16],[562,77+j*16]],'#897b911f',3);shape(z,'M159 104 L482 109 L478 228 L165 233Z','#a58297','#c6b0a9',3);shape(z,'M215 118 L428 127 L420 211 L211 202Z','#c2c5b2');shape(z,'M213 179 L259 151 L301 168 L337 146 L423 181 L420 211 L211 202Z','#788f9c');shape(z,'M213 190 Q292 169 420 192 L420 211 L211 202Z','#94ac92');for(let j=0;j<30;j++){line(z,[[165+j*10,110],[168+j*10,114]],'#d8c0b0',1);line(z,[[165+j*10,226],[168+j*10,230]],'#d8c0b0',1);}lid=paint(ld,4906,4,12,()=>0,12);
    const e=canvas(118,86),u=e.getContext('2d',{willReadFrequently:true});shape(u,'M5 9 L111 3 L116 76 L9 82Z','#dfc9ad','#ab8996',1.5);line(u,[[7,10],[61,46],[109,5]],'#9c8c98',2);line(u,[[10,80],[47,39]],'#baa8a3',1.5);line(u,[[113,76],[74,39]],'#baa8a3',1.5);letter=paint(e,4907,2.8,7,()=>.1,9);
  }
  function pos(p){const u=1-p;return [u*u*u*530+3*u*u*p*880+3*u*p*p*900+p*p*p*1255,u*u*u*890+3*u*u*p*200+3*u*p*p*170+p*p*p*575];}
  return {draw(c,lt){init();const t=Math.max(0,lt);c.drawImage(bg,0,0);
    // The bouquet grows out of the open case as its lid lifts, then breathes in the wind.
    const open=.56+.32*(.5-.5*Math.cos(Math.min(t/2.2,1)*Math.PI));c.save();c.translate(255,920);c.transform(1,-.08,-.13,open,0,0);c.drawImage(lid,0,-300);c.restore();
    c.save();c.translate(625,1000);c.rotate(-.14+Math.sin(t*.75)*.016);c.scale(.94,.94);c.drawImage(bouquet,-350,-890);c.restore();
    for(let i=0;i<7;i++){const p=(t*.135+i/7)%1,[x,y]=pos(p),sc=.48+Math.sin(p*Math.PI)*.32;c.save();c.translate(x,y);c.rotate(-.35+Math.sin(p*9+i)*.5);c.scale(sc,sc);c.drawImage(letter,-59,-43);c.restore();}
    c.save();c.translate(258,877);c.rotate(-.07);c.drawImage(caseBase,0,0);c.restore();
    // Petals are independent light fragments; their motion never re-seeds the canvas.
    for(let i=0;i<11;i++){const p=(t*.1+i*.091)%1,xx=590+p*570+Math.sin(p*7+i)*28,yy=370+p*540;oval(c,xx,yy,5+i%3*2,2.5,['#d9b1c6','#bca5c2','#e5ccbd'][i%3],p*5+i);}
  }};
})();
