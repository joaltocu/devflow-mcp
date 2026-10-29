"""Configuration management with hierarchical loading."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import toml
from dotenv import load_dotenv


class Config:
    """Hierarchical configuration system.

    Configuration precedence (lowest to highest):
    1. Defaults (hardcoded)
    2. Global config (~/.config/devflow/config.toml)
    3. Project config (.devflow.toml in project root)
    4. Environment variables (DEVFLOW_*)
    """

    _defaults: Dict[str, Any] = {
        "project": {
            "name": "",
            "language": "",
            "framework": "",
        },
        "agents": {
            "development": {
                "model": "claude-sonnet-4-5-20250929",
                "budget_tokens": 100000,
            },
            "review": {
                "model": "claude-sonnet-4-5-20250929",
                "parallel": True,
            },
        },
        "reviewers": {
            "code_quality": {
                "enabled": True,
                "style_guide": "",
            },
            "security": {
                "enabled": True,
                "auto_scan_secrets": True,
                "tools": ["bandit", "semgrep"],
            },
            "architecture": {
                "enabled": True,
                "architecture_doc": "docs/ARCHITECTURE.md",
                "adr_path": "docs/adr",
            },
            "test_coverage": {
                "enabled": True,
                "minimum_coverage": 80,
                "coverage_command": "pytest --cov=src --cov-report=json",
            },
        },
        "github": {
            "auto_create_pr": True,
            "pr_template": ".github/pull_request_template.md",
            "review_as_comments": True,
        },
    }

    def __init__(self, project_root: Optional[Path] = None) -> None:
        """Initialize configuration.

        Args:
            project_root: Root directory of the project. Defaults to current directory.
        """
        self.project_root = project_root or Path.cwd()
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from all sources."""
        # Start with defaults
        self._config = self._deep_copy(self._defaults)

        # Load global config
        global_config_path = Path.home() / ".config" / "devflow" / "config.toml"
        if global_config_path.exists():
            global_config = toml.load(global_config_path)
            self._merge_config(self._config, global_config)

        # Load project config
        project_config_path = self.project_root / ".devflow.toml"
        if project_config_path.exists():
            project_config = toml.load(project_config_path)
            self._merge_config(self._config, project_config)

        # Load environment variables
        load_dotenv(self.project_root / ".env")
        self._load_env_vars()

    def _load_env_vars(self) -> None:
        """Load configuration from environment variables."""
        # Map environment variables to config keys
        env_mappings = {
            "DEVFLOW_MODEL": ("agents", "development", "model"),
            "DEVFLOW_REVIEW_MODEL": ("agents", "review", "model"),
            "DEVFLOW_BUDGET_TOKENS": ("agents", "development", "budget_tokens"),
            "DEVFLOW_MIN_COVERAGE": ("reviewers", "test_coverage", "minimum_coverage"),
            "DEVFLOW_AUTO_PR": ("github", "auto_create_pr"),
        }

        for env_var, key_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert value to appropriate type
                if value.lower() in ("true", "false"):
                    value = value.lower() == "true"
                elif value.isdigit():
                    value = int(value)

                # Set value in config
                self._set_nested(self._config, key_path, value)

    def _deep_copy(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Create a deep copy of a dictionary."""
        result: Dict[str, Any] = {}
        for key, value in d.items():
            if isinstance(value, dict):
                result[key] = self._deep_copy(value)
            else:
                result[key] = value
        return result

    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Merge override config into base config."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def _set_nested(self, d: Dict[str, Any], keys: tuple[str, ...], value: Any) -> None:
        """Set a value in a nested dictionary."""
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation.

        Args:
            key_path: Dot-separated path to config value (e.g., "agents.development.model")
            default: Default value if key not found

        Returns:
            Configuration value or default

        Example:
            >>> config.get("agents.development.model")
            "claude-sonnet-4-5-20250929"
        """
        keys = key_path.split(".")
        value = self._config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any) -> None:
        """Set a configuration value using dot notation.

        Args:
            key_path: Dot-separated path to config value
            value: Value to set
        """
        keys = key_path.split(".")
        self._set_nested(self._config, tuple(keys), value)

    def save_project_config(self) -> None:
        """Save current configuration to project .devflow.toml file."""
        project_config_path = self.project_root / ".devflow.toml"
        with open(project_config_path, "w") as f:
            toml.dump(self._config, f)

    @property
    def config(self) -> Dict[str, Any]:
        """Get the entire configuration dictionary."""
        return self._config
