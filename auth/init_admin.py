"""
管理者ユーザーの初期化スクリプト
すべてのデバイスにアクセス可能な管理者ユーザーを作成
"""

from database import auth_db
import sys

def init_admin_user():
    """管理者ユーザーを初期化"""
    admin_username = "admin"
    admin_email = "admin@mcp-city.local"
    admin_password = "admin123"  # 本番環境では変更が必要
    
    try:
        # 管理者ユーザーを作成
        user_id = auth_db.create_user(admin_username, admin_email, admin_password)
        print(f"✅ 管理者ユーザーを作成しました: {admin_username}")
        
        # すべてのデバイスにフルアクセス権限を付与
        devices = [
            "vending_machine",
            "epalette", 
            "city_database"
        ]
        
        for device in devices:
            auth_db.set_device_permission(user_id, device, can_read=True, can_write=True)
            print(f"✅ {device} へのフルアクセス権限を付与しました")
        
        # 管理者用API Keyを生成
        api_key = auth_db.create_api_key(user_id, "Admin Default Key")
        print(f"✅ 管理者用API Keyを生成しました: {api_key}")
        
        print("\n" + "="*50)
        print("🔑 管理者認証情報")
        print("="*50)
        print(f"ユーザー名: {admin_username}")
        print(f"パスワード: {admin_password}")
        print(f"API Key: {api_key}")
        print("="*50)
        print("\n⚠️  本番環境では必ずパスワードとAPI Keyを変更してください")
        
        return True
        
    except Exception as e:
        print(f"❌ 管理者ユーザーの作成に失敗しました: {e}")
        return False

if __name__ == "__main__":
    success = init_admin_user()
    sys.exit(0 if success else 1)

