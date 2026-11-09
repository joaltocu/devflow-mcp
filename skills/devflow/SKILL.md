---
name: devflow
description: AI-powered code review using DevFlow MCP with multi-stage analysis (quality, security, architecture, coverage). Works with Claude Code, Cursor, Copilot and any MCP-compatible agent. Supports OpenAI, DeepSeek, GLM, Anthropic and other LLM providers. Use whenever the user wants to review code, check changes before commit, set up code review infrastructure, or analyze code quality. Triggers on "review my changes", "check my code", "set up devflow", "code review", "review before commit".
license: MIT
---

# DevFlow - AI-Powered Code Review

DevFlow is an **agent-driven development framework** with multi-stage code review. One command reviews code across **4 dimensions** (quality, security, architecture, coverage) using your choice of LLM provider, with all results stored locally in SQLite.

**How it works:** DevFlow runs as an MCP server that any agent (Claude Code, Cursor, Copilot, etc.) can call. Reviews use configurable LLM backends (OpenAI, DeepSeek, GLM, Anthropic, or Claude Code itself), categorize issues by severity, and store everything in `~/.devflow/devflow.db` for tracking over time.

**Paths.** `references/…` and `scripts/…` below are relative to the folder of this SKILL.md, wherever the skill is installed (plugin, `~/.claude/skills/`, or `skills/devflow/` inside a project). Everything else (`git`, `/mcp`, tool calls) is relative to the working directory.

## 0 · Prerequisites

Before using DevFlow, verify:

1. **MCP server is loaded**
   ```
   /mcp
   ```
   Should show `devflow` with 6 tools. If not, check your MCP configuration (`~/.claude.json` or `.mcp.json` in project) and restart your agent.

2. **Review backend is configured**
   DevFlow supports three modes (auto-detected by priority):
   - **Mode A (default)**: Claude Code reviews — no API key needed, uses your existing Claude Code access
   - **Mode B**: Generic LLM — OpenAI-compatible API (DeepSeek, GLM, OpenAI, Groq, etc.)
   - **Mode C**: Anthropic API — official Claude models via API

   Check `.env` in the DevFlow installation:
   ```bash
   # Mode A: No configuration needed (default)

   # Mode B: Generic LLM (recommended for custom providers)
   LLM_API_KEY=sk-...
   LLM_BASE_URL=https://api.provider.com/v1
   LLM_MODEL=model-name

   # Mode C: Anthropic API
   ANTHROPIC_API_KEY=sk-ant-...
   ```

3. **Database location**
   Reviews are stored in `~/.devflow/devflow.db` (SQLite). On first use, DevFlow creates this automatically.

If `/mcp` shows devflow but tools fail, run the test script from the DevFlow repo: `python test_generic_llm.py`.

## 1 · Register Your Project

Before first review, register the project in DevFlow's database. This tracks reviews per-project and provides context for analysis.

**Gather information:**
1. Project name (infer from directory name or ask)
2. Absolute path (run `pwd` in the working directory)
3. Primary language (detect from files: `package.json` → javascript, `pyproject.toml` → python, etc.)
4. Framework if applicable (`package.json` → look for react/vue/express, `requirements.txt` → django/flask/fastapi)
5. Repository URL (run `git remote get-url origin` if available)

**Create the project:**

Use the MCP tool `context/create_project`:
```json
{
  "name": "project-name",
  "path": "/absolute/path/to/project",
  "language": "python",
  "framework": "fastapi",
  "repository_url": "git@github.com:user/repo.git"
}
```

**Save the project UUID:**

The tool returns a UUID. Save it for future reviews. Best practice: create a `.devflow` file in the project:
```bash
echo "PROJECT_ID=a1b2c3d4-e5f6-7890-abcd-ef1234567890" > .devflow
echo ".devflow" >> .gitignore
```

Never commit `.devflow` to git — it's workspace-specific. The UUID is also stored in `~/.devflow/devflow.db`, so losing the file is not catastrophic (use `context/list_projects` to find it).

**Verify:**

Use `context/get_project` with the UUID to confirm registration and see stored metadata.

## 2 · Run Code Reviews

Once a project is registered, you can review any changes.

### 2.1 Get the diff

Determine what to review:

- **Uncommitted changes:** `git diff`
- **Staged changes only:** `git diff --cached`
- **Specific commit:** `git show <commit-hash>`
- **Branch comparison:** `git diff main...feature-branch`

Copy the diff output. DevFlow needs the full unified diff format (with `@@` hunks).

