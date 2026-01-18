---
name: port-allocator
description: 開発サーバーポートの自動割り当てと管理、複数の Claude Code インスタンス間のポート競合を回避
---

# Port Allocator

`package.json` を含む実際のプロジェクトにのみポートを割り当てるスマートポートアロケーター。

## 使用方法

| コマンド | 説明 |
|---------|------|
| `/port-allocator` | 現在のプロジェクトのポートを割り当て/照会 |
| `/port-allocator list` | 割り当て済みの全ポートを一覧表示 |
| `/port-allocator scan` | コードディレクトリをスキャンし、新しいプロジェクトを発見してポートを割り当て |
| `/port-allocator config <path>` | メインコードディレクトリのパスを設定 |
| `/port-allocator add <ディレクトリパス>` | プロジェクトのポート割り当てを手動で追加 |
| `/port-allocator allow` | このスキルのコマンドに対する Claude Code の権限を設定 |

## 重要なルール

### 1. サービス再起動時は現在のプロジェクトのポートのみを操作

開発サーバーを再起動する際は、**現在のプロジェクトのポート範囲内のプロセスのみを終了**し、他のポートには絶対に影響を与えないこと：

```bash
# 正しい：現在のプロジェクトのポートのみを終了（例：3000-3009）
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:3001 | xargs kill -9 2>/dev/null

# 間違い：すべての node プロセスや他のポートを終了
pkill -f node  # 他のプロジェクトに影響します！
lsof -ti:3010 | xargs kill  # これは別のプロジェクトのポートです！
```

### 2. CLAUDE.md 更新時は上書きではなく追記

`~/.claude/CLAUDE.md` を更新する際は、**ユーザーの既存コンテンツを保持する必要があります**：

```bash
# 正しい：特定のセクションを確認して追記または更新
# 間違い：ファイル全体を直接上書き
```

## 実行手順

### コマンド: `/port-allocator allow`

このスキルで使用するコマンドを Claude Code が許可するように設定し、毎回の手動確認を回避：

1. `~/.claude/settings.json` を読み取り（存在する場合）
2. 以下のコマンドを `permissions.allow` 配列にマージ（既存の設定を保持）：

```json
{
  "permissions": {
    "allow": [
      "Bash(ls -d *)",
      "Bash(find * -maxdepth * -name package.json *)",
      "Bash(cat ~/.claude/*)",
      "Bash(dirname *)",
      "Bash(lsof -i:3*)",
      "Bash(lsof -ti:3*)"
    ]
  }
}
```

3. 更新された settings.json を書き込み
4. 追加された権限リストを出力

**出力形式：**
```
Claude Code 権限を設定しました

追加された許可コマンドパターン：
  - Bash(ls -d *)
  - Bash(find * -maxdepth * -name package.json *)
  - Bash(cat ~/.claude/*)
  - Bash(lsof -i:3*)
  - Bash(lsof -ti:3*)

設定ファイル: ~/.claude/settings.json
```

### コマンド: `/port-allocator config <path>`

ユーザーのメインコードディレクトリを設定：

1. **パスの存在を確認**（必須！見つからない場合はエラーで終了）
2. `~/.claude/port-registry.json` の `code_root` フィールドを更新
3. 確認メッセージを出力

### 初回実行：自動検出

初回実行時（`~/.claude/port-registry.json` が存在しないか `code_root` がない場合）、コードディレクトリを自動検出：

```bash
# 一般的なコードディレクトリをチェック
for dir in ~/Codes ~/Code ~/Projects ~/Dev ~/Development ~/repos; do
  if [ -d "$dir" ]; then
    CODE_ROOT="$dir"
    break
  fi
done

# いずれも存在しない場合、デフォルトで ~/Codes を使用
CODE_ROOT="${CODE_ROOT:-~/Codes}"
```

**自動検出出力：**
```
初回実行、コードディレクトリを検出中...

コードディレクトリを検出: ~/Codes

ポートレジストリを初期化: ~/.claude/port-registry.json

変更するには:
   /port-allocator config ~/your/code/path
```

