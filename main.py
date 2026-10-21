import logging

from fastapi import FastAPI, HTTPException
from google.genai.errors import APIError
from httpx import HTTPError
from mcp.shared.exceptions import MCPError
from pydantic import BaseModel

from customer_agent import AgentConfigurationError, AgentExecutionError, run_agent

app = FastAPI()
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str

@app.post("/api/agent/chat")
async def chat(request: ChatRequest):
    response = await run_agent(request.message)
    return {
        "success": True,
        "response": response
    }
