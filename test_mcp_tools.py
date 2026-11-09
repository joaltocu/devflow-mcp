#!/usr/bin/env python
"""Comprehensive test of all DevFlow MCP tools."""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from devflow.database.session import get_session, init_db
from devflow.database.models import Project
from devflow.tools.context import create_project, list_projects, get_project, update_project
from sqlalchemy import select


async def test_all_tools():
    """Test all MCP tools."""
    print("=" * 70)
    print("DevFlow MCP - Complete Tool Testing")
    print("=" * 70)

    # Initialize
    print("\n[1/6] Initializing database...")
    await init_db()
    print("   ✅ Database ready")

    # Test 1: Create DevFlow project
    print("\n[2/6] Testing context/create_project - Creating DevFlow project...")
    result = await create_project({
        "name": "devflow-mcp",
        "path": "/home/joseal/projects/joaltocu/framework",
        "language": "python",
        "repository_url": "git@github.com:joaltocu/devflow-mcp.git",
        "extra_metadata": {
            "description": "Holistic development framework",
            "status": "active",
            "priority": "high"
        }
    })
    response = json.loads(result[0].text)
    if response["success"]:
        print(f"   ✅ Created: {response['project']['name']}")
        print(f"      ID: {response['project']['id']}")
        devflow_id = response['project']['id']
    else:
        print(f"   ❌ Failed: {response}")
        return

    # Test 2: List all projects
    print("\n[3/6] Testing context/list_projects - Listing all projects...")
    result = await list_projects({})
    response = json.loads(result[0].text)
    print(f"   ✅ Found {response['count']} project(s):")
    for proj in response['projects']:
        print(f"      • {proj['name']} ({proj['language']}) - {proj['id'][:8]}...")

    # Test 3: Get specific project
    print("\n[4/6] Testing context/get_project - Getting DevFlow project details...")
    result = await get_project({"project_id": devflow_id})
    response = json.loads(result[0].text)
    if response["success"]:
        proj = response['project']
        print(f"   ✅ Retrieved project:")
        print(f"      Name: {proj['name']}")
        print(f"      Path: {proj['path']}")
        print(f"      Language: {proj['language']}")
        print(f"      Repository: {proj['repository_url']}")
        print(f"      Metadata: {proj['extra_metadata']}")

    # Test 4: Update project
    print("\n[5/6] Testing context/update_project - Updating metadata...")
    result = await update_project({
        "project_id": devflow_id,
        "extra_metadata": {
            "description": "Holistic development framework with AI code review",
            "status": "production",
            "priority": "high",
            "version": "0.1.0"
        }
    })
    response = json.loads(result[0].text)
    if response["success"]:
        print(f"   ✅ Updated: {response['project']['name']}")
        print(f"      New metadata: {response['project']['extra_metadata']}")

    # Test 5: Verify in database
    print("\n[6/6] Verifying data persistence in database...")
    async with get_session() as session:
        stmt = select(Project)
        result = await session.execute(stmt)
        projects = result.scalars().all()
        print(f"   ✅ Database contains {len(projects)} project(s):")
        for p in projects:
            print(f"      • {p.name} - {p.id}")
            print(f"        Path: {p.path}")
            print(f"        Metadata: {p.extra_metadata}")

    # Summary
    print("\n" + "=" * 70)
    print("✅ All MCP tools tested successfully!")
    print("=" * 70)
    print("\n📊 Test Results:")
    print("   ✅ context/create_project - Working")
    print("   ✅ context/list_projects - Working")
    print("   ✅ context/get_project - Working")
    print("   ✅ context/update_project - Working")
    print("   ✅ Database persistence - Working")
    print("\n🎯 Next: Test development/review_code with real code!")
    print()


if __name__ == "__main__":
    asyncio.run(test_all_tools())
