# DevFlow MCP Server - Quick Reference

## One-Minute Overview

**What**: Holistic development infrastructure you own
**How**: MCP server + SQLite database
**For**: ANY agent (Claude, GPT, custom)
**Where**: Database at `~/.devflow/devflow.db`

## Installation (30 seconds)

```bash
cd /home/joseal/projects/joaltocu/framework
pip install -e .
devflow-mcp
```

Done! Server running, database at `~/.devflow/devflow.db`

## Key Locations

```
Code:     /home/joseal/projects/joaltocu/framework/
Database: ~/.devflow/devflow.db
Docs:     README_MCP.md (start here)
```

## Make it a Git Repo (1 minute)

```bash
cd /home/joseal/projects/joaltocu/framework
./scripts/setup-repo.sh

# Optional: Push to GitHub
git remote add origin git@github.com:joaltocu/devflow-mcp.git
git push -u origin main
```

## Setup NAS Storage (2 minutes)

```bash
# Mount NAS
sudo mount -t cifs //nas-ip/home /mnt/nas -o credentials=~/.nascreds

# Symlink database to NAS
mkdir -p /mnt/nas/.devflow
ln -s /mnt/nas/.devflow ~/.devflow

# Run (database now on NAS)
devflow-mcp
```

## Use from Any Agent

```python
# Review code
result = mcp.call_tool("development/review_code", {
    "project_id": "uuid",
    "diff": git_diff,
    "review_types": ["code_quality", "security"]
})

# Query knowledge
knowledge = mcp.call_tool("knowledge/query", {
    "query": "How to handle JWT tokens?",
    "category": "security"
})

# Create PR
pr = mcp.call_tool("github/create_pr", {
    "project_id": "uuid",
    "title": "Add authentication",
    "body": "..."
})
```

## Database Tables (You Own This Data)

```sql
-- Your 22 projects
SELECT * FROM projects;

-- Every review
SELECT * FROM reviews ORDER BY created_at DESC;

-- Learned patterns (THE MAGIC!)
SELECT pattern_name, effectiveness_score, usage_count
FROM patterns ORDER BY effectiveness_score DESC;

-- Knowledge base
SELECT * FROM knowledge_base WHERE category = 'security';
```

## Inspect Your Data

```bash
# Open database
sqlite3 ~/.devflow/devflow.db

# Quick queries
sqlite3 ~/.devflow/devflow.db "SELECT COUNT(*) FROM reviews;"
sqlite3 ~/.devflow/devflow.db "SELECT * FROM projects;"

# Export to CSV
sqlite3 -header -csv ~/.devflow/devflow.db "SELECT * FROM patterns;" > patterns.csv
```

## Backup

```bash
# Simple
cp ~/.devflow/devflow.db ~/backups/devflow-$(date +%Y%m%d).db

# Or if on NAS: automatic backups via NAS snapshots
```

## Multi-Machine Setup

```bash
# Machine 1 (laptop):
git clone git@github.com:joaltocu/devflow-mcp.git
pip install -e .
ln -s /mnt/nas/.devflow ~/.devflow
devflow-mcp

# Machine 2 (desktop):
git clone git@github.com:joaltocu/devflow-mcp.git
pip install -e .
ln -s /mnt/nas/.devflow ~/.devflow  # Same database!
devflow-mcp
```

## Key Files

| File | Purpose |
|------|---------|
| `README_MCP.md` | **START HERE** - Complete user guide |
| `ARCHITECTURE_MCP.md` | Architecture deep dive |
| `DATABASE.md` | Database storage options |
| `PORTABILITY.md` | Git & multi-machine setup |
| `SESSION_SUMMARY.md` | What we built (this session) |
| `IMPLEMENTATION_STATUS.md` | Current status & next steps |

## Environment Variables

```bash
# Database location (optional - default is good)
export DEVFLOW_DATABASE_URL="sqlite+aiosqlite:///~/.devflow/devflow.db"

# For reviews (required)
export ANTHROPIC_API_KEY="your-key"

# For GitHub (required for PR operations)
export GITHUB_TOKEN="your-token"
```

## What's Working Now

✅ MCP server core
✅ Database (7 tables)
✅ Example tool: `development/review_code`
✅ All review services
✅ Complete documentation

## What's Pending

🚧 GitHub tools (`github/create_pr`, etc.)
🚧 Knowledge tools (`knowledge/query`, etc.)
🚧 MCP resources
🚧 Example clients

## Troubleshooting

**Server won't start**
```bash
# Check database location
ls -la ~/.devflow/

# Check permissions
chmod 755 ~/.devflow/
```

**Database not found**
```bash
# Create directory
mkdir -p ~/.devflow/

# Check symlink (if using NAS)
ls -la ~ | grep devflow
```

**Import errors**
```bash
# Reinstall
pip install -e .
```

## Architecture

```
Any Agent → MCP Tools → DevFlow Server → Database (YOU OWN)
         ↑                                    ↓
         └──── MCP Resources ←────────────────┘
```

## Key Insight

**This is not just a tool - it's your personal development knowledge base that learns from all 22 projects.**

Every review stores:
- What was reviewed
- What issues were found
- What patterns worked
- What knowledge was gained

Future reviews get **smarter** based on past experience.

## Next Steps

1. **Start using**: `pip install -e . && devflow-mcp`
2. **Make it a repo**: `./scripts/setup-repo.sh`
3. **Setup NAS**: Symlink `~/.devflow` to NAS
4. **Connect agents**: Use MCP tools from any agent

## Support

- **Documentation**: See `README_MCP.md`
- **Architecture**: See `ARCHITECTURE_MCP.md`
- **Database**: See `DATABASE.md`
- **Git/Portability**: See `PORTABILITY.md`
- **Session history**: See `SESSION_SUMMARY.md`

---

**Remember**: You own all the data. It's in one clear location: `~/.devflow/devflow.db`
