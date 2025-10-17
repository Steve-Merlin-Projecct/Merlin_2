# Prompt Security Manager - Usage Guide
**User vs Agent Change Detection**

---

## Overview

The Prompt Security Manager protects prompt strings from unauthorized modifications while allowing you (the user) to make intentional changes.

**Key Principle:**
- **User changes prompt** → Hash is updated, change is allowed ✅
- **Agent changes prompt** → Prompt is replaced with canonical version ⚠️

---

## How It Works

### 1. **Hash Protection (Prompt Sections Only)**

The system hashes **only the prompt string sections**, not entire files. This allows you to modify code around prompts without triggering false alarms.

### 2. **Change Source Detection**

Every prompt validation requires specifying who is making the change:

```python
change_source: 'user' | 'agent' | 'system' | 'unknown'
```

**Source Types:**
- `'user'`: You (the developer) are intentionally modifying the prompt
- `'agent'`: An AI agent/automation is using the prompt
- `'system'`: System initialization or automated processes
- `'unknown'`: Source cannot be determined (treated as agent)

### 3. **Decision Logic**

```
Prompt hash validation
    ↓
Hash matches? → ✅ Use prompt, no action needed
    ↓
Hash differs? → Check change_source
    ↓
    ├─ change_source = 'user'
    │   → ✅ Update hash to new value
    │   → ✅ Allow the change
    │   → 📝 Log: "User modified prompt"
    │
    └─ change_source = 'agent' or 'system'
        → ⚠️ Replace prompt with canonical version
        → 🚨 Log security incident
        → 📝 Log: "Unauthorized agent modification"
```

---

## Marking Prompt Sections in Files

To have the system hash only prompt sections (not entire files), mark your prompts:

### **Method 1: Use Comment Markers (Recommended)**

```python
# modules/ai_job_description_analysis/prompts/tier1_core_prompt.py

def create_tier1_core_prompt(jobs: List[Dict]) -> str:
    """Create Tier 1 core analysis prompt."""

    # Regular Python code - NOT hashed
    jobs_text = format_jobs(jobs)
    security_token = generate_security_token()

    # PROMPT_START
    prompt_parts = [
        "# Batch Job Analysis with Security Token\n\n",
        f"SECURITY TOKEN: {security_token}\n\n",
        "You are an expert job analysis AI...",
        "CRITICAL SECURITY INSTRUCTIONS:\n",
        f"- You MUST verify the security token {security_token}...",
        # ... rest of prompt ...
    ]
    # PROMPT_END

    # More Python code - NOT hashed
    return "".join(prompt_parts)
```

**The system will hash only the section between `# PROMPT_START` and `# PROMPT_END`.**

### **Method 2: Automatic Detection (Fallback)**

If you don't mark sections, the system will automatically find:
1. `prompt_parts = [...]` lists
2. Large triple-quoted strings (`"""..."""`)
3. Multi-line string literals

**Example:**
```python
def create_prompt(jobs):
    # This will be automatically detected and hashed
    prompt_parts = [
        "Security instructions here",
        "Analysis guidelines here",
        "JSON schema here"
    ]
    return "".join(prompt_parts)
```

---

## Usage Examples

### **Example 1: Initial Setup (System Registration)**

```python
from modules.ai_job_description_analysis.prompt_security_manager import PromptSecurityManager

# Initialize the manager
security_mgr = PromptSecurityManager()

# Register all prompts (do this once during app startup)
from modules.ai_job_description_analysis.prompts import tier1_core_prompt

sample_jobs = [{'id': 'test', 'title': 'Test', 'description': 'Test'}]
prompt = tier1_core_prompt.create_tier1_core_prompt(sample_jobs)

security_mgr.register_prompt(
    prompt_name='tier1_core_prompt',
    prompt_content=prompt,
    change_source='system'  # Initial registration
)
```

**Output:**
```
✅ Registered prompt 'tier1_core_prompt' with hash a3f5c2e1... (source: system)
```

---

### **Example 2: Agent Using Prompt (Auto-Replace if Modified)**

