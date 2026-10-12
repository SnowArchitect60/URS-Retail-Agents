"""Retail inventory-optimization agent.

The calculation is intentionally visible rather than hidden in a large class.
The LLM interprets the business situation; the Python function performs the
numeric reorder calculation.
"""

import os
from google.adk.agents import Agent

MODEL = os.getenv("DEMO_AGENT_MODEL", "gemini-3.5-flash-lite")


def calculate_reorder_plan(
    product_name: str,
    current_stock: int,
    average_daily_sales: float,
    supplier_lead_time_days: int,
    safety_stock: int,
) -> dict:
    """Calculates a simple reorder point and suggested reorder quantity.

    Args:
        product_name: Product being evaluated.
        current_stock: Current units available.
        average_daily_sales: Average units sold per day.
        supplier_lead_time_days: Supplier lead time in days.
        safety_stock: Extra units kept as a buffer.

    Returns:
        A JSON-serializable inventory recommendation.
    """
    if current_stock < 0:
        return {"status": "error", "message": "current_stock cannot be negative."}

    if average_daily_sales < 0:
        return {
            "status": "error",
            "message": "average_daily_sales cannot be negative.",
        }

    if supplier_lead_time_days < 0:
        return {
            "status": "error",
            "message": "supplier_lead_time_days cannot be negative.",
        }

    if safety_stock < 0:
        return {"status": "error", "message": "safety_stock cannot be negative."}

    expected_lead_time_demand = average_daily_sales * supplier_lead_time_days
    reorder_point = expected_lead_time_demand + safety_stock

    # For a simple demo, replenish only enough to restore the stock to the
    # reorder-point level. A production system would use a target stock level,
    # order quantities, seasonality, and supplier constraints.
    suggested_order_quantity = max(
        0,
        round(reorder_point - current_stock),
    )

    return {
        "status": "success",
        "product": product_name,
        "current_stock": current_stock,
        "expected_lead_time_demand": round(expected_lead_time_demand, 2),
        "reorder_point": round(reorder_point, 2),
        "suggested_order_quantity": suggested_order_quantity,
        "needs_reorder": current_stock <= reorder_point,
    }


root_agent = Agent(
    name="inventory_optimization_agent",
    model=MODEL,
    instruction=(
        "You are an inventory analyst for a small retail business. "
        "When the user gives inventory figures, use calculate_reorder_plan "
        "to perform the arithmetic. Explain what the reorder point means, "
        "whether a reorder is currently indicated, and the suggested quantity. "
        "Be explicit that this is a simple baseline and not a full demand-forecasting "
        "system."
    ),
    tools=[calculate_reorder_plan],
)