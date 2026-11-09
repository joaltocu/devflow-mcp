# DevFlow MCP Server

**Holistic development infrastructure you own** - Code review, knowledge management, and GitHub integration for ANY agent.

## What is This?

DevFlow MCP Server is your **personal development infrastructure** that:
- 🧠 **Learns from all your projects** - Patterns, reviews, decisions stored in YOUR database
- 🤖 **Works with any agent** - Claude Code, GPT-4, custom agents - all use the same tools
- 📊 **Accumulates knowledge** - Every review improves future reviews
- 🔧 **Extensible by design** - Add new workflows without changing infrastructure
- 💰 **No API key required** - Uses Claude Code for reviews (or API if you prefer)
- 🏠 **Completely portable** - One SQLite file = all your data

## Multi-Level Holistic Architecture

DevFlow implements **holistic design at three levels**:

```
┌─────────────────────────────────────────────────────┐
│ Level 1: External Agents (ANY agent can use this)  │
│  Claude Code  │  GPT-4  │  Custom Agents            │
└─────────────────────┬───────────────────────────────┘
                      │ MCP Protocol
┌─────────────────────▼───────────────────────────────┐
│ Level 2: DevFlow MCP Server (Central Orchestration)│
│                                                     │
│  MCP Tools:                                         │
│  ├── development/review_code    ← Main review tool │
│  ├── github/create_pr                              │
│  ├── knowledge/query                               │
│  └── context/get_project                           │
│                                                     │
│  Review Backend (automatic selection):             │
│  • LLM_API_KEY set? → Use Generic LLM reviewers    │
│  • ANTHROPIC_API_KEY set? → Use Anthropic API      │
│  • No API key? → Use Claude Code reviewers         │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│ Level 3: Internal Review Agents                    │
│  Code Quality │ Security │ Architecture │ Coverage  │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│ Level 4: Your Database (YOU OWN THIS)              │
│  ~/.devflow/devflow.db (SQLite)                    │
│                                                     │
│  • All 22 projects                                 │
│  • Every review from every agent                   │
│  • Learned patterns (effectiveness scores)         │
│  • Knowledge base (cross-project insights)         │
└─────────────────────────────────────────────────────┘
```

**Why this is holistic:**
- Any external agent can use DevFlow MCP
- All data flows to one central database
- Patterns learned from ALL agents, ALL projects
- Internal implementation is flexible (Claude Code OR API)
- You completely own all the data

## Quick Start

### 1. Clone & Setup

```bash
cd /home/joseal/projects/joaltocu/framework

# Configure environment (optional)
cp .env.example .env
nano .env  # Configure your settings
```

**Configuration (optional):**
- Leave as-is to use Claude Code reviews (free, no API key needed)
- Add `LLM_API_KEY` + `LLM_BASE_URL` + `LLM_MODEL` for custom LLM providers (GLM, DeepSeek, OpenAI, etc.)
- Add `ANTHROPIC_API_KEY` for official Anthropic API reviews (costs tokens)
- Add `GITHUB_TOKEN` for PR creation features

### 2. Run Server

```bash
./run-mcp.sh
```

That's it! The server:
- Creates database at `~/.devflow/devflow.db` automatically
- Uses Claude Code for reviews (no API key needed)
- Runs over stdio, ready for MCP clients

### 3. Connect from Claude Code

Add to `~/.config/claude/mcp.json`:

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

Restart Claude Code and DevFlow tools are available!

### 4. Install Skills (Recommended)

DevFlow comes with Claude Code skills that make it easier to use:

```bash
# Copy skills to Claude Code
cp skills/*.md ~/.claude/skills/

# Or create symlinks for auto-updates
ln -s $(pwd)/skills/*.md ~/.claude/skills/
```

**Available skills:**
- `devflow-review` - Auto-review code changes
- `devflow-setup` - Set up new projects
- `devflow-help` - Quick help and examples
- `devflow-precommit` - Proactive pre-commit checks

Restart Claude Code and skills will be active. See `skills/README.md` for details.

### 5. Optional: Use API Reviews

If you want faster API-based reviews instead of Claude Code reviews, you have two options:

