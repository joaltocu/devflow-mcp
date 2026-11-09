"""MCP Tools for DevFlow - Centralized Registration.

This module provides a centralized tool registration system that combines
tools from all sub-modules into a single MCP server instance.
"""

from typing import Any, Dict
from mcp.server import Server
from mcp.types import Tool, TextContent

# Import tool definitions
from devflow.tools import development, context


def register_tools(server: Server) -> None:
    """Register all MCP tools with centralized handlers.

    This function creates a single list_tools() handler and a single call_tool()
    handler that combine tools from all modules.

    Args:
        server: MCP server instance
    """

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available tools from all modules."""
        tools = []

        # Development tools
        tools.extend(development.get_tool_definitions())

        # Context tools
        tools.extend(context.get_tool_definitions())

        # GitHub tools (not implemented yet)
        # tools.extend(github_ops.get_tool_definitions())

        # Knowledge tools (not implemented yet)
        # tools.extend(knowledge.get_tool_definitions())

        return tools

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
        """Handle tool calls by routing to the appropriate module."""

        # Route to development tools
        if name.startswith("development/"):
            return await development.handle_tool_call(name, arguments)

        # Route to context tools
        elif name.startswith("context/"):
            return await context.handle_tool_call(name, arguments)

        # Route to GitHub tools (not implemented yet)
        elif name.startswith("github/"):
            raise ValueError(f"GitHub tools not implemented yet: {name}")

        # Route to knowledge tools (not implemented yet)
        elif name.startswith("knowledge/"):
            raise ValueError(f"Knowledge tools not implemented yet: {name}")

        else:
            raise ValueError(f"Unknown tool: {name}")
