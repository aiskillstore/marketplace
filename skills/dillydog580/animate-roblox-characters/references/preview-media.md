# Animated GIF Preview

Read this before Phase 7. The GIF is a required final artifact for every completed animation.

## Order of operations

1. Finish the Phase 6 audit.
2. Save the final `.blend` and export `.rbxanim` or FBX.
3. Add preview-only camera/lights in `Review`.
4. Render sequential RGB PNG frames.
5. Encode and verify the GIF.
6. Deliver all artifacts together.

This ordering prevents review objects from entering the Roblox export.

## Camera and lighting

Inspect the visible model to establish forward direction. R6 V2.22 faces Blender `+Y`; the older nominal front camera at `-Y` shows its back.

For an origin-centered R6 V2.22 character, use:

- Resolution: `512 × 512`.
- Orthographic camera: `(6.8, 8.8, 4.8)`.
- Look target: `(0, 0, 2.55)`.
- Orthographic scale: `6.4`.
- Fixed framing for the entire animation.
- Three review-only area lights: key, fill, and rim.

Use `animation_tools.render_animation_preview_frames()` or the `render-preview` operation. It applies these R6 defaults, renders RGB PNGs, and requires explicit visually chosen camera coordinates for other rigs.

## Loop frames

Keep the duplicated closing frame for numerical seam/export checks, but do not include it in the preview. A cycle keyed at frames `1–25` with frame 25 duplicating frame 1 renders GIF playback frames `1–24`.

Use natural, zero-padded filenames such as `walk_0001.png` through `walk_0024.png`.

## Encoding

Run:

```sh
python3 scripts/build_animation_preview.py \
  --frames-dir <preview-frames> \
  --glob 'walk_*.png' \
  --output <animation-preview.gif> \
  --fps 30 \
  --expected-frames 24
```

The encoder:

- Converts every frame to RGB.
- Requires identical dimensions.
- Builds one adaptive 256-color median-cut palette from thumbnails of every frame.
- Quantizes every frame against that shared palette with Floyd–Steinberg dithering.
- Saves with `loop=0`, `disposal=2`, and `optimize=False`.
- Distributes GIF centiseconds across frames instead of rounding each frame independently.
- Reopens the result and verifies metadata and duration.

At 24 frames and 30 FPS, the exact duration list is `[30, 30, 40] * 8`, totaling `800 ms`.

## Visual verification

Inspect the animated result when the environment can display GIFs. Check framing, front direction, lighting, palette stability, trails, loop seam, foot contacts, and whether the motion reads like the final Blender action. If animated playback cannot be inspected, inspect representative PNGs and mark animated playback unverified.