### 2.2 Call the review tool

Use the MCP tool `development/review_code`:
```json
{
  "project_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "diff": "<full git diff output>",
  "review_types": ["code_quality", "security", "architecture", "coverage"],
  "context": {
    "branch": "feature/new-api",
    "author": "developer-name"
  }
}
```

**Review types explained:**
- `code_quality`: Style, maintainability, best practices, naming, duplication
- `security`: Vulnerabilities, OWASP top 10, credential leaks, injection risks
- `architecture`: Design patterns, separation of concerns, dependencies, coupling
- `coverage`: Missing tests, edge cases, test quality, untested paths

Run all four by default. Omit types only if you have a specific reason (e.g., reviewing documentation → skip coverage).

**What happens:**

DevFlow runs 4 parallel reviews (one per type) using the configured LLM backend. Each review analyzes the diff, checks for issues, and returns structured results. A synthesis step combines findings and produces an overall assessment. The full review (all issues, metadata, timestamps) is stored in `~/.devflow/devflow.db`.

**Time:** ~10-30 seconds depending on diff size and LLM provider (DeepSeek v4 Flash is fastest, Claude Code is slowest due to subprocess overhead).

### 2.3 Analyze without review

For quick stats without LLM analysis, use `development/analyze_diff`:
```json
{
  "diff": "<git diff output>"
}
```

Returns file changes, line counts, additions/deletions — useful for sanity checks before running a full review.

## 3 · Interpret Results

Review results follow a **severity-based structure**:

### Severity levels

- **CRITICAL** 🔴 — Security holes, data loss, credential leaks. **Must fix before commit.** Examples: hardcoded API keys, SQL injection, unvalidated user input reaching eval/exec.
- **HIGH** 🟠 — Bugs, design flaws, major architectural issues. **Should fix soon.** Examples: race conditions, incorrect error handling, broken logic.
- **MEDIUM** 🟡 — Code quality problems, maintainability concerns. **Good to improve.** Examples: duplicated code, magic numbers, unclear naming, missing docstrings.
- **LOW** 🔵 — Minor improvements, stylistic suggestions. **Nice to have.** Examples: unused imports, trailing whitespace, overly verbose code.
- **INFO** ⚪ — Observations, neutral comments. **For reference.** Examples: "This uses a deprecated pattern but still works," "Consider X for future refactors."

### Reading the output

Each issue includes:
- **severity**: One of the above levels
- **message**: What the problem is
- **file**: Affected file path
- **line**: Line number (if applicable)
- **category**: security, performance, maintainability, etc.
- **suggestion**: How to fix it (actionable steps)

The synthesis provides:
- **overall_assessment**: APPROVED, NEEDS_WORK, or BLOCKED (if critical issues exist)
- **critical_issues**: Count of CRITICAL findings
- **summary**: High-level takeaways

### Acting on results

**If CRITICAL issues exist:**

Do not commit. Fix immediately. These are not suggestions — they are **security/correctness failures** that will cause real harm (leaked credentials, exploitable vulnerabilities, data corruption).

**If HIGH issues exist:**

Strongly consider fixing before commit. These are real bugs or design problems that will likely cause issues in production.

**If only MEDIUM/LOW:**

Your call. MEDIUM issues improve long-term maintainability; LOW issues are polish. Both are safe to commit if time-constrained, but address them soon.

**If INFO only or no issues:**

Green light. Commit with confidence.

### Review history

All reviews are in `~/.devflow/devflow.db`. Query with sqlite3:
```bash
sqlite3 ~/.devflow/devflow.db "
  SELECT created_at, passed, critical_issues
  FROM reviews
  WHERE project_id = 'your-uuid'
  ORDER BY created_at DESC
  LIMIT 10;
"
```

Track improvement over time: fewer critical issues per review = healthier codebase.

## 4 · Common Workflows

### Workflow A: Daily development

1. Make changes
2. Before staging: `git diff` → review with DevFlow
3. Fix CRITICAL/HIGH issues
4. Stage clean code: `git add .`
5. Commit

**Why review before staging?** You catch issues while the context is fresh. Fixing is faster when you just wrote the code.

### Workflow B: Pre-commit gate

1. Stage changes: `git add .`
2. Review staged: `git diff --cached` → DevFlow
3. If CRITICAL found: **unstage, fix, re-review**
4. If clean: commit

**Trigger detection:** When the user says "let me commit" or "ready to commit," proactively suggest: "Before you commit, want me to review with DevFlow? Takes ~10 seconds and catches issues before they're in git history."

