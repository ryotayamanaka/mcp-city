"""
MCP Client Tools for integrating with MCP servers.

⚠️  DEPRECATED: This module is deprecated and will be removed in a future version.
    Use the new architecture instead:
    - mcp_client.py: Pure MCP client (framework-agnostic)
    - mcp_agno_adapter.py: Agno framework adapter
    
Migration guide:
    Old: from .mcp_client_tools import VendingMachineMCPTools
    New: from .mcp_agno_adapter import VendingMachineTools

This module provides tools that connect to MCP servers and expose their functionality
as Agno tools for use in AI agents.
"""

import asyncio
import json
import logging
import subprocess
from typing import Any, Dict, List, Optional

from agno.tools import Toolkit

logger = logging.getLogger(__name__)


class MCPClientTool(Toolkit):
    """Base class for MCP client tools."""
    
    def __init__(self, server_name: str, server_command: List[str]):
        """
        Initialize MCP client tool.
        
        Args:
            server_name: Name of the MCP server
            server_command: Command to start the MCP server
        """
        super().__init__(name=server_name.lower().replace(" ", "_"))
        self.server_name = server_name
        self.server_command = server_command
        self._process: Optional[subprocess.Popen] = None
        
    async def _start_server(self) -> subprocess.Popen:
        """Start the MCP server process."""
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
    
    async def _send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a request to the MCP server."""
        process = await self._start_server()
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        try:
            # Send request
            request_str = json.dumps(request) + "\n"
            logger.info(f"Sending MCP request: {request_str.strip()}")
            process.stdin.write(request_str)
            process.stdin.flush()
            
            # Read response with timeout
            import select
            import sys
            
            # Wait for response with timeout
            ready, _, _ = select.select([process.stdout], [], [], 10.0)
            if ready:
                response_line = process.stdout.readline()
                if response_line:
                    logger.info(f"Received MCP response: {response_line.strip()}")
                    response_data = json.loads(response_line.strip())
                    return response_data
                else:
                    raise Exception("Empty response from MCP server")
            else:
                raise Exception("Timeout waiting for MCP server response")
                
        except Exception as e:
            logger.error(f"Error communicating with MCP server: {e}")
            raise
    
    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> str:
        """Call a specific tool on the MCP server."""
        try:
            # First, list available tools
            tools_response = await self._send_request("tools/list")
            
            if "result" not in tools_response:
                return f"❌ Error listing tools: {tools_response.get('error', 'Unknown error')}"
            
            tools = tools_response["result"].get("tools", [])
            tool_found = any(tool.get("name") == tool_name for tool in tools)
            
            if not tool_found:
                available_tools = [tool.get("name") for tool in tools]
                return f"❌ Tool '{tool_name}' not found. Available tools: {', '.join(available_tools)}"
            
            # Call the tool
            call_response = await self._send_request("tools/call", {
                "name": tool_name,
                "arguments": arguments or {}
            })
            
            if "result" in call_response:
                content = call_response["result"].get("content", [])
                if content and len(content) > 0:
                    return content[0].get("text", "No text content")
                else:
                    return "No content returned"
            else:
                error = call_response.get("error", {})
                return f"❌ Tool call failed: {error.get('message', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return f"❌ Error calling tool {tool_name}: {str(e)}"
    
    def __del__(self):
        """Clean up the MCP server process when the tool is destroyed."""
        if self._process and self._process.poll() is None:
            self._process.terminate()
            self._process.wait()


class VendingMachineMCPTools(MCPClientTool):
    """MCP client tools for vending machine functionality."""
    
    def __init__(self):
        super().__init__(
            server_name="VendingMachineMCP",
            server_command=["python", "mcp_servers/vending_machine_mcp.py"]
        )
        # Register all the tool methods
        self.register(self.get_products)
        self.register(self.get_inventory)
        self.register(self.get_sales_data)
        self.register(self.make_purchase)
        self.register(self.get_analytics)
    
    def get_products(self) -> str:
        """Get all products available in the vending machine with their prices and categories."""
        return asyncio.run(self._call_tool("get_products"))
    
    def get_inventory(self) -> str:
        """Get current inventory status of the vending machine, including low stock alerts."""
        return asyncio.run(self._call_tool("get_inventory"))
    
    def get_sales_data(self) -> str:
        """Get sales data and daily statistics from the vending machine."""
        return asyncio.run(self._call_tool("get_sales_data"))
    
    def make_purchase(self, product_id: str, quantity: int = 1) -> str:
        """
        Simulate a purchase from the vending machine.
        
        Args:
            product_id: The ID of the product to purchase (e.g., 'p001')
            quantity: Number of items to purchase (default: 1)
        """
        return asyncio.run(self._call_tool("make_purchase", {
            "product_id": product_id,
            "quantity": quantity
        }))
    
    def get_analytics(self) -> str:
        """Get detailed analytics for the vending machine including sales trends and product performance."""
        return asyncio.run(self._call_tool("get_analytics"))
