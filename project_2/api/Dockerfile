# api/Dockerfile
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# FastAPI 실행 (호스트 0.0.0.0 필수)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]