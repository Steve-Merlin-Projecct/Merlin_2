# Gemini Optimization Implementation Guide
**Version:** 1.0
**Date:** 2025-10-12
**Status:** Ready for Integration

---

## Overview

This guide documents the implementation of Gemini AI optimization features targeting **30-40% cost reduction** while maintaining quality. All components have been built and are ready for integration.

---

## Implemented Components

### 1. **Prompt Security Manager** (`prompt_security_manager.py`)
Hash-based security system to prevent prompt tampering and unauthorized modifications.

**Features:**
- SHA-256 hashing of prompt templates
- Automatic tamper detection
- Secure prompt replacement
- Audit logging to database
- Integration with existing security tokens

**Usage Example:**
```python
from modules.ai_job_description_analysis.prompt_security_manager import PromptSecurityManager

# Initialize
security_mgr = PromptSecurityManager()

# Register prompt (do once during setup)
prompt_content = create_tier1_core_prompt([...])
security_mgr.register_prompt('tier1_core_prompt', prompt_content)

# Validate and get secure prompt (do before every API call)
def get_canonical_prompt():
    return create_tier1_core_prompt([...])

validated_prompt = security_mgr.get_validated_prompt(
    'tier1_core_prompt',
    current_prompt,
    get_canonical_prompt
)
```

**Security Benefits:**
- ✅ Protects against prompt injection
- ✅ Ensures security keys remain in place
- ✅ Logs all tampering attempts
- ✅ Automatic recovery with canonical versions

---

### 2. **Token Optimizer** (`token_optimizer.py`)
Dynamic token allocation based on job count and analysis tier.

**Features:**
- Calculate optimal `max_output_tokens` per batch
- Tier-aware token allocation
- Safety margins to prevent truncation
- Cost estimation
- Token efficiency metrics

**Usage Example:**
```python
from modules.ai_job_description_analysis.token_optimizer import TokenOptimizer

optimizer = TokenOptimizer()

# Calculate optimal tokens for a batch
allocation = optimizer.calculate_optimal_tokens(
    job_count=10,
    tier='tier1'
)

print(f"Use max_output_tokens: {allocation.max_output_tokens}")
print(f"Estimated cost: ${allocation.cost_estimate:.4f}")
print(f"Token efficiency: {allocation.token_efficiency:.1%}")

# Recommendations
for rec in allocation.recommendations:
    print(f"💡 {rec}")

# Use in API call
response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents=prompt,
    config=types.GenerateContentConfig(
        max_output_tokens=allocation.max_output_tokens  # Dynamic!
    )
)
```

**Before vs After:**
```python
# BEFORE: Fixed tokens (wasteful)
max_output_tokens = 8192  # Always maximum

# AFTER: Dynamic tokens (efficient)
allocation = optimizer.calculate_optimal_tokens(job_count=5, tier='tier1')
max_output_tokens = allocation.max_output_tokens  # ~4500 for 5 jobs
# Saves 45% tokens!
```

---

### 3. **Model Selector** (`model_selector.py`)
Intelligent model selection based on workload and constraints.

**Features:**
- Multi-factor model selection
- Quality-based auto-switching
- Budget-aware selection
- Time-of-day optimization
- Selection history tracking

**Usage Example:**
```python
from modules.ai_job_description_analysis.model_selector import ModelSelector

selector = ModelSelector(default_model='gemini-2.0-flash-001')

# Select optimal model
selection = selector.select_model(
    tier='tier1',
    batch_size=15,
    daily_tokens_used=500000,
    daily_token_limit=1500000,
    recent_quality_score=0.92,
    time_sensitive=False
)

print(f"Use model: {selection.model_id}")
print(f"Reason: {selection.selection_reason}")
print(f"Confidence: {selection.confidence:.1%}")
print(f"Estimated quality: {selection.estimated_quality:.1%}")

# Use selected model
response = client.models.generate_content(
    model=selection.model_id,  # Dynamic selection!
    contents=prompt,
    config=config
)
```

**Selection Strategies:**
- **Workload-based:** Tier 1 → Standard model, Tier 2/3 → Lite model
- **Budget-based:** >90% usage → Lite model, <40% usage → Premium model
- **Quality-based:** Low quality → Upgrade model, High quality → Try lite
- **Time-based:** Peak hours → Lite model, Off-peak → Better models

---

### 4. **Batch Size Optimizer** (`batch_size_optimizer.py`)
Calculate optimal batch sizes for maximum efficiency.

**Features:**
- Token-constrained sizing
- Rate-limit aware calculations
- Quality-priority options
- Time-constraint support
- Efficiency metrics

