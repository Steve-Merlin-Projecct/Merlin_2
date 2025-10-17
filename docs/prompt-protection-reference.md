# Prompt Protection Reference Guide
**Current State of Prompt Protection System**

---

## Quick Answer

### **Files That Need Prompt Protection**
✅ **ALL prompt files now have protection markers implemented!**

**Protected prompt files:**
1. ✅ `modules/ai_job_description_analysis/prompts/tier1_core_prompt.py` (lines 92-157)
2. ✅ `modules/ai_job_description_analysis/prompts/tier2_enhanced_prompt.py` (lines 92-144)
3. ✅ `modules/ai_job_description_analysis/prompts/tier3_strategic_prompt.py` (lines 92-169)

### **Where Canonical Prompts Are Stored**
**Canonical prompts are the Python functions themselves** in the files above.

The `PromptSecurityManager` doesn't store canonical prompts - it calls the **prompt generation functions** to get fresh canonical versions when needed.

---

## Current State

### **Protection System: Built & Integrated ✅**
- **File:** `modules/ai_job_description_analysis/prompt_security_manager.py`
- **Status:** ✅ Complete and active in production
- **Integration:** ✅ Integrated into `ai_analyzer.py` (line 411-417)
- **Registration:** ✅ Automatic at app startup in `app_modular.py` (line 96-164)
- **Storage:**
  - Hash registry: `storage/prompt_hashes.json` (created on app startup)
  - Change log: `storage/prompt_changes.jsonl` (created on first change)
  - Security incidents: `storage/security_incidents.jsonl` (created on first incident)

### **Prompt Files: FULLY Protected ✅**
All prompt files **have markers** and are registered at startup.

**Current structure (WITH markers - IMPLEMENTED):**
```python
# tier1_core_prompt.py - CURRENT PRODUCTION STATE

def create_tier1_core_prompt(jobs: List[Dict]) -> str:
    """Create Tier 1 core analysis prompt."""

    # ✅ Code before prompt - NOT hashed
    jobs_text = ""
    for i, job in enumerate(jobs, 1):
        # ... job formatting code ...

    security_token = generate_security_token()
    job_count = len(jobs)

    # PROMPT_START  ← Marker present (line 92)
    # ✅ Only this section is hashed
    prompt_parts = [
        "# Batch Job Analysis with Security Token\n\n",
        f"SECURITY TOKEN: {security_token}\n\n",
        f"You are an expert job analysis AI...",
        "CRITICAL SECURITY INSTRUCTIONS:\n",
        # ... rest of prompt parts ...
        f"\"security_token\": \"{{security_token}}\",\n",  # Variable-style token reference
    ]
    # PROMPT_END  ← Marker present (line 157)

    # ✅ Code after prompt - NOT hashed
    return "".join(prompt_parts)
```

---

## How Canonical Prompts Work

### **Concept: Canonical = Source of Truth**
The canonical prompt is **not stored as text** - it's the **output of the Python function**.

**Example Flow:**

```python
# 1. Agent generates a prompt (might be tampered with)
agent_prompt = create_tier1_core_prompt(jobs)  # Agent calls function

# 2. Security manager validates it
validated, was_replaced = security_mgr.validate_and_handle_prompt(
    prompt_name='tier1_core_prompt',
    current_prompt=agent_prompt,
    change_source='agent',
    canonical_prompt_getter=lambda: create_tier1_core_prompt(jobs)  # 👈 Function call
)

# 3. If tampered, security manager calls the function again to get canonical version
if hash_mismatch and source == 'agent':
    canonical = canonical_prompt_getter()  # Calls create_tier1_core_prompt(jobs)
    return canonical  # Returns fresh, untampered prompt
```

### **Why Not Store Canonical Text?**
1. **Dynamic content:** Prompts contain security tokens, job data, etc.
2. **Always fresh:** Calling the function ensures we get the latest code version
3. **No stale data:** Stored text could become outdated
4. **Simple:** Just call the function, no separate storage needed

---

## What Gets Protected

### **Protected (Hashed):**
```python
# PROMPT_START
prompt_parts = [
    "# Batch Job Analysis with Security Token\n\n",           # ✅ Hashed
    f"SECURITY TOKEN: {security_token}\n\n",                  # ✅ Hashed (normalized)
    "You are an expert job analysis AI...",                   # ✅ Hashed
    "CRITICAL SECURITY INSTRUCTIONS:\n",                      # ✅ Hashed
    f"- You MUST verify the security token {security_token}", # ✅ Hashed (normalized)
    # ... all prompt content ...
]
# PROMPT_END
```

**Hash normalization removes:**
- Security tokens (replaced with `SEC_TOKEN_PLACEHOLDER`)
- Timestamps (replaced with `TIMESTAMP_PLACEHOLDER`)
- Job IDs (replaced with `UUID_PLACEHOLDER`)
- Variable job descriptions (replaced with `PLACEHOLDER`)

**So the hash represents the prompt STRUCTURE, not the dynamic data.**

