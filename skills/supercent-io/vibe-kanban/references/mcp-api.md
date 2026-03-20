# Vibe Kanban MCP API 레퍼런스

> **검증 버전**: v0.1.17 (2026-02-22 Playwright 검증)
> MCP를 통해 에이전트가 직접 Vibe Kanban 워크스페이스를 생성하고 관리할 수 있습니다.

## 개요

Vibe Kanban MCP 서버는 표준 MCP 프로토콜을 통해 보드 조작 API를 제공합니다.

## 도구 목록

### vk_list_cards

카드 목록을 조회합니다.

**파라미터:**
| 이름 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `column` | string | 아니오 | 필터링할 칼럼 (`todo`, `in_progress`, `review`, `done`) |

**응답:**
```json
[
  {
    "id": "card_abc123",
    "title": "API 엔드포인트 구현",
    "description": "GET /api/users 엔드포인트 추가",
    "column": "in_progress",
    "agent": "claude",
    "worktree": "~/.vibe-kanban-workspaces/<workspace-uuid>",
    "created_at": "2026-02-21T10:00:00Z"
  }
]
```

### vk_create_card

새 카드를 생성합니다.

**파라미터:**
| 이름 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `title` | string | 예 | 카드 제목 |
| `description` | string | 아니오 | 카드 설명 |
| `agent` | string | 아니오 | 에이전트 타입 (`opencode`, `claude`, `codex`, `gemini`, `amp`, `qwen`, `copilot`, `droid`, `cursor`) |

**응답:**
```json
{
  "id": "card_xyz789",
  "title": "새 카드",
  "column": "todo",
  "created_at": "2026-02-21T10:30:00Z"
}
```

### vk_move_card

카드를 다른 칼럼으로 이동합니다.

**파라미터:**
| 이름 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `card_id` | string | 예 | 카드 ID |
| `column` | string | 예 | 목표 칼럼 (`todo`, `in_progress`, `review`, `done`) |

**응답:**
```json
{
  "id": "card_abc123",
  "column": "review",
  "worktree": "~/.vibe-kanban-workspaces/<workspace-uuid>"
}
```

**부작용:**
- 카드 생성 → Running: Git worktree + 브랜치(`vk/<4자ID>-<slug>`) 자동 생성 + 에이전트 실행
- Done/Archive: Draft PR 생성 (GitHub 연결 시)

### vk_get_logs

에이전트 실행 로그를 조회합니다.

**파라미터:**
| 이름 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `card_id` | string | 예 | 카드 ID |
| `tail` | number | 아니오 | 마지막 N줄만 (기본: 100) |

**응답:**
```json
{
  "card_id": "card_abc123",
  "logs": "Cloning worktree...\nRunning claude...\n✅ Task completed",
  "exit_code": 0,
  "duration_ms": 45000
}
```

### vk_retry_card

실패한 카드를 재시도합니다.

**파라미터:**
| 이름 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `card_id` | string | 예 | 카드 ID |
| `clear_worktree` | boolean | 아니오 | Worktree 초기화 여부 (기본: false) |

**응답:**
```json
{
  "id": "card_abc123",
  "column": "in_progress",
  "retry_count": 2
}
```

## 에러 코드

| 코드 | 설명 |
|------|------|
| `CARD_NOT_FOUND` | 카드를 찾을 수 없음 |
| `INVALID_COLUMN` | 잘못된 칼럼 이름 |
| `WORKTREE_CONFLICT` | Worktree 충돌 |
| `AGENT_ERROR` | 에이전트 실행 실패 |
| `GIT_ERROR` | Git 명령 실패 |
