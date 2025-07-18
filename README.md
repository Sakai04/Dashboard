# Dashboard - FastAPI CRUD Backend

Dashboard는 FastAPI를 기반으로 한 간단하면서도 강력한 CRUD 백엔드 애플리케이션입니다.

## 주요 기능

### 🚀 핵심 기능
- **FastAPI 기반**: 현대적이고 빠른 Python 웹 프레임워크
- **비동기 CRUD 작업**: PostgreSQL과 SQLAlchemy ORM을 활용한 효율적인 데이터베이스 작업
- **게시판 시스템**: 다중 게시판 지원 (Free, HN, Front, Back)
- **자동 API 문서**: Swagger UI 및 ReDoc 자동 생성

### 🔄 자동화된 커밋 추적 시스템
- **GitHub to Notion 통합**: 모든 커밋이 자동으로 Notion 데이터베이스에 기록
- **지능형 우선순위 분석**: FastAPI 프로젝트 특성에 맞는 커밋 분석 및 우선순위 자동 설정
- **실시간 보안 모니터링**: 보안 관련 파일 변경 시 즉시 알림
- **CI/CD 파이프라인 추적**: Jenkins 빌드 상태 자동 업데이트
- **API 변경사항 추적**: 엔드포인트 관련 파일 변경 시 특별 분석

### 🐳 컨테이너화 및 배포
- **Docker 지원**: 컨테이너 이미지 빌드 및 실행
- **Docker Compose**: 데이터베이스와 함께 간편한 로컬 개발 환경 구성
- **Jenkins CI/CD**: 자동화된 빌드, 테스트, 배포 파이프라인
- **AWS EC2 배포**: 클라우드 환경에서의 프로덕션 배포

## 자동화된 커밋 추적 기능

### 📊 커밋 분석 기능
- **파일별 중요도 분석**: requirements.txt, Dockerfile 등 중요 파일 변경 시 높은 우선순위 자동 설정
- **코드 변경 분류**: API, 데이터베이스, 보안, CI/CD 등 카테고리별 자동 분류
- **통계 수집**: 변경된 파일 수, 추가/삭제된 라인 수 자동 집계
- **브랜치별 추적**: 모든 브랜치의 커밋 내역 체계적 관리

### 🔐 보안 중심 모니터링
- **보안 파일 감지**: .env, requirements.txt, Dockerfile 등 보안 관련 파일 변경 즉시 감지
- **자동 알림 시스템**: Slack/Discord를 통한 실시간 보안 알림
- **우선순위 기반 검토**: Critical/High 우선순위 커밋 자동 플래그 지정

### 📈 개발 생산성 향상
- **커밋 히스토리 시각화**: Notion 데이터베이스를 통한 체계적인 개발 진행상황 추적
- **팀 협업 지원**: 코드 리뷰 및 개발 진행상황 공유 최적화
- **개발 패턴 분석**: 커밋 패턴 분석을 통한 개발 프로세스 개선 인사이트

## 설정 가이드

### 🚀 빠른 시작
1. **저장소 클론**
   ```bash
   git clone https://github.com/Sakai04/Dashboard.git
   cd Dashboard
   ```

2. **환경 변수 설정**
   ```bash
   cp .env.example .env
   # .env 파일의 필요한 값들을 설정하세요
   ```

3. **Docker Compose로 실행**
   ```bash
   docker-compose up -d
   ```

### 📚 자동화 설정
자동화된 커밋 추적 시스템을 설정하려면 다음 가이드를 참조하세요:
- **[완전한 설정 가이드](docs/github-notion-tracker.md)**: GitHub to Notion 통합 상세 설정 방법
- **환경 변수**: `.env.example` 파일의 커밋 추적 관련 설정 참조

## 기술 스택

### Backend
- **FastAPI**: 현대적인 Python 웹 프레임워크
- **SQLAlchemy**: 강력한 ORM 라이브러리
- **PostgreSQL**: 안정적인 관계형 데이터베이스
- **Pydantic**: 데이터 검증 및 직렬화

### DevOps & Automation
- **Docker**: 컨테이너화 기술
- **Jenkins**: CI/CD 파이프라인
- **n8n**: 워크플로우 자동화
- **GitHub Webhooks**: 실시간 이벤트 처리

### Monitoring & Analytics
- **Notion API**: 커밋 데이터 저장 및 시각화
- **Slack/Discord**: 실시간 알림
- **GitHub API**: 상세 커밋 정보 수집

## API 엔드포인트

### 게시판 관리
- `GET /board/` - 모든 게시판 조회
- `GET /board/{board_index}` - 특정 게시판 조회
- `POST /board/` - 새 게시판 생성
- `PUT /board/{board_index}` - 게시판 수정
- `DELETE /board/{board_index}` - 게시판 삭제

### 게시글 관리
- `GET /post/{post_id}` - 특정 게시글 조회
- `GET /post/board/{board_index}` - 게시판별 게시글 목록
- `POST /post/board/{board_index}` - 새 게시글 작성
- `PUT /post/{post_id}` - 게시글 수정
- `DELETE /post/{post_id}` - 게시글 삭제

## 개발 환경

### 로컬 개발
```bash
# 의존성 설치
pip install -r requirements.txt

# 개발 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker 개발
```bash
# 이미지 빌드
docker build -t dashboard .

# 컨테이너 실행
docker run -p 8000:8000 dashboard
```

## 프로젝트 구조

```
Dashboard/
├── app/
│   ├── crud/          # 데이터베이스 CRUD 작업
│   ├── models/        # SQLAlchemy 모델
│   ├── routers/       # FastAPI 라우터
│   ├── schemas/       # Pydantic 스키마
│   ├── database.py    # 데이터베이스 설정
│   └── main.py        # FastAPI 애플리케이션
├── docs/              # 프로젝트 문서
├── automation/        # 자동화 워크플로우
├── Dockerfile         # Docker 이미지 설정
├── docker-compose.yml # 개발 환경 구성
├── Jenkinsfile        # CI/CD 파이프라인
└── requirements.txt   # Python 의존성
```

## 기여하기

1. 이 저장소를 포크하세요
2. 새로운 기능 브랜치를 생성하세요 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋하세요 (`git commit -m 'Add some amazing feature'`)
4. 브랜치에 푸시하세요 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성하세요

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

### 개발년도
2025 winter

### 자동화 특징
이 프로젝트는 모든 커밋이 자동으로 분석되고 Notion에서 체계적으로 관리되는 지능형 개발 추적 시스템을 갖추고 있습니다. 개발자의 생산성 향상과 코드 품질 관리를 위한 현대적인 DevOps 도구들이 완벽하게 통합되어 있습니다.




