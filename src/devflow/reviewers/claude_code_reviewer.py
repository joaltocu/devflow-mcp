"""Base reviewer using Claude Code instead of Anthropic API."""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict

from devflow.agents.claude_code import ClaudeCodeAgent
from devflow.reviewers.base import BaseReviewer, ReviewIssue, ReviewResult, Severity


class ClaudeCodeReviewer(BaseReviewer):
    """Base reviewer that uses Claude Code CLI instead of Anthropic API.

    This eliminates the need for ANTHROPIC_API_KEY by delegating reviews
    to Claude Code, which the user already has access to.
    """

    def __init__(self, name: str, system_prompt: str, working_dir: Path | None = None) -> None:
        """Initialize Claude Code reviewer.

        Args:
            name: Reviewer name
            system_prompt: System prompt for the reviewer
            working_dir: Working directory (uses temp dir if not provided)
        """
        super().__init__(name=name)
        self.system_prompt = system_prompt
        self.working_dir = working_dir or Path(tempfile.mkdtemp(prefix="devflow-review-"))
        self.agent = ClaudeCodeAgent(self.working_dir)

    async def review(
        self, changes: Dict[str, Any], context: Dict[str, Any]
    ) -> ReviewResult:
        """Perform review using Claude Code.

        Args:
            changes: Dictionary containing code changes
            context: Review context

        Returns:
            Review result
        """
        result = self.create_result()

        # Build review task
        diff = changes.get("diff", "")
        if not diff:
            result.summary = "No changes to review"
            return result

        # Create review task for Claude Code
        review_task = self._build_review_task(diff, changes, context)

        # Save diff to a file for Claude to read
        diff_file = self.working_dir / ".devflow" / "current_diff.txt"
        diff_file.parent.mkdir(exist_ok=True)
        diff_file.write_text(diff)

        # Run Claude Code with the review task
        claude_result = await self.agent.run(review_task)

        if not claude_result.success:
            result.summary = f"Review failed: {claude_result.error}"
            return result

        # Parse Claude's response from the log
        try:
            # Claude Code will output the review as JSON
            # We need to extract it from the log
            review_data = self._parse_review_output(claude_result.log)

            # Convert to ReviewIssue objects
            for issue_data in review_data.get("issues", []):
                issue = ReviewIssue(
                    severity=Severity[issue_data.get("severity", "INFO").upper()],
                    file=issue_data.get("file", ""),
                    line=issue_data.get("line"),
                    message=issue_data.get("message", ""),
                    suggestion=issue_data.get("suggestion"),
                    category=issue_data.get("category", ""),
                )
                result.issues.append(issue)

            result.summary = review_data.get("summary", "Review completed")
            result.passed = len([i for i in result.issues if i.severity in [Severity.CRITICAL, Severity.HIGH]]) == 0

        except Exception as e:
            result.summary = f"Failed to parse review output: {str(e)}\n\nRaw output:\n{claude_result.log}"

        return result

    def _build_review_task(
        self, diff: str, changes: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        """Build the review task for Claude Code.

        Args:
            diff: Git diff to review
            changes: Change information
            context: Review context

        Returns:
            Task description for Claude Code
        """
        task = f"""# Code Review Task

{self.system_prompt}

## Your Task

Review the code changes in `.devflow/current_diff.txt` and provide a structured review.

## Context

- Language: {context.get('language', 'Unknown')}
- Framework: {context.get('framework', 'Unknown')}
- Files changed: {len(changes.get('files', []))}

## Output Format

You MUST output your review as a JSON object with this exact structure:

```json
{{
  "summary": "Brief overall summary of the review",
  "issues": [
    {{
      "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFO",
      "file": "path/to/file.py",
      "line": 42,
      "message": "Description of the issue",
      "suggestion": "Suggested fix (optional)",
      "category": "Category name"
    }}
  ]
}}
```

## Important

1. Read the diff from `.devflow/current_diff.txt`
2. Analyze according to the review criteria above
3. Output ONLY the JSON object, no other text
4. Be constructive and specific

Begin your review now.
"""
        return task

    def _parse_review_output(self, output: str) -> Dict[str, Any]:
        """Parse Claude Code's output to extract review JSON.

        Args:
            output: Raw output from Claude Code

        Returns:
            Parsed review data
        """
        # Try to find JSON in the output
        # Look for ```json blocks or raw JSON
        lines = output.split('\n')
        json_lines = []
        in_json_block = False

        for line in lines:
            if '```json' in line.lower():
                in_json_block = True
                continue
            elif '```' in line and in_json_block:
                break
            elif in_json_block or (line.strip().startswith('{') and not json_lines):
                json_lines.append(line)

        if json_lines:
            json_str = '\n'.join(json_lines)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # Fallback: try to parse the whole output as JSON
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            # If we can't parse, return a default structure
            return {
                "summary": "Review completed (unable to parse structured output)",
                "issues": []
            }


class CodeQualityClaudeCodeReviewer(ClaudeCodeReviewer):
    """Code quality reviewer using Claude Code."""

    SYSTEM_PROMPT = """You are an expert code quality reviewer. Review code changes for:
- Style consistency and best practices
- Naming conventions (variables, functions, classes)
- Code organization and structure
- Documentation (comments, docstrings)
- Maintainability and readability
- DRY (Don't Repeat Yourself) principle
- SOLID principles
- Appropriate error handling

Be constructive and provide specific, actionable suggestions."""

    def __init__(self, working_dir: Path | None = None) -> None:
        """Initialize code quality reviewer."""
        super().__init__(
            name="Code Quality (Claude Code)",
            system_prompt=self.SYSTEM_PROMPT,
            working_dir=working_dir
        )


class SecurityClaudeCodeReviewer(ClaudeCodeReviewer):
    """Security reviewer using Claude Code."""

    SYSTEM_PROMPT = """You are a security expert. Review code changes for:
- SQL injection vulnerabilities
- XSS (Cross-Site Scripting) vulnerabilities
- Authentication and authorization issues
- Hardcoded secrets or credentials
- Insecure dependencies
- OWASP Top 10 vulnerabilities
- Input validation issues
- Cryptography misuse

Be thorough and flag any potential security concerns."""

    def __init__(self, working_dir: Path | None = None) -> None:
        """Initialize security reviewer."""
        super().__init__(
            name="Security (Claude Code)",
            system_prompt=self.SYSTEM_PROMPT,
            working_dir=working_dir
        )


class ArchitectureClaudeCodeReviewer(ClaudeCodeReviewer):
    """Architecture reviewer using Claude Code."""

    SYSTEM_PROMPT = """You are a software architect. Review code changes for:
- Design pattern adherence
- Architecture Decision Record (ADR) compliance
- Module boundaries and separation of concerns
- Dependency direction (avoid circular dependencies)
- API design consistency
- Scalability considerations
- Technical debt introduction

Ensure changes align with project architecture."""

    def __init__(self, working_dir: Path | None = None) -> None:
        """Initialize architecture reviewer."""
        super().__init__(
            name="Architecture (Claude Code)",
            system_prompt=self.SYSTEM_PROMPT,
            working_dir=working_dir
        )


class TestCoverageClaudeCodeReviewer(ClaudeCodeReviewer):
    """Test coverage reviewer using Claude Code."""

    SYSTEM_PROMPT = """You are a testing expert. Review code changes for:
- New code has corresponding tests
- Edge cases are covered
- Test quality and clarity
- Test isolation and independence
- Appropriate use of mocks/stubs
- Test naming and organization
- Missing test scenarios

Ensure comprehensive test coverage."""

    def __init__(self, working_dir: Path | None = None) -> None:
        """Initialize test coverage reviewer."""
        super().__init__(
            name="Test Coverage (Claude Code)",
            system_prompt=self.SYSTEM_PROMPT,
            working_dir=working_dir
        )
