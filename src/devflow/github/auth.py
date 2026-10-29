"""GitHub authentication handling."""

import os
import subprocess
from typing import Optional


class GitHubAuth:
    """Handles GitHub authentication."""

    def __init__(self) -> None:
        """Initialize GitHub authentication."""
        self._token: Optional[str] = None

    def get_token(self) -> str:
        """Get GitHub authentication token.

        Returns:
            GitHub token

        Raises:
            RuntimeError: If token cannot be obtained
        """
        if self._token:
            return self._token

        # Try to get token from gh CLI
        try:
            result = subprocess.run(
                ["gh", "auth", "token"],
                capture_output=True,
                text=True,
                check=True,
            )
            self._token = result.stdout.strip()
            if self._token:
                return self._token
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Fallback to GITHUB_TOKEN environment variable
        self._token = os.getenv("GITHUB_TOKEN")
        if self._token:
            return self._token

        raise RuntimeError(
            "GitHub token not found. Please authenticate with 'gh auth login' "
            "or set GITHUB_TOKEN environment variable."
        )

    def validate_token(self) -> bool:
        """Validate that the token is valid.

        Returns:
            True if token is valid, False otherwise
        """
        try:
            token = self.get_token()
            # Try to use gh CLI to validate
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except RuntimeError:
            return False

    def get_repo_info(self) -> dict[str, str]:
        """Get information about the current repository.

        Returns:
            Dictionary with owner and repo name

        Raises:
            RuntimeError: If not in a git repository or no remote found
        """
        try:
            # Get remote URL
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True,
                text=True,
                check=True,
            )

            remote_url = result.stdout.strip()

            # Parse GitHub URL
            # Formats: https://github.com/owner/repo.git or git@github.com:owner/repo.git
            if "github.com" in remote_url:
                # Extract owner and repo
                if remote_url.startswith("https://"):
                    # https://github.com/owner/repo.git
                    parts = remote_url.replace("https://github.com/", "").replace(".git", "").split("/")
                elif "@github.com:" in remote_url:
                    # git@github.com:owner/repo.git
                    parts = remote_url.split(":")[1].replace(".git", "").split("/")
                else:
                    raise RuntimeError(f"Unrecognized GitHub URL format: {remote_url}")

                if len(parts) >= 2:
                    return {
                        "owner": parts[0],
                        "repo": parts[1],
                    }

            raise RuntimeError(f"Not a GitHub repository: {remote_url}")

        except subprocess.CalledProcessError:
            raise RuntimeError("Not in a git repository or no remote found")
