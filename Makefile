# Docker操作用Makefile

.PHONY: help up down api-up api-down db-up db-down logs logs-api logs-db clean

# デフォルトターゲット
help:
	@echo "利用可能なコマンド:"
	@echo "  make up          - 全サービス（API + データベース）を起動"
	@echo "  make down        - 全サービスを停止"
	@echo "  make api-up      - APIサーバーのみ起動"
	@echo "  make api-down    - APIサーバーのみ停止"
	@echo "  make db-up       - データベースのみ起動"
	@echo "  make db-down     - データベースのみ停止"
	@echo "  make logs        - 全サービスのログを表示"
	@echo "  make logs-api    - APIサーバーのログを表示"
	@echo "  make logs-db     - データベースのログを表示"
	@echo "  make clean       - 未使用のDockerリソースをクリーンアップ"
	@echo ""
	@echo "MCPサーバーは別途起動してください:"
	@echo "  python3 food-cart-demo/mcp_servers/vending_machine_mcp_server.py"
	@echo "  python3 food-cart-demo/mcp_servers/epalette_mcp_server.py"
	@echo "  python3 city-database/mcp_servers/city_database_client_mcp_server.py"

# 全サービスを起動
up:
	docker-compose up -d

# 全サービスを停止
down:
	docker-compose down

# APIサーバーのみ起動
api-up:
	docker-compose up -d food-cart-api

# APIサーバーのみ停止
api-down:
	docker-compose stop food-cart-api

# データベースのみ起動
db-up:
	docker-compose up -d city-database

# データベースのみ停止
db-down:
	docker-compose stop city-database

# 全サービスのログを表示
logs:
	docker-compose logs -f

# APIサーバーのログを表示
logs-api:
	docker-compose logs -f food-cart-api

# データベースのログを表示
logs-db:
	docker-compose logs -f city-database

# 未使用のDockerリソースをクリーンアップ
clean:
	docker system prune -f
	docker volume prune -f
