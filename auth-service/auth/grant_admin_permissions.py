#!/usr/bin/env python3
"""
管理者ユーザーに全デバイスの権限を付与するスクリプト
"""

import sqlite3
from database import AuthDatabase

def grant_admin_permissions():
    """管理者ユーザーに全デバイスの権限を付与"""
    db = AuthDatabase()
    
    # 管理者ユーザーを検索
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.execute("SELECT id, username FROM users WHERE username = 'admin'")
        admin_user = cursor.fetchone()
    
    if not admin_user:
        print("❌ 管理者ユーザーが見つかりません")
        return False
    
    admin_id, admin_username = admin_user
    print(f"✅ 管理者ユーザー発見: {admin_username} (ID: {admin_id})")
    
    # 全デバイスに権限を付与
    devices = ["epalette", "vending_machine", "city_database"]
    
    for device in devices:
        try:
            db.set_device_permission(admin_id, device, can_read=True, can_write=True)
            print(f"✅ {device}: 読み取り・書き込み権限付与")
        except Exception as e:
            print(f"❌ {device}: エラー - {e}")
    
    # 権限確認
    permissions = db.get_device_permissions(admin_id)
    print(f"\n=== 管理者権限一覧 ===")
    for perm in permissions:
        print(f"- {perm['device_type']}: read={perm['can_read']}, write={perm['can_write']}")
    
    return True

if __name__ == "__main__":
    success = grant_admin_permissions()
    exit(0 if success else 1)
