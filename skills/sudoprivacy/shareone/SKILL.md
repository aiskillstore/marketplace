---
name: shareone
version: 1.0.2
description: 发布本地生成的 HTML 网页、PDF 或 PPTX 到 ShareOne 平台，生成公网分享短链接（Capability URL）。当用户要求“发布”、“分享”、“生成链接”或“上线”某个生成的页面/文档时使用此技能。
---

# AI Agent 技能：发布到 ShareOne (shareone)

这个 Skill 允许 AI Agent（如Openclaw等）将当前生成的历史会话以及HTML/PDF/PPT等文件，自动发布到 ShareOne 线上托管服务，并为用户生成一个持久化的公网分享链接。

## 使用说明与触发条件

**如何触发 (Triggering):**
当用户表达出以下意图时，应主动调用此技能：

- "帮我把 `index.html` 发布到 ShareOne"
- "把我刚才生成的网页发布，给我个链接"
- "生成一个可分享的链接给我的团队看"
- "Upload this presentation to ShareOne and protect it with password 'secret'"
- "发布这个 PDF 到 ShareOne，并加上密码 1234"
- "把这个网页发布到 ShareOne，加上水印 '内部绝密'"
- "用 shareone 分享上一轮对话"
- "把我刚才写的代码/大段文字分享出去"
- "Share your last response as a note"

**前置条件 (Prerequisites):**
用户需要拥有 ShareOne 的 API 凭证 (API Key)。请确保已在环境变量中设置 `SHAREONE_API_KEY`。

---

## 核心执行指令 / Execution Instructions

当你被要求发布文件到 ShareOne 时，请**严格按照以下步骤执行**：

### 1. 识别目标与环境预检 (Identify & Pre-flight)

找出用户明确指定要发布的文件，或者提取对话内容：

- **如果用户要求分享对话/大段文本/代码**：请首先从你的对话历史中提取上一轮生成的完整文本或代码块。将其保存到当前目录下的一个临时文件中，例如 `share_note.md` 或 `share_note.html`。
  - **建议**：如果是 Markdown 格式内容，建议在保存为 `.html` 前，使用简单的 HTML 模板包裹它，或者在 ShareOne 后端支持 Markdown 渲染的情况下直接发送 Markdown。如果无法确定，优先生成美观的 `.html` 文件。
- **如果用户指定了文件**：使用用户指定的文件。如果用户没有指定，请根据上下文寻找你最近一次生成或编辑的文件（如 `.html`, `.pdf`, `.pptx`）。

- **校验文件是否存在**：如果你通过上述步骤生成或锁定了文件，但文件仍不存在，停止并告知用户。
- **获取或创建 API Key**：执行本技能目录下的 `check_api_key.js` 脚本，它会依次检查环境变量、本地配置文件。如果都没有找到，脚本会输出 `KEY_NOT_FOUND`。

```bash
node scripts/check_api_key.js
```

- **如果脚本输出 `KEY_FOUND:<api_key>`**：将该 API Key 用于后续的发布请求，直接进入第 2 步。
- **如果脚本输出 `KEY_NOT_FOUND`**：你**必须暂停发布流程**，并向用户询问是否已有 API Key：

  > 💡 **提示**：我没有找到您的 ShareOne API Key。
  > 请问您是否已经拥有 API Key？
  >
  > - 如果有，请直接回复您的 API Key（例如 `sk-xxx`），我将为您保存并继续发布。
  > - 如果没有，请回复“没有”或“创建”，我将自动为您创建一个临时 API Key。

