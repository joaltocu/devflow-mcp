# DevFlow MCP Server - Portability Guide

## TL;DR

✅ **Code**: Fully portable via Git
✅ **Data**: Portable via SQLite file (single file = all your data)

## Making It a Git Repository

```bash
cd /home/joseal/projects/joaltocu/framework

# Initialize git (if not already)
git init

# Check what will be committed (.gitignore already created)
git status

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: DevFlow MCP Server

- MCP server for holistic development workflows
- Database models: projects, reviews, patterns, knowledge
- Hybrid agent architecture
- SQLite storage at ~/.devflow/devflow.db"

# Optional: Push to GitHub/GitLab
git remote add origin git@github.com:joaltocu/devflow-mcp.git
git branch -M main
git push -u origin main
```

## Two Things to Port

### 1. Framework Code (Git Repository)

**What's included:**
- ✅ MCP server implementation
- ✅ Database schema (models)
- ✅ Review agents
- ✅ Documentation
- ✅ Configuration examples

**What's excluded (.gitignore):**
- ❌ Database files (`*.db`, `*.sqlite`)
- ❌ Environment files (`.env`)
- ❌ Python cache (`__pycache__`)
- ❌ Virtual environments

### 2. Database (Your Data)

**Single file:** `~/.devflow/devflow.db`

This contains ALL your data:
- All 22 projects
- Every review ever performed
- Learned patterns
- Knowledge base
- ADRs

## Portability Scenarios

### Scenario 1: Work from Multiple Machines

**Best solution: NAS as central storage**

```bash
# On each machine:

# 1. Clone the repo
git clone git@github.com:joaltocu/devflow-mcp.git
cd devflow-mcp
pip install -e .

# 2. Mount NAS
sudo mkdir -p /mnt/nas
# Add to /etc/fstab for auto-mount:
# //nas-ip/home /mnt/nas cifs credentials=/home/user/.nascreds 0 0
sudo mount -a

# 3. Symlink to NAS database
ln -s /mnt/nas/.devflow ~/.devflow

# 4. Run server
devflow-mcp

# ✅ All machines share same database on NAS
# ✅ Code updates via git pull
# ✅ Data always in sync
```

### Scenario 2: Transfer to New Machine

**Copy everything:**

```bash
# On old machine:
git remote add origin git@github.com:joaltocu/devflow-mcp.git
git push -u origin main

# Backup database
cp ~/.devflow/devflow.db ~/devflow-backup.db

# Transfer database
scp ~/devflow-backup.db new-machine:~/

# On new machine:
git clone git@github.com:joaltocu/devflow-mcp.git
cd devflow-mcp
pip install -e .

# Restore database
mkdir -p ~/.devflow
mv ~/devflow-backup.db ~/.devflow/devflow.db

# Run server
devflow-mcp
```

### Scenario 3: Backup Your Work

**Framework (code):**
```bash
# Already backed up if using Git
git push origin main
```

**Data (database):**
```bash
# Manual backup
cp ~/.devflow/devflow.db ~/backups/devflow-$(date +%Y%m%d).db

# Or if on NAS (automatic backups)
# NAS handles snapshots and backups
```

### Scenario 4: Share with Team

**Framework:**
```bash
# Push to shared repo
git remote add origin git@github.com:your-org/devflow-mcp.git
git push -u origin main

# Team members:
git clone git@github.com:your-org/devflow-mcp.git
pip install -e .
```

**Data:**
- Each team member gets their own database
- OR use PostgreSQL on shared server:
  ```bash
  # Team shares same PostgreSQL database
  export DEVFLOW_DATABASE_URL="postgresql+asyncpg://db-server:5432/devflow"
  ```

## Complete Setup: Laptop + NAS

### Initial Setup (One Time)

```bash
# 1. Make it a git repo
cd /home/joseal/projects/joaltocu/framework
git init
git add .
git commit -m "Initial commit: DevFlow MCP Server"

# 2. Optional: Push to GitHub
git remote add origin git@github.com:joaltocu/devflow-mcp.git
git push -u origin main

# 3. Setup NAS storage
# Mount NAS (add to /etc/fstab for persistence)
sudo mkdir -p /mnt/nas
echo "//nas-ip/home /mnt/nas cifs credentials=/home/joseal/.nascreds 0 0" | sudo tee -a /etc/fstab
sudo mount -a

# 4. Move database to NAS
mkdir -p /mnt/nas/.devflow
mv ~/.devflow/devflow.db /mnt/nas/.devflow/ 2>/dev/null || true
ln -sfn /mnt/nas/.devflow ~/.devflow

# 5. Verify
ls -la ~/.devflow
# Should show: .devflow -> /mnt/nas/.devflow
```

