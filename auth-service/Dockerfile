# Auth Service用Dockerfile
FROM python:3.11-alpine

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージのインストール
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    && rm -rf /var/cache/apk/*

# Pythonの依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# ポート8001を公開
EXPOSE 8001

# サーバーを起動
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
