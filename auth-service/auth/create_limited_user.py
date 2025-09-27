#!/usr/bin/env python3
"""
制限付きユーザー作成スクリプト
ePaletteと街のデータベースにはアクセス可能、自動販売機にはアクセス不可
"""

import sys
import os
from database import AuthDatabase
import secrets
import string

def generate_password(length=12):
    """安全なランダムパスワードを生成"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_limited_user():
    """制限付きユーザーを作成"""
    # データベース接続
    db = AuthDatabase()
    
    # ユーザー情報設定
    username = "city_observer"
    email = "observer@mcp-city.local"
    password = generate_password()
    
    print("=== 制限付きユーザー作成 ===")
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print()
    
    try:
        # ユーザー作成
        user_id = db.create_user(username, email, password)
        print(f"✅ ユーザー作成成功: {user_id}")
        
        # APIキー生成
        api_key = db.create_api_key(user_id, "City Observer API Key")
        print(f"✅ APIキー生成: {api_key}")
        print()
        
        # デバイス権限設定
        print("=== デバイス権限設定 ===")
        
        # ePalette: 読み取り・書き込み両方許可
        db.set_device_permission(user_id, "epalette", can_read=True, can_write=True)
        print("✅ ePalette: 読み取り・書き込み許可")
        
        # 街データベース: 読み取りのみ許可
        db.set_device_permission(user_id, "city_database", can_read=True, can_write=False)
        print("✅ 街データベース: 読み取りのみ許可")
        
        # 自動販売機: アクセス拒否（権限設定なし）
        print("✅ 自動販売機: アクセス拒否（権限未設定）")
        
        print()
        print("=== 作成完了 ===")
        print("このユーザーは以下にアクセス可能:")
        print("- ePalette (読み取り・制御)")
        print("- 街のデータベース (読み取りのみ)")
        print()
        print("アクセス不可:")
        print("- 自動販売機 (全機能)")
        print()
        print(f"APIキー: {api_key}")
        print("このAPIキーをClaude Desktop設定で使用してください。")
        
        return {
            "user_id": user_id,
            "username": username,
            "email": email,
            "password": password,
            "api_key": api_key
        }
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return None

if __name__ == "__main__":
    result = create_limited_user()
    if result:
        sys.exit(0)
    else:
        sys.exit(1)
