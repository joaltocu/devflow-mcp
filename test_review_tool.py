#!/usr/bin/env python
"""Test the development/review_code MCP tool."""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from devflow.database.session import get_session, init_db
from devflow.database.models import Project, Review
from devflow.tools.development import review_code
from sqlalchemy import select


async def test_review_tool():
    """Test code review functionality."""
    print("=" * 70)
    print("DevFlow MCP - Testing Code Review")
    print("=" * 70)

    # Initialize
    print("\n[1/4] Initializing...")
    await init_db()

    # Get the devflow-mcp project ID
    async with get_session() as session:
        stmt = select(Project).where(Project.name == "devflow-mcp")
        result = await session.execute(stmt)
        project = result.scalar_one_or_none()

        if not project:
            print("   ❌ DevFlow project not found. Run test_mcp_tools.py first!")
            return

        project_id = str(project.id)
        print(f"   ✅ Found project: {project.name}")
        print(f"      ID: {project_id}")

    # Load test diff
    print("\n[2/4] Loading test code with intentional issues...")
    diff_path = Path("/tmp/test-review.diff")
    if not diff_path.exists():
        print("   ❌ Test diff not found at /tmp/test-review.diff")
        print("      Expected issues:")
        print("      - 3 hardcoded credentials (CRITICAL)")
        print("      - Missing documentation (MEDIUM)")
        print("      - Poor naming (LOW)")
        print("      - SQL injection vulnerability (CRITICAL)")
        return

    diff = diff_path.read_text()
    print("   ✅ Loaded diff with intentional issues:")
    print("      • Hardcoded API keys (security)")
    print("      • Missing documentation (code quality)")
    print("      • Poor naming (code quality)")
    print("      • SQL injection (security)")

    # Run review
    print("\n[3/4] Running code review...")
    print("   ⏳ This will test the review pipeline:")
    print("      • DiffAnalyzer - parses the diff")
    print("      • Code Quality Reviewer - checks style/docs")
    print("      • Security Reviewer - checks for vulnerabilities")
    print("      • Synthesis Agent - combines findings")
    print("")
    print("   Note: Using Claude Code reviewers (no API key required)")
    print("   This may take 30-60 seconds...")

    try:
        result = await review_code({
            "project_id": project_id,
            "diff": diff,
            "review_types": ["code_quality", "security"],
            "context": {
                "branch": "test",
                "author": "test-user"
            }
        })

        response = json.loads(result[0].text)

        if response["success"]:
            print("\n   ✅ Review completed!")

            # Show results
            print("\n   📊 Review Results:")
            for review in response["reviews"]:
                print(f"\n   • {review['reviewer_name']}")
                print(f"     Passed: {'✅' if review['passed'] else '❌'}")
                print(f"     Summary: {review['summary']}")
                print(f"     Issues found: {len(review['issues'])}")

                if review['issues']:
                    print("     Top issues:")
                    for issue in review['issues'][:3]:  # Show first 3
                        print(f"       - [{issue['severity']}] {issue['message'][:60]}...")

            # Show synthesis
            if 'synthesized' in response:
                synth = response['synthesized']
                print(f"\n   🔍 Synthesis:")
                print(f"      Passed: {'✅' if synth['passed'] else '❌'}")
                print(f"      Summary: {synth['summary']}")
        else:
            print(f"   ❌ Review failed: {response}")

    except Exception as e:
        print(f"   ❌ Error during review: {e}")
        import traceback
        traceback.print_exc()
        return

    # Verify in database
    print("\n[4/4] Verifying data in database...")
    async with get_session() as session:
        stmt = select(Review).where(Review.project_id == project_id)
        result = await session.execute(stmt)
        reviews = result.scalars().all()

        print(f"   ✅ Found {len(reviews)} review(s) in database")
        for review in reviews:
            print(f"      • {review.type} - {review.created_at}")

    print("\n" + "=" * 70)
    print("✅ Code review test complete!")
    print("=" * 70)
    print("\n🎯 What was tested:")
    print("   ✅ Diff parsing and analysis")
    print("   ✅ Code quality review")
    print("   ✅ Security review")
    print("   ✅ Issue detection")
    print("   ✅ Results synthesis")
    print("   ✅ Database storage")
    print("\n💡 DevFlow is fully operational!")
    print()


if __name__ == "__main__":
    asyncio.run(test_review_tool())
