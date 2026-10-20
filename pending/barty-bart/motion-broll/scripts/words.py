"""SRT/VTT -> estimated word timestamps (spreads each cue across its characters; ~0.2s accuracy).
If faster-whisper is installed, prefer real word timestamps from the audio.
usage: python3 words.py transcript.srt|transcript.vtt > words.txt"""
import re, sys
def ts(x):  # SRT hh:mm:ss,mmm or VTT [hh:]mm:ss.mmm
    return sum(float(v)*60**i for i,v in enumerate(reversed(x.strip().replace(',','.').split(':'))))
cues=0
for blk in re.split(r'\n\s*\n',open(sys.argv[1],encoding='utf-8-sig').read().strip()):
    L=blk.strip().split('\n')
    i=next((i for i,l in enumerate(L[:2]) if '-->' in l),None)  # SRT has an index line first, VTT may not
    if i is None: continue  # WEBVTT header, NOTE/STYLE blocks
    a,b=[ts(x.split()[0]) for x in L[i].split('-->')]  # drop VTT cue settings after the end time
    words=re.sub(r'<[^>]*>','',' '.join(L[i+1:])).split()  # strip <i>, <c>, <00:00:01.500> tags
    if not words: continue
    n=sum(len(w)+1 for w in words); c=0; out=[]
    for w in words: out.append(f'{a+(b-a)*c/n:.2f}:{w}'); c+=len(w)+1
    print(' '.join(out)); cues+=1
if not cues: sys.exit(f'words.py: no cues found in {sys.argv[1]} (expected SRT or VTT)')
