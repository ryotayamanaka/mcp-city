"""
Test script for the Vending Machine Agent Tools
This script tests all the vending machine functions through the agent tools.
"""

import asyncio
from tools import VendingMachineTools

async def test_vending_machine_tools():
    """Test all vending machine tool functions"""
    
    print("=" * 60)
    print("🧪 Testing Vending Machine Agent Tools")
    print("=" * 60)
    
    # Initialize the tools
    vending_tools = VendingMachineTools()
    
    # Test 1: Get Products
    print("\n📦 Test 1: Getting Products List")
    print("-" * 40)
    products = vending_tools.get_products()
    print(products)
    
    # Test 2: Get Inventory
    print("\n📊 Test 2: Getting Inventory Status")
    print("-" * 40)
    inventory = vending_tools.get_inventory()
    print(inventory)
    
    # Test 3: Get Sales Data
    print("\n💰 Test 3: Getting Sales Data")
    print("-" * 40)
    sales = vending_tools.get_sales_data()
    print(sales)
    
    # Test 4: Get Analytics
    print("\n📈 Test 4: Getting Analytics Report")
    print("-" * 40)
    analytics = vending_tools.get_analytics()
    print(analytics)
    
    # Test 5: Make a Purchase
    print("\n🛒 Test 5: Making a Test Purchase")
    print("-" * 40)
    # Try to purchase a Coca Cola (p001)
    purchase = vending_tools.make_purchase("p001", 1)
    print(purchase)
    
    # Test 6: Check inventory after purchase
    print("\n📊 Test 6: Checking Inventory After Purchase")
    print("-" * 40)
    inventory_after = vending_tools.get_inventory()
    print(inventory_after)
    
    # Test 7: Invalid purchase (non-existent product)
    print("\n❌ Test 7: Testing Invalid Purchase")
    print("-" * 40)
    invalid_purchase = vending_tools.make_purchase("p999", 1)
    print(invalid_purchase)
    
    # Test 8: Purchase with insufficient stock
    print("\n⚠️ Test 8: Testing Purchase with Large Quantity")
    print("-" * 40)
    large_purchase = vending_tools.make_purchase("p001", 100)
    print(large_purchase)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    print("🚀 Starting Vending Machine Tools Test")
    print("⚠️  Make sure the server is running on http://localhost:8000")
    print()
    
    try:
        asyncio.run(test_vending_machine_tools())
    except KeyboardInterrupt:
        print("\n\n⛔ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
