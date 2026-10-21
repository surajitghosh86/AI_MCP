import logging
import sys
from pathlib import Path

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerStdio
from fastapi import FastAPI, HTTPException
from openai import RateLimitError
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent
MCP_SERVER_PATH = PROJECT_DIR / "mcp_server.py"

app = FastAPI(
    title="AI Agent REST API", description="Python AI Agent API", version="1.0.0"
)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    question: str
    answer: str


@app.get("/test")
async def test(request: ChatRequest):
    print(request.question)
    return {"message": "AI Agent API is running"}


@app.post("/chat", response_model=ChatResponse)
async def main(request: ChatRequest) -> ChatResponse:
    try:
        async with MCPServerStdio(
            name="Customer MCP Server",
            params={
                "command": sys.executable,
                "args": [str(MCP_SERVER_PATH)],
                "cwd": str(PROJECT_DIR),
            },
        ) as server:
            trace_id = gen_trace_id()
            with trace(workflow_name="Customer MCP Agent Example", trace_id=trace_id):
                answer = await run(server, request.question)
    except RateLimitError as ex:
        logger.exception("OpenAI API rejected the chat request due to rate or quota limits")
        raise HTTPException(
            status_code=503,
            detail=(
                "The OpenAI API is currently unavailable due to rate or quota limits. "
                "Check the configured API account's usage and billing, then retry."
            ),
        ) from ex

    return ChatResponse(question=request.question, answer=answer)


async def run(mcp_server: MCPServer, user_input: str) -> str:
    print(f"User input: {user_input}")
    prompt_result = await mcp_server.get_prompt("system_prompt")
    instructions = prompt_result.messages[0].content.text
    print(f"System instructions: {instructions}")
    
    agent = Agent(
        name="Customer Agent",
        instructions=instructions,
        mcp_servers=[mcp_server],
    )
    result = await Runner.run(agent, input=user_input)
    return result.final_output

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
