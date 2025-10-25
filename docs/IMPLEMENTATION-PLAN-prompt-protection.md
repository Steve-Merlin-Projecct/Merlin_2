---
title: "Implementation Plan Prompt Protection"
type: technical_doc
component: general
status: draft
tags: []
---

# Implementation Plan: Hash-and-Replace Canonical Prompt Protection
**Goal:** Integrate prompt security system to prevent unauthorized agent modifications while allowing user changes

---

## System Overview

**Current State:**
- ✅ `PromptSecurityManager` class built (`prompt_security_manager.py`)
- ✅ All three tier prompts have `# PROMPT_START` / `# PROMPT_END` markers
- ✅ Round-trip token validation implemented
- ⚠️ Not integrated into `ai_analyzer.py` yet
- ⚠️ No registration at startup
- ⚠️ No prompt protection active

**Target State:**
- ✅ All prompts registered at app startup
- ✅ Validation on every prompt use (agent source → auto-replace)
- ✅ Hash registry tracks approved versions
- ✅ Audit log records all changes
- ✅ CLI tool to view protection status

---

## Phase 1: Core Integration (Week 1)

### Step 1.1: Initialize Security Manager in Analyzer
**File:** `modules/ai_job_description_analysis/ai_analyzer.py`

**Current `__init__` method:** (around line 400)
```python
class GeminiJobAnalyzer:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        # ... existing init code ...
```

**Add after existing init code:**
```python
        # Initialize prompt security manager
        from modules.ai_job_description_analysis.prompt_security_manager import PromptSecurityManager
        self.security_mgr = PromptSecurityManager()
        logger.info("✅ Prompt security manager initialized")
```

**Estimated time:** 5 minutes

---

### Step 1.2: Add Prompt Validation to Tier 1
**File:** `modules/ai_job_description_analysis/ai_analyzer.py`

**Find:** `_create_batch_analysis_prompt()` method (line 639)

**Current code:**
```python
def _create_batch_analysis_prompt(self, jobs: List[Dict]) -> str:
    """Create comprehensive analysis prompt for batch processing"""

    # ... existing prompt building code ...

    return "".join(prompt_parts)
```

**Replace with:**
```python
def _create_batch_analysis_prompt(self, jobs: List[Dict]) -> str:
    """Create comprehensive analysis prompt for batch processing"""

    # ... existing prompt building code ...

    prompt = "".join(prompt_parts)

    # SECURITY: Validate prompt with hash-and-replace system
    validated_prompt, was_replaced = self.security_mgr.validate_and_handle_prompt(
        prompt_name='tier1_batch_prompt',
        current_prompt=prompt,
        change_source='agent',  # This is agent-generated
        canonical_prompt_getter=lambda: self._create_batch_analysis_prompt_canonical(jobs)
    )

    if was_replaced:
        logger.warning("⚠️ Tier 1 prompt was replaced due to unauthorized modification")

    return validated_prompt

def _create_batch_analysis_prompt_canonical(self, jobs: List[Dict]) -> str:
    """
    Canonical version of batch analysis prompt (used for hash-and-replace)
    This is the trusted source - if agent modifies prompt, this version replaces it
    """
    # Copy the ENTIRE prompt building logic from _create_batch_analysis_prompt
    # (This ensures canonical version is always available for replacement)

    jobs_text = ""
    for i, job in enumerate(jobs, 1):
        description = job.get("description", "")
        title = job.get("title", "")
        sanitized_description = sanitize_job_description(description)
        sanitized_title = sanitize_job_description(title)
        jobs_text += f"""
JOB {i}:
ID: {job['id']}
TITLE: {sanitized_title}
DESCRIPTION: {sanitized_description[:2000]}...
---
"""

    security_token = generate_security_token()
    self._current_security_token = security_token
    job_count = len(jobs)

    prompt_parts = [
        # ... ENTIRE prompt building logic from original method ...
    ]

    return "".join(prompt_parts)
```

