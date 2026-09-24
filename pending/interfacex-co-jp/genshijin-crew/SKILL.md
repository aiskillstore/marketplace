---
name: genshijin-crew
description: >
  原始人スタイル subagent への委譲判断ガイド。`genshijin-investigator` (コード位置特定)、
  `genshijin-builder` (1-2ファイル編集)、`genshijin-reviewer` (diff レビュー) を inline作業 or
  vanilla `Explore` の代わりにスポーンするタイミングを示す。subagent 出力は原始人圧縮 →
  主コンテキストに戻る tool-result が約60%縮小 → 長セッション持続。
  Trigger: 「subagent 委譲」「genshijin-crew 使用」「investigator/builder/reviewer 起動」「コンテキスト節約」「圧縮 agent 出力」。
---

genshijin-crew = 原始人形式で出力する3 subagent preset。役割は Anthropic デフォルト (`Explore`、編集系 agent、reviewer) と同じ。差分は返ってくる tool-result が圧縮済 → 主コンテキスト消費が委譲毎に縮む。

## genshijin-crew vs 代替の使い分け

| タスク | 使用 |
|---|---|
| 「Xの定義どこ / Yを呼ぶ箇所 / Zの全用法」 | `genshijin-investigator` |
| 同上 + アーキテクチャ解説/提案も欲しい | `Explore` (vanilla) |
| Surgical編集、≤2ファイル、スコープ明確 | `genshijin-builder` |
| 新機能 / 3+ファイル / cross-cutting refactor | 主スレッド or `feature-dev:code-architect` |
| Diff/branch/file の bug レビュー | `genshijin-reviewer` |
| rationale + alternatives 付き深いコードレビュー | `Code Reviewer` (vanilla) |
| 1行回答済の確実な内容 | 主スレッド、subagent不要 |

判断基準: **subagent 出力を1/3トークンで欲しいなら genshijin-crew、散文で欲しいなら vanilla**。

## なぜ存在するか (実利)

Subagent tool-result は主コンテキストに verbatim 注入される。Vanilla `Explore` が散文2k tokens 返すと毎回主コンテキスト2k消費。同じ発見が `genshijin-investigator` だと約700 tokens。1セッション20委譲で context exhaustion vs タスク完了の差。

## 出力契約

主スレッドが agent 別に依拠できる形式:

**`genshijin-investigator`**
```
<Header>:
- path:line — `symbol` — short note
集計: <counts>。
```
or `No match.` 必ずファイルパス先頭、行番号付、シンボルはバッククォート。`path:\d+` で grep可能。

**`genshijin-builder`**
```
<path:line-range> — <change ≤10語>。
verified: <re-read OK | mismatch @ path:line>。
```
or 以下のいずれか: `too-big.` / `needs-confirm.` / `ambiguous.` / `regressed.` (terminal first token)。

**`genshijin-reviewer`**
```
path:line: <emoji> <severity>: <問題>. <修正>.
totals: N🔴 N🟡 N🔵 N❓
```
or `No issues.` ファイル → 行昇順。

## チェイニングパターン

**位置特定 → 修正 → 検証** (最頻):
1. `genshijin-investigator` で site list 取得
2. 主スレッドが1-2 site選び `genshijin-builder` にパス渡す
3. `genshijin-reviewer` が diff 監査

**並列スカウト** (調査が広い時):
1メッセージで `genshijin-investigator` 2-3個並列起動 (異なる角度: defs vs callers vs tests)。主スレッドで集約。

**単発編集** (sit既知時):
investigator スキップ。`genshijin-builder` に直接 path:line 渡す。

## 禁止事項

- ファイル未特定で `genshijin-builder` 使用禁止。先に investigator 起動 → でないと主スレッドがコンテキスト渡しでトークン消費。
- 5ファイル refactor で `genshijin-investigator → genshijin-builder` チェーン禁止。Builder は `too-big.` 返却 → ターン浪費。
- `genshijin-reviewer` に「全般フィードバック」依頼禁止 → findings のみ返却、アーキテクチャ意見なし。それ用は `Code Reviewer`。
- 散文期待禁止。genshijin-crew 出力は構造化、時に cryptic。人間が直読する場合は主スレッドが言換え。

## 自動解除 (継承)

Subagent はセキュリティ警告・取消不可操作の確認・fragment 曖昧で誤読リスクある出力で原始人 → 通常日本語に切替。該当部分後復帰。
