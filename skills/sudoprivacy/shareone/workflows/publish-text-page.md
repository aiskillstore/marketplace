# 发布或更新文本/HTML 页面

当用户要发布对话、大段文本、代码、HTML、Markdown 或纯文本时读取本文件。发布前必须已经完成 `environment-and-credentials.md`。

适用文件类型：`.html`、`.md`、`.txt`。

不适用文件类型：`.ppt`、`.pptx`、`.pdf`、`.doc`、`.docx`、图片、zip 或其他二进制文件。遇到这些文件时，立即停止本 workflow，改读 `publish-binary-file.md`。不要使用 `upload_page.js` 发布二进制文件。

## 1. 识别目标内容

- 如果用户要求分享对话、大段文本或代码：从对话历史中提取上一轮生成的完整文本或代码块，保存到当前目录下的临时文件，例如 `share_note.md` 或 `share_note.html`。
- 如果是 Markdown 内容：建议在保存为 `.html` 前使用简单 HTML 模板包裹；如果无法确定后端是否渲染 Markdown，优先生成美观的 `.html` 文件。
- 对于提取的对话、大段文字或独立代码块，建议包装为带基础样式的美观 HTML，以保证展示效果。
- 如果用户指定了文件：使用用户指定的文件。
- 如果用户没有指定文件：根据上下文寻找最近一次生成或编辑的文本/HTML 文件，例如 `.html`、`.md`、`.txt`，或将对话/代码包装成 `.html`。
- 如果锁定的文件不存在，停止并告知用户。
- 如果锁定的文件是 `.ppt`、`.pptx`、`.pdf`、`.doc`、`.docx`、图片、zip 或其他二进制文件，停止本 workflow，改读 `publish-binary-file.md`。
- 提取用户可能要求的密码 (`password`)、水印 (`watermark`) 和自定义短链接后缀 (`slug`)。服务端会根据文件名自动生成可读的 slug，客户端无需主动设置。只有用户明确说”链接叫 xxx / 自定义短链接 xxx / URL 后缀 xxx”时才用 `--slug` 覆盖。

## 2. 发布前安全确认

发布前安全提示由入口 `SKILL.md` 统一描述。未展示入口安全提示并获得用户明确回复“同意”或 `agree` 前，不得执行本文件中的发布命令。

## 3. 判断创建还是更新

检查对话上下文。如果当前会话中已经为同一个文件生成过 ShareOne 链接，提取之前的 `share_id`（16 位字符串）并执行 PUT 更新。

- 有 `share_id`：执行更新。
- 没有 `share_id`：执行首次创建。

## 4. 文本页面发布规则

为了最大兼容性，推荐使用本 skill 的 Node.js 脚本发起 HTTP 请求。

`upload_page.js` 只用于 `.html`、`.md`、`.txt` 或已经包装成 HTML 的文本内容。

不要通过 pages JSON 接口上传任何二进制文件，例如 `.ppt`、`.pptx`、`.doc`、`.docx`、`.pdf`、`.zip`、`.png`。如果看到 `400 Bad Request` 且提示检测到二进制内容，立即改用 `publish-binary-file.md` 中的 `/api/v1/files` 流程重新上传。

接口：`https://shareone.app/api/v1/pages`

格式：`application/json`

## 5. 首次创建 (POST)

执行：

```bash
node scripts/upload_page.js "<YOUR_FILE_PATH>" --filename "YOUR_FILE_NAME" [--password "OPTIONAL_PASSWORD"] [--watermark "OPTIONAL_WATERMARK"] [--slug "OPTIONAL_SLUG"] [--allow-comments true]
```

规则：

- Sudowork 环境不要传 `--api-key`。
- 普通 AI Agent 环境可传 `--api-key`，也可以依赖 `SHAREONE_API_KEY` 或本地凭证。
- 只有当用户明确要求“开启评论”、“允许讨论”、“协同模式”等时，才加 `--allow-comments true`。
- 默认不开启评论。
- 服务端根据文件名自动生成 slug，无需手动设置。只有当用户明确要求自定义短链接时，才加 `--slug` 覆盖。

## 6. 更新已有链接 (PUT)

如果用户只要求修改已有链接的水印、访问密码、自定义短链接或评论开关，不要执行本节，不要下载原文件；改读 `update-share-settings.md`，使用 `update_share_settings.js` 只更新元数据。

执行：

```bash
node scripts/upload_page.js "<YOUR_FILE_PATH>" --filename "YOUR_FILE_NAME" --share-id <YOUR_SHARE_ID> [--password "OPTIONAL_PASSWORD"] [--watermark "OPTIONAL_WATERMARK"] [--slug "OPTIONAL_SLUG"] [--allow-comments true/false]
```

规则：

- Sudowork 环境不要传 `--api-key`。
- 如果用户要求关闭评论协同或开启评论协同，可以在 PUT 更新时传入 `--allow-comments false` 或 `--allow-comments true`。
- 如果用户要求修改或清除密码/水印，可以传入 `--password` 或 `--watermark`。
- 如果用户要求修改自定义短链接，可以传入 `--slug`。
- 空字符串 `""` 表示清除对应设置。

## 7. 使用 Mermaid.js 绘制图表

当 HTML 页面需要包含图表、流程图、时序图、思维导图等可视化内容时，优先使用 Mermaid.js 而非 CSS/字符串拼接的伪图表。Mermaid 渲染的图表响应式更好、更生动。

### 引入方式

在 HTML 的 `<style>` 中添加防闪烁 CSS，在 `<body>` 末尾通过 ESM 模块加载：

```css
/* 防止 Mermaid 加载前显示原始语法文本 */
pre.mermaid { background: none; border: none; text-align: center; padding: 20px 0; visibility: hidden; }
pre.mermaid[data-processed] { visibility: visible; }
```

```html
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true, theme: 'default', look: 'handDrawn' });
</script>
```

### 语法

在 HTML 中用 `<pre class="mermaid">` 包裹 Mermaid 语法：

```html
<pre class="mermaid">
flowchart LR
    A[开始] --> B{条件判断}
    B -->|是| C[执行]
    B -->|否| D[跳过]
</pre>
```

### 支持的图表类型

- `flowchart` — 流程图
- `sequenceDiagram` — 时序图
- `classDiagram` — 类图
- `stateDiagram-v2` — 状态图
- `erDiagram` — ER 关系图
- `gantt` — 甘特图
- `pie` — 饼图
- `mindmap` — 思维导图
- `timeline` — 时间线

### 使用原则

- 页面中有图表需求时，默认使用 Mermaid 替代 CSS 手工绘制的伪图表。
- 一个页面可以包含多个 `<pre class="mermaid">` 块。
- Mermaid 语法中不要包含 HTML 标签，保持纯文本描述。
- 如果图表极其复杂且 Mermaid 表达力不够，可以退回到 SVG 或 Canvas 方案。

## 8. 下一步

执行完成后读取 `result-and-errors.md`，按返回 JSON 展示结果或错误。
