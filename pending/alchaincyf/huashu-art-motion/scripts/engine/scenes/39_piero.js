SCENES['39_piero']=(()=>{
  const TAU=Math.PI*2; let bg,grain,raw;
  const rng=(s)=>()=>{s=(Math.imul(s,1664525)+1013904223)|0;return (s>>>0)/4294967296;};
  function path(c,d,col,st,lw=2){const p=new Path2D(d);if(col){c.fillStyle=col;c.fill(p);}if(st){c.strokeStyle=st;c.lineWidth=lw;c.stroke(p);}return p;}
  function poly(c,pts,col,st,lw=2){c.beginPath();pts.forEach((p,i)=>i?c.lineTo(...p):c.moveTo(...p));c.closePath();if(col){c.fillStyle=col;c.fill();}if(st){c.strokeStyle=st;c.lineWidth=lw;c.stroke();}}
  function el(c,x,y,rx,ry,col,st,lw=2){c.beginPath();c.ellipse(x,y,rx,ry,0,0,TAU);if(col){c.fillStyle=col;c.fill();}if(st){c.strokeStyle=st;c.lineWidth=lw;c.stroke();}}
  function line(c,pts,col,w=2){c.beginPath();pts.forEach((p,i)=>i?c.lineTo(...p):c.moveTo(...p));c.strokeStyle=col;c.lineWidth=w;c.stroke();}
  function grad(c,x,y,X,Y,colors){const g=c.createLinearGradient(x,y,X,Y);colors.forEach((a,i)=>g.addColorStop(i/(colors.length-1),a));return g;}
  function layer(fn){let a=document.createElement('canvas');a.width=1920;a.height=1080;fn(a.getContext('2d'));return a;}
  function finish(c){if(!grain)grain=layer(g=>{let r=rng(7891);for(let i=0;i<21000;i++){g.fillStyle=i%3?'rgba(49,32,22,.045)':'rgba(255,248,220,.08)';let x=r()*1920,y=r()*1080;g.fillRect(x,y,1+r()*2.4,1+r()*1.5);}});c.drawImage(grain,0,0);}

  function back(c){
    c.fillStyle=grad(c,0,0,0,1080,['#c3d4d3','#e0e0cd']);c.fillRect(0,0,1920,1080);
    // A contemporary measuring hall, ordered through repeated intervals rather than antique iconography.
    c.fillStyle='#d9d2b9';c.fillRect(0,80,1920,660);
    for(let x=100;x<1920;x+=420){c.fillStyle='#718c8c';c.fillRect(x,153,274,451);c.fillStyle=grad(c,0,150,0,610,['#b5cccf','#edf0d8']);c.fillRect(x+14,166,246,424);for(let j=0;j<3;j++)line(c,[[x+15,270+j*105],[x+259,270+j*105]],'#d7d8c4',7);line(c,[[x+138,165],[x+138,590]],'#d6d8c6',9);}
    poly(c,[[0,0],[1920,0],[1920,84],[0,84]],'#6b827e');c.fillStyle='#eee5cd';c.fillRect(0,78,1920,23);
    for(let x=20;x<1920;x+=420){c.fillStyle=grad(c,x,0,x+64,0,['#b1b19b','#e8e0c7','#c4bea8']);c.fillRect(x,101,64,620);c.fillStyle='#b3ac97';c.fillRect(x-10,690,85,37);}
    poly(c,[[0,735],[1920,735],[1920,1080],[0,1080]],'#d2c5a5');
    const vx=1010,vy=550;for(let x=-1800;x<4200;x+=260)line(c,[[vx+(x-vx)*.38,735],[x,1080]],'#a89e85',2);for(let y of [762,803,861,945,1060])line(c,[[0,y],[1920,y]],'#a89e85',2);
    // Stacked instruments inhabit different measured planes.
    poly(c,[[1310,718],[1650,682],[1820,754],[1485,811]],'#d3d0b8','#9a9f90',2);poly(c,[[1485,811],[1820,754],[1820,970],[1485,1042]],'#a6b0a3');poly(c,[[1310,718],[1485,811],[1485,1042],[1310,935]],'#b8b9a3');
    for(let y=836;y<1010;y+=42)line(c,[[1504,y],[1793,y-60]],'#81968f',3);
    c.fillStyle='#b7a889';c.fillRect(120,689,375,226);poly(c,[[120,689],[354,638],[535,682],[300,739]],'#e5d5b0');poly(c,[[300,739],[535,682],[535,910],[300,966]],'#8e9d90');
    let r=rng(391);for(let i=0;i<1400;i++){c.fillStyle=i%2?'rgba(255,255,228,.06)':'rgba(70,91,83,.04)';c.fillRect(r()*1920,r()*1080,1+r()*18,1);}
  }
  function sphere(c,x,y,r,col){let g=c.createRadialGradient(x-r*.4,y-r*.45,2,x,y,r);g.addColorStop(0,'#f3ebcc');g.addColorStop(.45,col);g.addColorStop(1,'#647d77');el(c,x,y,r,r,g);}
  return {draw(dst,lt){if(!raw)raw=layer(()=>{});const c=raw.getContext('2d',{willReadFrequently:true});c.reset();if(!bg)bg=layer(back);c.drawImage(bg,0,0);const t=lt;
    el(c,878,927,341,62,'rgba(85,100,88,.14)');
    // Plinth, precisely vertical axis and a suspended mechanical planetary model.
    poly(c,[[560,868],[898,802],[1180,880],[829,971]],'#ded8bb','#88988a',2);poly(c,[[560,868],[829,971],[829,1053],[560,947]],'#b2b79e');poly(c,[[829,971],[1180,880],[1180,964],[829,1053]],'#8e9c8b');
    c.fillStyle=grad(c,835,0,902,0,['#7c968b','#d8d9bd','#a4b19c']);c.fillRect(835,533,67,359);el(c,868,893,113,29,'#bec4aa','#819589',3);
    c.save();c.translate(868,444);
    // Meridian rings, with alternate back and front arcs around the central orb.
    c.save();c.rotate(-.35+t*.18);for(let i=0;i<3;i++){c.beginPath();c.ellipse(0,0,287-i*7,310-i*7,0,0,TAU);c.strokeStyle=i===1?'#d9c79a':'#7e8a71';c.lineWidth=i===1?13:3;c.stroke();}for(let j=0;j<64;j++){let a=j*TAU/64;line(c,[[Math.cos(a)*292,Math.sin(a)*315],[Math.cos(a)*(j%4?280:272),Math.sin(a)*(j%4?303:295)]],'#8a8f74',2);}c.restore();
    const a=t*.43,px=Math.cos(a)*251,py=Math.sin(a)*87;
    c.beginPath();c.ellipse(0,0,318,111,-.15,Math.PI,TAU);c.strokeStyle='#a89e79';c.lineWidth=10;c.stroke();
    line(c,[[0,0],[px,py]],'#8f987d',9);if(py<0)sphere(c,px,py,43,'#b87959');
    sphere(c,0,0,119,'#c5b979');
    // Very restrained latitude bands maintain rounded, clear volume.
    c.save();c.beginPath();c.arc(0,0,119,0,TAU);c.clip();for(let y=-80;y<110;y+=40)el(c,0,y,118,25,null,'rgba(100,120,94,.17)',2);c.restore();
    if(py>=0)sphere(c,px,py,43,'#b87959');
    c.beginPath();c.ellipse(0,0,318,111,-.15,0,Math.PI);c.strokeStyle='#d0bd8f';c.lineWidth=10;c.stroke();
    const b=-t*.69+1.4;let qx=Math.cos(b)*173,qy=Math.sin(b)*260;
    c.save();c.rotate(.68);c.beginPath();c.ellipse(0,0,173,260,0,0,TAU);c.strokeStyle='#9da98d';c.lineWidth=5;c.stroke();sphere(c,qx,qy,20,'#9ab6af');c.restore();
    el(c,0,-325,10,10,'#a39d76');el(c,0,325,10,10,'#a39d76');c.restore();
    // Displaced secondary objects form unequal but balanced intervals.
    sphere(c,1606,640,85,'#9aafa3');el(c,1606,727,91,13,'#8d9a88');
    c.save();c.translate(327,625);c.rotate(-.12+Math.sin(t*.45)*.045);poly(c,[[-125,-12],[108,-12],[108,16],[-125,16]],'#83988e','#687d76',2);el(c,111,0,14,35,'#5e7877','#c5c8af',7);for(let i=-105;i<100;i+=22)line(c,[[i,-9],[i,4]],'#d9d9be',2);c.restore();
    for(let i=0;i<24;i++){let y=330+(i*39)%400,x=200+(i*127)%1450;el(c,x+Math.sin(t*.35+i)*6,y-((t*5+i*13)%27),1.2,1.2,'rgba(255,255,230,.32)');}
    finish(c);dst.drawImage(raw,0,0);dst.save();dst.globalAlpha=0.18;PAINT.strokes(dst,raw,{cell:7,len:9,width:4,jitterCol:5,angle:(x,y)=>-.45,seed:39,boil:0,outline:0});dst.restore();
  }};
})();
