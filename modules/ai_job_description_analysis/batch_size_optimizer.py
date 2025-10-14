"""
Batch Size Optimizer - Intelligent Batch Sizing
================================================

Calculates optimal batch sizes for job analysis based on:
- Token limits
- Analysis tier complexity
- API rate limits
- Quality requirements
- Processing time constraints

Author: Automated Job Application System v4.3.2
Created: 2025-10-12
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BatchSizeRecommendation:
    """
    Batch size recommendation with rationale and metrics.
    """
    optimal_size: int
    min_size: int
    max_size: int
    reason: str
    batches_needed: int
    estimated_total_time: float  # seconds
    estimated_total_cost: float
    token_efficiency: float  # 0.0-1.0


class BatchSizeOptimizer:
    """
    Optimizes batch sizes for Gemini API calls to maximize efficiency
    while staying within token limits and rate limits.
    """

    # Token limits
    MAX_OUTPUT_TOKENS = 8192  # Gemini 2.0 Flash limit
    MAX_INPUT_TOKENS = 100000  # Approximate safe limit

    # API rate limits (free tier)
    REQUESTS_PER_MINUTE = 15
    REQUESTS_PER_DAY = 1500

    # Processing time estimates (seconds per job)
    PROCESSING_TIME_PER_JOB = {
        'tier1': 0.8,   # Complex analysis
        'tier2': 0.6,   # Medium analysis
        'tier3': 0.5,   # Light analysis
    }

    # Token allocations per job by tier
    TOKENS_PER_JOB = {
        'tier1': {
            'input': 600,   # Prompt + job description
            'output': 800,  # Analysis results
            'total': 1400
        },
        'tier2': {
            'input': 400,
            'output': 600,
            'total': 1000
        },
        'tier3': {
            'input': 400,
            'output': 600,
            'total': 1000
        }
    }

    # Overhead tokens (prompt structure, JSON schema, security)
    PROMPT_OVERHEAD = {
        'tier1': 1000,
        'tier2': 800,
        'tier3': 800,
    }

    def __init__(self):
        """Initialize the batch size optimizer."""
        logger.info("BatchSizeOptimizer initialized")

    def calculate_optimal_batch_size(
        self,
        total_jobs: int,
        tier: str = 'tier1',
        max_output_tokens: Optional[int] = None,
        time_constraint: Optional[float] = None,
        quality_priority: str = 'balanced'
    ) -> BatchSizeRecommendation:
        """
        Calculate optimal batch size for job analysis.

        Args:
            total_jobs: Total number of jobs to process
            tier: Analysis tier ('tier1', 'tier2', 'tier3')
            max_output_tokens: Override max output tokens (default: 8192)
            time_constraint: Maximum processing time in seconds (optional)
            quality_priority: 'speed', 'balanced', 'quality' (default: 'balanced')

        Returns:
            BatchSizeRecommendation with optimal settings
        """
        if tier not in self.TOKENS_PER_JOB:
            logger.warning(f"Unknown tier '{tier}', defaulting to tier1")
            tier = 'tier1'

        max_output = max_output_tokens or self.MAX_OUTPUT_TOKENS

        # Calculate constraints
        token_constrained_size = self._calculate_token_constrained_size(tier, max_output)
        rate_constrained_size = self._calculate_rate_constrained_size(total_jobs)
        quality_constrained_size = self._calculate_quality_constrained_size(tier, quality_priority)
        time_constrained_size = self._calculate_time_constrained_size(
            tier, time_constraint
        ) if time_constraint else None

        # Apply all constraints
        constraints = [
            token_constrained_size,
            rate_constrained_size,
            quality_constrained_size
        ]
        if time_constrained_size:
            constraints.append(time_constrained_size)

        optimal_size = min(constraints)
        optimal_size = max(1, optimal_size)  # At least 1 job

        # Calculate min/max range
        min_size = max(1, optimal_size // 2)
        max_size = min(optimal_size * 2, token_constrained_size)

        # Calculate metrics
        batches_needed = (total_jobs + optimal_size - 1) // optimal_size
        estimated_total_time = self._estimate_total_time(total_jobs, optimal_size, tier)
        estimated_total_cost = self._estimate_total_cost(total_jobs, tier)
        token_efficiency = self._calculate_token_efficiency(optimal_size, tier, max_output)

        # Build reason
        reason = self._build_reason(
            optimal_size,
            token_constrained_size,
            rate_constrained_size,
            quality_constrained_size,
            time_constrained_size,
            tier
        )

        recommendation = BatchSizeRecommendation(
            optimal_size=optimal_size,
            min_size=min_size,
            max_size=max_size,
            reason=reason,
            batches_needed=batches_needed,
            estimated_total_time=estimated_total_time,
            estimated_total_cost=estimated_total_cost,
            token_efficiency=token_efficiency
        )

        logger.info(
            f"Optimal batch size for {total_jobs} jobs ({tier}): {optimal_size} "
            f"({batches_needed} batches, ~{estimated_total_time:.1f}s total)"
        )

        return recommendation

    def _calculate_token_constrained_size(self, tier: str, max_output_tokens: int) -> int:
        """
        Calculate max batch size based on token limits.

        Args:
            tier: Analysis tier
            max_output_tokens: Maximum output tokens allowed

        Returns:
            Maximum jobs that fit within token limit
        """
        tokens_per_job = self.TOKENS_PER_JOB[tier]['output']
        overhead = self.PROMPT_OVERHEAD[tier]

        # Reserve tokens for overhead and safety margin (20%)
        available_tokens = max_output_tokens - overhead
        safety_margin = 0.8  # Use 80% of available tokens

        usable_tokens = available_tokens * safety_margin
        max_jobs = int(usable_tokens / tokens_per_job)

        return max(1, max_jobs)

    def _calculate_rate_constrained_size(self, total_jobs: int) -> int:
        """
        Calculate batch size based on API rate limits.

        For free tier: 15 requests/minute, 1500 requests/day
        Strategy: Balance between not hitting rate limits and completing in reasonable time

        Args:
            total_jobs: Total number of jobs to process

        Returns:
            Recommended batch size considering rate limits
        """
        # If total jobs are small, use smaller batches to stay under rate limits
        if total_jobs <= 150:  # Can be done in 10 requests
            return 15  # Medium batches

        elif total_jobs <= 1500:  # Can be done in 100 requests
            return 15  # Standard batches

        else:  # Large job sets
            # Need to maximize batch size to stay under daily limit
            # 1500 requests/day, aim for 80% utilization
            requests_available = int(self.REQUESTS_PER_DAY * 0.8)
            optimal_batch = (total_jobs + requests_available - 1) // requests_available
            return max(10, optimal_batch)

    def _calculate_quality_constrained_size(self, tier: str, quality_priority: str) -> int:
        """
        Calculate batch size based on quality requirements.

        Larger batches may reduce quality for complex analysis.

        Args:
            tier: Analysis tier
            quality_priority: 'speed', 'balanced', 'quality'

        Returns:
            Recommended batch size for quality
        """
        # Quality-based batch size recommendations
        quality_sizes = {
            'tier1': {
                'quality': 5,    # Small batches for best quality
                'balanced': 10,  # Balanced
                'speed': 20      # Larger batches for speed
            },
            'tier2': {
                'quality': 10,
                'balanced': 15,
                'speed': 25
            },
            'tier3': {
                'quality': 10,
                'balanced': 15,
                'speed': 25
            }
        }

        return quality_sizes.get(tier, {}).get(quality_priority, 10)

    def _calculate_time_constrained_size(self, tier: str, max_time: float) -> int:
        """
        Calculate batch size to meet time constraint.

        Args:
            tier: Analysis tier
            max_time: Maximum total time in seconds

        Returns:
            Batch size that fits within time constraint
        """
        time_per_job = self.PROCESSING_TIME_PER_JOB[tier]
        api_call_overhead = 2.0  # 2 seconds per API call

        # Calculate how many jobs can fit in time constraint
        # Account for multiple batches and API overhead
        # Approximate: time = (jobs * time_per_job) + (num_batches * overhead)

        # Try different batch sizes
        for batch_size in range(30, 0, -1):
            batches_needed = (1 + batch_size - 1) // batch_size  # At least 1 batch
            estimated_time = (batch_size * time_per_job) + (batches_needed * api_call_overhead)

            if estimated_time <= max_time:
                return batch_size

        return 1  # Minimum

    def _estimate_total_time(self, total_jobs: int, batch_size: int, tier: str) -> float:
        """
        Estimate total processing time.

        Args:
            total_jobs: Total number of jobs
            batch_size: Batch size
            tier: Analysis tier

        Returns:
            Estimated total time in seconds
        """
        batches_needed = (total_jobs + batch_size - 1) // batch_size
        time_per_batch = batch_size * self.PROCESSING_TIME_PER_JOB[tier]
        api_overhead = 2.0  # 2 seconds per API call
        rate_limit_delay = 0.0  # Add if hitting rate limits

        total_time = (batches_needed * time_per_batch) + (batches_needed * api_overhead)

        # Add rate limit delays if hitting 15 RPM limit
        batches_per_minute = 60 / (time_per_batch + api_overhead)
        if batches_per_minute > self.REQUESTS_PER_MINUTE:
            # Will hit rate limit, add delays
            rate_limit_delay = (batches_needed / self.REQUESTS_PER_MINUTE) * 60
            total_time += rate_limit_delay

        return total_time

    def _estimate_total_cost(self, total_jobs: int, tier: str) -> float:
        """
        Estimate total cost for processing all jobs.

        Args:
            total_jobs: Total number of jobs
            tier: Analysis tier

        Returns:
            Estimated cost in USD (free tier = $0.00)
        """
        # For free tier, cost is $0.00
        # For paid tier, calculate based on tokens

        tokens_per_job = self.TOKENS_PER_JOB[tier]['total']
        total_tokens = total_jobs * tokens_per_job

        # Assume free tier for now
        cost_per_1k_tokens = 0.0

        return (total_tokens / 1000) * cost_per_1k_tokens

    def _calculate_token_efficiency(
        self,
        batch_size: int,
        tier: str,
        max_output_tokens: int
    ) -> float:
        """
        Calculate token efficiency (how well we use allocated tokens).

        Args:
            batch_size: Batch size
            tier: Analysis tier
            max_output_tokens: Max output tokens allocated

        Returns:
            Efficiency score 0.0-1.0
        """
        tokens_per_job = self.TOKENS_PER_JOB[tier]['output']
        overhead = self.PROMPT_OVERHEAD[tier]

        tokens_used = (batch_size * tokens_per_job) + overhead
        efficiency = tokens_used / max_output_tokens

        return min(1.0, efficiency)

    def _build_reason(
        self,
        optimal_size: int,
        token_constrained: int,
        rate_constrained: int,
        quality_constrained: int,
        time_constrained: Optional[int],
        tier: str
    ) -> str:
        """Build explanation for batch size selection."""
        reasons = []

        # Identify binding constraint
        if optimal_size == token_constrained:
            reasons.append(f"Token limit constrains to {token_constrained} jobs/batch")

        if optimal_size == rate_constrained:
            reasons.append(f"API rate limits suggest {rate_constrained} jobs/batch")

        if optimal_size == quality_constrained:
            reasons.append(f"Quality optimization recommends {quality_constrained} jobs/batch")

        if time_constrained and optimal_size == time_constrained:
            reasons.append(f"Time constraint limits to {time_constrained} jobs/batch")

        # Add tier context
        reasons.append(f"{tier} analysis")

        return "; ".join(reasons)

    def get_batch_size_table(self, tier: str = 'tier1') -> Dict:
        """
        Get lookup table of batch sizes for different scenarios.

        Args:
            tier: Analysis tier

        Returns:
            Dict with batch size recommendations for various scenarios
        """
        scenarios = {
            'small_job_set': self.calculate_optimal_batch_size(50, tier),
            'medium_job_set': self.calculate_optimal_batch_size(500, tier),
            'large_job_set': self.calculate_optimal_batch_size(2000, tier),
            'speed_priority': self.calculate_optimal_batch_size(
                500, tier, quality_priority='speed'
            ),
            'quality_priority': self.calculate_optimal_batch_size(
                500, tier, quality_priority='quality'
            ),
            'time_constrained_5min': self.calculate_optimal_batch_size(
                100, tier, time_constraint=300
            ),
        }

        return {
            'tier': tier,
            'scenarios': {k: vars(v) for k, v in scenarios.items()}
        }
