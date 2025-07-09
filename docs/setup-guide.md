# GitHub Commit to Notion Automation - Setup Guide

이 가이드는 GitHub 커밋을 자동으로 Notion 데이터베이스에 보고하는 n8n 워크플로우와 MCP 서버를 설정하는 방법을 설명합니다.

## 목차
1. [요구사항](#요구사항)
2. [환경 설정](#환경-설정)
3. [Notion 데이터베이스 설정](#notion-데이터베이스-설정)
4. [MCP 서버 설정](#mcp-서버-설정)
5. [n8n 워크플로우 설정](#n8n-워크플로우-설정)
6. [GitHub Webhook 설정](#github-webhook-설정)
7. [테스트 및 검증](#테스트-및-검증)
8. [문제 해결](#문제-해결)

## 요구사항

### 소프트웨어 요구사항
- Python 3.8+
- Docker & Docker Compose
- n8n 1.0+
- GitHub 계정 (관리자 권한)
- Notion 계정 및 워크스페이스

### API 키 및 토큰
- GitHub Personal Access Token
- Notion Integration Token
- OpenAI API Key (선택사항, AI 분석용)

## 환경 설정

### 1. 저장소 클론 및 환경 변수 설정

```bash
git clone <repository-url>
cd Dashboard
cp .env.example .env
```

### 2. 환경 변수 구성

`.env` 파일을 편집하여 다음 값들을 설정하세요:

```bash
# GitHub Settings
GITHUB_TOKEN=ghp_your_github_token_here
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

# Notion Settings
NOTION_TOKEN=secret_your_notion_token_here
NOTION_DATABASE_ID=your_database_id_here

# OpenAI Settings (선택사항)
OPENAI_API_KEY=sk-your_openai_api_key_here

# MCP Server Settings
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8001

# n8n Settings
N8N_HOST=localhost
N8N_PORT=5678

# Slack Settings (선택사항 - 에러 알림용)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url
```

### 3. API 키 획득 방법

#### GitHub Personal Access Token
1. GitHub → Settings → Developer settings → Personal access tokens
2. "Generate new token" 클릭
3. 다음 권한 선택:
   - `repo` (전체 리포지토리 접근)
   - `admin:repo_hook` (웹훅 관리)
4. 생성된 토큰을 `GITHUB_TOKEN`에 설정

#### Notion Integration Token
1. [Notion Developers](https://developers.notion.com/) 접속
2. "New integration" 생성
3. 워크스페이스 선택 및 권한 설정
4. 생성된 토큰을 `NOTION_TOKEN`에 설정

#### OpenAI API Key (선택사항)
1. [OpenAI Platform](https://platform.openai.com/) 접속
2. API Keys 섹션에서 새 키 생성
3. 생성된 키를 `OPENAI_API_KEY`에 설정

## Notion 데이터베이스 설정

### 1. 데이터베이스 생성
1. Notion에서 새 페이지 생성
2. "Database" → "Table" 선택
3. 데이터베이스 이름: "GitHub Commits"

### 2. 데이터베이스 스키마 설정
다음 속성들을 추가하세요:

| 속성 이름 | 타입 | 설명 |
|-----------|------|------|
| Title | Title | 커밋 메시지 (자동으로 생성됨) |
| Commit Hash | Text | Git 커밋 해시 |
| Author | Text | 커밋 작성자 |
| Repository | Text | 저장소 이름 |
| Branch | Select | 브랜치 이름 |
| Files Changed | Number | 변경된 파일 수 |
| Added Lines | Number | 추가된 라인 수 |
| Deleted Lines | Number | 삭제된 라인 수 |
| Date | Date | 커밋 날짜 |
| Analysis Report | Text | MCP 분석 보고서 |
| Commit URL | URL | GitHub 커밋 링크 |

### 3. 데이터베이스 ID 획득
1. 데이터베이스 페이지 URL을 복사
2. URL에서 32자리 ID 부분을 추출 (예: `https://notion.so/workspace/DATABASE_ID?v=...`)
3. 추출한 ID를 `NOTION_DATABASE_ID`에 설정

### 4. Integration 권한 부여
1. 데이터베이스 페이지에서 "Share" 클릭
2. "Invite" 섹션에서 생성한 Integration 선택
3. "Can edit" 권한 부여

## MCP 서버 설정

### 1. Docker를 사용한 설정 (권장)

```bash
# Docker Compose를 사용하여 전체 스택 실행
docker-compose up -d
```

### 2. 수동 설정

```bash
# MCP 서버 디렉토리로 이동
cd mcp-server

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python commit-analyzer.py
```

### 3. 서버 상태 확인

```bash
# 헬스 체크
curl http://localhost:8001/

# 기능 확인
curl http://localhost:8001/capabilities
```

## n8n 워크플로우 설정

### 1. n8n 설치 및 실행

```bash
# Docker를 사용한 n8n 실행
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### 2. 워크플로우 임포트
1. n8n 웹 인터페이스 접속 (http://localhost:5678)
2. "Import from file" 선택
3. `workflows/github-notion-automation.json` 파일 업로드

### 3. 크리덴셜 설정
1. **Notion API** 크리덴셜:
   - Name: `notion-credentials`
   - Token: `NOTION_TOKEN` 값 입력

2. **HTTP Header Auth** (MCP 서버용, 필요시):
   - Name: `mcp-auth`
   - Header Name: `Authorization`
   - Header Value: `Bearer your_token_here`

### 4. 환경 변수 설정
n8n에서 다음 환경 변수들을 설정:
- `NOTION_DATABASE_ID`
- `SLACK_WEBHOOK_URL` (선택사항)

## GitHub Webhook 설정

### 1. 웹훅 URL 획득
n8n 워크플로우에서 "GitHub Webhook" 노드의 URL을 복사합니다.
형식: `https://your-n8n-instance.com/webhook/github-webhook`

### 2. GitHub 리포지토리에 웹훅 추가
1. GitHub 리포지토리 → Settings → Webhooks
2. "Add webhook" 클릭
3. 설정:
   - **Payload URL**: n8n 웹훅 URL
   - **Content type**: `application/json`
   - **Secret**: `GITHUB_WEBHOOK_SECRET` 값
   - **Events**: "Just the push event" 선택
   - **Active**: 체크

### 3. 웹훅 시크릿 설정 (보안)
```bash
# 웹훅 시크릿 생성
openssl rand -hex 20
```
생성된 값을 GitHub 웹훅 설정과 `.env` 파일에 모두 입력합니다.

## 테스트 및 검증

### 1. MCP 서버 테스트

```bash
# 테스트 커밋 데이터로 분석 요청
curl -X POST http://localhost:8001/analyze-commit \
  -H "Content-Type: application/json" \
  -d '{
    "commit_hash": "abc123",
    "commit_message": "feat: add new feature",
    "commit_author": "Test User",
    "repository_name": "test-repo",
    "branch_name": "main",
    "added_files": ["file1.py"],
    "modified_files": ["file2.py"],
    "removed_files": [],
    "total_files_changed": 2,
    "commit_url": "https://github.com/user/repo/commit/abc123"
  }'
```

### 2. n8n 워크플로우 테스트
1. n8n에서 워크플로우 수동 실행
2. 테스트 데이터를 입력하여 각 노드 동작 확인

### 3. 전체 파이프라인 테스트
1. 테스트 리포지토리에 커밋 푸시
2. GitHub 웹훅 호출 확인
3. n8n 워크플로우 실행 로그 확인
4. Notion 데이터베이스에 엔트리 생성 확인

## 문제 해결

### 일반적인 문제들

#### 1. MCP 서버 연결 실패
```bash
# 서버 상태 확인
docker-compose logs mcp-server

# 포트 충돌 확인
netstat -tulpn | grep 8001
```

#### 2. Notion API 오류
- Integration 토큰 유효성 확인
- 데이터베이스 권한 설정 확인
- 데이터베이스 스키마 일치 여부 확인

#### 3. GitHub Webhook 오류
- 웹훅 URL 접근 가능성 확인
- 시크릿 값 일치 여부 확인
- n8n 서버 상태 확인

#### 4. OpenAI API 오류
- API 키 유효성 확인
- 크레딧 잔액 확인
- 요청 한도 확인

### 로그 확인 방법

```bash
# Docker Compose 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f mcp-server
docker-compose logs -f n8n

# MCP 서버 직접 실행 시 로그
tail -f mcp-server/logs/mcp-server.log
```

### 성능 최적화

#### 1. 캐시 설정
MCP 서버의 `config.json`에서 캐시 설정을 조정:
```json
{
  "analysis": {
    "cache_enabled": true,
    "cache_ttl_hours": 24,
    "max_cache_size": 1000
  }
}
```

#### 2. 리소스 제한
Docker Compose에서 리소스 제한 설정:
```yaml
services:
  mcp-server:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
```

## 추가 기능

### 1. 슬랙 알림 설정
에러 발생 시 슬랙으로 알림을 받으려면:
1. 슬랙 워크스페이스에서 Incoming Webhook 생성
2. Webhook URL을 `SLACK_WEBHOOK_URL`에 설정

### 2. 다중 리포지토리 지원
여러 리포지토리에서 동일한 워크플로우를 사용하려면:
1. 각 리포지토리에 동일한 웹훅 설정
2. Notion 데이터베이스에서 리포지토리별 필터링 가능

### 3. 커스텀 분석 규칙
MCP 서버의 분석 로직을 수정하여 프로젝트별 요구사항에 맞게 조정 가능합니다.

## 지원 및 기여

문제가 발생하거나 개선 제안이 있으시면:
1. GitHub Issues에 문제 보고
2. Pull Request로 개선사항 기여
3. 문서 개선 제안

---

설정이 완료되면 GitHub에 커밋할 때마다 자동으로 Notion 데이터베이스에 상세한 분석 보고서가 생성됩니다!