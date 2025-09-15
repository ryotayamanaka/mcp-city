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
food-cart-demo/
├── index.html              # Food cart web interface
├── server.py               # FastAPI server with IoT API endpoints
├── mcp_servers/            # MCP servers for external access
│   └── vending_machine_mcp.py
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🚀 Quick Start

### 0. setup enviroment

```bash
cd food-cart-demo
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

### 4. Run the AI Agent

In a new terminal:

```bash
cd food-cart-demo
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
# export GOOGLE_API_KEY=xxxxxx
export AWS_ACCESS_KEY_ID=xxxxx
export AWS_SECRET_ACCESS_KEY=xxxxx
export AWS_REGION=us-west-2
python food_cart_agent.py
```

### 5. Run the Agent-UI

```bash
cd agent-ui
npm run dev
```

## 🎮 Using the Demo

### Agent Commands

Try these example commands with the AI agent:

```
🍕 You: Show a welcome message on the screen
🍕 You: Display today's special offers
🍕 You: Show an image of delicious pizza
🍕 You: Check the current screen status
🍕 You: Clear the screen
🍕 You: Create an attractive lunch promotion
```

### Available Tools

The agent has access to these tools:

1. **update_screen_text**: Display text messages on the promotional screen
2. **update_screen_image**: Display images from URLs on the screen
3. **clear_screen**: Clear the promotional screen
4. **get_screen_status**: Check current screen content and status

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

### Modify the Food Cart Interface

Edit `index.html` to customize:
- Cart appearance and styling
- Screen size and layout
- Status panel information
- Update polling frequency

### Extend Agent Capabilities

Edit `tools.py` to add new tools:
- Location control
- Menu management
- Customer interaction
- Sales analytics

### Agent Personality

Modify `food_cart_agent.py` instructions to change:
- Response style
- Promotional strategies
- Error handling
- Interaction patterns

## 🔍 Monitoring

### Web Interface
- Real-time screen updates
- Status panel with system information
- Visual feedback for agent actions

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation

### Agent Logs
The agent provides detailed logging for:
- Tool usage
- API calls
- Error handling
- Response generation

## 🛠️ Development

### Adding New Tools

1. Create a new method in `FoodCartScreenTools` class
2. Register the tool in the `__init__` method
3. Add corresponding API endpoint in `server.py`
4. Update the web interface if needed

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

3. **Agent not responding**
   - Ensure Agno is properly installed
   - Check API keys for the model provider
   - Verify tool registration

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export AGNO_LOG_LEVEL=DEBUG
```

## 📝 License

This demo is provided as-is for educational and demonstration purposes.

## 🤝 Contributing

Feel free to extend this demo with:
- Additional IoT device simulations
- More sophisticated agent behaviors
- Enhanced web interface features
- Integration with real IoT platforms

---

**Happy coding! 🚀**
