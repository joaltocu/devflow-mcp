# DevFlow Troubleshooting Guide

This document covers common issues when using DevFlow MCP and how to resolve them.

## MCP Server Issues

### DevFlow MCP not showing in `/mcp`

**Symptoms:**
- Running `/mcp` in Claude Code doesn't show devflow
- DevFlow tools not available

**Diagnosis:**
```bash
# Check if .mcp.json exists in project root
ls -la /home/joseal/projects/joaltocu/framework/.mcp.json

# Or check user config
ls -la ~/.claude.json
```

**Solutions:**

1. **Create project MCP config:**
   ```bash
   cd /home/joseal/projects/joaltocu/framework
   cat > .mcp.json << 'EOF'
   {
     "mcpServers": {
       "devflow": {
         "command": "/home/joseal/projects/joaltocu/framework/run-mcp.sh",
         "args": []
       }
     }
   }
   EOF
   ```

2. **Verify run-mcp.sh is executable:**
   ```bash
   chmod +x /home/joseal/projects/joaltocu/framework/run-mcp.sh
   ```

3. **Restart Claude Code:**
   - MCP configs are loaded at startup
   - Exit and restart your agent

4. **Check MCP server manually:**
   ```bash
   cd /home/joseal/projects/joaltocu/framework
   ./run-mcp.sh
   # Should start without errors
   ```

### Only partial tools showing (4 instead of 6)

**Symptoms:**
- Only context tools visible (create_project, list_projects, get_project, update_project)
- Missing development tools (review_code, analyze_diff)

**Cause:**
- Multiple `@server.list_tools()` decorators in different files
- MCP only supports ONE handler - last one overwrites previous

**Verification:**
```bash
# Run inspection script
cd /home/joseal/projects/joaltocu/framework
python inspect_mcp.py
# Should show all 6 tools
```

**Solution:**
This was fixed in commit e6db64a with centralized tool registration in `src/devflow/tools/__init__.py`. If you still see this issue:

1. **Pull latest code:**
   ```bash
   git pull origin main
   ```

2. **Verify centralized registration exists:**
   ```bash
   grep -A 10 "def register_tools" src/devflow/tools/__init__.py
   ```

3. **Restart MCP server:**
   - Restart your Claude Code session
   - Or restart the MCP server manually

## Review Backend Issues

### Review fails with API error

**Symptoms:**
- `devflow review` fails with 401/403/404 errors
- "Invalid API key" or "Not found" messages

**Diagnosis:**
```bash
# Check environment variables
cd /home/joseal/projects/joaltocu/framework
cat .env

# Test configuration
python test_generic_llm.py
```

**Solutions by mode:**

**Mode A (Claude Code reviews):**
- No configuration needed
- Verify Claude Code is working: `claude --version`
- Ensure you're in a Claude Code session

**Mode B (Generic LLM - OpenAI-compatible):**

1. **Invalid API key (401 Unauthorized):**
   ```bash
   # Verify key is set correctly
   grep LLM_API_KEY .env
   # Should show: LLM_API_KEY=sk-...
   ```

2. **Wrong base URL (404 Not Found):**
   ```bash
   # Check base URL format
   grep LLM_BASE_URL .env
   # Should be: https://api.provider.com/v1
   # NOT: https://api.provider.com/v1/models ❌
   ```

   Common providers:
   - DeepSeek: `https://api.deepseek.com/v1`
   - OpenAI: `https://api.openai.com/v1`
   - GLM (via nan.builders): `https://api.nan.builders/v1`
   - Groq: `https://api.groq.com/openai/v1`

3. **Model not available (404/400):**
   ```bash
   # Check model name
   grep LLM_MODEL .env

   # Common models:
   # DeepSeek: deepseek-v4-flash, deepseek-chat
   # OpenAI: gpt-4-turbo, gpt-3.5-turbo
   # GLM: glm5.3-flash, glm-4
   ```

**Mode C (Anthropic API):**

1. **Invalid API key:**
   ```bash
   # Verify Anthropic key
   grep ANTHROPIC_API_KEY .env
   # Should start with: sk-ant-
   ```

2. **Rate limits:**
   - Wait a few minutes and retry
   - Check your Anthropic console for quota

**Network issues:**

