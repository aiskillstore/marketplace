# Ark AgentPlan Seedream Skill

豆包 Seedream AI 图片生成 Skill - **火山方舟 Agent Plan 专属版本**

## ✨ 核心特性

- 🎨 **Agent Plan 专属架构**：使用 Agent Plan 统一 baseurl，与生图、语言模型使用相同地址
- 🔑 **三层智能 API Key 检测**：自动识别 OpenClaw / Hermes / Claude Code 配置，无需单独配置
- ⚡ **安全默认**：对话中发送的 API Key 默认仅本次临时使用，显式确认后才保存到平台配置
- 🖼️ **6 种生成场景全覆盖**：文生图、连贯图生成、图生图、多参考融合等
- 🌊 **流式输出**：生成一张返回一张，大幅降低首图可见时间
- ✨ **提示词自动优化**：自动增强画质描述、风格预设、构图指导
- 📂 **保存到启动目录**：默认保存到 Claude 启动目录（当前工作目录），可用环境变量自定义
- 💾 **自动下载归档**：按日期自动分类保存，附带完整 metadata

## 📦 目录结构

```
byted-ark-seedream-skill/
├── SKILL.md              # 主定义：触发器、参数、流程
├── README.md             # 本文档
├── INSTALL.md            # 安装指南
└── scripts/
    └── generate.js       # API 调用 + 下载保存
```

## ⚙️ 配置

### 🎯 设计原则

**开箱即用 + 灵活可控**：
- ✅ 预置合理默认值（正式环境、推荐模型），普通用户只需配置 API Key
- ✅ 支持通过环境变量自定义所有配置
- ✅ 命名空间隔离，避免与 Seedance 等其他 Skill 冲突

### 📋 配置说明（一般不需要改）

| 配置项 | 说明 | 默认值 |
|-------|------|--------|
| **🔑 API Key** | **自动从平台配置读取**，无需手动配置。<br>找不到时可以通过环境变量兜底。 | 自动检测 |
| `ARK_SEEDREAM_MODEL` | Seedream 模型 ID | `doubao-seedream-5.0-lite` |
| `ARK_SEEDREAM_API_BASE_URL` | Seedream 专用 API 地址 | `https://ark.cn-beijing.volces.com/api/plan/v3` |
| `ARK_SEEDREAM_SAVE_PATH` | 图片保存路径 | Claude 启动目录下的 `Seedream-Images`（当前工作目录） |

> 💡 **环境变量仅用于兜底，一般不需要设置！**<br>
> Skill 会自动从 OpenClaw / Hermes / Claude Code 的配置中读取 API Key。

### 🔑 API Key 配置（三层优先级）

Skill 会按以下优先级自动检测 API Key，真正做到「零配置开箱即用」：

#### 🥇 第一层（最高优先级）：用户对话中显式传入
当用户直接在对话中发送 Agent Plan 专属 API Key 时，Agent 层通过参数传给 Skill：
```bash
# ✅ 默认仅本次临时使用，不保存到全局配置
node scripts/generate.js --prompt "一只可爱的小猫" --api-key ark-xxx

# ✅ 仅当用户明确要求「保存/以后使用这个 Key」时，才加 --save-api-key
node scripts/generate.js --prompt "一只可爱的小猫" --api-key ark-xxx --save-api-key
```
> ✅ Skill 会校验 Key 是否 Agent Plan 专属。
> 
> ⚠️ **默认仅临时使用**：由于 Agent Plan API Key 是当前平台的全局 Key，会影响语言模型、生图、生视频、Embedding 等所有能力，因此默认不自动保存到配置。只有用户明确要求保存时，才传入 `--save-api-key`。

#### 🥈 第二层（平台专属检测）：根据当前运行平台读取配置
Skill 自动检测当前运行平台，并从对应位置读取：
- **Claude Code**：`~/.claude/settings.json` 中的 `env.ANTHROPIC_AUTH_TOKEN`（或会话环境变量）
- **OpenClaw**：`~/.openclaw/openclaw.json` 中的 `models.providers.*.apiKey`
- **Hermes**：`~/.hermes/config.yaml` 中的 `model.api_key`

#### 🥉 第三层（通用兜底）：6 个通用环境变量
如果无法识别平台，则自动查找以下通用命名的环境变量：
1. `ANTHROPIC_AUTH_TOKEN`
2. `API_KEY`
3. `API_Key`
4. `API_Keys`
5. `api_key`
6. `apiKey`

