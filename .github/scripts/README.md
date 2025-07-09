# GitHub Actions Notion Commit Tracker Scripts

이 디렉토리는 Dashboard 프로젝트의 GitHub Actions 기반 Notion 커밋 추적 시스템을 구현합니다.

## 스크립트 구성

### 1. `commit-analyzer.js`
- GitHub 커밋 정보를 분석하는 메인 스크립트
- FastAPI/Python 프로젝트 특화 분석 로직
- 우선순위 계산 및 카테고리 분류

### 2. `notion-client.js`
- Notion API를 통한 데이터베이스 통합
- 분석된 커밋 정보를 Notion에 저장
- AI 분석 결과 통합

### 3. `ai-analyzer.js`
- OpenAI GPT를 활용한 지능형 커밋 분석
- 한국어 분석 결과 생성
- 보안 위험도 평가 및 권장 조치 제안

## 환경 변수

GitHub Secrets으로 설정해야 하는 환경 변수들:

```bash
# 필수
GITHUB_TOKEN        # GitHub API 접근 (자동 제공)
NOTION_TOKEN        # Notion Integration Token
NOTION_DATABASE_ID  # Notion 데이터베이스 ID

# 선택사항
OPENAI_API_KEY      # OpenAI API 키 (AI 분석용)
```

## 실행 방법

GitHub Actions에서 자동 실행되지만, 로컬에서 테스트할 수 있습니다:

```bash
# 의존성 설치
npm install

# 환경 변수 설정 후 실행
export GITHUB_TOKEN="your_token"
export NOTION_TOKEN="your_notion_token"
export NOTION_DATABASE_ID="your_database_id"

# 커밋 분석
node commit-analyzer.js

# Notion 연동
node notion-client.js
```

## 주요 기능

- **실시간 커밋 분석**: push/PR 이벤트 시 자동 실행
- **FastAPI 특화**: Python/FastAPI 프로젝트에 최적화된 분석
- **보안 중심**: 보안 관련 파일 변경 우선 감지
- **AI 통합**: OpenAI를 통한 지능형 분석
- **한국어 지원**: 모든 분석 결과 한국어 제공