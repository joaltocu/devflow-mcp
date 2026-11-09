#!/usr/bin/env python3
"""Inspect MCP server to see exported tools and resources.

This script connects to the DevFlow MCP server and lists all available
tools, resources, and their schemas.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv


async def inspect_mcp():
    """Connect to MCP server and list available tools/resources."""
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    print("=" * 70)
    print("DevFlow MCP Server Inspector")
    print("=" * 70)
    print()

    # Server parameters - use the run-mcp.sh script
    import os
    script_dir = Path(__file__).parent
    run_script = script_dir / "run-mcp.sh"

    # Set up environment
    env = os.environ.copy()
    env["PYTHONPATH"] = str(script_dir / "src")

    server_params = StdioServerParameters(
        command=str(run_script),
        args=[],
        env=env,
    )

    print("Connecting to MCP server...")
    print(f"Command: {server_params.command}")
    print()

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()

                print("✅ Connected to MCP server")
                print()

                # List tools
                print("=" * 70)
                print("MCP TOOLS")
                print("=" * 70)
                print()

                tools_result = await session.list_tools()

                if not tools_result.tools:
                    print("No tools available")
                else:
                    for i, tool in enumerate(tools_result.tools, 1):
                        print(f"{i}. {tool.name}")
                        print(f"   Description: {tool.description}")
                        print(f"   Input Schema:")
                        print(f"   {json.dumps(tool.inputSchema, indent=6)}")
                        print()

                print(f"Total tools: {len(tools_result.tools)}")
                print()

                # List resources
                print("=" * 70)
                print("MCP RESOURCES")
                print("=" * 70)
                print()

                try:
                    resources_result = await session.list_resources()

                    if not resources_result.resources:
                        print("No resources available")
                    else:
                        for i, resource in enumerate(resources_result.resources, 1):
                            print(f"{i}. {resource.uri}")
                            print(f"   Name: {resource.name}")
                            print(f"   Description: {resource.description}")
                            print(f"   MIME Type: {resource.mimeType}")
                            print()

                        print(f"Total resources: {len(resources_result.resources)}")
                except Exception as e:
                    print(f"No resources available (error: {e})")
                print()

                # List prompts (if any)
                print("=" * 70)
                print("MCP PROMPTS")
                print("=" * 70)
                print()

                try:
                    prompts_result = await session.list_prompts()
                    if not prompts_result.prompts:
                        print("No prompts available")
                    else:
                        for i, prompt in enumerate(prompts_result.prompts, 1):
                            print(f"{i}. {prompt.name}")
                            print(f"   Description: {prompt.description}")
                            print()
                        print(f"Total prompts: {len(prompts_result.prompts)}")
                except Exception as e:
                    print(f"No prompts available (or error: {e})")

                print()
                print("=" * 70)
                print("SUMMARY")
                print("=" * 70)
                print(f"Tools: {len(tools_result.tools)}")
                try:
                    print(f"Resources: {len(resources_result.resources)}")
                except:
                    print("Resources: 0 (not implemented)")
                print()

    except Exception as e:
        print(f"❌ Error connecting to MCP server: {e}")
        import traceback
        traceback.print_exc()
        return


async def main():
    """Run the inspector."""
    # Load .env
    load_dotenv()

    # Add src to PYTHONPATH for subprocess
    import os
    pythonpath = str(Path(__file__).parent / "src")
    if "PYTHONPATH" in os.environ:
        os.environ["PYTHONPATH"] = f"{pythonpath}:{os.environ['PYTHONPATH']}"
    else:
        os.environ["PYTHONPATH"] = pythonpath

    await inspect_mcp()


if __name__ == "__main__":
    asyncio.run(main())
