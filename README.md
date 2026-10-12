# Google ADK Retail Multi-Agent Demo

This demo is designed to be presented progressively.

## The intended progression

### Step 1 — Simple tool-using agent

Start with:

```bash
adk create simple_store_agent
```

Then replace the generated Python agent code with:

`01_simple_store_agent/agent.py`

The point is to show the smallest useful ADK concept:

```text
User
  ↓
Agent
  ↓
decides to call get_store_hours()
  ↓
ordinary Python function
  ↓
tool result
  ↓
Agent's natural-language answer
```

The function is deliberately boring. That is a feature for a first demo: the audience can see exactly where the "tool" is.

Current Google documentation also shows the same core pattern: an `Agent` receives ordinary Python functions in `tools=[...]`, with the function docstring helping describe when the tool should be used. 

## Step 2 — Customer-support agent

Create:

```bash
adk create customer_support_agent
```

Then use:

`02_customer_support_agent/agent.py`

The tool reads `retail_store.md`, a synthetic store profile. This gives you a practical demonstration of an agent consulting business information without introducing a vector database or RAG framework yet.

## Step 3 — Price-comparison agent

Create:

```bash
adk create price_comparison_agent
```

Then use:

`03_price_comparison_agent/agent.py`

This version uses ADK's built-in `google_search` grounding tool.

Example prompt:

> Compare our PHP 1,499 wireless keyboard and mouse set with similar products currently listed online in the Philippines.

The agent should distinguish exact-model matches from merely similar products and should identify sources.

### Important ADK design note

Google's current ADK documentation describes `google_search` as a model-internal grounding tool. It should not simply be mixed into the same agent with ordinary FunctionTools, because that can disable automatic function calling for the other tools. For a teaching demo, keeping this as a search-specialist agent is therefore a clean design. 

## Step 4 — Sentiment agent

Create:

```bash
adk create sentiment_analysis_agent
```

Then use:

`04_sentiment_analysis_agent/agent.py`

Example:

> "The delivery was late and the box was damaged, but the support staff were very helpful."

The Python tool produces a transparent baseline score. The LLM then explains it and proposes a customer-service action.

This is intentionally *not* presented as a production sentiment classifier. It demonstrates the distinction between deterministic business logic and an LLM interpreting that result.

## Step 5 — Inventory optimization agent

Create:

```bash
adk create inventory_optimization_agent
```

Then use:

`05_inventory_optimization_agent/agent.py`

Example:

> For the 1.7 L electric kettle, current stock is 20, average daily sales are 5, supplier lead time is 4 days, and safety stock is 10.

The Python function calculates:

```text
lead-time demand = daily sales × lead time
                 = 5 × 4
                 = 20

reorder point = lead-time demand + safety stock
              = 20 + 10
              = 30

suggested order = reorder point - current stock
                = 30 - 20
                = 10
```

The LLM explains the result rather than hiding the arithmetic inside a large abstraction.

## Suggested presentation sequence

1. Show the generated project.
2. Open `agent.py`.
3. Point at the tool function.
4. Point at `tools=[...]`.
5. Run the agent.
6. Ask a question that causes the tool to be called.
7. Show the tool result in the ADK UI/event trace.
8. Only then move to the next specialist agent.

The progression is:

```text
One agent
  ↓
One simple tool
  ↓
One business knowledge source
  ↓
One web-grounded specialist
  ↓
One analysis specialist
  ↓
One numerical decision-support specialist
```

This is intentionally more useful for a live demo than starting immediately with a complicated multi-agent orchestration graph.

## Running

Google's current Agents CLI documentation uses:

```bash
agents-cli create my-agent --prototype --yes
cd my-agent
agents-cli install
agents-cli playground
```

The local playground provides an interactive UI and supports hot reload. The generated Python structure centers on an `Agent` and its tools.

If your installed environment specifically provides the older/simple `adk create` workflow, you can keep using that command and replace the generated `agent.py` contents with the corresponding script here.

## Model selection

Each script uses:

```python
MODEL = os.getenv("DEMO_AGENT_MODEL", "gemini-3.8-flash")
```

This keeps the model choice visible at the top of the file. If your installed ADK/Gemini environment exposes a different model, set:

```bash
set DEMO_AGENT_MODEL=YOUR_MODEL
```

on Windows, or:

```bash
export DEMO_AGENT_MODEL=YOUR_MODEL
```

on macOS/Linux.

## What is deliberately NOT included yet

To keep the first demo explainable, these scripts do not introduce:

- complex agent classes
- decorators everywhere
- custom tool classes
- vector databases
- embeddings
- elaborate state management
- callbacks
- evaluation frameworks
- A2A networking
- production authentication
- production databases

Those can be added after the audience understands the basic agent → tool → result loop.

## Sources

Google's current ADK/Agents CLI documentation:
- https://google.github.io/agents-cli/
- https://google.github.io/adk-docs/
- https://adk.dev/tools/gemini-api/google-search/
