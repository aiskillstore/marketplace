# GitHub 側の設定を揃える

テンプレートから作ったリポジトリの GitHub 側の設定を、gh で揃える手順である。対象リポジトリを `REPO=<owner>/<name>` とする。

## 1. アプリ名を変える

`apps/web/app-name.ts` の `APP_NAME` は、テンプレートの名前のままになっている。リポジトリ名に合わせて変える。同じ Cloudflare アカウントの別リポジトリと名前が重なると、お互いのリソースを置き換えてしまう。

## 2. secrets を登録する

値はユーザーに尋ねる。

```sh
gh secret set OPENROUTER_API_KEY --repo "$REPO"
gh secret set CLAUDE_CODE_OAUTH_TOKEN --repo "$REPO"
gh secret set CLOUDFLARE_ACCOUNT_ID --repo "$REPO"
gh secret set CLOUDFLARE_API_TOKEN --repo "$REPO"
```

| 名前                      | 用途                                         |
| ------------------------- | -------------------------------------------- |
| `OPENROUTER_API_KEY`      | verify ワークフローの oxlint-plugin-decision |
| `CLAUDE_CODE_OAUTH_TOKEN` | verify 失敗時に Claude Code が自動修正する   |
| `CLOUDFLARE_ACCOUNT_ID`   | デプロイ先と Alchemy の状態を置くアカウント  |
| `CLOUDFLARE_API_TOKEN`    | 同じアカウントの API トークン                |

Organization のリポジトリなら、Organization の secrets に一度登録すれば、リポジトリごとの登録は要らない。

## 3. Actions に PR の作成を許可する

release-please と自動修正のワークフローが PR を作る。

```sh
gh api --method PUT "repos/$REPO/actions/permissions/workflow" \
  -f default_workflow_permissions=read -F can_approve_pull_request_reviews=true
```

## 4. PR を作れる人を collaborator に限り、auto-merge を有効にする

```sh
gh api --method PATCH "repos/$REPO" -f pull_request_creation_policy=collaborators_only \
  -F allow_auto_merge=true -F allow_update_branch=true
```

## 5. 既定ブランチを保護する

既定ブランチにルールセットを置く。同じ名前のルールセットがあれば置き換える。

- 既定ブランチの削除と force push を禁じる
- `up-to-date` チェックを通っていない PR のマージを拒む
- 最新の既定ブランチを取り込んでいない PR のマージを拒む
- バイパスは置かない

release-please の PR は、Claude が既定ブランチを取り込んで push し、その push で動く `up-to-date` が通ってからマージする。

```sh
id="$(gh api "repos/$REPO/rulesets" --jq '.[] | select(.name == "protect default branch") | .id')"
gh api --method "$([ -n "$id" ] && echo PUT || echo POST)" "repos/$REPO/rulesets${id:+/$id}" --input - <<'JSON'
{
  "name": "protect default branch",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "bypass_actors": [],
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "do_not_enforce_on_create": false,
        "required_status_checks": [{ "context": "up-to-date", "integration_id": 15368 }]
      }
    }
  ]
}
JSON
```

## 6. 反映を確かめる

次の 2 つを確かめる。

- `gh api "repos/$REPO" --jq '[.pull_request_creation_policy, .allow_auto_merge]'` が `["collaborators_only",true]` を返す
- `gh api "repos/$REPO/rules/branches/$(gh api "repos/$REPO" --jq .default_branch)" --jq '[.[].type]'` に `required_status_checks` がある
