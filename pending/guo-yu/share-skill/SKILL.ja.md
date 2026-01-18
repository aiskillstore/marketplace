---
name: share-skill
description: スキルの自動共有、ローカルスキルのリポジトリ移行、スキルのオープンソース化、スキルバージョン管理、git リモート設定
---

# Share Skill

ユーザーがローカルで一時的に作成したスキルをシンボリックリンクでプロジェクトリポジトリに移行し、Git でバージョン管理を初期化します。

## 使用方法

| コマンド | 説明 |
|---------|------|
| `/share-skill <skill-name>` | 指定スキルを {skills_path} に移行し git を初期化 |
| `/share-skill <skill-name> --remote <url>` | 移行してリモート URL を設定 |
| `/share-skill list` | 移行可能なすべてのローカルスキルを一覧表示 |
| `/share-skill config` | コードディレクトリとカスタムドメインを設定 |
| `/share-skill remote <alias> <endpoint>` | Git リモートエイリアスを設定 |
| `/share-skill remote list` | 設定済みリモートエイリアスを一覧表示 |
| `/share-skill docs` | リポジトリのドキュメントサイトを生成 |
| `/share-skill docs --style <name>` | 指定デザインスタイルでドキュメントを生成 |
| `/share-skill docs --skill <ui-skill>` | 指定 UI スキルでドキュメントをデザイン |
| `/share-skill docs config` | デフォルトのデザインスタイルまたは UI スキルを設定 |
| `/share-skill allow` | このスキルの権限をワンタイム認証 |
| 自然言語 | 例：「port-allocator をオープンソース化して github に push して」 |

## 設定ファイル

リモートエイリアスとドキュメントデザイン設定は `~/.claude/share-skill-config.json` に保存：

```json
{
  "code_root": "~/Codes",
  "skills_repo": "skills",
  "github_username": "guo-yu",
  "remotes": {
    "github": "git@github.com:guo-yu/skills",
    "gitlab": "git@gitlab.com:guo-yu/skills"
  },
  "default_remote": "github",
  "auto_detected": true,
  "docs": {
    "style": "botanical",
    "custom_skill": null,
    "custom_domain": "skill.guoyu.me"
  }
}
```

### 設定項目

| 項目 | 説明 | デフォルト |
|------|------|------------|
| `code_root` | コードリポジトリのルートディレクトリ | `~/Codes` |
| `skills_repo` | スキルリポジトリのフォルダ名 | `skills` |
| `github_username` | GitHub ユーザー名 | 自動検出 |
| `remotes` | Git リモートエイリアスのマッピング | - |
| `default_remote` | デフォルトのリモート | `github` |
| `docs.style` | ドキュメントのデザインスタイル | `botanical` |
| `docs.custom_skill` | カスタム UI スキル名 | `null` |
| `docs.custom_domain` | カスタムドメイン（GitHub Pages 使用時は null） | `null` |

### パス変数

設定はパス変数を使用してリポジトリパスを動的に参照します：

- `{code_root}` → `code_root` 設定値（例：`~/Codes`）
- `{skills_repo}` → `skills_repo` 設定値（例：`skills`）
- `{skills_path}` → `{code_root}/{skills_repo}`（例：`~/Codes/skills`）
- `{username}` → `github_username` 設定値

### 初回実行時の自動検出

share-skill の初回実行時、ユーザーの Git グローバル設定からユーザー名を自動読み取り：

```bash
# GitHub ユーザー名を読み取り
git config --global user.name
# または GitHub URL パターンから抽出
git config --global --get-regexp "url.*github.com" | head -1
```

**自動検出ロジック：**

1. **設定ファイルの存在確認**
   ```bash
   if [ ! -f ~/.claude/share-skill-config.json ]; then
     # 初回実行、自動検出を実行
   fi
   ```

2. **コードディレクトリの自動検出**
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

3. **Git グローバル設定を読み取り**
   ```bash
   # ユーザー名の取得を試行
   USERNAME=$(git config --global user.name)

   # ユーザー名にスペースが含まれる場合、GitHub メールから抽出を試行
   if [[ "$USERNAME" == *" "* ]]; then
     EMAIL=$(git config --global user.email)
     # xxx@users.noreply.github.com から抽出
     USERNAME=$(echo "$EMAIL" | grep -oP '^\d+-?\K[^@]+(?=@users\.noreply\.github\.com)')
   fi

   # まだ判定できない場合、リモート URL から抽出を試行
   if [ -z "$USERNAME" ]; then
     USERNAME=$(git config --global --get-regexp "url.*github.com" | grep -oP 'github\.com[:/]\K[^/]+' | head -1)
   fi
   ```

4. **デフォルト設定を生成**
   ```json
   {
     "code_root": "~/Codes",
     "skills_repo": "skills",
     "github_username": "<検出されたユーザー名>",
     "remotes": {
       "github": "git@github.com:<検出されたユーザー名>/skills"
     },
     "default_remote": "github",
     "auto_detected": true
   }
   ```

5. **検出結果を出力**
   ```
   初回実行、Git 設定を自動検出中...

   GitHub ユーザー名を検出: guo-yu
   コードディレクトリを検出: ~/Codes

   デフォルトリモートを自動設定:
     github → git@github.com:guo-yu/skills

   スキルパス: ~/Codes/skills

   設定ファイル: ~/.claude/share-skill-config.json

   変更するには:
      /share-skill config
      /share-skill remote github git@github.com:他のユーザー名/skills
   ```

### 検出失敗時の処理

ユーザー名を自動検出できない場合、手動設定を促す：

```
Git ユーザー名を自動検出できませんでした

リモートアドレスを手動で設定してください:
  /share-skill remote github git@github.com:あなたのユーザー名/skills

または移行時に指定:
  /share-skill <skill-name> --remote git@github.com:あなたのユーザー名/skills.git
```

### `/share-skill config` コマンド

コードディレクトリとカスタムドメインを対話形式で設定：

**実行ステップ：**

1. **現在の設定を読み込み**
   ```bash
   cat ~/.claude/share-skill-config.json
   ```

2. **TUI インターフェースで設定項目を表示**
   ```
   ⚙️ Share Skill 設定

   コードディレクトリ:
     現在: ~/Codes
     [ ] ~/Codes
     [ ] ~/Code
     [ ] ~/Projects
     [ ] ~/Dev
     [ ] その他...

   スキルリポジトリ名:
     現在: skills
     [skills                    ]

   カスタムドメイン:
     現在: なし（GitHub Pages を使用）
     [ ] GitHub Pages（{username}.github.io/{repo}）
     [ ] カスタムドメイン...
   ```

3. **設定を保存し確認を出力**
   ```
   ✅ 設定を更新しました

   コードディレクトリ: ~/Codes
   スキルリポジトリ: skills
   スキルパス: ~/Codes/skills
   カスタムドメイン: skill.guoyu.me

   設定ファイル: ~/.claude/share-skill-config.json
   ```

