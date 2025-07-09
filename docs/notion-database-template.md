# Notion 데이터베이스 템플릿

이 문서는 GitHub 커밋 자동화 워크플로우에서 사용할 Notion 데이터베이스의 구조와 설정 방법을 설명합니다.

## 데이터베이스 개요

### 목적
- GitHub 커밋 정보를 구조화된 형태로 저장
- MCP 서버의 분석 결과를 시각화
- 프로젝트 진행 상황 추적 및 모니터링
- 코드 품질 및 개발 패턴 분석

### 주요 기능
- 자동 커밋 로깅
- 품질 점수 추적
- 파일 변경 통계
- AI 기반 분석 보고서
- 개발자별 활동 모니터링

## 데이터베이스 스키마

### 필수 속성 (Required Properties)

| 속성 이름 | 타입 | 설명 | 예시 |
|-----------|------|------|------|
| **Title** | Title | 커밋 메시지 (자동 제목) | `feat: add user authentication` |
| **Commit Hash** | Text | Git 커밋 해시 (짧은 형태) | `a1b2c3d` |
| **Author** | Text | 커밋 작성자 이름 | `John Doe` |
| **Date** | Date | 커밋 날짜 및 시간 | `2025-01-09` |
| **Repository** | Text | 저장소 이름 | `Dashboard` |

### 통계 속성 (Statistics Properties)

| 속성 이름 | 타입 | 설명 | 예시 |
|-----------|------|------|------|
| **Files Changed** | Number | 변경된 파일 총 개수 | `5` |
| **Added Lines** | Number | 추가된 코드 라인 수 | `127` |
| **Deleted Lines** | Number | 삭제된 코드 라인 수 | `43` |
| **Net Lines** | Formula | 순 증가 라인 수 (Added - Deleted) | `84` |

### 분류 속성 (Classification Properties)

| 속성 이름 | 타입 | 설명 | 선택 옵션 |
|-----------|------|------|----------|
| **Branch** | Select | 브랜치 이름 | `main`, `develop`, `feature/*`, `hotfix/*` |
| **Category** | Select | 커밋 유형 | `feature`, `bugfix`, `refactor`, `docs`, `test`, `chore` |
| **Impact Level** | Select | 영향도 수준 | `Low`, `Medium`, `High` |
| **Quality Score** | Select | 코드 품질 점수 | `Poor (1-3)`, `Fair (4-6)`, `Good (7-8)`, `Excellent (9-10)` |

### 상세 정보 속성 (Detail Properties)

| 속성 이름 | 타입 | 설명 | 예시 |
|-----------|------|------|------|
| **Analysis Report** | Text | MCP 분석 보고서 (마크다운) | `# Commit Analysis Report...` |
| **Commit URL** | URL | GitHub 커밋 링크 | `https://github.com/user/repo/commit/a1b2c3d` |
| **Issues Identified** | Multi-select | 식별된 문제들 | `Large commit`, `Missing tests` |
| **Recommendations** | Text | 개선 권장사항 | `Consider splitting large commits` |

### 선택적 속성 (Optional Properties)

| 속성 이름 | 타입 | 설명 | 사용 목적 |
|-----------|------|------|----------|
| **Sprint** | Select | 스프린트 정보 | 애자일 개발 추적 |
| **Epic** | Relation | 연관 에픽 | 대형 기능 추적 |
| **Reviewer** | Person | 코드 리뷰어 | 리뷰 프로세스 관리 |
| **Status** | Select | 처리 상태 | `Pending`, `Reviewed`, `Deployed` |

## 데이터베이스 설정 가이드

### 1. 새 데이터베이스 생성

```
1. Notion에서 새 페이지 생성
2. "Database" → "Table" 선택
3. 제목: "GitHub Commits" 또는 "Code Repository Tracker"
```

### 2. 속성 추가 순서

#### Step 1: 기본 속성 (자동 생성됨)
- **Title**: 기본으로 생성되는 제목 속성

#### Step 2: 필수 텍스트 속성
```
+ Add Property → Text
- Name: "Commit Hash"
- Description: "Git commit hash (short form)"

+ Add Property → Text  
- Name: "Author"
- Description: "Commit author name"

+ Add Property → Text
- Name: "Repository" 
- Description: "Repository name"
```

