FROM python:3.13

# 환경변수 설정: 바이트코드 생성 방지 및 stdout 바로 출력
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 작업 디렉터리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 프로젝트 전체 복사
COPY . .

# 컨테이너가 노출할 포트 (FastAPI 기본 포트)
EXPOSE 8000

# 애플리케이션 실행 (production 환경에서는 --reload 옵션 없이 실행)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
