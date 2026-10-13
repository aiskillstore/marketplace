---
name: egov-laws
description: e-Gov法令API v2(デジタル庁・認証不要)で日本の現行法令を引く。法令名検索、条文本文の取得(第709条など枝番つきも可)、時点指定(2017-04-01以降)、改正履歴(未施行の改正を含む)、条文本文の全文キーワード検索に対応。法律の解釈・判例・法的助言は対象外。国会での発言はkokkai、書誌はndl-booksを使う。
license: MIT
metadata:
  category: government
  locale: ja-JP
---

# egov-laws

e-Gov法令検索(デジタル庁)の公式API v2で、現行法令の条文を取得するスキル。APIキー・ログイン・ユーザー登録は一切不要。結果は条文そのもので、**法的な解釈や助言ではない**(判断は専門家に)。

**実測日: 2026-10-02。以下のURL・構造・件数はすべて当日の実測で確認。**

## エンドポイント

ベース: `laws.e-gov.go.jp/api/2`(HTTPS。仕様はSwagger UIが `https://laws.e-gov.go.jp/api/2/swagger-ui/` で公開)

| 用途 | パス | 備考 |
| --- | --- | --- |
| 法令一覧・名前検索 | `/laws?law_title=民法&limit=5` | 部分一致。総数は `total_count`(2026-10-02: 9,572法令) |
| 法令本文(全文) | `/law_data/{law_id}` | 民法で1.6MB。JSONの木構造 |
| 条・項だけ取得 | `/law_data/{law_id}?elm=Article[1]` | **Nは「第N条」ではなく「N番目の要素」(下の罠1)** |
| 時点指定 | `/law_data/{law_id}?asof=2017-04-01` | 2017-04-01以降のみ |
| 改正履歴 | `/law_revisions/{law_id}` | 施行済み+未施行の全リビジョン |
| 全文検索 | `/keyword?keyword=暴力&limit=3` | 条文本文のヒット(2026-10-02: 1,619法令) |

法令IDは `129AC0000000089`(民法)、`321CONSTITUTION`(日本国憲法)のような形式。

## 使い方(ヘルパー)

```bash
python3 egov-laws/lookup.py search 民法                      # 法令名検索
python3 egov-laws/lookup.py article 民法 709                  # 第709条の本文
python3 egov-laws/lookup.py article 民法 3の2                 # 枝番(第3条の2)
python3 egov-laws/lookup.py article 民法 4 --asof 2017-04-01  # 時点指定
python3 egov-laws/lookup.py revisions 民法                   # 改正履歴
python3 egov-laws/lookup.py keyword 暴力 --max 3              # 全文検索
```

`article` は全文を取って **Num属性(条番号)で本則から探す**。`elm=Article[N]` は使わない(罠1)。

## 実測で確認したこと (2026-10-02)

- 総数: 法令9,572件(法律2,144 / 政令2,444 / 府省令4,438 / 規則453 / 勅令71 ほか)。日本国憲法は103条。
- 民法の本則は1,173のArticle要素。条番号の最大は1050だが、枝番(第3条の2など)が181個、「第百七十条から第百七十四条まで 削除」のような範囲が `Num="170:174"` の1要素になっている箇所が8個ある。
- 民法のリビジョンは37個(施行済み32 + 未施行5。最後は2029-06-23施行)。`asof=2017-04-01` の第4条は「年齢二十歳」、現在は「年齢十八歳」。
- v1(`https://elaws.e-gov.go.jp/api/1/lawlists/1`)は2026-10-02時点でまだXMLを返す。ROADMAPに「v1は廃止済み」と書いていたが誤りで、公式にv1の終了告知は確認できない(2026-09-14の第三者調査でも同様)。ただしv2のほうが時点指定・改正履歴・全文検索があり、JSONで返る。

## 実測で確認した罠

1. **`elm=Article[N]` はN番目の要素で、第N条ではない。** 民法で `Article[709]` は**第643条(委任)**を返す。第709条(不法行為)は `Article[785]`。枝番・範囲削除が混ざるせいでずれる。さらに**リビジョンによってもずれる**: 第3条の2が入った今は `Article[4]` が第3条の2で、第4条(成年)は `Article[5]`、2017-04-01時点では `Article[4]` が第4条。条番号で取りたいなら全文を取ってNum属性で探す。
2. **存在しない要素は400。** `Article[1375]`(民法の最大は1374要素)や `Article[766_2]` は `{"code":"400021","message":"要素（elm）に合致する要素が法令本文に存在しません。"}` が返る。エラーは `code`/`message` の2項目だけのJSON(HTTP 400)。
3. **`asof` は2017-04-01以降のみ。** それ以前は `{"code":"400044","message":"法令の時点（asof）には2017-04-01以降を指定してください。"}`(HTTP 400)。
4. **有効なのに `PreviousEnforced`。** 一覧の `current_revision_status` が `CurrentEnforced` なのは8,916件、`Repeal` 559、`PreviousEnforced` 86、`UnEnforced` 11。民法・学校教育法・金融商品取引法などが該当し、施行日はすべて今日以前=実際は現行(`asof` なしで取れる本文も同じリビジョン)。サンプル12件のうち10件は未施行リビジョンを抱えていたが、全件の理由は未確認。`CurrentEnforced` だけで絞ると民法が消える。
5. **`law_title` は部分一致。** `民法` で11件(民法施行法や「…民法の特例に関する法律」を含む)。法令名は完全一致を選ぶ。
6. **条文は漢数字、項番号は全角。** 本文中は「第七百九条」「２」。取り出した後に数字を扱うなら正規化が要る。
7. **メンテナンス中はHTML。** 2026-10-02 02:31〜07:12 JSTの確認時は、APIがJSONではなく「システムメンテナンス中です」のHTML(HTTP 403)を返した。JSONとして読めなければ時間を置く。

## 失敗時の対応

- **JSONではない/403:** メンテナンス中の可能性。数時間後に再試行(2026-10-02は14:24 JSTの確認で復旧済み)。
- **法令名が一意に決まらない:** 候補が出るので、正式名称か `law_id` で指定する。
- **条が見つからない:** 本則にない。附則の条は対象外。条番号と枝番(`3の2`)を確認する。
- **古い時点が必要:** 2017-04-01より前はAPIでは取れない。

## English summary

Reads current Japanese statutes from the Digital Agency's e-Gov Law API v2 — no key or login. The helper searches law titles, fetches an article by its real article number (e.g. Civil Code Art. 709, branch articles like 3-2), supports point-in-time lookup (asof, 2017-04-01 or later), lists revision history including not-yet-enforced amendments, and runs full-text keyword search. Traps measured on 2026-10-02: elm=Article[N] is the N-th element, not Article N (Civil Code Article[709] returns Art. 643, and the index shifts between revisions), so look articles up by Num attribute; asof before 2017-04-01 returns HTTP 400; laws with pending amendments report PreviousEnforced even while in force (87 laws, including the Civil Code); and during maintenance the API returns an HTML page instead of JSON. Output is statute text, not legal advice. The older v1 API still responded on the same date.
