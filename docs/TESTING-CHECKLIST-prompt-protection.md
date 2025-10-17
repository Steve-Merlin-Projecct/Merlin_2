# Prompt Protection Testing Checklist

## Pre-Testing Setup
- [ ] Clear existing hash registry: `rm storage/prompt_hashes.json`
- [ ] Clear existing change log: `rm storage/prompt_changes.jsonl`
- [ ] Start app to trigger registration: `python app_modular.py`

## Test 1: Initial Registration
- [ ] Run app startup
- [ ] Verify `storage/prompt_hashes.json` created
- [ ] Verify 3 prompts registered (tier1, tier2, tier3)
- [ ] Run `python tools/check_prompt_protection.py`
- [ ] Verify all prompts show `Updated By: system`

**Expected Output:**
```
🔐 PROMPT PROTECTION STATUS
================================================================================

📊 Total Registered Prompts: 3

📄 tier1_core_prompt
   Hash: a3f9d2e8b4c7c9f1...
   Registered: 2025-10-13T10:00:00.000000
   Last Updated: 2025-10-13T10:00:00.000000
   Updated By: system

📄 tier2_enhanced_prompt
   ...

📄 tier3_strategic_prompt
   ...
```

## Test 2: Normal Operation
- [ ] Create test script that uses `analyzer.analyze_jobs_batch(sample_jobs)`
- [ ] Check logs for "✅ Security token validated"
- [ ] Verify no "⚠️ prompt was replaced" warnings
- [ ] Verify `storage/prompt_changes.jsonl` has no new entries

**Expected Log Output:**
```
✅ Prompt security manager initialized
✅ Security token validated: a3f9d2e8...
```

## Test 3: Agent Tampering Simulation
- [ ] Manually edit `tier1_core_prompt.py` (change text in PROMPT_START section)
- [ ] DON'T update hash
- [ ] Run Tier 1 analysis
- [ ] Verify log shows "⚠️ Tier 1 prompt was replaced"
- [ ] Verify `storage/prompt_changes.jsonl` has entry with `change_source: agent`
- [ ] Verify response still correct (used canonical version)

**Expected Log Output:**
```
⚠️ Hash mismatch detected for tier1_core_prompt
🔄 Replacing with canonical version (source: agent)
⚠️ Tier 1 prompt was replaced due to unauthorized modification
```

**Expected Change Log Entry:**
```json
{
  "timestamp": "2025-10-13T10:30:45.123456",
  "prompt_name": "tier1_core_prompt",
  "old_hash": "a3f5c2e1b4d7c8f9...",
  "new_hash": "a3f5c2e1b4d7c8f9...",
  "change_source": "agent",
  "action_taken": "replaced_prompt",
  "additional_info": {"reason": "unauthorized_agent_modification"}
}
```

## Test 4: User Modification
- [ ] Edit `tier1_core_prompt.py` intentionally (add comment or change wording)
- [ ] Run `python tools/update_prompt_hash.py tier1_core_prompt`
- [ ] Run Tier 1 analysis
- [ ] Verify NO replacement warning
- [ ] Verify `storage/prompt_changes.jsonl` has entry with `change_source: user`
- [ ] Run `python tools/check_prompt_protection.py`
- [ ] Verify updated hash and `Updated By: user`

**Expected Output:**
```bash
$ python tools/update_prompt_hash.py tier1_core_prompt
Updating hash for: tier1_core_prompt
✅ Hash updated successfully
```

**Expected Change Log Entry:**
```json
{
  "timestamp": "2025-10-13T10:35:22.456789",
  "prompt_name": "tier1_core_prompt",
  "old_hash": "a3f5c2e1b4d7c8f9...",
  "new_hash": "c9e4a7f3d1b8e5a2...",
  "change_source": "user",
  "action_taken": "updated_hash",
  "additional_info": {"reason": "user_modification"}
}
```

