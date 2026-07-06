# 隐私、数据流向与密钥安全

本文档说明 `yescan-ocr-universal` 在执行过程中涉及的全部数据流向、第三方服务交互范围，以及 API 密钥的配置、存储与轮换流程。SKILL.md 中只保留摘要，以下为完整版本。

---

## 1. 数据流向（What leaves your machine）

| 数据 | 是否外发 | 接收方 | 用途 |
|---|---|---|---|
| 用户提供的图片（URL / 本地文件 / BASE64） | 外发 | `https://scan-business.quark.cn`（夸克扫描王服务） | OCR 文字识别 |
| `SCAN_WEBSERVICE_KEY` | 随请求头发送 | 同上 | API 鉴权 |
| 识别结果（结构化 JSON 文本） | 不外发 | 仅返回给调用方 | 由脚本直接输出到 stdout |
| 用户提示词、对话上下文 | 不外发 | — | 仅在本地 Agent 处理 |

> **服务端处理说明**：夸克扫描王服务将获取并处理该图片内容，服务端不会永久保存。

## 2. 本地文件行为

- OCR 技能**不写入任何输出文件**，识别结果以 JSON 格式直接打印到 stdout。
- 唯一的文件读取操作是用户指定的本地图片路径（`--path` 参数）。
- **pic-translate 场景例外**：图片翻译场景会将译图保存到系统临时目录（`/tmp/imgs`），文件不会自动清理。

## 3. API 密钥配置

### 3.1 推荐方式：写入 `~/.yescan_env`（永久生效）

技能每次执行会读取 `~/.yescan_env`，无需重启会话。

**macOS / Linux**

```bash
echo 'SCAN_WEBSERVICE_KEY=<your_api_key_here>' > ~/.yescan_env
chmod 600 ~/.yescan_env
```

**Windows（PowerShell）**

```powershell
'SCAN_WEBSERVICE_KEY=<your_api_key_here>' | Out-File -FilePath $HOME\.yescan_env -Encoding utf8
```

### 3.2 备选方式：环境变量（仅当前会话）

```bash
export SCAN_WEBSERVICE_KEY=<your_api_key_here>
```

> 不推荐在命令行直接 `--key=xxx` 传递，密钥会被记录到 shell 历史。

## 4. 获取与轮换密钥

1. 访问 `https://scan.quark.cn/business`（**仅此一个有效官方入口**，若链接跳转到其他域名说明已失效，请手动输入域名）
2. 进入开发者后台 → 登录/注册账号 → 创建应用 → 查看 API Key
3. 如怀疑密钥泄露：在同一后台立即 *轮换* 或 *撤销* 旧密钥，并更新 `~/.yescan_env`

## 5. 安全实践清单

- [x] `~/.yescan_env` 设为 `0600` 权限，避免同机其他用户读取
- [x] 不要在公网截图/录屏中暴露 key 文件内容
- [x] 仅对用户主动指定的图片进行处理，不要遍历整个目录
- [x] 处理涉密 / PII 图片前，先评估第三方服务合规性

## 6. 适用范围

本技能图片来源 **仅限用户在当次请求中明确指定** 的图片文件、URL 或 BASE64 数据。技能不会主动扫描磁盘、访问剪贴板或读取额外文件。
