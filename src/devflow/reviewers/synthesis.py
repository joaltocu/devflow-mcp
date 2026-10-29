"""Synthesis agent to consolidate multiple review results."""

import json
from typing import Any, Dict, List

from devflow.agents.claude_api import ClaudeAPIAgent
from devflow.reviewers.base import ReviewIssue, ReviewResult, Severity


class SynthesisAgent:
    """Consolidates multiple review results into a unified review."""

    SYSTEM_PROMPT = """You are a code review synthesis expert. Your job is to:
1. Consolidate findings from multiple specialized reviewers
2. Identify and deduplicate similar or identical issues
3. Resolve conflicting recommendations
4. Prioritize issues by impact and urgency
5. Create a coherent, actionable review summary

Be clear, concise, and prioritize developer experience."""

    def __init__(self, model: str = "claude-opus-4-5-20251101") -> None:
        """Initialize synthesis agent.

        Note: Using Opus for synthesis to ensure high-quality consolidation.
        """
        self.model = model
        self.agent = ClaudeAPIAgent(model=model, system_prompt=self.SYSTEM_PROMPT)

    async def synthesize(
        self, review_results: List[ReviewResult]
    ) -> ReviewResult:
        """Synthesize multiple review results into one.

        Args:
            review_results: List of review results from different reviewers

        Returns:
            Synthesized review result
        """
        # Create output result
        synthesized = ReviewResult(reviewer_name="Synthesized Review")

        if not review_results:
            synthesized.summary = "No reviews to synthesize"
            return synthesized

        # Build synthesis prompt
        user_prompt = self._build_prompt(review_results)

        # Run synthesis
        response = await self.agent.run(user_prompt)

        # Parse response
        issues, summary = self._parse_response(response)
        for issue in issues:
            synthesized.add_issue(issue)

        synthesized.summary = summary or self._generate_default_summary(synthesized)

        return synthesized

    def _build_prompt(self, review_results: List[ReviewResult]) -> str:
        """Build synthesis prompt."""
        prompt = """Please synthesize the following code review results from multiple specialized reviewers.

REVIEW RESULTS:
"""

        for result in review_results:
            prompt += f"\n## {result.reviewer_name}\n"
            prompt += f"Summary: {result.summary}\n"
            prompt += f"Issues: {len(result.issues)}\n\n"

            for issue in result.issues:
                prompt += f"- [{issue.severity.value.upper()}] {issue.file or 'General'}"
                if issue.line:
                    prompt += f":{issue.line}"
                prompt += f"\n  {issue.message}\n"
                if issue.suggestion:
                    prompt += f"  Suggestion: {issue.suggestion}\n"
                prompt += "\n"

        prompt += """
Your task is to synthesize these reviews. Provide your output in the following JSON format:

```json
{
    "issues": [
        {
            "severity": "critical|high|medium|low|info",
            "file": "path/to/file.ext",
            "line": 42,
            "message": "Consolidated description",
            "suggestion": "Consolidated recommendation",
            "category": "original-category",
            "duplicate_of": ["reviewer1:issue1", "reviewer2:issue3"]
        }
    ],
    "summary": "Overall synthesized summary with key takeaways and priority actions"
}
```

Guidelines:
1. **Deduplicate**: If multiple reviewers flag the same issue, consolidate into one issue
2. **Prioritize**: Order by severity (critical → high → medium → low → info)
3. **Resolve conflicts**: If reviewers disagree, provide a balanced recommendation
4. **Be actionable**: Focus on what developers need to do
5. **Highlight blockers**: Clearly identify critical issues that must be fixed

The summary should be a brief paragraph highlighting:
- Overall code health
- Number of critical/high priority issues
- Key action items
- Whether the PR should be approved, needs changes, or is blocked
"""
        return prompt

    def _parse_response(self, response: str) -> tuple[list[ReviewIssue], str]:
        """Parse synthesis response."""
        issues = []
        summary = ""

        try:
            # Extract JSON from response
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()

            data = json.loads(json_str)

            # Parse issues
            for issue_data in data.get("issues", []):
                severity_str = issue_data.get("severity", "medium").lower()
                try:
                    severity = Severity[severity_str.upper()]
                except KeyError:
                    severity = Severity.MEDIUM

                issue = ReviewIssue(
                    severity=severity,
                    file=issue_data.get("file", ""),
                    line=issue_data.get("line"),
                    message=issue_data.get("message", ""),
                    suggestion=issue_data.get("suggestion"),
                    category=issue_data.get("category", "synthesized"),
                )
                issues.append(issue)

            # Get summary
            summary = data.get("summary", "")

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # If parsing fails, fall back to simple concatenation
            for result in review_results:
                for issue in result.issues:
                    issues.append(issue)

            summary = f"Synthesis parsing failed ({str(e)}). Showing all issues from individual reviewers."

        # Sort by severity
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4,
        }
        issues.sort(key=lambda i: severity_order.get(i.severity, 99))

        return issues, summary

    def _generate_default_summary(self, result: ReviewResult) -> str:
        """Generate a default summary if synthesis fails."""
        total_issues = len(result.issues)
        critical = result.get_critical_count()
        high = result.get_high_count()
        medium = result.get_medium_count()

        if critical > 0:
            return f"🔴 BLOCKED: {critical} critical issues must be fixed before merge. Total: {total_issues} issues."
        elif high > 0:
            return f"🟡 NEEDS CHANGES: {high} high-priority issues should be addressed. Total: {total_issues} issues."
        elif medium > 0:
            return f"🟢 APPROVED with suggestions: {medium} medium-priority improvements suggested. Total: {total_issues} issues."
        else:
            return f"✅ APPROVED: Code review passed with {total_issues} minor suggestions."
