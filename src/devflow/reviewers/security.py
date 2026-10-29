"""Security reviewer."""

import json
import re
from typing import Any, Dict

from devflow.agents.claude_api import ClaudeAPIAgent
from devflow.reviewers.base import BaseReviewer, ReviewIssue, ReviewResult, Severity


class SecurityReviewer(BaseReviewer):
    """Reviews code for security vulnerabilities."""

    SYSTEM_PROMPT = """You are an expert security code reviewer. Your job is to identify security vulnerabilities including:
- OWASP Top 10 vulnerabilities
- SQL Injection
- Cross-Site Scripting (XSS)
- Cross-Site Request Forgery (CSRF)
- Authentication and authorization issues
- Insecure cryptography
- Hardcoded secrets (API keys, passwords, tokens)
- Path traversal
- Command injection
- Insecure deserialization
- Dependency vulnerabilities
- Information exposure

Be thorough and flag potential security risks. Err on the side of caution."""

    # Patterns for detecting hardcoded secrets
    SECRET_PATTERNS = [
        (r'["\']([A-Za-z0-9_\-]{32,})["\']', "Possible API key or token"),
        (r'password\s*=\s*["\']([^"\']+)["\']', "Hardcoded password"),
        (r'api[_-]?key\s*=\s*["\']([^"\']+)["\']', "Hardcoded API key"),
        (r'secret\s*=\s*["\']([^"\']+)["\']', "Hardcoded secret"),
        (r'token\s*=\s*["\']([^"\']+)["\']', "Hardcoded token"),
        (r'bearer\s+[A-Za-z0-9_\-\.]{20,}', "Hardcoded bearer token"),
    ]

    def __init__(self, model: str = "claude-sonnet-4-5-20250929") -> None:
        """Initialize security reviewer."""
        super().__init__(name="Security", model=model)
        self.agent = ClaudeAPIAgent(model=model, system_prompt=self.SYSTEM_PROMPT)

    async def review(
        self, changes: Dict[str, Any], context: Dict[str, Any]
    ) -> ReviewResult:
        """Perform security review.

        Args:
            changes: Dictionary containing code changes
            context: Review context

        Returns:
            Review result with security issues
        """
        result = self.create_result()

        diff = changes.get("diff", "")
        if not diff:
            result.summary = "No changes to review"
            return result

        # First, scan for secrets with regex
        secret_issues = self._scan_for_secrets(diff)
        for issue in secret_issues:
            result.add_issue(issue)

        # Then, run AI-powered security review
        language = context.get("language", "")
        framework = context.get("framework", "")

        user_prompt = self._build_prompt(diff, language, framework)
        response = await self.agent.run(user_prompt)

        # Parse AI response
        ai_issues = self._parse_response(response)
        for issue in ai_issues:
            result.add_issue(issue)

        result.summary = self._generate_summary(result)

        return result

    def _scan_for_secrets(self, diff: str) -> list[ReviewIssue]:
        """Scan for hardcoded secrets using regex patterns."""
        issues = []

        for line_num, line in enumerate(diff.split("\n"), start=1):
            # Only check added lines (those starting with +)
            if not line.startswith("+"):
                continue

            for pattern, description in self.SECRET_PATTERNS:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Skip if it's a comment or example
                    if any(marker in line.lower() for marker in ["example", "todo", "fixme", "xxx"]):
                        continue

                    issues.append(
                        ReviewIssue(
                            severity=Severity.CRITICAL,
                            file="",  # Will be filled in by diff analyzer
                            line=line_num,
                            message=f"{description}: {match.group(0)[:20]}...",
                            suggestion="Remove hardcoded secret and use environment variables or secure secret management",
                            category="security:secrets",
                        )
                    )

        return issues

    def _build_prompt(self, diff: str, language: str, framework: str) -> str:
        """Build security review prompt."""
        prompt = f"""Please perform a thorough security review of the following code changes.

LANGUAGE: {language or "Unknown"}
FRAMEWORK: {framework or "Unknown"}

CODE CHANGES:
```diff
{diff}
```

Please identify any security vulnerabilities and provide your feedback in the following JSON format:

```json
{{
    "issues": [
        {{
            "severity": "critical|high|medium|low|info",
            "file": "path/to/file.ext",
            "line": 42,
            "message": "Brief description of the vulnerability",
            "suggestion": "Specific remediation advice",
            "category": "sql-injection|xss|auth|crypto|csrf|path-traversal|command-injection|other"
        }}
    ],
    "overall_risk": "critical|high|medium|low",
    "summary": "Brief security assessment"
}}
```

Focus on:
1. OWASP Top 10 vulnerabilities
2. SQL Injection
3. XSS (Cross-Site Scripting)
4. Authentication/Authorization flaws
5. Insecure cryptography
6. Command injection
7. Path traversal
8. CSRF vulnerabilities
9. Information exposure
10. Insecure dependencies

Flag anything that could potentially be exploited. Be thorough.
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
                    category=f"security:{issue_data.get('category', 'general')}",
                )
                issues.append(issue)

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # If parsing fails, create a generic issue
            issues.append(
                ReviewIssue(
                    severity=Severity.INFO,
                    file="",
                    line=None,
                    message=f"Security review completed but response parsing failed: {str(e)}",
                    suggestion="Manual security review recommended",
                    category="security:parse-error",
                )
            )

        return issues

    def _generate_summary(self, result: ReviewResult) -> str:
        """Generate summary of security review results."""
        if not result.issues:
            return "No security issues detected. Code appears secure."

        critical = result.get_critical_count()
        high = result.get_high_count()

        if critical > 0:
            return f"CRITICAL: Found {critical} critical security vulnerabilities that must be fixed immediately!"
        elif high > 0:
            return f"Found {high} high-severity security issues that should be addressed."
        else:
            return f"Found {len(result.issues)} security issues to review."
