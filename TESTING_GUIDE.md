# GitHub Actions Notion 커밋 트래커 테스트 가이드

## 구현 완료 사항

✅ **GitHub Actions 워크플로우** (`.github/workflows/notion-tracker.yml`)
✅ **커밋 분석 스크립트** (`.github/scripts/commit-analyzer.js`)
✅ **Notion 연동 스크립트** (`.github/scripts/notion-client.js`)
✅ **OpenAI 분석 스크립트** (`.github/scripts/ai-analyzer.js`)
✅ **완전한 문서화** (README.md 업데이트)

## 테스트 방법

### 1. GitHub Secrets 설정 (필수)
저장소 Settings → Secrets and variables → Actions에서 설정:

```bash
NOTION_TOKEN=secret_xxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_DATABASE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxx  # 선택사항
```

### 2. Notion 데이터베이스 생성
다음 속성들을 포함한 Notion 데이터베이스 생성:

- Name (Title) - 커밋 제목
- Commit Hash (Text) - 짧은 커밋 해시
- Author (Text) - 작성자
- Date (Date) - 커밋 날짜
- Priority (Select: Critical, High, Medium, Low)
- Status (Select: Completed, Pending, Review Required)
- Categories (Multi-select)
- Priority Score (Number)
- Files Changed (Number)
- Security Related (Checkbox)
- API Related (Checkbox)
- Database Related (Checkbox)

### 3. 자동 테스트
다음 중 하나를 실행하면 자동으로 워크플로우가 실행됩니다:

1. **main, develop, master 브랜치에 push**
2. **PR을 main/develop 브랜치로 병합**

### 4. 수동 테스트 (로컬)
```bash
cd .github/scripts
npm install

# 환경 변수 설정
export GITHUB_TOKEN="your_github_token"
export NOTION_TOKEN="your_notion_token" 
export NOTION_DATABASE_ID="your_database_id"
export OPENAI_API_KEY="your_openai_key"  # 선택사항

# 커밋 분석 테스트
node commit-analyzer.js

# Notion 연동 테스트  
node notion-client.js
```

## 예상 결과

### GitHub Actions 로그에서 확인할 수 있는 내용:
- 📦 커밋 개수 및 분석 진행상황
- 🔍 각 커밋의 우선순위 및 카테고리
- 📝 Notion 페이지 생성 결과
- 🤖 AI 분석 결과 (OpenAI 설정 시)

### Notion 데이터베이스에 생성되는 내용:
- 커밋별 상세 분석 페이지
- FastAPI 프로젝트 특화 분류
- 우선순위 점수 및 상태
- AI 분석 요약 (설정 시)

## 주요 특징

🚀 **완전 자동화**: Push 즉시 분석 및 Notion 업데이트
🐍 **FastAPI 특화**: Python/FastAPI 프로젝트 최적화
🔒 **보안 중심**: 보안 파일 변경 우선 감지
🤖 **AI 통합**: GPT를 통한 지능형 분석
🇰🇷 **한국어 지원**: 모든 결과 한국어 제공
🛡️ **견고한 처리**: 오류 시 graceful 처리

## 문제 해결

### 워크플로우가 실행되지 않는 경우:
1. GitHub Secrets 설정 확인
2. 브랜치명 확인 (main/develop/master)
3. Actions 탭에서 실행 로그 확인

### Notion 연동 실패 시:
1. NOTION_TOKEN 유효성 확인
2. NOTION_DATABASE_ID 정확성 확인
3. Integration이 데이터베이스에 연결되었는지 확인
4. 데이터베이스 속성이 올바르게 설정되었는지 확인

이제 로컬호스트 webhook 문제 없이 완전히 클라우드에서 실행되는 커밋 추적 시스템이 준비되었습니다!