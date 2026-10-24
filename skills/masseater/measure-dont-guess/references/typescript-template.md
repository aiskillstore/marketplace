# typescript-template での計測

masseater/typescript-template から作ったリポジトリで、何をどこで計り、どう読むかの参照である。

## 信号の出し方

サーバーの信号は Effect の API で出し、Cloudflare Workers Observability に集める。

- `Effect.withSpan` は `apps/web/src/pages/home/api/tracing.server.ts` が Workers のトレースに写す
- `Effect.log*` は Workers Logs に入る
- D1 や fetch の呼び出しは、Cloudflare が自動でスパンにする
- メトリクスは、Workers のリクエスト数、エラー数、CPU 時間、所要時間を使う
- 観測の設定とサンプリング率は `apps/web/alchemy.run.ts` の `observability` にある

| 課題   | 出すもの                                                                                                            |
| ------ | ------------------------------------------------------------------------------------------------------------------- |
| 不具合 | 入力と分岐を `Effect.annotateLogs` 付きの `Effect.logInfo` で出し、`Effect.withSpan` で経路を見て、テストで再現する |
| 遅さ   | `Effect.withSpan` の所要時間を変更の前後で比べ、ロジック単体は `vp test bench` で比べる                             |
| 新機能 | 受け入れテストに加え、成功と失敗を `Effect.annotateLogs` 付きのログで出し、Workers Logs で件数を集計する            |

## 標本

ログとトレースは、リクエストの一部だけを標本として残す。

- 計測のあいだだけサンプリング率を上げ、終わったら戻す
- 判断には、標本の件数が足りているかも添える

## 問い合わせ先

- 本番のログ、トレース、メトリクスは、`.mcp.json` の `cloudflare-observability` MCP サーバーで問い合わせる
- ほかの Cloudflare の API は `cloudflare-api` MCP サーバーで呼ぶ
- どちらも Alchemy のプロファイルの認証情報を使う
- デプロイした Worker のログを流して見るときは、`apps/web` で `vp exec alchemy logs --tail` を使う
- Effect のログとブラウザの console は、`vp run dev` のターミナルにも出る

## ブラウザ

`vp dlx @playwright/cli` で操作し、`console`、`requests`、`snapshot` で観測する。クラウド環境では、`.playwright/cli.config.json` の `launchOptions.executablePath` に `/opt/pw-browsers` の Chromium を書く。

`alchemy dev` が `CredentialsUnavailable` で止まったら、テストとログで計れる範囲を進める。画面を計れていないことをユーザーに伝える。
