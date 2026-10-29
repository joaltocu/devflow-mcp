"""GitHub pull request manager."""

import subprocess
from pathlib import Path
from typing import Optional

import httpx

from devflow.github.auth import GitHubAuth
from devflow.reviewers.base import ReviewResult


class PRManager:
    """Manages GitHub pull requests."""

    def __init__(self, project_root: Path) -> None:
        """Initialize PR manager.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root
        self.auth = GitHubAuth()

    async def create_pr(
        self,
        branch: str,
        title: str,
        body: str,
        base: str = "main",
    ) -> str:
        """Create a pull request.

        Args:
            branch: Source branch
            title: PR title
            body: PR description
            base: Base branch (default: main)

        Returns:
            PR URL

        Raises:
            RuntimeError: If PR creation fails
        """
        # First, push the branch to remote
        try:
            subprocess.run(
                ["git", "push", "-u", "origin", branch],
                cwd=self.project_root,
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to push branch: {e.stderr.decode()}")

        # Create PR using gh CLI
        try:
            result = subprocess.run(
                [
                    "gh",
                    "pr",
                    "create",
                    "--base",
                    base,
                    "--head",
                    branch,
                    "--title",
                    title,
                    "--body",
                    body,
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )

            pr_url = result.stdout.strip()
            return pr_url

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to create PR: {e.stderr}")

    async def post_review_comments(
        self,
        pr_number: int,
        review_result: ReviewResult,
    ) -> None:
        """Post review comments on a pull request.

        Args:
            pr_number: PR number
            review_result: Review result with issues

        Raises:
            RuntimeError: If posting comments fails
        """
        if not review_result.issues:
            # No issues, post approval comment
            await self._post_pr_comment(
                pr_number,
                f"✅ **{review_result.reviewer_name} Review**: {review_result.summary}",
            )
            return

        # Get repo info
        repo_info = self.auth.get_repo_info()
        owner = repo_info["owner"]
        repo = repo_info["repo"]

        # Get commit SHA for the PR
        commit_sha = await self._get_pr_head_sha(pr_number, owner, repo)

        # Format review body
        review_body = f"## {review_result.reviewer_name}\n\n"
        review_body += f"{review_result.summary}\n\n"

        if review_result.issues:
            review_body += "### Issues Found:\n\n"

            # Group issues by severity
            for severity_name in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
                severity_issues = [
                    issue for issue in review_result.issues
                    if issue.severity.value.upper() == severity_name
                ]

                if severity_issues:
                    emoji = {
                        "CRITICAL": "🔴",
                        "HIGH": "🟠",
                        "MEDIUM": "🟡",
                        "LOW": "🔵",
                        "INFO": "ℹ️",
                    }[severity_name]

                    review_body += f"\n#### {emoji} {severity_name}\n\n"

                    for issue in severity_issues:
                        review_body += f"- **{issue.file or 'General'}**"
                        if issue.line:
                            review_body += f" (line {issue.line})"
                        review_body += f": {issue.message}\n"
                        if issue.suggestion:
                            review_body += f"  - *Suggestion*: {issue.suggestion}\n"
                        review_body += "\n"

        # Post review comment
        await self._post_pr_comment(pr_number, review_body)

    async def _get_pr_head_sha(self, pr_number: int, owner: str, repo: str) -> str:
        """Get the HEAD SHA for a pull request.

        Args:
            pr_number: PR number
            owner: Repository owner
            repo: Repository name

        Returns:
            Commit SHA
        """
        token = self.auth.get_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                },
            )

            if response.status_code != 200:
                raise RuntimeError(f"Failed to get PR info: {response.text}")

            data = response.json()
            return data["head"]["sha"]

    async def _post_pr_comment(self, pr_number: int, body: str) -> None:
        """Post a comment on a pull request.

        Args:
            pr_number: PR number
            body: Comment body
        """
        repo_info = self.auth.get_repo_info()
        owner = repo_info["owner"]
        repo = repo_info["repo"]
        token = self.auth.get_token()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                },
                json={"body": body},
            )

            if response.status_code != 201:
                raise RuntimeError(f"Failed to post comment: {response.text}")

    def get_pr_number_from_branch(self, branch: str) -> Optional[int]:
        """Get PR number for a branch.

        Args:
            branch: Branch name

        Returns:
            PR number or None if not found
        """
        try:
            result = subprocess.run(
                ["gh", "pr", "view", branch, "--json", "number", "--jq", ".number"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )

            return int(result.stdout.strip())

        except (subprocess.CalledProcessError, ValueError):
            return None