### Workflow C: PR review

1. Compare branch to main: `git diff main...feature-branch`
2. Full review with DevFlow
3. Address findings in separate fixup commits or amend
4. Re-review after fixes
5. Create PR when clean

**Team usage:** Share `.mcp.json` in the repo so all teammates get DevFlow. Each dev's reviews go to their own `~/.devflow/devflow.db`, but the MCP setup is shared.

### Workflow D: Onboarding to a new codebase

1. Register the project in DevFlow
2. Pick a recent PR or commit: `git show <hash>`
3. Review it to see what DevFlow catches
4. Read the issues to learn code quality standards for this project

**Why this works:** DevFlow highlights patterns (good and bad) in unfamiliar code. Issues flagged → things to avoid when contributing.

## 5 · Troubleshooting

See `references/troubleshooting.md` for details. Quick fixes:

**DevFlow MCP not showing in `/mcp`:**
- Check `~/.claude.json` or `.mcp.json` in project has devflow configured
- Restart your agent (Claude Code, Cursor, etc.)
- Verify `run-mcp.sh` is executable: `chmod +x /path/to/devflow/run-mcp.sh`

**Review fails with API error:**
- Check `.env` has valid `LLM_API_KEY` or `ANTHROPIC_API_KEY`
- Run test script: `python test_generic_llm.py` from DevFlow repo
- Verify network access to API endpoint (check firewall, VPN)

**Review returns empty or nonsensical issues:**
- LLM model may not support JSON mode → check `references/llm-compatibility.md`
- Diff may be too large → split into smaller reviews per file
- Try a different model (e.g., DeepSeek → OpenAI)

**Database errors:**
- Check `~/.devflow/` directory exists and is writable: `ls -la ~/.devflow/`
- Delete and recreate DB: `rm ~/.devflow/devflow.db` (loses history!)
- Check disk space: `df -h ~`

**Project not found:**
- List all projects: use `context/list_projects` tool
- UUID mismatch: verify UUID in `.devflow` file matches DB
- Re-register if needed (won't duplicate if name+path match)

## 6 · Best Practices

**Content fidelity first:**

DevFlow's job is to **find real issues**, not to generate busywork. If a suggestion doesn't apply, ignore it. LLMs sometimes hallucinate problems — trust your judgment. The severity levels are guidance; you decide what matters.

**One review per logical change:**

Don't batch unrelated changes into one diff. Review the new feature separately from the refactor. Clear diffs → clearer issues → faster fixes.

**Fix critical issues immediately:**

CRITICAL severity means **exploitable vulnerability or data integrity failure**. These are not "tech debt" to defer. Fix before proceeding.

**Track trends, not absolutes:**

A project with 5 MEDIUM issues in a 500-line diff is healthier than one with 50 MEDIUM issues in a 100-line diff. Look at issue density over time.

**Review your own code:**

Catch issues **before** PR review. Teammates shouldn't find things DevFlow already flagged. Use DevFlow as a first pass; human review is the second.

**Don't game the system:**

Raising `tolerance` in `scenes.ts`-style configs to silence warnings defeats the purpose. If DevFlow flags something, either fix it or understand why it's a false positive (and document that).

**Offline is critical:**

DevFlow works entirely locally (MCP server + SQLite + configurable LLM). No cloud dependency for your data. Reviews use external LLM APIs, but **all metadata stays on disk**. Back up `~/.devflow/devflow.db` periodically.

## Hard Rules

1. **Never commit with unresolved CRITICAL issues.** Security vulnerabilities and data integrity failures are not negotiable.
2. **Always register a project before first review.** DevFlow needs the UUID to store review history correctly.
3. **Review history is local.** `~/.devflow/devflow.db` is **your workspace data**, not shared via git. Teams share the MCP config (`.mcp.json`), not the database.
4. **One click = one review.** Don't retry the same diff repeatedly hoping for different results. If the review is wrong, either the diff is unclear or the LLM model is unsuitable. Fix the input, don't reroll.
5. **Offline first.** DevFlow must work without internet (except for LLM API calls). Database, MCP server, and all logic are local.
6. **Severity levels are not suggestions.** CRITICAL = fix now. HIGH = fix soon. MEDIUM = improve when you can. LOW = polish. INFO = noted. Treat them as gates, not hints.
7. **Data ownership.** You own `~/.devflow/devflow.db`. Export, back up, or delete it as you see fit. DevFlow has no telemetry, no cloud sync, no lock-in.
