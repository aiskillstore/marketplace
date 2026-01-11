# Modularization Guide

파일 분리 시 참고하는 상세 가이드입니다.

## 분리 원칙

### 1. Single Responsibility Principle
- 각 파일은 하나의 명확한 책임만 가짐
- "이 파일은 무엇을 하는가?"에 한 문장으로 답할 수 있어야 함

### 2. 응집도 (Cohesion)
- 관련 있는 코드는 함께 유지
- 함께 변경되는 코드는 함께 배치

### 3. 결합도 (Coupling)
- 모듈 간 의존성 최소화
- 순환 의존성 금지

## 언어별 패턴

### TypeScript/React

#### 컴포넌트 분리
```typescript
// Before: BigComponent.tsx (400 lines)

// After:
// BigComponent/
// ├── index.tsx           // 메인 컴포넌트, re-export
// ├── BigComponent.tsx    // 실제 컴포넌트 로직
// ├── SubComponentA.tsx   // 하위 컴포넌트
// ├── SubComponentB.tsx
// ├── BigComponent.hooks.ts   // 커스텀 훅
// ├── BigComponent.types.ts   // 타입 정의
// ├── BigComponent.styles.ts  // 스타일 (styled-components)
// └── BigComponent.utils.ts   // 유틸리티 함수
```

#### index.tsx 패턴
```typescript
// index.tsx - 깔끔한 re-export
export { BigComponent } from './BigComponent';
export type { BigComponentProps } from './BigComponent.types';
```

### Python

```python
# Before: big_module.py (500 lines)

# After:
# big_module/
# ├── __init__.py      # 공개 API 정의
# ├── core.py          # 핵심 로직
# ├── helpers.py       # 헬퍼 함수
# ├── models.py        # 데이터 모델
# └── constants.py     # 상수
```

### Go

```go
// Before: big_service.go (400 lines)

// After:
// service/
// ├── service.go      // 메인 서비스
// ├── handlers.go     // HTTP 핸들러
// ├── repository.go   // 데이터 접근
// └── models.go       // 모델 정의
```

## 분리 체크리스트

### 분리 전
- [ ] 현재 라인 수 확인
- [ ] 파일 내 섹션 식별
- [ ] 각 섹션의 책임 파악
- [ ] 순환 의존성 체크

### 분리 중
- [ ] 각 새 파일이 200줄 이하인지 확인
- [ ] import/export 정리
- [ ] 테스트 파일도 함께 분리

### 분리 후
- [ ] 빌드 성공 확인
- [ ] 테스트 통과 확인
- [ ] 린트 에러 없음 확인

## 분리하면 안 되는 경우

1. **라인 수만 줄이기 위한 인위적 분리**
   - 논리적으로 하나인 것을 억지로 나누지 않음

2. **순환 의존성 발생 시**
   - A → B → A 구조가 되면 분리 재고

3. **응집도가 높은 코드**
   - 항상 함께 변경되는 코드는 함께 유지

## Anti-patterns

### ❌ 피해야 할 패턴

```
# 너무 잘게 쪼갬
utils/
├── add.ts        # 1 function
├── subtract.ts   # 1 function
├── multiply.ts   # 1 function
└── divide.ts     # 1 function
```

### ✅ 권장 패턴

```
# 논리적 그룹핑
utils/
├── math.ts       # 수학 관련 함수들
├── string.ts     # 문자열 관련 함수들
└── date.ts       # 날짜 관련 함수들
```
