#!/usr/bin/env python3
"""
Standalone MCP Server for Vending Machine Tools
Can be used with Claude Desktop or other MCP clients
"""

import json
import sys
import requests
import argparse
import os
import subprocess
import time

# Base URL for the food cart API
BASE_URL = "http://localhost:9001"
API_KEY = os.getenv("MCP_CITY_API_KEY") or os.getenv("CITY_DEVICES_API_KEY")

def auth_headers():
    return {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}

def get_products():
    """Get all products available in the vending machine with their prices and categories"""
    try:
        response = requests.get(f"{BASE_URL}/api/vending/products", headers=auth_headers(), timeout=10)
        response.raise_for_status()
        
        result = response.json()
        products = result.get("products", [])
        if not products:
            return "📦 No products available in the vending machine."
        
        product_list = ["🏪 **Vending Machine Products:**\n"]
        for product in products:
            product_list.append(
                f"• **{product['name']}** {product['image']}\n"
                f"  - Price: ¥{product['price']}\n"
                f"  - Stock: {product['stock']} units\n"
                f"  - Category: {product['category']}\n"
                f"  - ID: {product['id']}\n"
            )
        
        return "\n".join(product_list)
            
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to vending machine. Make sure the server is running on localhost:8000"
    except Exception as e:
        return f"❌ Error getting products: {str(e)}"

def get_inventory():
    """Get current inventory status of the vending machine, including low stock alerts"""
    try:
        response = requests.get(f"{BASE_URL}/api/vending/inventory", headers=auth_headers(), timeout=10)
        response.raise_for_status()
        
        result = response.json()
        inventory = result.get("inventory", {})
        if not inventory:
            return "📦 No inventory data available."
        
        inventory_info = ["📊 **Vending Machine Inventory Status:**\n"]
        
        total_items = sum(item['stock'] for item in inventory.values())
        total_products = len(inventory)
        
        inventory_info.append(f"📦 Total Items in Stock: {total_items}")
        inventory_info.append(f"🏷️ Total Product Types: {total_products}\n")
        
        # Categorize products by stock status
        low_stock = []
        out_of_stock = []
        
        for product_id, item in inventory.items():
            if item['stock'] == 0:
                out_of_stock.append(item)
            elif item['stock'] <= 2:  # Low stock threshold
                low_stock.append(item)
        
        # Low stock alerts
        if low_stock:
            inventory_info.append("⚠️ **Low Stock Alert:**")
            for item in low_stock:
                inventory_info.append(f"  • {item['name']}: {item['stock']} units remaining")
        
        # Out of stock
        if out_of_stock:
            inventory_info.append("\n🚫 **Out of Stock:**")
            for item in out_of_stock:
                inventory_info.append(f"  • {item['name']}")
        
        # Detailed inventory
        inventory_info.append("\n📋 **Detailed Inventory:**")
        for product_id, item in inventory.items():
            status = "✅" if item['stock'] > 2 else "⚠️" if item['stock'] > 0 else "🚫"
            inventory_info.append(f"  {status} **{item['name']}** ({item['category']}): {item['stock']} units")
        
        return "\n".join(inventory_info)
            
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to vending machine. Make sure the server is running on localhost:8000"
    except Exception as e:
        return f"❌ Error getting inventory: {str(e)}"

