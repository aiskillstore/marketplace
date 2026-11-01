# search-and-sharing

検索エンジンに掲載するかどうかと、リンクを共有したときの表示を確認する。決めておかないと、掲載したくないページが掲載され、掲載したいページは内容のないまま掲載される。基準は [Google 検索の基本事項](https://developers.google.com/search/docs/essentials) と [Open Graph protocol](https://ogp.me/) に従う。

| 確認する事項 | 現状の確認方法 | 充足条件 |
| --- | --- | --- |
| 検索エンジンへの掲載 | 本番の `robots.txt`、各ページの `meta name="robots"`、`X-Robots-Tag` ヘッダーを確認する | requirements の利用者と目的に合わせて掲載するページとしないページが決まっていて、そのとおりに設定されている |
| 掲載するページの内容 | 本番の HTML を `curl` で取得し、本文、title、description、canonical があるかを確認する | JavaScript を実行しなくても、本文とメタデータが HTML に含まれている |
| 共有したときの表示 | 本番の HTML の OGP タグを確認し、og:image の URL を開く | og:title、og:description、og:image があり、画像が返る |
