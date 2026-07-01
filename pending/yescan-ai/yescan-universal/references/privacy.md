# 隐私、数据流向与密钥安全

本文档说明 `yescan` 技能在执行过程中涉及的全部数据流向、第三方服务交互范围，以及 API 密钥的配置、存储与轮换流程。

---

## 1. 数据流向（What leaves your machine）

| 数据 | 是否外发 | 接收方 | 用途 |
|---|---|---|---|
| 用户提供的图片（URL / 本地文件） | 外发 | `https://scan-business.quark.cn`（夸克扫描王服务） | OCR / 增强 / 转换 / AIGC |
| `SCAN_WEBSERVICE_KEY` | 随请求头发送 | 同上 | API 鉴权 |
| 处理结果（JSON / 文件） | 不外发 | 仅返回给调用方 | CLI 输出到 stdout 或本地文件 |
| 用户提示词、对话上下文 | 不外发 | — | 仅在本地 Agent 处理 |

> **服务端处理说明**：夸克扫描王服务将获取并处理该图片内容，服务端不会永久保存。

## 2. 本地文件行为

- **OCR 场景**：不写入输出文件（结果以 JSON 打印到 stdout），`pic-translate` 场景例外（保存译图到临时目录）
- **图像增强场景**：输出增强后图片到系统临时目录下的 `imgs/` 子目录（如 `/tmp/imgs/`）或 `--output` 指定目录
- **文档转换场景**：输出文档文件到系统临时目录下的 `documents/` 子目录（如 `/tmp/documents/`）或 `--output` 指定目录
- **AIGC 场景**：输出生成图片到系统临时目录下的 `imgs/` 子目录（如 `/tmp/imgs/`）或 `--output` 指定目录
- 唯一的文件读取操作是用户指定的本地图片路径（`--path` 参数）

## 3. API 密钥配置

### 3.1 推荐方式：通过 CLI 配置（永久生效）

```bash
yescan config set SCAN_WEBSERVICE_KEY <your_api_key_here>
```

配置保存在 `~/.yescan/config.json`。

### 3.2 备选方式：环境变量（仅当前会话）

```bash
export SCAN_WEBSERVICE_KEY=<your_api_key_here>
```

> 优先级：CLI config（`~/.yescan/config.json`）> 环境变量

## 4. 获取与轮换密钥

1. 访问 `https://scan.quark.cn/business`（**仅此一个有效官方入口**）
2. 进入开发者后台 → 登录/注册账号 → 创建应用 → 查看 API Key
3. 如怀疑密钥泄露：在同一后台立即 *轮换* 或 *撤销* 旧密钥，并更新配置

## 5. 安全实践清单

- [x] 不要在公网截图/录屏中暴露 key 或配置文件内容
- [x] 仅对用户主动指定的图片进行处理，不要遍历整个目录
- [x] 处理涉密 / PII 图片前，用户应自行评估数据外发的合规性

## 6. 适用范围

本技能图片来源 **仅限用户在当次请求中明确指定** 的图片文件或 URL。技能不会主动扫描磁盘、访问剪贴板或读取额外文件。
