"""
Finance Agent module for financial data and analysis.

This agent provides financial information using Yahoo Finance data.
"""

from agno.agent import Agent
from agno.models.google import Gemini
from agno.storage.sqlite import SqliteStorage
from agno.tools.yfinance import YFinanceTools


def create_finance_agent(agent_storage: str) -> Agent:
    """
    Create and configure the Finance Agent.
    
    Args:
        agent_storage (str): Path to the SQLite database file for agent storage
        
    Returns:
        Agent: Configured Finance Agent instance
    """
    return Agent(
        name="Finance Agent",
        model=Gemini(id="gemini-2.5-pro"),
        tools=[YFinanceTools(
            stock_price=True, 
            analyst_recommendations=True, 
            company_info=True, 
            company_news=True
        )],
        instructions=["Always use tables to display data"],
        storage=SqliteStorage(table_name="finance_agent", db_file=agent_storage),
        add_datetime_to_instructions=True,
        add_history_to_messages=True,
        num_history_responses=5,
        markdown=True,
    )
