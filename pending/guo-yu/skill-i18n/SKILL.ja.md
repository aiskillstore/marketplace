---
name: skill-i18n
description: SKILL.md と README.md を複数言語に翻訳し、スキルの国際共有を容易に
---

# Skill i18n

スキルドキュメントファイル（SKILL.md、README.md）を複数言語に翻訳し、国際ユーザーとのスキル共有を容易にします。

## 使用方法

| コマンド | 説明 |
|----------|------|
| `/skill-i18n` | 現在のスキルディレクトリのファイルを翻訳 |
| `/skill-i18n <skill-name>` | 指定したスキルのファイルを翻訳 |
| `/skill-i18n config` | デフォルト言語とファイルタイプを設定 |
| `/skill-i18n --lang zh-CN,ja` | 指定した言語に翻訳（統合用） |
| `/skill-i18n --files SKILL.md,README.md` | 指定したファイルを翻訳 |

## サポートされている言語

| 言語 | コード | 出力ファイル |
|------|--------|--------------|
| 简体中文 | `zh-CN` | `SKILL.zh-CN.md` |
| 日本語 | `ja` | `SKILL.ja.md` |
| 한국어 | `ko` | `SKILL.ko.md` |
| Español | `es` | `SKILL.es.md` |
| カスタム | ユーザー定義 | `SKILL.<code>.md` |

## 設定

すべての設定は `~/.claude/skill-i18n-config.json` に保存されます：

```json
{
  "default_languages": ["zh-CN", "ja"],
  "default_files": ["SKILL.md"],
  "skills_config": {
    "port-allocator": {
      "languages": ["zh-CN", "ja", "ko"],
      "files": ["SKILL.md", "README.md"]
    }
  }
}
```

**設定フィールド：**

| フィールド | 説明 | デフォルト |
|------------|------|------------|
| `default_languages` | デフォルトで翻訳する言語 | `["zh-CN", "ja"]` |
| `default_files` | デフォルトで翻訳するファイル | `["SKILL.md"]` |
| `skills_config` | スキルごとの設定 | `{}` |

## 実行手順

### コマンド: `/skill-i18n`

現在のスキルディレクトリのファイルを翻訳：

1. **現在のディレクトリを検出**
   ```bash
   # 現在のディレクトリに SKILL.md が含まれているか確認
   if [ ! -f SKILL.md ]; then
     echo "Error: SKILL.md not found in current directory"
     exit 1
   fi
   ```

2. **設定を読み込み**
   ```bash
   # 設定ファイルを読み込み
   CONFIG=$(cat ~/.claude/skill-i18n-config.json 2>/dev/null || echo '{}')

   # ディレクトリからスキル名を取得
   SKILL_NAME=$(basename "$(pwd)")

   # スキル固有の設定を確認
   SKILL_CONFIG=$(echo "$CONFIG" | jq -r ".skills_config[\"$SKILL_NAME\"] // null")
   ```

3. **初回実行時の選択（設定がない場合）**

   このスキルの設定が存在しない場合、TUI選択画面を表示：

   ```json
   {
     "questions": [
       {
         "question": "どの言語を生成しますか？",
         "header": "言語",
         "multiSelect": true,
         "options": [
           { "label": "简体中文 (zh-CN)", "description": "簡体字中国語" },
           { "label": "日本語 (ja)", "description": "日本語" },
           { "label": "한국어 (ko)", "description": "韓国語" },
           { "label": "Español (es)", "description": "スペイン語" }
         ]
       },
       {
         "question": "どのファイルを翻訳しますか？",
         "header": "ファイル",
         "multiSelect": true,
         "options": [
           { "label": "SKILL.md", "description": "スキルドキュメント（推奨）" },
           { "label": "README.md", "description": "リポジトリ説明ファイル" }
         ]
       }
     ]
   }
   ```

4. **設定を保存**
   ```bash
   # 将来の実行のために選択を設定に保存
   jq --arg skill "$SKILL_NAME" \
      --argjson langs '["zh-CN", "ja"]' \
      --argjson files '["SKILL.md"]' \
      '.skills_config[$skill] = {"languages": $langs, "files": $files}' \
      ~/.claude/skill-i18n-config.json > tmp.json && mv tmp.json ~/.claude/skill-i18n-config.json
   ```

5. **翻訳を実行**
   - 選択した各ファイルと言語の翻訳を生成
   - 下記の「翻訳ルール」セクションを参照

### コマンド: `/skill-i18n <skill-name>`

指定したスキルのファイルを翻訳：

1. **スキルの場所を検索**
   ```bash
   # 一般的な場所で検索
   SKILL_PATH=""

   # ~/.claude/skills/ を確認
   if [ -d ~/.claude/skills/"$SKILL_NAME" ]; then
     SKILL_PATH=~/.claude/skills/"$SKILL_NAME"
   fi

   # コードリポジトリを確認（設定されている場合）
   if [ -z "$SKILL_PATH" ] && [ -d ~/Codes/skills/"$SKILL_NAME" ]; then
     SKILL_PATH=~/Codes/skills/"$SKILL_NAME"
   fi

   if [ -z "$SKILL_PATH" ]; then
     echo "Error: Skill '$SKILL_NAME' not found"
     exit 1
   fi
   ```

