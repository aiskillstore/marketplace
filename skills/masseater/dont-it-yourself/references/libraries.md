# よく使うもの

よくある場面とそこで使うものの参照である。

- 配列、オブジェクト、文字列のユーティリティ（`groupBy`、`chunk`、`debounce`、deep merge、深い等価比較）: `es-toolkit`
- 外から入ってくる値の解析と検証（URL、メールアドレス、日付の文字列、JSONの形）: `Schema`
- 環境変数や設定値の読み込み: `Config`
- 秘密の値を持ち回り、ログに出さないようにする: `Redacted`
- 日付、時刻、タイムゾーン、期間の計算と整形: `DateTime`、`Duration`
- リトライとバックオフ: `Effect.retry` と `Schedule.exponential`、`Schedule.jittered`
- cron式の解析と次の実行時刻: `Cron`
- base64やhexのエンコードとデコード: `Encoding`
- UUID、乱数、ランダムな文字列: `crypto.randomUUID`、`Random`、`Encoding.randomHex`
- ハッシュ、署名、暗号化: `crypto.subtle`
- 同時実行数の制限、ロック、キュー、キャッシュ: `Semaphore`、`Queue`、`Cache`
- 値の形による分岐: `Match`
- YAMLの読み書き: `yaml`
- Markdownの解析と変換: `remark`
- シェルに渡す文字列のエスケープ: `shell-quote`
- CLIの引数とサブコマンドの解析: `citty`
- 外部HTTPのモック: `msw`
- 外部APIやSaaSをEffectから呼ぶクライアント: `@distilled.cloud/<サービス名>` に生成済みのSDKがあればそれを使う。無ければ、公開されているOpenAPIから `@effect/openapi-generator` の `openapigen` で生成する
- SQLの組み立てとマイグレーション: `drizzle-orm`
- 認証、セッション、パスキー、APIキー: `better-auth`
- TOTP: `otpauth`
- サーバーから取ってきたデータの取得とキャッシュ: `@tanstack/react-query`
- フォームの状態と入力チェック: `@tanstack/react-form`
- テーブルの並べ替え、絞り込み、ページ送り: `@tanstack/react-table`
- 長いリストの仮想スクロール: `@tanstack/react-virtual`
- Reactでのdebounce、throttle、rate limit: `@tanstack/react-pacer`