## 自然言語での呼び出し

ユーザーが自然言語で呼び出す場合、インテリジェントな分析が必要：

### 1. ユーザーが指すスキルの識別

ユーザーが言う可能性：
- 「xxx スキルをオープンソース化して」→ スキル名 `xxx` を抽出
- 「さっき作ったスキルを共有して」→ 最近更新されたスキルを検索
- 「このスキルをリポジトリに移行して」→ 現在のコンテキストから判断
- 「port-allocator をオープンソース化」→ 名前を直接使用

### 2. リモートアドレスの識別

**デフォルト動作：** 自動検出されたユーザー名 + デフォルトリポジトリ名 `skills`

ユーザーが言う可能性：
- 「xxx をオープンソース化して」→ デフォルト使用: `git@github.com:<ユーザー名>/skills/<skill-name>.git`
- 「github に push して」→ デフォルト github 設定を使用
- 「git@github.com:other-user/repo.git に push して」→ **完全なアドレスを明示的に指定する必要あり**
- 「my-tools リポジトリにオープンソース化」→ **リポジトリ名を明示的に指定する必要あり**

**重要なルール：リモートパスの変更には明示的な指定が必要**

デフォルト以外のリモートパスを使用する場合、以下の方法で**明示的に指定**する必要があります：

1. **コマンドラインでの明示的指定**
   ```bash
   /share-skill <skill-name> --remote git@github.com:other-user/other-repo.git
   ```

2. **自然言語での明示的パス**
   ```
   OK: 「port-allocator を git@github.com:my-org/tools.git に push して」
   OK: 「gitlab にオープンソース化、アドレスは git@gitlab.com:team/shared-skills.git」

   NG: 「他の場所に push して」（不明確、具体的なアドレスを確認）
   NG: 「別のリポジトリに変更」（不明確、具体的なアドレスを確認）
   ```

**アドレス解決ルール：**
```
「xxx をオープンソース化して」
  → デフォルト設定を使用: git@github.com:<自動検出ユーザー>/skills
  → 最終アドレス: git@github.com:<ユーザー>/skills/<skill-name>.git

「git@github.com:other-user/repo.git に push」
  → 完全なアドレスを検出、直接使用

「gitlab にオープンソース化」（gitlab 未設定）
  → プロンプト: 完全な GitLab アドレスを指定してください
```

### 3. スキル位置の自動検索

スキルは以下の場所に存在する可能性があり、優先度順に検索：

```bash
# 1. 標準 skills ディレクトリ
~/.claude/skills/<skill-name>/SKILL.md

# 2. ユーザーカスタム skills ディレクトリ
~/.claude/skills/*/<skill-name>/SKILL.md

# 3. 独立スキルファイル
~/.claude/skills/<skill-name>.md

# 4. プロジェクトレベル skills（現在の作業ディレクトリ）
.claude/skills/<skill-name>/SKILL.md
```

**検索コマンド：**
```bash
# ~/.claude 下の SKILL.md を含むディレクトリを検索
find ~/.claude -name "SKILL.md" -type f 2>/dev/null | while read f; do
  dir=$(dirname "$f")
  name=$(basename "$dir")
  echo "$name: $dir"
done

# または特定名を検索
find ~/.claude -type d -name "<skill-name>" 2>/dev/null
```

### 4. 確認後の操作

スキルを見つけた後：
1. 見つかった場所を表示し、ユーザーに確認を求める
2. 複数の一致がある場合、選択肢をリスト表示
3. 確認後に移行を実行
4. **ユーザーがリモートを指定しなかった場合、移行完了後に設定するか確認**

## 実行手順

### コマンド: `/share-skill remote <alias> <endpoint>`

Git リモートエイリアスを設定：

1. **既存設定を読み取り**
   ```bash
   cat ~/.claude/share-skill-config.json 2>/dev/null || echo '{"remotes":{}}'
   ```

2. **設定を更新**
   ```json
   {
     "remotes": {
       "<alias>": "<endpoint>"
     }
   }
   ```

3. **設定ファイルに書き込み**（既存設定を保持）

4. **確認を出力**
   ```
   リモートエイリアスを設定しました

   エイリアス: github
   アドレス: git@github.com:guo-yu/skills

   使用方法:
     /share-skill <skill-name> --remote github
     または: 「xxx を github にオープンソース化して」
   ```

### コマンド: `/share-skill remote list`

設定済みリモートエイリアスを一覧表示：

```bash
cat ~/.claude/share-skill-config.json | jq '.remotes'
```

**出力形式：**
```
設定済みリモートエイリアス:

  github  → git@github.com:guo-yu/skills
  gitlab  → git@gitlab.com:guo-yu/skills
  gitee   → git@gitee.com:guo-yu/skills

デフォルト: github
```

### コマンド: `/share-skill <skill-name> [--remote <url|alias>]`

指定スキルを `~/.claude/` ディレクトリから `{skills_path}/` に移行：

1. **スキル位置を検索**
   ```bash
   # まず標準位置を確認
   if [ -d ~/.claude/skills/<skill-name> ]; then
     SKILL_PATH=~/.claude/skills/<skill-name>
   else
     # 再帰検索
     SKILL_PATH=$(find ~/.claude -type d -name "<skill-name>" 2>/dev/null | head -1)
   fi
   ```
   - 見つからない場合、エラーで終了
   - すでにシンボリックリンクの場合、移行済みを通知しリンク先を表示
   - 複数見つかった場合、ユーザーに選択を促す

2. **ターゲットディレクトリを確認**
   ```bash
   ls {skills_path}/<skill-name> 2>/dev/null
   ```
   - ターゲットが存在する場合、エラーで終了（上書き防止）

3. **移行を実行**
   ```bash
   # ターゲットディレクトリを作成（存在しない場合）
   mkdir -p {skills_path}

   # スキルをコードディレクトリに移動
   mv ~/.claude/skills/<skill-name> {skills_path}/

   # シンボリックリンクを作成
   ln -s {skills_path}/<skill-name> ~/.claude/skills/<skill-name>
   ```

4. **.gitignore を作成**
   ```bash
   cat > {skills_path}/<skill-name>/.gitignore << 'EOF'
   # OS
   .DS_Store
   Thumbs.db

   # Editor
   .vscode/
   .idea/
   *.swp
   *.swo

   # Logs
   *.log

   # Temp
   tmp/
   temp/
   EOF
   ```

5. **Git を初期化**
   ```bash
   cd {skills_path}/<skill-name>
   git init
   git add .
   git commit -m "Initial commit: <skill-name> skill"
   ```