**Alternative Approach (Recommended):** Use the new tier prompt files instead of monolithic prompt:

```python
def _create_batch_analysis_prompt(self, jobs: List[Dict]) -> str:
    """Create Tier 1 analysis prompt using modular tier system"""
    from modules.ai_job_description_analysis.prompts.tier1_core_prompt import create_tier1_core_prompt

    # Generate prompt using tier1 module
    prompt = create_tier1_core_prompt(jobs)

    # SECURITY: Validate with hash-and-replace
    validated_prompt, was_replaced = self.security_mgr.validate_and_handle_prompt(
        prompt_name='tier1_core_prompt',
        current_prompt=prompt,
        change_source='agent',
        canonical_prompt_getter=lambda: create_tier1_core_prompt(jobs)
    )

    if was_replaced:
        logger.warning("⚠️ Tier 1 prompt was replaced due to unauthorized modification")

    return validated_prompt
```

**Estimated time:** 30 minutes

---

### Step 1.3: Register Prompts at App Startup
**File:** `app_modular.py` or `app.py` (main application entry point)

**Find:** Application initialization section (after imports, before route definitions)

**Add registration code:**
```python
# Initialize AI analyzer and register prompts
from modules.ai_job_description_analysis.ai_analyzer import GeminiJobAnalyzer
from modules.ai_job_description_analysis.prompt_security_manager import PromptSecurityManager
from modules.ai_job_description_analysis.prompts.tier1_core_prompt import create_tier1_core_prompt
from modules.ai_job_description_analysis.prompts.tier2_enhanced_prompt import create_tier2_enhanced_prompt
from modules.ai_job_description_analysis.prompts.tier3_strategic_prompt import create_tier3_strategic_prompt

# Initialize security manager
security_mgr = PromptSecurityManager()

# Create sample jobs for registration (just need structure, not real data)
sample_jobs = [{
    'id': 'init_sample',
    'title': 'Sample Job Title',
    'description': 'Sample job description for initialization purposes. ' * 20
}]

# Register Tier 1 prompt
logger.info("Registering Tier 1 core prompt...")
tier1_prompt = create_tier1_core_prompt(sample_jobs)
security_mgr.register_prompt('tier1_core_prompt', tier1_prompt, change_source='system')

# Register Tier 2 prompt
logger.info("Registering Tier 2 enhanced prompt...")
tier2_jobs = [{
    'job_data': sample_jobs[0],
    'tier1_results': {
        'structured_data': {'skill_requirements': {'skills': []}},
        'classification': {'industry': 'Technology', 'seniority_level': 'Mid-Level'},
        'authenticity_check': {'credibility_score': 8}
    }
}]
tier2_prompt = create_tier2_enhanced_prompt(tier2_jobs)
security_mgr.register_prompt('tier2_enhanced_prompt', tier2_prompt, change_source='system')

# Register Tier 3 prompt
logger.info("Registering Tier 3 strategic prompt...")
tier3_jobs = [{
    'job_data': sample_jobs[0],
    'tier1_results': tier2_jobs[0]['tier1_results'],
    'tier2_results': {
        'stress_level_analysis': {'estimated_stress_level': 5},
        'red_flags': {'unrealistic_expectations': {'detected': False}},
        'implicit_requirements': {'unstated_skills': []}
    }
}]
tier3_prompt = create_tier3_strategic_prompt(tier3_jobs)
security_mgr.register_prompt('tier3_strategic_prompt', tier3_prompt, change_source='system')

logger.info("✅ All prompts registered and protected")
```

**Estimated time:** 20 minutes

---

### Step 1.4: Test Basic Protection
**Create test script:** `tools/test_prompt_protection.py`

