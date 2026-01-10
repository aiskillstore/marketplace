# Safe Edit Skill - 사용자 가이드

## 한 줄 요약
파일 수정 시 자동으로 백업, diff 저장, 에이전트 활용, 모듈화(200줄 제한)를 처리하는 자동화 스킬입니다.

## 이 스킬이 해결하는 문제

### Before (스킬 없이)
```
사용자: "pricing 페이지 수정해줘"
개발자: "알겠습니다"
→ 수정 완료
사용자: "맘에 안드는데 되돌릴 수 있어?"
개발자: "백업을 안 만들어서..."
```

### After (스킬 사용)
```
사용자: "pricing 페이지 수정해줘"
개발자: (safe-edit 자동 활성화)
  ✓ 백업 생성: .backups/2025-10-24/13-45-30_app_pricing_page.tsx.backup
  ✓ Diff 저장: /tmp/diffs/2025-10-24_13-45-30_pricing-update.patch
  ✓ Explore 에이전트로 구조 분석
  ✓ 파일 크기 확인 (180줄 - 안전)
  ✓ 수정 완료

사용자: "맘에 안드는데 되돌릴 수 있어?"
개발자: "네! 3가지 방법 가능합니다"
  1. cp .backups/... (백업 복원)
  2. patch -R (diff 역적용)
  3. git restore (Git 복원)
```

## 자동으로 처리되는 것들

### 1. 백업 자동 생성
- **위치**: `.backups/YYYY-MM-DD/`
- **형식**: `HH-MM-SS_{파일명}.backup`
- **예시**: `.backups/2025-10-24/13-45-30_app_pricing_page.tsx.backup`

### 2. Diff 자동 저장
- **위치**: `/tmp/diffs/`
- **형식**: `YYYY-MM-DD_HH-MM-SS_{설명}.patch`
- **예시**: `/tmp/diffs/2025-10-24_13-45-30_add-footer-links.patch`

### 3. 에이전트 자동 활용
- UI 작업 → `frontend-developer` 에이전트
- 구조 분석 → `Explore` 에이전트
- API 작업 → `backend-api-developer` 에이전트

### 4. 모듈화 자동 감지
- 200줄 초과 시 자동 경고
- 리팩토링 계획 제시
- 모듈 분리 자동 실행

## 사용 방법

### 자동 활성화 (권장)
스킬이 자동으로 감지하는 키워드:
- "구현해줘", "추가해줘", "만들어줘"
- "수정해줘", "고쳐줘", "바꿔줘"
- "리팩토링", "업데이트"

### 수동 활성화
```
@safe-edit 파일 수정해줘
```

## 실제 사용 예시

### 예시 1: 간단한 컴포넌트 수정
```
사용자: "대시보드에 로딩 스피너 추가해줘"

Agent (safe-edit 자동 활성화):
✓ TODO 리스트 생성 (3개 작업)
✓ components/dashboard/Dashboard.tsx 백업
✓ 변경 전 diff 저장
✓ 파일 크기 확인 (150줄 - 안전)
✓ 로딩 스피너 구현
✓ 변경 후 diff 저장
✓ TypeScript 타입 검증
✓ 롤백 명령어 제공

결과:
- 백업: .backups/2025-10-24/14-30-15_components_dashboard_Dashboard.tsx.backup
- Diff: /tmp/diffs/2025-10-24_14-30-15_add-loading-spinner.patch
```

### 예시 2: 대형 기능 (모듈화 필요)
```
사용자: "고급 비디오 편집 컨트롤 구현해줘"

Agent (safe-edit 자동 활성화):
✓ TODO 리스트 생성 (8개 작업)
✓ EditorContainer.tsx 분석 (320줄 - 초과!)
⚠️ 200줄 제한 초과 - 모듈화 계획 수립

모듈화 계획:
1. EditorContainer.tsx (메인, 180줄)
2. hooks/useVideoControls.ts (신규, 90줄)
3. actions/videoActions.ts (신규, 70줄)

✓ 모든 파일 백업
✓ frontend-developer 에이전트로 구현
✓ 모듈별로 분할 구현
✓ 포괄적인 diff 저장
✓ 빌드 성공 확인
✓ 아키텍처 변경사항 문서화
```

### 예시 3: 버그 수정
```
사용자: "TTS 타이밍 문제 고쳐줘"

Agent (safe-edit 자동 활성화):
✓ TODO 리스트 생성 (5개 작업)
✓ Explore 에이전트로 TTS 관련 파일 검색
✓ lib/audio/SegmentPlanner.ts 분석
✓ 영향받는 파일들 백업
✓ 근본 원인 분석
✓ 수정 구현
✓ diff 저장
✓ TTS 생성 테스트
✓ 증거와 함께 수정 완료 보고
```

## 롤백 방법

### 방법 1: 백업 파일 복원 (가장 간단)
```bash
# 백업 확인
ls -lt .backups/2025-10-24/

# 복원
cp .backups/2025-10-24/13-45-30_app_pricing_page.tsx.backup app/pricing/page.tsx
```

### 방법 2: Patch 역적용
```bash
# Diff 파일로 되돌리기
patch -R app/pricing/page.tsx < /tmp/diffs/2025-10-24_13-45-30_feature.patch
```

