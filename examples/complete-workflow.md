# DevFlow MCP - Complete Workflow Example

This example shows the **complete end-to-end workflow** for using DevFlow MCP with Claude Code.

## Setup (One Time)

### 1. Start DevFlow MCP Server

```bash
cd /home/joseal/projects/joaltocu/framework
./run-mcp.sh
```

Server output:
```
Starting DevFlow MCP Server...
Database initialized
Registering MCP tools...
Registering MCP resources...
DevFlow MCP Server ready
Serving over stdio...
```

### 2. Configure Claude Code

Add to `~/.config/claude/mcp.json`:

```json
{
  "mcpServers": {
    "devflow": {
      "command": "/home/joseal/projects/joaltocu/framework/run-mcp.sh",
      "args": [],
      "env": {}
    }
  }
}
```

Restart Claude Code to load the server.

---

## Workflow: Review Code for a Project

### Step 1: Create a Project

Use the `context/create_project` tool to register your project:

```json
{
  "name": "my-app",
  "path": "/home/joseal/projects/my-app",
  "language": "python",
  "framework": "fastapi",
  "repository_url": "git@github.com:myuser/my-app.git"
}
```

**Response:**
```json
{
  "success": true,
  "project": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "my-app",
    "path": "/home/joseal/projects/my-app",
    "language": "python",
    "framework": "fastapi",
    "repository_url": "git@github.com:myuser/my-app.git",
    "metadata": null,
    "created_at": "2024-10-29T12:00:00"
  },
  "message": "Project 'my-app' created successfully"
}
```

**Save the project ID** - you'll need it for reviews!

### Step 2: Make Some Code Changes

```bash
cd /home/joseal/projects/my-app
# Make changes to your code
git add .
```

### Step 3: Get the Diff

```bash
git diff --staged > /tmp/my-changes.diff
```

Or use `git diff HEAD` for uncommitted changes.

### Step 4: Review Your Code

Use the `development/review_code` tool:

```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "diff": "<paste your git diff here>",
  "review_types": ["code_quality", "security", "architecture", "coverage"],
  "context": {
    "branch": "feature/new-endpoint",
    "author": "joseal"
  }
}
```

**What happens:**

1. **DevFlow analyzes the diff**
   - Extracts changed files
   - Counts additions/deletions
   - Identifies modification types

2. **Review agents run** (automatic backend selection)
   - If no `ANTHROPIC_API_KEY` → Uses Claude Code reviewers
   - If API key set → Uses Anthropic API reviewers
   - All 4 review types run in parallel

3. **Results synthesized**
   - Issues deduplicated
   - Conflicts resolved
   - Prioritized by severity

4. **Stored in database**
   - Review record created
   - All issues saved
   - Linked to project

**Response:**
```json
{
  "success": true,
  "reviews": [
    {
      "reviewer_name": "Code Quality (Claude Code)",
      "passed": true,
      "summary": "Code follows Python best practices. Minor naming improvements suggested.",
      "issues": [
        {
          "severity": "LOW",
          "file": "src/api/users.py",
          "line": 42,
          "message": "Variable name 'usr' is too abbreviated",
          "suggestion": "Use 'user' for clarity",
          "category": "naming"
        }
      ]
    },
    {
      "reviewer_name": "Security (Claude Code)",
      "passed": false,
      "summary": "Found 1 critical security issue",
      "issues": [
        {
          "severity": "CRITICAL",
          "file": "src/api/auth.py",
          "line": 15,
          "message": "Hardcoded API key detected",
          "suggestion": "Move to environment variable",
          "category": "secrets"
        }
      ]
    },
    {
      "reviewer_name": "Architecture (Claude Code)",
      "passed": true,
      "summary": "Changes align with project architecture",
      "issues": []
    },
    {
      "reviewer_name": "Test Coverage (Claude Code)",
      "passed": false,
      "summary": "New endpoint lacks test coverage",
      "issues": [
        {
          "severity": "MEDIUM",
          "file": "src/api/users.py",
          "line": 35,
          "message": "New endpoint POST /users has no tests",
          "suggestion": "Add tests for success and error cases",
          "category": "coverage"
        }
      ]
    }
  ],
  "synthesized": {
    "reviewer_name": "Synthesis",
    "passed": false,
    "summary": "Found 1 critical issue, 1 medium issue, 1 low issue. Address critical security concern before merging.",
    "issues": [
      {
        "severity": "CRITICAL",
        "message": "Hardcoded API key in auth.py:15 - MUST FIX",
        "priority": 1
      },
      {
        "severity": "MEDIUM",
        "message": "Missing tests for new endpoint - SHOULD FIX",
        "priority": 2
      },
      {
        "severity": "LOW",
        "message": "Variable naming in users.py:42 - NICE TO FIX",
        "priority": 3
      }
    ]
  },
  "analysis": {
    "files_changed": 3,
    "additions": 45,
    "deletions": 12,
    "files": ["src/api/users.py", "src/api/auth.py", "tests/test_users.py"]
  }
}
```