**Option 1: Generic LLM (Recommended for custom providers)**
```bash
# Add to .env - Works with ANY OpenAI-compatible API
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_BASE_URL=https://api.nan.builders/v1
LLM_MODEL=glm5.3-flash
```

**Option 2: Anthropic API (Official Claude models)**
```bash
# Add to .env
ANTHROPIC_API_KEY=sk-ant-xxx
```

DevFlow automatically detects and uses the appropriate backend based on which keys are set.

## Core Concepts

### You Own the Data

All data lives in **your PostgreSQL database**:

```sql
-- Every review across all 22 projects
SELECT * FROM reviews ORDER BY created_at DESC;

-- Patterns learned from experience
SELECT pattern_name, effectiveness_score, usage_count
FROM patterns
WHERE category = 'security'
ORDER BY effectiveness_score DESC;

-- Architecture decisions (ADRs)
SELECT title, decision FROM decisions
WHERE project_id = '...';
```

### Agent-Agnostic

Any MCP-compatible agent can use your server:

```python
# Claude Code
result = mcp.call_tool("development/review_code", {
    "project_id": "fitness-ai",
    "diff": git_diff
})

# GPT-4 via MCP client
result = mcp.call_tool("knowledge/query", {
    "query": "How do we handle JWT tokens?",
    "category": "security"
})

# Your custom agent
result = mcp.call_tool("github/create_pr", {
    "project_id": "compliance-ai",
    "title": "Add GDPR compliance",
    "body": auto_generated_body
})
```

### Compound Learning

The server learns from every interaction:

```python
# After a security review finds a pattern
await store_pattern({
    "category": "security",
    "pattern_name": "Environment-based secrets",
    "effectiveness_score": 0.98,
    "projects": ["fitness-ai", "compliance-ai"]
})

# Future reviews automatically reference this pattern
knowledge = await query_knowledge({
    "query": "How to handle API keys?",
    "category": "security"
})
# Returns: "Based on 15 successful uses across your projects,
#           store secrets in environment variables..."
```

## MCP Tools

### development/review_code

Run comprehensive code review (reuses your existing review agents):

**Input:**
```json
{
    "project_id": "uuid",
    "diff": "git diff output",
    "review_types": ["code_quality", "security", "architecture", "coverage"]
}
```

**Output:**
```json
{
    "success": true,
    "reviews": [
        {
            "type": "security",
            "issues": [{
                "severity": "critical",
                "message": "Hardcoded API key",
                "suggestion": "Use environment variables"
            }]
        }
    ],
    "synthesized": {
        "overall_assessment": "BLOCKED",
        "critical_issues": 1
    }
}
```

### knowledge/query

Search your accumulated knowledge:

**Input:**
```json
{
    "query": "Best practices for JWT authentication",
    "category": "security"
}
```

**Output:**
```json
{
    "results": [
        {
            "topic": "JWT Best Practices",
            "content": "...",
            "source": "learned from compliance-ai-project",
            "relevance_score": 0.95
        }
    ]
}
```

### github/create_pr

Create pull request with review results:

**Input:**
```json
{
    "project_id": "uuid",
    "branch": "feature/auth",
    "title": "Add JWT authentication",
    "body": "..."
}
```

**Output:**
```json
{
    "success": true,
    "pr_url": "https://github.com/owner/repo/pull/123",
    "pr_number": 123
}
```

## MCP Resources

### project://{project_id}/context

Get complete project context:

```python
context = mcp.read_resource("project://fitness-ai/context")
# Returns: {
#     "name": "fitness-ai-platform",
#     "language": "python",
#     "framework": "fastapi",
#     "architecture_doc": "...",
#     "adrs": [...],
#     "recent_reviews": [...]
# }
```

### knowledge://patterns/security

Get security patterns learned across all projects:

```python
patterns = mcp.read_resource("knowledge://patterns/security")
# Returns patterns sorted by effectiveness_score
```

## Database Schema

### Projects
Stores metadata for all your projects (all 22):
- name, path, language, framework
- repository_url
- Custom metadata (JSONB)

### Reviews
Every code review ever performed:
- project_id, type, diff
- result (full review data)
- agent_type (which agent ran it)

### Review Issues
Individual issues from reviews:
- severity, category, file_path, line_number
- message, suggestion
- resolved status

