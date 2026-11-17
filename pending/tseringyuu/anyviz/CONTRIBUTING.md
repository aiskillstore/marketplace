# Contributing to anyviz

Thank you for your interest in contributing to anyviz! This guide will help you understand how to contribute code, templates, adapters, and documentation to the project.

**中文贡献指南 — 参见本文档下方「贡献指南（中文简述）」章节。**

---

## Table of Contents

- [How to Contribute](#how-to-contribute)
- [Adding New Chart Templates](#adding-new-chart-templates)
- [Adding New Adapters](#adding-new-adapters)
- [Reporting Issues](#reporting-issues)
- [Pull Request Process](#pull-request-process)
- [Code & Documentation Style](#code--documentation-style)
- [Local Validation](#local-validation)
- [贡献指南（中文简述）](#贡献指南中文简述)

---

## How to Contribute

### Reporting Issues

Found a bug, documentation error, or want to suggest a new chart type?

1. **Check existing issues** first to avoid duplicates
2. **Use the appropriate issue template**:
   - Bug reports → `.github/ISSUE_TEMPLATE/bug_report.md`
   - Feature requests → `.github/ISSUE_TEMPLATE/feature_request.md`
   - New chart suggestions → `.github/ISSUE_TEMPLATE/new_chart_template.md`
3. **Provide clear context**: what you tried, what happened, what you expected

### Adding New Chart Templates

Chart templates are the core of anyviz. Every new template must follow the specification in `templates/TEMPLATE-SPEC.md`.

#### Template Structure (Required Five Sections)

Every template in `templates/` must include these sections in order:

```markdown
# Chart Name（English Name）

## 适用场景
- 3-5 bullet points describing when to use this chart
- Include recommended data scale/category count

## 数据格式
```json
{ minimal working example showing input data structure }
```

## 美学参数
```json
{ chart-specific parameters, must align with default.json values }
```

## 设计要点
1. **Point Name**: specific rule with numeric values (hex colors, px, opacity)
2. (4-6 total points with executable details)

## 变体
### Variant Name
Brief explanation of when to use and how it differs from main chart
```

#### Checklist for New Templates

- [ ] Follow `TEMPLATE-SPEC.md` structure exactly (all five sections required)
- [ ] All colors reference `aesthetics/default.json` (use exact hex values)
- [ ] All dimensions use values from `default.json` (line width, point radius, opacity, corner radius, etc.)
- [ ] Data format uses consistent field names with similar chart types
- [ ] Design points are specific and measurable (not vague like "colors harmonize")
- [ ] Accessibility guidance included (redundant coding for color-only distinctions)
- [ ] Template saved in correct directory: `templates/charts/`, `templates/maps/`, `templates/graphs/`, or `templates/3d/`

#### Example: Adding a new chart to `templates/charts/`

```markdown
# 桑基图（Sankey Diagram）

## 适用场景
- 可视化多层级的流动与转变（如用户转化漏斗、能源流向）
- 展示源端点到目标端点的流量分布
- 最佳数据量：节点 5-50 个，边 10-200 条

## 数据格式
```json
{
  "nodes": [
    {"id": "A", "name": "Source A"},
    {"id": "B", "name": "Target B"}
  ],
  "links": [
    {"source": "A", "target": "B", "value": 100}
  ]
}
```

## 美学参数
```json
{
  "node_padding": 60,
  "link_opacity": 0.45,
  "node_color": "#4269d0",
  "link_colors_from_source": true
}
```

## 设计要点
1. **链接透明度**：opacity 0.45，便于查看重叠流
2. **节点对齐**：垂直排列，node_padding 60px
3. **流向标注**：数值标签 9px（H6 级别）
4. **色相连贯**：链接继承源节点颜色...

## 变体
### Circular Sankey
闭环流向，用于循环经济或系统反馈...
```

### Adding New Adapters

Adapters convert abstract chart specifications into code for specific libraries (D3.js, ECharts, Matplotlib, etc.).

#### Adapter Requirements

1. **Location**: `adapters/{platform}/{library}.md`
   - Platforms: `web`, `python`, `r`
   - Libraries: `d3`, `echarts`, `mapbox`, `three` (web); `matplotlib`, `plotly` (python); `ggplot2` (r)

2. **Structure**:
   - Brief description of library strengths/use cases
   - Key configuration mappings (how anyviz specs translate to library API)
   - Example code for a common template (e.g., bar chart, line chart)
   - Notes on accessibility and customization

3. **Code must be self-contained**:
   - Explicit aesthetic parameters (no reliance on library defaults)
   - Include data transformation steps
   - Runnable HTML or script examples where applicable

#### Example Adapter Addition

If adding support for a new visualization library:

1. Create `adapters/web/newlib.md` (or appropriate platform)
2. Document how core aesthetic parameters map to the library's API
3. Provide complete example code
4. Test with multiple chart types from templates
5. Verify colors exactly match `default.json`

---

## Pull Request Process

### Before Submitting

1. **Fork and create a feature branch** (not direct push to main)
   ```bash
   git checkout -b add-template-timeline-chart
   ```

2. **Run local validation** (see [Local Validation](#local-validation))

3. **Test your changes**:
   - If adding a template: verify it renders correctly with an adapter
   - If modifying aesthetics: check consistency across multiple charts
   - If adding an adapter: test with at least 3 different chart types

### PR Description

Use the provided `.github/PULL_REQUEST_TEMPLATE.md`. Include:

- **Summary**: What does this PR add or fix? (1-2 sentences)
- **Changes**: List of files modified/added
- **Checklist**: Confirm compliance with style and validation rules
- **Testing**: How did you verify this works?

### PR Checklist

The template includes mandatory checks:

- [ ] Follows `TEMPLATE-SPEC.md` structure (if adding templates)
- [ ] All colors reference `default.json` (exact hex values)
- [ ] Passes `theme_validator.py` validation
- [ ] Passes package export validation when public entry points or guides change
- [ ] Updated the workflow entry point or README index (if applicable)
- [ ] Accessibility considerations addressed
- [ ] JSON files are valid (if modified)
- [ ] Documentation is clear and complete

### Review & Merge

- Maintainers will review for correctness and consistency
- May request changes for alignment with project standards
- Once approved, PR will be merged to main and included in next release

---

## Code & Documentation Style

### Markdown Documentation

- Use consistent heading levels (start with `#` for document title)
- Chinese as primary language for content, English for code/API
- Technical terms: provide both forms on first use (e.g., "categorical palette 分类色板")
- Code blocks use triple backticks with language tag (```json, ```html, ```python, etc.)

### Aesthetic Parameters

All numeric values must be explicit:

- **Colors**: Use `default.json` hex values (e.g., `#4269d0`, not `primary-blue`)
- **Dimensions**: Write values explicitly (e.g., `border-radius: 5px`, not `rounded`)
- **Opacity**: Use decimal 0.0-1.0 (e.g., `opacity: 0.75`)
- **Typography**: Reference layer names (e.g., "H3 / 11px / 400 weight")

### JSON Structure

- 2-space indentation
- Alphabetize keys within objects (for consistency)
- Include descriptive comments in top-level metadata
- Validate with `python3 -m json.tool` before committing

### Comments & Docstrings

- Python code: follow PEP 257 (module, class, function docstrings)
- JavaScript/HTML: use clear comments for non-obvious logic
- Explain the "why" rather than the "what" in comments

---

## Local Validation

### Python: Theme Validator

Verify aesthetic consistency in chart configurations:

```bash
# Run the full local validation chain
npm run validate

# Validate single chart config
python3 scripts/theme_validator.py --config examples/test_config_valid.json

# Validate multi-chart output
python3 scripts/theme_validator.py --config examples/multi_chart.json --multi-chart

# Expected output (pass): ✅ All checks passed!
# Expected output (fail): ❌ Found N issues...
```

The validator checks:
- Typography parameters match `default.json` defaults
- Color palettes use `default.json` values
- Spacing aligns with specification
- Canvas-level title alignment, legend clearance, export visual centering, and source-note policy
- Multi-chart consistency (titles, legends, labels, margins)

### Package Export Validation

When adding or renaming public guides, themes, package entry points, or npm export-map entries,
run:

```bash
npm run validate:exports
```

This check confirms that `anyviz.guides.*` resolves to files present in the package and stays
consistent with the documented guide index.

### Template Structure Validation

Check that all templates follow the required five-section format:

```bash
# Bash one-liner to verify templates have required sections
for f in templates/**/*.md; do
  if [ "$f" != "templates/TEMPLATE-SPEC.md" ]; then
    if grep -q "^## 适用场景" "$f" && \
       grep -q "^## 数据格式" "$f" && \
       grep -q "^## 美学参数" "$f" && \
       grep -q "^## 设计要点" "$f" && \
       grep -q "^## 变体" "$f"; then
      echo "✓ $f"
    else
      echo "✗ $f (missing required section)"
    fi
  fi
done
```

### JSON Validation

Verify aesthetics and example JSON files are valid:

```bash
# Check aesthetics and example configs
for f in aesthetics/*.json aesthetics/themes/*.json examples/*.json; do
  python3 -m json.tool "$f" > /dev/null && echo "✓ $f" || echo "✗ $f"
done
```

### GitHub Actions CI

On every push and PR, the CI pipeline (`/.github/workflows/validate.yml`) automatically:
1. Runs `npm run validate` against theme and package-export checks
2. Verifies the invalid fixture is rejected by `theme_validator.py`
3. Checks all templates for required sections
4. Validates all aesthetics and example JSON files

If any check fails, the PR cannot be merged. Review the CI logs to fix issues.

---

## 贡献指南（中文简述）

欢迎贡献新的图表模板、适配器、修复 bug 或改进文档。

### 核心贡献流程

1. **Fork 本仓库** → **创建特性分支** → **进行改动** → **本地校验** → **提交 PR**

### 新增图表模板

所有模板必须遵循 `templates/TEMPLATE-SPEC.md` 的**五段式结构**：

| 章节 | 内容 |
|------|------|
| 适用场景 | 3-5 条要点，说明何时使用、数据规模建议 |
| 数据格式 | JSON 示例，展示最小可用数据结构 |
| 美学参数 | JSON 配置，所有值必须来自 `default.json` |
| 设计要点 | 4-6 条具体、可量化的设计规则（含数值） |
| 变体 | 主图表的参数调整或扩展方案 |

**重点要求**：
- 所有颜色必须使用 `aesthetics/default.json` 中的十色色板（如 `#4269d0`）
- 所有尺寸参数取自 `default.json`（线宽、圆角、透明度等）
- 字号层级统一用 H1-H6 标记
- 无障碍考虑：若图表只靠颜色区分，必须提示如何加纹理/形状/标签冗余编码

### 新增适配器

适配器将抽象的图表规范转换为具体库的代码（D3.js、ECharts、Matplotlib 等）。

1. 位置：`adapters/{平台}/{库}.md`
2. 包含库的配置映射、代码示例、无障碍和定制说明

### 报告问题

使用 GitHub Issue 模板，选择对应类别（Bug / Feature / New Chart）。提供清晰的上下文、复现步骤、预期行为。

### 提交 PR 前的校验

```bash
# 1. 运行完整本地校验链
npm run validate

# 2. 检查模板五段式结构
for f in templates/**/*.md; do
  if ! grep -q "^## 适用场景" "$f"; then
    echo "缺少必需章节: $f"
  fi
done

# 3. 验证 JSON 合法性
python3 -m json.tool aesthetics/default.json > /dev/null
```

### PR 清单

- [ ] 新模板遵循五段式规范
- [ ] 所有颜色取自 `default.json`
- [ ] 通过 `npm run validate` 校验
- [ ] 无障碍指南已考虑
- [ ] JSON 文件合法

---

## Questions or Need Help?

- **Documentation issues**: Open an issue with the `documentation` label
- **Design questions**: Discuss in issue before submitting PR
- **Implementation questions**: Open a discussion or issue with the relevant template, adapter, or guide context

Thank you for contributing to make anyviz better!