```python
#!/usr/bin/env python3
"""Test prompt protection system"""

from modules.ai_job_description_analysis.ai_analyzer import GeminiJobAnalyzer
from modules.ai_job_description_analysis.prompts.tier1_core_prompt import create_tier1_core_prompt

def test_protection():
    print("🧪 Testing prompt protection system...\n")

    # Initialize analyzer (includes security manager)
    analyzer = GeminiJobAnalyzer()

    # Create sample job
    sample_jobs = [{
        'id': 'test_job_1',
        'title': 'Software Engineer',
        'description': 'Test job description for protection testing. ' * 30
    }]

    # Test 1: Generate prompt through analyzer (should pass validation)
    print("Test 1: Normal prompt generation...")
    prompt = analyzer._create_batch_analysis_prompt(sample_jobs)
    print("✅ Normal generation passed\n")

    # Test 2: Manually modify prompt (simulate agent tampering)
    print("Test 2: Simulating agent tampering...")
    tampered_prompt = create_tier1_core_prompt(sample_jobs)
    tampered_prompt = tampered_prompt.replace("CRITICAL SECURITY", "MODIFIED BY AGENT")

    validated_prompt, was_replaced = analyzer.security_mgr.validate_and_handle_prompt(
        prompt_name='tier1_core_prompt',
        current_prompt=tampered_prompt,
        change_source='agent',
        canonical_prompt_getter=lambda: create_tier1_core_prompt(sample_jobs)
    )

    if was_replaced:
        print("✅ Tampered prompt was detected and replaced\n")
    else:
        print("❌ Tampering was NOT detected!\n")

    # Test 3: User modification (should update hash)
    print("Test 3: Simulating user modification...")
    user_modified_prompt = create_tier1_core_prompt(sample_jobs)
    user_modified_prompt = user_modified_prompt.replace("CRITICAL SECURITY", "UPDATED BY USER")

    validated_prompt, was_replaced = analyzer.security_mgr.validate_and_handle_prompt(
        prompt_name='tier1_core_prompt',
        current_prompt=user_modified_prompt,
        change_source='user',
        canonical_prompt_getter=lambda: create_tier1_core_prompt(sample_jobs)
    )

    if not was_replaced:
        print("✅ User modification was allowed (hash updated)\n")
    else:
        print("❌ User modification was incorrectly replaced!\n")

    print("🎉 All tests completed")

if __name__ == '__main__':
    test_protection()
```

**Run:**
```bash
python tools/test_prompt_protection.py
```

**Expected output:**
```
🧪 Testing prompt protection system...

Test 1: Normal prompt generation...
✅ Normal generation passed

Test 2: Simulating agent tampering...
⚠️ Hash mismatch detected for tier1_core_prompt
🔄 Replacing with canonical version (source: agent)
✅ Tampered prompt was detected and replaced

Test 3: Simulating user modification...
✅ Hash mismatch detected - updating hash (source: user)
✅ User modification was allowed (hash updated)

🎉 All tests completed
```

**Estimated time:** 30 minutes

---

## Phase 2: Tier 2 & 3 Integration (Week 1, Day 3-4)

### Step 2.1: Add Tier 2 Methods to Analyzer
**File:** `modules/ai_job_description_analysis/ai_analyzer.py`

**Add new method:**
```python
def analyze_jobs_tier2(self, jobs_with_tier1: List[Dict]) -> Dict:
    """
    Run Tier 2 (Enhanced) analysis with Tier 1 context

    Args:
        jobs_with_tier1: List of dicts with:
            - job_data: {id, title, description, company}
            - tier1_results: Complete Tier 1 analysis

    Returns:
        Dictionary with Tier 2 analysis results
    """
    from modules.ai_job_description_analysis.prompts.tier2_enhanced_prompt import create_tier2_enhanced_prompt

    if not jobs_with_tier1:
        return {"results": [], "success": False, "error": "No jobs provided"}

    try:
        # Generate Tier 2 prompt
        prompt = create_tier2_enhanced_prompt(jobs_with_tier1)

        # SECURITY: Validate with hash-and-replace
        validated_prompt, was_replaced = self.security_mgr.validate_and_handle_prompt(
            prompt_name='tier2_enhanced_prompt',
            current_prompt=prompt,
            change_source='agent',
            canonical_prompt_getter=lambda: create_tier2_enhanced_prompt(jobs_with_tier1)
        )

        if was_replaced:
            logger.warning("⚠️ Tier 2 prompt was replaced due to unauthorized modification")

        # Make API request
        response = self._make_gemini_request(validated_prompt)

        # Parse and validate
        results = self._parse_batch_response(response, [j['job_data'] for j in jobs_with_tier1])

        return {
            "results": results,
            "success": True,
            "jobs_analyzed": len(jobs_with_tier1)
        }

    except Exception as e:
        logger.error(f"Tier 2 analysis failed: {str(e)}")
        return {"results": [], "success": False, "error": str(e)}
```

