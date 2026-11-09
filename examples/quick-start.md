# DevFlow MCP - Quick Start (5 Minutes)

Get DevFlow running and review your first code in 5 minutes.

## Step 1: Start the Server (30 seconds)

```bash
cd /home/joseal/projects/joaltocu/framework
./run-mcp.sh
```

Leave this running in a terminal.

## Step 2: Configure Claude Code (1 minute)

Edit `~/.config/claude/mcp.json`:

```json
{
  "mcpServers": {
    "devflow": {
      "command": "/home/joseal/projects/joaltocu/framework/run-mcp.sh"
    }
  }
}
```

Restart Claude Code.

## Step 3: Create a Project (1 minute)

In Claude Code, call the tool:

**Tool:** `context/create_project`

**Input:**
```json
{
  "name": "my-first-project",
  "path": "/home/joseal/projects/my-first-project",
  "language": "python"
}
```

**Save the project ID** from the response!

## Step 4: Review Some Code (2 minutes)

**Tool:** `development/review_code`

**Input:**
```json
{
  "project_id": "<paste project id here>",
  "diff": "diff --git a/test.py b/test.py\nnew file mode 100644\nindex 0000000..abcd123\n--- /dev/null\n+++ b/test.py\n@@ -0,0 +1,5 @@\n+def add(a, b):\n+    return a + b\n+\n+password = \"admin123\"\n+API_KEY = \"sk-12345\"",
  "review_types": ["code_quality", "security"]
}
```

**Result:** DevFlow will find the security issues (hardcoded secrets)!

## Step 5: Inspect the Data (30 seconds)

```bash
sqlite3 ~/.devflow/devflow.db "SELECT * FROM projects;"
sqlite3 ~/.devflow/devflow.db "SELECT type, result FROM reviews LIMIT 1;"
```

## Done!

You now have:
- ✅ DevFlow MCP server running
- ✅ A project in the database
- ✅ Your first code review completed
- ✅ All data stored in `~/.devflow/devflow.db`

## What's Next?

- See `complete-workflow.md` for detailed examples
- Try reviewing real code from your projects
- Explore the database to see what's being learned
- Add `ANTHROPIC_API_KEY` to `.env` to try faster API reviews

## Available Tools

You now have access to:

**Context Management:**
- `context/create_project` - Register projects
- `context/list_projects` - See all projects
- `context/get_project` - Get project details
- `context/update_project` - Update metadata

**Code Review:**
- `development/review_code` - Multi-stage review
- `development/analyze_diff` - Parse git diffs

## Common Issues

**"Tool not found"**
- Make sure you restarted Claude Code after editing mcp.json
- Check that the server is running

**"Project not found"**
- Use `context/list_projects` to see all project IDs
- Make sure you're using the UUID, not the name

**"Review fails"**
- Check that your diff is valid (copy from `git diff`)
- Ensure project_id is a valid UUID

## Next Steps

1. Register your real projects using `context/create_project`
2. Make changes to your code
3. Run `git diff` to get the diff
4. Review with `development/review_code`
5. Fix issues and review again!
