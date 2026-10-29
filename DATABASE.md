# Database Storage Options

## Default: SQLite in Your Home Directory

**Location**: `~/.devflow/devflow.db`

```bash
# Database will be stored at:
/home/joseal/.devflow/devflow.db

# Easy to check:
ls -lh ~/.devflow/devflow.db

# Easy to inspect:
sqlite3 ~/.devflow/devflow.db "SELECT * FROM projects;"

# Easy to backup:
cp ~/.devflow/devflow.db ~/.devflow/backup-$(date +%Y%m%d).db
```

### Why SQLite?

✅ **Simple** - Single file, no server to manage
✅ **Portable** - Copy the file, you have all your data
✅ **You own it** - Clear location, easy to backup/restore
✅ **Fast** - Good performance for single-user use
✅ **Reliable** - Battle-tested, used by billions of devices

### Installation

```bash
# Install with default (SQLite)
pip install -e .

# That's it! No database server needed.
```

## Option 2: PostgreSQL (For Advanced Use)

Use PostgreSQL if you need:
- Multiple users accessing the database
- Advanced queries and analytics
- Better concurrent write performance
- Database clustering/replication

### Installation

```bash
# Install PostgreSQL support
pip install -e ".[postgres]"

# Install PostgreSQL server (if not already installed)
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb devflow

# Set connection string
export DEVFLOW_DATABASE_URL="postgresql+asyncpg://localhost/devflow"

# Or with user/password:
export DEVFLOW_DATABASE_URL="postgresql+asyncpg://user:pass@localhost/devflow"
```

**PostgreSQL data location**: `/var/lib/postgresql/{version}/main/`

## Option 3: Custom Location

### SQLite in Custom Directory

```bash
# Store in your projects directory
export DEVFLOW_DATABASE_URL="sqlite+aiosqlite:///home/joseal/projects/joaltocu/data/devflow.db"

# Store in framework directory
export DEVFLOW_DATABASE_URL="sqlite+aiosqlite:///home/joseal/projects/joaltocu/framework/devflow.db"

# Store on external drive
export DEVFLOW_DATABASE_URL="sqlite+aiosqlite:///mnt/external/devflow.db"
```

### PostgreSQL on Custom Port/Host

```bash
# Different port
export DEVFLOW_DATABASE_URL="postgresql+asyncpg://localhost:5433/devflow"

# Different host
export DEVFLOW_DATABASE_URL="postgresql+asyncpg://192.168.1.100/devflow"

# With credentials
export DEVFLOW_DATABASE_URL="postgresql+asyncpg://user:password@host:port/database"
```

## Database Structure

Regardless of SQLite or PostgreSQL, you get the same 7 tables:

```sql
-- Your 22 projects
SELECT * FROM projects;

-- Every code review
SELECT * FROM reviews ORDER BY created_at DESC;

-- Individual issues from reviews
SELECT * FROM review_issues WHERE severity = 'critical';

-- Learned patterns (the learning system!)
SELECT pattern_name, effectiveness_score, usage_count
FROM patterns
ORDER BY effectiveness_score DESC;

-- Architecture decisions (ADRs)
SELECT title, decision FROM decisions WHERE project_id = '...';

-- All agent interactions logged
SELECT agent_type, tool_name, success
FROM agent_interactions
ORDER BY created_at DESC;

-- Accumulated knowledge
SELECT topic, content FROM knowledge_base WHERE category = 'security';
```

## Backup & Restore

### SQLite Backup

```bash
# Simple file copy
cp ~/.devflow/devflow.db ~/.devflow/backup-$(date +%Y%m%d).db

# Compress for archival
tar -czf devflow-backup-$(date +%Y%m%d).tar.gz ~/.devflow/devflow.db

# Restore
cp ~/.devflow/backup-20261029.db ~/.devflow/devflow.db
```

### PostgreSQL Backup

```bash
# Backup
pg_dump devflow > devflow-backup-$(date +%Y%m%d).sql

# Restore
psql devflow < devflow-backup-20261029.sql
```

## Migration Between Databases

### SQLite → PostgreSQL

```bash
# 1. Export from SQLite
sqlite3 ~/.devflow/devflow.db .dump > dump.sql

# 2. Import to PostgreSQL (may need adjustments)
psql devflow < dump.sql

# 3. Update environment variable
export DEVFLOW_DATABASE_URL="postgresql+asyncpg://localhost/devflow"
```

### PostgreSQL → SQLite

```bash
# 1. Export from PostgreSQL
pg_dump devflow > dump.sql

# 2. Use pgloader or manual migration
# (This requires more manual work due to syntax differences)

# 3. Update environment variable
export DEVFLOW_DATABASE_URL="sqlite+aiosqlite:///~/.devflow/devflow.db"
```

## Viewing Your Data

### SQLite

```bash
# Interactive SQL
sqlite3 ~/.devflow/devflow.db

# Quick queries
sqlite3 ~/.devflow/devflow.db "SELECT COUNT(*) FROM reviews;"
sqlite3 ~/.devflow/devflow.db "SELECT * FROM patterns ORDER BY effectiveness_score DESC LIMIT 5;"

# Export to CSV
sqlite3 -header -csv ~/.devflow/devflow.db "SELECT * FROM projects;" > projects.csv

# Use GUI tools
# - DB Browser for SQLite (https://sqlitebrowser.org/)
# - DBeaver (https://dbeaver.io/)
```

### PostgreSQL

```bash
# Interactive SQL
psql devflow

# Quick queries
psql devflow -c "SELECT COUNT(*) FROM reviews;"

# Use GUI tools
# - pgAdmin (https://www.pgadmin.org/)
# - DBeaver (https://dbeaver.io/)
```

## Recommended Setup for You

Given your 22 projects and need to own all data:

**Use SQLite at `~/.devflow/devflow.db`**

Why?
- ✅ All data in one clear location
- ✅ Easy to backup (just copy the file)
- ✅ No server to maintain
- ✅ Fast enough for your use case
- ✅ Can upgrade to PostgreSQL later if needed

### Quick Start

```bash
# Install (SQLite is default)
cd /home/joseal/projects/joaltocu/framework
pip install -e .

# Run the server
devflow-mcp

# Your database is automatically created at:
# ~/.devflow/devflow.db

# Check it:
ls -lh ~/.devflow/devflow.db
sqlite3 ~/.devflow/devflow.db ".tables"
```

### Regular Backups

Add to your crontab:

```bash
# Daily backup at 2 AM
0 2 * * * cp ~/.devflow/devflow.db ~/.devflow/backups/devflow-$(date +\%Y\%m\%d).db

# Keep only last 30 days
0 3 * * * find ~/.devflow/backups/ -name "devflow-*.db" -mtime +30 -delete
```

## Summary

| Database | Location | Best For | Pros | Cons |
|----------|----------|----------|------|------|
| **SQLite (Default)** | `~/.devflow/devflow.db` | Single user, local use | Simple, portable, you own it | Not for concurrent writes |
| **PostgreSQL** | `/var/lib/postgresql/` | Multi-user, analytics | Powerful, scalable | Requires server setup |

**For your use case**: Stick with SQLite. It's perfect for a personal development infrastructure with 22 projects.
