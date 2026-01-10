# Documentation Restructuring Plan

## Problem
Two documentation files are too large:
- `registry.md`: 1,089 lines
- `EXTERNAL-TOOLS.md`: 547 lines

## Solution
Split into smaller, focused files using `@path/to/file.md` import feature discovered from deepwiki.

## New Structure

### EXTERNAL-TOOLS.md → Split (547 lines)

**Main index**: `EXTERNAL-TOOLS.md` (with @imports)

```
docs/external-tools/
├── 00-index.md                 # Overview & TOC
├── essential/                  # 基础必备（7个工具）
│   ├── fzf.md                 # 模糊查找
│   ├── eza.md                 # 文件列表
│   ├── zoxide.md              # 目录导航
│   ├── fd.md                  # 文件搜索
│   ├── bat.md                 # 文件查看
│   ├── ripgrep.md             # 代码搜索
│   └── starship.md            # Shell提示符
├── advanced/                   # 进阶推荐（3个工具）
│   ├── jq.md                  # JSON处理
│   ├── zellij.md              # 终端复用
│   └── procs.md               # 进程查看
└── expert/                     # 专家级（2个工具）
    ├── just.md                # 任务运行器
    └── hyperfine.md           # 性能测试
```

### registry.md → Split (1,089 lines)

**Main index**: `registry.md` (with @imports)

```
docs/registry/
├── 00-overview.md              # Philosophy & concepts
├── 01-quickstart.md            # Quick start guide
├── 02-tool-categories.md       # Category explanations
├── 03-external-integration.md  # External tools philosophy
├── 04-creating-tools.md        # How to create tools
├── TOC.md                      # Table of contents
└── internal-tools/             # Individual tool docs
    ├── service-checker.md
    ├── dependency-analyzer.md
    ├── code-stats.md
    └── api-tester.md
```

## Implementation Strategy

1. **Phase 1**: Create new `docs/` directory structure
2. **Phase 2**: Split EXTERNAL-TOOLS.md (easier, 547 lines)
3. **Phase 3**: Split registry.md (larger, 1,089 lines)
4. **Phase 4**: Update main index files with @imports
5. **Phase 5**: Test and verify

## Key Benefits

✅ **Better maintainability** - Each tool/file is self-contained
✅ **Faster loading** - AI assistant can load only needed sections
✅ **Easier updates** - Modify individual tools without affecting others
✅ **Clear organization** - Hierarchical structure by category
✅ **Reusable** - Individual tool docs can be referenced elsewhere

## Import Usage Example

New `EXTERNAL-TOOLS.md`:
```markdown
# External Tools

@docs/external-tools/00-index.md

## Essential Tools

@docs/external-tools/essential/fzf.md
@docs/external-tools/essential/eza.md
@docs/external-tools/essential/zoxide.md
# ...etc
```
