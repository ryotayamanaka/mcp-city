#!/usr/bin/env python3
"""
City Database Client MCP Server (HTTP)
MCPクライアント（Claude Desktop等）から、APIキー付きで city-database HTTP API
（/db/health, /db/tables, /db/select, /db/sample）を呼び出します。
"""

import json
import sys
import requests
import argparse
import os

BASE_URL = os.getenv("CITY_DATABASE_API_URL", "http://localhost:9002")
API_KEY = os.getenv("MCP_CITY_API_KEY") or os.getenv("CITY_DEVICES_API_KEY")


def auth_headers():
    return {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}


class CityDatabaseClientMCP:
    def list_tables(self):
        try:
            r = requests.get(f"{BASE_URL}/db/tables", headers=auth_headers(), timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            return {"success": False, "error": f"tables error: {e}", "tables": {}}

    def select_rows(self, payload: dict):
        try:
            r = requests.post(f"{BASE_URL}/db/select", json=payload, headers=auth_headers(), timeout=20)
            
            if r.status_code in (401, 403):
                try:
                    return {"success": False, "error": r.json().get("detail", "Unauthorized")}
                except Exception:
                    return {"success": False, "error": "Unauthorized"}
            r.raise_for_status()
            return r.json()
        except Exception as e:
            return {"success": False, "error": f"select error: {e}", "data": []}

    def get_sample_data(self, table: str, limit: int = 10):
        try:
            r = requests.get(
                f"{BASE_URL}/db/sample",
                params={"table": table, "limit": limit},
                headers=auth_headers(),
                timeout=10,
            )
            r.raise_for_status()
            return r.json()
        except Exception as e:
            return {"success": False, "error": f"sample error: {e}", "data": []}

    def test_connection(self) -> bool:
        try:
            r = requests.get(f"{BASE_URL}/db/health", timeout=5)
            return r.status_code == 200
        except Exception:
            return False

def handle_message(message):
    """Handle incoming MCP messages"""
    method = message.get("method")
    params = message.get("params", {})
    request_id = message.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "CityDatabaseClientMCP",
                    "version": "1.0.0"
                }
            }
        }

    elif method == "notifications/initialized":
        # No response needed for notifications
        return None

    elif method == "tools/list":
        tools_list = [
            {
                "name": "list_tables",
                "description": "List allowed tables and columns in the city database",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "select_rows",
                "description": "Safely select rows using whitelisted table/columns and filters",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "table": {"type": "string"},
                        "columns": {"type": "array", "items": {"type": "string"}},
                        "filters": {"type": "object"},
                        "order_by": {"type": "array", "items": {"type": "object"}},
                        "limit": {"type": "integer"},
                        "offset": {"type": "integer"}
                    },
                    "required": ["table"]
                }
            },
            {
                "name": "get_table_info",
                "description": "Alias for list_tables (kept for compatibility)",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_sample_data",
                "description": "Get sample data from a specific table",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "table": {
                            "type": "string",
                            "description": "Table name to get sample data from"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of rows to return (default: 10)",
                            "default": 10
                        }
                    },
                    "required": ["table"]
                }
            },
            {
                "name": "test_connection",
                "description": "Test connection to DuckDB database",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools_list
            }
        }

    elif method == "prompts/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "prompts": []
            }
        }

    elif method == "resources/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "resources": []
            }
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        # Initialize database client
        db = CityDatabaseClientMCP()
        
        try:
            if tool_name == "list_tables":
                result = db.list_tables()
                if result.get("success"):
                    response_text = "📊 **City Database Tables:**\n\n"
                    for table_name, info in result.get("tables", {}).items():
                        response_text += f"**{table_name}** ({info.get('row_count', 0)} rows)\n"
                        for col in info.get("columns", []):
                            response_text += f"  - {col['name']}: {col.get('type','N/A')}\n"
                        response_text += "\n"
                else:
                    response_text = f"❌ Error: {result.get('error','unknown')}"
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": response_text
                            }
                        ]
                    }
                }
            
            elif tool_name == "get_table_info":
                # Backward compatible alias
                result = db.list_tables()
                if result.get("success"):
                    response_text = "📊 **City Database Tables:**\n\n"
                    for table_name, info in result.get("tables", {}).items():
                        response_text += f"**{table_name}** ({info.get('row_count', 0)} rows)\n"
                        for col in info.get("columns", []):
                            response_text += f"  - {col['name']}: {col.get('type','N/A')}\n"
                        response_text += "\n"
                else:
                    response_text = f"❌ Error: {result.get('error','unknown')}"
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": response_text
                            }
                        ]
                    }
                }
            
            elif tool_name == "get_sample_data":
                table = arguments.get("table")
                limit = arguments.get("limit", 10)
                result = db.get_sample_data(table, limit)
                if result.get("success"):
                    rows = result.get("data", [])
                    response_text = f"📄 **Sample data from {table}:**\n\n"
                    for i, row in enumerate(rows):
                        response_text += f"{i+1}. {row}\n"
                else:
                    response_text = f"❌ Error: {result.get('error','unknown')}"
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": response_text
                            }
                        ]
                    }
                }

            elif tool_name == "select_rows":
                # None値を除外してペイロードを構築
                payload = {"table": arguments.get("table")}
                if arguments.get("columns") is not None:
                    payload["columns"] = arguments.get("columns")
                if arguments.get("filters") is not None:
                    # フィルター形式を自動変換（シンプル形式 → API形式）
                    filters = arguments.get("filters")
                    converted_filters = {}
                    for key, value in filters.items():
                        if isinstance(value, dict) and "op" in value:
                            # 既にAPI形式の場合はそのまま
                            converted_filters[key] = value
                        else:
                            # シンプル形式をAPI形式に変換
                            converted_filters[key] = {"op": "EQ", "value": value}
                    payload["filters"] = converted_filters
                if arguments.get("order_by") is not None:
                    payload["order_by"] = arguments.get("order_by")
                if arguments.get("limit") is not None:
                    payload["limit"] = arguments.get("limit")
                if arguments.get("offset") is not None:
                    payload["offset"] = arguments.get("offset")
                result = db.select_rows(payload)
                if result.get("success"):
                    rows = result.get("data", [])
                    cols = result.get("columns", [])
                    response_text = f"✅ Rows: {len(rows)}\nColumns: {', '.join(cols)}\n\n"
                    for i, row in enumerate(rows[:20]):
                        response_text += f"{i+1}. {row}\n"
                    if len(rows) > 20:
                        response_text += f"... and {len(rows)-20} more rows\n"
                else:
                    response_text = f"❌ Error: {result.get('error','unknown')}"
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": response_text
                            }
                        ]
                    }
                }
            
            elif tool_name == "test_connection":
                success = db.test_connection()
                if success:
                    response_text = "✅ Connection to DuckDB database successful"
                else:
                    response_text = "❌ Connection to DuckDB database failed"
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": response_text
                            }
                        ]
                    }
                }
            
            else:
                result = f"❌ Unknown tool: {tool_name}"
        except Exception as e:
            result = f"❌ Error: {str(e)}"
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
        }

    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }

def main():
    """Main function to run the MCP server"""
    parser = argparse.ArgumentParser(description="City Database Client MCP Server")
    parser.add_argument("--test-connection", action="store_true", help="Test connection to DuckDB server")
    parser.add_argument("--db-path", default="/Users/ryotayamanaka/git/mcp-city/city-database/database/city.db", help="DuckDB database file path")
    args = parser.parse_args()
    
    if args.test_connection:
        try:
            db = CityDatabaseClientMCP(args.db_path)
            if db.test_connection():
                print("✅ Connection to DuckDB database successful")
                return 0
            else:
                print("❌ Connection to DuckDB database failed")
                return 1
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    
    # Note: APIキーは将来のHTTP統合用に環境変数から読み込み済み
    print(f"Starting CityDatabaseClientMCP server...", file=sys.stderr)
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        try:
            message = json.loads(line)
            response = handle_message(message)
            if response is not None:  # Only print response if it's not None
                print(json.dumps(response), flush=True)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
