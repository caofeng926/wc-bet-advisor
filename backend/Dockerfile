FROM python:3.12-slim

WORKDIR /app

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc curl && \
    rm -rf /var/lib/apt/lists/*

# Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 应用代码
COPY app ./app

# 数据目录
RUN mkdir -p /app/data
ENV DATABASE_URL=sqlite:///./data/wc_bet.db

EXPOSE 8000

# 启动时先 seed(只 seed 一次)再启动 API
CMD ["sh", "-c", "python -m app.services.seed && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
