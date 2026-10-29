"""State management for DevFlow workflow runs."""

import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class WorkflowRun:
    """Represents a single workflow run."""

    id: str
    branch: str
    commit_sha: str
    stage: str
    status: str  # pending, in_progress, completed, failed
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None


class StateManager:
    """Manages workflow state in SQLite database."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        """Initialize state manager.

        Args:
            db_path: Path to SQLite database. Defaults to ./devflow.db
        """
        self.db_path = db_path or Path.cwd() / "devflow.db"
        self._init_database()

    def _init_database(self) -> None:
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_runs (
                id TEXT PRIMARY KEY,
                branch TEXT NOT NULL,
                commit_sha TEXT NOT NULL,
                stage TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                error_message TEXT
            )
        """)

        conn.commit()
        conn.close()

    def create_run(self, branch: str, commit_sha: str) -> WorkflowRun:
        """Create a new workflow run.

        Args:
            branch: Git branch name
            commit_sha: Git commit SHA

        Returns:
            Created workflow run
        """
        run = WorkflowRun(
            id=str(uuid.uuid4()),
            branch=branch,
            commit_sha=commit_sha,
            stage="develop",
            status="pending",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO workflow_runs
            (id, branch, commit_sha, stage, status, created_at, updated_at, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run.id,
                run.branch,
                run.commit_sha,
                run.stage,
                run.status,
                run.created_at.isoformat(),
                run.updated_at.isoformat(),
                run.error_message,
            ),
        )

        conn.commit()
        conn.close()

        return run

    def get_run(self, run_id: str) -> Optional[WorkflowRun]:
        """Get a workflow run by ID.

        Args:
            run_id: Workflow run ID

        Returns:
            Workflow run or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM workflow_runs WHERE id = ?",
            (run_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_run(row)

    def update_run(
        self,
        run_id: str,
        stage: Optional[str] = None,
        status: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Update a workflow run.

        Args:
            run_id: Workflow run ID
            stage: New stage (optional)
            status: New status (optional)
            error_message: Error message (optional)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = []
        params = []

        if stage is not None:
            updates.append("stage = ?")
            params.append(stage)

        if status is not None:
            updates.append("status = ?")
            params.append(status)

        if error_message is not None:
            updates.append("error_message = ?")
            params.append(error_message)

        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())

        params.append(run_id)

        cursor.execute(
            f"UPDATE workflow_runs SET {', '.join(updates)} WHERE id = ?",
            params,
        )

        conn.commit()
        conn.close()

    def list_runs(self, limit: int = 10) -> List[WorkflowRun]:
        """List recent workflow runs.

        Args:
            limit: Maximum number of runs to return

        Returns:
            List of workflow runs, ordered by created_at descending
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM workflow_runs ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_run(row) for row in rows]

    def get_latest_run(self, branch: Optional[str] = None) -> Optional[WorkflowRun]:
        """Get the latest workflow run, optionally filtered by branch.

        Args:
            branch: Optional branch name to filter by

        Returns:
            Latest workflow run or None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if branch:
            cursor.execute(
                "SELECT * FROM workflow_runs WHERE branch = ? ORDER BY created_at DESC LIMIT 1",
                (branch,),
            )
        else:
            cursor.execute(
                "SELECT * FROM workflow_runs ORDER BY created_at DESC LIMIT 1"
            )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_run(row)

    def delete_run(self, run_id: str) -> None:
        """Delete a workflow run.

        Args:
            run_id: Workflow run ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM workflow_runs WHERE id = ?", (run_id,))

        conn.commit()
        conn.close()

    def _row_to_run(self, row: tuple) -> WorkflowRun:
        """Convert database row to WorkflowRun object."""
        return WorkflowRun(
            id=row[0],
            branch=row[1],
            commit_sha=row[2],
            stage=row[3],
            status=row[4],
            created_at=datetime.fromisoformat(row[5]),
            updated_at=datetime.fromisoformat(row[6]),
            error_message=row[7],
        )
