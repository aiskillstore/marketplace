# 错误码与排错

yescan CLI 输出 JSON 响应，以下是常见错误码及对应排查步骤。

---

## 错误码一览

| 错误码 | 含义 | 排查步骤 |
|---|---|---|
| A0100 | 凭证无效 | 1. 执行 `yescan config get SCAN_WEBSERVICE_KEY` 确认已配置<br>2. 确认 key 无前后空格或引号问题<br>3. 访问 scan.quark.cn/business 确认 key 未过期 |
| A0211 | 配额不足 | 访问 scan.quark.cn/business 开发者后台充值 |
| INVALID_SCENE | 场景名无效 | 执行 `yescan --list-scenes` 查看所有可用场景名 |
| INVALID_INPUT | 输入参数冲突 | `--url` 和 `--path` 只能提供一个 |
| FILE_ERROR | 文件验证失败 | 确认文件存在、大小 ≤5MB、扩展名在支持列表中 |
| URL_VALIDATION_ERROR | URL 格式无效 | 确认 URL 以 http:// 或 https:// 开头 |
| HTTP_ERROR | 网络请求失败 | 检查网络连接，确认能访问 scan-business.quark.cn |

## 常见问题

### Q: yescan 命令不存在

1. 确认已安装：`pip3 install yescan --upgrade`
2. 若已安装仍找不到，说明 pip3 scripts 目录不在 PATH 中，执行 `python3 -m site --user-base` 查看安装路径，将其下的 `bin/`（macOS/Linux）或 `Scripts/`（Windows）加入 PATH
3. 验证：`yescan --version`

### Q: 提示凭证无效

1. 执行 `yescan config get SCAN_WEBSERVICE_KEY` 查看当前配置
2. 如果为空，执行 `yescan config set SCAN_WEBSERVICE_KEY <your_key>` 配置
3. 访问 https://scan.quark.cn/business 确认 key 有效

### Q: 执行后无任何输出

确认 yescan 版本 ≥ 1.0.5：`yescan --version`。

### Q: 识别结果为空或不准确

- 确认图片清晰度足够
- 确认选择了正确的 scene（如表格用 `table-ocr`，手写用 `handwritten-ocr`）
- 图片分辨率过低时，可先使用 `image-hd-enhance` 增强再识别

### Q: CLI 不支持 --base64 参数

yescan CLI **不支持 `--base64` 输入**。如果图片是 base64 格式，请先写入临时文件再用 `--path` 传入。

### Q: Pipeline 执行中某步失败

Pipeline 采用"失败即停"策略。排查失败步骤的错误码，修复后可从失败步骤重新执行。
