# Phase 4: VERIFY — 통합 검증 (상세)

## 4-1. 코드 통합

worktree에서 작업한 결과를 메인 브랜치로 통합한다:

```bash
# 각 worktree 브랜치를 순서대로 merge
git merge {worktree-branch-1} --no-edit
git merge {worktree-branch-2} --no-edit
# ...
```

> merge 충돌 발생 시:
> 1. 충돌 파일 확인 (`git diff --name-only --diff-filter=U`)
> 2. 충돌 내용 분석
> 3. 자동 해결 시도 (양쪽 의도를 파악하여 수동 병합)
> 4. 자동 해결 불가 → 사용자에게 충돌 파일과 양쪽 코드를 보여주고 판단 요청

## 4-2. 통합 검증

프로젝트에 검증 스크립트가 있으면 통합 후 실행한다:

```bash
bash verify.sh      # 또는 npm test / npm run build / pytest 등 프로젝트 검증 수단
```

- 검증 수단이 **없으면** 이 단계를 생략하고 Phase 5로 진행한다 (통합 merge 성공만 확인).
- **PASS** → Phase 5로
- **FAIL** → 실패 원인 분석:
  - 타입 충돌 → 팀 리더가 직접 수정
  - import 오류 → 팀 리더가 직접 수정
  - 로직 충돌 → 사용자에게 보고
- 수정 후 검증 재실행 (최대 3회)
- 3회 초과 실패 → 사용자에게 현재 상태 보고

## 4-3. 그룹 완료 보고

```
✅ 그룹 {N} 완료 ({n}개 SubTask)
══════════════════════════════════
SubTask 결과:
  ✅ SubTask {N}-1: {설명}
  ✅ SubTask {N}-2: {설명}
  ❌ SubTask {N}-3: {설명} → 팀 리더 직접 수정 완료

통합 검증: [스크립트명] ✅ PASS / — (검증 스크립트 없음)
수정 파일 (통합): {파일 목록}
══════════════════════════════════
```
