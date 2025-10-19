#!/usr/bin/env python3
"""
Test what token limits the optimizer is calculating
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.ai_job_description_analysis.token_optimizer import TokenOptimizer

optimizer = TokenOptimizer()

print("=" * 80)
print("TOKEN OPTIMIZER CALCULATIONS")
print("=" * 80)
print()

for job_count in [1, 3, 5, 10]:
    allocation = optimizer.calculate_optimal_tokens(job_count, tier='tier1')

    print(f"Job count: {job_count}")
    print(f"  Max output tokens: {allocation.max_output_tokens}")
    print(f"  Tokens per job: {allocation.estimated_tokens_per_job}")
    print(f"  Safety margin: {allocation.safety_margin:.1%}")
    print(f"  Recommendations: {len(allocation.recommendations)}")
    for rec in allocation.recommendations:
        print(f"    - {rec}")
    print()
