# Getting Started with DevFlow MCP

## Quick Start (5 minutes)

### 1. Choose Your Review Backend

DevFlow supports **two modes** for code reviews:

**Mode A: Claude Code Reviews (Recommended for getting started)**
- ✅ No API key required
- ✅ Uses your existing Claude Code access
- ✅ No additional costs
- Best for: Getting started, testing, personal projects

**Mode B: Anthropic API Reviews**
- ⚡ Faster parallel reviews
- 💰 Costs API tokens
- Best for: High-volume usage, production

### 2. Configure Environment

Edit `.env`:

```bash
# Optional: For faster API-based reviews (Mode B)
# Leave blank to use Claude Code reviews (Mode A)
ANTHROPIC_API_KEY=sk-ant-xxx

# Required for GitHub operations
GITHUB_TOKEN=ghp_xxx
```

**Important:** If you don't set `ANTHROPIC_API_KEY`, DevFlow will automatically use Claude Code for reviews. No API key needed!

### 2. Run the MCP Server

```bash
cd /home/joseal/projects/joaltocu/framework
./run-mcp.sh
```

The server will:
- Create database at `~/.devflow/devflow.db`
- Start listening for MCP requests over stdio
- Wait for connections from MCP clients

### 3. Connect from Claude Code

Add this to your Claude Code MCP configuration (`~/.config/claude/mcp.json`):

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

Restart Claude Code and the DevFlow MCP tools will be available.

## What Can You Do?

### Review Code

```python
# From any MCP-compatible agent:
result = mcp.call_tool("development/review_code", {
    "project_id": "uuid-here",
    "diff": git_diff,
    "review_types": ["code_quality", "security", "architecture", "coverage"]
})
```

### Query Your Database

```bash
# Inspect your data anytime
sqlite3 ~/.devflow/devflow.db

# List all projects
sqlite3 ~/.devflow/devflow.db "SELECT * FROM projects;"

# See recent reviews
sqlite3 ~/.devflow/devflow.db "SELECT * FROM reviews ORDER BY created_at DESC LIMIT 10;"

# Check learned patterns
sqlite3 ~/.devflow/devflow.db "SELECT pattern_name, effectiveness_score FROM patterns ORDER BY effectiveness_score DESC;"
```

## Database Location

By default: `~/.devflow/devflow.db`

**Want it on NAS?**

```bash
# Create directory on NAS
mkdir -p /mnt/nas/.devflow

# Symlink from home
ln -s /mnt/nas/.devflow ~/.devflow

# Run server (database now on NAS)
./run-mcp.sh
```

## Troubleshooting

### Server won't start

```bash
# Check Python path
PYTHONPATH=/home/joseal/projects/joaltocu/framework/src python -c "import devflow; print(devflow.__version__)"

# Should print: DevFlow version: 0.1.0
```

### Database not created

```bash
# Create directory manually
mkdir -p ~/.devflow

# Check permissions
ls -la ~/.devflow
```

### Missing dependencies

```bash
# Install dependencies
pip install anthropic httpx sqlalchemy aiosqlite pydantic python-dotenv rich mcp
```

## Understanding the Holistic Design

DevFlow is **holistic** at multiple levels:

### Level 1: Any Agent Can Use DevFlow
```
Claude Code     →  \
GPT-4 Agent     →   → DevFlow MCP  → Central Database
Custom Agent    →  /
```

All agents call the same MCP tools and write to your central database.

### Level 2: DevFlow Uses Internal Agents for Reviews
```
DevFlow receives review request
    ↓
If ANTHROPIC_API_KEY set:
    → Use Anthropic API reviewers (fast, costs tokens)
Else:
    → Use Claude Code reviewers (free, uses your access)
    ↓
Results stored in central database
```

### Level 3: All Data Centralized
```
~/.devflow/devflow.db
    ↑
All reviews, all agents, all projects
    ↑
Patterns learned, knowledge accumulated
```

**Key Insight:** The external agent calling DevFlow doesn't know or care how reviews are implemented internally. They just call `development/review_code` and get results. All data accumulates in one place regardless of which agents are used.

## How the Review Modes Work

**Mode A: Claude Code Reviews**
```
External Agent → DevFlow → Claude Code (subprocess) → Results → Database
                                ↓
                    Writes diff to file, asks Claude Code to review
```

**Mode B: API Reviews**
```
External Agent → DevFlow → Anthropic API → Results → Database
                                ↓
                    Sends request to Claude API directly
```

Both modes produce the same structured results. The difference is performance and cost.

## Next Steps

1. **Test with a project**: Create a project in the database and run a code review
2. **Explore the data**: Query the SQLite database to see what's being stored
3. **Try both modes**: Test with Claude Code first, then add API key to compare
4. **Setup NAS**: Move database to NAS for multi-machine access

## Documentation

- **Complete guide**: `README_MCP.md`
- **Architecture**: `ARCHITECTURE_MCP.md`
- **Database**: `DATABASE.md`
- **Portability**: `PORTABILITY.md`
- **Quick reference**: `QUICK_REFERENCE.md`

## Example: First Review

```bash
# 1. Start the server in one terminal
./run-mcp.sh

# 2. In Claude Code (or another MCP client), use the tool:
#    - Create a project
#    - Get a git diff
#    - Call development/review_code
#    - Review results are stored in ~/.devflow/devflow.db

# 3. Inspect the results
sqlite3 ~/.devflow/devflow.db "SELECT * FROM reviews;"
```

## Your Data, Your Control

- **All data** in one file: `~/.devflow/devflow.db`
- **Backup**: `cp ~/.devflow/devflow.db ~/backup/`
- **Export**: Use standard SQLite tools
- **Portable**: Move the .db file anywhere

You completely own this system. No cloud dependencies for your data.
