# Vibe Kanban 환경 변수 레퍼런스

## 서버 설정

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `PORT` | `3000` | 웹 서버 포트 |
| `VIBE_KANBAN_PORT` | `3000` | 웹 서버 포트 (별칭) |
| `VIBE_KANBAN_REMOTE` | `false` | 원격 연결 허용 (`true`/`false`) |
| `VIBE_KANBAN_DATA_DIR` | `.vibe-kanban` | 데이터 저장 디렉토리 |

## MCP 설정

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `MCP_HOST` | `127.0.0.1` | MCP 서버 바인딩 주소 |
| `MCP_PORT` | `3001` | MCP 서버 포트 |

## CORS 설정

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `VK_ALLOWED_ORIGINS` | `http://localhost:*` | 허용된 CORS 오리진 (쉼표 구분) |

## 에이전트 설정

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `ANTHROPIC_API_KEY` | - | Claude 에이전트용 API 키 |
| `OPENAI_API_KEY` | - | Codex/GPT 에이전트용 API 키 |
| `GOOGLE_API_KEY` | - | Gemini 에이전트용 API 키 |

## Git 설정

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `GITHUB_TOKEN` | - | GitHub PR 자동 생성용 토큰 |
| `GIT_WORKTREE_BASE` | `.worktrees` | Worktree 저장 디렉토리 |

## 예시: .env 파일

```bash
PORT=3000
VIBE_KANBAN_REMOTE=false
VK_ALLOWED_ORIGINS=http://localhost:3000,https://vk.example.com
ANTHROPIC_API_KEY=sk-ant-...
GITHUB_TOKEN=ghp_...
```

## 예시: Docker 환경

```bash
docker run -p 3000:3000 \
  -e VIBE_KANBAN_REMOTE=true \
  -e VK_ALLOWED_ORIGINS=https://vk.example.com \
  vibekanban/vibe-kanban
```
