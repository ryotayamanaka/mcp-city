# 🤖 Autonomous Food Cart IoT Demo

This demo showcases how AI agents can control IoT devices through simple API calls. The demo simulates an autonomous food cart with a promotional screen that can be controlled via MCP (Model Context Protocol) servers accessible from Claude Desktop.

## 🎯 Demo Overview

- **IoT Device Simulation**: A web-based autonomous food cart with a promotional screen
- **AI Agent Control**: MCP servers accessible from Claude Desktop to control the screen
- **API Integration**: RESTful API endpoints for device control
- **Real-time Updates**: Live screen updates visible in the web interface

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Claude Desktop  │───▶│   FastAPI       │───▶│   Food Cart     │
│ (MCP Client)    │    │   (IoT API)     │    │   (Web UI)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
city-devices/
├── index.html              # City devices 2D web interface
├── index-3d.html           # City devices 3D demo interface
├── server.py               # FastAPI server with API endpoints
├── mcp_servers/            # MCP servers for external access
│   ├── vending_machine_mcp_server.py
│   └── epalette_mcp_server.py
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## 🚀 Quick Start

### 0. setup enviroment

```bash
cd city-devices
uv venv --python 3.12
source .venv/bin/activate
```

### 1. Install Dependencies

```bash
uv pip install -r requirements.txt
```

### 2. Start the IoT Device Server

```bash
python server.py
```

The server will start on `http://localhost:8000`

### 3. Open the Food Cart Interface

Open your browser and navigate to: `http://localhost:8000`

You should see the autonomous food cart with its promotional screen.

### 4. MCPサーバーの起動

MCPサーバーを起動してClaude Desktopからアクセス可能にします：

```bash
# 自動販売機のMCPサーバー
python3 city-devices/mcp_servers/vending_machine_mcp_server.py

# ePaletteのMCPサーバー（別ターミナル）
python3 city-devices/mcp_servers/epalette_mcp_server.py
```

## 🎮 Using the Demo

### MCPサーバー経由での操作

Claude DesktopからMCPサーバー経由でデバイスを操作できます：

**自動販売機**:
- 商品一覧の取得
- 在庫状況の確認
- 購入のシミュレーション
- 売上データの分析

**ePalette**:
- ディスプレイテキストの更新
- 画像の表示
- 車両の制御
- 状態の確認

## 🔧 API Endpoints

The IoT device exposes these REST API endpoints:

### Update Screen Text
```http
POST /api/screen/update-text
Content-Type: application/json

{
  "text": "🎉 Special Offer!\nBuy 2 Get 1 Free Pizza\nValid Today Only!"
}
```

### Update Screen Image
```http
POST /api/screen/update-image
Content-Type: application/json

{
  "image_url": "https://example.com/pizza.jpg"
}
```

### Get Screen Status
```http
GET /api/screen/status
```

### Clear Screen
```http
GET /api/screen/clear
```

### Health Check
```http
GET /api/health
```

## 🎨 Customization

### Modify the City Devices Interface

Edit `index.html` または `index-3d.html` でカスタマイズ:
- デバイスの外観とスタイリング
- 画面サイズとレイアウト
- ステータスパネルの情報
- 更新ポーリング頻度

### MCPサーバーの拡張

新しいMCPサーバーを追加:
- 新しいデバイス用のMCPサーバー
- 追加のAPIエンドポイント
- カスタムツールの実装

## 🔍 Monitoring

### Web Interface
- Real-time screen updates
- Status panel with system information
- Visual feedback for agent actions

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation

### MCPサーバーログ
MCPサーバーは詳細なログを提供:
- ツールの使用状況
- API呼び出し
- エラーハンドリング
- レスポンス生成

## 🛠️ Development

### Adding New MCP Tools

1. 新しいMCPサーバーを作成
2. 必要なツールメソッドを実装
3. 対応するAPIエンドポイントを`server.py`に追加
4. 必要に応じてWebインターフェースを更新

### Testing API Endpoints

Use curl or any HTTP client:

```bash
# Update screen text
curl -X POST http://localhost:8000/api/screen/update-text \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from API!"}'

# Check status
curl http://localhost:8000/api/screen/status
```

## 🚨 Troubleshooting

### Common Issues

1. **Agent can't connect to food cart**
   - Make sure the server is running on port 8000
   - Check if the port is available
   - Verify the base_url in tools.py

2. **Screen not updating**
   - Check browser console for errors
   - Verify API endpoints are responding
   - Check network connectivity

3. **MCPサーバーが応答しない**
   - MCPサーバーが起動しているか確認
   - ポート8000が利用可能か確認
   - Claude Desktopの設定を確認

### Debug Mode

MCPサーバーのデバッグログを有効にする:
```bash
export PYTHONPATH=/path/to/mcp-city
python3 -u city-devices/mcp_servers/vending_machine_mcp_server.py
```

## 📝 License

This demo is provided as-is for educational and demonstration purposes.

## 🤝 Contributing

Feel free to extend this demo with:
- Additional IoT device simulations
- More sophisticated MCP servers
- Enhanced web interface features
- Integration with real IoT platforms

---

**Happy coding! 🚀**
