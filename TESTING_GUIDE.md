# Testing DevFlow MCP with Claude Code

## Step-by-Step Testing Guide

### Step 1: Configure Claude Code

Edit your MCP configuration file at `~/.config/claude/mcp.json`:

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

**Note:** If the file doesn't exist, create it with the above content.

### Step 2: Start DevFlow MCP Server

In a separate terminal, start the server:

```bash
cd /home/joseal/projects/joaltocu/framework
./run-mcp.sh
```

You should see:
```
Starting DevFlow MCP Server...
Database initialized
Registering MCP tools...
Registering MCP resources...
DevFlow MCP Server ready
Serving over stdio...
```

**Leave this terminal running!**

### Step 3: Restart Claude Code

If Claude Code is already running, restart it to load the new MCP configuration.

### Step 4: Verify DevFlow Tools are Available

In Claude Code, you should now see DevFlow MCP tools available:

**Context Tools:**
- `context/create_project`
- `context/list_projects`
- `context/get_project`
- `context/update_project`

**Development Tools:**
- `development/review_code`
- `development/analyze_diff`

### Step 5: Test Creating a Project

Ask Claude Code to call the `context/create_project` tool:

**Example request to Claude Code:**
```
Please use the context/create_project tool to register this DevFlow project:
- Name: "devflow-mcp"
- Path: "/home/joseal/projects/joaltocu/framework"
- Language: "python"
- Repository: "git@github.com:joaltocu/devflow-mcp.git"
```

**Expected result:**
```json
{
  "success": true,
  "project": {
    "id": "some-uuid-here",
    "name": "devflow-mcp",
    "path": "/home/joseal/projects/joaltocu/framework",
    "language": "python",
    ...
  },
  "message": "Project 'devflow-mcp' created successfully"
}
```

**Save the project ID!** You'll need it for the next step.

### Step 6: Test Listing Projects

Ask Claude Code:
```
Use context/list_projects to show all registered projects
```

**Expected result:**
```json
{
  "success": true,
  "count": 1,
  "projects": [
    {
      "id": "your-project-id",
      "name": "devflow-mcp",
      "path": "/home/joseal/projects/joaltocu/framework",
      "language": "python",
      ...
    }
  ]
}
```

### Step 7: Test Code Review

Create a simple test file with intentional issues:

```bash
cat > /tmp/test-code.py << 'EOF'
def add(a, b):
    return a + b

# Security issue: hardcoded credentials
API_KEY = "sk-12345678"
PASSWORD = "admin123"

# Missing documentation
def process_data(data):
    result = []
    for x in data:
        result.append(x * 2)
    return result
EOF
```

Get the diff:
```bash
cd /tmp
git init
git add test-code.py
git diff --cached
```

Copy the diff output, then ask Claude Code:
```
Use development/review_code to review this code:

Project ID: <paste-your-project-id>
Diff: <paste-the-git-diff>
Review types: ["code_quality", "security"]
```

**Expected result:**
- Security issues flagged (hardcoded secrets)
- Code quality suggestions (missing docs)
- Synthesis of all findings
- Results stored in database

### Step 8: Verify Data in Database

In a separate terminal:

```bash
# List all projects
sqlite3 ~/.devflow/devflow.db "SELECT id, name, language FROM projects;"

# List all reviews
sqlite3 ~/.devflow/devflow.db "SELECT type, created_at FROM reviews;"

# Check for critical security issues
sqlite3 ~/.devflow/devflow.db "
  SELECT file_path, line_number, message
  FROM review_issues
  WHERE severity = 'CRITICAL';
"
```

**Expected result:**
- One project entry
- Review records
- Security issues about hardcoded secrets

### Step 9: Test on Real Code (Optional)

If you want to test with real code from one of your projects:

1. Register the project with `context/create_project`
2. Make some changes to the code
3. Run `git diff` in that project
4. Ask Claude Code to review the diff

---

## Troubleshooting

### "DevFlow tools not showing up"

**Check:**
1. Is the server running? (check the terminal)
2. Did you restart Claude Code after editing mcp.json?
3. Is the path correct in mcp.json?

**Test manually:**
```bash
# This should show logs
./run-mcp.sh
```

### "Server won't start"

**Check logs for errors:**
```bash
./run-mcp.sh 2>&1 | head -20
```

**Common issues:**
- Missing dependencies: `pip install -r requirements.txt`
- Database permissions: `chmod 755 ~/.devflow/`

### "Tool calls fail"

**Check server logs** in the terminal where run-mcp.sh is running. Errors will appear there.

### "No data in database"

**Verify database exists:**
```bash
ls -lah ~/.devflow/
sqlite3 ~/.devflow/devflow.db ".tables"
```

---

## What to Test

### Must Test (Core Functionality):
- ✅ Create a project
- ✅ List projects
- ✅ Review code with security issues
- ✅ Verify data persists

### Nice to Test (Full Features):
- Get project details
- Update project metadata
- Review with all 4 review types
- Review real code from your projects

---

## Success Criteria

You'll know it's working when:

1. **Server starts** without errors
2. **Claude Code shows DevFlow tools** in available tools
3. **Projects can be created** and listed
4. **Code reviews work** and find issues
5. **Data appears in database** when queried

---

## After Testing

Once everything works:

1. **Use it for real!**
   - Register your 22 projects
   - Review code before commits
   - Build up the knowledge base

2. **Optional enhancements:**
   - Implement GitHub tools (PR creation)
   - Implement knowledge tools (pattern learning)
   - Add more review types

3. **Share feedback:**
   - What works well?
   - What's missing?
   - What would make it more useful?

---

## Quick Reference

**Start server:**
```bash
./run-mcp.sh
```

**Check database:**
```bash
sqlite3 ~/.devflow/devflow.db "SELECT * FROM projects;"
```

**MCP config location:**
```
~/.config/claude/mcp.json
```

**Database location:**
```
~/.devflow/devflow.db
```

---

Ready to test! Follow the steps above and let me know if you hit any issues.