**Estimated time:** 45 minutes (includes Tier 3 method below)

---

### Step 2.2: Add Tier 3 Methods to Analyzer
**File:** `modules/ai_job_description_analysis/ai_analyzer.py`

**Add new method:**
```python
def analyze_jobs_tier3(self, jobs_with_context: List[Dict]) -> Dict:
    """
    Run Tier 3 (Strategic) analysis with Tier 1 + 2 context

    Args:
        jobs_with_context: List of dicts with:
            - job_data: {id, title, description, company}
            - tier1_results: Complete Tier 1 analysis
            - tier2_results: Complete Tier 2 analysis

    Returns:
        Dictionary with Tier 3 analysis results
    """
    from modules.ai_job_description_analysis.prompts.tier3_strategic_prompt import create_tier3_strategic_prompt

    if not jobs_with_context:
        return {"results": [], "success": False, "error": "No jobs provided"}

    try:
        # Generate Tier 3 prompt
        prompt = create_tier3_strategic_prompt(jobs_with_context)

        # SECURITY: Validate with hash-and-replace
        validated_prompt, was_replaced = self.security_mgr.validate_and_handle_prompt(
            prompt_name='tier3_strategic_prompt',
            current_prompt=prompt,
            change_source='agent',
            canonical_prompt_getter=lambda: create_tier3_strategic_prompt(jobs_with_context)
        )

        if was_replaced:
            logger.warning("⚠️ Tier 3 prompt was replaced due to unauthorized modification")

        # Make API request
        response = self._make_gemini_request(validated_prompt)

        # Parse and validate
        results = self._parse_batch_response(response, [j['job_data'] for j in jobs_with_context])

        return {
            "results": results,
            "success": True,
            "jobs_analyzed": len(jobs_with_context)
        }

    except Exception as e:
        logger.error(f"Tier 3 analysis failed: {str(e)}")
        return {"results": [], "success": False, "error": str(e)}
```

---

## Phase 3: Monitoring & CLI Tools (Week 1, Day 5)

### Step 3.1: Create Protection Status CLI Tool
**File:** `tools/check_prompt_protection.py`

```python
#!/usr/bin/env python3
"""Check prompt protection status and view audit log"""

import json
import sys
from pathlib import Path
from modules.ai_job_description_analysis.prompt_security_manager import PromptSecurityManager

def main():
    security_mgr = PromptSecurityManager()

    print("=" * 80)
    print("🔐 PROMPT PROTECTION STATUS")
    print("=" * 80)
    print()

    # Check registry
    registry_file = Path("storage/prompt_hashes.json")
    if not registry_file.exists():
        print("⚠️  No prompts registered yet!")
        print("   Run app startup to initialize protection system.")
        print()
        return

    with open(registry_file, 'r') as f:
        registry = json.load(f)

    print(f"📊 Total Registered Prompts: {len(registry)}")
    print()

    # Display each prompt
    for prompt_name, info in registry.items():
        print(f"📄 {prompt_name}")
        print(f"   Hash: {info['hash'][:16]}...")
        print(f"   Registered: {info['registered_at']}")
        print(f"   Last Updated: {info['last_updated']}")
        print(f"   Updated By: {info['last_updated_by']}")
        print()

    # Check change log
    change_log_file = Path("storage/prompt_changes.jsonl")
    if change_log_file.exists():
        print("-" * 80)
        print("📝 RECENT CHANGES (Last 10):")
        print("-" * 80)
        print()

        with open(change_log_file, 'r') as f:
            changes = [json.loads(line) for line in f]

        for change in changes[-10:]:
            icon = "✅" if change['change_source'] == 'user' else "⚠️"
            print(f"{icon} {change['timestamp']}")
            print(f"   Prompt: {change['prompt_name']}")
            print(f"   Action: {change['action_taken']}")
            print(f"   Source: {change['change_source']}")
            print()

    print("=" * 80)

if __name__ == '__main__':
    main()
```

