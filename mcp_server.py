"""MCP server exposing customer CRUD tools backed by the same SQL database as app.py.

Claude Desktop uses stdio (default):
    uv run python mcp_server.py

The Angular app uses Streamable HTTP at http://127.0.0.1:8000/mcp:
    uv run python mcp_server.py --http
"""

from __future__ import annotations

import argparse
import json
from typing import Any

import pyodbc
import uvicorn
from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from starlette.middleware.cors import CORSMiddleware
import re
import os

from dbHelper_sp import ItemDatabase

ANGULAR_ORIGINS = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

mcp = MCPServer("CustomerManagement", dependencies=["pyodbc"])
_db: ItemDatabase | None = None


def _get_db() -> ItemDatabase:
    global _db
    if _db is None:
        _db = ItemDatabase()
    return _db


def _format_result(data: Any) -> str:
    return json.dumps(data, indent=2)


def _format_error(ex: Exception) -> str:
    return json.dumps({"error": str(ex)}, indent=2)

# Create prompt
@mcp.prompt()
def system_prompt() -> str:
    """Instructions for customer agent"""
    script_dir = os.path.dirname(__file__)
    prompt_path = os.path.join(script_dir, "prompts", "system_instructions.md")
    with open(prompt_path, "r") as file:
        return file.read()

@mcp.tool()
def get_customers() -> str:
    """Get all customers from the TestCustomer table."""
    try:
        return _format_result(_get_db().getCustomers())
    except pyodbc.Error as ex:
        return _format_error(ex)


@mcp.tool()
def get_customer(customer_id: int) -> str:
    """Get one customer by numeric Id."""
    try:
        customer = _get_db().getCustomer(customer_id)
        if customer:
            return _format_result(customer)
        return _format_result({"message": "Customer not found"})
    except pyodbc.Error as ex:
        return _format_error(ex)


@mcp.tool()
def create_customer(first_name: str, last_name: str) -> str:
    """Create a new customer with FirstName and LastName."""
    try:
        result = _get_db().createCustomer(
            {"FirstName": first_name, "LastName": last_name}
        )
        return _format_result(result)
    except pyodbc.Error as ex:
        return _format_error(ex)


@mcp.tool()
def update_customer(customer_id: int, first_name: str, last_name: str) -> str:
    """Update an existing customer by Id."""
    try:
        result = _get_db().updateCustomer(
            customer_id,
            {"FirstName": first_name, "LastName": last_name},
        )
        return _format_result(result)
    except pyodbc.Error as ex:
        return _format_error(ex)


@mcp.tool()
def delete_customer(customer_id: int) -> str:
    """Delete a customer by Id."""
    try:
        result = _get_db().deleteCustomer(customer_id)
        return _format_result(result)
    except pyodbc.Error as ex:
        return _format_error(ex)


@mcp.tool()
def get_patientInfo() -> str:
    """Get all patients data details like patientStatus, patientType, IVRStatus, BedStatus."""
    try:
        return _format_result(_get_db().getPatientInfoDetails())
    except pyodbc.Error as ex:
        return _format_error(ex)


def create_http_app():
    """Starlette app for the Angular (browser) MCP client."""
    security = TransportSecuritySettings(
        allowed_hosts=["127.0.0.1", "127.0.0.1:*", "localhost", "localhost:*"],
        allowed_origins=ANGULAR_ORIGINS,
    )
    http_app = mcp.streamable_http_app(
        json_response=True,
        transport_security=security,
        host="127.0.0.1",
    )
    http_app.add_middleware(
        CORSMiddleware,
        allow_origins=ANGULAR_ORIGINS,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["Mcp-Session-Id"],
    )
    return http_app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CustomerManagement MCP server")
    parser.add_argument(
        "--http",
        action="store_true",
        help="Serve Streamable HTTP for the Angular client (default is stdio)",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.http:
        uvicorn.run(create_http_app(), host=args.host, port=args.port)
    else:
        mcp.run()
