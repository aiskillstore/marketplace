# React 19 + Vite + TailwindCSS V4 初始化指南

## 0. 检查 Node.js 环境

```bash
node -v
```

**显示版本号（如 v20.x.x）**：跳到步骤 1

**提示 command not found**：按以下方式安装

### macOS 安装 Node.js

```bash
brew install node

# 验证安装
node -v && npm -v
```

### Windows 安装 Node.js

1. 访问 https://nodejs.org
2. 下载 LTS 版本
3. 双击安装，一路 Next
4. 重启终端，运行 `node -v` 验证

---

## 1. 创建项目并安装依赖

```bash
npm create vite@latest . -- --template react && npm install
```

---

## 2. 安装 TailwindCSS V4（Vite 插件版）

```bash
npm install tailwindcss @tailwindcss/vite
```

---

## 3. 配置 vite.config.js

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
})
```

---

## 4. 配置 src/index.css

清空文件，仅保留一行：

```css
@import "tailwindcss";
```

> Tailwind V4 已废弃 `@tailwind base/components/utilities` 写法

---

## 5. 添加路径别名（可选）

### jsconfig.json

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

### vite.config.js 追加 resolve

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

---

## 6. 安装 UI 增强库

```bash
npm install framer-motion lucide-react clsx tailwind-variants react-icons
```

| 库 | 用途 |
|---|------|
| `framer-motion` | 动效引擎 |
| `lucide-react` | 系统图标 |
| `clsx` | 条件类名 |
| `tailwind-variants` | 组件变体 |
| `react-icons` | 社媒图标（Si 前缀） |

---

## 7. 图标与动效约定

```jsx
// 系统图标 - lucide-react
import { Menu, X, ChevronDown } from 'lucide-react'

// 社媒图标 - react-icons（Si 前缀）
import { SiGithub, SiTwitter } from 'react-icons/si'

// 动效 - framer-motion
import { motion } from 'framer-motion'

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
  内容
</motion.div>
```

---

## 8. 推荐目录结构

```
src/
├── components/       # 通用组件
├── features/         # 业务功能模块
├── hooks/            # 自定义 Hooks
├── lib/              # 工具函数
├── styles/           # 全局样式
├── App.jsx
├── main.jsx
└── index.css
```

---

## 9. 初始化完成检查

- [ ] `npm run dev` 启动成功
- [ ] TailwindCSS 类名生效
- [ ] 路径别名 `@/` 可用
- [ ] 构建 L1/L2/L3 文档，实现分形初始化

等待下一步指令。
