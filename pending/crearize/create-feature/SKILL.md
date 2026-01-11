---
name: create-feature
description: 新機能開発統合スキル - 要件分析からPR作成まで、新機能開発の全工程を自動化します。analyze-requirements、develop-backend、develop-frontend、review-architecture、qa-check、create-prの各専門スキルを適切な順序で呼び出し、完全な機能開発を実現します。品質基準（テストカバレッジ80%以上、Lint/ビルド成功）を満たすまで自動的にレビュー・修正を繰り返します。
---

# Create Feature Skill - 新機能開発統合スキル

## 役割

新機能開発の全工程を統合的に実行するスキルです。要件分析から PR 作成まで、各専門スキルを適切な順序で呼び出し、完全な機能開発を自動化します。

## 実行フロー

### Phase 1: 事前確認とブランチ作成

#### 1-1. パラメータ確認
- feature_name: 機能名確認
- issue_number: Issue番号確認
- specification_path: 仕様書パス確認（オプション）
- figma_url: FigmaデザインURL確認（オプション）
- target: 実装対象確認（backend/frontend/fullstack）

#### 1-2. ブランチ管理
```bash
# 現在のブランチを確認
git branch --show-current

# mainブランチの場合は新しいブランチを作成
# ブランチ名: feature/[feature_name]-[issue_number]
# 例: feature/user-profile-123

# mainブランチでないことを確認
```

### Phase 2: 要件分析（analyze-requirements）

```
/analyze-requirements feature_name="[feature_name]" figma_url="[figma_url]"
```

**実行内容**:
- プロジェクト構造理解
- 既存機能調査
- 外部リソース取得（Figma、Context7）
- データモデル設計
- API設計
- 分析レポート作成

**成果物**:
- 分析レポート
- データモデル設計案
- API設計案

### Phase 3: Backend実装（develop-backend）

**条件**: target が "backend" または "fullstack" の場合のみ実行

```
/develop-backend feature_name="[feature_name]" specification_path="[specification_path]" issue_number=[issue_number] branch_type="feature"
```

**実行内容**:
- データベース設計（Flyway マイグレーション）
- Entity/DTO作成
- Mapper実装（MyBatis）
- Service実装
- Controller実装
- OpenAPI仕様書更新
- 単体テスト実装
- error-codes.md更新（新規エラー時）
- database-design.md更新（DB変更時）
- サーバー起動確認

**成果物**:
- Controller/Service/Mapper/Entity/DTO クラス
- XMLマッピングファイル
- Flywayマイグレーションファイル
- 単体テストコード
- 更新されたドキュメント

### Phase 4: Frontend実装（develop-frontend）

**条件**: target が "frontend" または "fullstack" の場合のみ実行

```
/develop-frontend feature_name="[feature_name]" specification_path="[specification_path]" figma_url="[figma_url]" issue_number=[issue_number] branch_type="feature"
```

**実行内容**:
- コンポーネント設計（Presentational/Container）
- 型定義とAPI連携準備
- Presentationalコンポーネント実装
- Containerコンポーネント実装
- API連携実装
- フォーム実装（該当する場合）
- 単体テスト実装
- サーバー起動確認

**成果物**:
- ページコンポーネント
- Presentational/Containerコンポーネント
- カスタムフック
- 単体テストコード
- Storybookストーリー

### Phase 5: アーキテクチャレビュー（review-architecture）

```
/review-architecture target="[target]"
```

**実行内容**:
- コーディング規約準拠確認
- 設計整合性チェック
- ドキュメント整合性チェック
- DRY原則の確認
- 禁止事項違反の検出

**判定**:
- ✅ 合格 → Phase 6へ
- ❌ 不合格 → Phase 3または4へ戻って修正

### Phase 6: 品質保証（qa-check）

```
/qa-check target="[target]"
```

**実行内容**:
- Lintチェック
- 単体テスト実行
- ビルド検証
- カバレッジ確認（80%以上）

**判定**:
- ✅ 合格 → Phase 7へ
- ❌ 不合格 → Phase 3または4へ戻って修正

### Phase 7: PR作成（create-pr）

```
/create-pr issue_number=[issue_number]
```

**実行内容**:
- 変更内容の確認
- PR説明文の自動生成
- GitHub PRの作成
- PR URL返却

**成果物**:
- GitHub Pull Request
- PR URL

### Phase 8: 完了報告

