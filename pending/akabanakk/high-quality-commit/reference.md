# High Quality Commit - Reference Guide

このドキュメントは、高品質なgitコミットを作成するための詳細なガイダンスとベストプラクティスを提供します。

## gitコミット戦略の詳細

### Squash戦略（デフォルト）

**使用タイミング:**
- 継続的な開発中で、機能追加やバグ修正を繰り返している
- レビュー指摘への対応や微調整を行っている
- 同じ機能に関連する複数の変更を一つにまとめたい

**メリット:**
- ブランチのgitコミット履歴がクリーンになる
- レビュー時に一つの論理的な変更として見やすい
- PRマージ時に整理されたgitコミット履歴が残る

**実行例:**

```bash
# 変更をステージング
git add -A

# 直前のコミットに統合（メッセージを編集）
git commit --amend

# または、メッセージを変更せずに統合
git commit --amend --no-edit
```

**注意点:**
- 既にpushしたgitコミットをamendする場合は、force pushが必要
- チーム開発では他の人がそのgitコミットをベースにしていないか確認

### 新規gitコミット戦略

**使用タイミング:**
- 明確に異なる機能や修正を追加する
- gitコミットを分けることで履歴の理解が容易になる
- 各gitコミットが独立してビルド・テスト可能

**メリット:**
- 変更のgitコミット履歴が詳細に残る
- git bisectなどでの問題追跡が容易
- 特定の変更だけをrevertできる

**実行例:**

```bash
# 変更をステージング
git add -A

# 新規コミット作成
git commit -m "feat: add user authentication

Implement JWT-based authentication:
- Add login endpoint
- Add token validation middleware
- Add user session management

Closes #123"
```

### Interactive Rebase戦略

**使用タイミング:**
- PR作成前にgitコミット履歴を整理したい
- 複数の小さなgitコミットを論理的にまとめたい
- gitコミットの順序を変更したい
- 不要なgitコミット（WIP、fixupなど）を削除したい

**メリット:**
- クリーンで意味のあるgitコミット履歴が作成できる
- レビュアーが理解しやすい
- mainブランチのgitコミット履歴が整理される

**実行例:**

```bash
# mainブランチとの差分で対話的にrebase
git rebase -i origin/main

# または、最新のN個のコミットをrebase
git rebase -i HEAD~3
```

**エディタでの操作:**

```
pick abc1234 feat: add user model
pick def5678 fix: typo in user model
pick ghi9012 feat: add user controller
pick jkl3456 fix: validation logic

# ↓ 以下のように編集

pick abc1234 feat: add user model
squash def5678 fix: typo in user model
pick ghi9012 feat: add user controller
squash jkl3456 fix: validation logic
```

結果：2つの論理的なコミットに統合される

## gitコミットメッセージのベストプラクティス

### 良いgitコミットメッセージの例

```
feat: add user profile editing feature

Allow users to update their profile information including:
- Display name
- Email address
- Profile picture
- Bio

Implemented with form validation and real-time preview.

Closes #456
```

### 避けるべきgitコミットメッセージ

```
# 悪い例1: 不明確
update files

# 悪い例2: 詳細すぎる実装の説明
Changed UserController.ts line 45 to use async/await instead of promises

# 悪い例3: 複数の無関係な変更
Fix bug and add feature and update docs
```

### Type選択のガイド

- **feat**: ユーザーに見える新機能
- **fix**: ユーザーに影響するバグ修正
- **refactor**: 動作を変えないコードの改善
- **perf**: パフォーマンス改善
- **test**: テストの追加・修正
- **docs**: ドキュメントのみの変更
- **style**: コードフォーマット、セミコロンなど
- **chore**: ビルド、依存関係の更新など

## よくあるシナリオと対応

### シナリオ1: レビュー指摘への対応

**状況:** PRにレビューコメントがあり、修正が必要

**推奨戦略:** Squash

```bash
# 修正を実施
# ...

# 既存のコミットに統合
git add -A
git commit --amend

# 強制push（PRを更新）
git push --force-with-lease
```

### シナリオ2: 大きな機能の段階的実装

**状況:** 大きな機能を複数のステップで実装している

**推奨戦略:** 新規コミット（各段階ごと）

```bash
# ステップ1: モデル作成
git add src/models/
git commit -m "feat: add user authentication model"

# ステップ2: API実装
git add src/api/
git commit -m "feat: add authentication API endpoints"

# ステップ3: UI実装
git add src/components/
git commit -m "feat: add login UI components"
```

### シナリオ3: WIPコミットの整理

**状況:** 開発中に多数のWIPコミットを作成してしまった

**推奨戦略:** Interactive Rebase

```bash
# WIPコミットを確認
git log --oneline

# Interactive rebaseで整理
git rebase -i origin/main

# エディタで不要なコミットをsquash/fixupに変更
# 意味のあるコミットだけを残す
```

## トラブルシューティング

### 問題: amendしたコミットがpushできない

**原因:** リモートの履歴と異なる

**解決策:**

```bash
# 安全な強制push
git push --force-with-lease
```

### 問題: rebase中にコンフリクト

**解決策:**

```bash
# コンフリクトを解決
# ファイルを編集...

# 解決後、rebaseを続行
git add .
git rebase --continue

# または中止
git rebase --abort
```

### 問題: 誤ってamendしてしまった

**解決策:**

```bash
# reflogで以前の状態を確認
git reflog

# 以前のコミットに戻る
git reset --hard HEAD@{1}
```

## まとめ

高品質なgitコミットのための2つの原則：

1. **適切な戦略を選択**: Squash（基本）、新規gitコミット（独立した変更）、Rebase（gitコミット履歴整理）
2. **明確なメッセージ**: なぜその変更が必要だったのかを記述

これらを守ることで、チーム全体の開発効率が向上し、将来のメンテナンスが容易になります。
