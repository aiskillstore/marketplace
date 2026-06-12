# Windows 用户指南 - render_deliverables.py

如果在 Windows 上运行 `render_deliverables.py` 时遇到报错，请参考本指南。

## 常见错误及解决方案

### 1. `ModuleNotFoundError: No module named 'skills'`

**原因**：脚本无法找到输入文件，或者运行方式不对。

**解决方案**：

#### 方法A：使用绝对路径（推荐）

无论在哪个目录都能运行：

```bash
python C:\path\to\scripts\render_deliverables.py all --input C:\path\to\payload.json
```

#### 方法B：从脚本所在目录运行

```bash
cd C:\path\to\skills\zach-product-research\scripts
python render_deliverables.py all --input ..\..\payload.json
```

#### 方法C：使用 --root 参数指定输出位置

```bash
python render_deliverables.py all --input payload.json --root C:\output\directory
```

### 2. 中文路径乱码

**原因**：Windows 的编码问题。

**解决方案**：

- 使用 Python 3.7+ 版本（已内置更好的 UTF-8 支持）
- 确保你的 payload.json 文件编码为 **UTF-8**（而不是 GB2312 或 ANSI）
- 在 PowerShell 中运行时，添加编码设置：
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  python render_deliverables.py all --input payload.json
  ```

### 3. `FileNotFoundError: [Errno 2] No such file or directory`

**原因**：输入文件路径错误。

**解决方案**：

检查以下几点：
- 文件名是否正确（大小写敏感）
- 路径中是否包含空格（用引号括起来）：
  ```bash
  python render_deliverables.py all --input "C:\My Documents\payload.json"
  ```
- 文件是否真的存在

## 快速测试

```bash
# 1. 进入脚本目录
cd C:\Users\你的用户名\...\.claude\skills\zach-product-research\scripts

# 2. 查看帮助信息
python render_deliverables.py --help

# 3. 运行验证
python render_deliverables.py validate --input ../../payload.json

# 4. 生成报告
python render_deliverables.py generate --input ../../payload.json
```

## 依赖检查

确保安装了必要的库：

```bash
pip install openpyxl
```

## 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `command` | generate / validate / all | all |
| `--input` | 输入的 JSON 数据包路径 | C:\payload.json |
| `--root` | 输出根目录（默认当前目录） | C:\output |

## 调试模式

如果出现未预期的错误，脚本会自动打印完整的错误堆栈，帮助诊断问题。

