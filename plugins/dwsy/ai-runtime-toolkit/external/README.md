# 外部工具装备目录 (External Toolkit)

## 目录结构

```
external/
├── search/              # 搜索工具
│   └── fzf.meta.yml     # 模糊查找器
├── navigation/          # 导航工具
│   └── zoxide.meta.yml  # 智能目录跳转
├── file-search/         # 文件搜索工具
│   └── fd.meta.yml      # find替代品
├── code-search/         # 代码搜索工具
│   └── ripgrep.meta.yml # 极速代码搜索
├── file-listing/        # 文件列表工具
│   └── eza.meta.yml     # 现代化ls
├── file-viewer/         # 文件查看工具
│   └── bat.meta.yml     # 语法高亮cat
├── data-processing/     # 数据处理工具
│   └── jq.meta.yml      # JSON处理器
├── api-testing/         # API测试工具
│   └── xh.meta.yml      # HTTP客户端
├── git-tools/           # Git工具
│   └── delta.meta.yml   # diff美化
└── shell-enhancement/   # Shell增强工具
    └── starship.meta.yml # Shell提示符
```

## 设计理念

### 简化元数据

外部工具（如fzf, ripgrep, bat等）是广为人知的CLI工具，它们：

1. **已预训练** - 大语言模型通常已了解这些常用工具，无需详细文档
2. **动态帮助** - 可使用 `command --help` 或 `man command` 获取最新信息
3. **避免重复** - 不重复官方文档，保持元数据简洁

### 元数据结构

每个外部工具仅需一个 `.meta.yml` 文件，包含：

```yaml
tool_id: EXT-FZF-001
tool_name: "fzf (Fuzzy Finder)"

基本信息:
  类型: external
  命令: fzf
  类别: search

功能描述:
  简介: "命令行模糊查找器，用于交互式选择"
  详细: "常用工具，支持交互式模糊搜索。使用 'fzf --help' 获取详细信息。"

使用场景:
  - 文件名模糊查找
  - 历史命令搜索

快速开始:
  安装: "brew install fzf"
  帮助命令: "fzf --help"
  常用示例:
    - "find . -type f | fzf"

检测状态:
  已安装: true
```

## 与内部工具的区别

| 特性 | 内部工具 (Internal) | 外部工具 (External) |
|------|-------------------|-------------------|
| 位置 | `bash/`, `python/`, `node/` | `external/` |
| 实现 | AI Runtime创建的工具脚本 | 系统级CLI工具 |
| 元数据 | 详细（包含完整描述、参数、示例） | 简化（模型已知工具） |
| 检测 | 检查工具文件exists | 使用 `shutil.which()` |
| 示例 | `dependency-analyzer.py` | `fzf`, `ripgrep`, `bat` |

## 检测机制

`ExternalToolDetector` 扫描 `external/` 目录：

1. **递归扫描** - 查找所有 `.meta.yml` 文件
2. **类型过滤** - 只处理 `基本信息.类型 == "external"`
3. **安装检测** - 使用 `shutil.which()` 检查命令是否可用
4. **运行时检测** - 每次运行都重新检测，获取最新状态

## 使用方式

```bash
cd .ai-runtime/toolkit

# 列出所有外部工具
python3 discover-toolkit.py list --external

# 显示外部工具详情
python3 discover-toolkit.py show fzf

# 搜索包含'search'的外部工具
python3 discover-toolkit.py search search --external

# 查看所有工具（内部 + 外部）
python3 discover-toolkit.py list
```

## 新增外部工具

添加新外部工具只需：

1. 在 `external/<category>/` 创建 `tool-name.meta.yml`
2. 填写基本信息（ID、名称、命令、类别）
3. 提供使用场景和快速开始
4. （可选）添加检测状态占位符

无需修改代码，自动检测加载。

## 已安装的外部工具

当前检测到的外部CLI工具（9个）：

- ✅ **fzf** - 模糊查找
- ✅ **eza** - 现代化ls
- ✅ **zoxide** - 智能cd
- ✅ **fd** - 文件搜索
- ✅ **ripgrep (rg)** - 代码搜索
- ✅ **bat** - 语法高亮查看器
- ✅ **jq** - JSON处理器
- ✅ **xh** - HTTP客户端
- ✅ **delta** - Git diff美化
- ❌ **starship** - Shell提示符（未安装）

## 优势

✅ **统一结构** - 内部/外部工具都使用 `.meta.yml` 文件
✅ **简化维护** - 外部工具不重复文档
✅ **动态检测** - 实时检测安装状态
✅ **分类清晰** - 按功能分类，便于查找
✅ **易于扩展** - 添加新工具只需创建元文件
