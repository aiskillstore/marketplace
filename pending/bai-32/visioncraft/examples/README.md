# VisionCraft Examples

A collection of copy-paste ready commands. Set `$env:AGNES_API_KEY` first (see [main README](../README.md#-quick-start)).

> All paths are relative to the repository root. Run from the directory that contains `scripts/`.

---

## 🖼️ Image Examples

### High-information-density landscape

```powershell
.\scripts\gen_image.ps1 -Prompt "A large fantasy harbor city built on cliffs, hundreds of small boats, layered stone bridges, glowing windows, distant mountains, cloudy sunset sky, cinematic fantasy realism, wide-angle composition, rich architectural details, high visual density"
```

### Cinematic portrait

```powershell
.\scripts\gen_image.ps1 -Prompt "Cinematic close-up portrait of a weathered explorer in arctic gear, tack-sharp eye contact, soft window light, shallow depth of field, premium photographic realism, magazine cover quality" -Size "2048x2048"
```

### Marketing poster (16:9)

```powershell
.\scripts\gen_image.ps1 -Prompt "A premium product hero shot of a luxury watch on dark marble, dramatic spotlight, water droplets, sharp reflections, cinematic commercial photography, ultra detailed" -Ratio 16:9
```

### Vertical social cover (9:16)

```powershell
.\scripts\gen_image.ps1 -Prompt "Stylized portrait of a futuristic samurai in glowing armor, neon backlight, mist, cinematic depth, premium key art" -Ratio 9:16
```

### Image-to-image: cyberpunk restyle

```powershell
.\scripts\gen_image.ps1 -Prompt "Convert the daytime street scene into a rain-soaked cyberpunk night, add neon signs and wet road reflections, preserve the original street layout, camera angle, and main building shapes" -ImageUrl "https://example.com/input-street.png"
```

### Image-to-image: seasonal transformation

```powershell
.\scripts\gen_image.ps1 -Prompt "Convert the image into a fantasy winter landscape, add snow, warm window lights, magical atmosphere, while preserving the original building structure and camera angle" -ImageUrl "https://example.com/input-house.png"
```

---

## 🎬 Video Examples

### Cinematic text-to-video

```powershell
.\scripts\gen_video.ps1 -Prompt "A young astronaut walking across a red desert planet, dust blowing in the wind, slow cinematic tracking shot, dramatic sunset lighting, realistic sci-fi style"
```

### Vertical short-form (9:16, 8 seconds)

```powershell
.\scripts\gen_video.ps1 -Prompt "Cyberpunk dancer spinning in a neon-lit alley, slow-motion, rain reflections, vibrant magenta and cyan lighting, music-video aesthetic" -Ratio 9:16 -Seconds 8
```

### Image-to-video: subtle animation

```powershell
.\scripts\gen_video.ps1 -Prompt "Animate the character with subtle breathing motion, hair moving gently in the wind, background lights flickering softly, while keeping the face and outfit consistent" -Image "https://example.com/portrait.png"
```

### 🔥 Keyframe animation: A → B morph

```powershell
.\scripts\gen_video.ps1 -Prompt "Create a smooth transition from the first keyframe to the second keyframe, maintaining character identity, consistent camera angle, and natural motion between scenes" -Image "https://example.com/keyframe-a.png","https://example.com/keyframe-b.png" -Mode keyframes
```

### Multi-image reference video

```powershell
.\scripts\gen_video.ps1 -Prompt "Use the first image as the starting scene and the second image as the target scene. Create a smooth transformation with consistent lighting, natural motion, and cinematic pacing" -Image "https://example.com/scene1.png","https://example.com/scene2.png"
```

### Longer cinematic clip (10s @ 24fps using `-Seconds`)

```powershell
.\scripts\gen_video.ps1 -Prompt "An epic wide shot: a lone figure walking across a vast salt flat at golden hour, long shadows, dust particles in light, cinematic anamorphic lens" -Seconds 10 -FrameRate 24
```

### Maximum-length video (~18s @ 24fps)

```powershell
.\scripts\gen_video.ps1 -Prompt "A serene drone shot gliding over a misty mountain valley at dawn, slow camera dolly forward, layered clouds, soft golden light, cinematic nature documentary style" -NumFrames 441 -FrameRate 24
```

### Reproducible result

```powershell
.\scripts\gen_video.ps1 -Prompt "..." -Seed 42
```

---

## 💡 Tips

- For longer videos, lower the frame rate (24fps) and increase frames.
- For ultra-smooth slow-motion looks, keep 60fps and accept ~4s duration.
- Use `-NegativePrompt` to exclude unwanted elements: `-NegativePrompt "blurry, distorted faces, watermark"`.
- Reuse the same `-Seed` to iterate on prompts while keeping composition stable.
