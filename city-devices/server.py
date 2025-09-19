from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import sys
from pathlib import Path
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

# Serve static files (images, etc.)
app.mount("/static", StaticFiles(directory="img"), name="static")

# Data models
class ScreenTextUpdate(BaseModel):
    text: str
    subtext: Optional[str] = None
    font_size: Optional[int] = 24
    color: Optional[str] = "white"

class ScreenImageUpdate(BaseModel):
    image_url: str
    duration: Optional[int] = 30

class VehicleControl(BaseModel):
    action: str  # "start", "stop", "pause", "move_to"
    destination: Optional[str] = None
    speed: Optional[float] = None

class VehicleStatus(BaseModel):
    location: str
    speed: float
    direction: str
    status: str
    passengers: int
    next_stop: Optional[str] = None

class PurchaseRequest(BaseModel):
    product_id: str
    quantity: int = 1
    payment_method: str = "card"

# In-memory storage for 3D simulation state
screen_data = {
    "text": "🍕 Mobile Food Service 🌮",
    "subtext": "AI-Powered · Auto Delivery",
    "imageUrl": None,
    "lastUpdate": datetime.now().isoformat(),
    "status": "ready",
    "speed": 15,
    "paused": False,
    "location": "central"
}

vehicle_data = {
    "location": "Central Plaza",
    "speed": 15,
    "paused": False,
    "view": "follow"
}

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "service": "Food Cart IoT API"
    }

# === e-Palette Screen Control ===

