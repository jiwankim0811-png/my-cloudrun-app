# ==============================================================================
# BFS vs DFS Maze Visualizer - Cloud Run 배포용 Dockerfile
# ==============================================================================

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# 의존성 설치
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 서버 소스 복사
COPY server/ .

EXPOSE 8080

CMD ["python", "main.py"]
