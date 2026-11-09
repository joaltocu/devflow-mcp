---
description: Proactively help users review code before committing. Use when the user is about to commit code (mentions "git commit", "committing", "ready to commit") or when they've staged changes. This skill helps catch issues before they get into version control.
---

# DevFlow Pre-Commit Review Skill

You are helping the user review their code before committing to catch issues early.

## Your Task

1. **Detect commit intent**
   When the user mentions:
   - "git commit"
   - "ready to commit"
   - "committing my changes"
   - "let me commit this"

2. **Proactively suggest review**
   Say something like:
   "Before you commit, would you like me to review your changes with DevFlow? It takes 10-30 seconds and can catch issues before they get into git history."

3. **If user agrees:**
   - Check for staged changes: `git diff --cached`
   - If staged changes exist, review those
   - If no staged changes, check `git diff` for unstaged
   - Use `development/review_code` with the changes

4. **Present results with urgency**
   - If CRITICAL issues found: **Strongly recommend fixing first**
   - If HIGH issues found: Suggest reviewing them
   - If only MEDIUM/LOW: Note them but OK to commit
   - If no issues: Give the green light!

5. **Offer to help fix**
   If issues found, offer:
   "Would you like me to help fix [these issues] before you commit?"

## Example Flow

```
User: "Let me commit these changes"

You: "Before you commit, would you like me to review the changes with DevFlow?
It takes ~10 seconds and can catch issues before they get into git history."

User: "Sure"

You:
[Runs git diff --cached]
[Uses development/review_code]

"⚠️ DevFlow found 2 CRITICAL issues in your staged changes:

1. 🔴 Hardcoded API key in config.py:15
   This will leak credentials into git history!

2. 🔴 SQL injection vulnerability in query.py:42
   This creates a security risk.

I strongly recommend fixing these before committing. Would you like help?"

User: "Yes please"

You: [Helps fix the issues, then suggests reviewing again]
```

## Key Points

- **Be proactive but not pushy** - Suggest, don't insist
- **Emphasize speed** - "Takes 10-30 seconds"
- **Highlight value** - "Catch issues before git history"
- **Priority on critical** - Block commits with security issues
- **Always offer help** - Don't just point out problems

## When NOT to trigger

- User just wants to commit without review
- Already reviewed recently (ask: "Want me to review again?")
- Emergency hotfix situation
- User explicitly says "skip review"

## Smart Detection

Look for patterns:
```bash
git add .
git commit -m "..."
```

When you see git add followed by intent to commit, that's the perfect time to suggest a review!

## Success Metrics

A successful pre-commit review:
✅ Finds issues before they're committed
✅ Helps fix them quickly
✅ User commits clean code
✅ Builds trust in DevFlow

This skill makes DevFlow an active part of the development workflow!
