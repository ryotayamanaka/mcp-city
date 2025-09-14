"""
Food Cart Agent module for e-Palette and vending machine control.

This agent provides control capabilities for autonomous food cart screens
and smart vending machine management.
"""

from agno.agent import Agent
from agno.models.google import Gemini
from agno.storage.sqlite import SqliteStorage
from tools import FoodCartScreenTools
from .mcp_agno_adapter import VendingMachineTools


def create_food_cart_agent(agent_storage: str) -> Agent:
    """
    Create and configure the Food Cart Agent.
    
    Args:
        agent_storage (str): Path to the SQLite database file for agent storage
        
    Returns:
        Agent: Configured Food Cart Agent instance
    """
    return Agent(
        name="e-Palette & Vending Machine Controller",
        model=Gemini(id="gemini-2.5-pro"),
        tools=[
            FoodCartScreenTools(),
            VendingMachineTools()
        ],
        instructions=[
            "You are an AI agent that controls the promotional screen on an autonomous e-Palette and manages a smart vending machine.",
            
            # e-Palette Screen Control
            "For the e-Palette screen, you can:",
            "- Update the screen with text messages and emojis",
            "- Display promotional images",
            "- Clear the screen",
            "- Check the current display status",
            
            # Vending Machine Management
            "For the vending machine, you can:",
            "- Get the list of available products with prices and stock levels",
            "- Check inventory status and receive low stock alerts",
            "- View sales data and daily performance statistics",
            "- Simulate purchases to test the system",
            "- Generate comprehensive analytics reports with trends and insights",
            
            # General Guidelines
            "Always be helpful and provide detailed information when asked.",
            "Use emojis and engaging language to make responses attractive.",
            "When showing data, format it clearly with bullet points and sections.",
            "Provide actionable insights when analyzing sales data.",
            "Alert about low stock items proactively.",
            "If asked about sales performance, provide both summary and detailed analytics.",
            "When there are connection issues, suggest checking if the IoT device server is running on localhost:8000.",
            
            # Analytics and Reporting
            "When providing analytics:",
            "- Highlight top-selling products",
            "- Identify trends in sales data",
            "- Suggest inventory replenishment for low stock items",
            "- Compare daily, weekly, and monthly performance",
            "- Provide category-wise performance analysis"
        ],
        storage=SqliteStorage(table_name="food_cart_agent", db_file=agent_storage),
        add_datetime_to_instructions=True,
        add_history_to_messages=True,
        num_history_responses=3,
        markdown=True,
    )
