#!/usr/bin/env python3
"""
Quick demo script to test the Food Cart IoT system
"""

import time
import requests
from food_cart_agent import food_cart_agent

def test_api_connection():
    """Test if the IoT device server is running"""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ IoT device server is running")
            return True
        else:
            print("❌ IoT device server returned error:", response.status_code)
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to IoT device server")
        print("   Please start the server with: python server.py")
        return False
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def run_demo_sequence():
    """Run a sequence of demo commands"""
    print("\n🎬 Running automated demo sequence...")
    
    demo_commands = [
        "Check the current screen status",
        "Show a welcome message with emojis",
        "Display today's lunch special with attractive formatting",
        "Show the current screen status again",
        "Clear the screen"
    ]
    
    for i, command in enumerate(demo_commands, 1):
        print(f"\n📝 Demo Step {i}: {command}")
        print("🤖 Agent Response:")
        
        try:
            response = food_cart_agent.run(command, stream=True)
            print()  # Add newline after response
            time.sleep(2)  # Pause between commands
        except Exception as e:
            print(f"❌ Error: {e}")
            break
    
    print("\n🎉 Demo sequence completed!")

def main():
    print("🚀 Food Cart IoT Demo")
    print("=" * 50)
    
    # Test API connection first
    if not test_api_connection():
        print("\n💡 To start the demo:")
        print("1. Run: python server.py")
        print("2. Open: http://localhost:8000")
        print("3. Run this demo again")
        return
    
    print("\n🎯 Demo Options:")
    print("1. Run automated demo sequence")
    print("2. Interactive agent chat")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\nSelect option (1-3): ").strip()
            
            if choice == "1":
                run_demo_sequence()
                break
            elif choice == "2":
                print("\n🗣️ Starting interactive chat...")
                print("Type 'quit' to exit")
                
                while True:
                    user_input = input("\n🍕 You: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        break
                    
                    if not user_input:
                        continue
                    
                    print("\n🤖 Agent:", end=" ")
                    try:
                        food_cart_agent.run(user_input, stream=True)
                        print()
                    except Exception as e:
                        print(f"❌ Error: {e}")
                break
            elif choice == "3":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()
