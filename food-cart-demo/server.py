from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
from datetime import datetime, timedelta
import json
import os
import requests
import random

app = FastAPI(title="e-Palette IoT API", description="API to control autonomous e-Palette promotional screen and vehicle")

# Add CORS middleware for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class ScreenTextUpdate(BaseModel):
    text: str
    subtext: Optional[str] = None

class ScreenImageUpdate(BaseModel):
    image_url: str

class VehicleControl(BaseModel):
    speed: Optional[int] = None  # 0-200
    paused: Optional[bool] = None
    location: Optional[str] = None  # central, east, tech, south, west, north

class VehicleStatus(BaseModel):
    location: str
    speed: int
    paused: bool
    view: str

class ScreenStatus(BaseModel):
    text: Optional[str] = None
    subtext: Optional[str] = None
    imageUrl: Optional[str] = None
    lastUpdate: str
    status: str = "ready"
    speed: Optional[int] = None
    paused: Optional[bool] = None
    location: Optional[str] = None

# Vending Machine Models
class PurchaseRequest(BaseModel):
    product_id: str
    quantity: int = 1

class SalesAnalytics(BaseModel):
    period: str = "today"  # today, week, month
    
class VendingProduct(BaseModel):
    id: str
    name: str
    price: int
    stock: int
    category: str
    image: str

# In-memory storage for demo (in production, use a database)
screen_data = {
    "text": "🍕 Mobile Food Service 🌮",
    "subtext": "AI-Powered · Auto Delivery",
    "imageUrl": None,
    "lastUpdate": datetime.now().isoformat(),
    "status": "ready",
    "speed": 25,  # デフォルトスピードを25%に変更
    "paused": False,
    "location": "central"
}

vehicle_data = {
    "location": "Central Plaza",
    "speed": 25,  # デフォルトスピードを25%に変更
    "paused": False,
    "view": "follow"
}

# Vending machine data file path
VENDING_DATA_FILE = "./mockdata/vending_data.json"

