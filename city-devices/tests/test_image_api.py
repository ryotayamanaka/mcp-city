#!/usr/bin/env python3
"""
Test script: Verify ePalette display image update functionality
"""

import requests
import time
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_image_update():
    """Test image update functionality"""
    print("=" * 60)
    print("🧪 Testing ePalette Display Image Update Functionality")
    print("=" * 60)
    
    # Test image URL list
    test_images = [
        # Using some public test images
        "https://via.placeholder.com/512x128/FF0000/FFFFFF?text=Red+Test+Image",
        "https://via.placeholder.com/512x128/00FF00/000000?text=Green+Test+Image",
        "https://via.placeholder.com/512x128/0000FF/FFFFFF?text=Blue+Test+Image",
        "https://picsum.photos/512/128",  # Random image
        "/img/ePalette001.jpg"  # Local image
    ]
    
    try:
        # 1. First check API health status
        print("\n1️⃣ Checking API health status...")
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ API service is running normally")
        else:
            print("❌ API service is not responding")
            return
        
        # 2. Get current display status
        print("\n2️⃣ Getting current display status...")
        response = requests.get(f"{BASE_URL}/api/epalette/display/status")
        if response.status_code == 200:
            data = response.json()
            print(f"Current status: {data.get('status')}")
            if data.get('text'):
                print(f"Current text: {data.get('text')}")
            if data.get('imageUrl'):
                print(f"Current image: {data.get('imageUrl')}")
        
        # 3. Test text display
        print("\n3️⃣ Testing text display...")
        text_data = {
            "text": "🎯 Preparing image test...",
            "subtext": "About to display test images"
        }
        response = requests.post(f"{BASE_URL}/api/epalette/display/text", json=text_data)
        if response.status_code == 200:
            print("✅ Text update successful")
        else:
            print(f"❌ Text update failed: {response.status_code}")
        
        time.sleep(3)
        
        # 4. Test image updates
        print("\n4️⃣ Starting image update tests...")
        for i, image_url in enumerate(test_images, 1):
            print(f"\nTest image {i}/{len(test_images)}: {image_url}")
            
            image_data = {
                "image_url": image_url
            }
            
            try:
                response = requests.post(f"{BASE_URL}/api/epalette/display/image", json=image_data)
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        print(f"✅ Image update successful")
                        
                        # Verify update
                        status_response = requests.get(f"{BASE_URL}/api/epalette/display/status")
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            if status_data.get("imageUrl") == image_url:
                                print(f"✅ Verification successful: Image URL saved correctly")
                            else:
                                print(f"⚠️ Warning: Saved URL does not match")
                    else:
                        print(f"❌ Image update failed: {result.get('message')}")
                else:
                    print(f"❌ API request failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Error occurred: {str(e)}")
            
            # Wait a few seconds before testing next image
            if i < len(test_images):
                print(f"Waiting 5 seconds before testing next image...")
                time.sleep(5)
        
        # 5. Test image proxy endpoint
        print("\n5️⃣ Testing image proxy endpoint...")
        proxy_test_url = "https://via.placeholder.com/150"
        try:
            response = requests.get(f"{BASE_URL}/api/proxy/image", params={"url": proxy_test_url})
            if response.status_code == 200:
                print(f"✅ Proxy endpoint working normally")
                print(f"   Content-Type: {response.headers.get('content-type')}")
                print(f"   Content-Length: {len(response.content)} bytes")
            else:
                print(f"❌ Proxy endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Proxy endpoint error: {str(e)}")
        
        # 6. Restore default display
        print("\n6️⃣ Restoring default display...")
        default_text = {
            "text": "🍕 Mobile Food Service 🌮",
            "subtext": "AI-Powered · Auto Delivery"
        }
        response = requests.post(f"{BASE_URL}/api/epalette/display/text", json=default_text)
        if response.status_code == 200:
            print("✅ Default display restored")
        
        print("\n" + "=" * 60)
        print("✅ Test completed!")
        print("Please visit http://localhost:8000 in your browser to view the 3D demo")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server")
        print("Please ensure the server is running:")
        print("  cd city-devices")
        print("  python server.py")
    except Exception as e:
        print(f"\n❌ Error occurred during testing: {str(e)}")

if __name__ == "__main__":
    test_image_update()
