# DevFlow MCP - Quick Start Guide

## Overview

DevFlow MCP is now loaded in your Claude Code session! You have access to 6 powerful tools for development workflow automation.

## Available Tools

### Development Tools (Code Review)

**1. development/review_code**
- Comprehensive code review using DeepSeek v4 Flash
- Analyzes: code quality, security, architecture, test coverage
- Returns: structured issues with severity levels and suggestions

**2. development/analyze_diff**
- Extract structured information from git diffs
- Returns: file changes, statistics, affected lines

### Context Tools (Project Management)

**3. context/create_project**
- Register a new project in DevFlow database
- Returns: project UUID for future operations

**4. context/list_projects**
- List all registered projects
- Returns: project list with metadata

**5. context/get_project**
- Get detailed project information
- Returns: full project context

**6. context/update_project**
- Update project metadata
- Returns: updated project info

## Common Workflows

### Workflow 1: First-Time Setup

**Step 1: Create a project for your codebase**

Ask Claude Code:
> "Use DevFlow MCP to create a project for this codebase. Name it 'framework', path is '/home/joseal/projects/joaltocu/framework', language is 'python', framework is 'mcp', and repository URL is 'git@github.com:joaltocu/devflow-mcp.git'"

Claude Code will use `context/create_project` and return a UUID.

**Step 2: Save the project ID**

Note down the UUID returned - you'll need it for reviews!

### Workflow 2: Code Review

**Step 1: Get your git diff**

```bash
# In your terminal
git diff > /tmp/my-changes.diff
# Or for staged changes:
git diff --cached > /tmp/my-changes.diff
```

**Step 2: Ask for a review**

> "Use DevFlow to review the changes in /tmp/my-changes.diff for project ID [your-uuid]. Run all review types."

Claude Code will:
- Read the diff file
- Call `development/review_code` with DeepSeek backend
- Return structured review with issues categorized by severity

**Step 3: Review the results**

The review will show:
- **Critical issues**: Security vulnerabilities, major bugs
- **High issues**: Design problems, significant concerns
- **Medium issues**: Code quality improvements
- **Low issues**: Minor suggestions
- **Info**: General observations

### Workflow 3: Quick Project Check

**List all your projects:**

> "Show me all projects in DevFlow"

**Get project details:**

> "Get details for project [uuid] from DevFlow"

### Workflow 4: Automated Pre-Commit Review

**Create a habit:**

Before committing, ask:
> "Review my staged changes using DevFlow for project [uuid]"

This will catch issues before they get committed!

## Example Session

```
You: Use DevFlow to create a project for this codebase at /home/joseal/projects/my-app

Claude: I'll create a project in DevFlow...
[Uses context/create_project]
✅ Project created! UUID: a1b2c3d4-e5f6-7890-abcd-ef1234567890

You: Review my changes in /tmp/changes.diff for that project

Claude: I'll review your changes using DeepSeek...
[Uses development/review_code]

Review Results:
- 2 critical issues found:
  1. Hardcoded API key in config.py:15
  2. SQL injection vulnerability in query.py:42

- 3 medium issues found:
  1. Missing error handling in api.py:28
  2. Inconsistent naming convention
  3. Unused import in utils.py

Would you like me to help fix these issues?
```

## Tips for Best Results

### 1. Be Specific with Project Context

When creating projects, provide as much context as possible:
- Accurate language and framework
- Repository URL for reference
- Any special metadata (monorepo structure, etc.)

### 2. Review Frequently

Don't wait until you have 1000 lines changed:
- Review after each feature
- Review before committing
- Review before creating PRs

### 3. Use All Review Types

The default reviews all four aspects:
- **code_quality**: Style, maintainability, best practices
- **security**: Vulnerabilities, OWASP top 10
- **architecture**: Design patterns, separation of concerns
- **coverage**: Missing tests, edge cases

### 4. Check the Database

Your review history is stored:

```bash
sqlite3 ~/.devflow/devflow.db "SELECT * FROM reviews ORDER BY created_at DESC LIMIT 5;"
```

All reviews are searchable and analyzable!

## Advanced Usage

### Custom Review Types

Ask for specific review aspects:
> "Use DevFlow to run only security and architecture reviews on this diff"

### Review Without Project

If you just want a quick analysis:
> "Use DevFlow to analyze this diff" (uses development/analyze_diff)

### Project Management

Update project metadata:
> "Update the framework project in DevFlow to add 'sqlalchemy' to the metadata"

## Understanding Results

### Review Structure

```json
{
  "success": true,
  "reviews": [
    {
      "type": "security",
      "passed": false,
      "issues": [
        {
          "severity": "critical",
          "file": "config.py",
          "line": 15,
          "message": "Hardcoded API key detected",
          "suggestion": "Move to environment variables",
          "category": "credentials"
        }
      ]
    }
  ],
  "synthesized": {
    "overall_assessment": "NEEDS_WORK",
    "critical_issues": 2,
    "summary": "..."
  }
}
```

### Severity Levels

- **CRITICAL**: Must fix before committing (security holes, data loss)
- **HIGH**: Should fix soon (bugs, design flaws)
- **MEDIUM**: Good to improve (code quality, maintainability)
- **LOW**: Nice to have (minor improvements)
- **INFO**: For your information (observations)

## Your Setup

✅ **Backend**: DeepSeek v4 Flash via OpenAI-compatible API
✅ **Database**: SQLite at ~/.devflow/devflow.db
✅ **MCP Server**: Running via run-mcp.sh
✅ **Tools**: 6 tools available (2 development + 4 context)

## Troubleshooting

### "Tool not found"

If Claude Code says a DevFlow tool isn't available:
- Run `/mcp` to verify DevFlow is connected
- Restart Claude Code if needed

### "Review failed"

If reviews fail:
1. Check your .env file has DeepSeek credentials
2. Test manually: `python test_generic_llm.py`
3. Check API quota/limits

### "Database error"

If database operations fail:
1. Check ~/.devflow/ directory exists
2. Check permissions: `ls -la ~/.devflow/`
3. Reinitialize: Delete ~/.devflow/devflow.db and retry

## Next Steps

1. **Create your first project** in DevFlow
2. **Run a review** on some changes
3. **Explore the database** to see what's stored
4. **Set up pre-commit hooks** to automate reviews

Your DevFlow MCP is ready to make your development workflow more efficient!

## Questions?

Check the documentation:
- Complete guide: `README_MCP.md`
- Getting started: `GETTING_STARTED.md`
- Architecture: `ARCHITECTURE_MCP.md`
