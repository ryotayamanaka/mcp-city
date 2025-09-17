#!/usr/bin/env python3
"""
ePalette MCP Server
Provides ePalette vehicle control and display management through MCP protocol
"""

import json
import sys
import requests
import argparse
import os
from datetime import datetime

# Base URL for the food cart API
BASE_URL = "http://localhost:8000"

def check_required_env_vars():
    """Check for required environment variables and display helpful error messages"""
    missing_vars = []
    
    # Check MCP_CITY_PATH
    if not os.getenv('MCP_CITY_PATH'):
        missing_vars.append('MCP_CITY_PATH')
    
    # Check GOOGLE_API_KEY (optional but recommended)
    if not os.getenv('GOOGLE_API_KEY'):
        missing_vars.append('GOOGLE_API_KEY (optional)')
    
    if missing_vars:
        print("❌ **Environment Variables Missing**", file=sys.stderr)
        print("", file=sys.stderr)
        print("The following environment variables are not set:", file=sys.stderr)
        for var in missing_vars:
            print(f"  - {var}", file=sys.stderr)
        print("", file=sys.stderr)
        print("**Required:**", file=sys.stderr)
        print("  export MCP_CITY_PATH=/path/to/mcp-city", file=sys.stderr)
        print("", file=sys.stderr)
        print("**Optional:**", file=sys.stderr)
        print("  export GOOGLE_API_KEY=your_google_api_key", file=sys.stderr)
        print("", file=sys.stderr)
        print("After setting the variables, restart Claude Desktop.", file=sys.stderr)
        return False
    
    return True

