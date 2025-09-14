# agent-ui Dockerfile
# マルチステージビルドで最適化

# ベースイメージ
FROM node:18-alpine AS base

# 依存関係インストールステージ
FROM base AS deps
# pnpmをインストール
RUN npm install -g pnpm
WORKDIR /app
# 依存関係ファイルをコピー
COPY package.json pnpm-lock.yaml* ./
# 依存関係をインストール
RUN pnpm install --frozen-lockfile

# ビルドステージ
FROM base AS builder
WORKDIR /app
# pnpmをインストール
RUN npm install -g pnpm
# 依存関係をコピー
COPY --from=deps /app/node_modules ./node_modules
# ソースコードをコピー
COPY . .
# ビルドを実行
RUN pnpm build

# 本番実行ステージ
FROM base AS runner
WORKDIR /app

# 非rootユーザーを作成
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# 必要なファイルをコピー（publicディレクトリが存在する場合のみ）
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# ユーザーを切り替え
USER nextjs

# ポートを公開
EXPOSE 3000

# 環境変数を設定
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# アプリケーションを起動
CMD ["node", "server.js"]
