# typescript-template の骨格

masseater/typescript-template から作ったリポジトリで確かめる、テンプレートが持ち続けている要素の一覧である。

各要素を「入り・効き・残り」の 3 点で見る。細部の正はテンプレートの実物にある。root の `vite.config.ts`、`.claude/hooks/`、`.vite-hooks/`、`.github/workflows/`、`apps/*/` がそれにあたる。

## 1. 道具立ては Vite+ ひとつ

- 入りは、root と各 app の `vite.config.ts` があり、`package.json` の scripts が vp 経由で、`devEngines` が pnpm である。
- 効きは、`git config core.hooksPath` が `.vite-hooks/_` を指し、`.vite-hooks/{pre-commit,commit-msg,pre-push}` が vp を呼ぶ。CI は `voidzero-dev/setup-vp` で install と verify を回す。エージェントの pnpm 直実行は `.claude/settings.json` の deny と `block-pnpm.ts` が止める。
- 残りは、turbo.json、husky、yarn・npm・bun のロックファイル、生の pnpm や npx や prettier を呼ぶ script や CI が消えているかを見る。

## 2. 依存のバージョンは pnpm カタログに一本化

- 入りは、`pnpm-workspace.yaml` に `catalog` と `catalogs: stack`、`catalogMode: prefer` があり、依存が `catalog:` と `catalog:stack` を参照している。
- 効きは、`vp run verify` の syncpack が通り、同じ依存の複数バージョンを許さない。
- 残りは、カタログにある依存の直書きと、パッケージに散った同じ依存の別バージョンが無いかを見る。

## 3. monorepo の構成は Nx スタイルで、パッケージマネージャは pnpm のまま

- 入りは、パッケージがアプリの `apps/`、共有するコードの `libs/`、リポジトリの道具の `tools/` に分かれ、`pnpm-workspace.yaml` の `packages` がこれらを挙げている。
- 効きは、`vp install` と `vp run -r` が、ワークスペースのパッケージを解決して回る。
- 残りは、`nx.json` や `@nx/*` を入れた形跡と、`apps/`・`libs/`・`tools/` の外に散ったパッケージが無いかを見る。

## 4. 型は `@effect/tsgo` で見る

- 入りは、`catalog:stack` の `@effect/tsgo` があり、全パッケージの tsconfig が `tsconfig.base.json` を `extends` し、app の `prepare` が `effect-tsgo patch --typescript --oxlint` を回す。
- 効きは、`vite.config.ts` の `vp check` で `typeAware: true` と `typeCheck: true` が有効で、`@effect/tsgo/oxlint-presets` の effect ルールが読み込まれ、`tsconfig.base.json` の `strict`・`exactOptionalPropertyTypes`・`noUncheckedIndexedAccess` が生きたままである。
- 残りは、独自の緩い tsconfig が継承を置き換えていないか、preset の読み込みを外していないか、patch の prepare を消していないかを見る。

## 5. Effect を土台にする

- 入りは、`effect` 依存があり、外部入力や外部 API との境界とドメインが Effect・Layer・Context・Schema で組まれている。
- 効きは、境界の値がライブラリの型のまま `Schema.decode*` に渡り、外部 API のクライアントが Effect 公式、distilled.cloud、OpenAPI 生成の順で選ばれ、時間やお金を使う処理が `Effect.withSpan` で見える。
- 残りは、素の Promise と try/catch のドメイン、valibot や zod の併存、手書きの API ラッパーが無いかを見る。

## 6. fallow で死にコード・重複・脆弱性・依存を見る

- 入りは、`.fallowrc.jsonc` と、root と app の `fallow` script、verify の `fallow-all` がある。
- 効きは、`vp run -r fallow` が型認識とセキュリティ検査を含めて回り、通る。`--fail-on-issues` のような失敗条件が生きている。緩めると緑の意味が消えるからである。
- 残りは、knip・jscpd・ts-prune のような置き換え済みの設定や script が消えているか、rc と script に設定が二重になっていないかを見る。

## 7. 検証の入口は `vp run verify` ひとつ

- 入りは、`vp run verify` が検証の入口として存在する。今のテンプレートでは root `vite.config.ts` の `run.tasks.verify` と dependsOn のグラフが入口で、script の連鎖でも、1 つの入口から検査がまとめて回っていれば働いている。
- 効きは、`.vite-hooks/pre-push`、CI の verify ジョブ、`.claude/hooks/stop-gate.ts` が同じ `vp run verify` を呼ぶ。test、eslint、syncpack、markdown-lint、renovate、actions-lint、steiger、db:check、fallow、audit のような、リポジトリに対象のある検査が入口から回っている。
- 残りは、verify の外に散った検査、対象が無いのに残ったタスク、タスクの削除で緑にした形跡が無いかを見る。

