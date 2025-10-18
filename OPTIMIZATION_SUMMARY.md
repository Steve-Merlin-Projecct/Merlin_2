# CLAUDE.md and Hooks Optimization Summary

## Problems with Current CLAUDE.md

1. **Massive Redundancy**: "Communication & Implementation Guide" appears 3 times (600+ lines total)
2. **Behavioral Instructions in Wrong Place**: Static file contains dynamic behavioral rules
3. **Overly Verbose**: Same concepts explained multiple ways
4. **Mixed Concerns**: Project info mixed with agent behavior instructions

## Optimal Architecture

### CLAUDE.md Should Contain (Static Project Context)
- ✅ Project overview and technical stack
- ✅ Architecture and component descriptions
- ✅ Critical workflows (database, git)
- ✅ Environment configuration
- ✅ File locations and standards

**Size**: ~100 lines (vs current 400+ lines)

### Hooks Should Contain (Dynamic Behavioral Guidance)
- ✅ Analysis vs implementation detection
- ✅ Task complexity assessment
- ✅ Documentation reminders
- ✅ TodoWrite enforcement
- ✅ Just-in-time contextual guidance

## Recommended Implementation

### Option 1: Minimal Change
Keep current CLAUDE.md but remove the 2 duplicate sections (lines 151-233 and 292-375)

### Option 2: Clean Separation (RECOMMENDED)
1. Use `CLAUDE_OPTIMIZED.md` (created) - 75 lines of pure project context
2. Use `behavioral_guidance.sh` - Single source for all behavioral rules
3. Use `user-prompt-submit-unified.sh` - Clean orchestrator

## Benefits of Clean Separation

1. **Reduced Token Usage**: 75 lines vs 400+ lines in context
2. **No Redundancy**: Each instruction appears exactly once
3. **Dynamic Guidance**: Hooks provide guidance only when relevant
4. **Maintainability**: Behavioral changes in one place (hooks)
5. **Clarity**: Project info separate from behavioral instructions

## Migration Path

```bash
# Backup current CLAUDE.md
cp CLAUDE.md CLAUDE_BACKUP.md

# Replace with optimized version
cp CLAUDE_OPTIMIZED.md CLAUDE.md

# Use unified hook
mv user-prompt-submit.sh user-prompt-submit-old.sh
mv user-prompt-submit-unified.sh user-prompt-submit.sh

# Remove redundant modules (now in behavioral_guidance.sh)
rm modules/communication_guidance.sh
rm modules/implementation_guidance.sh
```

## Key Insight

**CLAUDE.md should answer**: "What is this project?"
**Hooks should answer**: "How should I behave right now?"

This separation makes the system more efficient and maintainable.