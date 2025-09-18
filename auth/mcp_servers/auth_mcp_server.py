#!/usr/bin/env python3
"""
Auth MCP Server
認証専用のMCPサーバー - 街全体の認証情報を管理
"""

import json
import sys
import requests
import argparse
import os

# 認証サービスのベースURL
AUTH_BASE_URL = os.getenv("AUTH_VALIDATE_URL", "http://localhost:8000/auth")
API_KEY = os.getenv("MCP_CITY_API_KEY") or os.getenv("CITY_DEVICES_API_KEY")


def auth_headers():
    return {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}


class AuthMCP:
    def get_auth_info(self):
        """現在の認証ユーザー情報を取得"""
        try:
            r = requests.get(f"{AUTH_BASE_URL}/me", headers=auth_headers(), timeout=10)
            if r.status_code in (401, 403):
                return {"success": False, "error": "認証が必要です", "authenticated": False}
            r.raise_for_status()
            user_info = r.json()
            return {
                "success": True, 
                "authenticated": True,
                "user": user_info,
                "api_key_present": bool(API_KEY)
            }
        except Exception as e:
            return {"success": False, "error": f"auth info error: {e}", "authenticated": False}

    def get_permissions(self):
        """現在のユーザーの権限情報を取得"""
        try:
            # 将来的な拡張：権限詳細取得
            # 現在は基本的な認証情報のみ
            auth_result = self.get_auth_info()
            if not auth_result.get("success"):
                return auth_result
            
            return {
                "success": True,
                "permissions": {
                    "epalette": {"read": True, "write": True},  # 管理者は全権限
                    "vending_machine": {"read": True, "write": True},
                    "city_database": {"read": True, "write": True}
                }
            }
        except Exception as e:
            return {"success": False, "error": f"permissions error: {e}"}

    def test_auth_connection(self):
        """認証サービスへの接続テスト"""
        try:
            r = requests.get(f"{AUTH_BASE_URL}/me", headers=auth_headers(), timeout=5)
            return {
                "success": True,
                "status_code": r.status_code,
                "authenticated": r.status_code == 200
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


def handle_request(request_data):
    try:
        req = json.loads(request_data)
    except json.JSONDecodeError:
        return json.dumps({
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32700, "message": "Parse error"}
        })

    method = req.get("method")
    request_id = req.get("id")

    if method == "initialize":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "AuthMCP",
                    "version": "1.0.0"
                }
            }
        })

    elif method == "notifications/initialized":
        return None

    elif method == "tools/list":
        tools_list = [
            {
                "name": "get_auth_info",
                "description": "Get current authenticated user information",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "get_permissions",
                "description": "Get current user's permissions for city devices and systems",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "test_auth_connection",
                "description": "Test connection to authentication service",
                "inputSchema": {"type": "object", "properties": {}}
            }
        ]
        
        return json.dumps({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": tools_list}
        })

    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        auth = AuthMCP()
        
        try:
            if tool_name == "get_auth_info":
                result = auth.get_auth_info()
                if result.get("success"):
                    user = result.get("user", {})
                    response_text = f"👤 **認証情報:**\n\n"
                    response_text += f"✅ **認証状態:** 認証済み\n"
                    response_text += f"🆔 **ユーザーID:** {user.get('id', 'N/A')}\n"
                    response_text += f"👤 **ユーザー名:** {user.get('username', 'N/A')}\n"
                    response_text += f"📧 **メールアドレス:** {user.get('email', 'N/A')}\n"
                    response_text += f"📅 **作成日:** {user.get('created_at', 'N/A')}\n"
                    response_text += f"🔑 **APIキー:** {'設定済み' if result.get('api_key_present') else '未設定'}\n"
                    response_text += f"🔒 **アクティブ:** {'はい' if user.get('is_active') else 'いいえ'}"
                else:
                    response_text = f"❌ **認証情報取得エラー:**\n{result.get('error', 'Unknown error')}"
                
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": response_text
                            }
                        ]
                    }
                })

            elif tool_name == "get_permissions":
                result = auth.get_permissions()
                if result.get("success"):
                    permissions = result.get("permissions", {})
                    response_text = f"🔐 **権限情報:**\n\n"
                    
                    for device, perms in permissions.items():
                        device_name = {
                            "epalette": "🚌 ePalette",
                            "vending_machine": "🏪 自動販売機", 
                            "city_database": "🗄️ 街データベース"
                        }.get(device, device)
                        
                        read_status = "✅" if perms.get("read") else "❌"
                        write_status = "✅" if perms.get("write") else "❌"
                        response_text += f"{device_name}:\n"
                        response_text += f"  📖 **読み取り:** {read_status}\n"
                        response_text += f"  ✏️ **書き込み:** {write_status}\n\n"
                else:
                    response_text = f"❌ **権限情報取得エラー:**\n{result.get('error', 'Unknown error')}"
                
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": response_text
                            }
                        ]
                    }
                })

            elif tool_name == "test_auth_connection":
                result = auth.test_auth_connection()
                if result.get("success"):
                    status = result.get("status_code")
                    authenticated = result.get("authenticated")
                    if authenticated:
                        response_text = "✅ **認証サービス接続:** 正常\n✅ **認証状態:** 認証済み"
                    else:
                        response_text = f"⚠️ **認証サービス接続:** 正常\n❌ **認証状態:** 未認証 (HTTP {status})"
                else:
                    response_text = f"❌ **認証サービス接続エラー:**\n{result.get('error')}"
                
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": response_text
                            }
                        ]
                    }
                })

            else:
                result = f"❌ Unknown tool: {tool_name}"
        except Exception as e:
            result = f"❌ Error: {str(e)}"
        
        return json.dumps({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
        })

    else:
        return json.dumps({
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        })


def main():
    parser = argparse.ArgumentParser(description="Auth MCP Server")
    args = parser.parse_args()

    for line in sys.stdin:
        try:
            response = handle_request(line.strip())
            if response:
                print(response, flush=True)
        except KeyboardInterrupt:
            break
        except Exception as e:
            error_response = json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            })
            print(error_response, flush=True)


if __name__ == "__main__":
    main()
