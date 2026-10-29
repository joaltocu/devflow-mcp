"""MCP Tools for DevFlow."""

from mcp.server import Server

from devflow.tools.development import register_development_tools
from devflow.tools.github_ops import register_github_tools
from devflow.tools.knowledge import register_knowledge_tools
from devflow.tools.context import register_context_tools


def register_tools(server: Server) -> None:
    """Register all MCP tools.

    Args:
        server: MCP server instance
    """
    register_development_tools(server)
    register_github_tools(server)
    register_knowledge_tools(server)
    register_context_tools(server)
