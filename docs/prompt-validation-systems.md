# Prompt Validation Systems Documentation

## Overview

This document describes the two-system architecture implemented for prompt security validation in the Gemini AI Job Analysis module. The architecture ensures prompt integrity and prevents unauthorized modifications while maintaining security token validation across all three analysis tiers (Tier 1, Tier 2, and Tier 3).

## Architecture

### System 1: File Modification Validation

**Purpose**: Validates prompt templates at the file level BEFORE token insertion to ensure they match canonical versions.

**When it runs**: After any modification to prompt files

**Order of Operations**:
1. **Step 1.A**: Hash the prompt template (with placeholders, not runtime values)
2. **Step 1.B**: Compare hash to canonical hash stored in registry
3. **Step 1.C**: If different, replace prompt section with canonical version from git

### System 2: Runtime Execution Workflow

**Purpose**: Complete validation and execution workflow when sending data to Gemini AI

**When it runs**: During API calls to Gemini

**Order of Operations**:
1. **Step 2.A**: Run System 1 validation completely
2. **Step 2.B**: Generate security token
3. **Step 2.C**: Insert security token into prompt
4. **Step 2.D**: Send prompt and data to Gemini
5. **Step 2.E**: Receive data from Gemini
6. **Step 2.F**: Validate JSON format of response
7. **Step 2.G**: Validate Gemini returned correct security token
8. **Step 2.H**: Input validated data into database

## Implementation Details

### File Structure

```
modules/ai_job_description_analysis/
├── prompt_validation_systems.py    # System 1 & 2 implementation
├── prompts/
│   ├── tier1_core_prompt.py       # Tier 1: Core analysis prompt
│   ├── tier2_enhanced_prompt.py   # Tier 2: Enhanced analysis prompt
│   └── tier3_strategic_prompt.py  # Tier 3: Strategic analysis prompt
├── prompt_security_manager.py     # Legacy security manager (still used)
└── ai_analyzer.py                 # Integration point
```

### Analysis Tiers

**Tier 1: Core Analysis** (`tier1_core_prompt.py`)
- Essential job data extraction
- Target output: 1,500-2,000 tokens
- Returns: authenticity_check, classification, structured_data
- Used by: `GeminiJobAnalyzer.analyze_jobs_batch()`

**Tier 2: Enhanced Analysis** (`tier2_enhanced_prompt.py`)
- Risk assessment and cultural fit
- Target output: 1,000-1,500 tokens
- Builds on Tier 1 results
- Returns: stress_level_analysis, red_flags, implicit_requirements
- Used by: `GeminiJobAnalyzer.analyze_jobs_tier2()`

**Tier 3: Strategic Analysis** (`tier3_strategic_prompt.py`)
- Application preparation guidance
- Target output: 1,500-2,000 tokens
- Builds on Tier 1 + Tier 2 results
- Returns: prestige_analysis, cover_letter_insight
- Used by: `GeminiJobAnalyzer.analyze_jobs_tier3()`

### Key Classes

#### PromptValidationSystem1

Handles file-level validation:

```python
system1 = PromptValidationSystem1()

# Extract template from file
template = system1.extract_prompt_template(file_path)

# Calculate hash of template
hash = system1.calculate_template_hash(template)

# Validate and fix if needed
is_valid, was_replaced = system1.validate_and_fix(file_path, prompt_name)
```

#### PromptValidationSystem2

Handles complete runtime workflow for all tiers:

```python
system2 = PromptValidationSystem2()

# Tier 1 workflow
result = system2.execute_workflow(
    jobs=job_list,
    prompt_file_path="prompts/tier1_core_prompt.py",
    prompt_name="tier1_core_prompt",
    tier="tier1"
)

# Tier 2 workflow (with Tier 1 context)
result = system2.execute_workflow(
    jobs=jobs_with_tier1_context,
    prompt_file_path="prompts/tier2_enhanced_prompt.py",
    prompt_name="tier2_enhanced_prompt",
    tier="tier2"
)

# Tier 3 workflow (with Tier 1 + 2 context)
result = system2.execute_workflow(
    jobs=jobs_with_full_context,
    prompt_file_path="prompts/tier3_strategic_prompt.py",
    prompt_name="tier3_strategic_prompt",
    tier="tier3"
)

# Check results
if result['success']:
    analysis_results = result['data']
    steps_completed = result['steps_completed']
else:
    errors = result['errors']
```

### Canonical Prompt Storage

The canonical version of prompts is stored in git commit `a276ce8`. This ensures:
- Immutable reference point
- Version control integration
- Easy restoration

To manually restore canonical:
```bash
git checkout a276ce8 -- modules/ai_job_description_analysis/prompts/tier1_core_prompt.py
```

### Hash Registry

Canonical hashes for all three tiers are stored in `storage/prompt_hashes.json`:

