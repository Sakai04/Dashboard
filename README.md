# Dashboard - FastAPI 백엔드 & GitHub 커밋 자동화

이 프로젝트는 FastAPI로 구축된 간단한 CRUD 백엔드와 GitHub 커밋을 자동으로 Notion 데이터베이스에 보고하는 자동화 시스템을 포함합니다.

## 🚀 주요 기능

### 기존 FastAPI 백엔드
- Docker로 이미지 생성 가능
- Docker Compose로 PostgreSQL DB와 연결
- Jenkins를 이용한 자동 배포
- AWS EC2 배포 지원

### 새로운 GitHub 커밋 자동화 시스템
- **n8n 워크플로우**: GitHub 웹훅을 통한 자동 커밋 처리
- **MCP 서버**: AI 기반 커밋 분석 및 품질 평가
- **Notion 연동**: 자동 커밋 로깅 및 상세 보고서 생성
- **Docker 지원**: 완전한 컨테이너화된 솔루션

## 📋 요구사항

- Python 3.8+
- Docker & Docker Compose
- GitHub 계정 (관리자 권한)
- Notion 계정 및 워크스페이스
- OpenAI API 키 (선택사항, AI 분석용)

## 🛠️ 빠른 시작

### 1. 저장소 클론
```bash
git clone <repository-url>
cd Dashboard
```

### 2. 환경 설정
```bash
# 환경 변수 템플릿 복사
cp .env.example .env

# .env 파일 편집하여 API 키 및 설정 입력
nano .env
```

### 3. Docker Compose로 전체 스택 실행
```bash
# 모든 서비스 시작 (FastAPI, PostgreSQL, MCP 서버, n8n, PgAdmin)
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 4. 서비스 접속
- **FastAPI 백엔드**: http://localhost:8000
- **MCP 서버**: http://localhost:8001
- **n8n 워크플로우**: http://localhost:5678
- **PgAdmin**: http://localhost (포트 80)

### 5. 통합 테스트 실행
```bash
# MCP 서버가 실행 중인 상태에서
python test_integration.py
```

## 📚 상세 문서

- **[설치 및 설정 가이드](docs/setup-guide.md)**: 전체 시스템 설정 방법
- **[Notion 데이터베이스 템플릿](docs/notion-database-template.md)**: 데이터베이스 스키마 및 설정
- **[환경 변수 가이드](.env.example)**: 모든 설정 옵션 설명

## 🔧 시스템 아키텍처

```
GitHub Repository
       ↓ (Push Event)
GitHub Webhook
       ↓
n8n Workflow
       ↓
MCP Server (Commit Analysis)
       ↓
Notion Database (Report Storage)
```

### 구성 요소

1. **GitHub Webhook**: 푸시 이벤트를 감지하여 n8n으로 전송
2. **n8n Workflow**: 커밋 데이터를 처리하고 MCP 서버 호출
3. **MCP Server**: 커밋 분석, 품질 평가, 보고서 생성
4. **Notion API**: 분석 결과를 데이터베이스에 자동 저장

## 💡 사용 예시

커밋을 푸시하면 자동으로:
- 커밋 메시지 품질 분석 (1-10 점수)
- 파일 변경 통계 수집
- 코드 카테고리 분류 (feature, bugfix, docs 등)
- 잠재적 이슈 식별
- 개선 권장사항 제공
- Notion에 상세 보고서 생성

## 🔍 모니터링 및 로그

```bash
# 모든 서비스 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f mcp-server
docker-compose logs -f n8n

# MCP 서버 상태 확인
curl http://localhost:8001/

# 분석 캐시 상태
curl http://localhost:8001/stats
```

## 🛡️ 보안 설정

- API 키는 환경변수로 관리
- GitHub 웹훅 시크릿 검증
- Docker 컨테이너 격리
- 민감한 정보 로깅 방지

## 🔄 개발 모드

### MCP 서버 개별 실행
```bash
cd mcp-server
pip install -r requirements.txt
python commit-analyzer.py
```

### FastAPI 개발 서버
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📈 성능 최적화

- 커밋 분석 결과 캐싱 (24시간)
- 비동기 처리 지원
- 배치 요청 처리
- 자동 재시도 메커니즘

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python test_integration.py`
5. Submit a pull request

## 📄 라이선스

2025 Winter Project

---

## 🚨 문제 해결

### 일반적인 문제들

**MCP 서버 연결 실패**
```bash
# 서버 상태 확인
docker-compose logs mcp-server

# 포트 충돌 확인
netstat -tulpn | grep 8001
```

**n8n 워크플로우 오류**
- 환경 변수 설정 확인
- Notion 크리덴셜 설정 확인
- GitHub 웹훅 URL 검증

**데이터베이스 연결 문제**
```bash
# PostgreSQL 상태 확인
docker-compose logs db

# 연결 테스트
docker-compose exec db psql -U postgres -d dashboard
```

더 자세한 문제 해결 방법은 [setup-guide.md](docs/setup-guide.md)를 참조하세요.




