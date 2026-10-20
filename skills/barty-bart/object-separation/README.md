# object-separation

<p align="center"><img src="../../docs/object-separation.gif" width="80%" alt="Before and after: talking-head footage, then the same footage with the speaker separated and separated onto a new background"></p>

**Separate anything from the background in a video, on your own computer.** Point it at a video and tell it what to separate (you, a product, a hand). It uses SAM 2.1 (Segment Anything, from Meta), which is free and runs locally, so nothing gets uploaded.

The whole skill is one file, [`SKILL.md`](SKILL.md). Run it in Claude Code, which works directly on your computer and can use your graphics chip.

**What it does**

1. **Scans your computer** and picks the right model size, then downloads it:

   | Your machine | Model | Download |
   |---|---|---|
   | NVIDIA GPU with 12 GB+ | large | 898 MB |
   | Smaller NVIDIA GPU, or Apple Silicon | base-plus | 323 MB |
   | No GPU (CPU only) | tiny | 156 MB |

2. **Picks the subject** with a couple of click points on the first frame.
3. **Separates it** in every frame, trying a short test range first and then the full clip.
4. **Gives you back your video with the subject separated onto a new background**, with the original audio, so you can see exactly what it picked up. It also saves a mask for every frame.

Once you have the masks, your video is effectively two layers, so you can ask Claude for whatever you want to do with the subject next without running the separation again.

**Install:** `npx skills add Barty-Bart/motion-graphics` and pick `object-separation`, or copy `skills/object-separation` into `.claude/skills/`.

**Use it:** in Claude Code, ask something like *"use object-separation to separate me from the background in clip.mp4"*.

**Requirements:** any 64-bit Windows, Mac or Linux computer with 8 GB RAM, Python 3.10+ and ffmpeg. No GPU needed: on a plain CPU it works but is slow (about 5 seconds per frame). Apple Silicon or an NVIDIA GPU makes it much faster. Everything installs into one `.object-separation` folder in your project, and the skill tells you how to delete it and the model when you're done.

## Licence

MIT.
