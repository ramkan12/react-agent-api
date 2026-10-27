# ReAct Agent from Scratch

A minimal tool-using agent that lets Claude decide when to call a Python function, runs it, and feeds the result back until Claude gives a final answer.

## What it demonstrates

- **The ReAct loop:** Claude reasons, requests an action (a tool call), observes the result, and continues until it can answer.
- **Tool calling with the Anthropic API:** defining a tool with a JSON input schema and letting the model choose the tool and its arguments.
- **Conversation state management:** the full message history, including the assistant's tool requests and the matching `tool_result` blocks, is sent back on every turn.
- **A safety cap:** the loop is limited to 5 turns so it can never run forever.

## How it works

The user's question is sent to Claude along with a description of the available `get_weather` tool. If Claude's response has `stop_reason == "tool_use"`, the code finds each `tool_use` block, looks up the matching Python function by name, and calls it with the arguments Claude chose. Each result is wrapped in a `tool_result` block tied to the original request by its `tool_use_id`, then appended to the conversation. The updated history goes back to Claude, and the loop repeats until Claude returns `end_turn` with a final text answer or the turn cap is reached.

The agent is built up in four stages. Each file builds on the previous one and adds a single step:

| File | Step |
|---|---|
| `stage1.py` | Make one API call work, to prove the connection before adding anything else |
| `stage2.py` | Give Claude a tool it can choose to use |
| `stage3.py` | Read the tool request Claude sends back: the tool name, arguments, and ID |
| `stage4.py` | The actual loop: run the tool, return the result, repeat until Claude answers |

`get_weather` is a stub that returns fixed data, since the point is the agent mechanics rather than the weather API.

## Built from scratch

No agent frameworks like LangChain are used, on purpose. The loop, tool dispatch, and message handling are written by hand against the Anthropic SDK, one step at a time, to understand the mechanics that frameworks abstract away.

## Run it

```bash
pip install anthropic python-dotenv
```

Create a `.env` file in the project folder with your own key:

```
ANTHROPIC_API_KEY=your-key-here
```

Then run the full agent (or any earlier stage):

```bash
python stage4.py
```

## Tech used

Python, Anthropic API (Claude Sonnet 4.6), python-dotenv
