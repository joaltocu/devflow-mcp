#!/usr/bin/env python
"""Simple test script to verify DevFlow MCP tools work correctly."""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from devflow.database.session import get_session, init_db
from devflow.database.models import Project
from devflow.tools.context import create_project, list_projects, get_project
from sqlalchemy import select


async def test_context_tools():
    """Test context management tools."""
    print("=" * 60)
    print("Testing DevFlow MCP - Context Tools")
    print("=" * 60)

    # Initialize database
    print("\n1. Initializing database...")
    await init_db()
    print("   ✅ Database initialized")

    # Test create_project
    print("\n2. Testing context/create_project...")
    result = await create_project({
        "name": "test-project",
        "path": "/home/joseal/projects/test-project",
        "language": "python",
        "framework": "fastapi",
        "repository_url": "git@github.com:test/test-project.git",
        "extra_metadata": {
            "test": True,
            "environment": "testing"
        }
    })

    response = json.loads(result[0].text)
    print(f"   ✅ Project created: {response['project']['name']}")
    print(f"   Project ID: {response['project']['id']}")
    project_id = response['project']['id']

    # Test list_projects
    print("\n3. Testing context/list_projects...")
    result = await list_projects({})
    response = json.loads(result[0].text)
    print(f"   ✅ Found {response['count']} project(s)")
    for proj in response['projects']:
        print(f"      - {proj['name']} ({proj['language']})")

    # Test get_project
    print("\n4. Testing context/get_project...")
    result = await get_project({"project_id": project_id})
    response = json.loads(result[0].text)
    print(f"   ✅ Retrieved project: {response['project']['name']}")
    print(f"      Path: {response['project']['path']}")
    print(f"      Language: {response['project']['language']}")
    print(f"      Framework: {response['project']['framework']}")

    # Verify in database
    print("\n5. Verifying data in database...")
    async with get_session() as session:
        stmt = select(Project).where(Project.id == project_id)
        result = await session.execute(stmt)
        db_project = result.scalar_one()
        print(f"   ✅ Project exists in database")
        print(f"      Name: {db_project.name}")
        print(f"      ID: {db_project.id}")
        print(f"      Extra metadata: {db_project.extra_metadata}")

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Connect Claude Code to DevFlow MCP")
    print("2. Test development/review_code tool")
    print("3. Start using DevFlow for real projects!")
    print()


if __name__ == "__main__":
    asyncio.run(test_context_tools())
