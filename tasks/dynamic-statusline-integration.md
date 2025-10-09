---
title: Dynamic Statusline Integration
created: '2025-10-07'
updated: '2025-10-07'
author: Steve-Merlin-Projecct
type: task
status: active
tags:
- dynamic
- statusline
- integration
---

# Dynamic Statusline Integration

## Overview
Implement dynamic statusline that displays real-time Claude Code session information including active tools, engaged agents, and available context.

## Current State
Statusline currently displays static information:
- Project name and version
- Git branch and status
- Virtual environment
- Agent: always shows "direct"
- Tools: static list
- Context: static description

## Proposed Enhancement
Create a mechanism for Claude Code to communicate session state to the statusline script in real-time.

## Technical Approach

### Option 1: State File Approach
- Claude Code writes session state to `.claude/statusline-state.json`
- Statusline script reads and parses this file
- State file contains:
  ```json
  {
    "active_tools": ["code_analysis", "api_research", "debugging"],
    "current_agent": "direct" | "code-reviewer" | "debugger" | etc.,
    "available_context": "Full project structure",
    "last_updated": "2025-10-07T03:49:00Z"
  }
  ```

### Option 2: Hook-Based Approach
- Use Claude Code hooks to update state file on tool usage
- Pre/post tool hooks write to state file
- Statusline reads on each refresh

### Option 3: Process Communication
- Use named pipes or Unix sockets for IPC
- More complex but potentially more robust

## Implementation Tasks

1. **Design state schema**
   - Define JSON structure for session state
   - Determine what information is valuable to display
   - Consider performance implications

2. **Create state management system**
   - Implement state file writer (Python helper)
   - Add error handling for file I/O
   - Implement state file reader in bash statusline script

3. **Integrate with Claude Code session**
   - Determine trigger points for state updates
   - Consider using hooks vs. manual updates
   - Handle stale data (timeout mechanism)

4. **Update statusline script**
   - Parse JSON state file
   - Format dynamic information for display
   - Fallback to defaults if state unavailable
   - Handle malformed or missing state gracefully

5. **Testing**
   - Test with various agent types
   - Test tool engagement tracking
   - Test performance impact
   - Test failure modes (missing file, malformed JSON)

## Benefits
- Real-time visibility into Claude Code operations
- Better understanding of which agent is active
- Track tool usage patterns
- Improved debugging and workflow awareness

## Considerations
- Performance: statusline refresh rate vs. file I/O
- Race conditions: concurrent reads/writes
- Stale data: how long before data is considered outdated?
- File permissions and location
- Cross-platform compatibility (if needed)

## Priority
Medium - Nice to have for enhanced visibility, but not critical for core functionality

## Related Files
- `.claude/statusline.sh` - Current statusline implementation
- `.claude/hooks/` - Potential hook integration points
- `.claude/settings.local.json` - May need configuration options
