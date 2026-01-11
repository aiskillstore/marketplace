# 工具装备系统快速开始指南

## 10分钟上手工具装备系统

### 前置条件

**系统要求**:
- Python 3.8+
- Bash shell
- 基本CLI工具（curl, grep, find等）

**推荐安装**:
```bash
# macOS
brew install fzf eza zoxide fd bat ripgrep jq

# Ubuntu/Debian
sudo apt-get install fzf ripgrep jq bat
```

### 第一步：环境检查

```bash
# 进入工具装备目录
cd .ai-runtime/toolkit

# 检查Python环境
python3 --version

# 检查discover-toolkit工具
python3 discover-toolkit.py --help
```

### 第二步：查看可用工具

```bash
# 查看所有工具概览
python3 discover-toolkit.py list

# 查看内部工具
python3 discover-toolkit.py list --internal

# 查看外部工具
python3 discover-toolkit.py list --external
```

### 第三步：使用工具

#### 基础用法

```bash
# 查看工具详情
python3 discover-toolkit.py show SERVICE-CHECK-001

# 运行服务健康检查
python3 discover-toolkit.py run service-check http://localhost:3000

# 运行依赖分析
python3 discover-toolkit.py run dependency-analyzer . -o deps.json
```

#### 实际场景示例

**场景1: 项目代码分析**
```bash
# 分析当前项目的依赖关系
python3 discover-toolkit.py run dependency-analyzer . -o project-deps.json

# 查看结果
cat project-deps.json | jq '.summary'
```

**场景2: 日志文件分析**
```bash
# 分析应用日志，查找错误
python3 discover-toolkit.py run log-analyzer /var/log/app.log --level ERROR --since "1 hour ago"

# 生成错误统计报告
python3 discover-toolkit.py run log-analyzer /var/log/app.log --stats --output error-stats.json
```

**场景3: API测试**
```bash
# 测试REST API端点
python3 discover-toolkit.py run api-test http://api.example.com/users --method GET

# 测试POST请求
python3 discover-toolkit.py run api-test http://api.example.com/users \
  --method POST \
  --data '{"name": "test user"}' \
  --headers "Content-Type: application/json"
```

### 第四步：外部工具集成

#### 安装检查

```bash
# 检查外部工具安装状态
python3 discover-toolkit.py check-external

# 安装缺失的工具（macOS示例）
brew install fzf eza bat ripgrep
```

#### 实际使用

```bash
# 使用ripgrep搜索代码（比grep快10倍以上）
rg "TODO|FIXME" src/

# 使用fzf进行交互式选择
find src/ -name "*.py" | fzf

# 使用bat查看带语法高亮的代码
bat src/main.py

# 使用eza美化文件列表
eza -la src/

# 使用jq处理JSON数据
cat package.json | jq '.dependencies'
```

### 第五步：创建自定义工具

#### 快速创建Bash工具

```bash
# 使用模板创建新工具
cp templates/tool-template.sh bash/custom/my-tool.sh
cp templates/meta-template.yml bash/custom/my-tool.meta.yml

# 编辑工具脚本
nano bash/custom/my-tool.sh

# 编辑元数据
nano bash/custom/my-tool.meta.yml
```

#### 元数据示例

```yaml
name: MY-TOOL-001
description: 我的自定义工具
language: bash
category: UTILITY
complexity: level-2
version: 1.0.0

parameters:
  - name: input
    type: string
    required: true
    description: 输入文件路径

  - name: output
    type: string
    required: false
    description: 输出文件路径（可选）

examples:
  - description: 基本用法
    command: python3 discover-toolkit.py run my-tool input.txt

  - description: 指定输出
    command: python3 discover-toolkit.py run my-tool input.txt -o output.txt
```

#### 测试新工具

```bash
# 验证工具注册
python3 discover-toolkit.py show MY-TOOL-001

# 测试运行
python3 discover-toolkit.py run my-tool test-input.txt

# 查看帮助
python3 discover-toolkit.py help MY-TOOL-001
```

### 第六步：高级用法

#### 批量操作

```bash
# 批量检查多个服务
echo "http://api1.example.com
http://api2.example.com
http://db.example.com:5432" | \
while read url; do
  echo "Checking $url..."
  python3 discover-toolkit.py run service-check "$url"
done
```

#### 脚本集成

```bash
#!/bin/bash
# CI/CD 集成脚本示例

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOLKIT_DIR="$PROJECT_ROOT/.ai-runtime/toolkit"

cd "$TOOLKIT_DIR"

# 代码质量检查
echo "=== 代码质量检查 ==="
python3 discover-toolkit.py run code-stats src/ --format json > code-stats.json

# 依赖安全检查
echo "=== 依赖安全检查 ==="
python3 discover-toolkit.py run dependency-analyzer . --security-check > security-report.json

# 生成综合报告
echo "=== 生成报告 ==="
python3 discover-toolkit.py run report-generator \
  --code-stats code-stats.json \
  --security security-report.json \
  --output ci-report.html
```

#### 监控和告警

```bash
# 定期健康检查
while true; do
  echo "$(date): Health check..."
  python3 discover-toolkit.py run service-check http://localhost:3000 > /dev/null
  if [ $? -ne 0 ]; then
    echo "Service down! Sending alert..."
    # 发送告警逻辑
  fi
  sleep 300  # 5分钟检查一次
done
```

## 故障排除

### 常见问题

**工具未找到**
```bash
# 检查工具是否存在
python3 discover-toolkit.py list | grep <tool-name>

# 检查元数据文件
find . -name "*.meta.yml" | xargs grep <tool-name>
```

**运行时错误**
```bash
# 查看详细错误信息
python3 discover-toolkit.py run <tool-name> --verbose

# 检查依赖
python3 discover-toolkit.py show <tool-name>
```

**外部工具不可用**
```bash
# 检查安装
which <external-tool>

# 重新检测
python3 discover-toolkit.py check-external
```

### 获取帮助

```bash
# 通用帮助
python3 discover-toolkit.py --help

# 工具特定帮助
python3 discover-toolkit.py help <tool-name>

# 搜索相关工具
python3 discover-toolkit.py search <keyword>
```

## 下一步

完成这个快速开始指南后，你可以：

1. **深入学习**: 查看 [references/internal-tools.md](internal-tools.md) 了解所有内部工具
2. **扩展技能**: 阅读 [references/external-tools.md](external-tools.md) 掌握更多CLI工具
3. **开发工具**: 参考 [references/creating-tools.md](creating-tools.md) 创建自己的工具
4. **优化工作流**: 将工具集成到你的开发和部署流程中

---

*这个指南应该在10分钟内完成。如果遇到问题，请查看详细文档或寻求帮助。*
