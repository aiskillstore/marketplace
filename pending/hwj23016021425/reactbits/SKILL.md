---
name: reactbits
description: Search, browse, and install animated React components from ReactBits.dev (135+ components). Use when the user wants to add UI effects, animations, backgrounds, or interactive components to their React/Next.js project.
---

# ReactBits Skill

You have access to the ReactBits MCP server via the following tools:

- `mcp__reactbits__list_categories` — List all component categories
- `mcp__reactbits__list_components` — List components, optionally filter by `category` (Animations, Backgrounds, Text Animations, Components, Buttons, Forms, Loaders), `style` (tailwind, css, default), `limit`
- `mcp__reactbits__search_components` — Search components by `query`, filter by `category`, `limit`
- `mcp__reactbits__get_component` — Get full source code for a component by `name` (slug), optionally specify `style` (tailwind, css, default)
- `mcp__reactbits__get_component_demo` — Get usage example and demo code for a component by `name`

## Website Builder Mode

**When the user says they want to "build a website", "make a site", "create a landing page", "做一个网站", "帮我搭个页面", or any similar intent — DO NOT wait for them to specify what components they need. Instead, ASK these questions first:**

1. **Purpose** — 这个网站是做什么的？（个人作品集 / 公司官网 / 产品落地页 / 博客 / 活动页 / 其他）
2. **Style** — 你喜欢什么风格？（极简 / 科技感 / 复古 / 可爱卡通 / 暗黑炫酷 / 商务专业）
3. **Color** — 有偏好的主色调吗？（紫色 / 蓝色 / 绿色 / 暖色 / 黑白 / 让我推荐）
4. **Pages** — 需要哪些页面？（首页 / 关于 / 作品展示 / 联系 / 博客 / 其他）
5. **Key Features** — 有什么特别想要的功能？（3D 背景 / 粒子效果 / 滚动动画 / 视频展示 / 卡片交互 / 文字动画）

**After getting answers, DO this:**
1. Search ReactBits for components that match their style and needs
2. Recommend 3-5 components with brief descriptions
3. Ask which ones they want to add
4. Install and integrate them one by one

## How to use

When the user asks about ReactBits components:

1. **List available components**: Use `list_components` or `list_categories` to show what's available
2. **Search for something specific**: Use `search_components` with the user's query
3. **Get source code**: Use `get_component` to retrieve the full component source
4. **Get demo/usage example**: Use `get_component_demo` to see how to use it

## Integration workflow

When the user wants to add a component to their project:

1. **Get the component source** via `get_component` with the user's preferred style (tailwind or css)
2. **Get the demo code** via `get_component_demo` to understand usage
3. **Check dependencies** — the component metadata includes required packages (framer-motion, GSAP, Three.js, etc.). Install any missing ones.
4. **Write the component file** to the project's `components/` directory
5. **Import CSS if needed** — if `hasCSS: true`, create the corresponding CSS file
6. **Import and use** the component in the appropriate page/section

## Style preference

Always ask the user which style they prefer:
- **Tailwind** (recommended for this project) — uses Tailwind CSS classes
- **CSS** — uses separate CSS modules
- **TypeScript** — always use the TypeScript variant

## Categories reference

| Category | Count | Common components |
|----------|-------|-------------------|
| Text Animations | 23 | BlurText, ShinyText, SplitText, ShuffleText, CircularText |
| Animations | 27 | ClickSpark, BlobCursor, FadeContent, Crosshair, Cubes |
| Components | 35 | Stack, FlowingMenu, GooeyNav, BounceCards, CircularGallery |
| Backgrounds | 35 | Dither, ColorBends, GridScan, PixelSnow, LiquidEther |
| Buttons | — | Various animated button components |
| Forms | — | Animated form elements |
| Loaders | — | Loading animations |