### **NOT Protected (Not Hashed):**
```python
# Before markers
jobs_text = ""                           # ❌ Not hashed
for i, job in enumerate(jobs, 1):        # ❌ Not hashed
    jobs_text += format_job(job)         # ❌ Not hashed

security_token = generate_token()        # ❌ Not hashed
job_count = len(jobs)                    # ❌ Not hashed

# After markers
return "".join(prompt_parts)             # ❌ Not hashed
```

---

## Implementation Checklist

### **Step 1: Add Markers to Prompt Files** ✅

**File:** `tier1_core_prompt.py`
```python
def create_tier1_core_prompt(jobs: List[Dict]) -> str:
    # Existing code above...

    # PROMPT_START
    prompt_parts = [
        # ... existing prompt content ...
    ]
    # PROMPT_END

    return "".join(prompt_parts)
```

**File:** `tier2_enhanced_prompt.py`
```python
def create_tier2_enhanced_prompt(jobs_with_tier1: List[Dict]) -> str:
    # Existing code above...

    # PROMPT_START
    prompt_parts = [
        # ... existing prompt content ...
    ]
    # PROMPT_END

    return "".join(prompt_parts)
```

**File:** `tier3_strategic_prompt.py`
```python
def create_tier3_strategic_prompt(jobs_with_tier1_tier2: List[Dict]) -> str:
    # Existing code above...

    # PROMPT_START
    prompt_parts = [
        # ... existing prompt content ...
    ]
    # PROMPT_END

    return "".join(prompt_parts)
```

### **Step 2: Register Prompts at Startup** ✅

**File:** `app.py` or `__init__.py` (wherever your app initializes)

```python
from modules.ai_job_description_analysis.prompt_security_manager import PromptSecurityManager
from modules.ai_job_description_analysis.prompts.tier1_core_prompt import create_tier1_core_prompt
from modules.ai_job_description_analysis.prompts.tier2_enhanced_prompt import create_tier2_enhanced_prompt
from modules.ai_job_description_analysis.prompts.tier3_strategic_prompt import create_tier3_strategic_prompt

# Initialize security manager (do this once at app startup)
security_mgr = PromptSecurityManager()

# Register all prompts
sample_jobs = [{'id': 'init', 'title': 'Init Job', 'description': 'Init description'}]

# Tier 1
tier1_prompt = create_tier1_core_prompt(sample_jobs)
security_mgr.register_prompt('tier1_core_prompt', tier1_prompt, change_source='system')

# Tier 2
tier2_jobs = [{'job_data': sample_jobs[0], 'tier1_results': {}}]
tier2_prompt = create_tier2_enhanced_prompt(tier2_jobs)
security_mgr.register_prompt('tier2_enhanced_prompt', tier2_prompt, change_source='system')

# Tier 3
tier3_jobs = [{'job_data': sample_jobs[0], 'tier1_results': {}, 'tier2_results': {}}]
tier3_prompt = create_tier3_strategic_prompt(tier3_jobs)
security_mgr.register_prompt('tier3_strategic_prompt', tier3_prompt, change_source='system')

logger.info("✅ All prompts registered and protected")
```

### **Step 3: Integrate into AI Analyzer** ✅

**File:** `ai_analyzer.py`

```python
from modules.ai_job_description_analysis.prompt_security_manager import PromptSecurityManager

class GeminiJobAnalyzer:
    def __init__(self):
        # ... existing init code ...
        self.security_mgr = PromptSecurityManager()

    def analyze_jobs_batch(self, jobs: List[Dict]) -> Dict:
        # Create prompt
        current_prompt = self._create_batch_analysis_prompt(jobs)

        # Validate with agent source (will auto-replace if modified)
        validated_prompt, was_replaced = self.security_mgr.validate_and_handle_prompt(
            prompt_name='tier1_batch_prompt',
            current_prompt=current_prompt,
            change_source='agent',  # Agent is using this
            canonical_prompt_getter=lambda: self._create_batch_analysis_prompt(jobs)
        )

        if was_replaced:
            logger.warning("⚠️ Prompt was replaced due to tampering")

        # Use validated prompt for API call
        response = self._make_gemini_request(validated_prompt)
        return response
```

---

## Storage Files

### **1. Hash Registry** (`storage/prompt_hashes.json`)
**Purpose:** Stores approved hashes for each prompt

**Created:** Automatically on first registration

**Example content:**
```json
{
  "tier1_core_prompt": {
    "hash": "a3f5c2e1b4d7c8f9a1e3b5d7c9f1e3a5b7c9d1f3e5a7b9d1f3e5a7b9d1f3e5a7",
    "registered_at": "2025-10-12T10:00:00.000000",
    "last_updated": "2025-10-12T14:30:22.123456",
    "last_updated_by": "user"
  },
  "tier2_enhanced_prompt": {
    "hash": "b7d8f3a2c5e9d1f4a3e7b5c9d1f3e5a7b9d1f3e5a7b9d1f3e5a7b9d1f3e5a7b9",
    "registered_at": "2025-10-12T10:00:00.000000",
    "last_updated": "2025-10-12T10:00:00.000000",
    "last_updated_by": "system"
  },
  "tier3_strategic_prompt": {
    "hash": "c9e4a7f3d1b8e5a2c9f1e3a5b7d9c1e3f5a7b9d1e3f5a7b9d1e3f5a7b9d1e3f5",
    "registered_at": "2025-10-12T10:00:00.000000",
    "last_updated": "2025-10-12T10:00:00.000000",
    "last_updated_by": "system"
  }
}
```

