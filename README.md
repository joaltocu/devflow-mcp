# DevFlow

Agent-driven development framework with autonomous multi-stage code review and GitHub integration.

## Overview

DevFlow is a standalone CLI tool that automates your development workflow using AI agents:

1. **Development**: Claude Code agent implements your feature
2. **Review**: Specialized agents review for quality, security, architecture, and test coverage
3. **Synthesis**: AI consolidates all reviews into actionable feedback
4. **PR Creation**: Automatically creates pull request with review comments

## Features

- **Hybrid Agent Architecture**: Claude Code for development, custom API agents for specialized reviews
- **4-Stage Review Process**:
  - Code Quality (style, patterns, maintainability)
  - Security (OWASP Top 10, secrets, vulnerabilities)
  - Architecture (design patterns, ADR compliance)
  - Test Coverage (completeness, edge cases)
- **Intelligent Synthesis**: Deduplicates issues, resolves conflicts, prioritizes by impact
- **GitHub Integration**: Creates PRs and posts review comments
- **Local-First**: Runs on your machine, no cloud infrastructure needed
- **Resumable Workflows**: State persistence for interrupted runs

## Installation

### Prerequisites

- Python 3.11 or higher
- Claude CLI (`claude`) installed
- GitHub CLI (`gh`) installed and authenticated
- Git repository

### Install DevFlow

```bash
# Clone the repository
cd /home/joseal/projects/joaltocu/framework

# Install in development mode
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

### Configure Environment

```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Authenticate with GitHub (if not already done)
gh auth login
```

## Quick Start

```bash
# 1. Initialize DevFlow in your project
cd /path/to/your/project
devflow init

# 2. Run a development task
devflow dev "Add user authentication with JWT tokens"

# 3. Check workflow status
devflow status

# 4. Review staged changes only (without development)
git add .
devflow review
```

## Configuration

DevFlow uses hierarchical configuration with the following precedence:

1. Defaults (hardcoded)
2. Global config: `~/.config/devflow/config.toml`
3. Project config: `.devflow.toml` (in project root)
4. Environment variables: `DEVFLOW_*`

### Example `.devflow.toml`

```toml
[project]
name = "my-app"
language = "python"
framework = "fastapi"

[agents.development]
model = "claude-sonnet-4-5-20250929"
budget_tokens = 100000

[agents.review]
model = "claude-sonnet-4-5-20250929"
parallel = true  # Run reviews in parallel

[reviewers.code_quality]
enabled = true
style_guide = "docs/STYLE_GUIDE.md"

[reviewers.security]
enabled = true
auto_scan_secrets = true
tools = ["bandit", "semgrep"]

[reviewers.architecture]
enabled = true
architecture_doc = "docs/ARCHITECTURE.md"
adr_path = "docs/adr"

[reviewers.test_coverage]
enabled = true
minimum_coverage = 80
coverage_command = "pytest --cov=src --cov-report=json"

[github]
auto_create_pr = true
pr_template = ".github/pull_request_template.md"
review_as_comments = true
```

## CLI Commands

### `devflow init`

Initialize DevFlow in a project.

```bash
devflow init [--path /path/to/project]
```

Creates `.devflow.toml` and initializes state database.

### `devflow dev`

Run full development workflow.

```bash
devflow dev "task description" [OPTIONS]

Options:
  --path, -p PATH      Project root directory
  --no-pr              Skip PR creation
  --pr-title TEXT      Custom PR title
```

Example:

```bash
devflow dev "Implement password reset functionality"
devflow dev "Fix bug in checkout flow" --no-pr
```

### `devflow review`

Run code reviews on staged changes.

```bash
devflow review [--path /path/to/project]
```

Useful for reviewing code without running development agent.

### `devflow status`

Show workflow run status.

```bash
devflow status [OPTIONS]

Options:
  --path, -p PATH      Project root directory
  --limit, -n NUMBER   Number of runs to show (default: 10)
