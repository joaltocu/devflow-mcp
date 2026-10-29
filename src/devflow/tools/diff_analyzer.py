"""Parse and analyze git diffs."""

import re
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class FileChange:
    """Represents a change to a single file."""

    file_path: str
    change_type: str  # added, modified, deleted
    additions: int
    deletions: int
    diff_content: str


class DiffAnalyzer:
    """Analyze git diffs to extract structured information."""

    def __init__(self, diff_text: str) -> None:
        """Initialize diff analyzer.

        Args:
            diff_text: Raw git diff output
        """
        self.diff_text = diff_text
        self.file_changes: List[FileChange] = []
        self._parse_diff()

    def _parse_diff(self) -> None:
        """Parse the diff text into structured file changes."""
        # Split diff into file sections
        file_sections = re.split(r"^diff --git ", self.diff_text, flags=re.MULTILINE)

        for section in file_sections[1:]:  # Skip first empty section
            self._parse_file_section(section)

    def _parse_file_section(self, section: str) -> None:
        """Parse a single file's diff section."""
        lines = section.split("\n")

        if not lines:
            return

        # Extract file paths from first line: a/path/to/file b/path/to/file
        first_line = lines[0]
        file_match = re.search(r"a/(.+?)\s+b/(.+)", first_line)

        if not file_match:
            return

        file_path = file_match.group(2)  # Use 'b' path (destination)

        # Determine change type
        change_type = "modified"
        if any("new file mode" in line for line in lines[:10]):
            change_type = "added"
        elif any("deleted file mode" in line for line in lines[:10]):
            change_type = "deleted"

        # Count additions and deletions
        additions = sum(1 for line in lines if line.startswith("+") and not line.startswith("+++"))
        deletions = sum(1 for line in lines if line.startswith("-") and not line.startswith("---"))

        # Reconstruct file's diff content
        diff_content = "\n".join(lines)

        self.file_changes.append(
            FileChange(
                file_path=file_path,
                change_type=change_type,
                additions=additions,
                deletions=deletions,
                diff_content=diff_content,
            )
        )

    def get_changed_files(self) -> List[str]:
        """Get list of changed file paths.

        Returns:
            List of file paths that were changed
        """
        return [change.file_path for change in self.file_changes]

    def get_added_files(self) -> List[str]:
        """Get list of newly added files.

        Returns:
            List of file paths that were added
        """
        return [
            change.file_path
            for change in self.file_changes
            if change.change_type == "added"
        ]

    def get_modified_files(self) -> List[str]:
        """Get list of modified files.

        Returns:
            List of file paths that were modified
        """
        return [
            change.file_path
            for change in self.file_changes
            if change.change_type == "modified"
        ]

    def get_deleted_files(self) -> List[str]:
        """Get list of deleted files.

        Returns:
            List of file paths that were deleted
        """
        return [
            change.file_path
            for change in self.file_changes
            if change.change_type == "deleted"
        ]

    def get_stats(self) -> Dict[str, int]:
        """Get overall diff statistics.

        Returns:
            Dictionary with file counts and line change counts
        """
        return {
            "files_changed": len(self.file_changes),
            "files_added": len(self.get_added_files()),
            "files_modified": len(self.get_modified_files()),
            "files_deleted": len(self.get_deleted_files()),
            "total_additions": sum(change.additions for change in self.file_changes),
            "total_deletions": sum(change.deletions for change in self.file_changes),
        }

    def to_dict(self) -> Dict:
        """Convert diff analysis to dictionary.

        Returns:
            Dictionary representation of the diff analysis
        """
        return {
            "diff": self.diff_text,
            "stats": self.get_stats(),
            "changed_files": self.get_changed_files(),
            "added_files": self.get_added_files(),
            "modified_files": self.get_modified_files(),
            "deleted_files": self.get_deleted_files(),
            "file_changes": [
                {
                    "file_path": change.file_path,
                    "change_type": change.change_type,
                    "additions": change.additions,
                    "deletions": change.deletions,
                }
                for change in self.file_changes
            ],
        }
