---
description: Provide quick help and examples for using DevFlow MCP. Use when the user asks how to use DevFlow, what DevFlow can do, needs examples, or wants help. Triggers on: "how to use devflow", "devflow help", "what can devflow do", "show devflow examples".
---

# DevFlow MCP Help Skill

You are providing quick help and guidance for using DevFlow MCP.

## Your Task

Show the user a concise, actionable guide for using DevFlow MCP.

## Response Format

```
# DevFlow MCP - Quick Help

DevFlow provides AI-powered code review using DeepSeek v4 Flash.

## Available Commands

### Setup (First Time)
"Set up DevFlow for this project"
→ Registers your project and creates a UUID

### Code Review
"Review my changes using DevFlow"
→ Reviews uncommitted changes with full analysis

"Review staged changes using DevFlow"
→ Reviews only staged (git add) changes

"Review [file] using DevFlow"
→ Reviews specific file changes

### Project Management
"Show DevFlow projects"
→ Lists all registered projects

"Show this project in DevFlow"
→ Gets current project details

### Analysis
"Analyze this diff using DevFlow"
→ Extract structured info from a git diff

## What Gets Reviewed?

DevFlow analyzes 4 aspects:
✓ Code Quality - Style, maintainability, best practices
✓ Security - Vulnerabilities, OWASP top 10
✓ Architecture - Design patterns, structure
✓ Test Coverage - Missing tests, edge cases

## Review Severity Levels

- 🔴 CRITICAL: Security holes, data loss (must fix!)
- 🟠 HIGH: Bugs, design flaws (should fix)
- 🟡 MEDIUM: Code quality (good to improve)
- 🔵 LOW: Minor improvements (nice to have)
- ⚪ INFO: Observations (for reference)

## Your Setup

Backend: DeepSeek v4 Flash (via OpenAI-compatible API)
Database: ~/.devflow/devflow.db
Tools: 6 available (2 development + 4 context)

## Common Workflows

1. First time: "Set up DevFlow"
2. Before commit: "Review my changes"
3. After fix: "Review again to confirm"
4. View history: Check ~/.devflow/devflow.db

## Need More Help?

- Full guide: See QUICKSTART_MCP.md
- Tool details: Run /mcp in Claude Code
- Test setup: python test_generic_llm.py
```

## After Showing Help

Ask the user: "Would you like me to help you with any of these tasks?"

## Context-Aware Help

If you detect the user's situation, provide targeted help:

- **No project set up yet**: Emphasize "Set up DevFlow" first
- **Project exists**: Focus on review commands
- **Review errors**: Point to troubleshooting in QUICKSTART_MCP.md
- **First-time user**: Offer to walk them through setup

## Examples to Show

Always include at least one concrete example:

```
Example session:

You: "Review my changes using DevFlow"

Claude:
[Reviews code using DeepSeek]

Found 3 issues:
🔴 CRITICAL: Hardcoded password in auth.py:15
🟡 MEDIUM: Missing error handling in api.py:42
🔵 LOW: Unused import in utils.py:5

Would you like help fixing the critical issue?

You: "Yes, fix it"

Claude: [Helps refactor to use environment variables]
```

This makes DevFlow concrete and actionable!
