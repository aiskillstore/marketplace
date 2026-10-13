---
name: yubin-fee
description: 日本郵便の郵便料金(定形・定形外・ミニレター・レターパック・スマートレター・はがき)とオプション加算料金(速達・一般書留/簡易書留・特定記録)、ゆうパックのサイズ・地域別運賃を重量とサイズから調べる。切手代、郵便料金、何円の切手、送料、書留代、速達代の質問に対応。料金表はスキル内蔵(基準日明記)でAPIキー・ログイン不要。ゆうメール・国際郵便・本人限定受取などのオプションは対象外。
license: MIT
metadata:
  category: postal
  locale: ja-JP
  data_as_of: 2026-10-13
  valid_through: 2027-10-13
  source_version: "Japan Post postage 2024-10-01; Yu-Pack 2026-10-01"
---

# yubin-fee

日本郵便の基本的な郵便料金とオプション加算料金、ゆうパック運賃を重量・サイズ・差出地から調べるスキル。料金表を内蔵するので計算だけで答えられる。

**基準日: 郵便料金は2024-10-01の改定料金、オプション加算料金は2026-09-19確認、ゆうパック運賃は2026-10-01改定を2026-10-13に公式ページで確認。**
根拠URL: 手紙(第一種) https://www.post.japanpost.jp/send/domestic/charge/list/one_two.html ／ はがき https://www.post.japanpost.jp/service/send/domestic/mail/postcard/ ／ オプション加算料金一覧 https://www.post.japanpost.jp/send/domestic/charge/list/option.html ／ ゆうパック https://www.post.japanpost.jp/send/domestic/charge/list/parcel.html

**実測日: 2026-09-19。本文のコマンド・構造は実測で確認したものを収録(個所ごとの日付は各所の記載を参照)。**

## 料金表

### 定形郵便物(長辺14〜23.5cm × 短辺9〜12cm、厚さ1cm以内、50g以内)

| 重量 | 料金 |
| --- | --- |
| 50g以内 | 110円 |

### 定形外郵便物(規格内: 長辺34cm・短辺25cm・厚さ3cm・1kg以内 ／ 規格外: 長辺60cm以内、長辺+短辺+厚さ90cm以内、4kg以内)

| 重量 | 規格内 | 規格外 |
| --- | --- | --- |
| 50g以内 | 140円 | 260円 |
| 100g以内 | 180円 | 290円 |
| 150g以内 | 270円 | 390円 |
| 250g以内 | 320円 | 450円 |
| 500g以内 | 510円 | 660円 |
| 1kg以内 | 750円 | 920円 |
| 2kg以内 | (対象外) | 1,350円 |
| 4kg以内 | (対象外) | 1,750円 |

### その他の定番

| 種類 | 料金 | 条件 |
| --- | --- | --- |
| 通常はがき | 85円 | 全国一律(2026-09-11に公式ページで確認) |
| ミニレター(郵便書簡) | 85円 | 厚さ1cm・25gまで |
| レターパックライト | 430円 | 厚さ3cm・4kgまで |
| レターパックプラス | 600円 | 4kgまで(厚さ制限なし) |
| スマートレター | 210円 | 25×17cm・厚さ2cm・1kgまで |

## オプション加算料金(速達・書留・特定記録)

