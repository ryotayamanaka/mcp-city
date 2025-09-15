# Docker操作用Makefile

.PHONY: help build up down dev prod logs clean

# デフォルトターゲット
help:
	@echo "利用可能なコマンド:"
	@echo "  make api-up   - APIサーバーのみ起動（推奨）"
	@echo "  make api-down - APIサーバー停止"
	@echo "  make logs     - APIサーバーのログを表示"
	@echo "  make clean    - 未使用のDockerリソースをクリーンアップ"
	@echo ""
	@echo "MCPサーバーは別途起動してください:"
	@echo "  python3 food-cart-demo/mcp_servers/vending_machine_mcp_server.py"
	@echo "  python3 food-cart-demo/mcp_servers/epalette_mcp_server.py"

# 全サービスのイメージをビルド
build:
	docker-compose build

# 本番環境でサービスを起動
up:
	docker-compose up -d

# 全サービスを停止・削除
down:
	docker-compose down

# APIサーバーのみ起動（推奨）
api-up:
	docker-compose -f docker-compose.api.yml up -d

# APIサーバー停止
api-down:
	docker-compose -f docker-compose.api.yml down

# 開発環境でサービスを起動（非推奨）
dev:
	docker-compose -f docker-compose.dev.yml up -d

# 開発環境でサービスを停止・削除
dev-down:
	docker-compose -f docker-compose.dev.yml down

# 全サービスのログを表示
logs:
	docker-compose logs -f

# 開発環境のログを表示
dev-logs:
	docker-compose -f docker-compose.dev.yml logs -f

# 未使用のDockerリソースをクリーンアップ
clean:
	docker system prune -f
	docker volume prune -f

# 特定のサービスのログを表示
logs-ui:
	docker-compose logs -f agent-ui

logs-python:
	docker-compose logs -f python-agents

logs-api:
	docker-compose logs -f food-cart-api

# サービスを再起動
restart:
	docker-compose restart

# サービスの状態を確認
status:
	docker-compose ps
