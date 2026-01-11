---
name: spec-workflow
description: 仕様駆動開発（SDD）ワークフローを自動発動で強制。Subtask開始時にAC確認、TDD実行、完了時にACチェックを実施。スコープ外実装を禁止。Use when implementing features, creating new functionality, or when "実装して", "作成して", "開発して" keywords appear.
---

# Spec-Driven Development Workflow Skill

仕様駆動開発（SDD）の**下流工程（実装）** を担当するスキルです。
EPIC → Story → Subtaskの3階層構造に基づいた開発を行います。

> **Note**: 仕様策定（上流工程）は `/spec` Skill で行います。
> 連携フロー: `/spec`（仕様策定）→ `spec-workflow`（実装）

## 発動条件

以下のキーワード・コンテキストで自動発動：

- 実装して、作成して、開発して
- 新機能実装
- Subtask開始、Story開始
- EPIC、Story、Subtaskへの言及

## 基本原則

### 1. 仕様ファースト（必須）

実装前に必ず以下を確認：

1. `specs/{epic-id}/{story-id}/{subtask-id}.md` を読み込む
2. ユーザーストーリーを確認
3. ACを理解
4. ユーザーに「このACで進めますか？」と確認

### 2. TDD厳守（必須）

```
🔴 Red   : ACからテストケースを導出 → 失敗するテストを書く
🟢 Green : テストを通す最小限の実装
🔵 Refactor : テストを保ちながらコード改善
```

### EARS記法対応

ACがEARS記法で記述されている場合、テストケース導出を効率化：

```typescript
// EARS記法のAC例:
// WHEN ユーザーがログインを試行する際
// GIVEN 有効なメールとパスワードを入力した場合
// THEN システムはJWTトークンを発行する
// AND ダッシュボードにリダイレクトする

// テストケースへの変換:
describe('ログイン', () => {
  it('有効な認証情報でJWTトークンが発行される', () => {
    // GIVEN: 前提条件をセットアップ
    const credentials = { email: 'valid@example.com', password: 'validPass' };

    // WHEN: トリガーを実行
    const result = login(credentials);

    // THEN: 期待結果を検証
    expect(result.token).toBeDefined();
  });

  it('成功時にダッシュボードへリダイレクトする', () => {
    // AND条件のテスト
  });
});
```

### 3. スコープ管理（必須）

- ACに記載のある機能のみ実装
- スコープ外は「提案のみ」で実装しない
- 不明点はユーザーに確認

## ワークフロー詳細

### Phase 1: Subtask開始時（必須フロー）

```typescript
// 1. Subtaskファイルを読み込む
const subtaskFile = await read(`specs/{epic-id}/{story-id}/{subtask-id}.md`)

// 2. ACを確認
const acceptanceCriteria = parseAC(subtaskFile)

// 3. ユーザーストーリーを確認
const userStory = parseUserStory(subtaskFile)

// 4. ユーザーに確認
await ask(`以下のACで実装を進めます。よろしいですか？
${acceptanceCriteria.map(ac => `- ${ac}`).join('\n')}`)

// 5. テストケースを導出
const testCases = deriveTestCases(acceptanceCriteria)
```

### Phase 2: TDD実装

```typescript
// 🔴 Red: テストを先に書く
describe(subtaskTitle, () => {
  acceptanceCriteria.forEach(ac => {
    it(ac, async () => {
      // ACからテストケースを導出
    })
  })
})

// テストが失敗することを確認
await runTests() // Expected: FAIL

// 🟢 Green: 最小限の実装
// ACを満たす最小限のコードを実装
await runTests() // Expected: PASS

// 🔵 Refactor: コード改善
// テストを保ちながら改善
await runTests() // Expected: PASS
```

### Phase 3: 完了時（必須フロー）

```typescript
// 1. AC全項目をチェック
acceptanceCriteria.forEach(ac => {
  console.log(`✅ ${ac}`)
})

// 2. テストが全て通過していることを確認
await runTests() // All tests pass

// 3. ステータス更新
await updateSubtaskFile({
  status: 'completed',
  completed_at: new Date().toISOString()
})

// 4. 親Storyの確認
if (allSubtasksCompleted(storyId)) {
  await updateStoryFile({ status: 'completed' })
}

// 5. 次のSubtaskを提示
console.log(`次のSubtask: ${getNextSubtask()}`)
```

## スコープ判断

### スコープ内（実装OK）

- ACに明記されている機能
- ACを達成するために必須の技術的実装
- ユーザーストーリーの価値を実現する機能

### スコープ外（提案のみ）

- ACに記載のない「ついでに」の改善
- 将来必要になる「かもしれない」機能
- 他のSubtask/Storyで対応すべき機能

### スコープ外対応フロー

```typescript
if (isOutOfScope(request)) {
  const response = `
  ご依頼いただいた「${request}」は、現在のSubtaskのACに含まれていません。

  現在のAC:
  ${currentAC.map(ac => `- ${ac}`).join('\n')}

  対応案:
  1. 現在のSubtaskでは実装しない
  2. 別のSubtaskとして提案

  どちらを選択しますか？`

  await ask(response)
}
```

