"""
AI Playground Application

This is the main entry point for the AI playground application.
It creates and configures all available AI agents and provides
a unified interface for interacting with them.
"""

from agno.playground import Playground
from agents import create_web_agent, create_finance_agent, create_food_cart_agent

# Configuration
agent_storage: str = "tmp/agents.db"

# Create all agents using the modular approach
web_agent = create_web_agent(agent_storage)
finance_agent = create_finance_agent(agent_storage)
food_cart_agent = create_food_cart_agent(agent_storage)

# Create the playground with all agents
playground_app = Playground(agents=[web_agent, finance_agent, food_cart_agent])
app = playground_app.get_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("playground:app", host="0.0.0.0", port=8000, reload=True)