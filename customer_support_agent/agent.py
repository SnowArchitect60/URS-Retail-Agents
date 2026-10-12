"""Retail customer-support agent.

This is intentionally readable: one knowledge lookup function and one agent.
The Markdown file is the store's synthetic source of truth.
"""

import os
from pathlib import Path

from google.adk.agents import Agent

MODEL = os.getenv("DEMO_AGENT_MODEL", "gemini-3.5-flash-lite")
STORE_INFO_FILE = Path(__file__).resolve().parent.parent / "retail_store.md"


def lookup_store_information(topic: str) -> dict:
    """Looks up the retail store's information from its Markdown profile.

    Args:
        topic: A topic such as products, delivery, returns, contact,
            store hours, payment, or warranty.

    Returns:
        A JSON-serializable dictionary containing relevant store information.
    """
    if not STORE_INFO_FILE.exists():
        return {
            "status": "error",
            "message": f"Store information file not found: {STORE_INFO_FILE}",
        }

    document = STORE_INFO_FILE.read_text(encoding="utf-8")

    # Keep the first demo intentionally simple: return the whole small document.
    # The model is responsible for finding the relevant section.
    return {
        "status": "success",
        "topic_requested": topic,
        "store_information": document,
    }


root_agent = Agent(
    name="customer_support_agent",
    model=MODEL,
    instruction=(
        "You are the customer-support assistant for a fictional retail MSME. "
        "Use lookup_store_information before answering questions about the store. "
        "Do not invent prices, policies, contact details, delivery promises, or "
        "product availability. If the document does not contain the answer, say so. "
        "Be concise and helpful."
    ),
    tools=[lookup_store_information],
)