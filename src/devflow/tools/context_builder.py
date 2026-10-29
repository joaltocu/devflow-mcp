"""Build context for code reviews."""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional


class ContextBuilder:
    """Gathers context needed for code reviews."""

    def __init__(self, project_root: Path, config: Any) -> None:
        """Initialize context builder.

        Args:
            project_root: Root directory of the project
            config: Configuration object
        """
        self.project_root = project_root
        self.config = config

    def build_context(self) -> Dict[str, Any]:
        """Build complete review context.

        Returns:
            Dictionary containing all review context
        """
        context: Dict[str, Any] = {}

        # Detect language and framework
        context["language"] = self._detect_language()
        context["framework"] = self._detect_framework()

        # Load architecture documentation
        arch_doc_path = self.config.get(
            "reviewers.architecture.architecture_doc", "docs/ARCHITECTURE.md"
        )
        context["architecture_docs"] = self._load_file(arch_doc_path)

        # Load ADRs
        adr_path = self.config.get("reviewers.architecture.adr_path", "docs/adr")
        context["adrs"] = self._load_adrs(adr_path)

        # Load style guide
        style_guide = self.config.get("reviewers.code_quality.style_guide", "")
        if style_guide:
            context["style_guide"] = style_guide

        # Run coverage if configured
        if self.config.get("reviewers.test_coverage.enabled"):
            context["coverage"] = self._run_coverage()

        # Get minimum coverage threshold
        context["minimum_coverage"] = self.config.get(
            "reviewers.test_coverage.minimum_coverage", 80
        )

        return context

    def _detect_language(self) -> str:
        """Detect primary programming language."""
        # Check for common language indicators
        indicators = {
            "python": ["requirements.txt", "setup.py", "pyproject.toml"],
            "javascript": ["package.json", "package-lock.json"],
            "typescript": ["tsconfig.json"],
            "rust": ["Cargo.toml"],
            "go": ["go.mod"],
            "java": ["pom.xml", "build.gradle"],
            "ruby": ["Gemfile"],
            "php": ["composer.json"],
        }

        for lang, files in indicators.items():
            for file in files:
                if (self.project_root / file).exists():
                    return lang

        return "unknown"

    def _detect_framework(self) -> str:
        """Detect framework being used."""
        language = self._detect_language()

        # Python frameworks
        if language == "python":
            if (self.project_root / "requirements.txt").exists():
                requirements = (self.project_root / "requirements.txt").read_text()
                if "django" in requirements.lower():
                    return "django"
                elif "flask" in requirements.lower():
                    return "flask"
                elif "fastapi" in requirements.lower():
                    return "fastapi"

            if (self.project_root / "pyproject.toml").exists():
                pyproject = (self.project_root / "pyproject.toml").read_text()
                if "django" in pyproject.lower():
                    return "django"
                elif "flask" in pyproject.lower():
                    return "flask"
                elif "fastapi" in pyproject.lower():
                    return "fastapi"

        # JavaScript/TypeScript frameworks
        elif language in ("javascript", "typescript"):
            if (self.project_root / "package.json").exists():
                try:
                    package = json.loads(
                        (self.project_root / "package.json").read_text()
                    )
                    deps = {
                        **package.get("dependencies", {}),
                        **package.get("devDependencies", {}),
                    }

                    if "next" in deps:
                        return "nextjs"
                    elif "react" in deps:
                        return "react"
                    elif "vue" in deps:
                        return "vue"
                    elif "express" in deps:
                        return "express"
                except json.JSONDecodeError:
                    pass

        return "unknown"

    def _load_file(self, relative_path: str) -> str:
        """Load a file from the project.

        Args:
            relative_path: Path relative to project root

        Returns:
            File contents or empty string if not found
        """
        file_path = self.project_root / relative_path
        if file_path.exists() and file_path.is_file():
            return file_path.read_text()
        return ""

    def _load_adrs(self, relative_path: str) -> list[Dict[str, str]]:
        """Load Architecture Decision Records.

        Args:
            relative_path: Path to ADR directory relative to project root

        Returns:
            List of ADRs with file name and content
        """
        adrs = []
        adr_dir = self.project_root / relative_path

        if not adr_dir.exists() or not adr_dir.is_dir():
            return adrs

        for adr_file in sorted(adr_dir.glob("*.md")):
            adrs.append(
                {
                    "file": adr_file.name,
                    "content": adr_file.read_text(),
                }
            )

        return adrs

    def _run_coverage(self) -> Dict[str, Any]:
        """Run coverage tool and parse results.

        Returns:
            Coverage data including overall percentage and per-file coverage
        """
        coverage_command = self.config.get(
            "reviewers.test_coverage.coverage_command",
            "pytest --cov=src --cov-report=json",
        )

        try:
            # Run coverage command
            result = subprocess.run(
                coverage_command.split(),
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Try to parse JSON coverage report
            coverage_json = self.project_root / "coverage.json"
            if coverage_json.exists():
                with open(coverage_json) as f:
                    data = json.load(f)

                overall = data.get("totals", {}).get("percent_covered", 0)

                files_coverage = {}
                for file_path, file_data in data.get("files", {}).items():
                    files_coverage[file_path] = file_data.get(
                        "summary", {}
                    ).get("percent_covered", 0)

                # Find files with low coverage
                low_coverage_files = [
                    path
                    for path, coverage in files_coverage.items()
                    if coverage < 60
                ]

                return {
                    "overall": overall,
                    "files": files_coverage,
                    "low_coverage_files": low_coverage_files,
                }

        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pass

        return {}