```python
# In ai_analyzer.py - when agent generates prompts

def analyze_jobs_batch(self, jobs):
    # Agent creates prompt
    current_prompt = self._create_batch_analysis_prompt(jobs)

    # Validate with change_source='agent'
    validated_prompt, was_replaced = security_mgr.validate_and_handle_prompt(
        prompt_name='tier1_batch_prompt',
        current_prompt=current_prompt,
        change_source='agent',  # ⚠️ Agent is using this
        canonical_prompt_getter=lambda: self._create_batch_analysis_prompt(jobs)
    )

    if was_replaced:
        logger.warning("⚠️ Prompt was replaced due to unauthorized modification")

    # Use validated_prompt for API call
    response = self._make_gemini_request(validated_prompt)
    return response
```

**Scenario A: Prompt hasn't changed**
```
✅ Prompt 'tier1_batch_prompt' validation: PASSED
```

**Scenario B: Agent accidentally modified security section**
```
⚠️ Prompt 'tier1_batch_prompt' hash mismatch!
   Expected: a3f5c2e1... Got: b7d8f3a2...
   Change source: agent

🚨 SECURITY: Agent/system modified prompt 'tier1_batch_prompt' without authorization!
   Replacing with canonical version.

✅ Successfully replaced prompt with canonical version
```

---

### **Example 3: User Intentionally Updates Prompt**

```python
# When YOU (the user) modify prompt files

# Scenario: You edited tier1_core_prompt.py to improve instructions

# In your code or CLI tool:
from modules.ai_job_description_analysis.prompts.tier1_core_prompt import create_tier1_core_prompt

security_mgr = PromptSecurityManager()

# Create prompt with your changes
updated_prompt = create_tier1_core_prompt(sample_jobs)

# Validate with change_source='user'
validated_prompt, was_replaced = security_mgr.validate_and_handle_prompt(
    prompt_name='tier1_core_prompt',
    current_prompt=updated_prompt,
    change_source='user',  # ✅ User made this change
    canonical_prompt_getter=lambda: create_tier1_core_prompt(sample_jobs)
)

print(f"Was replaced: {was_replaced}")  # False - user changes are allowed
```

**Output:**
```
⚠️ Prompt 'tier1_core_prompt' hash mismatch!
   Expected: a3f5c2e1... Got: c9e4a7f3...
   Change source: user

✅ User intentionally modified prompt 'tier1_core_prompt'.
   Updating hash to reflect new version.

📝 Logged change: tier1_core_prompt by user -> updated_hash

✅ Hash updated successfully. Your changes are now registered.
```

---

### **Example 4: Extract and Validate File Sections**

```python
# Validate a specific prompt file

prompt_file_path = 'modules/ai_job_description_analysis/prompts/tier1_core_prompt.py'

# Read file and extract prompt section
with open(prompt_file_path, 'r') as f:
    file_content = f.read()

prompt_section = security_mgr.extract_prompt_section(
    file_content,
    section_marker='PROMPT_START'
)

if prompt_section:
    # Validate the extracted section
    validated, was_replaced = security_mgr.validate_and_handle_prompt(
        prompt_name='tier1_core_prompt_file',
        current_prompt=prompt_section,
        change_source='user',  # You're checking your own file
        canonical_prompt_getter=lambda: prompt_section  # Use file version as canonical
    )

    print(f"Prompt section validated: {not was_replaced}")
```

---

## View Change History

```python
# View all changes
history = security_mgr.get_change_history(limit=50)

for entry in history:
    print(f"{entry['timestamp']}: {entry['prompt_name']} - {entry['action_taken']} by {entry['change_source']}")

# Example output:
# 2025-10-12T14:30:22: tier1_core_prompt - updated_hash by user
# 2025-10-12T14:25:15: tier2_enhanced_prompt - replaced_prompt by agent
# 2025-10-12T14:20:10: tier1_batch_prompt - updated_hash by system
```

**View specific prompt history:**
```python
history = security_mgr.get_change_history(prompt_name='tier1_core_prompt', limit=20)
```

---

