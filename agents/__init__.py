"""
Agents module for the AI playground application.

This module contains all the AI agents used in the playground:
- Web Agent: For web search and information retrieval
- Finance Agent: For financial data and analysis
- Food Cart Agent: For e-Palette and vending machine control
"""

from .web_agent import create_web_agent
from .finance_agent import create_finance_agent
from .food_cart_agent import create_food_cart_agent

__all__ = [
    'create_web_agent',
    'create_finance_agent', 
    'create_food_cart_agent'
]
