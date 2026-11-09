# Testing DevFlow MCP from Claude Code

## Step 1: Check MCP Status

In your Claude Code session, run:

```
/mcp
```

**Expected output:**
- You should see "devflow" listed
- It should show 6 tools available
- Status should be "Connected"

## Step 2: Test Context Tools

Try creating a test project:

Ask Claude Code:
> "Use the devflow MCP to create a test project called 'my-test-project' at path '/tmp/test-project' with language 'python'"

Claude Code should use the `context/create_project` tool and return the project UUID.

## Step 3: List Projects

Ask Claude Code:
> "List all projects in devflow"

Claude Code should use the `context/list_projects` tool and show your test project.

## Step 4: Test Development Tools (Advanced)

Create a simple git diff and ask for a review:

```bash
# In your terminal, create a test diff
cat > /tmp/test.diff << 'EOF'
diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
+password = "hardcoded123"
 def hello():
     print("Hello World")
 EOF
```

Then ask Claude Code:
> "Use devflow to review this code change: [paste the diff above]. Use project_id: [UUID from step 2]"

Claude Code should use `development/review_code` with your DeepSeek backend and return security issues about the hardcoded password.

## Troubleshooting

### MCP Not Appearing in /mcp

If devflow doesn't appear:

1. **Check Claude Code is restarted**
   - Close and reopen Claude Code

2. **Check server starts manually**
   ```bash
   cd /home/joseal/projects/joaltocu/framework
   ./run-mcp.sh
   ```
   Should show: "DevFlow MCP Server ready"

3. **Check logs**
   Claude Code shows MCP connection errors in its output

### MCP Shows "Disconnected"

If it shows but status is disconnected:

1. Check the script is executable:
   ```bash
   ls -la /home/joseal/projects/joaltocu/framework/run-mcp.sh
   ```
   Should show `x` permissions

2. Test the script directly:
   ```bash
   /home/joseal/projects/joaltocu/framework/run-mcp.sh
   ```

3. Check Python dependencies:
   ```bash
   pip list | grep -E "(mcp|anthropic|sqlalchemy)"
   ```

### Tools Not Working

If MCP connects but tools fail:

1. Check .env file exists:
   ```bash
   ls -la /home/joseal/projects/joaltocu/framework/.env
   ```

2. Check DeepSeek API key is valid:
   ```bash
   cd /home/joseal/projects/joaltocu/framework
   python test_generic_llm.py
   ```

## Success Indicators

✅ `/mcp` shows devflow with 6 tools
✅ Can create and list projects
✅ Can run code reviews using DeepSeek
✅ All results stored in ~/.devflow/devflow.db

Your DevFlow MCP is working correctly!
