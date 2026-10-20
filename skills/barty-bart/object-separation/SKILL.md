---
name: object-separation
description: Separate a person, product or hand from the background in a video, on the user's own computer with SAM 2. Scans the machine first to pick the right model size, then outputs the same video with the separated subject highlighted in green, plus frame-by-frame masks. Use when someone wants to separate, isolate, cut out or rotoscope something in a video.
---

# Object separation

Separate one subject from the background in a video. Everything runs on the user's computer and nothing is uploaded. The result is the same video with the subject highlighted in green, so the user can see exactly what was separated, plus a mask for every frame saved to disk.

You write and run the Python as you go. The code blocks below are tested; adapt them rather than starting from scratch.

## 1. Set up in a folder that can be deleted

Needs python 3.10+ and ffmpeg. Install everything into a virtual environment in the project folder, so removing that one folder removes it all:

```
python3 -m venv .object-separation
.object-separation/bin/pip install torch transformers opencv-python-headless pillow numpy
```

On Windows use `.object-separation\Scripts\pip`. With an NVIDIA card on Windows, install the CUDA build of torch from pytorch.org first, because plain pip gives the slower CPU build. Run all the Python below with the venv's python.

## 2. Scan the computer and pick the model

Run the scan first and tell the user what it found: the device, the model it picked, the download size, and what speed to expect.

| Machine | Model | Download |
|---|---|---|
| NVIDIA GPU with 12 GB+ | `facebook/sam2.1-hiera-large` | 898 MB |
| NVIDIA GPU under 12 GB, or Apple Silicon | `facebook/sam2.1-hiera-base-plus` | 323 MB |
| No GPU (CPU only) | `facebook/sam2.1-hiera-tiny` | 156 MB |

On a CPU it works but it is slow: about 5 seconds per frame, so a 10 second clip at 30 fps takes around half an hour. It uses under 2 GB of RAM. A GPU is much faster. If the clip is long and there is no GPU, suggest separating only the part the user needs.

```python
# Set these from the user's request. Frame numbers start at 0; the video must be constant frame rate.
VIDEO = "clip.mp4"
START, END = 0, 89              # frames to separate. Click points are picked on the START frame.
PTS = [[480, 270], [100, 60]]   # click points in 960-wide pixels: on the subject first, then on things to leave out
LBL = [1, 0]                    # 1 = this is the subject, 0 = this is NOT the subject
```

```python
import os, platform, subprocess, numpy as np, torch, cv2
from transformers import Sam2VideoModel, Sam2VideoProcessor

print("system:", platform.system(), platform.machine())
if torch.cuda.is_available():
    gb = torch.cuda.get_device_properties(0).total_memory / 1e9
    print("gpu:", torch.cuda.get_device_name(0), f"{gb:.0f} GB")
    dev, MODEL = "cuda", "facebook/sam2.1-hiera-" + ("large" if gb >= 12 else "base-plus")
elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
    dev, MODEL = "mps", "facebook/sam2.1-hiera-base-plus"
else:
    dev, MODEL = "cpu", "facebook/sam2.1-hiera-tiny"
print("device:", dev, "| model:", MODEL)
model = Sam2VideoModel.from_pretrained(MODEL).to(dev).eval()     # downloads on first run
proc = Sam2VideoProcessor.from_pretrained(MODEL)
W = 960   # working width. SAM 2 resizes to 1024 itself, so a smaller width is NOT faster.
```

## 3. Pick the click points

Save frame START with a coordinate grid and look at it. Choose two or three points on the subject and add points with label 0 on anything that must be left out (fingers holding it, packaging, the table). Show the user what you picked if it is not obvious.

```python
def read_frames(video, a, b):
    cap = cv2.VideoCapture(video); cap.set(cv2.CAP_PROP_POS_FRAMES, a); out = []
    for _ in range(a, b + 1):
        ok, im = cap.read()
        if not ok: break
        out.append(cv2.cvtColor(cv2.resize(im, (W, int(im.shape[0] * W / im.shape[1]))), cv2.COLOR_BGR2RGB))
    return out

def preview(frame, path="work/preview.jpg"):       # frame with a labelled grid, to pick click points
    os.makedirs("work", exist_ok=True)
    im = cv2.cvtColor(read_frames(VIDEO, frame, frame)[0], cv2.COLOR_RGB2BGR)
    for x in range(0, im.shape[1], 80):
        cv2.line(im, (x, 0), (x, im.shape[0]), (0, 255, 255), 1); cv2.putText(im, str(x), (x + 2, 12), 0, 0.4, (0, 255, 255), 1)
    for y in range(0, im.shape[0], 60):
        cv2.line(im, (0, y), (im.shape[1], y), (0, 255, 255), 1); cv2.putText(im, str(y), (2, y - 2), 0, 0.4, (0, 255, 255), 1)
    cv2.imwrite(path, im); return path
```