2. **翻訳を実行**（デフォルトコマンドと同じ）

### コマンド: `/skill-i18n config`

デフォルト設定を構成：

1. **現在の設定を表示**
   ```bash
   echo "Current configuration:"
   cat ~/.claude/skill-i18n-config.json | jq .
   ```

2. **AskUserQuestion によるインタラクティブ設定**
   ```json
   {
     "questions": [
       {
         "question": "新しいスキルのデフォルト言語を選択：",
         "header": "デフォルト",
         "multiSelect": true,
         "options": [
           { "label": "简体中文 (zh-CN)", "description": "簡体字中国語" },
           { "label": "日本語 (ja)", "description": "日本語" },
           { "label": "한국어 (ko)", "description": "韓国語" },
           { "label": "Español (es)", "description": "スペイン語" }
         ]
       }
     ]
   }
   ```

3. **設定ファイルを更新**

### コマンドラインフラグ

他のスキルとの統合用（例：share-skill）：

| フラグ | 説明 | 例 |
|--------|------|-----|
| `--lang <codes>` | カンマ区切りの言語コード | `--lang zh-CN,ja,ko` |
| `--files <names>` | カンマ区切りのファイル名 | `--files SKILL.md,README.md` |
| `--skill <name>` | 対象スキル名 | `--skill port-allocator` |
| `--no-prompt` | TUIをスキップし、フラグ/設定を直接使用 | 自動化ワークフロー用 |
| `--overwrite` | 既存の翻訳を上書き | 確認をスキップ |

**優先順位：**
1. コマンドラインフラグ（最高優先度）
2. `skills_config` のスキル固有設定
3. グローバルの `default_languages` と `default_files`
4. インタラクティブTUI選択（設定がない場合）

**統合例：**
```bash
# share-skill が内部で skill-i18n を呼び出し
/skill-i18n --lang zh-CN,ja --files SKILL.md --skill port-allocator --no-prompt
```

## 翻訳ルール

### 変更しない要素

以下の要素は翻訳してはいけません：

- **コードブロック**（```bash、```json など）
- **ファイルパス**（`~/.claude/settings.json`、`~/Codes/skills/`）
- **コマンド名**（`/port-allocator`、`/skill-i18n`、`git push`）
- **技術的識別子**（変数名、JSONキー）
- **URLとリンク**

### 自然な翻訳

- 対象言語に合わせて文構造を調整
- 適切な敬語レベルを使用：
  - 日本語：丁寧体（です/ます）
  - 中国語：標準書面語
  - 韓国語：丁寧体（합니다/습니다）
  - スペイン語：正式なusted形式
- 必要に応じて例をローカライズ

### Frontmatter の処理

```yaml
---
name: port-allocator          # 変更しない（識別子）
description: この部分を翻訳    # 対象言語に翻訳
---
```

### スタイルの適応

言語によって異なる視覚スタイルを使用する場合があります：

| 言語 | 絵文字の使用 | 例 |
|------|-------------|-----|
| 中国語 (zh-CN) | よく使う | ✅ 正确 / ❌ 错误 |
| 日本語 (ja) | 控えめ | 正しい / 間違い |
| 韓国語 (ko) | 適度 | ✅ 올바름 / ❌ 잘못됨 |
| スペイン語 (es) | 控えめ | Correcto / Incorrecto |

プロジェクトに既存の翻訳パターンがあれば、それに従ってください。

## 出力形式

### 翻訳成功

```
Translation complete

Skill: port-allocator
Source: SKILL.md

Generated:
  - SKILL.zh-CN.md (简体中文)
  - SKILL.ja.md (日本語)

Config saved for: port-allocator
Next run will auto-translate to: zh-CN, ja
```

### 既存ファイルを検出

```
Existing translations detected:
  - SKILL.zh-CN.md (modified 2 days ago)
  - SKILL.ja.md (modified 2 days ago)

Options:
  [ ] Overwrite all
  [ ] Skip existing
  [ ] Select individually
```

### 設定を保存

```
Configuration updated

Default languages: zh-CN, ja
Default files: SKILL.md

Skill-specific config:
  port-allocator: zh-CN, ja, ko (SKILL.md, README.md)
  share-skill: zh-CN, ja (SKILL.md)
```

## share-skill との統合

skill-i18n は share-skill と統合してドキュメント生成に使用されます：

```bash
# share-skill docs で i18n を有効化
/share-skill docs --i18n

# 内部で呼び出し：
/skill-i18n --lang <configured-langs> --files SKILL.md --no-prompt
```

share-skill が `--i18n` フラグを検出した場合：
1. skill-i18n が利用可能か確認
2. 言語設定を読み込み
3. skill-i18n を呼び出して翻訳を生成
4. 翻訳ファイルをドキュメントサイトに含める

## 注意事項

1. **ソースファイルの安全性** - ソースの `SKILL.md` ファイルを上書きすることはありません
2. **初回実行時のプロンプト** - 初回の翻訳は言語選択が必要です
3. **スキルごとの設定** - 異なるスキルは異なる言語設定を持てます
4. **増分更新** - ソースファイルが翻訳より新しい場合のみ翻訳
5. **統合しやすい** - コマンドラインフラグにより他のスキルから skill-i18n を呼び出し可能