6. **リモートを設定（指定された場合）**

   ユーザーが `--remote` を指定した場合：
   ```bash
   # エイリアスの場合、完全なアドレスに解決
   if [ "<remote>" がエイリアス ]; then
     ENDPOINT=$(設定からエイリアスのエンドポイントを読み取り)
     REMOTE_URL="${ENDPOINT}/<skill-name>.git"
   else
     REMOTE_URL="<remote>"
   fi

   cd {skills_path}/<skill-name>
   git remote add origin "$REMOTE_URL"
   git push -u origin master
   ```

7. **リモート未指定時の確認**

   ユーザーがリモートを指定しなかった場合、移行後に AskUserQuestion で確認：
   ```
   Git リモートアドレスを設定しますか？

   選択肢:
   - github を使用 (git@github.com:guo-yu/skills/<skill-name>.git)
   - gitlab を使用 (git@gitlab.com:guo-yu/skills/<skill-name>.git)
   - カスタムアドレスを入力
   - 今はスキップ
   ```

### コマンド: `/share-skill list`

移行可能なすべてのローカルスキルを一覧表示（シンボリックリンクを除く）：

```bash
# ~/.claude 下の SKILL.md を含むすべてのディレクトリを検索
echo "発見されたスキル:"
find ~/.claude -name "SKILL.md" -type f 2>/dev/null | while read f; do
  dir=$(dirname "$f")
  name=$(basename "$dir")
  if [ -L "$dir" ]; then
    target=$(readlink "$dir")
    echo "  $name -> $target (移行済み)"
  else
    echo "  $name: $dir (移行可能)"
  fi
done
```

## 出力形式

### 移行成功（リモートあり）
```
スキル移行成功

スキル: <skill-name>
新しい場所: {skills_path}/<skill-name>
シンボリックリンク: ~/.claude/skills/<skill-name> -> {skills_path}/<skill-name>
Git: 初期化とコミット完了
リモート: git@github.com:guo-yu/skills/<skill-name>.git
リモートにプッシュ済み

リポジトリ URL: https://github.com/guo-yu/skills
```

### 移行成功（リモートなし）
```
スキル移行成功

スキル: <skill-name>
新しい場所: {skills_path}/<skill-name>
シンボリックリンク: ~/.claude/skills/<skill-name> -> {skills_path}/<skill-name>
Git: 初期化とコミット完了

リモートアドレスを設定しますか？
```

### 移行済み
```
スキルはすでに移行済みです

<skill-name> はすでにシンボリックリンクです：
  ~/.claude/skills/<skill-name> -> {skills_path}/<skill-name>
```

### リスト
```
移行可能なローカルスキル (N件):
  - art-master
  - design-master
  - prompt-generator

移行済みスキル (M件):
  - port-allocator -> {skills_path}/port-allocator
  - share-skill -> {skills_path}/share-skill
```

## ディレクトリ構造

### ハイブリッド Git 管理モード

share-skill は2つの Git 管理モードをサポート：

| モード | トリガー | Git 構造 | リモート |
|--------|---------|---------|---------|
| **Monorepo** | デフォルトエンドポイント | 親リポジトリ管理 | `guo-yu/skills` |
| **独立リポジトリ** | カスタムエンドポイント | 独立 .git | ユーザー指定 |

### Monorepo モード（デフォルト）

デフォルトエンドポイント使用時、すべてのスキルは親リポジトリ `{skills_path}/.git` で管理：

```
{skills_path}/
├── .git/                      # 親リポジトリ → guo-yu/skills
├── .gitignore
├── README.md
├── port-allocator/            # 独立 .git なし、親リポジトリで管理
│   ├── .gitignore
│   └── SKILL.md
├── share-skill/
│   ├── .gitignore
│   └── SKILL.md
└── skill-permissions/
    ├── .gitignore
    └── SKILL.md
```

**操作方法：**
```bash
# 新しいスキル追加後
cd {skills_path}
git add <new-skill>/
git commit -m "Add <new-skill>"
git push
```

### 独立リポジトリモード（カスタムエンドポイント）

ユーザーがカスタムエンドポイントを指定した場合、そのスキルは独立した .git を持つ：

```
{skills_path}/
├── .git/                      # 親リポジトリ
├── .gitignore                 # 含む: /custom-skill/
├── custom-skill/              # 独立リポジトリ → ユーザー指定のアドレス
│   ├── .git/
│   └── SKILL.md
└── port-allocator/            # 親リポジトリで管理
```

**親リポジトリの .gitignore 自動更新：**
```gitignore
# Skills with custom endpoints
/custom-skill/
```

### シンボリックリンク

モードに関係なく、`~/.claude/skills/` ではシンボリックリンクを使用：

```
~/.claude/skills/
├── port-allocator -> {skills_path}/port-allocator
├── share-skill -> {skills_path}/share-skill
└── skill-permissions -> {skills_path}/skill-permissions
```

## 初回使用

権限プロンプトが表示された場合、まず以下を実行：
```
/share-skill allow
```

### コマンド: `/share-skill allow`

ワンタイム認証を実行し、このスキルに必要な権限を Claude Code 設定に追加：

1. `~/.claude/settings.json` を読み取り
2. 以下の権限を `permissions.allow` にマージ：

```json
{
  "permissions": {
    "allow": [
      "Bash(cat ~/.claude/*)",
      "Bash(find ~/.claude *)",
      "Bash(ls {skills_path}/*)",
      "Bash(mkdir -p {skills_path}*)",
      "Bash(mv ~/.claude/skills/* *)",
      "Bash(ln -s {skills_path}/* *)",
      "Bash(git *)",
      "Bash(dirname *)",
      "Bash(basename *)",
      "Bash(readlink *)"
    ]
  }
}
```

3. 設定ファイルに書き込み（既存の権限を保持）
4. 認証結果を出力

**出力形式：**
```
Claude Code 権限を設定しました

追加された許可コマンドパターン：
  - Bash(cat ~/.claude/*)
  - Bash(find ~/.claude *)
  - Bash(ls {skills_path}/*)
  - Bash(mkdir -p {skills_path}*)
  - Bash(mv ~/.claude/skills/* *)
  - Bash(ln -s {skills_path}/* *)
  - Bash(git *)
  - Bash(dirname *)
  - Bash(basename *)
  - Bash(readlink *)

設定ファイル: ~/.claude/settings.json
```

## 注意事項

1. **上書きしない** - ターゲットディレクトリが存在する場合、上書きではなくエラー
2. **互換性を維持** - シンボリックリンクにより Claude Code は引き続きスキルを正常に読み取り可能
3. **Git 追跡** - git を自動初期化し初期コミットを作成
4. **エイリアス優先** - エイリアス使用時、スキル名を自動的にリポジトリ名として追加
5. **リモートについて確認** - リモート未指定時、移行後にユーザーに積極的に確認
6. **初回認証** - まず `/share-skill allow` を実行して権限を設定することを推奨

---

## ドキュメントサイト生成

