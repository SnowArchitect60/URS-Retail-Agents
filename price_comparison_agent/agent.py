"""Retail price-comparison agent.

Google Search is ADK's built-in web-grounding tool. The agent searches the
public web for comparable products, then compares the found information with
the store's supplied product price.

Important ADK detail:
Google Search is a model-internal grounding tool. Keep this agent focused on
search rather than mixing google_search with ordinary FunctionTools.
"""

import os

from google.adk.agents import Agent
from google.adk.tools import google_search

MODEL = os.getenv("DEMO_AGENT_MODEL", "gemini-3.5-flash-lite")


root_agent = Agent(
    name="price_comparison_agent",
    model=MODEL,
    instruction=(
        "You are a retail price-comparison analyst. "
        "When the user provides a product and our store price, search the web "
        "for similar or equivalent products from reputable retailers. "
        "Prefer the same model when available; otherwise use genuinely comparable "
        "specifications. Report the source, listed price, currency, and any major "
        "differences in specification or bundle. Do not claim that two products "
        "are equivalent when the evidence is unclear. Distinguish listed price "
        "from shipping, discounts, or other conditional costs. "
        "Use Google Search for current external information."
    ),
    tools=[google_search],
)