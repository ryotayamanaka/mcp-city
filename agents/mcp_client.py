"""
Pure MCP Client implementation - framework agnostic.

This module provides a clean MCP client that can communicate with MCP servers
using the JSON-RPC over stdio protocol, without any framework dependencies.
"""

import asyncio
import json
import logging
import subprocess
import select
import sys
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MCPClient:
    """Pure MCP client for communicating with MCP servers via stdio."""
    
    def __init__(self, server_command: List[str], server_name: str = "MCPServer"):
        """
        Initialize MCP client.
        
        Args:
            server_command: Command to start the MCP server
            server_name: Name of the MCP server for logging
        """
        self.server_command = server_command
        self.server_name = server_name
        self._process: Optional[subprocess.Popen] = None
        self._request_id = 0
        
    def _get_next_id(self) -> int:
        """Get next request ID."""
        self._request_id += 1
        return self._request_id
        
    async def start_server(self) -> subprocess.Popen:
        """Start the MCP server process if not already running."""
        if self._process is None or self._process.poll() is not None:
            logger.info(f"Starting MCP server: {self.server_name}")
            self._process = subprocess.Popen(
                self.server_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # Wait a moment for the server to start
            await asyncio.sleep(1.0)
        return self._process
    
    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send a JSON-RPC request to the MCP server.
        
        Args:
            method: The JSON-RPC method name
            params: Parameters for the method
            
        Returns:
            The JSON-RPC response
            
        Raises:
            Exception: If communication with server fails
        """
        process = await self.start_server()
        
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": method,
            "params": params or {}
        }
        
        try:
            # Send request
            request_str = json.dumps(request) + "\n"
            logger.debug(f"Sending MCP request: {request_str.strip()}")
            process.stdin.write(request_str)
            process.stdin.flush()
            
            # Read response with timeout
            ready, _, _ = select.select([process.stdout], [], [], 10.0)
            if ready:
                response_line = process.stdout.readline()
                if response_line:
                    logger.debug(f"Received MCP response: {response_line.strip()}")
                    response_data = json.loads(response_line.strip())
                    
                    if "error" in response_data:
                        error = response_data["error"]
                        raise MCPError(f"Server error: {error.get('message', 'Unknown error')}", error.get('code', -1))
                    
                    return response_data
                else:
                    raise MCPError("Empty response from MCP server")
            else:
                raise MCPError("Timeout waiting for MCP server response")
                
        except json.JSONDecodeError as e:
            raise MCPError(f"Invalid JSON response: {e}")
        except Exception as e:
            if isinstance(e, MCPError):
                raise
            logger.error(f"Error communicating with MCP server: {e}")
            raise MCPError(f"Communication error: {e}")
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the MCP session."""
        return await self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "PythonMCPClient",
                "version": "1.0.0"
            }
        })
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from the MCP server.
        
        Returns:
            List of tool definitions
        """
        response = await self.send_request("tools/list")
        if "result" in response:
            return response["result"].get("tools", [])
        return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> str:
        """
        Call a specific tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            The tool's response as a string
            
        Raises:
            MCPError: If the tool call fails
        """
        # Verify tool exists
        tools = await self.list_tools()
        tool_found = any(tool.get("name") == tool_name for tool in tools)
        
        if not tool_found:
            available_tools = [tool.get("name") for tool in tools]
            raise MCPError(f"Tool '{tool_name}' not found. Available tools: {', '.join(available_tools)}")
        
        # Call the tool
        response = await self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments or {}
        })
        
        if "result" in response:
            content = response["result"].get("content", [])
            if content and len(content) > 0:
                return content[0].get("text", "No text content")
            else:
                return "No content returned"
        else:
            error = response.get("error", {})
            raise MCPError(f"Tool call failed: {error.get('message', 'Unknown error')}")
    
    def stop(self):
        """Stop the MCP server process."""
        if self._process and self._process.poll() is None:
            logger.info(f"Stopping MCP server: {self.server_name}")
            self._process.terminate()
            try:
                self._process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                logger.warning("MCP server did not terminate gracefully, killing it")
                self._process.kill()
                self._process.wait()
            self._process = None
    
    def __del__(self):
        """Clean up when the client is destroyed."""
        self.stop()


class MCPError(Exception):
    """Exception raised for MCP-related errors."""
    
    def __init__(self, message: str, code: int = -1):
        super().__init__(message)
        self.code = code
        self.message = message


class VendingMachineMCPClient(MCPClient):
    """Specialized MCP client for vending machine operations."""
    
    def __init__(self, server_command: List[str] = None):
        """
        Initialize vending machine MCP client.
        
        Args:
            server_command: Command to start the vending machine MCP server.
                           Defaults to local server command.
        """
        if server_command is None:
            server_command = ["python", "mcp_servers/vending_machine_mcp.py"]
        
        super().__init__(server_command, "VendingMachineMCP")
    
    async def get_products(self) -> str:
        """Get all products available in the vending machine."""
        return await self.call_tool("get_products")
    
    async def get_inventory(self) -> str:
        """Get current inventory status of the vending machine."""
        return await self.call_tool("get_inventory")
    
    async def get_sales_data(self) -> str:
        """Get sales data and daily statistics from the vending machine."""
        return await self.call_tool("get_sales_data")
    
    async def make_purchase(self, product_id: str, quantity: int = 1) -> str:
        """
        Simulate a purchase from the vending machine.
        
        Args:
            product_id: The ID of the product to purchase
            quantity: Number of items to purchase
            
        Returns:
            Purchase result message
        """
        return await self.call_tool("make_purchase", {
            "product_id": product_id,
            "quantity": quantity
        })
    
    async def get_analytics(self) -> str:
        """Get detailed analytics for the vending machine."""
        return await self.call_tool("get_analytics")