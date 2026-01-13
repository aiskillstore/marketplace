# Technology Domain Profile

> For programming, frameworks, tools, APIs, and software development topics.

---

## Search Strategy

### Primary Sources

1. **Official Documentation**
   - Language/framework official docs
   - API references
   - Release notes and changelogs

2. **Code Repositories**
   - GitHub repositories (official + community)
   - GitLab, Bitbucket for enterprise topics
   - Example code and implementations

3. **Developer Communities**
   - Stack Overflow Q&A
   - GitHub Discussions/Issues
   - Reddit (r/programming, r/learnprogramming)

4. **Technical Content**
   - Technical blogs (official engineering blogs)
   - Conference talks and presentations
   - Online courses and tutorials

### Search Query Patterns

```
"{topic} official documentation"
"{topic} getting started guide"
"{topic} tutorial 2025"
"{topic} github examples"
"{topic} API reference"
"{topic} best practices"
"{topic} vs {alternative} comparison"
"awesome {topic} github"
"{topic} roadmap"
```

### Quality Indicators

- Official sources prioritized
- Recent updates (prefer 2024-2025)
- Active maintenance (stars, recent commits)
- Community validation (upvotes, accepted answers)

---

## Special Fields

### Code Policy

| Field                 | Description               | Example         |
| --------------------- | ------------------------- | --------------- |
| `primary_language`    | Main programming language | Python 3.11+    |
| `secondary_languages` | Supporting languages      | JavaScript, SQL |
| `code_style`          | Style guide reference     | PEP 8, Airbnb   |
| `version`             | Target version            | 3.11.0          |

### Environment

| Field             | Description               | Example              |
| ----------------- | ------------------------- | -------------------- |
| `os`              | Target operating system   | Linux (Ubuntu 22.04) |
| `runtime`         | Runtime environment       | Node.js 20 LTS       |
| `package_manager` | Preferred package manager | pip, npm, cargo      |
| `ide`             | Recommended IDE/editor    | VS Code, PyCharm     |

### Dependencies

| Field                 | Description               | Example            |
| --------------------- | ------------------------- | ------------------ |
| `required_packages`   | Essential dependencies    | numpy, pandas      |
| `optional_packages`   | Enhancement dependencies  | matplotlib         |
| `system_requirements` | System-level requirements | Docker, PostgreSQL |

---

## Terminology Policy

### Language Handling

| Type               | Policy                       | Example                                     |
| ------------------ | ---------------------------- | ------------------------------------------- |
| Technical terms    | Original (English) preferred | "function", "class", "API"                  |
| Korean explanation | Parenthetical on first use   | 함수(function)                              |
| Code/commands      | Always original language     | `pip install`, `npm run`                    |
| Concepts           | Bilingual on first use       | 비동기 프로그래밍(Asynchronous Programming) |

### First Occurrence Format

```markdown
## 콜백 함수 (Callback Function)

콜백 함수(callback function)란 다른 함수에 인자로 전달되어
나중에 호출되는 함수를 말합니다.
```

### Citation Format

```markdown
> 참조: [Python Documentation - Functions](https://docs.python.org/3/tutorial/controlflow.html#defining-functions)
```

---

## Content Structure

### Recommended Organization

```
1. 개요 및 개념 설명
   - 왜 필요한가? (동기)
   - 핵심 개념 정의
   - 활용 사례

2. 환경 설정
   - 설치 가이드
   - 기본 설정
   - 검증 방법

3. 기초 사용법
   - Hello World 예제
   - 기본 문법/API
   - 간단한 실습

4. 심화 내용
   - 고급 기능
   - 패턴 및 베스트 프랙티스
   - 성능 최적화

5. 실전 프로젝트
   - 종합 예제
   - 트러블슈팅
   - 다음 단계
```

### Code Example Requirements

- **실행 가능**: 복사-붙여넣기로 바로 실행
- **점진적 복잡도**: 간단한 것에서 복잡한 것으로
- **주석 포함**: 핵심 부분 설명
- **오류 처리**: 실패 케이스도 보여주기
- **테스트 포함**: 검증 방법 제시

### Code Block Format

````markdown
```python
# 파일명: example.py
# 설명: 비동기 HTTP 요청 예제

import asyncio
import aiohttp

async def fetch_data(url: str) -> dict:
    """URL에서 JSON 데이터를 가져옵니다."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# 실행 예시
# asyncio.run(fetch_data("https://api.example.com/data"))
```
````

---

## Forbidden Patterns

- `eval()`, `exec()` without sandboxing
- Hardcoded credentials or API keys
- Deprecated APIs without migration notes
- Platform-specific code without alternatives
- Unvalidated user input in examples

---

## Version Handling

When multiple versions exist:

````markdown
> **버전 참고**: 이 문서는 Python 3.11 기준으로 작성되었습니다.
> Python 3.9 이하에서는 일부 문법이 다를 수 있습니다.

<!-- Python 3.9 이하 -->

```python
from typing import Union
def process(data: Union[str, int]) -> None:
    pass
```
````

<!-- Python 3.10+ -->

```python
def process(data: str | int) -> None:
    pass
```

````

---

## Review Criteria

Review criteria for the reviewer agent when evaluating technology domain documents.

### Critical Checks (ERROR if failed)

These issues trigger `NEEDS_REVISION` status:

| Check | Detection | Example |
|-------|-----------|---------|
| Forbidden patterns | `eval()`, `exec()` without sandboxing | `eval(userInput)` |
| Hardcoded secrets | API keys, passwords in code | `apiKey = "sk-..."` |
| Missing language specifier | Code blocks without language | ` ```\ncode\n``` ` |
| Unvalidated user input | Direct use of user input in dangerous contexts | SQL injection patterns |

### Quality Checks (WARN if issues)

These issues are noted but don't block publication:

| Check | Expectation | Notes |
|-------|-------------|-------|
| Runnable examples | Code should be copy-paste executable | Check for missing imports, context |
| Error handling | Examples should show error cases | At least one try/catch or error check |
| Type annotations | Type hints present where applicable | Python type hints, TypeScript types |
| Version notes | Multi-version topics need compatibility notes | When syntax differs by version |

### Style Checks (INFO)

Minor issues for optional improvement:

| Check | Expectation | Notes |
|-------|-------------|-------|
| Terminology consistency | Same term throughout document | 컴포넌트 vs 구성요소 |
| Bilingual first-occurrence | 한국어(English) format | 콜백 함수(callback function) |
| Code comments | Comments in appropriate language | Per persona.md guidelines |
| Docstrings | Function documentation present | For complex examples |

### Automated Patterns

Regex patterns for automated detection:

```
# Forbidden patterns (ERROR)
/eval\s*\(/
/exec\s*\(/
/password\s*=\s*['"]/
/api[_-]?key\s*=\s*['"]/
/secret\s*=\s*['"]/

# Missing language specifier (ERROR)
/```\n[^`]/  # Code block without language

# Version note check (WARN for multi-version topics)
/버전|version|Python\s+\d|Node\.?js\s+\d/i  # If found, check for compatibility notes
```

---

## Domain-Specific Sections for persona.md

```markdown
## Domain Guidelines: Technology

**Primary Language**: {PRIMARY_LANGUAGE}
**Code Style**: {CODE_STYLE} 준수
**Environment**: {ENVIRONMENT}

**Coding Conventions**:
- Type hints 사용 권장
- Docstring 작성 (Google style)
- 에러 핸들링 명시

**Forbidden Patterns**:
- eval(), exec() 사용 금지
- 하드코딩된 시크릿 금지
- deprecated API 사용 시 경고 명시
````
