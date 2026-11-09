#!/bin/bash
# DevFlow MCP Server - Quick Start Script

cd "$(dirname "$0")"

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set Python path
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"

# Run the server
python -m devflow.server "$@"
