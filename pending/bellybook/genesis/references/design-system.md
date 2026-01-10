# 设计系统配置：shadcn/ui 组件库集成

## 1. 初始化 shadcn/ui

```bash
npx shadcn@latest init
```

配置选项：
- Style: Default
- Base color: 按需选择
- CSS variables: Yes
- 路径别名自动读取 jsconfig.json / tsconfig.json

---

## 2. 安装主题

```bash
npx shadcn@latest add https://tweakcn.com/r/themes/cyberpunk.json

```

---

## 3. 分批安装组件（避免超时）

> **重要**：一次安装太多组件会导致超时，必须分批安装！

**第一批：核心交互组件**
```bash
npx shadcn@latest add button input label card dialog sheet
```

**第二批：表单组件**
```bash
npx shadcn@latest add form select checkbox radio-group switch textarea
```

**第三批：反馈组件**
```bash
npx shadcn@latest add alert sonner badge skeleton progress
```

**第四批：导航组件**
```bash
npx shadcn@latest add tabs accordion dropdown-menu navigation-menu
```

**第五批：展示组件**
```bash
npx shadcn@latest add avatar table popover tooltip hover-card
```

**第六批：工具组件**
```bash
npx shadcn@latest add scroll-area separator command collapsible
```

**按需安装**（项目用到再装）：
```bash
npx shadcn@latest add slider toggle toggle-group menubar context-menu aspect-ratio
```

---

## 4. 设计系统约定

### src/index.css

```css
@import "tailwindcss";
```

### 核心原则

**一切设计必须来自设计系统的颜色和组件**

- 禁止使用硬编码颜色值（如 `#ff0000`、`rgb()`）
- 只使用 CSS 变量定义的语义化颜色（如 `bg-primary`、`text-muted-foreground`）
- 优先使用 shadcn/ui 组件，避免重复造轮子

---

## 5. 推荐目录结构

```
src/
├── components/
│   └── ui/              # shadcn 组件（自动生成）
├── lib/
│   └── utils.ts         # cn() 函数（自动生成）
├── index.css
└── App.jsx
```

---

## 6. 页面骨架搭建

初始化完成后，用设计系统组件制作：

1. **Header** - 导航栏，包含 react-router 驱动的 DesignSystem 展示页面入口
2. **Hero** - 首屏展示区
3. **Footer** - 页脚

---

## 7. 常见问题排查

| 问题 | 解决方案 |
|------|----------|
| 安装超时 | 分批安装，每批不超过 6 个组件 |
| npm warn Unknown user config | 可忽略，不影响安装 |
| 路径别名报错 | 检查 jsconfig.json 中 `@/*` 配置 |
| 组件样式不生效 | 确认 index.css 已导入 tailwindcss |

---

## 8. L1/L2 文档强调事项

在项目文档中必须明确：

```markdown
## 设计系统约束

- 所有颜色必须使用设计系统 CSS 变量
- 所有 UI 组件必须基于 shadcn/ui
- 禁止硬编码样式值
```

完成后等待下一步指令。
