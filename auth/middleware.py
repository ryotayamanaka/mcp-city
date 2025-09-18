"""
FastAPI認証ミドルウェア
API Key認証とJWT認証をサポート
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from .database import auth_db

security = HTTPBearer()

class AuthMiddleware:
    def __init__(self):
        self.db = auth_db
    
    def authenticate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """API Key認証"""
        return self.db.authenticate_api_key(api_key)
    
    def check_device_permission(self, user_id: str, device_type: str, action: str) -> bool:
        """デバイス権限チェック"""
        return self.db.check_permission(user_id, device_type, action)
    
    def get_user_permissions(self, user_id: str) -> list:
        """ユーザーの権限一覧を取得"""
        return self.db.get_device_permissions(user_id)

# グローバルインスタンス
auth_middleware = AuthMiddleware()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """現在のユーザーを取得（認証必須）"""
    print(f"DEBUG: get_current_user called with credentials = {credentials}")
    
    # API Key認証を試行
    user = auth_middleware.authenticate_api_key(credentials.credentials)
    print(f"DEBUG: user = {user}")
    if not user:
        print("DEBUG: Authentication failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効な認証情報です",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print("DEBUG: Authentication successful")
    return user

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """現在のユーザーを取得（認証オプション）"""
    if not credentials:
        return None
    
    return auth_middleware.authenticate_api_key(credentials.credentials)

def require_device_permission(device_type: str, action: str = "read"):
    """デバイス権限チェック用のデコレータ"""
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        if not auth_middleware.check_device_permission(current_user['id'], device_type, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{device_type}への{action}権限がありません"
            )
        return current_user
    
    return permission_checker

# デバイス別の権限チェック関数
def require_vending_machine_permission(action: str = "read"):
    """自動販売機権限チェック"""
    return require_device_permission("vending_machine", action)

def require_epalette_permission(action: str = "read"):
    """ePalette権限チェック"""
    return require_device_permission("epalette", action)

def require_city_database_permission(action: str = "read"):
    """街のデータベース権限チェック"""
    return require_device_permission("city_database", action)

