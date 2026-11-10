# 整包中文与东亚字体归一化

用户明确要求统一现有 PPTX 的中文/东亚字体时读取此文件。单个对象仍用
`set-run.font.eastAsian` 等局部操作；只改主题槽位用 `set-theme`。翻译、导出、
普通保真修复不自动授权整包字体替换，Refurbish 也不默认追加此操作。

## 发现与选择

从本次运行的 capability snapshot 检查 `text/font-family-normalization`，再读取：

```bash
xdoc schema --mode ops --ops set-font --minimal
xdoc schema --command pptx.set-font --minimal
```

按实时 schema 和 dry-run 路由，不按版本号；旧运行时未披露时继续使用已披露的
inspect → 局部字体 patch → Edit Contract 路径，不用原始 XML 全局替换冒充同等能力。

| 需求                                      | 模式                                    | 边界                                                                                    |
| ----------------------------------------- | --------------------------------------- | --------------------------------------------------------------------------------------- |
| 统一中文，保留日文/韩文及 Latin/CS 字体槽 | `target: "chinese"` / `--chinese`       | 更新 Hans/Hant 映射及选中的中文 run；保留通用 EA 默认值、Jpan/Hang 映射与明确 ja/ko run |
| 明确要求所有东亚字体一起统一              | `target: "east-asian"` / `--east-asian` | 更新支持范围内 DrawingML EA 槽位及 Hans/Hant/Jpan/Hang 映射，包含日文和韩文             |

两种 CLI 选项互斥。不要因中文模式跳过歧义 run 而自动扩大到 east-asian。
中文选择会解析 run、段落、列表、占位符、layout、master 与 presentation 的有效语言；
普通文本框不借用 master `otherStyle`，表格使用其自身继承路径，不能按顶层默认语言猜测。
未标记 Han 文本可能被推断为中文；Han 与假名/韩文混合且无法确定的文本保持原样。
图表 cache 的语言不等同于普通 run，混合语言图表的默认字体也可能被保留。

该操作遍历支持的原生 XML，包括文本、表格字体集合、图表默认字体及主题映射；
不承诺更改图片文字、OMML 公式、嵌入对象、未知扩展或 `extLst` 内的字体。
即使扩展负载使用已知 DrawingML 命名空间，也保持不透明。

## Patch、dry-run 与选择复核

一次字体任务使用一个独立的 top-level `set-font`；没有 `slide` 或 `shape` 选择器：

```json
{
  "schemaVersion": "pptx-patch/v1",
  "ops": [{ "op": "set-font", "target": "chinese", "typeface": "Noto Sans SC" }]
}
```

族名按 schema 限制为 1–256 个字符，patch 不带首尾空白或控制字符。不要写字体文件路径。
CLI 会 trim 族名；写 patch 前先归一化，保证契约和报告中的名称完全一致。

```bash
xdoc pptx inspect input.pptx --json > <run-dir>/inspect.json
xdoc pptx apply --input input.pptx --patch <run-dir>/patch.json \
  --output <run-dir>/candidate.pptx --dry-run --json > <run-dir>/dry-run.json
```

这次 read-only dry-run 用于整包字体选择发现，先于最终契约归一化。检查
`semanticIssues=[]` 和 `opResults[0].analysis`：

- `coverage="supported-xml-only"` 不是“所有可见文字已统一”。
- `visitedSlots`、`changedSlots` 统计 XML 槽位，不能当作幻灯片数或字符数。
- `selectionStatus="review-required"` 表示存在 `inferredSelections` 或
  `ambiguousSelections`。逐项查看 `findings[].part/path/status/reason`，复核推断及保留
  是否符合本次要求。`path` 是诊断位置，不是可执行 XPath、shape ID 或稳定选择器。
- `fontAvailability` 和 `visualFit` 始终为 `not-evaluated`；complete 也不证明字体已安装、
  已嵌入、字形齐全或排版安全。

复核通过后，用 `<skill-root>/scripts/lib/runtime/canonical-json.mjs` 导出的
`canonicalSha256V1(analysis)` 计算 analysis 摘要，写入下述
`expected.reviewedAnalysisSha256`。该字段在 review-required 时必需；重新 dry-run 若发现
变化，重新复核并更新契约。不要用布尔“忽略歧义”替代摘要，也不要只为通过门禁编造摘要。
若用户要求所有中文都必须统一而仍有歧义，需要检查这些原生 run 后使用局部操作解决，
并单独生成相应对象级 Edit Contract。

