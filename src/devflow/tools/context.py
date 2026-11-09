"""MCP tools for project context."""

import json
import uuid
from typing import Any, Dict

from mcp.server import Server
from mcp.types import Tool, TextContent

from devflow.database.models import Project
from devflow.database.session import get_session


def register_context_tools(server: Server) -> None:
    """Register context-related MCP tools.

    Args:
        server: MCP server instance
    """

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available context tools."""
        return [
            Tool(
                name="context/create_project",
                description="Create a new project in DevFlow database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Project name",
                        },
                        "path": {
                            "type": "string",
                            "description": "Absolute path to project directory",
                        },
                        "language": {
                            "type": "string",
                            "description": "Primary programming language (e.g., python, rust, javascript)",
                        },
                        "framework": {
                            "type": "string",
                            "description": "Framework if applicable (e.g., fastapi, react, actix)",
                        },
                        "repository_url": {
                            "type": "string",
                            "description": "Git repository URL",
                        },
                        "extra_metadata": {
                            "type": "object",
                            "description": "Additional project metadata",
                        },
                    },
                    "required": ["name", "path"],
                },
            ),
            Tool(
                name="context/list_projects",
                description="List all projects in DevFlow database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of projects to return",
                            "default": 100,
                        },
                        "offset": {
                            "type": "number",
                            "description": "Number of projects to skip",
                            "default": 0,
                        },
                    },
                },
            ),
            Tool(
                name="context/get_project",
                description="Get detailed information about a specific project",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Project UUID",
                        },
                    },
                    "required": ["project_id"],
                },
            ),
            Tool(
                name="context/update_project",
                description="Update project information",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Project UUID",
                        },
                        "name": {
                            "type": "string",
                            "description": "Project name",
                        },
                        "path": {
                            "type": "string",
                            "description": "Absolute path to project directory",
                        },
                        "language": {
                            "type": "string",
                            "description": "Primary programming language",
                        },
                        "framework": {
                            "type": "string",
                            "description": "Framework if applicable",
                        },
                        "repository_url": {
                            "type": "string",
                            "description": "Git repository URL",
                        },
                        "extra_metadata": {
                            "type": "object",
                            "description": "Additional project metadata",
                        },
                    },
                    "required": ["project_id"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
        """Handle tool calls.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result
        """
        if name == "context/create_project":
            return await create_project(arguments)
        elif name == "context/list_projects":
            return await list_projects(arguments)
        elif name == "context/get_project":
            return await get_project(arguments)
        elif name == "context/update_project":
            return await update_project(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")


async def create_project(arguments: Dict[str, Any]) -> list[TextContent]:
    """Create a new project.

    Args:
        arguments: Tool arguments

    Returns:
        Project creation result
    """
    name = arguments["name"]
    path = arguments["path"]
    language = arguments.get("language")
    framework = arguments.get("framework")
    repository_url = arguments.get("repository_url")
    extra_metadata = arguments.get("extra_metadata")

    async with get_session() as session:
        # Create project
        project = Project(
            name=name,
            path=path,
            language=language,
            framework=framework,
            repository_url=repository_url,
            extra_metadata=extra_metadata,
        )
        session.add(project)
        await session.commit()
        await session.refresh(project)

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "success": True,
                        "project": {
                            "id": str(project.id),
                            "name": project.name,
                            "path": project.path,
                            "language": project.language,
                            "framework": project.framework,
                            "repository_url": project.repository_url,
                            "extra_metadata": project.extra_metadata,
                            "created_at": project.created_at.isoformat(),
                        },
                        "message": f"Project '{name}' created successfully",
                    },
                    indent=2,
                ),
            )
        ]


async def list_projects(arguments: Dict[str, Any]) -> list[TextContent]:
    """List all projects.

    Args:
        arguments: Tool arguments

    Returns:
        List of projects
    """
    from sqlalchemy import select

    limit = arguments.get("limit", 100)
    offset = arguments.get("offset", 0)

    async with get_session() as session:
        # Query projects
        stmt = select(Project).limit(limit).offset(offset)
        result = await session.execute(stmt)
        projects = result.scalars().all()

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "success": True,
                        "count": len(projects),
                        "projects": [
                            {
                                "id": str(p.id),
                                "name": p.name,
                                "path": p.path,
                                "language": p.language,
                                "framework": p.framework,
                                "repository_url": p.repository_url,
                                "created_at": p.created_at.isoformat(),
                            }
                            for p in projects
                        ],
                    },
                    indent=2,
                ),
            )
        ]


async def get_project(arguments: Dict[str, Any]) -> list[TextContent]:
    """Get project details.

    Args:
        arguments: Tool arguments

    Returns:
        Project details
    """
    from sqlalchemy import select

    project_id = uuid.UUID(arguments["project_id"])

    async with get_session() as session:
        # Query project
        stmt = select(Project).where(Project.id == project_id)
        result = await session.execute(stmt)
        project = result.scalar_one_or_none()

        if not project:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "success": False,
                            "error": f"Project {project_id} not found",
                        },
                        indent=2,
                    ),
                )
            ]

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "success": True,
                        "project": {
                            "id": str(project.id),
                            "name": project.name,
                            "path": project.path,
                            "language": project.language,
                            "framework": project.framework,
                            "repository_url": project.repository_url,
                            "extra_metadata": project.extra_metadata,
                            "created_at": project.created_at.isoformat(),
                            "updated_at": project.updated_at.isoformat(),
                        },
                    },
                    indent=2,
                ),
            )
        ]


async def update_project(arguments: Dict[str, Any]) -> list[TextContent]:
    """Update project information.

    Args:
        arguments: Tool arguments

    Returns:
        Update result
    """
    from sqlalchemy import select

    project_id = uuid.UUID(arguments["project_id"])

    async with get_session() as session:
        # Get project
        stmt = select(Project).where(Project.id == project_id)
        result = await session.execute(stmt)
        project = result.scalar_one_or_none()

        if not project:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "success": False,
                            "error": f"Project {project_id} not found",
                        },
                        indent=2,
                    ),
                )
            ]

        # Update fields
        if "name" in arguments:
            project.name = arguments["name"]
        if "path" in arguments:
            project.path = arguments["path"]
        if "language" in arguments:
            project.language = arguments["language"]
        if "framework" in arguments:
            project.framework = arguments["framework"]
        if "repository_url" in arguments:
            project.repository_url = arguments["repository_url"]
        if "extra_metadata" in arguments:
            project.extra_metadata = arguments["extra_metadata"]

        await session.commit()
        await session.refresh(project)

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "success": True,
                        "project": {
                            "id": str(project.id),
                            "name": project.name,
                            "path": project.path,
                            "language": project.language,
                            "framework": project.framework,
                            "repository_url": project.repository_url,
                            "extra_metadata": project.extra_metadata,
                            "updated_at": project.updated_at.isoformat(),
                        },
                        "message": f"Project '{project.name}' updated successfully",
                    },
                    indent=2,
                ),
            )
        ]
