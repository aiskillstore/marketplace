"""Writes report.html after a sound pass: every cue with the sound used, source, licence,
play buttons, and alternatives to swap (or 'let model decide'). Exports swaps.json."""
import os,json,html,shutil
def write(out,placed,video,lufs,peak):
  e=html.escape
  vid=os.path.relpath(os.path.join(out,'after.mp4'),out)
  rows=[]
  for c in placed:
    used=os.path.relpath(c['sfx_path'],out)
    opts=[f'<label class=o><input type=radio name="c{c["idx"]}" value="" checked> keep</label>',
          f'<label class=o><input type=radio name="c{c["idx"]}" value="auto"> let model decide</label>']
    for a in c['alternatives']:
      if a['id']==c['sfx']: continue
      opts.append(f'<div class=o><label><input type=radio name="c{c["idx"]}" value="{e(a["id"])}"> {e(str(a["label"])[:40])}</label> <audio controls preload=none src="{e(a["play"])}"></audio> <a href="{e(a["source_url"] or "#")}" target=_blank>source</a> <span class=m>{e(a["license"] or "")}</span></div>')
    rows.append(f'''<tr><td><button onclick="seek({c['t']})">{c['t']:.2f}s</button></td><td>{e(c['type'])}<br><span class=m>{e(c.get('desc',''))}</span></td><td><b>{e(c['category'])}</b></td>
<td>{e(os.path.basename(str(c['sfx'])))}<br><audio controls preload=none src="{e(used)}"></audio><br><a href="{e(c['source_url'] or '#')}" target=_blank>source page</a> · <span class=m>{e(c['license'] or '')}</span><br><span class=m>{e(c['credit'] or '')}</span></td>
<td><details><summary>alternatives ({len(c['alternatives'])})</summary>{''.join(opts)}</details></td></tr>''')
  doc=f'''<!doctype html><meta charset=utf-8><title>Sound pass report</title>
<style>body{{font-family:system-ui;background:#111;color:#eee;margin:20px}}table{{border-collapse:collapse;width:100%}}td{{border-bottom:1px solid #333;padding:8px;vertical-align:top}}.m{{color:#999;font-size:12px}}a{{color:#9cf}}.o{{margin:4px 0}}audio{{height:28px;vertical-align:middle}}button{{background:#d97757;color:#fff;border:0;border-radius:6px;padding:6px 10px;cursor:pointer}}video{{max-height:420px}}</style>
<h1>Sound pass report</h1><p>Final mix: <b>{lufs:.1f} LUFS</b>, true peak <b>{peak:.1f} dBFS</b> (measured on the exported MP4). Approach: Vox (@Voxyz_ai).</p>
<video id=v controls src="{e(vid)}"></video>
<p>Click a timestamp to jump there. To swap a sound, pick an alternative or "let model decide", then <button onclick="dl()">Download swaps.json</button> and re-run:<br><code>python scripts/sound_pass.py ... --swaps swaps.json</code> (or tell Claude "apply swaps.json").</p>
<table><tr><th>time</th><th>cue</th><th>category</th><th>sound used</th><th>swap</th></tr>{''.join(rows)}</table>
<script>function seek(t){{const v=document.getElementById('v');v.currentTime=Math.max(0,t-0.5);v.play()}}
function dl(){{const s={{}};document.querySelectorAll('input[type=radio]:checked').forEach(i=>{{if(i.value)s[i.name.slice(1)]=i.value}});
const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(s,null,1)],{{type:'application/json'}}));a.download='swaps.json';a.click()}}</script>'''
  open(os.path.join(out,'report.html'),'w').write(doc)