**ディレクトリが見つからない場合：**
```
コードディレクトリを自動検出できませんでした

手動で設定してください:
   /port-allocator config ~/your/code/path

一般的な場所:
   ~/Codes, ~/Code, ~/Projects, ~/Dev
```

### コマンド: `/port-allocator scan`

コードディレクトリをスキャンし、プロジェクトを自動検出して登録：

1. `~/.claude/port-registry.json` から `code_root` を読み取り
   - 設定が存在しない場合、先に自動検出を実行
   - `code_root` ディレクトリが存在しない場合、ユーザーに設定を促す
2. `package.json` を含むすべてのディレクトリを検索（package.json の場所を正確に）：

```bash
# すべての package.json を検索、ビルド成果物ディレクトリを除外
find <code_root> -maxdepth 3 -name "package.json" -type f \
  -not -path "*/.next/*" \
  -not -path "*/node_modules/*" \
  -not -path "*/dist/*" \
  -not -path "*/build/*" | while read pkg; do
  dirname "$pkg"
done
```

3. **重要**：パスは `package.json` を含むディレクトリを正確に指定する必要があります
   - 正しい：`~/Codes/chekusu/landing`
   - 間違い：`~/Codes/chekusu`（package.json がサブディレクトリにある場合）

4. 検出された各プロジェクトディレクトリに対して：
   - 既に登録されているか確認
   - 未登録の場合、次に利用可能なポート範囲を割り当て
5. 設定ファイルを更新（**追記モード**、ユーザーコンテンツを上書きしない）
6. スキャン結果のサマリーを出力

### コマンド: `/port-allocator`（デフォルト）

現在のプロジェクトのポートを割り当て/照会：

1. 現在の作業ディレクトリを取得
2. 設定を読み取り `code_root` と割り当て済みポートを取得
3. 現在のディレクトリを対応するプロジェクトにマッチング
4. `package.json` がない場合、ポートが不要なプロジェクトであることを示す
5. 存在する場合、ポートが既に割り当てられているか確認、未割り当てなら自動割り当て
6. ポート情報を出力

### コマンド: `/port-allocator list`

割り当て済みの全ポートを一覧表示（読み取り専用操作）。

## 出力形式

### ポート情報
```
プロジェクトディレクトリ: ~/Codes/chekusu/landing
package.json: 検出済み
ポート範囲: 3000-3009
   - メインアプリ: 3000
   - API: 3001
   - その他のサービス: 3002-3009

警告：サービス再起動時は 3000-3009 ポートのみを操作してください！
```

### スキャン結果
```
スキャン完了: ~/Codes

登録済みプロジェクト (N件):
   - chekusu/landing: 3000-3009
   - saifuri: 3010-3019

新しく発見されたプロジェクト (M件):
   - new-project: 3090-3099 (新規割り当て)

スキップ (K件):
   - .next, node_modules (ビルド成果物)
   - research-folder (package.json なし)
```

## ポート割り当てルール

- 各プロジェクトに **10 個の連続ポート** を割り当て
- 開始ポート：3000
- 間隔：10
- `x0`：メインアプリケーション（例：3000, 3010, 3020）
- `x1`：API サービス（例：3001, 3011, 3021）
- `x2-x9`：その他のサービス（データベース、キャッシュなど）

## 設定ファイル

- **ポートレジストリ**: `~/.claude/port-registry.json`
- **グローバル説明**: `~/.claude/CLAUDE.md`（追記モードで更新）
- **Claude Code 設定**: `~/.claude/settings.json`（allowedCommands を保存）
- **スキップパターン**: `.next`, `node_modules`, `dist`, `build`

## 注意事項

1. **プロジェクトポートのみを操作** - サービス再起動時に他のプロジェクトに影響を与えない
2. **上書きではなく追記** - 設定ファイル更新時にユーザーの既存コンテンツを保持
3. **正確なパス** - package.json を含む実際のディレクトリを指定
4. **ビルド成果物をスキップ** - .next, node_modules などにはポートを割り当てない
5. **初回使用** - まず `/port-allocator allow` を実行して権限を設定することを推奨
