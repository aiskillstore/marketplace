# Landing Page 架构规范：一次性生成生产级落地页

> **前置条件**：必须先完成设计系统初始化和设计提升。

---

## 设计系统约束（强制）

```
本步骤所有代码必须遵循以下约束：

1. 颜色来源：只使用 index.css 中的 CSS 变量
   - hsl(var(--primary))、hsl(var(--secondary))、hsl(var(--accent))
   - hsl(var(--background))、hsl(var(--foreground))、hsl(var(--muted))
   - 禁止硬编码颜色值如 #fff、rgb()、hsl(330, 81%, 70%)

2. 组件来源：只使用 src/components/ui/ 下已安装的 shadcn 组件
   - Button、Card、Badge、Input、Accordion、Avatar 等
   - 如需更多组件，先运行：npx shadcn@latest add [组件名]
   - 禁止从零手写基础组件

3. 变体使用：优先使用设计提升后的变体
   - Button: 微拟物渐变效果
   - Card: 凸起/内凹变体
   - Badge: 渐变背景
```

---

## 全局 Design Tokens

```javascript
// 在生成代码前，先确认以下设计变量
const designTokens = {
  // 品牌色彩
  brand: {
    primary: '',      // 主色调（CTA、强调）
    secondary: '',    // 辅助色（次级操作）
    accent: '',       // 点缀色（图标、徽章）
  },
  
  // 排版比例 (Type Scale)
  typography: {
    hero: 'text-5xl md:text-6xl lg:text-7xl',     // H1 Hero
    display: 'text-4xl md:text-5xl',               // Section Heading
    title: 'text-2xl md:text-3xl',                 // Card Title
    subtitle: 'text-lg md:text-xl',                // Subheading
    body: 'text-base',                             // Paragraph
    caption: 'text-sm',                            // 辅助文字
  },
  
  // 间距系统 (Spacing Scale)
  spacing: {
    section: 'py-20 md:py-28 lg:py-32',           // Section 垂直间距
    container: 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8',
    stack: 'space-y-4',                            // 垂直堆叠
    inline: 'space-x-4',                           // 水平排列
  },
  
  // 动效曲线 (Motion Easing)
  motion: {
    entrance: { duration: 0.6, ease: [0.22, 1, 0.36, 1] },
    stagger: 0.1,
    viewport: { once: true, margin: '-100px' },
  }
}
```

---

## 页面信息架构 (IA)

请提供以下内容变量，AI 将据此填充各 Section：

```javascript
const pageContent = {
  // Meta
  siteName: '',
  tagline: '',
  
  // Hero Section
  hero: {
    headline: '',           // 主标题（6-12字，价值主张）
    subheadline: '',        // 副标题（20-40字，痛点共鸣）
    primaryCTA: '',         // 主按钮文案
    secondaryCTA: '',       // 次按钮文案（可选）
    socialProof: '',        // 信任背书（如：已有 10,000+ 用户）
    visual: 'hero|video|lottie|3d',  // 视觉类型
  },
  
  // Logos / Social Proof Bar
  logoBar: {
    title: '',              // 如："Trusted by"
    logos: [],              // 客户/媒体 Logo 数组
  },
  
  // Problem-Agitation Section
  problem: {
    headline: '',           // 痛点标题
    painPoints: [],         // 3-4个痛点描述
  },
  
  // Solution / Features Section
  features: {
    headline: '',
    subheadline: '',
    items: [
      { icon: '', title: '', description: '' },
      // ... 3-6 个特性
    ],
    layout: 'grid|bento|alternating',  // 布局模式
  },
  
  // How It Works Section
  howItWorks: {
    headline: '',
    steps: [
      { step: 1, title: '', description: '', visual: '' },
      // ... 3-5 个步骤
    ],
  },
  
  // Social Proof Section
  testimonials: {
    headline: '',
    items: [
      { quote: '', author: '', role: '', company: '', avatar: '' },
      // ... 3-6 条评价
    ],
    layout: 'carousel|grid|marquee',
  },
  
  // Pricing Section
  pricing: {
    headline: '',
    subheadline: '',
    plans: [
      { 
        name: '', 
        price: '', 
        period: '', 
        description: '',
        features: [],
        cta: '',
        highlighted: false 
      },
      // ... 2-4 个定价方案
    ],
  },
  
  // FAQ Section
  faq: {
    headline: '',
    items: [
      { question: '', answer: '' },
      // ... 5-8 个问题
    ],
  },
  
  // Final CTA Section
  finalCTA: {
    headline: '',
    subheadline: '',
    primaryCTA: '',
    secondaryCTA: '',
  },
  
  // Footer
  footer: {
    columns: [
      { title: '', links: [{ label: '', href: '' }] },
    ],
    legal: [],
    social: [],
  },
}
```

