"""
Agno Framework Adapter for MCP Clients.

This module provides adapter classes that bridge pure MCP clients
with the Agno framework, allowing MCP servers to be used as Agno tools.
"""

import asyncio
import logging
from typing import List

from agno.tools import Toolkit
from .mcp_client import VendingMachineMCPClient, MCPError

logger = logging.getLogger(__name__)


class MCPAgnoAdapter(Toolkit):
    """Base adapter class for integrating MCP clients with Agno framework."""
    
    def __init__(self, name: str, mcp_client):
        """
        Initialize MCP Agno adapter.
        
        Args:
            name: Name for the toolkit
            mcp_client: The MCP client instance to wrap
        """
        super().__init__(name=name)
        self.mcp_client = mcp_client
    
    def _run_async(self, coro):
        """Helper to run async operations in sync context."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an event loop, create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro)
                    return future.result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            # No event loop, create a new one
            return asyncio.run(coro)
    
    def __del__(self):
        """Clean up MCP client when adapter is destroyed."""
        if hasattr(self, 'mcp_client') and self.mcp_client:
            self.mcp_client.stop()


class VendingMachineTools(MCPAgnoAdapter):
    """Agno toolkit for vending machine MCP functionality."""
    
    def __init__(self, server_command: List[str] = None):
        """
        Initialize vending machine tools.
        
        Args:
            server_command: Command to start the vending machine MCP server.
                           If None, uses default local server command.
        """
        mcp_client = VendingMachineMCPClient(server_command)
        super().__init__(name="vending_machine", mcp_client=mcp_client)
        
        # Register all tool methods with Agno
        self.register(self.get_products)
        self.register(self.get_inventory)
        self.register(self.get_sales_data)
        self.register(self.make_purchase)
        self.register(self.get_analytics)
    
    def get_products(self) -> str:
        """
        Get all products available in the vending machine with their prices and categories.
        
        Returns:
            Formatted string listing all available products
        """
        try:
            return self._run_async(self.mcp_client.get_products())
        except MCPError as e:
            logger.error(f"MCP error getting products: {e}")
            return f"❌ Error getting products: {e.message}"
        except Exception as e:
            logger.error(f"Unexpected error getting products: {e}")
            return f"❌ Unexpected error getting products: {str(e)}"
    
    def get_inventory(self) -> str:
        """
        Get current inventory status of the vending machine, including low stock alerts.
        
        Returns:
            Formatted string showing inventory status and alerts
        """
        try:
            return self._run_async(self.mcp_client.get_inventory())
        except MCPError as e:
            logger.error(f"MCP error getting inventory: {e}")
            return f"❌ Error getting inventory: {e.message}"
        except Exception as e:
            logger.error(f"Unexpected error getting inventory: {e}")
            return f"❌ Unexpected error getting inventory: {str(e)}"
    
    def get_sales_data(self) -> str:
        """
        Get sales data and daily statistics from the vending machine.
        
        Returns:
            Formatted string showing sales statistics and recent transactions
        """
        try:
            return self._run_async(self.mcp_client.get_sales_data())
        except MCPError as e:
            logger.error(f"MCP error getting sales data: {e}")
            return f"❌ Error getting sales data: {e.message}"
        except Exception as e:
            logger.error(f"Unexpected error getting sales data: {e}")
            return f"❌ Unexpected error getting sales data: {str(e)}"
    
    def make_purchase(self, product_id: str, quantity: int = 1) -> str:
        """
        Simulate a purchase from the vending machine.
        
        Args:
            product_id: The ID of the product to purchase (e.g., 'p001')
            quantity: Number of items to purchase (default: 1)
            
        Returns:
            Purchase confirmation or error message
        """
        try:
            return self._run_async(self.mcp_client.make_purchase(product_id, quantity))
        except MCPError as e:
            logger.error(f"MCP error making purchase: {e}")
            return f"❌ Error making purchase: {e.message}"
        except Exception as e:
            logger.error(f"Unexpected error making purchase: {e}")
            return f"❌ Unexpected error making purchase: {str(e)}"
    
    def get_analytics(self) -> str:
        """
        Get detailed analytics for the vending machine including sales trends and product performance.
        
        Returns:
            Formatted string showing detailed analytics and performance metrics
        """
        try:
            return self._run_async(self.mcp_client.get_analytics())
        except MCPError as e:
            logger.error(f"MCP error getting analytics: {e}")
            return f"❌ Error getting analytics: {e.message}"
        except Exception as e:
            logger.error(f"Unexpected error getting analytics: {e}")
            return f"❌ Unexpected error getting analytics: {str(e)}"


# Convenience function to create vending machine tools
def create_vending_machine_tools(server_command: List[str] = None) -> VendingMachineTools:
    """
    Create a VendingMachineTools instance.
    
    Args:
        server_command: Command to start the vending machine MCP server.
                       If None, uses default local server command.
    
    Returns:
        Configured VendingMachineTools instance
    """
    return VendingMachineTools(server_command)