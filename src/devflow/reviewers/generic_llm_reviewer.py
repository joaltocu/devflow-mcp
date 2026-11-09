"""Code reviewers using generic LLM (OpenAI-compatible APIs)."""

import json
import os
from typing import Any, Dict

from devflow.agents.generic_llm import GenericLLMAgent
from devflow.reviewers.base import BaseReviewer, ReviewIssue, ReviewResult, Severity


class GenericLLMReviewer(BaseReviewer):
    """Base reviewer using generic OpenAI-compatible LLM."""

    def __init__(
        self,
        name: str,
        system_prompt: str,
        model: str | None = None,
    ):
        """Initialize generic LLM reviewer.

        Args:
            name: Reviewer name
            system_prompt: System prompt for the reviewer
            model: Model name (defaults to LLM_MODEL env var)
        """
        super().__init__(name=name)
        self.system_prompt = system_prompt
        self.model = model or os.getenv("LLM_MODEL", "gpt-4")
        self.agent = GenericLLMAgent(
            model=self.model,
            system_prompt=system_prompt,
        )

    async def review(
        self, changes: Dict[str, Any], context: Dict[str, Any]
    ) -> ReviewResult:
        """Perform code review using generic LLM.

        Args:
            changes: Dictionary containing code changes
            context: Review context

        Returns:
            Review result with issues
        """
        result = self.create_result()

        # Build review prompt
        diff = changes.get("diff", "")
        if not diff:
            result.summary = "No changes to review"
            return result

        # Create review prompt
        prompt = self._build_review_prompt(diff, changes, context)

        try:
            # Get review from LLM
            response_text = await self.agent.generate_json(
                prompt=prompt,
                temperature=0.0,
                max_tokens=4096,
            )

            # Parse response
            review_data = self._parse_review_response(response_text)

            # Convert to ReviewIssue objects
            for issue_data in review_data.get("issues", []):
                try:
                    severity_str = issue_data.get("severity", "INFO").upper()
                    # Map common severity strings
                    severity_map = {
                        "CRITICAL": Severity.CRITICAL,
                        "HIGH": Severity.HIGH,
                        "MEDIUM": Severity.MEDIUM,
                        "LOW": Severity.LOW,
                        "INFO": Severity.INFO,
                    }
                    severity = severity_map.get(severity_str, Severity.INFO)

                    issue = ReviewIssue(
                        severity=severity,
                        file=issue_data.get("file", "unknown"),
                        line=issue_data.get("line"),
                        message=issue_data.get("message", ""),
                        suggestion=issue_data.get("suggestion"),
                        category=issue_data.get("category", "general"),
                    )
                    result.issues.append(issue)
                except Exception as e:
                    # Log error but continue
                    print(f"Warning: Failed to parse issue: {e}")

            result.summary = review_data.get(
                "summary", f"Review completed with {len(result.issues)} issues found"
            )
            result.passed = len(
                [i for i in result.issues if i.severity in [Severity.CRITICAL, Severity.HIGH]]
            ) == 0

        except Exception as e:
            result.summary = f"Review failed: {str(e)}"
            result.passed = False

        return result

    def _build_review_prompt(
        self, diff: str, changes: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        """Build the review prompt for the LLM.

        Args:
            diff: Git diff to review
            changes: Change information
            context: Review context

        Returns:
            Prompt string
        """
        language = context.get("language", "unknown")
        framework = context.get("framework", "unknown")

        prompt = f"""Review the following code changes and provide a structured analysis.

**Context:**
- Language: {language}
- Framework: {framework}
- Files changed: {len(changes.get('file_changes', []))}

**Code Changes:**
```
{diff}
```

**Your Task:**
{self.system_prompt}

**Output Format:**
You MUST respond with a valid JSON object in this exact format:

{{
  "summary": "Brief summary of the review",
  "issues": [
    {{
      "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFO",
      "file": "path/to/file.py",
      "line": 42,
      "message": "Description of the issue",
      "suggestion": "How to fix it (optional)",
      "category": "security|quality|performance|etc"
    }}
  ]
}}

Respond ONLY with the JSON object, no other text.
"""
        return prompt

    def _parse_review_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response to extract review data.

        Args:
            response: Raw response from LLM

        Returns:
            Parsed review data
        """
        # Try to parse as JSON
        try:
            # First, try direct JSON parse
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            lines = response.split("\n")
            json_lines = []
            in_json_block = False

            for line in lines:
                if "```json" in line.lower():
                    in_json_block = True
                    continue
                elif "```" in line and in_json_block:
                    break
                elif in_json_block:
                    json_lines.append(line)

            if json_lines:
                try:
                    return json.loads("\n".join(json_lines))
                except json.JSONDecodeError:
                    pass

            # Fallback: return default structure
            return {
                "summary": "Failed to parse LLM response",
                "issues": [],
            }


class CodeQualityGenericReviewer(GenericLLMReviewer):
    """Code quality reviewer using generic LLM."""

    SYSTEM_PROMPT = """You are an expert code quality reviewer. Analyze the code for:
- Code style and consistency
- Naming conventions
- Documentation quality
- Code organization
- Maintainability
- Best practices
- DRY principle violations
- SOLID principles

Be specific and constructive. Only report real issues."""

    def __init__(self, model: str | None = None):
        """Initialize code quality reviewer."""
        super().__init__(
            name="Code Quality (Generic LLM)",
            system_prompt=self.SYSTEM_PROMPT,
            model=model,
        )


class SecurityGenericReviewer(GenericLLMReviewer):
    """Security reviewer using generic LLM."""

    SYSTEM_PROMPT = """You are a security expert. Analyze the code for:
- SQL injection vulnerabilities
- XSS vulnerabilities
- Authentication/authorization issues
- Hardcoded secrets or credentials
- Insecure dependencies
- OWASP Top 10 vulnerabilities
- Input validation issues
- Cryptography misuse
- Path traversal vulnerabilities
- Command injection

Be thorough. Flag anything suspicious."""

    def __init__(self, model: str | None = None):
        """Initialize security reviewer."""
        super().__init__(
            name="Security (Generic LLM)",
            system_prompt=self.SYSTEM_PROMPT,
            model=model,
        )


class ArchitectureGenericReviewer(GenericLLMReviewer):
    """Architecture reviewer using generic LLM."""

    SYSTEM_PROMPT = """You are a software architect. Analyze the code for:
- Design pattern usage
- Separation of concerns
- Module boundaries
- Circular dependencies
- API design consistency
- Scalability concerns
- Technical debt
- Architectural violations

Focus on high-level design issues."""

    def __init__(self, model: str | None = None):
        """Initialize architecture reviewer."""
        super().__init__(
            name="Architecture (Generic LLM)",
            system_prompt=self.SYSTEM_PROMPT,
            model=model,
        )


class TestCoverageGenericReviewer(GenericLLMReviewer):
    """Test coverage reviewer using generic LLM."""

    SYSTEM_PROMPT = """You are a testing expert. Analyze the code for:
- Missing test coverage for new code
- Edge cases not covered
- Test quality and clarity
- Test isolation
- Proper use of mocks/stubs
- Test naming and organization
- Missing test scenarios

Focus on what tests are missing or inadequate."""

    def __init__(self, model: str | None = None):
        """Initialize test coverage reviewer."""
        super().__init__(
            name="Test Coverage (Generic LLM)",
            system_prompt=self.SYSTEM_PROMPT,
            model=model,
        )
