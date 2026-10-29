"""Code quality reviewer."""

import json
from typing import Any, Dict

from devflow.agents.claude_api import ClaudeAPIAgent
from devflow.reviewers.base import BaseReviewer, ReviewIssue, ReviewResult, Severity


class CodeQualityReviewer(BaseReviewer):
    """Reviews code for quality, style, and maintainability."""

    SYSTEM_PROMPT = """You are an expert code quality reviewer. Your job is to review code changes for:
- Style consistency and adherence to best practices
- Naming conventions (variables, functions, classes)
- Code organization and structure
- Documentation (comments, docstrings)
- Maintainability and readability
- DRY (Don't Repeat Yourself) principle
- SOLID principles
- Appropriate error handling

Be constructive and provide specific, actionable suggestions for improvement."""

    def __init__(self, model: str = "claude-sonnet-4-5-20250929") -> None:
        """Initialize code quality reviewer."""
        super().__init__(name="Code Quality", model=model)
        self.agent = ClaudeAPIAgent(model=model, system_prompt=self.SYSTEM_PROMPT)

    async def review(
        self, changes: Dict[str, Any], context: Dict[str, Any]
    ) -> ReviewResult:
        """Perform code quality review.

        Args:
            changes: Dictionary containing code changes
            context: Review context

        Returns:
            Review result with quality issues
        """
        result = self.create_result()

        # Build review prompt
        diff = changes.get("diff", "")
        if not diff:
            result.summary = "No changes to review"
            return result

        language = context.get("language", "")
        framework = context.get("framework", "")
        style_guide = context.get("style_guide", "")

        user_prompt = self._build_prompt(diff, language, framework, style_guide)

        # Run review
        response = await self.agent.run(user_prompt)

        # Parse response
        issues = self._parse_response(response)
        for issue in issues:
            result.add_issue(issue)

        result.summary = self._generate_summary(result)

        return result

    def _build_prompt(
        self, diff: str, language: str, framework: str, style_guide: str
    ) -> str:
        """Build review prompt."""
        prompt = f"""Please review the following code changes for quality issues.

LANGUAGE: {language or "Unknown"}
FRAMEWORK: {framework or "Unknown"}
"""

        if style_guide:
            prompt += f"\nSTYLE GUIDE: Refer to {style_guide}\n"

        prompt += f"""
CODE CHANGES:
```diff
{diff}
```

Please identify any code quality issues and provide your feedback in the following JSON format:

```json
{{
    "issues": [
        {{
            "severity": "critical|high|medium|low|info",
            "file": "path/to/file.ext",
            "line": 42,
            "message": "Brief description of the issue",
            "suggestion": "Specific suggestion for improvement",
            "category": "style|naming|documentation|maintainability|error-handling"
        }}
    ],
    "overall_quality": "excellent|good|fair|poor",
    "summary": "Brief overall assessment"
}}
```

Focus on:
1. Code style and formatting
2. Naming conventions
3. Code organization
4. Documentation completeness
5. Maintainability concerns
6. Best practices for {language or "this language"}

Only report actionable issues. Be specific and constructive.
"""
        return prompt

    def _parse_response(self, response: str) -> list[ReviewIssue]:
        """Parse Claude's response into ReviewIssue objects."""
        issues = []

        try:
            # Extract JSON from response (may be wrapped in markdown code block)
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()

            data = json.loads(json_str)

            for issue_data in data.get("issues", []):
                severity_str = issue_data.get("severity", "medium").lower()
                severity = Severity[severity_str.upper()]

                issue = ReviewIssue(
                    severity=severity,
                    file=issue_data.get("file", ""),
                    line=issue_data.get("line"),
                    message=issue_data.get("message", ""),
                    suggestion=issue_data.get("suggestion"),
                    category=f"quality:{issue_data.get('category', 'general')}",
                )
                issues.append(issue)

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # If parsing fails, create a generic issue
            issues.append(
                ReviewIssue(
                    severity=Severity.INFO,
                    file="",
                    line=None,
                    message=f"Code quality review completed but response parsing failed: {str(e)}",
                    suggestion="Manual review may be needed",
                    category="quality:parse-error",
                )
            )

        return issues

    def _generate_summary(self, result: ReviewResult) -> str:
        """Generate summary of review results."""
        if not result.issues:
            return "No code quality issues found. Code looks good!"

        counts = {
            "critical": result.get_critical_count(),
            "high": result.get_high_count(),
            "medium": result.get_medium_count(),
            "low": result.get_low_count(),
        }

        summary_parts = []
        for severity, count in counts.items():
            if count > 0:
                summary_parts.append(f"{count} {severity}")

        return f"Found {sum(counts.values())} code quality issues: {', '.join(summary_parts)}"