**Run:**
```bash
python tools/check_prompt_protection.py
```

**Estimated time:** 20 minutes

---

### Step 3.2: Create Hash Update CLI Tool (For User Modifications)
**File:** `tools/update_prompt_hash.py`

```python
#!/usr/bin/env python3
"""Update prompt hash after intentional user modification"""

import sys
from modules.ai_job_description_analysis.prompt_security_manager import PromptSecurityManager
from modules.ai_job_description_analysis.prompts.tier1_core_prompt import create_tier1_core_prompt
from modules.ai_job_description_analysis.prompts.tier2_enhanced_prompt import create_tier2_enhanced_prompt
from modules.ai_job_description_analysis.prompts.tier3_strategic_prompt import create_tier3_strategic_prompt

def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/update_prompt_hash.py <prompt_name>")
        print()
        print("Available prompts:")
        print("  - tier1_core_prompt")
        print("  - tier2_enhanced_prompt")
        print("  - tier3_strategic_prompt")
        return

    prompt_name = sys.argv[1]
    security_mgr = PromptSecurityManager()

    # Sample data for prompt generation
    sample_jobs = [{'id': 'update', 'title': 'Update', 'description': 'Update prompt hash. ' * 20}]

    # Generate current version of prompt
    if prompt_name == 'tier1_core_prompt':
        current_prompt = create_tier1_core_prompt(sample_jobs)
    elif prompt_name == 'tier2_enhanced_prompt':
        tier2_jobs = [{'job_data': sample_jobs[0], 'tier1_results': {}}]
        current_prompt = create_tier2_enhanced_prompt(tier2_jobs)
    elif prompt_name == 'tier3_strategic_prompt':
        tier3_jobs = [{'job_data': sample_jobs[0], 'tier1_results': {}, 'tier2_results': {}}]
        current_prompt = create_tier3_strategic_prompt(tier3_jobs)
    else:
        print(f"❌ Unknown prompt: {prompt_name}")
        return

    # Register as user modification
    print(f"Updating hash for: {prompt_name}")
    security_mgr.register_prompt(prompt_name, current_prompt, change_source='user')
    print("✅ Hash updated successfully")

if __name__ == '__main__':
    main()
```

**Run:**
```bash
python tools/update_prompt_hash.py tier1_core_prompt
```

**Estimated time:** 15 minutes

---

## Phase 4: Testing & Validation (Week 2)

### Step 4.1: Integration Testing
**Create test suite:** `tests/test_prompt_protection_integration.py`

