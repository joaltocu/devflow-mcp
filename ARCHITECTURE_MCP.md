# DevFlow MCP Server Architecture

## Overview

DevFlow MCP Server is a **holistic, agent-agnostic development infrastructure** that provides:
- Central knowledge and context management across all projects
- Code review, security analysis, and quality checks as MCP tools
- GitHub integration for PR management
- Learning system that improves over time
- Works with ANY agent (Claude, GPT, custom agents)

## Core Principles

1. **You Own the Data**: All context, reviews, and knowledge stored in your database
2. **Agent-Agnostic**: Works with Claude Code, GPT-4, custom agents, or any MCP client
3. **Holistic**: Learns from all 22 projects, shares patterns across them
4. **Extensible**: Add new tools without changing infrastructure

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    MCP Server (Python)                          │
│                    Port: 3000 (stdio)                           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              MCP Protocol Handler                       │   │
│  │  - Tool discovery                                       │   │
│  │  - Resource discovery                                   │   │
│  │  - Prompt discovery                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   MCP Tools                             │   │
│  │                                                         │   │
│  │  development/                                           │   │
│  │    ├── review_code          (run code reviews)         │   │
│  │    ├── analyze_security     (security analysis)        │   │
│  │    ├── check_architecture   (architecture compliance)  │   │
│  │    └── measure_coverage     (test coverage)            │   │
│  │                                                         │   │
│  │  github/                                                │   │
│  │    ├── create_pr            (create pull request)      │   │
│  │    ├── post_review          (post review comments)     │   │
│  │    └── get_pr_status        (check PR status)          │   │
│  │                                                         │   │
│  │  knowledge/                                             │   │
│  │    ├── query                (search knowledge base)    │   │
│  │    ├── store_pattern        (save learned pattern)     │   │
│  │    ├── get_suggestions      (AI suggestions)           │   │
│  │    └── store_decision       (save ADR)                 │   │
│  │                                                         │   │
│  │  context/                                               │   │
│  │    ├── get_project          (project metadata)         │   │
│  │    ├── update_project       (update project)           │   │
│  │    └── analyze_diff         (parse git diff)           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 MCP Resources                           │   │
│  │                                                         │   │
│  │  project://{project_id}/context                         │   │
│  │  project://{project_id}/architecture                    │   │
│  │  project://{project_id}/adrs                            │   │
│  │  reviews://{project_id}/history                         │   │
│  │  reviews://{project_id}/latest                          │   │
│  │  knowledge://patterns/{category}                        │   │
│  │  knowledge://learnings/{topic}                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │               Central Database (PostgreSQL)             │   │
│  │                                                         │   │
│  │  Tables:                                                │   │
│  │    ├── projects                                         │   │
│  │    ├── reviews                                          │   │
│  │    ├── review_issues                                    │   │
│  │    ├── patterns                                         │   │
│  │    ├── decisions (ADRs)                                 │   │
│  │    ├── agent_interactions                               │   │
│  │    └── knowledge_base                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ MCP Protocol (stdio/SSE)
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Claude Code  │    │   GPT-4 via   │    │ Custom Agent  │
│               │    │   MCP Client  │    │               │
│ - Development │    │ - Docs        │    │ - Compliance  │
│ - Features    │    │ - Analysis    │    │ - Audits      │
└───────────────┘    └───────────────┘    └───────────────┘
```

## Database Schema

### Projects Table
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    path TEXT NOT NULL,
    language VARCHAR(50),
    framework VARCHAR(50),
    repository_url TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Reviews Table
```sql
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    type VARCHAR(50) NOT NULL, -- code_quality, security, architecture, coverage
    diff TEXT NOT NULL,
    context JSONB,
    result JSONB, -- ReviewResult structure
    agent_type VARCHAR(100), -- 'claude-sonnet-4-5', 'gpt-4', etc.
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Review Issues Table
```sql
CREATE TABLE review_issues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID REFERENCES reviews(id),
    severity VARCHAR(20) NOT NULL,
    category VARCHAR(100),
    file_path TEXT,
    line_number INTEGER,
    message TEXT NOT NULL,
    suggestion TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Patterns Table (Learning System)
```sql
CREATE TABLE patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(100) NOT NULL, -- security, performance, testing, etc.
    pattern_name VARCHAR(255) NOT NULL,
    description TEXT,
    code_example TEXT,
    effectiveness_score FLOAT DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    projects JSONB, -- List of projects where this pattern was successful
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Decisions Table (ADRs)
```sql
CREATE TABLE decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    title VARCHAR(255) NOT NULL,
    status VARCHAR(50), -- proposed, accepted, deprecated, superseded
    context TEXT,
    decision TEXT NOT NULL,
    consequences TEXT,
    alternatives JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Agent Interactions Table
```sql
CREATE TABLE agent_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    agent_type VARCHAR(100) NOT NULL,
    tool_name VARCHAR(255) NOT NULL,
    input_params JSONB,
    output_result JSONB,
    success BOOLEAN,
    error_message TEXT,
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Knowledge Base Table
```sql
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    content TEXT NOT NULL,
    source VARCHAR(255), -- 'review', 'manual', 'learned'
    relevance_score FLOAT DEFAULT 0.0,
    tags JSONB,
    projects JSONB, -- Relevant projects
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## MCP Tools Specification

### development/review_code

**Input:**
```json
{
    "project_id": "uuid",
    "diff": "git diff output",
    "review_types": ["code_quality", "security", "architecture", "coverage"],
    "context": {
        "branch": "feature/auth",
        "author": "developer"
    }
}
```

**Output:**
```json
{
    "success": true,
    "reviews": [
        {
            "type": "security",
            "issues": [
                {
                    "severity": "critical",
                    "file": "auth.py",
                    "line": 42,
                    "message": "Hardcoded API key detected",
                    "suggestion": "Use environment variables"
                }
            ],
            "summary": "Found 1 critical security issue"
        }
    ],
    "synthesized": {
        "overall_assessment": "BLOCKED",
        "critical_issues": 1,
        "recommendations": [...]
    }
}
```

### knowledge/query

**Input:**
```json
{
    "query": "What are the best practices for JWT authentication?",
    "category": "security",
    "project_id": "uuid (optional)"
}
```

**Output:**
```json
{
    "results": [
        {
            "topic": "JWT Best Practices",
            "content": "...",
            "relevance_score": 0.95,
            "source": "learned from compliance-ai-project"
        }
    ]
}
```

### github/create_pr

**Input:**
```json
{
    "project_id": "uuid",
    "branch": "feature/auth",
    "title": "Add JWT authentication",
    "body": "...",
    "base": "main"
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

## MCP Resources Specification

### project://{project_id}/context

Returns complete project context:
```json
{
    "name": "fitness-ai-platform",
    "language": "python",
    "framework": "fastapi",
    "architecture_doc": "...",
    "adrs": [...],
    "style_guide": "...",
    "recent_reviews": [...]
}
```

### knowledge://patterns/security

Returns security patterns learned across all projects:
```json
{
    "patterns": [
        {
            "name": "Environment-based secrets",
            "effectiveness_score": 0.98,
            "usage_count": 15,
            "projects": ["fitness-ai", "compliance-ai", ...]
        }
    ]
}
```

## Example Agent Workflows

### Workflow 1: Claude Code Development

```python
# Agent (Claude Code) uses MCP tools

1. Get project context:
   resource = mcp.read_resource("project://fitness-ai/context")

2. Implement feature:
   # Claude Code does the work

3. Review code:
   result = mcp.call_tool("development/review_code", {
       "project_id": "fitness-ai",
       "diff": git_diff,
       "review_types": ["code_quality", "security"]
   })

4. If approved, create PR:
   pr = mcp.call_tool("github/create_pr", {
       "project_id": "fitness-ai",
       "title": "Add user auth",
       "body": auto_generated_body
   })

5. Store learnings:
   mcp.call_tool("knowledge/store_pattern", {
       "category": "authentication",
       "pattern_name": "JWT with refresh tokens",
       "code_example": "...",
       "project_id": "fitness-ai"
   })
```

### Workflow 2: GPT-4 Documentation

```python
# GPT-4 via MCP client

1. Query knowledge:
   knowledge = mcp.call_tool("knowledge/query", {
       "query": "How does our auth system work?",
       "category": "architecture"
   })

2. Get project context:
   context = mcp.read_resource("project://fitness-ai/context")

3. Generate documentation:
   # GPT-4 generates docs

4. Store decision:
   mcp.call_tool("knowledge/store_decision", {
       "project_id": "fitness-ai",
       "title": "Documentation format",
       "decision": "Use MkDocs with Material theme"
   })
```

### Workflow 3: Custom Compliance Agent

```python
# Custom agent for compliance checks

1. Get all projects:
   projects = mcp.call_tool("context/list_projects", {})

2. For each project:
   reviews = mcp.read_resource(f"reviews://{project_id}/history")

3. Check compliance:
   compliance = custom_compliance_check(reviews)

4. Store findings:
   mcp.call_tool("knowledge/store_pattern", {
       "category": "compliance",
       "pattern_name": "GDPR data handling",
       "effectiveness_score": compliance_score
   })
```

## Implementation Stack

- **Server**: Python 3.11+ with MCP SDK
- **Database**: PostgreSQL 14+ (or SQLite for development)
- **Protocol**: MCP over stdio (can add SSE transport)
- **AI Models**: Anthropic SDK (Claude), OpenAI SDK (GPT), extensible
- **GitHub**: PyGithub + gh CLI

## Key Advantages

1. **Cross-Project Learning**: Security patterns from compliance-ai inform fitness-ai
2. **Agent Flexibility**: Switch from Claude to GPT without infrastructure changes
3. **Data Ownership**: All reviews, patterns, decisions in YOUR database
4. **Workflow Extensibility**: Add compliance, docs, testing workflows using same tools
5. **Historical Intelligence**: Every review improves future reviews
