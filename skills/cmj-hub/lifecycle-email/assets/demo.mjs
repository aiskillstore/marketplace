// Terminal-sim demo GIF for a JMC skill pack.
// Frames are driven from one browser session; ffmpeg assembles the palette + gif.
import { chromium } from './node_modules/playwright-core/index.mjs';
import { readFileSync, writeFileSync, mkdirSync, rmSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { join } from 'node:path';

const W = 960, H = 540, FPS = 12;
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

const page_html = (s) => {
const accent = s.accent_color || '#00D4FF';
const resp = JSON.stringify(s.response_lines || []);
const art  = JSON.stringify(s.artifact || null);
return `<!doctype html><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700&family=DM+Sans:opsz,wght@9..40,400&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:${W}px;height:${H}px;overflow:hidden;background:#060609}
.stage{position:relative;width:${W}px;height:${H}px;background:#060609;
  font-family:'IBM Plex Mono',monospace;color:#EAEAF0}
.grid{position:absolute;inset:0;background-image:
  linear-gradient(#252542 1px,transparent 1px),linear-gradient(90deg,#252542 1px,transparent 1px);
  background-size:48px 48px;opacity:.22}
.glow{position:absolute;inset:0;background:radial-gradient(55% 60% at 50% 35%, ${accent}1A 0%, transparent 60%)}
.bar{position:absolute;left:0;right:0;height:3px;background:linear-gradient(90deg,${accent}99,#8B5CF6,#CC471499)}
.bar.t{top:0}.bar.b{bottom:0}
.hd{position:absolute;top:16px;left:26px;right:26px;display:flex;justify-content:space-between;
  font-size:11px;letter-spacing:.18em;font-weight:500}
.hd .l{color:${accent}}.hd .r{color:#EAEAF080}
.win{position:absolute;left:26px;right:26px;top:48px;bottom:34px;border:1px solid #252542;
  border-radius:10px;background:#0C0C14;overflow:hidden}
.tb{height:30px;display:flex;align-items:center;gap:7px;padding:0 12px;border-bottom:1px solid #252542}
.tb i{width:9px;height:9px;border-radius:50%;display:block}
.tb .p{margin-left:10px;font-size:11px;color:#EAEAF066}
.body{padding:14px 16px;font-size:13.5px;line-height:1.85}
.cmd{color:#EAEAF0}.cmd .pr{color:${accent};margin-right:7px}
.cur{display:inline-block;width:7px;height:15px;background:${accent};vertical-align:-2px}
.ln{color:#EAEAF0B3;padding-left:16px}.ln b{color:${accent};font-weight:400;margin-right:8px}
.ok{color:#10B981}
.art{margin-top:11px;border:1px solid ${accent}66;border-radius:7px;background:#060609;overflow:hidden}
.art .h{padding:6px 11px;font-size:11.5px;color:${accent};border-bottom:1px solid ${accent}33}
.art .c{padding:9px 11px;font-size:12.5px;line-height:1.7;color:#EAEAF0CC;white-space:pre-wrap}
.end{position:absolute;inset:0;background:#060609;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:13px;text-align:center;padding:56px;opacity:0}
.end .eb{font-size:12px;letter-spacing:.22em;color:${accent};font-weight:500;text-transform:uppercase}
.end h1{font-family:'Syne',sans-serif;font-weight:700;font-size:52px;color:#EAEAF0;letter-spacing:-.025em;line-height:1.05}
.end .sb{font-family:'DM Sans',sans-serif;font-size:17px;color:#EAEAF0B3}
.end .pf{margin-top:3px;padding:8px 15px;border:1px solid #252542;border-radius:999px;
  background:#0C0C14;font-size:12.5px;color:#EAEAF0D9}
.end .ct{margin-top:5px;font-size:13px;color:${accent}}
</style>
<div class="stage">
  <div class="grid"></div><div class="glow"></div><div class="bar t"></div><div class="bar b"></div>
  <div class="hd"><span class="l">JMC SKILL PACK</span><span class="r" id="hr"></span></div>
  <div class="win" id="win">
    <div class="tb"><i style="background:#CC4714"></i><i style="background:#E5A50A"></i><i style="background:#10B981"></i>
      <span class="p">~/projects · agent</span></div>
    <div class="body"><div class="cmd"><span class="pr">&gt;</span><span id="typed"></span><span class="cur" id="cur"></span></div>
      <div id="lines"></div><div id="artwrap"></div></div>
  </div>
  <div class="end" id="end">
    <div class="eb" id="e1"></div><h1 id="e2"></h1><div class="sb" id="e3"></div>
    <div class="pf" id="e4"></div><div class="ct" id="e5"></div>
  </div>
</div>
<script>
const S=${JSON.stringify(s)}, RESP=${resp}, ART=${art};
document.getElementById('hr').textContent = 'AGENT · ' + S.command;
document.getElementById('e1').textContent = S.tagline_top || 'JMC Skill Pack';
document.getElementById('e2').textContent = S.title;
document.getElementById('e3').textContent = S.subtitle;
document.getElementById('e4').textContent = S.proof || '';
document.getElementById('e5').textContent = S.cta || '';
const FULL = S.command + ' ' + (S.user_prompt||'');
// timeline (seconds)
const T_TYPE0=0.35, T_TYPE1=2.5, T_L0=2.7, T_LSTEP=0.42;
const T_ART = T_L0 + RESP.length*T_LSTEP + 0.25;
const T_HOLD = T_ART + 1.5, T_END0 = T_HOLD + 0.5, T_END1 = T_END0 + 0.7;
window.DURATION = T_END1 + 2.0;
window.render = (t) => {
  const n = t<=T_TYPE0 ? 0 : Math.min(FULL.length,
    Math.round(FULL.length*(t-T_TYPE0)/(T_TYPE1-T_TYPE0)));
  document.getElementById('typed').textContent = FULL.slice(0,n);
  document.getElementById('cur').style.opacity = (t<T_ART && Math.floor(t*2)%2===0) ? 1 : (t<T_ART?0:0);
  let h='';
  RESP.forEach((L,i)=>{ if(t >= T_L0 + i*T_LSTEP){
    const done = t >= T_L0 + (i+1)*T_LSTEP - 0.05;
    h += '<div class="ln"><b>'+(done?'●':'○')+'</b>'+L+'</div>'; }});
  document.getElementById('lines').innerHTML = h;
  document.getElementById('artwrap').innerHTML = (ART && t>=T_ART)
    ? '<div class="art"><div class="h">+ '+ART.label+'</div><div class="c">'+ART.lines.join('\\n')+'</div></div>' : '';
  const e = t<=T_END0 ? 0 : Math.min(1,(t-T_END0)/(T_END1-T_END0));
  document.getElementById('end').style.opacity = e;
  document.getElementById('win').style.opacity = 1-e;
};
</script>`;
};

const spec = JSON.parse(readFileSync(process.argv[2],'utf8'));
const outGif = process.argv[3];
const tmp = outGif + '.frames'; rmSync(tmp,{recursive:true,force:true}); mkdirSync(tmp,{recursive:true});
const htmlPath = outGif + '.html'; writeFileSync(htmlPath, page_html(spec));

const b = await chromium.launch({ executablePath: CHROME });
const pg = await b.newPage({ viewport:{width:W,height:H}, deviceScaleFactor:1 });
await pg.goto('file://'+htmlPath);
await pg.evaluate(()=>document.fonts.ready);
const dur = await pg.evaluate(()=>window.DURATION);
const N = Math.round(dur*FPS);
for (let i=0;i<N;i++){
  await pg.evaluate(t=>window.render(t), i/FPS);
  await pg.screenshot({ path: join(tmp, String(i).padStart(4,'0')+'.png') });
}
await b.close();
execFileSync('ffmpeg',['-y','-loglevel','error','-framerate',String(FPS),'-i',join(tmp,'%04d.png'),
  '-filter_complex','[0:v]split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=3',
  '-loop','0', outGif]);
rmSync(tmp,{recursive:true,force:true});
console.log('gif:', outGif, N, 'frames', (dur).toFixed(1)+'s');