> 💡 **安全原则**：只有当用户明确说「保存这个 Key / 以后都用这个 / 替换全局 Key」时，Agent 层才应追加 `--save-api-key` 参数，写入当前平台的 Agent Plan 标准配置（如 OpenClaw 的 `volcengine-plan`），保存后所有相关功能都可以直接复用，无需重复输入。
> 
> ⚠️ 不会默认读取通用的 `ARK_API_KEY` 环境变量，避免误用火山其他业务的 API Key。

#### ❌ 都没找到：明确提示用户
如果以上都没有配置，Skill 会明确提示：
> 请在对话中发送 Agent Plan 专属 API Key，或在当前工具中配置。

---

## 🚀 使用方式

### 对话中直接使用（推荐）

```
用户：给我画一张赛博朋克风格的城市夜景
Agent：[触发 Skill] → 生成图片 → 保存到启动目录 → 返回结果
```

### 支持的触发词

```
生图、画图、生成图片、seedream、给我画、
画一张、画一个、图生图、参考图、生成一组图、
四季变迁、多风格、豆包画图、方舟生图
```

## 🎯 全部 6 种生成场景完整支持

---

### 场景 1：🖼️ 文生图 → 单张图片

**适用场景：** 单张创意图片生成

**用户输入示例：**
```
一只可爱的英短蓝猫，趴在洒满阳光的木质窗台上，背景是模糊的城市街景，暖色调，电影质感，8K分辨率
```

**参数映射：**
- `mode`: `text-to-image`（默认）
- `sequential`: `false`（默认）
- `size`: `2K` / `3K`（默认 `2K`）
- `watermark`: `true` / `false`（默认 `true`）
- `enable_web_search`: `true` / `false`（默认 `false`）开启联网搜索，适用于新闻、赛事、最新热点等场景
- `response_format`: `png` / `jpeg`（默认 `jpeg`）图片输出格式，jpeg 体积小加载快，png 无损画质更好

---

### 场景 2：🎨 文生图 → 一组连贯图（1-15张）

**适用场景：** 系列插画、四格漫画、四季变迁、多风格对比等

**用户输入示例：**
```
生成一组共4张治愈系插画，主题为同一间咖啡馆的四季变迁：
春天樱花飘落，夏天阳光斑驳，秋天金黄落叶，冬天温暖雪景
统一吉卜力画风，2K分辨率
```

**参数映射：**
- `mode`: `text-to-image`
- `sequential`: `true`
- `count`: `4`
- `stream`: `true`（自动开启）

---

### 场景 3：🖼️🖼️ 单参考图 → 单张图片

**适用场景：** 风格迁移、参考构图、保持角色一致性等

**用户输入示例：**
```
[用户上传一张宫崎骏风格的风景图]

参考这张图的配色和光影风格，画一个站在麦田里的小女孩
```

**参数映射：**
- `mode`: `image-to-image`
- `reference_images`: `["https://参考图地址.png"]`
- `sequential`: `false`

---

### 场景 4：🖼️🎨 单参考图 → 一组连贯图

**适用场景：** 基于同一参考风格，生成多角度/多配色/多表情的系列图

**用户输入示例：**
```
[用户上传一张 IP 角色图]

参考这个角色的人设，生成4张不同动作的游戏立绘：
站立、奔跑、施法、胜利姿势，保持服装和发色一致
```

**参数映射：**
- `mode`: `image-to-image`
- `reference_images`: `["https://参考图地址.png"]`
- `sequential`: `true`
- `count`: `4`
- `stream`: `true`（自动开启）

---

### 场景 5：🖼️🖼️🖼️ 多参考图 → 单张图片

**适用场景：** 融合多种风格、组合参考图中的不同元素

**用户输入示例：**
```
[用户上传2张图：图1是人物肖像，图2是赛博朋克风格背景]

参考图1的人物，换上图2的背景和配色风格，保持人物五官特征不变
```

**参数映射：**
- `mode`: `image-to-image`
- `reference_images`: `["https://图1地址.png", "https://图2地址.png"]`
- `sequential`: `false`

---

### 场景 6：🖼️🖼️🎨 多参考图 → 一组连贯图

**适用场景：** 融合多种风格参考，生成完整系列作品

**用户输入示例：**
```
[用户上传3张图：角色设定、场景设定、参考配色]

综合这3张图的设定，生成4张同一角色在不同场景下的插画：
城市街头、雨中漫步、傍晚天台、星空下的背影，保持画风和配色统一
```

