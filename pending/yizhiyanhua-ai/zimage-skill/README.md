# Z-Image Skill - AI Image Generation for Claude Code

<p align="center">
  <img src="./icon.png" alt="Z-Image Skill Icon" width="128" height="128">
</p>

> Generate beautiful images with natural language in Claude Code!

English | [中文](./README_CN.md)

## What is this?

Z-Image Skill is a Claude Code skill plugin that lets you generate AI images using simple natural language descriptions.

**Just say things like:**
- "Generate a picture of a golden cat"
- "Draw a sunset over mountains"
- "Create a cute cartoon avatar"

And Claude Code will automatically generate the image for you!

## Demo

```
You: Generate a cyberpunk style city at night

Claude: I'll generate that image for you...
        Task started: xxx
        Image saved to: cyberpunk_city.jpg

        Done! The image has been saved to cyberpunk_city.jpg
```

## Installation

> All steps can be completed using natural language in Claude Code - no manual commands needed!

### Step 1: Get Your Free API Key

1. Visit [ModelScope](https://modelscope.cn)
2. Click "Login/Register" in the top right corner
3. After logging in, go to [API Token page](https://modelscope.cn/my/myaccesstoken)
4. Click "Create Token" and copy your API Key

### Step 2: Install the Skill

Open Claude Code and simply say:

```
Install zimage-skill from https://github.com/yizhiyanhua-ai/zimage-skill
```

Claude will automatically:
- Download the skill to the correct directory
- Install the required Python dependencies

### Step 3: Configure API Key

In Claude Code, say:

```
Configure MODELSCOPE_API_KEY environment variable with value ms-xxxxxxxx (replace with your API Key)
```

Or you can say:

```
Add MODELSCOPE_API_KEY environment variable to ~/.claude/settings.json with value ms-xxxxxxxx
```

### Step 4: Verify Installation

After restarting Claude Code, simply say:

```
Generate a test image for me
```

If you see an image generated successfully, you're all set!

## Usage Examples

### Basic Usage

```
You: Generate a cute Shiba Inu picture
You: Draw an astronaut on the moon
You: Create an abstract art painting
```

### Specify Output Path

```
You: Generate a beach sunset image, save as sunset.jpg
You: Draw a panda, save to ~/Pictures/panda.png
```

### Detailed Descriptions for Better Results

```
You: Generate an image: an orange cat sitting on a windowsill,
     rainy city night outside, warm indoor lighting,
     cinematic composition, 4K high definition

You: Create a painting: Chinese ink wash style landscape,
     misty mountains in the distance, a small boat nearby,
     serene and peaceful atmosphere
```

### Style Examples

| Description | Result |
|-------------|--------|
| "Cyberpunk Tokyo street" | Neon lights, futuristic |
| "Ghibli-style forest" | Studio Ghibli aesthetic |
| "Oil painting of sunflowers" | Van Gogh style |
| "Minimalist geometric pattern" | Modern design |
| "Chinese style koi fish" | Traditional Chinese art |
| "Pixel art game character" | Retro gaming style |

### Practical Use Cases

**1. Create Avatars**
```
You: Generate a cute cartoon avatar, girl with pink hair, big eyes, smiling
```

**2. Article Illustrations**
```
You: I'm writing an article about AI, generate a tech-themed illustration
```

**3. Social Media Content**
```
You: Generate a scenic landscape photo suitable for Instagram, calming vibes
```

**4. Design Inspiration**
```
You: Draw an app splash screen background, gradient colors, abstract, modern
```

**5. Meme Creation**
```
You: Generate a surprised cat face, cartoon style, exaggerated expression
```

## FAQ

### Q: Getting "MODELSCOPE_API_KEY environment variable is required"

A: You haven't configured your API Key yet. Follow Steps 1 and 2 in the Installation section.

### Q: Image generation fails or times out

A: Possible reasons:
- Network connection issues - check your internet
- API service is busy - try again later
- Content may have triggered moderation - modify your description

### Q: Generated image quality is not ideal

A: Try these tips:
- Use more detailed descriptions
- Add quality keywords (e.g., "high definition", "4K", "cinematic", "professional photography")
- Specify art style (e.g., "oil painting style", "watercolor", "anime style")

### Q: What image formats are supported?

A: Default output is JPG format. PNG is also supported (just specify in the filename).

## Technical Information

- **Model**: Tongyi-MAI/Z-Image-Turbo
- **API Provider**: ModelScope (Alibaba Cloud)
- **Timeout**: 120 seconds
- **Supported Languages**: Chinese, English

## Getting Help

If you encounter issues:
1. Check the FAQ section above
2. Submit an Issue on GitHub
3. Verify your API Key is correctly configured

## License

MIT License - Free to use and modify
