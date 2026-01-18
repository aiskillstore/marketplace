---
name: skill-permissions
description: スキル権限分析、ワンタイム認証、スキル権限の分析、一括認証
---

# Skill Permissions

Claude Code のすべてのスキルが必要とする権限を自動分析し、ワンタイム認証コマンドを生成します。

## 危険な操作に関する警告

**このスキルは他のスキルファイルを変更できます。** 以下のコマンドは広範囲のファイル変更を引き起こす可能性があります：

| コマンド | リスクレベル | 説明 |
|---------|-------------|------|
| `/skill-permissions inject` | 高 | すべてのスキルの SKILL.md を一括変更 |
| `/skill-permissions allow-all` | 中 | settings.json を一括変更 |
| `/skill-permissions allow <name>` | 低 | settings.json のみを変更 |
| `/skill-permissions <name>` | 安全 | 読み取り専用分析、ファイル変更なし |

**推奨事項：**
- **明示的なコマンド**を優先（例：`/skill-permissions allow port-allocator`）
- 影響を理解していない限り `inject` や `allow-all` を避ける
- 一括操作の前に `/skill-permissions` を実行して分析結果を確認

## 使用方法

| コマンド | 説明 |
|---------|------|
| `/skill-permissions` | すべてのスキルを分析し権限サマリーを表示 |
| `/skill-permissions <skill-name>` | 特定スキルの権限要件を分析 |
| `/skill-permissions allow <skill-name>` | 特定スキルのワンタイム認証を実行 |
| `/skill-permissions allow-all` | すべてのスキルのワンタイム認証を実行 |
| `/skill-permissions inject` | すべてのスキルに allow コマンドを注入 |
| `/skill-permissions allow` | このスキルのワンタイム認証を実行 |

## 動作原理

### 1. 権限分析

スキルの SKILL.md ファイルをスキャンし、パターンを識別：

**Bash コマンドパターン：**
```
find * → Bash(find *)
ls * → Bash(ls *)
cat ~/.claude/* → Bash(cat ~/.claude/*)
lsof -i:3* → Bash(lsof -i:3*)
git * → Bash(git *)
```

**認識ルール：**
- コードブロック内の bash コマンド (```bash ... ```)
- インラインコマンド (`command`)
- 明示的に言及されたシステムコマンド

### 2. 権限ルール生成

識別されたコマンドを `permissions.allow` ルールに変換：

```json
{
  "permissions": {
    "allow": [
      "Bash(find * -name package.json *)",
      "Bash(ls -d *)",
      "Bash(cat ~/.claude/*)",
      "Bash(lsof -i:3*)"
    ]
  }
}
```

## 実行手順

### コマンド: `/skill-permissions`

すべてのスキルを分析し権限サマリーを表示：

1. **すべてのスキルをスキャン**
   ```bash
   find ~/.claude/skills -name "SKILL.md" -type f 2>/dev/null
   ```

2. **各スキルの権限を分析**
3. **分析結果を出力**

### コマンド: `/skill-permissions allow <skill-name>`

特定スキルのワンタイム認証を実行：

1. **スキルの権限要件を分析**
2. **既存の設定を読み取り**
3. **権限ルールをマージ**（重複排除、既存ルールを保持）
4. **設定ファイルに書き込み**
5. **認証結果を出力**

## ブロックされるコマンド

以下のコマンドパターンは**自動的にブロック**され、許可リストに追加されません：

### 危険なファイル操作
| コマンド | 理由 |
|---------|------|
| `rm *` | ファイル削除、データ損失の可能性 |
| `rm -rf *` | 再帰的強制削除、極めて危険 |
| `sudo *` | スーパーユーザー権限 |

### 危険なプロセス操作
| コマンド | 理由 |
|---------|------|
| `kill -9 *` | プロセスを強制終了 |
| `curl * \| bash` | リモートコード実行 |

### 危険な Git 操作
| コマンド | 理由 |
|---------|------|
| `git push --force *` | 強制プッシュ、リモートを上書きする可能性 |
| `git reset --hard *` | ハードリセット、コミットされていない変更を失う |

## 出力形式

### 分析結果（単一スキル）
```
スキル: port-allocator
場所: ~/.claude/skills/port-allocator

検出されたコマンド:
  - find ~/Codes -maxdepth 3 -name "package.json"
  - ls -d */
  - cat ~/.claude/port-registry.json

生成された権限ルール:
  - Bash(find * -maxdepth * -name package.json *)
  - Bash(ls -d *)
  - Bash(cat ~/.claude/*)

`/skill-permissions allow port-allocator` を実行して認証
```

### 認証成功
```
権限認証成功

スキル: port-allocator

追加された権限ルール:
  - Bash(find * -maxdepth * -name package.json *)
  - Bash(ls -d *)
  - Bash(cat ~/.claude/*)

設定ファイル: ~/.claude/settings.json

新しい権限は次のセッションで有効になります。すぐに適用するには /clear を実行
```

## 設定ファイル

- **権限設定**: `~/.claude/settings.json`
- **スキルディレクトリ**: `~/.claude/skills/`

## 初回使用

権限プロンプトが表示された場合、まず以下を実行：
```
/skill-permissions allow
```

### コマンド: `/skill-permissions allow`

このスキルのワンタイム認証を実行：

1. `~/.claude/settings.json` を読み取り
2. 以下の権限を `permissions.allow` にマージ：

```json
{
  "permissions": {
    "allow": [
      "Bash(find ~/.claude/skills *)",
      "Bash(cat ~/.claude/*)"
    ]
  }
}
```

3. 設定ファイルに書き込み（既存の権限を保持）
4. 認証結果を出力

## 注意事項

1. **保守的な分析** - 明示的に出現するコマンドのみを識別、過剰な認証を回避
2. **重複排除マージ** - 新しい権限は既存のものとマージ、重複なし
3. **削除なし** - 権限の追加のみ、ユーザーの既存の権限設定は削除しない
4. **ワイルドカード** - 変化するパラメータ部分にマッチするために `*` を使用
5. **セッション効果** - 権限更新は新しいセッションまたは /clear で有効になる
6. **明示的優先** - リスクを減らすためにバッチ操作よりも明示的なコマンドを推奨
