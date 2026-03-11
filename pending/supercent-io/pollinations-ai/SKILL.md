---
name: pollinations-ai
description: "Generate and save images using Pollinations.ai's free, open-source API. No signup required. Supports URL-based generation, custom parameters (width, height, model, seed), and automatic file saving. Perfect for quick prototypes, marketing assets, and creative workflows."
metadata:
  tags: image-generation, pollinations, free, api, creative, ai-art, url-based
  platforms: Claude, ChatGPT, Gemini, Codex
---


# Pollinations.ai Image Generation

Free, open-source AI image generation through simple URL parameters. No API key or signup required.

## When to use this skill

- **Quick prototyping**: Generate placeholder images instantly
- **Marketing assets**: Create hero images, banners, social media content
- **Creative exploration**: Test multiple styles and compositions rapidly
- **No-budget projects**: Free alternative to paid image generation services
- **Automated workflows**: Script-friendly URL-based API

---

## Instructions

### Step 1: Understand the API Structure

Pollinations.ai uses a simple URL-based API:

```
https://image.pollinations.ai/prompt/{YOUR_PROMPT}?{PARAMETERS}
```

**No authentication required** - just construct the URL and fetch the image.

**Available Parameters**:
- `width` / `height`: Resolution (default: 1024x1024)
- `model`: AI model (`flux`, `turbo`, `stable-diffusion`)
- `seed`: Number for reproducible results
- `nologo`: `true` to remove watermark (if supported)
- `enhance`: `true` for automatic prompt enhancement

### Step 2: Craft Your Prompt

Use descriptive prompts with specific details:

**Good prompt structure**:
```
[Subject], [Style], [Lighting], [Mood], [Composition], [Quality modifiers]
```

**Example**:
```
A father welcoming a beautiful holiday, warm golden hour lighting, 
cozy interior background with festive decorations, 8k resolution, 
highly detailed, cinematic depth of field
```

**Prompt styles**:
- **Photorealistic**: "photorealistic shot, 8k resolution, highly detailed, cinematic"
- **Illustrative**: "digital illustration, soft pastel colors, disney style animation"
- **Minimalist**: "minimalist vector art, flat design, simple geometric shapes"

### Step 3: Generate via URL (Browser Method)

Simply open the URL in a browser or use `curl`:

```bash
# Basic generation
curl "https://image.pollinations.ai/prompt/A_serene_mountain_landscape" -o mountain.jpg

# With parameters
curl "https://image.pollinations.ai/prompt/A_serene_mountain_landscape?width=1920&height=1080&model=flux&seed=42" -o mountain-hd.jpg
```

### Step 4: Generate and Save (Python Method)

For automation and file management:

```python
import requests
from urllib.parse import quote

def generate_image(prompt, output_file, width=1920, height=1080, model="flux", seed=None):
    """
    Generate image using Pollinations.ai and save to file
    
    Args:
        prompt: Description of the image to generate
        output_file: Path to save the image
        width: Image width in pixels
        height: Image height in pixels
        model: AI model ('flux', 'turbo', 'stable-diffusion')
        seed: Optional seed for reproducibility
    """
    # Encode prompt for URL
    encoded_prompt = quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
    
    # Build parameters
    params = {
        "width": width,
        "height": height,
        "model": model,
        "nologo": "true"
    }
    if seed:
        params["seed"] = seed
    
    # Generate and save
    print(f"Generating: {prompt[:50]}...")
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"✓ Saved to {output_file}")
        return True
    else:
        print(f"✗ Error: {response.status_code}")
        return False

# Example usage
generate_image(
    prompt="A father welcoming a beautiful holiday, warm lighting, festive decorations",
    output_file="holiday_father.jpg",
    width=1920,
    height=1080,
    model="flux",
    seed=12345
)
```

### Step 5: Batch Generation

Generate multiple variations:

```python
prompts = [
    "photorealistic shot of a father at front door, warm lighting, festive decorations",
    "digital illustration of a father in snow, magical winter wonderland, disney style",
    "minimalist silhouette of father and child, holiday fireworks, flat design"
]

for i, prompt in enumerate(prompts):
    generate_image(
        prompt=prompt,
        output_file=f"variant_{i+1}.jpg",
        width=1920,
        height=1080,
        model="flux"
    )
```

### Step 6: Document Your Generations

Save metadata for reproducibility:

```python
import json
from datetime import datetime

metadata = {
    "prompt": prompt,
    "model": "flux",
    "width": 1920,
    "height": 1080,
    "seed": 12345,
    "output_file": "holiday_father.jpg",
    "timestamp": datetime.now().isoformat()
}

with open("generation_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)
```

---

## Examples

### Example 1: Hero Image for Website

```python
generate_image(
    prompt="serene mountain landscape at sunset, wide 16:9, minimal style, soft gradients in blue tones, clean lines, modern aesthetic",
    output_file="hero-image.jpg",
    width=1920,
    height=1080,
    model="flux"
)
```

**Expected output**: 16:9 landscape image, minimal style, blue color palette

### Example 2: Product Thumbnail

```python
generate_image(
    prompt="futuristic dashboard UI, 1:1 square, clean interface, soft lighting, professional feel, dark theme, subtle glow effects",
    output_file="product-thumb.jpg",
    width=1024,
    height=1024,
    model="flux"
)
```

**Expected output**: Square thumbnail, dark theme, app store ready

### Example 3: Social Media Banner

