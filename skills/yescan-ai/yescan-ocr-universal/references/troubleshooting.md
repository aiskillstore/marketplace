# 错误码与排错

执行脚本输出 JSON 响应，以下是常见错误码及对应排查步骤。

---

## 错误码一览

| 错误码 | 含义 | 排查步骤 |
|---|---|---|
| A0100 | 凭证无效 | 1. 确认 `~/.yescan_env` 存在且包含 `SCAN_WEBSERVICE_KEY=<key>`<br>2. 确认 key 无前后空格或引号问题<br>3. 访问 scan.quark.cn/business 确认 key 未过期 |
| A0211 | 配额不足 | 访问 scan.quark.cn/business 开发者后台充值（注意购买 Skill 专用套餐） |
| INVALID_SCENE | 场景名无效 | 检查 `--scene` 值是否在 SKILL.md 场景列表中 |
| INVALID_INPUT | 输入参数冲突 | 三种输入方式（url/path/base64）只能提供一种 |
| FILE_ERROR | 文件验证失败 | 确认文件存在、大小 ≤5MB、扩展名在支持列表中 |
| URL_VALIDATION_ERROR | URL 格式无效 | 确认 URL 以 http:// 或 https:// 开头 |
| BASE64_DECODE_ERROR | BASE64 解码失败 | 确认字符串是合法的 base64 编码 |
| HTTP_ERROR | 网络请求失败 | 检查网络连接，确认能访问 scan-business.quark.cn |

## 常见问题

### Q: 执行后无任何输出

确认使用 `python3 scripts/scan.py` 执行（非 `python`），且 Python 版本 ≥ 3.9。

### Q: 提示 "No module named 'common'"

确认工作目录为技能根目录（`SKILL.md` 所在目录），或使用完整相对路径 `python3 scripts/scan.py`。

### Q: 识别结果为空或不准确

- 确认图片清晰度足够
- 确认选择了正确的 scene（如表格用 `table-ocr`，手写用 `handwritten-ocr`）
- 图片分辨率过低时可先增强再识别