## 4. Separate the subject

The video is processed in chunks of 60 frames so memory stays low. Each chunk starts from the last mask of the one before. Try a short range first (about 20 frames), check it, then run the full range.

```python
def separate_chunk(frames, points=None, labels=None, mask=None):
    H = frames[0].shape[0]
    s = proc.init_video_session(video=frames, inference_device=dev, video_storage_device="cpu",
                                inference_state_device="cpu", dtype=torch.float32)
    if mask is None:
        proc.add_inputs_to_inference_session(inference_session=s, frame_idx=0, obj_ids=1,
                                             input_points=[[points]], input_labels=[[labels]])
    else:
        proc.add_inputs_to_inference_session(inference_session=s, frame_idx=0, obj_ids=1,
                                             input_masks=mask.astype(np.uint8))
    res = {}
    with torch.inference_mode():
        model(inference_session=s, frame_idx=0)
        for o in model.propagate_in_video_iterator(s, start_frame_idx=0):
            m = proc.post_process_masks([o.pred_masks], original_sizes=[[H, W]], binarize=True)[0]
            res[o.frame_idx] = m.squeeze().cpu().numpy().astype(bool)
    return res

def separate(start, end, pts, lbl, ch=60):
    out, a, seed = {}, start, None
    while a < end:
        b = min(end, a + ch)
        fr = read_frames(VIDEO, a, b)
        r = separate_chunk(fr, points=pts, labels=lbl) if seed is None else separate_chunk(fr, mask=seed)
        for k, m in r.items():
            out[a + k] = m
        seed, a = r[len(fr) - 1], b
    return out

masks = separate(START, END, PTS, LBL)
os.makedirs("work/masks/subject", exist_ok=True)
for f, m in masks.items():
    cv2.imwrite(f"work/masks/subject/{f:05d}.png", m.astype(np.uint8) * 255)
```

## 5. Output the video with the subject in green

```python
def green(f, img, fill=0.35):                       # green tint, glow and a bright edge on the subject
    m = cv2.GaussianBlur(cv2.resize(masks[f].astype(np.float32), (img.shape[1], img.shape[0])), (5, 5), 0)
    edge = cv2.morphologyEx((m > 0.5).astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((7, 7), np.uint8)).astype(np.float32)
    glow = np.clip(cv2.GaussianBlur(edge, (37, 37), 0) * 2.5, 0, 1)[..., None]
    col = np.array([20, 255, 57], np.float32)          # BGR green
    img = img * (1 - m[..., None] * fill) + col * m[..., None] * fill + col * glow * 0.9
    return img * (1 - edge[..., None]) + np.array([220, 255, 200], np.float32) * edge[..., None]

def render(a, b, out, fn):                          # writes the frames a..b with the original audio
    cap = cv2.VideoCapture(VIDEO); cap.set(cv2.CAP_PROP_POS_FRAMES, a)
    fps = cap.get(cv2.CAP_PROP_FPS)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                           "-s", f"{int(cap.get(3))}x{int(cap.get(4))}", "-r", str(fps), "-i", "-",
                           "-ss", f"{a / fps:.4f}", "-t", f"{(b - a + 1) / fps:.4f}", "-i", VIDEO,
                           "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-shortest", out], stdin=subprocess.PIPE)
    for f in range(a, b + 1):
        ok, img = cap.read()
        if not ok: break
        ff.stdin.write(np.clip(fn(f, img.astype(np.float32)), 0, 255).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait()

render(START, END, "work/separated.mp4", green)
```

Look at a few frames of the result before handing it over: the start, the middle, and any moment where a hand or object passes in front. If green spills onto something that is not the subject, add a label-0 point on it and run step 4 again. If part of the subject is missing, add a label-1 point there.

Tell the user where the files are: `work/separated.mp4` (the video with the subject in green) and `work/masks/subject/` (one mask per frame, white = subject). The masks stay on disk, so anything the user wants to do with the separated subject next can start from them without running the separation again.

## 6. Clean up (optional)

Once the user is done, everything can be removed:
- the virtual environment: delete the `.object-separation` folder
- the model: delete `~/.cache/huggingface/hub/models--facebook--sam2.1-hiera-*` (on Windows: `C:\Users\<name>\.cache\huggingface\hub`)

## Notes

- Masks are hard-edged: very clean on objects and hands, less so on soft hair.
- Anything attached to the subject counts as part of it (packaging, peel-off film). Add a label-0 point on it.
- If the video is variable frame rate, convert it first: `ffmpeg -i in.mp4 -vsync cfr -r 30 out.mp4`.
- Only the first run needs the internet, to download the model.
