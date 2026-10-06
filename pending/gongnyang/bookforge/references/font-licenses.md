# 폰트 라이선스 대장 (font-licenses)

> bookforge가 PDF에 임베드하는 서체의 법적 사용 조건. **확인 일자: 2026-08-09**
> 결론은 전부 공식 소스(공식 사이트 · 공식 GitHub · 폰트 파일 내부 `name`/`OS/2` 테이블)에서 확정했다. 눈누(noonnu.cc) 등 3자 집계 사이트는 단서로만 썼고, 눈누만으로 판정한 항목은 없다.

## 판정 요약

| 폰트 | 라이선스 | PDF 임베드 | 공개 레포 동봉 | 판정 |
|---|---|---|---|---|
| **Pretendard** | SIL OFL 1.1 | 허용 | 허용 | **동봉 가능** |
| **Noto Serif KR** | SIL OFL 1.1 | 허용 | 허용 | **동봉 가능** |
| **KoPubWorld 바탕/돋움** | 자체 약관(버전 표기 없음) | 조건부 | 조건부 | **fetch만** |
| **Paperlogy** | SIL OFL 1.1 | 허용 | 허용 | **동봉 가능** |
| **Gmarket Sans** | SIL OFL 1.1 | 허용 (fsType=4) | 허용 | **동봉 가능** |
| **나눔고딕 / 나눔명조** | SIL OFL 1.1 | 허용 | 허용 | **동봉 가능** |
| **Libertinus Serif** (Typst 내장) | SIL OFL 1.1 | 허용 | 미동봉(Typst 배포에 포함) | academic 라틴 영숫자에 임베드됨 |
| **DejaVu Sans Mono** (Typst 내장) | Bitstream Vera 파생(자유 사용·재배포 허용) | 허용 | 미동봉(Typst 배포에 포함) | 코드 폰트 라틴 영숫자에 임베드됨 |

`fsType`은 폰트 `OS/2` 테이블의 임베드 허용 비트. 8 = Editable embedding, 4 = Preview & Print embedding. **둘 다 PDF 출력·열람용 임베드에는 문제가 없다.**

**Typst 내장 폰트 주의**: Libertinus·DejaVu는 assets/fonts가 아니라 **Typst 바이너리에 내장**된 서체로, `--ignore-system-fonts`로도 배제되지 않는다. Typst 버전이 바뀌면 내장 세트가 바뀔 수 있으므로 Typst는 **0.14.x 계열로 고정**한다(SKILL.md 실행 전 점검).

**TTF 전환 기록(v2, 2026-08-16)**: Chromium print-to-PDF가 CFF(.otf)를 서브셋하지 못해 Type3 글리프로 폴백(텍스트 추출·검색 불능, G2 무효)하는 문제로 동봉 폰트를 전량 TrueType으로 전환했다. Pretendard·Noto Serif KR은 **RFN(Reserved Font Name) 미선언** → `scripts/convert_fonts.py`(fontTools cu2qu, `MAX_ERR=1.0` 절대 unit — em 2048인 Pretendard는 1/2048em, em 1000인 Noto Serif KR은 1/1000em으로 2배 느슨)로 변환한 Modified Version을 OFL 조건(라이선스·저작권 고지 유지) 하에 동봉. **Gmarket Sans는 RFN 선언**("Gmarket Sans Font") → 변환판 재배포 불가, 공식 배포처의 TTF판(GmarketSansTTF*.ttf, 내부 패밀리명 "Gmarket Sans TTF")을 동봉하고 테마 @font-face에서 별칭으로 소비한다.

---

## 1. Pretendard — 동봉 가능

| 항목 | 내용 |
|---|---|
| 라이선스 | SIL Open Font License 1.1 |
| PDF 임베드 | 허용. OFL §Permission이 "use, study, copy, merge, **embed**, modify, redistribute"를 명시 |
| 레포 재배포 | 허용 (OFL 전문 `LICENSE` 동봉 조건) |
| 공식 다운로드 | https://github.com/orioncactus/pretendard/releases/latest (최신 v1.3.9) |
| 라이선스 원문 | https://raw.githubusercontent.com/orioncactus/pretendard/main/LICENSE |
| 고지 의무 | OFL 전문 + 저작권 4줄 동봉 |