## 整包字体 Edit Contract

字体操作的 `resolvedSelectors=[]` 是正常结果；不要伪造逐对象匹配。使用专用文档目标，
`slideCount` 从当前 inspect 获取，包含隐藏页；下面的一页示例须按实际页数填写：

```json
{
  "schemaVersion": "pptx-nova-edit-contract/v1",
  "request": "Unify Chinese fonts while preserving Japanese, Korean and Latin families",
  "scope": "all-slides-style",
  "operationKind": "font-normalization",
  "targets": [
    {
      "id": "document-fonts",
      "kind": "document-fonts",
      "slideCount": 1,
      "opIndexes": [0],
      "expected": {
        "fontTarget": "chinese",
        "typeface": "Noto Sans SC",
        "changeCategories": ["style"]
      }
    }
  ],
  "allowedChanges": ["style"],
  "preserve": ["slide-count"],
  "requiredEvidence": [
    "dry-run",
    "semantic-diff",
    "png-preview",
    "vision-diff",
    "final-inspect",
    "structure-check"
  ]
}
```

有选择推断/歧义时，在 `expected` 加上复核后的 `reviewedAnalysisSha256`。
按 [Edit Contract](edit-contract.md) 归一化、apply、生成证据清单并运行 contract gate。
专用目标只允许上述单操作字体任务，不可用于混入文本改写、其他样式操作或绕过普通
对象选择器；活动 session rule 产生额外对象目标时，改用可证明该规则的对象级流程。

```bash
node <skill-root>/scripts/cli/edit/contract.mjs \
  --draft <run-dir>/edit-contract-draft.json --source input.pptx \
  --output <run-dir>/edit-contract.json --json
xdoc pptx apply --input input.pptx --patch <run-dir>/patch.json \
  --output <run-dir>/candidate.pptx --json > <run-dir>/apply.json
```

CLI `xdoc pptx set-font input.pptx --chinese 'Noto Sans SC' --output ... --json`
编译为同一 canonical op，也可用于单独诊断。正式编辑保留 patch 与默认
`candidate.pptx.xdoc.json` sidecar；输入只读，dry-run 不发布 PPTX 或 sidecar。
不要用默认输出为 null 的 dry-run 替代已绑定 candidate 路径的最终证据。

## 验证与交付

apply 报告也须成功，`semanticIssues=[]`，选择分析与已复核意图一致。保存 full semantic
diff、final inspect、结构检查、全部页面的 PNG 与 vision-diff，按现有 evidence-manifest
和 contract-gate 命令绑定当前 candidate。专用门禁要求全页证据；不因只是“换字体”跳过
隐藏页或未直接修改的页面，因为主题映射可能改变它们的继承外观。
全页 vision-diff 可用真实 `agentGate.scopeMode="full-deck"` 与 `slideCount` 证明范围，
或显式传 `--slides 1-N`；不要给报告手补 `scope`。轻量结构检查若提示未提供预期颜色，
应从源文件回读并核对需保留的实际 palette，不能凭空添加品牌色来消除警告。

检查 XML 中实际 EA/Hans/Hant/Jpan/Hang 槽位、Latin/CS、原始文本、字号/样式、frame
geometry/autofit、表格/图表数据、关系及扩展负载。再次对同一候选执行相同 op 的 dry-run，
预期 `changedSlots=0` 且无 changed parts；幂等不替代选择正确性或视觉复核。

安装目标字体后，用相同 runtime、DPI 和冻结 field date 重渲染源文件与候选。保存的框与
autofit 保持不变仍可能导致可见换行、溢出或缺字；既有 pending reflow 不会被该操作撤销。
检查正文、表格、图表、notes，以及中日文/韩文/拉丁对照。可见的字形选择还取决于语言和
renderer：混合 run 即使 Latin 槽未变，也可能改变拉丁字形外观；不要仅凭 XML 槽位未变
承诺像素不变。精确保真要求或 Office 路线
可用时执行独立 PowerPoint 检查；自身 PDF/PNG 与 JSON 一致不证明 Office 等价。
最终明确说明模式、实际改动槽位、推断/保留歧义及字体/视觉验证结果。
