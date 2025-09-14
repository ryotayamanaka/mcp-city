import requests
from typing import Optional, Dict, List, Any
from agno.tools import Toolkit
from agno.utils.log import logger

class FoodCartScreenTools(Toolkit):
    def __init__(
        self,
        base_url: str = "http://food-cart-api:8000",
        update_text: bool = True,
        update_image: bool = True,
        clear_screen: bool = True,
        get_status: bool = True,
    ):
        super().__init__(name="food_cart_screen")
        self.base_url = base_url.rstrip("/")
        
        if update_text:
            self.register(self.update_screen_text)
        if update_image:
            self.register(self.update_screen_image)
        if clear_screen:
            self.register(self.clear_screen)
        if get_status:
            self.register(self.get_screen_status)

    def update_screen_text(self, text: str) -> str:
        """
        Update the promotional screen on the autonomous food cart with new text content.
        
        Args:
            text (str): The text message to display on the screen. Can include emojis and line breaks.
        
        Returns:
            str: Success message with confirmation of the update.
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/screen/update-text",
                json={"text": text},
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("success"):
                logger.info(f"Screen text updated successfully: {text[:50]}...")
                return f"✅ Screen updated successfully! Now displaying: '{text}'"
            else:
                return f"❌ Failed to update screen: {result.get('message', 'Unknown error')}"
                
        except requests.exceptions.ConnectionError:
            return "❌ Cannot connect to food cart. Make sure the IoT device server is running on food-cart-api:8000"
        except requests.exceptions.Timeout:
            return "❌ Request timed out. The food cart may be busy or offline."
        except Exception as e:
            logger.error(f"Error updating screen text: {e}")
            return f"❌ Error updating screen: {str(e)}"

    def update_screen_image(self, image_url: str) -> str:
        """
        Update the promotional screen on the autonomous food cart with an image.
        
        Args:
            image_url (str): The URL of the image to display on the screen. Must be a valid HTTP/HTTPS URL.
        
        Returns:
            str: Success message with confirmation of the update.
        """
        try:
            # Basic URL validation
            if not image_url.startswith(('http://', 'https://')):
                return "❌ Invalid image URL. Please provide a valid HTTP or HTTPS URL."
            
            response = requests.post(
                f"{self.base_url}/api/screen/update-image",
                json={"image_url": image_url},
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("success"):
                logger.info(f"Screen image updated successfully: {image_url}")
                return f"✅ Screen updated successfully! Now displaying image: {image_url}"
            else:
                return f"❌ Failed to update screen: {result.get('message', 'Unknown error')}"
                
        except requests.exceptions.ConnectionError:
            return "❌ Cannot connect to food cart. Make sure the IoT device server is running on food-cart-api:8000"
        except requests.exceptions.Timeout:
            return "❌ Request timed out. The food cart may be busy or offline."
        except Exception as e:
            logger.error(f"Error updating screen image: {e}")
            return f"❌ Error updating screen: {str(e)}"

    def clear_screen(self) -> str:
        """
        Clear the promotional screen on the autonomous food cart.
        
        Returns:
            str: Success message confirming the screen has been cleared.
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/screen/clear",
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("success"):
                logger.info("Screen cleared successfully")
                return "✅ Screen cleared successfully! The promotional display is now blank."
            else:
                return f"❌ Failed to clear screen: {result.get('message', 'Unknown error')}"
                
        except requests.exceptions.ConnectionError:
            return "❌ Cannot connect to food cart. Make sure the IoT device server is running on food-cart-api:8000"
        except requests.exceptions.Timeout:
            return "❌ Request timed out. The food cart may be busy or offline."
        except Exception as e:
            logger.error(f"Error clearing screen: {e}")
            return f"❌ Error clearing screen: {str(e)}"

    def get_screen_status(self) -> str:
        """
        Get the current status and content of the promotional screen on the autonomous food cart.
        
        Returns:
            str: Current screen status including what's currently displayed and last update time.
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/screen/status",
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            
            status_info = []
            status_info.append(f"📺 Screen Status: {result.get('status', 'unknown').upper()}")
            status_info.append(f"🕒 Last Update: {result.get('lastUpdate', 'Never')}")
            
            if result.get('text'):
                status_info.append(f"📝 Current Text: '{result['text']}'")
            elif result.get('imageUrl'):
                status_info.append(f"🖼️ Current Image: {result['imageUrl']}")
            else:
                status_info.append("📺 Screen is currently blank")
            
            return "\n".join(status_info)
                
        except requests.exceptions.ConnectionError:
            return "❌ Cannot connect to food cart. Make sure the IoT device server is running on food-cart-api:8000"
        except requests.exceptions.Timeout:
            return "❌ Request timed out. The food cart may be busy or offline."
        except Exception as e:
            logger.error(f"Error getting screen status: {e}")
            return f"❌ Error getting screen status: {str(e)}"


class VendingMachineTools(Toolkit):
    def __init__(
        self,
        base_url: str = "http://food-cart-api:8000",
        get_products: bool = True,
        get_inventory: bool = True,
        get_sales: bool = True,
        make_purchase: bool = True,
        get_analytics: bool = True,
    ):
        super().__init__(name="vending_machine")
        self.base_url = base_url.rstrip("/")
        
        if get_products:
            self.register(self.get_products)
        if get_inventory:
            self.register(self.get_inventory)
        if get_sales:
            self.register(self.get_sales_data)
        if make_purchase:
            self.register(self.make_purchase)
        if get_analytics:
            self.register(self.get_analytics)

    def get_products(self) -> str:
        """
        Get all products available in the vending machine with their prices and categories.
        
        Returns:
            str: List of available products with details.
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/vending-machine/products",
                timeout=10
            )
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
            logger.error(f"Error getting products: {e}")
            return f"❌ Error getting products: {str(e)}"

    def get_inventory(self) -> str:
        """
        Get current inventory status of the vending machine, including low stock alerts.
        
        Returns:
            str: Inventory status with stock levels and alerts.
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/vending-machine/inventory",
                timeout=10
            )
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
            logger.error(f"Error getting inventory: {e}")
            return f"❌ Error getting inventory: {str(e)}"

    def get_sales_data(self) -> str:
        """
        Get sales data and daily statistics from the vending machine.
        
        Returns:
            str: Sales data including recent transactions and daily stats.
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/vending-machine/sales",
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("success"):
                sales_info = ["💰 **Vending Machine Sales Data:**\n"]
                
                # Daily stats
                daily_stats = result.get("daily_stats", {})
                sales_info.append("📈 **Today's Performance:**")
                sales_info.append(f"  • Total Sales: {daily_stats.get('total_sales', 0)}")
                sales_info.append(f"  • Total Revenue: ¥{daily_stats.get('total_revenue', 0)}")
                if daily_stats.get('best_seller'):
                    sales_info.append(f"  • Best Seller: {daily_stats['best_seller']}")
                
                # Recent sales
                recent_sales = result.get("recent_sales", [])
                if recent_sales:
                    sales_info.append("\n🕐 **Recent Transactions:**")
                    for sale in recent_sales[-5:]:  # Show last 5
                        timestamp = sale['timestamp'].split('T')[1].split('.')[0]
                        sales_info.append(
                            f"  • {timestamp}: {sale['product_name']} "
                            f"(Qty: {sale['quantity']}, ¥{sale['total']})"
                        )
                
                return "\n".join(sales_info)
            else:
                return f"❌ Failed to get sales data: {result.get('message', 'Unknown error')}"
                
        except requests.exceptions.ConnectionError:
            return "❌ Cannot connect to vending machine. Make sure the server is running on food-cart-api:8000"
        except Exception as e:
            logger.error(f"Error getting sales data: {e}")
            return f"❌ Error getting sales data: {str(e)}"

    def make_purchase(self, product_id: str, quantity: int = 1) -> str:
        """
        Simulate a purchase from the vending machine.
        
        Args:
            product_id (str): The ID of the product to purchase (e.g., 'p001').
            quantity (int): Number of items to purchase (default: 1).
        
        Returns:
            str: Purchase confirmation or error message.
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/vending-machine/purchase",
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
            logger.error(f"Error making purchase: {e}")
            return f"❌ Error making purchase: {str(e)}"

    def get_analytics(self) -> str:
        """
        Get detailed analytics for the vending machine including sales trends and product performance.
        
        Returns:
            str: Comprehensive analytics report.
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/vending-machine/analytics",
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("success"):
                analytics = ["📊 **Vending Machine Analytics Report:**\n"]
                
                # Summary statistics
                summary = result.get("summary", {})
                analytics.append("📈 **Performance Summary:**")
                
                # Today
                today = summary.get("today", {})
                analytics.append(f"\n🔹 **Today:**")
                analytics.append(f"  • Sales: {today.get('sales', 0)}")
                analytics.append(f"  • Revenue: ¥{today.get('revenue', 0)}")
                
                # Week
                week = summary.get("week", {})
                analytics.append(f"\n🔹 **This Week:**")
                analytics.append(f"  • Sales: {week.get('sales', 0)}")
                analytics.append(f"  • Revenue: ¥{week.get('revenue', 0)}")
                analytics.append(f"  • Daily Average: ¥{week.get('daily_average', 0):.2f}")
                
                # Month
                month = summary.get("month", {})
                analytics.append(f"\n🔹 **This Month:**")
                analytics.append(f"  • Sales: {month.get('sales', 0)}")
                analytics.append(f"  • Revenue: ¥{month.get('revenue', 0)}")
                analytics.append(f"  • Daily Average: ¥{month.get('daily_average', 0):.2f}")
                
                # Top products
                top_products = result.get("top_products", [])
                if top_products:
                    analytics.append("\n🏆 **Top Selling Products:**")
                    for i, product in enumerate(top_products[:3], 1):
                        analytics.append(
                            f"  {i}. {product['product_name']}: "
                            f"{product['units_sold']} units, ¥{product['revenue']}"
                        )
                
                # Category performance
                categories = result.get("category_performance", {})
                if categories:
                    analytics.append("\n📂 **Category Performance:**")
                    for category, stats in categories.items():
                        analytics.append(
                            f"  • {category.capitalize()}: "
                            f"{stats['units_sold']} units, ¥{stats['revenue']}"
                        )
                
                # Inventory alerts
                alerts = result.get("inventory_alert", {})
                low_stock = alerts.get("low_stock", [])
                if low_stock:
                    analytics.append("\n⚠️ **Inventory Alerts:**")
                    for product in low_stock:
                        analytics.append(f"  • {product['name']}: Only {product['stock']} units left")
                
                return "\n".join(analytics)
            else:
                return f"❌ Failed to get analytics: {result.get('message', 'Unknown error')}"
                
        except requests.exceptions.ConnectionError:
            return "❌ Cannot connect to vending machine. Make sure the server is running on food-cart-api:8000"
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return f"❌ Error getting analytics: {str(e)}"
