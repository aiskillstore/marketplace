# Seedance-Product-Video

为 [Seedance 2.0](https://jimeng.jianying.com) 视频生成模型撰写产品宣传动画提示词的 AI Skill。

Generate professional 15-second motion graphics prompts for Seedance 2.0 video model — one-take, no cuts, smooth morphing transitions.

## Features

- 4 种美学风格可选：Apple Cupertino / Microsoft Fluent / Bauhaus Zen / Vercel Dark
- 15 秒一镜到底，5-6 个连续形变阶段的时间戳结构
- 支持垫图（参考图）模式，自动标注图片占位符并引导使用"全能参考"模式
- 生成后可通过即梦 Dreamina CLI 直接生成视频（自动检测安装状态）

## Installation

### Option 1: npx skills (Recommended)

Using [vercel-labs/skills](https://github.com/vercel-labs/skills):

```bash
npx skills add op7418/Seedance-Product-Video -a claude-code
```

Global install:

```bash
npx skills add op7418/Seedance-Product-Video -a claude-code -g
```

### Option 2: Manual

Clone the repo into your Claude Code skills directory:

```bash
git clone https://github.com/op7418/Seedance-Product-Video.git ~/.claude/skills/seedance-prompt
```

## Usage

Tell your AI assistant:

```
帮我生成一个 Seedance 产品宣传视频的提示词
```

Or use the slash command directly:

```
/seedance-prompt
```

The skill will:

1. Ask about your product, requirements, and image assets
2. Analyze your materials and select the best visual style
3. Generate a 1000-2000 character English prompt with timestamp structure
4. Guide you through reference image setup (if applicable)
5. Offer to generate the video via Dreamina CLI

## Aesthetic Styles

| Style | Vibe | Best For |
|-------|------|----------|
| A: Apple Cupertino | Frosted glass, titanium depth | Flagship products, premium hardware |
| B: Microsoft Fluent | Acrylic layers, colorful gradients | Productivity tools, platforms |
| C: Bauhaus / Kenya Hara | Matte zen, minimal whitespace | Efficiency tools, readers |
| D: Vercel / Linear | Void black, neon accent lines | Developer tools, frameworks |

## Prompt Structure

```
0–2s  [STATE A → STATE B]   Chaos snaps into first form
2–4s  [STATE B → STATE C]   Melts/morphs into second form
4–7s  [STATE C → STATE D]   Wraps into complex 3D structure
7–10s [STATE D → STATE E]   Flattens into dynamic 2D pattern
10–12s [STATE E → PRE-LOGO] Snaps into logo hint
12–13s [HOLD]               Silent beat
13–15s [LOGO]               Brand reveal

+ Sound Design              Audio arc referencing visual moments
+ Music                     Background music style & tempo
+ Voiceover (inline)        Embedded in timeline stages (if requested)
```

## Dreamina CLI Integration

After generating the prompt, the skill checks if [Dreamina CLI](https://jimeng.jianying.com/cli) is installed and offers to:

- Install it if missing: `curl -fsSL https://jimeng.jianying.com/cli | bash`
- Generate the video directly using the prompt

## File Structure

```
seedance-prompt/
├── SKILL.md                      # Main skill definition
├── README.md                     # This file
└── references/
    └── prompt-system.md          # Prompt system: aesthetic matrix + rules + template
```

## Credits

Prompt engineering inspiration from [@oggii_0](https://x.com/oggii_0/status/2041392542659584302).

## License

MIT
