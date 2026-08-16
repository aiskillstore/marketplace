# Seedream Agent 开发指南

本文档面向 Agent 开发者，包含图片预处理、脚本调用方式、流式输出说明。

---

## 🖼️ 图片预处理（Agent 层负责）

Skill 接受以下格式的参考图片文件，Agent 层需要负责转换：

### 支持的格式
```javascript
// 1. Base64 Data URI（推荐）
"data:image/jpeg;base64,/9j/4AAQSkZJRg..."
"data:image/png;base64,iVBORw0KGgo..."

// 2. HTTP/HTTPS URL（需要公网可访问）
"https://example.com/image.jpg"
```

**图片限制：**
- 单张大小：≤ 10MB
- 格式：JPEG / PNG / WebP
- 数量：最多 14 张
- 建议分辨率：≥ 1024x1024

---

## 📝 调用脚本方式

> ⚠️ **保存位置**：图片会保存到**脚本运行时的当前工作目录**（即 Claude 启动目录）下的 `Seedream-Images/YYYY-MM-DD/`。
> 因此实际调用时请使用脚本的【绝对路径】并保持在 Claude 启动目录运行，**不要 `cd` 进入 skill 安装目录**（否则图片会存到 skill 目录里）。
> 下方示例为简洁写成相对路径 `scripts/generate.js`，真实调用请替换为绝对路径，例如：
> `node ~/.agents/skills/byted-ark-seedream-skill/scripts/generate.js --prompt "..."`。
> 如需固定到其它位置，设置环境变量 `ARK_SEEDREAM_SAVE_PATH`。

### 方式一：单张图片生成
```bash
# 基本用法
node scripts/generate.js --prompt "一只可爱的小猫"

# 完整参数
node scripts/generate.js \
  --prompt "一只可爱的小猫" \
  --size "2K" \
  --mode "text-to-image" \
  --watermark true \
  --optimize true \
  --response_format "jpeg"
```

**输出示例（JSON）：**
```json
{
  "success": true,
  "images": [
    {
      "url": "https://ark.example.com/images/xxx.jpg",
      "local_path": "/Users/xxx/my-project/Seedream-Images/2026-04-27/seedream_123456_1.jpg",
      "width": 2048,
      "height": 2048
    }
  ],
  "metadata": {
    "generation_time": 12.5,
    "size": "2K"
    "mode": "text-to-image",
    "image_count": 1
  }
}
```

---

### 方式二：连贯组图生成（流式输出）
```bash
node scripts/generate.js \
  --prompt "春夏秋冬四季变迁，同一地点" \
  --sequential true \
  --count 4 \
  --stream true
```

**流式输出特点：**
- 生成一张返回一张，无需等待全部完成
- 首图可见时间降低 75%
- 自动保持风格、色调、构图一致

---

## 🌊 流式进度反馈

当 `sequential=true` 时，Skill 会通过 stderr 输出实时进度：

```
🎨 正在生成第 1/4 张图...
✅ 第 1 张已生成并保存
🎨 正在生成第 2/4 张图...
✅ 第 2 张已生成并保存
...
```

Agent 层可以捕获 stderr 输出，向用户展示实时进度。

---

## 🎯 Agent 层结果展示规范（重要）

Skill 采用 stderr / stdout 分离设计：

| 输出流 | 内容 | 用途 | Agent 层处理方式 |
|--------|------|------|------------------|
| **stderr** | 生成进度、日志、提示信息 | 人类可读的实时反馈 | 逐行打印给用户看 |
| **stdout** | 最终 JSON 结果（含图片链接） | Agent 解析使用 | 不要直接打印，要解析后结构化展示 |

### ✅ 正确的处理流程

```javascript
// 1. 分别捕获 stderr 和 stdout
const { stderr, stdout } = await execAsync('node scripts/generate.js --prompt "xxx"');

// 2. stderr 直接逐行展示给用户（实时进度反馈）
showToUser(stderr);

// 3. stdout 解析 JSON，然后格式化展示最终结果
const result = JSON.parse(stdout);

// 4. 最终结果：必须展示图片文件给用户！
if (result.success && result.images) {
  for (const img of result.images) {
    if (img.download_success) {
      // ✅ 重点：把本地文件发送给用户（不要只发路径字符串）
      sendFileToUser(img.local_path);
      // 可以同时展示在线链接
      sendTextToUser(`🔗 在线链接: ${img.url}`);
    } else {
      sendTextToUser(`❌ 第 ${img.index} 张下载失败: ${img.download_error}\n🔗 原始链接: ${img.url}`);
    }
  }
}
```

### ❌ 常见错误

- 只展示 stderr，不解析 stdout JSON → 用户看不到图片链接/文件
- 把 stdout JSON 直接打印给用户 → 用户看到乱码
- 只展示在线链接，不读取本地文件发送 → 用户体验差

---

## 🔌 支持的原生 API 接口

### 文生图 / 图生图 / 连贯组图（统一接口）
```http
POST https://ark.cn-beijing.volces.com/api/plan/v3/images/generations
Content-Type: application/json
Authorization: Bearer ark-xxx

{
  "prompt": "一只可爱的小猫",
  "size": "2K"
}
```

**说明：**
- 所有生图能力（文生图、图生图、连贯组图）统一使用上述接口
- **注意：连贯图数量不通过 `num_images` / `count` / `max_images` 等字段透传。** 连贯图数量由 prompt 语义触发，例如 `"生成4张一组的连贯插画..."`。脚本中的 `--count` 仅用于 Agent 构造 prompt、本地校验、进度展示和 metadata 记录

---

## ⚠️ 错误处理建议

Agent 层应该处理以下常见错误：

| 错误类型 | 建议处理 |
|----------|---------|
| API Key 未配置 | 提示用户直接发送 ark-xxx 开头的 Key，默认仅本次临时使用；如需保存到全局配置，请明确要求用户确认 |
| 网络错误 | 自动重试 2~3 次，失败再提示用户 |
| 图片下载失败 | 返回生成的在线 URL，提示用户手动保存 |
| 参数不合法 | 自动修正到合法范围，并提示用户 |