**参数映射：**
- `mode`: `image-to-image`
- `reference_images`: `["https://角色设定.png", "https://场景设定.png", "https://配色参考.png"]`
- `sequential`: `true`
- `count`: `4`
- `stream`: `true`（自动开启）

---

## ✨ 提示词自动优化

自动为用户的简单提示词增加专业描述，提升出图质量：

| 用户输入 | 自动优化后 |
|---------|-----------|
| "一只小猫" | 一只可爱的英国短毛小猫，趴在阳光洒进的窗台上，**电影质感，8K分辨率，细节丰富，专业摄影，治愈系风格，柔和自然光线** |
| "赛博朋克城市" | 赛博朋克风格的城市夜景，**赛博朋克2077风格，霓虹灯光，高科技低生活，雨天，未来感，电影级光影，杜比视界** |

### 内置 10 大风格预设

自动检测并套用：电影风、二次元、插画风、写实风、国潮风、赛博朋克、水彩风、3D渲染、暗黑风、治愈系

### 关闭优化

用户说"不要优化"、"用原提示词"则自动关闭优化功能。

## 🌊 流式输出

Skill 已原生支持流式输出。当 `sequential=true`（生成多张）时，自动启用流式输出模式，生成一张返回一张。

## 📂 保存路径

**默认保存到 Claude 启动目录**（脚本运行时的当前工作目录）：
1. ✅ **环境变量优先**：`ARK_SEEDREAM_SAVE_PATH` / `ARK_SAVE_PATH`（显式指定固定路径时）
2. 📂 **默认**：Claude 启动目录下的 `Seedream-Images/`（`process.cwd()`）

> ⚠️ 默认目录取自 `process.cwd()`，请用脚本【绝对路径】在启动目录调用，**不要 `cd` 进 skill 目录**，否则会存到 skill 目录里。

按日期归档：
```
{保存路径}/YYYY-MM-DD/
├── seedream_1713777600_1.png
├── seedream_1713777600_2.png
└── seedream_1713777600_metadata.json
```

> 💡 可通过环境变量 `ARK_SEEDREAM_SAVE_PATH` 自定义保存路径

## 🔧 手动验证

```bash
# 方式 1：直接传参数（默认临时使用，不保存配置）
node ~/.agents/skills/byted-ark-seedream-skill/scripts/generate.js \
  --prompt "一只可爱的小猫，阳光洒进窗台，温暖色调" \
  --mode text-to-image \
  --api-key "ark-xxx"

# 方式 2：设置环境变量
export API_KEY="ark-xxx"

# 测试文生图（如果用方式 2，不需要传 --api-key）
# 注意：图片会保存到你当前所在目录的 Seedream-Images/，请勿 cd 进 skill 目录
node ~/.agents/skills/byted-ark-seedream-skill/scripts/generate.js \
  --prompt "一只可爱的小猫，阳光洒进窗台，温暖色调" \
  --mode text-to-image \
  --size 2K \
  --sequential false \
  --count 1

# 测试连贯图生成
node ~/.agents/skills/byted-ark-seedream-skill/scripts/generate.js \
  --prompt "一个女孩在海边的四季变迁" \
  --mode text-to-image \
  --size 2K \
  --sequential true \
  --count 4
```

## 📋 返回格式

```json
{
  "success": true,
  "images": [
    {
      "url": "https://ark-project.tos-cn-beijing.volces.com/...",
      "local_path": "./Seedream-Images/2026-04-22/seedream_1234567890_1.png",
      "prompt": "一只可爱的小猫..."
    }
  ],
  "error": null,
  "metadata": {
    "generation_time": 8.5,
    "size": "2K",
    "mode": "text-to-image",
    "image_count": 1
  }
}
```

## 🐛 故障排查

### 问题：未检测到有效的 API Key
**解决：**
1. ✅ 推荐：直接在对话中发送你的 API Key（Agent Plan 专属），默认仅本次临时使用；如需保存，请明确说「保存这个 API Key」
2. 检查平台配置文件是否已正确配置 API Key
3. 确认平台配置中的 Key Agent Plan 专属

### 问题：图片无法下载
**解决：** 检查网络连接，确认保存路径有写入权限

### 问题：Skill 未触发
**解决：** 检查触发词是否匹配，查看 Skill 是否已正确加载

## 📄 相关文档

- [INSTALL.md](./INSTALL.md) - 详细安装指南
