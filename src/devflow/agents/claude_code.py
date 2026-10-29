"""Claude Code agent wrapper for development tasks."""

import asyncio
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ClaudeCodeResult:
    """Result from Claude Code execution."""

    success: bool
    changes: str  # git diff output
    log: str  # execution log
    error: Optional[str] = None


class ClaudeCodeAgent:
    """Wrapper for Claude Code CLI to run development tasks."""

    def __init__(self, working_dir: Path) -> None:
        """Initialize Claude Code agent.

        Args:
            working_dir: Working directory for the agent
        """
        self.working_dir = working_dir
        self.devflow_dir = working_dir / ".devflow"
        self.devflow_dir.mkdir(exist_ok=True)

    async def run(self, task: str) -> ClaudeCodeResult:
        """Run a development task using Claude Code.

        Args:
            task: High-level task description

        Returns:
            Result containing success status, changes, and logs
        """
        # Create task file for Claude to read
        task_file = self.devflow_dir / "current_task.md"
        task_file.write_text(task)

        try:
            # Execute Claude Code in non-interactive mode
            process = await asyncio.create_subprocess_exec(
                "claude",
                "--non-interactive",
                "--task-file",
                str(task_file),
                cwd=self.working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            # Capture changes via git
            changes = subprocess.run(
                ["git", "diff", "--staged"],
                cwd=self.working_dir,
                capture_output=True,
                text=True,
            ).stdout

            # Check for unstaged changes as well
            unstaged_changes = subprocess.run(
                ["git", "diff"],
                cwd=self.working_dir,
                capture_output=True,
                text=True,
            ).stdout

            all_changes = changes
            if unstaged_changes:
                all_changes = f"{changes}\n\n# Unstaged changes:\n{unstaged_changes}"

            success = process.returncode == 0

            return ClaudeCodeResult(
                success=success,
                changes=all_changes,
                log=stdout.decode() if stdout else "",
                error=stderr.decode() if stderr and not success else None,
            )

        except FileNotFoundError:
            return ClaudeCodeResult(
                success=False,
                changes="",
                log="",
                error="Claude Code CLI not found. Please install it first.",
            )
        except Exception as e:
            return ClaudeCodeResult(
                success=False,
                changes="",
                log="",
                error=f"Unexpected error: {str(e)}",
            )

    def get_current_branch(self) -> str:
        """Get the current git branch.

        Returns:
            Current branch name
        """
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=self.working_dir,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def get_current_commit(self) -> str:
        """Get the current git commit SHA.

        Returns:
            Current commit SHA
        """
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.working_dir,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def stage_all_changes(self) -> bool:
        """Stage all changes for commit.

        Returns:
            True if successful, False otherwise
        """
        result = subprocess.run(
            ["git", "add", "."],
            cwd=self.working_dir,
            capture_output=True,
        )
        return result.returncode == 0
