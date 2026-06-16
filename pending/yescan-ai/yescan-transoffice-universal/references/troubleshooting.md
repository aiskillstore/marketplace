# 错误码与常见问题排查

`scripts/scan.py` 返回的 JSON `code` 字段沿用夸克扫描王业务错误码体系。下表列出最常见的几种以及处理建议。Agent 在拿到非成功响应时应 *原样返回*，由用户决定是否重试。

---

## 1. 错误码速查

| code | 含义 | 处理建议 |
|---|---|---|
| `00000` | 成功 | 直接展示 `data.path` |
| `A0211` | 额度不足 | 前往开发者后台充值 |

> 其他错误码以服务端实际返回为准。常见情况：鉴权失败（检查 `SCAN_WEBSERVICE_KEY`）、图片格式/大小不符（见 SKILL.md 要求）。完整错误码列表请查阅 `https://scan.quark.cn/business` 官方文档。

## 2. 常见现象与排查

### 2.1 报鉴权失败

1. 确认 `~/.yescan_env` 中 `SCAN_WEBSERVICE_KEY` 不带引号、不带空格
2. 确认密钥未在后台被禁用或轮换过
3. macOS / Linux：检查文件权限 `ls -l ~/.yescan_env` 应为 `-rw-------`
4. Windows：确保编码为 UTF-8（PowerShell 默认可能写成 UTF-16，需要用 `-Encoding utf8` 显式指定）

### 2.2 响应有 `data.FileBase64` 但没有 `data.path`

说明 `file_saver.py` 落盘失败。可能原因：

- 临时目录无写权限
- 磁盘空间不足
- BASE64 损坏（magic byte 校验未通过）

排查方法：手动跑一次 `python3 scripts/scan.py ...` 看 stderr 输出。

### 2.3 输出 docx 打开是乱码 / 空白

- 可能是图片质量过低导致服务端识别为空表

### 2.4 请求一直挂起

- 检查网络是否能访问 `scan-business.quark.cn`

## 3. 不要做的事

- ❌ 不要自动重试：可能导致重复扣额度
- ❌ 不要把错误响应翻译/美化后交给用户：会丢失原始 code 信息
