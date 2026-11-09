---
description: Set up DevFlow MCP for a new project. Use when the user wants to set up DevFlow, initialize DevFlow for a project, register a project, or start using DevFlow. Triggers on: "setup devflow", "initialize devflow", "register this project", "start using devflow".
---

# DevFlow Project Setup Skill

You are helping the user set up DevFlow MCP for their project.

## Your Task

1. **Gather project information**
   Ask the user for:
   - Project name (or infer from current directory)
   - Absolute path (use `pwd` to get current directory)
   - Primary programming language (detect from files if possible)
   - Framework if applicable (check package files, README)
   - Repository URL (run `git remote get-url origin` if available)

2. **Create the project in DevFlow**
   - Use `context/create_project` tool with collected information
   - Save the returned project UUID
   - Display the UUID prominently to the user

3. **Save UUID for future use**
   Suggest creating a .devflow file in the project:
   ```bash
   echo "PROJECT_ID=<uuid>" > .devflow
   echo ".devflow" >> .gitignore
   ```

4. **Verify setup**
   - Use `context/get_project` to confirm project was created
   - Show the user their project details

5. **Next steps guidance**
   Tell the user:
   - "Your project is now registered in DevFlow!"
   - "Project UUID: <uuid> (saved in .devflow file)"
   - "You can now run code reviews with: 'review my changes using devflow'"
   - "All reviews will be stored in ~/.devflow/devflow.db"

## Example Flow

```
User: "Set up DevFlow for this project"

You:
1. [Run pwd to get path]
2. [Check git remote for repository URL]
3. [Detect language from files]
4. [Ask for confirmation]

"I'll set up DevFlow for your project. Here's what I detected:
- Name: framework
- Path: /home/joseal/projects/joaltocu/framework
- Language: python
- Framework: mcp (detected from setup.py)
- Repository: git@github.com:joaltocu/devflow-mcp.git

Is this correct?"

[User confirms]

5. [Use context/create_project]
6. [Create .devflow file with UUID]

"✅ DevFlow project created!

Project UUID: a1b2c3d4-e5f6-7890-abcd-ef1234567890

I've saved this UUID to .devflow (added to .gitignore).

You can now:
- Review code: 'review my changes'
- List projects: 'show devflow projects'
- Get project info: 'show this project in devflow'

All reviews use DeepSeek v4 Flash and are stored locally."
```

## Error Handling

- If project already exists: Show existing project and ask if they want to update it
- If path doesn't exist: Confirm the path with the user
- If required fields missing: Ask the user to provide them
- If DevFlow MCP not connected: Instruct user to check /mcp
