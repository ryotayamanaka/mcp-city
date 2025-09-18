#!/usr/bin/env python3
"""
City Database Client MCP Server
Connects to DuckDB server with MCP extension
"""

import json
import sys
import duckdb
import argparse
import os
from pathlib import Path

class CityDatabaseClientMCP:
    def __init__(self, db_path="/Users/ryotayamanaka/git/mcp-city/city-database/database/city.db"):
        """Initialize the city database client MCP server"""
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
        # API key placeholder (for future HTTP API integration)
        self.api_key = os.getenv("MCP_CITY_API_KEY") or os.getenv("CITY_DEVICES_API_KEY")
    
    def execute_sql(self, query):
        """Execute SQL query directly on DuckDB file"""
        try:
            result = self.conn.execute(query).fetchall()
            columns = [desc[0] for desc in self.conn.description]
            
            # Convert to list of dictionaries
            data = []
            for row in result:
                data.append(dict(zip(columns, row)))
            
            return {
                "success": True,
                "data": data,
                "row_count": len(data),
                "columns": columns
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Query execution error: {str(e)}",
                "data": [],
                "row_count": 0,
                "columns": []
            }
    
    def get_table_info(self):
        """Get information about all tables"""
        try:
            # Get table list
            tables_query = "SHOW TABLES"
            tables_result = self.execute_sql(tables_query)
            
            if not tables_result["success"]:
                return tables_result
            
            table_info = {}
            for table_row in tables_result["data"]:
                table_name = table_row[0]  # First column is table name
                
                # Get column information
                columns_query = f"DESCRIBE {table_name}"
                columns_result = self.execute_sql(columns_query)
                
                if columns_result["success"]:
                    columns = [{"name": row[0], "type": row[1]} for row in columns_result["data"]]
                else:
                    columns = []
                
                # Get row count
                count_query = f"SELECT COUNT(*) FROM {table_name}"
                count_result = self.execute_sql(count_query)
                
                if count_result["success"] and count_result["data"]:
                    row_count = count_result["data"][0][0]
                else:
                    row_count = 0
                
                table_info[table_name] = {
                    "columns": columns,
                    "row_count": row_count
                }
            
            return {
                "success": True,
                "tables": table_info
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tables": {}
            }
    
    def test_connection(self):
        """Test connection to DuckDB database"""
        try:
            result = self.execute_sql("SELECT 'Connection successful' as status")
            return result["success"]
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
                "name": "execute_sql",
                "description": "Execute SQL query on city database via DuckDB MCP server",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "SQL query to execute"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_table_info",
                "description": "Get information about all tables in the database",
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
            if tool_name == "execute_sql":
                query = arguments.get("query")
                result = db.execute_sql(query)
                
                if result["success"]:
                    response_text = f"✅ Query executed successfully\n"
                    response_text += f"📊 Rows returned: {result['row_count']}\n"
                    response_text += f"📋 Columns: {', '.join(result['columns'])}\n\n"
                    
                    if result["data"]:
                        # Format data as table
                        response_text += "📄 Results:\n"
                        for i, row in enumerate(result["data"][:20]):  # Limit to 20 rows
                            response_text += f"{i+1}. {row}\n"
                        
                        if len(result["data"]) > 20:
                            response_text += f"... and {len(result['data']) - 20} more rows\n"
                    else:
                        response_text += "No data returned\n"
                else:
                    response_text = f"❌ SQL Error: {result['error']}"
                
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
                result = db.get_table_info()
                
                if result["success"]:
                    response_text = "📊 **City Database Tables:**\n\n"
                    for table_name, info in result["tables"].items():
                        response_text += f"**{table_name}** ({info['row_count']} rows)\n"
                        for col in info["columns"]:
                            response_text += f"  - {col['name']}: {col['type']}\n"
                        response_text += "\n"
                else:
                    response_text = f"❌ Error: {result['error']}"
                
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
                
                query = f"SELECT * FROM {table} LIMIT {limit}"
                result = db.execute_sql(query)
                
                if result["success"]:
                    response_text = f"📄 **Sample data from {table}:**\n\n"
                    for i, row in enumerate(result["data"]):
                        response_text += f"{i+1}. {row}\n"
                else:
                    response_text = f"❌ Error: {result['error']}"
                
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
