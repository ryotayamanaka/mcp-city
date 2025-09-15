# 🏙️ MCP City

**街のシミュレーションとMCPサーバーの世界観を表現するプロジェクト**

MCP Cityは、街をシミュレーションしたUIと、その街に存在する様々なデバイスにAIエージェントからアクセスするためのMCP（Model Context Protocol）サーバーを提供します。各デバイスは独自のMCPサーバーを持ち、Claude DesktopなどのAIエージェントが街のデバイスと自然にやり取りできる世界を実現します。

## 🌟 コンセプト

### 街のシミュレーション
MCP Cityは、現実の街のように様々なデバイスが存在する仮想の街をシミュレーションします。各デバイスは独自の機能とAPIを持ち、街の一部として統合されています。

### MCPサーバーの世界観
各デバイスは独自のMCPサーバーを持ち、AIエージェントが自然言語でデバイスとやり取りできる世界を実現します。これにより、AIエージェントは街の住民のようにデバイスを操作できます。

### 現在のデバイス
- **ePalette**: 自動運転の移動販売車両
- **自動販売機**: 飲み物や軽食を提供する販売機

### 将来の拡張
街にはさらに多くのデバイスが追加される予定です。各デバイスは独自のMCPサーバーを持ち、AIエージェントとの自然な対話を可能にします。

## 🚀 クイックスタート

### 前提条件

- Docker & Docker Compose（街のシミュレーション用）
- Python 3.8+（MCPサーバー用）
- Claude Desktop（AIエージェント）

### アーキテクチャ

**街のシミュレーション**: Docker（環境の一貫性のため）
**MCPサーバー**: スタンドアロン（安定性とデバッグの容易さのため）

#### 1. 街のシミュレーション起動（Docker）

```bash
# 街のAPIサーバーを起動
make api-up

# または直接実行
docker-compose -f docker-compose.api.yml up -d
```

#### 2. デバイスのMCPサーバー起動（スタンドアロン）

```bash
# 自動販売機のMCPサーバー
python3 food-cart-demo/mcp_servers/vending_machine_mcp_server.py

# ePaletteのMCPサーバー（別ターミナル）
python3 food-cart-demo/mcp_servers/epalette_mcp_server.py
```

#### 3. Claude Desktop設定

`claude_desktop_config.json`をClaude Desktopの設定ディレクトリにコピーして、AIエージェントとして街のデバイスと対話できるようにします。

**設定ファイルの使い方**:
- すべてのデバイスが含まれています
- 特定のデバイスのみを使用したい場合は、不要なMCPサーバーの設定をコメントアウトしてください
- 例：自動販売機のみ使用する場合
  ```json
  {
    "mcpServers": {
      "vending-machine": { ... },
      // "epalette": { ... }  // コメントアウト
    }
  }
  ```

#### 4. サービスの停止

```bash
# 街のシミュレーション停止
make api-down

# MCPサーバーの停止
# Ctrl+C で各サーバーを停止
```

## 📁 プロジェクト構成

```
/
├── food-cart-demo/                    # 街のシミュレーション（FastAPI）
│   ├── server.py                      # 街のAPIサーバー
│   ├── index.html                     # 街のUI（3D表示）
│   ├── mcp_servers/                   # 各デバイスのMCPサーバー
│   │   ├── vending_machine_mcp_server.py   # 自動販売機のMCPサーバー
│   │   └── epalette_mcp_server.py    # ePaletteのMCPサーバー
│   └── mockdata/                      # 街のデータ
├── claude_desktop_config.json         # Claude Desktop設定ファイル
├── docker-compose.api.yml             # 街のシミュレーション用
├── requirements-mcp.txt               # MCPサーバー用依存関係
├── SETUP.md                          # 詳細セットアップガイド
└── Makefile                          # 便利なコマンド集
```

## 🌐 街の構成

### 街のシミュレーション
| サービス | ポート | 説明 | 実行方法 |
|---------|--------|------|----------|
| city-api | 8000 | 街のAPIサーバー（FastAPI） | Docker |

### 街のデバイス（MCPサーバー）
| デバイス | MCPサーバー | 説明 | 実行方法 |
|---------|-------------|------|----------|
| 自動販売機 | vending_machine_mcp_server.py | 飲み物・軽食の販売 | スタンドアロン |
| ePalette | epalette_mcp_server.py | 自動運転移動販売車両 | スタンドアロン |

## 🤖 AIエージェントとの統合

### Claude Desktop
このプロジェクトはClaude DesktopをメインのAIエージェントとして使用します。Claude Desktopは街の住民のように、自然言語で街のデバイスと対話できます。

### 街のデバイスとの対話

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

### 将来のAIエージェント
Claude Desktop以外のAIエージェントも、MCPプロトコルをサポートしていれば街のデバイスと対話できます。

## 🛠️ 利用可能なコマンド

```bash
make help      # 利用可能なコマンドを表示
make api-up    # APIサーバーのみ起動
make api-down  # APIサーバー停止
make logs      # APIサーバーのログを表示
make clean     # 未使用のDockerリソースをクリーンアップ
```

## 🔧 Claude Desktop設定

Claude DesktopでMCPサーバーを使用するには、以下の設定ファイルを使用してください：

```json
{
  "mcpServers": {
    "vending-machine": {
      "command": "python3",
      "args": ["/path/to/food-cart-demo/mcp_servers/standalone_mcp_server.py"],
      "env": {}
    },
    "epalette": {
      "command": "python3",
      "args": ["/path/to/food-cart-demo/mcp_servers/epalette_mcp_server.py"],
      "env": {}
    }
  }
}
```

## 🔧 開発

### 街のシミュレーション開発

街のシミュレーションはDockerで管理され、新しいデバイスを追加する際は以下の手順で行います：

1. **デバイスAPIの実装**: `food-cart-demo/server.py`にエンドポイントを追加
2. **デバイスUIの実装**: `food-cart-demo/index.html`に3D表示を追加
3. **MCPサーバーの実装**: `food-cart-demo/mcp_servers/`に新しいMCPサーバーを追加

### MCPサーバー開発

各デバイスのMCPサーバーは独立して開発・テストできます：

- **軽量**: `requests`パッケージのみで動作
- **デバッグ容易**: 直接実行でデバッグ可能
- **拡張性**: 新しいデバイス用のMCPサーバーを簡単に追加

### トラブルシューティング

1. **街のシミュレーションが起動しない**
   ```bash
   docker-compose logs food-cart-api
   ```

2. **MCPサーバーが接続できない**
   ```bash
   # 街のAPIサーバーが起動しているか確認
   curl http://localhost:8000/api/vending-machine/products
   ```

3. **ポートが使用中**
   ```bash
   lsof -i :8000
   ```

## 📚 詳細ドキュメント

- `SETUP.md` - 詳細なセットアップガイド
- `food-cart-demo/README.md` - 街のシミュレーションの詳細