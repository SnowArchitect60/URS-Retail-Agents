"""Step 1: the smallest useful Google ADK retail agent.

This agent has one plain Python function as a tool. The model decides when
that function is useful, calls it, and turns the result into a response.
"""

import os
from google.adk.agents import Agent

MODEL = os.getenv("DEMO_AGENT_MODEL", "gemini-3.5-flash-lite")


def get_store_hours(day: str) -> dict:
    """Returns the store's opening hours for a day of the week.

    Args:
        day: Day name such as Monday or Sunday.

    Returns:
        A JSON-serializable dictionary containing the hours or a closed status.
    """
    hours = {
        "monday": "9:00 AM - 7:00 PM",
        "tuesday": "9:00 AM - 7:00 PM",
        "wednesday": "9:00 AM - 7:00 PM",
        "thursday": "9:00 AM - 7:00 PM",
        "friday": "9:00 AM - 7:00 PM",
        "saturday": "9:00 AM - 6:00 PM",
        "sunday": "Closed",
    }

    normalized_day = day.strip().lower()

    if normalized_day not in hours:
        return {
            "status": "error",
            "message": "Please provide a valid day of the week.",
        }

    return {
        "status": "success",
        "day": day,
        "hours": hours[normalized_day],
    }


root_agent = Agent(
    name="simple_store_agent",
    model=MODEL,
    instruction=(
        "You are a simple retail store assistant. "
        "Answer store-hours questions using the get_store_hours tool. "
        "If the user asks something unrelated, say what you can help with."
    ),
    tools=[get_store_hours],
)