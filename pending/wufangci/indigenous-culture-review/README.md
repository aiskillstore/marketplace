# indigenous-culture-review

一份給 AI 編碼代理（Claude Code 等）使用的 Skill，用來審核並約束 AI 產出（文字或圖像）中涉及原住民族、部落、傳統文化、圖騰、服飾、祭儀、聖物等元素的內容，防止刻板印象、文化挪用與數位殖民。

## 這是什麼

AI 生成內容在描繪原住民族時，經常出現泛部落拼貼、「消失中的民族」敘事、聖物外流、未經授權的商業挪用等問題。這份 Skill 提供一套具體的審核流程，讓 AI 在產出相關內容前，先依國際原住民族資料主權框架與台灣相關法規進行檢核。

## 依據的框架

- **CARE Principles for Indigenous Data Governance**（Global Indigenous Data Alliance, 2019）
- **OCAP®**（First Nations Information Governance Centre, Canada）
- **UNDRIP** 第11條、第31條（聯合國原住民族權利宣言）
- **Indigenous Protocol and Artificial Intelligence Position Paper**（2020）
- **Local Contexts TK Labels**
- 台灣《原住民族基本法》第13條、《原住民族傳統智慧創作保護條例》

## 使用方式

將本 repo（或 `SKILL.md` 與 `references/` 資料夾）放進支援 Skill 的 AI 編碼代理環境中（如 Claude Code 的 `.claude/skills/` 目錄），代理偵測到請求涉及原住民族相關內容時會自動套用審核流程。

## 結構

```
SKILL.md                       # 觸發條件、核心框架摘要、四步驟審核流程
references/
  frameworks.md                # 各框架完整說明與引用來源
  taiwan-tribes.md             # 台灣16族列表 + 相關法規
  checklist.md                 # 文字/圖像審核紅旗清單，含正反例
```

## 授權與定位聲明

本 Skill 由審核者以通用倫理原則與公開文獻整理而成，**不代表任何特定原住民族、部落或官方機構的正式授權或立場**。使用本 Skill 通過審核的內容，仍不構成對特定族群傳統智慧創作的合法授權；涉及商業用途時，仍須依台灣《原住民族傳統智慧創作保護條例》或相關國家的規定，取得該族群或部落本身的同意。歡迎原住民族社群或相關組織提出修正建議。
