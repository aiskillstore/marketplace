---
name: visual-reviewer
description: >
  视觉审查 - 在产出可视化结果（网页、文档、UI
  界面等）后，自动打开/预览结果，通过截图分析视觉质量问题（布局、间距、对齐、排版、颜色、交互状态等），并自主修复发现的问题。

  This skill should be used automatically after producing any visual output.

  Triggers: 视觉审查, 视觉检查, 界面检查, UI审查, visual review, layout check, 检查界面, 看看效果
disable: false
---

# 视觉审查 (Visual Reviewer)

在 AI 产出一个可视化结果后，自动进行视觉层面的质量审查和自主修复。

## 触发条件

本 Skill 在以下产出物完成后应**自动触发**，无需用户手动要求：
- HTML 页面 / Web 应用界面
- Markdown 文档（含表格、代码块等富文本）
- PPT / 演示文稿
- 任何用户可见的视觉产出物

## 截图策略（按产物类型）

### 策略 A — Web 页面 (HTML/Web应用)

**首选方案：精确窗口截图**（Python，推荐）
1. 用 `preview_url` 打开页面 → 页面在 WorkBuddy 内置浏览器面板中渲染
2. 用 Python 截图脚本按 WorkBuddy 窗口标题精确截取客户区：
   ```bash
   python "<skill_path>/scripts/capture_screenshot.py" \
       --output "<screenshot_path>" \
       --mode window \
       --title "WorkBuddy"
   ```
   - 自动查找标题含 "WorkBuddy" 的窗口 → 置顶 → 截取**客户区**（不含标题栏/边框）
   - 使用 `ctypes` 调用 Win32 API + `mss` 高速截屏，无环境块限制

**备选方案：外部浏览器截图**
1. 启动本地 HTTP 服务器：`python -m http.server 8765 -d <产物目录>`
2. 打开浏览器访问 `http://localhost:8765/<file>.html`
3. 等待 2-3 秒页面加载，按浏览器进程名截图：
   ```bash
   python "<skill_path>/scripts/capture_screenshot.py" -o "<path>" -m window -p "chrome"
   # 或
   python "<skill_path>/scripts/capture_screenshot.py" -o "<path>" -m window -p "msedge"
   ```

### 策略 B — 文档 / PPT

1. 用 `open_result_view` 打开文档
2. 按窗口标题或进程名精确截图：
   ```bash
   # 按窗口标题部分匹配（文档名在窗口标题中）
   python "<skill_path>/scripts/capture_screenshot.py" -o "<path>" -m window -t "<文档名关键字>"

   # 按进程名截图
   python "<skill_path>/scripts/capture_screenshot.py" -o "<path>" -m window -p "WINWORD"
   ```

### 策略 C — 屏幕区域（指定坐标）

需要截取屏幕特定区域时（如 WorkBuddy 内置浏览器面板的精确位置）：
```bash
python "<skill_path>/scripts/capture_screenshot.py" -o "<path>" -m region -r "X,Y,W,H"
```

### 截图脚本参数速查

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--mode window -t` | `-m window -t` | 按窗口标题截取**特定程序窗口** | `-m window -t "stock-watcher"` |
| `--mode window -p` | `-m window -p` | 按进程名截取**特定程序窗口** | `-m window -p "chrome"` |
| `--mode region -r` | `-m region -r` | 按屏幕坐标截取**指定区域** | `-m region -r "100,200,800,600"` |
| `--mode activewindow` | `-m activewindow` | 截取当前**前台窗口** | `-m activewindow` |
| `--mode fullscreen` | `-m fullscreen` | 截取整个**主屏幕**（兜底） | `-m fullscreen` |
| `--client-only false` | | 截取含标题栏/边框的整窗 | 默认 `true`（仅客户区） |

**输出格式**：成功时最后一行输出 `OK:<mode>:<path>`，失败时输出错误信息和可见窗口列表方便调试。

**依赖**：需要 Python + `mss` + `pygetwindow`（已随 Skill 安装说明提供 requirements.txt）。

## 工作流程

### Step 1 — 打开/预览结果

| 产出类型 | 打开方式 |
|----------|----------|
| HTML / Web 页面 | `preview_url` 打开本地文件或 localhost URL |
| 文档 / PPT / 其他 | `open_result_view` 打开结果文件 |

### Step 2 — 选择截图策略并执行

根据产物类型选择上述策略 A/B/C，调用截图脚本。

截图保存为 PNG 格式后，使用 Read 工具读取截图进行视觉分析。

### Step 3 — 视觉检查清单

逐项检查以下维度，每个维度 0-3 分（0=严重问题 / 1=有问题 / 2=可接受 / 3=良好）：

| 维度 | 检查项 |
|------|--------|
| **布局** | 元素对齐（水平/垂直）、重叠、响应式断点、空白分布 |
| **间距** | padding/margin 一致性、元素间距匀称、边界留白 |
| **排版** | 字体层级（h1-h6 视觉差）、行高/字间距、文字截断/溢出 |
| **颜色** | 对比度（WCAG AA）、配色协调、暗色/亮色模式适配 |
| **交互** | 按钮可点击区域、hover/active 状态、焦点可见性 |
| **数据展示** | 表格列宽合理性、数字对齐、图表标签完整性 |
| **边界情况** | 空数据状态、超长文字截断、极端窗口尺寸（320px / 4K） |

详细清单见 `references/visual_checklist.md`。

### Step 4 — 自主修复

对每个发现的问题：
1. 确定根本原因（CSS 属性 / 布局逻辑 / 数据格式问题）
2. 修改对应代码或样式
3. 修复后重新预览 / 截图确认

### Step 5 — 审查报告

```
## 视觉审查报告

### 发现的问题 (共 N 个)
| # | 严重度 | 问题 | 原因 | 修复 | 状态 |
|---|--------|------|------|------|------|
| 1 | 严重 | 导航栏与内容区重叠 | z-index 缺失 | 添加 z-index: 100 | ✓ |
| 2 | 中等 | 按钮间距不一致 | margin 值不统一 | 统一为 8px | ✓ |
| 3 | 轻微 | 标题字体偏小 | font-size 16px | 建议改为 20px | 待确认 |

### 审查覆盖率
布局: ✓ | 间距: ✓ | 排版: ✓ | 颜色: ✓ | 交互: ✓ | 数据展示: N/A | 边界: ✓
```

## 工作原则

1. **自动触发**: 产出可视化结果后必须执行审查流程，不等待用户指令
2. **截图优先**: 必须通过截图分析视觉效果，不凭代码推断
3. **精确截图**: 优先使用按窗口标题/进程名的精确截图，全屏截图仅作兜底
4. **主动修复**: 明显的视觉问题直接修复，不"只报告不行动"
5. **分级处理**: 严重/中等问题 → 立即修复；轻微问题 → 修复 + 标注可回滚
6. **不破坏功能**: 视觉修复只改样式和布局，不改变业务逻辑
7. **循环验证**: 修复后必须重新截图确认，修复 → 验证最多循环 3 次
8. **报告完整**: 每次审查结束后输出完整报告，含修复前后对比