def make_purchase(product_id, quantity=1):
    """Simulate a purchase from the vending machine"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/vending/purchase",
            json={"product_id": product_id, "quantity": quantity},
            headers=auth_headers(),
            timeout=10
        )
        
        if response.status_code == 404:
            return f"❌ Product with ID '{product_id}' not found. Use get_products to see available items."
        elif response.status_code == 400:
            result = response.json()
            return f"❌ Purchase failed: {result.get('detail', 'Insufficient stock')}"
        
        response.raise_for_status()
        
        result = response.json()
        if result.get("success"):
            sale = result.get("sale", {})
            return (
                f"✅ **Purchase Successful!**\n"
                f"🛒 Product: {sale.get('product_name', 'Unknown')}\n"
                f"📦 Quantity: {sale.get('quantity', 0)}\n"
                f"💰 Total: ¥{sale.get('total', 0)}\n"
                f"📊 Remaining Stock: {result.get('remaining_stock', 'Unknown')}"
            )
        else:
            return f"❌ Purchase failed: {result.get('message', 'Unknown error')}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to vending machine. Make sure the server is running on localhost:8000"
    except Exception as e:
        return f"❌ Error making purchase: {str(e)}"

def get_sales_data():
    """Get sales data and analytics from the vending machine"""
    try:
        response = requests.get(f"{BASE_URL}/api/vending/sales", headers=auth_headers(), timeout=10)
        response.raise_for_status()
        
        result = response.json()
        sales_info = ["📈 **Vending Machine Sales Data:**\n"]
        
        # Daily sales data
        daily_sales = result.get("daily_sales", {})
        if daily_sales:
            sales_info.append(f"📅 **Today's Sales:**")
            sales_info.append(f"  💰 Revenue: ¥{daily_sales.get('total_revenue', 0):,}")
            sales_info.append(f"  🛒 Transactions: {daily_sales.get('total_transactions', 0)}")
            
            # Popular items from daily sales
            popular_items = daily_sales.get("popular_items", [])
            if popular_items:
                sales_info.append(f"\n🔥 **Popular Items Today:**")
                for item in popular_items[:5]:  # Top 5
                    sales_info.append(f"  • {item.get('name', 'Unknown')}: {item.get('sales_count', 0)} sold")
        
        # Weekly sales data if available
        weekly_sales = result.get("weekly_sales", {})
        if weekly_sales:
            sales_info.append(f"\n📊 **This Week:**")
            sales_info.append(f"  💰 Revenue: ¥{weekly_sales.get('total_revenue', 0):,}")
            sales_info.append(f"  🛒 Transactions: {weekly_sales.get('total_transactions', 0)}")
        
        # Monthly sales data if available
        monthly_sales = result.get("monthly_sales", {})
        if monthly_sales:
            sales_info.append(f"\n📈 **This Month:**")
            sales_info.append(f"  💰 Revenue: ¥{monthly_sales.get('total_revenue', 0):,}")
            sales_info.append(f"  🛒 Transactions: {monthly_sales.get('total_transactions', 0)}")
        
        return "\n".join(sales_info)
            
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to vending machine. Make sure the server is running on localhost:8000"
    except Exception as e:
        return f"❌ Error getting sales data: {str(e)}"

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
                    "name": "VendingMachineMCP",
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
                "name": "get_products",
                "description": "Get all products available in the vending machine with their prices and categories",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                }
            },
            {
                "name": "get_inventory",
                "description": "Get current inventory status of the vending machine, including low stock alerts",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                }
            },
            {
                "name": "make_purchase",
                "description": "Simulate a purchase from the vending machine",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "product_id": {
                            "type": "string",
                            "description": "The ID of the product to purchase (e.g., 'p001')",
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "Number of items to purchase",
                            "default": 1,
                        },
                    },
                    "required": ["product_id"],
                }
            },
            {
                "name": "get_sales_data",
                "description": "Get sales data and analytics from the vending machine including daily stats and recent sales",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
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
        
        try:
            if tool_name == "get_products":
                result = get_products()
            elif tool_name == "get_inventory":
                result = get_inventory()
            elif tool_name == "make_purchase":
                product_id = arguments.get("product_id")
                quantity = arguments.get("quantity", 1)
                result = make_purchase(product_id, quantity)
            elif tool_name == "get_sales_data":
                result = get_sales_data()
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
    parser = argparse.ArgumentParser(description="Vending Machine MCP Server")
    parser.add_argument("--check-api", action="store_true", help="Check if API is available")
    args = parser.parse_args()
    
    if args.check_api:
        try:
            response = requests.get(f"{BASE_URL}/api/vending/products", headers=auth_headers(), timeout=5)
            if response.status_code == 200:
                print("✅ API is available")
                return 0
            else:
                print(f"❌ API returned status {response.status_code}")
                return 1
        except Exception as e:
            print(f"❌ API is not available: {e}")
            return 1
    
    print(f"Starting VendingMachineMCP server...", file=sys.stderr)
    
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