```python
#!/usr/bin/env python3
"""Integration tests for prompt protection system"""

import pytest
from modules.ai_job_description_analysis.ai_analyzer import GeminiJobAnalyzer
from modules.ai_job_description_analysis.prompts.tier1_core_prompt import create_tier1_core_prompt

def test_analyzer_has_security_manager():
    """Test that analyzer initializes with security manager"""
    analyzer = GeminiJobAnalyzer()
    assert hasattr(analyzer, 'security_mgr')
    assert analyzer.security_mgr is not None

def test_prompt_validation_on_generation():
    """Test that prompts are validated when generated"""
    analyzer = GeminiJobAnalyzer()

    sample_jobs = [{
        'id': 'test_1',
        'title': 'Test Engineer',
        'description': 'Test description for integration testing. ' * 50
    }]

    # This should trigger validation
    prompt = analyzer._create_batch_analysis_prompt(sample_jobs)

    # Prompt should be validated and returned
    assert prompt is not None
    assert len(prompt) > 100

def test_agent_tampering_detection():
    """Test that agent tampering is detected and replaced"""
    analyzer = GeminiJobAnalyzer()

    sample_jobs = [{'id': 'test', 'title': 'Test', 'description': 'Test. ' * 30}]

    # Generate canonical prompt
    canonical_prompt = create_tier1_core_prompt(sample_jobs)

    # Simulate tampering
    tampered_prompt = canonical_prompt.replace("SECURITY TOKEN", "TAMPERED TOKEN")

    # Validate (should be replaced)
    validated_prompt, was_replaced = analyzer.security_mgr.validate_and_handle_prompt(
        prompt_name='tier1_core_prompt',
        current_prompt=tampered_prompt,
        change_source='agent',
        canonical_prompt_getter=lambda: create_tier1_core_prompt(sample_jobs)
    )

    assert was_replaced is True
    assert "TAMPERED TOKEN" not in validated_prompt
    assert "SECURITY TOKEN" in validated_prompt

def test_user_modification_allowed():
    """Test that user modifications are allowed (hash updated)"""
    analyzer = GeminiJobAnalyzer()

    sample_jobs = [{'id': 'test', 'title': 'Test', 'description': 'Test. ' * 30}]

    # Generate canonical prompt
    canonical_prompt = create_tier1_core_prompt(sample_jobs)

    # Simulate user modification
    user_modified_prompt = canonical_prompt.replace("SECURITY TOKEN", "USER MODIFIED TOKEN")

    # Validate as user change (should update hash)
    validated_prompt, was_replaced = analyzer.security_mgr.validate_and_handle_prompt(
        prompt_name='tier1_core_prompt',
        current_prompt=user_modified_prompt,
        change_source='user',
        canonical_prompt_getter=lambda: create_tier1_core_prompt(sample_jobs)
    )

    assert was_replaced is False
    assert "USER MODIFIED TOKEN" in validated_prompt

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

**Run:**
```bash
pytest tests/test_prompt_protection_integration.py -v
```

**Estimated time:** 1 hour

---

### Step 4.2: Manual Testing Checklist
**Create checklist:** `docs/TESTING-CHECKLIST-prompt-protection.md`

```markdown
# Prompt Protection Testing Checklist

## Pre-Testing Setup
- [ ] Clear existing hash registry: `rm storage/prompt_hashes.json`
- [ ] Clear existing change log: `rm storage/prompt_changes.jsonl`
- [ ] Start app to trigger registration

## Test 1: Initial Registration
- [ ] Run app startup
- [ ] Verify `storage/prompt_hashes.json` created
- [ ] Verify 3 prompts registered (tier1, tier2, tier3)
- [ ] Run `python tools/check_prompt_protection.py`
- [ ] Verify all prompts show `Updated By: system`

## Test 2: Normal Operation
- [ ] Run Tier 1 analysis on sample job
- [ ] Check logs for "✅ Security token validated"
- [ ] Verify no "⚠️ prompt was replaced" warnings
- [ ] Verify `storage/prompt_changes.jsonl` has no entries

## Test 3: Agent Tampering Simulation
- [ ] Manually edit `tier1_core_prompt.py` (change text in prompt)
- [ ] DON'T update hash
- [ ] Run Tier 1 analysis
- [ ] Verify log shows "⚠️ Tier 1 prompt was replaced"
- [ ] Verify `storage/prompt_changes.jsonl` has entry with `change_source: agent`
- [ ] Verify response still correct (used canonical version)

## Test 4: User Modification
- [ ] Edit `tier1_core_prompt.py` intentionally
- [ ] Run `python tools/update_prompt_hash.py tier1_core_prompt`
- [ ] Run Tier 1 analysis
- [ ] Verify NO replacement warning
- [ ] Verify `storage/prompt_changes.jsonl` has entry with `change_source: user`
- [ ] Run `python tools/check_prompt_protection.py`
- [ ] Verify updated hash and `Updated By: user`