저작권 원문: `Copyright (c) 2021, Kil Hyung-jin (https://github.com/orioncactus/pretendard), with Reserved Font Name 'Pretendard'.` — 여기에 Adobe(`Source`) / Inter Project Authors(`Inter`) / M+ FONTS Project Authors(`M PLUS 1`) 3건이 병기되어 있다.

⚠ **RFN 4종**: `Pretendard`, `Source`, `Inter`, `M PLUS 1`. 서브셋·개변 후에도 이 이름을 유지하면 OFL 위반이다. 배포물에 라이선스 파일이 **포함되어 있다**.

---

## 2. Noto Serif KR — 동봉 가능

| 항목 | 내용 |
|---|---|
| 라이선스 | SIL Open Font License 1.1 (`METADATA.pb`에 `license: "OFL"`) |
| PDF 임베드 / 레포 재배포 | 둘 다 허용 |
| 공식 다운로드 (notofonts) | https://github.com/notofonts/noto-cjk/releases/download/Serif2.003/13_NotoSerifKR.zip |
| 공식 다운로드 (Google Fonts) | https://fonts.google.com/download?family=Noto%20Serif%20KR |
| 라이선스 원문 | https://raw.githubusercontent.com/google/fonts/main/ofl/notoserifkr/OFL.txt |
| 고지 의무 | `OFL.txt` 동봉 |

저작권: google/fonts 정본 헤더 `Copyright 2012 Google Inc. All Rights Reserved.` / METADATA.pb 폰트 저작권 `(c) 2017-2024 Adobe (http://www.adobe.com/).`

✅ **RFN 지정 없음**(google/fonts OFL.txt 헤더에 Reserved Font Name 절 부재) → 개변 시 이름 변경 강제 없음. 배포물에 라이선스 **포함**.

---

## 3. KoPubWorld 바탕체 / 돋움체 — fetch만 ⚠ 공식 문서 2건이 충돌

**이번 조사 최대 리스크.** kopus.org 웹페이지 본문과, 그 페이지가 링크한 라이선스 약관 PDF의 내용이 어긋난다.

**(A) 약관 PDF 제4조** — https://www.kopus.org/wp-content/uploads/2021/04/서체_라이선스.pdf
> "서체 소프트웨어의 수정 혹은 수정되지 않은 복사본을 무료로 사용, 연구, 복사, 통합, **삽입, 수정, 재배포**할 수 있도록 허가합니다."
> "④ … 본 라이선스 하에 배포가 되어야 하며 기타 다른 라이선스 하에서는 배포를 할 수 없습니다. 본 서체 및 수정본을 배포 또는 전송하는 경우에는 **배포 또는 전송받는 자에게 약관을 안내하여야 합니다.**"
> "① … 유료로 판매하는 등 상업적 행위는 사전 동의가 있지 않는 한 금지합니다." / "② … 사전 동의 없이 'KoPub', 'KoPubWorld' 이름을 사용해서는 안 됩니다."

**(B) kopus.org 「라이선스 안내」 웹페이지 본문** (현재 라이브)
> "다만, **사전승인 없이 폰트를 수정, 변형하는 것은 불가**하며, 폰트 자체를 유료로 판매, 양도하는 모든 상업적 행위는 금지합니다."
> "단, **서체를 서버에 탑재한 후 웹서비스 및 프로그램 내 서비스 등 임베이딩하여 사용할 경우 별도의 승인이 필요합니다.**"
> "정확한 사용조건은 서체 라이선스 약관을 참고하시기 바랍니다."

