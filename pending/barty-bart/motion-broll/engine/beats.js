// NODE_PATH=motion/node_modules node beats.js dist/clip.html out/sheet.png t1 t2 ... -> contact sheet of stills at those times
const {chromium}=require('playwright');const path=require('path');const os=require('os');const {execFileSync}=require('child_process');const fs=require('fs');
(async()=>{const [html,out,...ts]=process.argv.slice(2);
 if(!html||!out||!ts.length){console.error('usage: node beats.js clip.html sheet.png t1 [t2 ...]');process.exit(2);}
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.goto('file://'+path.resolve(html)+'?render');await p.evaluate(()=>document.fonts.ready);
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'beats-'));const alpha=await p.evaluate(()=>{const a=document.documentElement.classList.contains('alpha');if(a){document.documentElement.style.background='#000';document.body.style.background='#000';}return a;});
 try{
  for(let i=0;i<ts.length;i++){await p.evaluate(t=>seek(t),+ts[i]);await p.screenshot({path:path.join(dir,`${String(i).padStart(3,'0')}.png`)});}
  await b.close();
  const cols=Math.min(4,ts.length),rows=Math.ceil(ts.length/cols);
  execFileSync('ffmpeg',['-loglevel','error','-y','-i',path.join(dir,'%03d.png'),'-vf',`scale=640:-1,tile=${cols}x${rows}:padding=4:color=white`,'-frames:v','1',out],{stdio:'inherit'});
 }finally{fs.rmSync(dir,{recursive:true,force:true});}
 if(errs.length){console.error('ERR',errs);process.exit(1);}})().catch(e=>{console.error(e);process.exit(1);});