### Daily Workflow

```bash
# Start working
cd /home/joseal/projects/joaltocu/framework
devflow-mcp  # Server uses database on NAS

# Make code changes
git add .
git commit -m "Add new MCP tool"
git push

# Database automatically saved to NAS
# No manual backup needed!
```

### Access from Another Machine

```bash
# One-time setup on new machine:
git clone git@github.com:joaltocu/devflow-mcp.git
cd devflow-mcp
pip install -e .

# Mount same NAS
sudo mount -t cifs //nas-ip/home /mnt/nas -o credentials=/home/user/.nascreds
ln -s /mnt/nas/.devflow ~/.devflow

# Run
devflow-mcp

# ✅ Same code (via git)
# ✅ Same data (via NAS)
```

## File Structure

```
Repository (Git):
/home/joseal/projects/joaltocu/framework/
├── .git/                      ✅ Version control
├── .gitignore                 ✅ Excludes data files
├── pyproject.toml             ✅ Dependencies
├── README_MCP.md              ✅ Documentation
├── ARCHITECTURE_MCP.md        ✅ Architecture
├── DATABASE.md                ✅ Database guide
├── PORTABILITY.md             ✅ This file
├── src/devflow/               ✅ All code
│   ├── server.py
│   ├── database/
│   ├── tools/
│   └── ...
└── examples/                  ✅ Example configs

Database (NOT in Git):
~/.devflow/                    ❌ Not in repo
├── devflow.db                 ❌ Your data (backed up separately)
└── backups/                   ❌ Optional backup directory

# If using NAS:
~/.devflow -> /mnt/nas/.devflow  (symlink)
```

## What Gets Committed vs What Doesn't

### ✅ Committed to Git

- All source code (`src/devflow/`)
- Database schema (models.py)
- Documentation
- Configuration examples
- Tests
- Dependencies (pyproject.toml)

### ❌ NOT Committed (in .gitignore)

- Database files (`*.db`)
- Your actual data
- Environment variables (`.env`)
- Python cache
- Virtual environments
- Logs

## Recovery Scenarios

### Lost Laptop

If your laptop dies:

```bash
# On new laptop:

# 1. Get code from Git
git clone git@github.com:joaltocu/devflow-mcp.git
cd devflow-mcp
pip install -e .

# 2. Get data from NAS
sudo mount -t cifs //nas-ip/home /mnt/nas -o credentials=~/.nascreds
ln -s /mnt/nas/.devflow ~/.devflow

# 3. Run
devflow-mcp

# ✅ Back to work in 5 minutes!
```

### Corrupted Database

```bash
# If database on NAS with snapshots:
# Restore from NAS snapshot (Synology example)
# Go to NAS web UI → Snapshot Replication → Restore

# Or from manual backup:
cp ~/.devflow/backups/devflow-20261029.db ~/.devflow/devflow.db
```

### NAS Failure

```bash
# If NAS goes down temporarily:
# Server will fail to start (can't access database)

# Option 1: Wait for NAS to come back online

# Option 2: Work with local database temporarily
unlink ~/.devflow  # Remove NAS symlink
mkdir ~/.devflow
# Database will be created locally
# Later sync back to NAS when it's restored
```

## Best Practices

### 1. Git Workflow

```bash
# Regular commits
git add .
git commit -m "Descriptive message"
git push

# Pull before making changes (if shared repo)
git pull
```

### 2. Database Backup

```bash
# Automated (on NAS):
# Enable NAS snapshots - automatic backups

# Manual (if needed):
cp ~/.devflow/devflow.db ~/.devflow/backups/devflow-$(date +%Y%m%d).db

# Or use rsync for incremental:
rsync -av ~/.devflow/devflow.db /path/to/backup/location/
```

### 3. Multi-Machine Sync

```bash
# Always pull latest code before running
cd /home/joseal/projects/joaltocu/framework
git pull

# Database syncs automatically (if on NAS)
# No manual sync needed!
```

## Summary

| Component | Storage | Portability | Backup |
|-----------|---------|-------------|--------|
| **Framework Code** | Git repository | `git clone` | GitHub/GitLab |
| **Database** | `~/.devflow/devflow.db` | Copy file or use NAS | NAS snapshots or manual copy |
| **Config** | `.env` file | Manual copy | Include in notes |

**Recommended Setup:**
- ✅ Framework: Git repository (GitHub/GitLab)
- ✅ Database: Symlink to NAS (`~/.devflow -> /mnt/nas/.devflow`)
- ✅ Result: Portable code + safe data + automatic backups

This gives you the best of both worlds:
- Code versioned and shareable
- Data centralized and backed up
- Work from any machine
- Nothing tied to a single device