---

## Section 组件规范

### 1. Hero Section（Above the Fold）

```
┌─────────────────────────────────────────────────────────────┐
│  [Nav]  Logo          Links...              [CTA Button]    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│         [Badge/Announcement Bar - optional]                 │
│                                                             │
│              ██  HEADLINE  ██                               │
│              (Display/H1, max 12 words)                     │
│                                                             │
│         Subheadline - Value proposition                     │
│         (Body text, 2-3 lines max)                          │
│                                                             │
│         [Primary CTA]    [Secondary CTA]                    │
│                                                             │
│         "Social proof micro-copy"                           │
│                                                             │
│              ┌─────────────────────┐                        │
│              │   Hero Visual       │                        │
│              │   (Screenshot/      │                        │
│              │    Video/3D)        │                        │
│              └─────────────────────┘                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**技术要求：**
- Viewport Height: `min-h-screen` 或 `min-h-[90vh]`
- Visual Hierarchy: F-pattern 或 Z-pattern
- CTA Contrast Ratio: ≥ 4.5:1 (WCAG AA)
- LCP Element: Hero image 需 `priority` + `fetchpriority="high"`
- Motion: `staggerChildren` 入场动画，`viewport` 触发

---

### 2. Logo Bar / Trust Strip

```
┌─────────────────────────────────────────────────────────────┐
│                  "Trusted by industry leaders"              │
│                                                             │
│    [Logo]    [Logo]    [Logo]    [Logo]    [Logo]          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**技术要求：**
- 布局: `flex justify-center items-center gap-8 md:gap-12`
- Logo 样式: `grayscale opacity-60 hover:grayscale-0 hover:opacity-100`
- 可选: Infinite marquee animation (for 6+ logos)

---

### 3. Problem-Agitation Section

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│              "Still struggling with...?"                    │
│                                                             │
│    ┌─────────┐    ┌─────────┐    ┌─────────┐               │
│    │  ✗ Pain │    │  ✗ Pain │    │  ✗ Pain │               │
│    │  Point  │    │  Point  │    │  Point  │               │
│    │   #1    │    │   #2    │    │   #3    │               │
│    └─────────┘    └─────────┘    └─────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**技术要求：**
- 背景: Subtle gradient 或 muted surface
- 图标: Lucide `X` 或 `AlertCircle`，使用 destructive color
- Motion: `whileInView` fade-up stagger

---

### 4. Features Section（Bento Grid 变体）

```
┌─────────────────────────────────────────────────────────────┐
│              "Everything you need to..."                    │
│              Subheadline description                        │
│                                                             │
│    ┌───────────────────────┐    ┌───────────┐              │
│    │                       │    │  Feature  │              │
│    │    Feature #1         │    │    #2     │              │
│    │    (2x span)          │    │           │              │
│    │                       │    ├───────────┤              │
│    │                       │    │  Feature  │              │
│    │                       │    │    #3     │              │
│    └───────────────────────┘    └───────────┘              │
│    ┌───────────┐    ┌───────────┐    ┌───────────┐         │
│    │  Feature  │    │  Feature  │    │  Feature  │         │
│    │    #4     │    │    #5     │    │    #6     │         │
│    └───────────┘    └───────────┘    └───────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**布局变体：**
- `grid`: 标准 3-column grid
- `bento`: 不规则网格，突出核心功能
- `alternating`: 左右交替图文布局

**技术要求：**
- Grid: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6`
- Card: shadcn `Card` + `hover:shadow-lg transition-shadow`
- Icon: 40-48px，brand primary color
- Motion: `staggerChildren` + `scale` micro-interaction

