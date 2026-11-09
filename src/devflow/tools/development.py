"""MCP tools for development workflows (code review, analysis)."""

import json
import os
import uuid
from pathlib import Path
from typing import Any, Dict

from mcp.server import Server
from mcp.types import Tool, TextContent

from devflow.database.models import Project, Review, ReviewIssue
from devflow.database.session import get_session

# Import review services
from devflow.reviewers.code_quality import CodeQualityReviewer
from devflow.reviewers.security import SecurityReviewer
from devflow.reviewers.architecture import ArchitectureReviewer
from devflow.reviewers.test_coverage import TestCoverageReviewer
from devflow.reviewers.synthesis import SynthesisAgent
from devflow.tools.diff_analyzer import DiffAnalyzer

# Import Claude Code reviewers (no API key needed!)
from devflow.reviewers.claude_code_reviewer import (
    CodeQualityClaudeCodeReviewer,
    SecurityClaudeCodeReviewer,
    ArchitectureClaudeCodeReviewer,
    TestCoverageClaudeCodeReviewer,
)

# Import Generic LLM reviewers (OpenAI-compatible APIs)
from devflow.reviewers.generic_llm_reviewer import (
    CodeQualityGenericReviewer,
    SecurityGenericReviewer,
    ArchitectureGenericReviewer,
    TestCoverageGenericReviewer,
)


def get_tool_definitions() -> list[Tool]:
    """Get development tool definitions.

    Returns:
        List of Tool objects
    """
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


async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle development tool calls.

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
        raise ValueError(f"Unknown development tool: {name}")


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

    # Determine which reviewer backend to use
    # Priority: LLM_API_KEY > ANTHROPIC_API_KEY > Claude Code
    llm_api_key = os.getenv("LLM_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    working_dir = Path(context.get("working_dir", "/tmp/devflow-review"))

    # Detect backend
    if llm_api_key:
        backend = "generic_llm"
        llm_model = os.getenv("LLM_MODEL", "gpt-4")
    elif anthropic_api_key:
        backend = "anthropic"
    else:
        backend = "claude_code"

    # Initialize reviewers based on backend
    reviewers = []

    if backend == "generic_llm":
        # Use Generic LLM reviewers (OpenAI-compatible API)
        if "code_quality" in review_types:
            reviewers.append(CodeQualityGenericReviewer(llm_model))
        if "security" in review_types:
            reviewers.append(SecurityGenericReviewer(llm_model))
        if "architecture" in review_types:
            reviewers.append(ArchitectureGenericReviewer(llm_model))
        if "coverage" in review_types:
            reviewers.append(TestCoverageGenericReviewer(llm_model))

    elif backend == "anthropic":
        # Use Anthropic API reviewers
        if "code_quality" in review_types:
            reviewers.append(CodeQualityReviewer())
        if "security" in review_types:
            reviewers.append(SecurityReviewer())
        if "architecture" in review_types:
            reviewers.append(ArchitectureReviewer())
        if "coverage" in review_types:
            reviewers.append(TestCoverageReviewer())

    else:  # claude_code
        # Use Claude Code reviewers (no API key required)
        if "code_quality" in review_types:
            reviewers.append(CodeQualityClaudeCodeReviewer(working_dir))
        if "security" in review_types:
            reviewers.append(SecurityClaudeCodeReviewer(working_dir))
        if "architecture" in review_types:
            reviewers.append(ArchitectureClaudeCodeReviewer(working_dir))
        if "coverage" in review_types:
            reviewers.append(TestCoverageClaudeCodeReviewer(working_dir))

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
