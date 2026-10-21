
import os
import sys
import logging
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult
from mcp.shared.exceptions import MCPError

# --------------------------------------------------
# Configuration
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent

load_dotenv(PROJECT_DIR / ".env")
load_dotenv(PROJECT_DIR.parent / ".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_TOOL_TURNS = 8

INSTRUCTIONS = """
You are a Customer Support AI Agent.

Use available MCP tools to Read/Add/Edit/Update/Delete customer information.
Do not guess customer information.
If required information is missing, ask the user.
"""

MCP_SERVER = StdioServerParameters(
    command=sys.executable,
    args=[str(PROJECT_DIR / "mcp_server.py")],
    cwd=str(PROJECT_DIR),
)

_client = None

class AgentConfigurationError(RuntimeError):
    pass

class AgentExecutionError(RuntimeError):
    pass

# --------------------------------------------------
# Gemini Client
# --------------------------------------------------

def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise AgentConfigurationError(
                "GEMINI_API_KEY is missing from .env"
            )
        _client = genai.Client(api_key=api_key)
    return _client

# --------------------------------------------------
# MCP Tool Result
# --------------------------------------------------

def _tool_result_payload(result: CallToolResult):

    return {
        "is_error": bool(result.is_error),
        "content": [
            item.model_dump(
                mode="json",
                exclude_none=True
            )
            for item in result.content
        ],
    }

# --------------------------------------------------
# AI Agent
# --------------------------------------------------

async def run_agent(user_message: str) -> str:
    if not user_message or not user_message.strip():
        raise ValueError("User message cannot be empty.")
    #client = _get_client()
    try:
        async with stdio_client(MCP_SERVER) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize MCP connection
                await session.initialize()
                logger.info("MCP server initialized")
                # Discover MCP tools
                tool_list = await session.list_tools()
                if not tool_list.tools:
                    raise AgentExecutionError(
                        "No MCP tools are available."
                    )
                logger.info(
                    "Available MCP tools: %s",
                    [tool.name for tool in tool_list.tools]
                )
                # Convert MCP tools to Gemini declarations
                declarations = []

                for tool in tool_list.tools:
                    declarations.append(
                        types.FunctionDeclaration(
                            name=tool.name,
                            description=tool.description or "",
                            parameters_json_schema=tool.input_schema,
                        )
                    )

                # Gemini configuration
                config = types.GenerateContentConfig(
                    temperature=0,
                    system_instruction=INSTRUCTIONS,
                    tools=[
                        types.Tool(
                            function_declarations=declarations
                        )
                    ],
                )

                contents = [user_message]
                # Gemini tool calling loop
                for turn in range(MAX_TOOL_TURNS):
                    logger.info(
                        "Gemini request - turn %s",
                        turn + 1
                    )
                    client = genai.Client()
                    response = client.models.generate_content(
                        model="gemini-3.1-flash-lite",
                        contents=contents,
                        config=config,
                    )
                    if not response.candidates:
                        raise AgentExecutionError(
                            "Gemini returned no candidates."
                        )
                    model_content = response.candidates[0].content
                    if not model_content or not model_content.parts:
                        raise AgentExecutionError(
                            "Gemini returned empty content."
                        )
                    function_calls = [
                        part.function_call
                        for part in model_content.parts
                        if part.function_call is not None
                    ]

                    # No more tool calls: return final response
                    if not function_calls:
                        if not response.text:
                            raise AgentExecutionError(
                                "Gemini returned an empty response."
                            )
                        return response.text

                    # Preserve Gemini's function-call message
                    contents.append(model_content)
                    function_responses = []
                    for function_call in function_calls:
                        tool_name = function_call.name
                        if not tool_name:
                            raise AgentExecutionError(
                                "Gemini returned an invalid tool name."
                            )
                        logger.info(
                            "Executing MCP tool: %s",
                            tool_name
                        )

                        try:
                            result = await session.call_tool(
                                tool_name,
                                arguments=dict(
                                    function_call.args or {}
                                ),
                            )
                            payload = _tool_result_payload(result)

                        except MCPError as ex:
                            logger.exception(
                                "MCP tool execution failed: %s",
                                tool_name
                            )
                            payload = {
                                "is_error": True,
                                "error": str(ex),
                            }
                        function_responses.append(
                            types.Part.from_function_response(
                                name=tool_name,
                                response=payload,
                            )
                        )

                    # Send MCP results back to Gemini
                    contents.append(
                        types.Content(
                            role="tool",
                            parts=function_responses,
                        )
                    )

                raise AgentExecutionError(
                    "Maximum Gemini tool-call turns exceeded."
                )
    except (AgentConfigurationError, AgentExecutionError):
        raise

    except Exception as ex:
        logger.exception("Customer Agent execution failed")
        raise AgentExecutionError(
            f"Agent execution failed: {str(ex)}"
        ) from ex
