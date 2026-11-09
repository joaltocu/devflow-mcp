#!/bin/bash
# register-project.sh - Register a project with DevFlow

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEVFLOW_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if project path provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Project path required${NC}"
    echo "Usage: $0 /path/to/project"
    exit 1
fi

PROJECT_PATH="$(cd "$1" && pwd)"

# Check if path exists
if [ ! -d "$PROJECT_PATH" ]; then
    echo -e "${RED}Error: Directory does not exist: $PROJECT_PATH${NC}"
    exit 1
fi

# Check if it's a git repo
if [ ! -d "$PROJECT_PATH/.git" ]; then
    echo -e "${YELLOW}Warning: Not a git repository${NC}"
    REPO_URL=""
else
    REPO_URL=$(cd "$PROJECT_PATH" && git remote get-url origin 2>/dev/null || echo "")
fi

# Detect project name
PROJECT_NAME=$(basename "$PROJECT_PATH")

# Detect language
LANGUAGE=""
if [ -f "$PROJECT_PATH/package.json" ]; then
    LANGUAGE="javascript"
elif [ -f "$PROJECT_PATH/pyproject.toml" ] || [ -f "$PROJECT_PATH/setup.py" ]; then
    LANGUAGE="python"
elif [ -f "$PROJECT_PATH/Cargo.toml" ]; then
    LANGUAGE="rust"
elif [ -f "$PROJECT_PATH/go.mod" ]; then
    LANGUAGE="go"
elif [ -f "$PROJECT_PATH/pom.xml" ] || [ -f "$PROJECT_PATH/build.gradle" ]; then
    LANGUAGE="java"
fi

# Detect framework
FRAMEWORK=""
if [ "$LANGUAGE" = "javascript" ] && [ -f "$PROJECT_PATH/package.json" ]; then
    if grep -q '"react"' "$PROJECT_PATH/package.json"; then
        FRAMEWORK="react"
    elif grep -q '"vue"' "$PROJECT_PATH/package.json"; then
        FRAMEWORK="vue"
    elif grep -q '"next"' "$PROJECT_PATH/package.json"; then
        FRAMEWORK="nextjs"
    elif grep -q '"express"' "$PROJECT_PATH/package.json"; then
        FRAMEWORK="express"
    fi
elif [ "$LANGUAGE" = "python" ]; then
    if grep -q "fastapi" "$PROJECT_PATH/pyproject.toml" 2>/dev/null || grep -q "fastapi" "$PROJECT_PATH/requirements.txt" 2>/dev/null; then
        FRAMEWORK="fastapi"
    elif grep -q "django" "$PROJECT_PATH/pyproject.toml" 2>/dev/null || grep -q "django" "$PROJECT_PATH/requirements.txt" 2>/dev/null; then
        FRAMEWORK="django"
    elif grep -q "flask" "$PROJECT_PATH/pyproject.toml" 2>/dev/null || grep -q "flask" "$PROJECT_PATH/requirements.txt" 2>/dev/null; then
        FRAMEWORK="flask"
    fi
fi

# Show detected info
echo -e "${GREEN}Project Information:${NC}"
echo "  Name: $PROJECT_NAME"
echo "  Path: $PROJECT_PATH"
echo "  Language: ${LANGUAGE:-unknown}"
echo "  Framework: ${FRAMEWORK:-none}"
echo "  Repository: ${REPO_URL:-none}"
echo ""

# Confirm
read -p "Register this project with DevFlow? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Create Python script to call MCP tool
TEMP_SCRIPT=$(mktemp)
cat > "$TEMP_SCRIPT" << 'EOFPYTHON'
import asyncio
import os
import sys
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def register_project(name, path, language, framework, repo_url):
    """Register a project using DevFlow MCP."""

    run_script = os.path.expanduser("DEVFLOW_ROOT/run-mcp.sh")

    # Get environment for MCP server
    env = os.environ.copy()

    server_params = StdioServerParameters(
        command=str(run_script),
        args=[],
        env=env,
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Call create_project tool
            arguments = {
                "name": name,
                "path": path,
            }
            if language:
                arguments["language"] = language
            if framework:
                arguments["framework"] = framework
            if repo_url:
                arguments["repository_url"] = repo_url

            result = await session.call_tool("context/create_project", arguments)

            # Parse result
            for item in result.content:
                if hasattr(item, 'text'):
                    data = json.loads(item.text)
                    return data

            return None

if __name__ == "__main__":
    name = sys.argv[1]
    path = sys.argv[2]
    language = sys.argv[3] if sys.argv[3] != "unknown" else None
    framework = sys.argv[4] if sys.argv[4] != "none" else None
    repo_url = sys.argv[5] if sys.argv[5] != "none" else None

    result = asyncio.run(register_project(name, path, language, framework, repo_url))

    if result and result.get("success"):
        project_id = result["project"]["id"]
        print(f"SUCCESS:{project_id}")
    else:
        error = result.get("error", "Unknown error") if result else "No response"
        print(f"ERROR:{error}")
        sys.exit(1)
EOFPYTHON

# Replace placeholder
sed -i "s|DEVFLOW_ROOT|$DEVFLOW_ROOT|g" "$TEMP_SCRIPT"

# Run the Python script
RESULT=$(python3 "$TEMP_SCRIPT" \
    "$PROJECT_NAME" \
    "$PROJECT_PATH" \
    "${LANGUAGE:-unknown}" \
    "${FRAMEWORK:-none}" \
    "${REPO_URL:-none}" 2>&1)

rm -f "$TEMP_SCRIPT"

# Check result
if echo "$RESULT" | grep -q "^SUCCESS:"; then
    PROJECT_ID=$(echo "$RESULT" | sed 's/SUCCESS://')
    echo -e "${GREEN}✓ Project registered successfully!${NC}"
    echo "  Project UUID: $PROJECT_ID"

    # Save to .devflow file
    echo "PROJECT_ID=$PROJECT_ID" > "$PROJECT_PATH/.devflow"
    echo -e "${GREEN}✓ Saved UUID to .devflow${NC}"

    # Add to .gitignore if not already there
    if [ -f "$PROJECT_PATH/.gitignore" ]; then
        if ! grep -q "^\.devflow$" "$PROJECT_PATH/.gitignore"; then
            echo ".devflow" >> "$PROJECT_PATH/.gitignore"
            echo -e "${GREEN}✓ Added .devflow to .gitignore${NC}"
        fi
    else
        echo ".devflow" > "$PROJECT_PATH/.gitignore"
        echo -e "${GREEN}✓ Created .gitignore with .devflow${NC}"
    fi

    echo ""
    echo "Next steps:"
    echo "  1. Make some code changes"
    echo "  2. Run: cd $PROJECT_PATH && git diff"
    echo "  3. Ask Claude Code to review with DevFlow"

else
    echo -e "${RED}✗ Failed to register project${NC}"
    echo "$RESULT" | sed 's/ERROR:/Error: /'
    exit 1
fi