基本料金・基本運賃に加算する料金。**2026-09-19に公式「オプションサービスの加算料金一覧」( https://www.post.japanpost.jp/send/domestic/charge/list/option.html )と各サービスページで確認。**

### 速達

| 対象 | 重量 | 加算料金 |
| --- | --- | --- |
| 郵便物(手紙・はがき) | 250gまで | +300円 |
| 郵便物(手紙・はがき) | 1kgまで | +400円 |
| 郵便物(手紙・はがき) | 4kgまで | +690円 |
| ゆうメール | 1kgまで | +330円 |

### 書留(郵便物)

| 種類 | 加算料金 | 損害要償額 |
| --- | --- | --- |
| 一般書留 | +480円 | 10万円まで。以降5万円ごとに+23円(上限500万円) |
| 現金書留 | +480円 | 1万円まで。以降5,000円ごとに+11円(上限50万円) |
| 簡易書留 | +350円 | 5万円まで(実損額) |

- ゆうメールの書留: 一般書留 +420円、簡易書留 +350円(条件は郵便物と同じ)。
- 簡易書留は引受けと配達のみ記録する。一般・現金書留は引受けから配達までの送達過程を記録する。

### 特定記録

| 対象 | 加算料金 |
| --- | --- |
| 郵便物(手紙・はがき) | +210円 |
| ゆうメール | +160円 |

- 差出の記録(受領証)と追跡が付くが、**損害賠償はない**。配達は郵便受けへの投函で、配達の記録(受領印・署名)は残らない。
- 土曜・日曜・休日の配達は行わない(速達併用時などを除く)。

### オプションの組み合わせルール

- **速達は書留・特定記録と併用できる**(ほかに代金引換・引受時刻証明・配達証明・内容証明とも併用可)。
- **書留と特定記録は併用できない**。特定記録と併用できるのは速達と配達日指定だけ。
- 計算は「基本料金 + 各オプション加算料金」の単純な合計。

組み合わせの計算例(2026-09-19時点):

| 内容 | 計算 | 合計 |
| --- | --- | --- |
| 定形郵便を速達の一般書留で | 110円 + 300円 + 480円 | 890円 |
| 定形外(規格内)100gを特定記録で | 180円 + 210円 | 390円 |
| はがきを速達で | 85円 + 300円 | 385円 |
| 定形外(規格内)100gを簡易書留の速達で | 180円 + 350円 + 300円 | 830円 |

## ゆうパック

**2026-10-13に公式ページ( https://www.post.japanpost.jp/send/domestic/charge/list/parcel.html と基本運賃表(東京) https://www.post.japanpost.jp/service/domestic/charge/list/yu-pack/13.html )で確認。**

### サイズと重さ

- サイズは縦+横+高さの合計で決まる: 60 / 80 / 100 / 120 / 140 / 160 / 170サイズ(170cm以内)。
- 重さは25kg以内。25kg超30kg以内は重量ゆうパック(基本運賃+620円、公式: https://www.post.japanpost.jp/service/send/domestic/delivery/yu-pack/weight/index.html )。

### 基本運賃(東京から差し出す場合)

| お届け先 | 60 | 80 | 100 | 120 | 140 | 160 | 170 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 東京 | 840円 | 1,150円 | 1,480円 | 1,810円 | 2,160円 | 2,500円 | 3,060円 |
| 北海道 | 1,550円 | 1,880円 | 2,220円 | 2,570円 | 3,220円 | 3,610円 | 4,970円 |
| 東北・関東・信越・北陸・東海 | 970円 | 1,320円 | 1,650円 | 2,010円 | 2,600円 | 3,000円 | 3,680円 |
| 近畿 | 1,090円 | 1,440円 | 1,780円 | 2,130円 | 2,760円 | 3,130円 | 4,500円 |
| 中国・四国 | 1,270円 | 1,580円 | 1,960円 | 2,290円 | 2,930円 | 3,300円 | 4,670円 |
| 九州 | 1,550円 | 1,880円 | 2,220円 | 2,570円 | 3,220円 | 3,610円 | 4,970円 |
| 沖縄 | 1,600円 | 1,990円 | 2,480円 | 2,860円 | 3,430円 | 3,820円 | 5,870円 |

地域の内訳: 東北=青森/岩手/宮城/秋田/山形/福島、関東=茨城/神奈川/栃木/千葉/群馬/山梨/埼玉、信越=新潟/長野、北陸=富山/石川/福井、東海=静岡/岐阜/愛知/三重、近畿=滋賀/京都/兵庫/大阪/奈良/和歌山、中国=鳥取/島根/岡山/広島/山口、四国=香川/愛媛/徳島/高知、九州=福岡/佐賀/長崎/熊本/大分/宮崎/鹿児島。

- **他の都道府県から差し出す場合は運賃が異なる**(例: 大阪発は大阪の基本運賃表を使う)。このスキルに表があるのは東京発だけなので、他の差出地は公式の料金計算( https://www.post.japanpost.jp/cgi-simulator/youpack_choice.php )か各都道府県の基本運賃表で確認するよう案内し、推測で東京発の額を答えない。
- ゆうパックスマホ割: 郵便局アプリで決済すると基本運賃-180円。発送時に郵便局を受取場所に指定すると100円引、前月までの1年間に10個以上の発送があれば割引後運賃から10%引(継続利用割引)。

## 基本の流れ

1. ユーザーが送りたいものの種類(手紙/はがき/荷物)を聞くか推定する。
2. 荷物なら縦+横+高さの合計と差出地・お届け先を、郵便物ならサイズと重量から区分(定形/定形外の規格内・規格外)を決める。重量もサイズも条件を満たす必要がある(例: 30gでも厚さ1cm超なら定形外)。
3. 速達・書留・特定記録の希望を確認し、表から基本料金+加算料金を返す。判断に使った区分・重量帯・オプションを一緒に伝える。

## エラー・失敗時の対応

共通の取得時チェックリストは [共通レスポンス契約](../docs/response-contract.md) の「取得時の落とし穴チェックリスト」を参照。

- このスキルはネットワークを使わない。
- **区分が判定できない(サイズ不明など)**: 推測で料金を出さず、足りない条件(重量・厚さ・3辺合計・差出地)を聞き返す。条件が違えば料金は倍近く変わる。
- **ゆうパックで東京以外からの差出**: 内蔵表は東京発のみ。公式の料金計算ページを案内し、東京発の額をそのまま答えない。
- **表にないもの(ゆうメール運賃、国際郵便、本人限定受取・内容証明・代金引換など上記以外のオプション)**: 対象外と明示し、公式の料金ページ( https://www.post.japanpost.jp/send/domestic/charge/list/option.html )を案内する。

## 注意

- 料金は改定される。直近では2024-10-01に手紙・はがきが改定(定形郵便は50g以内110円の一律に統一)、2025-11-01にゆうメール運賃が改定されている。**2026-10-01のゆうパック改定を反映済み**(日本郵便のお知らせ: https://www.post.japanpost.jp/newsrelease/pressrelease/26283434137.html )。今後の改定日が判明したら `effective_until` に旧表の効力終了日を記録し、適用日以降は旧表を使わない。
- 表の料金を答えるときは「郵便料金は2024-10-01改定、ゆうパックは2026-10-01改定・2026-10-13確認」と基準日を必ず添える。改定の可能性がある話題(来年の予定など)では、公式ページの確認を促す。
- 切手の組み合わせ(何円切手を何枚)を聞かれたら、不足のない組み合わせを計算してよい。オプション加算分も同じ方針で合計に含めてよい。料金そのものを勝手に安く見せる組み方(過不足のある貼り方)は提案しない。

## English summary

Looks up Japan Post's domestic postage (letters, postcards, mini-letters, Letter Pack, Smart Letter), option surcharges (express, general/cash/simplified registered mail, delivery-record "tokutei-kiroku"), and Yu-Pack parcel fares from weight, size, and origin using built-in fee tables. No network access needed. Base postage is the 2024-10-01 revision (standard letters are a flat 110 yen up to 50g); option surcharges were checked on 2026-09-19; all 49 Tokyo-origin Yu-Pack fares were checked on 2026-10-13 against the 2026-10-01 revision - always state that basis date when answering. Combination rules are built in: express can stack with registered mail or tokutei-kiroku, but registered mail and tokutei-kiroku cannot be combined. The built-in Yu-Pack table covers parcels sent from Tokyo only (60-170 size, by destination region); for other origins, point users to the official fare calculator instead of guessing. The 2026-10-01 Yu-Pack revision is included, with a 620 yen heavy-parcel surcharge. Known future changes must set effective_until (exclusive) in metadata. Out of scope: Yu-Mail fares, international mail, and other options - point users to the official fee page. If weight, size, or origin is unknown, ask instead of guessing - the fee can nearly double across categories.