| 항목 | 내용 |
|---|---|
| 라이선스 | 「'KoPub서체' 및 'KoPubWorld서체' 라이선스 약관」 — **버전 표기 없음**, OFL 아님 |
| PDF 임베드 | **조건부 허용.** 전자책·인쇄물 결과물로서의 임베드는 허용 범위(약관 §4 "삽입", 웹페이지 "종이책, 전자책, 인쇄물, 광고물, 온라인 등 상업적 목적 사용 가능"). 파일 `fsType=8`로 기술적 제한도 없음. **단 웹서비스 서버 탑재형 임베딩은 별도 승인 필요** |
| 레포 재배포 | **조건부.** 약관 §4는 허용(약관 안내 동반 조건), 웹페이지 본문은 재배포를 명시하지 않음 |
| 공식 다운로드 | TTF https://www.kopus.org/wp-content/uploads/2026/04/KOPUBWORLD_TTF_FONTS2026.zip · OTF https://www.kopus.org/wp-content/uploads/2026/04/KOPUBWORLD_OTF_FONTS2026.zip |
| 공식 페이지 / 사용 등록 | https://www.kopus.org/biz-electronic-font2/ · https://forms.gle/aQU7b3EoaF53zMKaA |
| 고지 의무 | `Copyright (c) 2018 한국출판인회의. All rights reserved. Font designed by FONTRIX Inc.` 표시 + 배포 시 **약관 전문(PDF)을 수령자에게 안내**. 지적재산권 귀속: 문화체육관광부 + 한국출판인회의. 상표: `KoPubWorldBatang/Dotum is a registered trademark of Korea Publisher Society` |

⚠ 배포 zip에 **라이선스 파일이 동봉되어 있지 않다**(ttf 6개만 존재).

**결론: fetch만.** 자체 약관 + 사용 등록(구글 폼) 요구 + 문서 간 충돌 + zip에 라이선스 미동봉. 공개 레포에는 다운로드 스크립트만 두고, 꼭 동봉해야 한다면 한국출판인회의 사전 확인을 받을 것.

---

## 4. Paperlogy — 동봉 가능

제작 = 이주임(PT&) / 김도균. 한글은 **G마켓 산스**, 영문 Montserrat, 일문 M PLUS 2 기반 파생작(원본이 모두 OFL이라 파생 자체가 적법).

| 항목 | 내용 |
|---|---|
| 라이선스 | SIL Open Font License 1.1 (폰트 name ID 13: "이 글꼴은 SIL Open Font License 1.1로 배포하고 있습니다.") |
| PDF 임베드 / 레포 재배포 | 둘 다 허용 (`fsType=8`) |
| 공식 다운로드 | https://github.com/Freesentation/paperlogy/raw/refs/heads/main/Paperlogy-1.001.zip (9웨이트 Thin~Black) |
| 공식 소개 | https://freesentation.blog/paperlogy |
| 고지 의무 | `OFL license.txt` 동봉. 저작권 `Copyright 2024 The PAPERLOGY Authors (https://freesentation.blog/paperlogy)` |

공식 소개 문구: "모든 상업적 행위 및 수정, 재배포" 가능, 단 **"글꼴 단독 판매 또는 글꼴 라이선스 변경"** 금지.

✅ **RFN 지정 없음** → 개변 시 이름 변경 강제 없음. 배포물에 라이선스 **포함**.

---

## 5. Gmarket Sans — 동봉 가능

⚠ **정정**: 흔히 "지마켓 자체 라이선스"로 알려져 있으나, 공식 페이지와 폰트 내부 메타데이터 모두 **SIL OFL 1.1**로 확인된다.

| 항목 | 내용 |
|---|---|
| 라이선스 | SIL Open Font License 1.1 |
| PDF 임베드 | 허용. `fsType=4` = **Preview & Print embedding**만 기술 허용 — PDF 출력·열람 임베드는 정상, "편집 가능 임베드"는 비트상 미허용. PDF 산출물 용도로는 문제 없음 |
| 레포 재배포 | 허용 |
| 공식 다운로드 | TTF https://corp.gmarket.com/fonts/GmarketSansTTF.zip · OTF https://corp.gmarket.com/fonts/GmarketSansOTF.zip |
| 공식 페이지 | https://corp.gmarket.com/fonts/ · https://gds.gmarket.co.kr/brand/typeface |
| 고지 의무 | OFL 전문 + 저작권 동봉. **zip에 라이선스 파일이 없으므로 직접 넣어야 한다** |

폰트 name ID 13 원문: `Copyright © <2019.>, <eBay Korea Co., Ltd.> (<www.gmarket.co.kr>), with Reserved Font Name <Gmarket Sans Font>. This Font Software is licensed under the SIL Open Font License, Version 1.1.`

