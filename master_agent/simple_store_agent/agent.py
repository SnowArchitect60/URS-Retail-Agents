"""Step 1: the smallest useful Google ADK retail agent.

This agent has one plain Python function as a tool. The model decides when
that function is useful, calls it, and turns the result into a response.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(dotenv_path=env_path)

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

STORE_INFO_FILE = Path(__file__).resolve().parent.parent.parent / "retail_store.md"

MODEL = os.getenv(
    "DEMO_AGENT_MODEL",
    "us.anthropic.claude-haiku-4-5-20251001-v1:0",
)

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
    name="simple_store_agent",
    description=(
        "Handles questions about store information, including "
        "opening hours, closing times, weekly and holiday schedules, "
        "store policies, delivery, payment, returns, warranties, "
        "and product information. Use for store-related inquiries "
        "that require retrieving information from the store's "
        "reference document."
    ),
    model=LiteLlm(MODEL),
    instruction=(
        "You are a retail store assistant. "
        "Use lookup_store_information before answering questions about the store. "
        "Do not invent prices, policies, contact details, delivery promises, or "
        "product availability. If the document does not contain the answer, say so. "
        "Be concise and helpful. "
        "For unrelated questions, explain what you can help with."
    ),
    tools=[lookup_store_information,],
)