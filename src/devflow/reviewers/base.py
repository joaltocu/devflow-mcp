"""Base classes for code reviewers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Severity(Enum):
    """Issue severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ReviewIssue:
    """Represents a single review issue."""

    severity: Severity
    file: str
    line: Optional[int]
    message: str
    suggestion: Optional[str] = None
    category: str = ""  # e.g., "security", "style", "architecture"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "severity": self.severity.value,
            "file": self.file,
            "line": self.line,
            "message": self.message,
            "suggestion": self.suggestion,
            "category": self.category,
        }


@dataclass
class ReviewResult:
    """Result from a code review."""

    reviewer_name: str
    issues: List[ReviewIssue] = field(default_factory=list)
    summary: str = ""
    passed: bool = True

    def add_issue(self, issue: ReviewIssue) -> None:
        """Add an issue to the review result."""
        self.issues.append(issue)

        # Mark as failed if critical or high severity issue
        if issue.severity in (Severity.CRITICAL, Severity.HIGH):
            self.passed = False

    def get_critical_count(self) -> int:
        """Get count of critical issues."""
        return sum(1 for issue in self.issues if issue.severity == Severity.CRITICAL)

    def get_high_count(self) -> int:
        """Get count of high severity issues."""
        return sum(1 for issue in self.issues if issue.severity == Severity.HIGH)

    def get_medium_count(self) -> int:
        """Get count of medium severity issues."""
        return sum(1 for issue in self.issues if issue.severity == Severity.MEDIUM)

    def get_low_count(self) -> int:
        """Get count of low severity issues."""
        return sum(1 for issue in self.issues if issue.severity == Severity.LOW)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "reviewer_name": self.reviewer_name,
            "issues": [issue.to_dict() for issue in self.issues],
            "summary": self.summary,
            "passed": self.passed,
            "counts": {
                "critical": self.get_critical_count(),
                "high": self.get_high_count(),
                "medium": self.get_medium_count(),
                "low": self.get_low_count(),
            },
        }


class BaseReviewer(ABC):
    """Abstract base class for code reviewers."""

    def __init__(self, name: str, model: str = "claude-sonnet-4-5-20250929") -> None:
        """Initialize reviewer.

        Args:
            name: Reviewer name
            model: Claude model to use
        """
        self.name = name
        self.model = model

    @abstractmethod
    async def review(
        self, changes: Dict[str, Any], context: Dict[str, Any]
    ) -> ReviewResult:
        """Perform code review.

        Args:
            changes: Dictionary containing code changes (diff, files, etc.)
            context: Review context (project metadata, architecture docs, etc.)

        Returns:
            Review result with issues and summary
        """
        pass

    def create_result(self) -> ReviewResult:
        """Create a new review result for this reviewer."""
        return ReviewResult(reviewer_name=self.name)
