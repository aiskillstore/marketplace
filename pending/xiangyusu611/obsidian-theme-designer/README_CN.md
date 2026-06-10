# Obsidian Theme Designer

English | [中文](README_CN.md)

**告别盲选主题。在浏览器中可视化设计你的 Obsidian 主题。**

一个 Claude Code 技能，通过逐步引导和浏览器实时预览，帮你设计 Obsidian 自定义主题。不需要 CSS 知识。

---

## 工作流程

### 第一步：选择风格方向

从 5 个风格方向中选择 —— 每个都以实际效果展示，而不是文字描述。

![风格方向选择](screenshots/style-directions.png)

### 第二步：选择配色

选择冷色、暖色或中性色调，立即看到效果。

![配色方案选择](screenshots/color-palettes.png)

### 第三步：选择字体

浏览 8-10 组特色字体搭配，用你的实际内容渲染。支持混搭 —— 中文选一个卡片的字体，英文选另一个。

![字体展示](screenshots/font-showcase.png)

### 第四步：预览和微调

在完整的 Obsidian 模拟界面中查看最终效果 —— 侧边栏、编辑器、浅色和深色模式并排展示。反复调整直到满意。

![双模式预览](screenshots/dual-mode-preview.png)

### 第五步：一键安装

技能自动生成 CSS 代码片段、安装字体，并告诉你如何在 Obsidian 中启用。完成。

---

## 特性

- **视觉优先** —— 所有选择都在浏览器中展示，不只是文字描述
- **双语预览** —— 所有预览都包含中英文混排内容
- **智能字体** —— 使用 `frontend-design` 技能选择有特色的非通用字体
- **双模式** —— 浅色和深色主题可以使用不同的强调色
- **自动安装字体** —— 从 Google Fonts 下载并安装到系统（Windows/macOS/Linux）
- **非设计师友好** —— 直观类比（"像 LaTeX PDF"）、推荐默认值、支持参考图

---

## 快速开始

1. 将 `obsidian-theme-designer/` 复制到 `~/.claude/skills/`
2. 在 Claude Code 中打开你的 Obsidian vault 文件夹
3. 输入：**"帮我设计 Obsidian 主题"**

## 依赖

- [Claude Code](https://claude.ai/code)
- [superpowers](https://github.com/claude-plugins-official/superpowers) 插件（用于浏览器可视化预览）
- [frontend-design](https://github.com/claude-plugins-official/frontend-design) 插件（可选，用于字体选择）

## 许可证

MIT
