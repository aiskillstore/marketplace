---
name: high-quality-commit
description: コード変更を適切なgitコミット戦略でgit commitします。基本的には既存のgitコミットへのsquash戦略を採用し、必要に応じてブランチ全体のgitコミット履歴を再構成します。実装完了時やユーザーがgit commitを依頼した時に使用します。
---

# High Quality Commit

このスキルは、コード変更を高品質なgitコミットとして記録するための包括的なガイダンスを提供します。

## Instructions

### ステップ1: ブランチとgitコミット履歴の確認

以下のコマンドで現在の状態を確認：

```bash
git status
git log --oneline --graph origin/main..HEAD
```

確認事項：
- 現在のブランチ名
- mainブランチから何gitコミット進んでいるか
- 各gitコミットの内容と粒度

### ステップ2: gitコミット戦略の判断

以下の基準でgitコミット戦略を選択：

#### 戦略A: Squash（基本戦略）

以下の条件を満たす場合、既存のgitコミットにsquashします：

- ブランチに既にgitコミットが存在する
- 変更内容が既存のgitコミットと同じテーマ・機能に関連している
- gitコミットを分ける合理的な理由がない

**実行方法：**

```bash
git add -A
git commit --amend
```

gitコミットメッセージを適切に更新してください。

#### 戦略B: 新規gitコミット

以下の場合は新規gitコミットを作成：

- ブランチに初めてのgitコミット
- 既存のgitコミットとは異なる独立した変更
- gitコミットを分けることで履歴がより理解しやすくなる

**実行方法：**

```bash
git add -A
git commit
```

#### 戦略C: Interactive Rebase（gitコミット再構成）

以下の場合はブランチ全体のgitコミットを再構成：

- 複数の小さなgitコミットを論理的なまとまりに整理したい
- gitコミットの順序を変更したい
- 不要なgitコミットを削除したい
- gitコミット履歴を意味のある単位に再編成したい

**実行方法：**

```bash
git rebase -i origin/main
```

エディタで以下の操作を実行：
- `pick`: gitコミットをそのまま維持
- `squash`または`s`: 前のgitコミットと統合
- `reword`または`r`: gitコミットメッセージを変更
- 行の順序を変更してgitコミット順を変更

### ステップ3: gitコミットメッセージのガイドライン

gitコミットメッセージは以下の形式で記述：

```
<type>: <subject>

<body>

<footer>
```

**Type:**
- `feat`: 新機能
- `fix`: バグ修正
- `refactor`: リファクタリング
- `test`: テスト追加・修正
- `docs`: ドキュメント変更
- `chore`: ビルドプロセスやツールの変更

**Subject:**
- 50文字以内
- 命令形で記述（例: "add"ではなく"Add"）
- 末尾にピリオドを付けない

**Body（オプション）:**
- 変更の理由と背景を説明
- 何を変更したかではなく、なぜ変更したかを記述
- 72文字で折り返す

**Footer（オプション）:**
- Issue番号への参照（例: `Closes #123`）
- Breaking changesの記述

### ステップ4: git commit後の確認

git commit後、以下を確認：

```bash
git log -1 --stat
git status
```

- gitコミットが正しく作成されたか
- 意図したファイルがすべて含まれているか
- gitコミットメッセージが適切か

## 重要な注意事項

1. **mainブランチでは実行しない**: mainブランチで直接git commitしないでください
2. **コメントは残さない**: コード内の説明コメントは削除してください
3. **原子的なgitコミット**: 各gitコミットは独立して意味を持つようにしてください
4. **一貫性**: プロジェクトの既存のgitコミットスタイルに従ってください

## 戦略選択のフローチャート

```
ブランチにgitコミットがある？
  ├─ No → 新規gitコミット作成
  └─ Yes → 変更は既存のgitコミットと同じテーマ？
      ├─ Yes → Squash（git commit --amend）
      └─ No → gitコミットを分ける合理性がある？
          ├─ Yes → 新規gitコミット作成
          └─ 履歴を整理したい → Interactive Rebase
```