```python
generate_image(
    prompt="LinkedIn banner for SaaS startup, modern gradient background, abstract geometric shapes, colors from purple to blue, space for text on left side",
    output_file="linkedin-banner.jpg",
    width=1584,
    height=396,
    model="flux"
)
```

**Expected output**: LinkedIn-optimized dimensions (1584x396), text-safe zone

### Example 4: Batch Variations with Seeds

```python
# Generate 4 variations of the same prompt with different seeds
base_prompt = "A father welcoming a beautiful holiday, cinematic lighting"

for seed in [100, 200, 300, 400]:
    generate_image(
        prompt=base_prompt,
        output_file=f"variation_seed_{seed}.jpg",
        width=1920,
        height=1080,
        model="flux",
        seed=seed
    )
```

**Expected output**: 4 similar images with subtle variations

---

## Best practices

1. **Use specific prompts**: Include style, lighting, mood, and quality modifiers
2. **Specify dimensions early**: Prevents unintended cropping
3. **Use seeds for consistency**: Same seed + prompt = same image
4. **Model selection**:
   - `flux`: Highest quality, slower
   - `turbo`: Fast iterations
   - `stable-diffusion`: Balanced
5. **Save metadata**: Track prompts, seeds, and parameters for reproducibility
6. **Batch similar requests**: Generate style sets with consistent parameters
7. **URL encode prompts**: Use `urllib.parse.quote()` for special characters

---

## Common pitfalls

- **Vague prompts**: Add specific details about style, lighting, and composition
- **Ignoring aspect ratios**: Check target platform requirements (Instagram 1:1, LinkedIn 1584x396, etc.)
- **Overly complex scenes**: Simplify for clarity and better results
- **Not saving metadata**: Difficult to reproduce or iterate on successful images
- **Forgetting URL encoding**: Special characters break URLs

---

## Troubleshooting

### Issue: Inconsistent outputs
**Cause**: No seed specified
**Solution**: Use a fixed seed for reproducible results

```python
generate_image(prompt="...", seed=12345, ...)  # Same output every time
```

### Issue: Wrong aspect ratio
**Cause**: Incorrect width/height parameters
**Solution**: Use platform-specific dimensions

```python
# Instagram: 1:1
generate_image(prompt="...", width=1080, height=1080)

# LinkedIn banner: ~4:1
generate_image(prompt="...", width=1584, height=396)

# YouTube thumbnail: 16:9
generate_image(prompt="...", width=1280, height=720)
```

### Issue: Image doesn't match brand colors
**Cause**: No color specification in prompt
**Solution**: Include HEX codes or color names

```python
prompt = "landscape with brand colors deep blue #2563EB and purple #8B5CF6"
```

### Issue: Request fails (HTTP error)
**Cause**: Network issue or service downtime
**Solution**: Add retry logic

```python
import time

def generate_with_retry(prompt, output_file, max_retries=3):
    for attempt in range(max_retries):
        if generate_image(prompt, output_file):
            return True
        print(f"Retry {attempt + 1}/{max_retries}...")
        time.sleep(2)
    return False
```

---

## Output format

```markdown
## Image Generation Report

### Request
- **Prompt**: [full prompt text]
- **Model**: flux
- **Dimensions**: 1920x1080
- **Seed**: 12345

### Output Files
1. `hero-image-v1.jpg` - Primary variant
2. `hero-image-v2.jpg` - Alternative style
3. `hero-image-v3.jpg` - Different lighting

### Metadata
- Generated: 2026-02-13T14:30:00Z
- Iterations: 3
- Selected: hero-image-v1.jpg

### Usage Notes
- Best for: Website hero section
- Format: JPEG, 1920x1080
- Reproducible: Yes (seed: 12345)
```

---

## Multi-Agent Workflow

### Validation & Quality Check

- **Round 1 (Orchestrator - Claude)**: 
  - Validate prompt completeness
  - Check dimension requirements
  - Verify seed consistency

- **Round 2 (Executor - Codex)**:
  - Execute generation script
  - Save files with proper naming
  - Generate metadata JSON

- **Round 3 (Analyst - Gemini)**:
  - Review style consistency
  - Check brand alignment
  - Suggest prompt improvements

### Agent Roles

| Agent | Role | Tools |
|-------|------|-------|
| Claude | Prompt engineering, quality validation | Write, Read |
| Codex | Script execution, batch processing | Bash, Write |
| Gemini | Style analysis, brand consistency check | Read, ask-gemini |

### Example Multi-Agent Workflow

```bash
# 1. Claude: Generate prompts and script
# 2. Codex: Execute generation
bash -c "python generate_images.py"

# 3. Gemini: Review outputs
ask-gemini "@outputs/ Analyze brand consistency of generated images"
```

---

## Metadata

### Version
- **Current Version**: 1.0.0
- **Last Updated**: 2026-02-13
- **Compatible Platforms**: Claude, ChatGPT, Gemini, Codex

### Related Skills
- [image-generation](../image-generation/SKILL.md) - MCP-based image generation
- [design-system](../design-system/SKILL.md) - Design system implementation
- [presentation-builder](../presentation-builder/SKILL.md) - Presentation creation

### API Documentation
- Official Site: https://pollinations.ai
- API Endpoint: https://image.pollinations.ai/prompt/{prompt}
- Models: flux, turbo, stable-diffusion

### Tags
`#pollinations` `#image-generation` `#free` `#api` `#url-based` `#no-signup` `#creative`