## 8. 手元と CI のゲートが効いている

- 入りは、`.vite-hooks/` と `.github/workflows/` に verify のセットがある。今のテンプレートは autofix・up-to-date・zap のワークフローを持ち、deploy と release は verify のワークフローのジョブである。
- 効きは、main の直近の verify が緑である。`gh run list --branch main --limit 5` で確かめる。ルールセットの必須チェックに挙がる名前のジョブがワークフローに実在し、実際に報告される。`gh api repos/{owner}/{repo}/rulesets` と `gh workflow list` で確かめる。報告されない必須チェックは PR を止める。デプロイするリポジトリでは deploy ジョブが緑で、README の「公開先」の URL が応答する。
- 残りは、deploy.yml や verify-autofix.yml のような前身のワークフローが消えているか、このリポジトリでは決して動かない条件が無いかを見る。`github.repository == 'masseater/typescript-template'` のままの release ジョブなどがそれにあたる。

## 9. エージェント用の設定が生きている

- 入りは、`.claude/hooks/` 一式、`.claude/settings.json`、`.claude/loop.md`、`AGENTS.md` と `CLAUDE.md`、`.intent/hooks/intent-claude-gate.mjs`、`.claude/skills` から張る `.agents/skills` と `skills-lock.json` がある。
- 効きは、settings.json の hooks が実在のファイルを指して起動時に走る。`skills ls` と `vp exec intent list` がスキルを返す。セッション開始でテンプレートの新リリースが案内される。
- 残りは、移行前の `.claude/rules/` や旧スキルの残骸、settings.json が指す実在しないファイルが無いかを見る。

## 10. デプロイするリポジトリは Alchemy で宣言する

- 入りは、`apps/<name>/alchemy.run.ts`、`app-name.ts` とそのテストがあり、リソース名が `app-name.ts` から取られている。
- 効きは、`vp run deploy` が通り、CI の deploy ジョブが secrets で回る。
- 残りは、wrangler.toml や wrangler の直呼び、Terraform や Pulumi の併存が無いかを見る。

## 11. 冗長な設定をしない

- 同じ役割の持ち主を 1 つにする。tsconfig の共通部は `tsconfig.base.json`、依存の版はカタログ、アプリ名は `app-name.ts` に置き、環境変数は環境ごとに変わる値だけにする。
- 置き換えの後始末を済ませる。prettier から oxfmt へ、eslint CLI の直接実行から `vp check` へ、knip から fallow へ、husky から `.vite-hooks` へ置き換わり、旧い側の設定、依存、script は消えている。
- 無効化を増やさない。`oxlint-disable` と `eslint-disable` のコメント、`ignorePatterns` の追加、severity の緩和を、移行の都合で増やさない。

## 12. 無駄なドキュメント、無駄なコードコメントを削除する

- 入りは、`vite.config.ts` の lint に `no-comments/disallowComments` が error で入り、許すのは `oxlint-disable` と `eslint-disable` だけである。
- 効きは、`vp run verify` の lint が、コメントを含むコードを落とす。
- 残りは、経緯や理由を書いたコメントやドキュメント、前の構成のままの README や docs、移行の間に書いたメモが消えているかを見る。

## 13. CI は差分とキャッシュで効率よく回す

- 入りは、verify が main への push と手動実行でだけ回り、PR では回らない。PR 側のゲートは `up-to-date` の必須チェックだけである。commitlint と gitleaks は push された範囲だけを対象にし、`fetch-depth: 0` の全履歴取得を禁じるルールが actions-lint にある。deploy は、その sha がブランチの先頭のときだけ動く。依存の install は setup-vp の `cache: true` でキャッシュし、oxlint-plugin-decision の判定は `actions/cache` の restore と save で持ち回る。
- 効きは、main の直近の run で確かめる。`gh run view <run-id> --log` に、依存のキャッシュと oxlint-plugin-decision の判定キャッシュの復元が出ていること、push のたびの検査が push された範囲だけを対象にしていることである。PR ごとのレビューはしない前提なので、PR 側は main の更新に追従しているかまででよい。
- 残りは、PR ごとに verify を回す形、全履歴を対象にした検査、`fetch-depth: 0`、キャッシュの restore や save の欠け、古い sha でも deploy が動く形が無いかを見る。