### Step 5: Fix Issues

Based on the review:

1. **Fix the critical security issue:**
   ```python
   # Before (auth.py:15)
   API_KEY = "sk-12345678"

   # After
   import os
   API_KEY = os.getenv("API_KEY")
   ```

2. **Add tests:**
   ```python
   # tests/test_users.py
   def test_create_user():
       response = client.post("/users", json={"name": "test"})
       assert response.status_code == 201
   ```

3. **Improve naming (optional):**
   ```python
   # Before
   usr = get_user(id)

   # After
   user = get_user(id)
   ```

### Step 6: Review Again

Get a new diff and review again:

```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "diff": "<new diff with fixes>",
  "review_types": ["code_quality", "security"]
}
```

This time all reviews should pass!

### Step 7: Inspect Your Data

```bash
# See all your projects
sqlite3 ~/.devflow/devflow.db "SELECT id, name, language FROM projects;"

# See review history for this project
sqlite3 ~/.devflow/devflow.db "
  SELECT type, created_at, result->>'summary' as summary
  FROM reviews
  WHERE project_id = '550e8400-e29b-41d4-a716-446655440000'
  ORDER BY created_at DESC;
"

# See all critical issues ever found
sqlite3 ~/.devflow/devflow.db "
  SELECT file_path, line_number, message
  FROM review_issues
  WHERE severity = 'CRITICAL'
  ORDER BY created_at DESC;
"
```

---

## Alternative: List All Projects

Use `context/list_projects` to see all registered projects:

```json
{}
```

**Response:**
```json
{
  "success": true,
  "count": 3,
  "projects": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "my-app",
      "path": "/home/joseal/projects/my-app",
      "language": "python",
      "framework": "fastapi",
      "repository_url": "git@github.com:myuser/my-app.git",
      "created_at": "2024-10-29T12:00:00"
    },
    {
      "id": "660f9511-f3ac-52e5-b827-557766551111",
      "name": "rust-cli",
      "path": "/home/joseal/projects/rust-cli",
      "language": "rust",
      "framework": null,
      "repository_url": "git@github.com:myuser/rust-cli.git",
      "created_at": "2024-10-28T10:30:00"
    },
    {
      "id": "770g0622-g4bd-63f6-c938-668877662222",
      "name": "react-dashboard",
      "path": "/home/joseal/projects/react-dashboard",
      "language": "javascript",
      "framework": "react",
      "repository_url": "git@github.com:myuser/react-dashboard.git",
      "created_at": "2024-10-27T09:15:00"
    }
  ]
}
```

---

## Alternative: Get Project Details

Use `context/get_project` to see detailed information:

```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Alternative: Update Project

Use `context/update_project` to modify project metadata:

```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "extra_metadata": {
    "team": "backend",
    "priority": "high",
    "last_deploy": "2024-10-29"
  }
}
```

---

## Using from Different Agents

### From GPT-4 (via MCP client)

```python
import mcp

# Connect to DevFlow
client = mcp.Client("devflow", command="/path/to/run-mcp.sh")

