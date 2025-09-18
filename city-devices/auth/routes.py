"""
認証関連のAPIエンドポイント
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from typing import List
from datetime import datetime
from .database import auth_db
from .models import (
    UserCreate, UserLogin, UserResponse, 
    ApiKeyCreate, ApiKeyResponse, UserPermissions,
    AuthResponse, ErrorResponse
)
from .middleware import get_current_user

router = APIRouter(prefix="/auth", tags=["認証"])

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """新しいユーザーを登録"""
    try:
        # ユーザー名とメールアドレスの重複チェック
        existing_user = auth_db.get_user_by_id("dummy")  # 簡易チェック用
        # 実際の重複チェックは実装が必要
        
        user_id = auth_db.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )
        
        user = auth_db.get_user_by_id(user_id)
        return UserResponse(**user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ユーザー登録に失敗しました: {str(e)}"
        )

@router.post("/login", response_model=AuthResponse)
async def login_user(login_data: UserLogin):
    """ユーザーログイン"""
    user = auth_db.authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが正しくありません"
        )
    
    # API Keyを生成（簡易的なトークンとして使用）
    api_key = auth_db.create_api_key(user['id'], "Login Session Key", expires_days=1)
    
    return AuthResponse(
        access_token=api_key,
        user=UserResponse(**user)
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """現在のユーザー情報を取得"""
    return UserResponse(**current_user)

@router.post("/api-keys", response_model=ApiKeyResponse)
async def create_api_key(
    key_data: ApiKeyCreate,
    current_user: dict = Depends(get_current_user)
):
    """API Keyを作成"""
    api_key = auth_db.create_api_key(
        user_id=current_user['id'],
        name=key_data.name,
        expires_days=key_data.expires_days
    )
    
    return ApiKeyResponse(
        id="generated",
        name=key_data.name,
        api_key=api_key,
        created_at=datetime.now(),
        expires_at=None
    )

@router.get("/permissions", response_model=UserPermissions)
async def get_user_permissions(current_user: dict = Depends(get_current_user)):
    """ユーザーの権限一覧を取得"""
    permissions = auth_db.get_device_permissions(current_user['id'])
    
    return UserPermissions(
        user_id=current_user['id'],
        username=current_user['username'],
        permissions=[
            {
                "device_type": perm['device_type'],
                "can_read": perm['can_read'],
                "can_write": perm['can_write']
            }
            for perm in permissions
        ]
    )

@router.get("/health")
async def auth_health_check():
    """認証システムのヘルスチェック"""
    return {
        "status": "healthy",
        "service": "認証システム",
        "database": "SQLite"
    }