#### Step 3: 날짜 및 숫자 속성
```
+ Add Property → Date
- Name: "Date"
- Description: "Commit timestamp"

+ Add Property → Number
- Name: "Files Changed"
- Description: "Total number of files changed"

+ Add Property → Number
- Name: "Added Lines"
- Description: "Number of lines added"

+ Add Property → Number  
- Name: "Deleted Lines"
- Description: "Number of lines deleted"
```

#### Step 4: 선택 속성 (Select)
```
+ Add Property → Select
- Name: "Branch"
- Options: main, develop, feature, hotfix, release

+ Add Property → Select
- Name: "Category" 
- Options: feature, bugfix, refactor, docs, test, chore, style

+ Add Property → Select
- Name: "Impact Level"
- Options: 🟢 Low, 🟡 Medium, 🔴 High

+ Add Property → Select
- Name: "Quality Score"
- Options: 🔴 Poor (1-3), 🟡 Fair (4-6), 🟢 Good (7-8), 🟦 Excellent (9-10)
```

#### Step 5: 상세 정보 속성
```
+ Add Property → Text
- Name: "Analysis Report"
- Description: "Detailed analysis from MCP server"

+ Add Property → URL
- Name: "Commit URL"
- Description: "Link to GitHub commit"

+ Add Property → Multi-select
- Name: "Issues Identified"
- Options: Large commit, Missing tests, Poor message, WIP commit

+ Add Property → Text
- Name: "Recommendations"
- Description: "Improvement suggestions"
```

### 3. 수식 속성 추가 (선택사항)

#### Net Lines 계산
```
+ Add Property → Formula
- Name: "Net Lines"
- Formula: prop("Added Lines") - prop("Deleted Lines")
- Description: "Net change in lines of code"
```

#### Quality Rating
```
+ Add Property → Formula
- Name: "Quality Rating"
- Formula: 
  if(prop("Quality Score") == "Excellent (9-10)", "⭐⭐⭐⭐⭐",
  if(prop("Quality Score") == "Good (7-8)", "⭐⭐⭐⭐",
  if(prop("Quality Score") == "Fair (4-6)", "⭐⭐⭐",
  if(prop("Quality Score") == "Poor (1-3)", "⭐⭐", "⭐"))))
```

## 뷰 설정 (Database Views)

### 1. 기본 테이블 뷰
- **이름**: "All Commits"
- **정렬**: Date (내림차순)
- **필터**: 없음
- **그룹**: 없음

### 2. 브랜치별 뷰
- **이름**: "By Branch"
- **정렬**: Date (내림차순)
- **필터**: 없음
- **그룹**: Branch

### 3. 작성자별 뷰
- **이름**: "By Author"
- **정렬**: Date (내림차순)
- **필터**: 없음
- **그룹**: Author

### 4. 품질 점수별 뷰
- **이름**: "Quality Overview"
- **정렬**: Quality Score (내림차순)
- **필터**: 없음
- **그룹**: Quality Score

### 5. 최근 커밋 뷰
- **이름**: "Recent Activity"
- **정렬**: Date (내림차순)
- **필터**: Date is within last 7 days
- **그룹**: 없음

## 템플릿 사용법

### 1. 데이터베이스 템플릿 복사

이 JSON 템플릿을 사용하여 Notion에서 데이터베이스를 빠르게 설정할 수 있습니다:

```json
{
  "database_template": {
    "title": "GitHub Commits",
    "description": "Automated commit tracking and analysis",
    "properties": {
      "Title": {"type": "title"},
      "Commit Hash": {"type": "rich_text"},
      "Author": {"type": "rich_text"},
      "Date": {"type": "date"},
      "Repository": {"type": "rich_text"},
      "Branch": {
        "type": "select",
        "options": ["main", "develop", "feature", "hotfix", "release"]
      },
      "Category": {
        "type": "select", 
        "options": ["feature", "bugfix", "refactor", "docs", "test", "chore"]
      },
      "Impact Level": {
        "type": "select",
        "options": ["🟢 Low", "🟡 Medium", "🔴 High"]
      },
      "Quality Score": {
        "type": "select",
        "options": ["🔴 Poor (1-3)", "🟡 Fair (4-6)", "🟢 Good (7-8)", "🟦 Excellent (9-10)"]
      },
      "Files Changed": {"type": "number"},
      "Added Lines": {"type": "number"},
      "Deleted Lines": {"type": "number"},
      "Analysis Report": {"type": "rich_text"},
      "Commit URL": {"type": "url"},
      "Issues Identified": {"type": "multi_select"},
      "Recommendations": {"type": "rich_text"}
    }
  }
}
```

