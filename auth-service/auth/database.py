"""
認証データベース管理モジュール
SQLiteを使用したユーザー認証とAPI Key管理
"""

import sqlite3
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

# データベースファイルのパス
DB_PATH = Path(__file__).parent / "auth.db"

class AuthDatabase:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DB_PATH)
        self.init_database()
    
    def init_database(self):
        """データベースとテーブルを初期化"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    key_hash TEXT NOT NULL,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS device_permissions (
                    user_id TEXT NOT NULL,
                    device_type TEXT NOT NULL,
                    can_read BOOLEAN DEFAULT FALSE,
                    can_write BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, device_type),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.commit()
    
    def create_user(self, username: str, email: str, password: str) -> str:
        """新しいユーザーを作成"""
        user_id = str(uuid.uuid4())
        password_hash = self._hash_password(password)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO users (id, username, email, password_hash)
                VALUES (?, ?, ?, ?)
            """, (user_id, username, email, password_hash))
            conn.commit()
        
        return user_id
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """ユーザー認証"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT id, username, email, password_hash, is_active
                FROM users 
                WHERE username = ? AND is_active = TRUE
            """, (username,))
            
            user = cursor.fetchone()
            if user and self._verify_password(password, user['password_hash']):
                return dict(user)
        
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """ユーザーIDでユーザー情報を取得"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT id, username, email, created_at, is_active
                FROM users 
                WHERE id = ? AND is_active = TRUE
            """, (user_id,))
            
            user = cursor.fetchone()
            return dict(user) if user else None
    
    def create_api_key(self, user_id: str, name: str, expires_days: int = 365) -> str:
        """API Keyを作成"""
        api_key = self._generate_api_key()
        key_hash = self._hash_password(api_key)
        key_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(days=expires_days)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO api_keys (id, user_id, key_hash, name, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """, (key_id, user_id, key_hash, name, expires_at.isoformat()))
            conn.commit()
        
        return api_key
    
    def authenticate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """API Key認証"""
        key_hash = self._hash_password(api_key)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT u.id, u.username, u.email, u.is_active, u.created_at, ak.name as key_name
                FROM users u
                JOIN api_keys ak ON u.id = ak.user_id
                WHERE ak.key_hash = ? 
                AND ak.is_active = TRUE 
                AND u.is_active = TRUE
                AND (ak.expires_at IS NULL OR ak.expires_at > ?)
            """, (key_hash, datetime.now().isoformat()))
            
            user = cursor.fetchone()
            return dict(user) if user else None
    
    def set_device_permission(self, user_id: str, device_type: str, can_read: bool, can_write: bool):
        """デバイス権限を設定"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO device_permissions 
                (user_id, device_type, can_read, can_write)
                VALUES (?, ?, ?, ?)
            """, (user_id, device_type, can_read, can_write))
            conn.commit()
    
    def get_device_permissions(self, user_id: str) -> List[Dict[str, Any]]:
        """ユーザーのデバイス権限を取得"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT device_type, can_read, can_write
                FROM device_permissions
                WHERE user_id = ?
            """, (user_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def check_permission(self, user_id: str, device_type: str, action: str) -> bool:
        """権限チェック"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT can_read, can_write
                FROM device_permissions
                WHERE user_id = ? AND device_type = ?
            """, (user_id, device_type))
            
            row = cursor.fetchone()
            if not row:
                return False
            
            if action == "read":
                return bool(row[0])
            elif action == "write":
                return bool(row[1])
            
            return False
    
    def _hash_password(self, password: str) -> str:
        """パスワードをハッシュ化"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """パスワードを検証"""
        return self._hash_password(password) == password_hash
    
    def _generate_api_key(self) -> str:
        """API Keyを生成（形式: mcp_xxxxxxxx）"""
        random_part = secrets.token_urlsafe(32)
        return f"mcp_{random_part}"

# シングルトンインスタンス
auth_db = AuthDatabase()