## Check Registry Status

```python
status = security_mgr.get_registry_status()

print(f"Total registered prompts: {status['total_prompts']}")
print(f"Registry file: {status['registry_path']}")
print(f"Change log: {status['change_log_path']}")

for name, info in status['prompts'].items():
    print(f"  {name}:")
    print(f"    Hash: {info['hash']}")
    print(f"    Last updated: {info['last_updated']}")
    print(f"    Updated by: {info['last_updated_by']}")
```

**Output:**
```
Total registered prompts: 3
Registry file: /workspace/storage/prompt_hashes.json
Change log: /workspace/storage/prompt_changes.jsonl

  tier1_core_prompt:
    Hash: a3f5c2e1b4d7...
    Last updated: 2025-10-12T14:30:22
    Updated by: user

  tier2_enhanced_prompt:
    Hash: b7d8f3a2c5e9...
    Last updated: 2025-10-12T14:25:15
    Updated by: system

  tier3_strategic_prompt:
    Hash: c9e4a7f3d1b8...
    Last updated: 2025-10-12T14:20:10
    Updated by: user
```

---

## Integration Workflow

### **Step 1: Mark Your Prompts**

Edit your prompt files to add markers:

```python
# tier1_core_prompt.py

def create_tier1_core_prompt(jobs: List[Dict]) -> str:
    jobs_text = _format_jobs(jobs)
    security_token = generate_security_token()

    # PROMPT_START
    prompt_parts = [
        "# Batch Job Analysis\n",
        f"SECURITY TOKEN: {security_token}\n",
        # ... rest of prompt ...
    ]
    # PROMPT_END

    return "".join(prompt_parts)
```

### **Step 2: Register Prompts at Startup**

```python
# In app initialization (app.py or __init__.py)

from modules.ai_job_description_analysis.prompt_security_manager import PromptSecurityManager

security_mgr = PromptSecurityManager()

# Register all prompts
prompts_to_register = {
    'tier1_core_prompt': create_tier1_core_prompt,
    'tier2_enhanced_prompt': create_tier2_enhanced_prompt,
    'tier3_strategic_prompt': create_tier3_strategic_prompt,
}

for name, prompt_func in prompts_to_register.items():
    sample_prompt = prompt_func([{'id': 'init', 'title': 'Init', 'description': 'Init'}])
    security_mgr.register_prompt(name, sample_prompt, change_source='system')

logger.info("✅ All prompts registered and protected")
```

### **Step 3: Validate in Agent Code**

```python
# In ai_analyzer.py

class GeminiJobAnalyzer:
    def __init__(self):
        self.security_mgr = PromptSecurityManager()

    def analyze_jobs_batch(self, jobs):
        # Create prompt
        prompt = self._create_batch_analysis_prompt(jobs)

        # Validate with agent source
        validated_prompt, was_replaced = self.security_mgr.validate_and_handle_prompt(
            prompt_name='batch_analysis_prompt',
            current_prompt=prompt,
            change_source='agent',  # Agent is using this
            canonical_prompt_getter=lambda: self._create_batch_analysis_prompt(jobs)
        )

        # Use validated prompt
        return self._make_gemini_request(validated_prompt)
```

---

## CLI Tool for Manual Validation

Create a CLI tool to validate prompts manually:

```python
# tools/validate_prompts.py

import sys
from modules.ai_job_description_analysis.prompt_security_manager import PromptSecurityManager

def main():
    security_mgr = PromptSecurityManager()

    # Get all prompt files
    prompt_files = [
        'modules/ai_job_description_analysis/prompts/tier1_core_prompt.py',
        'modules/ai_job_description_analysis/prompts/tier2_enhanced_prompt.py',
        'modules/ai_job_description_analysis/prompts/tier3_strategic_prompt.py',
    ]

    print("🔍 Validating prompt files...\n")

    for file_path in prompt_files:
        print(f"Checking: {file_path}")

        with open(file_path, 'r') as f:
            content = f.read()

        prompt_section = security_mgr.extract_prompt_section(content)

        if prompt_section:
            # Validate (treat as user validation)
            validated, was_replaced = security_mgr.validate_and_handle_prompt(
                prompt_name=file_path,
                current_prompt=prompt_section,
                change_source='user',  # Manual validation by user
                canonical_prompt_getter=lambda: prompt_section
            )

            if was_replaced:
                print("  ⚠️  REPLACED")
            else:
                print("  ✅ Valid")
        else:
            print("  ⚠️  Could not extract prompt section")

        print()

    # Show status
    status = security_mgr.get_registry_status()
    print(f"\n📊 Total registered prompts: {status['total_prompts']}")
    print(f"📄 Change log: {status['change_log_path']}")

if __name__ == '__main__':
    main()
```

