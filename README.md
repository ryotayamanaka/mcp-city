# Bootcamp AI Main

AIエージェントとフロントエンドUIを含む統合アプリケーションです。

## 🚀 クイックスタート

### 前提条件

- Docker
- Docker Compose
- Make（オプション）

### Dockerを使用した起動

#### 1. 開発環境での起動

```bash
# 開発環境でサービスを起動
make dev

# または直接実行
docker-compose -f docker-compose.dev.yml up -d
```

#### 2. 本番環境での起動

```bash
# 全サービスのイメージをビルド
make build

# 本番環境でサービスを起動
make up

# または直接実行
docker-compose up -d
```

#### 3. サービスの停止

```bash
# 開発環境の停止
make dev-down

# 本番環境の停止
make down
```

## 📁 プロジェクト構成

```
/
├── agent-ui/              # Next.jsフロントエンド
├── agents/                # モジュール化されたPythonエージェント
├── food-cart-demo/        # FastAPIバックエンド
│   └── mcp_servers/       # MCPサーバー（自動販売機ツール）
├── docker-compose.yml     # 本番環境用
├── docker-compose.dev.yml # 開発環境用
└── Makefile              # 便利なコマンド集
```

## 🌐 サービス一覧

| サービス | ポート | 説明 |
|---------|--------|------|
| agent-ui | 3000 | Next.jsフロントエンド |
| python-agents | 8001 | Pythonエージェント（agno） |
| food-cart-api | 8000 | Food Cart API（FastAPI） |
| vending-machine-mcp | - | MCPサーバー（自動販売機ツール） |

## 🛠️ 利用可能なコマンド

```bash
make help      # 利用可能なコマンドを表示
make build     # 全サービスのイメージをビルド
make up        # 本番環境でサービスを起動
make dev       # 開発環境でサービスを起動
make logs      # 全サービスのログを表示
make clean     # 未使用のDockerリソースをクリーンアップ
```

## 🔧 開発

### 開発環境での特徴

- ホットリロード対応
- ソースコードの変更が即座に反映
- デバッグしやすい設定

### 本番環境での特徴

- 最適化されたビルド
- 軽量なランタイム
- セキュリティ強化

## 📝 環境変数

必要に応じて`.env`ファイルを作成し、以下の環境変数を設定してください：

```bash
GOOGLE_API_KEY=your_google_api_key_here
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🐛 トラブルシューティング

### よくある問題

1. **ポートが既に使用されている**
   ```bash
   # 使用中のポートを確認
   lsof -i :3000
   ```

2. **Dockerイメージのビルドエラー**
   ```bash
   # キャッシュをクリアして再ビルド
   make clean
   make build
   ```

3. **サービスのログ確認**
   ```bash
   # 特定のサービスのログを表示
   make logs-ui
   make logs-python
   make logs-api
   ```

## 📚 詳細ドキュメント

各サービスの詳細については、以下のディレクトリを参照してください：

- `agent-ui/README.md` - フロントエンドの詳細
- `food-cart-demo/README.md` - Food Cart APIの詳細
