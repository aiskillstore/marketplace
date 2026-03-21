# Social Media

## Triggers

social media, instagram, twitter, X, facebook, linkedin, xiaohongshu, douyin, TikTok, post, story, reels, banner, thumbnail, cover photo, OG image

## Defaults

- **Resolution**: `2K`
- **Aspect ratio**: depends on platform (see table); default `1:1` if unspecified

## Platform Aspect Ratio Map

| Platform | Format | Aspect ratio |
|---|---|---|
| Instagram | Post | `1:1` or `4:5` |
| Instagram | Story / Reels | `9:16` |
| Twitter / X | Post image | `16:9` |
| Facebook | Post | `1:1` or `4:5` |
| Facebook | Cover photo | `16:9` |
| LinkedIn | Post | `1:1` or `4:5` |
| LinkedIn | Banner | `16:9` |
| Xiaohongshu (RED) | Post | `3:4` |
| Douyin / TikTok | Cover | `9:16` |
| YouTube | Thumbnail | `16:9` |
| Pinterest | Pin | `2:3` |

## Design Thinking

1. **Understand the scroll context** — Your image competes with hundreds of others in a feed. Design for the 0.3-second thumb-stop moment: if the core message isn't instantly clear, the post loses
2. **Platform personality matters** — Xiaohongshu rewards polished, aspirational aesthetics; Twitter/X favors bold statements and memes; LinkedIn expects professional clarity; Instagram rewards visual beauty. Tailor the visual tone to the platform
3. **Design for the crop** — Platforms display thumbnails, circular avatars, and cropped previews differently. Keep the hero element centered and away from edges. Mentally preview how the image looks in a feed grid
4. **Tell a micro-story** — The best social images create curiosity or emotion in a single frame. A before/after, a surprising visual, or a bold statement paired with an arresting image outperforms generic graphics
5. **Brand consistency across posts** — If creating a series, define a visual system upfront: consistent color palette, layout template, font style. Followers should recognize your brand before reading the handle

## Aesthetics Guidelines

- **Thumb-stop color**: Use bold, saturated colors that pop on both light and dark mode feeds. Avoid muddy mid-tones. Test mentally: would this stand out in a grid of muted photos?
- **Text hierarchy at phone scale**: On mobile, body text under 14pt equivalent is invisible. Use 2 levels max: a punchy headline and one short supporting line. If you need more text, it belongs in the caption, not the image
- **Safe zones**: Keep all critical elements (text, faces, key visuals) within the center 80% of the canvas. Platform UI overlays, cropping, and rounded corners eat the edges
- **Visual consistency for series**: Define a template system — same background color/texture, same text position, same accent color. Describe this template explicitly in the prompt and use `--input-image` to enforce it
- **Platform-native feel**: The image should feel native to the platform, not like a repurposed print ad. Xiaohongshu posts feel editorial; Instagram Stories feel immersive; LinkedIn posts feel clean and informative. Describe the target platform aesthetic in the prompt
- **Authenticity over polish**: Overly corporate, stock-photo-style graphics underperform on most platforms. Favor genuine, relatable, or visually surprising imagery. Describe specific scenes rather than generic concepts

## Prompt Rules

- Design for thumb-stopping: clear focal point and strong visual contrast. Adapt color intensity to the platform.
- Keep text in safe zones — away from edges where platforms crop
- Put all text content in double quotes for accurate rendering
- Headlines must be readable at thumbnail size
- For a series, use `--input-image` from the first post to maintain visual consistency
