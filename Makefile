# Docker操作用Makefile

.PHONY: help api-up api-down logs clean

# デフォルトターゲット
help:
	@echo "利用可能なコマンド:"
	@echo "  make api-up   - 街のシミュレーション（APIサーバー）を起動"
	@echo "  make api-down - 街のシミュレーションを停止"
	@echo "  make logs     - APIサーバーのログを表示"
	@echo "  make clean    - 未使用のDockerリソースをクリーンアップ"
	@echo ""
	@echo "MCPサーバーは別途起動してください:"
	@echo "  python3 food-cart-demo/mcp_servers/vending_machine_mcp_server.py"
	@echo "  python3 food-cart-demo/mcp_servers/epalette_mcp_server.py"

# 街のシミュレーション（APIサーバー）を起動
api-up:
	docker-compose -f docker-compose.api.yml up -d

# 街のシミュレーションを停止
api-down:
	docker-compose -f docker-compose.api.yml down

# APIサーバーのログを表示
logs:
	docker-compose -f docker-compose.api.yml logs -f

# 未使用のDockerリソースをクリーンアップ
clean:
	docker system prune -f
	docker volume prune -f