공식 페이지: "Gmarket Sans는 **'SIL Open Font License'에 따라** 개인 또는 기업이 영리적, 비영리적 목적으로 자유롭게 사용할 수 있습니다."
폰트 내부 한국어 요약: 가능 = 상업적 사용(인쇄물·광고물·온라인·영상 포함 **수정 및 배포**) / 불가 = **서브라이선스, 단독판매, 상표권 이용** / 필수 = **라이선스 포함, 수정 시 명칭 변경**.

⚠ **RFN**: `Gmarket Sans Font`.
※ `corp.gmarket.com/fonts/` HTML 소스에 "누구나 제약 없이 자유롭게 수정하고 재배포 하실 수 있습니다"라는 더 강한 문구가 있으나 **주석 처리되어 미노출** 상태다. 근거로 인용하지 말 것.

---

## 6. 나눔고딕 / 나눔명조 — 동봉 가능 (참고용)

| 항목 | 내용 |
|---|---|
| 라이선스 | SIL Open Font License 1.1 (지적재산권: 네이버·네이버문화재단) |
| PDF 임베드 / 레포 재배포 | 둘 다 허용 (`fsType=8`), 공식 라이선스 전문에 명시 |
| 공식 다운로드 | 고딕 https://hangeul.naver.com/hangeul_static/webfont/zips/nanum-gothic.zip · 명조 https://hangeul.naver.com/hangeul_static/webfont/zips/nanum-myeongjo.zip |
| 라이선스 전문 | https://help.naver.com/support/contents/contents.help?serviceNo=1074&categoryNo=3497 (공식 페이지 https://hangeul.naver.com/font) |
| 고지 의무 | 라이선스 전문 + 저작권 안내 동봉 |

공식 원문: `Copyright (c) 2010, NAVER Corporation (https://www.navercorp.com/) with Reserved Font Name Nanum, Naver Nanum, NanumGothic, Naver NanumGothic, NanumMyeongjo, Naver NanumMyeongjo, … licensed under the SIL Open Font License, Version 1.1.`

핵심 문구: "**본 저작권 안내와 라이선스 전문을 포함해서** 다른 소프트웨어와 번들하거나 재배포 또는 판매가 가능하고 자유롭게 수정, 재배포하실 수 있습니다." / "글꼴 자체를 유료로 판매하는 것을 제외한 상업적인 사용이 가능". 전문 포함이 어려우면 출처 표기 권장 — 예문: "이 페이지에는 네이버에서 제공한 나눔글꼴이 적용되어 있습니다."

⚠ `github.com/naver/nanumfont`은 **나눔고딕코딩체 전용 레포**로 본체가 없다(README만). 정본은 hangeul.naver.com.
부수 조항: "나눔글꼴을 사용한 인쇄물, 광고물의 이미지는 나눔글꼴 프로모션에 활용될 수 있습니다"(거부 요청 가능).

---

## bookforge 실무 규칙

1. **라이선스 파일을 직접 만들어야 하는 폰트**: Gmarket Sans, 나눔고딕/나눔명조 — 배포 zip에 라이선스가 없다. 각 폰트의 저작권 줄 + RFN을 넣은 `OFL.txt`를 함께 커밋해야 OFL 조건을 충족한다. Pretendard·Paperlogy·Noto Serif KR은 배포물에 포함되어 있다.
2. **KoPubWorld는 별도 취급** — 레포에 커밋하지 말고 빌드 시 공식 URL fetch. 동봉이 필요하면 한국출판인회의 사전 확인.
3. **RFN(Reserved Font Name) 주의** — 서브셋팅/개변 후 원래 이름을 유지하면 OFL 위반. 해당: Pretendard(4종), Gmarket Sans(`Gmarket Sans Font`), 나눔(다수). Paperlogy와 google/fonts판 Noto Serif KR은 RFN 없음.
4. **PDF/A 요건과의 정합** — PDF/A는 "제한 없는 보편적 렌더링을 위해 합법적으로 임베드 가능한 폰트"만 허용한다. 6종 모두 이 요건을 만족하나 **KoPubWorld는 개별 약관 해석에 의존**하므로, PDF/A 산출이 목표라면 OFL 5종 중에서 고르는 편이 안전하다.
5. **재확인 주기** — 라이선스 문서는 변경될 수 있다. 릴리스 전 이 문서의 확인 일자가 6개월 이상 지났으면 원 URL을 다시 확인할 것.
