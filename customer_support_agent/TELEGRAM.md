# Telegram + Google ADK

This connects the retail customer-support ADK agent to a Telegram bot.

## 1. Create the Telegram bot

In Telegram, open **@BotFather** and create a bot with `/newbot`.

BotFather will give you a bot token.

Keep the token private. Do not put it directly in Python source code or commit it to Git.

## 2. Install the Telegram dependency

With uv:

```bash
uv add python-telegram-bot
```

Or, if you are using a generated agents-cli project, add it to that project's environment:

```bash
uv add python-telegram-bot
```

The current `python-telegram-bot` API uses `ApplicationBuilder`, async handler functions, and `MessageHandler` for ordinary messages.

## 3. Set the token

Windows PowerShell:

```powershell
$env:TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Windows CMD:

```cmd
set TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN
```

macOS/Linux:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

You also still need whatever Gemini/Google authentication your ADK project uses.

You can also try manually creating a file named `.env`. Then, edit that file and copy-paste the following lines below to set your environment variables:

```bash
GOOGLE_GENAI_USE_ENTERPRISE = 0
GOOGLE_API_KEY = paste_your_google_api_key_here
TELEGRAM_BOT_TOKEN = paste_your_telegram_bot_token_here
```

## 4. Run it

From this directory:

```bash
python telegram_bot.py
```

Or with uv:

```bash
uv run python telegram_bot.py
```

Then open your Telegram bot and send:

```text
Hi! What time are you open on Saturday?
```

The path is:

```text
Telegram
   ↓
python-telegram-bot
   ↓
telegram_bot.py
   ↓
Google ADK Runner
   ↓
customer_support_agent
   ↓
lookup_store_information()
   ↓
Gemini response
   ↓
Telegram
```

## 5. Why there is a Runner here

The ADK playground hides this part for you.

When an external application such as Telegram wants to invoke the agent, your program needs to call ADK programmatically.

The important pieces are:

```python
session_service = InMemorySessionService()

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)
```

Then each Telegram message becomes an ADK `Content` object:

```python
user_message = types.Content(
    role="user",
    parts=[types.Part.from_text(text=message)],
)
```

and is passed to:

```python
runner.run_async(...)
```

ADK yields events while the agent works. The adapter waits for the final response and sends that text back to Telegram.

## 6. Conversation history

The demo maps:

```text
Telegram chat ID
        ↓
ADK user ID
        ↓
ADK session ID
```

For example:

```text
Telegram chat 123456
→ user_id = "123456"
→ session_id = "telegram_123456"
```

That means several messages from the same Telegram chat can remain in the same ADK session.

`/reset` starts a fresh conversation.

### Important limitation

The example uses `InMemorySessionService`, so conversation history disappears when the Python process stops.

For a production bot, use a persistent ADK session service/database instead.

## 7. Polling vs webhook

This demo uses:

```python
application.run_polling()
```

because it is much easier for a live demonstration: you can run it on your laptop without exposing a public HTTPS endpoint.

For production deployment, a webhook is usually more appropriate. Telegram documents webhooks as an alternative update-delivery mechanism and recommends protecting the webhook URL with a secret path. 

## 8. What this demonstrates

This is useful as the next step after your basic ADK demo because it changes the interface without changing the agent.

First:

```text
Human
 ↓
ADK Playground
 ↓
Agent
```

Then:

```text
Human
 ↓
Telegram
 ↓
Telegram adapter
 ↓
ADK Runner
 ↓
Agent
```

The actual AI agent remains the same.

That makes a strong teaching point:

> ADK is the agent layer. Telegram is simply another application interface that invokes the agent.

## 9. Extending it to the other agents

Once this works, you can route Telegram messages to different specialist agents.

For example:

```text
                    Telegram
                       |
                       v
               Retail Coordinator
                 /    |    |    \
                /     |    |     \
               v      v    v      v
          Support  Price  Sentiment Inventory
```

The coordinator could decide which specialist should handle a request.

However, I recommend **not doing this in the first Telegram demo**. First prove that:

```text
Telegram → ADK → Tool → Response → Telegram
```

works end-to-end.

Then introduce multi-agent orchestration.