### 2. 수동 설정 체크리스트

- [ ] 데이터베이스 생성
- [ ] 필수 속성 추가 (Title, Commit Hash, Author, Date, Repository)
- [ ] 통계 속성 추가 (Files Changed, Added Lines, Deleted Lines)
- [ ] 분류 속성 추가 (Branch, Category, Impact Level, Quality Score)
- [ ] 상세 속성 추가 (Analysis Report, Commit URL)
- [ ] 뷰 설정 (기본, 브랜치별, 작성자별, 품질별)
- [ ] Integration 권한 부여
- [ ] 데이터베이스 ID 획득

## Integration 설정

### 1. Notion Integration 생성
1. [Notion Developers](https://developers.notion.com/) 접속
2. "New integration" 클릭
3. 기본 정보 입력:
   - **Name**: GitHub Commit Tracker
   - **Logo**: GitHub 로고 (선택사항)
   - **Description**: Automated GitHub commit analysis and reporting

### 2. 권한 설정
다음 권한들을 활성화:
- [x] Read content
- [x] Update content  
- [x] Insert content
- [ ] Read comments (선택사항)
- [ ] Insert comments (선택사항)

### 3. 데이터베이스 공유
1. 생성한 데이터베이스 페이지로 이동
2. 우측 상단 "Share" 버튼 클릭
3. "Invite" 섹션에서 생성한 Integration 선택
4. "Can edit" 권한 부여

## 사용 예시

### 자동 생성되는 엔트리 예시

| Title | Commit Hash | Author | Date | Repository | Branch | Category | Quality Score |
|-------|-------------|--------|------|------------|--------|----------|---------------|
| feat: add user authentication | a1b2c3d | John Doe | 2025-01-09 | Dashboard | feature/auth | feature | 🟢 Good (7-8) |
| fix: resolve login bug | e4f5g6h | Jane Smith | 2025-01-09 | Dashboard | hotfix/login | bugfix | 🟡 Fair (4-6) |
| docs: update API documentation | i7j8k9l | Bob Wilson | 2025-01-08 | Dashboard | main | docs | 🟦 Excellent (9-10) |

### 분석 보고서 예시

```markdown
# Commit Analysis Report

## Commit Details
- **Hash**: `a1b2c3d...`
- **Message**: feat: add user authentication
- **Author**: John Doe
- **Repository**: Dashboard
- **Branch**: feature/auth

## Analysis Summary
- **Category**: feature
- **Quality Score**: 7/10
- **Impact Level**: medium

## File Changes
- **Total Files**: 8
- **Added**: 3 files
- **Modified**: 5 files
- **Removed**: 0 files

## Issues Identified
- No issues identified

## Recommendations
- Add unit tests for authentication module
- Consider adding integration tests

## AI Insights
This commit introduces a well-structured authentication system with proper separation of concerns. The implementation follows security best practices and includes proper error handling.

---
*Report generated on 2025-01-09 12:30:45 UTC*
```

## 유지보수 및 최적화

### 정기 작업
- [ ] 월간 품질 점수 분석
- [ ] 브랜치별 활동 검토  
- [ ] 개발자별 생산성 추적
- [ ] 이슈 패턴 분석

### 성능 최적화
- 오래된 엔트리 아카이브 (6개월 이상)
- 대용량 분석 보고서 압축
- 불필요한 속성 제거
- 인덱싱 최적화

이 템플릿을 사용하면 GitHub 커밋 활동을 체계적으로 추적하고 분석할 수 있습니다!