# DevFlow MCP Tools Reference

Complete reference for all 6 DevFlow MCP tools.

## Development Tools

### development/review_code

**Purpose:** Run comprehensive multi-stage code review

**Parameters:**
- `project_id` (string, required) — Project UUID from `context/create_project`
- `diff` (string, required) — Full git diff output (unified format with @@ hunks)
- `review_types` (array, optional) — Which reviews to run. Default: `["code_quality", "security", "architecture", "coverage"]`
- `context` (object, optional) — Additional metadata: `{ "branch": "...", "author": "...", "description": "..." }`

**Returns:**
```json
{
  "success": true,
  "reviews": [
    {
      "type": "security",
      "passed": false,
      "issues": [
        {
          "severity": "critical",
          "message": "Hardcoded API key detected",
          "file": "config.py",
          "line": 15,
          "category": "credentials",
          "suggestion": "Move to environment variables using os.getenv()"
        }
      ]
    },
    ...
  ],
  "synthesized": {
    "overall_assessment": "NEEDS_WORK",
    "critical_issues": 1,
    "summary": "Found 1 critical security issue that must be addressed..."
  }
}
```

**Review types explained:**

- **code_quality**: Checks style, naming, duplication, complexity, best practices. Flags: magic numbers, unclear names, long functions, nested conditionals, duplicated logic.

- **security**: Checks for vulnerabilities. Flags: hardcoded secrets, SQL/command injection, XSS, insecure deserialization, weak crypto, unvalidated input.

- **architecture**: Checks design patterns and structure. Flags: tight coupling, circular dependencies, god objects, missing abstractions, violated SOLID principles.

- **coverage**: Checks test gaps. Flags: untested code paths, missing edge case tests, insufficient assertions, lack of error case tests.

**Error handling:**

- Project not found → Use `context/list_projects` to find UUID or register new project
- Invalid diff format → Check git diff includes full context (not just changed lines)
- API error → Check `.env` has valid LLM credentials, test with `test_generic_llm.py`
- Too large diff → Split review into smaller chunks per file or module

---

### development/analyze_diff

**Purpose:** Extract structured metadata from a git diff without LLM analysis

**Parameters:**
- `diff` (string, required) — Git diff output

**Returns:**
```json
{
  "file_changes": [
    {
      "file": "src/main.py",
      "additions": 15,
      "deletions": 8,
      "change_type": "modified"
    }
  ],
  "stats": {
    "total_additions": 47,
    "total_deletions": 23,
    "files_changed": 5
  }
}
```

**Use cases:**
- Quick sanity check before full review (is this diff reasonable?)
- Automated gates in CI (fail if >500 lines changed in one PR)
- Metrics tracking (code churn, review burden)

---

## Context Tools

### context/create_project

**Purpose:** Register a new project in DevFlow database

**Parameters:**
- `name` (string, required) — Project name (human-readable, used in UIs)
- `path` (string, required) — Absolute path to project directory
- `language` (string, optional) — Primary language: `python`, `javascript`, `typescript`, `go`, `rust`, etc.
- `framework` (string, optional) — Framework if applicable: `react`, `fastapi`, `django`, `express`, etc.
- `repository_url` (string, optional) — Git remote URL (for reference)
- `extra_metadata` (object, optional) — Any additional key-value data

