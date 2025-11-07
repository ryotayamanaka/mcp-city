#!/usr/bin/env python3
"""
Auth Service - 認証専用マイクロサービス
街の認証・権限管理を担当する独立したサービス
"""

import os
import sys
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware

# 同一サービス内のauth モジュールを参照

from auth.routes import router as auth_router
from auth.middleware import get_current_user

app = FastAPI(
    title="MCP City - Authentication Service",
    description="街の認証・権限管理サービス",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限する
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 認証関連のルート
app.include_router(auth_router, prefix="/auth", tags=["authentication"])

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "service": "MCP City - Authentication Service",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "auth": "/auth/*",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy", "service": "auth-service"}

@app.get("/auth/validate")
async def validate_token(current_user: dict = Depends(get_current_user)):
    """トークン検証エンドポイント（他サービス用）"""
    return {
        "valid": True,
        "user": current_user
    }

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "9000"))

    print(f"🔐 Starting Auth Service on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
