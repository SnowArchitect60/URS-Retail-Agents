"""Retail customer-feedback sentiment agent.

The sentiment score is deliberately deterministic so the demo can show a
normal Python tool being called by an LLM. The LLM is still useful for
explaining the result and identifying the likely customer issue.
"""

import os
import re

from google.adk.agents import Agent

MODEL = os.getenv("DEMO_AGENT_MODEL", "gemini-3.5-flash-lite")


POSITIVE_WORDS = {
    "love", "great", "good", "excellent", "fast", "helpful", "friendly",
    "easy", "happy", "perfect", "recommend", "satisfied", "smooth",
}

NEGATIVE_WORDS = {
    "bad", "poor", "slow", "late", "broken", "wrong", "rude", "difficult",
    "expensive", "refund", "disappointed", "missing", "unhappy", "problem",
}


def score_customer_feedback(feedback: str) -> dict:
    """Scores customer feedback using a small transparent word-based baseline.

    Args:
        feedback: The customer's review or complaint.

    Returns:
        A JSON-serializable dictionary containing sentiment counts and a label.
    """
    words = re.findall(r"[a-zA-Z']+", feedback.lower())

    positive_hits = [word for word in words if word in POSITIVE_WORDS]
    negative_hits = [word for word in words if word in NEGATIVE_WORDS]

    score = len(positive_hits) - len(negative_hits)

    if score > 0:
        label = "positive"
    elif score < 0:
        label = "negative"
    else:
        label = "neutral"

    return {
        "status": "success",
        "sentiment": label,
        "score": score,
        "positive_signals": positive_hits,
        "negative_signals": negative_hits,
        "note": "This is a simple demo baseline, not a production sentiment model.",
    }


root_agent = Agent(
    name="sentiment_analysis_agent",
    model=MODEL,
    instruction=(
        "You analyze retail customer feedback. "
        "Always use score_customer_feedback first. "
        "Explain the result in plain language, identify the customer's main issue "
        "or praise, and suggest a practical customer-service action. "
        "Do not present the keyword score as a scientifically validated sentiment "
        "model; it is only a transparent demonstration."
    ),
    tools=[score_customer_feedback],
)