**Usage Example:**
```python
from modules.ai_job_description_analysis.batch_size_optimizer import BatchSizeOptimizer

optimizer = BatchSizeOptimizer()

# Calculate optimal batch size
recommendation = optimizer.calculate_optimal_batch_size(
    total_jobs=150,
    tier='tier1',
    quality_priority='balanced'
)

print(f"Optimal batch size: {recommendation.optimal_size}")
print(f"Will need {recommendation.batches_needed} batches")
print(f"Estimated time: {recommendation.estimated_total_time:.1f}s")
print(f"Token efficiency: {recommendation.token_efficiency:.1%}")
print(f"Reason: {recommendation.reason}")

# Use in processing loop
batch_size = recommendation.optimal_size
for i in range(0, total_jobs, batch_size):
    batch = jobs[i:i + batch_size]
    # Process batch...
```

**Dynamic Batch Sizing:**
```python
# Instead of fixed batch size
BATCH_SIZE = 10  # ❌ Fixed

# Use dynamic calculation
optimizer = BatchSizeOptimizer()
rec = optimizer.calculate_optimal_batch_size(len(jobs), 'tier1')
batch_size = rec.optimal_size  # ✅ Optimized
```

---

## Integration Checklist

### Phase 1: Core Integration (Week 1)

**Step 1: Add to `ai_analyzer.py`**
```python
from modules.ai_job_description_analysis.prompt_security_manager import PromptSecurityManager
from modules.ai_job_description_analysis.token_optimizer import TokenOptimizer
from modules.ai_job_description_analysis.model_selector import ModelSelector

class GeminiJobAnalyzer:
    def __init__(self):
        # ... existing code ...

        # Add new optimizers
        self.security_mgr = PromptSecurityManager()
        self.token_optimizer = TokenOptimizer()
        self.model_selector = ModelSelector()

    def analyze_jobs_batch(self, jobs: List[Dict]) -> Dict:
        # 1. Calculate optimal tokens
        allocation = self.token_optimizer.calculate_optimal_tokens(
            job_count=len(jobs),
            tier='tier1'
        )

        # 2. Select optimal model
        selection = self.model_selector.select_model(
            tier='tier1',
            batch_size=len(jobs),
            daily_tokens_used=self.current_usage.get('daily_tokens', 0),
            daily_token_limit=self.daily_token_limit
        )

        # 3. Create and validate prompt
        prompt = self._create_batch_analysis_prompt(jobs)

        validated_prompt = self.security_mgr.get_validated_prompt(
            'tier1_batch_prompt',
            prompt,
            lambda: self._create_batch_analysis_prompt(jobs)
        )

        # 4. Make API call with optimized settings
        response = self._make_gemini_request(
            validated_prompt,
            model=selection.model_id,
            max_output_tokens=allocation.max_output_tokens
        )

        return response
```

**Step 2: Update `_make_gemini_request()` to accept dynamic parameters**
```python
def _make_gemini_request(
    self,
    prompt: str,
    model: Optional[str] = None,
    max_output_tokens: Optional[int] = None
) -> Dict:
    """Make request with dynamic model and token settings."""

    model_to_use = model or self.current_model
    tokens_to_use = max_output_tokens or 8192

    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "topK": 1,
            "topP": 0.8,
            "maxOutputTokens": tokens_to_use,  # ✅ Dynamic
            "responseMimeType": "application/json",
        },
    }

    response = requests.post(
        f"{self.base_url}/v1beta/models/{model_to_use}:generateContent?key={self.api_key}",
        headers=headers,
        json=data,
        timeout=30
    )

    return response.json()
```

**Step 3: Initialize prompt registry (one-time setup)**
```python
# In app startup or migration script
from modules.ai_job_description_analysis.prompt_security_manager import PromptSecurityManager
from modules.ai_job_description_analysis.prompts import tier1_core_prompt, tier2_enhanced_prompt, tier3_strategic_prompt

security_mgr = PromptSecurityManager()

# Register all prompts
prompts_to_register = {
    'tier1_core_prompt': tier1_core_prompt.create_tier1_core_prompt,
    'tier2_enhanced_prompt': tier2_enhanced_prompt.create_tier2_enhanced_prompt,
    'tier3_strategic_prompt': tier3_strategic_prompt.create_tier3_strategic_prompt,
}

security_mgr.initialize_prompt_registry(prompts_to_register)
print("✅ Prompt registry initialized")
```

### Phase 2: Batch Processing Integration (Week 2)

