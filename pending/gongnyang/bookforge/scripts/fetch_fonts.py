#!/usr/bin/env python3
"""bookforge font fetcher.

Bundled in assets/fonts/ (OFL, redistributable): Pretendard, Noto Serif KR,
Paperlogy, Gmarket Sans — nothing to fetch for the default themes.

This script fetches CONDITIONAL fonts that must NOT be redistributed in this
repo (license requires direct download from the official source):
  - KoPubWorld 바탕/돋움 (한국출판인회의) -> assets/fonts/fetched/

Run: python3 scripts/fetch_fonts.py
See references/font-licenses.md for the license audit.
"""
import io, sys, urllib.request, zipfile
from pathlib import Path

FETCHED = Path(__file__).resolve().parent.parent / "assets" / "fonts" / "fetched"

KOPUB_URL = "https://www.kopus.org/wp-content/uploads/2021/12/KoPubWorld-%EC%84%9C%EC%B2%B4_ttf.zip"

def main():
    FETCHED.mkdir(parents=True, exist_ok=True)
    have = list(FETCHED.glob("KoPubWorld*"))
    if have:
        print(f"already fetched: {len(have)} KoPubWorld files")
        return
    print("KoPubWorld 서체를 한국출판인회의 공식 배포처에서 내려받습니다.")
    print("라이선스: 무료 사용 가능하나 재배포 조건이 상충 판정 → 레포 미동봉, 로컬 fetch 전용.")
    print("자세한 조건: https://www.kopus.org/biz/electronic/font/")
    try:
        req = urllib.request.Request(KOPUB_URL, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=120).read()
        zf = zipfile.ZipFile(io.BytesIO(data))
        n = 0
        for name in zf.namelist():
            base = Path(name).name
            if base.lower().endswith((".ttf", ".otf")) and "KoPubWorld" in base:
                (FETCHED / base).write_bytes(zf.read(name))
                n += 1
        print(f"OK: {n} fonts -> {FETCHED}")
    except Exception as e:
        print(f"FETCH FAIL ({e}). 수동 다운로드: https://www.kopus.org/biz/electronic/font/", file=sys.stderr)
        print("KoPubWorld 없이도 모든 테마는 동봉 폰트(Pretendard·Noto Serif KR·Paperlogy·Gmarket Sans)로 렌더됩니다.")
        sys.exit(1)

if __name__ == "__main__":
    main()
