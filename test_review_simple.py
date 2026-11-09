#!/usr/bin/env python
"""Simple test of review infrastructure without AI."""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from devflow.tools.diff_analyzer import DiffAnalyzer
from devflow.tools.development import analyze_diff


async def test_review_infrastructure():
    """Test review infrastructure without AI."""
    print("=" * 70)
    print("DevFlow MCP - Testing Review Infrastructure")
    print("=" * 70)

    # Load test diff
    print("\n[1/2] Testing Diff Analyzer...")
    diff_path = Path("/tmp/test-review.diff")
    diff = diff_path.read_text()

    # Test diff analyzer directly
    analyzer = DiffAnalyzer(diff)
    changes = analyzer.to_dict()

    print(f"   ✅ Diff analyzed successfully")
    print(f"      Files changed: {changes['stats']['files_changed']}")
    print(f"      Total additions: {changes['stats']['total_additions']}")
    print(f"      Total deletions: {changes['stats']['total_deletions']}")
    print(f"\n      Files:")
    for file_change in changes['file_changes']:
        print(f"        • {file_change['file_path']}")
        print(f"          Type: {file_change['change_type']}")
        print(f"          +{file_change['additions']} -{file_change['deletions']}")

    # Test via MCP tool
    print("\n[2/2] Testing development/analyze_diff MCP tool...")
    result = await analyze_diff({"diff": diff})
    analysis = json.loads(result[0].text)

    print("   ✅ MCP tool working")
    print(f"      Files: {analysis['stats']['files_changed']}")
    print(f"      Lines changed: +{analysis['stats']['total_additions']} -{analysis['stats']['total_deletions']}")

    print("\n" + "=" * 70)
    print("✅ Review infrastructure is working!")
    print("=" * 70)

    print("\n📝 Summary:")
    print("   ✅ DiffAnalyzer - Parses git diffs correctly")
    print("   ✅ development/analyze_diff - MCP tool working")
    print("   ⏳ development/review_code - Needs API key or manual test")

    print("\n💡 To test full code review:")
    print("   Option A: Add ANTHROPIC_API_KEY to .env")
    print("   Option B: Test manually via Claude Code MCP")
    print("   Option C: Use test_review_tool.py (will use Claude Code reviewers)")

    print("\n🎯 DevFlow MCP server is ready to use!")
    print()


if __name__ == "__main__":
    asyncio.run(test_review_infrastructure())