def load_vending_data():
    """Load vending machine data from file"""
    try:
        with open(VENDING_DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Initialize with default data if file doesn't exist
        default_data = {
            "products": [],
            "sales": [],
            "daily_stats": {
                "total_sales": 0,
                "total_revenue": 0,
                "best_seller": None,
                "last_update": None
            }
        }
        save_vending_data(default_data)
        return default_data

def save_vending_data(data):
    """Save vending machine data to file"""
    with open(VENDING_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def generate_random_sales():
    """Generate random sales data for simulation"""
    data = load_vending_data()
    products = data["products"]
    
    if not products:
        return
    
    # Generate random sales for the past 7 days
    sales = []
    for days_ago in range(7, -1, -1):
        sale_date = datetime.now() - timedelta(days=days_ago)
        num_sales = random.randint(5, 20)
        
        for _ in range(num_sales):
            product = random.choice(products)
            sale = {
                "timestamp": (sale_date + timedelta(hours=random.randint(6, 22))).isoformat(),
                "product_id": product["id"],
                "product_name": product["name"],
                "quantity": random.randint(1, 3),
                "price": product["price"],
                "total": product["price"] * random.randint(1, 3)
            }
            sales.append(sale)
    
    data["sales"] = sales
    
    # Update daily stats
    today_sales = [s for s in sales if datetime.fromisoformat(s["timestamp"]).date() == datetime.now().date()]
    data["daily_stats"]["total_sales"] = len(today_sales)
    data["daily_stats"]["total_revenue"] = sum(s["total"] for s in today_sales)
    
    # Find best seller
    if today_sales:
        product_counts = {}
        for sale in today_sales:
            pid = sale["product_id"]
            product_counts[pid] = product_counts.get(pid, 0) + sale["quantity"]
        best_seller_id = max(product_counts, key=product_counts.get)
        best_product = next((p for p in products if p["id"] == best_seller_id), None)
        if best_product:
            data["daily_stats"]["best_seller"] = best_product["name"]
    
    data["daily_stats"]["last_update"] = datetime.now().isoformat()
    
    save_vending_data(data)

# API Routes
@app.post("/api/screen/update-text")
async def update_screen_text(update: ScreenTextUpdate):
    """Update the promotional screen with new text content"""
    try:
        screen_data["text"] = update.text
        screen_data["subtext"] = update.subtext if update.subtext else ""
        screen_data["imageUrl"] = None  # Clear image when showing text
        screen_data["lastUpdate"] = datetime.now().isoformat()
        screen_data["status"] = "updated"
        
        return {
            "success": True,
            "message": "Screen text updated successfully",
            "data": screen_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update screen: {str(e)}")

@app.post("/api/screen/update-image")
async def update_screen_image(update: ScreenImageUpdate):
    """Update the promotional screen with new image content"""
    try:
        screen_data["imageUrl"] = update.image_url
        screen_data["text"] = None  # Clear text when showing image
        screen_data["lastUpdate"] = datetime.now().isoformat()
        screen_data["status"] = "updated"
        
        return {
            "success": True,
            "message": "Screen image updated successfully",
            "data": screen_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update screen: {str(e)}")

@app.get("/api/screen/status")
async def get_screen_status():
    """Get current screen status and content"""
    return screen_data

@app.get("/api/screen/clear")
async def clear_screen():
    """Clear the promotional screen"""
    try:
        screen_data["text"] = "Screen Cleared by AI Agent"
        screen_data["subtext"] = ""
        screen_data["imageUrl"] = None
        screen_data["lastUpdate"] = datetime.now().isoformat()
        screen_data["status"] = "cleared"
        
        return {
            "success": True,
            "message": "Screen cleared successfully",
            "data": screen_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear screen: {str(e)}")

# Vehicle control endpoints
@app.post("/api/vehicle/control")
async def control_vehicle(control: VehicleControl):
    """Control the e-Palette vehicle movement"""
    try:
        if control.speed is not None:
            screen_data["speed"] = max(0, min(200, control.speed))
            vehicle_data["speed"] = screen_data["speed"]
        
        if control.paused is not None:
            screen_data["paused"] = control.paused
            vehicle_data["paused"] = control.paused
        
        if control.location is not None:
            screen_data["location"] = control.location
            # Map location codes to display names
            location_map = {
                "central": "Central Plaza",
                "east": "East Commercial District",
                "tech": "Tech Park",
                "south": "South Residential",
                "west": "West Park",
                "north": "North School"
            }
            vehicle_data["location"] = location_map.get(control.location, "Unknown")
        
        screen_data["lastUpdate"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "message": "Vehicle control updated successfully",
            "data": {
                "speed": screen_data.get("speed"),
                "paused": screen_data.get("paused"),
                "location": screen_data.get("location")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to control vehicle: {str(e)}")

@app.get("/api/vehicle/status")
async def get_vehicle_status():
    """Get current vehicle status"""
    return vehicle_data

@app.post("/api/vehicle/status")
async def update_vehicle_status(status: VehicleStatus):
    """Update vehicle status from the 3D simulation"""
    try:
        vehicle_data["location"] = status.location
        vehicle_data["speed"] = status.speed
        vehicle_data["paused"] = status.paused
        vehicle_data["view"] = status.view
        
        return {
            "success": True,
            "message": "Vehicle status updated",
            "data": vehicle_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update vehicle status: {str(e)}")

# Image proxy endpoint to avoid CORS issues
@app.get("/api/proxy/image")
async def proxy_image(url: str):
    """Proxy external images to avoid CORS issues in the browser"""
    try:
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="Invalid URL. Must start with http:// or https://")
        
        # Fetch the image
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Get content type from response headers
        content_type = response.headers.get('content-type', 'image/jpeg')
        
        # Return the image content
        return Response(
            content=response.content,
            media_type=content_type,
            headers={
                "Cache-Control": "public, max-age=3600",
                "Access-Control-Allow-Origin": "*"
            }
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch image: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# Vending Machine API Endpoints
@app.get("/api/vending-machine/products")
async def get_vending_products():
    """Get all products available in the vending machine"""
    data = load_vending_data()
    return {
        "success": True,
        "products": data["products"],
        "total": len(data["products"])
    }

@app.get("/api/vending-machine/inventory")
async def get_vending_inventory():
    """Get current inventory status"""
    data = load_vending_data()
    products = data["products"]
    
    # Calculate inventory stats
    total_items = sum(p["stock"] for p in products)
    low_stock = [p for p in products if p["stock"] < 10]
    out_of_stock = [p for p in products if p["stock"] == 0]
    
    return {
        "success": True,
        "total_items": total_items,
        "total_products": len(products),
        "low_stock_products": low_stock,
        "out_of_stock_products": out_of_stock,
        "inventory": products
    }

@app.get("/api/vending-machine/sales")
async def get_vending_sales():
    """Get sales data and statistics"""
    data = load_vending_data()
    
    # Generate random sales if empty
    if not data["sales"]:
        generate_random_sales()
        data = load_vending_data()
    
    return {
        "success": True,
        "total_sales": len(data["sales"]),
        "recent_sales": data["sales"][-10:],  # Last 10 sales
        "daily_stats": data["daily_stats"]
    }

@app.post("/api/vending-machine/purchase")
async def make_purchase(purchase: PurchaseRequest):
    """Simulate a purchase from the vending machine"""
    data = load_vending_data()
    
    # Find product
    product = next((p for p in data["products"] if p["id"] == purchase.product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product["stock"] < purchase.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    # Update stock
    product["stock"] -= purchase.quantity
    
    # Record sale
    sale = {
        "timestamp": datetime.now().isoformat(),
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": purchase.quantity,
        "price": product["price"],
        "total": product["price"] * purchase.quantity
    }
    data["sales"].append(sale)
    
    # Update daily stats
    data["daily_stats"]["total_sales"] += 1
    data["daily_stats"]["total_revenue"] += sale["total"]
    data["daily_stats"]["last_update"] = datetime.now().isoformat()
    
    save_vending_data(data)
    
    return {
        "success": True,
        "message": f"Successfully purchased {purchase.quantity} x {product['name']}",
        "sale": sale,
        "remaining_stock": product["stock"]
    }

@app.get("/api/vending-machine/analytics")
async def get_vending_analytics():
    """Get detailed analytics for the vending machine"""
    data = load_vending_data()
    
    # Generate random sales if empty
    if not data["sales"]:
        generate_random_sales()
        data = load_vending_data()
    
    sales = data["sales"]
    products = data["products"]
    
    # Calculate analytics
    now = datetime.now()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Filter sales by period
    today_sales = [s for s in sales if datetime.fromisoformat(s["timestamp"]).date() == today]
    week_sales = [s for s in sales if datetime.fromisoformat(s["timestamp"]) >= week_ago]
    month_sales = [s for s in sales if datetime.fromisoformat(s["timestamp"]) >= month_ago]
    
    # Calculate revenue
    today_revenue = sum(s["total"] for s in today_sales)
    week_revenue = sum(s["total"] for s in week_sales)
    month_revenue = sum(s["total"] for s in month_sales)
    
    # Product performance
    product_stats = {}
    for sale in month_sales:
        pid = sale["product_id"]
        if pid not in product_stats:
            product_stats[pid] = {
                "product_id": pid,
                "product_name": sale["product_name"],
                "units_sold": 0,
                "revenue": 0
            }
        product_stats[pid]["units_sold"] += sale["quantity"]
        product_stats[pid]["revenue"] += sale["total"]
    
    # Sort by revenue
    top_products = sorted(product_stats.values(), key=lambda x: x["revenue"], reverse=True)[:5]
    
    # Category performance
    category_stats = {}
    for sale in month_sales:
        product = next((p for p in products if p["id"] == sale["product_id"]), None)
        if product:
            category = product["category"]
            if category not in category_stats:
                category_stats[category] = {"units_sold": 0, "revenue": 0}
            category_stats[category]["units_sold"] += sale["quantity"]
            category_stats[category]["revenue"] += sale["total"]
    
    # Hourly distribution (for today)
    hourly_sales = {}
    for sale in today_sales:
        hour = datetime.fromisoformat(sale["timestamp"]).hour
        if hour not in hourly_sales:
            hourly_sales[hour] = {"count": 0, "revenue": 0}
        hourly_sales[hour]["count"] += 1
        hourly_sales[hour]["revenue"] += sale["total"]
    
    return {
        "success": True,
        "summary": {
            "today": {
                "sales": len(today_sales),
                "revenue": today_revenue
            },
            "week": {
                "sales": len(week_sales),
                "revenue": week_revenue,
                "daily_average": week_revenue / 7
            },
            "month": {
                "sales": len(month_sales),
                "revenue": month_revenue,
                "daily_average": month_revenue / 30
            }
        },
        "top_products": top_products,
        "category_performance": category_stats,
        "hourly_distribution": hourly_sales,
        "inventory_alert": {
            "low_stock": [p for p in products if p["stock"] < 10],
            "out_of_stock": [p for p in products if p["stock"] == 0]
        }
    }

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Food Cart IoT API"
    }

# Serve the HTML files
@app.get("/")
async def serve_demo():
    """Serve the 3D e-Palette demo page"""
    return FileResponse("index-3d.html")

@app.get("/2d")
async def serve_2d_demo():
    """Serve the 2D e-Palette demo page"""
    return FileResponse("index.html")

# Mount static files (for any additional assets)
if os.path.exists("img"):
    app.mount("/img", StaticFiles(directory="img"), name="img")
if os.path.exists("food-cart-demo/static"):
    app.mount("/static", StaticFiles(directory="food-cart-demo/static"), name="static")

if __name__ == "__main__":
    print("🚀 Starting e-Palette IoT Demo Server...")
    print("🎮 3D Demo available at: http://localhost:8000")
    print("📱 2D Demo available at: http://localhost:8000/2d")
    print("📚 API docs available at: http://localhost:8000/docs")
    print("\n📡 API Endpoints:")
    print("  POST /api/screen/update-text - Update LED display text")
    print("  POST /api/screen/update-image - Update LED display image")
    print("  POST /api/vehicle/control - Control vehicle movement")
    print("  GET  /api/screen/status - Get display status")
    print("  GET  /api/vehicle/status - Get vehicle status")
    print("\n🏪 Vending Machine API:")
    print("  GET  /api/vending-machine/products - Get product list")
    print("  GET  /api/vending-machine/inventory - Get inventory status")
    print("  GET  /api/vending-machine/sales - Get sales data")
    print("  POST /api/vending-machine/purchase - Make a purchase")
    print("  GET  /api/vending-machine/analytics - Get analytics data")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
