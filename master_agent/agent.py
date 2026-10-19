import os
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(dotenv_path=env_path)

from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

from simple_store_agent.agent import root_agent as store_agent
from inventory_optimization_agent.agent import root_agent as inventory_agent
from price_comparison_agent.agent import root_agent as price_agent
from sentiment_analysis_agent.agent import root_agent as sentiment_agent


MODEL = os.getenv(
    "DEMO_AGENT_MODEL",
    "us.anthropic.claude-haiku-4-5-20251001-v1:0",
)


root_agent = Agent(
    model=LiteLlm(MODEL),
    name="root_agent",
    description="Coordinates specialized retail customer-support agents. This is the dedicated multi-agent orchestrator.",
    instruction="""
    You are the central coordinator for Mabuhay Home & Tech.

    Delegate each request to the specialist whose responsibilities
    match the user's actual intent.

    Routing rules:
    - Questions about store information, including opening hours,
      closing times, weekly and holiday schedules, store policies,
      delivery, payment, returns, warranties, and product information
      documented in the store's reference document:
      delegate to simple_store_agent.
    - Inventory calculations, current stock, reorder points,
      safety stock, and replenishment quantities:
      delegate to inventory_optimization_agent.
    - Comparing prices for equivalent products across retailers:
      delegate to price_comparison_agent.
    - Classifying customer reviews or complaints by sentiment:
      delegate to sentiment_analysis_agent.

    A question about store hours is a store-information request,
    not a price-comparison request. Do not invoke the price
    comparison agent for store schedules.

    If a request requires multiple specialists, coordinate them
    as needed. If no specialist can handle a request, explain
    your limitations without inventing information.

    Do not claim an operation was completed unless the relevant
    specialist actually completed it.
    """,
    sub_agents=[
        store_agent,
        inventory_agent,
        price_agent,
        sentiment_agent,
    ],
)