- **根据用户的回复进行处理**：
  - **如果用户回复了 API Key (例如 `sk-xxx`)**：
    执行本技能目录下的 `save_api_key.js` 脚本将用户提供的 Key 保存到本地，然后使用该 Key 继续发布（进入第 2 步）：
    ```bash
    node scripts/save_api_key.js <用户提供的KEY>
    ```
  - **如果用户回复“没有”或“创建”**：
    执行本技能目录下的 `create_guest_key.js` 脚本调用接口创建临时 API Key 并保存到本地：

    ```bash
    node scripts/create_guest_key.js
    ```

    - **如果输出 `GUEST_KEY_CREATED:<api_key>`**：将该 API Key 用于后续的发布请求，并在回复用户时加入以下提示：
      > 💡 **提示**：已为您自动分配了临时 API Key：`<api_key>`。
      > 为了方便您后续管理分享的链接，请前往 [ShareOne 官网](https://shareone.app/?key=<api_key>) 绑定您的永久账号。
    - **如果输出 `ERROR:RATE_LIMIT_EXCEEDED`**：请暂停发布，并提示用户：
      > ❌ **获取临时凭证失败**
      > 您今天自动创建临时 API Key 的次数已达上限（每天最多5次）。请前往 [ShareOne 官网](https://shareone.app) 手动注册并获取 API Key。

### 2. 免责声明机制 (Smart Consent) - 必须执行 (MANDATORY)

检查当前目录下是否存在 `.shareone_agreed` 文件。

- **如果存在**：静默跳过此步骤，直接进入第 3 步。
- **如果不存在**：你**必须**向用户展示安全提示，并等待用户明确回复“同意”或“agree”后才能继续：
  > ⚠️ **发布前安全提示**
  > 在将页面发布到公网前，请您确认该页面内容符合相关法律法规要求。禁止发布反动、涉政、暴力、色情、侵权或恶意代码。上传的内容将免费托管保留 90 天。
  > 如果您的内容符合要求，请回复 **“同意”**，我将为您发布。
- **用户同意后**：立即执行 `touch .shareone_agreed`，记录状态，然后再继续。

### 3. 判断发布类型：创建 (POST) 还是 更新 (PUT)

检查对话上下文。如果你在这个会话中，已经为**同一个文件**生成过 ShareOne 链接，你应该提取之前的 `share_id`（16位字符串）。

- 如果有 `share_id`，接下来执行**更新 (PUT)**。
- 如果没有，执行**首次创建 (POST)**。

### 4. 构造请求并执行发布 (Execute Request)

根据文件类型和操作类型构造请求。提取用户可能要求的密码 (`password`) 和水印 (`watermark`)。为了最大兼容性，推荐使用 Node.js 脚本发起 HTTP 请求。

#### 场景 A：文本、代码或纯 HTML 文件 (`.html`, `.md`, `.txt`)

> **⚠️ 警告 (CRITICAL):**
> 绝对不要通过这个接口上传任何二进制文件（如 `.ppt`, `.pptx`, `.pdf`, `.zip`, `.png` 等），否则服务器会返回 `400 Bad Request` 错误（提示检测到二进制内容）。如果你看到此类错误，请立即更换为 **场景 B** 的 `/api/v1/files` 接口重新上传。

接口：`https://shareone.app/api/v1/pages`
格式：`application/json`

对于提取的对话、大段文字或独立的代码块，请将其包装为一段美观的 HTML（含基础样式）以保证展示效果：

**如果是首次创建 (POST):**

执行本技能目录下的 `upload_page.js` 脚本：

```bash
node scripts/upload_page.js <YOUR_FILE_PATH> --api-key $SHAREONE_API_KEY --filename "YOUR_FILE_NAME" [--password "OPTIONAL_PASSWORD"] [--watermark "OPTIONAL_WATERMARK"]
```

**如果是更新已有链接 (PUT):**

执行本技能目录下的 `upload_page.js` 脚本，并传入 `--share-id` 参数：

```bash
node scripts/upload_page.js <YOUR_FILE_PATH> --api-key $SHAREONE_API_KEY --filename "YOUR_FILE_NAME" --share-id <YOUR_SHARE_ID>
```

#### 场景 B：二进制文件 (PDF, PPTX 等)

由于二进制文件可能较大，ShareOne 采用直传 S3 的方式。请直接调用本技能目录下的 `shareone_upload.js` 脚本进行上传：

**如果是首次创建 (POST):**

```bash
node scripts/shareone_upload.js <FILE_PATH> --api-key $SHAREONE_API_KEY [--password "OPTIONAL_PASSWORD"] [--watermark "OPTIONAL_WATERMARK"]
```

**如果是更新已有链接的密码或水印 (PUT):**

对于已经上传的二进制文件，如果用户要求修改密码或水印，请调用 `update_file_meta.js` 脚本（假设存在，或通过 curl 直接调用 `/api/v1/files/{share_id}` 接口）：

```bash
curl -X PUT "https://shareone.app/api/v1/files/<YOUR_SHARE_ID>" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: $SHAREONE_API_KEY" \
     -d '{"password": "NEW_PASSWORD", "watermark": "NEW_WATERMARK"}'
```

_(注意：传空字符串 `""` 表示取消密码或水印)_

### 5. 异常处理与结果反馈 (Feedback)

解析接口返回的 JSON。

- **发布成功 (HTTP 200/201)**:
  - 提取返回的 `share_id` (通常是返回的 JSON 中的 `id` 或 `share_id`，或者直接从返回的 `share_url` 中提取最后的路径部分)。
  - **组装分享链接 (CRITICAL DOMAIN CONSTRAINT)**:
    - ⚠️ **严格域名约束**：你**必须**且**只能**使用 `https://shareone.app` 作为基础域名！
    - **隔离上下文干扰**：无论用户之前的对话上下文中提到了什么其他域名（例如 `xxx.example.com`），或者你自己的记忆中存储了什么域名，在组装并返回分享链接给用户时，**绝对禁止**被这些无关的上下文污染。在你的内部处理逻辑中，组装 URL 时必须**硬编码 (Hardcode)** 使用 `https://shareone.app`！
    - 生成规则：
      - 如果是 PDF：`https://shareone.app/pdf/<share_id>`
      - 如果是 PPT/PPTX：`https://shareone.app/ppt/<share_id>`
      - HTML 默认：`https://shareone.app/s/<share_id>`
  - 如果设置了密码，务必在回复中加粗显示密码：
    > 🎉 **发布成功！**
    > 🔗 链接: <生成的URL>
    > 🔑 提取码: **<密码>**
  - **功能提示 (Feature Discovery)**: 在**本次会话首次**向用户展示生成的短链接时，请主动（但简短且友好地）提示他们支持未使用的功能，以便用户了解更多高级特性。**后续发布不再提示。**
    - 如果用户**未使用密码和水印**，提示：
      > “💡 提示：您也可以让我为分享链接‘加上访问密码’或‘添加自定义水印’，以更好地保护您的内容。”
    - 如果用户**使用了密码但未使用水印**，提示：
      > “💡 提示：除了密码，您也可以让我为内容‘添加自定义水印’。”
    - 如果用户**使用了水印但未使用密码**，提示：
      > “💡 提示：除了水印，您也可以让我为分享链接‘加上访问密码’。”
    - 如果用户**同时使用了密码和水印**，则**不进行任何提示**。
- **内容违规拦截 (HTTP 400)**: 提取 JSON 中的 `detail` 字段展示给用户，如："❌ 发布失败，内容未通过安全审核。原因：<detail>"
- **API Key 无效 (HTTP 401)**: 提示用户 "API Key 无效或权限不足"。
- **找不到页面 (HTTP 404)**: 若 PUT 更新遇 404，说明原页面已被后台删除，请询问用户是否作为新页面重新 POST。
