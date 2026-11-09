# DevFlow Helper Scripts

This directory contains command-line helper scripts for DevFlow.

## Available Scripts

### register-project.sh

Register a new project with DevFlow from the command line.

**Usage:**
```bash
./register-project.sh /path/to/project
```

**What it does:**
- Auto-detects project name, language, and framework
- Finds git repository URL if available
- Creates project in DevFlow database
- Saves project UUID to `.devflow` file
- Adds `.devflow` to `.gitignore`

**Example:**
```bash
$ ./register-project.sh ~/projects/my-app

Project Information:
  Name: my-app
  Path: /home/user/projects/my-app
  Language: python
  Framework: fastapi
  Repository: git@github.com:user/my-app.git

Register this project with DevFlow? (y/n) y

✓ Project registered successfully!
  Project UUID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
✓ Saved UUID to .devflow
✓ Added .devflow to .gitignore

Next steps:
  1. Make some code changes
  2. Run: cd /home/user/projects/my-app && git diff
  3. Ask Claude Code to review with DevFlow
```

### review-history.sh

Query review history for your projects.

**Usage:**
```bash
# List all projects
./review-history.sh

# Show review history for a specific project
./review-history.sh PROJECT_ID [LIMIT]

# Show latest project's history
./review-history.sh latest
```

**What it shows:**
- Project summary (total reviews, pass rate)
- Recent review results with pass/fail status
- Issue breakdown by severity
- Quality trend over time

**Example:**
```bash
$ ./review-history.sh latest

Review History for: my-app
  Path: /home/user/projects/my-app
  Project ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890

Summary:
  Total reviews: 15
  Passed: 12
  Pass rate: 80.0%

Recent Reviews (last 10):
Date                  Status     Critical   High        Assessment
2024-01-15 14:30:22   ✓ PASS     0          0           ✓ Approved
2024-01-15 11:20:15   ✗ FAIL     1          2           🛑 Blocked
2024-01-14 16:45:33   ✓ PASS     0          1           ⚠ Needs work
...

Latest Review Issues:
  🔴 CRITICAL: 0
  🟠 HIGH: 0
  🟡 MEDIUM: 2
  🔵 LOW: 3

Quality Trend:
Date                  Critical   High       Medium     Low
2024-01-15 14:30:22   0          0          2          3
2024-01-15 11:20:15   1          2          3          1
...
```

## Installation

These scripts are located in the DevFlow skills directory and can be run directly:

```bash
cd /home/joseal/projects/joaltocu/framework/skills/devflow/scripts
./register-project.sh /path/to/project
./review-history.sh latest
```

Or add to your PATH for global access:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$PATH:/home/joseal/projects/joaltocu/framework/skills/devflow/scripts"

# Then use from anywhere
register-project.sh ~/my-new-project
review-history.sh latest
```

## Requirements

- DevFlow MCP installed and configured
- SQLite3 (for review-history.sh)
- Python 3.11+ with MCP SDK (for register-project.sh)
- Bash shell

## Troubleshooting

### Permission denied

```bash
chmod +x /home/joseal/projects/joaltocu/framework/skills/devflow/scripts/*.sh
```

### Database not found (review-history.sh)

Run at least one review first to create `~/.devflow/devflow.db`.

### MCP connection error (register-project.sh)

Verify DevFlow MCP is installed:
```bash
cd /home/joseal/projects/joaltocu/framework
./run-mcp.sh
# Should start without errors
```

## Notes

- These are convenience scripts - you can also use DevFlow through Claude Code conversationally
- All scripts use the same DevFlow database (`~/.devflow/devflow.db`)
- Scripts are safe to run multiple times (won't duplicate projects)
- `.devflow` file is local to your workspace (never commit to git)
