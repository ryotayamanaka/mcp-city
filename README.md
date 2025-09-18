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
- **街のデータベース**: 住民、事業所、交通データの分析用データベース

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

#### 1. プロジェクトのクローン

```bash
git clone https://github.com/ryotayamanaka/mcp-city.git
cd mcp-city
```

#### 2. 環境変数の設定

```bash
# macOS/Linux
export MCP_CITY_PATH=$(pwd)

# Windows
set MCP_CITY_PATH=%CD%
```

#### 3. 街のシミュレーション起動（Docker）

```bash
# 全サービスを起動（API + データベース）
make up

# または個別に起動
make api-up    # APIサーバーのみ
make db-up     # データベースのみ
```

#### 4. デバイスのMCPサーバー起動（スタンドアロン）

**前提条件**: MCPサーバーには`requests`パッケージが必要です。インストールされていない場合は以下を実行してください：

```bash
pip install requests
```

**MCPサーバーの起動**:

```bash
# 自動販売機のMCPサーバー
python3 city-devices/mcp_servers/vending_machine_mcp_server.py

# ePaletteのMCPサーバー（別ターミナル）
python3 city-devices/mcp_servers/epalette_mcp_server.py

# 街のデータベースMCPサーバー（別ターミナル）
python3 city-database/mcp_servers/city_database_client_mcp_server.py
```

### 認証（簡潔）

- APIキー認証＋デバイス別権限（SQLite）を採用しています。
- まずAPIサーバーを起動してください（Docker または開発用スタンドアロン）。

開発用スタンドアロン起動（任意）:
```bash
cd city-devices
python3 -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload \
  > ../logs/server.out 2>&1 &
```

管理者APIキーの作成（最短手順）:
```bash
python3 - <<'PY'
from auth.database import auth_db
import sqlite3
conn = sqlite3.connect('auth/auth.db'); conn.row_factory = sqlite3.Row
admin = conn.execute("SELECT id FROM users WHERE username='admin'").fetchone()
if admin:
    auth_db.set_device_permission(admin['id'], 'epalette', True, True)
    auth_db.set_device_permission(admin['id'], 'vending_machine', True, True)
    print(auth_db.create_api_key(admin['id'], 'CLI Generated Key', 30))
else:
    print('admin user not found')
conn.close()
PY
```

リクエスト例（AuthorizationヘッダにAPIキー）:
```bash
API_KEY=... # 上で発行されたキー
# e-Palette（読み取り）
curl -H "Authorization: Bearer $API_KEY" \
  http://localhost:8000/api/epalette/display/status
# e-Palette（書き込み）
curl -H "Authorization: Bearer $API_KEY" -H 'Content-Type: application/json' \
  -d '{"text":"OPEN","subtext":"WELCOME"}' \
  http://localhost:8000/api/epalette/display/text
# Vending（読み取り）
curl -H "Authorization: Bearer $API_KEY" \
  http://localhost:8000/api/vending-machine/products
# Vending（購入）
curl -H "Authorization: Bearer $API_KEY" -H 'Content-Type: application/json' \
  -d '{"product_id":"p001","quantity":1}' \
  http://localhost:8000/api/vending-machine/purchase
```

#### 5. Claude Desktop設定

**重要**: Claude Desktopでは絶対パスを使用する必要があります。

**macOS**:
```bash
# 設定ディレクトリを作成
mkdir -p ~/Library/Application\ Support/Claude

# サンプル設定ファイルをコピー
cp claude_desktop_config.sample.json ~/Library/Application\ Support/Claude/claude_desktop_config.json

# パスを実際の環境に合わせて編集
# /path/to/your/mcp-city を実際のパスに変更してください
```

**Windows**:
```cmd
# 設定ディレクトリを作成
mkdir %APPDATA%\Claude

# サンプル設定ファイルをコピー
copy claude_desktop_config.sample.json %APPDATA%\Claude\claude_desktop_config.json

# パスを実際の環境に合わせて編集
# /path/to/your/mcp-city を実際のパスに変更してください
```

**設定ファイルの使い方**:
- すべてのデバイスが含まれています
- 特定のデバイスのみを使用したい場合は、不要なMCPサーバーの設定をコメントアウトしてください
- 例：自動販売機のみ使用する場合
  ```json
  {
    "mcpServers": {
      "vending-machine": { ... },
      // "epalette": { ... }  // コメントアウト
      // "city-database": { ... }  // コメントアウト
    }
  }
  ```

#### 6. Claude Desktop再起動

設定ファイルを更新した後、Claude Desktopを完全に再起動してください。

#### 7. サービスの停止

```bash
# 全サービス停止
make down

# 個別停止
make api-down  # APIサーバー停止
make db-down   # データベース停止

# MCPサーバーの停止
# Ctrl+C で各サーバーを停止
```

## 📁 プロジェクト構成

