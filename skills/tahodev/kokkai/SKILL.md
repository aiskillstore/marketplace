---
name: kokkai
description: 国会会議録検索システムの公式APIで国会議事録(第1回国会1947年〜最新)を検索する。発言本文のキーワード・発言者・会議名・院・開催日・回国数での検索に対応し、発言単位/会議単位/会議一覧の3モードで返す。APIキー・ログイン不要。法律の条文そのものはegov-laws、書誌はndl-booksを使う。投票結果・議員個人の属性情報は対象外。
license: MIT
metadata:
  category: government
  locale: ja-JP
---

# kokkai

国会会議録検索システム(国立国会図書館)の公式APIで、国会の全会議録・全発言を検索するスキル。第1回国会(1947年)から最新までカバーし、APIキー・ログイン・ユーザー登録は一切不要。

**実測日: 2026-10-01。以下のURL・構造・件数はすべて当日の実測で確認。**

## エンドポイント(3つ、使い分けが本質)

| モード | URL | 返るもの | 最大件数 |
| --- | --- | --- | --- |
| 発言単位 | `https://kokkai.ndl.go.jp/api/speech` | ヒットした発言の本文+会議情報 | 100 |
| 会議単位 | `https://kokkai.ndl.go.jp/api/meeting` | 会議録+**全発言の本文** | 10 |
| 会議一覧 | `https://kokkai.ndl.go.jp/api/meeting_list` | 会議の情報のみ(軽量) | 100 |

既定はXML。**`recordPacking=json` を必ず付ける**。件数未指定だとspeech/listは30件、meetingは3件。

## 使い方(ヘルパー)

```bash
python3 kokkai/lookup.py --any 憲法 --max 3                 # 発言検索
python3 kokkai/lookup.py --speaker 山田 --house 参議院       # 発言者+院
python3 kokkai/lookup.py --meeting 本会議 --mode list        # 会議一覧
python3 kokkai/lookup.py --any 科学技術 --mode meeting --max 1  # 会議+全発言
python3 kokkai/lookup.py --any 防災 --from-date 2026-01-01 --until-date 2026-03-31
```

## 実測で確認したこと (2026-10-01)

- `any=国会`: **608,479発言**。`any=憲法`: 184,057。`any=消費税`: 62,548(うち参議院 26,928)。
- 最古は第1回国会(1947年)。最新の本会議は2026-07-24(第221回)、委員会を含む最新発言は2026-08-26。**収録には約1か月のラグがある**。
- 本会議だけで8,886会議。宮沢賢治が国会で言及された発言は69件。
- `speaker=山田` は部分一致で50,286件(山田吉彦ほか)。姓名フルネームで渡すのが安全。

## 実測で確認した罠

1. **3エンドポイントの最大件数が違う。** speech/listは100、meetingは10。`maximumRecords=101` を渡すと **HTTP 400** で `{"message":"(19011)検索条件の入力に誤りがあります。","details":["...maximumRecordsには1～100の値を指定してください。"]}` が返る(2026-10-01実測)。エラーは日本語で具体的。
2. **`any` はスペース区切りでAND、`nameOfMeeting` はスペース区切りでOR。** 逆なので注意(実測: any=北海道 青森 → 両方を含む発言3,867件(2026-10-05再実測。「北海道」単独115,795件・「青森」単独18,908件より少ないのでAND)、nameOfMeeting=文部 文教 → どちらかを含む会議)。
3. **`any` の検索対象は発言本文だけ。** 会議名・発言者は別パラメータ(`nameOfMeeting` / `speaker`)。
4. **既定はXML。** `recordPacking=json` を忘れるとXMLが返る。
5. **speechIDに日付と回次が埋まっている。** `121704080X00920250411_169` = 第121回・2025-04-11。発言を一意に参照するIDとして使える。
6. **掲載ラグ約1か月。** 「昨日の国会で何が言われたか」はまだ取れないことが多い。最新日を確認してから答える。

## 失敗時の対応

- **0件:** キーワードの表記(漢字/かな)を変える。発言は話し言葉なので「熱中症」より「暑さ」に多い、ということがある。日付範囲を広げる。
- **HTTP 400:** detailsに理由が書いてある(maximumRecordsの範囲、日付形式など)。そのまま直す。
- **結果が古い:** 収録ラグ(約1か月)。`until` を指定せず最新日を確認し、「2026-08-26時点の収録では」と時点つきで答える。

## English summary

Searches Japan's National Diet proceedings via the official Kokkai (National Diet Library) API — no API key or login. Covers all sessions from the 1st Diet (1947) to the present, with three endpoints: speech-level search (full-text, max 100), meeting-level (returns every speech in the meeting, max 10), and meeting list (lightweight metadata, max 100). Filters: full-text keyword (space-separated AND), speaker (partial match), meeting name (space-separated OR), house, date range, session number. Always pass recordPacking=json — XML is the default. Traps: per-endpoint record caps (over-limit returns HTTP 400 with a Japanese error message), any vs nameOfMeeting use opposite space semantics, and new proceedings appear with roughly a one-month lag (latest record 2026-08-26 as of 2026-10-01). Measured live on 2026-10-01.
