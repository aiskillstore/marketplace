// JMC skill-pack card renderer. Vendored per repo so it cannot break from a deleted shared workflow.
// Renders assets/social-preview.png (1280x640) and assets/header.png (1280x320) from assets/spec.json.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';

const CHROME = process.env.CHROME_BIN
  || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

const BRAND = {
  bg: '#060609', markBg: '#0A0E12', surface: '#0C0C14', fg: '#EAEAF0',
  primary: '#00D4FF', secondary: '#CC4714', accent: '#8B5CF6',
  border: '#252542', success: '#10B981',
};

function html(spec, { w, h, variant }) {
  const accent = spec.accent_color || BRAND.primary;
  const pad = variant === 'header' ? 56 : 72;
  const titleMax = variant === 'header' ? 76 : 96;
  const showProof = variant !== 'header';
  return `<!doctype html><html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700&family=DM+Sans:opsz,wght@9..40,400;9..40,500&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{width:${w}px;height:${h}px;overflow:hidden}
  body{background:${spec.dot ? BRAND.markBg : BRAND.bg};color:${BRAND.fg};
    font-family:'DM Sans',system-ui,sans-serif;-webkit-font-smoothing:antialiased}
  .card{position:relative;width:${w}px;height:${h}px;display:flex;flex-direction:column;
    align-items:center;justify-content:center;text-align:center;padding:${pad}px;gap:${variant==='header'?14:18}px}
  .grid{position:absolute;inset:0;background-image:
      linear-gradient(${BRAND.border} 1px,transparent 1px),
      linear-gradient(90deg,${BRAND.border} 1px,transparent 1px);
    background-size:60px 60px;opacity:.28}
  .glow{position:absolute;inset:0;background:
    radial-gradient(60% 70% at 50% 38%, ${accent}1F 0%, transparent 62%)}
  .bar{position:absolute;left:0;right:0;height:3px;
    background:linear-gradient(90deg,${accent}99 0%,${BRAND.accent} 50%,${BRAND.secondary}99 100%)}
  .bar.t{top:0}.bar.b{bottom:0}
  .inner{position:relative;display:flex;flex-direction:column;align-items:center;gap:inherit;max-width:100%}
  .eyebrow{font-family:'IBM Plex Mono',monospace;font-size:${variant==='header'?15:17}px;
    font-weight:500;letter-spacing:.22em;text-transform:uppercase;color:${accent}}
  h1{font-family:'Syne',system-ui,sans-serif;font-weight:700;line-height:1.06;
    letter-spacing:-.025em;color:#EAEAF0;font-size:${titleMax}px;white-space:nowrap;
    display:inline-block}
  .sub{font-size:${variant==='header'?21:25}px;color:${BRAND.fg}B3;line-height:1.35;max-width:${w-pad*2}px}
  .proof{display:flex;align-items:center;gap:14px;margin-top:6px;padding:11px 20px;
    border:1px solid ${BRAND.border};border-radius:999px;background:${BRAND.surface}CC}
  .proof .dot{width:7px;height:7px;border-radius:50%;background:${BRAND.success};flex:none}
  .proof span{font-family:'IBM Plex Mono',monospace;font-size:16px;color:${BRAND.fg}D9;white-space:nowrap}
  .dot{display:inline-block;width:.1525em;height:.115em;margin-left:.02em;
    background:#00D4FF;vertical-align:baseline;
    box-shadow:0 0 12px rgba(0,212,255,.20),0 0 20px rgba(0,212,255,.15),0 0 60px rgba(0,212,255,.05)}
  .cta{margin-top:${variant==='header'?4:10}px;font-family:'IBM Plex Mono',monospace;
    font-size:${variant==='header'?15:17}px;color:${accent};letter-spacing:.02em;white-space:nowrap}
</style></head><body>
<div class="card">
  <div class="grid"></div><div class="glow"></div>
  <div class="bar t"></div><div class="bar b"></div>
  <div class="inner">
    <div class="eyebrow">${esc(spec.tagline_top || 'JMC Skill Pack')}</div>
    <h1 id="t">${esc(spec.title)}${spec.dot ? '<i class="dot"></i>' : ''}</h1>
    <div class="sub">${esc(spec.subtitle)}</div>
    ${showProof && spec.proof ? `<div class="proof"><i class="dot"></i><span>${esc(spec.proof)}</span></div>` : ''}
    ${spec.cta ? `<div class="cta">${esc(spec.cta)}</div>` : ''}
  </div>
</div>
<script>
  // Auto-fit the title. Waits for webfonts, measures the true (unconstrained)
  // text box, then falls back to two lines before it ever clips.
  (function(){
    var t=document.getElementById('t'), avail=${w - pad*2}, max=${titleMax}, floor=${Math.round(titleMax*0.72)}, min=34;
    function wid(){ return t.getBoundingClientRect().width; }
    function hgt(){ return t.getBoundingClientRect().height; }
    function run(){
      for(var s=max; s>=floor; s--){ t.style.fontSize=s+'px'; if(wid()<=avail) return done(); }
      t.style.whiteSpace='normal';            // two lines beat a shrunken headline
      t.style.maxWidth=avail+'px';
      for(var s2=max; s2>=min; s2--){ t.style.fontSize=s2+'px';
        if(wid()<=avail && hgt()<=s2*2.25) return done(); }
      done();
    }
    function done(){ document.documentElement.setAttribute('data-fitted','1'); }
    if(document.fonts && document.fonts.ready) document.fonts.ready.then(run); else run();
  })();
</script></body></html>`;
}
const esc = s => String(s).replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));

export function render(specPath, outDir, targets) {
  const spec = JSON.parse(readFileSync(specPath, 'utf8'));
  mkdirSync(outDir, { recursive: true });
  for (const t of targets) {
    const tmp = join(outDir, `.${t.name}.html`);
    writeFileSync(tmp, html(spec, t));
    execFileSync(CHROME, [
      '--headless', '--disable-gpu', '--hide-scrollbars', '--force-color-profile=srgb',
      `--window-size=${t.w},${t.h}`, '--force-device-scale-factor=2',
      '--virtual-time-budget=8000',
      `--screenshot=${join(outDir, t.name + '.png')}`,
      'file://' + tmp,
    ], { stdio: 'pipe' });
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const specPath = process.argv[2], outDir = process.argv[3] || dirname(specPath);
  render(specPath, outDir, [
    { name: 'social-preview', w: 1280, h: 640, variant: 'social' },
    { name: 'header',         w: 1280, h: 320, variant: 'header' },
  ]);
  console.log('rendered ->', outDir);
}
