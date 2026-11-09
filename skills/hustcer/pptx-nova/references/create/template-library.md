# Template Library

Use this reference when choosing or adding local assets under
`skills/pptx-nova/assets/`.

## Catalogs

| Directory  | Catalog                | Purpose                                                  |
| ---------- | ---------------------- | -------------------------------------------------------- |
| `brands/`  | `brands/catalog.json`  | Brand profiles and apply/check commands                  |
| `layouts/` | `layouts/catalog.json` | Layout patterns, grid systems, and layout-contract hints |
| `decks/`   | `decks/catalog.json`   | Complete generators, outlines, and patch bundles         |
| `themes/`  | `themes/catalog.json`  | themePack/stylePack entries for `catalog themes`         |
| `charts/`  | `charts/catalog.json`  | Native chart/table/diagram presets                       |
| `icons/`   | `icons/catalog.json`   | Native shape icons, Tabler bundle, and vector policy     |

## Selection Flow

1. Pick theme/style first with `xdoc pptx catalog themes --json`.
2. If the user provided a reference deck and a new outline/content goal, follow
   `reference-create.md` first. If the reference deck is only for style study, run:

```bash
xdoc pptx extract-style reference.pptx --output style.json --json
```

3. If the reference deck should become a reusable local template asset, run:

```bash
xdoc pptx import-template reference.pptx --name stable-id --output-dir skills/pptx-nova/assets --json
```

This writes `decks/<id>/template.pptx`, `decks/<id>/profile.json`,
brand/layout/deck profile JSON, theme/style pack JSON, and updates
`brands/`, `layouts/`, `decks/`, and `themes/` catalog files. Use
`--overwrite` only when replacing the same imported id.

4. For whole-slide reuse, use:

```bash
xdoc pptx slide-copy -i target.pptx --source reference.pptx \
  --slides 1,3,5-8 --output out.pptx --json
```

`--slides` is 1-based and copies the requested set in one transaction.
Provide the target either positionally or with `--input`, never both, even when
equal; blank targets are invalid. Path equality with source/output does not replace
argument identity or bypass normal authorization and overwrite checks.
`--all` selects every source slide, and the two selectors are mutually
exclusive; there is no `--slide N` option. Retain
the native `pptx-slide-copy/v1` report when this copy participates in an Edit
Contract; require its read-only `ready` preflight, current input fingerprints,
and empty blockers.

5. For generated decks, start from `assets/examples/generator/deck-generator-template.mjs`
   and pass selected theme/style IDs.

## Brand / Layout / Deck Fusion

`pptx-nova` 支持把 catalog 中的 brand、layout、deck 资产组合成一次生成任务，但融合结果必须
进入 run 目录的 `deck_lock.json`，不要在 generator 里临时猜测。触发方式是用户明确给出
精确 catalog id 或显式路径；不要用模糊品牌名、风格形容词或相似文件名自动匹配。
这不是一套独立模板流程；它只是把模板影响拆成 identity / structure / deck 起点三段，
然后自然落进 `deck_lock`、DeckKit 选择和 `assets_manifest`。

### 三类资产的职责

| kind     | 拥有的段                     | 典型内容                                                                       |
| -------- | ---------------------------- | ------------------------------------------------------------------------------ |
| `brand`  | identity                     | 颜色、字体、logo、品牌标识、页脚口径、图标风格、禁止项                         |
| `layout` | structure                    | 画布、网格、边距、page rhythm、layoutIntent、slide type 到布局的映射、密度限制 |
| `deck`   | complete deck starting point | 完整 generator / outline / patch bundle、默认 identity/structure               |

融合优先级按段而不是按字段：