share-skill はスキルの使用説明を紹介するエレガントなドキュメントサイトの自動生成をサポート。

### コマンド: `/share-skill docs`

skills リポジトリ用の GitHub Pages ドキュメントサイトを生成。

**パラメータ：**
- `--style <name>`: プリセットデザインスタイルを使用（デフォルト: `botanical`）
- `--skill <ui-skill>`: 指定 UI スキルでデザイン
- `--domain <domain>`: カスタムドメインを設定
- `--i18n`: SKILL.md と README ファイルの多言語選択を有効化

### i18n 言語選択

多言語ドキュメントの生成は時間とトークンを消費するため、ユーザーはインタラクティブな TUI チェックボックスで生成する言語を選択できます。

**トリガー：** `/share-skill docs` を `--i18n` フラグ付きで実行するか、コマンドが SKILL.md ファイルの翻訳が必要と検出した場合。

**TUI インターフェース：**
```
ドキュメントの言語を選択（スペースで切り替え、エンターで確定）：

  [x] English (en)        - 常に生成
  [ ] 简体中文 (zh-CN)    - 簡体字中国語
  [ ] 日本語 (ja)         - 日本語
  [ ] その他...           - カスタム言語コードを入力

選択済み: English
```

**デフォルト選択：**
- English: **チェック済み**（必須、常に生成）
- 简体中文 (zh-CN): **未チェック**
- 日本語 (ja): **未チェック**
- その他: **未チェック**（カスタム言語コードの入力を許可）

**カスタム言語入力：**
ユーザーが「その他...」を選択した場合、言語コードの入力を促す：
```
言語コードを入力（例：'ko' は韓国語、'de' はドイツ語）：
> ko

言語を追加しました: 한국어 (ko)
```

**AskUserQuestion 実装：**
```json
{
  "questions": [
    {
      "question": "ドキュメントに生成する言語を選択してください",
      "header": "言語",
      "multiSelect": true,
      "options": [
        { "label": "English (en)", "description": "必須、常に生成" },
        { "label": "简体中文 (zh-CN)", "description": "簡体字中国語翻訳" },
        { "label": "日本語 (ja)", "description": "日本語翻訳" },
        { "label": "その他...", "description": "カスタム言語コードを入力" }
      ]
    }
  ]
}
```

**選択に基づいて生成されるファイル：**
| 選択 | SKILL ファイル | README ファイル |
|------|--------------|----------------|
| 英語のみ | `SKILL.md` | `README.md` |
| +中国語 | `SKILL.md`, `SKILL.zh-CN.md` | `README.md`, `README.zh-CN.md` |
| +日本語 | `SKILL.md`, `SKILL.ja.md` | `README.md`, `README.ja.md` |
| +韓国語 | `SKILL.md`, `SKILL.ko.md` | `README.md`, `README.ko.md` |

### ドキュメントサイト機能特性

`/share-skill docs` で生成されるドキュメントサイトには以下の機能が含まれます：

#### 1. ダイナミックナビバーブランド

ナビゲーションバー左側のアバターと名前はリポジトリの URL にリンクします：

```html
<!-- index.html テンプレート -->
<a class="navbar-brand" id="repoLink" href="https://github.com/{username}/{repo}" target="_blank">
    <img class="brand-avatar" id="userAvatar" src="" alt="Avatar">
    <span class="brand-text" id="brandTitle">Skills</span>
</a>
```

```javascript
// main.js でリポジトリリンクを動的に更新
const repoLink = document.getElementById('repoLink');
if (repoLink) {
    repoLink.href = `https://github.com/${REPO_OWNER}/${REPO_NAME}`;
}
```

#### 2. ダイナミック Favicon

ウェブサイトの favicon は GitHub ユーザーのアバターを自動的に使用します：

```html
<!-- index.html テンプレート -->
<link rel="icon" id="favicon" type="image/png" href="">
```

```javascript
// main.js で favicon を動的に設定
const favicon = document.getElementById('favicon');
if (favicon) {
    favicon.href = user.avatar_url;  // GitHub API から取得
}
```

#### 3. フッターアトリビューション

README とドキュメントサイトのフッターリンクはドキュメントサイトを指します。URL は `custom_domain` 設定に基づいて動的に生成されます：

**main.js の動的 URL ロジック：**
```javascript
// main.js
function getDocsUrl() {
    if (CUSTOM_DOMAIN) {
        return `https://${CUSTOM_DOMAIN}/`;
    }
    return `https://${REPO_OWNER}.github.io/${REPO_NAME}/`;
}

