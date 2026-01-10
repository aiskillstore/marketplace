---
name: create-git-worktree
description: git worktree を利用した分離作業環境を自動構築します。デフォルトブランチから最新コードを取得し、.git-worktrees/ ディレクトリに新規worktreeを作成、.env・npm依存関係を自動セットアップします。ブランチ名の '/' は自動的に '-' に変換されます。既存worktreeは再利用されます。
---

# Create Git Worktree and Setup Environment

## Instructions

以下のコマンドを実行して、git worktreeを作成し、環境のセットアップを行います。
引数にはgit worktree化するブランチ名を指定してください。

```
bash scripts/create-worktree.sh [ブランチ名]
```