```
/
├── city-devices/                      # 街のデバイス（FastAPI）
│   ├── server.py                      # 街のAPIサーバー
│   ├── index.html                     # 街のUI（3D表示）
│   ├── index-3d.html                  # 3Dデモ
│   ├── mcp_servers/                   # 各デバイスのMCPサーバー
│   │   ├── vending_machine_mcp_server.py   # 自動販売機のMCPサーバー
│   │   └── epalette_mcp_server.py    # ePaletteのMCPサーバー
│   └── mockdata/                      # 街のデータ
├── city-database/                     # 街のデータベース
│   ├── data/                          # CSVデータ
│   │   ├── residents.csv              # 住民データ
│   │   ├── businesses.csv             # 事業所データ
│   │   └── traffic.csv                # 交通データ
│   ├── database/                      # DuckDBファイル
│   │   └── city.db                    # データベースファイル
│   ├── mcp_servers/                   # データベースMCPサーバー
│   │   └── city_database_client_mcp_server.py
│   └── scripts/                       # 初期化スクリプト
│       └── init_database.sql
├── claude_desktop_config.sample.json  # Claude Desktop設定サンプルファイル
├── docker-compose.yml                 # 統合Docker Compose
└── Makefile                          # 便利なコマンド集
```

## 🌐 街の構成

### 街のシミュレーション
| サービス | ポート | 説明 | 実行方法 |
|---------|--------|------|----------|
| city-devices-api | 8000 | 街のデバイスAPIサーバー（FastAPI） | Docker |
| city-database | 5432, 8080 | 街のデータベース（DuckDB） | Docker |

### 街のデバイス（MCPサーバー）
| デバイス | MCPサーバー | 説明 | 実行方法 |
|---------|-------------|------|----------|
| 自動販売機 | vending_machine_mcp_server.py | 飲み物・軽食の販売 | スタンドアロン |
| ePalette | epalette_mcp_server.py | 自動運転移動販売車両 | スタンドアロン |
| 街のデータベース | city_database_client_mcp_server.py | 住民・事業所・交通データ分析 | スタンドアロン |

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

**街のデータベース**:
- 「住民の年収分布を教えて」
- 「事業所の売上ランキングTOP10を表示して」
- 「渋谷通りの交通状況を分析して」
- 「中央区の住民の平均年収を教えて」

### 将来のAIエージェント
Claude Desktop以外のAIエージェントも、MCPプロトコルをサポートしていれば街のデバイスと対話できます。

## 🛠️ 利用可能なコマンド

```bash
make help      # 利用可能なコマンドを表示
make up        # 全サービス（API + データベース）を起動
make down      # 全サービスを停止
make api-up    # APIサーバーのみ起動
make api-down  # APIサーバー停止
make db-up     # データベースのみ起動
make db-down   # データベース停止
make logs      # 全サービスのログを表示
make logs-api  # APIサーバーのログを表示
make logs-db   # データベースのログを表示
make clean     # 未使用のDockerリソースをクリーンアップ
```

## 🔧 開発

### 街のシミュレーション開発

街のシミュレーションはDockerで管理され、新しいデバイスを追加する際は以下の手順で行います：

1. **デバイスAPIの実装**: `city-devices/server.py`にエンドポイントを追加
2. **デバイスUIの実装**: `city-devices/index.html`に3D表示を追加
3. **MCPサーバーの実装**: `city-devices/mcp_servers/`に新しいMCPサーバーを追加

### MCPサーバー開発

各デバイスのMCPサーバーは独立して開発・テストできます：

- **軽量**: `requests`パッケージのみで動作
- **デバッグ容易**: 直接実行でデバッグ可能
- **拡張性**: 新しいデバイス用のMCPサーバーを簡単に追加

### データベース開発

街のデータベースはDuckDBを使用し、以下の特徴があります：

- **分析特化**: SQLクエリで複雑な分析が可能
- **メモリ内**: 高速な処理
- **MCP統合**: Claude Desktopから直接SQLクエリを実行可能

### トラブルシューティング

1. **街のシミュレーションが起動しない**
   ```bash
   make logs-api
   ```

2. **データベースが起動しない**
   ```bash
   make logs-db
   ```

3. **MCPサーバーが接続できない**
   ```bash
   # 街のAPIサーバーが起動しているか確認
   curl http://localhost:8000/api/vending-machine/products
   
   # データベースが起動しているか確認
   python3 city-database/mcp_servers/city_database_client_mcp_server.py --test-connection
   ```

6. **401/403 が返る**
   - Authorization ヘッダ（Bearer APIキー）が付与されているか
   - APIキーの権限（epalette / vending_machine の read/write）が適切か
   - APIキーの有効期限切れでないか

4. **ポートが使用中**
   ```bash
   lsof -i :8000  # APIサーバー
   lsof -i :5432  # データベース
   ```

5. **Claude DesktopでMCPサーバーが認識されない**
   - 環境変数`MCP_CITY_PATH`が設定されているか確認
   - 設定ファイルのパスが正しいか確認
   - MCPサーバーが起動しているか確認

## 📚 詳細ドキュメント

- `city-devices/README.md` - 街のデバイスの詳細