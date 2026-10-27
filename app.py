# FastAPI wrapper: exposes the ReAct agent in main.py as an HTTP API.

import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from main import run_agent

app = FastAPI(title="ReAct Agent API")

# Uvicorn's logger, so our messages show up in the same server output.
logger = logging.getLogger("uvicorn.error")


# Pydantic models describe the JSON shape going in and coming out.
# FastAPI uses them to parse the request body and build the response.
class AskRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)    # "   " becomes "" and fails min_length

    # min_length rejects empty questions; max_length caps cost on a public endpoint
    question: str = Field(min_length=1, max_length=1000)

class AskResponse(BaseModel):
    answer: str


# FastAPI's default for a bad request body is a 422 with a detailed error list.
# Replace it with a plain 400 and one readable message.
@app.exception_handler(RequestValidationError)
async def handle_bad_request(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": 'Send JSON like {"question": "..."} with a non-empty question (max 1000 characters).'},
    )


@app.get("/health")
def health():
    # Cheap check that the server is up. Does not call Claude.
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    try:
        answer = run_agent(request.question)
    except Exception:
        # Full details go to the server log only; the caller gets a generic message,
        # so internals (stack traces, upstream error bodies) never leak in a response.
        logger.exception("Agent failed")
        return JSONResponse(status_code=500, content={"error": "The agent failed to answer. Please try again."})
    return {"answer": answer}
