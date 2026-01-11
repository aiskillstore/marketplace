---
name: ask-project-type
description: "曖昧なプロジェクト状態（ambiguous）のときにユーザーへ新規/既存を質問し、project_type を確定するスキル"
allowed-tools: ["Read", "AskUserQuestion"]
metadata:
  skillport:
    category: setup
    tags: [setup, project-detection, ambiguous]
    alwaysApply: false
---

# Ask Project Type Skill

`project_type == 'ambiguous'` のときに呼び出され、ユーザーに「新規/既存」を質問して `project_type` を `new` または `existing` に確定します。

---

## 入力

workflow から渡される変数:

| 変数 | 型 | 説明 |
|------|-----|------|
| `ambiguity_reason` | string | 曖昧判定の理由（`template_only`, `few_files`, `readme_only`, `scaffold_only`） |
| `code_file_count` | number | 検出されたコードファイル数 |
| `tech_stack` | object | 検出された技術スタック |

---

## 出力

| 変数 | 型 | 説明 |
|------|-----|------|
| `project_type` | `"new"` \| `"existing"` | ユーザー選択で確定したプロジェクトタイプ |

---

## 実行手順

### Step 1: 理由の日本語変換

```javascript
const REASON_MAP = {
  "template_only": "テンプレート直後の状態（package.json はあるがコードファイルがない）",
  "few_files": "コードファイルが少量（1〜9ファイル）で判断困難",
  "readme_only": "README.md / LICENSE のみ（ドキュメントだけ）",
  "scaffold_only": "設定ファイルのみ（tsconfig.json, .eslintrc など）"
};
```

### Step 2: AskUserQuestion で質問

**AskUserQuestion ツールを使用**:

```json
{
  "questions": [
    {
      "question": "プロジェクトの状態を判断できませんでした。どちらとして扱いますか？",
      "header": "プロジェクト種別",
      "options": [
        {
          "label": "新規プロジェクト",
          "description": "最初からセットアップ。Plans.md に基本タスクを追加"
        },
        {
          "label": "既存プロジェクト",
          "description": "既存コードを破壊しない。不足ファイルのみ追加"
        }
      ],
      "multiSelect": false
    }
  ]
}
```

**質問の前にコンテキストを表示**:

```
🤔 プロジェクトの状態を判断できませんでした。

**検出結果**:
- コードファイル: {{code_file_count}} ファイル
- 理由: {{ambiguity_reason の日本語説明}}
- 検出技術: {{tech_stack.frameworks があれば表示}}
```

### Step 3: 回答の処理

| ユーザー選択 | project_type |
|-------------|--------------|
| 「新規プロジェクト」 | `"new"` |
| 「既存プロジェクト」 | `"existing"` |

### Step 4: 結果を返す

確定した `project_type` を workflow に返す。

---

## 使用例

### 入力例

```json
{
  "ambiguity_reason": "template_only",
  "code_file_count": 2,
  "tech_stack": {
    "languages": ["typescript"],
    "frameworks": ["next.js"],
    "package_manager": "npm"
  }
}
```

### 出力例

```json
{
  "project_type": "new"
}
```

---

## 注意事項

- **必ずユーザー入力を待つ**: 自動判定せず、明示的な選択を求める
- **デフォルト選択なし**: どちらかを選ばせる（誤判定防止）
- **キャンセル不可**: このスキルが呼ばれた時点で判定が必要
