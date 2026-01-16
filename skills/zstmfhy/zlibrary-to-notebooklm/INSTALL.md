# 安装指南

## 系统要求

- Python 3.8 或更高版本
- macOS / Linux / Windows
- 网络连接

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/zlibrary-to-notebooklm.git
cd zlibrary-to-notebooklm
```

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 3. 安装 Playwright 浏览器

```bash
playwright install chromium
```

### 4. 确保 NotebookLM CLI 已安装

```bash
# 检查 notebooklm 命令是否可用
notebooklm --version

# 如果未安装，请先安装 NotebookLM CLI
npm install -g @google-notebooklm/cli
```

## 验证安装

```bash
# 测试登录脚本（不会实际登录）
python3 scripts/login.py --help

# 测试上传脚本（不会实际上传）
python3 scripts/upload.py --help
```

## 故障排除

### Playwright 安装失败

```bash
# 手动下载浏览器
playwright install --with-deps chromium
```

### Python 版本问题

```bash
# 使用 pyenv 安装 Python 3.8+
pyenv install 3.11.0
pyenv global 3.11.0
```

### 权限问题

```bash
# macOS/Linux: 添加执行权限
chmod +x scripts/*.py
```

## 下一步

安装完成后，请查看 [快速开始](README.md#快速开始)