### **2. Change Log** (`storage/prompt_changes.jsonl`)
**Purpose:** Audit trail of all prompt changes

**Created:** Automatically on first change

**Example content:**
```jsonl
{"timestamp":"2025-10-12T14:30:22.123456","prompt_name":"tier1_core_prompt","old_hash":"a3f5c2e1b4d7c8f9","new_hash":"c9e4a7f3d1b8e5a2","change_source":"user","action_taken":"updated_hash","additional_info":{"reason":"user_modification"}}
{"timestamp":"2025-10-12T14:35:10.987654","prompt_name":"tier1_batch_prompt","old_hash":"b7d8f3a2c5e9d1f4","new_hash":"e3a5b7c9d1f3e5a7","change_source":"agent","action_taken":"replaced_prompt","additional_info":{"reason":"unauthorized_agent_modification"}}
{"timestamp":"2025-10-12T14:40:05.456789","prompt_name":"tier2_enhanced_prompt","old_hash":"c9e4a7f3d1b8e5a2","new_hash":"f1e3a5b7c9d1f3e5","change_source":"user","action_taken":"updated_hash","additional_info":{"reason":"user_modification"}}
```

---

## Viewing Prompt Protection Status

### **CLI Command (Create This)**

**File:** `tools/check_prompt_protection.py`

```python
#!/usr/bin/env python3
"""Check prompt protection status"""

from modules.ai_job_description_analysis.prompt_security_manager import PromptSecurityManager

def main():
    security_mgr = PromptSecurityManager()

    print("🔐 Prompt Protection Status\n")
    print("=" * 60)

    # Check if registry exists
    status = security_mgr.get_registry_status()

    print(f"Total registered prompts: {status['total_prompts']}")
    print(f"Registry file: {status['registry_path']}")
    print(f"Change log: {status['change_log_path']}")
    print()

    if status['total_prompts'] > 0:
        print("Registered Prompts:")
        print("-" * 60)
        for name, info in status['prompts'].items():
            print(f"  📄 {name}")
            print(f"     Hash: {info['hash']}...")
            print(f"     Last updated: {info['last_updated']}")
            print(f"     Updated by: {info['last_updated_by']}")
            print()
    else:
        print("⚠️  No prompts registered yet!")
        print("   Run registration script to initialize protection.")
        print()

    # Check recent changes
    history = security_mgr.get_change_history(limit=10)
    if history:
        print("\nRecent Changes (last 10):")
        print("-" * 60)
        for entry in history:
            action = entry['action_taken']
            source = entry['change_source']
            icon = "✅" if source == 'user' else "⚠️"
            print(f"  {icon} {entry['timestamp']}: {entry['prompt_name']}")
            print(f"     Action: {action} by {source}")
            print()

    print("=" * 60)

if __name__ == '__main__':
    main()
```

**Run it:**
```bash
python tools/check_prompt_protection.py
```

---

## Summary

### **Current State:**
- ✅ Protection system built and ready (`prompt_security_manager.py`)
- ✅ Prompt files have markers added (`# PROMPT_START` / `# PROMPT_END`)
- ✅ Integrated into AI analyzer (`ai_analyzer.py:411-417, 647-683`)
- ✅ Registration active at app startup (`app_modular.py:96-164`)
- ✅ CLI tools created (`tools/check_prompt_protection.py`, `tools/update_prompt_hash.py`)
- ✅ Test suite created (`tests/test_prompt_protection_integration.py`)

### **Canonical Prompts:**
- **Location:** The Python functions themselves (not stored separately)
- **Access:** Call the function to get fresh canonical version
- **Files:**
  - `tier1_core_prompt.py::create_tier1_core_prompt()`
  - `tier2_enhanced_prompt.py::create_tier2_enhanced_prompt()`
  - `tier3_strategic_prompt.py::create_tier3_strategic_prompt()`

### **Storage:**
- **Hashes:** `storage/prompt_hashes.json` (created on first use)
- **Audit log:** `storage/prompt_changes.jsonl` (created on first use)
- **Both created automatically** when first prompt is registered

### **Usage:**
1. **Check Protection Status:** `python tools/check_prompt_protection.py`
2. **Update Hash After User Change:** `python tools/update_prompt_hash.py tier1_core_prompt`
3. **Run Tests:** `pytest tests/test_prompt_protection_integration.py -v`
4. **Testing Checklist:** See `docs/TESTING-CHECKLIST-prompt-protection.md`

---

**Need help with implementation? See:**
- Usage guide: `docs/prompt-security-usage-guide.md`
- Code reference: `modules/ai_job_description_analysis/prompt_security_manager.py`
