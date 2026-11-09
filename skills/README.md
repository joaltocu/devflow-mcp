# DevFlow MCP Skills

This directory contains the comprehensive DevFlow skill for Claude Code. The skill provides complete guidance for using DevFlow MCP's AI-powered code review system.

## Skill Structure

DevFlow uses a **comprehensive skill format** with all documentation in one place:

```
skills/
├── devflow/
│   ├── SKILL.md              # Main comprehensive skill
│   ├── references/           # Reference documentation
│   │   ├── mcp-tools.md      # Complete MCP tool reference
│   │   ├── quickstart.md     # 5-minute quick start guide
│   │   ├── llm-compatibility.md  # LLM provider compatibility
│   │   └── troubleshooting.md    # Common issues and fixes
│   └── scripts/              # Helper scripts
│       ├── register-project.sh   # Register projects from CLI
│       ├── review-history.sh     # Query review history
│       └── README.md             # Scripts documentation
└── devflow-archive/          # Old individual skills (deprecated)
```

## The DevFlow Skill

### SKILL.md

The main skill file provides complete guidance across 7 sections:

**Section 0: Prerequisites**
- MCP server verification
- Review backend configuration (3 modes)
- Database location

**Section 1: Register Your Project**
- Project registration workflow
- UUID management
- Verification steps

**Section 2: Run Code Reviews**
- Getting diffs (uncommitted, staged, branches)
- Calling review tools
- Review types explained

