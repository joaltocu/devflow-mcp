"""DevFlow CLI application."""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from devflow.core.config import Config
from devflow.core.state import StateManager
from devflow.core.workflow import Workflow

app = typer.Typer(
    name="devflow",
    help="Agent-driven development framework with autonomous code review",
    add_completion=False,
)

console = Console()


@app.command()
def init(
    project_root: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Project root directory"
    )
) -> None:
    """Initialize DevFlow in a project.

    Creates .devflow.toml configuration file and initializes state database.
    """
    root = project_root or Path.cwd()

    try:
        # Create config
        config = Config(root)

        # Save default config to project
        config_path = root / ".devflow.toml"
        if config_path.exists():
            if not typer.confirm(f"{config_path} already exists. Overwrite?"):
                console.print("[yellow]Initialization cancelled[/yellow]")
                raise typer.Exit(0)

        config.save_project_config()

        # Initialize state database
        StateManager(db_path=root / "devflow.db")

        console.print(f"[green]✓[/green] DevFlow initialized in {root}")
        console.print(f"[green]✓[/green] Created {config_path}")
        console.print(f"[green]✓[/green] Created devflow.db")
        console.print("\nNext steps:")
        console.print("  1. Edit .devflow.toml to customize configuration")
        console.print('  2. Run: devflow dev "your task description"')

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def dev(
    task: str = typer.Argument(..., help="Development task description"),
    project_root: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Project root directory"
    ),
    no_pr: bool = typer.Option(
        False, "--no-pr", help="Skip PR creation"
    ),
    pr_title: Optional[str] = typer.Option(
        None, "--pr-title", help="PR title"
    ),
) -> None:
    """Run full development workflow.

    Executes: development → reviews → synthesis → PR creation
    """
    root = project_root or Path.cwd()

    try:
        # Load config
        config = Config(root)

        # Create workflow
        workflow = Workflow(root, config)

        # Run workflow
        console.print(f"\n[bold]DevFlow Workflow[/bold]")
        console.print(f"Task: {task}\n")

        result = asyncio.run(
            workflow.run(
                task=task,
                create_pr=not no_pr,
                pr_title=pr_title,
            )
        )

        if result["success"]:
            console.print("\n[bold green]✓ Workflow completed successfully![/bold green]")
            console.print(f"Run ID: {result['run_id']}")
        else:
            console.print(f"\n[bold red]✗ Workflow failed[/bold red]")
            if "error" in result:
                console.print(f"Error: {result['error']}")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def review(
    project_root: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Project root directory"
    ),
) -> None:
    """Run code reviews on current staged changes.

    Reviews staged changes without running development agent.
    """
    root = project_root or Path.cwd()

    try:
        import subprocess

        # Get staged changes
        result = subprocess.run(
            ["git", "diff", "--staged"],
            cwd=root,
            capture_output=True,
            text=True,
        )

        if not result.stdout:
            console.print("[yellow]No staged changes to review[/yellow]")
            raise typer.Exit(0)

        # Load config
        config = Config(root)

        # Create workflow and orchestrator
        from devflow.agents.orchestrator import AgentOrchestrator

        orchestrator = AgentOrchestrator(root, config)

        # Analyze changes
        changes = orchestrator.analyze_changes(result.stdout)

        # Build context
        context = orchestrator.build_context()

        # Run reviews
        console.print("\n[bold]Running code reviews...[/bold]\n")

        review_results = asyncio.run(orchestrator.run_reviews(changes, context))

        # Show results
        for result in review_results:
            console.print(f"\n[bold]{result.reviewer_name}[/bold]")
            console.print(f"{result.summary}")

            if result.issues:
                console.print(f"\nIssues ({len(result.issues)}):")
                for issue in result.issues[:5]:  # Show first 5 issues
                    console.print(
                        f"  [{issue.severity.value.upper()}] {issue.file or 'General'}: {issue.message}"
                    )

                if len(result.issues) > 5:
                    console.print(f"  ... and {len(result.issues) - 5} more")

        # Synthesize
        console.print("\n[bold]Synthesizing reviews...[/bold]")
        from devflow.reviewers.synthesis import SynthesisAgent

        synthesis = SynthesisAgent()
        synthesized = asyncio.run(synthesis.synthesize(review_results))

        console.print(f"\n[bold]Final Review:[/bold]")
        console.print(f"{synthesized.summary}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def status(
    project_root: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Project root directory"
    ),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of runs to show"),
) -> None:
    """Show workflow run status.

    Displays recent workflow runs with their status.
    """
    root = project_root or Path.cwd()

    try:
        state = StateManager(db_path=root / "devflow.db")
        runs = state.list_runs(limit=limit)

        if not runs:
            console.print("[yellow]No workflow runs found[/yellow]")
            raise typer.Exit(0)

        # Create table
        table = Table(title="DevFlow Workflow Runs")
        table.add_column("ID", style="cyan")
        table.add_column("Branch", style="green")
        table.add_column("Stage", style="blue")
        table.add_column("Status", style="magenta")
        table.add_column("Created", style="white")

        for run in runs:
            # Truncate ID for display
            short_id = run.id[:8]

            # Color code status
            status_color = {
                "completed": "green",
                "failed": "red",
                "in_progress": "yellow",
                "pending": "blue",
            }.get(run.status, "white")

            table.add_row(
                short_id,
                run.branch,
                run.stage,
                f"[{status_color}]{run.status}[/{status_color}]",
                run.created_at.strftime("%Y-%m-%d %H:%M"),
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def resume(
    run_id: str = typer.Argument(..., help="Workflow run ID to resume"),
    project_root: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Project root directory"
    ),
) -> None:
    """Resume a failed or interrupted workflow run.

    NOT IMPLEMENTED YET - placeholder for future functionality.
    """
    console.print("[yellow]Resume functionality not yet implemented[/yellow]")
    console.print("This feature will allow resuming workflows from their last checkpoint.")
    raise typer.Exit(0)


@app.callback()
def main() -> None:
    """DevFlow: Agent-driven development with autonomous code review."""
    pass


# Entry point for the CLI
if __name__ == "__main__":
    app()
