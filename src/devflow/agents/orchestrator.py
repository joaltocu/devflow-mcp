"""Agent orchestrator for coordinating development and review agents."""

import asyncio
from pathlib import Path
from typing import Any, Dict, List

from devflow.agents.claude_code import ClaudeCodeAgent, ClaudeCodeResult
from devflow.reviewers.architecture import ArchitectureReviewer
from devflow.reviewers.base import ReviewResult
from devflow.reviewers.code_quality import CodeQualityReviewer
from devflow.reviewers.security import SecurityReviewer
from devflow.reviewers.synthesis import SynthesisAgent
from devflow.reviewers.test_coverage import TestCoverageReviewer
from devflow.tools.context_builder import ContextBuilder
from devflow.tools.diff_analyzer import DiffAnalyzer


class AgentOrchestrator:
    """Orchestrates development and review agents."""

    def __init__(self, project_root: Path, config: Any) -> None:
        """Initialize orchestrator.

        Args:
            project_root: Root directory of the project
            config: Configuration object
        """
        self.project_root = project_root
        self.config = config

        # Initialize agents
        self.claude_code_agent = ClaudeCodeAgent(project_root)

        # Initialize reviewers based on config
        self.reviewers: List[Any] = []

        review_model = config.get("agents.review.model", "claude-sonnet-4-5-20250929")

        if config.get("reviewers.code_quality.enabled", True):
            self.reviewers.append(CodeQualityReviewer(model=review_model))

        if config.get("reviewers.security.enabled", True):
            self.reviewers.append(SecurityReviewer(model=review_model))

        if config.get("reviewers.architecture.enabled", True):
            self.reviewers.append(ArchitectureReviewer(model=review_model))

        if config.get("reviewers.test_coverage.enabled", True):
            self.reviewers.append(TestCoverageReviewer(model=review_model))

        # Initialize synthesis agent (uses Opus for better quality)
        self.synthesis_agent = SynthesisAgent()

        # Initialize context builder
        self.context_builder = ContextBuilder(project_root, config)

    async def run_development(self, task: str) -> ClaudeCodeResult:
        """Run development task using Claude Code agent.

        Args:
            task: Development task description

        Returns:
            Result from Claude Code execution
        """
        return await self.claude_code_agent.run(task)

    async def run_reviews(
        self, changes: Dict[str, Any], context: Dict[str, Any]
    ) -> List[ReviewResult]:
        """Run all enabled reviewers in parallel.

        Args:
            changes: Code changes to review
            context: Review context

        Returns:
            List of review results from all reviewers
        """
        if not self.reviewers:
            return []

        # Run reviews in parallel or sequentially based on config
        parallel = self.config.get("agents.review.parallel", True)

        if parallel:
            tasks = [
                reviewer.review(changes, context)
                for reviewer in self.reviewers
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out any exceptions and log them
            review_results = []
            for result in results:
                if isinstance(result, Exception):
                    print(f"Review failed with error: {result}")
                else:
                    review_results.append(result)

            return review_results
        else:
            # Sequential execution
            review_results = []
            for reviewer in self.reviewers:
                try:
                    result = await reviewer.review(changes, context)
                    review_results.append(result)
                except Exception as e:
                    print(f"Review by {reviewer.name} failed: {e}")

            return review_results

    async def run_synthesis(
        self, review_results: List[ReviewResult]
    ) -> ReviewResult:
        """Synthesize review results.

        Args:
            review_results: List of individual review results

        Returns:
            Synthesized review result
        """
        return await self.synthesis_agent.synthesize(review_results)

    def build_context(self) -> Dict[str, Any]:
        """Build review context.

        Returns:
            Context dictionary with project metadata and documentation
        """
        return self.context_builder.build_context()

    def analyze_changes(self, diff: str) -> Dict[str, Any]:
        """Analyze code changes.

        Args:
            diff: Git diff output

        Returns:
            Dictionary with analyzed changes
        """
        analyzer = DiffAnalyzer(diff)
        return analyzer.to_dict()

    async def run_full_workflow(self, task: str) -> Dict[str, Any]:
        """Run complete workflow: development → reviews → synthesis.

        Args:
            task: Development task description

        Returns:
            Dictionary with all results
        """
        # Step 1: Run development task
        dev_result = await self.run_development(task)

        if not dev_result.success:
            return {
                "success": False,
                "error": dev_result.error,
                "stage": "development",
            }

        # Step 2: Analyze changes
        changes = self.analyze_changes(dev_result.changes)

        # Step 3: Build context
        context = self.build_context()

        # Step 4: Run reviews
        review_results = await self.run_reviews(changes, context)

        # Step 5: Synthesize reviews
        synthesized_review = await self.run_synthesis(review_results)

        return {
            "success": True,
            "development": {
                "changes": dev_result.changes,
                "log": dev_result.log,
            },
            "analysis": changes,
            "reviews": {
                "individual": [result.to_dict() for result in review_results],
                "synthesized": synthesized_review.to_dict(),
            },
            "stage": "completed",
        }
