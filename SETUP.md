# 🚀 MCP City セットアップガイド

## 概要

MCP Cityは、Claude Desktopからアクセス可能な自動販売機とePaletteの制御システムです。

## アーキテクチャ

- **APIサーバー**: Docker（環境の一貫性）
- **MCPサーバー**: スタンドアロン（安定性とデバッグの容易さ）

## 前提条件

- Docker & Docker Compose
- Python 3.8以上
- Claude Desktop

## セットアップ手順

### 1. リポジトリのクローン

```bash
git clone https://github.com/ryotayamanaka/mcp-city.git
cd mcp-city
```

### 2. APIサーバーの起動（Docker）

```bash
# APIサーバーのみを起動
make api-up

# または直接実行
docker-compose -f docker-compose.api.yml up -d
```

### 3. MCPサーバーのセットアップ（スタンドアロン）

#### 3.1 Python環境の確認

```bash
python3 --version  # Python 3.8以上が必要
```

#### 3.2 必要パッケージのインストール

```bash
# 最小限のインストール
pip install requests

# または requirements-mcp.txt を使用
pip install -r requirements-mcp.txt
```

#### 3.3 仮想環境の使用（推奨）

```bash
# 仮想環境を作成
python3 -m venv mcp-env

# 仮想環境をアクティベート
# macOS/Linux
source mcp-env/bin/activate

# Windows
mcp-env\Scripts\activate

# パッケージをインストール
pip install requests
```

### 4. MCPサーバーの起動

#### 4.1 自動販売機MCPサーバー

```bash
python3 food-cart-demo/mcp_servers/standalone_mcp_server.py
```

#### 4.2 ePalette MCPサーバー（別ターミナル）

```bash
python3 food-cart-demo/mcp_servers/epalette_mcp_server.py
```

### 5. Claude Desktop設定

Claude Desktopの設定ファイル（`claude_desktop_config.json`）に以下を追加：

```json
{
  "mcpServers": {
    "vending-machine": {
      "command": "python3",
      "args": ["/path/to/mcp-city/food-cart-demo/mcp_servers/standalone_mcp_server.py"],
      "env": {}
    },
    "epalette": {
      "command": "python3",
      "args": ["/path/to/mcp-city/food-cart-demo/mcp_servers/epalette_mcp_server.py"],
      "env": {}
    }
  }
}
```

## 使用方法

### Claude Desktopでの操作

**自動販売機**:
- 「自動販売機の商品一覧を教えて」
- 「在庫状況を確認して」
- 「コーラを2本購入して」
- 「売上データを教えて」

**ePalette**:
- 「ePaletteの状態を教えて」
- 「ディスプレイに『営業中』と表示して」
- 「車両の速度を30km/hに設定して」
- 「車両を一時停止して」

## トラブルシューティング

### APIサーバーが起動しない

```bash
# ログを確認
docker-compose logs food-cart-api

# ポートが使用中か確認
lsof -i :8000
```

### MCPサーバーが接続できない

```bash
# APIサーバーが起動しているか確認
curl http://localhost:8000/api/vending-machine/products

# MCPサーバーのテスト
python3 food-cart-demo/mcp_servers/standalone_mcp_server.py --check-api
```

### Claude DesktopでMCPサーバーが認識されない

1. 設定ファイルのパスが正しいか確認
2. Python環境が正しく設定されているか確認
3. MCPサーバーが起動しているか確認

## 停止方法

### APIサーバーの停止

```bash
make api-down
# または
docker-compose -f docker-compose.api.yml down
```

### MCPサーバーの停止

各ターミナルで `Ctrl+C` を押して停止

## 開発

### ログの確認

```bash
# APIサーバーのログ
make logs

# MCPサーバーのログ
# ターミナルに直接出力されます
```

### 設定の変更

- **API設定**: `food-cart-demo/server.py`
- **MCP設定**: `food-cart-demo/mcp_servers/*.py`

## サポート

問題が発生した場合は、GitHubのIssuesで報告してください。
