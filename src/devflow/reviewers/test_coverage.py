"""Test coverage reviewer."""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from devflow.agents.claude_api import ClaudeAPIAgent
from devflow.reviewers.base import BaseReviewer, ReviewIssue, ReviewResult, Severity


class TestCoverageReviewer(BaseReviewer):
    """Reviews code for test coverage and quality."""

    SYSTEM_PROMPT = """You are an expert test reviewer. Your job is to ensure:
- All new code has adequate test coverage
- Edge cases are properly tested
- Tests are well-structured and maintainable
- Tests follow testing best practices (AAA pattern, clear assertions)
- Integration tests exist where needed
- Mock usage is appropriate
- Test names are descriptive

Focus on test completeness and quality."""

    def __init__(self, model: str = "claude-sonnet-4-5-20250929") -> None:
        """Initialize test coverage reviewer."""
        super().__init__(name="Test Coverage", model=model)
        self.agent = ClaudeAPIAgent(model=model, system_prompt=self.SYSTEM_PROMPT)

    async def review(
        self, changes: Dict[str, Any], context: Dict[str, Any]
    ) -> ReviewResult:
        """Perform test coverage review.

        Args:
            changes: Dictionary containing code changes
            context: Review context including coverage data

        Returns:
            Review result with test coverage issues
        """
        result = self.create_result()

        diff = changes.get("diff", "")
        if not diff:
            result.summary = "No changes to review"
            return result

        # Get coverage data if available
        coverage_data = context.get("coverage", {})
        minimum_coverage = context.get("minimum_coverage", 80)

        # Check coverage thresholds
        if coverage_data:
            coverage_issues = self._check_coverage_thresholds(
                coverage_data, minimum_coverage
            )
            for issue in coverage_issues:
                result.add_issue(issue)

        # Run AI-powered test review
        language = context.get("language", "")
        framework = context.get("framework", "")

        user_prompt = self._build_prompt(diff, coverage_data, language, framework)
        response = await self.agent.run(user_prompt)

        # Parse response
        ai_issues = self._parse_response(response)
        for issue in ai_issues:
            result.add_issue(issue)

        result.summary = self._generate_summary(result, coverage_data)

        return result

    def _check_coverage_thresholds(
        self, coverage_data: Dict[str, Any], minimum: int
    ) -> list[ReviewIssue]:
        """Check if coverage meets minimum thresholds."""
        issues = []

        overall_coverage = coverage_data.get("overall", 0)
        if overall_coverage < minimum:
            issues.append(
                ReviewIssue(
                    severity=Severity.HIGH,
                    file="",
                    line=None,
                    message=f"Overall test coverage ({overall_coverage}%) is below minimum threshold ({minimum}%)",
                    suggestion=f"Add tests to reach at least {minimum}% coverage",
                    category="coverage:threshold",
                )
            )

        # Check per-file coverage
        files_coverage = coverage_data.get("files", {})
        for file_path, file_coverage in files_coverage.items():
            if file_coverage < minimum:
                issues.append(
                    ReviewIssue(
                        severity=Severity.MEDIUM,
                        file=file_path,
                        line=None,
                        message=f"File coverage ({file_coverage}%) is below minimum threshold ({minimum}%)",
                        suggestion=f"Add tests for {file_path}",
                        category="coverage:file",
                    )
                )

        return issues

    def _build_prompt(
        self,
        diff: str,
        coverage_data: Dict[str, Any],
        language: str,
        framework: str,
    ) -> str:
        """Build test coverage review prompt."""
        prompt = f"""Please review the following code changes for test coverage and quality.

LANGUAGE: {language or "Unknown"}
FRAMEWORK: {framework or "Unknown"}

"""

        if coverage_data:
            prompt += f"""COVERAGE DATA:
- Overall coverage: {coverage_data.get('overall', 'N/A')}%
- Files with low coverage: {coverage_data.get('low_coverage_files', [])}
"""

        prompt += f"""
CODE CHANGES:
```diff
{diff}
```

Please identify any test coverage issues and provide your feedback in the following JSON format:

```json
{{
    "issues": [
        {{
            "severity": "critical|high|medium|low|info",
            "file": "path/to/file.ext",
            "line": 42,
            "message": "Brief description of the test coverage issue",
            "suggestion": "Specific testing recommendation",
            "category": "missing-tests|edge-cases|test-quality|integration|mocking|other"
        }}
    ],
    "overall_quality": "excellent|good|fair|poor",
    "summary": "Brief test coverage assessment"
}}
```

Focus on:
1. Are new functions/classes covered by tests?
2. Are edge cases tested?
3. Are error conditions tested?
4. Is the test quality good (clear, maintainable)?
5. Are integration points tested?
6. Is mocking used appropriately?
7. Are test names descriptive?

Flag any significant gaps in test coverage or test quality issues.
"""
        return prompt

    def _parse_response(self, response: str) -> list[ReviewIssue]:
        """Parse Claude's response into ReviewIssue objects."""
        issues = []

        try:
            # Extract JSON from response
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
                    category=f"coverage:{issue_data.get('category', 'general')}",
                )
                issues.append(issue)

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # If parsing fails, create a generic issue
            issues.append(
                ReviewIssue(
                    severity=Severity.INFO,
                    file="",
                    line=None,
                    message=f"Test coverage review completed but response parsing failed: {str(e)}",
                    suggestion="Manual test review may be needed",
                    category="coverage:parse-error",
                )
            )

        return issues

    def _generate_summary(
        self, result: ReviewResult, coverage_data: Dict[str, Any]
    ) -> str:
        """Generate summary of test coverage review results."""
        summary_parts = []

        if coverage_data:
            overall = coverage_data.get("overall", 0)
            summary_parts.append(f"Overall coverage: {overall}%")

        if not result.issues:
            return f"Test coverage looks good! {' '.join(summary_parts) if summary_parts else 'All new code appears to be tested.'}"

        issue_count = len(result.issues)
        summary_parts.append(f"{issue_count} test coverage issues found")

        return " | ".join(summary_parts)