// フッターリンクを設定
const footerLink = document.querySelector('.footer a');
if (footerLink) {
    footerLink.href = getDocsUrl();
}
```

**README.md フッター（動的生成）：**
```markdown
<!-- custom_domain が設定されている場合 -->
Made with ♥ by [Yu's skills](https://skill.guoyu.me/)

<!-- GitHub Pages を使用する場合 -->
Made with ♥ by [Yu's skills](https://guo-yu.github.io/skills/)
```

```html
<!-- index.html フッター -->
<footer class="footer">
    <div class="footer-content">
        <p>Made with <span class="heart">♥</span> by <a href="https://skill.guoyu.me/" id="footerLink">Yu's skills</a></p>
    </div>
</footer>
```

#### 4. i18n SKILL.md キャッシュバスティング

言語切り替え時にキャッシュされたコンテンツが読み込まれるのを防ぐため、SKILL.md をフェッチする際にタイムスタンプを追加します：

```javascript
// main.js
const CACHE_VERSION = Date.now();

function getBasePath(skillName, lang = 'en') {
    const fileName = lang === 'en' ? 'SKILL.md' : `SKILL.${lang}.md`;

    if (isGitHubPages) {
        return `https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/${BRANCH}/${skillName}/${fileName}?v=${CACHE_VERSION}`;
    } else {
        return `../${skillName}/${fileName}?v=${CACHE_VERSION}`;
    }
}
```

#### 5. main.js 設定

main.js の先頭にリポジトリ設定定数を含めます：

```javascript
// main.js
const REPO_OWNER = '{username}';    // GitHub ユーザー名
const REPO_NAME = '{repo}';          // リポジトリ名
const BRANCH = 'master';             // または 'main'
const CACHE_VERSION = Date.now();    // キャッシュバスティング用
```

#### 6. マーケティングセクション（なぜこのスキルを使うのか？）

各スキルはドキュメントコンテンツの上に魅力的なマーケティングセクションを表示します：
- **ヘッドライン**：価値提案を説明するキャッチーな一行
- **理由**：ユーザーがこのスキルを使うべき理由を説明する段落
- **ペインポイント**：スキルが解決する問題を示す3つのカード

**main.js の SKILL_MARKETING データ構造：**

```javascript
const SKILL_MARKETING = {
    'skill-name': {
        en: {
            headline: '魅力的な一行の価値提案',
            why: 'このスキルが存在する理由とユーザーにどう役立つかの詳細説明...',
            painPoints: [
                {
                    icon: '🔥',
                    title: '問題のタイトル',
                    desc: 'このスキルが解決する問題の説明。'
                },
                {
                    icon: '🧠',
                    title: '別の問題',
                    desc: '別のペインポイントの説明。'
                },
                {
                    icon: '💥',
                    title: '3つ目の問題',
                    desc: '3つ目の問題の説明。'
                }
            ]
        },
        'zh-CN': {
            headline: '中文标题',
            why: '中文说明...',
            painPoints: [/* ... */]
        },
        ja: {
            headline: '日本語タイトル',
            why: '日本語説明...',
            painPoints: [/* ... */]
        }
    }
};
```

**レンダリング関数：**

```javascript
function renderMarketingSection(skillName) {
    const marketing = SKILL_MARKETING[skillName];
    if (!marketing) return '';

    const content = marketing[currentLang] || marketing['en'];
    // .marketing-section 構造の HTML を返す
}
```

**CSS クラス：**
- `.marketing-section` - グラデーション背景のコンテナ
- `.marketing-title` - グラデーションテキストのヘッドライン
- `.marketing-why` - 価値提案の段落
- `.pain-points-grid` - レスポンシブ3カラムグリッド
- `.pain-point-card` - アイコン、タイトル、説明を含むグラスカード

**マーケティングコンテンツ作成ガイドライン：**
1. ユーザーの視点で書く（「このスキル」ではなく「あなた」）
2. まずペインポイントを示し、次に解決策を提示
3. 具体的で共感できる例を使用（例：「ポート3000は既に使用中」）
4. ヘッドラインは10語以内に
5. ペインポイントのタイトルは解決策ではなく問題そのものを

#### 7. 三カラムレイアウト

ドキュメントサイトはレスポンシブ三カラムレイアウトを使用：

```html
<div class="main-container three-column">
    <!-- 左サイドバー：スキルナビゲーション + 目次 -->
    <aside class="sidebar glass">
        <div class="sidebar-content">
            <div class="sidebar-section">
                <h4 class="sidebar-heading" data-i18n="skills">スキル</h4>
                <nav class="sidebar-nav">
                    <a class="sidebar-link" href="?skill=port-allocator">port-allocator</a>
                    <a class="sidebar-link" href="?skill=share-skill">share-skill</a>
                    <!-- ... その他のスキル -->
                </nav>
            </div>
            <div class="sidebar-section">
                <h4 class="sidebar-heading" data-i18n="onThisPage">このページ</h4>
                <div class="js-toc"></div>  <!-- Tocbot がここに目次を生成 -->
            </div>
        </div>
    </aside>

    <!-- メインコンテンツ：Markdown ドキュメント -->
    <main class="main-content">
        <article class="js-toc-content content-card glass" id="content">
            <!-- レンダリングされた markdown コンテンツ -->
        </article>
    </main>

    <!-- 右サイドバー：インストール手順 -->
    <aside class="sidebar-right glass">
        <!-- インストールセクション -->
    </aside>
</div>
```

**レスポンシブ動作：**
- デスクトップ：三カラムすべて表示
- タブレット：右サイドバー非表示
- モバイル：両サイドバー非表示、モバイルメニュー表示

#### 8. 右サイドバー - インストールセクション

右サイドバーはクイックインストール手順を提供：

```html
<aside class="sidebar-right glass">
    <div class="sidebar-content">
        <div class="sidebar-section">
            <h4 class="sidebar-heading" data-i18n="installation">インストール</h4>
            <p class="install-desc" data-i18n="installDesc">最も簡単なインストール方法：</p>
            <div class="install-code">
                <pre><code><span class="comment"># <span data-i18n="addMarketplace">マーケットプレイスを追加</span></span>
<span class="cmd">/plugin marketplace add {username}/{repo}</span>

<span class="comment"># <span data-i18n="installSkills">スキルをインストール</span></span>
<span class="cmd">/plugin install {skill-name}@{username}-{repo}</span></code></pre>
            </div>
            <a class="install-link" href="https://github.com/{username}/{repo}#installation" target="_blank" data-i18n="moreOptions">その他のインストールオプション</a>
        </div>
    </div>
</aside>
```

**インストールセクションの i18n サポート：**
```javascript
const I18N = {
    en: {
        installation: 'Installation',
        installDesc: 'The easiest way to install:',
        addMarketplace: 'Add marketplace',
        installSkills: 'Install skills',
        moreOptions: 'More installation options'
    },
    'zh-CN': {
        installation: '安装方法',
        installDesc: '最简单的安装方式：',
        addMarketplace: '添加技能市场',
        installSkills: '安装技能',
        moreOptions: '更多安装选项'
    },
    ja: {
        installation: 'インストール',
        installDesc: '最も簡単なインストール方法：',
        addMarketplace: 'マーケットプレイスを追加',
        installSkills: 'スキルをインストール',
        moreOptions: 'その他のインストールオプション'
    }
};
```

#### 9. 目次生成 (Tocbot)

Tocbot ライブラリを使用して見出しから目次を自動生成：

```html
<!-- <head> 内 -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/tocbot/4.32.2/tocbot.min.css">

<!-- </body> の前 -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/tocbot/4.32.2/tocbot.min.js"></script>
```

```javascript
// コンテンツ読み込み後に初期化
tocbot.init({
    tocSelector: '.js-toc',
    contentSelector: '.js-toc-content',
    headingSelector: 'h1, h2, h3',
    scrollSmooth: true,
    scrollSmoothDuration: 300,
    headingsOffset: 100,
    scrollSmoothOffset: -100
});
```

#### 10. コード構文ハイライト (highlight.js)

highlight.js を使用してコードブロックの構文ハイライト：

```html
<!-- <head> 内 -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">

<!-- </body> の前 -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
```

```javascript
// markdown レンダリング後
document.querySelectorAll('pre code').forEach((block) => {
    hljs.highlightElement(block);
});
```

**実行手順：**

1. **リポジトリ構造を確認**
   ```bash
   # skills リポジトリディレクトリにいることを確認
   if [ ! -d {skills_path}/.git ]; then
     echo "まず skills リポジトリでこのコマンドを実行してください"
     exit 1
   fi
   ```

2. **設定を読み取り**
   ```bash
   # 設定からデザイン設定を読み取り
   cat ~/.claude/share-skill-config.json | jq '.docs'
   ```

3. **デザイン方法を選択**
   - `--skill` 指定時：対応する UI スキルを呼び出し（例：`ui-ux-pro-max`）
   - それ以外は `--style` で指定されたプリセットスタイルを使用（デフォルト `botanical`）

4. **ドキュメントサイトを生成**
   ```bash
   mkdir -p {skills_path}/docs
   mkdir -p {skills_path}/docs/css
   mkdir -p {skills_path}/docs/js
   ```

5. **ローカル開発サーバーを設定**

   エンドポイント設定と既存の package.json に基づいて処理：

   **シナリオ A: Monorepo モード（デフォルトエンドポイント）**

   `{skills_path}/package.json` が存在するか確認：

   ```bash
   if [ -f {skills_path}/package.json ]; then
     # 存在する場合、docs 関連スクリプトのみ追加（既存内容を上書きしない）
     # jq または手動で scripts をマージ
   else
     # 存在しない場合、新しい package.json を作成
   fi
   ```

   - **package.json が存在**: `dev:docs` スクリプトを追加
     ```bash
     # 既存の package.json を読み取り、新しいスクリプトを追加
     jq '.scripts["dev:docs"] = "npx serve . -l <ポート>"' package.json > tmp.json
     mv tmp.json package.json
     ```

   - **package.json が存在しない**: 新しいファイルを作成
     ```json
     {
       "name": "claude-code-skills",
       "version": "1.0.0",
       "private": true,
       "scripts": {
         "dev": "npx serve . -l <ポート>"
       }
     }
     ```

   **シナリオ B: 独立リポジトリモード（カスタムエンドポイント）**

   各スキルは独立した Git リポジトリを持ち、それぞれの package.json を確認：

   ```bash
   SKILL_DIR={skills_path}/<skill-name>

   if [ -f "$SKILL_DIR/package.json" ]; then
     # 重要：ユーザーの既存 package.json を上書きしない
     # docs スクリプトのみ追加（存在しない場合）
     echo "既存の package.json を検出、dev:docs スクリプトを追加"
   else
     # 最小限の package.json を作成
     echo "package.json を作成中..."
   fi
   ```

   **ポート割り当てフロー：**
   - `~/.claude/port-registry.json` を読み取り、次に利用可能なポートを取得
   - port-registry を更新してこのプロジェクトを登録
   - package.json に開発スクリプトを追加または作成

   **安全ルール：**
   - 既存の package.json を**絶対に上書きしない**
   - `scripts` フィールドにのみ新しいコマンドを**追加**
   - `dev` スクリプトが存在する場合、代替コマンド名として `dev:docs` を使用

6. **カスタムドメインを設定**

   設定からカスタムドメインの設定を読み取り：

   ```bash
   CUSTOM_DOMAIN=$(cat ~/.claude/share-skill-config.json | grep -o '"custom_domain":\s*"[^"]*"' | cut -d'"' -f4)
   ```

   **設定されていない場合（初回生成時）、ユーザーにプロンプト：**
   ```
   カスタムドメインを設定しますか？

   [ ] GitHub Pages を使用（{username}.github.io/{repo}）（推奨）
   [ ] カスタムドメインを設定...
   ```

   ユーザーがカスタムドメインを選択した場合、入力を促す：
   ```
   カスタムドメインを入力してください（例：skill.guoyu.me）：
   > skill.guoyu.me
   ```

   **CNAME ファイルを生成：**
   ```bash
   if [ -n "$CUSTOM_DOMAIN" ]; then
     echo "$CUSTOM_DOMAIN" > {skills_path}/docs/CNAME
   else
     rm -f {skills_path}/docs/CNAME
   fi
   ```

   **設定を更新：**
   ```bash
   # custom_domain 設定を更新（null または文字列）
   # jq または手動でファイルを編集
   ```

7. **キャッシュバージョン番号を更新**

   docs コンテンツを変更するたびに、ブラウザキャッシュの問題を避けるためリソースファイルのバージョン番号を自動更新：

   ```bash
   # バージョン番号を生成（タイムスタンプを使用）
   VERSION=$(date +%s)

   # index.html のバージョン番号を更新
   sed -i '' "s/main.js?v=[0-9]*/main.js?v=$VERSION/" docs/index.html
   sed -i '' "s/custom.css?v=[0-9]*/custom.css?v=$VERSION/" docs/index.html
   ```

   **またはファイルハッシュを使用：**
   ```bash
   JS_HASH=$(md5 -q docs/js/main.js | head -c 8)
   CSS_HASH=$(md5 -q docs/css/custom.css | head -c 8)

   sed -i '' "s/main.js?v=[a-z0-9]*/main.js?v=$JS_HASH/" docs/index.html
   sed -i '' "s/custom.css?v=[a-z0-9]*/custom.css?v=$CSS_HASH/" docs/index.html
   ```

   **index.html テンプレートにはバージョンプレースホルダーを含める：**
   ```html
   <link rel="stylesheet" href="css/custom.css?v=1">
   <script src="js/main.js?v=1"></script>
   ```

8. **コミットしてプッシュ**
   ```bash
   git add docs/
   git commit -m "Update documentation site"
   git push
   ```

### コマンド: `/share-skill docs config`

ドキュメント生成のデフォルト設定を構成。

**対話オプション：**
```
ドキュメントサイトのデザインを設定

デザイン方法:
  1. プリセットスタイルを使用
  2. UI スキルを使用

プリセットスタイル:
  - botanical (デフォルト): 自然な植物スタイル、エレガントで柔らか
  - minimal: ミニマリスト白黒スタイル
  - tech: モダンテック感スタイル

UI スキル:
  - ui-ux-pro-max: プロフェッショナル UI/UX デザインスキル
  - (ユーザーがインストールした他の UI スキル)

カスタムドメイン: (オプション)
```

### デザインスタイルプリセット

#### `botanical` - 自然植物スタイル（デフォルト）

**デザイン哲学：**
自然へのデジタルな敬意——呼吸し、流れ、有機的な美しさに根ざして。柔らかく、洗練され、思慮深く、現代のテック美学の硬直した冷たさとハイパーデジタルな鋭さを拒否し、暖かさ、触感、自然界の不完全さを受け入れる。

**コア要素：**
- **有機的な柔らかさ**: 至る所に丸みを帯びた角、テラゾのように流れる形状
- **エレガントなタイポグラフィ**: Playfair Display ハイコントラストセリフ + Source Sans 3 ヒューマニストサンセリフ
- **アーストーン**: フォレストグリーン (#2D3A31)、セージグリーン (#8C9A84)、テラコッタ (#C27B66)、ライスペーパーホワイト (#F9F8F4)
- **紙のテクスチャ**: 必須の SVG ノイズオーバーレイ、冷たいデジタルピクセルを暖かい触感に変換
- **呼吸空間**: 豊富な余白、セクション間隔 py-32、カード間隔 gap-16
- **スローモーション**: そよ風に揺れる植物のように、duration-500 から duration-700

**カラーシステム：**
| 用途 | 色 | 値 |
|------|-----|-----|
| 背景 | ウォームホワイト/ライスペーパー | `#F9F8F4` |
| 前景 | ディープフォレストグリーン | `#2D3A31` |
| プライマリ | セージグリーン | `#8C9A84` |
| セカンダリ | ソフトクレイ/マッシュルーム | `#DCCFC2` |
| ボーダー | ストーン | `#E6E2DA` |
| インタラクティブ | テラコッタ | `#C27B66` |

**フォントペアリング：**
- 見出し: **Playfair Display** (Google Font) - トランジショナルセリフ、ハイコントラストストローク
- 本文: **Source Sans 3** (Google Font) - 読みやすいヒューマニストサンセリフ

**ボーダーラジウスルール：**
- カード: `rounded-3xl` (24px)
- ボタン: `rounded-full` (ピル形状)
- 画像: `rounded-t-full` (アーチ) または `rounded-[40px]`

**紙のテクスチャオーバーレイ（重要）：**
```jsx
<div
  className="pointer-events-none fixed inset-0 z-50 opacity-[0.015]"
  style={{
    backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
    backgroundRepeat: "repeat",
  }}
/>
```

**シャドウシステム：**
```css
/* デフォルト */
box-shadow: 0 4px 6px -1px rgba(45, 58, 49, 0.05);
/* ミディアム */
box-shadow: 0 10px 15px -3px rgba(45, 58, 49, 0.05);
/* ラージ */
box-shadow: 0 20px 40px -10px rgba(45, 58, 49, 0.05);
```

**モーションガイドライン：**
- 高速インタラクション: `duration-300` (ボタンホバー、リンクカラー)
- 標準: `duration-500` (カードリフト、トランスフォーム)
- スロードラマチック: `duration-700` から `duration-1000` (画像ズーム)
- ホバー動作: `-translate-y-1` とシャドウ強化

**レスポンシブ戦略：**
- モバイル: サイドバーを非表示、タイトルを text-8xl から text-5xl に縮小
- タッチターゲット: 最小 44px の高さを維持
- グリッドブレークポイント: `grid-cols-1` → `md:grid-cols-3`

### 外部 UI スキルの使用

ユーザーが `ui-ux-pro-max` や他の UI スキルをインストールしている場合、それを呼び出してドキュメントをデザイン可能：

```bash
/share-skill docs --skill ui-ux-pro-max
```

**実行フロー：**

1. **スキルの存在を検出**
   ```bash
   if [ -d ~/.claude/skills/ui-ux-pro-max ] || [ -L ~/.claude/skills/ui-ux-pro-max ]; then
     echo "ui-ux-pro-max スキルを検出しました"
   fi
   ```

2. **スキルを呼び出してデザインを生成**
   - 現在のスキルリストと構造情報を UI スキルに渡す
   - UI スキルが完全な HTML/CSS/JS を生成
   - `{skills_path}/docs/` ディレクトリに出力

3. **デザイン設定を確認**（UI スキルがサポートする場合）
   ```
   ui-ux-pro-max を使用してドキュメントサイトをデザイン

   デザインスタイルを選択:
     1. glassmorphism - グラスモーフィズム
     2. claymorphism - クレイモーフィズム
     3. minimalism - ミニマリズム
     4. brutalism - ブルータリズム
     5. neumorphism - ニューモーフィズム
     6. bento-grid - ベントグリッド
   ```

### 出力形式

**生成成功：**
```
ドキュメントサイトを生成しました

場所: {skills_path}/docs/
デザインスタイル: botanical (自然植物スタイル)
カスタムドメイン: skill.guoyu.me

ファイル構造:
  docs/
  ├── index.html
  ├── CNAME
  ├── css/
  │   └── custom.css
  └── js/
      └── main.js

GitHub にプッシュ済み
アクセス: https://skill.guoyu.me

GitHub Pages 設定:
   1. リポジトリ Settings → Pages
   2. Source: Deploy from a branch
   3. Branch: master, /docs
```

**UI スキル使用時：**
```
ドキュメントサイトを生成しました

場所: {skills_path}/docs/
デザイン: ui-ux-pro-max (glassmorphism スタイル)
カスタムドメイン: skill.guoyu.me

アクセス: https://skill.guoyu.me
```

---

## README 自動生成

share-skill はリポジトリの作成または更新時に、多言語 README ファイルを自動生成/更新。

### サポート言語

| 言語 | ファイル名 | 言語コード |
|------|----------|-----------|
| English (デフォルト) | `README.md` | `en` |
| 简体中文 | `README.zh-CN.md` | `zh-CN` |
| 日本語 | `README.ja.md` | `ja` |

### ファイル構造

```
skills/
├── README.md              # English (デフォルト)
├── README.zh-CN.md        # 简体中文
├── README.ja.md           # 日本語
└── ...
```

### 言語切り替えナビゲーション

各 README ファイルの上部に言語切り替えリンクを含む：

```markdown
<p align="center">
  <a href="README.md">English</a> |
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="README.ja.md">日本語</a>
</p>
```

### README タイトルルール

| リポジトリタイプ | English | 简体中文 | 日本語 |
|----------------|---------|---------|--------|
| **スキルセット** | `{username}'s Skills` | `{username} 的技能集` | `{username} のスキル` |
| **単一スキル** | `{username}'s Skill: {name}` | `{username} 的技能: {name}` | `{username} のスキル: {name}` |

### README テンプレート - English (README.md)

```markdown
<p align="center">
  <a href="README.md">English</a> |
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="README.ja.md">日本語</a>
</p>

# {username}'s Skills

My collection of custom Claude Code skills for productivity and automation.

## Skills

| Skill | Description |
|-------|-------------|
| [port-allocator](./port-allocator/) | Automatically allocate development server ports |
| [share-skill](./share-skill/) | Migrate skills to repositories with Git support |

## Documentation

This skill set has an online documentation site generated by [share-skill](https://github.com/guo-yu/skills/tree/master/share-skill).

**With Custom Domain:**
```
https://{custom_domain}/
```

**GitHub Pages:**
```
https://{username}.github.io/{repo-name}/
```

### Setup GitHub Pages

1. Go to repository **Settings** → **Pages**
2. Under "Source", select **Deploy from a branch**
3. Choose branch: `master` (or `main`), folder: `/docs`
4. (Optional) Add custom domain

## License

MIT

---

Made with ♥ by [Yu's skills](https://skill.guoyu.me/)
```

### README テンプレート - 简体中文 (README.zh-CN.md)

```markdown
<p align="center">
  <a href="README.md">English</a> |
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="README.ja.md">日本語</a>
</p>

# {username} 的技能集

我的 Claude Code 自定义技能集合，用于提高生产力和自动化。

## 技能列表

| 技能 | 说明 |
|------|------|
| [port-allocator](./port-allocator/) | 自动分配开发服务器端口 |
| [share-skill](./share-skill/) | 将技能迁移到仓库并支持 Git 版本管理 |

## 在线文档

本技能集有一个由 [share-skill](https://github.com/guo-yu/skills/tree/master/share-skill) 生成的在线文档网站。

**自定义域名访问：**
```
https://{custom_domain}/
```

**GitHub Pages 访问：**
```
https://{username}.github.io/{repo-name}/
```

### 配置 GitHub Pages

1. 进入仓库 **Settings** → **Pages**
2. 在 "Source" 下选择 **Deploy from a branch**
3. 选择分支: `master` (或 `main`)，文件夹: `/docs`
4. (可选) 在 "Custom domain" 中添加自定义域名

## 许可证

MIT

---

Made with ♥ by [Yu's skills](https://skill.guoyu.me/)
```

### README テンプレート - 日本語 (README.ja.md)

```markdown
<p align="center">
  <a href="README.md">English</a> |
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="README.ja.md">日本語</a>
</p>

# {username} のスキル

生産性と自動化のための Claude Code カスタムスキルコレクション。

## スキル一覧

| スキル | 説明 |
|--------|------|
| [port-allocator](./port-allocator/) | 開発サーバーポートの自動割り当て |
| [share-skill](./share-skill/) | Git サポート付きでスキルをリポジトリに移行 |

## ドキュメント

このスキルセットには [share-skill](https://github.com/guo-yu/skills/tree/master/share-skill) で生成されたオンラインドキュメントサイトがあります。

**カスタムドメイン：**
```
https://{custom_domain}/
```

**GitHub Pages：**
```
https://{username}.github.io/{repo-name}/
```

### GitHub Pages の設定

1. リポジトリの **Settings** → **Pages** に移動
2. "Source" で **Deploy from a branch** を選択
3. ブランチ: `master` (または `main`)、フォルダ: `/docs` を選択
4. (オプション) "Custom domain" にカスタムドメインを追加

## ライセンス

MIT

---

Made with ♥ by [Yu's skills](https://skill.guoyu.me/)
```

### 実行手順

`/share-skill docs` または `/share-skill <skill-name>` 実行時：

1. **設定を読み取り**
   ```bash
   CONFIG=$(cat ~/.claude/share-skill-config.json)
   GITHUB_URL=$(echo "$CONFIG" | jq -r '.remotes.github')
   GITHUB_USERNAME=$(echo "$GITHUB_URL" | grep -oP 'github\.com[:/]\K[^/]+')
   CUSTOM_DOMAIN=$(echo "$CONFIG" | jq -r '.docs.custom_domain // empty')
   REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")
   ```

2. **言語切り替えナビゲーションを生成**
   ```bash
   LANG_NAV='<p align="center">
     <a href="README.md">English</a> |
     <a href="README.zh-CN.md">简体中文</a> |
     <a href="README.ja.md">日本語</a>
   </p>'
   ```

3. **すべての言語の README を生成**
   ```bash
   # 言語設定を定義
   declare -A LANG_CONFIG
   LANG_CONFIG[en]="README.md"
   LANG_CONFIG[zh-CN]="README.zh-CN.md"
   LANG_CONFIG[ja]="README.ja.md"

   # 各言語の README を生成
   for lang in en zh-CN ja; do
     FILE="${LANG_CONFIG[$lang]}"
     generate_readme "$lang" "$FILE"
   done
   ```

4. **README ファイルに書き込み**
   ```bash
   generate_readme() {
     local lang=$1
     local file=$2

     # 言語に基づいてテンプレートを選択
     case $lang in
       en)
         TITLE="${GITHUB_USERNAME}'s Skills"
         # ... 英語コンテンツ
         ;;
       zh-CN)
         TITLE="${GITHUB_USERNAME} 的技能集"
         # ... 中国語コンテンツ
         ;;
       ja)
         TITLE="${GITHUB_USERNAME} のスキル"
         # ... 日本語コンテンツ
         ;;
     esac

     cat > "$file" << EOF
     $LANG_NAV

     # $TITLE
     ...
     EOF
   }
   ```

### 出力形式

```
README 多言語ファイルを更新しました

生成されたファイル:
  ✓ README.md (English)
  ✓ README.zh-CN.md (简体中文)
  ✓ README.ja.md (日本語)

ドキュメントリンク: https://skill.guoyu.me/

含まれるセクション:
  ✓ 言語切り替えナビゲーション
  ✓ Skills リスト
  ✓ Documentation (オンラインドキュメント説明)
  ✓ License
  ✓ Attribution (Made with ♥)
```

---

## ローカルテスト

share-skill は生成されたドキュメントが SKILL.md の仕様に準拠していることを確認する検証スクリプトを提供します。

### 検証スクリプト

場所：`share-skill/test/verify-docs.sh`

**使用方法：**
```bash
# 現在のディレクトリをテスト
./share-skill/test/verify-docs.sh .

# 特定のリポジトリをテスト
./share-skill/test/verify-docs.sh {skills_path}
```

**チェック項目：**

| カテゴリ | チェック内容 |
|----------|-------------|
| **ディレクトリ構造** | docs/index.html, docs/js/main.js, docs/css/custom.css, docs/CNAME |
| **index.html** | Favicon, ナビバーブランド, 三カラムレイアウト, 言語切り替え, インストールセクション, tocbot, highlight.js, フッター, バージョン番号 |
| **main.js** | REPO_OWNER, REPO_NAME, BRANCH, CACHE_VERSION, I18N オブジェクト, getBasePath, 動的 favicon/repoLink, tocbot.init, hljs |
| **README ファイル** | README.md, README.zh-CN.md, README.ja.md, 言語ナビゲーションリンク, フッターアトリビューション |
| **スキルファイル** | 各スキルの SKILL.md, SKILL.zh-CN.md, SKILL.ja.md |
| **スキル設定** | 各スキルが main.js SKILLS オブジェクトに設定 |

**サンプル出力：**
```
╔════════════════════════════════════════════════════════════╗
║     share-skill Documentation Verification Script          ║
╚════════════════════════════════════════════════════════════╝

Repository: /Users/username/Codes/skills

── 1. Directory Structure ──
  ✓ docs/index.html exists
  ✓ docs/js/main.js exists
  ✓ docs/css/custom.css exists
  ✓ docs/CNAME exists (custom domain configured)

── 2. index.html Structure ──
  ✓ Favicon element with id='favicon'
  ✓ Navbar brand with id='repoLink'
  ...

════════════════════════════════════════════════════════════
                        Summary
════════════════════════════════════════════════════════════

  Passed:  71
  Failed:  0
  Warnings: 0

✓ All required checks passed!
```

**終了コード：**
- `0`：すべてのチェックに合格
- `1`：1つ以上のチェックに失敗

### 実行タイミング

以下の場合に検証スクリプトを実行することを推奨：
- `/share-skill docs` でドキュメント生成後
- ドキュメント変更をコミットする前
- ドキュメントの問題をトラブルシューティングする際
- ドキュメントの CI/CD パイプラインの一部として
