"""Telegram adapter for the Google ADK customer-support agent.

Architecture:

    Telegram user
        |
        v
    python-telegram-bot
        |
        v
    Google ADK Runner
        |
        v
    customer_support_agent
        |
        v
    Telegram reply

This file is intentionally separate from agent.py. The ADK agent can therefore
still be run from the ADK playground/CLI without Telegram.
"""

import os

from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from telegramify_markdown import convert, split_entities

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent import root_agent

current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(dotenv_path=env_path)

APP_NAME = "customer_support_agent"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

# In-memory sessions are excellent for a demo.
# Each Telegram chat gets its own ADK conversation.
session_service = InMemorySessionService()

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


async def get_or_create_session(chat_id: int):
    """Gets this Telegram chat's ADK session, creating it if necessary."""
    user_id = str(chat_id)
    session_id = f"telegram_{chat_id}"

    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )

    if session is None:
        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )

    return session


async def ask_adk(chat_id: int, message: str) -> str:
    """Sends one Telegram message into ADK and returns the final response."""
    session = await get_or_create_session(chat_id)

    user_message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=message)],
    )

    final_response = "I couldn't generate a response."

    async for event in runner.run_async(
        user_id=str(chat_id),
        session_id=session.id,
        new_message=user_message,
    ):
        # ADK can yield multiple events, including tool-related events.
        # We only send the final model response back to Telegram.
        if event.is_final_response() and event.content:
            text_parts = [
                part.text
                for part in event.content.parts
                if part.text
            ]

            if text_parts:
                final_response = "\n".join(text_parts)

    return final_response


async def send_formatted_reply(message, markdown: str) -> None:
    """Converts Markdown to Telegram formatting and sends it safely."""
    text, entities = convert(markdown)

    chunks = split_entities(
        text,
        entities,
        max_utf16_len=4000,
    )

    for chunk_text, chunk_entities in chunks:
        await message.reply_text(
            chunk_text,
            entities=[
                entity.to_dict()
                for entity in chunk_entities
            ],
        )


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handles /start in Telegram."""
    await update.message.reply_text(
        "Hi! I'm the Mabuhay Home & Tech AI assistant. "
        "Ask me about products, delivery, returns, payments, or store hours."
    )


async def reset_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Starts a fresh ADK conversation for this Telegram chat."""
    chat_id = update.effective_chat.id
    user_id = str(chat_id)
    session_id = f"telegram_{chat_id}"

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )

    await update.message.reply_text(
        "Conversation reset. Let's start fresh!"
    )


async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Sends an ordinary Telegram text message to the ADK agent."""
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    user_message = update.message.text

    # Let the user know the bot received the message.
    await update.message.chat.send_action("typing")

    try:
        response = await ask_adk(chat_id, user_message)
        await send_formatted_reply(update.message, response)
    except Exception:
        # Don't expose internal stack traces or credentials to customers.
        await update.message.reply_text(
            "Sorry, I ran into a problem while processing that request."
        )


def main() -> None:
    """Starts the Telegram bot using long polling."""
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is not set. "
            "Create a bot with @BotFather and set the token first."
        )

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
    )

    print("Telegram bot is running. Press Ctrl+C to stop.")
    application.run_polling()


if __name__ == "__main__":
    main()