## Test 5: All Tiers
- [ ] Repeat Test 2 for Tier 2
- [ ] Repeat Test 2 for Tier 3
- [ ] Verify all three tiers protected independently

## Test 6: Security Incident Logging
- [ ] Trigger token mismatch (modify response in test)
- [ ] Verify `storage/security_incidents.jsonl` created
- [ ] Verify incident logged with full details

## Success Criteria
✅ All prompts registered at startup
✅ Agent tampering detected and replaced
✅ User modifications allowed (hash updated)
✅ No false positives (normal operation = no warnings)
✅ All tiers independently protected
✅ Audit log complete and accurate
```

**Estimated time:** 2 hours

---

## Phase 5: Documentation & Deployment (Week 2, Days 4-5)

### Step 5.1: Update Main Documentation
**Files to update:**

1. **`docs/prompt-protection-reference.md`**
   - Update "Current State" section to show all prompts protected
   - Add actual integration examples from implementation

2. **`docs/prompt-security-usage-guide.md`**
   - Add production usage examples
   - Include CLI tool usage instructions

3. **`CLAUDE.md`**
   - Add section on prompt protection system
   - Document CLI tools for team

**Estimated time:** 1 hour

---

### Step 5.2: Create Deployment Guide
**File:** `docs/DEPLOYMENT-GUIDE-prompt-protection.md`

**Content:**
- Pre-deployment checklist
- Rollback procedure
- Monitoring during first week
- Troubleshooting guide

**Estimated time:** 30 minutes

---

## Total Estimated Time

| Phase | Estimated Time |
|-------|----------------|
| Phase 1: Core Integration | 2 hours |
| Phase 2: Tier 2 & 3 Integration | 1.5 hours |
| Phase 3: Monitoring & CLI | 1 hour |
| Phase 4: Testing & Validation | 3 hours |
| Phase 5: Documentation | 1.5 hours |
| **Total** | **9 hours (~2 work days)** |

---

## Implementation Order (Recommended)

**Day 1 (4 hours):**
1. Phase 1, Steps 1.1-1.2: Core integration in analyzer ✅
2. Phase 1, Step 1.3: Registration at startup ✅
3. Phase 1, Step 1.4: Basic testing ✅

**Day 2 (5 hours):**
4. Phase 2: Tier 2 & 3 integration ✅
5. Phase 3: CLI tools ✅
6. Phase 4: Integration testing ✅
7. Phase 5: Documentation ✅

---

## Success Metrics

**After Implementation:**
- ✅ 0 unauthorized agent modifications reach production
- ✅ 100% of agent tampering attempts logged
- ✅ User modifications tracked with full audit trail
- ✅ No false positives (normal operations don't trigger warnings)
- ✅ All three tiers independently protected

**After 1 Week:**
- Review `storage/prompt_changes.jsonl` for patterns
- Check `storage/security_incidents.jsonl` for unexpected entries
- Validate no performance degradation (hash validation <10ms overhead)

---

## Rollback Plan

**If issues detected:**
1. Comment out validation in `ai_analyzer.py` methods
2. Restart app (falls back to direct prompt usage)
3. Debug hash registry or change log
4. Fix issues, redeploy
5. Total rollback time: <5 minutes

**Safety:** Prompt protection is additive - removing it doesn't break core functionality

---

## Next Steps After Implementation

1. **Integrate with other optimizer modules:**
   - Token optimizer
   - Model selector
   - Batch size optimizer

2. **Add protection to other prompt types:**
   - Cover letter generation prompts
   - Resume optimization prompts
   - Any other AI-generated content

3. **Enhanced monitoring:**
   - Dashboard for protection status
   - Alerts for repeated tampering attempts
   - Weekly security reports

---

**Status:** 📋 Ready for Implementation
**Owner:** To be assigned
**Priority:** High (Security Critical)