### 방법 3: Git 복원
```bash
# 아직 커밋 안 한 경우
git restore app/pricing/page.tsx

# 커밋했지만 푸시 안 한 경우
git reset --hard HEAD~1
```

## 파일 크기 관리

### 목표 크기
- **컴포넌트**: 80-150줄 (이상적), 최대 200줄
- **훅**: 40-80줄 (이상적), 최대 120줄
- **유틸**: 50-100줄 (이상적), 최대 150줄
- **액션**: 60-120줄 (이상적), 최대 180줄

### 경고 수준
- ⚠️ 200줄 초과: 즉시 리팩토링 계획
- 🚨 300줄 초과: 긴급 리팩토링 필요
- 🔥 500줄 초과: 치명적 - 지금 당장 모듈 분리!

### 자동 리팩토링 전략

**1. 훅 추출**
```typescript
// 이전: 상태 로직이 포함된 컴포넌트 (280줄)
// 이후: 컴포넌트 (120줄) + useEditorState (80줄) + useKeyboard (60줄)
```

**2. 액션 추출**
```typescript
// 이전: 비즈니스 로직이 포함된 컴포넌트 (350줄)
// 이후: 컴포넌트 (150줄) + ttsActions (100줄) + mediaActions (80줄)
```

**3. 서브 컴포넌트 추출**
```typescript
// 이전: 거대한 컴포넌트 (420줄)
// 이후: 컨테이너 (120줄) + 서브 컴포넌트 3개 (80+90+110줄)
```

## 유용한 명령어

```bash
# 오늘의 백업 확인
ls -lt .backups/$(date +%Y-%m-%d)/

# 최근 diff 확인
ls -lt /tmp/diffs/ | head -10

# 큰 파일 찾기 (200줄 이상)
find . -name "*.tsx" -o -name "*.ts" | xargs wc -l | sort -nr | head -20

# 오래된 백업 삭제 (7일 이상)
find .backups/ -type f -mtime +7 -delete
```

## FAQ

### Q: 매번 "백업하고 diff 저장해줘" 말 안 해도 되나요?
**A**: 네! 이 스킬이 자동으로 처리합니다. 그냥 "수정해줘"라고만 하세요.

### Q: 백업 파일은 언제 삭제하나요?
**A**: 자동으로 7일 후 삭제됩니다. 수동 삭제도 가능합니다.

### Q: 200줄 제한은 왜 있나요?
**A**: 코드 유지보수성과 가독성을 위해서입니다. 200줄 이하면:
- 한 화면에 전체 파일을 볼 수 있음
- 책임이 명확하게 분리됨
- 테스트 작성이 쉬움
- 버그 찾기가 쉬움

### Q: 에이전트는 언제 사용되나요?
**A**: 작업 복잡도에 따라 자동 선택됩니다:
- UI 작업 → frontend-developer
- 구조 분석 → Explore
- API 개발 → backend-api-developer
- DB 설계 → database-architect

### Q: diff 파일과 백업 파일의 차이는?
**A**:
- **백업**: 전체 파일 복사본 (완전한 복원)
- **Diff**: 변경 사항만 기록 (선택적 복원, 작은 용량)

### Q: 롤백하면 백업은 자동 삭제되나요?
**A**: 아니요. 백업은 유지됩니다. 필요시 수동 삭제하세요.

## 디렉토리 구조

```
프로젝트/
├── .backups/                    # 백업 저장소
│   ├── 2025-10-24/
│   │   ├── 13-45-30_app_pricing_page.tsx.backup
│   │   └── 14-20-15_components_editor_Editor.tsx.backup
│   └── ROLLBACK_GUIDE.md        # 롤백 가이드
├── /tmp/diffs/                  # Diff 저장소
│   ├── 2025-10-24_13-45-30_add-footer-links.patch
│   ├── 2025-10-24_14-20-15_pricing-update.patch
│   └── latest.patch             # 가장 최근 diff
└── .claude/
    └── skills/
        └── safe-edit/
            ├── SKILL.md         # 스킬 정의 (AI용)
            └── README.md        # 이 문서 (사용자용)
```

## 베스트 프랙티스

### 해야 할 것
✅ 코드 변경 시 항상 safe-edit 활성화
✅ 파일을 200줄 이하로 유지
✅ 복잡한 작업에는 에이전트 활용
✅ 롤백 절차 문서화
✅ 변경 전 테스트
✅ TODO 진행상황 정기적으로 업데이트
✅ 의미있는 설명과 함께 diff 저장

### 하지 말아야 할 것
❌ "작은 변경"이라고 백업 건너뛰기
❌ 파일을 200줄 넘게 방치
❌ 분석 없이 구현
❌ 백업을 즉시 삭제
❌ TypeScript 에러 무시
❌ 변경사항 문서화 생략

## 관련 스킬

- **supabase-manager**: 데이터베이스 작업
- **safe-edit** (이 스킬): 모든 코드 변경

## 업데이트 내역

- 2025-10-24: 초기 버전 생성
  - 자동 백업 시스템
  - Diff 추적
  - 에이전트 통합
  - 200줄 제한 자동화
  - 모듈화 가이드