## テストファイル配置

```
specs/{epic-id}/{story-id}/{subtask-id}.md  # Subtask定義
{feature}/
├── service.ts         # 実装ファイル
└── __dev__/
    └── service.test.ts  # テストファイル（Colocation）
```

## 禁止事項

- ❌ ACなしでの実装開始
- ❌ テストなしでの実装（TDD違反）
- ❌ スコープ外の「ついでに」実装
- ❌ 複数機能の同時実装（1 Subtask = 1機能）
- ❌ ユーザー確認なしの仕様変更
- ❌ 完了確認なしのステータス更新

## エラー対応

### ACが曖昧な場合

```typescript
if (isACAmbiguous(ac)) {
  await ask(`
  以下のACが曖昧なため、実装を開始できません。

  曖昧なAC: ${ac}

  以下のように明確化することを提案します:
  「${suggestedAC}」

  この明確化で進めてよいですか？
  `)
}
```

### テストが通らない場合

```typescript
if (testsFailed) {
  // 実装を修正（Green達成まで）
  // テスト自体の問題なら修正
  // ACの解釈に問題があればユーザーに確認
}
```

## ブランチ・PR連携

本Skillは `/branch` と `/pr` を自動的に呼び出します。

### 連携フロー

```
spec-workflow 開始
    │
    ├─ Subtaskファイル読み込み
    │
    ├─ AC確認・ユーザー承認
    │       │
    │       └─ 承認後 → /branch 発火
    │          ブランチ: impl/{subtask-id}-{description}
    │
    ├─ TDD実装
    │   - 🔴 Red: テスト作成
    │   - 🟢 Green: 最小実装
    │   - 🔵 Refactor: 改善
    │
    ├─ AC全項目チェック
    │
    └─ 完了時 → /pr 発火
        PR: 実装レビュー用
```

### /branch 呼び出し

AC確認・承認後に自動発火：

```
Claude: 以下のACで実装を進めます。よろしいですか？
        - AC1: ...
        - AC2: ...

ユーザー: OK

Claude: 実装用ブランチを作成します。

        ブランチ名: impl/001-01-01-user-auth
        ベース: main

        作成してよいですか？
```

### /pr 呼び出し

AC全項目チェック完了後に自動発火：

```
Claude: 全てのACを満たしました。

        ✅ AC1: 有効な認証情報でログイン成功
        ✅ AC2: 無効な認証情報でエラー表示
        ✅ AC3: MFAコード検証

        PRを作成しますか？
        タイトル: impl: ユーザー認証機能の実装

        ## Summary
        - 001-01-01 を実装
        - ログイン/ログアウト機能

        ## AC確認
        - [x] AC1
        - [x] AC2
        - [x] AC3
```

---

## 参照ドキュメント

- [SPEC_FORMAT.md](../../../.ai/SPEC_FORMAT.md) - 仕様フォーマット定義
- [WORKFLOW.md](../../../.ai/WORKFLOW.md) - ワークフロー詳細

---

## 関連Skill

- **/branch**: ブランチ作成（本Skillから自動呼び出し）
- **/pr**: PR作成（本Skillから自動呼び出し）
- **/spec**: 仕様策定（本Skillの上流工程）

### 全体連携フロー

```
/spec（仕様策定）
    ├─ /branch 発火（spec/*）
    ├─ ファイル生成
    └─ /pr 発火（仕様レビュー）
        ↓ マージ後
spec-workflow（実装）← 本Skill
    ├─ /branch 発火（impl/*）
    ├─ TDD実装
    └─ /pr 発火（実装レビュー）
```

## 使用例

### 例1: 新規Subtask実装

```
ユーザー: 「001-01-01の設定要件Subtaskを実装して」

[自動] spec-workflow Skill発動
[自動] specs/001-environment-setup/001-01-common-config/001-01-01-config-requirements.md を読み込み

Claude: 「以下のACで実装を進めます。よろしいですか？
- 設定ファイル配置方針が明確に決定されていること
- ESLint、Prettier、TypeScriptの設定内容が仕様として確定していること
- package.jsonスクリプトの統一方針が決定されていること」

ユーザー: 「OK」

Claude: 「🔴 Red: テストケースを導出します...」
（以下、TDDサイクル）
```

### 例2: スコープ外リクエスト

```
ユーザー: 「ついでにCI/CDも設定して」

Claude: 「ご依頼いただいた「CI/CD設定」は、現在のSubtaskのACに含まれていません。

現在のAC:
- 設定ファイル配置方針が明確に決定されていること
- ESLint、Prettier、TypeScriptの設定内容が仕様として確定していること

対応案:
1. 現在のSubtaskでは実装しない（推奨）
2. 新規Subtaskとして定義する

どちらを選択しますか？」
```