# Create project
result = client.call_tool("context/create_project", {
    "name": "gpt-project",
    "path": "/path/to/project"
})

# Review code
review = client.call_tool("development/review_code", {
    "project_id": result["project"]["id"],
    "diff": diff_content
})
```

### From Custom Python Agent

```python
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def use_devflow():
    # Start DevFlow MCP server
    server_params = StdioServerParameters(
        command="/home/joseal/projects/joaltocu/framework/run-mcp.sh"
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()

            # List tools
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")

            # Create project
            result = await session.call_tool(
                "context/create_project",
                {
                    "name": "my-project",
                    "path": "/path/to/project",
                    "language": "python"
                }
            )
            print(result)
```

---

## Multi-Machine Workflow

If using NAS storage:

**Machine 1 (Laptop):**
```bash
# Mount NAS
sudo mount -t cifs //nas-ip/home /mnt/nas -o credentials=~/.nascreds

# Symlink database
ln -s /mnt/nas/.devflow ~/.devflow

# Run server
./run-mcp.sh

# Create project, do reviews
# All data goes to NAS
```

**Machine 2 (Desktop):**
```bash
# Same setup
ln -s /mnt/nas/.devflow ~/.devflow
./run-mcp.sh

# Same projects available!
# All review history accessible!
```

---

## Complete Tool Reference

### Context Tools ✅

| Tool | Purpose | Status |
|------|---------|--------|
| `context/create_project` | Register a new project | ✅ Working |
| `context/list_projects` | List all projects | ✅ Working |
| `context/get_project` | Get project details | ✅ Working |
| `context/update_project` | Update project metadata | ✅ Working |

### Development Tools ✅

| Tool | Purpose | Status |
|------|---------|--------|
| `development/review_code` | Multi-stage code review | ✅ Working |
| `development/analyze_diff` | Analyze git diff | ✅ Working |

### GitHub Tools 🚧

| Tool | Purpose | Status |
|------|---------|--------|
| `github/create_pr` | Create pull request | 🚧 Not yet exposed |
| `github/post_review` | Post review comments | 🚧 Not yet exposed |

### Knowledge Tools 🚧

| Tool | Purpose | Status |
|------|---------|--------|
| `knowledge/query` | Search knowledge base | 🚧 Not implemented |
| `knowledge/store_pattern` | Save learned pattern | 🚧 Not implemented |

---

## Troubleshooting

### Server won't start

```bash
# Check Python path
PYTHONPATH=/home/joseal/projects/joaltocu/framework/src python -c "import devflow"

# Check database directory
ls -la ~/.devflow/

# Check dependencies
pip list | grep -E "(mcp|anthropic|sqlalchemy)"
```

### Tool not found

```bash
# In Claude Code, list available tools
# DevFlow tools should appear as:
# - context/create_project
# - context/list_projects
# - context/get_project
# - context/update_project
# - development/review_code
# - development/analyze_diff
```

### Review fails

```bash
# Check logs in terminal where server is running
# Common issues:
# - Invalid project_id (not a UUID)
# - Empty diff (no changes to review)
# - Claude Code not installed (if no API key)
```

---

## Next Steps

1. **Try it yourself** - Create a test project and review some code
2. **Explore the database** - See what data is being stored
3. **Try both backends** - Test with Claude Code, then add API key to compare
4. **Multi-project** - Register all your projects, see patterns emerge

---

## Key Insights

**What makes DevFlow holistic:**

1. **Any agent can use it** - Claude Code, GPT-4, custom agents all call same tools
2. **All data centralized** - One database at `~/.devflow/devflow.db`
3. **Learning accumulates** - Patterns from all projects stored together
4. **Flexible backend** - Works with Claude Code (free) or API (paid)
5. **You own everything** - Database is a single SQLite file you control

**The workflow pattern:**
```
Register Project → Make Changes → Review → Fix → Review Again → Data Stored
                                                                      ↓
                                                            Patterns Learned
                                                                      ↓
                                                          Future Reviews Better
```

This is the power of a holistic system - every review improves the next one!
