"""Workflow state machine for DevFlow."""

from pathlib import Path
from typing import Any, Dict, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from devflow.agents.orchestrator import AgentOrchestrator
from devflow.core.config import Config
from devflow.core.state import StateManager
from devflow.github.pr_manager import PRManager


class Workflow:
    """Manages the DevFlow workflow state machine."""

    STAGES = [
        "develop",
        "review",
        "synthesis",
        "create_pr",
    ]

    def __init__(
        self,
        project_root: Optional[Path] = None,
        config: Optional[Config] = None,
    ) -> None:
        """Initialize workflow.

        Args:
            project_root: Root directory of the project
            config: Configuration object
        """
        self.project_root = project_root or Path.cwd()
        self.config = config or Config(self.project_root)

        # Initialize components
        self.state = StateManager()
        self.orchestrator = AgentOrchestrator(self.project_root, self.config)
        self.pr_manager = PRManager(self.project_root)
        self.console = Console()

    async def run(
        self,
        task: str,
        create_pr: bool = True,
        pr_title: Optional[str] = None,
        pr_body: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run complete workflow.

        Args:
            task: Development task description
            create_pr: Whether to create a PR
            pr_title: PR title (auto-generated if not provided)
            pr_body: PR body (auto-generated if not provided)

        Returns:
            Workflow results
        """
        # Get current branch and commit
        branch = self.orchestrator.claude_code_agent.get_current_branch()
        commit_sha = self.orchestrator.claude_code_agent.get_current_commit()

        # Create workflow run
        run = self.state.create_run(branch=branch, commit_sha=commit_sha)

        try:
            # Stage 1: Development
            self.console.print(f"\n[bold cyan]Stage 1: Development[/bold cyan]")
            self.state.update_run(run.id, stage="develop", status="in_progress")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task_id = progress.add_task("Running development agent...", total=None)

                dev_result = await self.orchestrator.run_development(task)

                if not dev_result.success:
                    self.state.update_run(
                        run.id,
                        status="failed",
                        error_message=dev_result.error,
                    )
                    return {
                        "success": False,
                        "error": dev_result.error,
                        "run_id": run.id,
                    }

                progress.update(task_id, description="✓ Development complete")

            # Analyze changes
            changes = self.orchestrator.analyze_changes(dev_result.changes)
            self.console.print(
                f"[green]✓[/green] Changes: {changes['stats']['files_changed']} files, "
                f"+{changes['stats']['total_additions']} -{changes['stats']['total_deletions']}"
            )

            # Stage 2: Reviews
            self.console.print(f"\n[bold cyan]Stage 2: Code Reviews[/bold cyan]")
            self.state.update_run(run.id, stage="review", status="in_progress")

            # Build context
            context = self.orchestrator.build_context()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task_id = progress.add_task("Running code reviews...", total=None)

                review_results = await self.orchestrator.run_reviews(changes, context)

                progress.update(task_id, description=f"✓ {len(review_results)} reviews complete")

            # Show individual review summaries
            for result in review_results:
                icon = "✓" if result.passed else "⚠"
                self.console.print(f"  [{icon}] {result.reviewer_name}: {result.summary}")

            # Stage 3: Synthesis
            self.console.print(f"\n[bold cyan]Stage 3: Review Synthesis[/bold cyan]")
            self.state.update_run(run.id, stage="synthesis", status="in_progress")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task_id = progress.add_task("Synthesizing reviews...", total=None)

                synthesized = await self.orchestrator.run_synthesis(review_results)

                progress.update(task_id, description="✓ Synthesis complete")

            self.console.print(f"\n[bold]Final Review:[/bold]")
            self.console.print(f"{synthesized.summary}\n")

            # Show issue counts by severity
            if synthesized.issues:
                critical = synthesized.get_critical_count()
                high = synthesized.get_high_count()
                medium = synthesized.get_medium_count()

                if critical > 0:
                    self.console.print(f"  [red]🔴 Critical: {critical}[/red]")
                if high > 0:
                    self.console.print(f"  [yellow]🟠 High: {high}[/yellow]")
                if medium > 0:
                    self.console.print(f"  [blue]🟡 Medium: {medium}[/blue]")

            # Stage 4: Create PR (if requested)
            if create_pr and self.config.get("github.auto_create_pr", True):
                self.console.print(f"\n[bold cyan]Stage 4: Create Pull Request[/bold cyan]")
                self.state.update_run(run.id, stage="create_pr", status="in_progress")

                # Auto-generate PR title and body if not provided
                if not pr_title:
                    pr_title = task[:100]  # Use first 100 chars of task

                if not pr_body:
                    pr_body = self._generate_pr_body(task, synthesized, changes)

                try:
                    pr_url = await self.pr_manager.create_pr(
                        branch=branch,
                        title=pr_title,
                        body=pr_body,
                    )

                    self.console.print(f"[green]✓[/green] Pull request created: {pr_url}")

                    # Get PR number and post review comments
                    pr_number = self.pr_manager.get_pr_number_from_branch(branch)
                    if pr_number:
                        await self.pr_manager.post_review_comments(
                            pr_number, synthesized
                        )
                        self.console.print(f"[green]✓[/green] Review comments posted")

                except Exception as e:
                    self.console.print(f"[yellow]⚠[/yellow] Failed to create PR: {e}")

            # Mark workflow as completed
            self.state.update_run(run.id, stage="complete", status="completed")

            return {
                "success": True,
                "run_id": run.id,
                "development": {
                    "changes": dev_result.changes,
                    "log": dev_result.log,
                },
                "analysis": changes,
                "reviews": {
                    "individual": [r.to_dict() for r in review_results],
                    "synthesized": synthesized.to_dict(),
                },
            }

        except Exception as e:
            self.state.update_run(
                run.id,
                status="failed",
                error_message=str(e),
            )
            raise

    def _generate_pr_body(
        self, task: str, synthesized: Any, changes: Dict[str, Any]
    ) -> str:
        """Generate PR body from review results.

        Args:
            task: Original task description
            synthesized: Synthesized review result
            changes: Change analysis

        Returns:
            PR body markdown
        """
        body = f"## Task\n\n{task}\n\n"

        body += f"## Changes\n\n"
        body += f"- Files changed: {changes['stats']['files_changed']}\n"
        body += f"- Lines added: +{changes['stats']['total_additions']}\n"
        body += f"- Lines removed: -{changes['stats']['total_deletions']}\n\n"

        body += f"## Code Review\n\n{synthesized.summary}\n\n"

        if synthesized.issues:
            body += f"### Issues ({len(synthesized.issues)})\n\n"

            # Group by severity
            for severity in ["CRITICAL", "HIGH", "MEDIUM"]:
                severity_issues = [
                    i for i in synthesized.issues
                    if i.severity.value.upper() == severity
                ]

                if severity_issues:
                    emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡"}[severity]
                    body += f"#### {emoji} {severity}\n\n"

                    for issue in severity_issues:
                        body += f"- {issue.message}\n"

                    body += "\n"

        body += "\n---\n"
        body += "🤖 Generated with [DevFlow](https://github.com/joaltocu/framework)\n"

        return body
