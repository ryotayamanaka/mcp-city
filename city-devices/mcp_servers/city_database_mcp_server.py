#!/usr/bin/env python3
"""
City Database MCP Server
Provides SQL access to city data through MCP protocol
"""

import json
import sys
import duckdb
import argparse
from pathlib import Path

class CityDatabaseMCP:
    def __init__(self):
        """Initialize the city database MCP server"""
        self.conn = duckdb.connect(':memory:')
        self.load_data()
    
    def load_data(self):
        """Load CSV data into the database"""
        data_dir = Path(__file__).parent.parent / "data"
        
        # Load residents data
        self.conn.execute(f"""
            CREATE TABLE residents AS 
            SELECT * FROM '{data_dir}/residents.csv'
        """)
        
        # Load businesses data
        self.conn.execute(f"""
            CREATE TABLE businesses AS 
            SELECT * FROM '{data_dir}/businesses.csv'
        """)
        
        # Load traffic data
        self.conn.execute(f"""
            CREATE TABLE traffic AS 
            SELECT * FROM '{data_dir}/traffic.csv'
        """)
    
    def execute_sql(self, query):
        """Execute SQL query and return results"""
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
                "error": str(e),
                "data": [],
                "row_count": 0,
                "columns": []
            }
    
    def get_table_info(self):
        """Get information about all tables"""
        try:
            result = self.conn.execute("SHOW TABLES").fetchall()
            tables = [row[0] for row in result]
            
            table_info = {}
            for table in tables:
                # Get column information
                columns_result = self.conn.execute(f"DESCRIBE {table}").fetchall()
                columns = [{"name": row[0], "type": row[1]} for row in columns_result]
                
                # Get row count
                count_result = self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchall()
                row_count = count_result[0][0] if count_result else 0
                
                table_info[table] = {
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
                    "name": "CityDatabaseMCP",
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
                "description": "Execute SQL query on city database",
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
        
        # Initialize database connection
        db = CityDatabaseMCP()
        
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
    parser = argparse.ArgumentParser(description="City Database MCP Server")
    parser.add_argument("--check-data", action="store_true", help="Check if data files are available")
    args = parser.parse_args()
    
    if args.check_data:
        try:
            db = CityDatabaseMCP()
            result = db.get_table_info()
            if result["success"]:
                print("✅ City database data loaded successfully")
                for table_name, info in result["tables"].items():
                    print(f"  - {table_name}: {info['row_count']} rows")
                return 0
            else:
                print(f"❌ Error loading data: {result['error']}")
                return 1
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    
    print(f"Starting CityDatabaseMCP server...", file=sys.stderr)
    
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
