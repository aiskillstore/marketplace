# Taro 4.x + React + Tailwind CSS v4 小程序

> 基于 Taro 4.x 构建跨端小程序，支持微信、支付宝、抖音等多平台

## 技术栈

- **Taro 4.x**: 跨端小程序开发框架
- **React 18**: 前端框架
- **Tailwind CSS v4**: 原子化 CSS 框架
- **Vite**: 构建工具
- **weapp-tailwindcss**: 小程序 Tailwind 适配插件

---

## 一、项目初始化

### 使用 Taro CLI 创建项目

```bash
npx @tarojs/cli init {项目名} \
  --description "{项目名}" \
  --framework React \
  --no-typescript \
  --no-build-es5 \
  --npm Npm \
  --css None \
  --compiler Vite \
  --template-source github \
  --template default
```

---

## 二、Tailwind CSS v4 集成

### 1. 安装依赖

```bash
cd {项目名}
npm install -D tailwindcss @tailwindcss/postcss postcss weapp-tailwindcss
```

### 2. 配置 package.json

在 `scripts` 中添加：

```json
{
  "scripts": {
    "postinstall": "weapp-tw patch"
  }
}
```

> **重要**：该脚本用于 patch Tailwind CSS v4 以支持 `rpx` 单位  
> 若使用 pnpm@10+，需额外执行：`pnpm approve-builds weapp-tailwindcss`

### 3. 执行 patch

```bash
npm run postinstall
```

### 4. 配置 Vite 插件

修改 `config/index.js`：

```javascript
import { defineConfig } from "@tarojs/cli";
import { UnifiedViteWeappTailwindcssPlugin } from "weapp-tailwindcss/vite";
import tailwindcss from "@tailwindcss/postcss";
import path from "node:path";

export default defineConfig(async (merge, { command, mode }) => {
  const baseConfig = {
    // ... 其他配置

    compiler: {
      type: "vite",
      vitePlugins: [
        {
          name: "postcss-config-loader-plugin",
          config(config) {
            if (typeof config.css?.postcss === "object") {
              config.css?.postcss.plugins?.unshift(tailwindcss());
            }
          },
        },
        UnifiedViteWeappTailwindcssPlugin({
          rem2rpx: true,
          cssEntries: [path.resolve(__dirname, "../src/app.css")],
        }),
      ],
    },
  };

  // ... 环境配置
});
```

### 5. 引入 Tailwind 样式

修改 `src/app.css`：

```css
@import "tailwindcss";
```

---

## 三、tweakcn 主题系统集成

> [tweakcn](https://tweakcn.com) 是 shadcn/ui 风格的主题生成器，提供语义化设计令牌

将以下内容写入 `src/app.css`（完整替换）：

```css
@import "tailwindcss";

/* ============================================================
   CYBER NEON DESIGN SYSTEM (tweakcn)
   霓虹粉 #ff00c8 + 赛博青 #00ffcc | Outfit 字体
   ============================================================ */

/* ------------------------------------------------------------
   LIGHT MODE
   ------------------------------------------------------------ */
:root {
  --background: #f8f9fa;
  --foreground: #0c0c1d;
  --card: #ffffff;
  --card-foreground: #0c0c1d;
  --popover: #ffffff;
  --popover-foreground: #0c0c1d;
  --primary: #ff00c8;
  --primary-foreground: #ffffff;
  --secondary: #f0f0ff;
  --secondary-foreground: #0c0c1d;
  --muted: #f0f0ff;
  --muted-foreground: #0c0c1d;
  --accent: #00ffcc;
  --accent-foreground: #0c0c1d;
  --destructive: #ff3d00;
  --destructive-foreground: #ffffff;
  --border: #dfe6e9;
  --input: #dfe6e9;
  --ring: #ff00c8;
  --chart-1: #ff00c8;
  --chart-2: #9000ff;
  --chart-3: #00e5ff;
  --chart-4: #00ffcc;
  --chart-5: #ffe600;
  --radius: 0.5rem;
}

/* ------------------------------------------------------------
   DARK MODE
   ------------------------------------------------------------ */
.dark {
  --background: #0c0c1d;
  --foreground: #eceff4;
  --card: #1e1e3f;
  --card-foreground: #eceff4;
  --popover: #1e1e3f;
  --popover-foreground: #eceff4;
  --primary: #ff00c8;
  --primary-foreground: #ffffff;
  --secondary: #1e1e3f;
  --secondary-foreground: #eceff4;
  --muted: #151530;
  --muted-foreground: #8085a6;
  --accent: #00ffcc;
  --accent-foreground: #0c0c1d;
  --destructive: #ff3d00;
  --destructive-foreground: #ffffff;
  --border: #2e2e5e;
  --input: #2e2e5e;
  --ring: #ff00c8;
  --chart-1: #ff00c8;
  --chart-2: #9000ff;
  --chart-3: #00e5ff;
  --chart-4: #00ffcc;
  --chart-5: #ffe600;
}

/* ------------------------------------------------------------
   TAILWIND CSS V4 @theme
   ------------------------------------------------------------ */
@theme inline {
  --font-sans: Outfit, system-ui, sans-serif;
  --font-mono: "Fira Code", monospace;

  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-popover: var(--popover);
  --color-popover-foreground: var(--popover-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-destructive-foreground: var(--destructive-foreground);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --color-chart-1: var(--chart-1);
  --color-chart-2: var(--chart-2);
  --color-chart-3: var(--chart-3);
  --color-chart-4: var(--chart-4);
  --color-chart-5: var(--chart-5);

  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
}

/* ------------------------------------------------------------
   BASE STYLES
   ------------------------------------------------------------ */
@layer base {
  page {
    background-color: var(--background);
    color: var(--foreground);
    font-family: Outfit, system-ui, sans-serif;
  }
}
```

### 验证主题生效

修改 `src/pages/index/index.jsx`，使用语义化设计令牌创建主题展示页面。

---

## 四、清理无关资源

### 1. 删除无用 CSS 文件

```bash
rm src/pages/index/index.css
```

### 2. 删除 stylelint 配置文件

```bash
rm stylelint.config.mjs
```

### 3. 移除 stylelint 依赖（用 Tailwind 后不需要 CSS lint）

```bash
npm uninstall stylelint stylelint-config-standard
```

---

## 五、初始化完成检查

- [ ] `npm run dev:weapp` 启动成功
- [ ] Tailwind CSS 类名生效
- [ ] tweakcn 主题色彩正确显示
- [ ] 深色模式切换正常（添加 `.dark` 类到 `page` 元素）
- [ ] 构建 L1/L2/L3 分形文档体系

---

## 参考资源

- [Taro 官方文档](https://taro-docs.jd.com/)
- [weapp-tailwindcss 文档](https://weapp-tw.icebreaker.top/)
- [Tailwind CSS v4 文档](https://tailwindcss.com/docs)
- [tweakcn 主题生成器](https://tweakcn.com) - shadcn/ui 风格主题系统

等待下一步指令。
