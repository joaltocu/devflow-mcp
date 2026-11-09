# DevFlow Quick Start Guide

Get DevFlow running in under 5 minutes.

## Prerequisites

- Claude Code (or any MCP-compatible agent)
- Python 3.11 or higher
- Git repository

## Installation

### 1. Clone DevFlow

```bash
cd ~/projects
git clone git@github.com:joaltocu/framework.git
cd framework
```

### 2. Install Dependencies

```bash
pip install -e .
```

### 3. Configure MCP

**Option A: Project-specific (recommended for sharing with team)**

Create `.mcp.json` in your project root:

```bash
cd /path/to/your/project
cat > .mcp.json << 'EOF'
{
  "mcpServers": {
    "devflow": {
      "command": "/home/joseal/projects/joaltocu/framework/run-mcp.sh",
      "args": []
    }
  }
}
EOF
```

**Option B: User-wide (for all projects)**

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "devflow": {
      "command": "/home/joseal/projects/joaltocu/framework/run-mcp.sh",
      "args": []
    }
  }
}
```

### 4. Configure Review Backend (Optional)

**Default:** Uses Claude Code for reviews (no setup needed)

**For faster API reviews:**

```bash
cd /home/joseal/projects/joaltocu/framework
cp .env.example .env
nano .env
```

Add your preferred provider:

```bash
# DeepSeek (recommended - fast and cheap)
LLM_API_KEY=sk-your-deepseek-key
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-v4-flash

# OR OpenAI
LLM_API_KEY=sk-your-openai-key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4-turbo

# OR Anthropic
ANTHROPIC_API_KEY=sk-ant-your-key
```

### 5. Restart Claude Code

MCP configs load at startup. Restart your agent to load DevFlow.

### 6. Verify Installation

In Claude Code:

```
You: /mcp
```

Should show devflow with 6 tools:
- development/review_code
- development/analyze_diff
- context/create_project
- context/list_projects
- context/get_project
- context/update_project

## First Review

### 1. Register Your Project

```
You: Set up DevFlow for this project
```

Claude will:
- Detect project name from directory
- Find git repository URL
- Detect language/framework
- Create project in DevFlow database
- Save project UUID to `.devflow` file

### 2. Make Some Changes

```bash
# Edit some files
vim src/app.py

# Check what changed
git diff
```

### 3. Run Code Review

```
You: Review my changes with DevFlow
```

Claude will:
- Get git diff
- Run 4 parallel reviews (quality, security, architecture, coverage)
- Show issues grouped by severity
- Suggest fixes for critical issues

### 4. Fix Critical Issues

If DevFlow finds CRITICAL issues (security vulnerabilities, hardcoded secrets), fix them before committing:

```
You: Fix the hardcoded API key issue
```

Claude will help you move it to environment variables.

### 5. Commit Clean Code

Once clean:

```bash
git add .
git commit -m "Add feature with DevFlow review"
```

## Common Workflows

### Daily Development Flow

```
You: I want to add user authentication

[Claude implements the feature]

You: Review my changes with DevFlow

[DevFlow analyzes the diff]

Claude: Found 1 CRITICAL issue - password stored in plaintext
        Want me to fix it?

You: Yes, hash it properly

[Claude fixes the issue]

You: Review again

Claude: All clear! Ready to commit.
```

### Pre-Commit Review

```bash
# Stage your changes
git add .
```

```
You: Review staged changes before I commit

[DevFlow reviews git diff --cached]

Claude: Found no critical issues.
        2 MEDIUM suggestions for code quality.
        Safe to commit.
```

### Branch Review Before PR

```bash
# Compare your feature branch to main
git diff main...feature-branch
```

```
You: Review all changes in this branch vs main

[DevFlow reviews full branch diff]

Claude: Comprehensive review of 15 files:
        - No critical/high issues
        - 3 medium code quality improvements suggested
        - Test coverage looks good
        Ready for PR.
```

## Configuration Options

### Using Different Models

Edit `/home/joseal/projects/joaltocu/framework/.env`:

```bash
# Fast and cheap (recommended for daily use)
LLM_MODEL=deepseek-v4-flash

# Best quality (for critical reviews)
LLM_MODEL=gpt-4-turbo

