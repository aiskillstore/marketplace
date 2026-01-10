# Safe Edit 스킬 - 빠른 시작 가이드

## 30초 요약

이제 **코드 수정 시 자동으로**:
- ✅ 백업 생성 (`.backups/날짜/시간_파일명.backup`)
- ✅ Diff 저장 (`/tmp/diffs/날짜_시간_설명.patch`)
- ✅ 에이전트 활용 (분석, 구현)
- ✅ 모듈화 강제 (200줄 제한)

**더 이상 "백업하고 diff 저장해줘" 말할 필요 없음!**

---

## 사용법

### 자동 활성화 (아무것도 안 해도 됨)
```
사용자: "pricing 페이지 수정해줘"
→ safe-edit 자동 활성화
→ 모든 안전장치 자동 적용
```

### 되돌리기 (3가지 방법)
```bash
# 1. 백업 복원 (가장 쉬움)
cp .backups/2025-10-24/13-45-30_파일명.backup 원본경로

# 2. Patch 역적용
patch -R 파일경로 < /tmp/diffs/날짜_시간_설명.patch

# 3. Git 복원
git restore 파일경로
```

---

## 파일 위치

```
프로젝트/
├── .backups/              # 백업 저장
│   ├── 2025-10-24/       # 날짜별 폴더
│   └── ROLLBACK_GUIDE.md # 롤백 가이드
├── /tmp/diffs/            # Diff 저장
└── .claude/skills/safe-edit/
    ├── SKILL.md          # 스킬 정의
    ├── README.md         # 상세 가이드
    └── QUICK_START.md    # 이 문서
```

---

## 실제 예시

### Before
```
사용자: "pricing 페이지에 footer 추가해줘"
개발자: "네"
→ 수정 완료

사용자: "맘에 안 드는데?"
개발자: "백업이 없어서..."
```

### After (safe-edit 적용)
```
사용자: "pricing 페이지에 footer 추가해줘"
개발자: (safe-edit 자동 활성화)
  ✓ 백업: .backups/2025-10-24/13-45-30_app_pricing_page.tsx.backup
  ✓ Diff: /tmp/diffs/2025-10-24_13-45-30_add-footer.patch
  ✓ 구현 완료

사용자: "맘에 안 드는데?"
개발자: "롤백 가능! 3가지 방법 있습니다"
```

---

## 200줄 제한

파일이 200줄을 넘으면 **자동으로 모듈화**합니다:

```
EditorContainer.tsx (320줄) ❌
↓ 자동 리팩토링
EditorContainer.tsx (180줄) ✅
hooks/useEditorState.ts (80줄) ✅
actions/editorActions.ts (60줄) ✅
```

---

## 에이전트 자동 선택

작업에 맞는 에이전트가 **자동으로** 선택됩니다:

| 작업 | 에이전트 |
|-----|---------|
| UI 작업 | frontend-developer |
| 구조 분석 | Explore |
| API 개발 | backend-api-developer |
| DB 설계 | database-architect |

---

## 자주 묻는 질문

**Q: 매번 "백업해줘" 말해야 하나요?**
A: 아니요! 자동입니다.

**Q: 백업은 언제 삭제되나요?**
A: 7일 후 자동 삭제됩니다.

**Q: 200줄 제한은 왜 있나요?**
A: 유지보수성과 가독성을 위해서입니다.

**Q: diff는 어디에 저장되나요?**
A: `/tmp/diffs/` 폴더에 저장됩니다.

---

## 유용한 명령어

```bash
# 오늘 백업 보기
ls -lt .backups/$(date +%Y-%m-%d)/

# 최근 diff 보기
ls -lt /tmp/diffs/ | head -10

# 큰 파일 찾기 (200줄 이상)
find . -name "*.tsx" | xargs wc -l | sort -nr | head -20
```

---

## 더 알아보기

- **상세 가이드**: [README.md](README.md)
- **롤백 가이드**: [/.backups/ROLLBACK_GUIDE.md](/.backups/ROLLBACK_GUIDE.md)
- **스킬 정의**: [SKILL.md](SKILL.md)

---

**이제 안전하게 코딩하세요! 🚀**
