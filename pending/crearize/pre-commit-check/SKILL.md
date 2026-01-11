---
name: pre-commit-check
description: コミット前品質チェックスキル（Lint、テスト、ビルドの高速検証）
---

# Pre-Commit Check Skill - コミット前品質チェックスキル

## 役割

コミット前の品質チェックを高速に実行するスキルです。qa-checkよりも軽量で、開発中の頻繁なチェックに適しています。

## qa-check との違い

| 項目 | pre-commit-check | qa-check |
|------|-----------------|----------|
| 目的 | 開発中の頻繁なチェック | PR作成前の最終チェック |
| 実行速度 | 高速（変更ファイルのみ） | 通常（全体チェック） |
| テスト | 変更箇所のみ（オプション） | 全テスト実行 |
| カバレッジ | チェックしない | 80%以上必須 |
| ビルド | スキップ可能 | 必須 |
| 使用タイミング | コミット直前 | PR作成直前 |

## 実行フロー

### Phase 1: 変更ファイル確認

```bash
# 変更されたファイルを確認
git status --short

# ステージングされたファイルを確認
git diff --cached --name-only

# 変更ファイルからBackend/Frontendを判定
```

### Phase 2: Backend チェック（変更がある場合）

#### 2-1. Lint実行（変更ファイルのみ）
```bash
cd backend

# Checkstyle（変更ファイルのみ）
./gradlew checkstyleMain checkstyleTest

# SpotBugs（変更ファイルのみ）
./gradlew spotbugsMain spotbugsTest
```

#### 2-2. テスト実行（skip_tests=false の場合）
```bash
# 変更されたクラスに関連するテストのみ実行
./gradlew test --tests "*[変更されたクラス名]Test"
```

#### 2-3. コンパイル確認
```bash
# ビルドはスキップしてコンパイルのみ
./gradlew compileJava compileTestJava
```

### Phase 3: Frontend チェック（変更がある場合）

#### 3-1. Lint実行
```bash
cd frontend

# Biome Lint（全体）
pnpm run lint:check
```

#### 3-2. テスト実行（skip_tests=false の場合）
```bash
# 変更されたファイルに関連するテストのみ実行
pnpm run test:ci --changed
```

#### 3-3. 型チェック
```bash
# TypeScript型チェック
npx tsc --noEmit
```

### Phase 4: 結果レポート

#### 成功時
```markdown
## Pre-Commit Check 完了

### Backend
- ✅ Lint: エラーなし
- ✅ テスト: [実行数] 件成功
- ✅ コンパイル: 成功

### Frontend
- ✅ Lint: エラーなし
- ✅ テスト: [実行数] 件成功
- ✅ 型チェック: エラーなし

### 次のステップ
コミット可能です。
```

#### 失敗時
```markdown
## Pre-Commit Check 失敗

### Backend
- ❌ Lint: エラー [数] 件
  - [エラー内容]
- ❌ テスト: [失敗数] 件失敗
  - [失敗テスト名]
- ✅ コンパイル: 成功

### Frontend
- ✅ Lint: エラーなし
- ✅ テスト: すべて成功
- ✅ 型チェック: エラーなし

### 修正が必要な項目
1. Backend Lintエラーを修正
2. Backend テスト失敗を修正

### 次のステップ
上記を修正してから再度チェックしてください。
```

## 高速化のポイント

### 1. 変更ファイルのみチェック
- git diffで変更ファイルを検出
- 関連するテストのみ実行
- ビルドをスキップ

### 2. 並行実行
- Backend/Frontendのチェックを並行実行
- Lint/テスト/型チェックを並行実行可能な場合は並行実行

### 3. キャッシュ活用
- Gradleのビルドキャッシュ活用
- pnpmのキャッシュ活用

## 使用ツール

### 必須ツール
- **Bash**: Lint/テスト/コンパイル実行、git操作

### 推奨ツール
- **Grep**: エラーパターン検索
- **Read**: レポートファイル確認

## 重要な注意事項

### pre-commit-check は軽量チェック
- PR作成前は必ず qa-check を実行すること
- pre-commit-check は開発中の頻繁なチェック用
- カバレッジチェックは行わない

### テストスキップの判断
- skip_tests=true は緊急時のみ使用
- 通常は skip_tests=false でテストを実行すること
- テストをスキップした場合は後で必ず実行

## 参照ドキュメント

### 必須参照
- `documents/development/development-policy.md`: 開発ガイドライン

### 設定ファイル
- `backend/config/checkstyle/checkstyle.xml`: Checkstyle設定
- `backend/config/spotbugs/spotbugs-exclude.xml`: SpotBugs設定
- `frontend/biome.json`: Biome設定
