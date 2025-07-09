# GitHub to Notion Complete Tracker 설정 가이드

Dashboard 프로젝트에 GitHub to Notion Complete Tracker를 적용하기 위한 완전한 설정 가이드입니다.

## 목차

1. [개요](#개요)
2. [사전 준비사항](#사전-준비사항)
3. [Notion 설정](#notion-설정)
4. [GitHub 설정](#github-설정)
5. [n8n 설정](#n8n-설정)
6. [환경 변수 설정](#환경-변수-설정)
7. [보안 고려사항](#보안-고려사항)
8. [Dashboard 프로젝트 특화 설정](#dashboard-프로젝트-특화-설정)
9. [문제 해결](#문제-해결)

## 개요

이 시스템은 GitHub 저장소의 모든 커밋을 자동으로 분석하고 Notion 데이터베이스에 체계적으로 기록하는 자동화 도구입니다. 특히 Dashboard 프로젝트의 FastAPI/Python 특성에 최적화되어 있습니다.

### 주요 기능

- 🔄 실시간 커밋 추적 및 분석
- 📊 코드 변경사항 자동 분류
- 🐍 Python/FastAPI 프로젝트 특화 분석
- 🔐 보안 변경사항 우선 감지
- 📈 CI/CD 파이프라인 모니터링
- 🎯 중요도 기반 우선순위 설정

## 사전 준비사항

### 필요한 계정 및 도구

1. **Notion 계정** (워크스페이스 관리자 권한)
2. **GitHub 계정** (저장소 관리자 권한)
3. **n8n 인스턴스** (셀프 호스팅 또는 클라우드)
4. **서버 환경** (webhook 수신용)

### 필요한 권한

- GitHub: 저장소 설정 권한 (Webhooks, API access)
- Notion: 데이터베이스 생성 및 Integration 생성 권한
- n8n: 워크플로우 생성 및 실행 권한

## Notion 설정

### 1. Notion Integration 생성

1. [Notion Developers](https://www.notion.so/my-integrations)에 접속
2. "새 통합 만들기" 클릭
3. 다음 정보 입력:
   - **이름**: `Dashboard GitHub Tracker`
   - **로고**: (선택사항)
   - **연결된 워크스페이스**: 대상 워크스페이스 선택
4. **Capabilities** 설정:
   - ✅ 콘텐츠 읽기
   - ✅ 콘텐츠 업데이트
   - ✅ 콘텐츠 삽입
   - ❌ 코멘트 읽기 (선택사항)
5. "제출" 클릭
6. **Internal Integration Token** 복사 및 안전하게 보관

### 2. Notion 데이터베이스 생성

다음 스키마로 데이터베이스를 생성하세요:

#### 데이터베이스 이름: `Dashboard Commits Tracker`

| 속성 이름 | 속성 타입 | 설명 | 필수 여부 |
|-----------|-----------|------|-----------|
| **Title** | Title | 커밋 메시지 | ✅ |
| **Commit Hash** | Rich Text | Git 커밋 해시 | ✅ |
| **Author** | Rich Text | 커밋 작성자 | ✅ |
| **Date** | Date | 커밋 날짜 | ✅ |
| **Repository** | Rich Text | 저장소 이름 | ✅ |
| **Branch** | Rich Text | 브랜치 명 | ✅ |
| **Status** | Select | 커밋 상태 | ✅ |
| **Priority** | Select | 우선순위 | ✅ |
| **Category** | Multi-select | 변경 카테고리 | ✅ |
| **Files Changed** | Number | 변경된 파일 수 | ❌ |
| **Lines Added** | Number | 추가된 라인 수 | ❌ |
| **Lines Deleted** | Number | 삭제된 라인 수 | ❌ |
| **Description** | Rich Text | 상세 설명 | ❌ |
| **URL** | URL | GitHub 커밋 URL | ✅ |
| **CI/CD Status** | Select | 빌드 상태 | ❌ |
| **Reviewer** | Rich Text | 리뷰어 | ❌ |

#### Select 옵션 설정

**Status 옵션:**
- 🔄 `Pending` (회색)
- ✅ `Completed` (초록색)
- 🔍 `Review Required` (노란색)
- ❌ `Failed` (빨간색)
- 🚀 `Deployed` (파란색)

**Priority 옵션:**
- 🔥 `Critical` (빨간색)
- ⚡ `High` (주황색)
- 📋 `Medium` (노란색)
- 📝 `Low` (회색)

**Category 옵션:**
- 🐍 `API Development`
- 🗄️ `Database`
- 🔧 `Configuration`
- 🐛 `Bug Fix`
- ✨ `Feature`
- 🔐 `Security`
- 📚 `Documentation`
- 🧪 `Testing`
- 🚀 `CI/CD`
- 🔄 `Refactoring`
- 🎨 `UI/UX`
- 📦 `Dependencies`

**CI/CD Status 옵션:**
- ✅ `Build Success` (초록색)
- ❌ `Build Failed` (빨간색)
- 🔄 `Building` (노란색)
- ⏸️ `Pending` (회색)

### 3. 데이터베이스 권한 설정

1. 생성한 데이터베이스 페이지에서 우상단 "공유" 버튼 클릭
2. "사용자, 이메일, 통합 초대" 검색창에 Integration 이름 검색
3. `Dashboard GitHub Tracker` Integration 선택
4. 권한을 "편집 가능"으로 설정
5. "초대" 클릭

### 4. 데이터베이스 ID 확인

데이터베이스 URL에서 ID를 추출하세요:
```
https://www.notion.so/your-workspace/DATABASE_ID?v=VIEW_ID
```

## GitHub 설정

### 1. Personal Access Token 생성

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token" → "Generate new token (classic)" 클릭
3. 다음 권한 선택:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `read:user` (Read user profile data)
   - ✅ `user:email` (Access user email addresses)
4. Token 생성 후 안전하게 보관

### 2. Webhook 설정

1. GitHub 저장소 → Settings → Webhooks
2. "Add webhook" 클릭
3. 다음 설정 적용:
   - **Payload URL**: `https://your-n8n-instance.com/webhook/github-commits`
   - **Content type**: `application/json`
   - **Secret**: 강력한 비밀번호 생성 (나중에 환경 변수로 사용)
   - **SSL verification**: Enable SSL verification
4. **이벤트 선택**:
   - ✅ Pushes
   - ✅ Pull requests
   - ✅ Pull request reviews
   - ✅ Repository
5. "Add webhook" 클릭

## n8n 설정

### 1. Credentials 설정

#### GitHub Credentials
1. n8n → Credentials → Add Credential → GitHub
2. **Credential Name**: `Dashboard GitHub`
3. **Access Token**: 생성한 GitHub Personal Access Token
4. "Save" 클릭

#### Notion Credentials
1. n8n → Credentials → Add Credential → Notion API
2. **Credential Name**: `Dashboard Notion`
3. **Internal Integration Token**: Notion Integration Token
4. "Save" 클릭

### 2. 워크플로우 Import

1. `automation/n8n-workflow.json` 파일을 n8n에 import
2. Credentials 연결 확인
3. Webhook URL 업데이트
4. 워크플로우 활성화

## 환경 변수 설정

`.env` 파일에 다음 변수들을 추가하세요:

```bash
# Notion Configuration
NOTION_API_TOKEN=secret_xxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_DATABASE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# GitHub Configuration
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_WEBHOOK_SECRET=your-strong-webhook-secret
GITHUB_REPOSITORY=Sakai04/Dashboard

# n8n Configuration
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/github-commits
N8N_EXECUTION_WEBHOOK_URL=https://your-n8n-instance.com/webhook

# Dashboard Specific Configuration
PROJECT_TYPE=fastapi
PROJECT_LANGUAGE=python
PROJECT_FRAMEWORK=fastapi
CI_CD_PLATFORM=jenkins

# Monitoring Configuration
ENABLE_PRIORITY_DETECTION=true
ENABLE_SECURITY_ALERTS=true
ENABLE_DEPENDENCY_TRACKING=true
ENABLE_CICD_MONITORING=true

# Notification Settings
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx (optional)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxx (optional)
```

## 보안 고려사항

### 1. API 키 보안

- **환경 변수 사용**: 모든 민감한 정보는 환경 변수로 관리
- **액세스 권한 최소화**: 필요한 최소한의 권한만 부여
- **정기적 갱신**: API 토큰을 정기적으로 갱신
- **모니터링**: API 사용량 및 비정상적인 접근 모니터링

### 2. Webhook 보안

```json
{
  "security_measures": {
    "signature_verification": "HMAC-SHA256로 요청 서명 검증",
    "ip_whitelist": "GitHub IP 대역만 허용",
    "rate_limiting": "요청 빈도 제한",
    "ssl_enforcement": "HTTPS 강제 사용"
  }
}
```

### 3. n8n 보안

- **인증 활성화**: Basic Auth 또는 OAuth 설정
- **네트워크 보안**: VPN 또는 방화벽으로 접근 제한
- **정기 업데이트**: n8n 버전 정기 업데이트
- **백업**: 워크플로우 정기 백업

## Dashboard 프로젝트 특화 설정

### 1. 파일 변경 우선순위 매트릭스

| 파일/경로 | 우선순위 | 카테고리 | 자동 알림 |
|-----------|----------|----------|-----------|
| `requirements.txt` | 🔥 Critical | Dependencies | ✅ |
| `Dockerfile` | ⚡ High | Configuration | ✅ |
| `docker-compose.yml` | ⚡ High | Configuration | ✅ |
| `app/main.py` | ⚡ High | API Development | ✅ |
| `app/routers/*.py` | ⚡ High | API Development | ✅ |
| `app/models/*.py` | 📋 Medium | Database | ❌ |
| `app/schemas/*.py` | 📋 Medium | API Development | ❌ |
| `Jenkinsfile` | 🔥 Critical | CI/CD | ✅ |
| `.env*` | 🔥 Critical | Security | ✅ |
| `README.md` | 📝 Low | Documentation | ❌ |
| `docs/*.md` | 📝 Low | Documentation | ❌ |

### 2. FastAPI 특화 분석 규칙

```python
# 우선순위 결정 로직
def calculate_priority(files_changed, commit_message):
    priority_score = 0
    
    # 보안 관련 파일 변경
    security_files = ['.env', 'requirements.txt', 'Dockerfile']
    if any(file in files_changed for file in security_files):
        priority_score += 100
    
    # API 엔드포인트 변경
    api_files = ['app/routers/', 'app/main.py']
    if any(path in str(files_changed) for path in api_files):
        priority_score += 80
    
    # 데이터베이스 스키마 변경
    db_files = ['app/models/', 'app/database.py']
    if any(path in str(files_changed) for path in db_files):
        priority_score += 60
    
    # CI/CD 관련 변경
    cicd_files = ['Jenkinsfile', 'docker-compose.yml']
    if any(file in files_changed for file in cicd_files):
        priority_score += 90
    
    # 커밋 메시지 키워드 분석
    high_priority_keywords = ['fix', 'security', 'urgent', 'hotfix', 'critical']
    if any(keyword in commit_message.lower() for keyword in high_priority_keywords):
        priority_score += 70
    
    return priority_score
```

### 3. Jenkins CI/CD 통합

Jenkins 빌드 상태를 Notion에 자동 업데이트하는 추가 webhook 설정:

```json
{
  "jenkins_webhook": {
    "url": "https://your-n8n-instance.com/webhook/jenkins-build",
    "events": ["build_started", "build_completed", "build_failed"]
  }
}
```

### 4. 의존성 변경 모니터링

`requirements.txt` 변경 시 자동 분석:

```python
# requirements.txt 변경 분석
def analyze_dependency_changes(old_content, new_content):
    old_deps = parse_requirements(old_content)
    new_deps = parse_requirements(new_content)
    
    added = new_deps - old_deps
    removed = old_deps - new_deps
    updated = []
    
    for dep in old_deps & new_deps:
        if old_deps[dep] != new_deps[dep]:
            updated.append(f"{dep}: {old_deps[dep]} → {new_deps[dep]}")
    
    return {
        "added": list(added),
        "removed": list(removed),
        "updated": updated,
        "security_risk": check_security_vulnerabilities(added)
    }
```

## 문제 해결

### 일반적인 문제들

#### 1. Webhook이 트리거되지 않는 경우

**확인사항:**
- GitHub Webhook URL이 올바른지 확인
- n8n 인스턴스가 외부에서 접근 가능한지 확인
- SSL 인증서가 유효한지 확인
- Webhook 비밀키가 올바르게 설정되었는지 확인

**해결방법:**
```bash
# Webhook 테스트
curl -X POST https://your-n8n-instance.com/webhook/github-commits \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -d '{"test": "data"}'
```

#### 2. Notion API 오류

**일반적인 오류:**
- `401 Unauthorized`: Integration Token 확인
- `404 Not Found`: 데이터베이스 ID 확인
- `403 Forbidden`: 데이터베이스 권한 확인

**해결방법:**
```bash
# Notion API 테스트
curl -X GET https://api.notion.com/v1/databases/YOUR_DATABASE_ID \
  -H "Authorization: Bearer YOUR_NOTION_TOKEN" \
  -H "Notion-Version: 2022-06-28"
```

#### 3. n8n 워크플로우 오류

**디버깅 단계:**
1. n8n 워크플로우 실행 로그 확인
2. 각 노드의 입출력 데이터 검토
3. Credentials 연결 상태 확인
4. 네트워크 연결성 테스트

### 성능 최적화

#### 1. 대용량 저장소 처리

```json
{
  "optimization_settings": {
    "batch_processing": true,
    "max_commits_per_batch": 50,
    "processing_delay": "5s",
    "retry_failed_requests": 3
  }
}
```

#### 2. API 사용량 제한

```json
{
  "rate_limiting": {
    "github_api_calls_per_hour": 5000,
    "notion_api_calls_per_minute": 3,
    "webhook_processing_delay": "1s"
  }
}
```

## 유지보수

### 정기 점검 사항

- [ ] API 토큰 만료일 확인 (월 1회)
- [ ] Webhook 응답 시간 모니터링 (주 1회)
- [ ] Notion 데이터베이스 용량 확인 (월 1회)
- [ ] n8n 워크플로우 성능 분석 (월 1회)
- [ ] 보안 로그 검토 (주 1회)

### 업데이트 절차

1. **백업 생성**
   - n8n 워크플로우 export
   - Notion 데이터베이스 백업
   - 환경 변수 백업

2. **테스트 환경에서 검증**
   - 새로운 기능 테스트
   - 기존 기능 회귀 테스트

3. **점진적 배포**
   - 단계별 업데이트 적용
   - 각 단계별 검증

4. **모니터링**
   - 업데이트 후 24시간 집중 모니터링
   - 성능 지표 비교 분석

---

## 지원 및 문의

- **프로젝트 저장소**: [Dashboard Repository](https://github.com/Sakai04/Dashboard)
- **이슈 트래커**: GitHub Issues
- **문서 업데이트**: `docs/` 디렉토리에서 관리

이 가이드는 Dashboard 프로젝트의 GitHub to Notion 통합을 위한 완전한 설정 방법을 제공합니다. 추가 질문이나 문제가 있는 경우 GitHub Issues를 통해 문의해 주세요.