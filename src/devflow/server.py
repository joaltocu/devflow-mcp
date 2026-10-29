"""DevFlow MCP Server - Holistic development infrastructure.

This MCP server provides tools and resources for:
- Code review (quality, security, architecture, coverage)
- GitHub integration (PR management)
- Knowledge management (patterns, learnings, decisions)
- Project context (metadata, ADRs, architecture)
"""

import asyncio
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server

from devflow.database.session import init_db
from devflow.resources import register_resources
from devflow.tools import register_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Run the DevFlow MCP server."""
    logger.info("Starting DevFlow MCP Server...")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Create MCP server
    server = Server("devflow-mcp")

    logger.info("Registering MCP tools...")
    register_tools(server)

    logger.info("Registering MCP resources...")
    register_resources(server)

    logger.info("DevFlow MCP Server ready")
    logger.info("Serving over stdio...")

    # Run server over stdio
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def run() -> None:
    """Entry point for the server."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
