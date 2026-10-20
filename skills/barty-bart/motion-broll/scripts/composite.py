"""Preview composite: lay the rendered clips over the source video (hard cuts, original audio).
usage: python3 composite.py motion/plan.json motion/out/preview.mp4
Clips shorter than their slot hold their last frame. Audio is re-encoded to AAC so any source muxes into MP4. Transparent .mov clips composite with alpha."""
import json, sys, subprocess, pathlib
P = json.load(open(sys.argv[1])); base = pathlib.Path(sys.argv[1]).parent; out = sys.argv[2]
rel = lambda f: str((base/f).resolve()) if not pathlib.Path(f).is_absolute() else f
cmd = ['ffmpeg', '-loglevel', 'error', '-y', '-i', rel(P['video'])]; fc = []; last = '0:v'
for i, c in enumerate(P['clips'], 1):
    cmd += ['-i', rel(c['file'])]
    fc.append(f"[{i}:v]format=yuva444p,tpad=stop_mode=clone:stop_duration={c['out']-c['in']:.3f},setpts=PTS-STARTPTS+{c['in']}/TB[c{i}]")
    fc.append(f"[{last}][c{i}]overlay=enable='between(t,{c['in']},{c['out']})':eof_action=pass[v{i}]"); last = f'v{i}'
fc.append(f'[{last}]format=yuv420p[v]')
cmd += ['-filter_complex', ';'.join(fc), '-map', '[v]', '-map', '0:a?', '-c:v', 'libx264', '-crf', '18', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', out]
subprocess.run(cmd, check=True); print('wrote', out)
