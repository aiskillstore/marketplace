#!/usr/bin/env python3
"""国会会議録検索システムAPI(国会議事録)を検索するヘルパー。

使い方:
  python3 kokkai/lookup.py --any 憲法 --max 3            # 発言検索(全文対象)
  python3 kokkai/lookup.py --speaker 山田 --house 参議院  # 発言者+院で絞る
  python3 kokkai/lookup.py --meeting 東日本大震災 --mode list   # 会議録一覧(軽量)
  python3 kokkai/lookup.py --any 科学技術 --mode meeting --max 1 # 会議録+全発言
  python3 kokkai/lookup.py --any 防災 --from-date 2026-01-01 --until-date 2026-03-31
  python3 kokkai/lookup.py --any 憲法 --start 101 --max 100     # ページング

外部パッケージ不要。APIキー・ログイン・ユーザー登録不要。
実測日: 2026-10-01 (speech/meeting/meeting_list ともに同日実測)
"""
import argparse, json, sys, urllib.request, urllib.parse, urllib.error

BASE = "https://kokkai.ndl.go.jp/api"
UA = {"User-Agent": "kurashi-skill/kokkai"}

def fetch_json(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
    except urllib.error.HTTPError as e:
        raw = e.read()  # 400でも読めるJSONエラーが返る(実測: maximumRecords=101 -> 400)
    d = json.loads(raw)
    if "message" in d:  # APIエラー形式 {"message": "(19011)...", "details": [...]}
        raise SystemExit(json.dumps({"error": d["message"], "details": d.get("details", [])}, ensure_ascii=False))
    return d

def build_url(mode, args):
    params = {"recordPacking": "json"}
    if args.any:
        params["any"] = " ".join(args.any)     # スペース区切りでAND(実測: 北海道 青森=両方含む)
    if args.speaker:
        params["speaker"] = args.speaker        # 部分一致(実測: 山田 -> 山田吉彦 ほか50,286件)
    if args.meeting:
        params["nameOfMeeting"] = args.meeting  # スペース区切りでOR(実測: 文部 文教)
    if args.house:
        params["nameOfHouse"] = args.house      # 衆議院 / 参議院 / 両院
    if args.from_date:
        params["from"] = args.from_date
    if args.until_date:
        params["until"] = args.until_date
    if args.session:
        params["session"] = str(args.session)   # 回国数(例: 221)
    params["startRecord"] = str(args.start)
    params["maximumRecords"] = str(args.max)
    return f"{BASE}/{mode}?" + urllib.parse.urlencode(params)

def slim_speech(r):
    return {k: r.get(k, "") for k in
            ("speechID", "date", "session", "nameOfHouse", "nameOfMeeting", "issue",
             "speaker", "speakerYomi", "speakerGroup", "speakerPosition", "speakerRole",
             "speechOrder", "startPage", "speech", "speechURL", "meetingURL", "pdfURL")}

def slim_meeting(m, with_speeches):
    out = {k: m.get(k, "") for k in
           ("issueID", "date", "session", "nameOfHouse", "nameOfMeeting", "issue",
            "closing", "meetingURL", "pdfURL")}
    if with_speeches:
        out["speech_count"] = len(m.get("speechRecord", []))
        out["speeches"] = [slim_speech(s) for s in m.get("speechRecord", [])]
    return out

def main():
    ap = argparse.ArgumentParser(description="国会会議録検索API")
    ap.add_argument("--any", nargs="+", help="発言本文のキーワード(スペース区切りでAND)")
    ap.add_argument("--speaker", help="発言者名(部分一致)")
    ap.add_argument("--meeting", help="会議名(スペース区切りでOR)")
    ap.add_argument("--house", choices=["衆議院", "参議院", "両院"], help="院で絞る")
    ap.add_argument("--from-date", help="開催日From (YYYY-MM-DD)")
    ap.add_argument("--until-date", help="開催日Until (YYYY-MM-DD)")
    ap.add_argument("--session", type=int, help="回国数で絞る")
    ap.add_argument("--mode", choices=["speech", "meeting", "list"], default="speech",
                    help="speech=発言単位(既定), meeting=会議+全発言(最大10件), list=会議一覧(軽量)")
    ap.add_argument("--start", type=int, default=1, help="開始位置(1始まり)")
    ap.add_argument("--max", type=int, default=3, help="件数(speech/list: 1-100, meeting: 1-10)")
    args = ap.parse_args()
    if not (args.any or args.speaker or args.meeting or args.from_date or args.session):
        ap.error("--any / --speaker / --meeting / --from-date / --session のいずれかが必要")
    endpoint = {"speech": "speech", "meeting": "meeting", "list": "meeting_list"}[args.mode]
    url = build_url(endpoint, args)
    d = fetch_json(url)
    out = {"query_url": url, "total": d.get("numberOfRecords"),
           "returned": d.get("numberOfReturn"), "next_start": d.get("nextRecordPosition")}
    if args.mode == "speech":
        out["speeches"] = [slim_speech(r) for r in d.get("speechRecord", [])]
    else:
        out["meetings"] = [slim_meeting(m, args.mode == "meeting") for m in d.get("meetingRecord", [])]
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()

if __name__ == "__main__":
    main()
