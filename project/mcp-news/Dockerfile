FROM python:3.10-slim

WORKDIR /app
RUN pip install fastmcp feedparser uvicorn mysql-connector-python python-dotenv openai

COPY server.py .
COPY .env .
# 서버 실행 명령어 (SSE 모드)
CMD ["python", "server.py"]