**Section 3: Interpret Results**
- Severity levels (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- Issue structure
- When to commit vs fix

**Section 4: Common Workflows**
- Daily development
- Pre-commit gate
- PR review
- Onboarding to new codebases

**Section 5: Troubleshooting**
- References troubleshooting.md for detailed fixes

**Section 6: Best Practices**
- Content fidelity
- Fix critical immediately
- Track trends
- Offline-first approach

**Hard Rules**
- Never commit with CRITICAL issues
- Always register before review
- Review history is local
- One click = one review
- Offline first
- Severity levels are gates
- Data ownership

### Skill Triggers

The skill activates on phrases like:
- "review my changes"
- "check my code"
- "set up devflow"
- "code review"
- "review before commit"

## Installation

### Option 1: Symlink (Recommended for Development)

```bash
# Create symlink to always use latest version
ln -s /home/joseal/projects/joaltocu/framework/skills/devflow/SKILL.md \
      ~/.claude/skills/devflow.md
```

### Option 2: Copy (For Stable Deployment)

```bash
# Copy the comprehensive skill
cp /home/joseal/projects/joaltocu/framework/skills/devflow/SKILL.md \
   ~/.claude/skills/devflow.md
```

**Note:** The skill file references `references/` and `scripts/` directories using relative paths. These work whether you symlink or copy, as long as the directory structure is preserved.

## Verifying Installation

After installing the skill, verify it's available:

```bash
ls -la ~/.claude/skills/devflow.md
```

Start a new Claude Code session and try:

```
You: "How do I use DevFlow?"
```

Claude should automatically load the DevFlow skill and provide comprehensive guidance.

## Requirements

- DevFlow MCP must be installed and configured
- MCP server running (configured in `.mcp.json` or `~/.claude.json`)
- Optional: LLM API credentials in `.env` (or use Claude Code mode - free, no API key needed)

## Usage Examples

### Example 1: First-Time Project Setup

```
You: "Set up DevFlow for this project"

Claude: [Loads DevFlow skill, Section 1]
        [Collects project info: name, path, language, framework, repo URL]
        [Calls context/create_project MCP tool]
        [Saves UUID to .devflow file]

"✅ DevFlow project created!
Project UUID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
Saved to .devflow (added to .gitignore)

You can now run code reviews. Make some changes and say:
'Review my changes with DevFlow'"
```

### Example 2: Code Review Workflow

```
You: "Review my changes"

Claude: [Loads DevFlow skill, Section 2]
        [Runs: git diff]
        [Calls development/review_code with 4 review types]
        [Analyzes results per Section 3]

"Code review complete:

🔴 CRITICAL (1):
  • src/config.py:12 - Hardcoded API key in source code
    Suggestion: Move to environment variables

🟠 HIGH (0)
🟡 MEDIUM (2):
  • Missing docstrings in new functions
  • Duplicated error handling logic

Overall: 🛑 BLOCKED - Fix critical issue before committing.
Want me to fix the API key issue?"

You: "Yes, fix it"

Claude: [Moves API key to .env, updates code]
        "Fixed! Review again?"
```

### Example 3: Pre-Commit Safety Net

```
You: "Let me commit these changes"

Claude: [Loads DevFlow skill, Section 4 - Pre-commit workflow]

"Before you commit, I should review with DevFlow.
Takes ~10 seconds and catches issues early.

[Runs review automatically]

✓ No critical issues found.
Safe to commit!"
```

### Example 4: Branch Review Before PR

```
You: "Review all changes in my feature branch vs main"

Claude: [Runs: git diff main...feature-branch]
        [Reviews complete branch diff]

"Branch review (15 files, 847 lines changed):

✓ No critical or high issues
🟡 3 medium code quality suggestions:
  1. Add tests for new API endpoints
  2. Document the new authentication flow
  3. Extract magic numbers to constants

Quality score: 85/100 - Ready for PR with minor improvements"
```

## How the Skill Works

The DevFlow skill is a comprehensive markdown file with:

1. **Frontmatter** - Defines when the skill triggers:
   ```yaml
   ---
   name: devflow
   description: AI-powered code review using DevFlow MCP...
   license: MIT
   ---
   ```

2. **Numbered sections (0-6)** - Complete guidance for each workflow stage

3. **Hard Rules** - Non-negotiable requirements (security, data ownership)

4. **References** - Linked documentation in `references/` directory:
   - `mcp-tools.md` - Complete tool specifications
   - `quickstart.md` - Fast setup guide
   - `llm-compatibility.md` - Provider compatibility matrix
   - `troubleshooting.md` - Solutions to common issues

5. **Scripts** - Helper commands in `scripts/` directory:
   - `register-project.sh` - CLI project registration
   - `review-history.sh` - Query review database

When Claude detects trigger phrases (like "review my changes"), it loads the skill and follows the structured workflow, providing consistent, comprehensive guidance.

## Customization

You can extend the DevFlow skill:

1. **Add custom workflows** - Extend Section 4 (Common Workflows)
2. **Add reference docs** - Create new files in `references/`
3. **Add helper scripts** - Add scripts to `scripts/`
4. **Customize triggers** - Modify `description` in frontmatter

## Troubleshooting

### Skill Not Loading

1. **Check installation**:
   ```bash
   ls -la ~/.claude/skills/devflow.md
   ```

2. **Verify symlink** (if using symlinks):
   ```bash
   readlink ~/.claude/skills/devflow.md
   # Should point to: /home/joseal/projects/joaltocu/framework/skills/devflow/SKILL.md
   ```

3. **Restart Claude Code**:
   Skills are loaded at startup - exit and restart

4. **Check MCP connection**:
   ```
   /mcp
   ```
   Should show devflow with 6 tools (2 development + 4 context)

### Skill Triggers Incorrectly

If the skill activates when you don't want it:
- Edit `description` in `SKILL.md` frontmatter
- Make trigger phrases more specific
- Restart Claude Code after editing

### Reviews Failing

See `skills/devflow/references/troubleshooting.md` for detailed solutions:
- MCP server issues
- API configuration errors
- Database problems
- Git integration issues

### Helper Scripts Not Working

Make scripts executable:
```bash
chmod +x /home/joseal/projects/joaltocu/framework/skills/devflow/scripts/*.sh
```

See `skills/devflow/scripts/README.md` for script-specific troubleshooting.

## Reference Documentation

The `references/` directory contains detailed documentation:

- **mcp-tools.md** - Complete reference for all 6 MCP tools with parameters, returns, examples
- **quickstart.md** - Get DevFlow running in 5 minutes
- **llm-compatibility.md** - Tested LLM providers with performance comparison
- **troubleshooting.md** - Solutions to common issues

## Helper Scripts

The `scripts/` directory contains CLI helpers:

- **register-project.sh** - Register projects from command line
- **review-history.sh** - Query review database, show trends
- **README.md** - Complete scripts documentation

## Old Skills (Deprecated)

The `devflow-archive/` directory contains old individual skills:
- devflow-review.md
- devflow-setup.md
- devflow-help.md
- devflow-precommit.md

These are deprecated in favor of the comprehensive SKILL.md format. They're kept for reference but should not be used.

## More Information

- DevFlow MCP server: `README_MCP.md`
- Main documentation: `README.md`
- Quick start: `skills/devflow/references/quickstart.md`

## Contributing

To contribute to the DevFlow skill:

1. **Extend sections** - Add to Section 4 (workflows) or Section 6 (best practices)
2. **Add references** - Create new reference docs in `references/`
3. **Add scripts** - Create helper scripts in `scripts/`
4. **Improve examples** - Add real-world usage examples
5. **Test thoroughly** - Verify in Claude Code before submitting
6. **Submit PR** - Include before/after examples

## License

The DevFlow skill and all associated documentation are part of the DevFlow MCP project and are distributed under the MIT license.
