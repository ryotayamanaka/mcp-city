"""
Web Agent module for web search and information retrieval.

This agent provides web search capabilities using DuckDuckGo search.
"""

from agno.agent import Agent
from agno.models.google import Gemini
from agno.storage.sqlite import SqliteStorage
from agno.tools.duckduckgo import DuckDuckGoTools


def create_web_agent(agent_storage: str) -> Agent:
    """
    Create and configure the Web Agent.
    
    Args:
        agent_storage (str): Path to the SQLite database file for agent storage
        
    Returns:
        Agent: Configured Web Agent instance
    """
    return Agent(
        name="Web Agent",
        model=Gemini(id="gemini-2.5-pro"),
        tools=[DuckDuckGoTools()],
        instructions=["Always include sources"],
        # Store the agent sessions in a sqlite database
        storage=SqliteStorage(table_name="web_agent", db_file=agent_storage),
        # Adds the current date and time to the instructions
        add_datetime_to_instructions=True,
        # Adds the history of the conversation to the messages
        add_history_to_messages=True,
        # Number of history responses to add to the messages
        num_history_responses=5,
        # Adds markdown formatting to the messages
        markdown=True,
    )