# Balance
LLM_MODEL=gpt-3.5-turbo
```

### Review Specific Types

By default, all 4 review types run. To run specific types:

```
You: Review my changes for security only
```

Claude will call `development/review_code` with:
```json
{
  "review_types": ["security"]
}
```

Available types:
- `code_quality` - Style, maintainability, best practices
- `security` - Vulnerabilities, secrets, OWASP top 10
- `architecture` - Design patterns, ADR compliance
- `coverage` - Test coverage, edge cases

## Understanding Results

### Severity Levels

DevFlow categorizes issues by severity:

**CRITICAL** 🔴
- Security vulnerabilities
- Hardcoded credentials
- Data integrity risks
- **Action:** Fix immediately before commit

**HIGH** 🟠
- Bugs that will cause failures
- Incorrect logic
- Race conditions
- **Action:** Fix soon, ideally before commit

**MEDIUM** 🟡
- Code quality issues
- Maintainability concerns
- Missing documentation
- **Action:** Good to improve, safe to defer

**LOW** 🔵
- Minor style improvements
- Nitpicks
- **Action:** Nice to have

**INFO** ⚪
- Observations
- Neutral comments
- **Action:** For reference only

### When to Commit

- ✅ **Safe to commit:** INFO, LOW, MEDIUM only
- ⚠️ **Consider fixing:** HIGH issues present
- 🛑 **Do not commit:** CRITICAL issues exist

## Troubleshooting

### DevFlow not showing in `/mcp`

1. Check config exists:
   ```bash
   cat .mcp.json
   # or
   cat ~/.claude.json
   ```

2. Verify run-mcp.sh is executable:
   ```bash
   chmod +x /home/joseal/projects/joaltocu/framework/run-mcp.sh
   ```

3. Restart Claude Code

### Reviews failing

Test your configuration:

```bash
cd /home/joseal/projects/joaltocu/framework
python test_generic_llm.py
```

Common fixes:

**API key invalid:**
```bash
# Check .env
cat .env | grep LLM_API_KEY
# Should show your key (starting with sk-)
```

**Wrong base URL:**
```bash
# Should be /v1 endpoint, not /v1/models
LLM_BASE_URL=https://api.provider.com/v1  ✓
LLM_BASE_URL=https://api.provider.com/v1/models  ✗
```

### Only 4 tools showing (missing development tools)

This was fixed in commit e6db64a. Update to latest:

```bash
cd /home/joseal/projects/joaltocu/framework
git pull origin main
```

Restart Claude Code.

## Next Steps

### Install Skills (Optional)

DevFlow comes with comprehensive skills that make it easier to use:

```bash
# Copy or symlink the skill
ln -s /home/joseal/projects/joaltocu/framework/skills/devflow/SKILL.md \
      ~/.claude/skills/devflow.md
```

Restart Claude Code. Now phrases like "review my changes" will automatically invoke DevFlow workflows.

### Explore Advanced Features

- **Review history:** Query `~/.devflow/devflow.db` to see past reviews
- **Custom contexts:** Add architecture docs for better reviews
- **Multiple projects:** Register all your projects for cross-project learning
- **API integration:** Use DevFlow MCP tools from other agents (GPT-4, custom agents)

### Read More

- Complete skill guide: `skills/devflow/SKILL.md`
- MCP tools reference: `skills/devflow/references/mcp-tools.md`
- LLM compatibility: `skills/devflow/references/llm-compatibility.md`
- Troubleshooting: `skills/devflow/references/troubleshooting.md`

## Getting Help

- Issues: https://github.com/joaltocu/framework/issues
- Test script: `python test_generic_llm.py`
- Inspect tools: `python inspect_mcp.py`

## Quick Reference Card

```bash
# Installation
cd ~/projects && git clone git@github.com:joaltocu/framework.git
cd framework && pip install -e .

# Configure MCP (in your project)
echo '{"mcpServers":{"devflow":{"command":"/path/to/run-mcp.sh","args":[]}}}' > .mcp.json

# Optional: API backend
cp .env.example .env && nano .env

# Restart Claude Code
# Then use in conversation:

"Set up DevFlow for this project"    # First time only
"Review my changes with DevFlow"      # Daily use
"Review for security issues"          # Specific review type
"Fix the critical issues"             # After review
```

## Tips

1. **Review early, review often** - Catch issues while context is fresh
2. **Don't batch unrelated changes** - Review one feature at a time
3. **Fix CRITICAL immediately** - Security issues are not negotiable
4. **Use fast models for daily work** - DeepSeek v4 Flash is excellent
5. **Use best models for critical reviews** - GPT-4 or Claude for security audits
6. **Track your improvements** - Query review history to see progress over time