---

### 5. How It Works Section

```
┌─────────────────────────────────────────────────────────────┐
│                    "How it works"                           │
│                                                             │
│      ①              ②              ③                        │
│    ┌────┐   ───▶  ┌────┐   ───▶  ┌────┐                    │
│    │Step│         │Step│         │Step│                    │
│    │ 1  │         │ 2  │         │ 3  │                    │
│    └────┘         └────┘         └────┘                    │
│    Title          Title          Title                      │
│    Desc           Desc           Desc                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**技术要求：**
- Step Indicator: 圆形数字徽章，brand primary
- Connector: 虚线或渐变线连接各步骤
- Motion: 顺序 reveal，带 path drawing animation

---

### 6. Testimonials Section

```
┌─────────────────────────────────────────────────────────────┐
│                "What our users say"                         │
│                                                             │
│    ┌────────────────────────────────────────────────┐      │
│    │  "Quote text here..."                          │      │
│    │                                                │      │
│    │  [Avatar]  Name                                │      │
│    │            Role @ Company                      │      │
│    └────────────────────────────────────────────────┘      │
│                                                             │
│              ●  ○  ○  ○  (carousel dots)                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**布局变体：**
- `carousel`: Embla Carousel，auto-play
- `grid`: 2-3 column masonry
- `marquee`: 无限滚动墙

**技术要求：**
- Quote Mark: 装饰性引号图形
- Avatar: 48px 圆形，带 ring border
- Star Rating: 可选，Lucide `Star` filled

---

### 7. Pricing Section

```
┌─────────────────────────────────────────────────────────────┐
│                    "Simple pricing"                         │
│              "No hidden fees, cancel anytime"               │
│                                                             │
│    ┌─────────┐    ┌─────────────┐    ┌─────────┐           │
│    │  Free   │    │    Pro      │    │  Team   │           │
│    │         │    │  ★ Popular  │    │         │           │
│    │   $0    │    │    $19      │    │   $49   │           │
│    │  /month │    │   /month    │    │  /month │           │
│    │         │    │             │    │         │           │
│    │ ✓ feat  │    │ ✓ feat      │    │ ✓ feat  │           │
│    │ ✓ feat  │    │ ✓ feat      │    │ ✓ feat  │           │
│    │ ✗ feat  │    │ ✓ feat      │    │ ✓ feat  │           │
│    │         │    │             │    │         │           │
│    │ [CTA]   │    │ [CTA]       │    │ [CTA]   │           │
│    └─────────┘    └─────────────┘    └─────────┘           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**技术要求：**
- Highlighted Plan: `ring-2 ring-primary scale-105`
- Badge: shadcn `Badge` 标注 "Most Popular"
- Feature List: Lucide `Check` / `X` icons
- Toggle: 可选 Monthly/Annual 切换器

---

### 8. FAQ Section

```
┌─────────────────────────────────────────────────────────────┐
│                 "Frequently asked questions"                │
│                                                             │
│    ┌────────────────────────────────────────────────┐      │
│    │  ▼  Question 1?                                │      │
│    │     Answer text...                             │      │
│    ├────────────────────────────────────────────────┤      │
│    │  ▶  Question 2?                                │      │
│    ├────────────────────────────────────────────────┤      │
│    │  ▶  Question 3?                                │      │
│    └────────────────────────────────────────────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**技术要求：**
- 组件: shadcn `Accordion`
- 布局: 单列居中，`max-w-3xl`
- Motion: `AnimatePresence` + height animation