def get_epalette_status():
    """Get comprehensive ePalette status including display and vehicle information"""
    try:
        response = requests.get(f"{BASE_URL}/api/epalette/status", timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        status_info = ["🚐 **ePalette Status:**\n"]
        
        # Display information
        display = result.get("display", {})
        status_info.append("📺 **Display:**")
        status_info.append(f"  • Text: {display.get('text', 'N/A')}")
        status_info.append(f"  • Subtext: {display.get('subtext', 'N/A')}")
        status_info.append(f"  • Status: {display.get('status', 'N/A')}")
        status_info.append(f"  • Last Update: {display.get('lastUpdate', 'N/A')}")
        
        # Vehicle information
        vehicle = result.get("vehicle", {})
        status_info.append(f"\n🚗 **Vehicle:**")
        status_info.append(f"  • Location: {vehicle.get('location', 'N/A')}")
        status_info.append(f"  • Speed: {vehicle.get('speed', 0)} km/h")
        status_info.append(f"  • Paused: {'Yes' if vehicle.get('paused', False) else 'No'}")
        status_info.append(f"  • View: {vehicle.get('view', 'N/A')}")
        
        return "\n".join(status_info)
        
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to ePalette. Make sure the server is running on localhost:8000"
    except Exception as e:
        return f"❌ Error getting ePalette status: {str(e)}"

def update_display_text(text, subtext=""):
    """Update ePalette LED display text"""
    try:
        payload = {
            "text": text,
            "subtext": subtext
        }
        
        response = requests.post(
            f"{BASE_URL}/api/epalette/display/text",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        if result.get("success"):
            return (
                f"✅ **Display Text Updated Successfully!**\n"
                f"📺 Main Text: {result['data']['text']}\n"
                f"📝 Sub Text: {result['data']['subtext']}\n"
                f"🕐 Updated: {result['data']['lastUpdate']}"
            )
        else:
            return f"❌ Failed to update display text: {result.get('message', 'Unknown error')}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to ePalette. Make sure the server is running on localhost:8000"
    except Exception as e:
        return f"❌ Error updating display text: {str(e)}"

def update_display_image(image_url):
    """Update ePalette LED display image"""
    try:
        payload = {
            "imageUrl": image_url
        }
        
        response = requests.post(
            f"{BASE_URL}/api/epalette/display/image",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        if result.get("success"):
            return (
                f"✅ **Display Image Updated Successfully!**\n"
                f"🖼️ Image URL: {result['data']['imageUrl']}\n"
                f"🕐 Updated: {result['data']['lastUpdate']}"
            )
        else:
            return f"❌ Failed to update display image: {result.get('message', 'Unknown error')}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to ePalette. Make sure the server is running on localhost:8000"
    except Exception as e:
        return f"❌ Error updating display image: {str(e)}"

def clear_display():
    """Clear ePalette LED display"""
    try:
        response = requests.post(f"{BASE_URL}/api/epalette/display/clear", timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get("success"):
            return (
                f"✅ **Display Cleared Successfully!**\n"
                f"📺 Display is now blank\n"
                f"🕐 Cleared: {result['data']['lastUpdate']}"
            )
        else:
            return f"❌ Failed to clear display: {result.get('message', 'Unknown error')}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to ePalette. Make sure the server is running on localhost:8000"
    except Exception as e:
        return f"❌ Error clearing display: {str(e)}"

def control_vehicle(speed=None, paused=None, location=None):
    """Control ePalette vehicle movement and status"""
    try:
        payload = {}
        if speed is not None:
            payload["speed"] = speed
        if paused is not None:
            payload["paused"] = paused
        if location is not None:
            payload["location"] = location
        
        response = requests.post(
            f"{BASE_URL}/api/epalette/control",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        if result.get("success"):
            control_info = ["✅ **Vehicle Control Updated Successfully!**\n"]
            data = result.get("data", {})
            
            if "speed" in data:
                control_info.append(f"🚗 Speed: {data['speed']} km/h")
            if "paused" in data:
                control_info.append(f"⏸️ Paused: {'Yes' if data['paused'] else 'No'}")
            if "location" in data:
                control_info.append(f"📍 Location: {data['location']}")
            
            return "\n".join(control_info)
        else:
            return f"❌ Failed to control vehicle: {result.get('message', 'Unknown error')}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to ePalette. Make sure the server is running on localhost:8000"
    except Exception as e:
        return f"❌ Error controlling vehicle: {str(e)}"

def get_display_status():
    """Get current ePalette display status"""
    try:
        response = requests.get(f"{BASE_URL}/api/epalette/display/status", timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        display_info = ["📺 **ePalette Display Status:**\n"]
        display_info.append(f"📝 Text: {result.get('text', 'N/A')}")
        display_info.append(f"📄 Subtext: {result.get('subtext', 'N/A')}")
        display_info.append(f"🖼️ Image URL: {result.get('imageUrl', 'N/A')}")
        display_info.append(f"📊 Status: {result.get('status', 'N/A')}")
        display_info.append(f"🕐 Last Update: {result.get('lastUpdate', 'N/A')}")
        
        return "\n".join(display_info)
        
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to ePalette. Make sure the server is running on localhost:8000"
    except Exception as e:
        return f"❌ Error getting display status: {str(e)}"

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
                    "name": "ePaletteMCP",
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
                "name": "get_epalette_status",
                "description": "Get comprehensive ePalette status including display and vehicle information",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                }
            },
            {
                "name": "update_display_text",
                "description": "Update ePalette LED display text",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Main text to display on the LED screen",
                        },
                        "subtext": {
                            "type": "string",
                            "description": "Sub text to display below the main text",
                            "default": "",
                        },
                    },
                    "required": ["text"],
                }
            },
            {
                "name": "update_display_image",
                "description": "Update ePalette LED display image",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "image_url": {
                            "type": "string",
                            "description": "URL of the image to display on the LED screen",
                        },
                    },
                    "required": ["image_url"],
                }
            },
            {
                "name": "clear_display",
                "description": "Clear ePalette LED display",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                }
            },
            {
                "name": "control_vehicle",
                "description": "Control ePalette vehicle movement and status",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "speed": {
                            "type": "integer",
                            "description": "Vehicle speed in km/h (0-200)",
                            "minimum": 0,
                            "maximum": 200,
                        },
                        "paused": {
                            "type": "boolean",
                            "description": "Whether to pause the vehicle",
                        },
                        "location": {
                            "type": "string",
                            "description": "Vehicle location (central, east, tech, south, west, north)",
                            "enum": ["central", "east", "tech", "south", "west", "north"],
                        },
                    },
                }
            },
            {
                "name": "get_display_status",
                "description": "Get current ePalette display status",
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
            if tool_name == "get_epalette_status":
                result = get_epalette_status()
            elif tool_name == "update_display_text":
                text = arguments.get("text")
                subtext = arguments.get("subtext", "")
                result = update_display_text(text, subtext)
            elif tool_name == "update_display_image":
                image_url = arguments.get("image_url")
                result = update_display_image(image_url)
            elif tool_name == "clear_display":
                result = clear_display()
            elif tool_name == "control_vehicle":
                speed = arguments.get("speed")
                paused = arguments.get("paused")
                location = arguments.get("location")
                result = control_vehicle(speed, paused, location)
            elif tool_name == "get_display_status":
                result = get_display_status()
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
    # Check environment variables first
    if not check_required_env_vars():
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description="ePalette MCP Server")
    parser.add_argument("--check-api", action="store_true", help="Check if API is available")
    args = parser.parse_args()
    
    if args.check_api:
        try:
            response = requests.get(f"{BASE_URL}/api/epalette/status", timeout=5)
            if response.status_code == 200:
                print("✅ ePalette API is available")
                return 0
            else:
                print(f"❌ ePalette API returned status {response.status_code}")
                return 1
        except Exception as e:
            print(f"❌ ePalette API is not available: {e}")
            return 1
    
    print(f"Starting ePalette MCP server...", file=sys.stderr)
    
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