```

### `devflow resume`

Resume a failed workflow (NOT YET IMPLEMENTED).

```bash
devflow resume RUN_ID
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI (Typer)                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    Workflow Engine                          │
│  - State management (SQLite)                                │
│  - Progress tracking                                        │
│  - Error handling                                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                 Agent Orchestrator                          │
│  - Coordinates all agents                                   │
│  - Builds context                                           │
│  - Analyzes diffs                                           │
└───┬────────────────────────┬─────────────────────────┬──────┘
    │                        │                         │
    ▼                        ▼                         ▼
┌───────────┐    ┌──────────────────────┐    ┌────────────────┐
│  Claude   │    │  Review Agents       │    │   Synthesis    │
│   Code    │    │  - Code Quality      │    │     Agent      │
│   Agent   │    │  - Security          │    │  (Opus 4.5)    │
│           │    │  - Architecture      │    │                │
│           │    │  - Test Coverage     │    │                │
└───────────┘    └──────────────────────┘    └────────────────┘
```

## Workflow Stages

1. **Development** (`develop`)
   - Claude Code agent implements the task
   - Captures git diff of changes

2. **Review** (`review`)
   - Runs 4 specialized reviewers in parallel
   - Each reviewer analyzes code for specific concerns
   - Builds context from architecture docs, ADRs, etc.

3. **Synthesis** (`synthesis`)
   - Opus 4.5 model consolidates all reviews
   - Deduplicates issues
   - Resolves conflicts
   - Prioritizes by severity

4. **PR Creation** (`create_pr`)
   - Pushes branch to GitHub
   - Creates pull request via `gh` CLI
   - Posts review comments via GitHub API

## Review Categories

### Code Quality

- Style consistency
- Naming conventions
- Documentation completeness
- Maintainability
- Best practices for language/framework

### Security

- OWASP Top 10 vulnerabilities
- Hardcoded secrets (API keys, passwords)
- SQL injection, XSS, CSRF
- Authentication/authorization flaws
- Dependency vulnerabilities

### Architecture

- Design pattern adherence
- ADR compliance
- Module boundaries
- Dependency direction
- SOLID principles

### Test Coverage

- New code has tests
- Edge cases covered
- Test quality
- Coverage thresholds met

## Development

### Setup Development Environment

```bash
# Clone the repo
cd /home/joseal/projects/joaltocu/framework

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check src/

# Run type checker
mypy src/
```

### Project Structure

```
framework/
├── src/devflow/
│   ├── cli/              # CLI interface
│   ├── core/             # Config, state, workflow
│   ├── agents/           # Agent coordination
│   ├── reviewers/        # Review agents
│   ├── github/           # GitHub integration
│   └── tools/            # Utilities
├── tests/                # Test suite
├── docs/                 # Documentation
└── examples/             # Example configs
```

## Troubleshooting

### Claude Code not found

```bash
# Install Claude CLI
# Follow instructions at: https://claude.com/claude-code
```

### GitHub token issues

```bash
# Re-authenticate with gh CLI
gh auth login

# Or set token manually
export GITHUB_TOKEN="your-token"
```

### API key not found

```bash
# Set Anthropic API key
export ANTHROPIC_API_KEY="your-key"

# Or add to .env file in project root
echo "ANTHROPIC_API_KEY=your-key" >> .env
```

### Reviews failing to parse

The review agents expect structured JSON responses. If parsing fails:

1. Check your API key is valid
2. Verify model availability
3. Check logs for specific errors

## Roadmap

- [ ] Resume workflow functionality
- [ ] Web UI for workflow visualization
- [ ] Language-specific reviewers (Python, Rust, JS)
- [ ] Eval suite for review quality
- [ ] Integration with CI/CD pipelines
- [ ] Custom reviewer plugins

## Contributing

Contributions welcome! This is an early-stage project.

## License

MIT

## Credits

Built with:
- [Claude Code](https://claude.com/claude-code) - AI-powered development
- [Anthropic API](https://anthropic.com) - Claude models
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal UI
