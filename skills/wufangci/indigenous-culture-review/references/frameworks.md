# 國際原住民族資料/文化主權框架

本文件提供 SKILL.md 所引用之各框架的完整背景，供需要深入說明審核理由時查閱。

## 1. CARE Principles for Indigenous Data Governance

由 Global Indigenous Data Alliance（GIDA）於 2019 年在波札那 Gaborone 的一場原住民主導工作坊中提出，作為 FAIR 資料原則（Findable, Accessible, Interoperable, Reusable）的補充——FAIR 只關心資料好不好用，CARE 關心資料的使用**是否符合原住民族的權益與自決權**。

- **Collective Benefit（集體受益）**：資料生態系的設計與運作，應讓原住民族能從中受益，而非只讓資料使用者（含 AI 公司）單方受益。
- **Authority to Control（控制權）**：原住民族對於涉及自身的資料，其權利與利益須被承認，其控制權須被賦權，而非預設由外部機構或平台決定如何使用。
- **Responsibility（責任）**：使用原住民資料/文化素材者，有責任揭露這些資料如何被使用、由誰使用。
- **Ethics（倫理）**：原住民族的權利與福祉應優先於資料使用的「效率」或「創新」本身。

**對本 Skill 的意義**：AI 生成內容如果無法說明「這個文化元素的使用，原住民族本身能否受益、能否控制」，就應視為未通過 CARE 檢驗。

來源：The CARE Principles for Indigenous Data Governance, *Data Science Journal*, 2020；Global Indigenous Data Alliance。

## 2. OCAP®（First Nations 原則）

1998 年由加拿大 First Nations Information Governance Centre（FNIGC）建立，是北美原住民資料主權運動最早、最具體的原則框架之一。

- **Ownership（所有權）**：社群集體擁有其資訊，如同個人擁有其個資。
- **Control（控制）**：從資料蒐集、使用、揭露到銷毀的全流程，社群有控制權。
- **Access（近用權）**：社群有權取得關於自身的資料，並決定誰能存取。
- **Possession（保管）**：資料的實體/技術保管方式，是落實所有權的具體機制。

**對本 Skill 的意義**：當 AI 被要求「生成」某族群的傳統知識內容時，等同於在沒有該族群 Control 與 Possession 的情況下創造關於他們的新「資料」——這正是 OCAP 想防止的情境，因此高風險項目應從嚴處理。

來源：First Nations Information Governance Centre；*First Nations principles of OCAP*（Wikipedia 條目整理版）。

## 3. UNDRIP（聯合國原住民族權利宣言，2007）

- **第11條**：原住民族有權維護、保護與發展其文化過去、現在與未來的表現形式；各國應提供有效機制，救濟未經其**自由、事先、知情同意（Free, Prior and Informed Consent, FPIC）**而取用其文化、智慧、宗教與精神財產的行為。
- **第31條**：原住民族有權維護、控制、保護與發展其文化遺產、傳統知識、傳統文化表現形式，以及科學、技術與文化表現的表徵，包括人類與遺傳資源、種子、藥物、動植物特性知識、口述傳統、文學、設計、體育與傳統遊戲、視覺與表演藝術等。

**對本 Skill 的意義**：FPIC 是判斷「這個內容能不能生成」的關鍵門檻——AI 平台本身不是原住民族的代理人，不能替族群「同意」自己的文化被如何使用；當無法確認 FPIC 是否存在時，應採保守立場。

## 4. Indigenous Protocol and Artificial Intelligence Position Paper（2020）

由 Initiative for Indigenous Futures 與加拿大 CIFAR（Canadian Institute for Advanced Research）發起，匯集北美、澳洲、紐西蘭與太平洋地區原住民學者與創作者歷時 20 個月的討論成果。

核心主張：AI 訓練資料不應被當成可任意榨取的「公共財」（extractive approach），而應採取**關係性（relational）**取徑——承認資料背後有具體的人、土地、祖先關係與責任。文件同時提供了設計指南、學術論文、藝術創作與技術原型描述，作為 AI 開發者將原住民觀點納入倫理設計的起點。

**對本 Skill 的意義**：本 Skill 的「預設限制、需要具體脈絡才放行」邏輯，即是此文件「拒絕榨取式取徑」主張的具體落地。

## 5. Local Contexts / Traditional Knowledge (TK) Labels

由 Local Contexts 組織開發，讓原住民社群能針對數位化流通在外的文化遺產、資料，標註具體的使用條件，例如：

- TK 神聖（Sacred）：僅限特定儀式脈絡使用
- TK 限性別（Gender Restricted）：僅特定性別成員可觀看/使用
- TK 季節性（Seasonal）：僅限特定季節/時節使用
- TK 外展用（Outreach）：社群主動同意用於公眾教育

與機構單方發出的 Notices 不同，Labels 是由原住民社群自己制定與套用的。

**對本 Skill 的意義**：AI 無法得知某個圖騰、祭儀場景是否被標註為神聖或限制性內容，因此**「無法確認」本身就是風險訊號**，應比照最嚴格的標籤（視為受限）處理，而非預設可自由生成。

## 6. 相關性總結

CARE、OCAP 與 UNDRIP 都指向同一個核心判準：**誰有權決定這個文化元素能不能被使用、怎麼被使用**。AI 系統既非原住民族本身，也非其正式授權代理人，因此在無法確認「族群自己是否同意、是否受益」的情況下，審核應傾向保守，而非以「創作自由」或「藝術表現」作為預設放行的理由。