```json
{
  "tier1_core_prompt": {
    "hash": "c15ee5c3bff63efd2c01f42f6fde5adfb0363b7f8d72ee45dfa72d70f478f25c",
    "registered_at": "2025-10-19T04:46:34.870153",
    "last_validated": "2025-10-19T04:46:34.870153",
    "description": "Tier 1 Core Analysis - Essential job data extraction",
    "file_path": "modules/ai_job_description_analysis/prompts/tier1_core_prompt.py"
  },
  "tier2_enhanced_prompt": {
    "hash": "9070dab27c5905578304abc50b99fa103cc0878a2d799275d81b55dec2e67597",
    "registered_at": "2025-10-19T04:46:34.892196",
    "last_validated": "2025-10-19T04:46:34.892196",
    "description": "Tier 2 Enhanced Analysis - Risk assessment and cultural fit",
    "file_path": "modules/ai_job_description_analysis/prompts/tier2_enhanced_prompt.py"
  },
  "tier3_strategic_prompt": {
    "hash": "a42d7fb123049b8e77978e4e3192a5f495744ac0d9dee74e6059a85780476eb6",
    "registered_at": "2025-10-19T04:46:34.913962",
    "last_validated": "2025-10-19T04:46:34.913962",
    "description": "Tier 3 Strategic Analysis - Application preparation guidance",
    "file_path": "modules/ai_job_description_analysis/prompts/tier3_strategic_prompt.py"
  }
}
```

To register or update canonical hashes:
```bash
python register_canonical_prompts.py
```

## Integration with AI Analyzer

All three tier analysis methods automatically use System 2 when available:

**Tier 1 - Core Analysis:**
```python
analyzer = GeminiJobAnalyzer()
result = analyzer.analyze_jobs_batch(jobs)

# Check which workflow was used
if result.get('workflow') == 'System2':
    # System 2 was used with full validation
    steps = result.get('steps_completed', [])
```

**Tier 2 - Enhanced Analysis:**
```python
analyzer = GeminiJobAnalyzer()
result = analyzer.analyze_jobs_tier2(jobs_with_tier1)

# Automatically uses System 2 validation
if result.get('workflow') == 'System2':
    steps = result.get('steps_completed', [])
```

**Tier 3 - Strategic Analysis:**
```python
analyzer = GeminiJobAnalyzer()
result = analyzer.analyze_jobs_tier3(jobs_with_tier1_and_tier2)

# Automatically uses System 2 validation
if result.get('workflow') == 'System2':
    steps = result.get('steps_completed', [])
```

## Security Features

### Template Hash Validation
- Hashes are calculated on template structure with placeholders
- Dynamic content (tokens, timestamps) are normalized before hashing
- Prevents unauthorized modifications to prompt structure

### Security Token Validation
- Random tokens generated at runtime (format: `SEC_TOKEN_[32 chars]`)
- Token must be returned by Gemini in response
- Mismatch triggers security incident logging

### Canonical Enforcement
- Automatic replacement with canonical version on hash mismatch
- Git-based canonical storage ensures immutability
- Audit trail of all replacements

### Security Incident Logging
- Failed validations logged to `storage/security_incidents.jsonl`
- Database logging to `security_detections` table when available
- Detailed incident metadata for forensics

## Testing

### Test Scripts

**Multi-Tier Validation Test:**
```bash
python test_all_tiers_validation.py
```
Tests System 1 validation for all three tiers:
- Tier 1 core prompt validation
- Tier 2 enhanced prompt validation
- Tier 3 strategic prompt validation
- Canonical hash registry verification

**Individual Validation Systems:**
```bash
python test_validation_systems.py
```
Tests:
- System 1 file validation (Tier 1 only)
- System 2 complete workflow
- Integration with AI analyzer

**End-to-End Flow:**
```bash
python test_end_to_end_flow.py
```
Tests complete data flow from job input through Gemini API to database storage.

**Register Canonical Hashes:**
```bash
python register_canonical_prompts.py
```
Registers or updates canonical hashes for all three tiers.

## Troubleshooting

### Common Issues

1. **Hash Mismatch on Valid Prompt**
   - Cause: Template extraction logic may not match prompt structure
   - Solution: Check PROMPT_START/END markers are correct

2. **Unterminated String Literal**
   - Cause: System 1 replacement corrupted Python syntax
   - Solution: Restore from canonical using git

3. **Security Token Validation Fails**
   - Cause: Gemini didn't return token or returned wrong token
   - Check: Gemini API response format
   - Check: Token extraction regex patterns

4. **System 2 Falls Back to Original Workflow**
   - Cause: Import error or validation failure in System 1
   - Check: Error logs for specific failure
   - Check: File permissions and paths

### Debug Logging

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Key log messages to watch:
- `System 1: Validating...` - File validation starting
- `System 1: Hash mismatch...` - Canonical replacement triggered
- `System 2: Step X...` - Workflow progress tracking
- `System 2: SECURITY WARNING...` - Security validation failed

## Best Practices

1. **Always Test After Prompt Changes**
   - Run validation tests after modifying prompts
   - Verify canonical hash updates if intentional change

2. **Monitor Security Incidents**
   - Regularly review `storage/security_incidents.jsonl`
   - Investigate any token validation failures

3. **Backup Canonical Versions**
   - Keep git commit reference documented
   - Consider tagging canonical commits

4. **Use System 2 for All API Calls**
   - Ensures complete validation workflow
   - Provides security token verification
   - Creates audit trail

## Future Enhancements

Potential improvements to consider:

1. **Multi-tier Prompt Support**
   - Extend to tier2_enhanced_prompt.py
   - Support for custom prompt templates

2. **Dynamic Canonical Updates**
   - Admin interface for updating canonical versions
   - Approval workflow for prompt changes

3. **Enhanced Monitoring**
   - Real-time alerts for security incidents
   - Dashboard for validation metrics

4. **Performance Optimization**
   - Cache validated prompts
   - Batch validation for multiple prompts

## Contact

For questions or issues with the prompt validation systems:
- Review this documentation
- Check test results and logs
- Consult git history for canonical versions

---

*Last updated: 2025-10-18*
*Version: 1.0.0*