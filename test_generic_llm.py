#!/usr/bin/env python3
"""Test script for Generic LLM integration.

This script tests that your LLM_API_KEY, LLM_BASE_URL, and LLM_MODEL
configuration is working correctly.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from devflow.agents.generic_llm import GenericLLMAgent
from devflow.reviewers.generic_llm_reviewer import CodeQualityGenericReviewer


async def test_environment():
    """Test that environment variables are set correctly."""
    print("=" * 60)
    print("Step 1: Checking Environment Variables")
    print("=" * 60)

    llm_api_key = os.getenv("LLM_API_KEY")
    llm_base_url = os.getenv("LLM_BASE_URL")
    llm_model = os.getenv("LLM_MODEL")

    if not llm_api_key:
        print("❌ LLM_API_KEY not set in .env")
        return False
    else:
        # Show only first 10 chars
        print(f"✅ LLM_API_KEY: {llm_api_key[:10]}...")

    if not llm_base_url:
        print("⚠️  LLM_BASE_URL not set (will use default: https://api.openai.com/v1)")
        llm_base_url = "https://api.openai.com/v1"
    else:
        print(f"✅ LLM_BASE_URL: {llm_base_url}")

    if not llm_model:
        print("⚠️  LLM_MODEL not set (will use default: gpt-4)")
        llm_model = "gpt-4"
    else:
        print(f"✅ LLM_MODEL: {llm_model}")

    print()
    return True


async def test_generic_llm_agent():
    """Test the GenericLLMAgent with a simple prompt."""
    print("=" * 60)
    print("Step 2: Testing GenericLLMAgent")
    print("=" * 60)

    llm_model = os.getenv("LLM_MODEL", "gpt-4")

    try:
        agent = GenericLLMAgent(
            model=llm_model,
            system_prompt="You are a helpful assistant. Respond concisely.",
        )

        print(f"Sending test prompt to {llm_model}...")
        response = await agent.generate(
            prompt="Say 'Hello from DevFlow!' in exactly 5 words.",
            temperature=0.0,
            max_tokens=50,
        )

        print(f"✅ Response received: {response}")
        print()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        return False


async def test_code_review():
    """Test a code review with the generic LLM backend."""
    print("=" * 60)
    print("Step 3: Testing Code Review with Generic LLM")
    print("=" * 60)

    # Sample git diff
    sample_diff = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,5 +1,8 @@
+import os
+
 def calculate_total(items):
-    total = 0
-    for item in items:
-        total += item
-    return total
+    # Calculate total price
+    api_key = "sk-1234567890abcdef"  # TODO: Move to env
+    total = sum(items)
+    print(f"Total: {total}")
+    return total
"""

    changes = {
        "diff": sample_diff,
        "file_changes": [
            {
                "file": "test.py",
                "additions": 4,
                "deletions": 4,
            }
        ],
        "stats": {
            "total_additions": 4,
            "total_deletions": 4,
            "files_changed": 1,
        }
    }

    context = {
        "language": "python",
        "framework": "unknown",
    }

    try:
        llm_model = os.getenv("LLM_MODEL", "gpt-4")
        reviewer = CodeQualityGenericReviewer(model=llm_model)

        print(f"Running code quality review with {llm_model}...")
        print("(This may take 10-30 seconds depending on the provider)")
        print()

        result = await reviewer.review(changes, context)

        print(f"✅ Review completed!")
        print(f"   Reviewer: {result.reviewer_name}")
        print(f"   Passed: {result.passed}")
        print(f"   Summary: {result.summary}")
        print(f"   Issues found: {len(result.issues)}")
        print()

        if result.issues:
            print("Issues:")
            for i, issue in enumerate(result.issues, 1):
                print(f"  {i}. [{issue.severity.value}] {issue.message}")
                if issue.suggestion:
                    print(f"     Suggestion: {issue.suggestion}")
            print()

        return True

    except Exception as e:
        print(f"❌ Error during review: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("DevFlow Generic LLM Integration Test")
    print("=" * 60)
    print()

    # Load .env
    load_dotenv()

    # Run tests
    env_ok = await test_environment()
    if not env_ok:
        print("❌ Environment variables not configured correctly.")
        print("   Please check your .env file.")
        return

    agent_ok = await test_generic_llm_agent()
    if not agent_ok:
        print("❌ GenericLLMAgent test failed.")
        print("   Please check your API key and base URL.")
        return

    review_ok = await test_code_review()
    if not review_ok:
        print("❌ Code review test failed.")
        return

    print("=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    print()
    print("Your Generic LLM configuration is working correctly.")
    print("DevFlow will now use your LLM provider for code reviews.")
    print()


if __name__ == "__main__":
    asyncio.run(main())
