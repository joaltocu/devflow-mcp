---
description: Automatically review code changes using DevFlow MCP with DeepSeek. Use when the user asks to review their changes, run a code review, check their code, or before committing. Triggers on: "review my changes", "check my code", "run devflow review", "review before commit".
---

# DevFlow Code Review Skill

You are helping the user review their code changes using DevFlow MCP with DeepSeek v4 Flash backend.

## Your Task

1. **Check if project exists in DevFlow**
   - Use `context/list_projects` to see if the current project is registered
   - If not found, ask if they want to create one first

2. **Get the changes to review**
   - Check for uncommitted changes: `git diff`
   - Check for staged changes: `git diff --cached`
   - Ask which changes they want to review if both exist

3. **Run the review**
   - Use `development/review_code` tool with:
     - project_id: The UUID from step 1
     - diff: The git diff output
     - review_types: ["code_quality", "security", "architecture", "coverage"]
     - context: Include working_dir, branch name, etc.

4. **Present results clearly**
   - Show critical and high severity issues first
   - Group issues by category
   - Provide actionable suggestions
   - Offer to help fix issues

## Important Notes

- ALWAYS use the DevFlow MCP tools, don't just analyze manually
- The review uses DeepSeek v4 Flash automatically
- All reviews are stored in ~/.devflow/devflow.db for future reference
- If the review finds critical issues, strongly recommend fixing before commit

## Example Flow

```
User: "Review my changes"

You:
1. [Check git diff to see what changed]
2. [Use context/list_projects to find the project]
3. [Use development/review_code with the diff]
4. Present results:

"I've reviewed your changes using DevFlow (DeepSeek v4 Flash):

⚠️ CRITICAL ISSUES (2):
1. Hardcoded API key in config.py:15
   → Move to environment variables

2. SQL injection vulnerability in query.py:42
   → Use parameterized queries

📋 MEDIUM ISSUES (3):
...

Would you like me to help fix the critical issues before you commit?"
```

## Error Handling

- If no project exists: Offer to create one
- If no changes found: Check if they meant to review a specific file
- If review fails: Check the .env configuration and API connectivity
