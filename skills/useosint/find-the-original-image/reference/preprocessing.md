# Preprocessing recipes before you search

Every recipe below produces a *derivative* file. Keep the original untouched and
hashed; work on copies with names that record what you did
(`subject_crop-patch.png`, `subject_flop.png`). If your finding ends up in a
report, you must be able to say what you fed each engine.

Commands use ImageMagick 7 (`magick`) and FFmpeg. On ImageMagick 6 the command is
`convert` with the same options.

## Before you touch anything

```bash
magick identify -verbose original.jpg | head -40   # dimensions, colourspace, quality estimate
exiftool original.jpg                             # do this FIRST, editing destroys it
sha256sum original.jpg > original.sha256
```

If width is under about 400 px on the subject of interest, expect poor recall
everywhere and go straight to upscaling.

## Recipe 1 — Crop to the distinctive element

The single highest-yield transform. Run once per interesting object.

```bash
magick original.jpg -crop 480x480+1220+640 +repage crop_patch.png
```

`WxH+X+Y`, origin top-left. `+repage` clears the virtual canvas offset so
downstream tools don't see a weird geometry. Output PNG so you don't stack a
second JPEG generation onto the crop.

What to crop, in rough order of value: shoulder patches and insignia, shop and
street signs, licence plates, vehicle badges and liveries, tattoos, jewellery,
unusual architectural detail, product logos, watermarks and agency slugs, a
single face. What not to crop: sky, grass, water, plain walls, road surface.

Bing Visual Search does this interactively after upload, which is faster for
exploration. Use the CLI when you need a reproducible artifact.

## Recipe 2 — Horizontal mirror

```bash
magick original.jpg -flop flop.jpg
```

`-flop` is horizontal, `-flip` is vertical (rarely useful). Mirroring is a common
deliberate evasion of automated matching and a common accident of
screen-recording and short-video reposting. Search both orientations as a matter
of routine, including on crops.

## Recipe 3 — Upscale a small or thumbnailed image

Plain interpolation first, since it is instant and sometimes enough:

```bash
magick original.jpg -filter Lanczos -resize 300% up_lanczos.png
```

For anything genuinely small, a learned upscaler recovers far more usable
structure:

```bash
realesrgan-ncnn-vulkan -i original.jpg -o up_esrgan.png -n realesrgan-x4plus -s 4
```

Caveat that matters: learned upscalers **hallucinate**. They invent plausible
detail. An upscaled image is a search aid only. Never read a licence plate, a
face, or text off an upscaled image and treat it as evidence — go back to the
original pixels to confirm anything you think you see, and say in the report that
the read came from the original, not the upscale.

## Recipe 4 — Denoise and clean a compressed or low-light image

```bash
magick original.jpg -despeckle -enhance clean.png            # mild, general
magick original.jpg -auto-level -contrast-stretch 1x1% lvl.png
magick original.jpg -modulate 115,110 -unsharp 0x1.0 pop.png # brightness, saturation, sharpen
```

For shadow detail in a dark frame:

```bash
magick original.jpg -level 5%,70% shadows.png
```

Levelling the shadows is also how you read text on a signboard that is
underexposed, and how you check whether something in a dark region is an object
or compression mush.

## Recipe 5 — Straighten and de-rotate

```bash
magick original.jpg -rotate -7 rot.png
magick original.jpg -deskew 40% deskew.png     # for scanned or photographed documents
```

Engines tolerate small rotations badly. If a sign in the frame is at an angle,
crop it and straighten it before OCR or search.

## Recipe 6 — Isolate text for OCR

```bash
magick original.jpg -crop 900x220+300+1500 +repage \
  -colorspace Gray -contrast-stretch 2x2% -resize 300% sign.png
tesseract sign.png - -l rus+eng
```

Set `-l` to the language you actually suspect; the wrong language model produces
confident garbage on non-Latin scripts. Google Lens is often better than local
Tesseract on curved, stylised or low-contrast signage, so try both. The extracted
string is frequently a stronger selector than the image ever was — hand it to
`google-like-a-spy`.

## Recipe 7 — Keyframes from a video

Fastest, decodes only keyframes:

```bash
ffmpeg -skip_frame nokey -i video.mp4 -vsync 0 -frame_pts true key_%d.png
```

Equivalent via a filter, if the above misbehaves on an odd container:

```bash
ffmpeg -i video.mp4 -vf "select='eq(pict_type,I)'" -vsync vfr key_%04d.png
```

One frame per scene change rather than per keyframe — usually a better spread for
reverse search:

```bash
ffmpeg -i video.mp4 -vf "select='gt(scene,0.4)',showinfo" -vsync vfr scene_%04d.png
```

A fixed cadence, when the video is short:

```bash
ffmpeg -i video.mp4 -vf fps=1 sec_%04d.png
```

One exact frame at a timestamp you care about:

```bash
ffmpeg -ss 00:01:23.400 -i video.mp4 -frames:v 1 -q:v 1 frame.png
```

Then search at minimum: one frame near the start, one near the middle, one near
the end, plus every frame containing a sign, a face, a vehicle or a skyline. Also
check container-level metadata before you start:

```bash
ffprobe -v error -show_format -show_streams video.mp4
exiftool video.mp4
```

If the video came from a platform, pull the highest available rendition rather
than a screen recording:

```bash
yt-dlp --write-info-json -f "bv*+ba/b" "URL"
```

The sidecar JSON carries upload time, uploader and description — provenance you
would otherwise have to reconstruct.

## Ordering

1. Metadata extraction and hashing (destructive edits come after, never before).
2. Full frame, unmodified, to every engine.
3. Crops of each distinctive element.
4. Mirror of the frame and of the best crops.
5. Upscale/denoise only what came back empty.
6. OCR any text and pivot to a text search.

Log each of these as a separate documented query with its result, including the
nulls.