1. **Firewall/VPN blocking API:**
   ```bash
   # Test connectivity
   curl https://api.nan.builders/v1/models \
     -H "Authorization: Bearer $LLM_API_KEY"
   ```

2. **Proxy required:**
   ```bash
   # Add to .env
   HTTP_PROXY=http://proxy:port
   HTTPS_PROXY=http://proxy:port
   ```

### Review returns empty or nonsensical issues

**Symptoms:**
- Review completes but shows no issues when there clearly are problems
- Issues are vague or hallucinated
- JSON parsing errors

**Diagnosis:**
Check LLM model compatibility with structured output (JSON mode).

**Solutions:**

1. **Model doesn't support JSON mode:**
   - See `references/llm-compatibility.md` for tested models
   - Switch to a known-compatible model:
     ```bash
     # In .env
     LLM_MODEL=deepseek-v4-flash  # Known good
     # or
     LLM_MODEL=gpt-4-turbo        # Known good
     ```

2. **Diff is too large:**
   - LLM context limits exceeded
   - Split into smaller reviews:
     ```bash
     # Review specific files
     git diff -- src/module1/ | devflow review
     git diff -- src/module2/ | devflow review
     ```

3. **Try a different model:**
   - DeepSeek v4 Flash → very fast, cheap, good quality
   - GPT-4 Turbo → slower, more expensive, best quality
   - Claude 3.5 Sonnet → via Anthropic API, excellent reasoning

## Database Issues

### Database errors on first use

**Symptoms:**
- "Unable to create database" errors
- Permission denied on `~/.devflow/`

**Solutions:**

1. **Create directory manually:**
   ```bash
   mkdir -p ~/.devflow
   chmod 755 ~/.devflow
   ```

2. **Check disk space:**
   ```bash
   df -h ~
   # Need at least 100MB free
   ```

3. **Check permissions:**
   ```bash
   ls -la ~/.devflow/
   # Should be writable by your user
   ```

### Database corruption

**Symptoms:**
- "database disk image is malformed"
- Unexpected errors reading review history

**Solutions:**

1. **Backup and recreate:**
   ```bash
   # Backup old database
   cp ~/.devflow/devflow.db ~/.devflow/devflow.db.backup

   # Remove corrupted database
   rm ~/.devflow/devflow.db

   # DevFlow will recreate on next use
   ```

2. **Try to recover:**
   ```bash
   # Dump and reload
   sqlite3 ~/.devflow/devflow.db .dump > backup.sql
   rm ~/.devflow/devflow.db
   sqlite3 ~/.devflow/devflow.db < backup.sql
   ```

### "Project not found" errors

**Symptoms:**
- Review fails with "Project with ID xxx not found"
- Can't find project UUID

**Diagnosis:**
```bash
# List all projects
sqlite3 ~/.devflow/devflow.db "SELECT id, name, path FROM projects;"
```

**Solutions:**

1. **UUID mismatch:**
   - Check `.devflow` file in project root:
     ```bash
     cat .devflow
     # Should show: PROJECT_ID=uuid-here
     ```
   - Compare with database:
     ```bash
     sqlite3 ~/.devflow/devflow.db \
       "SELECT id FROM projects WHERE name='your-project';"
     ```

2. **Re-register project:**
   - Use `context/create_project` MCP tool
   - Won't duplicate if name+path match

3. **Missing .devflow file:**
   - Find UUID from database:
     ```bash
     sqlite3 ~/.devflow/devflow.db \
       "SELECT id FROM projects WHERE path='/your/project/path';"
     ```
   - Recreate `.devflow`:
     ```bash
     echo "PROJECT_ID=uuid-from-query" > .devflow
     ```

## Git Integration Issues

### Git diff empty or incorrect

**Symptoms:**
- "No changes to review"
- Review runs but misses obvious changes

**Diagnosis:**
```bash
# Check what git sees
git status
git diff
git diff --cached
```

**Solutions:**

1. **No unstaged changes:**
   - You may have already staged everything
   - Use: `git diff --cached` for staged changes

2. **Untracked files:**
   - Git diff doesn't show new files until added
   - Stage them first: `git add .`

3. **Wrong branch:**
   - Verify you're on the correct branch:
     ```bash
     git branch --show-current
     ```

### Review ignores certain files

**Symptoms:**
- Some changed files not reviewed
- Only partial diff analyzed