```markdown
## Create Feature 完了報告

### 機能名
- [feature_name]

### Issue番号
- #[issue_number]

### PR URL
- [PR URL]

### 実装内容

#### Backend（実装した場合）
- **API**: [実装したエンドポイント一覧]
- **データベース**: [追加/変更したテーブル]
- **テスト**: [テストクラス数] クラス、[テストケース数] ケース
- **カバレッジ**: [数値]%

#### Frontend（実装した場合）
- **ページ**: [実装したページ一覧]
- **コンポーネント**: [作成したコンポーネント一覧]
- **テスト**: [テストファイル数] ファイル、[テストケース数] ケース
- **カバレッジ**: [数値]%

### 品質保証結果
- ✅ アーキテクチャレビュー: 合格
- ✅ QAチェック: 合格
- ✅ テストカバレッジ: 80%以上
- ✅ Lint/ビルド: 成功

### 次のステップ
Pull Requestのレビューを依頼してください。
```

## エラーハンドリング

### Phase 5（アーキテクチャレビュー）で不合格の場合

1. レビュー結果を分析
2. Backend/Frontendの該当箇所を特定
3. 必須修正事項を修正:
   - Backend修正が必要 → develop-backend を再実行
   - Frontend修正が必要 → develop-frontend を再実行
4. 修正完了後、review-architecture を再実行
5. 合格するまで繰り返し

### Phase 6（QAチェック）で不合格の場合

1. QA結果を分析
2. 問題箇所を特定:
   - Lintエラー → コーディング規約準拠のため修正
   - テスト失敗 → テストまたは実装を修正
   - ビルドエラー → ビルドエラーを修正
   - カバレッジ不足 → テストを追加
3. 修正完了後、qa-check を再実行
4. 合格するまで繰り返し

### 各Phaseでのエラー

各スキル実行時にエラーが発生した場合:
1. エラー内容を詳細に確認
2. 原因を分析
3. 該当スキルを再実行（パラメータ調整等）
4. 解決しない場合はユーザーに報告

## 使用するスキル一覧

1. **analyze-requirements**: 要件分析
2. **develop-backend**: バックエンド実装（条件付き）
3. **develop-frontend**: フロントエンド実装（条件付き）
4. **review-architecture**: アーキテクチャレビュー
5. **qa-check**: 品質保証
6. **create-pr**: PR作成

## 重要な注意事項

### 必ず守るべきルール

1. **ブランチ確認**: mainブランチでないことを必ず確認
2. **Issue番号必須**: 全てのスキル呼び出しで統一したIssue番号を使用
3. **順序厳守**: Phase 1 → 2 → 3/4 → 5 → 6 → 7 → 8 の順序を守る
4. **レビュー/QA合格必須**: Phase 5, 6 で不合格の場合は修正して再実行
5. **完全自動化**: 人間の介入なしで完結させる（エラー時を除く）

### 品質基準

- テストカバレッジ: 80%以上
- Lintエラー: 0件
- テスト失敗: 0件
- ビルドエラー: 0件
- アーキテクチャレビュー: 合格
- QAチェック: 合格

### タイムアウト対策

- 各スキル実行時のタイムアウトに注意
- 長時間かかる処理（ビルド等）はタイムアウト設定を調整
- バックグラウンド実行も活用

## トラブルシューティング

### analyze-requirements が失敗
- 仕様書パスを確認
- Figma URLを確認
- プロジェクト構造を確認

### develop-backend/frontend が失敗
- ブランチを確認
- Issue番号を確認
- 依存関係を確認
- サーバー起動確認

### review-architecture が不合格
- レビュー結果の必須修正事項を確認
- 該当箇所を修正
- 再度レビュー実行

### qa-check が不合格
- QA結果の修正必要項目を確認
- Lint/テスト/ビルドエラーを修正
- 再度QA実行

### create-pr が失敗
- git statusを確認
- コミット内容を確認
- GitHub認証を確認

## 参照ドキュメント

### 必須参照
- `documents/development/development-policy.md`: 開発ガイドライン
- `documents/development/quick-checklist.md`: 簡易チェックリスト

### 各スキルの詳細
- `.claude/skills/analyze-requirements/README.md`
- `.claude/skills/develop-backend/README.md`
- `.claude/skills/develop-frontend/README.md`
- `.claude/skills/review-architecture/README.md`
- `.claude/skills/qa-check/README.md`
- `.claude/skills/create-pr/README.md`