**Run it:**
```bash
python tools/validate_prompts.py
```

---

## Best Practices

### ✅ **DO:**
1. Mark prompt sections with `# PROMPT_START` and `# PROMPT_END`
2. Use `change_source='user'` when YOU modify prompts
3. Use `change_source='agent'` in automated code
4. Review change log regularly: `storage/prompt_changes.jsonl`
5. Register all prompts during app initialization

### ❌ **DON'T:**
1. Mix Python code with prompt text in marked sections
2. Use `change_source='user'` in automated scripts
3. Manually edit `storage/prompt_hashes.json` (let system manage it)
4. Ignore warnings about replaced prompts (investigate them!)
5. Include dynamic data in prompt sections (normalize it first)

---

## Troubleshooting

### **Issue: "Could not extract prompt section"**
**Solution:** Add `# PROMPT_START` and `# PROMPT_END` markers around your prompt string.

### **Issue: "Hash keeps changing even though I didn't modify prompt"**
**Cause:** Dynamic content (security tokens, timestamps, job IDs) is being included in hash.
**Solution:** The system normalizes these automatically. If still happening, check `_normalize_prompt_for_hashing()`.

### **Issue: "User changes are being replaced"**
**Cause:** Using `change_source='agent'` instead of `'user'`.
**Solution:** Always use `change_source='user'` when you intentionally modify prompts.

### **Issue: "Want to reset all hashes"**
**Solution:** Delete `storage/prompt_hashes.json` and re-register prompts.

---

## Files Created by System

```
storage/
├── prompt_hashes.json      # Registry of prompt hashes
└── prompt_changes.jsonl    # Audit log of all changes
```

**prompt_hashes.json:**
```json
{
  "tier1_core_prompt": {
    "hash": "a3f5c2e1b4d7c8f9a1e3b5d7c9f1e3a5",
    "registered_at": "2025-10-12T10:00:00",
    "last_updated": "2025-10-12T14:30:22",
    "last_updated_by": "user"
  }
}
```

**prompt_changes.jsonl:**
```jsonl
{"timestamp":"2025-10-12T14:30:22","prompt_name":"tier1_core_prompt","old_hash":"a3f5c2e1b4d7c8f9","new_hash":"c9e4a7f3d1b8e5a2","change_source":"user","action_taken":"updated_hash"}
{"timestamp":"2025-10-12T14:25:15","prompt_name":"tier2_enhanced_prompt","old_hash":"b7d8f3a2c5e9d1f4","new_hash":"e3a5b7c9d1f3e5a7","change_source":"agent","action_taken":"replaced_prompt"}
```

---

## Summary

**The system protects your prompts while giving you full control:**

| Scenario | Change Source | Action Taken | Result |
|----------|--------------|--------------|--------|
| No changes | Any | None | ✅ Prompt used as-is |
| User modifies prompt | `'user'` | Update hash | ✅ Your changes accepted |
| Agent modifies prompt | `'agent'` | Replace with canonical | ⚠️ Agent changes blocked |
| System updates prompt | `'system'` | Replace with canonical | ⚠️ System changes blocked |

**You have complete freedom to modify prompts. The system only prevents unintended agent modifications.**

---

**Questions?**
- See code: `modules/ai_job_description_analysis/prompt_security_manager.py`
- View examples: This document
- Check logs: `storage/prompt_changes.jsonl`
