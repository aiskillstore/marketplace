# WorkBuddy 沙箱运行与授权

本技能包不下载程序，不执行 `npm install`，只使用 Node.js 18+ 内置模块。

## 分层检查

### 离线自检

```bash
node scripts/inkroom.mjs self-test
```

自检验证运行时、JSON/SSE 解析、PNG 容器与压缩行、URL 限制和原子文件写入。它不联网、不读取 Key、不生成图片、不扣点。脚本无需下载外部程序。

### 公开服务检查

```bash
node scripts/inkroom.mjs doctor
```

`doctor` 访问 InkRoom 公开设置端点，确认 Remote MCP 地址属于 `inkroom.ai`。它不调用生成工具。

## 用户授权

`models`、`capabilities`、`tools` 以及 `call` 中的 `list_models` / `help` / 公开 `prompts`（action 缺省/search/get，scope 缺省/recommended）可无 Key 查询公开信息，不执行上游模型或消耗积分。`help`、`self-test` 是离线检查，`doctor` 只检查公开服务。公开销售价不等于个人可调用权限、最终预览报价或上游官方原价。

私有数据、任务、预览和实际媒体操作需要用户自己的 InkRoom Key。用户从 `https://inkroom.ai/skill-server` 复制 Key 后，通过标准输入交给脚本：

```bash
node scripts/inkroom.mjs authorize
```

脚本从标准输入读取 Key，使用只读 `tools/list` 验证后保存到用户私有状态目录。不要把 Key 写进命令参数、技能文件、对话回复或共享输出。

默认状态目录为 `~/.inkroom-workbuddy`；可用 `INKROOM_STATE_DIR` 指定沙箱允许的私有目录。宿主如已安全注入 `INKROOM_MCP_TOKEN`，脚本优先使用该环境变量且不落盘。

## 错误处理

| 结果 | 处理 |
| --- | --- |
| `authorization_required` | 请用户提供自己的 Key 并执行授权，不回退到游客或共享 Key |
| `invalid_token` | Key 无效或被撤销；重新授权 |
| `forbidden` | 当前账号或 Key 没有对应权限；到 InkRoom 检查授权范围 |
| `confirmation_required` | 展示本次最高费用，等待用户明确确认后继续原请求 |
| 网络中断 | 保留请求和响应文件；恢复原任务，不自动重提生成 |
| 原图下载失败 | 优先用 `resume` 继续原回执；`recover` 只重新保存已记录响应中的图片 |
| 余额不足 | 充值后重新预览原失败项；不自动执行、不缩减张数、不重跑成功项 |
| `continuationPending` | 从 `.resume.json` 接续；到达轮数上限不代表任务失败 |
| `needsHostDecode` | 用宿主图片能力重新打开；不能仅凭文件头宣称完整解码 |

任何状态以脚本结构化 JSON 和服务端回执为准。命令退出成功不等于全部原图已经交付。

下载仅支持公开 HTTPS，不跟随重定向，不发送 MCP Token；DNS 解析到私有地址时拒绝。新普通原图的对象和链接 72 小时期限由新版服务端控制，客户端不改写 URL 或延长签名，旧结果按原到期时间处理。
