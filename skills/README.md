# DevFlow MCP Skills

This directory contains Claude Code skills for DevFlow MCP. Skills make it easier to use DevFlow by providing specialized prompts and workflows.

## Available Skills

### 1. devflow-review.md
**Automatic code review using DevFlow**

Triggers: "review my changes", "check my code", "run devflow review"

What it does:
- Checks for uncommitted or staged changes
- Runs comprehensive code review using DeepSeek
- Presents issues grouped by severity
- Offers to help fix critical issues

### 2. devflow-setup.md
**Set up DevFlow for a new project**

Triggers: "setup devflow", "initialize devflow", "register this project"

What it does:
- Collects project information
- Creates project in DevFlow database
- Saves project UUID for future use
- Provides next steps guidance

### 3. devflow-help.md
**Quick help and examples for DevFlow**

Triggers: "how to use devflow", "devflow help", "what can devflow do"

What it does:
- Shows available commands
- Explains review process
- Provides examples
- Offers context-aware guidance

### 4. devflow-precommit.md
**Proactive pre-commit review**

Triggers: When user mentions "git commit", "ready to commit"

What it does:
- Suggests reviewing before commit
- Analyzes staged changes
- Strongly warns about critical issues
- Helps fix problems before committing

## Installation

### Option 1: Copy All Skills (Recommended)

```bash
# From the DevFlow repository
cp skills/*.md ~/.claude/skills/
```

### Option 2: Copy Individual Skills

```bash
# Copy only the skills you want
cp skills/devflow-review.md ~/.claude/skills/
cp skills/devflow-setup.md ~/.claude/skills/
```

### Option 3: Symlink (For Development)

```bash
# Create symlinks to always use latest versions
ln -s /home/joseal/projects/joaltocu/framework/skills/*.md ~/.claude/skills/
```

## Verifying Installation

After copying skills, start a new Claude Code session and try:

```
You: "How do I use DevFlow?"
```

Claude should automatically invoke the `devflow-help` skill and show you a guide.

## Requirements

- DevFlow MCP must be installed and configured
- MCP server must be running (configured in ~/.config/claude/mcp.json)
- DeepSeek API credentials configured in .env (or Claude Code mode)

## Usage Examples

### Example 1: First-Time Setup

```
You: "Set up DevFlow for this project"

Claude: [Invokes devflow-setup skill]
        [Collects project info and creates it in DevFlow]

"✅ DevFlow project created!
Project UUID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
..."
```

### Example 2: Code Review

```
You: "Review my changes"

Claude: [Invokes devflow-review skill]
        [Checks git diff and runs review]

"I've reviewed your changes using DevFlow:
⚠️ CRITICAL ISSUES (1):
1. Hardcoded API key in config.py
..."
```

### Example 3: Pre-Commit

```
You: "Let me commit these changes"

Claude: [Invokes devflow-precommit skill]

"Before you commit, would you like me to review with DevFlow?
Takes ~10 seconds and catches issues early."
```

## How Skills Work

Skills are markdown files with:
1. **Frontmatter**: Defines when the skill triggers
2. **Content**: Instructions for Claude on how to help

When Claude detects a trigger phrase, it automatically loads the skill and follows its instructions, making DevFlow easier to use.

## Customization

You can customize skills by editing the .md files:

1. **Change triggers**: Modify the `description` in frontmatter
2. **Add workflows**: Extend the task instructions
3. **Create new skills**: Copy existing skill and modify

## Troubleshooting

### Skills Not Working

1. **Check installation**:
   ```bash
   ls -la ~/.claude/skills/devflow-*.md
   ```

2. **Restart Claude Code**:
   Skills are loaded at startup

3. **Check MCP connection**:
   ```
   /mcp
   ```
   Should show devflow with 6 tools

### Skill Triggers Wrong

If a skill triggers when you don't want it:
- Edit the `description` in the skill file
- Make the trigger phrases more specific
- Restart Claude Code after editing

## Contributing

To create a new DevFlow skill:

1. Copy an existing skill as a template
2. Modify the frontmatter `description`
3. Update the task instructions
4. Test in a new Claude Code session
5. Submit a PR with your skill

## More Information

- DevFlow MCP documentation: See README_MCP.md
- Quick start guide: See QUICKSTART_MCP.md
- MCP server setup: See GETTING_STARTED.md

## License

These skills are part of the DevFlow MCP project and are distributed under the same MIT license.