---

### 9. Final CTA Section

```
┌─────────────────────────────────────────────────────────────┐
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│  ░                                                       ░  │
│  ░         "Ready to get started?"                       ░  │
│  ░         Subheadline reinforcing value                 ░  │
│  ░                                                       ░  │
│  ░         [Primary CTA]    [Secondary CTA]              ░  │
│  ░                                                       ░  │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
└─────────────────────────────────────────────────────────────┘
```

**技术要求：**
- 背景: Gradient mesh 或 brand primary with pattern
- 对比: 确保 CTA 在背景上清晰可见
- Motion: Subtle floating animation

---

### 10. Footer

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Logo              Product      Resources     Company       │
│  Tagline           Features     Blog          About         │
│                    Pricing      Docs          Careers       │
│                    Changelog    Help          Contact       │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  © 2025 Company     Privacy  Terms     [Social Icons]       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**技术要求：**
- Layout: 4-column grid，responsive collapse
- Links: `text-muted-foreground hover:text-foreground`
- Social: Lucide icons，24px

---

## 生成文件结构

```
src/
├── components/
│   ├── landing/
│   │   ├── Hero.jsx
│   │   ├── LogoBar.jsx
│   │   ├── ProblemSection.jsx
│   │   ├── FeaturesSection.jsx
│   │   ├── HowItWorks.jsx
│   │   ├── Testimonials.jsx
│   │   ├── Pricing.jsx
│   │   ├── FAQ.jsx
│   │   ├── FinalCTA.jsx
│   │   └── Footer.jsx
│   └── ui/
│       └── ... (shadcn components)
├── pages/
│   └── LandingPage.jsx       # 组合所有 sections
└── lib/
    └── motion.js             # Framer Motion variants
```

---

## Motion Variants 预设

```javascript
// src/lib/motion.js
export const fadeInUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] }
  }
}

export const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.2 }
  }
}

export const scaleIn = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: { 
    opacity: 1, 
    scale: 1,
    transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] }
  }
}

export const slideInLeft = {
  hidden: { opacity: 0, x: -30 },
  visible: { 
    opacity: 1, 
    x: 0,
    transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] }
  }
}

export const slideInRight = {
  hidden: { opacity: 0, x: 30 },
  visible: { 
    opacity: 1, 
    x: 0,
    transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] }
  }
}
```

---

## Accessibility Checklist

| 要求 | 实现方式 |
|------|----------|
| Semantic HTML | 使用 `<section>`, `<nav>`, `<main>`, `<footer>` |
| Heading Hierarchy | 每个 Section 仅一个 H2，子标题用 H3 |
| Color Contrast | 所有文字 ≥ 4.5:1，大文字 ≥ 3:1 |
| Focus States | 所有交互元素有 `focus-visible:ring-2` |
| Alt Text | 所有图片有描述性 alt |
| Reduced Motion | `prefers-reduced-motion` 媒体查询 |
| Keyboard Nav | Tab 顺序合理，可 Enter 激活 |

---

## Performance Checklist

| 指标 | 目标 | 实现方式 |
|------|------|----------|
| LCP | < 2.5s | Hero image 预加载，优先级提升 |
| FID | < 100ms | 延迟加载非关键 JS |
| CLS | < 0.1 | 图片设置 width/height，字体预加载 |
| Bundle Size | < 200KB | Tree-shaking，动态 import |

---

## GEB 分形文档检查

完成 Landing Page 开发后，**必须执行**以下文档同步：

```
L3 检查 → 新创建的组件文件头部是否添加 [INPUT]/[OUTPUT]/[POS] 注释？
L2 检查 → components/landing/CLAUDE.md 是否创建并记录所有 Section 组件？
L1 检查 → 项目根目录 CLAUDE.md 是否更新页面结构说明？
```

确保代码与文档同构，完成后等待下一步指令。