**Returns:**
```json
{
  "project_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "my-project",
  "path": "/home/user/projects/my-project",
  "language": "python",
  "framework": "fastapi",
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Best practices:**
- Save the UUID to `.devflow` file in project root
- Add `.devflow` to `.gitignore` (workspace-specific, not shared)
- Use descriptive names (not just "project" or "repo")
- Set language/framework accurately — helps review context

**Error handling:**
- Duplicate name+path → Returns existing project (idempotent)
- Invalid path → Check path exists and is readable
- Missing required fields → Provide name and path at minimum

---

### context/list_projects

**Purpose:** List all projects in DevFlow database

**Parameters:**
- `limit` (number, optional) — Max projects to return. Default: 100
- `offset` (number, optional) — Skip N projects (for pagination). Default: 0

**Returns:**
```json
{
  "projects": [
    {
      "project_id": "...",
      "name": "framework",
      "path": "/home/joseal/projects/joaltocu/framework",
      "language": "python",
      "created_at": "..."
    },
    ...
  ],
  "total": 15
}
```

**Use cases:**
- Find UUID when `.devflow` file is lost
- Show user all registered projects
- Audit which projects are tracked
- Pagination for large project lists

---

### context/get_project

**Purpose:** Get detailed information about a specific project

**Parameters:**
- `project_id` (string, required) — Project UUID

**Returns:**
```json
{
  "project_id": "...",
  "name": "framework",
  "path": "/home/joseal/projects/joaltocu/framework",
  "language": "python",
  "framework": "mcp",
  "repository_url": "git@github.com:joaltocu/devflow-mcp.git",
  "extra_metadata": {},
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Use cases:**
- Verify project registration after creation
- Show project details to user
- Check metadata before review
- Audit project configuration

---

### context/update_project

**Purpose:** Update project metadata

**Parameters:**
- `project_id` (string, required) — Project UUID
- `name` (string, optional) — New name
- `path` (string, optional) — New path
- `language` (string, optional) — Update language
- `framework` (string, optional) — Update framework
- `repository_url` (string, optional) — Update repo URL
- `extra_metadata` (object, optional) — Update or add metadata

**Returns:** Updated project object (same as `get_project`)

**Use cases:**
- Project moved to new directory
- Framework changed (e.g., migrated from Express to Fastapi)
- Add metadata discovered later
- Fix incorrect initial registration

**Note:** Cannot change UUID (immutable). To "rename" a project with new UUID, create new and delete old.

---

## Tool Composition Patterns

### Pattern A: First-time setup

```
1. context/list_projects → check if already registered
2. If not found:
   - Gather info (pwd, git remote, detect language)
   - context/create_project
   - Save UUID to .devflow file
3. context/get_project → verify
```

### Pattern B: Standard review

```
1. Run `git diff` (or `git diff --cached`)
2. context/list_projects → find UUID for current project
3. development/review_code with UUID + diff
4. Present issues, offer to fix CRITICAL/HIGH
```

### Pattern C: Pre-commit gate

```
1. Detect user intent ("ready to commit")
2. Check `git diff --cached` (staged changes)
3. If changes exist:
   - Ask user: "Review before commit?"
   - If yes: development/review_code
   - If CRITICAL found: Strongly warn, offer to fix
```

### Pattern D: Quick stats

```
1. Run `git diff`
2. development/analyze_diff (no LLM call)
3. Show file count, line count
4. If reasonable size: Offer full review
5. If too large: Suggest splitting
```

---

## Rate Limits and Performance

**LLM backend limits:**
- DeepSeek v4 Flash: Fast (~5-15 sec/review), cheap (~$0.001/review)
- Claude via Anthropic API: Medium (~10-20 sec), moderate cost (~$0.003/review)
- Claude Code subprocess: Slow (~20-40 sec), free (uses your Claude Code quota)
- OpenAI GPT-4: Slow (~20-30 sec), expensive (~$0.01/review)

**Parallelization:**
- Four review types run in parallel (quality + security + architecture + coverage)
- One synthesis step runs after all four complete
- Total time ≈ slowest individual review + synthesis (~2-3 sec)

**Diff size recommendations:**
- **< 500 lines**: Single review, fast
- **500-2000 lines**: Single review, slower but manageable
- **2000-5000 lines**: Consider splitting by file or module
- **> 5000 lines**: Definitely split — LLM context limits may cause failures

**Best practices:**
- Review frequently (small diffs)
- Use `analyze_diff` first to check size
- Split large PRs into multiple reviews per component
- Cache results in DB → don't re-review identical diffs
