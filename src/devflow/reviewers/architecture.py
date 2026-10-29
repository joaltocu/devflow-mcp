"""Architecture reviewer."""

import json
from pathlib import Path
from typing import Any, Dict

from devflow.agents.claude_api import ClaudeAPIAgent
from devflow.reviewers.base import BaseReviewer, ReviewIssue, ReviewResult, Severity


class ArchitectureReviewer(BaseReviewer):
    """Reviews code for architectural compliance and design patterns."""

    SYSTEM_PROMPT = """You are an expert software architect reviewing code changes. Your job is to ensure:
- Adherence to established architecture patterns and design principles
- Compliance with Architecture Decision Records (ADRs)
- Proper module boundaries and separation of concerns
- Correct dependency directions (no circular dependencies)
- Appropriate design patterns for the problem
- SOLID principles
- Clean architecture / hexagonal architecture compliance
- Proper layering (presentation, business logic, data)

Focus on structural and architectural concerns, not syntax or style."""

    def __init__(self, model: str = "claude-sonnet-4-5-20250929") -> None:
        """Initialize architecture reviewer."""
        super().__init__(name="Architecture", model=model)
        self.agent = ClaudeAPIAgent(model=model, system_prompt=self.SYSTEM_PROMPT)

    async def review(
        self, changes: Dict[str, Any], context: Dict[str, Any]
    ) -> ReviewResult:
        """Perform architecture review.

        Args:
            changes: Dictionary containing code changes
            context: Review context including architecture docs and ADRs

        Returns:
            Review result with architecture issues
        """
        result = self.create_result()

        diff = changes.get("diff", "")
        if not diff:
            result.summary = "No changes to review"
            return result

        # Get architecture context
        architecture_docs = context.get("architecture_docs", "")
        adrs = context.get("adrs", [])
        language = context.get("language", "")
        framework = context.get("framework", "")

        user_prompt = self._build_prompt(diff, architecture_docs, adrs, language, framework)
        response = await self.agent.run(user_prompt)

        # Parse response
        issues = self._parse_response(response)
        for issue in issues:
            result.add_issue(issue)

        result.summary = self._generate_summary(result)

        return result

    def _build_prompt(
        self,
        diff: str,
        architecture_docs: str,
        adrs: list,
        language: str,
        framework: str,
    ) -> str:
        """Build architecture review prompt."""
        prompt = f"""Please review the following code changes for architectural compliance.

LANGUAGE: {language or "Unknown"}
FRAMEWORK: {framework or "Unknown"}

"""

        if architecture_docs:
            prompt += f"""ARCHITECTURE DOCUMENTATION:
```
{architecture_docs[:2000]}  # Limit to avoid token overflow
```

"""

        if adrs:
            prompt += "ARCHITECTURE DECISION RECORDS (ADRs):\n"
            for adr in adrs[:5]:  # Limit to first 5 ADRs
                prompt += f"\nADR: {adr.get('file', 'Unknown')}\n"
                prompt += f"```\n{adr.get('content', '')[:500]}\n```\n"

        prompt += f"""
CODE CHANGES:
```diff
{diff}
```

Please identify any architectural issues and provide your feedback in the following JSON format:

```json
{{
    "issues": [
        {{
            "severity": "critical|high|medium|low|info",
            "file": "path/to/file.ext",
            "line": 42,
            "message": "Brief description of the architectural concern",
            "suggestion": "Specific architectural recommendation",
            "category": "boundaries|dependencies|patterns|solid|layering|adr-violation|other"
        }}
    ],
    "overall_compliance": "compliant|minor-issues|major-issues|non-compliant",
    "summary": "Brief architectural assessment"
}}
```

Focus on:
1. Module boundaries and separation of concerns
2. Dependency direction (should dependencies point inward?)
3. ADR compliance (if ADRs provided)
4. Design pattern appropriateness
5. SOLID principles
6. Layer violations
7. Circular dependencies

Only flag significant architectural concerns that could impact maintainability or scalability.
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
                    category=f"architecture:{issue_data.get('category', 'general')}",
                )
                issues.append(issue)

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # If parsing fails, create a generic issue
            issues.append(
                ReviewIssue(
                    severity=Severity.INFO,
                    file="",
                    line=None,
                    message=f"Architecture review completed but response parsing failed: {str(e)}",
                    suggestion="Manual architecture review may be needed",
                    category="architecture:parse-error",
                )
            )

        return issues

    def _generate_summary(self, result: ReviewResult) -> str:
        """Generate summary of architecture review results."""
        if not result.issues:
            return "No architectural issues found. Changes align with system architecture."

        counts = {
            "critical": result.get_critical_count(),
            "high": result.get_high_count(),
            "medium": result.get_medium_count(),
        }

        if counts["critical"] > 0:
            return f"CRITICAL: Found {counts['critical']} critical architectural violations!"
        elif counts["high"] > 0:
            return f"Found {counts['high']} significant architectural concerns."
        else:
            return f"Found {len(result.issues)} architectural issues to review."
