#!/usr/bin/env python3
"""
Simple MCP Server for Vending Machine Tools
Provides vending machine functionality through MCP protocol
"""

import json
import sys
import requests

# Base URL for the food cart API
BASE_URL = "http://food-cart-api:8000"

def get_products():
    """Get all products available in the vending machine with their prices and categories"""
    try:
        response = requests.get(f"{BASE_URL}/api/vending-machine/products", timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get("success"):
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
        else:
            return f"❌ Failed to get products: {result.get('message', 'Unknown error')}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to vending machine. Make sure the server is running on food-cart-api:8000"
    except Exception as e:
        return f"❌ Error getting products: {str(e)}"

def get_inventory():
    """Get current inventory status of the vending machine, including low stock alerts"""
    try:
        response = requests.get(f"{BASE_URL}/api/vending-machine/inventory", timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get("success"):
            inventory_info = ["📊 **Vending Machine Inventory Status:**\n"]
            inventory_info.append(f"📦 Total Items in Stock: {result.get('total_items', 0)}")
            inventory_info.append(f"🏷️ Total Product Types: {result.get('total_products', 0)}\n")
            
            # Low stock alerts
            low_stock = result.get("low_stock_products", [])
            if low_stock:
                inventory_info.append("⚠️ **Low Stock Alert:**")
                for product in low_stock:
                    inventory_info.append(f"  • {product['name']}: {product['stock']} units remaining")
            
            # Out of stock
            out_of_stock = result.get("out_of_stock_products", [])
            if out_of_stock:
                inventory_info.append("\n🚫 **Out of Stock:**")
                for product in out_of_stock:
                    inventory_info.append(f"  • {product['name']}")
            
            return "\n".join(inventory_info)
        else:
            return f"❌ Failed to get inventory: {result.get('message', 'Unknown error')}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to vending machine. Make sure the server is running on food-cart-api:8000"
    except Exception as e:
        return f"❌ Error getting inventory: {str(e)}"

def make_purchase(product_id, quantity=1):
    """Simulate a purchase from the vending machine"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/vending-machine/purchase",
            json={"product_id": product_id, "quantity": quantity},
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
        return "❌ Cannot connect to vending machine. Make sure the server is running on food-cart-api:8000"
    except Exception as e:
        return f"❌ Error making purchase: {str(e)}"

def get_sales_data():
    """Get sales data and analytics from the vending machine"""
    try:
        response = requests.get(f"{BASE_URL}/api/vending-machine/sales", timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get("success"):
            sales_info = ["📈 **Vending Machine Sales Data:**\n"]
            
            # Total sales
            total_sales = result.get("total_sales", 0)
            sales_info.append(f"🛒 Total Sales: {total_sales} transactions")
            
            # Daily stats
            daily_stats = result.get("daily_stats", {})
            if daily_stats:
                sales_info.append(f"📅 Daily Sales: {daily_stats.get('total_sales', 0)} transactions")
                sales_info.append(f"💰 Daily Revenue: ¥{daily_stats.get('total_revenue', 0)}")
                sales_info.append(f"🏆 Best Seller: {daily_stats.get('best_seller', 'N/A')}")
                sales_info.append(f"🕐 Last Update: {daily_stats.get('last_update', 'N/A')}")
            
            # Recent sales
            recent_sales = result.get("recent_sales", [])
            if recent_sales:
                sales_info.append(f"\n🕒 **Recent Sales (Last 5):**")
                for sale in recent_sales[:5]:
                    sales_info.append(
                        f"• {sale.get('product_name', 'Unknown')} x{sale.get('quantity', 0)} "
                        f"¥{sale.get('total', 0)} ({sale.get('timestamp', 'Unknown time')})"
                    )
            
            return "\n".join(sales_info)
        else:
            return f"❌ Failed to get sales data: {result.get('message', 'Unknown error')}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to vending machine. Make sure the server is running on food-cart-api:8000"
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
    print(f"Starting VendingMachineMCP server...", file=sys.stderr)
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        try:
            message = json.loads(line)
            response = handle_message(message)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()