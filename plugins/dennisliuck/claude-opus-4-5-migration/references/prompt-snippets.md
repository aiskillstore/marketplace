# Opus 4.5 提示詞片段 | Prompt Snippets for Opus 4.5

這些是遷移至 Claude Opus 4.5 時可選的提示詞修改。僅在使用者明確請求或報告特定問題時才套用這些片段。

These are optional prompt modifications for migrating to Claude Opus 4.5. They should only be applied when users explicitly request them or report specific issues.

---

## 1. 工具過度觸發 | Tool Overtriggering

**問題 Issue**：為了防止舊模型觸發不足而設計的強硬語言，在 Opus 4.5 上導致過多的工具呼叫。

Aggressive language designed to prevent undertriggering on older models causes excessive tool calls in Opus 4.5.

**替換建議 Replacements**：

| 原始 Original | 替換為 Replace with |
|---------------|---------------------|
| `CRITICAL: You MUST use this tool when...` | `Use this tool when...` |
| `ALWAYS call the search function before...` | `Call the search function before...` |
| `You are REQUIRED to...` | `You should...` |
| `NEVER skip this step` | `Don't skip this step` |

---

## 2. 過度工程化防範 | Over-Engineering Prevention

**要添加的片段 Snippet to add**：

```
# English version:
Avoid over-engineering. Only make changes directly requested or necessary. Keep solutions simple.
Don't add unrequested features, refactor code, or make "improvements" beyond scope.
Don't add error handling for impossible scenarios.
Trust internal code guarantees. Only validate at system boundaries.
Don't create helpers for one-time operations.

# 中文版本：
避免過度工程化。只進行直接請求或必要的變更。保持解決方案簡單。
不要添加未請求的功能、重構程式碼，或進行超出範圍的「改進」。
不要為不可能發生的場景添加錯誤處理。
信任內部程式碼保證。只在系統邊界進行驗證。
不要為一次性操作建立輔助函數。
```

---

## 3. 程式碼探索 | Code Exploration

**要添加的片段 Snippet to add**：

```
# English version:
ALWAYS read relevant files before proposing edits. Don't speculate about code unreviewed.
If user references specific files, you MUST inspect them before explaining fixes.
Be rigorous searching for key facts.
Thoroughly review codebase style, conventions, and abstractions before implementing.

# 中文版本：
在提出編輯之前，務必先讀取相關檔案。不要對未審閱的程式碼進行推測。
如果使用者提及特定檔案，您必須在解釋修正之前檢視它們。
嚴格搜尋關鍵事實。
在實作之前徹底審閱程式碼庫的風格、慣例和抽象化。
```

---

## 4. 前端設計品質 | Frontend Design Quality

**問題 Issue**：預設輸出可能看起來很通用（「AI 模板」美學）。

Default outputs may appear generic ("AI slop" aesthetic).

**要添加的片段 Snippet to add**：

```
# English version:
Avoid overused fonts (Inter, Roboto, Arial), clichéd color schemes (purple gradients), and predictable layouts.
Focus on distinctive typography, cohesive color themes, thoughtful animations, and atmospheric backgrounds.
Make unexpected creative choices specific to context.

# 中文版本：
避免使用過度使用的字體（Inter、Roboto、Arial）、陳腔濫調的配色（紫色漸層），以及可預測的版面配置。
專注於獨特的字體排版、有凝聚力的色彩主題、深思熟慮的動畫效果，以及有氛圍的背景。
做出針對特定情境的意外創意選擇。
```

---

## 5. 思考敏感度 | Thinking Sensitivity

**問題 Issue**：當延伸思考被停用時，Opus 4.5 對「think」術語很敏感。

When extended thinking is disabled, Opus 4.5 is sensitive to "think" terminology.

**替換建議 Replacements**：

| 原始 Original | 替換為 Replace with |
|---------------|---------------------|
| `think about` | `consider` |
| `think through` | `evaluate` |
| `I think` | `I believe` |
| `thinking` | `reasoning` 或 `considering` |

---

## 使用指南 | Usage Guidelines

- 深思熟慮地整合到現有提示詞結構中
  Integrate thoughtfully into existing prompt structure
- 用描述性的 XML 標籤包裝新增內容
  Wrap additions in descriptive XML tags
- 匹配現有提示詞的風格和詳細程度
  Match existing prompt style and verbosity
- 將內容邏輯性地放在相關指令附近
  Place logically near related instructions
- 保留所有現有的功能性內容
  Preserve all functional existing content
- 記錄遷移過程中所做的所有變更
  Document all changes made during migration