| 输入组合              | identity 来源 | structure 来源 | deck 起点 |
| --------------------- | ------------- | -------------- | --------- |
| brand only            | brand         | 当前模式默认   | 无        |
| layout only           | 当前模式默认  | layout         | 无        |
| deck only             | deck          | deck           | deck      |
| brand + layout        | brand         | layout         | 无        |
| brand + deck          | brand         | deck           | deck      |
| layout + deck         | deck          | layout         | deck      |
| brand + layout + deck | brand         | layout         | deck      |

同段内不做隐式字段级混搭。例如 `brand` 覆盖 identity 时，颜色、字体、logo、图标风格作为
一个整体进入 `deck_lock.templateFusion.identityFrom`；如果用户要求“用 A 品牌但主色改成
红色”，把这个改动记录为 Studio 确认后的 override，而不是在 fusion 阶段偷偷改 catalog。

### 冲突处理

- 同 kind 多个资产（两个 brand、两个 layout、两个 deck）默认冲突，先问用户选哪个；只有用户
  明确要求逐段挑选时，才列出可选段。
- brand 与 deck 的 identity 冲突时，显式 brand 覆盖 deck；layout 与 deck 的 structure 冲突时，
  显式 layout 覆盖 deck。
- 如果 deck 的 generator 不支持 layout 要求的 slide type 或密度，fusion 失败；先扩展 DeckKit
  或换 deck 起点，不要硬套。
- 任何被复用的 logo、照片、插画或第三方图标都要进入 `assets_manifest.json`，并记录来源和授权。

### Run 目录产物

融合结果默认只写入 `deck_lock.json.templateFusion`。只有同时满足以下任一条件时，才额外写
`template_fusion.json`：多来源有冲突、用户做了 override、需要给后续人类审计或模板沉淀复用。

- `deck_lock.json.templateFusion`：只保留生成所需的段级结果，例如
  `identityFrom`、`structureFrom`、`deckFrom`、`overrides[]`。structure 约束还应反映到
  `slides[].rhythm`、`slides[].layoutIntent` 和 `slides[].visualDensity`，不要只记录模板 id。
- `template_fusion.json`（按需）：完整记录输入资产、段级来源、冲突和用户 override，方便审计。

需要审计时的最小 `template_fusion.json`：

```json
{
  "schemaVersion": "pptx-nova-template-fusion/v1",
  "sources": [
    { "kind": "brand", "id": "example-brand-profile", "path": "assets/brand-profile.example.json" },
    { "kind": "layout", "id": "executive-grid" },
    { "kind": "deck", "id": "deck-generator-template" }
  ],
  "segments": {
    "identityFrom": "brand:example-brand-profile",
    "structureFrom": "layout:executive-grid",
    "deckFrom": "deck:deck-generator-template"
  },
  "overrides": [
    {
      "segment": "identity",
      "reason": "User requested darker primary blue in Studio confirmation",
      "path": "colors.primary"
    }
  ],
  "conflicts": []
}
```

`cli/create/check-lock.mjs` 不解析完整 fusion 语义，但会检查 `deck_lock.json` 中的颜色、
字体、资源和 slide type 是否被 content/patch 漂移。fusion 阶段的目标是让这些约束先进入 lock。

## Adding Assets

- Add metadata to the relevant `catalog.json` before adding binaries.
- Prefer `import-template` for reference PPTX ingestion so catalog entries and
  extracted profiles stay consistent.
- Record license/source before committing any logo, icon, image, or template file.
- Prefer native editable objects over SVG/image-only assets.
- For common deck icons, use the Tabler full icon pack:
  `icons/tabler-icons.pack.br` contains outline and filled icons, and
  `icons/icon-license` carries the Tabler MIT license. Agents should search or
  fetch icon names through `node <skill-root>/scripts/cli/assets/icons.mjs ...`; DeckKit
  generators should read icons through `assets/deckkits/shared/icon-assets.kit.mjs`
  instead of fetching icons online or reading the Tabler checkout during PPTX
  generation.
- Keep chart/table/diagram presets themePack-aware so `swap-theme` can recolor
  the resulting deck without regeneration.