**Update `batch_analyzer.py`:**
```python
from modules.ai_job_description_analysis.batch_size_optimizer import BatchSizeOptimizer

class BatchAIAnalyzer:
    def __init__(self):
        # ... existing code ...
        self.batch_optimizer = BatchSizeOptimizer()

    def process_analysis_queue(self, batch_size: Optional[int] = None, force_run: bool = False) -> Dict:
        # Use optimizer if batch_size not specified
        if batch_size is None:
            # Get total jobs to process
            total_jobs = self._count_queued_jobs()

            # Calculate optimal batch size
            recommendation = self.batch_optimizer.calculate_optimal_batch_size(
                total_jobs=total_jobs,
                tier='tier1',
                quality_priority='balanced'
            )

            batch_size = recommendation.optimal_size
            logger.info(f"Using optimized batch size: {batch_size} ({recommendation.reason})")

        # ... rest of existing code ...
```

---

## Testing & Validation

### Unit Tests

**Test 1: Token Optimizer**
```python
def test_token_optimizer():
    optimizer = TokenOptimizer()

    # Test Tier 1
    allocation = optimizer.calculate_optimal_tokens(job_count=10, tier='tier1')
    assert allocation.max_output_tokens <= 8192
    assert allocation.max_output_tokens >= 5000  # Should be reasonable

    # Test Tier 2
    allocation = optimizer.calculate_optimal_tokens(job_count=10, tier='tier2')
    assert allocation.max_output_tokens < 8000  # Should be less than Tier 1

    print("✅ Token optimizer tests passed")
```

**Test 2: Model Selector**
```python
def test_model_selector():
    selector = ModelSelector()

    # High usage should select lite model
    selection = selector.select_model(
        tier='tier1',
        batch_size=10,
        daily_tokens_used=1400000,  # 93% of 1.5M
        daily_token_limit=1500000
    )
    assert 'lite' in selection.model_id.lower()

    # Low usage can select better model
    selection = selector.select_model(
        tier='tier1',
        batch_size=10,
        daily_tokens_used=100000,  # 6% of 1.5M
        daily_token_limit=1500000
    )
    assert 'lite' not in selection.model_id.lower()

    print("✅ Model selector tests passed")
```

**Test 3: Batch Size Optimizer**
```python
def test_batch_size_optimizer():
    optimizer = BatchSizeOptimizer()

    # Small job set
    rec = optimizer.calculate_optimal_batch_size(50, tier='tier1')
    assert 5 <= rec.optimal_size <= 20

    # Large job set
    rec = optimizer.calculate_optimal_batch_size(2000, tier='tier1')
    assert rec.batches_needed > 100
    assert rec.optimal_size <= 25

    print("✅ Batch size optimizer tests passed")
```

**Test 4: Prompt Security Manager**
```python
def test_prompt_security_manager():
    from modules.ai_job_description_analysis.prompts.tier1_core_prompt import create_tier1_core_prompt

    security_mgr = PromptSecurityManager()

    # Create and register a prompt
    jobs = [{'id': 'test', 'title': 'Test Job', 'description': 'Test description'}]
    prompt = create_tier1_core_prompt(jobs)

    security_mgr.register_prompt('test_prompt', prompt)

    # Validate the same prompt
    is_valid, _ = security_mgr.validate_prompt('test_prompt', prompt)
    assert is_valid

    # Tamper with the prompt
    tampered_prompt = prompt.replace("SECURITY", "HACKED")

    # Should detect tampering
    is_valid, _ = security_mgr.validate_prompt('test_prompt', tampered_prompt)
    assert not is_valid

    print("✅ Prompt security manager tests passed")
```

### Integration Test

**Full workflow test:**
```python
def test_full_optimization_workflow():
    """Test all optimizers working together."""
    from modules.ai_job_description_analysis.ai_analyzer import GeminiJobAnalyzer

    analyzer = GeminiJobAnalyzer()

    # Add optimizers
    from modules.ai_job_description_analysis.token_optimizer import TokenOptimizer
    from modules.ai_job_description_analysis.model_selector import ModelSelector

    analyzer.token_optimizer = TokenOptimizer()
    analyzer.model_selector = ModelSelector()

    # Simulate analysis
    jobs = [
        {'id': f'job_{i}', 'title': f'Job {i}', 'description': 'Test description' * 50}
        for i in range(10)
    ]

    # Get optimal settings
    token_allocation = analyzer.token_optimizer.calculate_optimal_tokens(
        job_count=len(jobs),
        tier='tier1'
    )

    model_selection = analyzer.model_selector.select_model(
        tier='tier1',
        batch_size=len(jobs),
        daily_tokens_used=0,
        daily_token_limit=1500000
    )

    print(f"✅ Token allocation: {token_allocation.max_output_tokens}")
    print(f"✅ Model selected: {model_selection.model_id}")
    print(f"✅ Selection reason: {model_selection.selection_reason}")

    assert token_allocation.max_output_tokens > 0
    assert model_selection.model_id in ['gemini-2.0-flash-001', 'gemini-2.0-flash-lite-001']

    print("✅ Full workflow test passed")
```