**Causes:**
- `.gitignore` excludes them (correct behavior)
- Binary files (can't be reviewed)
- Submodules (not included in diff by default)

**Solutions:**

1. **Include submodule changes:**
   ```bash
   git diff --submodule=diff
   ```

2. **Review binary file metadata:**
   - DevFlow can't review binary content
   - Only metadata changes are shown

## Performance Issues

### Reviews are very slow (>60 seconds)

**Diagnosis:**
Identify which mode is active:
```bash
# Check .env
grep -E "LLM_API_KEY|ANTHROPIC_API_KEY" .env
```

**Solutions by mode:**

1. **Mode A (Claude Code subprocess):**
   - Inherently slower (~30-60s per review)
   - Each review spawns Claude Code subprocess
   - **Fix:** Switch to Mode B (API) for speed:
     ```bash
     # Add to .env
     LLM_API_KEY=sk-your-key
     LLM_BASE_URL=https://api.nan.builders/v1
     LLM_MODEL=deepseek-v4-flash  # Very fast
     ```

2. **Mode B (Generic LLM API):**
   - Check model speed:
     - DeepSeek v4 Flash: ~5-10s ✓ (fastest)
     - GPT-3.5 Turbo: ~10-15s ✓
     - GPT-4 Turbo: ~20-30s (slower but better)
   - **Fix:** Use faster model (deepseek-v4-flash)

3. **Mode C (Anthropic API):**
   - Claude models are thorough but slower
   - ~15-30s per review
   - **Fix:** Accept slower speed or switch to Mode B

4. **Large diffs:**
   - 500+ lines → slower
   - **Fix:** Review smaller chunks:
     ```bash
     git diff -- src/module1/ | devflow review
     ```

### High API costs

**Symptoms:**
- Unexpected API bills
- Want to reduce token usage

**Solutions:**

1. **Switch to cheaper models:**
   ```bash
   # DeepSeek v4 Flash: ~$0.001 per review
   LLM_MODEL=deepseek-v4-flash

   # vs GPT-4 Turbo: ~$0.10 per review
   ```

2. **Use Claude Code mode (free):**
   - Remove LLM_API_KEY and ANTHROPIC_API_KEY from .env
   - DevFlow uses your existing Claude Code access
   - Slower but no API cost

3. **Review smaller diffs:**
   - Stage and review incrementally
   - Don't batch multiple features in one review

## Installation Issues

### `run-mcp.sh` fails to start

**Symptoms:**
- "python: command not found"
- "No module named 'devflow'"

**Solutions:**

1. **Python not in PATH:**
   ```bash
   # Verify Python 3.11+
   python3 --version

   # Update run-mcp.sh to use python3
   sed -i 's/python /python3 /' run-mcp.sh
   ```

2. **Virtual environment not activated:**
   ```bash
   # Check if venv exists
   ls .venv/

   # Update run-mcp.sh to activate venv
   # Should have: source .venv/bin/activate
   ```

3. **Dependencies not installed:**
   ```bash
   cd /home/joseal/projects/joaltocu/framework
   pip install -e .
   ```

### Import errors when running

**Symptoms:**
- "ModuleNotFoundError: No module named 'mcp'"
- "ImportError: cannot import name 'Server'"

**Solutions:**

1. **Install MCP SDK:**
   ```bash
   pip install 'mcp>=1.0.0'
   ```

2. **Install all dependencies:**
   ```bash
   cd /home/joseal/projects/joaltocu/framework
   pip install -e .
   ```

3. **Check Python version:**
   ```bash
   python --version
   # Must be 3.11 or higher
   ```

## Getting Help

If none of these solutions work:

1. **Check logs:**
   ```bash
   # MCP server logs (if running in background)
   cat ~/.devflow/mcp.log
   ```

2. **Run test suite:**
   ```bash
   cd /home/joseal/projects/joaltocu/framework
   python test_generic_llm.py
   ```

3. **Inspect MCP tools:**
   ```bash
   python inspect_mcp.py
   # Should show all 6 tools with schemas
   ```

4. **Report an issue:**
   - Check existing issues: https://github.com/joaltocu/framework/issues
   - Include:
     - DevFlow version
     - Python version
     - Operating system
     - Full error message
     - .env configuration (redact API keys)
