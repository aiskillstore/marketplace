# 동봉 폰트 라이선스 고지

이 폴더의 모든 폰트는 SIL Open Font License 1.1 (OFL) 하에 재배포됩니다. 각 폰트의 저작권자는 다음과 같습니다. 전체 감사 기록과 공식 출처는 [`references/font-licenses.md`](../../references/font-licenses.md) 참조.

| 폰트 | 저작권자 | 라이선스 |
|---|---|---|
| Pretendard | Kil Hyung-jin (길형진) | OFL 1.1 — 전문: `LICENSE-Pretendard-OFL.txt` |
| Noto Serif KR | Google / Adobe | OFL 1.1 |
| Paperlogy | Freesentation (김형진) | OFL 1.1 (폰트 내부 name 테이블에 명시) |
| Gmarket Sans | eBay Korea Co., Ltd. | OFL 1.1, RFN 선언 (공식 배포처: corp.gmarket.com/fonts — 동봉본은 공식 TTF판 원본) |
| Barlow | Jeremy Tribby | OFL 1.1 |

OFL 1.1 전문: https://openfontlicense.org/open-font-license-official-text/

**포맷 참고**: Pretendard·Noto Serif KR은 원배포(OTF/CFF)를 TrueType으로 변환한 Modified Version이다(`scripts/convert_fonts.py`, OFL 허용 — 두 서체 모두 Reserved Font Name 미선언, 라이선스·저작권 고지 유지). 변환 사유는 `references/font-licenses.md`의 TTF 전환 기록 참조.

KoPubWorld 서체(한국출판인회의)는 재배포 조건이 상충 판정되어 **동봉하지 않습니다** — 필요 시 `python3 scripts/fetch_fonts.py`로 공식 배포처에서 직접 내려받으세요. 동봉 폰트만으로 6개 스타일 전부 렌더 가능합니다.