---

## Monitoring & Metrics

### Metrics to Track

**Cost Metrics:**
```python
# Before optimization
avg_tokens_per_job_before = 2000
cost_per_job_before = (2000 / 1000) * 0.60  # $0.0012

# After optimization
avg_tokens_per_job_after = 1400  # 30% reduction
cost_per_job_after = (1400 / 1000) * 0.60  # $0.00084

savings = ((cost_per_job_before - cost_per_job_after) / cost_per_job_before) * 100
print(f"Cost savings: {savings:.1f}%")  # 30%
```

**Quality Metrics:**
```python
def measure_quality(results):
    """Measure analysis quality."""
    metrics = {
        'json_parse_rate': 0,
        'field_completeness': 0,
        'skill_count_avg': 0,
    }

    for result in results:
        # JSON parsing
        try:
            parsed = json.loads(result)
            metrics['json_parse_rate'] += 1
        except:
            continue

        # Field completeness
        required_fields = ['job_id', 'skills_analysis', 'authenticity_check']
        complete = all(field in parsed for field in required_fields)
        if complete:
            metrics['field_completeness'] += 1

        # Skill count
        skills = parsed.get('skills_analysis', {}).get('top_skills', [])
        metrics['skill_count_avg'] += len(skills)

    total = len(results)
    return {
        'json_parse_rate': metrics['json_parse_rate'] / total,
        'field_completeness': metrics['field_completeness'] / total,
        'skill_count_avg': metrics['skill_count_avg'] / total,
    }
```

### Dashboard Integration

Add to your monitoring dashboard:

```python
# Token efficiency over time
token_efficiency_data = {
    'timestamp': datetime.now().isoformat(),
    'allocated_tokens': allocation.max_output_tokens,
    'used_tokens': actual_tokens_used,
    'efficiency': actual_tokens_used / allocation.max_output_tokens,
}

# Model selection distribution
model_usage = {
    'gemini-2.0-flash-001': selection_count_flash,
    'gemini-2.0-flash-lite-001': selection_count_lite,
}

# Cost savings
cost_savings = {
    'baseline_cost': baseline_cost,
    'optimized_cost': optimized_cost,
    'savings_percent': ((baseline_cost - optimized_cost) / baseline_cost) * 100,
}
```

---

## Expected Results

### Cost Reduction Breakdown

| Component | Savings | Notes |
|-----------|---------|-------|
| Dynamic token allocation | 15-20% | No over-allocation |
| Smart model selection | 5-10% | Use lite when appropriate |
| Optimized batch sizes | 5-8% | Better token utilization |
| Prompt optimizations (future) | 10-15% | When implementing prompt changes |
| **Total Savings** | **35-53%** | **Exceeds 30-40% target** |

### Quality Maintenance

- JSON parse rate: >99% (same as before)
- Field completeness: >95% (same as before)
- Skill extraction: 5-35 skills (maintained)
- Analysis coherence: 4.5/5.0 (maintained)

---

## Rollback Plan

If optimization causes issues:

1. **Immediate Rollback:**
   ```python
   # Disable optimizations
   USE_TOKEN_OPTIMIZER = False
   USE_MODEL_SELECTOR = False
   USE_DYNAMIC_BATCHING = False

   # Revert to fixed settings
   max_output_tokens = 8192
   model = 'gemini-2.0-flash-001'
   batch_size = 10
   ```

2. **Partial Rollback:**
   - Keep prompt security (no cost impact)
   - Disable dynamic tokens
   - Keep fixed model selection

3. **Gradual Re-enable:**
   - Enable token optimizer only (lowest risk)
   - Add model selector after 1 week
   - Add batch optimizer after 2 weeks

---

## Next Steps

1. ✅ Review this implementation guide
2. ⏳ Run unit tests (see Testing section)
3. ⏳ Integrate Phase 1 (Core Integration)
4. ⏳ Monitor for 1 week, validate metrics
5. ⏳ Integrate Phase 2 (Batch Processing)
6. ⏳ Deploy to production with feature flags
7. ⏳ Monitor cost and quality for 1 month
8. ⏳ Implement prompt optimizations (Phase 3)

---

**Questions? See:**
- Technical details: `docs/prompt-optimization-suggestions.md`
- Code examples: Individual module files
- Security details: `prompt_security_manager.py` docstrings

**Last Updated:** 2025-10-12
**Owner:** AI Job Analysis Team