### Patterns (Learning System)
Patterns learned from successful reviews:
- category, pattern_name, description
- effectiveness_score (0.0-1.0)
- usage_count
- projects where it worked

### Knowledge Base
Accumulated knowledge:
- topic, content, source
- relevance_score
- tags, projects

## Example Workflows

### Workflow 1: Development with Claude Code

```python
# 1. Agent gets project context
context = mcp.read_resource("project://fitness-ai/context")

# 2. Claude Code implements feature
# (agent does its work)

# 3. Agent runs code review
review = mcp.call_tool("development/review_code", {
    "project_id": "fitness-ai",
    "diff": git_diff,
    "review_types": ["security", "code_quality"]
})

# 4. If approved, create PR
if review["synthesized"]["overall_assessment"] == "APPROVED":
    pr = mcp.call_tool("github/create_pr", {
        "project_id": "fitness-ai",
        "title": "Add user authentication",
        "body": auto_generated_from_review
    })

# 5. Store learning
mcp.call_tool("knowledge/store_pattern", {
    "category": "authentication",
    "pattern_name": "JWT with refresh tokens",
    "project_id": "fitness-ai"
})
```

### Workflow 2: Knowledge Query

```python
# GPT-4 agent needs to know about your architecture
knowledge = mcp.call_tool("knowledge/query", {
    "query": "How do we structure FastAPI applications?",
    "category": "architecture"
})

# Returns patterns from all 22 projects that use FastAPI
```

### Workflow 3: Cross-Project Learning

```python
# Security pattern learned from compliance-ai
# Automatically applied to fitness-ai review

# 1. Compliance review finds good pattern
mcp.call_tool("knowledge/store_pattern", {
    "category": "security",
    "pattern_name": "GDPR data encryption",
    "code_example": "...",
    "effectiveness_score": 1.0,
    "project_id": "compliance-ai"
})

# 2. Later, fitness-ai review automatically references it
review = mcp.call_tool("development/review_code", {
    "project_id": "fitness-ai",
    "diff": user_data_handling_code
})
# Review will suggest: "Based on patterns from compliance-ai,
#                       encrypt user data following GDPR requirements"
```

## Configuration

### Environment Variables

```bash
# Database URL (required)
export DEVFLOW_DATABASE_URL="postgresql+asyncpg://localhost/devflow"

# Anthropic API key (for reviews)
export ANTHROPIC_API_KEY="your-key"

# GitHub token (for PR operations)
export GITHUB_TOKEN="your-token"
```

### MCP Client Configuration

Add to your MCP client config (e.g., Claude Desktop):

```json
{
    "mcpServers": {
        "devflow": {
            "command": "devflow-mcp",
            "env": {
                "DEVFLOW_DATABASE_URL": "postgresql+asyncpg://localhost/devflow"
            }
        }
    }
}
```

## Implementation Status

See `IMPLEMENTATION_STATUS.md` for detailed progress.

**Completed:**
- ✅ MCP server framework
- ✅ Database models (all 7 tables)
- ✅ Session management
- ✅ Tool registration system
- ✅ Example tool: `development/review_code`

**In Progress:**
- 🚧 Remaining MCP tools
- 🚧 MCP resources
- 🚧 Example clients

**Next:**
- GitHub tools implementation
- Knowledge tools implementation
- Resource providers
- Example agent integrations

## Why MCP Server vs Standalone CLI?

| Feature | Standalone CLI | MCP Server |
|---------|---------------|------------|
| **Agent Support** | Claude only | Any agent (Claude, GPT, custom) |
| **Data Ownership** | Isolated per-project | Central database YOU own |
| **Learning** | No accumulation | Learns from all 22 projects |
| **Extensibility** | Rebuild for new workflows | Add tools, keep infrastructure |
| **Knowledge Sharing** | None | Patterns flow between projects |
| **Workflow Scope** | Development only | Dev, docs, compliance, audits, etc. |

## Contributing

This is an early-stage MCP server. Contributions welcome!

## License

MIT

## Credits

Built with:
- [MCP SDK](https://github.com/anthropics/mcp) - Model Context Protocol
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [Claude API](https://anthropic.com) - Code review intelligence