@app.post("/api/epalette/screen/text")
async def epalette_update_screen_text(update: ScreenTextUpdate):
    """Update promotional screen text display"""
    try:
        screen_data["text"] = update.text
        if update.subtext is not None:
            screen_data["subtext"] = update.subtext
        screen_data["imageUrl"] = None  # Clear image when setting text
        screen_data["lastUpdate"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "message": f"Screen text updated to: '{update.text}'",
            "font_size": update.font_size,
            "color": update.color,
            "timestamp": screen_data["lastUpdate"],
            "data": {
                "text": screen_data["text"],
                "subtext": screen_data.get("subtext"),
                "lastUpdate": screen_data["lastUpdate"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update screen: {str(e)}")

@app.post("/api/epalette/screen/image")
async def epalette_update_screen_image(update: ScreenImageUpdate):
    """Update promotional screen image display"""
    try:
        screen_data["imageUrl"] = update.image_url
        screen_data["text"] = None  # Clear text when setting image
        screen_data["subtext"] = None  # Clear subtext when setting image
        screen_data["lastUpdate"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "message": f"Screen image updated to: {update.image_url}",
            "duration": update.duration,
            "timestamp": screen_data["lastUpdate"],
            "data": {
                "imageUrl": screen_data["imageUrl"],
                "lastUpdate": screen_data["lastUpdate"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update screen: {str(e)}")

@app.get("/api/epalette/screen/status")
async def epalette_get_display_status():
    """Get current display status"""
    return {
        "text": screen_data.get("text"),
        "subtext": screen_data.get("subtext"),
        "imageUrl": screen_data.get("imageUrl"),
        "lastUpdate": screen_data.get("lastUpdate"),
        "status": screen_data.get("status"),
        "screen_active": True,
        "brightness": 85
    }

@app.delete("/api/epalette/screen")
async def epalette_clear_display():
    """Clear the promotional screen"""
    try:
        screen_data["text"] = "🍕 Mobile Food Service 🌮"
        screen_data["subtext"] = "AI-Powered · Auto Delivery"
        screen_data["imageUrl"] = None
        screen_data["lastUpdate"] = datetime.now().isoformat()
        screen_data["status"] = "ready"
        
        return {
            "success": True,
            "message": "Screen cleared successfully",
            "timestamp": screen_data["lastUpdate"],
            "data": screen_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear screen: {str(e)}")

# === e-Palette Vehicle Control (Unified API) ===

@app.post("/api/epalette/control")
async def epalette_control_vehicle(control: VehicleControl):
    """Control e-Palette vehicle movement (unified API)"""
    try:
        # Update vehicle state based on action
        if control.action == "start":
            vehicle_data["paused"] = False
            screen_data["paused"] = False
        elif control.action == "stop":
            vehicle_data["speed"] = 0
            screen_data["speed"] = 0
            vehicle_data["paused"] = True
            screen_data["paused"] = True
        elif control.action == "pause":
            vehicle_data["paused"] = True
            screen_data["paused"] = True
        elif control.action == "move_to" and control.destination:
            # Map destination to location codes
            location_map = {
                "Central Plaza": "central",
                "East Commercial District": "east", 
                "Tech Park": "tech",
                "South Residential": "south",
                "West Park": "west",
                "North School": "north"
            }
            location_code = location_map.get(control.destination, "central")
            screen_data["location"] = location_code
            vehicle_data["location"] = control.destination
        
        if control.speed is not None:
            vehicle_data["speed"] = max(0, min(200, control.speed))
            screen_data["speed"] = vehicle_data["speed"]
        
        screen_data["lastUpdate"] = datetime.now().isoformat()
        
        action_responses = {
            "start": "Vehicle started and ready to move",
            "stop": "Vehicle stopped safely", 
            "pause": "Vehicle paused at current location",
            "move_to": f"Moving to destination: {control.destination}"
        }
        
        response = {
            "success": True,
            "action": control.action,
            "message": action_responses.get(control.action, "Unknown action"),
            "timestamp": screen_data["lastUpdate"],
            "data": {
                "speed": vehicle_data.get("speed"),
                "paused": vehicle_data.get("paused"),
                "location": vehicle_data.get("location")
            }
        }
        
        if control.destination:
            response["destination"] = control.destination
        if control.speed:
            response["speed"] = control.speed
            
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to control vehicle: {str(e)}")

@app.get("/api/epalette/status")
async def epalette_get_status():
    """Get comprehensive e-Palette status (unified API)"""
    return {
        "display": {
            "text": screen_data.get("text"),
            "subtext": screen_data.get("subtext"),
            "imageUrl": screen_data.get("imageUrl"),
            "lastUpdate": screen_data.get("lastUpdate"),
            "status": screen_data.get("status")
        },
        "vehicle": {
            "location": vehicle_data.get("location"),
            "speed": vehicle_data.get("speed"),
            "paused": vehicle_data.get("paused"),
            "view": vehicle_data.get("view")
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/epalette/status")
async def epalette_update_status(status: VehicleStatus):
    """Update e-Palette vehicle status from 3D simulation (unified API)"""
    try:
        vehicle_data["location"] = status.location
        vehicle_data["speed"] = status.speed
        # Convert new format to old format for compatibility
        vehicle_data["paused"] = (status.status == "paused")
        
        # Map to old vehicle data format for 3D simulation compatibility
        screen_data["location"] = status.location.lower().replace(" ", "_")
        screen_data["speed"] = status.speed
        screen_data["paused"] = vehicle_data["paused"]
        screen_data["lastUpdate"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "message": "Vehicle status updated from 3D simulation",
            "updated_status": {
                "location": status.location,
                "speed": status.speed,
                "direction": status.direction,
                "status": status.status,
                "passengers": status.passengers,
                "next_stop": status.next_stop
            },
            "timestamp": screen_data["lastUpdate"],
            "internal_data": vehicle_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")

# === Vending Machine API ===

@app.get("/api/vending/products")
async def get_vending_products():
    """Get available products in vending machine"""
    with open('mockdata/vending_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {"products": data["products"]}

@app.get("/api/vending/inventory") 
async def get_vending_inventory():
    """Get current inventory levels"""
    with open('mockdata/vending_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create inventory summary from products
    inventory = {}
    for product in data["products"]:
        inventory[product["id"]] = {
            "name": product["name"],
            "stock": product["stock"],
            "category": product["category"]
        }
    
    return {"inventory": inventory}

@app.get("/api/vending/sales")
async def get_vending_sales():
    """Get sales data and analytics"""
    # Mock sales data
    sales_data = {
        "daily_sales": {
            "total_revenue": 12450,
            "total_transactions": 67,
            "popular_items": [
                {"product_id": "p001", "name": "Coca Cola", "sales_count": 15},
                {"product_id": "p003", "name": "Green Tea", "sales_count": 12},
                {"product_id": "p007", "name": "Coffee", "sales_count": 10}
            ]
        },
        "hourly_trends": [
            {"hour": 9, "transactions": 8},
            {"hour": 12, "transactions": 15},
            {"hour": 15, "transactions": 12},
            {"hour": 18, "transactions": 20}
        ]
    }
    return sales_data

@app.post("/api/vending/purchase")
async def purchase_product(purchase: PurchaseRequest):
    """Process a product purchase"""
    # Load current inventory
    with open('mockdata/vending_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Find product
    product = None
    for p in data["products"]:
        if p["id"] == purchase.product_id:
            product = p
            break
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check and update inventory directly in products array
    current_stock = product["stock"]
    if current_stock < purchase.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    # Update inventory (simulate)
    new_stock = current_stock - purchase.quantity
    product["stock"] = new_stock
    
    # Save updated inventory
    with open('mockdata/vending_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    total_price = product["price"] * purchase.quantity
    
    return {
        "success": True,
        "transaction_id": f"TXN{random.randint(10000, 99999)}",
        "product": product,
        "quantity": purchase.quantity,
        "total_price": total_price,
        "payment_method": purchase.payment_method,
        "remaining_stock": new_stock,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/vending/analytics")
async def get_vending_analytics():
    """Get detailed analytics and insights"""
    return {
        "performance": {
            "uptime": "99.2%",
            "average_response_time": "1.2s",
            "error_rate": "0.3%"
        },
        "maintenance": {
            "last_service": "2024-01-15",
            "next_service": "2024-02-15", 
            "alerts": []
        },
        "revenue": {
            "weekly": 87450,
            "monthly": 340200,
            "year_to_date": 1250000
        }
    }

# === Web Interface ===

@app.get("/")
async def serve_3d_demo():
    """Serve the 3D city simulation page"""
    return FileResponse("index-3d.html")

@app.get("/2d")
async def serve_2d_demo():
    """Serve the 2D e-Palette demo page"""
    return FileResponse("index.html")

if __name__ == "__main__":
    print("🚀 Starting e-Palette IoT Demo Server...")
    print("🎮 3D City Simulation: http://localhost:8000")
    print("📱 2D Demo: http://localhost:8000/2d")
    print("📚 API docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
