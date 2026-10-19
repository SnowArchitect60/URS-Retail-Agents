
"""Retail price-comparison agent.

Claude Haiku performs the analysis, while a custom Tavily search
function retrieves external product listings through Google ADK.
"""

import os
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, ".env")
load_dotenv(dotenv_path=env_path, override=True)

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from tavily import TavilyClient


MODEL = os.getenv(
    "DEMO_AGENT_MODEL",
    "us.anthropic.claude-haiku-4-5-20251001-v1:0",
)


def search_product_prices(
    query: str,
    max_results: int = 5,
) -> dict:
    """Searches the public web for product listings and price information.

    Args:
        query: A specific web search query. Include the product name,
            model number, relevant specifications, and retail pricing terms.
        max_results: Maximum number of search results to return, from 1 to 10.

    Returns:
        A dictionary containing the search status and a list of results.
        Each result includes its title, URL, and available text snippet.
    """
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return {
            "status": "error",
            "message": (
                "TAVILY_API_KEY is missing. Configure it in the "
                "agent's .env file."
            ),
        }

    if not query.strip():
        return {
            "status": "error",
            "message": "The search query cannot be empty.",
        }

    max_results = max(1, min(max_results, 10))

    try:
        client = TavilyClient(api_key=api_key)

        response = client.search(
            query=query,
            search_depth="basic",
            topic="general",
            max_results=max_results,
            include_answer=False,
        )

        results = []

        for item in response.get("results", []):
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", ""),
                }
            )

        return {
            "status": "success",
            "query": query,
            "result_count": len(results),
            "results": results,
            "notice": (
                "Search snippets are not verified live prices. "
                "Check the linked retailer pages before treating "
                "a price as current or available."
            ),
        }

    except Exception as exc:
        # Return a tool-level error so the agent can explain the
        # search failure instead of confusing it with a price result.
        return {
            "status": "error",
            "message": f"Product search failed: {type(exc).__name__}: {exc}",
        }


root_agent = Agent(
    name="price_comparison_agent",
    model=LiteLlm(MODEL),
    description=(
        "Searches the public web for comparable products and "
        "compares their listed prices with a store's supplied price."
    ),
    instruction=(
        "You are a retail price-comparison analyst. "

        "When the user provides a product and our store price, "
        "use search_product_prices to find comparable products from "
        "reputable retailers. Construct a focused search query using "
        "the product name, model number, relevant specifications, "
        "and pricing terms. Search again with a more specific query "
        "when the initial results are insufficient. "

        "Prefer the exact same model when available. Otherwise, "
        "compare products with genuinely similar specifications. "

        "For every useful result, report the retailer or source, "
        "URL, listed price, currency, and relevant differences in "
        "specifications or included accessories when that information "
        "is available in the search results. "

        "Never invent prices, currencies, specifications, or URLs. "
        "A search snippet is not proof that a price is current. "
        "If the price cannot be established from the available "
        "evidence, say so explicitly. Distinguish shipping costs, "
        "discounts, and conditional prices from ordinary listed prices. "

        "If the search fails or returns insufficient evidence, "
        "explain the limitation rather than fabricate a comparison. "

        "Finish with a concise comparison against our store price, "
        "including the absolute difference and percentage difference "
        "when both prices are available in the same currency. "
        "State which product is cheaper and disclose important "
        "limitations in the comparison."
    ),
    tools=[search_product_prices],
)
