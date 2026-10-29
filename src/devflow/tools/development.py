"""MCP tools for development workflows (code review, analysis)."""

import json
import uuid
from typing import Any, Dict

from mcp.server import Server
from mcp.types import Tool, TextContent

from devflow.database.models import Project, Review, ReviewIssue
from devflow.database.session import get_session

# Import existing review services (we'll reuse the logic you already built)
from devflow.reviewers.code_quality import CodeQualityReviewer
from devflow.reviewers.security import SecurityReviewer
from devflow.reviewers.architecture import ArchitectureReviewer
from devflow.reviewers.test_coverage import TestCoverageReviewer
from devflow.reviewers.synthesis import SynthesisAgent
from devflow.tools.diff_analyzer import DiffAnalyzer


def register_development_tools(server: Server) -> None:
    """Register development-related MCP tools.

    Args:
        server: MCP server instance
    """

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available development tools."""
        return [
            Tool(
                name="development/review_code",
                description="Run comprehensive code review (quality, security, architecture, coverage)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Project UUID",
                        },
                        "diff": {
                            "type": "string",
                            "description": "Git diff output to review",
                        },
                        "review_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Types of reviews to run",
                            "default": ["code_quality", "security", "architecture", "coverage"],
                        },
                        "context": {
                            "type": "object",
                            "description": "Additional context (branch, author, etc.)",
                        },
                    },
                    "required": ["project_id", "diff"],
                },
            ),
            Tool(
                name="development/analyze_diff",
                description="Analyze git diff to extract structured information about changes",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "diff": {
                            "type": "string",
                            "description": "Git diff output",
                        },
                    },
                    "required": ["diff"],
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
        if name == "development/review_code":
            return await review_code(arguments)
        elif name == "development/analyze_diff":
            return await analyze_diff(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")


async def review_code(arguments: Dict[str, Any]) -> list[TextContent]:
    """Run code review.

    Args:
        arguments: Tool arguments

    Returns:
        Review results
    """
    project_id = uuid.UUID(arguments["project_id"])
    diff = arguments["diff"]
    review_types = arguments.get("review_types", [
        "code_quality",
        "security",
        "architecture",
        "coverage",
    ])
    context = arguments.get("context", {})

    # Analyze diff
    analyzer = DiffAnalyzer(diff)
    changes = analyzer.to_dict()

    # Initialize reviewers
    reviewers = []
    if "code_quality" in review_types:
        reviewers.append(CodeQualityReviewer())
    if "security" in review_types:
        reviewers.append(SecurityReviewer())
    if "architecture" in review_types:
        reviewers.append(ArchitectureReviewer())
    if "coverage" in review_types:
        reviewers.append(TestCoverageReviewer())

    # Run reviews
    review_results = []
    for reviewer in reviewers:
        result = await reviewer.review(changes, context)
        review_results.append(result)

    # Synthesize
    synthesis_agent = SynthesisAgent()
    synthesized = await synthesis_agent.synthesize(review_results)

    # Save to database
    async with get_session() as session:
        # Save individual reviews
        for result in review_results:
            review = Review(
                project_id=project_id,
                type=result.reviewer_name.lower().replace(" ", "_"),
                diff=diff,
                context=context,
                result=result.to_dict(),
                agent_type="devflow-mcp",
            )
            session.add(review)

            # Save issues
            for issue in result.issues:
                review_issue = ReviewIssue(
                    review_id=review.id,
                    severity=issue.severity.value,
                    category=issue.category,
                    file_path=issue.file,
                    line_number=issue.line,
                    message=issue.message,
                    suggestion=issue.suggestion,
                )
                session.add(review_issue)

        await session.commit()

    # Return synthesized result
    return [
        TextContent(
            type="text",
            text=json.dumps(
                {
                    "success": True,
                    "reviews": [r.to_dict() for r in review_results],
                    "synthesized": synthesized.to_dict(),
                    "analysis": changes,
                },
                indent=2,
            ),
        )
    ]


async def analyze_diff(arguments: Dict[str, Any]) -> list[TextContent]:
    """Analyze git diff.

    Args:
        arguments: Tool arguments

    Returns:
        Diff analysis
    """
    diff = arguments["diff"]

    analyzer = DiffAnalyzer(diff)
    analysis = analyzer.to_dict()

    return [
        TextContent(
            type="text",
            text=json.dumps(analysis, indent=2),
        )
    ]