## Test 5: All Tiers Independent Protection
- [ ] Repeat Test 2 for Tier 2 (`analyzer.analyze_jobs_tier2()`)
- [ ] Repeat Test 2 for Tier 3 (`analyzer.analyze_jobs_tier3()`)
- [ ] Verify all three tiers protected independently
- [ ] Verify modifying one tier doesn't affect others

## Test 6: Security Incident Logging (Round-Trip Token)
- [ ] Create mock response with wrong security token
- [ ] Trigger validation in `_parse_batch_response()`
- [ ] Verify `storage/security_incidents.jsonl` created
- [ ] Verify incident logged with full details

**Expected Security Incident:**
```json
{
  "timestamp": "2025-10-13T10:40:15.789012",
  "incident_type": "token_mismatch",
  "expected_token": "a3f9d2e8b4c7c9f1",
  "received_token": "fake123",
  "full_expected_token": "a3f9d2e8b4c7c9f1e3a5b7d9c1e3f5a7",
  "full_received_token": "fake123",
  "response_preview": "{\"security_token\": \"fake123\", \"analysis_results\": [...]}",
  "model": "gemini-2.0-flash"
}
```

## Test 7: Automated Test Suite
- [ ] Run `pytest tests/test_prompt_protection_integration.py -v`
- [ ] Verify all tests pass
- [ ] Check coverage report

**Expected Output:**
```bash
$ pytest tests/test_prompt_protection_integration.py -v

tests/test_prompt_protection_integration.py::test_analyzer_has_security_manager PASSED
tests/test_prompt_protection_integration.py::test_prompt_validation_on_generation PASSED
tests/test_prompt_protection_integration.py::test_agent_tampering_detection PASSED
tests/test_prompt_protection_integration.py::test_user_modification_allowed PASSED
tests/test_prompt_protection_integration.py::test_tier2_protection PASSED
tests/test_prompt_protection_integration.py::test_tier3_protection PASSED

============================== 6 passed in 2.34s ===============================
```

## Test 8: CLI Tools Functionality
- [ ] Run `python tools/check_prompt_protection.py`
- [ ] Verify correct display of all registered prompts
- [ ] Verify recent changes displayed (if any)
- [ ] Test hash update tool: `python tools/update_prompt_hash.py tier1_core_prompt`
- [ ] Verify hash update successful

## Test 9: Performance Impact
- [ ] Time normal prompt generation (without protection)
- [ ] Time protected prompt generation (with validation)
- [ ] Verify overhead < 10ms per prompt
- [ ] Check no memory leaks after 100 validations

**Expected Performance:**
- Hash validation: < 5ms
- Token extraction: < 2ms
- Total overhead: < 10ms per prompt

## Test 10: Error Handling
- [ ] Test with missing `storage/` directory
- [ ] Test with corrupted `prompt_hashes.json`
- [ ] Test with invalid prompt name
- [ ] Verify graceful degradation (logs warning, continues)

## Success Criteria

✅ **All tests must pass:**
- [ ] All prompts registered at startup
- [ ] Agent tampering detected and replaced (100% detection rate)
- [ ] User modifications allowed (hash updated correctly)
- [ ] No false positives (normal operation = no warnings)
- [ ] All tiers independently protected
- [ ] Audit log complete and accurate
- [ ] CLI tools functional
- [ ] Performance impact < 10ms
- [ ] Graceful error handling

## Rollback Plan

**If any test fails:**
1. Document the failure in detail
2. Comment out validation in affected methods
3. Restart app (falls back to direct prompt usage)
4. Debug hash registry or change log
5. Fix issues, redeploy
6. Re-run full test suite

**Total rollback time: < 5 minutes**

## Post-Testing Validation

After successful testing:
- [ ] Review all log files for unexpected warnings
- [ ] Verify storage files created correctly
- [ ] Check file permissions on storage directory
- [ ] Document any issues or edge cases discovered
- [ ] Update this checklist with lessons learned

---

**Testing Duration:** 1-2 hours
**Required Environment:** GEMINI_API_KEY must be set
**Cleanup:** Remove test storage files after completion
