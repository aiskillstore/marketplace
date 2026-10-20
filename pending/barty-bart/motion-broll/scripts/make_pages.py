"""Write viewer.html (step through clips) and compare.html (original vs preview, synced) next to the renders.
usage: python3 make_pages.py motion/plan.json motion/out/preview.mp4"""
import json, sys, pathlib, os, subprocess, html, urllib.parse
S = pathlib.Path(__file__).resolve().parent.parent / 'templates'
plan_p = pathlib.Path(sys.argv[1]); P = json.load(open(plan_p)); base = plan_p.parent
preview = pathlib.Path(sys.argv[2]).resolve(); out = preview.parent
rel = lambda f: os.path.relpath((base / f).resolve(), out)
fmt = lambda t: (lambda cs: f"{cs//6000}:{cs%6000/100:05.2f}")(round(t*100))  # round first: 59.999 -> 1:00.00, not 0:60.00
probe = lambda f, e: subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', e, '-of', 'csv=p=0', str(f)], capture_output=True, text=True).stdout.strip()
js = lambda o: json.dumps(o, ensure_ascii=False).replace('</', '<\\/')  # safe inside <script>
title = P.get('title', 'Video'); title_h = html.escape(title)
def web_src(c):
    f = (base / c['file']).resolve()
    if f.suffix.lower() == '.mov':  # browsers can't play ProRes: make an on-black preview for the page
        pv = out / (f.stem + '_preview.mp4')
        size = probe(f, 'stream=width,height').replace(',', 'x') or '1920x1080'
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', f'color=black:s={size}', '-i', str(f), '-filter_complex', '[0][1]overlay=shortest=1',
                        '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', str(pv)], check=True)
        return pv.name
    return os.path.relpath(f, out)
clips = [{'n': c['id'], 't': c['title'], 'tc': f"{fmt(c['in'])} – {fmt(c['out'])}", 'q': c.get('line', ''), 'f': pathlib.Path(c['file']).name,
          'src': web_src(c), **({'alpha': True} if c.get('kind') == 'panel' else {})} for c in P['clips']]
clips.insert(0, {'n': '▶', 'full': True, 't': 'Full preview · your video with every clip', 'tc': 'whole video', 'q': 'Composite for review. For the final cut, place the clips in your editor.', 'f': preview.name, 'src': preview.name})
v = open(S / 'viewer.html').read().replace('/*CLIPS*/[]', js(clips)).replace('/*TITLE*/', title_h).replace('/*SUB*/', f"{len(P['clips'])} clips + full preview")
open(out / 'viewer.html', 'w').write(v)
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(preview)], capture_output=True, text=True).stdout.strip() or 0)
marks = [[c['in'], c['out'], c['id'], c['title']] for c in P['clips']]
c = (open(S / 'compare.html').read().replace('/*DUR*/0', f'{dur:.2f}').replace('/*MARKS*/[]', js(marks))
     .replace('/*ORIG*/', urllib.parse.quote(rel(P['video']))).replace('/*BROLL*/', urllib.parse.quote(preview.name)).replace('/*TITLE*/', title_h)
     .replace('/*SUB*/', 'Left or top is the original. Right or bottom has the motion graphics cut in.'))
open(out / 'compare.html', 'w').write(c); print('wrote', out / 'viewer.html', 'and', out / 'compare.html')
# TIMING.md for the editor
rows = ['| File | In | Out | Treatment | Covers the line |', '|---|---|---|---|---|']
for c in P['clips']:
    rows.append(f"| {pathlib.Path(c['file']).name} | {fmt(c['in'])} | {fmt(c['out'])} | {'transparent panel' if c.get('kind') == 'panel' else 'full-frame cutaway'} | {c.get('line', '')} |")
notes = P.get('notes', [])
open(out / 'TIMING.md', 'w').write(f"# Motion graphics for {title}\n\nEach file name ends with its timeline in-point (`0m32s40` = 0:32.40). Transparent panels are ProRes 4444 .mov files: put them on a track above the video.\n\n" + '\n'.join(rows) + ('\n\nNotes\n' + '\n'.join('- ' + n for n in notes) if notes else '') + '\n')
print('wrote', out / 'TIMING.md')
