from pathlib import Path
#!/usr/bin/env python3
"""kokkai lookup.py のパース・URL構築・エラー処理の回帰テスト(ネットワーク不要、fixture使用)。"""
import json, os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import lookup

FIX = os.path.join(os.path.dirname(__file__), "fixtures")

class SpeechParseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(Path(FIX, "speech_kenpo.json").read_text(encoding="utf-8"))

    def test_totals(self):
        # 2026-10-01実測: any=憲法 -> 184,057件
        self.assertEqual(self.d["numberOfRecords"], 184057)
        self.assertEqual(self.d["numberOfReturn"], 2)
        self.assertEqual(self.d["nextRecordPosition"], 3)

    def test_slim_fields(self):
        r = lookup.slim_speech(self.d["speechRecord"][0])
        for k in ("speechID", "date", "session", "nameOfHouse", "nameOfMeeting",
                  "speaker", "speech", "speechURL"):
            self.assertIn(k, r)
        self.assertTrue(r["speechURL"].startswith("https://kokkai.ndl.go.jp/"))

class MeetingParseTest(unittest.TestCase):
    def test_meeting_with_speeches(self):
        d = json.loads(Path(FIX, "meeting_higashinihon.json").read_text(encoding="utf-8"))
        m = d["meetingRecord"][0]
        out = lookup.slim_meeting(m, with_speeches=True)
        self.assertEqual(out["speech_count"], 3)
        self.assertEqual(len(out["speeches"]), 3)
        out2 = lookup.slim_meeting(m, with_speeches=False)
        self.assertNotIn("speeches", out2)

class UrlBuildTest(unittest.TestCase):
    def _args(self, **kw):
        class A: pass
        a = A()
        a.any = None; a.speaker = None; a.meeting = None; a.house = None
        a.from_date = None; a.until_date = None; a.session = None
        a.start = 1; a.max = 3
        for k, v in kw.items():
            setattr(a, k, v)
        return a

    def test_json_param_and_endpoint(self):
        url = lookup.build_url("speech", self._args(any=["憲法"]))
        self.assertTrue(url.startswith("https://kokkai.ndl.go.jp/api/speech?"))
        self.assertIn("recordPacking=json", url)

    def test_any_space_join_is_and(self):
        # 実測: any=北海道 青森 はAND(両方含む発言3,867件、2026-10-05再実測)
        url = lookup.build_url("speech", self._args(any=["北海道", "青森"]))
        self.assertIn("any=%E5%8C%97%E6%B5%B7%E9%81%93+%E9%9D%92%E6%A3%AE", url)

    def test_meeting_list_endpoint(self):
        url = lookup.build_url("meeting_list", self._args(meeting="本会議"))
        self.assertIn("/api/meeting_list?", url)

class ErrorShapeTest(unittest.TestCase):
    def test_error_fixture(self):
        # 実測: maximumRecords=101 -> HTTP 400 + このJSON
        d = json.loads(Path(FIX, "error_maxrecords.json").read_text(encoding="utf-8"))
        self.assertIn("maximumRecordsには1～100", d["details"][0])
        self.assertNotIn("speechRecord", d)

if __name__ == "__main__":
    unittest.main()
