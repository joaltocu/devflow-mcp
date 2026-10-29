#!/bin/bash
# Setup script to initialize DevFlow MCP as a git repository

set -e

echo "🚀 DevFlow MCP - Repository Setup"
echo "=================================="
echo ""

# Check if already a git repo
if [ -d .git ]; then
    echo "✓ Already a git repository"
else
    echo "→ Initializing git repository..."
    git init
    echo "✓ Git repository initialized"
fi

# Check if .gitignore exists
if [ -f .gitignore ]; then
    echo "✓ .gitignore exists"
else
    echo "⚠ .gitignore missing - creating it..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*.so
.venv/
*.egg-info/

# DevFlow - DON'T COMMIT YOUR DATA!
.devflow/
*.db
*.sqlite

# Environment
.env
.env.local
EOF
    echo "✓ .gitignore created"
fi

# Check if there are uncommitted changes
if git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "✓ No uncommitted changes"
else
    echo "→ Staging all files..."
    git add .
    echo "✓ Files staged"

    echo ""
    echo "→ Creating initial commit..."
    git commit -m "Initial commit: DevFlow MCP Server

- MCP server for holistic development workflows
- Database models: projects, reviews, patterns, knowledge
- Hybrid agent architecture (Claude Code + custom agents)
- SQLite storage at ~/.devflow/devflow.db
- Review services: code quality, security, architecture, coverage
- Tools: development/review_code (example implementation)
- Architecture and documentation" 2>/dev/null || echo "✓ Already committed"
fi

echo ""
echo "✅ Repository setup complete!"
echo ""
echo "Next steps:"
echo ""
echo "1. Add remote repository (optional):"
echo "   git remote add origin https://github.com/joaltocu/devflow-mcp.git"
echo "   git push -u origin main"
echo ""
echo "2. Setup NAS storage (recommended):"
echo "   # Mount NAS"
echo "   sudo mount -t cifs //nas-ip/home /mnt/nas -o credentials=~/.nascreds"
echo "   # Symlink database to NAS"
echo "   mkdir -p /mnt/nas/.devflow"
echo "   ln -s /mnt/nas/.devflow ~/.devflow"
echo ""
echo "3. Install and run:"
echo "   pip install -e ."
echo "   devflow-mcp"
echo ""
