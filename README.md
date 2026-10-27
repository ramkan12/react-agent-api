# ReAct Agent API

A from-scratch ReAct agent that uses Claude and a Python tool, served as a FastAPI endpoint, containerized with Docker, and deployed on Render.

**Live:** https://react-agent-api.onrender.com (interactive docs at [`/docs`](https://react-agent-api.onrender.com/docs))

> Hosted on Render's free tier, which sleeps after inactivity. The first request may take up to a minute while it wakes up.

## Try it

```bash
curl -X POST https://react-agent-api.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the weather in Tokyo?"}'
```

```json
{"answer": "The current weather in Tokyo is **72°F (22°C)** and **sunny**! It sounds like a beautiful day in Tokyo. 🌞 Perfect weather for outdoor activities or sightseeing!"}
```

## What it demonstrates

- **A ReAct loop written by hand:** Claude reasons, requests a tool call, sees the result, and continues until it can answer. No agent frameworks.
- **Tool use with the Anthropic API:** a tool defined with a JSON input schema, with Claude choosing when to call it and with what arguments.
- **A safety cap:** the loop stops after 5 turns, so it can never run forever.
- **The agent as a deployed API:** a FastAPI service with request validation and clean JSON errors.
- **Containerized deployment:** a Docker image run on Render, with the API key supplied only through the environment.

## How it works

1. A client sends `POST /ask` with a question.
2. The question is sent to Claude along with a description of the `get_weather` tool.
3. If Claude replies that it wants to use the tool, the code runs the matching Python function with the arguments Claude chose and sends the result back, tied to the original request by its ID.
4. Claude sees the result and either asks for another tool call or gives a final answer. The full conversation is resent on every turn.
5. The final answer is returned as `{"answer": "..."}`. If Claude has not answered within 5 turns, the loop stops.

`get_weather` is a stub that returns fixed data, since the point is the agent mechanics rather than a weather API.

## API

| Endpoint | Description |
|---|---|
| `POST /ask` | Body `{"question": "..."}` (1 to 1000 characters). Returns `{"answer": "..."}`. |
| `GET /health` | Returns `{"status": "ok"}` for uptime checks. |

Errors return JSON, never a stack trace:

- `400` for a missing, empty, or too-long question
- `500` with a generic message if the agent fails (details are logged server-side only)

## Project structure

| File | Purpose |
|---|---|
| `main.py` | The agent: tool definition and the ReAct loop in `run_agent(question)` |
| `app.py` | FastAPI app: endpoints, validation, and error handling |
| `Dockerfile` | Slim Python image that runs the app with uvicorn on `$PORT` |
| `requirements.txt` | Pinned dependencies |

## Run locally

Create a `.env` file with your key (it is git-ignored and excluded from the Docker image):

```
ANTHROPIC_API_KEY=your-key-here
```

With Python:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

With Docker:

```bash
docker build -t react-agent .
docker run --rm -p 8000:8000 --env-file .env react-agent
```

Then call `http://localhost:8000/ask` with the curl command above.

## Tech

Python, Anthropic API (Claude Sonnet 4.6), FastAPI, Docker, Render
