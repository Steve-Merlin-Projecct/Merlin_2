# /cltr Command: Claude Tree Context Loader

## Overview
The `/cltr` command (Claude Tree) is a specialized context loader for worktree-specific tasks, designed to streamline Claude's interaction with task-specific contexts.

## Command Workflow
1. Detect current worktree automatically
2. Load `.claude-task-context.md` file
3. Launch Claude in a mode that skips standard permission checks
4. Pre-inject task description into Claude's context
5. Prompt Claude to ask 1-3 clarifying questions

## Usage
\`\`\`bash
/cltr  # Loads context from current worktree
\`\`\`

## Behavior
- Automatically finds task context file
- Handles different context scenarios
- Provides flexible, context-aware initialization

## Configuration
- Context file: \`.claude-task-context.md\`
- Assumed location: Current worktree root
- Optional: Can specify explicit context file path

## Error Handling
- Gracefully handles missing context files
- Provides informative messages about context loading
- Fallback to standard Claude initialization if no context found

## Best Practices
- Always maintain an up-to-date \`.claude-task-context.md\`
- Use clear, concise task descriptions
- Include relevant technical details and constraints
