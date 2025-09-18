"""
認証関連のPydanticモデル
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime
    is_active: bool

class ApiKeyCreate(BaseModel):
    name: str
    expires_days: Optional[int] = 365

class ApiKeyResponse(BaseModel):
    id: str
    name: str
    api_key: str
    created_at: datetime
    expires_at: Optional[datetime]

class DevicePermission(BaseModel):
    device_type: str
    can_read: bool
    can_write: bool

class UserPermissions(BaseModel):
    user_id: str
    username: str
    permissions: List[DevicePermission]

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

