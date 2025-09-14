#!/usr/bin/env python3
"""
测试脚本：验证 e-Palette 屏幕图片更新功能
"""

import requests
import time
import json

# API 基础 URL
BASE_URL = "http://localhost:8000"

def test_image_update():
    """测试图片更新功能"""
    print("=" * 60)
    print("🧪 测试 e-Palette 屏幕图片更新功能")
    print("=" * 60)
    
    # 测试图片 URL 列表
    test_images = [
        # 使用一些公开的测试图片
        "https://via.placeholder.com/512x128/FF0000/FFFFFF?text=Red+Test+Image",
        "https://via.placeholder.com/512x128/00FF00/000000?text=Green+Test+Image",
        "https://via.placeholder.com/512x128/0000FF/FFFFFF?text=Blue+Test+Image",
        "https://picsum.photos/512/128",  # 随机图片
        "/img/ePalette001.jpg"  # 本地图片
    ]
    
    try:
        # 1. 首先检查 API 健康状态
        print("\n1️⃣ 检查 API 健康状态...")
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ API 服务正常运行")
        else:
            print("❌ API 服务未响应")
            return
        
        # 2. 获取当前屏幕状态
        print("\n2️⃣ 获取当前屏幕状态...")
        response = requests.get(f"{BASE_URL}/api/screen/status")
        if response.status_code == 200:
            data = response.json()
            print(f"当前状态: {data.get('status')}")
            if data.get('text'):
                print(f"当前文本: {data.get('text')}")
            if data.get('imageUrl'):
                print(f"当前图片: {data.get('imageUrl')}")
        
        # 3. 测试文本显示
        print("\n3️⃣ 测试文本显示...")
        text_data = {
            "text": "🎯 图片测试准备中...",
            "subtext": "即将显示测试图片"
        }
        response = requests.post(f"{BASE_URL}/api/screen/update-text", json=text_data)
        if response.status_code == 200:
            print("✅ 文本更新成功")
        else:
            print(f"❌ 文本更新失败: {response.status_code}")
        
        time.sleep(3)
        
        # 4. 测试图片更新
        print("\n4️⃣ 开始测试图片更新...")
        for i, image_url in enumerate(test_images, 1):
            print(f"\n测试图片 {i}/{len(test_images)}: {image_url}")
            
            image_data = {
                "image_url": image_url
            }
            
            try:
                response = requests.post(f"{BASE_URL}/api/screen/update-image", json=image_data)
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        print(f"✅ 图片更新成功")
                        
                        # 验证更新
                        status_response = requests.get(f"{BASE_URL}/api/screen/status")
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            if status_data.get("imageUrl") == image_url:
                                print(f"✅ 验证成功：图片 URL 已正确保存")
                            else:
                                print(f"⚠️ 警告：保存的 URL 不匹配")
                    else:
                        print(f"❌ 图片更新失败: {result.get('message')}")
                else:
                    print(f"❌ API 请求失败: {response.status_code}")
            except Exception as e:
                print(f"❌ 发生错误: {str(e)}")
            
            # 等待几秒再测试下一张图片
            if i < len(test_images):
                print(f"等待 5 秒后测试下一张图片...")
                time.sleep(5)
        
        # 5. 测试代理端点
        print("\n5️⃣ 测试图片代理端点...")
        proxy_test_url = "https://via.placeholder.com/150"
        try:
            response = requests.get(f"{BASE_URL}/api/proxy/image", params={"url": proxy_test_url})
            if response.status_code == 200:
                print(f"✅ 代理端点正常工作")
                print(f"   Content-Type: {response.headers.get('content-type')}")
                print(f"   Content-Length: {len(response.content)} bytes")
            else:
                print(f"❌ 代理端点失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 代理端点错误: {str(e)}")
        
        # 6. 恢复默认显示
        print("\n6️⃣ 恢复默认显示...")
        default_text = {
            "text": "🍕 Mobile Food Service 🌮",
            "subtext": "AI-Powered · Auto Delivery"
        }
        response = requests.post(f"{BASE_URL}/api/screen/update-text", json=default_text)
        if response.status_code == 200:
            print("✅ 已恢复默认显示")
        
        print("\n" + "=" * 60)
        print("✅ 测试完成！")
        print("请在浏览器中访问 http://localhost:8000 查看 3D 演示")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器")
        print("请确保服务器正在运行：")
        print("  cd food-cart-demo")
        print("  python server.py")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    test_image_update()
